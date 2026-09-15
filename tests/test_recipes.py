import os
import shutil
import subprocess

from cascade.repos import Repo
from cascade.lines import DataLine, ModelLine


def clean(recipe_dir, manifest):
    for name in manifest.get("outputs", {}).keys():
        path = os.path.join(recipe_dir, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)


def check_metrics(recipe_dir, line_name, index, meta, expected_metrics):
    metrics = {m["name"]: m["value"] for m in meta.get("metrics", [])}
    for metric_name, bounds in expected_metrics.items():
        model = f"{recipe_dir}/{line_name}[{index}]"
        assert metric_name in metrics, f"{model} is missing metric '{metric_name}'"

        value = metrics[metric_name]
        assert value == value, f"{model} metric '{metric_name}' is NaN"

        lo, hi = bounds.get("min"), bounds.get("max")
        if lo is not None:
            assert value >= lo, f"{model} metric '{metric_name}'={value} is below {lo}"
        if hi is not None:
            assert value <= hi, f"{model} metric '{metric_name}'={value} is above {hi}"


def check_line(root, name, expect):
    if expect["type"] == "model_line":
        line = ModelLine(os.path.join(root, name))
    elif expect["type"] == "data_line":
        line = DataLine(os.path.join(root, name))
    else:
        raise RuntimeError(f"{expect['type']} is an unknown line type")

    item_num = expect.get("len")
    if item_num is not None:
        assert len(line) == item_num

    for i in range(len(line)):
        meta = line.load_obj_meta(i)[0]

        if expect["type"] == "model_line":
            check_metrics(root, name, i, meta, expect.get("metrics", {}))


def check_repo(recipe_dir, name, expected):
    repo = Repo(os.path.join(recipe_dir, name))
    lines = repo.get_line_names()

    assert len(lines) == len(expected["lines"])

    for line in lines:
        check_line(os.path.join(recipe_dir, name), line, expected["lines"][line])


def check_outputs(expected, outputs):
    assert len(expected) == len(outputs)

    for exp, out in zip(expected, outputs):
        if exp.get("not_in"):
            assert exp["not_in"] not in out


def test_recipe_runs_end_to_end(recipe_dir, manifest):
    clean(recipe_dir, manifest)

    results = []
    for step in manifest["steps"]:
        result = subprocess.run(
            step,
            cwd=recipe_dir,
            capture_output=True,
            text=True,
            timeout=manifest.get("timeout_s", 300),
        )
        results.append(result)

        assert result.returncode == 0, (
            f"{recipe_dir}/{step} exited with {result.returncode}\n"
            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
        )

    for out_name in manifest.get("outputs", {}):
        output = manifest["outputs"][out_name]

        if output["type"] == "repo":
            check_repo(recipe_dir, out_name, output)
        elif output["type"] in ("model_line", "data_line"):
            check_line(recipe_dir, out_name, output)
        elif output["type"] == "folder":
            assert os.path.exists(os.path.join(recipe_dir, out_name))
        elif output["type"] == "steps":
            check_outputs(output["stdout"], [res.stdout for res in results])
        else:
            raise RuntimeError(f"Unknown output type: {output['type']}")

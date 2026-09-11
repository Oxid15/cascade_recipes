import os
import shutil
import subprocess
import sys

from cascade.repos import Repo


def clean(recipe_dir, manifest):
    for rel in manifest.get("outputs", []):
        path = os.path.join(recipe_dir, rel)
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


def test_recipe_runs_end_to_end(recipe_dir, manifest):
    clean(recipe_dir, manifest)

    for step in manifest["steps"]:
        result = subprocess.run(
            [sys.executable, step],
            cwd=recipe_dir,
            capture_output=True,
            text=True,
            timeout=manifest.get("timeout_s", 300),
        )
        assert result.returncode == 0, (
            f"{recipe_dir}/{step} exited with {result.returncode}\n"
            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
        )

    repo = Repo(os.path.join(recipe_dir, manifest.get("repo_path", "repo")))
    line_names = repo.get_line_names()

    for name, expect in manifest.get("model_lines", {}).items():
        assert name in line_names, f"expected model line '{name}' in {recipe_dir}/repo"
        line = repo[name]
        min_models = expect.get("min_models", 1)
        assert (
            len(line) >= min_models
        ), f"{recipe_dir}/{name} has {len(line)} models, expected >= {min_models}"
        for i in range(len(line)):
            meta = line.load_obj_meta(i)[0]
            check_metrics(recipe_dir, name, i, meta, expect.get("metrics", {}))

    for name, expect in manifest.get("data_lines", {}).items():
        assert name in line_names, f"expected data line '{name}' in {recipe_dir}/repo"
        line = repo[name]
        min_versions = expect.get("min_versions", 1)
        assert (
            len(line) >= min_versions
        ), f"{recipe_dir}/{name} has {len(line)} versions, expected >= {min_versions}"

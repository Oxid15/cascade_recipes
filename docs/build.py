import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Compiler:
    """
    Compiles multiple .py files into a single .rst
    """

    def make_rst_block(self, block: str):
        rst = ""
        for line in block.split("\n"):
            if line.startswith("[rst]"):
                continue
            if line.startswith("# "):
                line = line[2:]
            if line == "#":
                line = ""

            rst += line
            rst += "\n"

        rst += "\n"
        return rst

    def make_code_block(self, block: str):
        code_block = ".. code-block:: python\n\n"
        for line in block.split("\n"):
            code_block += "    "
            code_block += line
            code_block += "\n"
        code_block += "\n"
        return code_block

    def compile(self, files: list[str]):
        rst = ""
        for file in files:
            with open(file, "r") as f:
                text = f.read()

            for block in text.split("# %%"):
                block = block.strip()
                if not block:
                    continue
                elif block.startswith("[rst]"):
                    rst += self.make_rst_block(block)
                else:
                    rst += self.make_code_block(block)
        return rst


if __name__ == "__main__":
    recipe_dirs = []
    for d_name in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, d_name)

        if os.path.isfile(d):
            continue

        if "recipe.yaml" in os.listdir(d):
            recipe_dirs.append(d)

    compiler = Compiler()
    for d in recipe_dirs:
        try:
            with open(os.path.join(d, "recipe.yaml"), "r") as f:
                manifest = yaml.safe_load(f)
        except Exception as e:
            print(f"Error during reading recipe manifest at {d}: ", e)
            continue

        try:
            files = manifest["docs"]["files"]
        except KeyError:
            print(
                f"{os.path.join(d, 'recipe.yaml')} should have docs.files key with the file order"
            )
            continue

        files = [os.path.join(d, f) for f in files]
        rst = compiler.compile(files)

        recipe_name = os.path.basename(d)
        with open(os.path.join(ROOT, "docs", f"{recipe_name}.rst"), "w") as f:
            f.write(rst)

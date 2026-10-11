import os

import yaml

DOCS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DOCS)


class Compiler:
    """
    Generates .rst docs for all recipes using .py files
    and recipe.yaml manifests
    """

    def make_rst_block(self, block: str) -> str:
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

    def make_code_block(self, block: str) -> str:
        code_block = ".. code-block:: python\n\n"
        for line in block.split("\n"):
            code_block += "    "
            code_block += line
            code_block += "\n"
        code_block += "\n"
        return code_block

    def make_recipes_page(self, names: list[str]) -> str:
        rst = "Cascade Recipes"
        rst = rst + "\n" + "#" * len(rst) + "\n\n"
        rst += ".. toctree::\n    :maxdepth: 1\n\n"

        for name in names:
            rst += f"    {name}\n"
        return rst

    def make_howtos_grid(self, names: list[str], titles: list[str]) -> str:
        rst = ".. grid:: 1\n\n"

        for name, title in zip(names, titles, strict=True):
            cell = "    .. grid-item::\n"
            cell += f"        .. card:: {title}\n"
            cell += f"            :link: /howtos/recipes/{name}.rst\n"
            cell += "            :link-type: ref\n\n"

            rst += cell

        return rst

    def compile(self, files: list[str], title: str) -> str:
        rst = ""
        rst = rst + title + "\n"
        rst = rst + "#" * len(title) + "\n"

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

    build_dir = os.path.join(DOCS, "build")
    os.makedirs(build_dir, exist_ok=True)

    compiler = Compiler()
    recipe_names = []
    recipe_titles = []
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

        title = manifest["docs"].get("title")
        if not title:
            raise ValueError(
                f"{os.path.join(d, 'recipe.yaml')} should have non-empty docs.title key with the posts title"
            )

        files = [os.path.join(d, f) for f in files]
        rst = compiler.compile(files, title)

        recipe_name = os.path.basename(d)
        with open(os.path.join(build_dir, f"{recipe_name}.rst"), "w") as f:
            f.write(rst)

        recipe_names.append(recipe_name)
        recipe_titles.append(title)

    recipes_rst = compiler.make_recipes_page(recipe_names)
    with open(os.path.join(build_dir, "recipes.rst"), "w") as f:
        f.write(recipes_rst)

    howtos_grid_rst = compiler.make_howtos_grid(recipe_names, recipe_titles)
    with open(os.path.join(build_dir, "howtos_grid.rst"), "w") as f:
        f.write(howtos_grid_rst)

import glob
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def discover_recipes():
    recipes = []
    for manifest_path in sorted(glob.glob(os.path.join(ROOT, "*", "recipe.yaml"))):
        recipe_dir = os.path.dirname(manifest_path)
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)
        recipes.append((recipe_dir, manifest))
    return recipes


def pytest_generate_tests(metafunc):
    if "recipe_dir" in metafunc.fixturenames and "manifest" in metafunc.fixturenames:
        recipes = discover_recipes()
        metafunc.parametrize(
            "recipe_dir,manifest",
            recipes,
            ids=[d for d, _ in recipes],
        )

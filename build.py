from fastapi import Request
from main import root, item_page
import shutil
from pathlib import Path
from utils.load_data import load_data


def build_index():
    page = root(Request)
    (site_path / "index.html").write_bytes(page.body)


def build_items():
    items, site_data = load_data()
    for item in items:
        page = item_page(Request, item.slug)
        (site_path / "item" / (item.slug + ".html")).write_bytes(page.body)


if __name__ == "__main__":
    # Create site directory
    site_path = Path.cwd() / "site"
    if not site_path.exists():
        site_path.mkdir(parents=True, exist_ok=True)

    # Copy assets to site directory
    if not (site_path / "assets").exists():
        shutil.copytree((Path.cwd() / "assets"), (site_path / "assets"))
    else:
        shutil.rmtree((site_path / "assets"))
        shutil.copytree((Path.cwd() / "assets"), (site_path / "assets"))

    if not (site_path / "item").exists():
        (site_path / "item").mkdir(parents=True, exist_ok=True)

    build_index()
    build_items()

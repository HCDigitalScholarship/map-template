from fastapi import Request
from main import root
import shutil
from pathlib import Path 


def build_index():
    page = root(Request)
    (site_path / 'index.html').write_bytes(page.body)
    


if __name__ == '__main__':
    # Create site directory
    site_path = Path.cwd() / 'site'
    if not site_path.exists():
        site_path.mkdir(parents=True, exist_ok=True)

    # Copy assets to site directory
    if not (site_path / 'assets').exists():
        shutil.copytree((Path.cwd() / 'assets'), (site_path / 'assets')) 
    else:
        shutil.rmtree((site_path / 'assets'))
        shutil.copytree((Path.cwd() / 'assets'), (site_path / 'assets')) 

    build_index()
import jinja2

from src.utils import find_file


def get_template(name: str, dir="src/templates"):
    loader = jinja2.FileSystemLoader(find_file(dir))
    env = jinja2.Environment(loader=loader)
    return env.get_template(name)

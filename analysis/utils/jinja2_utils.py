import jinja2

from analysis.utils import find_file


def get_template(name: str, dir="analysis/templates"):
    loader = jinja2.FileSystemLoader(find_file(dir))
    env = jinja2.Environment(loader=loader)
    return env.get_template(name)

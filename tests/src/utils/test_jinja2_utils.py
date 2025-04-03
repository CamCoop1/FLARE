import jinja2
import pytest

from flare.src.utils.jinja2_utils import get_template


@pytest.fixture
def fake_template_dir(tmp_path):
    """Creates a temporary template directory with a sample template."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "test_template.py"
    template_file.write_text("Hello, {{ name }}!")  # Sample Jinja2 template
    return template_dir


def test_get_template_success(fake_template_dir):
    """Test given a valid template, get_template is successful"""
    template = get_template("test_template.py", fake_template_dir)

    assert isinstance(template, jinja2.Template)
    assert template.render(name="World") == "Hello, World!"


def test_get_template_missing(fake_template_dir):
    """Test TemplateNotFound is raised when no template is found"""
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        get_template("incorrect_template.yaml", fake_template_dir)


def test_get_template_custom_dir(tmp_path):
    """Test when given a custom directory, get_template still located the requested file"""
    custom_dir = tmp_path / "custom_templates"
    custom_dir.mkdir()
    (custom_dir / "custom.py").write_text("Custom Template!")

    get_template("custom.py", dir=custom_dir)

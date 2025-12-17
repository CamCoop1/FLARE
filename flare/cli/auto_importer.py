import importlib
import pkgutil


def auto_import_package(pkg_name: str):
    """
    Import all submodules of a package, excluding 'registry'.
    """
    pkg = importlib.import_module(pkg_name)

    if not hasattr(pkg, "__path__"):
        raise ValueError(f"{pkg_name} is not a package")

    for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
        if modname == "registry":
            continue

        importlib.import_module(f"{pkg_name}.{modname}")


def auto_import_registry(pkg_name: str):
    """
    Import all submodules of a package, excluding 'registry'.
    """
    pkg = importlib.import_module(pkg_name)

    if not hasattr(pkg, "__path__"):
        raise ValueError(f"{pkg_name} is not a package")

    for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
        if modname == "registry":
            importlib.import_module(f"{pkg_name}.{modname}")

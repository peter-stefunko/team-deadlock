def import_db_all_models() -> None:
    import pkgutil
    from pathlib import Path

    package_dir = Path(__file__).resolve().parent.parent.parent

    modules = pkgutil.walk_packages(
        path=[str(package_dir)],
    )

    model_modules = []

    for module in modules:
        path = Path(f"{module.module_finder.path}/{module.name}")  # type: ignore
        if not path.is_dir():
            continue

        for child in path.iterdir():
            if child.name == "models.py":
                model_modules.append(child.parent.name)
                break

    for model_module in model_modules:
        __import__(f"src.{model_module}.models")

from src.utils.dirs import find_file
from src.utils.yaml import get_config

flare_config = get_config("details")
results_subdir = f"{flare_config['Name']}/{flare_config['Version']}"

dataprod_dir = find_file(flare_config["StudyDir"], "mc_production")

dataprod_config = (
    get_config("details.yaml", dataprod_dir) if dataprod_dir.exists() else None
)

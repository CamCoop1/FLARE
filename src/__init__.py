from src.utils.yaml import get_config

details = get_config("details")
results_subdir = f"{details['Name']}/{details['Version']}"
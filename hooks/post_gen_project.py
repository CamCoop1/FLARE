import os
import subprocess


def init_git_repo():
    subprocess.run(["git", "init"], check=True)


def init_git_commit():
    subprocess.run(["git", "add", ".gitignore", ".pre-commit-config.yaml"], check=True)
    subprocess.run(["git", "add", "*"], check=True)
    subprocess.run(["git", "commit", "-m", "'Init commit'"], check=True)


def create_analysis_artifacts():
    analysis_config_dir = 'analysis/config'
    
    os.makedirs(analysis_config_dir, exist_ok=True)
    
    with open(f'{analysis_config_dir}/details.yaml', 'w') as f:
        f.write(
""""$schema": "src/schemas/config_details.json"

Name : {{ cookiecutter.project_slug }}
Version: {{ cookiecutter.version }}
Description: {{ cookiecutter.description}}

"""
        )
        
def create_mc_production_artifacts():
    mc_production = "{{ cookiecutter.mc_production }}".strip().upper()

    if mc_production == 'Y':
        prod_dir = 'analysis/mc_production'
        os.makedirs(prod_dir, exist_ok=True)
        
        with open(f'{prod_dir}/detail.yaml', 'w') as f:
            f.write(
""""$schema": "src/schemas/mc_production_details.json"

prodtype : Choose your production type

datatype:
    - add 
    - your
    - datatypes 
"""
            )
if __name__ == "__main__":
    create_analysis_artifacts()
    create_mc_production_artifacts()
    if os.path.isdir(".git"):
        print("Git repository already initialized.")
    else:
        print("Initializing git repo for your analysis")
        init_git_repo()
        init_git_commit()
        print("Initialised git repo")

    print("Your FCC analysis framework powered by b2luigi is installed.")

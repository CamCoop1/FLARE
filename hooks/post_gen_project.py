import os
import subprocess


def init_git_repo():
    subprocess.run(["git", "init"], check=True)


def init_git_commit():
    subprocess.run(["git", "add", ".gitignore", ".pre-commit-config.yaml"], check=True)
    subprocess.run(["git", "add", "*"], check=True)
    subprocess.run(["git", "commit", "-m", "'Init commit'"], check=True)


if __name__ == "__main__":
    if os.path.isdir(".git"):
        print("Git repository already initialized.")
    else:
        print("Initializing git repo for your analysis")
        init_git_repo()
        init_git_commit()
        print("Initialised git repo")

    print("Your FCC analysis framework powered by b2luigi is installed.")

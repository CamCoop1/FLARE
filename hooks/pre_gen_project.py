

mc_production = "{{ cookiecutter.mc_production }}".strip().upper()

if mc_production not in ['Y', 'N']:
    raise ValueError(
        f'The returned value of mc_prodiction is not Y or N. Ensure you are correctly answering the questions on the commandline'
    )
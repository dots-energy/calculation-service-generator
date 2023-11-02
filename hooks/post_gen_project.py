import os
import shutil
import yaml

# remove jinja2 templates folder
shutil.rmtree(os.path.join(os.getcwd(), "jinja2-templates"))

# save cookiecutter config file
with open("cookiecutter_service_config.yaml", "w") as outfile:
    yaml.dump(
        dict({{cookiecutter | dictsort}}),
        outfile,
        default_flow_style=False,
        sort_keys=False,
    )

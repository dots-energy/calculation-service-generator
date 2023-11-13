#  This work is based on original code developed and copyrighted by TNO 2023.
#  Subsequent contributions are licensed to you by the developers of such code and are
#  made available to the Project under one or several contributor license agreements.
#
#  This work is licensed to you under the Apache License, Version 2.0.
#  You may obtain a copy of the license at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Contributors:
#      TNO         - Initial implementation
#  Manager:
#      TNO

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

import json

from gssutils import *
from pathlib import Path

from assets.attributes import Attributes
from assets.referenceGenerator import generate_reference_data
from assets.jenkinsUtils import update_jenkins

with open("data.json", "r") as f:
    data_dict = json.load(f)
    
for url, arguments in data_dict.items():

    directory_name = pathify(url).replace("https-//", "").replace("/", "-")
    try:
        update_jenkins(directory_name)
    except Exception:
        raise Exception("Aborting. Unable to generate Jenkins job for job '{}'.".format(url))
    
    outputFolder = Path('datasets/{}'.format(directory_name))
    outputFolder.mkdir(exist_ok=True, parents=True)
    
    # TODO - we're adding a blank info.json to satisfy jenkins
    # probably need to get more use out of this.
    info_path = Path(outputFolder / 'info.json')
    with open(info_path, "w") as f:
        json.dump({}, f)

    # TODO -  we may be able to just call this info.json, spike it.
    json_path = Path(outputFolder / 'cmd-info.json')
    with open(json_path, "w") as f:
        json.dump(data_dict, f)
        
    pipeline_path = Path(outputFolder / 'main.py')
    with open("./assets/pipeline-template.txt", "r") as f1:
        with open(pipeline_path, "w") as f2:
            f2.write(f1.read())
    
    # TODO move attributes into gssutils
    pipeline_path = Path(outputFolder / 'attributes.py')
    with open("./assets/attributes.py", "r") as f1:
        with open(pipeline_path, "w") as f2:
            f2.write(f1.read())
            
    pipeline_path = Path(outputFolder / 'cmdScraper.py')
    with open("./assets/cmdScraper.py", "r") as f1:
        with open(pipeline_path, "w") as f2:
            f2.write(f1.read())
            
generate_reference_data()
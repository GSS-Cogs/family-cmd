from gssutils import *
from attributes import Attributes
import json
from pathlib import Path
from referenceGenerator import generate_reference_data
with open("data.json", "r") as f:
    data_dict = json.load(f)
    
for url, arguments in data_dict.items():
    
    directory_name = pathify(url).replace("https-//", "").replace("/", "-")
    outputFolder = Path('datasets/{}'.format(directory_name))
    outputFolder.mkdir(exist_ok=True, parents=True)
    
    json_path = Path(outputFolder / 'cmd-info.json')
    with open(json_path, "w") as f:
        json.dump(data_dict, f)
        
    pipeline_path = Path(outputFolder / 'main.py')
    with open("pipeline-template.txt", "r") as f1:
        with open(pipeline_path, "w") as f2:
            f2.write(f1.read())
    
    # TODO move attributes into gssutils
    pipeline_path = Path(outputFolder / 'attributes.py')
    with open("attributes.py", "r") as f1:
        with open(pipeline_path, "w") as f2:
            f2.write(f1.read())
            
generate_reference_data()
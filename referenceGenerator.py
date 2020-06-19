import requests
from pprint import pprint
import pandas as pd
import json
def write_time_column(data):
    data["title"].append("Year")
    data["name"].append("year")
    data["component_attachment"].append("qb:dimension")
    data["property_template"].append("http://purl.org/linked-data/sdmx/2009/dimension#refPeriod")
    data["value_template"].append("http://reference.data.gov.uk/id/year/{year}")
    data["datatype"].append("string")
    data["value_transformation"].append("")
    data["regex"].append("")
    data["range"].append("")
    return data
def write_admin_geography(data):
    data["title"].append("Geography")
    data["name"].append("geography")
    data["component_attachment"].append("qb:dimension")
    data["property_template"].append("http://purl.org/linked-data/sdmx/2009/dimension#refArea")
    data["value_template"].append("http://statistics.data.gov.uk/id/statistical-geography/{geography}")
    data["datatype"].append("string")
    data["value_transformation"].append("")
    data["regex"].append("[A-Z][0-9]{8}")
    data["range"].append("")
    return data
# TODO - these should be automatically included in the new columns.csv's
# code lists that we dont want to convert for...reasons
NON_STANDARD = {
    "calendar-years": {
        "write_column": write_time_column
    },
    "admin-geography": {
        "write_column": write_admin_geography
    }
}
def get_unique_codelist_urls_from_a_dataset(url):
    codelist_list = []
    # Get the dataset info
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError("Failed with status code: " + r.status_code)
    dataset_as_dict = r.json()
    lastest_version_url = dataset_as_dict["links"]["latest_version"]["href"]
    #  Get the lastest version of that dataset info
    r = requests.get(lastest_version_url)
    if r.status_code != 200:
        raise ValueError("Failed with status code: " + r.status_code)
    lastest_version_as_dict = r.json()
    # For each dimension
    for dimension in lastest_version_as_dict["dimensions"]:
        code_list_url = "https://api.beta.ons.gov.uk/v1/code-lists/{}/editions/one-off/codes".format(dimension["id"])
        codelist_list.append(code_list_url)
    return codelist_list
def create_codelist_reference_csv_from_codelist_url(url):
    #  Get the lastest version of that dataset info
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError("Failed with status code: " + r.status_code)
    code_list_info = r.json()
    # Get the codelist id
    code_list_id = code_list_info["items"][0]["links"]["code_list"]["href"].split("/")[-1]
    if code_list_id in NON_STANDARD.keys():
        return 
    df_dict = {
        "Label":[],
        "Notation":[],
        "Parent Notation":[],
        "Sort Priority":[]
    }
    for code_list in code_list_info["items"]:
        df_dict["Label"].append(code_list["label"])
        df_dict["Notation"].append(code_list["code"])
        df_dict["Parent Notation"].append("")
        df_dict["Sort Priority"].append("")
    df = pd.DataFrame().from_dict(df_dict)
    df.to_csv("reference/codelists/{}.csv".format(code_list_id), index=False)
def get_list_of_code_list_url_for_list_of_datasets(dataset_url_list):
    all_code_lists = []
    for dataset in dataset_url_list:
        code_list_urls_from_dataset = get_unique_codelist_urls_from_a_dataset(dataset)
    for code_list_url in code_list_urls_from_dataset:
        if code_list_url not in all_code_lists:
            all_code_lists.append(code_list_url)
    return all_code_lists
def populate_codelist_reference_csvs_from_codelist_urls(code_list_urls_from_dataset):
    for cl in code_list_urls_from_dataset:
        create_codelist_reference_csv_from_codelist_url(cl)
def components_csv_from_list_of_code_list_urls(code_list_urls_from_dataset, details):
    columns=["Label", "Description", "Component Type", "Codelist"]
    try:
        df = pd.read_csv("reference/components.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
    except:
        raise
    # add measures and attributes
    data = {
        "Label":[],
        "Description":[],
        "Component Type":[],
        "Codelist":[]
    }
    for measure in details["attributes to add"]["Measure Type"].keys():
        data["Label"].append(measure)
        data["Description"].append("")
        data["Component Type"].append("Measure")
        data["Codelist"].append("")
    attributes_to_add = [x for x in details["attributes to add"].keys() if x != "Measure Type"]
    attributes_to_add = attributes_to_add + details["existing attributes"]
    for attribute in attributes_to_add:
        data["Label"].append(attribute)
        data["Description"].append("")
        data["Component Type"].append("Attribute")
        data["Codelist"].append("")
    for code_list_url in code_list_urls_from_dataset:
        # Get the codelist id
        code_list_id = "cmd " + code_list_url.split("/")[-4]
        # Where non standard handling is required, call it then go to next code list
        if code_list_id in NON_STANDARD.keys():
            continue
        data["Label"].append(code_list_id.replace("-", " "))
        data["Description"].append("")
        data["Component Type"].append("Dimension")
        data["Codelist"].append("http://gss-data.org.uk/def/concept-scheme/"+code_list_id)
    df = pd.concat([df, pd.DataFrame().from_dict(data)])
    df = df.fillna("")
    df = df.drop_duplicates()
    df.to_csv("reference/components.csv", index=False)
def populate_columns_csv_from_list_of_code_list_urls(code_list_urls_from_dataset, details):
    columns=["title", "name", "component_attachment", "property_template", "value_template",
                                   "datatype", "value_transformation", "regex", "range"]
    try:
        df = pd.read_csv("reference/columns.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
    except:
        raise
    # Start with Value and Measure Type column as default (have to have a value definition)
    data = {
        "title":["Value", "Measure Type"],
        "name":["value", "measure_type"],
        "component_attachment":["qb:dimension", "qb:attribute"],
        "property_template":["http://purl.org/linked-data/cube#measureType", ""],
        "value_template":["http://gss-data.org.uk/def/measure/{measure_type}", "http://gss-data.org.uk/def/measure/{measure_type}"],
        "datatype":["number", "string"],
        "value_transformation":["", ""],
        "regex":["", ""],
        "range":["", ""]
    }
    # First, add the measures (so anything from details that goes into the "Measure Type" column)
    # and any attributes identified by our cmd-info.json
    attributes_to_write = []
    for mtype_or_attribute, instructions in details["attributes to add"].items():
        if mtype_or_attribute == "Measure Type":
            for measure_type in instructions.keys():
                data["title"].append("{}".format(measure_type))
                data["name"].append("{}".format(measure_type.lower().replace("-", "-")))
                data["component_attachment"].append("qb:measure")
                data["property_template"].append("")
                data["value_template"].append("")
                data["datatype"].append("string")
                data["value_transformation"].append("")
                data["regex"].append("")
                data["range"].append("")
        else:
            attributes_to_write.append(mtype_or_attribute)
    attributes_to_write = attributes_to_write + details["existing attributes"]
    for attribute in attributes_to_write:
        data["title"].append("{}".format(attribute))
        data["name"].append("{}".format(attribute.lower().replace("-", "-")))
        data["component_attachment"].append("qb:attribute")
        prop = "http://gss-data.org.uk/def/attribute/{}".format(attribute.replace(" ", "-").lower())
        data["property_template"].append(prop)
        data["value_template"].append(prop + "/{" + attribute.lower().replace(" ", "_") + "}")
        data["datatype"].append("string")
        data["value_transformation"].append("")
        data["regex"].append("")
        data["range"].append("")           
    # Then add the dimensions using the codelist urls
    for code_list_url in code_list_urls_from_dataset:
        # Get the codelist id
        code_list_id = "cmd-" + code_list_url.split("/")[-4]
        # Where non standard handling is required, call it then go to next code list
        if code_list_id in NON_STANDARD.keys():
            data = NON_STANDARD[code_list_id]["write_column"](data)
        else:
            data["title"].append(code_list_id.replace("-", " "))
            data["name"].append(code_list_id.replace("-", "_"))
            data["component_attachment"].append("qb:dimension")
            data["property_template"].append("http://gss-data.org.uk/def/dimension/"+code_list_id)
            data["value_template"].append("http://gss-data.org.uk/def/concept/"+code_list_id+"/{"+code_list_id.replace("-", "_")+"}")
            data["datatype"].append("string")
            data["value_transformation"].append("slugize")
            data["regex"].append("")
            data["range"].append("")
    df = pd.concat([df, pd.DataFrame().from_dict(data)])
    df = df.fillna("")
    df = df.drop_duplicates()
    df.to_csv("reference/columns.csv", index=False)
def codelists_metadata_from_list_of_code_lists(code_list_urls_from_dataset):
    tables = []
    for code_list_url in code_list_urls_from_dataset:
        # Get the codelist id
        code_list_id = "cmd " + code_list_url.split("/")[-4]
        # Where non standard handling is required, call it then go to next code list
        if code_list_id in NON_STANDARD.keys():
            continue
        table = {
            "url": "codelists/{}.csv".format(code_list_id.lower()),
            "tableSchema": "https://gss-cogs.github.io/ref_common/codelist-schema.json",
            "rdfs:label": code_list_id.replace("-", " ").lower()
        }
        tables.append(table)
    metadata_dict = {
      "@context": ["http://www.w3.org/ns/csvw", {"@language": "en"}],
      "tables": tables
    }
    with open("reference/codelists-metadata.json" , "w") as f:
        json.dump(metadata_dict, f)
        
def generate_reference_data():
    with open("data.json", "r") as f:
        data = json.load(f)

        for dataset_id, details in data.items():
            url = [dataset_id]
            # Populate /reference/codelists
            code_list_urls_from_dataset = get_list_of_code_list_url_for_list_of_datasets(url)
            populate_codelist_reference_csvs_from_codelist_urls(code_list_urls_from_dataset)
            # Populuate ../reference/columns.csv
            populate_columns_csv_from_list_of_code_list_urls(code_list_urls_from_dataset, details)
            # Populate ../reference/components.csv
            components_csv_from_list_of_code_list_urls(code_list_urls_from_dataset, details)
            # Populate ../reference/codelists-metadata.json
            codelists_metadata_from_list_of_code_lists(code_list_urls_from_dataset)
from gssutils import *
from attributes import Attributes
import json
from pathlib import Path
from cmdScraper import CmdScrape

with open("cmd-info.json", "r") as f:
    data_dict = json.load(f)

scrapers.scraper_list = [('https://api.beta.ons', CmdScrape)]

# TODO use next statement rather than loop
for url, arguments in data_dict.items():
    
    scraper = Scraper(url)
    df = scraper.distribution(latest=True).as_pandas()
    index_number = int(df.columns[0].split('_')[-1])
    columns_to_drop = df.columns[index_number+2::2]
    df = df.drop(columns_to_drop, axis=1)
    attributes_applier = Attributes(arguments["attributes to add"])
    df = attributes_applier.applied_to(df)
    df = df.rename(columns={df.columns[0]:'Value'})

    scraper.dataset.family = arguments['family']

    destinationFolder = Path('out')
    destinationFolder.mkdir(exist_ok=True, parents=True)

    df.to_csv(destinationFolder / 'observations.csv', index=False)

    with open(destinationFolder / 'observations.csv-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())

    schema = CSVWMetadata('https://gss-cogs.github.io/family-cmd/reference/')
    schema.create(destinationFolder / 'observations.csv', destinationFolder / 'observations.csv-schema.json')
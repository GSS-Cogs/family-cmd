# +

from gssutils import *

scraper = Scraper("https://api.beta.ons.gov.uk/v1/datasets/ashe-tables-7-and-8")

scraper

# +

df = scraper.distribution(title="ashe-tables-7-and-8, 2019, version 1").as_pandas()

df[:10]
# + {}

# ashe-statistics	statistics	ashe-sex	sex	ashe-working-pattern	workingpattern	
# ashe-hours-and-earnings	hoursandearnings	ashe-workplace-or-residence	workplaceorresidence

def MeasureTypeFunction(value):
    if value.startswith('paid-hours-worked'):
        return "Paid hours worked"
    else:
        return "Pay GBP"

tidy_data = pd.DataFrame()

tidy_data["Value"] = df["V4_2"]
tidy_data["Marker"] = df["Data Marking"]
tidy_data["CV"] = df["CV"]
tidy_data["Year"] = df["time"]
tidy_data["Geography"] = df["admin-geography"]
tidy_data["ashe statistics"] = df["ashe-statistics"]
tidy_data["ashe sex"] = df["ashe-sex"]
tidy_data["ashe working pattern"] = df["ashe-working-pattern"]
tidy_data["ashe hours and earnings"] = df["ashe-hours-and-earnings"]
tidy_data["ashe workplace or residence"] = df["ashe-workplace-or-residence"]
tidy_data["Measure Type"] = tidy_data["ashe hours and earnings"].apply(MeasureTypeFunction)
tidy_data['Marker'] = tidy_data['Marker'].fillna('not-applicable')

tidy_data[:10]


# +

# Output observations file
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True)
tidy_data.to_csv("out/observations.csv", index=False)

# Trig and metadata
with open(destinationFolder / f'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-cmd/reference/')
csvw.create(destinationFolder / 'observations.csv', destinationFolder / 'observations.csv-schema.json')
# -



# +

from gssutils import *

scrape = Scraper("https://api.beta.ons.gov.uk/v1/datasets/ashe-tables-7-and-8")

scrape

# +

df = scrape.distribution(title="ashe-tables-7-and-8, 2019, version 1").as_pandas()

df[:10]
# -



from gssutils import * 
from pprint import pprint
from dateutil.parser import parse
from gssutils.metadata import *
import logging

def request_json_data(scraper, uri):
    """
    A simple helper to return a dict when given the url of a json endpoint
    """
    r = scraper.session.get(uri)
    if r.status_code != 200:
        raise ValueError("Failed to get url '{}' with status code {}.".format(uri, r.status_code))

    return r.json()

def CmdScrape(scraper, tree):
    """
    This is a scraper intended to use the ONS cmd (customise my data) functionality.
    :param scraper:         the Scraper object
    :param landing_page:    lxml tree
    :return:
    """
    # Stuff that happens when we call the scraper.
    # this is where we go and populate fields etc

    edition_document = request_json_data(scraper, scraper.uri)
    dataset_document = request_json_data(scraper, edition_document['links']['dataset']['href'])

    title = dataset_document["id"] + ', ' + edition_document['edition']
    title = title.replace('-', ' ').title()
    scraper.dataset.title = title
    scraper.dataset.description = dataset_document["description"]

    # publication_document = request_json_data(scraper, dataset_document["publications"][0]["href"]+"/data")
    # scraper.dataset.issued = parse(publication_document["description"]["releaseDate"])

    # Theoretically you can have more than one contact, but I'm just taking the first
    scraper.dataset.contactPoint = "mailto:"+dataset_document["contacts"][0]["email"].strip()

    scraper.dataset.publisher = 'https://www.gov.uk/government/organisations/office-for-national-statistics'
    scraper.dataset.license = "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"

    version_documents = request_json_data(scraper, edition_document["links"]["versions"]["href"])

    for version_document in version_documents["items"]:

        version_name = str(version_document["version"])

        # known issue
        if 'downloads' not in version_document.keys():
            logging.warning("Skipping extraction for version {}, missing download link".format(version_name))
            continue

        this_distribution = Distribution(scraper)

        this_distribution.issued = version_document["release_date"]
        this_distribution.downloadURL = version_document["downloads"]["csv"]["href"]
        this_distribution.mediaType = CSV

        this_distribution.title = scraper.dataset.title + ", version {}".format(version_name)
        if 'csvw' in version_document["downloads"].keys():
            metadata_document = request_json_data(scraper, version_document["downloads"]["csvw"]["href"])
            this_distribution.description = metadata_document['dct:description']
            this_distribution.contactPoint = metadata_document['dcat:contactPoint'][0]['vcard:email']
        else:
            this_distribution.description = scraper.dataset.description
            this_distribution.contactPoint = scraper.dataset.contactPoint

        logging.debug("Created distribution for download '{}'.".format(this_distribution.downloadURL))
        scraper.distributions.append(this_distribution)

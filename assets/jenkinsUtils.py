
import os
import json

from jenkins import Jenkins, JenkinsException
from string import Template
from importlib import resources
from lxml.etree import canonicalize

try:
    from . import templates
except:
    import templates

def update_jenkins(name):

    JENKINS_CREDENTIAL_PATH = os.environ["JENKINS_CREDENTIALS"]
    with open(JENKINS_CREDENTIAL_PATH) as f:
        creds = json.load(f)

    base = "https://ci.floop.org.uk"
    path = [
            "GSS_data",
            "Cmd"
        ]

    server = Jenkins(base, username=creds['username'], password=creds['token'])
    full_job_name = '/'.join(path) + '/' + name

    if server.job_exists(full_job_name):
        print(f"Job already exists for {full_job_name}. Continuing")
        return
    else:
        print(f'Jenkins job {full_job_name} doesn''t exist. Will create.')
        job = None

    job_template = Template(resources.read_text(templates, 'jenkins_job.xml'))
    config_xml = job_template.substitute(github_home="https://github.com/GSS-Cogs/family-cmd",
                                         git_clone_url="https://github.com/GSS-Cogs/family-cmd" + '.git',
                                         dataset_dir=name)
    config_xml = canonicalize(config_xml)

    if job is None:
        print(f'Attempting to create new job {full_job_name}')
        try:
            server.create_job(full_job_name, config_xml)
        except JenkinsException as e:
            raise Exception("Failed to create Jenkins job '{}'.".format(full_job_name)) from e
# family-cmd

Pipeline for CMD->PMD dataset transformations.

## Setup

You'll need to have exported Jenkins credentials exported to run the pipeline builder.

So export `JENKINS_CREDENTIALS` as a path pointing to a json file (outside of a git repo please) where the json consists of:

```json
{
  "username": "<JENKINS_ID>",
  "token": "<JENKINS_TOKEN>"
}
```

To get this information, if you log into the jenkins UI and click your login name (top right of the screen) you'll get to a page that gives you your `JENKINS_ID` (it calls it "Jenkins User ID" but it's the same thing).

If you open the user configure menu (via a drop down on your top right name) you can create a Jenkins token for yourself - copy it into your credentials json.

Once you have the credentials file setup, if you add `export JENKINS_CREDENTIALS=<whevever you're keeping that json>` to your bashrc or zshrc (or bash_profile if that's your thing) then they'll be availible by default. 

## Usage

- Declare all dataset you want to transform via `data.json`.
- Run `python3 build.py` - this will create the relevant files in `/reference` and `/datasets` for those datasets.
- Push changes to git to trigger the transforms via jenkins.


### The data.json

This is principally for defining which columns in the data are attributes and for adding appropriate measures types. Each URL represents a dataset as prsented by CMD, the value dictionary for each is these additional information we need to do the transform.

### Attributes

Some attributes are already declared by the cmd v4_x convention, but we may wish to add to that (eg we may want to add a unit type if one is not already included).

There are two fields to populate for this:
`existing attributes`: these need to be declared so we can map them as the correct RDF component type (so anything you do not declare as an attribute can be declared as a dimension).

`attributes to add`: this holds simple logic for how to post-fix attributes to the data, this can be done in two ways.
- Adding a constant, eg `{"Unit": 1}`. This adds a column of `Unit`with a constant value of 1.

- Conditionally, based on the contents of the the columns: example
```
"Measure Type": {
                "GBP": {
                    "ashe-hours-and-earnings": "pay"
                    },
                "Count": {
                    "ashe-hours-and-earnings": "paid"
            }
```
Is expressing we want to a column of 'Measure Type' and set it to:
- "GBP" when "pay" appears in the column "ashe-hours-and-earnings"
- "Count" when "paid" appears in the column "ashe-hours-and-earnings"
    

### Additional Metadata

This data.json also allows you to pass single high level metadata items in, for example `family` and `theme`.


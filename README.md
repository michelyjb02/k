# JIRA Cumulative Flow Exporter
## Background
Cumulative flow diagrams in JIRA are very useful for tracking quantity of work over time. They can also be useful in csv format. However, JIRA does not have an export feature for cumulative flow diagrams as per [JSWSERVER-11292](https://jira.atlassian.com/browse/JSWSERVER-11292)

## Purpose
The aim of this repository is to export cumulative flow data in csv format

## Requirements
- python3

## Get the data
In order to get the data:
- Go to the cumulative flow diagram page
- Select desired filters
- Open browser devtools (inspect element or equivalent)
- Refresh the page (this is needed so that the filters to appear in the URL)
- In the devtools, open the "Network" tab and look for the `cumulativeflowdiagram.json` document
- Open it in a new tab and save it to disk

## Usage
Once you've cloned this repo and fetched the required data as described above, you can run the `export_cumulative_flow.py` script by supplying the json input file, along with the start and end date of the desired report:

`python export_cumulative_flow.py <FLOW_DATA>.json YYYY-mm-dd YYYY-mm-dd`

This will export a csv file named `<FLOW_DATA>.csv` in the same directory as the input file
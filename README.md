# Telekom Login Robot

A utility to log into a prepaid Telekom account and fetch the current phone number of the account. Exposes a login endpoint as a webservice so that this can be triggered by REST API

Currently used as part of my home automation setup where I pull in stats about my prepaid telekom account and display it on my dashboard

## Usage Instructions

- Install python requirements with `pip install requirements.txt`
- If running as a library, then run `python robot.py --help` to see arguments
- If running as a web service, then run `python server.py`
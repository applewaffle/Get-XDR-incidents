#!/usr/bin/python3

import json
import hashlib
import os
import random
import requests
import smtplib
import string
import time
from email.message import EmailMessage
from datetime import datetime, timezone


# customer_name = "CUSTOMER_NAME"
customer_name = os.environ.get('CUSTOMER_NAME')

# customer_id = "unique ID code goes here"
customer_id = os.environ.get('CUSTOMER_ID')

# reference_ticket = "ticket number field goes here"
reference_ticket = os.environ.get('REFERENCE_TICKET')

# api_key = "itsamysecretkey<---this-is-not-a-real-API-key"
api_key = os.environ.get('API_KEY')

# api_key_id = 0
api_key_id = int(os.environ.get('API_KEY_ID'))

# api_url = "https://api-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.xdr.eu.paloaltonetworks.com/public_api/v1/incidents/get_incidents/"
api_url = os.environ.get('API_URL')

# log_file = customer_name + "_last_incident.log"
log_file = os.environ.get('LOG_FILE')

# last_incident = 1
last_incident = int(os.environ.get('LAST_INCIDENT'))


# Keep track of the last incident
if os.path.isfile(log_file):
    with open(log_file) as file:
        last_incident = int(list(file)[-1])

# Function to generate the payload for the API request
def payload(last_incident):
    payload = {
        "request_data": {
            "filters": [{
                "field": "incident_id_list",
                "operator": "in",
                "value": [str(last_incident)]
            }],
            "search_from": 0,
            "search_to": 100,
            "sort": {
                "field": "creation_time",
                "keyword": "desc"
            }
        }
    }
    return payload

# Function to generate the headers for the API request
def advanced_authentication(api_key_id, api_key):
    nonce = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))
    timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
    auth_key = "%s%s%s" % (api_key, nonce, timestamp)
    auth_key = auth_key.encode("utf-8")
    api_key_hash = hashlib.sha256(auth_key).hexdigest()
    headers = {
        "x-xdr-timestamp": str(timestamp),
        "x-xdr-nonce": nonce,
        "x-xdr-auth-id": str(api_key_id),
        "Authorization": api_key_hash
    }
    return headers

# Polling loop
while True:
    response = requests.post(api_url,
                             headers=advanced_authentication(api_key_id, api_key),
                             json=payload(last_incident))
    if response.status_code == requests.codes.ok:
        data = response.json()
        if "reply" in data:
            if "total_count" in data["reply"] and data["reply"]["total_count"] == 1:
                # We have new incidents
                for incident in data["reply"]["incidents"]:

                    # Print the incident
                    print(incident["incident_id"] + ' ' + str(incident["creation_time"]) + ' ' + incident["description"])

                    # Send the email
                    msg = EmailMessage()
                    msg.set_content('\nIncident number: ' + incident["incident_id"] + '\nIncident description: ' + incident["description"])
                    msg['Subject'] = customer_name + ' XDR: New incident! ' + reference_ticket
                    msg['From'] = 'workaround@testco.net'
                    msg['To'] = 'servicedesk@testco.net'
                    s = smtplib.SMTP('smtp.yoursite.net')
                    s.send_message(msg)
                    s.quit()

                    # Keep track of the last incident
                    last_incident += 1
                    with open(log_file, 'a+') as file:
                        file.write(str(last_incident)+'\n')
            else:
                time.sleep(7)
    time.sleep(3)

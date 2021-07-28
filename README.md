XDR Workaround
A script to retrieve incidents from XDR and send them via e-mail to the ticket list.


The script needs an open reference ticket in order for DARYL to be able to merge the new events into it.


Environment variables have to be created for each client.





Variable
Description




API_KEY
API_KEY


API_KEY_ID
Key number, one customer can have several keys


API_URL
API_URL


CUSTOMER_NAME
Will appear in the email subjet


CUSTOMER_ID
Not used yet


REFERENCE_TICKET
Required by DARYL to merge tickets


LOG_FILE
File to keep a record of the last incident


LAST_INCIDENT
Previous incidents will not be reported.

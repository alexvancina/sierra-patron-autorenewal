#!/usr/bin/env python3

import json
from datetime import datetime, date, timedelta
from calendar import monthrange
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Environment, FileSystemLoader
from Sierra import SierraAPI
import config

# Configure Sierra API client
sierra = SierraAPI(config.API_URL, config.API_KEY, config.API_SECRET)

# Configure SendGrid API client
sg = SendGridAPIClient(config.SENDGRID_API_KEY)

# Set up Jinja
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

year = int(datetime.now().strftime('%Y'))   # Current year as int
month = int(datetime.now().strftime('%m'))   # Current month as int
firstOfMonth = datetime.now().strftime('%m-01-%Y')   # Date of the first of this month
lastOfMonth = date(year, month, monthrange(year,month)[1]).strftime('%m-%d-%Y')   # Date of the last of this month
sixMonthsAgo = date.today() + timedelta(-180)
newExpirationDate = (date.today() + timedelta(365)).strftime('%Y-%m-%d')

# A lists of renewed patrons with and without email addresses will be sent to
# the staff email address provided in config.py
patronsWithEmail = []
patronsWithoutEmail = []

# Query from Create Lists to find patrons expiring this month who have been 
# CIRCATIVE within the last 180 days. The %s placeholders are replaced with  
# actual YYYY-MM-DD dates. 
query = '''
{
  "queries": [
    {
      "target": {
        "record": {
          "type": "patron"
        },
        "id": 43
      },
      "expr": {
        "op": "between",
        "operands": [
          "%s",
          "%s"
        ]
      }
    },
    "and",
    {
      "target": {
        "record": {
          "type": "patron"
        },
        "id": 163
      },
      "expr": {
        "op": "greater_than_or_equal",
        "operands": [
          "%s",
          ""
        ]
      }
    }
  ]
}
''' % (firstOfMonth, lastOfMonth, sixMonthsAgo)

# TODO: Currently limited to 10,000 patron record. Refactor this to loop through larger result sets.
patrons = sierra.post(sierra.apiURL + 'patrons/query', params={'offset': 0, 'limit': 10000}, data=query).json()

if patrons['total'] > 0:
    for patron in patrons['entries']:
        patronData = sierra.get(patron['link'], params={'fields': 'barcodes,expirationDate,emails,addresses'}).json()
        
        patronEmail = ''
        patronAddress = ''
        patronBarcode = patronData['barcodes'][0]

        print('Barcode ending in: ' + patronBarcode[-4:])
        for line in patronData['addresses'][0]['lines']:
            patronAddress = patronAddress + line + '\n'
        patronAddress = patronAddress.strip()
        print('Address:\n' + patronAddress)
        if 'emails' in patronData:
            patronEmail = patronData['emails'][0]
            print('Email:' + patronEmail)
        else:
            print('NO EMAIL ADDRESS')
        print('Current Exp: ' + patronData['expirationDate'])
        print('New Exp: ' + newExpirationDate)

        try:
            print('Attempting to renew patron ' + patronBarcode)
            sierra.put(patron['link'], data='{"expirationDate": "%s"}' % newExpirationDate)
            print('Renewal succeeded')
        except:
            print('Failed to renew patron ' + patronBarcode)

        if 'emails' in patronData:
            patronsWithEmail.append(patronBarcode)
            emailTemplate = env.get_template('renewal-notice.html')
            message = Mail(
                from_email = config.FROM_ADDRESS,
                to_emails = patronEmail,
                subject = 'Your library account has been automatically renewed',
                html_content = emailTemplate.render(barcode=patronBarcode[-4:], 
                                                    expiration=newExpirationDate, 
                                                    address=patronAddress)
            )
            try:
                response = sg.send(message)
                print('Successfully sent renewal notice to: ' + patronEmail)
            except Exception as e:
                print('Failed to send renewal notice to: ' + patronEmail)
        else:
            patronsWithoutEmail.append(patronBarcode)
        
        print('\n')
else:
    print('No expiring patrons found.')

# Email staff a list of patrons without email addresses that were renewed
emailTemplate = env.get_template('staff-report.html')
message = Mail(
    from_email = config.FROM_ADDRESS,
    to_emails = config.STAFF_ADDRESS,
    subject = 'Patron account renewal report',
    html_content = emailTemplate.render(expiration=newExpirationDate, 
                                        patronsWithEmail=patronsWithEmail, 
                                        patronsWithoutEmail=patronsWithoutEmail)
)
try:
    response = sg.send(message)
    print('Successfully staff report to: ' + config.STAFF_ADDRESS)
except Exception as e:
    print('Failed to send staff report to: ' + config.STAFF_ADDRESS)
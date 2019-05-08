# Sierra Patron Account Auto-Renewal

A Python script using the Sierra API to automatically extend the expiration date for patron accounts that have recent circulation activity. Patrons are notified by email and a report containing a list of renewed accounts is emailed to staff.

## How It Works

* The Sierra API is queried for patrons who have an account expiring between the first and last day of the current month *and* who have a CIRCACTIVE date within the last 180 days. 
* These patrons have their expiration date extended by 365 days.
* For patrons with an email address associated with their account, an email is sent notifying them of the renewal.
* A report is emailed to library staff containing a list of all of the renewed patrons and whether or not they were able to be notified by email.

## Getting Started

This script requires a Sierra API key with the Patrons Read and Patron Write permissions and a SendGrid API key for sending email. You will need to rename example.config.py to config.py and edit it to include these API keys, the URL of your Sierra server, the "from" address for email notifications, and a staff email address for recieving renewal reports.

The renewal script is intended to be run once per month on the first day of the month using cron, Windows Task Scheduler, etc.

Jinja2 templates are used to format the email messages and these can be easily modified to include additional instructions for patrons. For example, asking them to contact the library if their address has changed.

## Authors

Alex Vancina - Helen Plum Library

Stephen Wynn - Pickler Memorial Library, Truman State University

## License

This project is licensed under the MIT License.

"""
    Description
    =====================
    Class for sending emails from the Raspberry Pi
    
    References
    =====================
    https://www.bc-robotics.com/tutorials/sending-email-using-python-raspberry-pi/
"""

import smtplib
import json

GMAIL_DETAILS_TXT = '/home/pi/Documents/home_chores_project/email_details.txt'

with open(GMAIL_DETAILS_TXT) as json_file:
    GMAIL_DETAILS = json.load(json_file)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USERNAME = GMAIL_DETAILS['username']
GMAIL_PASSWORD = GMAIL_DETAILS['password']

class Emailer:
    def sendmail(self, recipient, subject, content):
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject,
                   "To :" + recipient, "MIME-Version: 1.0",
                   "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
        
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)

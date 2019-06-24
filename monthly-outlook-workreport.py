import win32com.client
import win32com
import os
import sys
import datetime
import calendar

# https://docs.microsoft.com/en-us/office/vba/api/Outlook.NameSpace
# https://stackoverflow.com/questions/22813814/clearly-documented-reading-of-emails-functionality-with-python-win32com-outlook
# https://docs.microsoft.com/en-us/office/vba/api/outlook.recipient

f = open("emailsummary.txt","w+")

outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")



sentmailbox=outlook.GetDefaultFolder(5)

today = datetime.date.today()

firstdayofthismonth=datetime.date.today().replace(day=1).strftime("%d-%m-%y")
firstdayofnextmonth=(datetime.date.today().replace(day=1) + datetime.timedelta(days=calendar.monthrange(today.year,today.month)[1])).strftime("%d-%m-%y")

messages=sentmailbox.Items.restrict("[SentOn] > '{} 12:00 AM' And [SentOn]  < '{} 12:00 AM'".format(firstdayofthismonth, firstdayofnextmonth))

for message in messages:
    subject = message.Subject

    if (not subject.startswith("Canceled:") and not subject.startswith("Accepted:") and not subject.startswith("Declined:")):
        try:
            recipients = str(message.To).strip();
            sender = str(message.Sender).strip();

            if (sender != recipients and not "@gmail.com" in recipients):           
                senttime = message.SentOn;

                toprint = "To {} at {} with subject: '{}'".format(recipients, senttime, subject)
                
                print(toprint,file=f)
                print(toprint)
        except:
            pass;

f.close()

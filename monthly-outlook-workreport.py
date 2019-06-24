import win32com.client
import win32com
from pywintypes import com_error
import os
import sys
import datetime
import calendar
import csv

# Pre-requisite: install pywin32 using 'pip install pywin32'
# Resources:
# https://docs.microsoft.com/en-us/office/vba/api/Outlook.NameSpace
# https://stackoverflow.com/questions/22813814/clearly-documented-reading-of-emails-functionality-with-python-win32com-outlook
# https://docs.microsoft.com/en-us/office/vba/api/outlook.recipient
# https://msdn.microsoft.com/en-us/library/office/ff870566%28v=office.14%29.aspx


today = datetime.date.today()

f = open("emailsummary-{}.csv".format(today.strftime("%b").upper()),"w", newline='')

fieldnames = ['Time', 'Subject', 'Recipients']
writer = csv.DictWriter(f, fieldnames=fieldnames)

outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
sentmailbox=outlook.GetDefaultFolder(5).Items
appointments=outlook.GetDefaultFolder(9).Items 

firstdayofthismonth=today.replace(day=1).strftime("%d-%m-%y")
firstdayofnextmonth=(today.replace(day=1) + datetime.timedelta(days=calendar.monthrange(today.year,today.month)[1])).strftime("%d-%m-%y")

restriction_mail="[SentOn] > '{} 12:00 AM' And [SentOn]  < '{} 12:00 AM'".format(firstdayofthismonth, firstdayofnextmonth);
restriction_meeting="[Start] > '{} 12:00 AM' And [End]  < '{} 12:00 AM'".format(firstdayofthismonth, firstdayofnextmonth);

messages=sentmailbox.restrict(restriction_mail);

writer.writeheader();

for message in messages:
    
    subject = message.Subject;
    print(subject)

    if (not subject.startswith("Canceled:") and not subject.startswith("Accepted:") and not subject.startswith("Declined:")):
        try:
            recipients = str(message.To).strip();
            sender = str(message.Sender).strip();
            senttime = message.SentOn;

            if (sender != recipients and not "@gmail.com" in recipients):
                writer.writerow({'Time': senttime, 'Subject': subject, 'Recipients':recipients });
                
        except com_error as e:           
            writer.writerow({'Time': "<encrypted email>", 'Subject': subject, 'Recipients':"<encrypted email>" });
        except:            
            pass;
        

# TODO: organize data by week (both sent emails and outlook meetings togethere.)
# TODO order calendar items by actual event date

# TODO: keep a list of people for each project to let script determine which email/meeting is for which project
#	Recipient list: LastName FirstName; LastName FirstName
#	Read from projec-data.json 

writer.writeheader();

restrictedItems = appointments.Restrict(restriction_meeting)

for appointmentItem in restrictedItems:
    
    subject = appointmentItem.Subject;
    print(subject);

    if (not subject.startswith("Canceled:") and not subject.startswith("Accepted:") and not subject.startswith("Declined:")):
        try:
            organizer = str(appointmentItem.Organizer).strip();
            starttime = appointmentItem.Start;
            writer.writerow({'Time': starttime, 'Subject': subject, 'Recipients':organizer });
                
        except com_error as e:
            writer.writerow({'Time': "<encrypted email>", 'Subject': subject, 'Recipients':"<encrypted email>" });	
        except:            
            pass;
		  

f.close()

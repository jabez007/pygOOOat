from __future__ import unicode_literals
import win32com.client as winClient
from win32com.client import constants as c

from GuruBackups import SetGuruBackups

OUTLOOK = winClient.gencache.EnsureDispatch("Outlook.Application")


def send_meeting_request(to, subject, location, start_time, end_time, body_text, all_day=False):
    appt = OUTLOOK.CreateItem(c.olAppointmentItem)  # https://msdn.microsoft.com/en-us/library/office/ff869291.aspx
    appt.MeetingStatus = c.olMeeting  # https://msdn.microsoft.com/EN-US/library/office/ff869427.aspx

    # only after setting the MeetingStatus can we add recipients
    appt.Recipients.Add(to)
    appt.Subject = subject
    appt.Location = location

    appt.Start = start_time

    appt.AllDayEvent = all_day

    end_time_list = end_time.split("/")
    end_time_list[-2] = str(int(end_time_list[-2]) + 1)
    appt.End = "/".join(end_time_list)

    appt.Body = body_text
    # appt.Save()
    # appt.Send()
    appt.Display()
    return True


def find_accepted_backups(start, end, me):
    backups = dict()

    ol = winClient.Dispatch("Outlook.Application").GetNamespace("MAPI")
    calendar = ol.GetDefaultFolder(c.olFolderCalendar)
    appointments = calendar.Items
    # https://msdn.microsoft.com/en-us/library/office/gg619398.aspx
    appointments.IncludeRecurrences = True
    appointments.Sort("[Start]")
    # https://msdn.microsoft.com/EN-US/library/office/ff869427.aspx
    restriction = "([MeetingStatus] = 1 OR [MeetingStatus] = 3) AND ([Start] >= '%s' AND [End] <= '%s')" % (start, end)
    restricted_items = appointments.Restrict(restriction)

    for appointment_item in restricted_items:
        if appointment_item.Subject.startswith('Backup'):
            cust = " ".join(appointment_item.Subject.split(" ")[1:])
            for recipient in appointment_item.Recipients:
                # https://msdn.microsoft.com/EN-US/library/office/ff862677.aspx
                if me in recipient.Name:
                    continue
                # '/o=Epic' in recipient.Address
                if recipient.MeetingResponseStatus == c.olResponseAccepted:
                    # https://msdn.microsoft.com/EN-US/library/office/ff868658.aspx
                    backups[cust] = recipient.Name
                    break

    return backups


def send_email(to, cc, message_text):
    to = ";".join(to)
    cc = ";".join(cc)

    msg = OUTLOOK.CreateItem(c.olMailItem)  # https://msdn.microsoft.com/en-us/library/office/ff869291.aspx
    msg.To = to
    msg.CC = cc
    msg.Subject = "OOO Notification"

    # msg.BodyFormat = c.olFormatHTML
    # tmp = msg.Body.split('<BODY>')
    # split by a known HTML tag with only one occurrence then rejoin
    msg.Body = message_text  # '<BODY>'.join([tmp[0],message_text + tmp[1]])

    # msg.Send()
    msg.Display()


def find_available_backup(start, end, backups):
    ol = winClient.Dispatch("Outlook.Application").GetNamespace("MAPI")
    for backup in backups:
        recipient = ol.CreateRecipient(backup)
        if recipient.Resolve():
            # https://msdn.microsoft.com/EN-US/library/office/ff861868.aspx
            shared_calendar = ol.GetSharedDefaultFolder(recipient, c.olFolderCalendar)
            appointments = shared_calendar.Items
            
            start_ary = start.split('-')
            start_ary[2] = str(int(start_ary[2])-1)  # Set the day back 1
            end_ary = end.split('-')
            end_ary[2] = str(int(end_ary[2])+1)  # Set the day ahead 1
            
            leaving = "([Start] > '"+'-'.join(start_ary)+"' AND [Start] < '"+'-'.join(end_ary)+"')"
            returning = "([End] > '"+'-'.join(start_ary)+"' AND [End] < '"+'-'.join(end_ary)+"')"
            gone = "([Start] < '"+'-'.join(start_ary)+"' AND [End] > '"+'-'.join(end_ary)+"')"

            # https://msdn.microsoft.com/EN-US/library/office/ff864234.aspx
            restriction = "[BusyStatus] = 3 AND [IsRecurring] = False AND ("+leaving+" OR "+returning+" OR "+gone+")"
            restricted_items = appointments.Restrict(restriction)
            if restricted_items.Count > 0:
                continue

            return backup


def send_backup_email(to, cust, start, end, me, message_text):
    contacts = ""
    emails = []
    for r in to:
        contacts += ' '.join(r[0].split(" ")[:-1])+", "
        emails += [r[1]]

    # print start, end, cust, me
    cc = find_accepted_backups(start, end, me)
    if cc is None:
        return False
    
    message_text = message_text.replace('[customer contacts]',
                                        contacts[:-2].title())
    message_text = message_text.replace('[start]',
                                        '/'.join([start.split('-')[1], start.split('-')[2]]))
    message_text = message_text.replace('[end]',
                                        '/'.join([end.split('-')[1], end.split('-')[2]]))
    message_text = message_text.replace('[backup]',
                                        cc.split(" ")[0])
    
    msg = OUTLOOK.CreateItem(c.olMailItem)  # https://msdn.microsoft.com/en-us/library/office/ff869291.aspx
    msg.To = ";".join(emails)
    msg.CC = cc
    msg.Subject = "OOO Notification"

    # msg.BodyFormat = c.olFormatHTML
    # tmp = msg.Body.split('<BODY>')
    # split by a known HTML tag with only one occurrence then rejoin
    msg.Body = message_text  # '<BODY>'.join([tmp[0],message_text + tmp[1]])

    # msg.Send()
    msg.Display()
    return True


def set_guru(me, customers, start, end):
    backups = []
    for c in customers:
        b = find_accepted_backups(start, end, me[1])
        backups.append((c, b))

    SetGuruBackups(me[0],
                   backups,
                   '/'.join([start.split('-')[1], start.split('-')[2], start.split('-')[0]]),
                   '/'.join([end.split('-')[1], end.split('-')[2], end.split('-')[0]]))

# # # #


if __name__ == "__main__":
    print find_accepted_backups("07-01-2016", "07-05-2016", "Jimmy McCann")

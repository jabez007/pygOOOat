from __future__ import unicode_literals
from Tkinter import *
import calendar
import ttkcalendar
import tkMessageBox as box

from random import randint
from datetime import timedelta
import operator

from PasswordPrompt import PasswordDialog
from DXOname2SLG import DXO2SLG
from Me import Me
from InternalWebsite import *
from Outlook import *


class pygOOOat(Frame):

    def __init__(self, parent):
        Frame.__init__(self,
                       parent,
                       background="white")
        self.parent = parent
        
        self.user = None
        self.password = None
        
        while self.password is None:
            self.wait_window(PasswordDialog(self))
        
        self.me = Me(self.password)

        self.backups = dict()  # {customer_name: [backup_ts1, backup_ts2]}
        self.get_backups("/".join(str(elm) for elm in self.me.events_outages[0][1]),
                         "/".join(str(elm) for elm in self.me.events_outages[0][2]))

        self.customer_listbox = None
        self.backup_listbox = None

        self.start_cal = None
        self.start_tod = StringVar()

        self.end_tod = StringVar()
        self.end_cal = None

        self.email_message_text = ""
        self.calendar_message_text = ""

        self.init_ui()

        self.password = None

    def get_backups(self, start, end):
        self.get_available(start,
                           end)

        for name, cust in self.me.customers.iteritems():
            for ts in cust.ts[self.me.team]['Secondary']:
                if ts is not None:
                    self.add_to_backups(name,
                                        ts)

            if "Care Everywhere" in self.me.team:
                top_partners = get_json_response("http://ce-nexus.epic.com/ajax/Get_Top_Partners?slgID=%s" % cust.slg_id,
                                                 self.password)

                if name not in self.backups:
                    self.backups[name] = list()

                for p in top_partners:
                    if p['other_org'] in DXO2SLG.keys():
                        other_org = get_json_response("http://ce-nexus.epic.com/ajax/Get_Org_Info?slgID=%s" % DXO2SLG[p['other_org']],
                                                      self.password)
                        self.add_to_backups(name,
                                            other_org['primary_ts'])

            while not self.backups[name]:
                if len(self.available) == 0:
                    break

                index = randint(0,
                                len(self.available)-1)
                self.add_to_backups(name,
                                    self.available[index])
                self.available.pop(index)

    def add_to_backups(self, org, to_add):
        if to_add == self.me.name:
            return

        if to_add not in self.available:
            return

        for b in self.backups.values():
            if to_add in b:
                return
        
        if org in self.backups.keys():
            self.backups[org].append(to_add)
        else:
            self.backups[org] = [to_add]

    def get_available(self, start, end):
        self.available = get_guru_whos_in(self.password,
                                          self.me.team.replace(" ", "+"),
                                          self.me.role.replace(" ", "+"),
                                          start,
                                          end)

    def init_ui(self):

        self.parent.title("pygOOOat")
        self.pack(fill=BOTH,
                  expand=1)

        '''
        Order of sections in the code matters, otherwise we get everything on the same row
        '''

        # Menu bar
        # # build a Frame to put all the components of this section in
        toolbar = Frame(self,
                        bd=1,
                        relief=RAISED)
        toolbar.pack(side=TOP,
                     fill=X)
        # # Build components and add to Frame
        set_button = Button(toolbar,
                            text="Set Backups in Guru",
                            relief=FLAT,
                            command=self.on_set)
        set_button.pack(side=RIGHT,
                        padx=2,
                        pady=2)
        submit_button = Button(toolbar,
                               text="Send Emails",
                               relief=FLAT,
                               command=self.on_submit)
        submit_button.pack(side=RIGHT,
                           padx=2,
                           pady=2)
        request_button = Button(toolbar,
                                text="Send Calendar Holds",
                                relief=FLAT,
                                command=self.on_request)
        request_button.pack(side=RIGHT,
                            padx=2,
                            pady=2)
        # END Menu Bar

        # List boxes
        listboxes_frame = Frame(self)
        listboxes_frame.pack(side=TOP,
                             expand=True,
                             fill=BOTH)
        # # Customers
        customer_frame = Frame(listboxes_frame)
        customer_frame.pack(side=LEFT,
                            expand=True,
                            fill=BOTH)
        customer_lbl = Label(customer_frame,
                             text="Customers")
        customer_lbl.pack(side=TOP,
                          padx=5,
                          pady=5,
                          expand=True,
                          fill=X)
        self.customer_listbox = Listbox(customer_frame,
                                        selectmode=MULTIPLE,
                                        exportselection=0,  # allow selecting from multiple List boxes
                                        width=30)
        for cust in self.backups:
            self.customer_listbox.insert(END,
                                         cust)
        self.customer_listbox.selection_set(0,
                                            END)  # default all selected
        self.customer_listbox.pack(side=TOP,
                                   padx=5,
                                   pady=5,
                                   expand=True,
                                   fill=Y)
        # # END Customers

        # # Back-ups
        backup_frame = Frame(listboxes_frame)
        backup_frame.pack(side=RIGHT,
                          expand=True,
                          fill=BOTH)
        backup_lbl = Label(backup_frame,
                           text="Back-ups")
        backup_lbl.pack(side=TOP,
                        padx=5,
                        pady=5,
                        expand=True,
                        fill=BOTH)
        self.backup_listbox = Listbox(backup_frame,
                                      selectmode=SINGLE,
                                      exportselection=0,
                                      width=20)
        for cust in self.backups:
            if len(self.backups[cust]) >= 1:
                self.backup_listbox.insert(END,
                                           self.backups[cust][0])
        self.backup_listbox.bind("<Double-Button-1>", self.on_double)
        self.backup_listbox.pack(side=TOP,
                                 padx=5,
                                 pady=5)
        # # END Backups
        # # END List boxes

        # Calendars
        calendar_frame = Frame(self,
                               bd=1,
                               relief=GROOVE)
        calendar_frame.pack(side=TOP,
                            fill=X,
                            expand=1)
        # # Title for the calendars so that users know what to do
        cal_title_frame = Frame(calendar_frame)
        cal_title_frame.pack(side=TOP,
                             fill=X)
        start_cal_title = Label(cal_title_frame,
                                text="\tStart Date of Absence\t")
        start_cal_title.pack(side=LEFT,
                             padx=5,
                             pady=5)
        end_cal_title = Label(cal_title_frame,
                              text="\tEnd Date of Absence\t\t\t\t")
        end_cal_title.pack(side=RIGHT,
                           padx=5,
                           pady=5)
        # # Put the Calendars in
        cal_frame = Frame(calendar_frame)
        cal_frame.pack(side=BOTTOM)

        tod = [("AM", "1"),
               ("PM", "2")]  # Time of Day options

        self.start_cal = ttkcalendar.Calendar(cal_frame,
                                              month=self.me.events_outages[0][1][0],
                                              year=self.me.events_outages[0][1][2],
                                              firstweekday=calendar.SUNDAY)
        self.start_cal.set_day(self.me.events_outages[0][1][1])
        self.start_cal.pack(side=LEFT,
                            padx=5,
                            pady=5)
        start_tod_frame = Frame(cal_frame)
        start_tod_frame.pack(side=LEFT)
        self.start_tod.set("1")  # initialize
        for text, mode in tod:
            b = Radiobutton(start_tod_frame,
                            text=text,
                            variable=self.start_tod,
                            value=mode)
            b.pack(side=TOP,
                   padx=5,
                   pady=5)

        end_tod_frame = Frame(cal_frame)
        end_tod_frame.pack(side=RIGHT)
        self.end_tod.set("2")  # initialize
        for text, mode in tod:
            b = Radiobutton(end_tod_frame,
                            text=text,
                            variable=self.end_tod,
                            value=mode)
            b.pack(side=TOP,
                   padx=5,
                   pady=5)
        self.end_cal = ttkcalendar.Calendar(cal_frame,
                                            month=self.me.events_outages[0][2][0],
                                            year=self.me.events_outages[0][2][2],
                                            firstweekday=calendar.SUNDAY)
        self.end_cal.set_day(self.me.events_outages[0][2][1])
        self.end_cal.pack(side=RIGHT,
                          padx=5,
                          pady=5)
        # END Calendars

        # OOO Email Message
        email_message_frame = Frame(self,
                                    bd=1,
                                    relief=GROOVE)
        email_message_frame.pack(side=BOTTOM,
                                 fill=X,
                                 expand=1)
        # # Title for text box
        email_message_title = Label(email_message_frame,
                                    text="OOO Email Message:")
        email_message_title.pack(side=LEFT,
                                 padx=2)
        # # Text box
        self.email_message_text = Text(email_message_frame,
                                       height=11,
                                       width=50)
        self.email_message_text.insert(INSERT,
                                       "Hi,\n\nI'm going to be out of the office from [start] \
through [end]. For any urgent Care Everywhere issues that come up during this \
time, please reach out to [backup] (CC'ed).\n\nThanks,\n\t-%s" % self.me.name)
        self.email_message_text.config(wrap=WORD)
        self.email_message_text.pack(side=RIGHT)
        # END OOO Email Message

        # Meeting Invite Message
        calendar_message_frame = Frame(self,
                                       bd=1,
                                       relief=GROOVE)
        calendar_message_frame.pack(side=BOTTOM,
                                    fill=X,
                                    expand=1)
        # # Title for text box
        calendar_message_title = Label(calendar_message_frame,
                                       text="Calendar Invite Message:")
        calendar_message_title.pack(side=LEFT,
                                    padx=2)
        # # Text box
        self.calendar_message_text = Text(calendar_message_frame,
                                          height=8,
                                          width=50)
        self.calendar_message_text.insert(INSERT,
                                          "Hi [backup],\n\nCould you back up [customer] for me?\
                                          \n\nThanks,\n\t-%s\nsent via pygOOOat" % self.me.name)
        self.calendar_message_text.config(wrap=WORD)
        self.calendar_message_text.pack(side=RIGHT)
        # END Meeting Invite Message

    def on_double(self, event):
        widget = event.widget
        selection = widget.curselection()
        self.backup_listbox.selection_clear(selection[0])

        if self.check_input():
            msg = ""
            for b in self.backups[self.customer_listbox.get(selection[0])]:
                msg += b+"\n"
            box.showinfo("Available Backups for %s" % self.customer_listbox.get(selection[0]),
                         msg)
            #self.wait_window(PasswordDialog(self))

    def on_request(self):
        all_day = True
        date_format = "%m/%d/%Y"
        if self.check_input():
            start_date = self.start_cal.selection.strftime(date_format)
            end_date = self.end_cal.selection.strftime(date_format)

            if start_date == end_date:
                start_tod = self.start_tod.get()
                end_tod = self.end_tod.get()
                if start_tod == end_tod:
                    all_day = False
                    if start_tod == '1':
                        start_date += " 8:00 AM"
                        end_date += " 12:00 PM"
                    else:
                        start_date += " 12:00 PM"
                        end_date += " 5:00 PM"

            message = self.calendar_message_text.get(1.0,
                                                     END)

            selected_customers = [(self.customer_listbox.get(idx), idx) for idx in self.customer_listbox.curselection()]

            for cust, index in selected_customers:
                backup = self.backup_listbox.get(index)

                body = (message.replace('[backup]', backup.split(" ")[0])).replace('[customer]', cust)

                send_meeting_request(backup,
                                     "Backup %s" % cust,
                                     "Your Office",
                                     start_date,
                                     end_date,
                                     body,
                                     all_day)

    def on_submit(self):
        date_format = "%m/%d/%Y"
        if self.check_input():
            start_date = (self.start_cal.selection - timedelta(days=1)).strftime(date_format)
            end_date = (self.end_cal.selection + timedelta(days=1)).strftime(date_format)

            message = self.email_message_text.get(1.0,
                                                  END)
            message = message.replace('[start]', self.start_cal.selection.strftime("%m/%d"))
            message = message.replace('[end]', self.end_cal.selection.strftime("%m/%d"))

            selected_customers = [self.customer_listbox.get(idx) for idx in self.customer_listbox.curselection()]

            backups = find_accepted_backups(start_date,
                                            end_date,
                                            self.me.name)
            for cust in selected_customers:
                to = list()
                for role_k, role_v in self.me.customers[cust].contacts[self.me.team].iteritems():
                    for contact_k, contact_v in role_v.iteritems():
                        if contact_v[None] not in to:
                            to.append(contact_v[None])

                backup = ""
                if cust in backups.keys():
                    if not backups[cust]:
                        box.showinfo("OOO Notification Email",
                                     "No accepted backup found for %s" % cust)
                        continue
                    backup = backups[cust]

                message_text = message.replace('[backup]', backup.split(" ")[0])

                send_email(to,
                           [backup],
                           message_text)

    def on_set(self):
        DATEFMT = ""
        if self.check_input():
            set_guru((self.user, self.me),
                     self.customers.values(),
                     self.start_cal.selection.strftime(DATEFMT),
                     self.end_cal.selection.strftime(DATEFMT))
                    
    def check_input(self):
        #Critical errors
        if self.start_cal.selection is None:
            box.showerror("Input Error",
                          "No Start Date selected.")
            return 0
        if self.end_cal.selection is None:
            box.showerror("Input Error",
                          "No End Date selected.")
            return 0
        if self.end_cal.selection < self.start_cal.selection:
            box.showerror("Input Error",
                          "The end date of your absence is before its start date.")
            return 0
        # Not? critical error
        """
        if not self.contacts:
            box.showerror("Back-end Error",
                          "No customer contacts found.")
        # Initialize
        if not self.available:
            self.available = self.get_available()
            self.addAvailableToBackups()
        """
        return 1


def main():

    root = Tk()
    #root.geometry("250x150+300+300")
    app = pygOOOat(root)
    root.lift()
    root.mainloop()


if __name__ == '__main__':
    main()

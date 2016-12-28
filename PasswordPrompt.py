from Tkinter import *
from InternalWebsite import check_password
import tkMessageBox as box


class PasswordDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self)
        self.parent = parent

        self.user = self.make_entry("TLG ID:", 10)

        self.password = self.make_entry("Password:", 10, show="*")
        self.password.bind("<KeyRelease-Return>", self.store_password_event)
        
        self.button = Button(self)
        self.button["text"] = "Submit"
        self.button["command"] = self.store_password
        self.button.pack()

        self.attributes("-topmost", True)
        self.user.focus_set()

    def make_entry(self, caption, width=None, **options):
        Label(self, text=caption).pack(side=LEFT)
        entry = Entry(self, **options)
        if width:
            entry.config(width=width)
        entry.pack(side=LEFT)
        return entry

    def store_password_event(self, event):
        self.store_password()

    def store_password(self):
        if check_password(self.password.get()):
            self.parent.user = self.user.get()
            self.parent.password = self.password.get()
            self.destroy()
        else:
            box.showerror("Password Error",
                          "The password you supplied\ndid not work for logging in\nto the internal websites")
            self.destroy()


class MainApplication(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.password = None
        self.button = Button(self)
        self.button["text"] = "Password"
        self.button["command"] = self.get_password
        self.button.pack()

    def get_password(self):
        self.wait_window(PasswordDialog(self))

if __name__ == "__main__":
    root = Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()

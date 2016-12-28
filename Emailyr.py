from __future__ import unicode_literals
from Tkinter import *
from bs4 import BeautifulSoup

from PasswordPrompt import PasswordDialog
from InternalWebsite import *
from Render import Render
from Customer import Customer


class Emailyr(Frame):

    def __init__(self, parent):
        Frame.__init__(self,
                       parent,
                       background="white")

        self.parent = parent

        self.user = None
        self.password = None

        while self.password is None:
            self.wait_window(PasswordDialog(self))

        self.all_customers = self._get_all_customers_()

        self.password = None

        print(self.all_customers)

    def _get_all_customers_(self):
        customers = dict()

        soup = self._get_customer_soup_("http://guru/Customers/")

        for row in soup.findAll('tr'):

            row_id = row.get('id')
            if row_id is None:
                continue

            if 'Row' in row_id:
                for col in row.findAll('td'):
                    column_link = col.find('a')
                    if column_link is not None:
                        link_url = column_link.get('href')
                        if "SLG" in link_url:
                            customer_slg = link_url.split("/")[-1]
                            if not self._is_child_customer_(customer_slg):
                                customer_name = column_link.get_text().strip()
                                '''
                                row_customer = Customer(link_url.split("/")[-1],
                                                    self.password)
                                '''
                                customers[customer_slg] = customer_name

        return customers

    def _is_child_customer_(self, slg_id):
        customer_url = "http://guru/Customers/Overview/SLG/%s" % slg_id

        customer_page = Render(customer_url,
                               self.password)
        soup = BeautifulSoup(customer_page.get_html(),
                             "html.parser")
        del customer_page

        div = soup.find('li',
                        attrs={'id': 'gidget_CustomerOverviewDetails'})
        if div is not None:
            for elm in div.findAll('td'):
                if elm is not None and "Parent customer:" in elm.get_text():
                    return True

        return False

    def _get_customer_soup_(self, url):
        page = establish_ntlm(url,
                              self.password)
        soup = BeautifulSoup(page,
                             "html.parser")
        return soup
# # # #


def main():

    root = Tk()
    # root.geometry("250x150+300+300")
    app = Emailyr(root)
    root.lift()
    root.mainloop()


if __name__ == '__main__':
    main()

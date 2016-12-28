from __future__ import unicode_literals
from bs4 import BeautifulSoup
import time

from InternalWebsite import *
from Customer import Customer


class Me(object):

    def __init__(self, password):
        self.password = password

        self.name = ""
        self.team = ""  # application
        self.role = ""  # ex. Technical Services
        self.customers = dict()  # customer_name: Customer(object)
        self.events_outages = list()  # [type, date_range]

        self._get_my_guru_page_()

        self.password = None

    def _get_my_guru_page_(self):
        my_page = establish_ntlm("http://guru/Staff/EmployeeProfile.aspx?id=me",
                                 self.password)
        my_soup = BeautifulSoup(my_page,
                                "html.parser")

        self.name = my_soup.find('span', attrs={'id': 'lblEmployeeName'}).get_text()

        for link in my_soup.find_all('a'):
            link_id = link.get('id')
            try:
                if "TeamRole" in link_id:
                    team_role = [text.strip() for text in link.get_text().split('\n')]
                    self.team = team_role[0]
                    self.role = team_role[1]
            except TypeError:
                continue

        self._get_my_ooo_(my_soup)
        self._get_my_customers_(my_soup)

    def _get_my_ooo_(self, soup):
        ooo_table = soup.find('div',
                              attrs={'id': 'ctl00_ctl00_ctl00_ContentWrapper_ContentWrapper_Content_Content_pnlEvents_phContent'})
        for row in ooo_table.findAll('tr'):
            ooo_row = list()

            row_style = row.get('style')
            if row_style is not None and 'display: none;' in row_style:
                continue

            for col in row.findAll('td'):
                column_text = col.get_text().strip()
                if column_text:
                    ooo_row.append(column_text)

            if ooo_row:
                end_mon, end_mday, end_year = None, None, None
                date_range = ooo_row[1].split('-')
                for index, date in enumerate(date_range):
                    date_time = date.split(" ")
                    if len(date_time) >= 2:
                        date_string = " ".join(date_time[0:2])
                        if index == 0:
                            start_mon, start_mday, start_year = self._split_date_(date_string.strip())
                        elif index == 1:
                            try:
                                end_mon, end_mday, end_year = self._split_date_(date_string.strip())
                            except ValueError:
                                end_mon, end_mday, end_year = None, None, None
                if not any(end for end in [end_mon, end_mday, end_year]):
                    end_mon, end_mday, end_year = start_mon, start_mday, start_year

                ooo_row = [ooo_row[0], (start_mon, start_mday, start_year), (end_mon, end_mday, end_year)]

                self.events_outages.append(ooo_row)
        return

    def _split_date_(self, date_str):
        now_year = int(time.strftime("%Y"))
        now_mon = int(time.strftime("%m"))
        struct_time = time.strptime(date_str.strip(),
                                    "%a %m/%d")
        my_mon, my_mday = struct_time.tm_mon, struct_time.tm_mday
        if my_mon < now_mon:
            my_year = now_year + 1
        else:
            my_year = now_year
        return my_mon, my_mday, my_year

    def _get_my_customers_(self, soup):
        customer = None
        customer_slg = 0
        for link in soup.find_all('a'):
            link_id = link.get('id')
            try:
                if "Customer" in link_id:
                    customer = link.get_text().strip()
                    customer_link = link.get('href')
                    customer_slg = customer_link.split('/')[-1]
                elif "Modifier" in link_id:
                    modifier = link.get_text().strip()
                    if customer is not None and 'Primary' in modifier:
                        self.customers[customer] = Customer(customer_slg,
                                                            self.password)
                        customer = None
                        customer_slg = 0
                elif "Role" in link_id:
                    role = link.get_text().strip()
                elif "Application" in link_id:
                    application = link.get_text().strip()

            except TypeError:
                continue

# # # #


if __name__ == "__main__":
    from getpass import getpass

    psswrd = getpass()
    me = Me(psswrd)

    print(me.name)
    print(me.team)
    print(me.role)
    print(me.events_outages)
    for c in me.customers:
        print(c)
        print(me.customers[c].ts[me.team])
        print(me.customers[c].contacts[me.team])

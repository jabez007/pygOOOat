from __future__ import unicode_literals
from bs4 import BeautifulSoup

from InternalWebsite import *
from AutoVivification import AutoVivification


class Customer(object):

    def __init__(self, slg_id, password):
        self.password = password
        self.slg_id = slg_id

        main_url = 'http://guru/Customers/Overview/SLG/%s' % self.slg_id
        self.name = self._get_customer_name_(main_url)
        self.guru_id = self._get_guru_customer_id_(main_url)

        epic_staff_url = 'http://guru/Customers/Contacts/OverviewEpicContacts?data={"StaticParameter":"","customerID":"%s"}' % self.guru_id
        self.ts = self._get_customer_ts_(epic_staff_url)

        customer_staff_url = 'http://guru/Customers/Contacts/CustomerContacts?data={"StaticParameter":"","customerID":"%s"}' % self.guru_id
        self.contacts = self._get_customer_contacts_(customer_staff_url)

        self.password = None

    def _get_customer_name_(self, url):
        soup = self._get_soup_(url)

        name_header = soup.find('span',
                                attrs={'id': 'Cust_Header_Name'})

        return name_header.get_text().strip()

    def _get_soup_(self, url):
        page = establish_ntlm(url,
                              self.password)
        soup = BeautifulSoup(page,
                             "html.parser")
        return soup

    def _get_customer_ts_(self, url):
        ts = AutoVivification()

        epic_contacts = establish_ntlm(url,
                                       self.password)

        contacts_json = ((epic_contacts.decode('utf8')).split(u'var configuration = ')[1]).split(u'\n')[0]
        parsed = json.loads(contacts_json)
        for contact in parsed['Data']:
            if 'Technical Services' in contact['Role']:
                ts[contact['Product']][contact['Modifier']][contact['FullName']] = contact['PrimaryEmail']

        return ts

    def _get_customer_contacts_(self, url):
        cust_contacts = AutoVivification()

        contacts_page = establish_ntlm(url,
                                       self.password)

        contacts_json = ((contacts_page.decode('utf8')).split(u'var configuration = ')[1]).split(u'\n')[0]
        parsed = json.loads(contacts_json)
        for contact in parsed['Data']:
            cust_contacts[contact['Product']][contact['Role']][contact['FullName']] = contact['PrimaryEmail']

        return cust_contacts

    def _get_guru_customer_id_(self, url):
        customer_page = establish_ntlm(url,
                                       self.password)

        document = ((customer_page.decode('utf8')).split('$("#content").gidgets(')[1]).split('});')[0] + '}'

        dicts = []
        for parsed_json in parse_json_stream(document):
            dicts.append(parsed_json)

        kv = traverse_json(dicts)
        if kv:
            key, value = kv

            for k in key:
                if k == 'CustomerID':
                    return value[key.index(k)]

    def __str___(self):
        return self.name

# # # #


if __name__ == "__main__":
    from getpass import getpass

    password = getpass()
    customer = Customer(842,
                        password)
    print(customer)
    print(customer.ts["Care Everywhere"])
    print(customer.contacts["Care Everywhere"])

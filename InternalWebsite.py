from __future__ import unicode_literals
import urllib2
from ntlm import HTTPNtlmAuthHandler
from getpass import getuser
import json
from lxml import html


def establish_ntlm(url, password):
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None,
                         url,
                         getuser(),
                         password)
    # create the NTLM authentication handler
    auth_ntlm = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
    # create and install the opener
    opener = urllib2.build_opener(auth_ntlm)
    urllib2.install_opener(opener)
    # retrieve the result
    return urllib2.urlopen(url).read()


def check_password(password):
    response = establish_ntlm('http://guru.epic.com',
                              password)

    if '401 - Unauthorized' in response.decode('utf8'):
        return False

    return True


def get_json_response(url, password):
    response = establish_ntlm(url,
                              password)
    data = json.loads(response)
    return data


def parse_json_stream(stream):  # http://stackoverflow.com/questions/26620714/json-loads-valueerror-extra-data-in-python
    decoder = json.JSONDecoder()
    while stream:
        obj, idx = decoder.raw_decode(stream)
        yield obj
        stream = stream[idx:].strip()  


def get_guru_whos_in(password, team, role, start, end):
    url = 'http://guru/Staff/OutOfOffice/WhosIn.aspx?team=%s&role=%s&start=%s+12:00:00+AM&startFullDay=True&end=%s+11:59:59+PM&endFullDay=True&pgNum=all' % \
          (team, role, start, end)
    employee_elm = '//a[@data-hovercard-type="employee"]'
    is_in = []

    whos_in = establish_ntlm(url,
                             password)
    tree = html.fromstring(whos_in)
    for employee in tree.xpath(employee_elm):
        is_in.append(employee.text)
    return is_in


def guru_date_format(date):
    date_ary = date.split('-')
    return '/'.join([date_ary[1], date_ary[2], date_ary[0]])

    
def traverse_json(arry):  # dicts[0]['Groups']['ColumnGroups'][0]['Columns'][1]['Gidgets'][0]['DynamicParameterValues']
    for d in arry:
        if (type(d) is dict) and ('Groups' in d.keys()) and (type(d['Groups']) is dict) and ('ColumnGroups' in d['Groups'].keys()) and (type(d['Groups']['ColumnGroups']) is list):
            for cg in d['Groups']['ColumnGroups']:
                if (type(cg) is dict) and ('Columns' in cg.keys()) and (type(cg['Columns']) is list):
                    for c in cg['Columns']:
                        if (type(c) is dict) and ('Gidgets' in c.keys()) and (type(c['Gidgets']) is list):
                            for g in c['Gidgets']:
                                if (type(g) is dict) and ('DynamicParameterKeys' in g.keys()) and ('DynamicParameterValues' in g.keys()):
                                    if ('CustomerID' in g['DynamicParameterKeys']) and g['DynamicParameterValues']:
                                        return g['DynamicParameterKeys'],g['DynamicParameterValues']

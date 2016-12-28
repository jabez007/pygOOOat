import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep
import win32com.client as comclt

def SetGuruBackups(TLGID, backups, start, end):
    wsh = comclt.Dispatch("WScript.Shell")
    
    browser = webdriver.Chrome(executable_path = os.path.join(os.getcwd(),'chromedriver.exe'))
    delay = 3 # seconds

    browser.get('http://guru/Staff/Backup/ManageBackups?employeeID='+TLGID)
    assert 'Guru' in browser.title

    for c,b in backups:
        if b:
            try:
                WebDriverWait(browser, delay).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@id="btnAdd"]')))
                add = browser.find_element_by_xpath('//input[@id="btnAdd"]')
                add.click()
            except TimeoutException:
                print "Loading page took too much time!"
        
            try:
                WebDriverWait(browser, delay).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@id="txtNewCustomerName"]')))
    
                customer = browser.find_element_by_xpath('//input[@id="txtNewCustomerName"]')
                customer.click()
                customer.send_keys(c)
                sleep(1)
                customer.send_keys(Keys.ENTER)
   
                backup = browser.find_element_by_xpath('//input[@id="txtNewEmployeeName"]')
                backup.click()
                backup.send_keys(b)
                sleep(1)
                backup.send_keys(Keys.ENTER)
    
                temporary = browser.find_element_by_xpath('//input[@id="chkTemporaryBackup"]')
                temporary.click()
                sleep(1)

                wsh.SendKeys("{TAB}"+start+"{TAB}{TAB}"+end)
                sleep(1)

                backup = browser.find_element_by_xpath('//button[@class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" and span="Accept"]') 
                backup.click()
    
            except TimeoutException:
                print "Loading form took too much time!"

            sleep(1)

import json
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import shutil

link = f"https://idx.co.id/primary/ListedCompany/GetCompanyProfiles?emitenType=s&start=0&length=9999"

BIN_DIR = "/tmp/bin"
CURR_BIN_DIR = os.getcwd()

def _init_bin(executable_name):
    if not os.path.exists(BIN_DIR):
        print("Creating bin folder")
        os.makedirs(BIN_DIR)
    print("Copying binaries for " + executable_name + " in /tmp/bin")
    currfile = os.path.join(CURR_BIN_DIR, executable_name)
    newfile = os.path.join(BIN_DIR, executable_name)
    shutil.copy2(currfile, newfile)
    print("Giving new binaries permissions for lambda")
    os.chmod(newfile, 0o775)

def handler(event, context):
	_init_bin("chromedriver")
	
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--window-size=1280x1696')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--hide-scrollbars')
	chrome_options.add_argument('--enable-logging')
	chrome_options.add_argument('--log-level=0')
	chrome_options.add_argument('--v=99')
	chrome_options.add_argument('--single-process')
	chrome_options.add_argument('--ignore-certificate-errors')
	chrome_options.binary_location = "/tmp/bin/headless-chromium"
	http = webdriver.Chrome("/tmp/bin/chromedriver", chrome_options=chrome_options)
	http.get(link)

	try:
		result = http.find_element(By.CSS_SELECTOR, "pre").text
		result = json.loads(result)
	except:
		print("Unknown error")

	stock_code = []
	for data in result["data"]:
	    stock_code.append(data["KodeEmiten"] + ".JK")

import json
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

link = f"https://idx.co.id/primary/ListedCompany/GetCompanyProfiles?emitenType=s&start=0&length=9999"
http = Chrome()
http.get(link)

try:
	result = http.find_element(By.CSS_SELECTOR, "pre").text
	result = json.loads(result)
except:
	print("Unknown error")
    
stock_code = []
for data in result["data"]:
    stock_code.append(data["KodeEmiten"] + ".JK")

import json
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import os
import shutil

link = f"https://idx.co.id/primary/ListedCompany/GetCompanyProfiles?emitenType=s&start=0&length=9999"

BIN_DIR = "/tmp/bin"
CURR_BIN_DIR = os.getcwd()

def _init_bin(executable_name):
    """Initialize binary files for Lambda execution with optimization to avoid redundant copies."""
    if not os.path.exists(BIN_DIR):
        print("Creating bin folder")
        os.makedirs(BIN_DIR)
    
    newfile = os.path.join(BIN_DIR, executable_name)
    
    # Skip copy if file already exists and has correct permissions
    if os.path.exists(newfile):
        print(f"Binary {executable_name} already exists in /tmp/bin, skipping copy")
        return
    
    print("Copying binaries for " + executable_name + " in /tmp/bin")
    currfile = os.path.join(CURR_BIN_DIR, executable_name)
    shutil.copy2(currfile, newfile)
    print("Giving new binaries permissions for lambda")
    os.chmod(newfile, 0o775)

def handler(event, context):
    """Lambda handler to fetch and return stock codes from IDX."""
    driver = None
    try:
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
        
        # Use Service object for modern Selenium syntax
        service = Service(executable_path="/tmp/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(link)

        try:
            result = driver.find_element(By.CSS_SELECTOR, "pre").text
            result = json.loads(result)
        except NoSuchElementException as e:
            print(f"Element not found: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to find data element on page'})
            }
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to parse JSON response'})
            }

        # Use list comprehension for better performance
        stock_code = [data["KodeEmiten"] + ".JK" for data in result["data"]]
        
        return {
            'statusCode': 200,
            'body': json.dumps({'stock_codes': stock_code, 'count': len(stock_code)})
        }
        
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'WebDriver error: {str(e)}'})
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Unexpected error: {str(e)}'})
        }
    finally:
        # Always cleanup the driver to prevent memory leaks
        if driver:
            try:
                driver.quit()
                print("WebDriver closed successfully")
            except Exception as e:
                print(f"Error closing driver: {e}")

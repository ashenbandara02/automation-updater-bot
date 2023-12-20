import os
import re
import time
import mailer
import changelog_creater
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


update_start_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
proceed = False


# returns current date and time
def current_date_time():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


# 03 dec 2023 ----> d/m/y converter
def convert_date_format(input_date):
    date_obj = datetime.strptime(input_date, '%d %B %Y')
    formatted_date = date_obj.strftime('%d/%m/%Y')
    return formatted_date


# regex function to remove version no
def remove_version_number(title):
    pattern = r'\s\d+(\.\d+|-\w+)*(\.\d+)*\.?\s*$'
    title_without_version = re.sub(pattern, '', title).strip()
    if '..' in title_without_version:
        title_without_version = title_without_version.replace('..', '')
        title_without_version = re.sub(pattern, '', title_without_version).strip()

    return title_without_version


# Special Char remover
def remove_special_characters(input_string): # very important func
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\<>?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace("–","-").replace("&", "")

def remove_special_characters2(input_string): # very important func
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\<>?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace("–","-").replace(".", "")

def remove_special_characters3(input_string): # very important func
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\<>?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace("–","-").replace("&", "-")

def remove_special_characters4(input_string): # very important func
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\<>?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace("–","-").replace("&", "-").replace(".", "").replace("#", "")


# Remove special characters, replace spaces with a single hyphen, and convert to lowercase
def format_title(title):
    formatted_title = re.sub(r'[^a-zA-Z0-9\s./&()\-:|#]', '', title)
    formatted_title = formatted_title.replace('.', '-').replace('/', '-').replace('&', '').replace('(', '').replace(')', '')
    formatted_title = re.sub(r'[:#|]+', '-', formatted_title)
    formatted_title = re.sub(r'\s+', '-', formatted_title)
    formatted_title = formatted_title.lower()
    return formatted_title


def format_title_special_case(title):
    if '+' in title:
        title_parts = title.split('+')
        title = title_parts[0].strip()

    return format_title(title)


# Email Sender
def send_report(errors, *args):
    all_errors = "<br>".join("• " + error for error in errors)
    urlset = "<br>".join(url_address for url_address in args[3])
    if len(args) != 0:
        mailer.sendmail(update_start_time, current_date_time(), str(args[0]), str(args[1]), str(args[2]), urlset, all_errors)
    else:
        mailer.sendmail(update_start_time, current_date_time(), '-', '-', '-', '-', all_errors)


# Check period.txt for last update and check site for newest update
last_updated_date = ""
changelog = ""

try:
    changelog_soup = BeautifulSoup(requests.get(changelog).content, 'lxml')
except Exception as e:
    send_report(["• " + e])
    exit()


try:
    new_updated_titles = [convert_date_format((date.find_all("tr"))[0].find("strong").text) for date in changelog_soup.find_all("figure", class_="wp-block-table")]
    new_updated_date = new_updated_titles[0]
    
except:
    send_report(["• Error Finding Change Log !"])
    exit()

with open("period.txt", 'r', encoding='utf-8') as period_checkfile:
    last_updated_date = period_checkfile.readlines()[-1].replace("[ \u2713 ] ", "")

date_obj1 = datetime.strptime(last_updated_date, '%d/%m/%Y') # txt datesaved
date_obj2 = datetime.strptime(new_updated_date, '%d/%m/%Y')

if date_obj1 < date_obj2:
    proceed = True
else:
    exit() # if no updates are available bot exits


alldata = changelog_soup.find_all("figure", class_="wp-block-table")
titles = []
for per_section in alldata:
    section_data = per_section.find_all("tr")
    section_date = convert_date_format(section_data[0].find("strong").text)
    date_object = datetime.strptime(section_date, '%d/%m/%Y')
    if date_obj1 < date_object:
        for row in section_data[1:]:
            the_row = [td.text for td in row.find_all("td")]
            if 'UPDATE' in the_row:
                titles.append(the_row[1])


# List of products to be Updated
urls = [{remove_version_number(title):f'https://wpshop.net/shop/{format_title((remove_version_number(title)))}/'} for title in titles]
changelog = []

# Email Setup
filestobe = len(urls)
filesdone = 0
failed = 0
error_list = []
url_list = []


## Selenium Initiation ##
# Admin-Data - Wpshop
wpshop_url = ''
username = ''
password = ''

# Admin-Data - WordPress
wordpress_url = ''
username_wp = ''
password_wp = ''

# Headers   
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': '*/*'
}

if proceed:
    # Log to Wpshop
    session = requests.Session()
    login_response = session.get(wpshop_url) 
    soup = BeautifulSoup(login_response.text, 'lxml')
    csrf_token = soup.find('input', {'name': 'woocommerce-login-nonce'})['value'] #obtain CSRF token after login using requests

    login_data = {
        'username': username,
        'password': password,
        'rememberme': 'forever', 
        'woocommerce-login-nonce': csrf_token,
        '_wp_http_referer': '/my-account/',
        'login': 'Log in',
    }

    # To Avoid Charset Error
    charset_error = 0
    while True:
        try:
            login_response = session.post("https://wpshop.net/my-account/", data=login_data) # Perform the login request using requests and validation check
            break
        except:
            pass

        if charset_error == 2:
            send_report(["Error With Sending Data login response Charset error !"])
            session.close()
            exit()
        
        charset_error += 1
        

    if 'Dashboard' in login_response.text:
        print("Login to Wpshop successful! [ \u2713 ]")
    else:
        print("Login failed.")
        session.close()
        exit()


    # Login to Wordpress
    # ##### windows
    # options_cd = Options()
    # # options_cd.add_argument("--headless") # headless mode *
    # driver = webdriver.Chrome(options=options_cd) # Initialize the webdriver
    # driver.maximize_window()

    

    ##### Ubuntu 
    options_cd = Options()
    options_cd.add_argument('--headless')
    options_cd.add_argument('--no-sandbox')
    options_cd.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options_cd) # Initialize the webdriver
    driver.maximize_window()


    try:
        driver.get(wordpress_url)
        driver.implicitly_wait(10)
        # loginwithpass = driver.find_element(By.CLASS_NAME, "itsec-pwls-login-fallback__link")
        # driver.execute_script("arguments[0].click();", loginwithpass)

    except Exception as e:
        send_report(["Error with Getting Connection with Wordpress "+e])
        session.close()
        driver.close()
        exit()

    driver.implicitly_wait(10)

    try:
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_login')))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_pass')))
        username_input.clear()
        username_input.send_keys(username_wp)
        password_input.clear()
        password_input.send_keys(password_wp)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "rememberme"))).click() # remember me button to avoid wordpress from logging out

        login_button_locator = (By.ID, 'wp-submit') # Find the login button and click it
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(login_button_locator))
        login_button.click()
    except Exception as e:
        send_report([f'• Error While Loging Into The wordpress {e}'])
        session.close()
        driver.close()
        exit()

    print("Wordpress Login [ \u2713 ]")

    # moving to wpshop with selenium
    driver.get("")
    cookies_dict = session.cookies.get_dict() # We must use the request cookies and transfer them to driver
    for key, value in cookies_dict.items():
        driver.add_cookie({
            'name': key,
            'value': value,
            'domain': 'wpshop.net',  
            'path': '/',  
        })



    def wordpress_updater(url, title, version, p_last_update, file_path):
        """Goes to Woocommerce Bulk Edit and updates"""
        global failed
        global filesdone
        error = ''
        p_version = version.replace(" ", "")

        # goto products page bulk page
        driver.get("")
        # searches for title
        run = True

        check_start = 0
        while True:
            try:
                select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "titleparams"))))
                select.select_by_visible_text("starts with")
                break
            except Exception as e:
                if check_start == 2:
                    error += f"• Error : {url} Selection Contains Error : {e}<br>"
                    failed += 1
                    url_list.append(f"[ ✗ ] {url}")
                    run = False
                    break
                time.sleep(1)
                check_start += 1

        check_A = 0
        if run:
            while True:
                try:
                    # element to be clickable ---> presence 
                    title_search_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'titlevalue')))
                    driver.execute_script("arguments[0].value = arguments[1];", title_search_field, title)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'getproducts'))).click()
                    break
                except Exception as e:
                    if check_A == 2:
                        error += f"• Error : {url} Search : {e}<br>"
                        failed += 1
                        url_list.append(f"[ ✗ ] {url}")
                        run = False
                        break
                    time.sleep(1)
                    check_A += 1

        # get the first found element that matches the title
        check_A2 = 0
        if run:
            while True:
                try:
                    try:
                        # element to be clickable ---> presence 
                        content_grid = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'grid-canvas')))
                        the_product = content_grid.find_element(By.CLASS_NAME, "ui-widget-content")
                        break
                    except Exception as e:
                        selectcontains = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "titleparams"))))
                        selectcontains.select_by_visible_text("contains")
                        
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'getproducts'))).click()
                        # element to be clickable ---> presence 
                        content_grid = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'grid-canvas')))
                        the_product = content_grid.find_element(By.CLASS_NAME, "ui-widget-content")
                        break

                except Exception as e:
                    if check_A2 == 2:
                        error += f"• The Product {title} at {url} was not found inside wptoolsite!! - {e}<br>"
                        failed += 1
                        url_list.append(f"[ ✗ ] {url}")
                        run = False
                        break
                time.sleep(1)
                check_A2 += 1
            
            
        # Add the New Title
        if run:
            check_B = 0
            while True:
                try:
                    the_product_title = the_product.find_element(By.CLASS_NAME, "slick-cell.l2.r2")
                    driver.execute_script("arguments[0].scrollIntoView(true);", the_product_title)
                    driver.execute_script("arguments[0].click();", the_product_title)

                    the_product_title.find_element(By.CLASS_NAME, "editor-text").clear()
                    the_product_title.find_element(By.CLASS_NAME, "editor-text").send_keys(f"{title} v{p_version}")
                    break
                except Exception as e:
                    if check_B == 2:
                        error += f"Error : {url} Adding new title : {e}<br>"
                        failed += 1
                        url_list.append(f"[ ✗ ] {url}")
                        run = False
                        break
                    time.sleep(1)
                    check_B += 1
        
        # changes the version
        oldversion = ""
        if run:
            check_C = 0
            while True:
                try:
                    the_product_version = the_product.find_element(By.CLASS_NAME, "slick-cell.l4.r4")
                    oldversion += the_product_version.text
                    driver.execute_script("arguments[0].click();", the_product_version)

                    the_product_version.find_element(By.CLASS_NAME, "editor-text").clear()
                    the_product_version.find_element(By.CLASS_NAME, "editor-text").send_keys(p_version)
                    break
                except Exception as e:
                    if check_C == 2:
                        error += f"• Error : {url} Adding new Version : {e}<br>"
                        failed += 1
                        url_list.append(f"[ ✗ ] {url}")
                        run = False
                        break
                    time.sleep(1)
                    check_C += 1

        # changes the last update
        if run:
            check_D = 0
            while True:
                try:
                    the_product_update = the_product.find_element(By.CLASS_NAME, "slick-cell.l5.r5")
                    driver.execute_script("arguments[0].click();", the_product_update)

                    the_product_update.find_element(By.CLASS_NAME, "editor-text").clear()
                    the_product_update.find_element(By.CLASS_NAME, "editor-text").send_keys(p_last_update)
                    break
                except Exception as e:
                    if check_D == 2:
                        error += f"• Error : {url} Adding new Updated Date : {e}<br>"
                        failed += 1
                        url_list.append(f"[ ✗ ] {url}")
                        run = False
                        break
                    time.sleep(1)
                    check_D += 1

        ### Changing zip file part
        if run:
            check_E = 0
            while True:
                try:
                    # removes old file
                    the_product_file = the_product.find_element(By.CLASS_NAME, "slick-cell.l3.r3")
                    the_product_file.click()
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "deletefile"))).click()

                    # upload new file
                    addfilebutton = '''
                    var elements = document.querySelectorAll("a.button.insert");
                    for (var i = 0; i < elements.length; i++) {
                        elements[i].click();
                        break;
                    }
                    '''
                    driver.execute_script(addfilebutton)

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "upload_file_button"))).click()

                    # Deleting Previous file
                    search_bar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "media-search-input"))) # element to be clickable ---> presence

                    for i in range(1, 5):
                        if i == 1:
                            try:
                                    # search for the file and wait 
                                oldfile = f"{remove_special_characters(title)}-"
                                driver.execute_script("arguments[0].click();", search_bar)
                                search_bar.send_keys(remove_special_characters(oldfile))
                    

                                    # get the first file and it should be a zip file
                                selecttodel = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, "attachments-wrapper"))).find_element(By.TAG_NAME, "li").find_element(By.TAG_NAME,"div")
                                driver.execute_script("arguments[0].click();", selecttodel) # element to be clickable ---> presence 
                                break
                            except:
                                pass
                        if i == 2:
                            try:
                                    # search for the file and wait 
                                oldfile = f"{remove_special_characters2(title)}-"
                                search_bar.clear()
                                driver.execute_script("arguments[0].click();", search_bar)
                                search_bar.send_keys(remove_special_characters(oldfile))
                    

                                    # get the first file and it should be a zip file
                                selecttodel = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, "attachments-wrapper"))).find_element(By.TAG_NAME, "li").find_element(By.TAG_NAME,"div")
                                driver.execute_script("arguments[0].click();", selecttodel) # element to be clickable ---> presence 
                                break
                            except:
                                pass
                        if i == 3:
                            try:
                                    # search for the file and wait 
                                oldfile = f"{remove_special_characters3(title)}-"
                                search_bar.clear()
                                driver.execute_script("arguments[0].click();", search_bar)
                                search_bar.send_keys(remove_special_characters(oldfile))
                    

                                    # get the first file and it should be a zip file
                                selecttodel = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, "attachments-wrapper"))).find_element(By.TAG_NAME, "li").find_element(By.TAG_NAME,"div")
                                driver.execute_script("arguments[0].click();", selecttodel) # element to be clickable ---> presence 
                                break
                            except:
                                pass
                        if i == 4:
                            try:
                                    # search for the file and wait 
                                oldfile = f"{remove_special_characters4(title)}-" 
                                search_bar.clear()
                                driver.execute_script("arguments[0].click();", search_bar)
                                search_bar.send_keys(remove_special_characters(oldfile))
                    

                                    # get the first file and it should be a zip file
                                selecttodel = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, "attachments-wrapper"))).find_element(By.TAG_NAME, "li").find_element(By.TAG_NAME,"div")
                                driver.execute_script("arguments[0].click();", selecttodel) # element to be clickable ---> presence 
                                break
                            except:
                                pass
                    


                        # press delete and wait some time
                    delete_zip_from_cloud = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "button-link.delete-attachment")))
                    driver.execute_script("arguments[0].click();", delete_zip_from_cloud)
                    time.sleep(2)
                        # Switch to the alert
                    alert = driver.switch_to.alert
                    alert.accept()

                    # Uploading the new file
                    select_upload_section = driver.find_element(By.ID, "menu-item-upload")
                    driver.execute_script("arguments[0].click();", select_upload_section)
                    break

                except Exception as e:
                    if check_E == 2:
                        error += f"• Error : {url} AddingFile/Deleting Old Zip File/Selecting the File : {e}<br>"
                        failed += 1
                        url_list.append(f"[ ✗ ] {url}")
                        run = False
                        break
                
                    time.sleep(1)
                    check_E += 1

        # Run the rest if all the functions are accurately perform else will be moved to next url
        if run:
            input_tag_file_zip = "//input[starts-with(@id,'html5_')]" # Identifies the Upload Field for downloadable (Very Important)
            while True:
                try:
                    driver.find_element(By.XPATH, input_tag_file_zip).send_keys('/home/autoupdatebot/'+file_path)
                    break
                except:
                    pass
                time.sleep(5)
                    
            print("Uploading the New Zip File ...")

            turn = 0
            percentage = []
            uploading = False
            while True: # Check if file is uploaded to goto next step !
                try:
                    try:
                        progress_bar = driver.find_element(By.CLASS_NAME, "media-uploader-status").find_element(By.CLASS_NAME, "media-progress-bar").find_element(By.TAG_NAME, "div")
                        number_str = progress_bar.get_attribute('style').split()[1]
                        number = str(number_str[:-1])
                        percentage.append(number)
                        print(f"Uploaded : {number}")

                        if 'width: 100%' in progress_bar.get_attribute('style'):
                            uploading = True
                            break
                    except: 
                        pass


                    turn += 1
                    if turn >= 10:
                        if percentage[0] == number:
                            error += f"• Error Uploading was Stuck {url}<br>"
                            url_list.append(f"[ ✗ ] {url}")
                            failed += 1
                            break

                        else:
                            pass

                    try:
                        insert_file_button = WebDriverWait(driver, 30).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Insert file URL')]"))
                        )
                        uploading = True
                        break
                    except:
                        pass

                except Exception as e:
                    pass 
                time.sleep(1)  # Wait for 1 second before checking again


            if uploading:
                check_insert_file = 0
                check_insert_function = False

                check_file_name_change = 0

                savefile = False
                while True:
                    try:
                        insert_file_button = WebDriverWait(driver, 300).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Insert file URL')]"))
                        )
                        insert_file_button.click()
                        check_insert_function = True
                        break
                    except Exception as e:
                        if check_insert_file == 2:
                            error += f"• Error : {url} While Clicking the Insert File Url Button : {e}<br>"
                            failed += 1
                            url_list.append(f"[ ✗ ] {url}")
                            break
                        
                        time.sleep(1)
                        check_insert_file += 1

                if check_insert_function:
                    while True:
                        try:
                            filename_script = '''
                                var elements = document.querySelectorAll(".filename");
                                for (var i = 0; i < elements.length; i++) {
                                    // Assuming you want to send keys to the first filename field, you can modify this part
                                    elements[i].value = "Download";
                                    break;
                                }
                            '''
                            driver.execute_script(filename_script)
                            savefile = True
                            break

                        except Exception as e:
                            if check_file_name_change == 2:
                                error += f"• Error : {url} While Changing filename as Download : {e}<br>"
                                failed += 1
                                url_list.append(f"[ ✗ ] {url}")
                                break

                            time.sleep(1)
                            check_file_name_change += 1

                if savefile:
                    print("[ \u2713 ] Zip File Uploaded")
                    
                    # save changes
                    check_F = 0
                    while True:
                        try:
                            save1 = driver.find_element(By.CSS_SELECTOR, 'div[style*="z-index: 10000;"] button:first-child')
                            driver.execute_script("arguments[0].click();", save1)
                            break
                        except Exception as e:
                            if check_F == 2:
                                error += f"• Error : {url} When Saving the file : {e}<br>"
                                failed += 1
                                url_list.append(f"[ ✗ ] {url}")
                                run = False
                                break

                            check_F += 1
                    
                    check_G = 0
                    while True:
                        try:
                            save2 = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "savechanges")))
                            driver.execute_script("arguments[0].click();", save2)
                            break
                        except Exception as e:
                            if check_G == 2:
                                error += f"• Error : {url} When Saving Changes : {e}<br>"
                                failed += 1
                                url_list.append(f"[ ✗ ] {url}")
                                run = False
                                break

                            check_G += 1

                    if run:
                        filesdone += 1
                        url_list.append(f"[ ✓ ] {url}")
                        changelog.append(title+f" v{p_version}")
                        print("[ \u2713 ] UPDATED !")

                    time.sleep(10)
                    os.system("clear")

        # remove the zip file from system
        if not run:
            error += f"• Failed to update {url} Skipped ....<br>"
            error_list.append(error)
        os.remove(f"/home/autoupdatebot/{file_path}")
        

    def scraper_getter(title, url):
        """Function Retrieves product details and get the zip file"""
        global failed
        process = False
        error = ''

        check = 1
        while check < 4:
            time.sleep(2)
            # Scraping the Product Info 
            try:
                element = requests.get(url, headers=headers)
            except:
                element = ''
                
            try:
                response_code = element.status_code
            except:
                response_code = ''

            if response_code == 200:
                parsed_element = BeautifulSoup(element.content, 'lxml')

                try:
                    product_details_div = parsed_element.find('div', class_='woocommerce-product-details__short-description')
                except AttributeError as e:
                    if check < 2:
                        error += f"• Error When getting product details : {title} : {e}<br>"


                p_version = ''
                p_last_update = ''
                try:
                    # p_version = product_details_div.find_all('li')[-3].text.split(":")[1]
                    li_tags = product_details_div.find_all('li')

                    for li in li_tags:
                        text = li.get_text(strip=True)
                        if text.startswith("Product Version"):
                            p_version = text.split(":")[1].strip()
                        elif text.startswith("Product Last Updated"):
                            p_last_update = text.split(":")[1].strip()
                except:
                    p_version = ''
                    p_last_update = ''
                    if check < 2:
                        error += f"• Error While Obtaining Product Version : {title}<br>"

                # try:
                #     p_last_update = product_details_div.find_all('li')[-2].text.split(":")[1]
                # except:
                #     p_last_update = ''
                #     if check < 2:
                #         error += f"• Error While Obtaining Product Last Update : {title}<br>"

                if p_version != '' and p_last_update != '':
                    check2 = 1
                    while check2 < 4:
                        driver.get(url)
                        time.sleep(5)
                        # goto the url
                        try:
                            element2 = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.yith-wcmbs-product-download-box__downloads a.yith-wcmbs-download-button'))
                            )
                            zip_check = "K" 
                        except:
                            zip_check = "X"

                        # download the urls new zip file
                        if zip_check == "K":
                            zip_file = element2.get_attribute('href')
                            print("Files to Update: "+str(filestobe) + " | Files Updated : "+ str(filesdone))
                            print(f"[ \u2713 ] Fetch -> {title}")
                            get_file = session.get(zip_file)
                            if get_file.status_code == 200:
                                file_path = f"products/{remove_special_characters(title)}_{remove_special_characters(p_version)}_wptoolmart.zip"
                                # save the zip file
                                with open(file_path, 'wb') as content_file:
                                    content_file.write(get_file.content)
                                print("[ \u2713 ] Version/ Last Date Updated Retrived !")
                                print("[ \u2713 ] Zip File Download !")
                        
                                process = True
                                # move to the next func
                                wordpress_updater(url, title, p_version, p_last_update, file_path)
                                break
                        else:
                            if check2 == 3:
                                error += f"• Error Searching for Download Button {title}<br>"
                                process = False
                            check2 += 1
                    break
                else:
                    check += 1
            else:
                if check == 3:
                    error += f"Error Getting Response : {str(element.status_code)}<br>"
                
                if check < 3:
                    try:
                        # driver.get("https://wpshop.net/my-account/")
                        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "orig"))).send_keys(title)
                        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "promagnifier"))).click() ################################### bug 404
                        # time.sleep(10)
                        # the_product = driver.find_element(By.XPATH, "//div[starts-with(@id,'asp-res-')]").find_element(By.CLASS_NAME, "asp_res_url")
                        # url = the_product.get_attribute('href')

                        url = f"https://wpshop.net/shop/{format_title_special_case(title)}/"
                    except Exception as e:
                        pass

                check += 1

        if process == False:
            error += f"• Failed to update {title} Skipped ....<br>"
            url_list.append(f"[ ✗ ] {url}")
            error_list.append(error)
            failed += 1


for product in urls:
    for title, url in product.items():
        scraper_getter(title, url)

# scraper_getter("Electro Electronics Store WooCommerce Theme", "https://wpshop.net/shop/ocommamdmsadms")

with open("period.txt", 'a', encoding="utf-8") as period_adder:
    period_adder.write("\n[ \u2713 ] "+datetime.now().strftime("%d/%m/%Y"))

send_report(error_list, filestobe, filesdone, failed, url_list)
changelog_creater.changelog_activate(changelog, driver, WebDriverWait, EC, By)
driver.close()
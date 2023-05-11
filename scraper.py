import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from credentials import CREDENTIALS
import time

chrome_options = Options()
chrome_options.add_experimental_option('detach', True)
# need to sleep to wait for the Javascript to load
SLEEP_TIME = 2
df = pd.DataFrame()

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

def login():
    driver.get('https://www.linkedin.com/login')

    # fills in username, password, and clicks the login_button
    username = driver.find_element(by=By.ID, value='username')
    username.send_keys(CREDENTIALS['USERNAME'])
    password = driver.find_element(by=By.ID, value='password')
    password.send_keys(CREDENTIALS['PASSWORD'])
    login_button = driver.find_element(by=By.XPATH, value="//button[text()='Sign in']")
    login_button.click()
    time.sleep(SLEEP_TIME)

    # if 2S verification is required
    try:
        # fills in the verification code based on user input and clicks the confirm_button
        verification_input = driver.find_element(by=By.ID, value='input__email_verification_pin')
        verification_code = input('Verification code: ')
        verification_input.send_keys(verification_code)
        time.sleep(SLEEP_TIME)
        confirm_button = driver.find_element(by=By.ID, value='email-pin-submit-button')
        confirm_button.click()
    except:
        pass

    # acts as a buffer; input anything AFTER you successfully login (there are tasks I can't automate)
    input('Continue: ')

def search(company_to_search, role_to_search):
    linkedin_url_header = 'https://www.linkedin.com/search/results/people/'
    role_to_search = '%20'.join(role_to_search.split())
    brown_filter = '%5B%22157343%22%5D'
    search_query = linkedin_url_header + f'?keywords={role_to_search}&schoolFilter={brown_filter}'
    driver.get(search_query)
    time.sleep(SLEEP_TIME)

    # clicks the current_company_button and inputs the company_to_search
    current_company_button = driver.find_element(by=By.XPATH, value="//button[text()='Current company']")
    current_company_button.click()
    current_company_input = driver.find_element(by=By.XPATH, value="//input[@placeholder='Add a company']")
    current_company_input.send_keys(company_to_search)
    time.sleep(SLEEP_TIME)

    # select first entry
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(current_company_input, 0, 50)
    action.click()
    action.perform()
    time.sleep(SLEEP_TIME)

    # show results
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(current_company_input, 250, 350)
    action.click()
    action.perform()
    time.sleep(SLEEP_TIME)

    # grabs all of the urls of the found people
    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')
    url_list = []
    people_list = soup.find_all('div', {'class': 'entity-result__item'})
    for people in people_list:
        a = people.find('a')
        href = a.get('href')
        url_list.append(href)

    return url_list

def scrape_person(company_to_search, url_list_to_search):
    url_list_to_search = [x.partition('?')[0] for x in url_list_to_search]
    name_list = []
    company_list = []
    role_list = []
    url_list = []

    for url in url_list_to_search:
        driver.get(url)
        time.sleep(SLEEP_TIME)
        html = driver.page_source
        soup = BeautifulSoup(html, features='lxml')
        # get the name
        name = soup.find("h1").get_text().strip().replace('\n', '').replace('  ', ' ')

        # get the experience section
        driver.get(url + '/details/experience/')
        time.sleep(SLEEP_TIME)
        html = driver.page_source
        soup = BeautifulSoup(html, features='lxml')
        experience = soup.find('div', {'class': 'pvs-entity pvs-entity--padded pvs-list__item--no-padding-in-columns'})

        # get the company
        if experience.find('span', {'class': 't-14 t-normal'}):
            company = experience.find('span', {'class': 't-14 t-normal'}).get_text()
            company = company[0:int(len(company)//2)].partition(' · ')[0].strip().replace('  ', ' ')

        # get the role
        if experience.find('span', {'class': 'mr1 t-bold'}):
            role = experience.find('span', {'class': 'mr1 t-bold'}).get_text()
        else:
            role = experience.find_all('span', {'class': 'mr1 hoverable-link-text t-bold'})[1].get_text()
        role = role[0:int(len(role)//2)].strip().replace('  ', ' ')

        # account for edge cases
        if 'yrs' in company and 'mos' in company:
            company = company_to_search

        name_list.append(name)
        role_list.append(role)
        company_list.append(company)
        url_list.append(url)
    
    df['name'] = name_list
    df['role'] = role_list
    df['company'] = company_list
    df['url'] = url_list
    df.to_csv('database.csv')

# TODO: change
company_to_search = 'Microsoft'
login()
search_res = search(company_to_search, 'corporate strategy')
scrape_person(company_to_search, search_res)
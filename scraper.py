import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from credentials import CREDENTIALS
import time

chrome_options = Options()
chrome_options.add_experimental_option('detach', True)
SLEEP_TIME = 2
df = pd.DataFrame()

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

def login():
    driver.get('https://www.linkedin.com/login')

    username = driver.find_element(by=By.ID, value='username')
    username.send_keys(CREDENTIALS['USERNAME'])
    password = driver.find_element(by=By.ID, value='password')
    password.send_keys(CREDENTIALS['PASSWORD'])
    login_button = driver.find_element(by=By.XPATH, value="//button[text()='Sign in']")
    login_button.click()
    time.sleep(SLEEP_TIME)

    # if 2S verification is required
    try:
        verify = driver.find_element(by=By.ID, value='input__email_verification_pin')
        code = input('Verification code: ')
        verify.send_keys(code)
        time.sleep(SLEEP_TIME)
        confirm_button = driver.find_element(by=By.ID, value='email-pin-submit-button')
        confirm_button.click()
    except:
        pass

    input('Continue: ')

def search():
    # TODO: fill in
    company = 'Microsoft'
    role = 'corporate strategy'

    linkedin_header = 'https://www.linkedin.com/search/results/people/'
    role = '%20'.join(role.split())
    brown_filter = '%5B%22157343%22%5D'
    search_query = linkedin_header + f'?keywords={role}&schoolFilter={brown_filter}'
    driver.get(search_query)
    time.sleep(SLEEP_TIME)

    current_company_button = driver.find_element(by=By.XPATH, value="//button[text()='Current company']")
    current_company_button.click()
    current_company_input = driver.find_element(by=By.XPATH, value="//input[@placeholder='Add a company']")
    current_company_input.send_keys(company)
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

    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')
    url_list = []
    soup_res = soup.find_all('div', {'class': 'entity-result__item'})
    for res in soup_res:
        a = res.find('a')
        href = a.get('href')
        url_list.append(href)

    return company, url_list

def scrape_person(global_company, res_url_list):
    res_url_list = [x.partition('?')[0] for x in res_url_list]
    url_list = []
    name_list = []
    company_list = []
    role_list = []

    for url in res_url_list:
        driver.get(url)
        time.sleep(SLEEP_TIME)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.find("h1").get_text().strip().replace('\n', '').replace('  ', ' ')

        driver.get(url + '/details/experience/')
        time.sleep(SLEEP_TIME)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        experience = soup.find('div', {'class': 'pvs-entity pvs-entity--padded pvs-list__item--no-padding-in-columns'})

        if experience.find('span', {'class': 'mr1 t-bold'}):
            role = experience.find('span', {'class': 'mr1 t-bold'}).get_text()
        else:
            role = experience.find_all('span', {'class': 'mr1 hoverable-link-text t-bold'})[1].get_text()
        role = role[0:int(len(role)//2)].strip().replace('  ', ' ')

        if experience.find('span', {'class': 't-14 t-normal'}):
            company = experience.find('span', {'class': 't-14 t-normal'}).get_text()
            company = company[0:int(len(company)//2)].partition(' · ')[0].strip().replace('  ', ' ')

        if 'yrs' in company and 'mos' in company:
            company = global_company

        url_list.append(url)
        name_list.append(name)
        company_list.append(company)
        role_list.append(role)
    
    df['url'] = url_list
    df['name'] = name_list
    df['company'] = company_list
    df['role'] = role_list
    df.to_csv('microsoft.csv')

login()
res = search()
scrape_person(res[0], res[1])
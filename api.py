import requests
import json
from dotenv import load_dotenv
import os

def call_API(domain_name, first_name, last_name):
    load_dotenv()
    api_key = os.getenv('API_KEY')

    r = requests.get(f'https://api.hunter.io/v2/email-finder?domain={domain_name}&first_name={first_name}&last_name={last_name}&api_key={api_key}')
    data = json.loads(r.text)
    return data['data']['email']
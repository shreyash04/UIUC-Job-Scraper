import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import concurrent.futures
from airflow.providers.mongo.hooks.mongo import MongoHook


base_url = 'https://secure.osfa.illinois.edu/vjb/'

mongo_hook = MongoHook(mongo_conn_id='mongo_default')
client = mongo_hook.get_conn()
db = client['jobs']  # Database name
collection = db['job_listing']  # Collection name

def scrape_job_details(job_id):
    detail_url = f'{base_url}detail.aspx?type=nonfws&postid={job_id}'
    response = requests.get(detail_url)
    job_details = {}

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if cols:  
                    key = row.find("th").text.strip().replace(":", "") if row.find("th") else "Unknown Key"
                    value = cols[0].text.strip() 
                    job_details[key] = value
    else:
        print(f"Could not retrieve details for job ID {job_id}. Status code: {response.status_code}")
    job_details['job_html'] = str(tables[0])
    return job_details

def process_job_listing(job_td):
    strong_tag = job_td.find('strong')
    if strong_tag:
        strong_text = strong_tag.text.strip()
        job_id, _ = strong_text.split(':', 1) if ':' in strong_text else (strong_text, "Unknown Title")
        
        if not job_id_exists(job_id.strip()):
            job_details = scrape_job_details(job_id.strip())
            job_details['ID'] = job_id.strip() 
            job_details['last_updated'] = datetime.utcnow()
            job_details['root_website'] = "secure.osfa.illinois.edu"
            result = collection.insert_one(job_details)
            return str(result.inserted_id)
    return []

def job_id_exists(job_id):
    return collection.count_documents({'ID': job_id}) > 0

def run_scraping_uiuc_student_aid():
    new_job_ids = [] 
    list_url = f'{base_url}joblist.aspx?listtype=nonfws'
    response = requests.get(list_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        job_listings = soup.find_all('td')

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_job_listing, job_td) for job_td in job_listings]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    new_job_ids.append(result) 
    else:
        print(f"Failed to retrieve job listings. Status code: {response.status_code}")
    print("New or updated job IDs:", new_job_ids)
    return new_job_ids
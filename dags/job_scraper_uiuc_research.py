import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from airflow.providers.mongo.hooks.mongo import MongoHook

mongo_hook = MongoHook(mongo_conn_id='mongo_default')
client = mongo_hook.get_conn()
db = client['jobs']  # Database name
collection = db['job_listing']  # Collection name

base_url = "https://researchpark.illinois.edu/jm-ajax/get_listings/"

headers = {
  'authority': 'researchpark.illinois.edu',
  'accept': '*/*',
  'accept-language': 'en-US,en;q=0.9',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'cookie': 'OptanonAlertBoxClosed=2024-03-01T18:46:26.894Z; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Mar+02+2024+00%3A16%3A26+GMT%2B0530+(India+Standard+Time)&version=6.39.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; _fbp=fb.1.1709318852396.229215456; __cf_bm=a_IAen8AOUTj_rSFfnnZIS8DyaLrtWWV1VR08MYNt0U-1709487440-1.0.1.1-uQRGMVfsFcBVkhX1XWsr3gCoyJrskzK5XcXLnRQN3saoqEgOKpvKLAKPhVANBJj2pQtC.JTVZJF9n2iS9rFReQ; __cf_bm=4__n7uynPTEyzrbySrBiVjdlmtX9tim4Uwgbu3LsH.A-1709490465-1.0.1.1-6GUUTI_MSzg0Zs94POGr9lcLSC9unWE2lZe6Hz9Um7t_DOQpZVo0pIj.BHkudSqz1zVrbmgTmox3jYVUmTYZVg',
  'origin': 'https://researchpark.illinois.edu',
  'referer': 'https://researchpark.illinois.edu/work-here/careers/',
  'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'x-requested-with': 'XMLHttpRequest'
}

payload = "lang=&search_keywords=&search_location=&filter_job_type%5B%5D=full-time&filter_job_type%5B%5D=student-employment&filter_job_type%5B%5D=&per_page=500&orderby=date&featured_first=false&order=DESC&page=1&show_pagination=true&form_data=search_keywords%3D%26filter_job_type%255B%255D%3Dfull-time%26filter_job_type%255B%255D%3Dstudent-employment%26filter_job_type%255B%255D%3D"


def extract_particular_job_data(url, headers):
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        job_description_div = soup.find("div", class_="job_description")

        # if job_description_div:
        #     extracted_data = {}
        #     for title_element in job_description_div.find_all("h4"):
        #         next_p_tag = title_element.find_next_sibling("p")
        #         if next_p_tag:
        #             extracted_data[title_element.text.strip()] = next_p_tag.text.strip()

        #     return json.dumps(extracted_data)
        # else:
        #     return None
        return job_description_div 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def extract_job_data(job_listing):
    title_element = job_listing.find("h3").find("a")
    title = title_element.text.strip()
    job_details_url = title_element["href"]

    company_element = job_listing.find("h3").find_next_sibling("br")
    company = company_element.next_sibling.strip() if company_element else "Not available"

    description_element = job_listing.find("div", class_="description")
    description = description_element.text.strip() if description_element else "Not available"

    posted_on_element = job_listing.find("div", class_="posted-on")
    posted_date = posted_on_element.find("span").text.strip() if posted_on_element else "Not available"


    return {
        "title": title,
        "job_details_url": job_details_url,
        "company": company,
        "description": description,
        "posted_date": posted_date,
        "job_html": str(extract_particular_job_data(job_details_url, headers))
    }

def run_scraping_uiuc_research():
    response = requests.post(base_url, data=payload, headers=headers)
    response.raise_for_status() 

    response_json = json.loads(response.text)
    max_num_pages = response_json["max_num_pages"]

    new_job_ids = []

    for page_num in range(1, max_num_pages + 1):
        data = "lang=&search_keywords=&search_location=&filter_job_type%5B%5D=full-time&filter_job_type%5B%5D=student-employment&filter_job_type%5B%5D=&per_page=500&orderby=date&featured_first=false&order=DESC&page="+str(page_num)+"&show_pagination=true&form_data=search_keywords%3D%26filter_job_type%255B%255D%3Dfull-time%26filter_job_type%255B%255D%3Dstudent-employment%26filter_job_type%255B%255D%3D"

        response = requests.post(base_url, data=data, headers=headers)
        response.raise_for_status()  # Raise an exception for error responses

        page_json = json.loads(response.text)
        page_html = page_json["html"]
        soup = BeautifulSoup(page_html, "lxml")

        page_job_listings = soup.find_all("li", class_="job-listing")
        for job_listing in page_job_listings:
            title_element = job_listing.find("h3").find("a")
            title = title_element.text.strip()

            if collection.find_one({"title": title}) is None:
                extracted_data = extract_job_data(job_listing)
                extracted_data['root_website'] = "researchpark.illinois.edu"
                result = collection.insert_one(extracted_data)
                new_job_ids.append(str(result.inserted_id))
    print("New or updated job IDs:", new_job_ids)
    return new_job_ids

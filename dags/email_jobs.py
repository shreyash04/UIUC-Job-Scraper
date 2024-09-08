# email_jobs.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pymongo import MongoClient
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.models import Variable
from bson.objectid import ObjectId

def fetch_users_and_send_emails(**kwargs):
    mongo_hook = MongoHook(conn_id='mongo_default')
    client = mongo_hook.get_conn()
    ti = kwargs['ti']

    # Fetch SMTP configuration from Airflow Variables
    smtp_host = Variable.get("SMTP_HOST")
    smtp_port = int(Variable.get("SMTP_PORT"))
    smtp_user = Variable.get("SMTP_USER")
    smtp_password = Variable.get("SMTP_PASSWORD")
    db = client['jobs']
    users_collection = db['users']
    job_listing_collection = db['job_listing']

    ti = kwargs['ti']
    job_ids = ti.xcom_pull(task_ids='scrape_uiuc_student_jobs_task')  # Adjust task_id as necessary
    uiuc_job_ids = ti.xcom_pull(task_ids='scrape_uiuc_research_task')  # Adjust task_id as necessary
    job_ids += uiuc_job_ids
    users = users_collection.find({})
    emails = [user['email'] for user in users if 'email' in user]

    print(emails, job_ids, smtp_host, smtp_port, smtp_user, smtp_password)
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    
    for job_id in job_ids:
        job_details = job_listing_collection.find_one({'_id': ObjectId(job_id)})
        if(job_details.get('root_website') is None):
            continue
        
        message = MIMEMultipart()
        title = job_details.get('title')
        if(job_details.get('title') is None):
            title = job_details.get('Job Title')
        subject = f"New Job Listing: {title}"

        message['From'] = smtp_user
        message['To'] = smtp_user
        message['Subject'] = subject
        message['CC'] = ','.join(emails)
        if(job_details.get("job_html") is not None):
            message.attach(MIMEText(job_details.get("job_html"), 'html'))
        else:
            job_details_formatted = '\n'.join([f"{key}: {value}" for key, value in job_details.items() if key != '_id' and key != 'job_html'])
            body = f"Here are the details of the job you might be interested in:\n\n{job_details_formatted}"
            message.attach(MIMEText(body, 'plain'))
        

        server.sendmail(smtp_user, emails, message.as_string())  # Send email to self, CC to all users

    server.quit()
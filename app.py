import boto3
import psycopg2
import hashlib
import json
import os
import datetime
from pprint import pprint

# configuring sqs
# configuring aws - we need dummy aws configurations for boto3 and botocore to work with sqs
QUEUE_URL = "http://localhost:4566/000000000000/login-queue"
AWS_REGION = "us-east-1"

# posstgres config
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# connecting to sqs
sqs = boto3.client('sqs', region_name=AWS_REGION, endpoint_url="http://localhost:4566", aws_access_key_id="dummy", aws_secret_access_key="dummy")

# setting up a postgres connection
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
)
cur = conn.cursor()


# hash function to mask the PII information using sha256
def pii_masking(value):
    return hashlib.sha256(value.encode()).hexdigest()


# receive the message from sqs and process it
# insert the data into postgres database
def input_processing(message):
    data = json.loads(message['Body'])

    # to check if the json body loads in data
    pprint(data)
    

    # collecting json data into variables as required for the postgres table
    # hashing the ip and device_id using the function created before
    user_id = data['user_id']
    device_type = data['device_type']
    masked_ip = pii_masking(data['ip'])
    masked_device_id = pii_masking(data['device_id'])
    locale = data['locale']
    app_version_str = data.get('app_version', '0')
    app_version = int(app_version_str.split('.')[0])
    create_date = datetime.datetime.strptime(data.get("create_date", "1970-01-01"), '%Y-%m-%d').date()
    
    insert_query = """
    INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(insert_query, (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date))
    conn.commit()

def main():
    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10
        )
        
        if 'Messages' in response:
            for message in response['Messages']:
                try:
                    input_processing(message)
                    sqs.delete_message(
                        QueueUrl=QUEUE_URL,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                except KeyError as e:
                    print(f"skip messages if there are missing fields: {e}")
        else:
            print("End of queue.")
            break

if __name__ == "__main__":
    main()

import boto3
import json
from urllib import request, parse
from requests_aws4auth import AWS4Auth
import requests
import logging
logging.basicConfig(level=logging.DEBUG)

key = '<>'
secret= '<>'
awsauth = AWS4Auth(key,secret,'us-east-1','es')
headers = {'Content-Type': 'application/json'}
es_host = 'search-photos-cvzunv7hxyngbl5yg22sbc3xha.us-east-1.es.amazonaws.com'
es_index = 'photos'
es_type = '_doc'


def lambda_handler(event, context):
    # Initialize clients
    s3_client = boto3.client('s3')
    rekognition_client = boto3.client('rekognition')
    
    print('event--> ', event)
    
    # Extract bucket name and object key from the S3 PUT event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    print('bucket name: ',bucket_name)
    print('object_key: ',object_key)
    
    # Detect labels in the image using Rekognition
    rekognition_response = rekognition_client.detect_labels(
        Image={'S3Object': {'Bucket': bucket_name, 'Name': object_key}},
        MaxLabels=10 
    )
    print('rekog-resp: ', rekognition_response)
    detected_labels = [label['Name'] for label in rekognition_response['Labels']]
    
    # Retrieve the S3 metadata
    s3_metadata_response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
    custom_labels = s3_metadata_response.get('Metadata', {}).get('x-amz-meta-customlabels', '[]')
    custom_labels_array = json.loads(custom_labels)
    
    # Combine labels from Rekognition and custom labels from metadata
    all_labels = detected_labels + custom_labels_array
    
    print("labels: ", all_labels)
    
    # Prepare the JSON object for Elasticsearch
    es_document = {
        "objectKey": object_key,
        "bucket": bucket_name,
        "createdTimestamp": s3_metadata_response['LastModified'].strftime("%Y-%m-%dT%H:%M:%S"),
        "labels": all_labels
    }

    url = f'https://{es_host}/{es_index}/{es_type}'  # Adjust if you have a specific document ID

    # Make the POST request to index the document
    response = requests.post(url, json=es_document, auth=awsauth)
    
    print("Index Response: ",response)

    return {
        'statusCode': 200,
        'body': json.dumps(response.json())
    }

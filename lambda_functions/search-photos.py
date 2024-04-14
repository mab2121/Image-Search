import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    # AWS Credentials and Region
    region = 'us-east-1'  # Change this based on your region
    service = 'es'
    credentials = boto3.Session().get_credentials()

    # AWS4Auth instance
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

    # Initialize Lex client
    lex_client = boto3.client('lex-runtime')

    # Extract query from event
    query = event.get('q', '')

    # Post text to Amazon Lex
    lex_response = lex_client.post_text(
        botName='YourBotName',
        botAlias='YourBotAlias',
        userId='userID123',  
        inputText=query
    )

    # Attempt to extract keywords if intent matches
    if lex_response.get('intentName') == 'SearchIntent' and 'slots' in lex_response:
        keywords = ' '.join([v for v in lex_response['slots'].values() if v])
    else:
        keywords = ''

    # If keywords present, search in Elasticsearch
    if keywords:
        es_url = 'https://your-elasticsearch-domain.us-east-1.es.amazonaws.com/photos/_search'  # Modify as necessary
        query = {
            "query": {
                "multi_match": {
                    "query": keywords,
                    "fields": ["description", "tags"]
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        response = requests.get(es_url, auth=awsauth, headers=headers, data=json.dumps(query))
        if response.status_code == 200:
            return {'results': response.json()['hits']['hits']}
        else:
            return {'error': response.text, 'status_code': response.status_code}
    else:
        # Return empty results if no keywords are found
        return {'results': []}


import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key

# Initialize AWS clients
region = 'us-east-1'
lexbot = boto3.client('lexv2-runtime', region_name=region)

key = '<>'
secret= '<>'
# Initialize Elasticsearch authentication
auth = AWS4Auth(key, secret, region, 'es')

# Elasticsearch configuration
host = 'https://search-photos-cvzunv7hxyngbl5yg22sbc3xha.us-east-1.es.amazonaws.com'
index = 'photos'
url = f'{host}/{index}/_search'

def recognize_intent(query_text):
    try:
        lexresponse = lexbot.recognize_text(
            botId='<>',
            botAliasId='<>',
            localeId='en_US',
            sessionId="test",
            text=query_text
        )
        return lexresponse['sessionState']['intent']['slots'].get('PhotoType', {}).get('value', {}).get('originalValue', query_text)
    except Exception as e:
        print(f"Lex bot error: {e}")
        return query_text

def lambda_handler(event, context):
    try:
        query_text = event.get('queryStringParameters', {}).get('q', '')
        print("Received query:", query_text)

        # Recognize intent using Lex
        res_ = recognize_intent(query_text)
        print('Intent recognized:', res_)

        # Prepare search terms
        key_word_list = res_.replace(' and', '').split()
        
        # Initialize response dictionary
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": '*',
                "Access-Control-Allow-Headers": '*',
                "Access-Control-Allow-Methods": '*'
            },
        }
        
        # Construct Elasticsearch query
        query = {
            "query": {
            "bool": {
            "should": [
                        {"match": {"labels": keyword}}
                        for keyword in key_word_list
                    ]
                }
            },
            "size": 10
        }

        r = requests.get(url, auth=auth, json=query)
        print(r)
        if r.status_code == 200:
            # Extract URLs from Elasticsearch response
            final_url_list = []
            posts_list = r.json().get('hits', {}).get('hits', [])
            print(posts_list)
            final_url_list = ['https://s3.amazonaws.com/' + x["_source"]["bucket"] + '/' + x["_source"]["objectKey"] for x in posts_list]

            # Remove duplicate URLs
            final_url_list = list(set(final_url_list))

            # Set response body
            response['body'] = json.dumps(final_url_list)
        else:
            print(f"Elasticsearch request failed: {r.text}")
            response['statusCode'] = 500
            response['body'] = json.dumps({"error": "Elasticsearch request failed"})

    except Exception as e:
        print(f"Error occurred: {e}")
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }

    return response

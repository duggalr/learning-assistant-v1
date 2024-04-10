import json
import os 
import requests
from dotenv import load_dotenv, find_dotenv


if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)


def get_bing_results(query):
    subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
    endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"

    mkt = 'en-US'
    params = { 'q': query, 'mkt': mkt, 'answerCount': 10, 'responseFilter': 'Webpages'}
    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

    response = requests.get(
        endpoint, headers=headers, params=params
    )
    response.raise_for_status()

    search_results = response.json()

    web_results_json = search_results['webPages']
    web_results_values = web_results_json['value']

    final_rv = []
    for wp_di in web_results_values:
        # cached_page_url = wp_di['cachedPageUrl']
        # date_last_crawled = wp_di['dateLastCrawled']
        result_name = wp_di['name']
        result_snippet = wp_di['snippet']
        result_url = wp_di['displayUrl']
        print(f"Name: {result_name} | Url: {result_url}")
        final_rv.append({
            'name': result_name,
            'url': result_url,
            'snippet': result_snippet
        })

    return final_rv


import os
import json
import time
from pprint import pprint
import requests
from dotenv import load_dotenv, find_dotenv


if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)

# Add your Bing Search V7 subscription key and endpoint to your environment variables.
subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"


def search_query(query, q_type, k = 3):
    
    if q_type == 'textbook':
        query = query + ' Textbook'
        save_fn = f"search_results_{query}_textbook.txt"
    elif q_type == 'course_notes':
        query = query + ' Course Notes'
        save_fn = f"search_results_{query}_course_notes.txt"
    else:
        query = query
        save_fn = f"search_results_{query}_general.txt"
    
    
    mkt = 'en-US'
    params = { 'q': query, 'mkt': mkt, 'answerCount': k, 'responseFilter': 'Webpages'}
    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }
    
    response = requests.get(
        endpoint, headers=headers, params=params
    )
    response.raise_for_status()
    search_results = response.json()

    web_results_json = search_results['webPages']
    web_results_values = web_results_json['value']

    search_results_dir = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/search_results_txt_files'
    f = open(os.path.join(search_results_dir, save_fn), 'w')
    for wp_di in web_results_values:
        result_name = wp_di['name']
        result_snippet = wp_di['snippet']
        result_url = wp_di['displayUrl']
        print(f"Name: {result_name} | Url: {result_url}")
        f.write(f"Name: {result_name} | Url: {result_url}")
        f.write('\n')

    f.close()



# TODO: 
    # start with just 10 webpages as is for the course outline
    # now, split the module notes by subtopic and go from there
    # push my V1 usable version in local or prod
        # use it for learning something and iterate from there

# search_query(
#     query = "Exploring Lisp: The Path to Functional Programming" ,
#     q_type = 'textbook',
#     k = 3
# )

# time.sleep(1.2)

# search_query(
#     query = "Exploring Lisp: The Path to Functional Programming" ,
#     q_type = 'course_notes',
#     k = 3
# )

# time.sleep(1.2)

# search_query(
#     query = "Exploring Lisp: The Path to Functional Programming" ,
#     q_type = 'general',
#     k = 3
# )

# # Query term(s) to search for. 
# # query = "functional programming vs object oriented programming"
# # query = 'Introduction to Functional Programming with a Gateway to Lisp'
# query = "Exploring Lisp: The Path to Functional Programming Course Notes"

# # Construct a request
# mkt = 'en-US'
# params = { 'q': query, 'mkt': mkt, 'answerCount': 10, 'responseFilter': 'Webpages'}
# headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

# response = requests.get(
#     endpoint, headers=headers, params=params
# )
# response.raise_for_status()

# # print("JSON Response:")
# search_results = response.json()
# # pprint(search_results)

# web_results_json = search_results['webPages']
# web_results_values = web_results_json['value']
# search_results_dir = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/search_results_txt_files'
# f = open(os.path.join(search_results_dir, f'search_results_{query}.txt'), 'w')
# for wp_di in web_results_values:
#     # cached_page_url = wp_di['cachedPageUrl']
#     # date_last_crawled = wp_di['dateLastCrawled']
#     result_name = wp_di['name']
#     result_snippet = wp_di['snippet']
#     result_url = wp_di['displayUrl']
#     print(f"Name: {result_name} | Url: {result_url}")
#     f.write(f"Name: {result_name} | Url: {result_url}")
#     f.write('\n')

# f.close()

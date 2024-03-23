import os
from dotenv import load_dotenv
load_dotenv()

import psycopg2
import psycopg2.extras
import openai



openai.api_key = os.environ['OPENAI_KEY']

conn = psycopg2.connect(
    host = os.environ['RDS_DB_HOST'],
    port = '5432',
    database = os.environ['RDS_DB_NAME'],
    user = os.environ['RDS_DB_USERNAME'],
    password = os.environ['RDS_DB_PASSWORD']
)
cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

sql = """
SELECT id, code_unique_name, user_code
	FROM public.learning_assistant_usercode
where user_auth_obj_id = 5
order by created_at asc
"""
cur.execute(sql)
user_code_files = cur.fetchall()
# print(user_code_files[0]['id'])
# ex_dict = user_code_files[0]

count = 0
rv = []
for di in user_code_files:

    if count >= 10:
        break

    code_id, user_code = di['id'], di['user_code']
    
    q_prompt = """##Instructions:
Your goal is to extract the concepts the question and code below touched upon.
Only return 3 of the most meaningful concepts you believe the question and code touched upon.
Return your answer in a list format.

##Programming Question + Code:
{user_code}

##Your Answer:
"""
    
    q_prompt = q_prompt.format(
        code_id = code_id,
        user_code = user_code.strip()
    )
    # print(q_prompt)

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]
    response = openai.ChatCompletion.create(
        model = "gpt-4",
        messages = messages_list,
    )
    response_message = response["choices"][0]["message"]['content']

    print(response_message)

    full_st = f"Code-ID: {code_id} | Concepts: {response_message}"

    f = open('q_extracted_concepts_two.txt', 'a')
    f.write(full_st)
    f.write('\n')

    count += 1

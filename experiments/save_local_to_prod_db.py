# import sys
# import os
# import django

# sys.path.append('/Users/rahul/Desktop/code_companion/gpt_learning_assistant/')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'gpt_learning_assistant.settings'
# django.setup()

# from learning_assistant.models import PythonCourseLesson


# li = [
#     'https://player.vimeo.com/video/879178069',
#     'https://player.vimeo.com/video/881236906',
#     'https://player.vimeo.com/video/881261646',
#     'https://player.vimeo.com/video/881263754',
#     'https://player.vimeo.com/video/881270114',
#     'https://player.vimeo.com/video/881272238',
# ]

# py_cl_objects = list(PythonCourseLesson.objects.all().order_by('order_number'))
# # for cl_obj in py_cl_objects:
# for idx in range(0, len(li)):
#     cl_obj = py_cl_objects[idx]
#     cl_obj.lesson_video = li[idx]
#     cl_obj.save()


import os
from dotenv import load_dotenv
load_dotenv()

import psycopg2


# Local database connection parameters
local_db_params = {
    'host': os.environ['LOCAL_DB_HOST'],
    'database': os.environ['LOCAL_DB_NAME'],
    'user': os.environ['LOCAL_DB_HOST_USER'],
    'password': os.environ['LOCAL_DB_PASSWORD'],
}

# Production database connection parameters
prod_db_params = {
    'host': os.environ['RDS_DB_HOST'],
    'database': os.environ['RDS_DB_NAME'],
    'user': os.environ['RDS_DB_USERNAME'],
    'password': os.environ['RDS_DB_PASSWORD'],
}

prod_conn = psycopg2.connect(**prod_db_params)
prod_cursor = prod_conn.cursor()

local_conn = psycopg2.connect(**local_db_params)
local_cursor = local_conn.cursor()

local_select_query = "select * from learning_assistant_pythoncourselesson"
local_cursor.execute(local_select_query)
all_course_values = local_cursor.fetchall()

# print(all_course_values)

# for cs_tup in all_course_values:
#     print(cs_tup)
#     prod_insert_query = "INSERT INTO learning_assistant_pythoncourselesson(id, lesson_title, lesson_description, lesson_video, created_at, order_number) VALUES (%s, %s, %s, %s, %s, %s)"
#     prod_cursor.execute(prod_insert_query, cs_tup)
#     prod_conn.commit()


local_select_query = "select * from learning_assistant_pythonlessonquestion"
local_cursor.execute(local_select_query)
all_course_question_values = local_cursor.fetchall()
# for cq_tup in all_course_question_values:
#     print(cq_tup)
#     prod_insert_query = "INSERT INTO learning_assistant_pythonlessonquestion(id, question_name, question_text, created_at, course_lesson_obj_id, order_number) VALUES (%s, %s, %s, %s, %s, %s)"
#     prod_cursor.execute(prod_insert_query, cq_tup)
#     prod_conn.commit()


local_select_query = "select * from learning_assistant_pythonlessonquestiontestcase"
local_cursor.execute(local_select_query)
all_course_question_test_case_values = local_cursor.fetchall()
# for ctc_tup in all_course_question_test_case_values:
#     print(ctc_tup)
#     prod_insert_query = "INSERT INTO learning_assistant_pythonlessonquestiontestcase(id, input_param, correct_output, lesson_question_obj_id) VALUES (%s, %s, %s, %s)"
#     prod_cursor.execute(prod_insert_query, ctc_tup)
#     prod_conn.commit()


import os
from dotenv import load_dotenv
load_dotenv()

import uuid
import json
import pickle
import datetime
# from pypdf import PdfReader
# import numpy as np
# import openai
from openai import OpenAI
# import pinecone

from dotenv import load_dotenv, find_dotenv

from operator import getitem
from RestrictedPython import compile_restricted
from RestrictedPython import safe_builtins



# openai.api_key = os.environ['OPENAI_KEY']


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']


def main_handle_question(question, programming_problem, student_code, previous_chat_history_st):
    
#     q_prompt = """##Instructions:
# You are a Python Programming Tutor / Teacher.
# Your goal is to help the student achieve their objective, through the problem they present you.
# Some potential problems you may get asked include getting help debugging code below, getting further information or examples on a concept or python library, or the student may ask you to generate questions to help them better understand a concept.
# You MUST NEVER provide a direct answer to the student's problem.
# Instead, your goal is to help guide the student in thr ight direction and provide useful hints, for the questions they ask.
# Do not explicitly provide the answer to the student's question. This will not be helpful to them.
# If you sense the student is discouraged, frustrated, or is just simply looking for the answer, provide useful hints and encouragement.
# The students are new to programming, and your role in helping them become better programmers will be critical. 
# If you need further clarification, please ask the student.
# You will be provided with the student's question, along with their code (although note: the code may not always be relevant as sometimes they might be asking to learn about a concept more generally).
# Again, provide the students with hints and meaningful information on how they can achieve the right answer, but do not give them the answer.

# ##Student Question:
# {question}

# ##Student Code:
# {passages}

# ##Your Answer:
# """

#     q_prompt = """##Instructions:
# You are assisting a group of beginner Python programming students, by being their tutor. Your primary goal is to guide and mentor them, helping them learn Python effectively, but also to become a great individual thinker. Please adhere to these guidelines. See examples below of what not to say, and what to say instead.
# No Direct Answers: Do not provide direct code solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
# Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.

# ##Example Student Question:
# # Find the total product of the list

# list_one = [2,23,523,1231,32,9]
# total_product = 0
# for idx in list_one:
#     total_product = idx * idx

# I'm confused here. I am multiplying idx and setting it to total_product but getting the wrong answer. What is wrong?

# ##Example Bad Answer (Avoid this type of answer):
# You are correct in iterating through the list with the for loop but at the moment, your total_product is incorrectly setup. Try this instead:
# list_one = [2,23,523,1231,32,9]
# total_product = 1
# for idx in list_one:
#     total_product = total_product * idx

# ##Example Good Answer: (this is a good answer because it identifies the mistake the student is making but instead of correcting it for the student, it asks the student a follow-up question as a hint, forcing the student to think on their own)
# You are on the right track. Pay close attention to the operation you are performing in the loop. You're currently multiplying the number with itself, but you want to find the product of all numbers. What operation should you use instead to continuously update 'total_product'?

# ##Previous Chat History with Student:
# {previous_chat_history_st}

# ##Student Question:
# {question}

# ##Student Code:
# {student_code}

# ##Your Answer:
# """

    if programming_problem is None:
        q_prompt = """##Instructions:
    You will be assisting a student who is learning Python, by being their upbeat, encouraging tutor. 
    Your primary goal is to guide and mentor them, helping them learn Python effectively, but also to become a great individual thinker. Please adhere to these guidelines. See examples below of what not to say, and what to say instead.
    No Direct Answers: Do not provide direct code solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
    Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.
    Make sure you consider both correctness and efficiency. You want to help the student write optimal code, that is also correct for their given problem.
    Only ask one question or offer only one suggestion at a time. Wait for the students response before asking a new question or offering a new suggestion.
    Encourage the student. Always motivate the student and provide encourage, even when they are struggling or haven't figured out the solution yet. This will help provide motivation and elicit positive emotion for the student. 

    ##Example Student Question:
    # Find the total product of the list

    list_one = [2,23,523,1231,32,9]
    total_product = 0
    for idx in list_one:
        total_product = idx * idx

    I'm confused here. I am multiplying idx and setting it to total_product but getting the wrong answer. What is wrong?

    ##Example Bad Answer (Avoid this type of answer):
    You are correct in iterating through the list with the for loop but at the moment, your total_product is incorrectly setup. Try this instead:
    list_one = [2,23,523,1231,32,9]
    total_product = 1
    for idx in list_one:
        total_product = total_product * idx

    ##Example Good Answer: (this is a good answer because it identifies the mistake the student is making but instead of correcting it for the student, it asks the student a follow-up question as a hint, forcing the student to think on their own)
    You are on the right track. Pay close attention to the operation you are performing in the loop. You're currently multiplying the number with itself, but you want to find the product of all numbers. What operation should you use instead to continuously update 'total_product'?

    ##Previous Chat History with Student:
    {previous_chat_history_st}

    ##Student Question:
    {question}

    ##Student Code:
    {student_code}

    ##Your Answer:
    """
        question = question.strip()
        student_code = student_code.strip()

        q_prompt = q_prompt.format(
            previous_chat_history_st = previous_chat_history_st,
            question = question,
            student_code = student_code
        )
        
    else:
        q_prompt = """##Instructions:
    You will be assisting a student who is learning Python, by being their upbeat, encouraging tutor. 
    Your primary goal is to guide and mentor them, helping them learn Python effectively, but also to become a great individual thinker. Please adhere to these guidelines. See examples below of what not to say, and what to say instead.
    No Direct Answers: Do not provide direct code solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
    Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.
    Make sure you consider both correctness and efficiency. You want to help the student write optimal code, that is also correct for their given problem.
    Only ask one question or offer only one suggestion at a time. Wait for the students response before asking a new question or offering a new suggestion.
    Encourage the student. Always motivate the student and provide encourage, even when they are struggling or haven't figured out the solution yet. This will help provide motivation and elicit positive emotion for the student. 

    ##Example Student Question:
    # Find the total product of the list

    list_one = [2,23,523,1231,32,9]
    total_product = 0
    for idx in list_one:
        total_product = idx * idx

    I'm confused here. I am multiplying idx and setting it to total_product but getting the wrong answer. What is wrong?

    ##Example Bad Answer (Avoid this type of answer):
    You are correct in iterating through the list with the for loop but at the moment, your total_product is incorrectly setup. Try this instead:
    list_one = [2,23,523,1231,32,9]
    total_product = 1
    for idx in list_one:
        total_product = total_product * idx

    ##Example Good Answer: (this is a good answer because it identifies the mistake the student is making but instead of correcting it for the student, it asks the student a follow-up question as a hint, forcing the student to think on their own)
    You are on the right track. Pay close attention to the operation you are performing in the loop. You're currently multiplying the number with itself, but you want to find the product of all numbers. What operation should you use instead to continuously update 'total_product'?

    ##Previous Chat History with Student:
    {previous_chat_history_st}

    ##Student Question:
    {question}

    #Student Programming Problem:
    {programming_problem}

    ##Student Code:
    {student_code}

    ##Your Answer:
    """
        question = question.strip()
        student_code = student_code.strip()
        programming_problem = programming_problem.strip()

        q_prompt = q_prompt.format(
            previous_chat_history_st = previous_chat_history_st,
            question = question,
            programming_problem = programming_problem,
            student_code = student_code
        )


    di = {"role": "user", "content": q_prompt}
    messages_list = [di]
    response = openai.ChatCompletion.create(
        model = "gpt-4",
        # model = "gpt-3.5-turbo-16k-0613",
        messages = messages_list,
    )
    response_message = response["choices"][0]["message"]['content']

    final_dict_rv = {
        'question': question,
        'q_prompt': q_prompt,
        'response': response_message,
    }
    return final_dict_rv 



def general_tutor_handle_question(question, previous_chat_history_st):

#     q_prompt = """##Instructions:
# You are assisting a group of beginner Python programming students, by being their tutor. Your primary goal is to guide and mentor them, helping them learn Programming (specifically Python) effectively, but also to become a great individual thinker.
# Please adhere to these guidelines. See examplesz below of what to say and what not to say.
# No Direct Answers: Do not provide direct code solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
# Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.

# ##Example Student Question:
# list_one = [2,23,523,1231,32,9]
# total_product = 0
# for idx in list_one:
#     total_product = idx * idx

# I'm confused here. I am multiplying idx and setting it to total_product but getting the wrong answer. What is wrong?

# ##Example Bad Answer (Avoid this type of answer):
# You are correct in iterating through the list with the for loop but at the moment, your total_product is incorrectly setup. Try this instead:
# list_one = [2,23,523,1231,32,9]
# total_product = 1
# for idx in list_one:
#     total_product = total_product * idx

# ##Example Good Answer: (this is a good answer because it identifies the mistake the student is making but instead of correcting it for the student, it asks the student a follow-up question as a hint, forcing the student to think on their own)
# You are on the right track. Pay close attention to the operation you are performing in the loop. You're currently multiplying the number with itself, but you want to find the product of all numbers. What operation should you use instead to continuously update 'total_product'?

# ##Previous Chat History with Student:
# {previous_chat_history_st}

# ##Student Question:
# {question}

# ##Your Answer:
# """

#     q_prompt = """##Instructions:
# You are assisting a group of students, where you will be their tutor. 
# Your primary goal as a tutor is to guide and mentor the students, providing meaningful responses to their questions. 
# Your ultimate goal is to help each student become a great individual thinker.
# Please adhere to these guidelines. See examples below of what to say and what not to say.
# No Direct Answers: Do not provide direct solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
# Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.

# ##Example Student Question:
# list_one = [2,23,523,1231,32,9]
# total_product = 0
# for idx in list_one:
#     total_product = idx * idx

# I'm confused here. I am multiplying idx and setting it to total_product but getting the wrong answer. What is wrong?

# ##Example Bad Answer (Avoid this type of answer):
# You are correct in iterating through the list with the for loop but at the moment, your total_product is incorrectly setup. Try this instead:
# list_one = [2,23,523,1231,32,9]
# total_product = 1
# for idx in list_one:
#     total_product = total_product * idx

# ##Example Good Answer: (this is a good answer because it identifies the mistake the student is making but instead of correcting it for the student, it asks the student a follow-up question as a hint, forcing the student to think on their own)
# You are on the right track. Pay close attention to the operation you are performing in the loop. You're currently multiplying the number with itself, but you want to find the product of all numbers. What operation should you use instead to continuously update 'total_product'?

# ##Previous Chat History with Student:
# {previous_chat_history_st}

# ##Student Question:
# {question}

# ##Your Answer:
# """

#     q_prompt = """##Instructions:
# You will be a personal learning assistant, primarily for students or individuals who are learning new concepts and fields during their own time.
# Be as resourceful to them as possible and provide them with as much guidance and help. Help the individual develop their own syllabus, lesson plan, questions, quizzes, so they can get a deep understanding of their material.

# If you get a question where an individual is asking for the answer to a specific problem they are facing (say, a bug for a computer program they have written), do not provide direct solutions. Instead, in this case, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own.
# Do encourage problem solving. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.

# ##Previous Chat History with Student:
# {previous_chat_history_st}

# ##Student Question:
# {question}

# ##Your Answer:
# """

#     q_prompt = """##Instructions:
# You will be a personal learning assistant, primarily for students or individuals who are learning new concepts and fields during their own time.
# Be as resourceful to them as possible and provide them with as much guidance and help. 
# Help the individual develop their own syllabus, lesson plan, questions, quizzes, so they can get a deep understanding of their material.

# If you get a question where an individual is asking for the answer to a specific problem they are facing (say, a bug for a computer program they have written), do not provide direct solutions. Instead, in this case, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own.
# Here is an example of how to deal with someone directly asking for a solution, to a specific problem:
# # Example:
# # list_one = [2,23,523,1231,32,9]
# # total_product = 0
# # for idx in list_one:
# #     total_product = idx * idx

# # I'm confused here. I am multiplying idx and setting it to total_product but getting the wrong answer. What is wrong?

# # ##Example Bad Answer (Avoid this type of answer):
# # You are correct in iterating through the list with the for loop but at the moment, your total_product is incorrectly setup. Try this instead:
# # list_one = [2,23,523,1231,32,9]
# # total_product = 1
# # for idx in list_one:
# #     total_product = total_product * idx

# # ##Example Good Answer: (this is a good answer because it identifies the mistake the student is making but instead of correcting it for the student, it asks the student a follow-up question as a hint, forcing the student to think on their own)
# # You are on the right track. Pay close attention to the operation you are performing in the loop. You're currently multiplying the number with itself, but you want to find the product of all numbers. What operation should you use instead to continuously update 'total_product'?

# Based on the conversation, try to always ask follow-up questions to the individual. This is a great way to foster a more meaningful conversation, and help the individual gain a more deeper understanding of the material they are trying to learn.

# ##Previous Chat History with Student:
# {previous_chat_history_st}

# ##Student Question:
# {question}

# ##Your Answer:
# """

    q_prompt = """##Instructions:
You will be a personal tutor primarily for students or individuals who are learning new concepts and fields.
Be as resourceful to them as possible and provide them with as much guidance and help. 
Help the individual develop their own syllabus, lesson plan, questions, quizzes, so they can get a deep understanding of their material.

No Direct Answers: Do not provide direct solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.

##Example Student Question:
list_one = [2,23,523,1231,32,9]
total_product = 0
for idx in list_one:
    total_product = idx * idx

I'm confused here. I am multiplying idx and setting it to total_product but getting the wrong answer. What is wrong?

##Example Bad Answer (Avoid this type of answer):
You are correct in iterating through the list with the for loop but at the moment, your total_product is incorrectly setup. Try this instead:
list_one = [2,23,523,1231,32,9]
total_product = 1
for idx in list_one:
    total_product = total_product * idx

##Example Good Answer: (this is a good answer because it identifies the mistake the student is making but instead of correcting it for the student, it asks the student a follow-up question as a hint, forcing the student to think on their own)
You are on the right track. Pay close attention to the operation you are performing in the loop. You're currently multiplying the number with itself, but you want to find the product of all numbers. What operation should you use instead to continuously update 'total_product'?

Based on the conversation, try to always ask meaningful follow-up questions to the individual. 
This is a great way to foster a more engaging conversation, and help the individual gain a more deeper understanding of the material they are trying to learn.
However, if you feel the student has received the information they need and there is no meaningful follow-up question you can think of, please close out the conversation by thanking the student and telling them they can ask any other questions if they wish.

##Previous Chat History with Student:
{previous_chat_history_st}

##Student Question:
{question}

##Your Answer:
"""

    question = question.strip()

    q_prompt = q_prompt.format(
        previous_chat_history_st = previous_chat_history_st,
        question = question,
    )
    print(q_prompt)

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]
    response = openai.ChatCompletion.create(
        model = "gpt-4",
        # model = "gpt-3.5-turbo-16k",
        messages = messages_list,
    )
    response_message = response["choices"][0]["message"]['content']

    final_dict_rv = {
        'question': question,
        'q_prompt': q_prompt,
        'response': response_message,
    }
    return final_dict_rv 



# TODO:
def teacher_question_response(question, previous_chat_history_st):
    t_prompt = """##Instructions:
You are assisting a teacher, who is currently teaching an introductory programming class their students.
Your primary goal is to help the teacher maximize the understanding for each of their students.
The teacher will have conversations with you, asking for help in generating lesson plans, questions, new ways of explaining concepts, or for administrative help.
Please provide all the help needed, along with additional suggestions you feel could be valuable for the teacher, so they can help their students learn in an optimal manner.

##Previous Chat History with Student:
{previous_chat_history_st}

##Student Question:
{question}

##Your Answer:
"""

    question = question.strip()

    t_prompt = t_prompt.format(
        previous_chat_history_st = previous_chat_history_st,
        question = question,
    )
    print(t_prompt)

    di = {"role": "user", "content": t_prompt}
    messages_list = [di]
    response = openai.ChatCompletion.create(
        # model = "gpt-4",        
        model = "gpt-3.5-turbo-16k",
        # model = "gpt-4-0613",
        messages = messages_list,
    )
    response_message = response["choices"][0]["message"]['content']

    final_dict_rv = {
        'question': question,
        'q_prompt': t_prompt,
        'response': response_message,
    }
    return final_dict_rv 




def extract_text_from_pdf(pdf_fp):
    reader = PdfReader(pdf_fp)
    number_of_pages = len(reader.pages)
    print(f"Number Pages Found: {number_of_pages}")

    rv = []
    for pg in reader.pages:
        txt = pg.extract_text().strip()
        rv.append(txt)
    return rv






## Pinecone Functions ##

def pinecone_handle_question(question, previous_chat_history_st, pc_namespace, k=3):
    
    q_prompt = """#Instructions:
You will be a personal tutor primarily for students or individuals who are learning new concepts and fields.
Be as resourceful to them as possible and provide them with as much guidance and help. 
Help the individual develop their own syllabus, lesson plan, questions, quizzes, so they can get a deep understanding of their material.

No Direct Answers: Do not provide direct solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.

##Example Student Question:
list_one = [2,23,523,1231,32,9]
total_product = 0
for idx in list_one:
    total_product = idx * idx

I'm confused here. I am multiplying idx and setting it to total_product but getting the wrong answer. What is wrong?

##Example Bad Answer (Avoid this type of answer):
You are correct in iterating through the list with the for loop but at the moment, your total_product is incorrectly setup. Try this instead:
list_one = [2,23,523,1231,32,9]
total_product = 1
for idx in list_one:
    total_product = total_product * idx

##Example Good Answer: (this is a good answer because it identifies the mistake the student is making but instead of correcting it for the student, it asks the student a follow-up question as a hint, forcing the student to think on their own)
You are on the right track. Pay close attention to the operation you are performing in the loop. You're currently multiplying the number with itself, but you want to find the product of all numbers. What operation should you use instead to continuously update 'total_product'?

Based on the conversation, try to always ask follow-up questions to the individual. 
This is a great way to foster a more engaging conversation, and help the individual gain a more deeper understanding of the material they are trying to learn.

Below, you will receive the students question, any relevant text that can be used to help answer the question, along with previous chat history with the student.

##Previous Chat History with Student:
{previous_chat_history_st}

#Retrieved Passages:
{passages}

##Student Question:
{question}

##Your Answer:
"""

    question = question.strip()
    q_embd = list(get_embedding(question))


    pinecone.init(
        api_key = os.environ['PINECONE_API_KEY'],
        environment = os.environ['PINECONE_ENVIRONMENT_NAME']
    )
    index = pinecone.Index('companion-app-main')
    xc = index.query(
        q_embd, 
        top_k = k, 
        include_metadata = True,
        namespace = pc_namespace
    )

    full_result_list = []
    for result in xc['matches']:
        # print('result:', result)
        result_score = result['score']
        result_metadata = result['metadata']
        result_page_number = result_metadata['page_number']
        result_page_text = result_metadata['page_text']
        
        full_result_list.append({
            'result_score': result_score,
            'page_number': result_page_number,
            'page_text': result_page_text
        })

    
    full_psg_str =  '\n'.join([rdi['page_text'].strip() for rdi in full_result_list])
    q_prompt = q_prompt.format(
        previous_chat_history_st = previous_chat_history_st,
        question = question,        
        passages = full_psg_str
    )
    print(q_prompt)

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]
    response = openai.ChatCompletion.create(
        # model = "gpt-4",
        model = "gpt-3.5-turbo-16k-0613",
        messages = messages_list,
    )
    response_message = response["choices"][0]["message"]['content']

    reference_list = []
    for rdi in full_result_list:
        psg_text = rdi['page_text'].strip()
        reference_list.append({
            'result_score': rdi['result_score'],
            'page_number': rdi['page_number'],
            'page_text': str(psg_text[:250] + '...').replace('\n', ' ')
        })

    reference_list_st = '- ' + '<br/>- '.join([f"Retrieval Score: {round(dt['result_score'], 2)} | Page Number: {int(dt['page_number'])} | {dt['page_text']}" for dt in reference_list])
    final_text = f"""{response_message}<br/><br/><b>References:</b><br/> {reference_list_st}"""

    final_dict_rv = {
        'question': question,
        'q_prompt': q_prompt,
        'response': response_message,
        'reference_list': reference_list,
        'final_text_response': final_text
    }
    return final_dict_rv 






## Handle Solution Checking 

import ast

# restricted_globals = dict(
#     __builtins__ = safe_builtins, 
#     _getiter_ = list.__iter__ ,
#     _getattr_ = getattr,
#     _getitem_ = getitem,
#     list = list, 
#     dict = dict, 
#     enumerate = enumerate, 
#     map = map, 
#     sum = sum,
#     abs = abs,
#     min = min, 
#     max = max,
#     range = range
# )

def course_question_solution_check(source_code, input_param, output_param):
    try:
        tree = ast.parse(source_code, mode='exec')
        function = tree.body[0]
        num_inputs = len([a.arg for a in function.args.args])
    except: 
        return {'success': False, 'message': 'Invalid Syntax. Code could not compile.', 'user_function_output': None}

    try:
        byte_code = compile_restricted(
            source_code,
            filename='<inline code>',
            mode='exec'
        )
        exec(byte_code, restricted_globals)
        # exec(byte_code, {'__builtins__': safe_builtins}, None)
    except:
        return {'success': False, 'message': 'Code did not compile. Ensure no print or import statements are present in the code.', 'user_function_output': None}
    
    # print(locals())
    # user_function = locals()[function.name]
    # print('user-function:', user_function)
    # print(num_inputs, input_param)

    user_function = restricted_globals[function.name]
    print('user-function:', user_function)
    
    if num_inputs != len(input_param):  # user incorrectly specified number of required inputs in their function
        return {'success': False, 'message': 'The number of the parameters in the function is not correct.', 'user_function_output': None}

    if num_inputs == 1:
        try:
            function_output = user_function(input_param[0])
        except: # function execution error
            return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords.', 'user_function_output': None}
        
        if function_output == output_param:
            return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
        else:
            return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}

    elif num_inputs == 2:
        # print('input-params', input_param[0], input_param[1])
        function_output = user_function(input_param[0], input_param[1])
        try:
            function_output = user_function(input_param[0], input_param[1])
        except: # function likely named a special python keyword
            return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords.', 'user_function_output': None}
        
        if function_output == output_param:
            return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
        else:
            return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}

    elif num_inputs == 3:
        try:
            function_output = user_function(input_param[0], input_param[1], input_param[2])
        except: # function likely named a special python keyword
            return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords.', 'user_function_output': None}
        
        if function_output == output_param:
            return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
        else:
            return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}
    
    elif num_inputs == 4:
        try:
            function_output = user_function(input_param[0], input_param[1], input_param[2], input_param[3])
        except: # function likely named a special python keyword
            return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords.', 'user_function_output': None}
        
        if function_output == output_param:
            return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
        else:
            return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}




# globals_dict = {}
# globals_dict.update(
#     __builtins__={
#         'True': True,
#         'False': False,
#         'None': None,
#         'str': str,
#         'bool': bool,
#         'int': int,
#         'float': float,
#         'enumerate': enumerate,
#         'dict': dict,
#         'list': list,
#         'tuple': tuple,
#         'map': map,
#         'abs': abs,
#         'min': min,
#         'max': max,
#         'sum': sum,
#         'filter': filter,
#         'round': round,
#         'len': len,
#         'repr': repr,
#         'set': set,
#         'all': all,
#         'any': any,
#         'ord': ord,
#         'chr': chr,
#         'divmod': divmod,
#         'isinstance': isinstance,
#         'range': range,
#         'zip': zip,
#     }
# )


# import time
# import timeout_decorator

# from wrapt_timeout_decorator import *

# @timeout(5)
# def new_question_solution_check(source_code, input_param, output_param, mode="exec"):
#     source_code = source_code.strip()

#     try:
#         tree = ast.parse(source_code, mode=mode)
#         function = tree.body[0]
#         num_inputs = len(function.args.args)
#     except: 
#         return {'success': False, 'message': 'Invalid Syntax. Code could not compile.', 'user_function_output': None}

#     try:
#         source_code = compile(tree, "<string>", mode)
#         restricted_locals = {}
#         exec(source_code, globals_dict, restricted_locals)
#         # print(restricted_locals[function.name](4,5))
#     except:
#         return {'success': False, 'message': 'Code did not compile. Ensure no print or import statements are present in the code.', 'user_function_output': None}

#     user_function = restricted_locals[function.name]
        
#     if num_inputs != len(input_param):  # user incorrectly specified number of required inputs in their function
#         return {'success': False, 'message': 'The number of the parameters in the function is not correct.', 'user_function_output': None}

#     if num_inputs == 1:
#         try:
#             function_output = user_function(input_param[0])
#         except: # function execution error
#             return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords.', 'user_function_output': None}
        
#         if function_output == output_param:
#             return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
#         else:
#             return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}

#     elif num_inputs == 2:
#         # print('input-params', input_param[0], input_param[1])
#         function_output = user_function(input_param[0], input_param[1])
#         try:
#             function_output = user_function(input_param[0], input_param[1])
#         except: # function likely named a special python keyword
#             return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords.', 'user_function_output': None}
        
#         if function_output == output_param:
#             return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
#         else:
#             return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}

#     elif num_inputs == 3:
#         try:
#             function_output = user_function(input_param[0], input_param[1], input_param[2])
#         except: # function likely named a special python keyword
#             return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords.', 'user_function_output': None}
        
#         if function_output == output_param:
#             return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
#         else:
#             return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}
    
#     elif num_inputs == 4:
#         try:
#             function_output = user_function(input_param[0], input_param[1], input_param[2], input_param[3])
#         except: # function likely named a special python keyword
#             return {'success': False, 'message': 'Python compilation error. Ensure your function does not contain any special keywords.', 'user_function_output': None}
        
#         if function_output == output_param:
#             return {'success': True, 'message': 'Test case successfully passed.', 'user_function_output': function_output}
#         else:
#             return {'success': False, 'message': 'Function returned wrong output.', 'user_function_output': function_output}




# source_code = """
# def fn_two(a, b):
# 	if a % b <= 0:
# 		return True
	
# 	return False
# """

# val = new_question_solution_check(
#     source_code,
#     [101, 3],
#     True
# )
# print(val)


# source_code = """
# def user_fn(a):
#     b = a
#     while True:
#         b += 1
#     # b = a
#     # b += 4
#     # b *= 12
#     # return b
# """
# x, y = [3], 9
# res = new_question_solution_check(source_code, x, y)
# print(f"Res: {res}")


# course_question_solution_check(source_code, x, y)

# source_code = """
# def function_one(x, y):
#     def function_two(z):
#         return z ** 2

#     val_two = function_two(3)
#     return (9 ** 9) / val_two
# """

# x, y = [3], 9
# course_question_solution_check(source_code, x, y)


# source_code = """
# def fun_one(s_one, s_two):
#     return s_one[0]
# """
# x, y = ["hello", "world"], 'hello'
# print( course_question_solution_check(source_code, x, y) )


# source_code = """
# def fn_one(n):
# 	c = 0
# 	n = abs(n)
# 	while n != 0:
# 		n = n // 10
# 		c += 1
# 	return c
# """
# x = [4]
# y = 1
# print( course_question_solution_check(source_code, x, y) )


# source_code = """
# def fn_two(a, b):
# 	for idx in range(b, a):
# 		return idx
# """
# x = [15,3]
# y = 1
# print( course_question_solution_check(source_code, x, y) )





# from RestrictedPython import compile_restricted
# from RestrictedPython import safe_builtins

# source_code = """
# def fun_one(s_one, s_two):
#     return str(len(s_one)) + s_one[1:] + s_two[:-1] + str(len(s_two))
# """

# from operator import getitem

# # Create a restricted built-ins dictionary with '__getitem__' allowed
# restricted_globals = dict(
#     __builtins__ = safe_builtins, 
#     _getiter_ = list.__iter__ ,
#     _getattr_ = getattr,
#     _getitem_ = getitem,
#     list = list, 
#     dict = dict, 
#     enumerate = enumerate, 
#     map = map, 
#     sum = sum
# )

# byte_code = compile_restricted(
#     source_code,
#     filename='<inline code>',
#     mode='exec'
# )

# exec(byte_code, restricted_globals)

# # Now, call the function
# s_one = "Hello"
# s_two = "World"
# result = restricted_globals['fun_one'](s_one, s_two)
# print(result)




# def sum_fibonacci_sequence(n):
#     if n <= 0:
#         return 0  # The sum is 0 for n <= 0
#     elif n == 1:
#         return 1  # The sum is 1 for n = 1

#     fib_sequence = [0, 1]
#     count = 0
#     # while fib_sequence[-1] + fib_sequence[-2] <= n:
#     while count <= (n-2):        
#         next_fib = fib_sequence[-1] + fib_sequence[-2]
#         fib_sequence.append(next_fib)
#         count += 1

#     print(fib_sequence)
#     return sum(fib_sequence)


# print( sum_fibonacci_sequence(10) )

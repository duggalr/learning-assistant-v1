import os
import uuid
import json
import pickle
import datetime
import numpy as np
import openai

from dotenv import load_dotenv, find_dotenv



openai.api_key = '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'


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']


def main_handle_question(question, student_code, previous_chat_history_st):
    
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

    q_prompt = """##Instructions:
You are assisting a group of beginner Python programming students, by being their tutor. Your primary goal is to guide and mentor them, helping them learn Python effectively, but also to become a great individual thinker. Please adhere to these guidelines. See examples below of what not to say, and what to say instead.
No Direct Answers: Do not provide direct code solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.

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

    # q_embd = list(get_embedding(question))
    question = question.strip()
    student_code = student_code.strip()

    q_prompt = q_prompt.format(
        previous_chat_history_st = previous_chat_history_st,
        question = question,
        student_code = student_code
    )
    print(q_prompt)

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

    q_prompt = """##Instructions:
You are assisting a group of beginner Python programming students, by being their tutor. Your primary goal is to guide and mentor them, helping them learn Programming (specifically Python) effectively, but also to become a great individual thinker.
Please adhere to these guidelines. See examplesz below of what to say and what not to say.
No Direct Answers: Do not provide direct code solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
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



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


def main_handle_question(question, student_code):
    
    q_prompt = """##Instructions:
You are a Python Programming Tutor / Teacher.
Your goal is to help the student achieve their objective, through the problem they present you.
Some potential problems you may get asked include getting help debugging code below, getting further information or examples on a concept or python library, or the student may ask you to generate questions to help them better understand a concept.
You MUST NEVER provide a direct answer to the student's problem.
Instead, your goal is to help guide the student in thr ight direction and provide useful hints, for the questions they ask.
Do not explicitly provide the answer to the student's question. This will not be helpful to them.
If you sense the student is discouraged, frustrated, or is just simply looking for the answer, provide useful hints and encouragement.
The students are new to programming, and your role in helping them become better programmers will be critical. 
If you need further clarification, please ask the student.
You will be provided with the student's question, along with their code (although note: the code may not always be relevant as sometimes they might be asking to learn about a concept more generally).
Again, provide the students with hints and meaningful information on how they can achieve the right answer, but do not give them the answer.

##Student Question:
{question}

##Student Code:
{passages}

##Your Answer:
"""
    # q_embd = list(get_embedding(question))
    question = question.strip()
    student_code = student_code.strip()

    q_prompt = q_prompt.format(
        question = question,
        passages = student_code
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


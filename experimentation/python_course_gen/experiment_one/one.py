import os
import json
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI


if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)


API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(
    api_key = API_KEY,
)

q_prompt_template = """##Instructions:
You will be helping a student who wants to learn Python.
The student will learn Python by having a conversation with you.

You will be given the following function types:
- save_student_goals
- save_new_note
- update_existing_note
- save_exercise
- mark_exercise_complete
- no_function_needed

Each function type will include a "message_response" key, which will be your response to the student, in your conversation.
You will be return a JSON containing:
- "function_type": "function_type_name"
- "message_response": "This will be the response you will give back to the student in your chat conversation."
- additional key/values unique to each function type. Details provided below.

Function Type Details:
- save_student_goals:
    - This type will be used to save the student goals you have generated
    - You will be returning a JSON, containing the following information:
        - "function_type: "save_student_goals"
        - "message_response": This will be the response you will give back to the student in your chat conversation.
        - "student_goals": This will be the text containing the students background and goals you generated, based on your converation.
        
- save_new_note:
    - This type will be used to save notes for the student.
    - You will be returning a JSON, containing the following information:
        - "function_type: "save_new_note"
        - "message_response": This will be the response you will give back to the student, in your chat conversation.
        - "note": This will be the text containing the notes you generate for the student, based on your conversation.

- update_existing_note:
    - This type will be used to update an existing note for the student.
    - You will be returning a JSON, containing the following information:
        - "function_type: "update_existing_note"
        - "message_response": This will be the response you will give back to the student in your chat conversation.
        - "note_id": This will be the ID of the note you are updating.
        - "note_text": This will be the text containing the updated notes you generate for the student, based on your conversation.

- save_exercise:
    - This type will be used to save the exercise generated for the student.
    - You will be returning a JSON, containing the following information:
        - "function_type: "save_exercise"
        - "message_response": This will be the response you will give back to the student in your chat conversation.
        - "exercise": This will be the text containing the exercise you generate for the student, based on your conversation.

- mark_exercise_complete:
    - This type will be used to mark an existing exercise as complete.
        - The purpose of this function is to ensure the student knows when they have successfully completed the exercise, so they can move on to the next task.
    - You will be returning a JSON, containing the following information:
        - "function_type: "mark_exercise_complete"
        - "message_response": This will be the response you will give back to the student in your chat conversation.
        - "exercise_id": This will be the ID of the exercise you are marking as complete.

- no_function_needed
    - This type will be used when you don't to call any of the other functions and simply just return a message_response to the user, in the conversation.    
    - You will be returning a JSON, containing the following information:
        - "function_type: "no_function_needed"
        - "message_response": This will be the response you will give back to the student in your chat conversation.

Here is context on what has been generated for the student thus far, along with past information on the student:
- Student Goals Information Generated: False
- Number of Notes Generated: 0
- Number of Exercises Generated: 0
- Number of Exercises Completed by Student: 0

Previous Chat History with Student:
{previous_student_chat_history_str}

Current Student Response:
{current_student_response_str}

Your goal is to leverage the function types above, along with the student information above, to help the student learn Python.

Here are a few things to keep in mind:
- You will be teaching the student Python primarily through conversation. 
    - The functions above are created to help save information in the Database and present those to the user, beside the chat interface.
    - However, the primary way the student is going to learn Python is through the "message_responses" you provide, based on your conversation with the student.
        - It is fundamental that you maintain a very smooth, natural progression of conversation, with the student.
        - Continue the conversation and save the notes, exercises, you generate through conversation leveraging the function calls,
        to help the student learn Python in an efficient manner.

- You MUST only present ONE QUESTION OR TOPIC at a time to the student. This is very important.
    - Don't overwhelm the student with an abundance of information. This is counter-productive to learning.

- Start with understanding the student's goals, why they want to learn Python, and their background knowledege.
    - This is critical. Ask follow-up questions. Do not ask too many questions though. Keep it at a BALANCED amount as you can always get more information, later on.

- When generating notes, make them as detailed as possible, filled with examples, focused on a SINGLE OR FEW CONCEPTS.
    - Again, the student will be leveraging your notes to help them learn Python.
    - It is critical you provide them with the best information possible, which is easiest for them to understand.

- When generating an exercise, provide a clear problem with input/output examples.
    - Make the exercises relevant for the student, the notes and the conversations you have currently had.

##Your Answer:
"""

output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/python_course_gen/experiment_one/output_files/run_three'
previous_student_chat_history = ""
c = 1

while True:

    user_response = input("Question: ").strip()

    q_prompt = q_prompt_template.format(
        previous_student_chat_history_str = previous_student_chat_history,
        current_student_response_str = user_response
    )

    di = {"role": "user", "content": q_prompt}

    messages_list = [di]
    chat_completion = client.chat.completions.create(
        messages = messages_list,
        model = "gpt-4-0125-preview",
        response_format={ "type": "json_object" }
    )

    response_msg_json_str = chat_completion.choices[0].message.content
    response_message_json_data = json.loads(response_msg_json_str)
    
    ## Save Information
    tmp_fp = os.path.join(output_dir_fp, f"prompt-{c}.txt")
    f = open(tmp_fp, 'w')
    f.write(q_prompt)
    f.close()

    tmp_json_fp = os.path.join(output_dir_fp, f'response_message_json_{c}.json')
    with open(tmp_json_fp, 'w', encoding='utf-8') as f:
        json.dump(response_message_json_data, f, ensure_ascii=False, indent=4)

    c += 1

    ## Response Information
    function_type = response_message_json_data['function_type']
    model_response_str = response_message_json_data['message_response'].strip()
    
    tmp_past_st = f"Student Response: {user_response}\nYour Response: {model_response_str}\n"
    previous_student_chat_history += tmp_past_st
    
    ## Display Info to User
    print(f"Function-Type: {function_type} | Message: {model_response_str}")
    print('\n')

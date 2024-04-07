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

def generate_course_outline(student_response, student_info, student_course_outline, previous_student_chat_history):

    q_prompt = """##Instructions:
Below, you will be given a description of a student, specifically what they want to learn, why they want to learn it, and their background on that topic.
You will also be given a current student question/response, along with past conversation history with the student (if any).
You will also be given a current version of the course outline the student is using (if any).
Your goal will be to either generate a response to the student's question, or to generate a new or updated course outline for the student.

If your response requires you to generate a course outline, please follow these guidelines:
- Your goal is to leverage this information to generate a course outline for the student.
- The course outline should be split by a modular basis.
- Each module will represent a specific topic that the student will learn.
- Ensure each module does not cover too much information but at the same time, it doesn't cover too little information either.
- Each module should contain sub-topics, to provide more clarity for the student on what will be covered.
- If a course outline already exists and you are updating it, or adding to it, depending on the user's feedback, YOU MUST REGENERATE AND OUTPUT THE ENTIRE COURSE OUTLINE AS IT WAS BRAND NEW.

Output Format: Your response must be outputted in JSON FORMAT, containing the following information:
- "outline_generation":
    - This value will be a boolean, either containing True if a new/updated outline was generated, and False, otherwise.
- "name"
    - This value will be the name of the course. (leave value blank if unchanged or not required)
- "description"
    - This value will be the description of the course. (leave value blank if unchanged or not required)
- "modules"
    - This value will be populated based on the format described below, if the task on hand requires you to generate a course outline.
        - This value will be a list of dictionaries (in JSON FORMAT), where each dictionary will contain:
            - "module_number": this will be a number of the module which will be used to order the modules, when presenting to user
                - 1 --> First Module, 2 --> Second Module, ...
            - "module_topic": this will be the primary topic the module will cover
            - "module_description": this will be a list, where each value in the list will be a string representing a sub-topic the module will cover
    - Leave value blank if unchanged or not required
- "message_to_student"
    - This value will be where you can respond to the student, if they have sent any current question/response. (leave value blank if unchanged or not required)

##Student Information
{student_info}

##Course Outline
{student_course_outline}

##Previous Chat History with Student:
{previous_student_chat_history}

##Current Student Response:
{student_response}

##Your Answer:
"""

    student_response = student_response.strip()
    student_info = student_info.strip()
    previous_student_chat_history = previous_student_chat_history.strip()
    
    q_prompt = q_prompt.format(
        student_info = student_info,
        student_course_outline = '',
        previous_student_chat_history = previous_student_chat_history,
        student_response = student_response
    )

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]

    chat_completion = client.chat.completions.create(
        messages = messages_list,
        # model = "gpt-4",
        model = "gpt-3.5-turbo-0125",
        response_format={ "type": "json_object" }
    )

    response_message_json_str = chat_completion.choices[0].message.content
    # print(response_message_json_str)
    
    response_message_json_data = json.loads(response_message_json_str)

    final_dict_rv = {
        'student_response': student_response,
        'q_prompt': q_prompt,
        'response': response_message_json_data,
    }
    return final_dict_rv


# desc = "The student wants to implement their own simple SMTP server."
# student_course_outline = generate_course_outline(
#     student_response = '', 
#     student_info = desc, 
#     previous_student_chat_history = ''
# )
# print(student_course_outline['response'])


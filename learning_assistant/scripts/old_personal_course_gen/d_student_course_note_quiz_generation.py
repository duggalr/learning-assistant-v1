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


def generate_quiz(student_info, course_notes):

    q_prompt = """##Instructions:
Your goal is to generate a solid multiple-choice quiz, given the course notes below.
The quiz should be relevant to the user's goals/background.
The questions and exercises should be well thought out, really probing a deep understanding for the student.

##Student Goals/Background Information
{student_info}

##Course Notes
{course_notes}

Your response MUST BE OUTPUTED IN JSON FORMAT, containing the following key:
- "quiz"
    - This value will be a list of dictionaries (in JSON FORMAT), where each dictionary will contain:
        - "question_number": this will be a number of the question which will be used to order the questions, when presenting to user
            - 1 --> First Question, 2 --> Second Question, ...
        - "question": this will be the actual question, represented as a string
        - "multiple_choice_options": this will be a list of the multiple choice options available, for this question
        - "answer": this will be the answer to the question, represented as a string.

##Your Answer:
"""

    q_prompt = q_prompt.format(
        student_info  = student_info,
        course_notes = course_notes
    )
    print(f"Total length of prompt: {len(q_prompt)}")

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]

    chat_completion = client.chat.completions.create(
        messages = messages_list,
        model = "gpt-4-0125-preview",
        # model = "gpt-3.5-turbo-0125",
        response_format={ "type": "json_object" }
    )

    response_message_json_str = chat_completion.choices[0].message.content
    # print(response_message_json_str)
    
    response_message_json_data = json.loads(response_message_json_str)

    final_dict_rv = {
        'q_prompt': q_prompt,
        'response': response_message_json_data,
    }
    return final_dict_rv


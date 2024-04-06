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

def generate_course_outline(student_response, student_info, previous_student_chat_history):
    q_prompt = """##Instructions:
Below, you will given a description of a student, specifically what they want to learn, why they want to learn it, and their background on that topic.

Your goal is to leverage this information to generate a course outline for the student.
The course outline should be split by a modular basis.
Each module will represent a specific topic that the student will learn.
Ensure each module does not cover too much information but at the same time, it doesn't cover too little information either.
Each module should contain sub-topics, to provide more clarity for the student on what will be covered.
Please also add a name for the course.
Please also add a brief description describing what the course outline entails and why you set it up this way.
This course outline is dynamic and can change, depending on the student's progress and interests so please do mention that in your description.

The course outline MUST BE GENERATED in Markdown Format.
You will also be given any past chat history with the student, along with a current student response (if any).
The student may provide feedback for the course outline you generate.
Please incorporate this feedback, as you generate the course outline.

Your response MUST BE IN JSON FORMAT, containing the following 3 keys:
- "name"
    - The value will be the course name.
- "description"
    - The value will be the description you generate for the student's course outline.
- "outline"
    - The value will be a string, containing the course outline IN MARKDOWN FORMAT, which will be presented to the student.

##Student Information
{student_info}

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
        previous_student_chat_history = previous_student_chat_history,
        student_response = student_response
    )

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]
    chat_completion = client.chat.completions.create(
        messages = messages_list,
        # model = "gpt-4",
        model = "gpt-3.5-turbo-0125",
    )

    response_message_json_str = chat_completion.choices[0].message.content
    
    # TODO: assume it's always a JSON? potentially re-generate if it is not?
    response_message_json_data = json.loads(response_message_json_str)

    final_dict_rv = {
        'student_response': student_response,
        'q_prompt': q_prompt,
        'response': response_message_json_data,
    }
    return final_dict_rv


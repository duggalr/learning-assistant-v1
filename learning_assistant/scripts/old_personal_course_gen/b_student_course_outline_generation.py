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
    # - "name"
    #     - The value will be the course name.
    # - "description"
    #     - The value will be the description you generate for the student's course outline.
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
For your markdown course outline, please include the name of the course and description at the top (in markdown), before the remaining outline.

You will also be given any past chat history with the student, along with a current student response (if any).
The student may provide feedback for the course outline you generate.
Please incorporate this feedback, as you generate the course outline.
If there is a student response and you want to respond back, you can add that response to the "message_to_student" key in your JSON output below.

Your response MUST BE OUTPUTED IN JSON FORMAT, containing the following 3 keys:
- "name"
    - This value will be the name of the course.
- "description"
    - This value will be the description of the course.
- "outline"
    - This will be the course outline IN MARKDOWN FORMAT, which will be presented to the student.
        - Please ensure at the beginning of your markdown, you include the Course Name and Description, before you include your outline.
        - The Course Name and Course Description must be included in our generated Course Outline Markdown, at the top.
- "message_to_student"
    - This value will be where you can respond to the student, if they have sent any current question/response.

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
        response_format={ "type": "json_object" }
    )

    # TODO: add the response_format above to all completion calls

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


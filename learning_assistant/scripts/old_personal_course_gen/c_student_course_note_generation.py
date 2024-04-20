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


def generate_course_notes(student_info, course_outline, current_module_information, student_response, previous_conversation_history):
    
    q_prompt = """##Instructions:
You will be given a student's course outline, along with the specific module the student is currently working on.
Your goal is to generate course notes ONLY ON THE CURRENT MODULE the student is working on.
The goal of the course notes will be to help the student develop a strong understanding of that topic.

Your course notes must be generated such that it is specific for the student, given their goals and background.
The notes should be generated such that, it is very engaging and easy for the student to understand the material.
Please ensure your course notes for the module are as DETAILED AS POSSIBLE. The more detail, the better for the student.

DO NOT GENERATE ANY NOTES FOR FUTURE MODULES. ONLY FOCUS ON THE CURRENT MODULE.
Your course notes MUST BE GENERATED in Markdown Format.

You will also be given any past chat history with the student, along with a current student response (if any).
The student may provide feedback for the course notes you generated or they may have a question about a specific concept.
Please incorporate this feedback, as you generate the course notes or answer the student's question.

Below, you will be given 5 critical pieces of information:
- The student's goals, what they want to learn, and their background.
- The entire course outline.
- The current module information.
- Past Conversation History with the Student (if any)
- Current Student Response (if any)

Your response MUST BE OUTPUTED IN JSON FORMAT, containing the following 3 keys:
- "course_note_generation"
    - This will be a boolean indicating whether you generated course notes or provided an answer to the student's question.
        - If True, then it means you have generated course notes for the student, given the information
        - If False, then it means you have answered a student's question instead.
- "course_notes"
    - This will be the course notes IN MARKDOWN FORMAT, which will be presented to the student.
    - If "course_note_generation": False, then this will just be an empty string.
- "model_response"
    - This will be either a response to the student's question, or any additional information you want to share to the student in the chat.

##Student Goals/Background Information
{student_info}

##Course Outline
{course_outline}

##Current Module Information
{week_information}

##Previous Chat History with Student:
{previous_student_chat_history}

##Current Student Response:
{student_response}

##Your Answer:
"""

    q_prompt = q_prompt.format(
        student_info  = student_info,
        course_outline = course_outline,
        week_information = current_module_information,
        previous_student_chat_history = previous_conversation_history,
        student_response = student_response
    )
    print(f"Total length of prompt: {len(q_prompt)}")

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]
    chat_completion = client.chat.completions.create(
        messages = messages_list,
        # model = "gpt-4-0125-preview",
        model = "gpt-3.5-turbo-0125",
        response_format={ "type": "json_object" }
    )
    response_message_json_str = chat_completion.choices[0].message.content
    
    response_message_json_data = json.loads(response_message_json_str)
    final_dict_rv = {
        'student_response': student_response,
        'q_prompt': q_prompt,
        'response': response_message_json_data,
    }
    return final_dict_rv


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


def generate_course_notes(student_info, course_outline, current_module_information, current_week_course_notes, student_response, previous_conversation_history):
    
    q_prompt = """##Instructions:
You will be given a student's course outline, along with the specific module the student is currently working on.
Your goal will be to either generate/update course notes ONLY ON THE CURRENT MODULE THE STUDENT is working on, or generate a response to the student's question.

If your response requires you to generate course notes, please follow these guidelines:
- ONLY GENERATE COURSE NOTES ON THE CURRENT MODULE the student is working on.
- The goal of the course notes will be to help the student develop a strong understanding of that topic.
- Your course notes must be generated such that it is specific for the student, given their goals and background.
- The notes should be generated such that, it is very engaging and easy for the student to understand the material.
- Please ensure your course notes for the module are as DETAILED AS POSSIBLE. The more detail, the better for the student.
- Please provide relevant examples for the student, when explaining a specific topic. Examples will help make it easier for the student to understand the content.
- DO NOT GENERATE ANY NOTES FOR FUTURE MODULES. ONLY FOCUS ON THE CURRENT MODULE.
- Your course notes MUST BE GENERATED in Markdown Format.
- If exisitng course notes for the current module exist and you are updating it, or adding to it, depending on the user's feedback, YOU MUST REGENERATE AND OUTPUT THE ENTIRE COURSE OUTLINE AS IT WAS BRAND NEW.

Below, you will be given 6 critical pieces of information:
- The student's goals, what they want to learn, and their background.
- The entire course outline.
- The current module information.
- Current module existing course notes.
- Past Conversation History with the Student (if any)
- Current Student Response (if any)

Your response MUST BE OUTPUTED IN JSON FORMAT, containing the following 3 keys:
- "course_note_generation"
    - This will be a boolean indicating whether you generated course notes or provided an answer to the student's question.
        - If True, then it means you have generated course notes for the student, given the information.
        - If False, then it means you didn't need to generate course notes and rather, just answered a student's question instead.
- "course_notes"
    - This will be the course notes IN MARKDOWN FORMAT, which will be presented to the student.
    - Please ensure at the beginning of your markdown, you include the Current Module Name and SubTopics that will be covered, before you include your notes.
    - If "course_note_generation": False, then this will just be an empty string.
- "model_response"
    - This will be either a response to the student's question, or any additional information you want to share to the student in the chat.
        - If you have generated new course notes, add a short response here, summarizing what changes you made.
    
##Student Goals/Background Information
{student_info}

##Course Outline
{course_outline}

##Current Module Information
{current_week_information}

##Current Module Course Notes
{current_week_course_notes}

##Previous Chat History with Student:
{previous_student_chat_history}

##Current Student Response:
{student_response}

##Your Answer:
"""

    q_prompt = q_prompt.format(
        student_info  = student_info,
        course_outline = course_outline,
        current_week_information = current_module_information,
        current_week_course_notes = current_week_course_notes,
        previous_student_chat_history = previous_conversation_history,
        student_response = student_response
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
    
    response_message_json_data = json.loads(response_message_json_str)
    final_dict_rv = {
        'student_response': student_response,
        'q_prompt': q_prompt,
        'response': response_message_json_data,
    }
    return final_dict_rv


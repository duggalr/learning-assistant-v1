import os
import json
from openai import OpenAI


class OpenAIWrapper(object):
    """
    """
    def __init__(self):
        self.api_key = os.environ['OPENAI_API_KEY']
        self.client = OpenAI(
            api_key = self.api_key
        )
        self.model_name = "gpt-4-0125-preview"


    def _generate_answer(self, prompt, return_json = True):
        di = {"role": "user", "content": prompt}
        messages_list = [di]
        if return_json:
            chat_completion = self.client.chat.completions.create(
                messages = messages_list,
                model = self.model_name,
                response_format={ "type": "json_object" }
            )
        else:
            chat_completion = self.client.chat.completions.create(
                messages = messages_list,
                model = self.model_name,
            )
        response_message = chat_completion.choices[0].message.content
        return response_message


    def generate_learning_outline(self, conversation_history):
        q_prompt = """##Instructions:
Below, you will be given a converation with a student, explaining what they want to learn, along with their background on that topic.
Your goal will be to either generate a personalized course outline for the student.
- The course outline should be split by a modular basis.
- Each module will represent a specific topic that the student will learn.
- Ensure each module does not cover too much information but at the same time, it doesn't cover too little information either.
- Each module should contain sub-topics, to provide more clarity for the student on what will be covered.
- The student already has an IDE environment setup with Python so no need to worry or include anything about setting up a Python environment.
    - DO NOT MENTION ANYTHING IN YOUR COURSE OUTLINE ABOUT PYTHON ENVIRONMENT OR IDE SETUP. That is already complete for the student.

Output Format: Your response must be outputted in JSON FORMAT, containing the following information:
- "student_background"
    - This value will be a summary containing what the student wants to learn, their goals and background.
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

##Conversation History with Student
{conversation_history}

##Your Answer:
"""
        conversation_history = conversation_history.strip()
        q_prompt = q_prompt.format(
            conversation_history = conversation_history,
        )

        response = self._generate_answer(
            prompt = q_prompt,
            return_json = True
        )

        final_dict_rv = {
            'q_prompt': q_prompt,
            'response': response,
        }
        return final_dict_rv


    def generate_new_note(self, topic_str, conversation_history):
        q_prompt = """##Instructions:
Below, you will be given a topic that the student is currently learning.
Your goal is to generate notes for that particular topic, for the student.
- The goal of the course notes will be to help the student develop a strong understanding of that topic.
- The notes should be generated such that, it is very engaging and easy for the student to understand the material.
- Please ensure your course notes for the module are as DETAILED AS POSSIBLE. The more detail, the better for the student.
- Your notes MUST CONTAIN EXAMPLES. It is very important to demonstrate the topic through examples.
- Your course notes MUST BE GENERATED in Markdown Format.

Your response MUST BE OUTPUTED IN JSON FORMAT, containing the following key:
- "course_notes"
    - This will be the course notes IN MARKDOWN FORMAT, which will be presented to the student.
    - Please ensure at the beginning of your markdown, you include the Current Topic Name.

Below, you will be given a conversation with a student, along with the topic to generate your notes on.

##Note Generation Topic:
{topic_str}

##Conversation History with Student
{conversation_history}

##Your Answer:
"""
        topic_str = topic_str.strip()
        conversation_history = conversation_history.strip()
        q_prompt = q_prompt.format(
            topic_str = topic_str,
            conversation_history = conversation_history
        )

        response = self._generate_answer(
            prompt = q_prompt,
            return_json = True
        )

        final_dict_rv = {
            'q_prompt': q_prompt,
            'response': response,
        }
        return final_dict_rv


    def generate_new_exercise(self, topic_str, conversation_history):
        q_prompt = """##Instructions:
Below, you will be given notes and recent student/teacher conversation history.
Your goal is to generate extremely well-thought out exercises for the student, given the notes and conversation history.
The exercises should be Python programming exercises, where the student will implement the solution by writing code in an IDE.
- The student already has an IDE environment with Python setup.
Ensure the exercises are as clear as possible for the student to understand.

Your response MUST BE OUTPUTED IN JSON FORMAT, containing the following key:
- "exercises"
    - This value will be a list of dictionaries (in JSON FORMAT) containing exercises, where each dictionary will contain:
        - "question": this will be the question the student will work on.

Below, you will be given a conversation with a student, along with the notes you will generate your exercise on.

##Exercise Generation Notes:
{topic_str}

##Conversation History with Student
{conversation_history}

##Your Answer:
"""
        topic_str = topic_str.strip()
        conversation_history = conversation_history.strip()
        q_prompt = q_prompt.format(
            topic_str = topic_str,
            conversation_history = conversation_history
        )

        response = self._generate_answer(
            prompt = q_prompt,
            return_json = True
        )

        final_dict_rv = {
            'q_prompt': q_prompt,
            'response': response,
        }
        return final_dict_rv


    def generate_router(self, previous_student_chat_history_str, current_student_response_str, generated_learning_plan_str = None):
        q_prompt_template = """##Instructions:
Your goal will be to help a student learn/practice Python.
The student will be learning/practicing Python in an online web app.
The web app consists of:
- An Online IDE where they can run Python Code.
- A Notes Tab where they can see all the notes that have been generated from the conversation.
- An Exercises Tab where they can see all the exercises that have been generated from the conversation.
- A Course Outline Tab, where they can see the course outline that has been generated from the conversation.
- A Chat Interface where they will be talking with you.

You will be the 'router'.
You will be outputting specific functions to call, based on the conversation with the student.
Your job is to output a JSON containing the following:
- "function_type": "function_type_name" (that is most appropriate to call, given the conversation)
- "message_response": "This will be the response you will give back to the student in your chat conversation."

Flow of conversation:
- The student will be learning Python with you, primarily through conversation.
- You MUST only present ONE QUESTION OR TOPIC at a time to the student. This is very important.
- Don't overwhelm the student with an abundance of information. This is counter-productive to learning.
- Start first by understanding the student's background and goals.
- Do they have a specific project in mind they want to create?
- Do they have any experience with python or programming before?
- This is critical. Ask follow-up questions. Do not ask too many questions though. Keep it at a BALANCED amount as you can always get more information, later on.
- Once you understand the student's background and goals, then call the generate_student_background using the function.
- From there:
    - Interchangably call the other 3 functions to generate:
        - notes with examples for the student
        - exercises that they will solve
        - or 'no_function_needed' which is simply just you responding to a question the student may have.
- Please note:
    - Until you understand the student's background and goals and have called the 'generate_student_background' function, only then should you
    call the other functions to generate notes/exercises, etc. Do not call those beforehand.

Below are the functions you are provided:
- generate_learning_plan
- generate_note_with_examples
- generate_new_exercise_question
- no_function_needed

Function Type Details:
- generate_learning_plan:
    - This function will be called when you have learned more about the student's background and goals and now, want to generate a learning plan for the student.
    - You will not be generating the learning plan here. The function will generate it. Your job is simply to call it, when you feel it is relevant during the conversation.
    - ONLY CALL THIS FUNCTION ONCE YOU HAVE ENOUGH INFORMATION. WHEN YOU ARE GATHERING INFORMATION, just call the `no_function_needed`.
    - You will be returning a JSON, containing the following information:
        - "function_type: "generate_learning_plan"
        - "message_response": This will be your reply to the student, depending on the conversation. Part of your reply can also include that you generated a learning plan or course outline, which the user will be able to view on their screen.

- generate_note_with_examples:
    - This function will be called to generate a new note, based on the conversation with the student. 
    - You will not be generating the notes here. The function will generate it. Your job is simply to call it, when you feel it is relevant during the conversation.
    - You will be returning a JSON, containing the following information:
        - "function_type: "generate_note_with_examples"
        - "note_topic": This will contain the topic the note will be generated on.
        - "message_response": This will be your reply to the student, depending on the conversation. This reply will not be the note that will be displayed to the user. The function will output that. This reply can inform the user that you generated the notes, and they can view it on their screen, along with asking any questions they may have.

- generate_new_exercise_question:
    - This function will be called to generate a new exercise, based on the conversation with the student. 
    - You will not be generating the notes here. The function will generate it. Your job is simply to call it, when you feel it is relevant during the conversation.
    - You will be returning a JSON, containing the following information:
        - "function_type: "generate_new_exercise_question"
        - "message_response": This will be your reply to the student, depending on the conversation. Part of your reply can also include that you generated an exercise, which the user will be able to view on their screen.

- no_function_needed:
    - This function will be called when you don't need to call any of the other functions and simply just return a message_response to the user, in the conversation.
    - You will be returning a JSON, containing the following information:
        - "function_type: "no_function_needed"
        - "message_response": This will be your reply to the student, depending on the conversation. Part of your reply can also include that you generated an exercise, which the user will be able to view on their screen.

Here is the past conversation history with the student, along with their current response:

Previous Chat History with Student:
{previous_student_chat_history_str}

Current Student Response:
{current_student_response_str}
"""

        previous_student_chat_history_str = previous_student_chat_history_str.strip()
        current_student_response_str = current_student_response_str.strip()
        
        if generated_learning_plan_str is not None:
            q_prompt_template += """

Here is the past learning plan that has been generated for the student:
{generated_learning_plan_str}
"""
            generated_learning_plan_str = generated_learning_plan_str.strip()
            q_prompt = q_prompt_template.format(
                previous_student_chat_history_str = previous_student_chat_history_str,
                current_student_response_str = current_student_response_str,
                generated_learning_plan_str = generated_learning_plan_str
            )

        else:
            q_prompt = q_prompt_template.format(
                previous_student_chat_history_str = previous_student_chat_history_str,
                current_student_response_str = current_student_response_str
            )

        response = self._generate_answer(
            prompt = q_prompt,
            return_json = True
        )

        final_dict_rv = {
            'q_prompt': q_prompt,
            'response': response,
        }
        return final_dict_rv


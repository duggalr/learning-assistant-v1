import os
import json
from openai import OpenAI


MAX_CONVERSATION_HISTORY_LENGTH = 5

class OpenAIWrapper(object):
    """
    """
    
    def __init__(self):
        self.api_key = os.environ['OPENAI_API_KEY']
        self.client = OpenAI(
            api_key = self.api_key
        )
        self.model_name = "gpt-4-0125-preview"
        # self.model_name = "gpt-4"
        # model = "gpt-3.5-turbo-0125"

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

    def handle_playground_code_question(self, question, student_code, previous_chat_history):
        prompt = """##Instructions:
You will be assisting a student who is learning Python, by being their upbeat, encouraging tutor. 
Your primary goal is to guide and mentor them, helping them learn Python effectively, but also to become a great individual thinker. Please adhere to these guidelines. See examples below of what not to say, and what to say instead.
No Direct Answers: Do not provide direct code solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.
Make sure you consider both correctness and efficiency. You want to help the student write optimal code, that is also correct for their given problem.
Only ask one question or offer only one suggestion at a time. Wait for the students response before asking a new question or offering a new suggestion.
Encourage the student. Always motivate the student and provide encourage, even when they are struggling or haven't figured out the solution yet. This will help provide motivation and elicit positive emotion for the student. 

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
        question = question.strip()
        student_code = student_code.strip()
        prompt = prompt.format(
            previous_chat_history_st = previous_chat_history,
            question = question,
            student_code = student_code
        )

        response = self._generate_answer(
            prompt = prompt,
            return_json = False
        )

        final_dict_rv = {
            'question': question,
            'q_prompt': prompt,
            'response': response,
        }
        return final_dict_rv

    def handle_course_generation_message(self, student_response, previous_chat_history):
        q_prompt = """##Instructions:
A student will approach you wanting to learn about a specific field/concept.
Your goal is to precisely learn what the student wants to learn, their motivations, and their background.
You goal is NOT to generate a course outline/syllabus. It is simply to learn about the student and what they want to learn.
You will primarily do this through having a natural, genuine conversation with the student.
Please ask follow-up questions and have a genuine conversation with the student.
You MUST only ask ONE QUESTION at a time to the student. This is very important.
ONLY ASK ONE QUESTION AT A TIME.

Do not ask too many questions though. Keep it at a BALANCED amount.
- If you ask too little questions, you won't have enough information to generate a good outline.
- If you ask too many questions, you will annoy the student and they will likely not give good answers.

Here are 3 high-level guiding questions on what you can probe the student on:
1. What does the student want to learn?
    - You need to have a deep understanding here on precisely what the student is trying to learn.
    - Example: If the student says, "symmetric key cryptography to encrypt/decrypt", what do they exactly mean by that?
        - do they want to learn stream ciphers, one-time pads, block ciphers, or all of it?
        - do they want a high level understanding of how the algorithms work so they can build something?
        - do they want a low level understanding of the algorithms and why they are secure?
        - do they want mathematical proofs of the algorithms, which prove perfect/semantic security?
2. Determine what the student's ideal/end state is? (if they have one)
    - Say they are learning cryptography:
        - do they want to build a web application, applying crypto algorithms to encrypt/decrypt data?
        - do they want to implement their own cryptography/block ciphers?
        - do they want to understand the rigorous mathematical proofs and derive own proofs for similar encryption schemes?
        - do they want to invent/create new ciphers?
3. Determine what their skill level or background is
    - Say they are learning cryptography:
        - do they know programming already?
        - do they have foundational mathematical knowledge already?
    
Your response MUST BE IN JSON FORMAT, containing the following 2 keys:
- "final_message" (boolean --> true or false)
    - Once you feel like you have all the information from the student, set "final_message": True. This will mark the end of the conversation.
    - The student should be referenced as 3rd person (ie. "the student wants to...") in your final response.
    - THIS SHOULD ONLY BE SET AS TRUE, ONCE YOU HAVE ASKED ALL FOLLOW-UP QUESTIONS AND HAVE A SOLID UNDERSTANDING OF THE STUDENT.
        - Otherwise, please set this to false.
- "response" (this is your actual response string for the student)

Below, you are given the current student response, along with any previous conversation that took place between you and the student.

##Previous Chat History with Student:
{previous_student_chat_history}

##Student Response:
{student_response}

##Your Answer:
"""
        previous_chat_history = previous_chat_history.strip()
        student_response = student_response.strip()

        q_prompt = q_prompt.format(
            previous_student_chat_history = previous_chat_history,
            student_response = student_response,
        )

        response = self._generate_answer(
            prompt = q_prompt,
            return_json=True            
        )
        
        response_message_json_data = json.loads(response)

        final_dict_rv = {
            'student_response': student_response,
            'q_prompt': q_prompt,
            'response': response_message_json_data,
        }
        return final_dict_rv

    def handle_general_tutor_message(self, question, previous_chat_history_str):
        q_prompt = """##Instructions:
You will be a personal tutor primarily for students or individuals who are learning new concepts and fields.
Be as resourceful to them as possible and provide them with as much guidance and help. 
Help the individual develop their own syllabus, lesson plan, questions, quizzes, so they can get a deep understanding of their material.

No Direct Answers: Do not provide direct solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
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

Based on the conversation, try to always ask meaningful follow-up questions to the individual. 
This is a great way to foster a more engaging conversation, and help the individual gain a more deeper understanding of the material they are trying to learn.
However, if you feel the student has received the information they need and there is no meaningful follow-up question you can think of, please close out the conversation by thanking the student and telling them they can ask any other questions if they wish.

##Previous Chat History with Student:
{previous_chat_history_st}

##Student Question:
{question}

##Your Answer:
"""
        
        question = question.strip()
        previous_chat_history_str = previous_chat_history_str.strip()

        q_prompt = q_prompt.format(
            question = question,
            previous_chat_history_st = previous_chat_history_str
        )
        # print(q_prompt)
        
        response = self._generate_answer(
            prompt = q_prompt,
            return_json=False
        )

        final_dict_rv = {
            'student_response': question,
            'q_prompt': q_prompt,
            'response': response,
        }
        return final_dict_rv


    def handle_python_course_gen_message(self, current_student_response_str, previous_student_chat_history_str, user_past_information_dict):

# Here is context on what has been generated for the student thus far, along with past information on the student:
# - Student Goals Information Generated: False
# - Number of Notes Generated: 0
# - Number of Exercises Generated: 0
# - Number of Exercises Completed by Student: 0

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

Student Goals Information Generated:
{student_information_str}

Notes Generated:
{notes_generated_str}

Exercises Generated:
{exercises_generated_str}

Exercises Completed By Student:
{exercises_completed_by_student_str}

Here is the past conversation history with the student, along with their current response:

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

        current_student_response_str = current_student_response_str.strip()
        previous_student_chat_history_str = previous_student_chat_history_str.strip()

# {student_information_str}
# - Notes Generated:
# {notes_generated_str}
# - Exercises Generated:
# {exercises_generated_str}
# - Exercises Completed By Student:
# {exercises_completed_by_student_str}

        # TODO: 
            # add completed exercises string for user

        q_prompt_template = q_prompt_template.format(
            previous_student_chat_history_str = previous_student_chat_history_str,
            current_student_response_str = current_student_response_str,

            student_information_str = user_past_information_dict['student_background_text'],
            notes_generated_str = user_past_information_dict['course_note_text'],
            exercises_generated_str = user_past_information_dict['course_exercise_text'],
            exercises_completed_by_student_str = ''
        )
        
        response = self._generate_answer(
            prompt = q_prompt_template,
            return_json = True
        )
        response_message_json_data = json.loads(response)

        final_dict_rv = {
            'question': current_student_response_str,
            'q_prompt': q_prompt_template,
            'response': response_message_json_data,
        }
        return final_dict_rv



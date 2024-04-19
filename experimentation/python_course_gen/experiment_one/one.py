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

# TODO: 
    # draft experiment prompt and play around / finalize here first 

q_prompt = """##Instructions:
A student will approach you wanting to learn about a specific field/concept.
Your goal is to precisely learn what the student wants to learn, their motivations, and their background.
You goal is NOT to generate a course outline/syllabus. It is simply to learn about the student and what they want to learn.
You will primarily do this through having a natural, genuine conversation with the student.
Please ask follow-up questions and have a genuine conversation with the student.
You MUST only ask ONE QUESTION at a time to the student. This is very important.
ONLY ASK ONE QUESTION AT A TIME.

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

## Student Response:
{student_response}

##Your Answer:
"""

# previouse_student_chat_history = ""
# c = 1
# output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/course_generation_round_two/student_background_conversation_files'
# while True:
#     q_prompt = """##Instructions:
# A student will approach you wanting to learn about a specific field/concept.
# Your goal is to precisely learn what the student wants to learn, their motivations, and their background.
# You goal is NOT to generate a course outline/syllabus. It is simply to learn about the student and what they want to learn.
# You will primarily do this through having a natural, genuine conversation with the student.
# Please ask follow-up questions and have a genuine conversation with the student.
# You MUST only ask ONE QUESTION at a time to the student. This is very important.
# ONLY ASK ONE QUESTION AT A TIME.

# Here are 3 high-level guiding questions on what you can probe the student on:
# 1. What does the student want to learn?
#     - You need to have a deep understanding here on precisely what the student is trying to learn.
#     - Example: If the student says, "symmetric key cryptography to encrypt/decrypt", what do they exactly mean by that?
#         - do they want to learn stream ciphers, one-time pads, block ciphers, or all of it?
#         - do they want a high level understanding of how the algorithms work so they can build something?
#         - do they want a low level understanding of the algorithms and why they are secure?
#         - do they want mathematical proofs of the algorithms, which prove perfect/semantic security?
# 2. Determine what the student's ideal/end state is? (if they have one)
#     - Say they are learning cryptography:
#         - do they want to build a web application, applying crypto algorithms to encrypt/decrypt data?
#         - do they want to implement their own cryptography/block ciphers?
#         - do they want to understand the rigorous mathematical proofs and derive own proofs for similar encryption schemes?
#         - do they want to invent/create new ciphers?
# 3. Determine what their skill level or background is
#     - Say they are learning cryptography:
#         - do they know programming already?
#         - do they have foundational mathematical knowledge already?
    
# Your response MUST BE IN JSON FORMAT, containing the following 2 keys:
# - "final_message" (boolean --> true or false)
#     - Once you feel like you have all the information from the student, set "final_message": True. This will mark the end of the conversation.
#     - The student should be referenced as 3rd person (ie. "the student wants to...") in your final response.
#     - THIS SHOULD ONLY BE SET AS TRUE, ONCE YOU HAVE ASKED ALL FOLLOW-UP QUESTIONS AND HAVE A SOLID UNDERSTANDING OF THE STUDENT.
#         - Otherwise, please set this to false.
# - "response" (this is your actual response string for the student)

# Below, you are given the current student response, along with any previous conversation that took place between you and the student.

# ##Previous Chat History with Student:
# {previous_student_chat_history}

# ## Student Response:
# {student_response}

# ##Your Answer:
# """

#     user_response = input("Question: ")
#     user_response = user_response.strip()

#     q_prompt = q_prompt.format(
#         previous_student_chat_history = previouse_student_chat_history,
#         student_response = user_response,
#     )
#     # print(q_prompt)

#     tmp_fp = os.path.join(output_dir_fp, f"Student-Background-Description-Count-{c}.txt")
#     f = open(tmp_fp, 'w')
#     f.write(q_prompt)
#     f.close()
    
#     c += 1

#     di = {"role": "user", "content": q_prompt}
#     messages_list = [di]
#     chat_completion = client.chat.completions.create(
#         messages = messages_list,
#         # model = "gpt-4",
#         model = "gpt-3.5-turbo-0125",
#     )

#     response_msg_json_str = chat_completion.choices[0].message.content

#     print(f"Response: {response_msg_json_str}")
#     response_message_json_data = json.loads(response_msg_json_str)

#     response_final = response_message_json_data['final_message']
#     response_msg_str = response_message_json_data['response'].strip()

#     if response_final is False:
#         tmp_past_st = f"Student Response: {user_response}\nYour Response: {response_msg_str}\n"
#         previouse_student_chat_history += tmp_past_st
#     else:
#         print(f"Final Response: {response_final}")
#         break

#     # print()
#     # print(response_message_json_data)
#     # print(response_final)
#     # print(response_msg_str)

#     # tmp_past_st = f"Student Response: {user_response}\nYour Response: {response_message}\n"
#     # previouse_student_chat_history += tmp_past_st


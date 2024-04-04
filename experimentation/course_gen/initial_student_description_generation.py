import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI


if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)

API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(
    api_key = API_KEY,
)

# objective/goal
# breadth of background material for AI will be critical

# First: ("Qualify")
    # Determine specifically what the student wants to learn
        # ie. even if they say, 'symmetric key cryptography to encrypt/decrypt', what do they mean?
            # - high level understanding of how the algorithms work so they can build something?
            # - low level understanding of the algorithms and why they are secure
            # - mathematical proofs of the algorithms, which prove perfect/semantic security
    # Determine what their end/ideal state is
        # do they want to build a web application, applying crypto algorithms to encrypt/decrypt data?
        # do they want to implement their own cryptography/block ciphers?
        # do they want to understand the rigorous mathematical proofs and derive own proofs for similar encryption schemes/
        # do they want to invent/create new ciphers?
    # Determine what their skill level is
        # do they know programming already?
        # do they have foundational mathematical knowledge already?

# Based on above: ("Product") (<-- this can be applied to enterprise-AI-development)
    # AI can generate a first 'module', so this is a truly dynamic, interactive course
    # First Module: "XYZ"
        # AI fetches relevant course background material
        # Uses this course background material to then generate a custom module for the student, based on their individual background
        # Module will consist of:
            # Notes
            # Questions/Ideas the Notes 'answer/cover'
            # Exercises
            # Quiz
            # High-level concepts/tags that were covereed 


previouse_student_chat_history = ""
c = 1
output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/gpt_4_output'
while True:

    # Your overall goal is to generate a starting course module for a student.
    # Asking more follow-up questions and probing the student is exactly what you must do.

    q_prompt = """##Instructions:
A student will approach you wanting to learn about a specific field/concept.
Your goal is to determine what the student wants to learn and their background.
Your goal is to precisely learn what the student wants to learn, their motivations, and their background.
You goal is NOT to generate a course outline/syllabus. It is simply to learn about the student and what they want to learn.
You will primarily do this through having a natural, genuine conversation with the student.
Please ask follow-up questions and have a genuine conversation with the student.
You MUST only ask ONE QUESTION at a time to the student. This is very important.
ONLY ASK ONE QUESTION AT A TIME.

Here are 4 high-level guiding questions on what you can probe the student on:
1. What does the student want to learn?
    - You need to have a deep understanding here on precisely what the student is trying to learn.
    - Example: If student says, "symmetric key cryptography to encrypt/decrypt", what do they exactly mean by that?
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
4. What is their expected timeline, IN WEEKS
    - How long do they want 'a potential learning plan / course' to be?
    - How many hours can they dedicate per week?

Once you feel like you have all the information from the student, please output your final response in the list format below:
["your answer..."]

This will mark the end of the conversation.
The student should be referenced in 3rd person (ie. "the student wants to...") in your final answer.
PLEASE ONLY OUTPUT THIS ANSWER AT THE END, ONCE YOU HAVE ASKED ALL FOLLOW-UP QUESTIONS AND HAVE A SOLID UNDERSTANDING OF THE STUDENT.

Below, you are given the current student response, along with any previous conversation that took place between you and the student.

##Previous Chat History with Student:
{previous_student_chat_history}

## Student Response:
{student_response}

##Your Answer:
"""
    
    user_response = input("Question: ")
    user_response = user_response.strip()

    q_prompt = q_prompt.format(
        previous_student_chat_history = previouse_student_chat_history,
        student_response = user_response,
    )
    # print(q_prompt)

    tmp_fp = os.path.join(output_dir_fp, f"Q-Prompt-Round-Four-{c}.txt")
    # f = open(f"Q-Prompt-{c}.txt", 'w')
    f = open(tmp_fp, 'w')
    f.write(q_prompt)
    f.close()
    
    c += 1

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]
    chat_completion = client.chat.completions.create(
        messages = messages_list,
        model = "gpt-4",
        # model = "gpt-3.5-turbo-0125",
    )

    response_message = chat_completion.choices[0].message.content

    print(f"Response: {response_message}")

    tmp_past_st = f"Student Response: {user_response}\nYour Response: {response_message}\n"
    previouse_student_chat_history += tmp_past_st


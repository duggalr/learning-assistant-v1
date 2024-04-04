import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI


# Week 1: Introduction to Cryptography and Symmetric Cryptography
# - Day 1-2: Basics of cryptography and its applications
# - Day 3-4: Overview of symmetric cryptography
# - Day 5: Practical examples and uses of symmetric cryptography"

if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)

API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(
    api_key = API_KEY,
)

q_prompt = """##Instructions:
Your goal is to generate course notes which the student will use, to help them understand the material for the specific week.
The goal here is to generate course notes, specific for the student, given their goals and background.
The goal is for you to generate the course notes in such a manner that make it very easy for the student to understand the material.
Please ensure your course notes for the week are as DETAILED AS POSSIBLE. The more detail, the better for the student.
Please understand that your course notes will be the primary resource for the student, as they are learning the topics for that given week.
Thus, ensure your course notes are as detailed and complete as possible.

Below, you will be given 3 critical pieces of information:
- The student's goals, what they want to learn, and their background.
- You will be given a specific week, which will be your focus for the generation of your course notes.
- You will be given supplementary, relevant material, which you can utilize to help you generate the course notes.

Please output your final response in the list format below:
["Course Notes: ..."]

##Student Goals/Background Information
{student_info}

##Target Week Information
{week_information}

##Supplementary Material
{supplementary_material}

##Your Answer:
"""

student_info = "The student wants to learn about symmetric cryptography and cryptographic hash functions. Their primary purpose is to understand how to programmatically encrypt and decrypt messages with different ciphers using Python. They are primarily interested in constructing simpler encryption and hash algorithms from scratch, aiming to comprehend these topics thoroughly by challenging themselves. While the student does not aim to apply these skills in a specific context right now, they are driven by a curiosity to understand these devices at a fundamental level. They don't currently plan to progress onto complicated aspects of cryptography, but this could potentially change as they delve deeper into the subject. Regarding their background, the student has a good grasp of Python programming and holds fundamental knowledge of mathematics and statistics, which would aid in comprehending cryptographic algorithms and hash functions. The student expects to dedicate 5 weeks to learning this material and will be working a few days a day."
week_info = """Week 1: Understanding Symmetric Cryptography: 
- Definition, purpose and application of Symmetric Cryptography
- Studying popular Symmetric Key Algorithms like Data Encryption Standard (DES) and Advanced Encryption Standard (AES)
- Understanding how encryption and decryption works in Symmetric Cryptography
"""

f_wiki = open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/part_three/wiki_symmetric_encryption.txt', 'r')
wiki_lines = f_wiki.read().strip()

f_tb = open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/part_three/applied_crypto_symmetric_encryption.txt', 'r')
tb_lines = f_tb.read().strip()

jy_tb = open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/part_three/joy_of_crypto_symmetric_encryption.txt', 'r')
jy_lines = jy_tb.read().strip()

supplementary_material = wiki_lines + '\n\n\n' + tb_lines + '\n\n\n' + jy_lines
print(f"Total length of supplementary material text: {len(supplementary_material)}")

q_prompt = q_prompt.format(
    student_info = student_info,
    week_information = week_info,
    supplementary_material = supplementary_material,
)
print(f"Total length of prompt: {len(q_prompt)}")

di = {"role": "user", "content": q_prompt}
messages_list = [di]
chat_completion = client.chat.completions.create(
    messages = messages_list,
    model = "gpt-4-0125-preview",
    # model = "gpt-3.5-turbo-0125",
)

response_message = chat_completion.choices[0].message.content
print(f"Response: {response_message}")


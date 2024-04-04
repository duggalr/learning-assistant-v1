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

q_prompt = """##Instructions:
Your goal is to generate course notes on a specific topic that the student will use, to help them develop a strong understanding of that topic.
Your course notes must be generated such that it is specific for the student, given their goals and background.
The notes should be generated such that, it is very engaging and easy for the student to understand the material.
Please ensure your course notes for the week are as DETAILED AS POSSIBLE. The more detail, the better for the student.

Below, you will be given 3 critical pieces of information:
- The student's goals, what they want to learn, and their background.
- The specific topic to focus your course notes on.
- Additional supplementary material on that topip, which you can utilize to help you generate the course notes.

Please output your final response in the list format below:
["Course Notes: ..."]

##Student Goals/Background Information
{student_info}

##Topic Information
{week_information}

##Supplementary Material
{supplementary_material}

##Your Answer:
"""

student_info_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/course_generation_round_one/student_background.txt'
student_info_file = open(student_info_fp, 'r')
student_info_text = student_info_file.read().strip()

# week_information_text = """Week 1: Fundamentals of Cryptography
# - Definition and Basics of Cryptography
# - Symmetric vs Asymmetric Key Cryptography
# - Importance and real-life application of Cryptography
# - Introduction to Python libraries for cryptography"""

week_information_text = """Week 1: Fundamentals of Cryptography
- Focused Purely On --> Definition and Basics of Cryptography"""

f_wiki = open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material/wiki_symmetric_encryption.txt', 'r')
wiki_lines = f_wiki.read().strip()

f_tb = open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material/applied_crypto_symmetric_encryption.txt', 'r')
tb_lines = f_tb.read().strip()

# jy_tb = open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material/joy_of_crypto_symmetric_encryption.txt', 'r')
# jy_lines = jy_tb.read().strip()

# supplementary_material = wiki_lines + '\n\n\n' + tb_lines + '\n\n\n' + jy_lines
supplementary_material = wiki_lines + '\n\n\n' + tb_lines + '\n\n\n'
print(f"Total length of supplementary material text: {len(supplementary_material)}")

q_prompt = q_prompt.format(
    student_info = student_info_text,
    week_information = week_information_text,
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
# print(f"Response: {response_message}")

output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/course_generation_round_one'
# tmp_fp = os.path.join(output_dir_fp, f"week_one_full_course_notes.txt")
tmp_fp = os.path.join(output_dir_fp, f"week_one_topic_one_course_notes.txt")
f = open(tmp_fp, 'w')
f.write(response_message)
f.close()

# TODO: 
    # Keep experimenting here and main_four
        # generation of the course notes + quiz/exercises <-- **need more relevant resources for course-note and quiz/exercise gen**
        # once I have intuitive feel that this is good V1
            # implement in app and literally use it to learn something
            # go from there...

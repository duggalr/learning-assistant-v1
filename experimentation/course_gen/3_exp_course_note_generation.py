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

# q_prompt = """##Instructions:
# Your goal is to generate course notes on a specific topic that the student will use, to help them develop a strong understanding of that topic.
# Your course notes must be generated such that it is specific for the student, given their goals and background.
# The notes should be generated such that, it is very engaging and easy for the student to understand the material.
# Please ensure your course notes for the week are as DETAILED AS POSSIBLE. The more detail, the better for the student.
# For context, you will also be given the planned topics to be covered for next week but DO NOT GENERATE ANY NOTES FOR NEXT WEEK.
# The full focus for your course notes will be for the current  week.
# As mentioned below, to help you generate detailed notes, you will be given additional, relevant supplementary material from different textbooks and wikipedia.
# Please leverage this supplementary material for your course note generation.

# Below, you will be given 3 critical pieces of information:
# - The student's goals, what they want to learn, and their background.
# - The specific topic to focus your course notes on.
# - Additional supplementary material on that topic, which you can leverage to help you generate the course notes.

# Please output your final response in the list format below:
# ["Course Notes: ..."]

# ##Student Goals/Background Information
# {student_info}

# ##Current Week Topic Information
# {week_information}

# ##Next Week Topic Information
# {next_week_information}

# ##Supplementary Material
# {supplementary_material}

# ##Your Answer:
# """


q_prompt = """##Instructions:
You will be given a student's course outline, along with the specific module the student is currently working on.
Your goal is to generate course notes ONLY ON THE CURRENT MODULE the student is working on.
The goal of the course notes will be to help the student develop a strong understanding of that topic.

Your course notes must be generated such that it is specific for the student, given their goals and background.
The notes should be generated such that, it is very engaging and easy for the student to understand the material.
Please ensure your course notes for the module are as DETAILED AS POSSIBLE. The more detail, the better for the student.

DO NOT GENERATE ANY NOTES FOR FUTURE MODULES. ONLY FOCUS ON THE CURRENT MODULE.
As mentioned below, to help you generate detailed notes, you will be given additional, relevant supplementary material from different textbooks and wikipedia.
Please leverage this supplementary material for your course note generation.

Below, you will be given 3 critical pieces of information:
- The student's goals, what they want to learn, and their background.
- The specific topic to focus your course notes on.
- Additional supplementary material on that topic, which you can leverage to help you generate the course notes.

Please output your final response in the list format below:
["Course Notes: ..."]

##Student Goals/Background Information
{student_info}

##Course Outline
{course_outline}

##Current Week Topic Information
{week_information}

##Supplementary Material
{supplementary_material}

##Your Answer:
"""

# student_info_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/course_generation_round_one/student_background.txt'
# student_info_file = open(student_info_fp, 'r')
# student_info_text = student_info_file.read().strip()

# # week_information_text = """Week 1: Fundamentals of Cryptography
# # - Definition and Basics of Cryptography
# # - Symmetric vs Asymmetric Key Cryptography
# # - Importance and real-life application of Cryptography
# # - Introduction to Python libraries for cryptography"""

# week_information_text = """Week 1: Fundamentals of Cryptography
# - Definition and Basics of Cryptography
# - Symmetric vs Asymmetric Key Cryptography
# - Importance and real-life application of Cryptography
# - Introduction to Python libraries for cryptography"""

# next_week_information_text = """Week 2: Basics of Ciphers
# - Historical overview and types of ciphers
# - Working of a basic cipher (Caesar Cipher)
# - Python implementation of a basic cipher
# - Decoding of a Caesar cipher"""

# # f_wiki = open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material/wiki_symmetric_encryption.txt', 'r')
# # wiki_lines = f_wiki.read().strip()

# # f_tb = open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material/applied_crypto_symmetric_encryption.txt', 'r')
# # tb_lines = f_tb.read().strip()

# # jy_tb = open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material/joy_of_crypto_symmetric_encryption.txt', 'r')
# # jy_lines = jy_tb.read().strip()

# # # supplementary_material = wiki_lines + '\n\n\n' + tb_lines + '\n\n\n' + jy_lines
# # supplementary_material = wiki_lines + '\n\n\n' + tb_lines + '\n\n\n'
# # print(f"Total length of supplementary material text: {len(supplementary_material)}")


student_background = 'It seems like the student is interested in implementing their own SMTP server in Python.'
course_outline = """Course Name:
Building an SMTP Server in Python

Course Description:
This course will guide you through the process of building your own SMTP server using Python. The modules are designed to help you understand networking concepts, delve into the SMTP protocol, and implement a functional server by the end of the course.

Module 1: Introduction to Networking Concepts - Part 1
- Understanding basic networking terminologies
- Overview of client-server architecture

Module 2: Introduction to Networking Concepts - Part 2
- Introduction to TCP/IP and sockets
- Network communication basics

Module 3: Deep Dive into the SMTP Protocol
- Understanding the SMTP protocol
- SMTP commands and responses
- Hands-on exercises on sending emails using SMTP

Module 4: Parsing Incoming Email Requests
- What is meant by incoming email requests
- Processing email headers and body
- Validating email content

Module 5: Building the SMTP Server - Part 2
- Implementing SMTP message transfer functionality
- Error handling and response codes
- Integrating security features such as TLS/SSL

Module 6: Advanced Topics and Troubleshooting
- Load testing your SMTP server
- Implementing additional SMTP extensions
- Troubleshooting common server issues

Note:
- Feel free to suggest any modifications or areas where you would like to focus more based on your progress and interests. Remember, the course outline is flexible and can be adapted to suit your learning pace and goals.
"""
current_week_information = """Module 1: Introduction to Networking Concepts - Part 1
Understanding basic networking terminologies
Overview of client-server architecture"""

supplementary_material = ""
supp_material_dir = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material/second/pdf_files'
supp_material_files = os.listdir(supp_material_dir)

final_supplementary_material_string = ""
for fn in supp_material_files:
    if '.txt' in fn:
        print(fn)
        # text_file_name_list.append(os.path.join(supp_material_dir, fn))
        fn_text = open(os.path.join(supp_material_dir, fn), 'r').read().strip()
        final_supplementary_material_string += fn_text

# print(final_supplementary_material_string)
print(f"length of string: {len(final_supplementary_material_string)}")

# q_prompt = q_prompt.format(
#     student_info = student_info_text,
#     week_information = week_information_text,
#     next_week_information = next_week_information_text,
#     supplementary_material = final_supplementary_material_string,
# )

q_prompt = q_prompt.format(
    student_info = student_background,
    course_outline = course_outline,
    week_information = current_week_information,
    supplementary_material = final_supplementary_material_string,
)
print(f"Total length of prompt: {len(q_prompt)}")
# print(q_prompt)

di = {"role": "user", "content": q_prompt}
messages_list = [di]
chat_completion = client.chat.completions.create(
    messages = messages_list,
    model = "gpt-4-0125-preview",
    # model = "gpt-3.5-turbo-0125",
)


response_message = chat_completion.choices[0].message.content
# # print(f"Response: {response_message}")

output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/course_generation_round_three'
# tmp_fp = os.path.join(output_dir_fp, f"week_one_full_course_notes.txt")
tmp_fp = os.path.join(output_dir_fp, f"course_notes_module_one.txt")
f = open(tmp_fp, 'w')
f.write(response_message)
f.close()


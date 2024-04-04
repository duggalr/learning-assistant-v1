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
Below, you will given a description of a student below, along with what they want to learn, their background, along with their
approximate duration/timeline for completion.

Your goal is to leverage this information to generate a course outline for the student.
The course outline should be split scheduled for a weekly basis dependent upon the student's timeline.
Each week should describe what topic will be covered.
Ensure the topic in each week does not cover too much information, but at the same time, it doesn't cover too little information either.
Feel free to add sub-topics under a week, to provide more clarity for the user on what will be covered.
Don't add "days under any specific week", but feel free to additional additional information/concepts that may be covered for that week.
Also, in the beginning, please add a brief description describing what the course outline entails and why you set it up this way.

Please output your final response in the list format below:
["Description...", "Week 1: ...", "Week 2: ...", ...]

##Student Information
{student_info}

##Your Answer:
"""

student_info = "The student wants to learn about symmetric cryptography and cryptographic hash functions. Their primary purpose is to understand how to programmatically encrypt and decrypt messages with different ciphers using Python. They are primarily interested in constructing simpler encryption and hash algorithms from scratch, aiming to comprehend these topics thoroughly by challenging themselves. While the student does not aim to apply these skills in a specific context right now, they are driven by a curiosity to understand these devices at a fundamental level. They don't currently plan to progress onto complicated aspects of cryptography, but this could potentially change as they delve deeper into the subject. Regarding their background, the student has a good grasp of Python programming and holds fundamental knowledge of mathematics and statistics, which would aid in comprehending cryptographic algorithms and hash functions. The student expects to dedicate 5 weeks to learning this material and will be working a few days a day."
q_prompt = q_prompt.format(
    student_info = student_info
)

output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen'
tmp_fp = os.path.join(output_dir_fp, f"Course-Outline-Gen-Round-Three.txt")
f = open(tmp_fp, 'w')
f.write(q_prompt)
f.close()

di = {"role": "user", "content": q_prompt}
messages_list = [di]
chat_completion = client.chat.completions.create(
    messages = messages_list,
    # model = "gpt-4",
    model = "gpt-3.5-turbo-0125",
)

response_message = chat_completion.choices[0].message.content
print(f"Response: {response_message}")



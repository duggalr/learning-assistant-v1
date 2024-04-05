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
The course outline should be split over a weekly basis.
Each week should describe what topic will be covered.
Ensure the topic in each week does not cover too much information, but at the same time, it doesn't cover too little information either.
Each week should contain sub-topics, to provide more clarity for the student on what will be covered.
Don't add "days under any specific week".
Also, in the beginning of your answer, please add a brief description describing what the course outline entails and why you set it up this way.
This course outline is dynamic and can change, depending the student's progress and interests so please do mention that in your description.

Please output your final response in the list format below:
["Description...", "Week 1: ...", "Week 2: ...", ...]

##Student Information
{student_info}

##Your Answer:
"""

student_info_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/course_generation_round_one/student_background.txt'
student_info_file = open(student_info_fp, 'r')
student_info_text = student_info_file.read().strip()
q_prompt = q_prompt.format(
    student_info = student_info_text
)

di = {"role": "user", "content": q_prompt}
messages_list = [di]
chat_completion = client.chat.completions.create(
    messages = messages_list,
    model = "gpt-4",
    # model = "gpt-3.5-turbo-0125",
)

response_message = chat_completion.choices[0].message.content
# print(f"Response: {response_message}")

output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/course_gen/course_generation_round_one'
tmp_fp = os.path.join(output_dir_fp, f"course_outline.txt")
f = open(tmp_fp, 'w')
f.write(response_message)
f.close()


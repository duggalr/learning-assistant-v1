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

while True:
    
    q_prompt = """##Instructions:
Below, you will given a description of a student, specifically what they want to learn, why they want to learn it, and their background on that topic.

Your goal is to leverage this information to generate a course outline for the student.
The course outline should be split by a modular basis.
Each module will represent a specific topic that the student will learn.
Ensure each module does not cover too much information but at the same time, it doesn't cover too little information either.
Each module should contain sub-topics, to provide more clarity for the student on what will be covered.
Please also add a name for the course.
Please also add a brief description describing what the course outline entails and why you set it up this way.
This course outline is dynamic and can change, depending on the student's progress and interests so please do mention that in your description.

The course outline MUST BE GENERATED in Markdown Format.
For your markdown course outline, please include the name of the course and description at the top (in markdown), before the remaining outline.

You will also be given any past chat history with the student, along with a current student response (if any).
The student may provide feedback for the course outline you generate.
Please incorporate this feedback, as you generate the course outline.
If there is a student response and you want to respond back, you can add that response to the "message_to_student" key in your JSON output below.

Your response MUST BE OUTPUTED IN JSON FORMAT, containing the following 3 keys:
- "name"
    - This value will be the name of the course.
- "description"
    - This value will be the description of the course.
- "outline"
    - This will be the course outline IN MARKDOWN FORMAT, which will be presented to the student.
        - Please ensure at the beginning of your markdown, you include the Course Name and Description, before you include your outline.
        - The Course Name and Course Description must be included in our generated Course Outline Markdown, at the top.
- "message_to_student"
    - This value will be where you can respond to the student, if they have sent any current question/response.

##Student Information
{student_info}

##Previous Chat History with Student:
{previous_student_chat_history}

##Current Student Response:
{student_response}

##Your Answer:
"""




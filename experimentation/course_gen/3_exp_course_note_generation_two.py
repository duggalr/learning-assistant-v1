import os
from dotenv import load_dotenv, find_dotenv
import pickle
import numpy as np
import faiss
from openai import OpenAI


if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)

API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(
    api_key = API_KEY,
)


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding


def get_top_k_supplementary_material(embd, k = 3):
    D, I = index.search(embd, k)
    # print(I)
    rv = []
    for idx in I[0]:
        file_dict = final_file_list[idx]
        # fp = file_dict['file_path']
        f = open(f'tmp_{idx}.txt', 'w')
        f.write(f"{file_dict['file_path']}\n\n | {file_dict['batch_text']}")
        f.close()
        batch_text = file_dict['batch_text'].strip()
        rv.append(batch_text)
    return rv



def generate_note(note_info_dict):
    q_prompt = """##Instructions:
You will be given a student's course outline, along with the specific module the student is currently working on.
Your goal is to generate course notes ONLY ON THE CURRENT MODULE the student is working on.
The goal of the course notes will be to help the student develop a strong understanding of that topic.

Your course notes must be generated such that it is specific for the student, given their goals and background.
The notes should be generated such that, it is very engaging and easy for the student to understand the material.
Please ensure your course notes for the module are as DETAILED AS POSSIBLE. The more detail, the better for the student.

DO NOT GENERATE ANY NOTES FOR FUTURE MODULES. ONLY FOCUS ON THE CURRENT MODULE.
As mentioned below, to help you generate detailed notes, you will be given additional, relevant supplementary material from different textbooks and wikipedia.
Please use this supplementary material for your course note generation.
Please note that your course notes will be the primary resource for the student, so ensure they are very detailed, rich with examples.

DO NOT PROVIDE ANY REFERENCES OR CITATIONS FOR YOUR COURSE NOTES. Simply generate detailed, relevant notes for the student.

Below, you will be given 4 critical pieces of information:
- The student's goals, what they want to learn, and their background.
- The outline of the course the student is currently taking.
- The specific topic to focus your course notes on.
- Additional supplementary material on that topic, which you can leverage to help you generate the course notes.

Your response MUST BE OUTPUTED IN JSON FORMAT, containing the following key:
- "course_notes"
    - This will be the course notes IN MARKDOWN FORMAT, which will be presented to the student.
    - Please ensure at the beginning of your markdown, you include the Current Module Name and SubTopics that will be covered, before you include your notes.

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

    q_prompt = q_prompt.format(
        student_info = note_info_dict['student_info'],
        course_outline = note_info_dict['course_outline'],
        week_information = note_info_dict['week_information'],
        supplementary_material = note_info_dict['supplementary_material'],
    )

    output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/ai_note_gen/five'
    tmp_fp = os.path.join(output_dir_fp, f"q_prompt.txt")
    f = open(tmp_fp, 'w')
    f.write(q_prompt)
    f.close()

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]
    chat_completion = client.chat.completions.create(
        messages = messages_list,
        model = "gpt-4-0125-preview",
        # model = "gpt-3.5-turbo-0125",
    )    

    response_message = chat_completion.choices[0].message.content
    # # print(f"Response: {response_message}")

    output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/ai_note_gen/five'
    tmp_fp = os.path.join(output_dir_fp, f"course_notes_gpt_4.txt")
    f = open(tmp_fp, 'w')
    f.write(response_message)
    f.close()



def generate_note_no_supplementary_info(note_info_dict):
    q_prompt = """##Instructions:
You will be given a student's course outline, along with the specific module the student is currently working on.
Your goal is to generate course notes ONLY ON THE CURRENT MODULE the student is working on.
The goal of the course notes will be to help the student develop a strong understanding of that topic.

Your course notes must be generated such that it is specific for the student, given their goals and background.
The notes should be generated such that, it is very engaging and easy for the student to understand the material.
Please ensure your course notes for the module are as DETAILED AS POSSIBLE. The more detail, the better for the student.

DO NOT GENERATE ANY NOTES FOR FUTURE MODULES. ONLY FOCUS ON THE CURRENT MODULE.

DO NOT PROVIDE ANY REFERENCES OR CITATIONS FOR YOUR COURSE NOTES. Simply generate detailed, relevant notes for the student.

Below, you will be given 3 critical pieces of information:
- The student's goals, what they want to learn, and their background.
- The outline of the course the student is currently taking.
- The specific topic to focus your course notes on.

Your response MUST BE OUTPUTED IN JSON FORMAT, containing the following key:
- "course_notes"
    - This will be the course notes IN MARKDOWN FORMAT, which will be presented to the student.
    - Please ensure at the beginning of your markdown, you include the Current Module Name and SubTopics that will be covered, before you include your notes.

##Student Goals/Background Information
{student_info}

##Course Outline
{course_outline}

##Current Week Topic Information
{week_information}

##Your Answer:
"""

    q_prompt = q_prompt.format(
        student_info = note_info_dict['student_info'],
        course_outline = note_info_dict['course_outline'],
        week_information = note_info_dict['week_information'],
    )

    output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/ai_note_gen/six'
    tmp_fp = os.path.join(output_dir_fp, f"q_prompt.txt")
    f = open(tmp_fp, 'w')
    f.write(q_prompt)
    f.close()

    di = {"role": "user", "content": q_prompt}
    messages_list = [di]
    chat_completion = client.chat.completions.create(
        messages = messages_list,
        model = "gpt-4-0125-preview",
        # model = "gpt-3.5-turbo-0125",
    )    

    response_message = chat_completion.choices[0].message.content
    # # print(f"Response: {response_message}")

    output_dir_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/ai_note_gen/six'
    tmp_fp = os.path.join(output_dir_fp, f"course_notes_gpt_4.txt")
    f = open(tmp_fp, 'w')
    f.write(response_message)
    f.close()




if __name__ == "__main__":
    # student_background = 'It seems like the student is interested in implementing their own SMTP server in Python. The student has experience in Python but does not have much knowledge in network protocols or SMTP.'
    student_background = "The student wants to learn the foundations of AI, specifically Machine Learning and Deep Learning. They also want to apply this knowledge to real-world applications using LLMs such as GPT."
    course_outline = """Course Name:
Introduction to Artificial Intelligence and Machine Learning

Course Description:
Module 1: Introduction to Artificial Intelligence
- What is Artificial Intelligence?
- Overview of AI applications
- Ethics and impact of AI

Module 2: Fundamentals of Machine Learning
- Introduction to machine learning
- Supervised, unsupervised, and reinforcement learning
- Training and testing models

Module 3: Neural Networks and Deep Learning
- Understanding neural networks
- Deep learning concepts
- Building and training neural networks

Module 4: AI Applications
- Real-world applications of AI
- Case studies
- Project planning

Module 5: Large Language Models and GPT
- Overview of large language models like GPT
- Understanding GPT-3
- Practical applications of GPT

Module 6: Building AI Applications with GPT API
- Introduction to GPT API
- Implementing GPT API in projects
- Developing a simple application using GPT API
"""
    current_week_information = """Fundamentals of Machine Learning
- Supervised, unsupervised, and reinforcement learning"""

    print(f"Opening all Pickle Files...")

    with open('/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/scripts/final_file_list.pkl', 'rb') as f:
        final_file_list = pickle.load(f)

    print(f"Total number of supplementary passages: {len(final_file_list)}")
    
    index_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/scripts/embedding.index'
    index = faiss.read_index(index_fp)
    
    print(f"Index ntotal: {index.ntotal}")

    current_week_info_embedding = get_embedding(
        text = current_week_information,
    )
    current_week_info_embedding = np.array(current_week_info_embedding)
    current_week_info_embedding = current_week_info_embedding.reshape(1, current_week_info_embedding.shape[0])
    print(current_week_info_embedding)
    print(current_week_info_embedding.shape)

    # supplementary_material_list = get_top_k_supplementary_material(
    #     embd = current_week_info_embedding,
    #     k = 4
    # )

    # supplementary_material_str = '\n'.join(supplementary_material_list)
    # print(f"Total length of supplementary material: {len(supplementary_material_str)}")
    
    note_dict = {
        'student_info': student_background,
        'course_outline': course_outline,
        'week_information': current_week_information,
        # 'supplementary_material': supplementary_material_str
    }

    # generate_note(note_dict)
    generate_note_no_supplementary_info(note_dict)


# TODO:
    # notes seem reasonable for now
        # determine how to expand the knowledge-base <-- wiki is solid source (a lot of data to embed though?)
            # go from there



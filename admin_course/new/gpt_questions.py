import os
import ast
import openai
from dotenv import load_dotenv
load_dotenv()



api_key = "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"
openai.api_key = api_key

f = open('preliminary_questions.txt')
lines = f.readlines()

# ex = lines[1].strip()
# print(ex)

for idx in range(0, len(lines), 5):

    start_idx = idx
    end_idx = idx + 5
    print(f"On Range: {start_idx} - {end_idx}")
    batch_string = '\n'.join([ln.strip() for ln in lines[start_idx:end_idx]])

    batch_prompt_question = """# Question:
For each of the questions below, can you turn this into a json dict,  where I have the question name, question text, and test cases in a list of dictionaries with input / output.
Example output: 

`[{'question_name': '...', 'question_text': '...', 'question_test_cases': [{'input': ..., 'output'}, {...}]}, {...}]`

# Text:
""" 
    batch_prompt_question = batch_prompt_question + batch_string
    # print(batch_prompt_question)

    message_list = [{
        'role': 'user',
        'content': batch_prompt_question
    }]

    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo-16k-0613",
        messages = message_list,
    )

    response_content = response['choices'][0]['message']['content']
    f = open(f"prompt_response_{start_idx}_{end_idx}.txt", "w")
    f.write(response_content)
    f.close()




# full_ex_string = '\n'.join([ln.strip() for ln in lines[1:]])

# # Personalized Greeting | Create a program that asks the user for their name and then prints a greeting using their name (i.e., "Hello" + name). | Test Case 1: Input: John --> Output: Hello John, Test Case 2: Input: Alice --> Output: Hello Alice, Test Case 3: Input: Bob --> Output: Hello Bob, Test Case 4: Input: Sarah --> Output: Hello Sarah
# prompt_question = f"""# Question:
# For each of the questions below, can you turn this into a json dict,  where I have the question name, question text, and test cases in a list of dictionaries with input / output.

# # Text:
# {full_ex_string}
# """

# print(prompt_question)

# message_list = [{
#     'role': 'user',
#     'content': prompt_question
# }]

# response = openai.ChatCompletion.create(
#     model = "gpt-3.5-turbo-16k-0613",
#     messages = message_list,
# )

# response_content = response['choices'][0]['message']['content']
# f = open("prompt_response.txt", "w")
# f.write(response_content)
# f.close()


# lesson_obj_new = Lesson.objects.create(
#     title = 'new_void'
# )
# lesson_obj_new.save()

# response_dict = response['choices'][0]['message']['content']
# mod_response_list = ast.literal_eval(response_dict)
# for mod_di in mod_response_list:
#     question_name = mod_di['question_name']
#     question_text = mod_di['question_text']
#     question_test_cases = mod_di['test_cases']

#     lq_obj = LessonQuestion.objects.create(
#         question_name = question_name, 
#         question_text = question_text,
#         lesson_obj = lesson_obj_new
#     )
#     lq_obj.save()

#     for tc in question_test_cases:
#         lq_tc_obj = LessonQuestionTestCase.objects.create(
#             lesson_question_obj = lq_obj,
#             test_case_full_text = tc
#         )
#         lq_tc_obj.save()




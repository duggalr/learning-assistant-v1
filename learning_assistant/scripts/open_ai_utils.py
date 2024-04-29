"""
File containing all the Classes/Methods corresponding to the OpenAI API
"""
import os
import json
import logging
import tiktoken
from openai import OpenAI


# TODO: conversation length is hardcoded for now
MAX_CONVERSATION_HISTORY_LENGTH = 5

class BaseOpenAIWrapper(object):
    """
    """
    def __init__(self) -> None:
        # self.model_name = "gpt-4"
        # self.model_name = "gpt-3.5-turbo-0125"
        self.model_name = "gpt-4-0125-preview"
        self.api_key = os.environ['OPENAI_API_KEY']
        self.encoding = tiktoken.encoding_for_model(self.model_name)
        self.client = OpenAI(
            api_key = self.api_key
        )


class TokenCount(BaseOpenAIWrapper):
    """
    """
    def get_token_count(self, string) -> int:
        num_tokens = len(self.encoding.encode(string))
        return num_tokens


class ModelCompletion(BaseOpenAIWrapper):
    """
    """

    def __init__(self) -> None:
        super().__init__()
        self.token_count = TokenCount()

    def _generate_answer(self, prompt, return_json = True):
        prompt_token_count = self.token_count.get_token_count(
            string = prompt
        )
        if prompt_token_count >= 120000:  # TODO: expect this to not happen which is why I'm handling it like this right now
            logging.error(f"Prompt had 120k tokens or more!\n\n{prompt}")
            raise NotImplementedError

        di = {"role": "user", "content": prompt}
        messages_list = [di]
        if return_json:
            chat_completion = self.client.chat.completions.create(
                messages = messages_list,
                model = self.model_name,
                response_format={ "type": "json_object" }
            )
        else:
            chat_completion = self.client.chat.completions.create(
                messages = messages_list,
                model = self.model_name,
            )
        
        response_message = chat_completion.choices[0].message.content

        rv = {
            'prompt_token_count': prompt_token_count,
            'response': response_message
        }
        return rv

    def handle_general_tutor_message(self, question, previous_chat_history_str):
        q_prompt = """##Instructions:
You will be a personal tutor primarily for students or individuals who are learning new concepts and fields.
Be as resourceful to them as possible and provide them with as much guidance and help. 
Help the individual develop their own syllabus, lesson plan, questions, quizzes, so they can get a deep understanding of their material.

No Direct Answers: Do not provide direct solutions to the students' questions or challenges. Instead, focus on providing hints, explanations, and guidance that help them understand and solve the problems on their own. For questions students ask, don't simply provide the answer. Instead, provide a hint and try to ask the student a follow-up question/suggestion. Under no circumstance should you provide the student a direct answer to their problem/question.
Encourage Problem Solving: Always encourage the students to think through the problems themselves. Ask leading questions that guide them toward a solution, and provide feedback on their thought processes.

##Example Student Question:
list_one = [2,23,523,1231,32,9]
total_product = 0
for idx in list_one:
    total_product = idx * idx

I'm confused here. I am multiplying idx and setting it to total_product but getting the wrong answer. What is wrong?

##Example Bad Answer (Avoid this type of answer):
You are correct in iterating through the list with the for loop but at the moment, your total_product is incorrectly setup. Try this instead:
list_one = [2,23,523,1231,32,9]
total_product = 1
for idx in list_one:
    total_product = total_product * idx

##Example Good Answer: (this is a good answer because it identifies the mistake the student is making but instead of correcting it for the student, it asks the student a follow-up question as a hint, forcing the student to think on their own)
You are on the right track. Pay close attention to the operation you are performing in the loop. You're currently multiplying the number with itself, but you want to find the product of all numbers. What operation should you use instead to continuously update 'total_product'?

Based on the conversation, try to always ask meaningful follow-up questions to the individual. 
This is a great way to foster a more engaging conversation, and help the individual gain a more deeper understanding of the material they are trying to learn.
However, if you feel the student has received the information they need and there is no meaningful follow-up question you can think of, please close out the conversation by thanking the student and telling them they can ask any other questions if they wish.

##Previous Chat History with Student:
{previous_chat_history_st}

##Student Question:
{question}

##Your Answer:
"""

        question = question.strip()
        previous_chat_history_str = previous_chat_history_str.strip()

        q_prompt = q_prompt.format(
            question = question,
            previous_chat_history_st = previous_chat_history_str
        )

        response = self._generate_answer(
            prompt = q_prompt,
            return_json=False
        )

        prompt_token_count = response['prompt_token_count']
        model_response = response['response']

        final_dict_rv = {
            'prompt_token_count': prompt_token_count,
            'student_response': question,
            'q_prompt': q_prompt,
            'response': model_response,
        }
        return final_dict_rv

    def handle_playground_code_question(self, question, student_code, previous_chat_history, student_code_output):
        prompt = """##Instructions:
You will be a personal tutor for students, who are learning new concepts.
The student will provide you with a question, along with their code from the IDE and the problem they are working.
You will also be given the output from the execution of the code the student wrote.

Your goal is to help the student solve their question and problem they are working are.
You must NOT GIVE DIRECT ANSWERS.
- Focus on providing meaningful hints, explanations, and guidance that will help the student understand and solve the problem on their own.
- Your goal is to be that resource that will provide an additional insight/guidance that the student is overlooking or may not know about.
- Do not provide direct solutions to the students' questions or challenges.
- UNDER NO CIRCUMSTANCE should you provide the student with a direct answer to their problem/question.
- ONLY PROVIDE 1 PIECE OF INFORMATION OR QUESTION AT A TIME. This will make it easier for the student to understand.

WHEN EXPLAINING CONCEPTS OR DEMONSTRATING A FLAW IN THE STUDENT'S CODE, PROVIDE EXAMPLES.
- If you notice the student is struggling to understand a particular concept, PROVIDE A LITERAL EXAMPLE DEMONSTRATING THE CONCEPT.
    - This will make it much easier for the student to understand the concept.
- If you notice the student's code is potentially wrong for a certain case, PROVIDE A COUNTEREXAMPLE DEMONSTRATING AN INPUT WHERE THE STUDENT'S CODE WILL FAIL TO RUN.
    - This is critical as it will then help the student create a more robust solution.

- If the student has achieved the correct answer and has solved the problem, INFORM THE STUDENT THEY HAVE SUCCESSFULLY SOLVED THE PROBLEM.
- If you feel the student has received the information they need and there is no meaningful follow-up question you can think of, please close out the conversation by thanking the student and telling them they can ask any other questions if they wish.

##Previous Chat History with Student:
{previous_chat_history_st}

##Student Code:
{student_code}

##Student Code Output:
{student_code_output}

##Current Student Question:
{question}

##Your Answer:
"""

        question = question.strip()
        student_code = student_code.strip()
        student_code_output = student_code_output.strip()
        prompt = prompt.format(
            previous_chat_history_st = previous_chat_history,
            question = question,
            student_code = student_code,
            student_code_output = student_code_output
        )

        response = self._generate_answer(
            prompt = prompt,
            return_json = False
        )

        prompt_token_count = response['prompt_token_count']
        model_response = response['response']

        final_dict_rv = {
            'prompt_token_count': prompt_token_count,
            'question': question,
            'q_prompt': prompt,
            'response': model_response,
        }
        return final_dict_rv

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
Your goal is to generate a quiz and exercises, given the course notes below.
The quiz and exercises should be relevant to the user's goals/background, which will also be provided.
The questions and exercises should be well thought out, really probing a deep understanding for the student.

##Student Goals/Background Information
{student_info}

##Course Notes
{course_note_information}

Please output your final response in the list format below:
["Quiz Questions + Answers", "Exercises"]

##Your Answer:
"""

student_info = "The student wants to learn about symmetric cryptography and cryptographic hash functions. Their primary purpose is to understand how to programmatically encrypt and decrypt messages with different ciphers using Python. They are primarily interested in constructing simpler encryption and hash algorithms from scratch, aiming to comprehend these topics thoroughly by challenging themselves. While the student does not aim to apply these skills in a specific context right now, they are driven by a curiosity to understand these devices at a fundamental level. They don't currently plan to progress onto complicated aspects of cryptography, but this could potentially change as they delve deeper into the subject. Regarding their background, the student has a good grasp of Python programming and holds fundamental knowledge of mathematics and statistics, which would aid in comprehending cryptographic algorithms and hash functions. The student expects to dedicate 5 weeks to learning this material and will be working a few days a day."
course_notes_text = """"Course Notes: Understanding Symmetric Cryptography",

"**Week 1 Objective**: Our goal this week is to lay a solid foundation of understanding symmetric cryptography, focusing on its definition, purpose, applications, and delving into the workings of symmetric key algorithms such as Data Encryption Standard (DES) and Advanced Encryption Standard (AES). Through this week's study, students will gain insight into the encryption and decryption processes in symmetric cryptography and understand how symmetric key algorithms serve in secure communication protocols.",

"### Definition of Symmetric Cryptography",
"Symmetric Cryptography, also known as symmetric-key encryption, involves the use of a single key for both encryption and decryption processes. This means that both the sender and receiver must possess the same key, and keep it secret, to successfully decrypt the encrypted message.",

"### Purpose and Application",
"The primary purpose of symmetric cryptography is to ensure confidentiality encryption provides. It is widely used in various areas such as securing the connection between web servers and clients (SSL/TLS), encryption of data at rest (file or database encryption), and in the banking sector for PIN and ATM encryption. Symmetric encryption algorithms are generally faster and less complex than their asymmetric counterparts, making them suitable for encrypting large volumes of data.",

"### Popular Symmetric Key Algorithms",
"1. **Data Encryption Standard (DES)**: Developed in the early 1970s, DES was among the first standard symmetric encryption algorithms. DES encrypts data in 64-bit blocks using a 56-bit key. Despite its wide use historically, DES's shorter key length makes it vulnerable to brute-force attacks today.",
"2. **Advanced Encryption Standard (AES)**: AES, selected by NIST in 2001, replaced DES as the standard for symmetric key encryption. AES is more secure than DES, supporting key lengths of 128, 192, and 256 bits and encrypting data in 128-bit blocks. Due to its security and efficiency, AES is used globally to protect sensitive information.",

"### Understanding Encryption and Decryption in Symmetric Cryptography",
"In symmetric cryptography, encryption and decryption involve processing the plaintext and ciphertext with the same secret key. The process can be boiled down to mathematical functions and algorithms that convert plaintext into ciphertext (encryption) and back into plaintext (decryption), using the symmetric key. The security of symmetric encryption lies in the secrecy of the symmetric key.",

"**Encryption Process**:",
"1. Plaintext is input into the encryption algorithm along with the symmetric key.",
"2. The algorithm performs a series of complex computations and transformations on the plaintext.",
"3. The output is the encrypted data, known as ciphertext.",

"**Decryption Process**:",
"1. Ciphertext is input into the decryption algorithm along with the same symmetric key used for encryption.",
"2. The algorithm reverses the encryption processes and computations.",
"3. The output is the original plaintext.",

"**Key Points to Remember**:",
"- The security of symmetric encryption heavily relies on the secrecy of the key.",
"- Key management is crucial; securely exchanging and storing the symmetric key is a major concern.",
"- Symmetric algorithms are generally faster than asymmetric algorithms and are suited for encrypting large amounts of data.",

"### Conclusion",
"This week's study establishes a basic understanding of symmetric cryptography, covering its purpose, application, and the inner workings of DES and AES. Asymmetric cryptography and cryptographic hash functions will be explored in the coming weeks, further enriching the student's knowledge in the field of cryptography.",
"""

q_prompt = q_prompt.format(
    student_info = student_info,
    course_note_information = course_notes_text
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


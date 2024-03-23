import tokenize
from io import BytesIO
from collections import deque


code_string = """
# Run the code by clicking the button above
# If you need any help, ask the AI to provide guidance

# Programming Question:
# Write your question here...

# Write your code below:

def function_one(x, y):
	# return x + y
    import os
    print(os.listdir('.'))
    return os.listdir('.')

"""

# file = BytesIO(code_string.encode())
# tokens = deque(tokenize.tokenize(file.readline))

def extract_function_from_string(content):
    import ast
    tree = ast.parse(content, mode='exec')
    print(tree.body)
    function = tree.body[0]
    module = ast.Module([function], [])
    print(module)
    exec(compile(module, filename="<ast>", mode='exec'))
    print('function-name:', function.name)
    return locals()[function.name]

    # val = exec(content)
    # start = 4
    # end = content.find("(")
    # function_name = content[start:end]
    # print()
    # return eval(function_name)


# content = "#comment1\ndef my_function(x):\n    return x**2"
# # user_function = extract_function_from_string(content)
# # print(user_function(25))
# code_string = code_string.strip()
# user_function = extract_function_from_string(code_string)
# print(user_function(3, 4))



import ast
from RestrictedPython import compile_restricted


source_code = """
def function_one(x, y):
    def function_two(z):
        return z ** 2

    val_two = function_two(3)
    return (9 ** 9) / val_two
"""


tree = ast.parse(source_code, mode='exec')
print(tree.body)
function = tree.body[0]

byte_code = compile_restricted(
    source_code,
    filename='<inline code>',
    mode='exec'
)
exec(byte_code)
user_function = locals()[function.name]
print(user_function(3, 4))

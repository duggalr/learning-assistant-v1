

class CodeEval(object):
    """
    """
    
    def __init__(self):
        pass

    def evaluate_code(self, code_str):
        output = eval(code_str)
        return output


## Creating tests

# s = """print('hello world')
# """

# ce = CodeEval()
# output = ce.evaluate_code(
#     code_str = s
# )
# print(output)

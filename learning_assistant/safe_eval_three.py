import ast



globals_dict = {}
globals_dict.update(
    __builtins__={
        'True': True,
        'False': False,
        'None': None,
        'str': str,
        'bool': bool,
        'int': int,
        'float': float,
        'enumerate': enumerate,
        'dict': dict,
        'list': list,
        'tuple': tuple,
        'map': map,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'round': round,
        'len': len,
        'repr': repr,
        'set': set,
        'all': all,
        'any': any,
        'ord': ord,
        'chr': chr,
        'divmod': divmod,
        'isinstance': isinstance,
        'range': range,
        'zip': zip,
    }
)

def new_safe_eval(source_code, mode="exec"):
    
    # try:
    #     # tree = ast.parse(source_code, mode='exec')
    #     # function = tree.body[0]
    #     # num_inputs = len([a.arg for a in function.args.args])
    #     tree = ast.parse(source_code, mode=mode)
    #     function = tree.body[0]
    #     num_inputs = len(function.args.args)
    #     source_code = compile(tree, "<string>", mode)
    # except: 
    #     return {'success': False, 'message': 'Invalid Syntax. Code could not compile.', 'user_function_output': None}


    source_code = source_code.strip()
    tree = ast.parse(source_code, mode=mode)
    function = tree.body[0]
    num_inputs = len(function.args.args)
    source_code = compile(tree, "<string>", mode)

    restricted_locals = {}
    exec(source_code, globals_dict, restricted_locals)
    print(restricted_locals)
    print(restricted_locals[function.name](4,5))

    # print(function.name)
    # print(globals_dict[function.name])
    
    # print(globals())
    # user_function = locals()[function.name]
    # print('user-function:', user_function)

    # try:
    #     result = eval(source_code, globals_dict, {})
    #     user_function = locals()[function.name]
    #     print('user-function:', user_function)
    #     return {'success': True, 'message': 'Code executed successfully.', 'user_function_output': result}
    # except Exception as e:
    #     return {'success': False, 'message': 'Code execution failed.', 'user_function_output': None, 'error_message': str(e)}


    # source_code = source_code.strip()
    # print(source_code)
    # code_obj = compile(source_code, "<string>", mode)
    # result = eval(code_obj, globals_dict, {})
    # print(result)



## TODO: 
    # create new function in main_utils with below
    # finalize and go through each question and fix from there...
source_code = """
def function_one(x, y):
    user_input = input('>>')
    return user_input
    # c = 1 + x
    # c += y
    # return c
    # # li = list(range(x))
    # return li[0:2]
    # return sum(li)
    # return x ** y
"""
# print( new_safe_eval(source_code) )

# from RestrictedPython import safe_builtins, compile_restricted

# for k in safe_builtins:
#     print(k, safe_builtins[k])



# code_obj = compile(expr, "", mode)
# eval(c, globals_dict, locals_dict)



# source_code = "2 ** 8"
# code = compile(source_code, "<string>", "eval")
# print(code)
# print( eval(source_code) )

# # d = { k : v for k,v in locals().items() if v}
# # print(d)

# # d = { k : v for k,v in globals().items() if v}
# # print(d)

# # d  = { k : v for k,v in vars().items() if v}
# # print(d)

# print(dir())
# print(dir(__builtins__))


# # To evaluate a string-based expression, Python’s eval() runs the following steps:
#     # Parse expression
#     # Compile it to bytecode
#     # Evaluate it as a Python expression
#     # Return the result of the evaluation

# # TODO: 
#     # leverage real-python and the safe_eval to make my own safe eval function
#         # go from there to release
#         # **need to factor timeouts and ddos attacks <-- this is serious threat and should factor in (accidental infinite loops)



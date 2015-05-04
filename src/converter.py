import re
from numerricconvert.code_parser import cleanup


standard_mappings = {r'str': r'std::string', r'float': r'double'}
forbidden_signs = {' ', '+', '-', '*', '/', ')', '(', '\n'}

# r'for\s+([^\s\n=+/\\-]+)\s+in\s+range\((\d+)\):', r'for (\1=0; \1<\2; \1++) {'
# r'if\s+(.+)\s*:', r'if (\1) {'
# r'if\s+\((.+)\sis\sTrue\)', r'if (\1 == true)'
# r'if\s+\((.+)\s==\sTrue\)', r'if (\1 == true)'
# r'if\s+\(not\s+([a-zA-Z0-9_]+)\)', r'if (!(\1))
# r'if\s+\((.+)\sis\sFalse\)', r'if (\1 == false)'
# r'if\s+\((.+)\s==\sFalse\)', r'if (\1 == false)'
# r'else\s*:', r'else {'


def insert_string(code: str, index: int, insertion_string: str) -> str:
    res = code[:index]
    res += insertion_string
    res += code[index:]
    return res


def string_overwrite(code: str, original_len: int, index: int, replacement: str) -> list:
    res = code[:index]
    replacement_len = len(replacement)
    code_len = len(code)
    offset = replacement_len - original_len

    for i in range(replacement_len):
        res += replacement[i]
    for i in range(code_len - index - original_len):
        res += code[i + index + original_len]
    return [res, offset]


def delete_substring(code: str, start: int, end: int) -> str:
    res = code[:start]
    res += code[end:]
    return res


def convert_defs(code: str) -> str:
    function_beginnings = re.finditer(r'def(\s+[^\s\n/\\+=-]+\()', code)
    offset = 0
    for function_beginning in function_beginnings:
        function_beginning_start = function_beginning.start() + offset
        function_beginning_end = function_beginning.end() + offset

        function_end = re.search(r'\)', code[function_beginning_end + offset:])
        function_end_pos = function_end.start()
        code_snippet = re.sub(r'([^\s\n/\\,+=-]+)\s*:\s*([^\s\n/\\,+=-]+)', r'\2 \1',
                              code[function_beginning_end:function_beginning_end + function_end_pos])
        string_over = string_overwrite(code, function_end_pos, function_beginning_end,
                                       code_snippet)
        code = string_over[0]
        offset += string_over[1]
        code_snippet = re.sub(r'([^\s\n/\\,+=-]+)\s*:\s*([^\s\n/\\,+-]+)\s*=\s*([^\s\n/\\,+=-]+)', r'\2 \1=\3',
                              code[function_beginning_end:function_beginning_end + function_end_pos])
        string_over = string_overwrite(code, function_end_pos, function_beginning_end,
                                       code_snippet)
        code = string_over[0]
        offset += string_over[1]

        ret_type = re.search(r'->(\s*[^\s\n:+=-]+):', code[function_beginning_start:])

        if ret_type:
            ret_type_str = ret_type.group()
            ret_type_str = re.sub(r'\s*', r'', ret_type_str)
            ret_type_str = ret_type_str[:len(ret_type_str) - 1]
            code = delete_substring(code, function_beginning_start + ret_type.start(), function_beginning_start
                                    + ret_type.end())
            offset -= ret_type.end() - ret_type.start()

            code = delete_substring(code, function_beginning_start, function_beginning_start + 3)
            code = insert_string(code, function_beginning_start, ret_type_str[2:])
            offset += len(ret_type_str) - 5

        for alias in standard_mappings:
            code_snippet = re.sub(alias, standard_mappings[alias],
                                  code[function_beginning_start:function_beginning_end + function_end_pos])
            string_over = string_overwrite(code, function_end_pos + function_beginning_end - function_beginning_start,
                                           function_beginning_start, code_snippet)
            code = string_over[0]
            offset += string_over[1]
    return code


def add_semicolons(code: str) -> str:
    res = ''
    code = re.sub(r'\s+\n', r'\n', code)
    code = re.sub(r'\s+$', r'', code)
    code_list = code.split('\n')
    for code_string in code_list:
        if not (code_string.endswith('}') or code_string.endswith('{')):
            res += code_string + ';\n'
        else:
            res += code_string + '\n'
    if res.endswith('\n'):
        res = res[:len(res) - 1]
    return res


def basic_convert(code: str, aliases: dict, custom_mappings: dict=None) -> str:
    code = cleanup(code)
    code = convert_defs(code)

    code = code.replace('True', 'true')
    code = code.replace('False', 'false')
    # for alias in aliases:
    #     if aliases[alias] == 'scipy':
    #         code = code.replace(alias + '.special.gamma', 'tgamma')  # gamma is tgamma in C++  # custom function names here
    #
    # for alias in aliases:
    #     code = code.replace(alias + '.', '')

    code = add_semicolons(code)
    return code


print(basic_convert("def f(ve_before1: float, ve_before2: float, ve_after1: float, ve_after2: float, ni_before1: float, ni_before2: float, ni_afer1: float, ni_afer2: float) -> int:", {'np': 'numpy', 'scipy': 'scipy'}))
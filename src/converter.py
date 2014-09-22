import re
import queue


standard_mappings = {r'str': r'std::string', r'float': r'double'}


def right_bracket(snippet: str, starting_pos: int) -> str:
    pass


def left_bracket(snippet: str, starting_pos: int) -> str:
    pass


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


def find_block(code: str, substring: str) -> list:
    res = []
    index = 0
    code_len = len(code)
    while index < code_len:

        substr_index = code.find(substring, index)
        if substr_index != -1:
            start_pos = substr_index
            if substr_index > 0:
                block_indent = 0
                curr_pos = substr_index - 1
                while code[curr_pos] == ' ' and curr_pos >= 0:
                    block_indent += 1
                    curr_pos -= 1
            else:
                block_indent = 0
            next_newline = code.find('\n', start_pos)
            if next_newline == -1 or next_newline == code_len - 1:
                res.append([start_pos, len(code), block_indent])  # start position, end position
                index = code_len
            else:
                flag = True
                while flag:
                    curr_indent = 0
                    curr_pos = next_newline + 1
                    while code[curr_pos] == ' ' and curr_pos <= code_len:
                        curr_pos += 1
                        curr_indent += 1
                    if curr_indent <= block_indent:
                        flag = False
                        res.append([start_pos, next_newline, block_indent])
                        index = next_newline + 1
                    else:
                        next_newline = code.find('\n', curr_pos)
                        if next_newline == -1 or next_newline == code_len - 1:
                            res.append([start_pos, len(code), block_indent])  # start position, end position
                            index = code_len
                            flag = False
        else:
            break
    return res


def find_all_blocks(code: str, substring: str) -> list:
    unchecked_blocks = queue.Queue()
    base_blocks = find_block(code, substring)
    res = []
    substring_len = len(substring)
    if base_blocks:
        for base_block in base_blocks:
            unchecked_blocks.put(base_block)
            res.append(base_block)
        while not unchecked_blocks.empty():
            tmp_block = unchecked_blocks.get()
            start_pos = tmp_block[0]
            tmp_block = code[tmp_block[0] + substring_len + tmp_block[2]:]
            new_blocks = find_block(tmp_block, substring)
            if new_blocks:
                for new_block in new_blocks:
                    offset_new_block = new_block.copy()
                    offset_new_block[0] += start_pos
                    offset_new_block[1] += start_pos
                    unchecked_blocks.put(offset_new_block)
                    res.append(offset_new_block)
        for block in res:
            while not code[block[0]:].startswith(substring):
                block[0] += 1
                block[1] += 1
        return res
    else:
        return None


def add_semicolons(code: str) -> str:
    pass


def convert_fors(code: str) -> str:
    for_blocks = find_block(code, 'for ')
    if for_blocks:
        offset = 0
        for block in for_blocks:
            string_to_match = r'for\s+([^\s\n=+/\\-]+)\s+in\s+range\((\d+)\):'

            rem = re.match(string_to_match, code[block[0] + offset:block[1] + offset])

            if rem:
                code_substr = re.sub(string_to_match, r'for (\1=0; \1<\2; \1++) {',
                                     code[block[0] + offset + rem.start():block[0] + offset + rem.end() + 1])
                string_over = string_overwrite(code, rem.end() - rem.start(), rem.start() + block[0] + offset, code_substr)
                offset += string_over[1]

                code = string_over[0]
                code = insert_string(code, block[1] + offset, '\n' + ' ' * block[2] + '}')
                code = code.replace('{\n\n', '{\n')
                offset += 1 + block[2]
    return code


def convert_ifs(code: str) -> str:
    if_blocks = find_all_blocks(code, 'if ')
    if if_blocks:
        offset = 0
        if_blocks.reverse()
        for block in if_blocks:
            string_to_match = r'if\s+(.+)\s*:'
            rem = re.match(string_to_match, code[block[0]:block[1] + offset])

            if rem:
                code_substr = re.sub(string_to_match, r'if (\1) {',
                                     code[block[0] + rem.start():block[0] + rem.end() + 1],
                                     count=1)
                string_over = string_overwrite(code, rem.end() - rem.start(), rem.start() + block[0],
                                               code_substr)
                offset += string_over[1]

                code = string_over[0]
                code = insert_string(code, block[1] + offset, '\n' + ' ' * block[2] + '}')
                code = code.replace('{\n\n', '{\n')
                offset += 1
                offset += block[2]
    code = re.sub(r'if\s+\((.+)\sis\sTrue\)', r'if (\1 == true)', code)
    code = re.sub(r'if\s+\((.+)\s==\sTrue\)', r'if (\1 == true)', code)
    code = re.sub(r'if\s+\(not\s+([a-zA-Z0-9_]+)\)', r'if (!(\1))', code)
    code = re.sub(r'if\s+\((.+)\sis\sFalse\)', r'if (\1 == false)', code)
    code = re.sub(r'if\s+\((.+)\s==\sFalse\)', r'if (\1 == false)', code)
    return code


def convert_elses(code: str) -> str:
    if_blocks = find_block(code, 'else ')
    if if_blocks:
        offset = 0
        for block in if_blocks:
            string_to_match = r'else\s*:'

            rem = re.match(string_to_match, code[block[0] + offset:block[1] + offset])

            if rem:
                code_substr = re.sub(string_to_match, r'else {',
                                     code[block[0] + offset + rem.start():block[0] + offset + rem.end() + 1])
                string_over = string_overwrite(code, rem.end() - rem.start(), rem.start() + block[0] + offset,
                                               code_substr)
                offset += string_over[1]

                code = string_over[0]
                code = insert_string(code, block[1] + offset, '\n}')
                code = code.replace('{\n\n', '{\n')
                offset += 1
    # code = re.sub(r'if\s+\((.+)\sis\sTrue\)', r'if (\1 == true)', code)
    # code = re.sub(r'if\s+\((.+)\s==\sTrue\)', r'if (\1 == true)', code)
    # code = re.sub(r'if\s+\(not\s+([a-zA-Z0-9_]+)\)', r'if (!(\1))', code)
    # code = re.sub(r'if\s+\((.+)\sis\sFalse\)', r'if (\1 == false)', code)
    # code = re.sub(r'if\s+\((.+)\s==\sFalse\)', r'if (\1 == false)', code)
    return code


def convert_def(code: str) -> str:
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


def basic_convert(code: str, aliases: dict, custom_mappings: dict=None) -> str:
    code = re.sub(r'\\\s*\n\s*', ' ', code)

    code = convert_def(code)
    code = convert_fors(code)
    code = convert_ifs(code)
    code = convert_elses(code)

    code = code.replace('True', 'true')
    code = code.replace('False', 'false')
    for alias in aliases:
        if aliases[alias] == 'scipy':
            code = code.replace(alias + '.special.gamma', 'tgamma')  # gamma is tgamma in C++  # custom function names here

    for alias in aliases:
        code = code.replace(alias + '.', '')

    return code

# vl_dependent = false

a = "if vl_dependent:\n"\
    "    if center_of_mass:\n"\
    "        if 12345:\n"\
    "            return 34000"
print(a, '\n')
print('=======New=======')
print(basic_convert(a, {'np': 'numpy', 'scipy': 'scipy'}))
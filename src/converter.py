import re
import queue


standard_mappings = {r'str': r'std::string', r'float': r'double'}
forbidden_signs = {' ', '+', '-', '*', '/', ')', '(', '\n'}


def right_bracket(snippet: str, starting_pos: int) -> str:
    pass


def left_bracket(snippet: str, starting_pos: int) -> str:
    pass


def insert_string(code: str, index: int, insertion_string: str) -> str:
    res = code[:index]
    res += insertion_string
    res += code[index:]
    return res


def find_non_bracket_expression(code: str, start_pos: int, direction: int) -> list:
    end_pos = start_pos
    code_len = len(code)
    while 0 < end_pos < code_len - 1 and code[end_pos] not in forbidden_signs:
        end_pos += direction
    if code[end_pos] in forbidden_signs or code[end_pos] in {'(', ')'}:
        end_pos -= direction
    return [start_pos, end_pos]


def convert_pows(code: str) -> str:
    pow_operators = re.finditer(r'\s*\*\*\s*', code)
    offset = 0
    for pow_operator in pow_operators:
        curr_start = pow_operator.start() + offset
        curr_end = pow_operator.end() + offset
        if code[curr_start - 1] != ')' and code[curr_end] != '(':
            left_expr_pos = find_non_bracket_expression(code, curr_start - 1, -1)
            right_expr_pos = find_non_bracket_expression(code, curr_end, 1)
            original_len = right_expr_pos[1] - right_expr_pos[0] + left_expr_pos[0]\
                           - left_expr_pos[1] + curr_end - curr_start + 2

            if right_expr_pos[0] == right_expr_pos[1]:
                right_snippet = code[right_expr_pos[0]]
            else:
                right_snippet = code[right_expr_pos[0]:right_expr_pos[1] + 1]
            overwritten = string_overwrite(code, original_len,
                                           left_expr_pos[1], 'pow(' + code[left_expr_pos[1]:left_expr_pos[0] + 1]
                                           + ', ' + right_snippet + ')')
            code = overwritten[0]
            offset += overwritten[1]
    return code


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
                res.append([start_pos, len(code), block_indent, -1])  # start position, end position
                index = code_len
            else:
                flag = True
                while flag:
                    curr_indent = 0
                    curr_pos = next_newline + 1
                    while curr_pos < code_len and code[curr_pos] == ' ':
                        curr_pos += 1
                        curr_indent += 1
                    if curr_indent <= block_indent:
                        flag = False
                        res.append([start_pos, next_newline, block_indent, -1])
                        index = next_newline + 1
                    else:
                        next_newline = code.find('\n', curr_pos)
                        if next_newline == -1 or next_newline == code_len - 1:
                            res.append([start_pos, len(code), block_indent, -1])  # start position, end position
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
            tmp_block = code[tmp_block[0] + substring_len + tmp_block[2]:tmp_block[1] + tmp_block[2]]
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
        res.sort(key=lambda x: x[0])
        return res
    else:
        return None


def add_hierarchy(code_blocks: list) -> list:
    if code_blocks:
        min_indent = None
        code_blocks_amt = len(code_blocks)
        for block in code_blocks:
            if min_indent is None or min_indent > block[2]:
                min_indent = block[2]
        for block in enumerate(reversed(code_blocks)):
            if block[1][2] > min_indent:
                cursor_pos = code_blocks_amt - block[0]
                found_parent = False
                while cursor_pos > 0 and not found_parent:
                    cursor_pos -= 1
                    if code_blocks[cursor_pos][2] < block[1][2]:
                        code_blocks[code_blocks_amt - block[0] - 1][3] = cursor_pos
                        found_parent = True


def convert_constructs(code: str, construct_blocks: list, string_to_match: str, replacement_string: str) -> str:
    # construct_blocks = find_all_blocks(code, construct + ' ')
    if construct_blocks:
        # for block in construct_blocks:
        #     print(code[block[0]:block[1]])
        # add_hierarchy(construct_blocks)
        construct_blocks.reverse()
        blocks_amt = len(construct_blocks)
        for block in construct_blocks:

            fixit_re = re.search(r'\n\s*$', code[block[0]: block[1]])
            if fixit_re:
                end_bracket_insertion_position = block[0] + fixit_re.start()
            else:
                end_bracket_insertion_position = block[1]
            rem = re.match(string_to_match, code[block[0]:block[1]])
            if rem:
                code = insert_string(code, end_bracket_insertion_position, '\n' + ' ' * block[2] + '}')
                code_substr = re.sub(string_to_match, replacement_string,
                                     code[block[0] + rem.start():block[0] + rem.end() + 1],
                                     count=1)
                string_over = string_overwrite(code, rem.end() - rem.start(), rem.start() + block[0],
                                               code_substr)

                if block[3] != -1:
                    parent_block_id = block[3]
                    flag = True
                    while flag:
                        construct_blocks[blocks_amt - parent_block_id - 1][1] += string_over[1] + 1 + block[2]
                        if construct_blocks[blocks_amt - parent_block_id - 1][3] == -1:
                            flag = False
                        else:
                            parent_block_id = construct_blocks[blocks_amt - parent_block_id - 1][3]
                code = string_over[0]
                code = code.replace('{\n\n', '{\n')
    return code


def convert_fors(code: str, for_blocks: list) -> str:
    return convert_constructs(code, for_blocks, r'for\s+([^\s\n=+/\\-]+)\s+in\s+range\((\d+)\):',
                              r'for (\1=0; \1<\2; \1++) {')


def convert_ifs(code: str, if_blocks: list) -> str:
    code = convert_constructs(code, if_blocks, r'if\s+(.+)\s*:', r'if (\1) {')
    code = re.sub(r'if\s+\((.+)\sis\sTrue\)', r'if (\1 == true)', code)
    code = re.sub(r'if\s+\((.+)\s==\sTrue\)', r'if (\1 == true)', code)
    code = re.sub(r'if\s+\(not\s+([a-zA-Z0-9_]+)\)', r'if (!(\1))', code)
    code = re.sub(r'if\s+\((.+)\sis\sFalse\)', r'if (\1 == false)', code)
    code = re.sub(r'if\s+\((.+)\s==\sFalse\)', r'if (\1 == false)', code)
    return code


def convert_elses(code: str, else_blocks: list) -> str:
    return convert_constructs(code, else_blocks, r'else\s*:', r'else {')


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


def this_might_be_the_worst_crutch_ever(these_blocks: list, those_blocks: list) -> list:
    if these_blocks:
        blocks_amt = len(these_blocks)
        for block in enumerate(reversed(these_blocks)):
            if block[1][3] != -1:
                parent_block_id = block[1][3]

                parent_block = these_blocks[blocks_amt - parent_block_id - 1]
                parent_start = parent_block[0]
                parent_offset = parent_block[2]
                if those_blocks:
                    for that_block_blocks in those_blocks:
                        if that_block_blocks:
                            for that_block in that_block_blocks:
                                if block[1][0] > that_block[0] > parent_start and that_block[1] > block[1][1]\
                                        and that_block[2] <= parent_offset:
                                    these_blocks[blocks_amt - block[0] - 1][3] = -1

    return these_blocks


def basic_convert(code: str, aliases: dict, custom_mappings: dict=None) -> str:
    code = re.sub(r'\\\s*\n\s*', ' ', code)
    code = re.sub(r',\n\s*', ', ', code)
    code = re.sub(r'\n\s*,', ', ', code)

    if_blocks = find_all_blocks(code, 'if ')
    add_hierarchy(if_blocks)
    for_blocks = find_all_blocks(code, 'for ')
    add_hierarchy(for_blocks)
    else_blocks = find_all_blocks(code, 'else')
    add_hierarchy(else_blocks)

    if_blocks = this_might_be_the_worst_crutch_ever(if_blocks, [for_blocks, else_blocks])

    code = convert_defs(code)
    code = convert_ifs(code, if_blocks)
    for_blocks = find_all_blocks(code, 'for ')
    add_hierarchy(for_blocks)
    else_blocks = find_all_blocks(code, 'else')
    add_hierarchy(else_blocks)

    for_blocks = this_might_be_the_worst_crutch_ever(for_blocks, [else_blocks])

    code = convert_fors(code, for_blocks)

    else_blocks = find_all_blocks(code, 'else')
    add_hierarchy(else_blocks)
    code = convert_elses(code, else_blocks)

    code = code.replace('True', 'true')
    code = code.replace('False', 'false')
    for alias in aliases:
        if aliases[alias] == 'scipy':
            code = code.replace(alias + '.special.gamma', 'tgamma')  # gamma is tgamma in C++  # custom function names here

    for alias in aliases:
        code = code.replace(alias + '.', '')

    code = convert_pows(code)
    code = add_semicolons(code)
    return code

a = "if not center_of_mass:\n"\
    "    if not nokt:\n"\
    "        multiplier = constants.pi * (sigma ** 2) * ((constants.k * T / (2 * constants.pi * mass)) ** 0.5)\n"\
    "    else:\n"\
    "        multiplier = constants.pi * (sigma ** 2) * ((0.5 / (constants.pi * mass)) ** 0.5)\n"\
    "    if deg == 0:\n"\
    "        return 0.5 * multiplier * (min_sq + 1.0) * np.exp(-min_sq)\n"\
    "    else:\n"\
    "        min_g = min_sq ** 0.5\n"\
    "        f = lambda g: raw_crosssection_diss_rigid_sphere(g, T, sigma, molecule_vibr, molecule_diss, center_of_mass, vl_dependent) * (g ** (3.0 + 2.0 * deg)) * np.exp(-g ** 2)\n"\
    "        if not nokt:\n"\
    "            return ((constants.k * T / (2 * constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]\n"\
    "        else:\n"\
    "            return ((0.5 / (constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]\n"\
    "else:\n"\
    "    min_g = min_sq ** 0.5\n"\
    "    f = lambda g: raw_crosssection_diss_rigid_sphere(g, T, sigma, molecule_vibr, molecule_diss, center_of_mass, vl_dependent) * (g ** (3.0 + 2.0 * deg)) * np.exp(-g ** 2)\n"\
    "    if not nokt:\n"\
    "        return ((constants.k * T / (2 * constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]\n"\
    "    else:\n"\
    "        return ((0.5 / (constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]\n"
# a = "min_g = 2.1 ** 2.7"
print(a, '\n')
print('=======New=======')
print(basic_convert(a, {'np': 'numpy', 'scipy': 'scipy'}))
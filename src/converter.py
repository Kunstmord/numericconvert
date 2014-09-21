import re


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
    res = ''
    res = res.join(code[:index])
    replacement_len = len(replacement)
    code_len = len(code)
    offset = replacement_len - original_len

    for i in range(replacement_len):
        res += replacement[i]
    for i in range(code_len - index - original_len):
        res += code[i + index + original_len]
    return [res, offset]


def basic_convert(code: str, aliases: dict) -> str:
    code = convert_fors(code)
    code = convert_ifs(code)

    code = code.replace('True', 'true')
    code = code.replace('False', 'false')
    for alias in aliases:
        if aliases[alias] == 'scipy':
            code = code.replace(alias + '.special.gamma', 'tgamma')  # gamma is tgamma in C++
    return code


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
                    curr_pos -= 1
                    block_indent += 1
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


def add_semicolons(code: str) -> str:
    pass


def convert_fors(code: str) -> str:
    for_blocks = find_block(code, 'for ')
    if for_blocks:
        offset = 0
        for block in for_blocks:
            rem = re.match(r'for\s+([^\s\n=+/\\]+)\s+in\s+range\((\d+)\):', code[block[0] + offset:block[1] + offset])

            if rem:
                code_substr = re.sub(r'for\s+([^\s\n=+/\\]+)\s+in\s+range\((\d+)\):', r'for (\1=0; \1<\2; \1++) {',
                                     code[block[0] + offset + rem.start():block[0] + offset + rem.end() + 1])
                string_over = string_overwrite(code, rem.end() - rem.start(), rem.start() + block[0] + offset, code_substr)
                offset += string_over[1]

                code = string_over[0]
                code = insert_string(code, block[1] + offset, '\n' + ' ' * block[2] + '}')
                code = code.replace('{\n\n', '{\n')
                offset += 1 + block[2]
    return code


def convert_ifs(code: str) -> str:
    if_blocks = find_block(code, 'if ')
    if if_blocks:
        offset = 0
        for block in if_blocks:
            rem = re.match(r'if\s+(.+)\s*:', code[block[0] + offset:block[1] + offset])

            if rem:
                code_substr = re.sub(r'if\s+(.+)\s*:', r'if (\1) {',
                                     code[block[0] + offset + rem.start():block[0] + offset + rem.end() + 1])
                string_over = string_overwrite(code, rem.end() - rem.start(), rem.start() + block[0] + offset, code_substr)
                offset += string_over[1]

                code = string_over[0]
                code = insert_string(code, block[1] + offset, '\n}')
                code = code.replace('{\n\n', '{\n')
                offset += 1
    code = re.sub(r'if\s+\((.+)\sis\sTrue\)', r'if (\1 == true)', code)
    code = re.sub(r'if\s+\((.+)\s==\sTrue\)', r'if (\1 == true)', code)
    code = re.sub(r'if\s+\(not\s+([a-zA-Z0-9_-]+)\)', r'if (!(\1))', code)
    code = re.sub(r'if\s+\((.+)\sis\sFalse\)', r'if (\1 == false)', code)
    code = re.sub(r'if\s+\((.+)\s==\sFalse\)', r'if (\1 == false)', code)
    return code



a = "for i in range(2000):\n" \
    "  tmp += 80 * i\n\n" \
    "if not tmp and k == True:\n" \
    "   for q in range(400):\n" \
    "       ttmp = 40 *\ \n" \
    "           340 - 30i"\
    "  tmp += 80 * i\n\n" \
    "if not tmp and k == True:\n" \
    "   for q in range(400):\n" \
    "       ttmp = 40 *\ \n" \
    "           340 - 30i"
print(a, '\n\n')
print('=======New=======')
print(basic_convert(a, {'np': 'numpy', 'scipy': 'scipy'}))
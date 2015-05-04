import re


def cleanup(code):
    code = re.sub(r'\\\s*\n\s*', ' ', code)
    code = re.sub(r',\n\s*', ', ', code)
    code = re.sub(r'\n\s*,', ', ', code)
    return code


def get_indent(snippet_line: str):
    i = 0
    while snippet_line[i] == ' ':
        i += 1
    return i


def extract_single_token_type(lines_with_indents: list, pattern, token: str):
    res = []
    for i, line_indent in enumerate(lines_with_indents):
        line, indent = line_indent
        match = pattern.match(line)
        if match:
            res.append([token, i, indent])
    return res


def extract_all_tokens(snippet: str):
    tokens = []  # token, line number, last line of indent >= token indent, indent
    lines = snippet.split('\n')
    lines_with_indents = [[line, get_indent(line)] for line in lines]

    pattern_if = re.compile(r'\s*if\s')
    pattern_elif = re.compile(r'\s*elif\s')
    pattern_else = re.compile(r'\s*else:')
    pattern_while = re.compile(r'\s*while\s')
    pattern_for = re.compile(r'\s*for\s')

    tokens += extract_single_token_type(lines_with_indents, pattern_if, 'if')
    tokens += extract_single_token_type(lines_with_indents, pattern_elif, 'elif')
    tokens += extract_single_token_type(lines_with_indents, pattern_else, 'else')
    tokens += extract_single_token_type(lines_with_indents, pattern_while, 'while')
    tokens += extract_single_token_type(lines_with_indents, pattern_for, 'for')

    if len(tokens) > 0:
        tokens.sort(key=lambda x: x[1])
        total_lines = len(lines_with_indents)
        token_ends = []
        for token in tokens:
            token_name, token_line, token_indent = token
            while token_line < total_lines-1 and lines_with_indents[token_line+1][1] > token_indent:
                token_line += 1  # check lines until we find a one with an indent less than or equal to the current one
            token_ends.append(token_line)
        tokens = [[token[0], token[1], token_end, token[2]] for token, token_end in zip(tokens, token_ends)]
    return [tokens, lines_with_indents]


def get_parent_blocks(tokens: list):
    parent_blocks = []
    for i, token in enumerate(tokens):
        if token[3] > 0:  # we need to find parent blocks of indented tokens
            potential_parents = [[j, tk] for j, tk in enumerate(tokens)
                                 if tk[2] >= token[2] and tk[3] < token[3]]
            if len(potential_parents) == 1:
                parent_blocks.append([i, potential_parents[0][0]])
            # print(potential_parents)
    return parent_blocks


def extract_brackets(snippet):
    pass


test1 = "if not center_of_mass:\n"\
        "    if not nokt:\n"\
        "        a *= 2 ** 4\n"\
        "        if a<5:\n"\
        "            multiplier = constants.pi * (sigma ** 2) * ((0.5 / (constants.pi * mass)) ** 0.5)\n"\
        "    if deg == 0:\n"\
        "        return 0.5 * multiplier * (min_sq + 1.0) * np.exp(-min_sq ** min_pow)\n"\
        "    else:\n"\
        "        min_g = min_sq ** 0.5"
blcks = extract_all_tokens(test1)

print(blcks[0])
for line in blcks[1]:
    print(line[0])
# print(get_parent_blocks(blcks[0]))
# print(get_block_end(blcks[0], blcks[1]))
# print(test2[blcks[0][1]:])
# print(test2[blcks[1][1]:])
# print(get_indent('  ddd'))
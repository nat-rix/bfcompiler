#!/usr/bin/env python3

OUT = 'out.bf'

import sys

if len(sys.argv) < 2:
    print('error: no file specified')
    exit(-1)

f = open(sys.argv[1])
c = f.read()
f.close()

if not c.startswith('('):
    exit(1)
if ')' not in c[1:]:
    exit(1)
p = c[1:].index(')')

vars = c[1:p+1].replace('\n', '').replace(' ', '').split(',')
cmdl = tuple(enumerate(c[p+3:].split('\n')))

char_set = []
char_set_n = 0
instr_to_char_set = dict()

for i, cmd in cmdl:
    if not cmd:
        continue
    cmdf = cmd.split(' ')
    while not cmdf[0]:
        del cmdf[0]
    cmdh = cmdf[0]
    if cmdh == 'cpy':
        vars.append('_instr{}'.format(i))
    elif cmdh == 'add':
        vars.append('_instr{}a'.format(i))
        vars.append('_instr{}b'.format(i))
    elif cmdh == 'if=':
        vars.append('_instr{}a'.format(i))
        vars.append('_instr{}b'.format(i))
        vars.append('_instr{}c'.format(i))
    elif cmdh == 'if':
        vars.append('_instr{}a'.format(i))
        vars.append('_instr{}b'.format(i))
    elif cmdh in ('div', 'mult'):
        vars.append('_instr{}a'.format(i))
        vars.append('_instr{}b'.format(i))
        vars.append('_instr{}c'.format(i))
        vars.append('_instr{}d'.format(i))
    elif cmdh == 'mod':
        vars.append('_instr{}a'.format(i))
        vars.append('_instr{}b'.format(i))
        vars.append('_instr{}c'.format(i))
        vars.append('_instr{}d'.format(i))
        vars.append('_instr{}e'.format(i))
        vars.append('_instr{}f'.format(i))
        vars.append('_instr{}g'.format(i))
    elif cmdh == 'print_num':
        vars.append('_instr{}a'.format(i))
        vars.append('_instr{}b'.format(i))
        vars.append('_instr{}c'.format(i))
        vars.append('_instr{}d'.format(i))
        vars.append('_instr{}e'.format(i))
        vars.append('_instr{}f'.format(i))
        vars.append('_instr{}g'.format(i))
        vars.append('_instr{}h'.format(i))
        vars.append('_instr{}i'.format(i))
        vars.append('_instr{}j'.format(i))
        vars.append('_instr{}k'.format(i))
    elif cmdh == 'print_text':
        text = (' '.join(cmdf[1:]))[1:-1].replace('\\n', '\n').encode('ascii')
        char_set.append([0, tuple(text)])
        instr_to_char_set[i] = char_set_n
        char_set_n += 1

variables = len(vars)
for i in range(len(char_set)):
    char_set[i][0] = variables
    variables += len(char_set[i][1])

vars = {char : i for i, char in enumerate(vars)}

glob_code = ''
arraypos = 0

pos_stack = []

def get_pos(val):
    if val.startswith('#'):
        return int(val[1:])
    else:
        return vars[val]

def goto_pos(pos):
    global arraypos
    code = ''
    offs = pos - arraypos
    arraypos = pos
    if offs < 0:
        for j in range(-offs):
            code += '<'
    elif offs > 0:
        for j in range(offs):
            code += '>'
    return code

def goto(pos):
    global arraypos
    return goto_pos(get_pos(pos))

def get_actual_pos():
    global arraypos
    return '#{}'.format(arraypos)

def bf_set(a, b):
    global arraypos
    args = cmdf[1:]
    code = goto(a)
    code += '[-]'
    code += ('+' * int(b))
    return code

def bf_setchar(a, b):
    global arraypos
    args = cmdf[1:]
    code = goto(a)
    code += '[-]'
    code += ('+' * (b[1:-1].encode('ascii')[0]))
    return code

def bf_mov(a, args):
    global arraypos
    return goto(a) + mov_on_pos(*args)

def mov_on_pos(*args):
    global arraypos
    p = arraypos
    code = '[-'
    for i in args:
        code += goto(i)
        code += '+'
    code += goto_pos(p)
    code += ']'
    return code

def bf_cpy(a, b, c):
    global arraypos
    code = bf_mov(a, (b, c))
    code += bf_mov(c, (a,))
    return code

def bf_add(a, b, c, d):
    global arraypos
    code = bf_cpy(a, c, d)
    code += bf_mov(c, (b,))
    return code

def bf_getchr(a):
    global arraypos
    return goto(a) + ','

def bf_print_raw(a):
    global arraypos
    return goto(a) + '.'

def bf_print_num_1(a):
    global arraypos
    code = goto(a)
    code += (('+' * 48) + '.' + ('-' * 48))
    return code

def bf_print_text(a):
    global arraypos
    code = goto_pos(a[0])
    lot = len(a[1])
    code += ('.>' * lot)
    arraypos += lot
    return code

def bf_if_equals(a, b, c, d, e):
    global arraypos, pos_stack
    code = bf_cpy(a, c, d)
    code += bf_cpy(b, d, e)
    code += goto(d) + '[-' + goto(c) + '-' + goto(d) + ']+' + goto(c)
    code += '[[-]' + goto(d) + '-' + goto(c) + ']' + goto(d) + '[-'
    pos_stack.append(arraypos)
    return code

def bf_if_clr(a):
    global arraypos, pos_stack
    code = goto(a) + '[[-]'
    pos_stack.append(arraypos)
    return code

def bf_if(a, b, c):
    global arraypos, pos_stack
    code = bf_cpy(a, b, c)
    code += goto(b) + '[[-]'
    pos_stack.append(arraypos)
    return code

def bf_endif():
    global arraypos, pos_stack
    code = goto_pos(pos_stack.pop())
    code += ']'
    return code

def bf_while(a):
    global arraypos, pos_stack
    code = goto(a) + '['
    pos_stack.append(arraypos)
    return code

def bf_endwhile():
    global arraypos, pos_stack
    code = goto_pos(pos_stack.pop())
    code += ']'
    return code

def bf_increment(a):
    global arraypos
    return goto(a) + '+'

def bf_decrement(a):
    global arraypos
    return goto(a) + '-'

def bf_chr_to_int(a):
    global arraypos
    return goto(a) + ('-' * 48)

def bf_divide(a, b, c, d, e, f):
    global arraypos
    code = goto(a) + '+' + bf_mov(a, (c,))
    code += goto(c) + '[' + bf_cpy(b, d, e)
    code += goto(d) + '[-' + goto(c) + '-' + bf_cpy(c, e, f) + goto(f) + '+'
    code += goto(e) + '[' + goto(f) + '-' + goto(e) + '[-]]'
    code += goto(f) + '[-' + goto(d) + '[-]' + goto(a) + '-' + goto(f) + ']'
    code += goto(d) + ']' + goto(a) + '+' + goto(c) + ']'
    return code

def bf_mod(a, b, c, d, e, f, g, h, i):
    global arraypos
    code = (
    bf_mov(a, (e,)) + goto(g) + '+' + goto(e) + '[' + goto(c) + '[-]' + bf_cpy(b, c, i) + goto(c) + '-' + goto(a) + '[-]' + bf_cpy(e, a, i) + goto(c) + '[-' + goto(a) + '-' + goto(f) + '+' + goto(d) + '[-]' + bf_cpy(a, d, i) + goto(a) + '[[-]' + goto(f) + '[-]' + goto(a) + ']' + bf_mov(d, (a,)) + goto(f) + '[[-]' + goto(e) + '[-]' + goto(h) + '[-]+' + goto(g) + '[-]' + goto(f) + ']' + goto(c) + ']' + goto(a) + '-' + goto(g) + '[[-]' + goto(e) + '[-]' + bf_cpy(a, e, i) + goto(g) + ']+' + goto(e) + ']' + goto(h) + '[[-]' + bf_cpy(b, h, i) + goto(h) + '[-' + goto(a) + '+' + goto(h) + ']]'
    )
    return code

def bf_mult(a, b, c, d, e, f):
    code = (
    bf_cpy(b, c, d) + goto(c) + '[-' + bf_cpy(a, d, e) + goto(d) + '[-' + goto(f) + '+' + goto(d) + ']' + goto(c) + ']' + goto(a) + '[-]' + bf_mov(f, (a,))
    )
    return code

def bf_print_num(a, b, c, d, h, j, k, l, m, n, o, p):
    # m = c
    # h = 10
    code = (
    bf_cpy(a, b, c) + bf_set(h, 10) + goto(c) + '+' + bf_divide(b, h, j, k, l, m) + goto(b) + '[' + bf_divide(b, h, j, k, l, m) + bf_mult(c, h, j, k, l, m) + goto(b) + ']' + bf_cpy(a, b, j) + goto(c) + '[' + goto(d) + '[-]' + bf_cpy(b, d, j) + bf_divide(d, c, j, k, l, m) + bf_mod(b, c, j, k, l, m, n, o, p) + bf_divide(c, h, j, k, l, m) + bf_print_num_1(d) + goto(c) + ']'
    )
    global arraypos
    
    return code

for tp, text in char_set:
    glob_code += goto_pos(tp)
    for i in text:
        glob_code += (('+' * i) + '>')
        arraypos += 1
    glob_code += '\n'

for i, cmd in cmdl:
    if not cmd:
        continue
    cmdf = cmd.split(' ')
    while not cmdf[0]:
        del cmdf[0]
    cmdh = cmdf[0]
    args = cmdf[1:]
    if cmdh == 'set':
        glob_code += bf_set(args[0], args[1])
    elif cmdh == 'setchar':
        glob_code += bf_setchar(args[0], args[1])
    elif cmdh == 'mov':
        glob_code += bf_mov(args[0], args[1:])
    elif cmdh == 'cpy':
        glob_code += bf_cpy(args[0], args[1],
                '_instr{}'.format(i))
    elif cmdh == 'add':
        glob_code += bf_add(args[0], args[1],
                '_instr{}a'.format(i), '_instr{}b'.format(i))
    elif cmdh == 'raw':
        glob_code += args[1]
    elif cmdh == 'print_raw':
        glob_code += bf_print_raw(args[0])
    elif cmdh == 'print_text':
        glob_code += bf_print_text(char_set[instr_to_char_set[i]])
    elif cmdh == 'print_num_1':
        glob_code += bf_print_num_1(args[0])
    elif cmdh == 'print_num':
        glob_code += bf_print_num(args[0], '_instr{}a'.format(i),
                '_instr{}b'.format(i), '_instr{}c'.format(i),
                '_instr{}d'.format(i), '_instr{}e'.format(i),
                '_instr{}f'.format(i), '_instr{}g'.format(i),
                '_instr{}h'.format(i), '_instr{}i'.format(i),
                '_instr{}j'.format(i), '_instr{}k'.format(i))
    elif cmdh == 'if=':
        glob_code += bf_if_equals(args[0], args[1],
                '_instr{}a'.format(i), '_instr{}b'.format(i),
                '_instr{}c'.format(i))
    elif cmdh == 'if_clr':
        glob_code += bf_if_clr(args[0])
    elif cmdh == 'if':
        glob_code += bf_if(args[0], '_instr{}a'.format(i),
                '_instr{}b'.format(i))
    elif cmdh == 'while':
        glob_code += bf_while(args[0])
    elif cmdh == 'endwhile':
        glob_code += bf_endwhile()
    elif cmdh == 'endif':
        glob_code += bf_endif()
    elif cmdh == 'incr':
        glob_code += bf_increment(args[0])
    elif cmdh == 'decr':
        glob_code += bf_decrement(args[0])
    elif cmdh == 'getchr':
        glob_code += bf_getchr(args[0])
    elif cmdh == 'chr_to_int':
        glob_code += bf_chr_to_int(args[0])
    elif cmdh == 'div':
        glob_code += bf_divide(args[0], args[1], '_instr{}a'.format(i),
                '_instr{}b'.format(i), '_instr{}c'.format(i),
                '_instr{}d'.format(i))
    elif cmdh == 'mod':
        glob_code += bf_mod(args[0], args[1], '_instr{}a'.format(i),
                '_instr{}b'.format(i), '_instr{}c'.format(i),
                '_instr{}d'.format(i), '_instr{}e'.format(i),
                '_instr{}f'.format(i), '_instr{}g'.format(i))
    elif cmdh == 'mult':
        glob_code += bf_mult(args[0], args[1], '_instr{}a'.format(i),
                '_instr{}b'.format(i), '_instr{}c'.format(i),
                '_instr{}d'.format(i))
    glob_code += '\n'
f = open(OUT, 'w')
f.write(glob_code)
f.close()

#!/usr/bin/python3

# Logs:
# [*] - info
# [W] - warning
# [!] - error

# Exit codes:
# 0 - success
# 1 - invalid usage
# 2 - file I/O error
# 3 - compilation error

import sys

BUS_SIZE = 84
REG_SIZE = 128
MEM_SIZE = 33554432
GRID_MIN = int(-(1 << BUS_SIZE) / 2)
GRID_MAX = int((1 << BUS_SIZE) / 2) - 1

CMDS = {
    'add':   [0,  3],
    'nand':  [1,  3],
    'lw':    [2,  3],
    'sw':    [3,  3],
    'beq':   [4,  3],
    'jalr':  [5,  2],
    'halt':  [6,  0],
    'noop':  [7,  0],
    'dec':   [8,  1],
    'xadd':  [9,  3],
    'xidiv': [10, 3],
    'xor':   [11, 3],
    'shr':   [12, 3],
    'cmpge': [13, 3],
    'jmbe':  [14, 3],
    'jmg':   [15, 3],
    'stc':   [16, 0],
    'clc':   [17, 0],
    'rcl':   [18, 3],
    '.fill': [-1, 1]
}

def init(f_in, f_out):
    try:
        print(f'[*] Parsing "{f_in}"...')
        with open(f_in, 'r') as f:
            data = f.readlines()
    except:
        print(f'[!] Failed to read file "{f_in}"')
        exit(2)
    code = parse_code(data)
    mc = build_mc(code)
    try:
        print(f'[*] Generating "{f_out}"...')
        with open(f_out, 'w') as f:
            f.write('\n'.join(mc))
        print('[*] Done')
    except:
        print(f'[!] Failed to create file "{f_out}"')
        exit(2)

def is_number (n):
    try:
        int(n)
        return True
    except:
        return False

def handle_arg (arg, labels, index, is_var, is_mem):
    addr = 0
    argmin = 0
    argmax = REG_SIZE - 1
    if is_mem:
        argmax = MEM_SIZE - 1
    if arg.startswith('@'):
        addr = 1
        argmax = MEM_SIZE - 1
        arg = arg[1:]
    if not is_number(arg):
        if arg in labels:
            arg = labels.index(arg)
        else:
            print(f'[!] Line {index + 1}: Label "{arg}" is undefined')
            exit(3)
    if is_var:
        argmin = GRID_MIN
        argmax = GRID_MAX
    arg = int(arg)
    if arg < argmin or arg > argmax:
        print(f'[!] Line {index + 1}: Argument {arg} out of range [{argmin} - {argmax}]')
        exit(3)
    return [addr, arg]

def parse_code (data):
    code = []
    labels = []
    labels_def = []
    for i in range(len(data)):
        args = data[i].split()
        if len(args) > 0 and args[0].endswith(':'):
            args[0] = args[0][:-1]
        else:
            args.insert(0, None)
        args = args[:5]
        if len(args) < 2:
            print(f'[!] Line {i + 1}: Missing instruction')
            exit(3)
        if args[1] not in CMDS:
            print(f'[!] Line {i + 1}: Unrecognized instruction "{args[1]}"')
            exit(3)
        argc = len(args) - 2
        argreq = CMDS[args[1]][1]
        if argc < argreq:
            print(f'[!] Line {i + 1}: Missing {argreq - argc} argument(s) for "{args[1]}"')
            exit(3)
        args = args[:2 + CMDS[args[1]][1]]
        if len(args) < 5:
            args.extend(['0'] * (5 - len(args)))
        labels.append(args[0])
        if args[0] != None:
            labels_def.append(args[0])
        code.append(args)
    for i in labels_def:
        if labels_def.count(i) > 1:
            print(f'[!] Multiple definitions of label "{i}"')
            exit(3)
    for i in range(len(code)):
        label, cmd, arg0, arg1, arg2 = code[i]
        if CMDS[cmd][0] == -1:
            addr_f, arg_f = handle_arg(arg0, labels, i, True, False)
            if addr_f == 1:
                print(f'[W] Line {i + 1}: "@" will be ignored')
            code[i] = [-1, arg_f, 0, 0, 0]
            continue
        is_mem = False
        if CMDS[cmd][0] in [2, 3, 4, 14, 15]:
            is_mem = True
        addr0, arg0 = handle_arg(arg0, labels, i, False, False)
        addr1, arg1 = handle_arg(arg1, labels, i, False, False)
        addr2, arg2 = handle_arg(arg2, labels, i, False, is_mem)
        code[i] = [CMDS[cmd][0], addr0, arg0, addr1, arg1, addr2, arg2]
    return code

def build_mc (code):
    mc = []
    for i in code:
        if i[0] == -1:
            mc.append(i[1])
            continue
        mc.append(
            i[0] << 78 | 
            i[1] << 77 |
            i[2] << 52 |
            i[3] << 51 |
            i[4] << 26 |
            i[5] << 25 |
            i[6]
        )
    mc = [str(i) for i in mc]
    return mc

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:')
        print(f'{sys.argv[0]} <input> <output>')
        exit(1)
    init(sys.argv[1], sys.argv[2])
    exit(0)
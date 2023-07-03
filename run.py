#!/usr/bin/python3

# Logs:
# [*] - info
# [W] - warning
# [!] - error

# Exit codes:
# 0 - success
# 1 - invalid usage
# 2 - file I/O error
# 3 - simulation error

import sys

BUS_SIZE = 84
REG_SIZE = 128
MEM_SIZE = 33554432
GRID_MIN = int(-(1 << BUS_SIZE) / 2)
GRID_MAX = int((1 << BUS_SIZE) / 2) - 1

CMDS = {
    0: 'add',
    1: 'nand',
    2: 'lw',
    3: 'sw',
    4: 'beq',
    5: 'jalr',
    6: 'halt',
    7: 'noop',
    8: 'dec',
    9: 'xadd',
    10: 'xidiv',
    11: 'xor',
    12: 'shr',
    13: 'cmpge',
    14: 'jmbe',
    15: 'jmg',
    16: 'stc',
    17: 'clc',
    18: 'rcl'
}

class Machine:
    def __init__ (self):
        self.pc = 0
        self.reg = [0] * REG_SIZE
        self.mem = [0] * MEM_SIZE
        self.reg_used = [0]
        self.mem_used = [0]
        self.cf = 0
        self.instructions = 0

    def print_state (self):
        print('\n@@@')
        print('state:')
        print(f'\tpc {self.pc}')
        print(f'\tcf {self.cf}')
        print('\tmemory:')
        for i in sorted(self.mem_used):
            print(f'\t\tmem[{i}] {self.mem[i]}')
        print('\tregisters:')
        for i in sorted(self.reg_used):
            print(f'\t\treg[{i}] {self.reg[i]}')    
        print('end state')        

    def run (self):
        while True:
            self.print_state()
            
            if self.pc >= MEM_SIZE:
                print('\n[!] PC went out of memory range')
                exit(3)

            cmd   = (self.mem[self.pc] >> 78) & 0xFF
            addr0 = (self.mem[self.pc] >> 77) & 0x1
            arg0  = (self.mem[self.pc] >> 52) & 0x1FFFFFF
            addr1 = (self.mem[self.pc] >> 51) & 0x1
            arg1  = (self.mem[self.pc] >> 26) & 0x1FFFFFF
            addr2 = (self.mem[self.pc] >> 25) & 0x1
            arg2  = (self.mem[self.pc]      ) & 0x1FFFFFF
            self.pc += 1

            if cmd not in CMDS:
                print(f'\n[!] Line {self.pc}: Unrecognized opcode {cmd}')
                exit(3)

            cmd_str = CMDS[cmd]
            if cmd_str in ['add', 'nand', 'xor', 'shr', 'cmpge', 'rcl']:
                self.mark_used_reg(arg2)
                if addr0 == 0:
                    src0 = self.reg[arg0]
                else:
                    src0 = self.mem[self.mem[arg0]]
                if addr1 == 0:
                    src1 = self.reg[arg1]
                else:
                    src1 = self.mem[self.mem[arg1]]
                if cmd_str == 'add':
                    res = src0 + src1
                    if res < GRID_MIN or res > GRID_MAX:
                        print(f'\n[!] Line {self.pc}: grid overflow')
                        exit(3)
                    self.reg[arg2] = src0 + src1
                elif cmd_str == 'nand':
                    self.reg[arg2] = ~(src0 & src1)
                elif cmd_str == 'xor':
                    self.reg[arg2] = src0 ^ src1
                elif cmd_str == 'shr':
                    self.reg[arg2] = src0 >> src1
                elif cmd_str == 'cmpge':
                    if src0 >= src1:
                        self.reg[arg2] = 1
                    else:
                        self.reg[arg2] = 0
                else:
                    bin0 = '{:b}'.format(src0).zfill(BUS_SIZE + 1)
                    bin0 = ''.join([bin0[src1:], bin0[:src1]])
                    self.cf = int(bin0[0], 2)
                    self.reg[arg2] = int(bin0[1:], 2)

            elif cmd_str in ['lw', 'sw']:
                if addr0 == 0:
                    mem_addr = self.reg[arg0]
                else:
                    mem_addr = self.mem[self.mem[arg0]]
                if addr2 == 0:
                    offset = mem_addr + arg2
                else:
                    offset = mem_addr + self.mem[arg2]
                if cmd_str == 'lw':
                    if addr1 == 0:
                        self.mark_used_reg(arg1)
                        self.reg[arg1] = self.mem[offset]
                    else:
                        self.mark_used_mem(self.mem[arg1])
                        self.mem[self.mem[arg1]] = self.mem[offset]
                else:
                    self.mark_used_mem(offset)
                    if addr1 == 0:
                        self.mem[offset] = self.reg[arg1]
                    else:
                        self.mem[offset] = self.mem[self.mem[arg1]]

            elif cmd_str in ['beq', 'jmbe', 'jmg']:
                if addr0 == 0:
                    src0 = self.reg[arg0]
                else:
                    src0 = self.mem[self.mem[arg0]]
                if addr1 == 0:
                    src1 = self.reg[arg1]
                else:
                    src1 = self.mem[self.mem[arg1]]
                if addr2 == 0:
                    offset = arg2
                else:
                    offset = self.mem[arg2]
                if cmd_str == 'beq':
                    if src0 == src1:
                        self.pc = offset
                elif cmd_str == 'jmbe':
                    if abs(src0) <= abs(src1):
                        self.pc = offset
                else:
                    if src0 > src1:
                        self.pc = offset

            elif cmd_str == 'jalr':
                if addr0 == 0:
                    offset = self.reg[arg0]
                else:
                    offset = self.mem[self.mem[arg0]]
                if addr1 == 0:
                    self.mark_used_reg(arg1)
                    self.reg[arg1] = self.pc
                else:
                    self.mark_used_mem(self.mem[arg1])
                    self.mem[self.mem[arg1]] = self.pc
                self.pc = offset

            elif cmd_str == 'dec':
                if addr0 == 0:
                    if self.reg[arg0] - 1 < GRID_MIN:
                        print(f'\n[!] Line {self.pc}: grid overflow')
                        exit(3)
                    self.reg[arg0] -= 1
                else:
                    if self.mem[self.mem[arg0]] - 1 < GRID_MIN:
                        print(f'\n[!] Line {self.pc}: grid overflow')
                        exit(3)
                    self.mem[self.mem[arg0]] -= 1

            elif cmd_str in ['xadd', 'xidiv']:
                self.mark_used_reg(arg2)
                if addr0 == 0:
                    src0 = self.reg[arg0]
                else:
                    src0 = self.mem[self.mem[arg0]]
                if addr1 == 0:
                    src1 = self.reg[arg1]
                else:
                    src1 = self.mem[self.mem[arg1]]
                if addr0 == 0:
                    self.mark_used_reg(arg0)
                    self.reg[arg0] = src1
                else:
                    self.mark_used_mem(self.mem[arg0])
                    self.mem[self.mem[arg0]] = src1
                if addr1 == 0:
                    self.mark_used_reg(arg1)
                    self.reg[arg1] = src0
                else:
                    self.mark_used_mem(self.mem[arg1])
                    self.mem[self.mem[arg1]] = src0
                if cmd_str == 'xadd':
                    res = src0 + src1
                    if res < GRID_MIN or res > GRID_MAX:
                        print(f'\n[!] Line {self.pc}: grid overflow')
                        exit(3)
                    self.reg[arg2] = src0 + src1
                else:
                    if src1 == 0:
                        print(f'\n[!] Line {self.pc}: division by 0')
                        exit(3)
                    self.reg[arg2] = int(src0 / src1)
            else:
                if cmd_str == 'halt':
                    print('\n[*] Machine halted')
                    print(f'[*] Total instructions executed: {self.instructions}')
                    exit(0)
                elif cmd_str == 'stc':
                    self.cf = 1
                elif cmd_str == 'clc':
                    self.cf = 0
                else:
                    pass

            self.instructions += 1
            self.reg[0] = 0
    
    def mark_used_reg (self, index):
        if index not in self.reg_used:
            if index < 0 or index > REG_SIZE - 1:
                print('\n[!] Out of registers range')
                exit(3)
            self.reg_used.append(index)

    def mark_used_mem (self, index):
        if index not in self.mem_used:
            if index < 0 or index > MEM_SIZE - 1:
                print('\n[!] Out of memory range')
                exit(3)
            self.mem_used.append(index)

def init (f_in):
    m = Machine()
    try:
        with open(f_in, 'r') as f:
            data = [int(i) for i in f.readlines()]
    except:
            print(f'[!] Failed to read file "{f_in}"')
            exit(2)
    for i in range(len(data)):
        m.mark_used_mem(i)
        m.mem[i] = data[i]
    m.run()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print(f'{sys.argv[0]} <input>')
        exit(1)
    init(sys.argv[1])
    exit(0)
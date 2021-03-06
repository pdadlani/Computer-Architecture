"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
PUSH = 0b01000101
POP = 0b01000110
ST = 0b10000100
# LD = 0b10000010
# NOP = 0b00000000
# PRA = 0b01001000

# handled by ALU
ADD = 0b10100000
AND = 0b10100000
CMP = 0b10100111
# DEC = 0b01100110
DIV = 0b10100011
# INC = 0b01100101
MOD = 0b10100100
MUL = 0b10100010
NOT = 0b01101001
OR = 0b10101010
SHL = 0b10101100
SHR = 0b10101101
SUB = 0b10100001
XOR = 0b10101011

# the following explicityy set the PC
CALL = 0b01010000
# INT = 0b01010010
IRET = 0b00010011
JEQ = 0b01010101
JGE = 0b01011010
JGT = 0b01010111
JLE = 0b01011001
JLT = 0b01011000
JMP = 0b01010100
JNE = 0b01010110
RET = 0b00010001

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0 # program counter, the address of the current instruction
        self.fl = 0b00000000 # 00000LGE
        self.sp = 7 # stack pointer aka R7 of register
        self.reg[self.sp] = 0xf4
        # self.is = 6 # interrupt status aka R6 of register
        # self.reg[self.is] = ?
        # self.im = 5 # interrupt mask aka R5 of register
        # self.reg[self.im] = ?
        self.branchtable = {
            LDI: self.handle_ldi,
            PRN: self.handle_prn,
            HLT: self.handle_hlt,
            ADD: self.handle_add,
            SUB: self.handle_sub,
            MUL: self.handle_mul,
            DIV: self.handle_div,
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET: self.ret,
            ST: self.st,
            IRET: self.iret,
            CMP: self.cmp,
            JEQ: self.jeq,
            JGE: self.jge,
            JGT: self.jgt,
            JLE: self.jle,
            JLT: self.jlt,
            JMP: self.jmp,
            JNE: self.jne,
            AND: self.handle_and,
            OR: self.handle_or,
            XOR: self.handle_xor,
            NOT: self.handle_not,
            SHL: self.handle_shl,
            SHR: self.handle_shr,
            MOD: self.handle_mod,
        }        

    def load(self, file):
        """Load a program into memory."""

        address = 0

        with open(file) as f: # what about case to handle if index out of range
            # aka no argument provided to command line
            for line in f:
                val = line.split("#")[0].strip()
                if val == '':
                    continue
                cmd = int(val, 2)
                self.ram[address] = cmd
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'SUB':
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'DIV':
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == 'CMP':
            diff = self.reg[reg_a] - self.reg[reg_b]
            if diff == 0:
                self.fl = 0b00000001
            elif diff > 0:
                self.fl = 0b00000010
            elif diff < 0:
                self.fl = 0b00000100
        elif op == 'AND':
            ans = self.reg[reg_a] & self.reg[reg_b]
            self.reg[reg_a] = ans
        elif op == 'OR':
            ans = self.reg[reg_a] | self.reg[reg_b]
            self.reg[reg_a] = ans
        elif op == 'XOR':
            ans = self.reg[reg_a] ^ self.reg[reg_b]
            self.reg[reg_a] = ans
        elif op == 'NOT':
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == 'SHL':
            ans = self.reg[reg_a] << self.reg[reg_b]
            self.reg[reg_a] = ans
        elif op == 'SHR':
            ans = self.reg[reg_a] >> self.reg[reg_b]
            self.reg[reg_a] = ans
        elif op == 'MOD':
            ans = self.reg[reg_a] % self.reg[reg_b]
            self.reg[reg_a] = ans
        else:
            raise Exception("Unsupported ALU operation")

    def handle_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def handle_prn(self, operand_a, operand_b):
        value = self.reg[operand_a]
        print(value)
        self.pc += 2

    def handle_hlt(self, operand_a, operand_b):
        running = False
        sys.exit()

    def handle_add(self, operand_a, operand_b):
        self.alu('ADD', operand_a, operand_b)
        self.pc += 3

    def handle_sub(self, operand_a, operand_b):
        self.alu('SUB', operand_a, operand_b)
        self.pc += 3

    def handle_mul(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def handle_div(self, operand_a, operand_b):
        self.alu('DIV', operand_a, operand_b)
        self.pc += 3

    def push(self, opa, opb):
        # decrement stack pointer
        self.reg[self.sp] -= 1
        # get value from register
        val = self.reg[opa]
        # copy it in memory
        self.ram_write(self.reg[self.sp], val)
        self.pc += 2

    def pop(self, opa, opb):
        # copy the value from address pointed to by SP  in memory
        val = self.ram_read(self.reg[self.sp])
        # and save value to given register
        self.reg[opa] = val
        # increment SP
        self.reg[self.sp] += 1
        self.pc += 2

    def call(self, opa, opb):
        '''return address gets pushed on the stack'''

        # compute return address
        return_addr = self.pc + 2

        # push the return address aka opb aka pc+2 on the stack
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], return_addr)

        # set the pc to the value in the given register
        self.pc = self.reg[self.ram[self.pc + 1]]

    def cmp(self, reg_a, reg_b):
        self.alu('CMP', reg_a, reg_b)
        self.pc += 3

    def jmp(self, reg_a, *kwargs):
        self.pc = self.reg[reg_a]

    def jeq(self, reg_a, *kwargs):
        '''If equal flag is set (true), jump to the address stored in given register.'''
        if self.fl & 0b00000001:
            self.jmp(reg_a)
        else:
            self.pc += 2
    
    def jge(self, reg_a, *kwargs):
        '''If greater than or equal flag is set (true), jump to address stored in given register.'''
        if self.fl >> 1 == 1 or self.fl & 0b00000001:
            self.jmp(reg_a)
        else:
            self.pc += 2

    def jgt(self, reg_a, *kwargs):
        '''If greater than flag is set (true), jump to address stored in given register.'''
        if self.fl >> 1 == 1:
            self.jmp(reg_a)
        else:
            self.pc += 2

    def jle(self, reg_a, *kwargs):
        '''If less than or equal flag is set (true), jump to address stored in given register.''' 
        if self.fl >> 2 or self.fl & 0b00000001:
            self.jmp(reg_a)
        else:
            self.pc += 2
    
    def jlt(self, reg_a, *kwargs):
        '''If less than flag is set (true), jump to address stored in given register.'''
        if self.fl >> 2:
            self.jmp(reg_a)
        else:
            self.pc += 2

    def jne(self, reg_a, *kwargs):
        '''If equal flag is clear (false, 0), jump to address stored in given register.'''
        if self.fl & 0b00000001:
            self.pc += 2
        else:
            self.jmp(reg_a)

    def ret(self, opa, opb):
        '''return address gets popped off the stack and stored in PC'''

        # pop return address from top of stack
        return_addr = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

        # set the pc
        self.pc = return_addr

    def st(self, reg_a, reg_b):
        '''Store value in regB in the address stored in regA.'''
        self.ram_write(self.reg[reg_a], self.reg[reg_b])

    def handle_and(self, operand_a, operand_b):
        self.alu('AND', operand_a, operand_b)
        self.pc += 3

    def handle_or(self, operand_a, operand_b):
        self.alu('OR', operand_a, operand_b)
        self.pc += 3 

    def handle_xor(self, operand_a, operand_b):
        self.alu('XOR', operand_a, operand_b)
        self.pc += 3

    def handle_not(self, operand_a, operand_b):
        self.alu('NOT', operand_a, operand_b)
        self.pc += 2

    def handle_shl(self, operand_a, operand_b):
        self.alu('SHL', operand_a, operand_b)
        self.pc += 3

    def handle_shr(self, operand_a, operand_b):
        self.alu('SHR', operand_a, operand_b)
        self.pc += 3

    def handle_mod(self, operand_a, operand_b):
        self.alu('MOD', operand_a, operand_b)
        self.pc += 3

    def iret(self):
        '''return from an interrupt handler.'''

        # registers R6-R0 are popped off the stack, in that order
        for i in range(6, -1, -1):
            self.pop(i)
        # FL register is popped off the stack
        # return address is popped off the stack and stored in PC
        # interrupts are re-enabled
        pass

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            # read the mar stored in PC, and store in IR
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir in self.branchtable:
                self.branchtable[ir](operand_a, operand_b)
            else:
                print('Unknown instruction')
                print(ir, self.pc)
                running = False

    def ram_read(self, mar):
        '''Return value stored at address (mar) param.'''
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        '''Should write given value (mdr) to given address (mar).'''
        self.ram[mar] = mdr
"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0 # program counter, the address of the current instruction
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[MUL] = self.handle_mul

    def load(self, file):
        """Load a program into memory."""

        address = 0

        program = []

        with open(file) as f: # what about case to handle if index out of range
            # aka no argument provided to command line
            for line in f:
                val = line.split("#")[0].strip()
                if val == '':
                    continue
                cmd = int(val, 2)
                self.ram[address] = cmd
                address += 1

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
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

    def handle_mul(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
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
                running = False

    def ram_read(self, mar):
        '''Return value stored at address (mar) param.'''
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        '''Should write given value (mdr) to given address (mar).'''
        self.ram[mar] = mdr
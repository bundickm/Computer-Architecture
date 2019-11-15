"""CPU functionality."""

import sys


IM = 5  # R5 = interrupt mask (IM)
IS = 6  # R6 = interrupt status (IS)
SP = 7  # R7 = stack pointer (SP)


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.registers = [0b0] * 8  # Registers R0-R7
        self.ram = [0] * 256

        self.halted = False

        self.pc = 0 # Program Counter, location of current instruction executing
        self.fl = 0 # Flags
        self.ir = None # Instruction Register, current instruction executing

        self.ram = [0b0] * 0xFF
        self.registers[SP] = 0xf4

        self.OPCODES = {
            0b01000111: 'PRN',
            0b00000001: 'HLT',
            0b10000010: 'LDI',
            0b10100000: 'ADD',
            0b10100010: 'MUL',
            0b01000101: 'PUSH',
            0b01000110: 'POP',
            0b10000100: 'STOR',
            0b01010000: 'CALL',
            0b00010001: 'RET',
        }

    def load(self, filename):
        """Load a program into memory."""
        address = 0

        try:
            # Read in the program
            with open(filename, 'r') as file:
                lines = (line for line in file.readlines() 
                        if not (line[0]=='#' or line[0]=='\n'))
                program = [int(line.split('#')[0].strip(), 2) 
                          for line in lines]

            for instruction in program:
                self.ram[address] = instruction
                address += 1
        except FileNotFoundError as e:
            print(e)
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == 'ADD':
            self.registers[reg_a] += self.registers[reg_b]
        elif op == 'SUB':
            self.registers[reg_a] -= self.registers[reg_b]
        elif op == 'MUL':
            self.registers[reg_a] *= self.registers[reg_b]
        elif op == 'DIV':
            self.registers[reg_a] //= self.registers[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def ram_read(self, mar):
        return self.ram[mar]

    def op_prn(self, r1):
        val = self.registers[r1]
        print(f'value: {val}')
        self.pc += 2

    def op_ldi(self, r1, r2):
        self.registers[r1] = r2
        self.pc += 3

    def op_alu(self, op, r1, r2):
        self.alu(op, r1, r2)
        self.pc += 3

    def op_push(self, r1):
        val = self.registers[r1]
        self.registers[SP] -= 1
        self.ram_write(val, self.registers[SP])
        self.pc += 2

    def op_pop(self, r1):
        val = self.ram_read(self.registers[SP])
        self.registers[r1] = val
        self.registers[SP] += 1
        self.pc += 2

    def op_call(self, r1):
        self.registers[SP] -= 1
        self.ram_write(self.pc + 2, self.registers[SP])
        self.pc = self.registers[r1]

    def op_ret(self):
        val = self.ram_read(self.registers[SP])
        self.pc = val
        self.registers[SP] += 1

    def run(self):
        while not self.halted:
            self.ir = self.ram[self.pc]
            op = self.OPCODES[self.ir]
            r1 = self.ram_read(self.pc + 1)
            r2 = self.ram_read(self.pc + 2)

            if op == 'LDI': # Save to Register
                self.op_ldi(r1, r2)
            elif op == 'PRN': # Print
                self.op_prn(r1)
            elif op in ['ADD', 'MUL', 'SUB', 'DIV']: # Math
                self.op_alu(op, r1, r2)
            elif op == 'PUSH': # Write to Stack
                self.op_push(r1)
            elif op == 'POP': # Pull from Stack
                self.op_pop(r1)
            elif op == 'CALL':
                self.op_call(r1)
            elif op == 'RET':
                self.op_ret()
            elif op == 'HLT': # Exit
                self.halted = True
            else:
                print(f'Unknown Operation: {op}')
                self.halted = True
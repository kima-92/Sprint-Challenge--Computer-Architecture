"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        self.ram = [0] * 256
        self.running = True

        # General-purpose Registers
        self.registers = [0] * 8        # 8 general-purpose registers, like variables. R0, R1, R2, R3...

        # Internal Registers
        self.program_counter = 0        # Index of the current executing intruction
        self.instruction_register = 0   # Copy of the program_counter
        self.mar = 0                    # Memory Address Register, holds the memory address we're reading or writing
        self.mdr = 0                    # Memory Data Register, holds the value to write or the value just read
        self.SP = 7                     # Slot in registers that will hold the Stack_Pointer
        self.FL = 0                     # Flags, current flags status

        # Method Keys Dictionaries
        self.functions_dict = {}
        self.alu_functs_dict = {}

        # CPU Method Commands
        self.HLT = 0b00000001
        self.PRN = 0b01000111
        self.LDI = 0b10000010
        self.CALL = 0b01010000
        self.RET = 0b00010001

        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110

        # Stack Commends
        self.PUSH = 0b01000101
        self.POP = 0b01000110

        # ALU Method Commands
        self.ADD = 0b10100000
        self.MUL = 0b10100010
        self.CMP = 0b10100111

        # Comparison Flags
        self.less_than_fl = 0b00000100
        self.greater_than_fl = 0b00000010
        self.equal_to_fl = 0b00000001
        
    def load(self):
        """Load a program into memory."""

        # Grab the file with the intructions entered,
        # after running this program:
        intruction_file = sys.argv[1]

        # TODO: error checking on sys.argv

        with open(intruction_file) as f:
            index = 0
            
            # Go through each line
            for line in f:
                # Split the string by #
                str_line = line.split("#")

                # Try to get the number in that line
                try:
                    number = int(str_line[0], 2)  # The 2 tells it that this should be a base 2 number (binary)
                    # Save it in RAM
                    self.ram_write(index, number)

                    index += 1

                # If you can't, just continue to the next line
                except ValueError:
                    continue

        # Print what you have in memory for index 0-num
        num = 15
        print(f"\nRAM's current state from [:{num}]: \n{self.ram[:num]}\n")

        # Set up functions_dictionary, and the ALU_dictionary
        self.setup_functions_dict()
        self.setup_ALU_functions_dict()

        # Set R7 to store the SP,
        # pointing to F4 (a RAM slot)
        self.registers[self.SP] = 0xF4
    
    # Set up functions dictionary
    def setup_functions_dict(self):
        self.functions_dict = {
            self.HLT : self.halt,
            self.PRN : self.print_value_at_reg,
            self.LDI : self.ldi,
            # Stack functions
            self.PUSH : self.push,
            self.POP : self.pop,
            # Subroutine Calling functions
            self.CALL : self.call,
            self.RET : self.return_from_call,

            self.JMP : self.jump,
            self.JEQ : self.if_equal,
            self.JNE : self.if_not_equal
        }

    # Setup ALU functions Keys Dictionary
    def setup_ALU_functions_dict(self):
        self.alu_functs_dict = {
            self.ADD : "ADD",
            self.MUL : "MUL",
            self.CMP : "CMP"
        }

    def alu(self, op, registers_a=None, registers_b=None):
        """ALU operations."""

        if op == "ADD":
            self.add()
            #self.registers[registers_a] += self.reg[registers_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.multiply()
        elif op == "CMP":
            self.compare()
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.program_counter,
            #self.fl,
            #self.ie,
            self.ram_read(self.program_counter),
            self.ram_read(self.program_counter + 1),
            self.ram_read(self.program_counter + 2)
        ), end='')
        
        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()

    # Return what's in RAM at this index (program_counter)
    def ram_read(self, program_counter):
        return self.ram[program_counter]

    # Save a value into RAM, at this index (program_counter)
    def ram_write(self, program_counter, value):
        self.ram[program_counter] = value
        return value

    # Run the CPU
    def run(self):
        self.trace()  # For debugging

        # While-Loop that constantly runs the Program
        while self.running:
            # Set the current_instruction
            curr_instruction = self.ram[self.program_counter]

            # Print what instruction is currently beign called
            print(f"\n--- Intruction called: {curr_instruction} ---")
            print(f"--- program counter: {self.program_counter} --- \n")

            # If curr_instuction is 0
            if curr_instruction == 0b00000000:
                print("Empty Instruction of 0")
                # Continue to the next instruction
                self.program_counter += 1

            # Elif : If curr_instruction is in the functions_dictionary
            elif curr_instruction in self.functions_dict:
                # Call the function for that instruction
                f = self.functions_dict[curr_instruction]
                f()
            
            # Elif : If curr_instruction is in the alu_functs_dict
            elif curr_instruction in self.alu_functs_dict:
                self.alu(self.alu_functs_dict[curr_instruction])

            # Else : If that instruction is not in the functions_dict, or in the alu_functs_dict
            else:
                print("Instruction NOT in functions_dict, and NOT in alu_functs_dict")
                # Just go to the next instruction
                self.program_counter += 1

    # CPU Intruction Functions

    # HLT : Stop running the program
    def halt(self):
        # Print that your using this function
        print(f"Called intruction {self.ram[self.program_counter]}, HALT:")

        # Set running to False, to stop the While-Loop
        self.running = False

        # Print that we used HALT
        print(f"Gonna HALT now..")

    # PRN : Print the value at provited register
    def print_value_at_reg(self):
        # Print that your using this function
        print(f"Called intruction {self.ram[self.program_counter]}, print_value_at_reg:")

        # Go to next intruction
        self.program_counter += 1

        # Get the register_index
        reg_index = self.ram_read(self.program_counter)

        # Print the value at this register
        print(self.registers[reg_index])

        # Go to the next instruction
        self.program_counter += 1

    # LDI : Saving a value in a Register
    def ldi(self):
        # Print that your using this function
        print(f"Called intruction {self.ram[self.program_counter]}, LDI:")

        # grab the next intruction from RAM;
        # Which it's the register_index at which to save the value
        self.program_counter += 1
        reg_index = self.ram[self.program_counter]

        # Grab the next intruction,
        # Which is the value that needs to be saved
        self.program_counter += 1
        num = self.ram[self.program_counter]

        # Save that value in correct Register
        self.registers[reg_index] = num

        # Go to the next instruction
        self.program_counter += 1

        print(f"Saved num: {num}, at reg: {reg_index}")
    
    # PUSH : Push to the Stack
    def push(self):
        # Print that your using this function
        print(f"Called intruction {self.ram[self.program_counter]}, Push:")
        
        # Decrement SP
        self.registers[self.SP] -= 1
        
        # Get the next instruction,
        # which is the register_number that has the value that needs to be stored (pushed)
        self.program_counter += 1
        reg_num = self.ram[self.program_counter]

        # Get the value at this register
        value = self.registers[reg_num] 
        
        # Get the RAM slot currently holding the top of the Stack,
        # from the Stack_Pointer ( SP == R7 )
        top_of_stack_ram_slot = self.registers[self.SP]
        
        # Store the value in RAM at that top_of_stack_ram_slot
        self.ram[top_of_stack_ram_slot] = value

        # Go to the next instruction
        self.program_counter += 1

        print(f"Value at the top of the stack: {value}, stored in ram[top_of_stack_addr]: {top_of_stack_ram_slot}")

    # POP : Pop from the Stack
    def pop(self):
        # Print that your using this funciton
        print(f"Called intruction {self.ram[self.program_counter]}, Pop:")

        # Get the RAM slot currently holding the value that needs to be popped,
        # from the SP
        ram_slot = self.registers[self.SP]

        # Get the value at that RAM_slot
        value = self.ram_read(ram_slot)

        # Get the next intruction,
        # which says in which Register to store the popped value
        self.program_counter += 1
        reg_num = self.ram_read(self.program_counter)

        # Save the value at this register_num
        self.registers[reg_num] = value

        # Decrement the SP 
        self.registers[self.SP] -= 1

        # Go to the next intruction
        self.program_counter += 1

        # Return the value
        return self.registers[reg_num]

    # CALL : Calling a subroutine (function)
    def call(self):
        # Print that your using this funciton
        print(f"Called intruction {self.ram[self.program_counter]}, CALL:")

        # Save the address it needs to return to,
        # when it's time to call self.return_from_call
        return_addr = self.program_counter + 2  # Where we're going to RETURN to
        
        # Push on the stack:

        # Reduce the SP
        self.registers[self.SP] -= 1
        # Grab the value of register 7  ( R7 == SP ),
        # Which is the RAM slot with the (currently empty) top of the stack
        top_of_stack_slot = self.registers[self.SP]
        # Save the return address in RAM at the top of the Stack
        self.ram[top_of_stack_slot] = return_addr      
        
        # Get the next instruction,
        # which tells you which register currently holds the 
        # subroutine that needs to be called now
        self.program_counter += 1
        subroutine_reg = self.ram[self.program_counter]
        subroutine_ram_slot = self.registers[subroutine_reg]
        
        # Set program_counter to subroutine_ram_slot so it will call this 
        # function in the next loop
        self.program_counter = subroutine_ram_slot

    # RET : Return from calling a subroutine (function)
    def return_from_call(self):
        # Print that your using this funciton
        print(f"Called intruction {self.ram[self.program_counter]}, Return from CALL:")

        # Grab the ram_slot it needs to return to,
        # from the SP ( R7 )
        sp_reg = self.registers[self.SP]
        return_addr = self.ram_read(sp_reg)

        # Set the program_counter to that address (RAM slot)
        self.program_counter = return_addr

    # JMP : Jump 
    def jump(self):
        # Print that your using this funciton
        print(f"Called intruction {self.ram[self.program_counter]}, JMP:")

        # Get the register_num with the instruction (address) we need to jump to
        self.program_counter += 1
        reg_num = self.ram_read(self.program_counter)
        print(f"reg_num: {reg_num}, pc: {self.program_counter}, ram[pc]: {self.ram[self.program_counter]}")

        # Get the address
        address = self.registers[reg_num]
        print(f"reg_num: {reg_num}, address: {address}, pc: {self.program_counter}, ram[pc]: {self.ram[self.program_counter]}")

        # Set the pc to jump to that address
        self.program_counter = address



        print(f"reg_num: {reg_num}, address: {address}, pc: {self.program_counter}, ram[pc]: {self.ram[self.program_counter]}")
        """
        JMP register
        Jump to the address stored in the given register.
        Set the PC to the address stored in the given register."""

    # JEQ : Check if equal_flag == True
    def if_equal(self):
        # Print that your using this funciton
        print(f"Called intruction {self.ram[self.program_counter]}, JEQ (is equal):")

        # If FL is set to equal_to_fl (the CMP gave Equal)
        if self.FL == self.equal_to_fl:
            # Re-set FL
            #self.FL = 0b00000000

            # Jump to the address stored in the given register
            print("It is equal to, so jump")
            self.jump()

        # Else: If it's not equal
        else:
            # Don't Jump, just continue
            print("It's NOT equal to, so continue")
            self.program_counter += 2
            
        """JEQ register
        If equal flag is set (true), jump to the address stored in the given register."""

    # JNE : Check if equal_flag == False
    def if_not_equal(self):
        # Print that your using this funciton
        print(f"Called intruction {self.ram[self.program_counter]}, JNE (not equal):")

        # If FL is set to equal_to_fl (CMP gave Equal)
        if self.FL == self.equal_to_fl:

            # Don't jump, Continue
            print("it IS Equal to, so continue")
            self.program_counter += 2
        
        # Else: If it's not Equal
        else:
            # Jump to the address stored in the given register
            print("in not equal to, so jump")
            self.jump()

        """JNE register
        If E flag is clear (false, 0), jump to the address stored in the given register."""

    # ALU Intruction Functions

    # ADD : Add two values
    def add(self):
        # Print that your using this function
        print(f"Called intruction {self.ram[self.program_counter]}, Add:")

        # Go to the next intruction,
        # and get the reg_index for the FIRST value
        self.program_counter += 1
        reg_index1 = self.ram_read(self.program_counter)

        # Go to the next intruction,
        # and get the reg_index for the SECOND value
        self.program_counter += 1
        reg_index2 = self.ram_read(self.program_counter)

        # Get the values
        value1 = self.registers[reg_index1]
        value2 = self.registers[reg_index2]
        print(f"val1: {value1}, val2: {value2}")

        value1 += value2

        # Go to the next intruction
        self.program_counter += 1

        print(f"After mul, val1: {value1}, val2: {value2}")

    # MUL : Multiplying two values
    def multiply(self):
        # Print that your using this function
        print(f"Called intruction {self.ram[self.program_counter]}, Multiply:")

        # Go to the next intruction,
        # and get the reg_index for the FIRST value
        self.program_counter += 1
        reg_index1 = self.ram_read(self.program_counter)

        # Go to the next intruction,
        # and get the reg_index for the SECOND value
        self.program_counter += 1
        reg_index2 = self.ram_read(self.program_counter)

        # Get the values
        value1 = self.registers[reg_index1]
        value2 = self.registers[reg_index2]
        print(f"val1: {value1}, val2: {value2}")

        value1 *= value2

        # Go to the next intruction
        self.program_counter += 1

        print(f"After mul, val1: {value1}, val2: {value2}")
    
    # CMP : Compare two values
    def compare(self):
        # Print that your using this function
        print(f"Called intruction {self.ram[self.program_counter]}, Compare:")
        
        # Get the next intruction,
        # which is the register with the FIRST num to compare
        self.program_counter += 1
        reg_a = self.ram_read(self.program_counter)
        var_a = self.registers[reg_a]

        # Get the next intruction,
        # which is the register with the SECOND num to compare
        self.program_counter += 1
        reg_b = self.ram_read(self.program_counter)
        var_b = self.registers[reg_b]

        # Set FL depending on whether a is LESS, GREATER or EQUAL to b
        # 00000LGE
        if var_a < var_b:
            print(f"{var_a} is less than {var_b}")
            self.FL = self.less_than_fl
        elif var_a > var_b:
            print(f"{var_a} is greater than {var_b}")
            self.FL = self.greater_than_fl
        elif var_a == var_b:
            print(f"{var_a} is equal to {var_b}")
            self.FL = self.equal_to_fl
        else: 
            print("Couldn't Compare Values")

        print(f"FL status: {bin(self.FL)}")

        # Go to the next instruction
        self.program_counter += 1
        



        


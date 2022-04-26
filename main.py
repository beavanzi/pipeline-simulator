from array import array
from atexit import register
import string
import sys
from tabulate import tabulate
from copy import deepcopy


# MODELO DE INSTRUÇÃO:
# [4 bits opcode | 4 bits dest | 4 bits r1 | 4 bits r2]

# MODELO DE DADO QUE NAO É INSTRUÇAO:
# 4 bits

# OPCODES:
# add - 0001
# sub - 0010
# mul - 0100
# div - 1000

class Instruction:
    id_number: int
    opcode: string
    dest: string
    r1: string
    r2: string

    def __init__(self, pc, opcode, dest, r1, r2) -> None:
        self.id = pc
        self.opcode = opcode
        self.dest = dest
        self.r1 = r1
        self.r2 = r2


class Memory:
    memory: array

    def __init__(self) -> None:
        self.memory = []
        self.head = 0

    def saveInMemory(self, dataOrInstruction: list):
        self.memory.append(dataOrInstruction)

    def getNextInMemory(self) -> Instruction:
        dataOrInstruction = deepcopy(self.memory[self.head])
        self.head = self.head + 1

        return dataOrInstruction


# class Table:
#     def __init__(self) -> None:


class Registers:
    def __init__(self):
        self.instructions_status = []
        self.MBR = ""
        self.MAR = ""
        self.PC = 0

        # self.register_status = {
        #     'r0': "",
        #     'r1': "",
        #     'r2': "",
        #     'r3': "",
        #     'r4': "",
        #     'r5': "",
        #     'rb': "",
        #     'MBR': "",
        #     'MAR': "",

        #     }

    def is_all_instructions_writen(self):
        for inst in self.instructions_status:
            if inst.write == "":
                return False
        return True


def print_table_example():
    l = [["Hassan", 21, "LUMS"], ["Ali", 22, "FAST"], ["Ahmed", 23, "UET"]]
    table = tabulate(l, headers=['Name', 'Age', 'University'], tablefmt='orgtbl')

    print(table)


def is_instruction(data):
    return len(data) == 4


def search(memory: Memory, registers: Registers, clock: int):
    memory_information = memory.getNextInMemory()

    if (is_instruction(memory_information)):
        inst = Instruction(clock, memory_information[0], memory_information[1], memory_information[2],
                           memory_information[3])
        return inst
    else:
        # entao nao é instruçao, é dado, o que fazer???
        pass


def read():
    pass


def execution():
    pass


def write():
    pass


def processor_simulation(memory: Memory):
    registers: Registers = Registers()

    pipeline(memory, registers)


def empty_pipeline(memory: Memory, registers: Registers):
    return len(memory) <= registers.PC  # and scoreboarding.is_all_instructions_writen()


def pipeline(memory: Memory, registers, clock):
    write(registers)
    execution(registers)
    read(registers)
    search(memory, registers, clock)


# def entryInstruction():
#     print("Escolha um opcode: ")
#     print("Qual é o registrador de destino? ")
#     print("Qual é o registrador r1? ")
#     print("Qual é o registrador r2? ")


## FUNÇOES DE FILE -------------------------------

def read_file(file_path):
    file_in = open(file_path, "r")
    memory: Memory = append_lines_to_memory(file_in)
    create_log_file()
    file_in.close()
    return memory


def append_lines_to_memory(opened_file):
    memory: Memory = Memory()

    for line in opened_file:
        opcode = line[0:3]
        rd = line[4:7]
        r1 = line[8:11]
        r2 = line[12:15]
        # inst = Instruction(opcode, rd, r1, r2)
        memory.saveInMemory([opcode, rd, r1, r2])

    return memory


def create_log_file():
    file_out = open(file_out_name(), "w")
    file_out.close()


def file_out_name():
    file = sys.argv[1]
    file = file.split(".")
    out_path = file[0]
    return "{}.out".format(out_path)


def write_log(scoreboarding, functional_units, clock: int):
    file_out = open(file_out_name(), "a")
    file_out.write('\n\nClock: ' + clock.__str__())
    scoreboarding.show_instructions_status(file_out)
    functional_units.show_functional_units_table(file_out)
    scoreboarding.show_registers_status_table(file_out)
    file_out.close()


## --------------------------------------------------


def __init__():
    file = sys.argv[1]
    memory = read_file(file)
    processor_simulation(memory)
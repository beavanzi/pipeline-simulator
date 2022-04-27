import string
import sys
from tabulate import tabulate
from copy import deepcopy


# MODELO DE INSTRUÇÃO:
# [4 bits opcode | 4 bits dest | 4 bits r1 | 4 bits r2]

# MODELO DE DADO QUE NAO É INSTRUÇAO:
# [0000|0000|0000| 4 bits informaçao]
# será que é isso mesmo??

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

    def getId(self):
        return 'Inst ' + self.id

    def setR1(self, value):
        self.r1 = value

    def setR2(self, value):
        self.r2 = value


class Memory:
    memory: list

    def __init__(self) -> None:
        self.memory = []

    def saveInMemory(self, word: list):
        self.memory.append(word)

    def getMemorySize(self):
        return len(self.memory)

    def getByAddress(self, index):
        word: list = self.memory[index]
        return word


class PipelineTable:
    instructionsStatuses: list[list]

    def __init__(self):
        self.instructionsStatuses = []

    def setInstructionSearched(self, clock, inst):
        self.setNewLineOrUpdateLast(clock, inst, 0)

    def setInstructionDecoded(self, clock, inst):
        self.setNewLineOrUpdateLast(clock, inst, 1)

    def setInstructionExecuted(self, clock, inst):
        self.setNewLineOrUpdateLast(clock, inst, 2)

    def setInstructionAccessedMemory(self, clock, inst):
        self.setNewLineOrUpdateLast(clock, inst, 3)

    def setInstructionWrote(self, clock, inst):
        if len(self.instructionsStatuses) >= 4:
            line = self.createNewLine(clock, inst, inst)
            self.instructionsStatuses.append(line)

    def isInstructionsEmpty(self):
        return len(self.instructionsStatuses) == 0

    def setNewLineOrUpdateLast(self, clock, inst, newLineCriterion):
        instPosition = newLineCriterion + 1

        if len(self.instructionsStatuses) == newLineCriterion:
            line = self.createNewLine(clock, inst, instPosition)
            self.instructionsStatuses.append(line)
        else:
            self.updateLastLine(inst, instPosition)

    def updateLastLine(self, newValue, index):
        lastLine = self.instructionsStatuses[-1]
        lastLine[index] = newValue

    def createNewLine(self, clock, value, index):
        line = [clock, "", "", "", "", ""]
        line[index] = value
        return line

    def printTable(self):
        table = tabulate(self.instructionsStatuses, headers=['Clock', "Busca", "Decodificacao", "Execucao", "Acesso a Memoria", "Escrita"], tablefmt='orgtbl')
        print(table)


class ALU:
    def __init__(self):
        self.r1 = 0
        self.r2 = 0

    def add(self):
        return self.r1 + self.r2

    def sub(self):
        return self.r1 - self.r2

    def mul(self):
        return self.r1 * self.r2

    def div(self):
        return self.r1 / self.r2

    def setR1(self, value):
        self.r1 = value

    def setR2(self, value):
        self.r2 = value


class Registers:
    def __init__(self):
        # self.instructions_status = []
        self.MBR = []     # armazena uma palavra de dados
        self.MAR = None     # armazena um end de memoria
        self.PC = 0       # armazena o end da inst a ser executada
        self.IR = None      # contem a ultima instruçao buscada

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

    def incrementPc(self):
        self.PC = self.PC + 1

    def setMBR(self, mbr):
        self.MBR = deepcopy(mbr)

    def setMAR(self, mar):
        self.MAR = deepcopy(mar)

    def setIR(self, ir):
        self.IR = deepcopy(ir)


# FUNÇOES AUXILIARES ----------------------------------------------

def is_instruction(data):
    opcodes = {
        "0001": "add",
        "0010": "sub",
        "0100": "mul",
        "1000": "div"
    }

    for opcode in opcodes.keys():
        if str(data[0]) == opcode and len(data) == 4:
            return True

    return False


def empty_pipeline(memory: Memory, registers: Registers, table: PipelineTable):
    return len(table.instructionsStatuses) > registers.PC


def has_memory_to_read(memory, registers):
    return memory.getMemorySize() > registers.PC


# ----------------------------------------------------------------------
# FUNCOES DO PROCESSADOR -----------------------------------------------

def search(memory: Memory, registers: Registers, table: PipelineTable):
    if has_memory_to_read(memory, registers):
        registers.setMAR(registers.PC)
        registers.setMBR(memory.getByAddress(registers.MAR))
        memory_information: list = deepcopy(registers.MBR)
        if is_instruction(memory_information):
            inst = Instruction(registers.PC - 1, memory_information[0], memory_information[1], memory_information[2],
                               memory_information[3])
            registers.setIR(inst)
            table.setInstructionSearched(registers.PC - 1, inst.getId())


        registers.incrementPc()


def decode(registers: Registers, table: PipelineTable):
    inst: Instruction = deepcopy(registers.IR)

    while ((isIndirectFetch(inst.r1) or isIndirectFetch(inst.r2)) and not isStall(inst)):
        if (isIndirectFetch(inst.r1)):
            registers.setMAR(inst.r1)
            registers.setMBR(memory.getByAddress(registers.MAR))
            inst.setR1(registers.MBR)
            registers.setIR(inst)

        if (isIndirectFetch(inst.r2)):
            registers.setMAR(inst.r2)
            registers.setMBR(memory.getByAddress(registers.MAR))
            inst.setR2(registers.MBR)
            registers.setIR(inst)

    if isStall(inst):
        table.setInstructionDecoded(registers.PC - 1, "----STALL----")
    else:
        table.setInstructionDecoded(registers.PC - 1, inst.getId())


def execution(registers: Registers, pipeTable: PipelineTable):
    pass


def memoryAccess(registers: Registers, pipeTable: PipelineTable):
    pass


def write(registers: Registers, pipeTable: PipelineTable):
    pass


def processor_simulation(memory: Memory):
    registers: Registers = Registers()
    pipeline_table: PipelineTable = PipelineTable()
    clock = 0

    while not (empty_pipeline(memory, registers, pipeline_table)):
        pipeline(memory, registers, pipeline_table)
        # write_log(scoreboarding, functional_units, clock)
        pipeline_table.printTable()
        clock = clock + 1


def pipeline(memory: Memory, registers: Registers, pipe_table: PipelineTable):
    write(registers, pipe_table)
    memoryAccess(registers, pipe_table)
    execution(registers, pipe_table)
    decode(registers, pipe_table)
    search(memory, registers, pipe_table)


# def entryInstruction():
#     print("Escolha um opcode: ")
#     print("Qual é o registrador de destino? ")
#     print("Qual é o registrador r1? ")
#     print("Qual é o registrador r2? ")


# --------------------------------------------------
# FUNÇOES DE FILE ---------------------------------

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


# write log era do trab do anderson
# def write_log(scoreboarding, functional_units, clock: int):
#     file_out = open(file_out_name(), "a")
#     file_out.write('\n\nClock: ' + clock.__str__())
#     scoreboarding.show_instructions_status(file_out)
#     functional_units.show_functional_units_table(file_out)
#     scoreboarding.show_registers_status_table(file_out)
#     file_out.close()


# --------------------------------------------------

if __name__ == '__main__':
    file = sys.argv[1]
    memory = read_file(file)
    processor_simulation(memory)

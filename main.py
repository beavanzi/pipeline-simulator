import math
from atexit import register
import string
import sys
from tabulate import tabulate
from copy import deepcopy
from typing import List
import random


# MODELO DE INSTRUÇÃO:
# [4 bits opcode | 4 bits dest | 4 bits r1 | 4 bits r2]

# OPCODES:
# add - 0000
# sub - 0001
# mul - 0010
# div - 0011

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
        return 'Inst ' + str(self.id)

    def setR1(self, value):
        self.r1 = value

    def setR2(self, value):
        self.r2 = value

    def getR1(self):
        return self.r1

    def getR2(self):
        return self.r2

    def getOpcode(self):
        return self.opcode


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
        self.instructionsStatuses = [[""] * 5]

    def setInstructionSearched(self, clock, inst):
        self.setNewLineOrUpdateLast(clock, inst, 0)

    def setInstructionDecoded(self, clock, inst):
        self.setNewLineOrUpdateLast(clock, inst, 1)

    def setInstructionExecuted(self, clock, inst):
        self.setNewLineOrUpdateLast(clock, inst, 2)

    def setInstructionAccessedMemory(self, clock, inst):
        self.setNewLineOrUpdateLast(clock, inst, 3)

    def setInstructionWrote(self, clock, inst):
        self.setNewLineOrUpdateLast(clock, inst, 4)

    def isInstructionsEmpty(self):
        return len(self.instructionsStatuses) == 0

    def setNewLineOrUpdateLast(self, clock, inst, newLineCriterion):
        if clock == len(self.instructionsStatuses) - 1:
            self.instructionsStatuses[clock][newLineCriterion] = inst
        else:
            newLine = [""] * 5
            newLine[newLineCriterion] = inst
            self.instructionsStatuses.append(newLine)

    def printTable(self):
        table = tabulate(self.instructionsStatuses, headers=[
            "Busca", "Decodificacao", "Execucao", "Acesso a Memoria", "Escrita"], tablefmt='orgtbl')
        print(table)


class ALU:
    def __init__(self, op1, op2):
        self.r1 = op1
        self.r2 = op2

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
        self.MBR = []  # armazena uma palavra de dados
        self.MAR = None  # armazena um end de memoria
        self.PC = 0  # armazena o end da inst a ser executada
        self.IR = None  # contem a ultima instruçao decodificada
        self.registers = [random.randint(0, 10) for _ in range(16)] # outros registradores

    def incrementPc(self):
        self.PC = self.PC + 1

    def setMBR(self, mbr):
        self.MBR = deepcopy(mbr)

    def setMAR(self, mar):
        self.MAR = deepcopy(mar)

    def setIR(self, ir):
        self.IR = deepcopy(ir)


# Barramentos dos estágios

class Bus():
    def __init__(self) -> None:
        self.ID = None
        self.inst = None
        self.result = None
        self.op1 = None
        self.op2 = None
        self.resultValue = None
        pass

    def getInstruct(self):
        return self.inst

    def setInstruct(self, inst):
        self.inst = inst

    def getID(self):
        return self.ID

    def setID(self, ID):
        self.ID = ID

    def getResult(self):
        return self.result

    def setResult(self, result):
        self.result = result

    def getResultValue(self):
        return self.resultValue

    def setResultValue(self, result):
        self.resultValue = result

    def getOP1(self):
        return self.op1

    def setOP1(self, op1):
        self.op1 = op1

    def getOP2(self):
        return self.result

    def setOP2(self, op2):
        self.op2 = op2

    def reset(self):
        self.ID = None
        self.inst = None
        self.result = None
        self.op1 = None
        self.op2 = None
        self.resultValue = None
        pass

    def isEmpty(self):
        return self.inst == None


# FUNÇOES AUXILIARES ----------------------------------------------

def is_instruction(data):
    opcodes = {
        "0000": "add",
        "0001": "sub",
        "0010": "mul",
        "0011": "div"
    }

    for opcode in opcodes.keys():
        if str(data[0]) == opcode and len(data) == 4:
            return True

    return False


def empty_pipeline(buses):
    for i in range(len(buses)):
        if not buses[i].isEmpty():
            return False
    return True


def has_memory_to_read(memory, registers):
    return memory.getMemorySize() > registers.PC


# ----------------------------------------------------------------------
# FUNCOES DO PROCESSADOR -----------------------------------------------

def search(memory: Memory, registers: Registers, table: PipelineTable, bus: List[Bus], clock):
    if has_memory_to_read(memory, registers):
        if bus[0].isEmpty():

            registers.setMAR(registers.PC)
            registers.setMBR(memory.getByAddress(registers.MAR))
            memory_information: list = deepcopy(registers.MBR)
            inst = Instruction(registers.PC, memory_information[0], memory_information[1], memory_information[2],
                               memory_information[3])
            bus[0].setID("Inst " + str(registers.PC))
            bus[0].setInstruct(inst.opcode)
            bus[0].setResult(inst.dest)
            bus[0].setOP1(inst.r1)
            bus[0].setOP2(inst.r2)
            registers.incrementPc()

        table.setInstructionSearched(clock, bus[0].getID())
    bus[4].reset()


def isStall(bus: List[Bus]):
    for i in range(2, len(bus)):
        if bus[0].getOP1() != "" and bus[0].getOP2() != "":
            if not bus[i].isEmpty():
                result = bin(bus[i].getResult())

                if bus[0].getOP1() == result or bus[0].getOP2() == result:
                    return True
    return False


def decode(registers: Registers, table: PipelineTable, bus: List[Bus], clock):
    if not isStall(bus) and not bus[0].isEmpty():
        bus[1].setID(bus[0].getID())
        bus[1].setInstruct(int(bus[0].getInstruct(), 2))
        bus[1].setResult(int(bus[0].getResult(), 2))
        bus[1].setOP1(int(bus[0].getOP1(), 2))
        bus[1].setOP2(int(bus[0].getOP2(), 2))
        inst = Instruction(int(bus[1].getID().split(" ")[1]), bus[1].getInstruct(),
                           bus[1].getResult(), bus[1].getOP1(),
                           bus[1].getOP2())
        registers.setIR(inst)

    if isStall(bus):
        table.setInstructionDecoded(clock, "----STALL----")
    elif bus[0].isEmpty():
        table.setInstructionDecoded(clock, " ")
    else:
        table.setInstructionDecoded(clock, bus[1].getID())
        bus[0].reset()


def execution(registers: Registers, pipeTable: PipelineTable, bus: List[Bus], clock):
    if not bus[1].isEmpty():
        IR = registers.IR
        ULA = ALU(IR.getR1(), IR.getR2())
        result = math.inf
        if IR.getOpcode() == 0:
            result = ULA.add()
        elif IR.getOpcode() == 1:
            result = ULA.sub()
        elif IR.getOpcode() == 2:
            result = ULA.mul()
        elif IR.getOpcode() == 3:
            result = ULA.div()
        bus[2].setID(bus[1].getID())
        bus[2].setInstruct(bus[1].getInstruct())
        bus[2].setResult(bus[1].getResult())
        bus[2].setOP1(bus[1].getOP1())
        bus[2].setOP2(bus[1].getOP2())
        bus[2].setResultValue(result)
        pipeTable.setInstructionExecuted(clock, bus[2].getID())
        bus[1].reset()
    else:
        if not bus[0].isEmpty():
            if "STALL" in pipeTable.instructionsStatuses[clock - 1][1]:
                pipeTable.setInstructionExecuted(clock, "----STALL----")
        else:
            pipeTable.setInstructionExecuted(clock, " ")


def memoryAccess(pipeTable: PipelineTable, bus: List[Bus], clock):
    if not bus[2].isEmpty():
        bus[3].setID(bus[2].getID())
        bus[3].setInstruct(bus[2].getInstruct())
        bus[3].setResult(bus[2].getResult())
        bus[3].setOP1(bus[2].getOP1())
        bus[3].setOP2(bus[2].getOP2())
        bus[3].setResultValue(bus[2].getResultValue())
        pipeTable.setInstructionAccessedMemory(clock, bus[3].getID())
        bus[2].reset()
    else:
        if not bus[0].isEmpty() and pipeTable.instructionsStatuses[clock - 1][1] == "----STALL----":
            pipeTable.setInstructionAccessedMemory(clock, "----STALL----")
        else:
            pipeTable.setInstructionAccessedMemory(clock, " ")


def write(registers: Registers, pipeTable: PipelineTable, bus: List[Bus], clock):
    if not bus[3].isEmpty():
        registers.registers[bus[3].getResult()] = bus[3].getResultValue()
        bus[4].setID(bus[3].getID())
        bus[4].setInstruct(bus[3].getInstruct())
        bus[4].setResult(bus[3].getResult())
        bus[4].setOP1(bus[3].getOP1())
        bus[4].setOP2(bus[3].getOP2())
        bus[4].setResultValue(bus[2].getResultValue())
        pipeTable.setInstructionWrote(clock, bus[4].getID())
        bus[3].reset()
    else:
        pipeTable.setInstructionWrote(clock, " ")


def processor_simulation(memory: Memory):
    registers: Registers = Registers()
    pipeline_table: PipelineTable = PipelineTable()
    buses = []
    for _ in range(5):
        buses.append(Bus())

    clock = initPipeline(memory, registers, pipeline_table, buses)

    while not (empty_pipeline(buses)):
        pipeline(memory, registers, pipeline_table, buses, clock)
        pipeline_table.printTable()
        print_registers(registers)
        clock = clock + 1


def print_registers(registers: Registers):
    table = tabulate([registers.registers], headers=[
        'R0', "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15"], tablefmt='orgtbl')
    print(table)


def initPipeline(memory: Memory, registers: Registers, pipeline_table: PipelineTable, buses: list):
    clock = 0

    search(memory, registers, pipeline_table, buses, clock)
    clock = clock + 1

    decode(registers, pipeline_table, buses, clock)
    search(memory, registers, pipeline_table, buses, clock)
    clock = clock + 1

    execution(registers, pipeline_table, buses, clock)
    decode(registers, pipeline_table, buses, clock)
    search(memory, registers, pipeline_table, buses, clock)
    clock = clock + 1

    memoryAccess(pipeline_table, buses, clock)
    execution(registers, pipeline_table, buses, clock)
    decode(registers, pipeline_table, buses, clock)
    search(memory, registers, pipeline_table, buses, clock)
    clock = clock + 1
    return clock


def pipeline(memory: Memory, registers: Registers, pipe_table: PipelineTable, bus, clock):
    write(registers, pipe_table, bus, clock)
    memoryAccess(pipe_table, bus, clock)
    execution(registers, pipe_table, bus, clock)
    decode(registers, pipe_table, bus, clock)
    search(memory, registers, pipe_table, bus, clock)


# --------------------------------------------------
# FUNÇOES DE FILE ---------------------------------

def read_file(file_path):
    file_in = open(file_path, "r")
    memory: Memory = append_lines_to_memory(file_in)
    file_in.close()
    return memory


def append_lines_to_memory(opened_file):
    memory: Memory = Memory()

    for line in opened_file:
        opcode = "0b" + line[0:4]
        rd = "0b" + line[5:9]
        r1 = "0b" + line[10:14]
        r2 = "0b" + line[15:19]
        memory.saveInMemory([opcode, rd, r1, r2])

    return memory

# --------------------------------------------------

if __name__ == '__main__':
    file = sys.argv[1]
    memory = read_file(file)
    processor_simulation(memory)

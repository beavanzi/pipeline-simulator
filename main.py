from atexit import register
import string
import sys
from tabulate import tabulate
from copy import deepcopy
from typing import List
import random

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
        self.instructionsStatuses = [[""]*5]

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
       if clock == len( self.instructionsStatuses)-1:
           self.instructionsStatuses[clock][newLineCriterion]=inst
       else:
           newLine=[""]*5
           newLine[newLineCriterion]=inst
           self.instructionsStatuses.append(newLine)
           


    
    def printTable(self):
        table = tabulate(self.instructionsStatuses, headers=[
                         'Clock', "Busca", "Decodificacao", "Execucao", "Acesso a Memoria", "Escrita"], tablefmt='orgtbl')
        print(table)


class ALU:
    def __init__(self,op1,op2):
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
        # self.instructions_status = []
        self.MBR = []     # armazena uma palavra de dados
        self.MAR = None     # armazena um end de memoria
        self.PC = 0       # armazena o end da inst a ser executada
        self.IR = None      # contem a ultima instruçao decodificada
        self.registradores=[random.randint(0,10) for _ in range(16)]

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



#Barramentos dos estágios

class Bus():
    def __init__(self) -> None:
        self.ID=None
        self.inst=None
        self.result=None
        self.op1=None
        self.op2=None
        self.resultValue=None
        pass
    
    def getInstruct(self):
        return self.inst
    
    def setInstruct(self,inst):
        self.inst=inst
        
    def getID(self):
        return self.ID
    
    def setID(self,ID):
        self.ID=ID
        
    def getResult(self):
        return self.result
    
    def setResult(self,result):
        self.result=result  
        
    def getResultValue(self):
        return self.resultValue
    
    def setResultValue(self,result):
        self.resultValue=result  
        
    def getOP1(self):
        return self.op1
    
    def setOP1(self,op1):
        self.op1=op1  
    
    def getOP2(self):
        return self.result
    
    def setOP2(self,op2):
        self.op2=op2  
    
    def reset(self):
        self.ID=None
        self.inst=None
        self.result=None
        self.op1=None
        self.op2=None
        self.resultValue=None
        pass
    def isVazio(self):
        return self.inst==None
        
        
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


def empty_pipeline(barramentos):
    for i in range(len(barramentos)):
        if not barramentos[i].isVazio():
            return False
    return True

def has_memory_to_read(memory, registers):
    return memory.getMemorySize() > registers.PC


# ----------------------------------------------------------------------
# FUNCOES DO PROCESSADOR -----------------------------------------------

def search(memory: Memory, registers: Registers, table: PipelineTable,barramento:List[Bus],clock):
    if has_memory_to_read(memory, registers):
        if barramento[0].isVazio():
            registers.setMAR(registers.PC)
            registers.setMBR(memory.getByAddress(registers.MAR))
            memory_information: list = deepcopy(registers.MBR)
            inst = Instruction(registers.PC, memory_information[0], memory_information[1], memory_information[2],
                                memory_information[3])
            barramento[0].setID( "Inst "+str(registers.PC))
            barramento[0].setInstruct(inst.opcode)
            barramento[0].setResult(inst.dest)
            barramento[0].setOP1(inst.r1)
            barramento[0].setOP2(inst.r2)
            registers.incrementPc()
            table.setInstructionSearched(clock, barramento[0].getID())
    barramento[4].reset()
            

def isStall(barramento:List[Bus]):
    for i in range(2,len(barramento)):
        if barramento[0].getOP1()!="" and barramento[0].getOP2()!="":
            if not barramento[i].isVazio():
                result=bin(barramento[i].getResult())
                
                if (barramento[0].getOP1()==result or barramento[0].getOP2()==result):
                    return True
    return False

def decode(registers: Registers, table: PipelineTable,barramento:List[Bus],clock):
    if not isStall(barramento) and not barramento[0].isVazio():
        barramento[1].setID(barramento[0].getID())
        barramento[1].setInstruct(int(barramento[0].getInstruct(),2))
        barramento[1].setResult(int(barramento[0].getResult(),2))
        barramento[1].setOP1(int(barramento[0].getOP1(),2))
        barramento[1].setOP2(int(barramento[0].getOP2(),2))
        inst = Instruction( int(barramento[1].getID().split(" ")[1]), barramento[1].getInstruct(), barramento[1].getResult(), barramento[1].getOP1(),
                               barramento[1].getOP2())
        registers.setIR(inst)
        
        
    if isStall(barramento):
        table.setInstructionDecoded(clock, "----STALL----")
    elif barramento[0].isVazio():
        table.setInstructionDecoded(clock, " ")
    else:
        table.setInstructionDecoded(clock, barramento[1].getID())
        barramento[0].reset()


def execution(registers: Registers, pipeTable: PipelineTable,barramento:List[Bus],clock):
    if not barramento[1].isVazio():
        IR=registers.IR
        ULA=ALU(IR.getR1(),IR.getR2())
        if IR.getOpcode()==0:
            result = ULA.add()
        elif IR.getOpcode()==1:
            result = ULA.sub()
        elif IR.getOpcode()==2:
            result = ULA.mul()
        elif IR.getOpcode()==3:
            result = ULA.div()
        barramento[2].setID(barramento[1].getID())
        barramento[2].setInstruct(barramento[1].getInstruct())
        barramento[2].setResult(barramento[1].getResult())
        barramento[2].setOP1(barramento[1].getOP1())
        barramento[2].setOP2(barramento[1].getOP2())
        barramento[2].setResultValue(result)
        pipeTable.setInstructionExecuted(clock, barramento[2].getID())
        barramento[1].reset()
    else:
        if not barramento[0].isVazio() :
            if "STALL"in pipeTable.instructionsStatuses[clock-1][1]:
                pipeTable.setInstructionExecuted(clock, "----STALL----")
        else:
            pipeTable.setInstructionExecuted(clock, " ")



def memoryAccess(registers: Registers, pipeTable: PipelineTable,barramento:List[Bus],clock):
    if not barramento[2].isVazio():
        barramento[3].setID(barramento[2].getID())
        barramento[3].setInstruct(barramento[2].getInstruct())
        barramento[3].setResult(barramento[2].getResult())
        barramento[3].setOP1(barramento[2].getOP1())
        barramento[3].setOP2(barramento[2].getOP2())
        barramento[3].setResultValue(barramento[2].getResultValue())
        pipeTable.setInstructionAccessedMemory(clock, barramento[3].getID())
        barramento[2].reset()
    else:
        if not barramento[0].isVazio() and pipeTable.instructionsStatuses[clock-1][1]=="----STALL----": 
            pipeTable.setInstructionAccessedMemory(clock, "----STALL----")
        else:
            pipeTable.setInstructionAccessedMemory(clock, " ")


def write(registers: Registers, pipeTable: PipelineTable,barramento:List[Bus],clock):
    
    if not barramento[3].isVazio():
        registers.registradores[barramento[3].getResult()]=barramento[3].getResultValue()
        barramento[4].setID(barramento[3].getID())
        barramento[4].setInstruct(barramento[3].getInstruct())
        barramento[4].setResult(barramento[3].getResult())
        barramento[4].setOP1(barramento[3].getOP1())
        barramento[4].setOP2(barramento[3].getOP2())
        barramento[4].setResultValue(barramento[2].getResultValue())
        pipeTable.setInstructionWrote(clock, barramento[4].getID())
        barramento[3].reset()
    else:
            pipeTable.setInstructionWrote(clock, " ")


def processor_simulation(memory: Memory):
    registers: Registers = Registers()
    pipeline_table: PipelineTable = PipelineTable()
    barramentos = []
    for _ in range(5):
        barramentos.append(Bus())
        
    clock = 0
    search(memory, registers, pipeline_table,barramentos,clock)
    clock = clock + 1
    decode(registers, pipeline_table,barramentos,clock)
    search(memory, registers, pipeline_table,barramentos,clock)
    clock = clock + 1
    execution(registers, pipeline_table,barramentos,clock)
    decode(registers, pipeline_table,barramentos,clock)
    search(memory, registers, pipeline_table,barramentos,clock)
    clock = clock + 1
    memoryAccess(registers, pipeline_table,barramentos,clock)
    execution(registers, pipeline_table,barramentos,clock)
    decode(registers, pipeline_table,barramentos,clock)
    search(memory, registers, pipeline_table,barramentos,clock)
    clock = clock + 1

    while not (empty_pipeline(barramentos)):
        pipeline(memory, registers, pipeline_table,barramentos,clock)
        # write_log(scoreboarding, functional_units, clock)
        pipeline_table.printTable()
        print(registers.registradores)
        clock = clock + 1


def pipeline(memory: Memory, registers: Registers, pipe_table: PipelineTable,barramento,clock):
    write(registers, pipe_table,barramento,clock)
    memoryAccess(registers, pipe_table,barramento,clock)
    execution(registers, pipe_table,barramento,clock)
    decode(registers, pipe_table,barramento,clock)
    search(memory, registers, pipe_table,barramento,clock)


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
        opcode = "0b"+line[0:4]
        rd = "0b"+line[5:9]
        r1 = "0b"+line[10:14]
        r2 = "0b"+line[15:19]
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

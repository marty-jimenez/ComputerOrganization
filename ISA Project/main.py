# MEDP Simulator    #
# Project 3         #
# Group 6, ECE 366  #

import math

# All my registers (0-18) #
# Initialized to equal 0  #
Registers = [0] * 18
# 16 = sum                #
# 17 = tempReg            #

# All of our instructions          #
# Used to write into writefile.txt #
Instructions = [] 

# Memory[]   #
Mem = {}                    # Dictionary
memAddr = range(0, 1024, 1) # 16-bit memory addresses
for i in memAddr:
  # Initialzing every Memory Address to 0
  Mem[i] = 0 

# All the supported functions # 
# Used for printing what instructions happen in writefile.txt #
func = {}               
func["00"] = "j"    
func["0100"] = "bgeqz"
func["0101"] = "incr"
func["0110"] = "ld" 
func["0111"] = "st"
func["1000"] = "mult"
func["1001"] = "div2"
func["1010"] = "stsum"
func["1011"] = "sub"
func["1100"] = "add"    
func["1101"] = "stb"
func["1110"] = "appb"
func["1111"] = "initb"

# ******************************************* #

# twos_comp: 
# Returns the twos comp of a given value
def twos_comp(val, bits):

  if (val & (1 << (bits - 1))) != 0: 
    val = val - (1 << bits) 
  return val 

# formatChecker:
# Checks if given binary instr is good
def formatChecker(instr):
  checker = False

  if any(n > '1' or n < '0' for n in instr): # if not 0 or 1
    print("Binary only uses 1's and 0's")
  elif len(instr) != 8: # if too long or short
    print("Only 8-bit instructions are supported")
  else: 
    checker = True
  
  return checker

# PC:
# counts the number of written instructions in 
# the .asm file provided
def PC(dataFile):
  PC = 0
  for instr in dataFile:
    PC = PC + 1 
  return PC

# simulator: 
# actually simulates the assembly code
def simulator(dataFile, functions):
  # acts like a for loop in C++/C/Java 
  # did this so we can easily go backwards and forwards 
  # where i sort of acts like pc
  i = 0
  instructionCount = 0
  while i < len(dataFile):

    # For debug purposes #
    # print("i " + str(i) + ", r10: " + str(Registers[10]))
    #if (instructionCount == 3779):
      # break

    # Getting the instruction
    instr = dataFile[i]
    instr = instr.replace(" ", "") # Gets rid of spaces
    instr = instr.replace("\n", "") # Gets rid of newlines
    
    # If the format isn't right for at least one instruction
    if (formatChecker(instr) == False):
      print("\nAborting...")
      exit()
    
    # Incrementing now 
    # If we don't then our jump breaks
    i = i + 1
    
    # Instruction counter, does not equal i because 
    # i changes with each jump and branch
    instructionCount = instructionCount + 1

    # j imm
    # works more like branch
    if(instr[0:2] == "00"):
      # 00 iiiiii
      # imm = [-64, 63], done by multiplying the twos_comp by 2
      # PC = imm + PC
      imm = instr[2:8]
      newImm = twos_comp(int(instr[2:8], 2), 6)
      newImm = newImm * 2
      
      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:2]] + " " + str(newImm))

      i = i + (newImm) - 1 # jumping
    
    # bgeqz Rx
    if(instr[0:4] == "0100"):
      # 0100 xxxx
      # if (Rx >= 0) PC = PC + 2
      # else PC++
      
      Rx = int(instr[4:8], 2)

      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx))
      
      if (int(Registers[Rx]) >= 0):
        i = i + 1 # Only 1 because we already incremented i by 1 in the very beginning of this loop
    
    # incr Rx, imm
    if(instr[0:4] == "0101"):
      # 0101 xxx i
      # Rx = Rx + i
      # i = -1 or 1

      Rx = int(instr[4:7], 2)
      imm = int(instr[7:8], 2)
      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx) + ", " + str(imm))

      if (imm == 0):
        Registers[Rx] = Registers[Rx] - 1
      if (imm == 1):
        Registers[Rx] = Registers[Rx] + 1
    
    # ld Rx, (Ry)
    if(instr[0:4] == "0110"):
      # 0110 xx, yy
      # xx = [6, 9]
      # yy = [0, 3]
      Rx = int(instr[4:6], 2) + 6
      Ry = int(instr[6:8], 2)
      
      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx) + ", ($" + str(Ry) + ")")

      Registers[Rx] = Mem[Registers[Ry]]
    
    # st Rx, (Ry)
    if(instr[0:4] == "0111"):
      # Mem[Ry] = Rx
      # 0111 xx, yy
      # xx = [6, 9]
      # yy = [0, 3]
      Rx = int(instr[4:6], 2) + 6
      Ry = int(instr[6:8], 2)
      
      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx) + ", ($" + str(Ry) + ") Addr:" + str(Registers[Ry]) + " = " +  str(Registers[Rx]))

      Mem[Registers[Ry]] = Registers[Rx]
    
    # mult Rx, Ry
    if(instr[0:4] == "1000"):
      # 1000 xx yy
      # xx, yy = [4-7]
      Rx = int(instr[4:6], 2) + 4
      Ry = int(instr[6:8], 2) + 4

      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx) + ", $" + str(Ry))

      Registers[Rx] = Registers[Rx] * Registers[Ry]
    
    # div2 Rx
    if(instr[0:4] == "1001"):
      # Rx = Rx / 2
      # R15 = Remainder
      # 1001 xxxx
      Rx = int(instr[4:8], 2)

      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx))
      
      R15 = Registers[Rx] % 2
      R15 = R15 * -1
      Registers[15] = R15

      Registers[Rx] = math.floor(Registers[Rx] / 2)
    
    # stsum Rx
    if(instr[0:4] == "1010"):
      # Rx = sum
      # 1010 xxxx
      Rx = int(instr[4:8], 2)

      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx))

      Registers[Rx] = Registers[16]
      # Reset sum
      Registers[16] = 0

    # sub Rx
    if(instr[0:4] == "1011"):
      # 1011 xxxx
      # sum = sum - Rx
      Rx = int(instr[4:8], 2) 

      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx))

      Registers[16] = Registers[16] - Registers[Rx]

    # add Rx
    if(instr[0:4] == "1100"):
      # 1100 xxxx
      # sum = sum + Rx
      Rx = int(instr[4:8], 2) 

      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx))

      Registers[16] = Registers[16] + Registers[Rx]

    # stb Rx
    if(instr[0:4] == "1101"):
      # Rx = tempReg
      # 1101 xxxx
      Rx = int(instr[4:8], 2)

      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " $" + str(Rx))

      # THIS ALWAYS TAKES THE twos_comp
      # EVEN IF tempReg is 4, 8, 16 BITS
      Registers[Rx] = twos_comp(int(Registers[17], 2), len(Registers[17]))
      # print(Registers[Rx])
    
    # appb bbbb
    if(instr[0:4] == "1110"):
      # tempReg = [tempReg][bbbb]
      # 1110 bbbb

      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " " + instr[4:8])

      Registers[17] = str(Registers[17]) + instr[4:8]
      # print(Registers[17])
   
    # initb bbbb
    if(instr[0:4] == "1111"):
      # tempReg = bbbb
      # 1111 bbbb

      # So we can print what instructions happen #
      Instructions.append(functions[instr[0:4]] + " " + instr[4:8])

      Registers[17] = instr[4:8]
      # print(Registers[17])

  return instructionCount



def main():
  print("Welcome to MEDP Simulator!\n\n")
  dataFile = str(input("Enter the filename with the MEDP instructions: "))
  printInstr = str(input("\nTranslate instructions into writefile.txt (y/n)? "))
  print("\n\tMEDP Simulator\n\n")
  try:
    with open(dataFile) as myFile:

      # Open file to write in
      w = open('writefile.txt', 'w+')
      dataFile = myFile.readlines()   # Read my file

      # Call the simulator
      # instructionCount is the amount of instructions done
      instructionCount = simulator(dataFile, func)

      # Basically a count of the instructions written in the file
      pc = PC(dataFile)

      # Prints our registers
      print("Registers: \n")
      count = 0
      for reg in Registers:
        # our special registers
        if (count == 16):
          register = "sum:"
        elif (count == 17):
          register = "tempReg:"
        else:
          # regular registers 
          register = "$" + str(count) + ":"

        # Formats so they print nicely
        print("{:<8} {:<5}".format(register, str(Registers[count])))
        count = count + 1

      print("PC: " + str(pc))

      # printing the amount of instructions done
      print("\nInstruction Count: " + str(instructionCount) + "\n")

      # Writes instructions into a file
      if(printInstr.lower() == 'y'):
        w.write("Instructions:\n\n")
        for instr in Instructions:
          w.write(str(instr) + "\n")         # Write instructions in the file
        w.write("--------------------\n")

      w.write("Memory Content:\n\n")

      # Writes memory into a file 
      # Full-screened txt file looks the best #
      printCounter = 0
      for addr, content in Mem.items():
        printCounter = printCounter + 1
        addr = str(addr) + ":"
        # Formats so it prints nicely while fullscreened
        writeMe = "{:<8} {:<5}".format(str((addr)), str(content))

        # Just limits the amount of addresses per line to 8, which looks the best when you give the writefile.txt all the space you can on repl.it
        if (printCounter == 8):
          w.write(writeMe)
          w.write("\n")
          printCounter = 0
        else: 
          w.write(writeMe)

      w.close()                       # Close the file
  except IOError:
    # This happens if the filename is wrong
    print("Uh oh, this file either does not exist or we can not reach it...\n\nAborting...")
    exit()

if __name__ == "__main__":
  main()

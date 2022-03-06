####################   imports   ##################

import sys
import re

###############   global variables  ###########

global last_register     #variable holding last used register
global a                 #register A
global b                 #regisrer B
global vars              #array with variables
global index_name        #dictionary returning name of variable of given index
global name_index        #dictionary returning index in vars of given variable's name
global vars_count        #number of variables in vars

vars = []                #initialisation of global variables
index_name = {}
name_index = {}
vars_count = 0
last_register = None
a = None
b = None

##############   classes   #############

class pointer:                           #pointer class used to access and iterate over arrays
    def __init__(self, address, offset):
        if not address in name_index:
            abort("unknown address: " + address)
        self.address = address
        self.offset = offset

##############   functions' declarations   #############

def abort(message):     
    print("!!!!=======ERROR=======!!!!")
    print(message)
    print("execution aborted, no further instructions were performed")
    print("!!!!=======ERROR=======!!!!")
    sys.exit(1)

def abort_compilation(message,line):
    print("!!!!=======ERROR=======!!!!")
    print("execution aborted at line:\n" + line)
    print(message)
    print("current state of variables")
    print_vars()
    print("execution aborted, no further instructions were performed")
    print("!!!!=======ERROR=======!!!!")
    sys.exit(1)

def uncomment(string):                  #gets rid of a comment in line
    if ";" in string:
        return string[:string.find(";")]
    else:
        return string

def print_vars():                       #prints variables
    for x in range(len(vars)):
        if (type(vars[x]) is pointer):
            print(index_name[x] + ": " + vars[x].address + ((" + " + str(vars[x].offset)) if vars[x].offset else ""))
        else:
            print(index_name[x] + ": " + str(vars[x]))

def segment_declaration(line):          #checks if line contains segment declaration. 
                                        #Returns True if segment is present and False otherwise
                                        #doesn't include .END !
    segments = [".UNIT",".DATA",".CODE"]
    for x in segments:
        if x in line:
            return True
    return False

def get_segment(line):                  #returns string with segment name extracted from line
                                        #doesn't include .END!
    index = line.find(".")
    return line[index:index+5]

def load(register,value):               #loads value to given register
    global a
    global b
    global last_register
    if (register=="@A" or register=="@a"):
        a=value
        last_register = a
    elif (register=="@B" or register=="@b"):
        b=value
        last_register = b
    else:
        abort("invalid register provided: " + register)

def check_ptrs(a,b):                #checks if a or b is pointer
    if (type(a) is pointer or type(b) is pointer):
        return True
    return False

def check_both_ptrs(a,b):           #checks if a and b are pointers
    if (type(a) is pointer and type(b) is pointer):
        return True
    return False

def add_values(register,value):     #returns new offset which is sum of register and value
    if (type(a) is pointer and type(b) is pointer):
        abort("cannot perform operation on two pointers")
    if (type(value) is pointer and not type(register) is pointer):
        return value.offset + register
    if (not type(value) is pointer and type(register) is pointer):
        return register.offset + value

def add(register,value):        #adds value to register
    global a
    global b
    global last_register
    if (register=="@A" or register=="@a"):      #register A
        if (a==None):                           #check if A is not empty
            abort("Nothing was loaded to @A. Cannot perform addition")
        if (check_ptrs(a,value)):               #check if operation is performed on pointers
            if (type(a) is pointer):
                a.offset = add_values(a,value)
            else:
                value.offset = add_values(a,value)
                a = value
        else:                                   #default case
            a+=value
        last_register = a
    elif (register=="@B" or register=="@b"):    #register B (same as A)
        if (b==None):
            abort("Nothing was loaded to @B. Cannot perform addition")
        if (check_ptrs(b,value)):
            if (type(b) is tuple):
                b.offset = add_values(b,value)
            else:
                value.offset = add_values(b,value)
                b = value
        else:
            b+=value
        last_register = b
    else:
        abort("invalid register provided: " + register)

def sub(register,value):        #subtracts value from register
    global a
    global b
    global last_register
    if (register=="@A" or register=="@a"):      #register A
        if (a==None):                           #check if register is empty
            abort("Nothing was loaded to @A. Cannot perform sub")
        if (check_ptrs(a,value)):               #pointers case
            if (check_both_ptrs(a,value)):
                a = a.offset - value.offset
            else:
                a.offset = a.offset - value
            return
        a-=value                                #int case
        last_register = a
    elif (register=="@B" or register=="@b"):    #register B (same as A)
        if (b==None):
            abort("Nothing was loaded to @B. Cannot perform sub")
        if (check_ptrs(b,value)):
            if (check_both_ptrs(b,value)):
                b = b.offset - value.offset
            else:
                b.offset = b.offset - value
            return
        b-=value
        last_register = b
    else:
        abort("invalid register provided: " + register)

def mult(register,value):               #multiplies register by value
    global a
    global b
    global last_register 
    if (register=="@A" or register=="@a"):      #register A
        if check_ptrs(a,value):                 #make sure there are no ptrs
            abort("cannot perform multiplication on pointers!")
        if (a==None):                           #check if register is empty
            abort("Nothing was loaded to @A. Cannot perform mult")

        a*=value                                #perform multiplication
        last_register = a
    elif (register=="@B" or register=="@b"):    #register B (same as A)
        if check_ptrs(b,value):
            abort("cannot perform multiplication on pointers!")
        if (b==None):
            abort("Nothing was loaded to @B. Cannot perform mult")

        b*=value
        last_register = b
    else:
        abort("invalid register provided: " + register)

def div(register,value):                        #divides register by value
    global a
    global b
    global last_register
    if (value==0):                              #check if value != 0
        abort("cannot perform division by 0")
    
    if (register=="@A" or register=="@a"):      #register A
        if check_ptrs(a,value):                 #make sure there are no pointers 
            abort("cannot perform division on pointers!")

        if (a==None):                           #make sure A is not empty
            abort("Nothing was loaded to @A. Cannot perform div")
        a/=value                                #perform division
        last_register = a
    elif (register=="@B" or register=="@b"):    #register B (same as A)
        if check_ptrs(b,value):
            abort("cannot perform division on pointers!")
        if (b==None):
            abort("Nothing was loaded to @B. Cannot perform div")
        b/=value
        last_register = b
    else:
        abort("invalid register provided: " + register)
    
def store(register,address):        #saves value from given register to address
    global a
    global b    
    global last_register
    global vars
    if (register=="@A" or register=="@a"):  #register A
        if (a==None):                       #check if A is empty
            abort("Nothing was loaded to @A. Cannot perform store")
        if (type(a) is list):               #case 1: save pointer to array
            if not address in name_index:
                abort("Unknown variable: " + address)

            vars[name_index[address]] = pointer(index_name[vars.index(a)],0)
            last_register = a
            return
        if ("(" in address):                #case 2: save integer in array
            if not address[1:-1] in name_index:
                abort("Unknown variable: " + address)
            ptr = vars[name_index[address[1:-1]]]
            vars[name_index[ptr.address]][ptr.offset] = a
            last_register = a
            return

        if not address in name_index:       #case 3: save integer in normal address
            abort("Unknown variable: " + address)
        vars[name_index[address]] = a
        last_register = a
    elif (register=="@B" or register=="@b"):    #register B (same as A)
        if (b==None):
            abort("Nothing was loaded to @B. Cannot perform store")
        if (type(b) is list):
            if not address in name_index:
                abort("Unknown variable: " + address)
            vars[name_index[address]] = pointer(index_name[vars.index(b)],0)
            last_register = b
            return
        if ("(" in address):
            if not address[1:-1] in name_index:
                abort("Unknown variable: " + address)
            ptr = vars[name_index[address[1:-1]]]
            vars[name_index[ptr.address]][ptr.offset] = b
            last_register = b
            return

        if not address in name_index:
            abort("Unknown variable: " + address)
        vars[name_index[address]] = b
        last_register = b
    else:
        abort("invalid register provided: " + register)

def get_value(string):                  #extracts value from instruction
    if re.match("[-+]?\d+$",string):    #case 1: a number
        return int(string)
    if string.count(")")==2:            #case 2: element from array
        res = string.replace(")", "")
        res = res.replace("(","")

        if not res in name_index:
            abort("Unknown variable " + string)

        return vars[name_index[vars[name_index[res]].address]][vars[name_index[res]].offset]
    if string.count(")")==1:            #case 3: normal variable
        if not (string[string.find("(")+1:string.find(")")]) in name_index:
            abort("Unknown variable " + string)

        return vars[name_index[(string[string.find("(")+1:string.find(")")])]]

    if not string in name_index:        #case 4: array (pointer to array)
        abort("Unknown variable " + string)

    return vars[name_index[string]]

def unhash(string):                     #converts # to normal input (used in array initialisaion)
    res = ""
    input = string.split(",")

    for cell in input:
        if '#' in cell:
            value = cell[cell.find("#")+1:]
            repeat = int(cell[:cell.find("#")])

            for iterator in range(repeat):
                res+=value
                if (iterator+1!=repeat):
                    res+=","

        else:
            res+=cell

        res+=','
    
    res =res[:-1]
    return res

def initialise_array(string,name):          #initialises array
    global vars_count
    global index_name
    global name_index
    global vars
    array = []
    for num in string.split(","):
        array.append(int(num))

    vars.append(array)
    index_name[vars_count]=name
    name_index[name]=vars_count
    vars_count+=1

##############   main   #############

def main():
    global vars_count
    global index_name
    global name_index
    global vars

    file = open("main.txt", "r")            #open file
    raw_input = file.readlines()

    lab_dict = {}                           #dictionary with number of lines corresponding to each goto label
    input = []                              #lines from .CODE segments
    segment = None                          #current segment

    line_count = 0                          #number of lines of .CODE segments

    for line in raw_input:

        current_line = line         #create copy

        current_line = uncomment(current_line)      #get rid of unwanted characters
        current_line = current_line.replace(" ","")
        current_line = current_line.replace("\t","")
        current_line = current_line.replace("\n","")
        
        if (segment_declaration(current_line)):     #check if line contains new segment
            segment = get_segment(current_line)
            continue
        
        if (segment == ".DATA"):                    #DATA segment case
            if (current_line.count(",")==1):        #creating new variable
                index = current_line.find(":")      
                
                if (not re.match("^[a-zA-Z_]\\w*$",current_line[:index])):      #check if variable name is correct
                    abort_compilation("invalid variable name: "+ current_line[:index], current_line)

                if(re.match("[-+]?\d+$",current_line.split(",")[1])):    #case 1: simple number

                    index_name[vars_count]=current_line[:index]          #index -> name
                    name_index[current_line[:index]]=vars_count          #name -> index
                    vars.append(int(current_line.split(",")[1]))
                    vars_count+=1
            
                else:                                                    #case 2: pointer
                    vars.append(pointer(current_line.split(",")[1],0))
                    index_name[vars_count]=current_line[:index]          #index -> name
                    name_index[current_line[:index]]=vars_count          #name -> index
                    vars_count+=1

            if (current_line.count(",")>1):     #creating new array
                initialise_array(unhash(current_line[current_line.find(".WORD")+6:]),current_line[:current_line.find(":")])

        if (segment == ".CODE"):                                         #CODE segment
            
            if ((":" in current_line) and (not ".WORD" in current_line)):   #create dictionary with labels
                label = current_line.split(":")[0]
                lab_dict[label] = line_count
                current_line = current_line.replace(label + ":","")
        
            line_count+=1
            input.append(current_line)                                      #prepare code to be executes


    raw_input.clear()   #clean up
    file.close()        

    print("exec start: ")   #print initial state of variables
    print_vars()

    x = 0                   #variable with information which line are we in
    while(True):            #exec start
        line = input[x]     #load line
        
        x += 1              #prepare move to next line

        #print(repr(line))

        if (len(line)==0):  #check if line is empty
            continue


        split = line.split(",") 
            
        if split[0]=="null":            #instructions
            continue

        elif split[0]=="load":
            load(split[1],get_value(split[2]))

        elif split[0]=="add":
            add(split[1],get_value(split[2]))

        elif split[0]=="sub":
            sub(split[1],get_value(split[2]))

        elif split[0]=="div":
            div(split[1],get_value(split[2]))

        elif split[0]=="mult":
            mult(split[1],get_value(split[2]))

        elif split[0]=="store":
            store(split[1],split[2])
            #print_vars()

        elif split[0]=="jump":
            if not split[1] in lab_dict:
                abort_compilation("label: " + split[1] + "not found in code", line)
            x=lab_dict[split[1]]

        elif split[0]=="jzero":
            if not split[1] in lab_dict:
                abort_compilation("label: " + split[1] + "not found in code", line)
            if last_register==0:
                x=lab_dict[split[1]]
            else:
                continue

        elif split[0]=="jnzero":
            if not split[1] in lab_dict:
                abort_compilation("label: " + split[1] + "not found in code", line)        
            if last_register!=0:
                x=lab_dict[split[1]]
            else:
                continue

        elif split[0]=="jpos":
            if not split[1] in lab_dict:
                abort_compilation("label: " + split[1] + "not found in code", line)
            if last_register>0:
                x=lab_dict[split[1]]
            else:
                continue

        elif split[0]=="jneg":
            if not split[1] in lab_dict:
                abort_compilation("label: " + split[1] + " not found in code", line)
            if last_register<0:
                x=lab_dict[split[1]]
            else:
                continue

        elif split[0]=="halt":
            break

        else:
            abort_compilation("Inavlid instruction: " + split[0],line)

        if (".END" in line):
            break

    print("final state:")  #print final state of variables
    print_vars()
    print("press enter to quit")
    sys.stdin.read(1)               #enter to close

if __name__=='__main__':
    main()
"""Convert regular expression to NFA."""
import json
import graphviz
import pydot
def validate_reg(reg):
    #check if the input regular expression is valid
    if reg=="":
        return False
    if reg[0]=="*" or reg[0]=="+" or reg[0]=="?"  :
        #example "*abc" is invalid
        return False
    # if reg[-1]=="|":
    #     #example "a|b|c|"" is invalid
    #     return False
    for i in range(0,len(reg)-1):
        if reg[i]=="*":##error reg[i]=="+" when 3  w kaman reg[i]=="?
            if reg[i+1]==reg[i]:
                #example "a|b**c" is invalid
                return False
        if i<len(reg)-2 and ((reg[i]=="+" and reg[i+1]=="+" and reg[i+2]=="+")or(reg[i]=="?" and reg[i+1]=="?" and reg[i+2]=="?")):
            #example "a+++" or "a???" is invalid
            return False
        if reg[i]=="+" and reg[i+1]=="*" :
            #example "a+*" is invalid
            return False
        if reg[i]=="?" and reg[i+1]=="*" :
            #example "a?*" is invalid
            return False
        if reg[i]=="|" :
            if reg[i+1]=="*" or reg[i]=="?" or reg[i+1]=="+" or reg[i+1]==")" or reg[i+1]=="]":
                #example "a|b|+c" or "a|b|+*" is invalid
                return False
        
        if reg[i]=="-":#TODO checkkkkk if all alphanumeric
            if i>0 and reg[i+1].isalnum() and reg[i-1].isalnum():
                continue
            return False
        if reg[i]=="[":
            if reg[i+1]=="]" or reg[i+1]=="|":#[] invalid
                return False
    return True
def validate_brackets(reg):
    stack=[]
    for char in reg:
        if char=="(":
            stack.append(char)
        elif char==")":
            #stack[-1] is the last element in the stack
            while stack and stack[-1]!="(":
                stack.pop()
            if stack:
                stack.pop()
            else:
                return "unbalanced parentheses"
        elif char=="[":
            stack.append(char)
        elif char=="]":
            #stack[-1] is the last element in the stack
            while stack and stack[-1]!="[":
                stack.pop()
            if stack:
                stack.pop()
            else:
                return "unbalanced parentheses"
    if stack:
        return "unbalanced parentheses"
        
    return "balanced parentheses"
#start with adding special character to represent Anding
def regex_anding(reg):
    correct_reg=[]
    range_str=""
    is_range=False
    last_is_put=False
    first_is_operator_and_already_put=False
    # take care this loop is from 0 to len(reg)-2 so concentarte to know how we handle the last character 
    for i in range(0,len(reg)-1):
        if is_range:
            if reg[i]=="]":
                is_range=False
                correct_reg.append(range_str)
                range_str=""
            else:
                range_str+=reg[i]
                continue
        if reg[i]=="|" or reg[i+1]=="|":
            if not first_is_operator_and_already_put:
                correct_reg.append(reg[i])
            else:
                first_is_operator_and_already_put=False
            continue
        elif reg[i+1]=="?" or reg[i+1]=="*" or reg[i+1]=="+":
            if not first_is_operator_and_already_put:
                correct_reg.append(reg[i])
            else:
                first_is_operator_and_already_put=False
            correct_reg.append(reg[i+1])
            # this is the only case where we put TWO chars together
            # so, if we reached the end of the regular expression,
            # we dont want to put the last character (which is always an operator as we are in this elif) again
            # as it will be put in the last if condition
            # so we set last_is_put to True to avoid putting it again
            if i==len(reg)-2:
                last_is_put=True
                break
            #TODO check if the next character is an operator if yes dont put anding
            if i<len(reg)-2 and (reg[i+2]=="*" or reg[i+2]=="+" or reg[i+2]=="?" or reg[i+2]=="|"):#example "a*?" we dont want to put anding
                first_is_operator_and_already_put=True #if we have multiple operators together we dont want to put them twice each
                continue
            correct_reg.append("×")    
            continue
        # elif reg[i]=="]":
        #     if reg[i+1].isalnum() or reg[i+1]=="[" or reg[i+1]=="(":
        #         #we will not put the "]" in the correct_reg as it is already put as a string (range_str) in the correct_reg
        #         correct_reg.append("×")
        #         continue
        elif reg[i].isalnum() or reg[i]=="]" or reg[i]==")":
            if reg[i+1].isalnum() or reg[i+1]=="[" or reg[i+1]=="(":
                correct_reg.append(reg[i])
                correct_reg.append("×")
                continue
        elif reg[i]=="[" :
            correct_reg.append(reg[i])
            range_str=""
            is_range=True
            continue
        if reg[i]=="?" or reg[i]=="*" or reg[i]=="+":
            continue        
        else:
            correct_reg.append(reg[i])
    # put the last character in the regular expression
    # only if last_is_put is False
    if i==len(reg)-2 and not last_is_put:
        if is_range:#this means that the regex was ending with the "]" example 1[a-z] this means that we didnot put the range_str in the correct_reg
                    #as is_range is still True
            correct_reg.append(range_str)
        correct_reg.append(reg[i+1])
    return correct_reg #the result could be ['[', 'a-z_', ']', '[', 'a-z0-9_', ']', '*'] then we want to concat the range in one string (function concat_range)

def concat_range(correct_reg):
    reg=[]
    range_str=""
    is_range=False
    for i in range(0,len(correct_reg)):
        if correct_reg[i]=="]":
            continue
        if is_range:
            range_str="["+correct_reg[i]+"]"
            # check that something like [a-c-f] does not exist 
            # so check that the distance between the two "-" is 2 at least. so [a-ce-k] is valid
            indices_of_a = [p for p, char in enumerate(correct_reg[i]) if char == "-"]
            for j in range(0,len(indices_of_a)-1):
                if indices_of_a[j+1]-indices_of_a[j]<3:
                    return ["%"]#just to mark that the regular expression is invalid
            if correct_reg[i+1]!="]":
                return ["%"]#just to mark that the regular expression is invalid
            reg.append(range_str)
            is_range=False
        elif correct_reg[i]=="[" :
            is_range=True
        else:
            reg.append(correct_reg[i])
    return reg
        

def remove_extra_anding(reg):
    correct_regex=[]
    for i in range(0, len(reg)-1):
        if (reg[i]=="×" and reg[i+1]==")"):
            continue
        correct_regex.append(reg[i])
    correct_regex.append(reg[len(reg)-1])
    return correct_regex

def precedence(operator):
    if operator=="*":
        return 5
    elif operator=="+":
        return 4
    elif operator=="?":
        return 3
    elif operator=="×":
        return 2
    elif operator=="|":
        return 1
    else:
        return -1
def infix_to_postfix(infix):
    operators=["*","+","?","×","|"]
    stack=[]
    postfix=[]
    for char in infix:
        # if char.isalnum() or char=="×":
        #     postfix+=char
        if char=="(":
            stack.append(char)
        elif char==")":
            #stack[-1] is the last element in the stack
            while stack and stack[-1]!="(":
                postfix.append(stack.pop())
            if stack:
                stack.pop()
            else:
                return "unbalanced parentheses"
        elif char in operators:
            while stack and precedence(char)<=precedence(stack[-1]):
                postfix.append(stack.pop())
            stack.append(char)
        else:
            #if char is a alphanumeric character or a range string example "[a-z]"
            postfix.append(char)
    while stack:
        if stack[-1]=="(":
            return "unbalanced parentheses"
        postfix.append(stack.pop())
    return postfix


#convert the postfix to NFA

class State:
    def __init__(self,label):
        self.label=label
        self.transitions=dict()
        self.epsilon_closure=set()
class NFA:
    def __init__(self,start:State,accept:State):
        self.start=start
        self.accept=accept
def concat(nfa1:NFA,nfa2:NFA):
    #create new edge between the accept state of nfa1 and the start state of nfa2
<<<<<<< HEAD
    nfa1.accept.epsilon_closure.add(nfa2.start)
    # create new nfaf
=======
    nfa1.accept.epsilon_closure.add(nfa2.start.label)
    # create new nfa
>>>>>>> c08f1c87f6b053854d73a09a9f842fc069a574a2
    new_nfa=NFA(nfa1.start,nfa2.accept) 
    return new_nfa

def oring(nfa1:NFA,nfa2:NFA,index):
    #create new start state
    new_start_state=State(index)
    #create new accept state
    new_accept_state=State(index+1)
    #create new edge between the new start state and the start state of nfa1
    new_start_state.epsilon_closure.add(nfa1.start.label)
    #create new edge between the new start state and the start state of nfa2
    new_start_state.epsilon_closure.add(nfa2.start.label)
    #create new edge between the accept state of nfa1 and the new accept state
    nfa1.accept.epsilon_closure.add(new_accept_state.label)
    #create new edge between the accept state of nfa2 and the new accept state
    nfa2.accept.epsilon_closure.add(new_accept_state.label)
    #create new nfa
    new_nfa=NFA(new_start_state,new_accept_state)
    new_states=[new_start_state,new_accept_state]
    return new_nfa,new_states

def zero_or_more(nfa:NFA,index):
    #create new start state
    new_start_state=State(index)
    #create new accept state
    new_accept_state=State(index+1)
    #create new edge between the new start state and the start state of nfa
    new_start_state.epsilon_closure.add(nfa.start.label)
    #create new edge between the new start state and the new accept state
    new_start_state.epsilon_closure.add(new_accept_state.label)
    #create new edge between the accept state of nfa and the new accept state
    nfa.accept.epsilon_closure.add(new_accept_state.label)
    #create new edge between the accept state of nfa and the start state of nfa
    nfa.accept.epsilon_closure.add(new_start_state.label)#(nfa.start.label)
    #create new nfa
    new_nfa=NFA(new_start_state,new_accept_state)
    new_states=[new_start_state,new_accept_state]
    return new_nfa,new_states

def one_or_more(nfa:NFA,index):
    #create new start state
    new_start_state=State(index)
    #create new accept state
    new_accept_state=State(index+1)
    #create new edge between the new start state and the start state of nfa
    new_start_state.epsilon_closure.add(nfa.start.label)
    #create new edge between the accept state of nfa and the new accept state
    nfa.accept.epsilon_closure.add(new_accept_state.label)
    #create new edge between the accept state of nfa and the start state of nfa
    nfa.accept.epsilon_closure.add(new_start_state.label)#(nfa.start.label)
    #create new nfa
    new_nfa=NFA(new_start_state,new_accept_state)
    new_states=[new_start_state,new_accept_state]
    return new_nfa,new_states

def zero_or_one(nfa:NFA,index):
    #create new start state
    new_start_state=State(index)
    #create new accept state
    new_accept_state=State(index+1)
    #create new edge between the new start state and the start state of nfa
    new_start_state.epsilon_closure.add(nfa.start.label)
    #create new edge between the new start state and the new accept state
    new_start_state.epsilon_closure.add(new_accept_state.label)
    #create new edge between the accept state of nfa and the new accept state
    nfa.accept.epsilon_closure.add(new_accept_state.label)
    #create new nfa
    new_nfa=NFA(new_start_state,new_accept_state)
    new_states=[new_start_state,new_accept_state]
    return new_nfa,new_states

def create_nfa(char,index):
    #create new start state
    start_state=State(index)
    #create new accept state
    accept_state=State(index+1)
    #create new edge between the start state and the accept state
    start_state.transitions[char]=accept_state.label
    #create new nfa
    new_nfa=NFA(start_state,accept_state)
    new_states=[start_state,accept_state]
    return new_nfa,new_states


    
def postfix_to_nfa(postfix):
    nfa_stack=[]
    all_states=[]
    index=0
    for char in postfix:
        if char=="*":
            nfa,new_states=zero_or_more(nfa_stack.pop(),index)
            nfa_stack.append(nfa)
            all_states.extend(new_states)
            index+=2
        elif char=="+":
            nfa,new_states=one_or_more(nfa_stack.pop(),index)
            nfa_stack.append(nfa)
            all_states.extend(new_states)
            index+=2
        elif char=="?":
            nfa,new_states=zero_or_one(nfa_stack.pop(),index)
            nfa_stack.append(nfa)
            all_states.extend(new_states)
            index+=2
        elif char=="×":
            operand2=nfa_stack.pop()
            operand1=nfa_stack.pop()
            nfa=concat(operand1,operand2)
            nfa_stack.append(nfa)
        elif char=="|":
            operand2=nfa_stack.pop()
            operand1=nfa_stack.pop()
            nfa,new_states=oring(operand1,operand2,index)
            nfa_stack.append(nfa)
            all_states.extend(new_states)
            index+=2
        else:
            nfa,new_states=create_nfa(char,index)
            nfa_stack.append(nfa)
            all_states.extend(new_states)
            index+=2
    return nfa_stack.pop(),all_states

def create_dict_for_jason(nfa,all_states):
    nfa_dict=dict()
    nfa_dict["startingState"]="S"+str(nfa.start.label)
    for state in all_states:
        #the state info to be added must be like that
        #"S0": { "isTerminatingState": true, "a": "S0", "b": "S1"}
        #where a, b are the transitions 
        state_info=dict()
        
        if state==nfa.accept:
            state_info["isTerminatingState"]=True
        else:
            state_info["isTerminatingState"]=False
        for char in state.transitions:
            state_info[char]="S"+str(state.transitions[char])
        
        if len(state.epsilon_closure)>0:
            state_info["epsilon"]=[]
            for epsilon_state in state.epsilon_closure:
                state_info["epsilon"].append("S"+str(epsilon_state))
        nfa_dict["S"+str(state.label)]=state_info

    return nfa_dict

def create_json(nfa_dict):  
    with open("nfa.json","w") as file:
        json.dump(nfa_dict,file,indent=4)
    print("json file created successfully")
    
# Draw the NFA graph using Graphviz

def draw_nfa(json_filename):
    # Load the NFA data from the JSON file
    with open(json_filename, 'r') as json_file:
        nfa_data = json.load(json_file)

    # Create a new Graphviz graph
    graph = graphviz.Digraph(format='png', name='NFA_graph', graph_attr={'rankdir': 'LR'})
    # graph = pydot.Dot("NFA_graph",graph_type='digraph')
    # node=pydot.Node("S"+str(nfa_data['startingState']),label="S"+str(nfa_data['startingState']),shape='circle')

    start_state=None
    # Add nodes for each state
    for state, state_data in nfa_data.items():
        if state == 'startingState':
            graph.node(state_data, label=state_data, shape= 'circle')
            start_state=state_data
            #add an edge to point to start state
            graph.node('None', label='', style='invisible')
            graph.edge('None', start_state)
        else:
            if state!=start_state:
                graph.node(state, label=state, shape='doublecircle' if state_data['isTerminatingState'] else 'circle')

    # Add edges for transitions
    for state, state_data in nfa_data.items():
        if state != 'startingState':
            for symbol, next_state in state_data.items():
                if symbol not in ['isTerminatingState', 'epsilon']:
                    graph.edge(state, next_state, label=symbol)
            for epsilon_move in state_data.get('epsilon', []):
                graph.edge(state, epsilon_move, label='ε')

    # Save the graph to a file
    graph.render('nfa_graph', format='png', cleanup=True)

    print("NFA graph generated successfully.")
    


reg="a+|b+"#"(a*b)(b?a+)"#"(a*?)*"#"(a*)*"#"(a|b)*a[ab]?"#"(a+a+)+b"#"(a*b*)([a-b]*)"##"[a-c]*" #"(a*b)(b?a+)"  #"([)" #"[a-z_][a-z0-9_]*[!?]?" #"(a|b)*bc+" #"((00)|1)*1(0|1)" #"(a*)*" #"ab(b|c)*d+" #"aa+b*b" #"(a++"
    #"a|bc1+3d4(df2)(y+2)"
#validate the regular expression
if not validate_reg(reg):
    print("invalid regular expression")
    exit()
#validate the brackets
if validate_brackets(reg)=="unbalanced parentheses":
    print("unbalanced parentheses")
    exit()
print("\n======")
print("after adding anding the regular expression")
regex_anded=regex_anding(reg)
print(regex_anded)
print("\n======")
print("after concating the range in one string")
correct_regex_with_range=concat_range(regex_anded)
if correct_regex_with_range==["%"]:
    print("invalid range expression")
    exit()
print(correct_regex_with_range)
print("\n======")
print("after removing extra anding")
correct_regex=remove_extra_anding(correct_regex_with_range)
print(correct_regex)
print("\n======")
postfix=infix_to_postfix(correct_regex)
if postfix=="unbalanced parentheses":
    print("unbalanced parentheses")
    exit()
print("after converting the regular expression to postfix")#['[a-z_]', '×', '[a-z0-9_]', ']*', '×', '[!?]', ']?']
print(postfix)
print("\n======")

nfa,all_states=postfix_to_nfa(postfix)
print("start state ")
print(nfa.start.label)
print("accept state")   
print(nfa.accept.label)
print("\n======")
nfa_dict=create_dict_for_jason(nfa,all_states)
print("NFA in json format")
# print(nfa_dict)
create_json(nfa_dict)
# Example usage
draw_nfa("nfa.json")
    
    
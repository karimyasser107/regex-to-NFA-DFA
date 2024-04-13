"""Convert regular expression to NFA."""

#start with adding special character to represent Anding
reg="ab(b|c)*d+"#"aa+b*b"#"(a++"
    #"a|bc1+3d4(df2)(y+2)"

def validate_reg(reg):
    #check if the input regular expression is valid
    if reg=="":
        return False
    if reg[0]=="*" or reg[0]=="+" or reg[0]=="?" or reg[0]=="×" or reg[0]=="|" or reg[0]=="-":
        #example "*abc" is invalid
        return False
    if reg[-1]=="|":
        #example "a|b|c|"" is invalid
        return False
    for i in range(0,len(reg)-1):
        if reg[i]=="*" or reg[i]=="+" or reg[i]=="?" or reg[i]=="|":
            if reg[i+1]=="*" or reg[i+1]=="+" or reg[i+1]=="?" or reg[i+1]=="|":
                #example "a|b||c" is invalid
                return False
        if reg[i]=="-":
            if reg[i+1].isalnum() and reg[i-1].isalnum():
                return False
    return True
def regex_anding(reg):
    correct_reg=""
    is_range=False
    last_is_put=False
    # take care this loop is from 0 to len(reg)-2 so concentarte to know how we handle the last character 
    for i in range(0,len(reg)-1):
        if reg[i]=="|" or reg[i+1]=="|":
            correct_reg+=reg[i]
            continue
        elif reg[i+1]=="." or reg[i+1]=="?" or reg[i+1]=="*" or reg[i+1]=="+":
            correct_reg+=reg[i]+reg[i+1]
            # this is the only case where we put TWO chars together
            # so, if we reached the end of the regular expression,
            # we dont want to put the last character (which is always an operator as we are in this elif) again
            # as it will be put in the last if condition
            # so we set last_is_put to True to avoid putting it again
            if i==len(reg)-2:
                last_is_put=True
                break
            correct_reg+="×"    
            continue
        elif reg[i].isalnum() or reg[i]=="]"or reg[i]==")":
            if reg[i+1].isalnum() or reg[i+1]=="[" or reg[i+1]=="(":
                correct_reg+=reg[i]
                correct_reg+="×"
                continue
        # elif reg[i]=="[" :
        #     correct_reg+=reg[i]
        #     is_range=True
        #     continue
        if reg[i]=="." or reg[i]=="?" or reg[i]=="*" or reg[i]=="+":
            continue        
        else:
            correct_reg+=reg[i]
    # put the last character in the regular expression
    # only if last_is_put is False
    if i==len(reg)-2 and not last_is_put:
        correct_reg+=reg[i+1]
    return correct_reg



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
    postfix=""
    is_range=False
    for char in infix:
        # if char.isalnum() or char=="×":
        #     postfix+=char
        if char=="(":
            stack.append(char)
        elif char==")":
            #stack[-1] is the last element in the stack
            while stack and stack[-1]!="(":
                postfix+=stack.pop()
            if stack:
                stack.pop()
            else:
                return "unbalanced parentheses"
        elif char=="[":
            is_range=True
            stack.append(char)
        elif char=="]":
            is_range=False
            #stack[-1] is the last element in the stack
            while stack and stack[-1]!="[":
                postfix+=stack.pop()
            if stack:
                stack.pop()
            else:
                return "unbalanced parentheses"
        elif char in operators:
            while stack and precedence(char)<=precedence(stack[-1]):
                postfix+=stack.pop()
            stack.append(char)
        elif char=="-":
            #if the character is a range example [a-z]
            #TODO
            postfix+=char
        else:
            #if char is a alphanumeric character
            postfix+=char
            if is_range:
                #if the character is in a range example [abc]
                postfix+="×"
    while stack:
        if stack[-1]=="(" or stack[-1]=="[":
            return "unbalanced parentheses"
        postfix+=stack.pop()
    return postfix

#validate the regular expression

if not validate_reg(reg):
    print("invalid regular expression")
    exit()
print("\n======")
regex_anded=regex_anding(reg)
print(regex_anded)
print("\n======")

postfix=infix_to_postfix(regex_anded)
if postfix=="unbalanced parentheses":
    print("unbalanced parentheses")
    exit()
print(postfix)
print("\n======")
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
    nfa1.accept.epsilon_closure.add(nfa2.start)
    # create new nfa
    new_nfa=NFA(nfa1.start,nfa2.accept) 
    return new_nfa

def oring(nfa1:NFA,nfa2:NFA,index):
    #create new start state
    new_start_state=State(index)
    #create new accept state
    new_accept_state=State(index+1)
    #create new edge between the new start state and the start state of nfa1
    new_start_state.epsilon_closure.add(nfa1.start)
    #create new edge between the new start state and the start state of nfa2
    new_start_state.epsilon_closure.add(nfa2.start)
    #create new edge between the accept state of nfa1 and the new accept state
    nfa1.accept.epsilon_closure.add(new_accept_state)
    #create new edge between the accept state of nfa2 and the new accept state
    nfa2.accept.epsilon_closure.add(new_accept_state)
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
    new_start_state.epsilon_closure.add(nfa.start)
    #create new edge between the new start state and the new accept state
    new_start_state.epsilon_closure.add(new_accept_state)
    #create new edge between the accept state of nfa and the new accept state
    nfa.accept.epsilon_closure.add(new_accept_state)
    #create new edge between the accept state of nfa and the start state of nfa
    nfa.accept.epsilon_closure.add(nfa.start)
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
    new_start_state.epsilon_closure.add(nfa.start)
    #create new edge between the accept state of nfa and the new accept state
    nfa.accept.epsilon_closure.add(new_accept_state)
    #create new edge between the accept state of nfa and the start state of nfa
    nfa.accept.epsilon_closure.add(nfa.start)
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
    new_start_state.epsilon_closure.add(nfa.start)
    #create new edge between the new start state and the new accept state
    new_start_state.epsilon_closure.add(new_accept_state)
    #create new edge between the accept state of nfa and the new accept state
    nfa.accept.epsilon_closure.add(new_accept_state)
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
    start_state.transitions[char]=accept_state
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

nfa,all_states=postfix_to_nfa(postfix)
print(nfa.start.label)
print(nfa.accept.label)
    
    
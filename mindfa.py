import json
from queue import Queue
from automathon import DFA



def DFADrawer(DFADiagram, alphabet, drawingName="DFA"):
    # Extract states
    states = set(DFADiagram.keys()) - {'startingState'}
    # Extract initial state
    initialState = DFADiagram['startingState']

    # Extract final states
    finalStates = {k for k, v in DFADiagram.items() if k != 'startingState' and v['isTerminatingState']}

    # Extract transitions
    transitions = {k: {key: value for key, value in v.items() if key not in ['isTerminatingState', 'isStartingState']}
                   for k, v in DFADiagram.items() if k != 'startingState'}

    # Create DFA object
    automata2 = DFA(states, alphabet, transitions, initialState, finalStates)

    # View DFA
    automata2.view(drawingName)



def stateEquality(stateList1, stateList2):
    # Checks if state is unique or not
    if len(stateList1) != len(stateList2):
        return False
    
    # Create sets of state names for fast membership testing
    state_names1 = {list(state.keys())[0] for state in stateList1}
    state_names2 = {list(state.keys())[0] for state in stateList2}
    
    # Check if the sets of state names are equal
    return state_names1 == state_names2

def checkUnique(lst, elem):
    # check if element is unique
    return lst.count(elem) == 0

def epsilonClosure(state, allStates):

    newStateList = []  # List to store states in the epsilon closure
    findEpsilon = Queue(maxsize=0)  # Queue to perform BFS for epsilon transitions
    
    # Extract state key and value
    key, value = list(state.keys())[0], list(state.values())[0]
    findEpsilon.put(value)
    newStateList.append(state)
    
    while not findEpsilon.empty():
        # Walk through each state in epsilon of current state if any epsilon transitions exist
        current_state = findEpsilon.get()  
        if current_state==None:
            continue
        if "epsilon" in current_state:
            for i in current_state['epsilon']:
                # Check uniqueness before adding to the queue and newStateList
                if checkUnique(newStateList, {i: allStates.get(i)}):
                    findEpsilon.put(allStates.get(i))
                    newStateList.append({i: allStates.get(i)})
    
    # Return all states in this epsilon closure
    return newStateList
def move(state, char, allStates):

    stateList = []  # List to store states reached by the move operation
    
    # Loop through the state's key-value pairs
    for key, value in state.items():
        # Skip 'isTerminatingState' key
        if key == 'isTerminatingState':
            continue
        
        # Check if the input character leads to any next states
        if char in value:
            nextState = value[char]
            for i in nextState:
                # Compute the epsilon closure for each next state and add to stateList
                stateList.extend(epsilonClosure({i: allStates.get(i)}, allStates))
    
    return stateList

stateCounter = 0
def stateMaker(states, alphabet):

    global stateCounter  # Global counter for state names
    new_state = {}  # Dictionary to store the new state
    
    # Create state name
    new_state["stateList"] = states
    new_state["bigStateName"] = "S" + str(stateCounter)
    stateCounter += 1

    # Initialize transitions for each character in the alphabet
    for char in alphabet:
        new_state[char] = ""
    
    return new_state


def DFAMaker(states):
 
    queue = Queue(maxsize=0)  # Queue for state exploration
    queue.put(states[0])  # Add starting state to the queue


    # Explore states in the DFA
    while not queue.empty():
        curr_state = queue.get()  # Get the current big state

        curr_state_list = curr_state["stateList"]  # Extract list of states from the big state
        for char in alphabet:
            new_state_list = []  # List to store states reached by transition on character 'char'

            # Compute the move operation for each state in the current big state
            for state in curr_state_list:
                new_states = move(state, char, statesOfAllTime)
                new_state_list.extend([new_state for new_state in new_states if new_state not in new_state_list])

            # Create a new big state from the list of reached states
            new_state_list = stateMaker(new_state_list, alphabet)

            # Skip if the new big state is empty
            if len(new_state_list["stateList"]) == 0:
                continue

            # Check if the new big state already exists in the big state list
            state_exists = False
            connect_to_state = new_state_list
            for s in states:
                if stateEquality(s["stateList"], new_state_list["stateList"]):
                    state_exists = True
                    connect_to_state = s
                    break

            # Update transitions of the current big state
            curr_state[char] = connect_to_state["bigStateName"]

            # Add the new big state to the big state list if it doesn't already exist
            if not state_exists:
                states.append(new_state_list)
                queue.put(new_state_list)
            
            
def format_dfa(big_state_list):
    counter = 0
    state_names_dict = {}

    # Sanitize state names and create a mapping
    for state in big_state_list:
        old_state_name = state['bigStateName']
        new_state_name = "S" + str(counter)
        state_names_dict[old_state_name] = new_state_name
        state['bigStateName'] = new_state_name
        counter += 1

    # Mark terminal states
    for state in big_state_list:
        is_terminal = any(v['isTerminatingState']  for s in state['stateList'] for k, v in s.items())
        state['isTerminatingState'] = is_terminal

    # Remove stateList and make stateName the key in the final dictionary
    dfa_dict = {'startingState': None}
    for state in big_state_list:
        if state.get('isStartingState') and state['isStartingState']:
            dfa_dict['startingState'] = state['bigStateName']
            break
    for state in big_state_list:
        del state['stateList']
        dfa_dict[state['bigStateName']] = state
        del state['bigStateName']

    # Update all old references to new state names
    for state_name, state in dfa_dict.items():
        if state_name != 'startingState':
            for char in alphabet:
                if char == 'isTerminatingState':
                    continue
                
                if char in state and len(state[char]) != 0:
                    state[char] = state_names_dict[state[char]]
                # remove unnecessary key characters
                if char in state and len(state[char]) == 0:
                    del state[char]

    return dfa_dict

def get_state_from_name(state_name):

    global DFADiagram
    for k, v in DFADiagram.items():
        if k == state_name:
            return {k: v}
    return None

def get_new_state(state, char):
   
    for k, v in state.items():
        if k not in ('isStartingState', 'isTerminatingState') and char in v:
            state_name = v[char]
            return get_state_from_name(state_name)

    return None


def get_state_group(state, state_groups):

    for group in state_groups:
        if state is None:
            break
        for k, v in state.items():
            if k not in ('isStartingState', 'isTerminatingState') and k in group["stateNames"]:
                return group
    return None
def get_state_name(state):
  
    for key, value in state.items():
        if key not in ('isStartingState', 'isTerminatingState'):
            return key


def check_other_group_members(new_state_group, state_group, current_state_groups, character):
 
    for state in state_group["states"]:
        new_state = get_new_state(state, character)
        if new_state is None:
            return False  # If there is no state to transition to, it's not in the same group

        # Get the state group of the new state
        vnew_state_group = get_state_group(new_state, current_state_groups)
        if new_state_group != vnew_state_group:
            return False

    return True


def check_other_groups(state, original_state_group, current_state_groups, alphabet):
    for state_group in current_state_groups:
        # Skip the original state group
        if state_group == original_state_group:
            continue

        # Take any state from the group
        if len(state_group["states"]) == 0:
            continue
        
        the_other_state = state_group["states"][0]
        flag = True

        # Check if the current state and any state from the other group have the same transitions
        for char in alphabet:
            new_state = get_new_state(state, char)
            the_other_state_new_state = get_new_state(the_other_state, char)
           
            
            if state != None and  list(state.values())[0]["isTerminatingState"] :
                    flag = False
                    break
            if the_other_state != None and  list(the_other_state.values())[0]["isTerminatingState"] :
                    flag = False
                    break
            if new_state != the_other_state_new_state :
                flag = False
                break

        # If all transitions match, return the other state group
        if flag:
            return state_group

    # If no matching state group is found, return None
    return None

def minDFA(state_groups, alphabet):

    old_state_group_size = -1
    # Continue until no further merges can be made
    while old_state_group_size != len(state_groups):
       
        # Create a copy of state_groups to iterate over
        curr_state_groups = state_groups.copy()
        # Loop through each state group
        for state_group in curr_state_groups:
            # If the state group has only one state, check if it can be merged with another state group
            if len(state_group["states"]) == 1:
                state = state_group["states"][0]
                potential_merge_group = check_other_groups(state, state_group, state_groups, alphabet)
                if potential_merge_group!=None:
                    # Merge the state group with the potential merge group
                    potential_merge_group["stateNames"].append(get_state_name(state))
                    potential_merge_group["states"].append(state)
                    state_group["stateNames"].remove(get_state_name(state))
                    state_group["states"].remove(state)
                    # Remove the empty state group
                    state_groups.remove(state_group)
                continue
            # Loop through each state in the state group and each character in the alphabet
            for state in state_group["states"]:
                for char in alphabet:
                    # Get the new state resulting from the transition on the current character
                    new_state = get_new_state(state, char)
                    if new_state is None and not list(state.values())[0]["isTerminatingState"]:
                        continue
                    # Get the state group of the new state
                    new_state_group = get_state_group(new_state, state_groups)
                    # If the new state group is different from the current state group, check for equivalence
                    if new_state_group != state_group:
                        if not check_other_group_members(new_state_group, state_group, curr_state_groups, char):
                            # If the rest of the group members do not transition to the same group, create a new group
                            potential_merge_group = check_other_groups(state, state_group, state_groups, alphabet)
                            if potential_merge_group!=None:
                                # Merge the state group with the potential merge group
                                potential_merge_group["stateNames"].append(get_state_name(state))
                                potential_merge_group["states"].append(state)
                                state_group["stateNames"].remove(get_state_name(state))
                                state_group["states"].remove(state)
                             
                            else:
                                # Create a new group for the state
                                new_group_of_state = {"stateNames": [get_state_name(state)], "states": [state]}
                                state_groups.append(new_group_of_state)
                                state_group["stateNames"].remove(get_state_name(state))
                                state_group["states"].remove(state)
                            break
        old_state_group_size = len(curr_state_groups)
    return state_groups



def format_minimised_dfa(minimised_dfa, alphabet):

    # Name all the state groups
    for i, state_group in enumerate(minimised_dfa):
        state_group["stateGroupName"] = 'S' + str(i)

    final_states_dict = {}
    # Create a dictionary to store the formatted states
    for state_group in minimised_dfa:
        final_state_form = {}
        # Format each state in the state group
        for state in state_group["states"]:
            state_info = list(state.values())[0]
            for k, v in state_info.items():
                if k == 'isStartingState':
                    final_state_form["isStartingState"] = True
                if k == 'isTerminatingState':
                    final_state_form["isTerminatingState"] = v

        new_name = state_group["stateGroupName"]
        # Format transitions for each character in the alphabet
        for char in alphabet:
            first_state = list(state_group["states"][0].values())[0]
            if char not in first_state.keys():
                continue
            new_state = get_new_state(state_group["states"][0], char)
            new_state_group = get_state_group(new_state, minimised_dfa)
            if new_state_group is None:
                continue
            final_state_form[char] = new_state_group["stateGroupName"]

        final_states_dict[new_name] = final_state_form

    very_final_state = {}
    # Create a dictionary to store the final formatted DFA
    for name, state_info in final_states_dict.items():
        if 'isStartingState' in state_info.keys():
            very_final_state['startingState'] = name
            break
    very_final_state.update(final_states_dict)
    return very_final_state





statesOfAllTime =None

with open("NFA.json", "r") as inputFile:
   statesOfAllTime= json.load(inputFile)
alphabet= set()

# get alphabet
for state in statesOfAllTime:
    if state != 'startingState':
        for key, value in statesOfAllTime[state].items():
            if key != 'isTerminatingState':
                 if type(value) != list:
                     value = [value]
                     statesOfAllTime[state][key] = value
            if key != 'isTerminatingState' and key != 'epsilon':
                    alphabet.add(key)


#part2 main
DFADiagram = dict()
startingState = statesOfAllTime.get("startingState")

# get epsilon closure of starting state
initState = epsilonClosure(
    {startingState: statesOfAllTime.get(startingState)}, statesOfAllTime)
initState = stateMaker(initState, alphabet) # make a initial state
# initState by this point contains the big State
initState["isStartingState"] = True
bigStateList = [initState]

DFAMaker(bigStateList)
DFADiagram = format_dfa(bigStateList)
DFADrawer(DFADiagram, alphabet, "DFA")



# let state group be of form {states: {{S1:bla bla}, {S2:bla bla}}, stateNames: ["S1", "S2"]}

# minimization
nonTerminalStates = {"states": [], "stateNames": []}
TerminalStates = {"states": [], "stateNames": []}


for k, v in DFADiagram.items():
    if k != 'startingState' and v['isTerminatingState'] == True:
        TerminalStates["states"].append({k: v})
        TerminalStates["stateNames"].append(k)
    else:
        if k != 'startingState':
            nonTerminalStates["states"].append({k: v})
            nonTerminalStates["stateNames"].append(k)


# keda we have the starting 2 groups
StateGroups = []
if (len(nonTerminalStates["stateNames"]) == 0):
    StateGroups = [TerminalStates]
elif (len(TerminalStates["stateNames"]) == 0):
    StateGroups = [nonTerminalStates]
elif (len(TerminalStates["stateNames"]) != 0 and len(nonTerminalStates["stateNames"]) != 0):
    StateGroups = [nonTerminalStates, TerminalStates]
print(StateGroups)

minimisedDFA = minDFA(StateGroups, alphabet)


format_minDFA = format_minimised_dfa(minimisedDFA, alphabet)


with open("MinimizedDFA.json", "w") as outfile:
    json.dump(format_minDFA, outfile, indent=4)
DFADrawer(format_minDFA, alphabet, "MinimizedDFA")


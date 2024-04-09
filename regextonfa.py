"""Convert regular expression to NFA."""
import re

#start with adding special character to represent Anding
reg="abc"

def regextonfa(reg):
    correct_reg=""
    for i in range(len(reg)-1):
        correct_reg+=reg[i]
        if re.match('[a-z]',reg[i]) and re.match('[a-z]',reg[i+1]):
            correct_reg+="×"
    correct_reg+=reg[len(reg)-1]
    return correct_reg

print(regextonfa(reg))
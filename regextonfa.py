"""Convert regular expression to NFA."""

#start with adding special character to represent Anding
reg="a|bc1+3d4(df2)([gh]+2)"
    #a|b×c×1+×3×d×4×(d×f×2)
def regextonfa(reg):
    correct_reg=""
    for i in range(0,len(reg)-1):
        if reg[i]=="|" or reg[i+1]=="|":
            correct_reg+=reg[i]
            continue
        elif reg[i+1]=="." or reg[i+1]=="?" or reg[i+1]=="*" or reg[i+1]=="+":
            correct_reg+=reg[i]+reg[i+1]
            correct_reg+="×"    
            continue
        elif reg[i].isalnum() or reg[i]=="]"or reg[i]==")":
            if reg[i+1].isalnum() or reg[i+1]=="[" or reg[i+1]=="(":
                correct_reg+=reg[i]
                correct_reg+="×"
                continue
        if reg[i]=="." or reg[i]=="?" or reg[i]=="*" or reg[i]=="+":
            continue        
        else:
            correct_reg+=reg[i]
        if i==len(reg)-2:
            correct_reg+=reg[i+1]
    return correct_reg

print(regextonfa(reg))
flag="hacking_for_fun}"

# hack1ng_fo1_fun}
flag2=""

print(len(flag))



for item in flag:
    if ord(item)==105 or ord(item)==114:
        flag2+=chr(49)
    else:
        flag2+=item

print(flag2)
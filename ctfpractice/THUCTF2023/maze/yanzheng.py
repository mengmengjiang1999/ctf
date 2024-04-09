import os
import random

COUNTER=100


def randomInput():
    i=random.randint(0,2)
    inputname=""
    if i==0:
        for j in range(random.randint(0,20)):
            inputname+=chr(random.randint(37,127))
    elif i==2:
        for j in range(random.randint(0,14)):
            inputname+=chr(random.randint(37,127))
    elif i==1:
        inputname="wwdwwdddsssssd"
    return inputname,i

if __name__=='__main__':
    for i in range(COUNTER):
        inputname,j=randomInput()
        with open("input.txt","w")as f:
            f.write(inputname)
        print(inputname)
        os.system("./main < ./input.txt")
        print(j)
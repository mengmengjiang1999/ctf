import os

table="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def estabilishTable():
    with open("../flag2/table.txt","r")as f:
        newtable=f.readline().strip()
    maptable={}
    for i in range(26):
        maptable[chr(ord('A')+i)]=newtable[i]
    for i in range(26):
        maptable[chr(ord('a')+i)]=newtable[i+26]
    return maptable

if __name__=='__main__':
    with open("../flag2/table.txt","r")as f:
        newtable=f.readline().strip()

    cipher=""
    with open("./message.txt","r")as f:
        message=f.read()
        for item in message:
            if ord(item)>=ord("A")and ord(item)<=ord("Z"):
                cipher+=newtable[ord(item)-ord("A")]
            elif ord(item)>=ord("a")and ord(item)<=ord("z"):
                cipher+=newtable[ord(item)-ord("a")+26]
            else:
                cipher+=item
                
    with open("./cipher.txt","w")as g:
        g.write(cipher)
        
    
    
    
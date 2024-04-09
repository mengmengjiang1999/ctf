import os
table="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

if __name__=='__main__':
    # flag1
    with open("./table.txt","r")as f:
        newtable=f.readline().strip()

    assert(len(newtable)==len(table))
    assert(newtable[-12:]==table[-12:])
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
        
    # flag2
    os.system("./main < ./table.txt > ./encoded.txt")
    
    
    
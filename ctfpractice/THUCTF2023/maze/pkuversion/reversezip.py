

with open("./attachment.zip","rb")as f:
    data=bytearray(f.read())
    print(data)
    data.reverse()
    print("\n\n")
    print(data)

    with open("./origin.png","rb")as g:
        imagedata=bytearray(g.read())
        
    finaldata=imagedata+data
    with open("./finalimage.png","wb")as g:
        g.write(bytes(finaldata))
        
        
        
        


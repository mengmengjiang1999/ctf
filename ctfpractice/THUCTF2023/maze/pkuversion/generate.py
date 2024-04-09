

maze="*** ******"+\
     "*   *    *"+\
     "* * * ** *"+\
     "* *   ** *"+\
     "**** *** *"+\
     "*   S*** *"+\
     "******** T"

# wwdwwdddsssssd

x=5
y=4
if __name__=='__main__':
    cin=input()
    if len(cin)!=14:
        pass
    else:
        for p in cin:
            if ord(p)==ord("a"):
                y-=1
            if ord(p)==ord("s"):
                x+=1
            if ord(p)==ord("w"):
                x-=1
            if ord(p)==ord("d"):
                y+=1
            
            if x<0 or x>6 or y<0 or y>9:
                break
            
            z=10*x+y
            if maze[z]==" ":
                continue
            elif maze[z]=='T':
                print("you find the flag! flag is flag{"+cin+"}")
            else:
                break
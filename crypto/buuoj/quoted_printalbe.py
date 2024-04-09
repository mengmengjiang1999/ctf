c="=E9=82=A3=E4=BD=A0=E4=B9=9F=E5=BE=88=E6=A3=92=E5=93=A6"

import quopri

from io import BytesIO

inputfile=BytesIO((c).encode('utf-8'))
outputfile=BytesIO()

# c=c.split("=")
# print(c)
# s=[]

# for item in c:
#     if item!="":
#         print(int(item,16))
#         s.append(int(item,16))
        
# print(s)

# for item in s:
#     print(chr(item))

quopri.decode(inputfile,outputfile)

print(outputfile.getvalue().decode())
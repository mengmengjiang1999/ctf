import base64


table="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


# d2G0ZjLwHjS7DmOzZAY0X2lzX3CoZV9zdNOydO9vZl9yZXZlcnGlfD==

ciphter="d2G0ZjLwHjS7DmOzZAY0X2lzX3CoZV9zdNOydO9vZl9yZXZlcnGlfD=="

print(table)

def changeTable(table:list):
    table_new=[item for item in table]
    for i in range(10):
        v=table_new[i]
        table_new[i]=table_new[19-i]
        result=19-i
        table_new[19-i]=v
    return table_new

table_new="".join(changeTable(list(table)))

print(table_new)


print (base64.b64decode(ciphter.translate(str.maketrans(table,table_new))))
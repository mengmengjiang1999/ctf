base64Char = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

base64Char=list(base64Char)

for i in range(len(base64Char)):
    base64Char[i],base64Char[(2*i+1)%64]=base64Char[(2*i+1)%64],base64Char[i]
    
print("".join(base64Char))

# BgFQJiNIRkVSZmdEholUpqtKxs1W5u9CDwLYTybMj0raz27GH4Xcn63OP8vef+/A
calculate = {}
calculate2 = {}

emoji2word = {
    '🤨': 'a', '😚': 'b', '😗': 'c', '😛': 'd', 
    '🤣': 'e', 
    '😘': 'f', 
    '😁': 'g', 
    '😆': 'h', '😄': 'i', 
    '😙': 'j', 
    '😋': 'k', 
    '🤪': 'l', 
    '😃': 'm', '😇': 'n', '😊': 'o', '😝': 'p', '😅': 'q', 
    '😜': 'r', '😍': 's', '😂': 't', '🙂': 'u', 
    '😌': 'v', '😉': 'w', '🙃': 'x',
}
emoji2text = {
    '🤨':'a',
    # '😗':'s',#待定
}

filename = './emojicorrre.txt'
resultname = './emojicorrre-result.txt'
result = []
with open(filename,"r") as file:
    line = file.readline();
    # calculate 1
    for item in line:
        # print(item)
        if item in calculate:
            calculate[item] = calculate[item] + 1
        else:
            calculate[item] = 1
    print(calculate)
    cal2 = line.split(" ")
    for item in cal2:
        if len(item)==2:
            if item in calculate2:
                calculate2[item] = calculate2[item] + 1
            else:
                calculate2[item] = 1
    print(calculate2)
    for i in range(len(line)):
        result.append(line[i])
    for i in range(len(result)):
        if result[i] in emoji2word:
            result[i] = emoji2word[result[i]]

with open(resultname, "w") as resultfile:
    resultfile.write("".join(result))





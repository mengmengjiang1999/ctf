**前言：前段时间老大发来任务，让帮忙用nmap扫一些ip段，我拿过来就准备开扫，但是发现nmap无法直接扫描同一B段不同C段下的IP段，例如111.111.111.0-111.111.222.255**

原本我是准备写个工具联动nmap来扫描大批量IP段资产的，但是由于环境有些问题，工具成品还没有出来，并且h攻防演练在即，就先和大家分享一下写的小脚本，将我们要扫描的IP循环写入文件中，再用nmap扫描就可以了

小白向脚本，保存为test.py运行，根据提示输入即可：

    
    
    a = int(input("请输入您要扫描的ip A段地址："))  
    while not 0 < a <= 255:  
    a = int(input("您的输入有误，请重新输入您要扫描的ip A段地址："))  
    ​  
    b = int(input("请输入您要扫描的ip B段地址："))  
    while not 0 <= b <= 255:  
    b = int(input("您的输入有误，请重新输入您要扫描的ip B段地址："))  
    ​  
    ipAB = str(a) + "." + str(b)  
    while 1:  
    c1 = int(input("请输入您要扫描的ip C段地址（起始地址）："))  
    while not 0 <= c1 <= 255:  
    c1 = int(input("您的输入有误，请重新输入您要扫描的ip C段地址（起始地址）："))  
    ​  
    c2 = int(input("请输入您要扫描的ip C段地址（结束地址）："))  
    while not 0 <= c2 <= 255:  
    c2 = int(input("您的输入有误，请重新输入您要扫描的ip C段地址（结束地址）："))  
    if c2 < c1:  
    print("您的输入有误，青重新输入！")  
    else:  
    break  
    ​  
    ip = []  
    ​  
    g = input("请输入要您要储存的IP的方式：\n1.单条IP方式，例：192.168.0.1\n2.同一C段IP存储为/24形式，例：192.168.0.0/24\n")  
    ​  
    while 1:  
    if g=="1":  
    for i in range(c2 + 1 - c1):  
    e = c1 + i  
    e = str(e)  
    for j in range(256):  
    j = str(j)  
    ip.append(ipAB + "." + e + "." + j)  
    break  
    elif g=="2":  
    for i in range(c2 + 1 - c1):  
    e = c1 + i  
    e = str(e)  
    ip.append(ipAB + "." + e + ".0/24")  
    break  
    else:  
    g=input("您的输入有误，请重新输入要您要储存的IP的方式：\n1.单条IP方式，例：192.168.0.1\n2.同一C段IP存储为/24形式，例：192.168.0.0/24\n")  
    ​  
    ​  
    ​  
    f = input("是否要保存全部ip地址？(Y/N)：").upper()  
    while 1:  
    if f == "Y":  
    spath = input(r"请输入您要保存的路径+文件名，例如（C:\test.txt），只输入文件名则默认保存在工具路径下：")  
    while 1:  
    try:  
    with open(spath, "a+") as file:  
    for i in range(len(ip)):  
    file.write(ip[i] + "\n")  
    print("保存成功！")  
    break  
    except:  
    spath=input(r"您输入的路径路径有误，请重新输入您要保存的路径+文件名，例如（C:\test.txt），只输入文件名则默认保存在工具路径下：")  
    break  
    elif f == "N":  
    print("没有保存ip地址！")  
    break  
    else:  
    f = input("您的输入有误，请重新输入(Y/N)：")

可以选择自己想要保存的IP形式，可以是以同一C段形式，也可以是单条形式，代码写的不好，师傅们有建议的尽管提出来，会听取师傅们意见改进的~


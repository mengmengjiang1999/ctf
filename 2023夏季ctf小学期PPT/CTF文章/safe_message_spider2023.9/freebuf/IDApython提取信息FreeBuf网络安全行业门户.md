### 数据提取：以Hitcon-Training LAB1为例 | IDApython

![1919808-20200913203620597-1783608277.png](https://image.3001.net/images/20210418/1618714218_607b9e6a8977726c219b4.png!small)

![1919808-20200913204401003-1100083111.png](https://image.3001.net/images/20210418/1618714339_607b9ee3daccc56a35587.png!small)

    
    
    ea=here()
    print hex(ea),idc.GetDisasm(ea)
    ch=idc.GetDisasm(ea)
    print ch[-9:]
    
    
    
    ea=here()
    print hex(ea),idc.GetDisasm(ea)
    ch=idc.GetDisasm(ea)
    print ch[-9:]
    print hex(ea+7),idc.GetDisasm(ea+7)
    
    ch=idc.GetDisasm(ea+7)
    print ch[-9:]
    

![1919808-20200913232747585-1793162165.png](https://image.3001.net/images/20210418/1618714377_607b9f09248d3eab8d300.png!small)

    
    
    #脚本的制约条件：锁定.text的具体定位，只能在类似数组结构的开头
    ea=here()
    test=''
    for i in range(12):
        ch=idc.GetDisasm(ea+i*7)
        test+=('0x'+ch[-9:]).rstrip('h')
        test+=','
    #print test
        #print type(ch)
    la=idc.GetDisasm(ea+12*7)
    org=la[-3:]
    num='0x'+org.rstrip('h')
    test+=num
    #print test
    l=test.split(',')
    #print l
    list=[int(x.lstrip('0x'),16) for x in l]
    #print list
    str=""
    for i in list:
        str+=chr(i%0x100)
        str+=chr(int(i%0x10000/0x100))
        str+=chr(int(i%0x1000000/0x10000))
        str+=chr(int((i%0x100000000/0x1000000)))
    #str+=chr(0x3f)
    print(str)
    

![1919808-20200915064932039-138787263.png](https://image.3001.net/images/20210418/1618714400_607b9f2036c2b30beae27.png!small)

    
    
    ea=here()
    print ea,idc.GetDisasm(ea)
    l=[]
        #数据的提取，大致分为两种类型
    for n in range(49):
        i=idc.GetDisasm(ea+n*4)
        if(i[-1:]=='h'):  #可以已结尾是否是h作为判断标志对数据进行提取
            cn=int("0x"+i[-3:-1],16)
    
        else:
            cn=int(i[-1:],10)
        l.append(cn)
    print l
    

![1919808-20200915070821720-1362506405.png](https://image.3001.net/images/20210418/1618714426_607b9f3ac70958d3d6336.png!small)

    
    
    #脚本的制约条件：锁定.text的具体定位，只能在类似数组结构的开头
    ea=here()
    test=''
    for i in range(12):
        ch=idc.GetDisasm(ea+i*7)
        test+=('0x'+ch[-9:]).rstrip('h')
        test+=','
    #print test
        #print type(ch)
    la=idc.GetDisasm(ea+12*7)
    org=la[-3:]
    num='0x'+org.rstrip('h')
    test+=num
    #print test
    l=test.split(',')
    #print l
    list=[int(x.lstrip('0x'),16) for x in l]
    #print list
    str=""
    for i in list:
        str+=chr(i%0x100)
        str+=chr(int(i%0x10000/0x100))
        str+=chr(int(i%0x1000000/0x10000))
        str+=chr(int((i%0x100000000/0x1000000)))
    #str+=chr(0x3f)
    ##print(str)
    #ea=here()
    #print ea,idc.GetDisasm(ea)
    
    l=[]
        #数据的提取，大致分为两种类型
    for n in range(49):
        i=idc.GetDisasm(ea+90+n*4)
        if(i[-1:]=='h'):  #可以已结尾是否是h作为判断标志对数据进行提取
            cn=int("0x"+i[-3:-1],16)
    
        else:
            cn=int(i[-1:],10)
        l.append(cn)
    ##print l
    flag=""
    for i in range(49):
        flag+=chr(ord(str[i])^l[i])
    print flag
    

![1919808-20200915071019317-1067745949.png](https://image.3001.net/images/20210418/1618714471_607b9f67b7bbacd320635.png!small)

![1919808-20200915071041468-98535267.png](https://image.3001.net/images/20210418/1618714501_607b9f850fc181f17e392.png!small)

**上述两个地址的差值是用来计算两组数据的偏移的，用来具体的数据提取。**


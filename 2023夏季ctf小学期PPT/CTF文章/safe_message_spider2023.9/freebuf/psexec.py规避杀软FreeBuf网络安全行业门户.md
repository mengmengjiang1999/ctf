# 前言

在内网渗透中，当获取到一个账号密码后，经常会使用impacket套件中的psexec.py进行远程连接并执行命令，但是因为用的人多了，杀软也对psexec.py特征进行了拦截，也就导致了如果使用默认的psexec.py进行执行命令时会失败。

# 原理分析

psexec.py的原理是通过smb上传一个服务程序到c:\windows（ADMIN$）目录，服务程序通过管道进行后续的命令执行的输入输出。

服务程序来自于remcomsvc.py：

![image-20220202154142470.png](https://image.3001.net/images/20220509/1652075801_6278ad195442925a9a274.png!small)

服务安装通过serviceinstall.py进行：

![image-20220202154257907.png](https://image.3001.net/images/20220509/1652075802_6278ad1a306a76b2ef165.png!small)

服务和服务文件的名字默认是随机的：

![image-20220202154435362.png](https://image.3001.net/images/20220509/1652075803_6278ad1b41c9129118c03.png!small)

直接psexec.py不带任何参数，上传过去的服务文件名就长这样：

![image-20220202154531337.png](https://image.3001.net/images/20220509/1652075803_6278ad1bd4fb76c051dd5.png!small)

因此为了防止奇奇怪怪的名字很容易被机器负责人发现，psexec.py也是提供了相应的参数用来自定义：

![image-20220202154745539.png](https://image.3001.net/images/20220509/1652075804_6278ad1c66f42e240c740.png!small)

这里要提一嘴的是，因为UAC的缘故，如果RID不是500，就算账号是管理员也是没权限上传文件到ADMIN$目录，程序报错如下：

![image-20220202152542982.png](https://image.3001.net/images/20220509/1652075805_6278ad1d03135421fed34.png!small)

# 改造

默认情况下，使用psexec.py会被拦截：

![image-20220202155144783.png](https://image.3001.net/images/20220509/1652075805_6278ad1d8b20da1b19897.png!small)

![image-20220202155118856.png](https://image.3001.net/images/20220509/1652075806_6278ad1e2a9e5032dc14b.png!small)

![image-20220202155601814.png](https://image.3001.net/images/20220509/1652075806_6278ad1ee70745e887aa8.png!small)

根据上面的杀软截图能看到是服务程序被拦截，因此我们需要对服务程序进行修改来尝试绕过杀软，源码在这：

<https://github.com/kavika13/RemCom>

这里可以尝试修改print的输出：

![image-20220202160926347.png](https://image.3001.net/images/20220509/1652075807_6278ad1fa30509bb2a813.png!small)

或者修改管道名称：

![image-20220202161001349.png](https://image.3001.net/images/20220509/1652075808_6278ad2084cb510637ad2.png!small)

然后重新生成RemComSvc，然后转成hex：

    
    
    import binascii  
    filename = 'RemComSvc.exe'  
    with open(filename, 'rb') as f:  
      content = f.read()  
    print(binascii.hexlify(content))

最终可以规避杀软进行命令执行：

![image-20220202161206479.png](https://image.3001.net/images/20220509/1652075809_6278ad21a2ec9abd274e9.png!small)

# 总结

本文介绍了通过修改服务程序来绕过杀软，让psexec.py再次大放异彩。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**


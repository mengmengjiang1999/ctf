## **事件描述**

**近日，亚信安全截获一款伪装成补丁安装程序的下载器木马病毒，该病毒运行后会弹出补丁安装成功的消息框，用来迷惑用户。实质上其会链接恶意网址下载恶意文件，并将下载的恶意文件加载到内存中，经过解密后再次下载恶意后门程序，最终的恶意程序是使用meterpreter（MSF）攻击框架生成的标准攻击载荷。亚信安全将该恶意下载器命名为：Trojan.Win32.DLOADER.BK。**

##  **攻击流程**

**![1.png](https://image.3001.net/images/20190627/1561627015_5d148987087ae.png!small)**

##  **详细分析**

### 母体文件KB4346084.exe分析

该病毒首先会创建一个线程，该线程主要用于弹出补丁安装成功的消息框，掩盖其真实的恶意行为。

![2.png](https://image.3001.net/images/20190627/1561627034_5d14899a676d8.png!small)

![3.png](https://image.3001.net/images/20190627/1561627044_5d1489a4f18e4.png!small)![4.png](https://image.3001.net/images/20190627/1561627051_5d1489ab412b4.png!small)然后其会通过访问恶意网址下载360.bin和360.ico恶意文件到系统中，我们分析发现，其下载的两个文件内容相同。其中360.bin文件是通过病毒当前进程id与恶意网址拼凑后得到的恶意URL下载而来。

![5.png](https://image.3001.net/images/20190627/1561627078_5d1489c635df0.png!small)![6.png](https://image.3001.net/images/20190627/1561627083_5d1489cb8a9d2.png!small)
![7.png](https://image.3001.net/images/20190627/1561627090_5d1489d21196c.png!small)

360.bin文件下载到系统后，该病毒文件会申请一段内存，将360.bin文件解密并删除，随后执行。  

![8.png](https://image.3001.net/images/20190627/1561627107_5d1489e3ef6e7.png!small)

![9.png](https://image.3001.net/images/20190627/1561627114_5d1489eabc306.png!small)解密后的Shellcode的行为是利用网络wininet模块从<https://XXX.1XX.112.237/rDqdZyfiIYdCHEMdHw5AsApfDh805UfvgKP4jiKWxOqeJt47-XXXXXXXXXXXXXXX>恶意网址下载另外一个恶意DLL文件。  

![10.png](https://image.3001.net/images/20190627/1561627140_5d148a0462ee9.png!small)![11.png](https://image.3001.net/images/20190627/1561627146_5d148a0a357cc.png!small)
![12.png](https://image.3001.net/images/20190627/1561627151_5d148a0f3aa84.png!small)![13.png](https://image.3001.net/images/20190627/1561627156_5d148a14489ed.png!small)![14.png](https://image.3001.net/images/20190627/1561627161_5d148a193aa1f.png!small)

### **恶意DLL文件分析**

通过查看恶意DLL的导出表，我们发现有很多导出函数，其中包括用于反射注入DLL的ReflectiveLoader()
函数和channel模块（包括创建，打开等功能函数）。其还使用了metsrv.dll文件, 该文件是meterpreter的核心组件，常常用来进行网络渗透。

![15.png](https://image.3001.net/images/20190627/1561627178_5d148a2a3847c.png!small)![16.png](https://image.3001.net/images/20190627/1561627187_5d148a33860e4.png!small)

通过进一步分析，我们发现该文件是使用meterpreter（MSF）攻击框架生成的标准攻击载荷。其使用了一种叫做Reflective
Load的技术，也就是在PE头部插入shellcode并实现一个模拟加载dll的导出函数。在shellcode中调用该导出函数将自身加载进来，并以fdwReason
= 4来调用DllMain。选择是4的原因是使正常加载的dll不会执行到功能流程（因为在MSDN中指明了fdwReason的值只能为0、1、2、3）。

实现自加载的导出函数ReflectiveLoader的校验PE头部分代码：

![17.png](https://image.3001.net/images/20190627/1561627204_5d148a44dc1d4.png!small)![18.png](https://image.3001.net/images/20190627/1561627211_5d148a4b8241b.png!small)
![19.png](https://image.3001.net/images/20190627/1561627216_5d148a5022fa1.png!small)我们可以从main函数代码中得到，只有在fdwReason
==
4时才会进入真正的功能流程，进入后会执行init()函数，其中包括远程连接到远端功能。由于是使用MSF框架，常用的功能包括加载脚本，获取代理信息，文件下载等等。  

![20.png](https://image.3001.net/images/20190627/1561627230_5d148a5e521da.png!small)

## **解决方案**

> ü 不要点击来源不明的邮件以及附件；
>
> ü 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> ü 打开系统自动更新，并检测更新进行安装。
>
> ü 更新补丁时，务必从微软官方网站下载补丁程序，切勿从其他渠道获取。
>
> 微软官方补丁查询和下载地址：<http://www.catalog.update.microsoft.com/Home.aspx>

## **IOCs**

文件名  |  SHA-1  |  亚信安全检测名  
---|---|---  
KB4346084.exe  |  8ade83ac9f3ec4885df2e887b1fd2c19ec28ec18  |
Trojan.Win32.DLOADER.BK  
360.ico/360.bin  |  5d0af0038c488635306c61e03245a5fa0284ccc9  |
Trojan.Win32.DLOADER.BK  
rDqdZyfiIYdCHEMdHw5AsApfDh805Ufxxx.dll  |
55b5b8a8f2017b5e3a9a916f6940d9330390b1e2  |  Backdoor.Win32.METERPRETER.AB  
  
***本文作者：亚信安全，转载请注明来自FreeBuf.COM**


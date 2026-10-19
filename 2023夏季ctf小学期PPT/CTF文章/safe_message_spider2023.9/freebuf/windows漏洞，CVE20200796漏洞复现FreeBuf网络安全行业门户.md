漏洞主要影响win10系统

漏洞影响主要涉及系统

> Windows 10 Version 1903 for 3.2-bit Systems
>
> Windows 10 Version 1903 for x64-based Systems
>
> Windows 10 Version 1903 for ARM64-based Systems
>
> Windows Server, Version 1903 (Server Core installation)
>
> Windows 10 Version 1909 for 3.2-bit Systems
>
> Windows 10 Version 1909 for x64-based Systems
>
> Windows 10 Version 1909 for ARM64-based Systems
>
> Windows Server, Version 1909 (Server Core installation)

首先Win10需要关闭防火墙，使网络能够到达。

1.使用奇安信的扫描软件扫描确认系统有此漏洞，扫描软件地址：<http://dl.qianxin.com/skylar6/CVE-2020-0796-Scanner.zip>

![1628501046_6110f43684795ddce35f3.png!small](https://image.3001.net/images/20210809/1628501046_6110f43684795ddce35f3.png!small)

2.使用工具使其蓝屏，确认目标有此漏洞，工具链接：<https://github.com/eerykitty/CVE-2020-0796-PoC>

![1628501119_6110f47f3fd37d813b5ce.png!small](https://image.3001.net/images/20210809/1628501119_6110f47f3fd37d813b5ce.png!small)

![1628501128_6110f488edf4a0bb25749.png!small](https://image.3001.net/images/20210809/1628501128_6110f488edf4a0bb25749.png!small)

靶机蓝屏，确认靶机系统有此漏洞，进行下一步。

3.使用msfvenom生成一个payload

![1628501264_6110f5100ccb3b8a8257a.png!small](https://image.3001.net/images/20210809/1628501264_6110f5100ccb3b8a8257a.png!small)

4.下载远程代码执行漏洞程序，链接：<https://github.com/chompie1337/SMBGhost_RCE_PoC>

![1628501307_6110f53be8f760b2c6290.png!small](https://image.3001.net/images/20210809/1628501307_6110f53be8f760b2c6290.png!small)

5.将生成的payload中标注的内容替换到下载的远程代码执行漏洞中的exploit文件中![1628501367_6110f577b7f3137be62e0.png!small](https://image.3001.net/images/20210809/1628501367_6110f577b7f3137be62e0.png!small)

注意，替换的是buf=b“”里面的内容

6.执行修改过的exploit文件

![1628501447_6110f5c7cde673121ec02.png!small](https://image.3001.net/images/20210809/1628501447_6110f5c7cde673121ec02.png!small)

注意，如果执行失败多执行几次直到出现如图的效果后，敲下回车键，

![1628501520_6110f610a3b2c4a2ac50e.png!small](https://image.3001.net/images/20210809/1628501520_6110f610a3b2c4a2ac50e.png!small)

回车后会出现以下结果，程序执行结束。

7.使用msf工具监听端口

    
    
    调用攻击模块：use exploit/multi/handler
    
    
    设置payload：setpayload windows/x64/meterpreter/bind_tcp
    
    
    设置监听端口：setlport 1234（注意，此端口为msfvenom生成payload时设置的端口）
    
    
    设置靶机的ip地址：setrhost 192.168.172.128

![1628501763_6110f70339edf73ec6011.png!small](https://image.3001.net/images/20210809/1628501763_6110f70339edf73ec6011.png!small)

exploit运行，得到shell

![1628501801_6110f7298a17dcecd410c.png!small](https://image.3001.net/images/20210809/1628501801_6110f7298a17dcecd410c.png!small)

备注：win10靶机需要提权到system，提权工具：https://github.com/danigargu/CVE-2020-0796。


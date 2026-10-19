## **前言**  

****

**什么是GPON终端？PON终端，俗称“ 光猫”，作用类似于大家所熟悉的ADSL Modem，是光纤到户家庭需备的网络设备。根据不同的技术和标准，PON
又为分为EPON和GPON两种**

腾讯WiFi安全实验室在4月30 日收到vpnMentor在其技术Blog公布了两个关于GPON Home Router
（家庭光纤网关设备）的漏洞，其中CVE为[CVE-2018-10561(
验证绕过漏洞)和CVE-2018-10562（命令注入漏洞)](https://www.vpnmentor.com/blog/critical-vulnerability-gpon-router/)
，使得攻击者可以远程用很简单的命令构造发送请求到GPON路由器上进行任意命令执行，腾讯WiFi管家安全实验室在收到以上漏洞之后进行了详细的技术分析

## 一、漏洞验证

发布的POC直接运行在某些系统上会有问题，这里直接转换成了python3代码

![1.png](https://image.3001.net/images/20180529/15275753994707.png!small)

运行结果：  

![2.png](https://image.3001.net/images/20180529/15275754108644.png!small)

可以看到POC首先利用CVE-2018-10561绕过了验证，直接访问了
/GponForm/dialog_Form(用于执行命令)和/dialog.html(用于查看执行结果
)这两个页面，再利用CVE-2018-10562在ping后注入了任意命令。

## 二、漏洞代码分析

为了更好的验证以及分析以上两个漏洞成因以及原理，我们在网上寻找了很久终于找到了相关设备的固件文件，然后利用我们的固件分析平台对固件进行解包并且反编译后，最后根据对反编译后的源码进行深入分析，可以看到漏洞代码主要是在/bin/WebMgr这个执行文件中

![3.png](https://image.3001.net/images/20180529/15275754481567.png!small)

直接搜索'images'字符串，找到sub_402c30函数，如下

![4.png](https://image.3001.net/images/20180529/15275754578179.png!small)

当字符串含有style/,script/,images/ 均对v0赋值0

![5.png](https://image.3001.net/images/20180529/15275754707256.png!small)

最后验证通过返回v0 ==0否则v0 == -1, 通过上面的分析，发现不仅仅是images/,style/和script/ 均可以触发该验证绕过漏洞。

**接下来查找注入漏洞的函数** ****

漏洞触发的整个流程是 web_mainLoop -> websUrlHandlerDefine -> E8C_Dialog_init ->
sub_4154a8 -> sub_415b88 以下是对各个函数触发的分析

**1** **、** **web_mainLoop** ****

![6.png](https://image.3001.net/images/20180529/15275754991714.png!small)

这个是一个循环，接收到了 /GponForm之后跳入websUrlHandlerDefine

 **2** **、** ******E8C_Dialog_init** ****

![7.png](https://image.3001.net/images/20180529/15275755197816.png!small)

dialog_Form 之后进入sub_4154a8

 **3** **、** ******sub_4154a8** ****

![8.png](https://image.3001.net/images/20180529/15275755472409.png!small)

首先是对 dialog_action和dest_host的取值，接着跳入 sub_415b88

![9.png](https://image.3001.net/images/20180529/1527575561669.png!small) **4**
**、** **sub_415b88**

strncpy拼接了dest_host，并且在后面直接对其进行了执行，见下面两张图

![10.png](https://image.3001.net/images/20180529/15275755785433.png!small)

![11.png](https://image.3001.net/images/20180529/15275755853560.png!small)

执行了dest_host所带的命令

我们的漏洞分析平台也发现了该注入点

![12.png](https://image.3001.net/images/20180529/15275756093860.png!small)

## 三、漏洞影响

根据腾讯WiFi管家安全实验室针对该次漏洞事件的扫描结果发现GPON Home Gameway的主机信息

![13.png](https://image.3001.net/images/20180529/15275756581260.png!small)

可以看到影响最大的墨西哥和越南两个国家受影响的设备估计有几十万(这里只列出了近期活跃的设备)。而因为国内
ISP对于网络的限制而导致我们在针对国内影响面统计上面无法给出较为客观的数据显示，但基于我们以腾讯WiFi管家的大数据进行统计分析发现，国内三大网络运营商所提供家庭用户的光猫设备，有部分型号存在相同的漏洞，截止发稿为止部分海外设备已经过其运营商远程管理服务进行远程漏洞修复，但修复速度以及覆盖面有限。

![14.png](https://image.3001.net/images/20180529/15275756736384.png!small)
此外，面对潜在的风险WiFi，腾讯WiFi管家提供了全面的 WiFi安全解决方案，为用户营造稳定、安全、绿色的WiFi网络环境。其一，腾讯WiFi
管家会根据五星WiFi标准向用户推荐网络快、网络安全的公共WiFi；其二， “风险检测”功能可以对上网环境进行关于ARP欺诈、
DNS篡改、虚假钓鱼等全方位的安全检测，并根据风险项提示帮助用户避免连上风险WiFi，保护个人信息安全和手机安全；其三，腾讯
WiFi管家特别设置安全支付通道，在用户支付时自动识别网络环境，并开启专属安全加密通道，保障用户支付安全。

 *** 本文作者：腾讯WiFi管家，转载注明来自FreeBuf.COM**  


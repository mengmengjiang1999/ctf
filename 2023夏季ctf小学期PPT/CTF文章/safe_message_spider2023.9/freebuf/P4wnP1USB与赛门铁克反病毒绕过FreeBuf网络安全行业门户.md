**最近，我使用P4wnP1 image把我手头的Raspberry Pi Zero W转换成了一个bad
USB。我的最终目标是运行远程命令shell，同时绕过已启用完全保护的最新版Symantec
SEP。我通过创建自己的有效负载payload，可以轻松的运行远程shell，但由于Symantec提供的高级功能SONAR和IPS检测技术使其难以执行。想要解决这个问题并不难，你只需对payload进行加密传送即可，因为这样赛门铁克将无法对其进行分析。**

在本文的内容正式开始之前，我建议大家先去阅览以下是这些有关反病毒绕过的文章：

> <http://niiconsulting.com/checkmate/2018/06/bypassing-detection-for-a-> reverse-meterpreter-shell/>
>
> <https://gbhackers.com/malicious-payload-evasion-techniques/>
>
> <https://www.shellterproject.com/>

实验环境及设备要求：

> Raspberry Pi Zero W 和 SD Card
>
> Pi Zero W USB A addon（<https://www.amazon.com/MakerFocus-Raspberry-Required-> Provide-Connector/dp/B077W69CD1> and
> <http://www.raspberrypiwiki.com/index.php/Raspberry_Pi_Zero_W_USB-> A_Addon_Board>）
>
> 用于攻击的笔记本电脑，本文中的攻击机IP为192.168.1.106。
>
> 启用Symantec SEP完全保护的Windows 10机器

## 设置

### P4wnP1

在这里我不会再对P4wnP1 USB的设置进行说明，因为已有几篇文章对此进行了详细的介绍。你可以参阅官方的git
<https://github.com/mame82/P4wnP1_aloa> 和 WIKI
<https://p4wnp1.readthedocs.io/en/latest/>。

设置的一些注意事项，我更改了以下的重要设置项：

> 热点名称
>
> USB HID攻击脚本

最终设备的一些图片。

![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239374_5cc2540e15aa5.jpeg!small)![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239372_5cc2540ce8557.jpeg!small)![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239375_5cc2540f28a55.jpeg!small)

###  **受害者机器**

我的测试机器运行Windows 10.0.16299.125 和 Symantec Endpoint Protection 14.2的试用版。

![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239395_5cc25423b2e45.png!small)

![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239413_5cc254351b94d.png!small)

我还需确保UAC在默认设置下已启用。

![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239428_5cc25444adfdd.png!small)

###  **攻击机**

我将自己定制的Ubuntu机器用于渗透测试。测试的一个警告是，我在同一个网络上才能连接。你可以通过443等端口隐藏你的连接和出站，这在公司网络上通常是允许的，几乎没有过滤。

## 攻击我们的目标

### Payload

混淆技术在躲避payload检测方面发挥着巨大作用。我喜欢使用c# 或 c来创建自己的payload。这里有一篇关于这方面的精彩文章，你可以进行参阅
<https://medium.com/@Bank_Security/undetectable-c-c-reverse-shells-fab4c0ec4f15>。对于这个特定的实例，我使用了一个简单的c#
payload，源码由上述作者在[github](https://gist.github.com/BankSecurity/55faad0d0c4259c623147db79b2a83cc)托管和创建。

这里我要提醒你对攻击机的IP和端口做一些小的改动，我使用443端口进行测试。

我在受害者机器上运行了一个测试实例，我很惊讶赛门铁克竟然没有检测到。

## Payload Delivery

传送payload并不容易。赛门铁克的SONAR非常严密的监控着powershell和命令提示符，似乎能检测到我所有的行为。

我尝试使用certutil从我本地网络服务器上托管的网站上来提供payload。另一种方法是将payload解码为base64，并使用certutil进行解码。但这都失败了。

最终我使用了一种非常简单的技术，就是通过正在运行的SyncAppvPublishingServer来执行代码。你可以在[这里](https://ired.team/offensive-security/powershell-without-powershell)找到有关该技术及类似技术的详细说明。这也让我完全躲过了赛门铁克对powershell的监控。

传送payload我使用了一个简单的命令，通过已躲避检测的powershell下载payload，并且自定义的payload也可以躲避检测。下载后文件将从用户的配置文件中运行。让我们注意力转向以下代码。

## 获取 shell

为了完成攻击，我设置了bad USB来执行命令。下面是我的设置中的一些图片。我通过WiFi连接到了我的Android手机，访问了我的bad
USB。赛门铁克没有检测到，因为这不是USB设备，而是被当作键盘。

![7P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239464_5cc2546864fa4.png!small)![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239468_5cc2546c1bd5c.png!small)

![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239546_5cc254baad859.png!small)![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239516_5cc2549c832c7.png!small)

HID脚本被设置为等待用户重复性按下Numlock键，何时以及如何执行你完全可以根据你个人的喜好进行修改。注意！USB
HID设备将在屏幕上显示，你必须确保用户不会发现或怀疑才行。

我设置的HID脚本如下：

执行后，我获得了一个远程shell。

![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239607_5cc254f7091b4.png!small)

## 更新— 其他AV解决方案

根据反馈，我试着测试其他一些解决方案。

到目前为止，Windows Defender在攻击检测方面的能力还是非常强的，如下所示。

 **Windows Defender**

 **![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239637_5cc255156eb01.png!small)![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239671_5cc2553788f75.png!small)**

###  **赛门铁克**

 **![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239689_5cc2554976b1e.png!small)**

 **![P4wnP1
USB与赛门铁克反病毒绕过](https://image.3001.net/images/20190426/1556239721_5cc25569cf477.png!small)**

## 未来计划

> 使用基于c的持久性payload传送
>
> 修改HID使其更为隐蔽

 ***参考来源：[medium](https://medium.com/@fbotes2/advance-av-evasion-symantec-and-p4wnp1-usb-c7899bcbc6af)，FB小编secist编译，转载请注明来自FreeBuf.COM**  


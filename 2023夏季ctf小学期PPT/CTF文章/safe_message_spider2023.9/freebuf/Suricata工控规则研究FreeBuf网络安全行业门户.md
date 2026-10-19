****

****

****

**Suricata是一款免费开源的网络威胁检测工具。主要用于实时入侵检测（IDS），嵌入式入侵防御（IPS）和网络安全监控（NSM）等。因工作需要，我也准备来盘一下，准备部署检测一下工控这块的流量，同时也添加一些工控规则来提高检测效率。**  

##  ****Suricata介绍： ****

虽然Suricata作为一款免费开源的安全工具，但是它得到了众多企业的认可，很多都在部署和使用它。这代表Suricata是成熟的，功能完善，实用性强的安全工具。Suricata是一款高性能网络入侵检测防御引擎。该引擎基于多线程，充分利用多核优势。它支持多种协议，如：ip4、ipv6、tcp、udp、http、smtp、pop3、imap、ftp等。可动态加载预设规则，支持多种文件格式统计数据输出，如pcap、json、unified2等，非常便于与Barnyard2等工具集成。

suricata所有版本：<https://openinfosecfoundation.org/download/>

![image.png](https://image.3001.net/images/20200522/1590114590_5ec7391e0412d.png!small)

##  **Suricata架构：**

有三种运行模式，分别为single，workers，autofp。官方推荐性能最佳的运行模式为workers模式。  
single模式：只有一个包处理线程，一般在开发模式下使用。

workers模式：多个包处理线程，每个线程包含完整的处理逻辑。

autofp模式：有多个包捕获线程，多个包处理线程。一般适用于nfqueue场景，从多个queue中消费流量来处理。

报文检测系统通常包含四大部分，报文获取、报文解码、报文检测、日志记录；Suricata不同的功能安装模块划分，一个模块的输出是另一个模块的输入，Suricata通过线程将模块串联起来，如下图所示：

![image.png](https://image.3001.net/images/20200522/1590116501_5ec74095b5395.png!small)

##  **Suricata部署** **：**

安装步骤，以Ubuntu1804版本为例，可以使用官方的PPA进行安装：

    
    
    sudo add-apt-repository ppa:oisf/suricata-stable      
    sudo apt update      
    sudo apt install suricata jq

1、更新规则：

    
    
    suricata-update

2、测试suricata正常运行：

    
    
    suricata -T

3、启动运行：

    
    
    suricata -i ens33 -c /etc/suricata/suricata.yaml

 **配置解读：**

cd 到suricata配置文件目录： cd /etc/suricata/, 我们会查看到如下4个配置文件
classification.config/reference.config/suricata.yaml/threshold.config
和一个rules文件夹。

suricata.yaml：是Suricata默认的配置文件，以硬编码的形式写在源代码中,里面定义了几乎关于Suricata的所有运行内容，包括运行模式、抓包的数量和大小、签名和规则的属性和日志告警输出等等。

classification.config：定义了各种流量攻击类型和优先级，类似拒绝服务攻击和web应用攻击等，如下图所示：

![image.png](https://image.3001.net/images/20200525/1590410212_5ecbbbe46760b.png!small)

reference.config：记录一些安全网站，漏洞平台的网址，或者是自己可以自定义的url，是参考的意思，用来联系外部的恶意攻击检测网站中关于此类攻击的页面。

threshold.config：threshold（阈值）关键字可用于控制规则的警报频率，可用于在规则生成警报之前为其设置最小阈值.

rules文件夹：存放不同种类的规则，规则用来判定流量攻击类型，并定义攻击类型和告警种类，可以存放自带的规则，也可以自己按规则语法编写，如下图所示：

![image.png](https://image.3001.net/images/20200524/1590306599_5eca272730eb6.png!small)

 **规则详解** **：**

接下来我们主要讲Suricata的规则，这是检测工具的灵魂，同样的产品，别人的好用，拦截率准确率高，误报率低，那就是人家规则写得好。Suricata的规则书写参考snort规则（suricata完全兼容snort规则），下面我就来简单介绍下规则的每段含义，因为主要是讲工控规则，所以我取一条工控规则来说，规则如下：

    
    
    alert modbus any any -> any any (msg:"SURICATA Modbus Request flood detected"; flow:to_server;app-layer-event:modbus.flooded; classtype:protocol-command-decode; sid:2250009; rev:2;)

alert：默认顺序为：pass，drop，reject，alert，跳过、丢弃、拒绝、警告四种类型的动作

Modbus：注明协议种类，UDP/ICMP等

Any：源地址/目的地址（IP）

Any：源端口/目的端口

->：方向，单向流量；<>双向流量

Any：源地址/目的地址（IP）

Any：源端口/目的端口

msg:"SURICATA Modbus Request flood detected"：关键字msg提供对触发警报的有关签名/规则相关文本提示信息

flow:to_server：客户端到服务器

app-layer-event:modbus.flooded：具体攻击内容

classtype:protocol-command-decode：提供有关规则和警报分类的信息，由classification.config文件定义。

sid:2250009：用于唯一性规则标识，sid不能重复

rev:2：规则版本号，每次修改规则rev则递增1

 **工控规则编写：**

Suricata现在主要是et/open
规则，这是系统自带的规则，目前开源免费的就是et/open、pt规则、sslbl规则，其余的需要授权码才能更新。推荐给大家一个补充规则的链接，<https://github.com/ptresearch/AttackDetection>
的开源规则，里面包含了近几年常见cve漏洞的检测，大家可以酌情使用。

其实自己规则编写也不难，上面介绍了规则每部分的含义，最好写的是包含content的规则，例如我们知道modbus的停启功能码是40,41，我们可以在规则里编写content:
"|00 00 00 00 33 41 ff 00|"来匹配；如果是应用层的流量攻击，就可以写成 app-layer-event:dnp3.flooded/app-layer-event:modbus.invalid_length等。一般在工控规则中，最常见的应用层的检测和对功能码的检测，截取关键的功能码配合偏移位置（offset）和结束位置来匹配（depth）,如下图所示：

![image.png](https://image.3001.net/images/20200525/1590410472_5ecbbce838211.png!small)

我参考了之前大佬写的Suricata（Snort）工控方面的规则，如下图所示，这是关于西门子S7的规则，主要用来检测关于Nmap通过扫描102端口开启来寻找PLC的流量：

![image.png](https://image.3001.net/images/20200524/1590327443_5eca78936afe4.png!small)

里面还包含了对现有modbus、enip和dnp3规则补充，建议有兴趣的朋友可以去看下：

链接奉上：<https://github.com/digitalbond/Quickdraw-Snort>

 **模拟流量攻击** **：**

分析和编写了Suricata的规则，下面就进行实际的流量测试，不过在测试之前，对suricata.yaml 配置文件还要做小小的修改，因为我是对Modbus
PLC设备进行攻击的时候抓取流量包，然后保存下来放到Suricata里面回放，所以要将下图中的pcap-file改成yes：

![image.png](https://image.3001.net/images/20200521/1590063043_5ec66fc37f6de.png!small)

虽然规则里包含了Modbus的规则，但是默认是不开启的，所以我们在suricata.yaml里面找到Modbus这块，改成yes：

![image.png](https://image.3001.net/images/20200521/1590062971_5ec66f7b436b9.png!small)

接着我通过修改抓取到Modbus PLC之间的通信的Session id，然后带上Session
id对数据包进行长度和非法字符串的修改，再通过python脚本发送给PLC，同时用wireshark来抓取，以此来获取我们需要的数据包。我把数据包放入服务器中后，通过执行suricata
-r
modbus.pcap，对数据包进行回放，然后导出json格式的日志进行查看，如下图所示，显示alert并且显示唯一的SID号，可以去rules里面找到对应命中的是哪条规则：

![image.png](https://image.3001.net/images/20200524/1590323066_5eca677a6925c.png!small)

![image.png](https://image.3001.net/images/20200524/1590326869_5eca7655792bd.png!small)

下图是suricata操作的一些命令，有需要的朋友可以看一下：

![image.png](https://image.3001.net/images/20200522/1590137321_5ec791e996093.png!small)

## 总结：

Suricata其实包含的功能十分丰富，因篇幅有限，我只验证解释了关于Suricata工控方面的使用，Suricata支持内嵌lua脚本，以实现自定义检测和输出脚本，支持常见数据包解码，支持常见应用层协议解码，支持分析离线pcap文件和pcap文件方式存储流量数据，这些好用的功能都需要大家一点点去摸索和拓展使用。

Suricata规则这一块，是需要大家一点点去积累完善的，通过平时搜集的威胁情报，结合自己系统的生产环境，以及定期关注新爆出的安全漏洞等，自己慢慢去增加丰富规则，来使我们的安全世界更加坚固！

 ***本文作者：黄一113530，转载请注明来自FreeBuf.COM**


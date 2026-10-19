本文作者： 3s_NwGeek

原创投稿详情：[重金悬赏 | 合天原创投稿等你来！](http://mp.weixin.qq.com/s/PTOqQmOppIaQjx-_teGdqQ)

* * *

 **背景介绍** ：

公司检测到异常流量，及多名员工收到钓鱼邮件，发现某邮件系统存在漏洞 , 黑客通过该漏洞获取大量信息
，所以抽取当天网络流量进行分析，数量有5.3G，大概一千三百万个数据包。

![模拟企业流量入侵溯源分析.-20180404改--通过128.png](https://image.3001.net/images/20180417/15239280216827.png!small)  

 **  
**

 **分析目标：**

1\. 攻击者使用的伪造邮箱地址是多少

2\. 攻击者发送钓鱼邮件的ip是多少

3\. 邮件中的恶意url是多少

4\. 攻击者发送成功的钓鱼邮件是什么

5\. 服务器的漏洞是什么

6\. 黑客对系统进行了什么攻击

 **  
**

 **前期准备：**

 **1.** Wireshark（流量分析工具）

2\. Python（pyshark数据包处理模块）

3\. 面对一千三百万个数据包不放弃的精神

##  

## 分析过程大纲：

1\. 流量清洗

2\. 流量分层

3\. 入侵流量追踪

4\. 漏洞溯源分析

## 0x01: 流量清洗

在等量分解的数据包中，取样抽查，每个分包大概有66万个包左右

![模拟企业流量入侵溯源分析.-20180404改--通过410.png](https://image.3001.net/images/20180417/15239282461131.png!small)  

  

再看看数据包协议分层  

![模拟企业流量入侵溯源分析.-20180404改--通过424.png](https://image.3001.net/images/20180417/1523950149593.png!small)  

协议分层中看到smtp协议(邮件服务协议) #SMTP协议详解请见附录4

  

根据背景描述，公司检测到异常流量，及多名员工收到钓鱼邮件，初步猜测，攻击者对网站攻击引发异常流量并且使用邮件服务协议发送的钓鱼邮件。

  

所以暂且先看smtp协议和http协议的数据包

进行流量清洗  

  

 **Wireshark自带工具：**

mergecap（合并流量包）

tshark（流量包过滤）

editcap（流量包分解）

（用法参考附录：流量包分解合并（wireshark自带））

  

清洗思路（合并流量包→筛选smtp、http协议→得出流量包）

  

第一步将所有流量包合并：

mergecap -w total.pcap a.pcap b.pcap //（文件名太长简写成a和b）

得到total.pcap,对它经行流量清洗，目标是过滤出，smtp，http流量

清洗：tshark -r total.pcap -Y pop||smtp||http -w
result.pcap（total.pcap为上一步合并的数据包）

  

（过滤参数可以参考文末附录： **Tshark使用参数详解** ）

得出：result.pcap 2万个数据包左右，以下过程都基于这个数据包

## 0x02: 流量分层

接下来先看smtp数据包，wireshark过滤条件为：smtp

![模拟企业流量入侵溯源分析.-20180404改--通过999.png](https://image.3001.net/images/20180417/15239503424525.png!small)  

  

选择统计→对话，查看流量走向情况

![模拟企业流量入侵溯源分析.-20180404改--通过1018.png](https://image.3001.net/images/20180417/15239503649940.png!small)  

  

发现两个ip地址存在。分别查看他们ip的流量

![模拟企业流量入侵溯源分析.-20180404改--通过1044.png](https://image.3001.net/images/20180417/15239524737467.png!small)  

  

1）. 过滤条件为smtp and ip.addr==101.36.79.67

发现一个邮箱发到多个邮箱相同的邮件，

邮件内容为：A new system of IT is online, please click on the link below, to assist
to test the running state of system,thank you!
[http://211341.vhost328.cloudvhost.cn](https://link.zhihu.com/?target=http%3A//211341.vhost328.cloudvhost.cn/)

邮件内容有诱导性点击链接并带有url地址[http://211341.vhost328.cloudvhost.cn](https://link.zhihu.com/?target=http%3A//211341.vhost328.cloudvhost.cn)，比较可疑

![模拟企业流量入侵溯源分析.-20180404改--通过1387.png](https://image.3001.net/images/20180417/15239524949248.png!small)  

  

尝试过滤条件为smtp and ip.addr==112.90.83.115

![模拟企业流量入侵溯源分析.-20180404改--通过1429.png](https://image.3001.net/images/20180417/15239525084702.png!small)  

  

从该ip邮件中内容上看未发现异常

相比之下101.36.79.67比较可疑，需再一步证实

  

再回到筛选条件为smtp的数据包，遍历所有的数据包，统计邮箱出现最多的次数（附件在附录解释下，先看图）

![模拟企业流量入侵溯源分析.-20180404改--通过1532.png](https://image.3001.net/images/20180417/15239525242279.png!small)  

  

遍历所有stmp邮件发现[it@t3sec.cc](mailto:it@t3sec.cc)这个邮箱出现次数异常，比其他邮箱出现次数多10倍，由此综合上面先前推测可疑邮件发送ip地址，和发送这个邮件的ip地址101.36.79.67地址相吻合，所以推断：

攻击者ip为101.36.79.67

攻击者使用的伪造邮箱地址是[it@t3sec.cc](mailto:it@t3sec.cc)

可疑钓鱼链接为：
[http://211341.vhost328.cloudvhost.cn](https://link.zhihu.com/?target=http%3A//211341.vhost328.cloudvhost.cn)

发现基本只有172.16.60.200在使用邮件服务器172.16.60.247

并且登陆邮箱为

##  

## 0x03: 入侵流量追踪

根据发现攻击者的ip

去重新筛选数据包，条件为源ip为101.36.79.67的数据包

尝试搜索木马及注入或xss关键字

ip.addr == 101.36.79.67 && http matches "upload|alert|script|eval|select"

最终在条件为POST请求，内容包含eval 筛选出木马流量

![模拟企业流量入侵溯源分析.-20180404改--通过2047.png](https://image.3001.net/images/20180417/15239525415632.png!small)  

##  

## 0x04: 漏洞溯源分析

根据url路径和页面名称，推出该网站漏洞是任意文件上传漏洞

（该post数据包有upload关键字→推测试上传页面）

（该post数据包访问文件为hack.php→推测为webshell）

总体推测：上传页面上传了webshell

查看该上传源码，发现的确存在没有任何安全防护，存在任意文件上传漏洞。

![模拟企业流量入侵溯源分析.-20180404改--通过2220.png](https://image.3001.net/images/20180417/15239525581110.png!small)  

  

Up.php 没有任何文件后缀等过滤

![模拟企业流量入侵溯源分析.-20180404改--通过2241.png](https://image.3001.net/images/20180417/15239525727999.png!small)  

  

证实：任意文件上传漏洞

攻击者上传木马后，执行命令

![模拟企业流量入侵溯源分析.-20180404改--通过2273.png](https://image.3001.net/images/20180417/15239525862105.png!small)  

  

命令进行了base64加密，相关命令如下

V2hvYW1p

SWZjb25maWc=

Q2F0IC9ldGMvcGFzc3dk

解密后为Whoami、Ifconfig、Cat /etc/passwd等等

但此次分析目标到此已达成

1\. 攻击者使用的伪造邮箱地址是多少

it@t3sec.cc

2\. 攻击者发送钓鱼邮件的ip是多少

101.36.79.67

3\. 邮件中的恶意url是多少

[http://211341.vhost328.cloudvhost.cn](https://link.zhihu.com/?target=http%3A//211341.vhost328.cloudvhost.cn)

4\. 攻击者发送成功的钓鱼邮件是什么

Hi all

A new system of IT is online, please click on the link below, to assist to
test the running state of system,thank you!
[http://211341.vhost328.cloudvhost.cn](https://link.zhihu.com/?target=http%3A//211341.vhost328.cloudvhost.cn/)

5\. 服务器的漏洞是什么

任意文件上传漏洞

6\. 黑客对系统进行了什么攻击

服务器远程代码执行；针对公司的apt攻击（钓鱼）

参加过铁三的前辈大哥可能比较熟悉这些，数据包来源铁三比赛，小弟想更多人认识到这个流量分析，网上搜了下好像关于使用流量分析的文章比较少，使用python进行分析流量包的更少之又少了，总结了一下特此一码。

由于尽量使大家简单明白分析的过程的原理，此次使用wireshark给大家分析过程

其实实际过程中所有的分析过程都可以用python写的脚本来进行分析

Python 的pyshark模块

上述文章分析过程中有错误的话请大家指点一下，谢谢大家

  

附上简单的pyshark入门代码

    
    
    （python2.7）
    import sys
    import pyshark
    from pyshark.capture.capture import Capture
    reload(sys)
    sys.setdefaultencoding('utf-8') （环境初始化）
     def main():
        pass
        path='C:\Users\Desktop\result.pcap'			#读取pcap文件路径 cap = pyshark.FileCapture(path,display_filter='http')	#定义对象并筛选过滤条件为http for p in cap:			#遍历所有数据包
     try:
                print p.http.file_data	#提取数据包中的http内容
     except Exception as e:		#报错显示
     print e
    
    if __name__ == '__main__' :
        main()
        pass
    

初衷是想读者了解 除了手工打开pcap一个一个看并分析，原来还可以用python读取自动分析。

上面只是打开一个pcap文件读取数据包的入门方法。直接贴代码只能告诉大家可能只学到一个知识点，告诉大家入门方法去探索，就有学到无限知识的可能

而本次流量分分析用到的关键思路只是用正则匹配邮箱，然后做一次统计而已，比较简单，下面追加关键代码。

  

关键代码如下

    
    
    patten = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b') #正则爬邮箱
    path='C:\Users\Desktop\\result.pcap '#文件路径 cap = pyshark.FileCapture(path,display_filter='imf') #过滤文件smtp邮件内容imf for p in cap:		#遍历数据包
        p=str(p)		#转str格式 try:
            print p
            # a=a+re.findall(re.compile(patten),p)	#数组中加入邮箱方便统计
        except Exception as e:
            print e
    print a
    

pyshark参数条件参考附录

## 附录

## 附录一：流量包分解合并（wireshark自带）

editcap.exe -c 100 D:\dump.pcap D:\test.pcap

  
![模拟企业流量入侵溯源分析.-20180404改--通过4261.png](https://image.3001.net/images/20180417/15239526122352.png!small)

![模拟企业流量入侵溯源分析.-20180404改--通过4263.png](https://image.3001.net/images/20180417/1523952885506.png!small)  

  

在wireshark中通过filter过滤出sip信令，但是在多个文件中,megecap可以将多个pcap文件合并为一个文件。

用法：mergecap -w <输出文件> <源文件1> <源文件2> ...  
示例：  
mergecap -w compare.pcap a.pcap b.pcap

Tshark -r target.pcap -Y pop -w pop.pcap

##  

## 附录二：Tshark使用参数详解

Tshark官方文档[https://www.wireshark.org/docs/man-pages/tshark.html](https://link.zhihu.com/?target=https%3A//www.wireshark.org/docs/man-pages/tshark.html)

 **捕获接口:**  
-i: -i <interface> 指定捕获接口，默认是第一个非本地循环接口;

-f: -f <capture filter> 设置抓包过滤表达式，遵循libpcap过滤语法，这个实在抓包的过程中过滤，如果是分析本地文件则用不到。

-s: -s <snaplen> 设置快照长度，用来读取完整的数据包，因为网络中传输有65535的限制，值0代表快照长度65535，默认也是这个值；  
-p: 以非混合模式工作，即只关心和本机有关的流量。  
-B: -B <buffer size> 设置缓冲区的大小，只对windows生效，默认是2M;  
-y: -y<link type> 设置抓包的数据链路层协议，不设置则默认为-L找到的第一个协议，局域网一般是EN10MB等;  
-D: 打印接口的列表并退出;  
-L 列出本机支持的数据链路层协议，供-y参数使用。  
  
 **捕获停止选项:**  
-c: -c <packet count> 捕获n个包之后结束，默认捕获无限个;  
-a: -a <autostop cond.> ... duration:NUM，在num秒之后停止捕获;  
filesize:NUM，在numKB之后停止捕获;  
files:NUM，在捕获num个文件之后停止捕获;

捕获输出选项:  
-b <ringbuffer opt.> ... ring buffer的文件名由-w参数决定,-b参数采用test:value的形式书写;  
duration:NUM - 在NUM秒之后切换到下一个文件;  
filesize:NUM - 在NUM KB之后切换到下一个文件;  
files:NUM - 形成环形缓冲，在NUM文件达到之后;  

 **RPCAP选项:**  
remote packet capture protocol，远程抓包协议进行抓包；  
-A: -A <user>:<password>,使用RPCAP密码进行认证;

输入文件:  
-r: -r <infile> 设置读取本地文件 

**处理选项:**  
-2: 执行两次分析  
-R: -R <read filter>,包的读取过滤器，可以在wireshark的filter语法上查看；在wireshark的视图->过滤器视图，在这一栏点击表达式，就会列出来对所有协议的支持。  
-Y: -Y <display filter>,使用读取过滤器的语法，在单次分析中可以代替-R选项;  
-n: 禁止所有地址名字解析（默认为允许所有）  
-N: 启用某一层的地址名字解析。“m”代表MAC层，“n”代表网络层，“t”代表传输层，“C”代表当前异步DNS查找。如果-n和-N参数同时存在，-n将被忽略。如果-n和-N参数都不写，则默认打开所有地址名字解析。

-d: 将指定的数据按有关协议解包输出,如要将tcp 8888端口的流量按http解包，应该写为“-d tcp.port==8888,http”;tshark -d. 可以列出所有支持的有效选择器。  

**输出选项:**  
-w: -w <outfile|-> 设置raw数据的输出文件。这个参数不设置，tshark将会把解码结果输出到stdout,“-w -”表示把raw输出到stdout。如果要把解码结果输出到文件，使用重定向“>”而不要-w参数。  
-F: -F <output file type>,设置输出的文件格式，默认是.pcapng,使用tshark -F可列出所有支持的输出文件类型。  
-V: 增加细节输出;  
-O: -O <protocols>,只显示此选项指定的协议的详细信息。  
-P: 即使将解码结果写入文件中，也打印包的概要信息；  
-S: -S <separator> 行分割符  
-x: 设置在解码输出结果中，每个packet后面以HEX dump的方式显示具体数据。  
-T: -T pdml|ps|text|fields|psml,设置解码结果输出的格式，包括text,ps,psml和pdml，默认为text  
-e: 如果-T fields选项指定，-e用来指定输出哪些字段;  
-E: -E <fieldsoption>=<value>如果-T fields选项指定，使用-E来设置一些属性，比如  
header=y|n  
separator=/t|/s|<char>  
occurrence=f|l|a  
aggregator=,|/s|<char>  
-t: -t a|ad|d|dd|e|r|u|ud 设置解码结果的时间格式。“ad”表示带日期的绝对时间，“a”表示不带日期的绝对时间，“r”表示从第一个包到现在的相对时间，“d”表示两个相邻包之间的增量时间（delta）。

-u: s|hms 格式化输出秒；  
-l: 在输出每个包之后flush标准输出  
-q: 结合-z选项进行使用，来进行统计分析；  
-X: <key>:<value> 扩展项，lua_script、read_format，具体参见 man pages；  
-z：统计选项，具体的参考文档;tshark -z help,可以列出，-z选项支持的统计方式。  
  
**其他选项:**  
-h: 显示命令行帮助；  
-v: 显示tshark 的版本信息; 

## 附录三：Pyshark过滤参数

a= pyshark.FileCapture(path,display_filter='http')

a为定义pcap文件对象

本次主要用到过滤参数有

a.highest_layer 最高层的协议内容

a.http.request_method 请求方法

a.http.chat 访问方法加路径

a.http.request_uri 访问路径

a.http.host 访问host地址

a.http.field_names http包参数

a.ip.src_host 源ip地址

a.ip.dst_host 目的地址

a.http.request_full_uri url地址

str(c.http.file_data) 返回包内容

## 附录四：SMTP协议解释

SMTP协议 服务器的熟知端口号为25
，与之前总结过的telnet协议和FTP协议类似的地方是，SMTP协议的客户端和服务器端都是通过命令和响应的形式进行交互
，即SMTP客户通过命令向SMTP服务器发送操作请求，而服务器则通过3位的数字对响应的请求作出响应。SMTP规定了14条命令和21中应答信息，每条命令有4个字母组成，而每一种应答一般只有一行信息，有一个3位数字的代码开始，后面附上很简单的附加说明。

邮件传送主要包括3个阶段： 建立连接 、 邮件传送 和 终止连接 。

  

**建立连接阶段：**

1.当SMTP客户端每隔一定时间对邮件缓存扫描一次，如发现有邮件，就使用SMTP的熟知端口号25与接收方的邮件服务器的SMTP服务器建立TCP连接。

2.接收方SMTP服务器发出“220 Service ready"告诉客户端它已经准备好接收邮件。若服务器未就绪，它就发送代码421（服务器不可用）。

3.客户发送HELO报文，并使用它的域名地址标志自己。目的是：用来把客户的域名通知服务器，值得注意的是，
在TCP的连接建立阶段，发送方和接收方都是通过它们的IP地址来告诉对方的
。（HELO报文是最初的，用户名和密码都不加密。现在改为EHLO，用户名和密码都进行base64编码发送）

4.服务器响应代码250（请求命令完成）或根据情况的其他一些代码。

  

**邮件传送阶段：**

在SMTP客户与服务器之间建立连接后，发件人就可以与一个或多个收件人交换单个的报文了。若收件人超过一个，则下面步骤3和步骤4将重复进行。

1.客户发送MAIL
FROM报文介绍报文的发送者。它包括发送人的邮件地址（邮箱名和域名，如house@qq）。这个步骤是必要的：因为可以给服务器在返回差错或报文时的返回邮件地址
。

2.服务器响应代码250（请求命令完成）或其他适当的代码。

3.客户发送RCPT（收件人）报文，包括收件人的邮件地址，RCPT命令的作用是 ：
先弄清接收方系统是否已经准备好接收邮件的准备，然后才发送邮件，这样做视为了避免浪费通信资源，不至于发送了很长的邮件以后才知道是因地址错误 。

4.服务器响应代码250或其他适当的代码。

5.客户发送DATA报文对报文的传送进行初始化，DATA命令表示要开始传送邮件的内容了。

6.服务器响应代码"354 Start mail input: end with <CRLF>.<CRLF>"或其他适当的报文（如421
服务器不可用，500 命令无法识别）。

7.客户用连续的行发送报文的内容。每一行的行结束时输入 <CRLF>.<CRLF> ，即回车换行.回车换行，表示邮件内容结束。

8.服务器响应代码（250 请求命令完成）或其他适当的代码。

值得注意的是：虽然SMTP使用TCP连接试图使邮件的传送可靠，但它并不能保证不丢失邮件。也就是说，使用SMTP传送邮件只能说可以可靠地传送接收方的邮件服务器，在往后的情况就不知道了。接收方的邮件服务器也许会出故障，使收到的服务器全部丢失（在收件人读取信件之前）。

  

 **终止连接**

在报文传送成功后，客户就终止连接。包括如下步骤：

1.客户发送QUIT命令。

2.服务器响应221（服务关闭）或其他代码。

在连接终止阶段后，TCP连接必须关闭。

注：本文属“合天智汇”原创奖励文章，未经允许，禁止以任何形式转载！


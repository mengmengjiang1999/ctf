作者：[红发香克斯](https://bbs.ichunqiu.com/space-uid-294673.html?from=beef)

开篇之前一直想借助一台高性能PC利用VMWare组建一个攻防网络，之前有一贴写过找到了一个软路由系统，就是可以在VMWare中使用的路由器操作系统，那个系统还挺常用，上次帖子写到了安装和连接，没写后续的IP配置等等，上篇的地址：[https://bbs.ichunqiu.com/thread-33583-1-1.html](https://bbs.ichunqiu.com/thread-36817-1-1.html?from=beef)，这节给大家讲讲如何配置和挖洞的思路，首先上这个路由器软件的下载地址[https://mikrotik.com/download](https://bbs.ichunqiu.com/thread-36817-1-1.html?from=beef)，因为公司要做一个工控相关缓冲区溢出的课件，所以我找到了这个路由器，因为我看到它在SMB协议上有个缓冲区溢出，好像刚公开的。

设置IP地址

路由器使用VM安装以后使用你并不知道IP地址，它也没有IP地址，所以你只能通过MAC地址访问，默认用户名为admin，密码为空，详细请看这个文章[https://bbs.ichunqiu.com/thread-33583-1-1.html](https://bbs.ichunqiu.com/thread-36817-1-1.html?from=beef)，

查看网卡信息

打开路由器并登陆，然后在shell中使用/interface pri，然后看到两块网卡wlan和lan

![image.png](https://image.3001.net/images/20180330/15223801961910.png!small)  

这两块网卡，应该是一个设置公网IP，一个设置内网IP的，路由器吧公网的数据包转发到内网IP，内网的IP就是你内网的IP段

winbox设置IP

打开winbox以后，输入Mac地址，用户名输入admin，密码为空，连接VMWare里的软路由系统

![image.png](https://image.3001.net/images/20180330/15223802069274.png!small)  

点击上图红框中的按钮，打开快速设置页面，然后需要配置两个网卡的IP地址和网关，一个是wlan的IP和网关，一个是lan的IP和网关，

![https://bbs.ichunqiu.com/thread-36817-1-1.html?from=beef](https://image.3001.net/images/20180330/15223802187223.png!small)  

这边插说两句路由模式和桥接模式，之前计算机网络没做过实验，所以对这个不在行，在网上找了一些资料，感觉这个比较浅显易懂

[https://baijiahao.baidu.com/s?id ...
r=spider&for=pc](https://bbs.ichunqiu.com/thread-36817-1-1.html?from=beef)

为了我本地的IP可以访问路由器，我就设置为一个网段而且IP为静态IP，这边Internet的IP设置成192.168.1.123，本地网络设置成为另外一个段，我的目的是要能访问它，然后挖它的漏洞，设置好以后点击OK保存

扫描路由器

刚才已经设置好了，下面要用nmap扫一下，看通不通，还有就是收集一下端口信息，这是基本流程，如果你网络不通那你咋收集端口信息，如果你没收集端口信息那你咋挖漏洞？下面对扫描结果上图

![image.png](https://image.3001.net/images/20180330/15223802299689.png!small)  

结果很称心，开着21 22 23 80 8291
2000等端口，其中8291是咱们使用winbox连接路由的端口，2000看着像测试路由器带宽的端口，80端口很surprise！因为路由器一般都有web服务，而这个只有十几M的系统居然有web服务，打开看一下

![image.png](https://image.3001.net/images/20180330/1522380236828.png!small)  

![image.png](https://image.3001.net/images/20180330/15223802516111.png!small)  

一般路由器中的功能该有的都有了，有DNS，DHCP等等，麻雀碎小，五脏俱全，亮瞎我的双眼，还可以远程连接路由器控制台

![image.png](https://image.3001.net/images/20180330/15223802609943.png!small)  

Fuzz一下FTP

对于这个新发布的系统，我没看到SMB，所以网上的那个漏洞我没法搞，但是新系统可能就有0day也说不定，所以我准备对它开放的协议进行FUZZ一下，先拿它的FTP开刀

打开metasploit，搜索fuzz，找到ftp_pre_post，常见的RHOST，RPORT这些不用讲

![image.png](https://image.3001.net/images/20180330/15223802702700.png!small)  

红框中有几个重点，其中USER参数是ftp用户名，PASS是密码，为啥要用正确的用户名密码呢，和ftp协议有关，有的FTP命令你只有登录成功才能使用，如果你填错误的用户名和密码，那么登录不成功，只能fuzz一下user和pass这俩命令，如果要深入就必须登录以后fuzz，所以这边用户名和密码设置为正确的，用户名设‘admin’，密码设为''，注意设置密码使用的是set
PASS
""，这样密码就为空，就可以登录了，然后是stepsize参数，这个是设置数据增长的步长，比如第一次发送的数据包是100个字符，你设置stepsize为200的话，那第二次发的数据包就是300个字符，往后每次加200个

设置好以后执行exploit

![image.png](https://image.3001.net/images/20180330/15223802798014.png!small)  

如果路由器有报错的信息日志啥的，你可以在http的控制台里查看，比如你fuzz的时候用户名和密码不对，就会在控制台中报错

![image.png](https://image.3001.net/images/20180330/15223802874563.png!small)  

经过我一下午的fuzz奋斗努力，hia hia hia
，不找个0day---------------------------------------------------------
也是正常的，没错，特么的我fuzz了一下午，这个路由器的ftp连个小毛病都没找到，看来得转移阵地

\--------------------------------------------------------------------------------------------------------------------------------------------华丽的分割线

文章结束，撒扬娜拉

##  

  


## **一、** **概述** ****

**2019年8月30日，安洵信息星际实验室蜜网捕获到利用Redis未授权访问漏洞的攻击行为。Redis因配置不当可以导致未授权访问，被攻击者恶意利用。**

当前流行的针对Redis未授权访问的一种新型攻击方式，在特定条件下，如果Redis以root身份运行，黑客可以给root账户写入SSH公钥文件，直接通过SSH登录受害服务器，可导致服务器权限被获取和数据删除、泄露或加密勒索事件发生，严重危害业务正常服务。
部分服务器上的Redis 绑定在 0.0.0.0:6379，并且没有开启认证（这是Redis
的默认配置），以及该端口可以通过公网直接访问，如果没有采用相关的策略，比如添加防火墙规则避免其他非信任来源 ip 访问等，将会导致 Redis
服务直接暴露在公网上，可能造成其他用户可以直接在非授权情况下直接访问Redis服务并进行相关操作。安全团队对此次事件进行了详细的样本分析，并给出预防及修复建议。

##  **二、** **攻击原理** ****

攻击原理非常简单 –
攻击者在内存中设置一个键/值对，然后将其保存到磁盘中的文件中，该位置将强制文件运行（例如/etc/crontabs，/var/spool/cron/crontab等）。

##  **三、样本分析** ****

攻击者先尝试对不设置密码的redis或者若密码的redis服务器进行连接,然后执行脚本,创建定时任务。

![1.png](https://image.3001.net/images/20190904/1567591255_5d6f8b5788e8a.png!small)  

**脚本** **pm.sh** **分析**

通过<http://pm.ipfswallet.tk/pm.sh>下载并执行脚本，该脚本会检查并从<http://pm.ipfswallet.tk/pc>下载可执行文件”pc”。

 **可执行程序** **pc** **分析** ****

该可执行文件未进行加壳处理，主要包括下载挖矿程序、配置定时任务、关闭系统防火墙及相关进程等功能。

程序首先通过<http://pm.ipfswallet.tk/miner2>下载挖矿程序”miner2”，并赋予其相应权限，使其开始执行。

![3.png](https://image.3001.net/images/20190904/1567591373_5d6f8bcd231d1.png!small)

之后程序开始修改系统配置文件、关闭相关进程并配置定时任务：  
![4.png](https://image.3001.net/images/20190904/1567591409_5d6f8bf1591f8.png!small)![5.png](https://image.3001.net/images/20190904/1567591409_5d6f8bf18728c.png!small)

**挖矿程序** **miner2** **分析：**

miner2程序内部实际包含一个xmrig挖矿程序以及攻击者的相关信息。

![6.png](https://image.3001.net/images/20190904/1567591453_5d6f8c1dd9e5e.png!small)

![7.png](https://image.3001.net/images/20190904/1567591495_5d6f8c4739807.png!small)

同时程序会在宿主机配置ssh公钥，攻击者可以远程访问服务器并将其接管。

![8.png](https://image.3001.net/images/20190904/1567591522_5d6f8c62a0118.png!small)

![9.png](https://image.3001.net/images/20190904/1567591544_5d6f8c7889fe5.png!small)

经过对程序数据区域的分析，得到攻击者的矿池地址以及钱包信息。

 **矿池地址：**

> stratum+tcp://pool.cpuminerpool.com:443
>
> stratum+tcp://pool.minexmr.com:80
>
> stratum+tcp://pool.minexmr.com:5555

 **钱包地址：**

>
> 4AM2tbxHyDKLY2SLvwSoJ9S61mCdh8NXV6QZJQ7PVxm4T8ieufvW5zwJ84p8hS5Zij1DNeP195oBgPMBd8Gzmoj962Fjw1a

![10.png](https://image.3001.net/images/20190904/1567591589_5d6f8ca543348.png!small)

![11.png](https://image.3001.net/images/20190904/1567591608_5d6f8cb85a950.png!small)

##  **四、IOC**

 **攻击者IP** **：**

> 220.194.237.43 河北唐山
>
> 104.28.30.36 美国

 **攻击者URL** **：**

> [http://***.***wallet.tk/pm.sh]()
>
> [http://***.***wallet.tk/pc]()
>
> [http://***.***wallet.tk/miner2]()

 **样本MD5** **：**

> fec85360ad9b3d894f958c4ad1aabb9c
>
> c1c516250b1b5e7cbaaf00b9f38e197d

## 五、预防与修复建议 ****

 **预防建议**

> (1)、确保系统与应用程序及时下载更新为官方提供的最新补丁；
>
> (2)、禁止使用弱口令密码；
>
> (3)、定期检查服务器异常，如CPU持续占用高、磁盘异常情况；
>
> (4)、Redis不要监听在危险IP上，如果有请加网络防火墙规则控制；
>
> (5)、LINUX 系统下Redis不要用Root用户身份来启动。Windows系统下不要以system权限运行

 **修复建议**

> (1)、断网、备份重要的crontab，关闭或删除定时任务：systemctl stop crontab或 rm -rf /etc/cron.d/*；
>
> (2)、锁定crontab中的恶意文件；
>
> (3)、查看并杀掉病毒进程

 ***本文作者：安洵信息，转载请注明来自FreeBuf.COM**


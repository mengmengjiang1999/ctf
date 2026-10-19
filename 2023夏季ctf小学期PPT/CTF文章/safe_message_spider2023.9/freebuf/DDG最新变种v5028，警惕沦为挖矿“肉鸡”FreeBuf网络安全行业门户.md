**近期，深信服安全团队捕获到DDG挖矿木马最新变种v5028，和之前的变种v5023相比，新版本的DDG挖矿木马更新了C
&C地址及挖矿地址，同时弃用了传统的i.sh驻留方式。**

经深信服安全云脑数据统计，该木马在短短一个月时间已有大量拦截数据，且每日攻击次数还呈递增的趋势。

## 威胁数据

根据云脑数据显示，截止2020年6月20号，全网已监测到近大量来自DDG v5028变种的流量攻击。

![1592824629_5ef09335bbfa3.png!small](https://image.3001.net/images/20200622/1592824629_5ef09335bbfa3.png!small)

攻击数据拦截地区的分布大致如下，其中天津和北京的拦截数据量最大。

![1592824698_5ef0937a1f291.png!small](https://image.3001.net/images/20200622/1592824698_5ef0937a1f291.png!small)

## 一、版本简介

自2020年开始，DDG已开始启用v5版本号，从以往的Memberlist开源P2P通信方式改为了自研的P2P通信方式。

在v5023中有较大更新，木马会在/var/lib/或/usr/local/下生成随机名目录，用于存放P2P通信中获取到的文件及数据，以及新增jobs配置文件来进行一些较高级的清除异己操作。

本次v5028的更新在于弃用了i.sh的驻留方式。

## 二、木马分析

中毒后的主机现象如下，存在一个挖矿进程playstation及随机名母体进程cqhzxp。

![1592824742_5ef093a66b6e6.png!small](https://image.3001.net/images/20200622/1592824742_5ef093a66b6e6.png!small)

主机上无发现恶意定时任务，通过ssh特征匹配确认该木马为DDG家族。

![1592824768_5ef093c0f38f4.png!small](https://image.3001.net/images/20200622/1592824768_5ef093c0f38f4.png!small)

本次DDG家族为最新的5028版本，其恶意组件在/var/lib/的一个随机名目录下。

![1592824785_5ef093d116d4e.png!small](https://image.3001.net/images/20200622/1592824785_5ef093d116d4e.png!small)

重定向域名中，较5025版本新增了[www.minpop.com](http://www.minpop.com/)，经过威胁关联确认这是一个名为shellbot的perl恶意软件。

![1592824823_5ef093f7396dd.png!small](https://image.3001.net/images/20200622/1592824823_5ef093f7396dd.png!small)

借助P2P僵尸网络，DDG挖矿木马运行后会随机从其他失陷主机中拉取slave或jobs配置文件，slave里配置的是攻击组件的信息，jobs配置的是清除异己家族的信息。

![1592824841_5ef0940968fd1.png!small](https://image.3001.net/images/20200622/1592824841_5ef0940968fd1.png!small)

slave配置文件的核心内容如下，使用了2个挖矿程序，MD5分别为cfde21dc48f06da5688e81b1cdeb2b3e和d146612bed765ba32200e0f97d0330c8，新增了2个矿池地址，50.116.37.115和134.209.249.49。同时，slave配置中去掉了i.sh部分的内容，也说明5028变种已弃用i.sh的传播&驻留方式。

![1592824858_5ef0941a42a9a.png!small](https://image.3001.net/images/20200622/1592824858_5ef0941a42a9a.png!small)

使用开源工具<https://github.com/0xjiayu/DDGBotnetTracker>解密出目前失陷的主机列表如下。

![1592824879_5ef0942f3b02e.png!small](https://image.3001.net/images/20200622/1592824879_5ef0942f3b02e.png!small)

代码部分没有太大变化，新增了killLowCpuMiner函数，用于清除一些智能挖矿的进程。

![1592824893_5ef0943d18787.png!small](https://image.3001.net/images/20200622/1592824893_5ef0943d18787.png!small)

传播方式还是沿用了以下4个漏洞进行攻击：

> 1.SSH密码暴破
>
> 2.Redis未授权访问漏洞
>
> 3.Nexus Repository Manager 3 RCE漏洞(CVE-2019-7238)
>
> 4.Supervisord RCE漏洞(CVE-2017-11610)

![1592824938_5ef0946a63ee4.png!small](https://image.3001.net/images/20200622/1592824938_5ef0946a63ee4.png!small)

## 三、加固建议

> 1、Linux恶意软件以挖矿为主，一旦主机被挖矿了，CPU占用率高，将会影响业务，所以需要实时监控主机CPU状态。
>
> 2、定时任务是恶意软件惯用的持久化攻击技巧，应定时检查系统是否出现可疑定时任务。
>
> 3、部分企业还存在ssh弱密码的现象，应及时更改为复杂密码，且检查在/root/.ssh/目录下是否存在可疑的authorized_key缓存公钥。
>
> 4、定时检查Web程序是否存在漏洞，特别关注Redis未授权访问等RCE漏洞。

## 四、IOC

### C&C地址

> 68.183.186.25

### 矿池地址

> 50.116.37.115:443
>
> 178.128.108.158:443
>
> 134.209.249.49:443
>
> 103.195.4.139:443
>
> 68.183.182.120:443

### 样本MD5

> 17028FABB703AD98E44691DEDC7C3D1F
>
> cfde21dc48f06da5688e81b1cdeb2b3e
>
> d146612bed765ba32200e0f97d0330c8

## 五、参考链接

> <https://blog.netlab.360.com/ddg-upgrade-to-new-p2p-hybrid-model/>
>
> [https://www.freebuf.com/column/232333.html](../column/232333.html)


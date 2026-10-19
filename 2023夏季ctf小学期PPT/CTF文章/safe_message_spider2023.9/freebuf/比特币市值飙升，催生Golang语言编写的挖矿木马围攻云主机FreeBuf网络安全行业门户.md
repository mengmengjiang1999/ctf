## 一、背景

受近期比特币暴涨带动数字虚拟币整体市值飙升影响，挖矿木马十分活跃。腾讯安全威胁情报中心检测到利用Redis未授权访问漏洞直接写入计划任务，下载用golang语言编写的挖矿木马下载器superman，根据挖矿算力推测该团伙已控制约1万台失陷系统进行门罗币挖矿。​

腾讯安全近期已捕获较多利用golang语言编写的各类脚本木马，这些木马利用多个不同linux服务器组件的高危漏洞或弱密码入侵云服务器挖矿。对这些挖矿木马进行分析溯源，发现分属不同的黑产团伙控制，有点“千军万马一窝蜂携漏洞武器弱口令武器抢占云主机挖矿淘金”的意思。腾讯安全专家建议政企机构安全运维人员及时修补漏洞，排查弱口令，避免服务器沦为黑产控制的肉鸡。

在本例中，部分政企机构使用Redis时，由于没有对redis进行良好的配置，如使用空口令或者弱口令等，导致攻击者可以直接访问redis服务器，并可以通过该问题直接写入计划任务甚至可以直接拿到服务器权限。

 **腾讯安全专家推荐的修复建议** ：

  1. 针对未配置redis密码访问的，需要对其进行配置添加用户和密码访问。针对弱口令则需要使用强密码。
  2. 如非必须，不对外开放redis端口，如需要对外开放服务则正确配置好ACL策略。

 **清理利用漏洞入侵的挖矿木马** ：

  1. 清除计划任务中的8m.sh相关条目；
  2. 在确认JavaUpdate和mysqlserver进程异常后，将其kill掉；
  3. 删除/var/tmp/下的.system-python3.8-Updates和.Javadoc 文件夹。

针对supermanminer系列挖矿木马的活动，腾讯安全各产品均已响应拦截。

![](https://image.3001.net/images/20210111/1610358167_5ffc1d97a620f6094c86a.png!small)

## 二、详细分析

在使用redis应用时没有配置好访问策略导致攻击者可以利用弱口令或者空口令直接访问redis应用，并通过该应用直接向系统写入计划任务或者通过写入ssh公钥文件直接控制服务器。

通过未授权直接写入计划任务

![](https://image.3001.net/images/20210111/1610358189_5ffc1dad1a6dc061c5548.png!small)

在/var/spool/cron/root可以看到如下内容

![](https://image.3001.net/images/20210111/1610358198_5ffc1db6541a0b1f62c1f.png!small)

通过计划任务到pastebin下载脚本并执行

下载的脚本内容用base64进行编码

![](https://image.3001.net/images/20210111/1610358207_5ffc1dbfa16d81d496ce5.png!small)

解码后的内容：

![](https://image.3001.net/images/20210111/1610358216_5ffc1dc89ab62f77ffcb7.png!small)

该脚本主要功能是判断当前主机进程中是否有包含/var/tmp/.system-python3.8-Updates路径，然后指定站点下载superman文件，命名为f存放到/var/tmp/目录下，运行后将该文件删除。

superman是一个go编写的下载器，主要功能是下载核心挖矿程序xmrig及配置文件，并通过重新下载superman，并将其命名为mysqlserver，写入计划任务的方式进行持久化操作。

在运行superman后会写入计划任务。

![](https://image.3001.net/images/20210111/1610358228_5ffc1dd4a13d706dabb12.png!small)

其中python3.8m.sh的内容为：

![](https://image.3001.net/images/20210111/1610358240_5ffc1de02987b9e5ddde2.png!small)

脚本中的将mysqlserver是将superman下载后重命名，并将其存放在.system-python3.8-updates路径下。

通过流量分析发现，木马会频繁请求www.hellomeyou.cyou，且域名对应的IP一直在变化。该网站主要是查询在NameSilo注册的域名的whois信息等。

![](https://image.3001.net/images/20210111/1610358251_5ffc1deb701e9096143ea.png!small)

通过查看网站源码，发现源码中嵌入了一些内容，包括xmirg下载链接，矿池配置，superman下载链接及文件大小等。

![](https://image.3001.net/images/20210111/1610358260_5ffc1df4295ba778263e0.png!small)

通过查询域名相关信息该域名与namesilo属于同一组织，判断应该是hellomeyou这个网站被攻击后，在网站中嵌入了这些内容。

通过对superman文件分析，发现其通过正则表达式的方式匹配相应内容，分别匹配superman下载的url，xmrig下载路径，文件大小及矿池配置内容。

![](https://image.3001.net/images/20210111/1610358270_5ffc1dfe5fdc6b3fef865.png!small)

Superman文件通过github下载xmrig文件，并将其命名为JavaUpdate，并将其存放在/var/tmp/.Javadoc/路径下。同时通过匹配到的矿池内容修改相应的config.json文件。

![](https://image.3001.net/images/20210111/1610358279_5ffc1e07b7dfa2e3a83f7.png!small)

Congfig文件内容：

![](https://image.3001.net/images/20210111/1610358290_5ffc1e121db32351d08b6.png!small)

其中挖矿使用矿池：

> 54.37.7.208:443（xmrpool.eu）

挖矿使用钱包：

>
> 88XEAsyefa9DyzyMJSdcEUR9PJPphWrSp632D2ia83zuJHLKDBxQZ1iDSVY8MspBoFiqdZdQupm4xBasSkahdfdXRuUU1j6

根据其钱包算力223Kh/s推算，该挖矿团伙已控制约1万台电脑进行挖矿。

![](https://image.3001.net/images/20210111/1610358303_5ffc1e1f6245bf0a61b2f.png!small)

Superman采用Go语言编写，除了启动挖矿程序之外，还具有下载文件、执行任意程序、执行远程命令、在线升级、安装crontab定时任务等功能。

![](https://image.3001.net/images/20210111/1610358314_5ffc1e2a2d1170858f913.png!small)

## IOCs

 **URL**

> hxxp://138.124.180.20:8080/superman
>
>
> hxxps://github.com/xmrig/xmrig/releases/download/v6.6.1/xmrig-6.6.1-linux-x64.tar.gz
>
> hxxps://pastebin.com/raw/xnxWdRJ8
>
> hxxp://www.hellomeyou.cyou/

 **MD5**

> JavaUpdate
>
> a66c6c00d09529066b03070646127286
>
> superman/mysqlserver
>
> 96dc8dcd5bf8f6e62c3ce5219e556ba3

 **矿池地址**

> xmrpool.eu

 **钱包地址**

>
> 88XEAsyefa9DyzyMJSdcEUR9PJPphWrSp632D2ia83zuJHLKDBxQZ1iDSVY8MspBoFiqdZdQupm4xBasSkahdfdXRuUU1j6

## 参考链接：

https://paper.seebug.org/1440/


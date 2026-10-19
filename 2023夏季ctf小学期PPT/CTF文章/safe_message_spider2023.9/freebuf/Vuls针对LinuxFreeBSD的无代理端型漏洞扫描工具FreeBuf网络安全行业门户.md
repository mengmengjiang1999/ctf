***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![Vuls](https://image.3001.net/images/20190320/1553047465_5c919fa9819f4.png!small)

**今天给大家介绍的是一款名叫Vuls的漏洞扫描工具，该工具采用Go语言编写，可帮助研究人员在无需安装任何代理工具的情况下实现对Linux/FreeBSD的漏洞扫描。**

![２.png](https://image.3001.net/images/20190320/1553047477_5c919fb53930a.png!small)

## 工具演示视频

视频地址：<https://asciinema.org/a/3y9zrf950agiko7klg8abvyck>

![Vuls](https://image.3001.net/images/20190320/1553047533_5c919fedb6fbb.png!small)

## 工具介绍

对于系统管理员来说，每天的安全漏洞扫描以及软件更新任务肯定是非常繁重的．为了避免产品生产环境没有及时更新，很多管理员不会选择使用安装管理器所提供的自动更新选项，而是选择进行手动更新．这样就会导致下列问题出现：

> 1\. 系统管理员不可能持续关注NVD(国家漏洞数据库)或类似数据库中更新的新漏洞；
>
> 2\. 如果服务器端安装了大量的软件，那么系统管理员也不可能手动监控所有这些软件；
>
> 3\. 对服务器端执行新型安全漏洞扫描和分析的花销非常的大

因此，Vuls这款工具就应运而生了，Vuls拥有以下几种特性：

> 1\. 一旦数据库中新增了跟自己系统相关的漏洞时，告知管理员；
>
> 2\. 服务器在受到漏洞影响时，通知管理员；
>
> 3\. 自动执行漏洞检测，以防止管理员忽略某些应用；
>
> 4\. 使用CRON或其他方法自动生成常规漏洞报告，以帮助管理员更好地管理漏洞

![Vuls](https://image.3001.net/images/20190320/1553047552_5c91a00070305.png!small)

## 主要功能

### 扫描Linux/FreeBSD服务器中的任意漏洞(支持主流Linux/FreeBSD平台)

-Alpine,Ubuntu, Debian, CentOS, Amazon Linux, RHEL, Oracle Linux, SUSE Enterprise Linux和Raspbian, FreeBSD;

-Cloud,on-premise, Docker

### 高质量的漏洞扫描

Vuls使用了多款漏洞数据库:

> [NVD](https://nvd.nist.gov/)
>
> [JVN(日本)](http://jvndb.jvn.jp/apis/myjvn/)

 **OVAL**

> [RedHat](https://www.redhat.com/security/data/oval/)
>
> [Debian](https://www.debian.org/security/oval/)
>
> [Ubuntu](https://people.canonical.com/~ubuntu-security/oval/)
>
> [SUSE](http://ftp.suse.com/pub/projects/security/oval/)
>
> [Oracle Linux](https://linux.oracle.com/security/oval/)
>
> [Alpine-secdb](https://git.alpinelinux.org/cgit/alpine-secdb/)
>
> [Red Hat安全公告](https://access.redhat.com/security/security-updates/)
>
> [Debian安全漏洞追踪库](https://security-tracker.debian.org/tracker/)

支持命令(yum,zypper, pkg-audit)

RHSA/ALAS/ELSA/FreeBSD-SA

> [Exploit Database](https://www.exploit-db.com/)
>
> [US-CERT](https://www.us-cert.gov/ncas/alerts)
>
> [JPCERT](http://www.jpcert.or.jp/at/2019.html)

### 快速扫描和深度扫描

快速扫描：

> -无需root权限或任何依赖组件;
>
> -几乎不会给目标服务器增加任何负载;
>
> -支持断网环境下的离线扫描模式(Red Hat,CentOS, OracleLinux, Ubuntu, Debian)

快速Root扫描：

> -使用root权限进行扫描;
>
> -几乎不会给目标服务器增加任何负载;
>
> -使用yun-ps检测受影响的进程(RedHat, CentOS, Oracle Linux和Amazon Linux);
>
> -检测已更新但未重启的进程(Debian和Ubuntu);
>
> -支持断网环境下的离线扫描模式(Red Hat,CentOS, OracleLinux, Ubuntu, Debian)

### 深度扫描

> -使用root权限进行扫描;
>
> -通过解析漏洞数据库中的CVE编号来检测服务器上的产品漏洞以及更新情况;
>
> -某些情况下会给目标服务器增加一定的负载

### 远程扫描和本地扫描

远程扫描

> -用户需搭建一台设备,并通过SSH与远程目标主机进行连接后方可进行扫描操作;

本地扫描

> -如果你不想使用中央Vuls服务器来连接每一台目标服务器的话(通过SSH),你可以使用Vuls的本地模式;

## Stargaers增长变化

![６.png](https://image.3001.net/images/20190320/1553047650_5c91a0627de95.png!small)

## 项目地址

Vuls：【[GitHub传送门](https://github.com/sensepost/DNS-Shell)】

## 许可证协议

本项目遵循[GNU](https://github.com/future-architect/vuls/blob/master/LICENSE)许可证协议。

 *** 参考来源：[future-architect](https://github.com/future-architect/vuls)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


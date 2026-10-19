![](https://image.3001.net/images/20190827/1566886202_5d64c93a9deb2.jpg!small)

##  工具概述

**SUDO_KILLER这款工具可以帮助我们通过多种渠道利用SUDO来在Linux环境下实现提权。该工具能够识别目标操作系统版本，并发现环境中sudo规则的错误配置、安全漏洞，以及不安全的代码，而研究人员就可以利用SUDO_KILLER所提供的功能来将权限提升为ROOT权限。**

SUDO_KILLER将提供一份命令列表或本地漏洞利用信息，以帮助研究人员实现提权。需要注意的是，该工具本身并不会执行任何形式的漏洞利用操作，漏洞利用操作需要研究人员手动执行。

##  功能介绍

SUDO_KILLER可以执行的检测以及功能包括：

> 1、错误配置
>
> 2、危险代码
>
> 3、Sudo漏洞版本（CVE）
>
> 4、危险环境变量
>
> 5、凭证收集
>
> 6、识别可执行脚本的目录（可写）
>
> 7、可替换的代码
>
> 8、识别错误脚本

##  工具使用

###  参考样例：

    
    
    ./sudo_killer.sh-c -r report.txt -e /tmp/

###  可用参数：

    
    
    -k : 关键词 
    
    -e : 导出路径 (export/etc/sudoers)
    
    -c : 使用CVE检测相应的sudo版本
    
    -s : 提供用户密码进行sudo检测
    
    -r : 需保存的输出报告名称
    
    -h : 查看帮助信息

###  CVE检测

如需更新CVE漏洞数据库，请运行这个更新脚本：./cve_update.sh。

##  提供密码（重要）

当你需要输入密码来运行命令“sudo -l“时，如果你无法使用-s参数来提供有效密码，那么脚本将无法正常工作。

##  Docker-漏洞测试环境

我们建议大家使用Docker镜像来作为工具的测试环境，镜像中已包含多个跟SUDO使用相关的漏洞以及错误配置。

![](https://image.3001.net/images/20190827/1566886236_5d64c95c1239b.png!small)

Docker镜像可以直接在Docker
Hub上获取，并且在每次重构之后都可以自动更新：【[点我下载](https://hub.docker.com/r/th3xace/sudo_killer_demo)】。

1、从Docker Hub获取SUDO_KILLER_DEMO这个Docker镜像：

    
    
    service docker start
    
        docker pull th3xace/sudo_killer_demo
    
        docker run --rm -it th3xace/sudo_killer_demo

2、使用Dockerfile构建镜像：

    
    
    service docker start
    
        git clone <https://github.com/TH3xACE/SUDO_KILLER.git>
    
        cd SUDO_KILLER
    
        docker build -t th3xace/sudo_killer_demo .
    
        docker run --rm -it th3xace/sudo_killer_demo

##  演示样例

下面是我们给出的部分工具使用场景以及参考样例：【视频集】（需科学上网）

视频一：【[Docker-设置漏洞环境](https://youtu.be/Q8iO9mYrfv8)】

![](https://image.3001.net/images/20190827/1566886262_5d64c97681779.jpg!small)

视频二：【[场景1-CVE漏洞利用](https://youtu.be/CpLJ9kY6eig)】

![](https://image.3001.net/images/20190827/1566886267_5d64c97bb8b88.jpg!small)

视频三：【[场景2-危险代码](https://youtu.be/cELFVC6cTyU)】

![](https://image.3001.net/images/20190827/1566886271_5d64c97f95573.jpg!small)

视频四：【[场景3-错误配置（通配符）](https://youtu.be/rKA55mis8-4)】

![](https://image.3001.net/images/20190827/1566886275_5d64c983895cb.jpg!small)

视频五：【[场景4-错误配置（过度权限）](https://youtu.be/s1KK6go1nGY)】

![](https://image.3001.net/images/20190827/1566886282_5d64c98a394f4.jpg!small)

视频六：【[场景5-错误配置（错误脚本）](https://youtu.be/zsxvsSYz4as)】

![](https://image.3001.net/images/20190827/1566886286_5d64c98eea39b.jpg!small)

视频七：【[场景6-凭证收集](https://youtu.be/i7ixN0sv2Qw)】

![](https://image.3001.net/images/20190827/1566886298_5d64c99a0ca03.jpg!small)

视频八：【[场景7-环境变量利用](https://youtu.be/sGd8KW_eqhw)】

![](https://image.3001.net/images/20190827/1566886302_5d64c99e2109a.jpg!small)

##  项目地址

SUDO_KILLER：【[GitHub传送门](https://github.com/TH3xACE/SUDO_KILLER)】

 ***
参考来源：[TH3xACE](https://github.com/TH3xACE/SUDO_KILLER)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


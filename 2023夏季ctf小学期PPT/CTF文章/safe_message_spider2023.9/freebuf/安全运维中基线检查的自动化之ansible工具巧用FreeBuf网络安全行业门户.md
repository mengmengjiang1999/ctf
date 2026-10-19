**i春秋作家：yanzm**

**原文来自：[安全运维中基线检查的自动化之ansible工具巧用](https://bbs.ichunqiu.com/thread-46896-1-1.html?from=beef)**

前几周斗哥分享了基线检查获取数据的脚本，但是在面对上百台的服务器，每台服务器上都跑一遍脚本那工作量可想而知，而且都是重复性的操作，于是斗哥思考能不能找到一种方法来实现自动下发脚本，批量执行，并且能取回执行的结果。对比参考学习某些开源的平台都有这么一个特点就是需要安装客户端(说白了就是类似后门木马的插件)，客户端的兼容性适应问题不说，而且全部服务器都要装相应的客户端，明显超出斗哥预期的轻量级的实现自动化的初衷，但是办法总比困难多作为老板的省钱小能手身轻如燕的斗哥还真找到一个工具无需安装客户端就能实现自动化运维的工具。

话不多说，斗哥决定先给大家演示一下ansible如何实现基线检查脚本的自动下发，批量执行和结果取回，然后再进一步学习这款工具的安装和使用，以及后期的自动化思路。

0x01 效果演示

环境说明:

主控端：192.168.159.55

节点：192.168.159.92、192.168.159.94

确保主控端和节点的连通性，主控端/tmp目录下已创建好需执行的基线检查脚本。

  

#!/bin/bash

#主控端生成密钥

ssh-keygen -t rsa

#将节点加入/etc/ansible/hosts，增加的可参照下面的格式添加

echo "[web]" >> /etc/ansible/hosts

echo "192.168.159.92 ansible_ssh_pass=root" >> /etc/ansible/hosts

echo "192.168.159.94 ansible_ssh_pass=root" >> /etc/ansible/hosts

#记录节点密钥，新增节点参照下面的格式进行添加

ssh-keyscan 192.168.159.92 >> /root/.ssh/known_hosts

ssh-keyscan 192.168.159.94 >> /root/.ssh/known_hosts

#创建playbook

touch /etc/ansible/push-ssh.yml

echo "---" >> /etc/ansible/push-ssh.yml

echo "- hosts: web" >> /etc/ansible/push-ssh.yml

echo " user: root" >> /etc/ansible/push-ssh.yml

echo " tasks:" >> /etc/ansible/push-ssh.yml

echo " - name: ssh-key-copy" >> /etc/ansible/push-ssh.yml

echo " authorized_key: user=root
key=\"{{lookup('file','/root/.ssh/id_rsa.pub')}}\"" >> /etc/ansible/push-ssh.yml

echo " tags:" >> /etc/ansible/push-ssh.yml

echo " - sshkey" >> /etc/ansible/push-ssh.yml

#执行playbook

ansible-playbook /etc/ansible/push-ssh.yml

#测试

ansible web -m ping

#主控端创建脚本，在节点执行

mkdir /tmp/check

ansible web -m script -a "/tmp/linux_centos7.sh"

#ansible web -m raw -a "ls /tmp/check"

#取回脚本执行结果，保存在/tmp/check/目录下

result=(`ansible web -m raw -a "ls /tmp/check" | grep dict | awk '{print
$1}'`)

for i in ${result[@]}

do

ansible ${i:13:14} -m raw -a "cat /tmp/check/$i" >> /tmp/check/$i

done

  

执行自动化脚本demo，linux_centos7.sh为创建在主控端的基线检查脚本：

![image.png](https://image.3001.net/images/20181022/1540190869_5bcd7295212f4.png!small)  

脚本执行结束即可在本地的/tmp/check目录下查看到节点的执行结果：

![image.png](https://image.3001.net/images/20181022/1540190874_5bcd729a3681f.png!small)  

上述的过程，在面对众服务器节点的时候可以省去很多工作量，是不是感觉一下清爽了许多。

but

当节点没有python的情况下，上述脚本是不适用的哦，会出现如下报错提示。

  
![image.png](https://image.3001.net/images/20181022/1540190887_5bcd72a7ec3e9.png!small)  

这里先卖个关子，如何实现节点没有安装python的情况下的批量化请继续往下看，斗哥决定先带领大家先来掌握批量脚本涉及的相关知识，工欲善其事必先利其器。

0x02 ansible介绍以及安装

Ansible是一款为类Unix系统开发的自由开源的配置和自动化工具，基于Python开发，集合了众多运维工具（puppet、cfengine、chef、func、fabric，ps：反正斗哥是没用过啦）的优点，同时ansible最大的优点是不需要在节点中安装任何客户端，它使用SSH来和节点进行通信。
ansible是基于模块工作的，比如常用的script、command、shell、copy、fetch、raw等模块，同时ansible还支持自定义模块和playbook以适应更丰富的自动化运维场景的需求（得益于python的强大基因）。

step1：准备工作

主控端：centos7.5（Red Hat Enterprise Linux，CentOS，Fedora和Ubuntu等发行版都默认安装了python
2.X的解释器，pip不一定是默认安装，如果有安装也需要更新到最新版），具体主控端安装环境要求如下：

![image.png](https://image.3001.net/images/20181022/1540190894_5bcd72ae412bc.png!small)  

ansible的主控端只能安装在类unix的操作系统上，其他发行版的linux安装可以详见ansible中文权威指南-安装管理主机，本文的安装方法仅适用于centos系统。

step2：下载和安装EPEL仓库

[root[@root](https://bbs.ichunqiu.com/home.php?mod=space&uid=54) tmp]# wget
[http://dl.fedoraproject.org/pub/ ...
latest-7.noarch.rpm](http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm)

[root@root tmp]# rpm -ivh epel-release-latest-7.noarch.rpm

  
![image.png](https://image.3001.net/images/20181022/1540190901_5bcd72b5975be.png!small)  

step3：安装Ansible以及查看对应的版本

[root@root tmp]# yum -y install ansible

[root@root tmp]# ansible –version

![image.png](https://image.3001.net/images/20181022/1540190910_5bcd72beb398c.png!small)  

到step3
ansible就已经安装完毕，如果安装在虚拟机的强烈建议这里可以打个快照方便后续的测试调试。step4和step5步骤后面纳入批量化要考虑的需求，但是手工的流程我们先走一遍。

step4：设置用于鉴权的SSH密钥

主控端生成ssh的公私钥，默认生成的密钥保存在/root/.ssh文件夹下

[root@root tmp]# ssh-keygen

![image.png](https://image.3001.net/images/20181022/1540190920_5bcd72c8bbfe7.png!small)  

主控端向单个节点下发公钥：

[root@root tmp]# ssh-copy-id -i [email]root@192.168.159.61[/email]

![image.png](https://image.3001.net/images/20181022/1540190928_5bcd72d05621c.png!small)  

step5：添加Ansible定义的节点到host清单

在ansible的配置文件添加host清单，建议根据实际分类对组进行命名。

[root@root tmp]# vi /etc/ansible/hosts

![image.png](https://image.3001.net/images/20181022/1540190934_5bcd72d6843cf.png!small)  

step6：在ansible主控端运行命令测试

[root@root tmp]# ansible -m command -a “ifconfig” ‘webservers’

![image.png](https://image.3001.net/images/20181022/1540190940_5bcd72dccaa98.png!small)  

以上只是针对单个节点的情况下ansible的基本要达到的条件。

  
0x03 ansible的基础用法、模块的使用条件以及playbook的使用

  
1\. Ansible基本语法如下：

ansible <pattern_goes_here> -m <module_name> -a <arguments>

指定操作的节点 指定模块名称 为模块指定参数

<pattern_goes_here>指的是要操作节点的组名，即/etc/ansible/hosts文件中定义的节点分类的组名或者具体的节点的IP地址或者域名等；

-m 用于指定模块的名称，比如常用的command、script、raw等模块； 

-a 定义模块的参数，比如指定模块command后再-a “date”即可查看节点的时间，其他使用以此类推。

  
2\. ansible执行结果的颜色含义：  

红色：表示ansible对节点执行的命令出现异常

绿色：表示ansible对节点执行的命令正常执行，并且没有对节点产生修改操作。

黄色：表示ansible对节点执行的命令正常执行，并且对节点产生相应的改动操作。

3\. 模块的使用条件：

模块的使用，这里斗哥考虑的是条件是节点是否需要python环境。这里ansible有两个模块是节点是不需要安装python环境就可以使用，分别是raw模块和script模块，其他模块的使用都是基于节点有python环境。

![image.png](https://image.3001.net/images/20181022/1540190949_5bcd72e524690.png!small)  

具体的模块的使用条件，参数说明可以在使用相关模块的时候再查读ansible 模块官方文档即可。

  
4\. playbook初识：

playbook其实就是ansible各个模块的组合使用，用专门的yaml语言将一个或多个模块合并在一个playbook里面的组合使用。playbook具体由playbook的角色以及playbook的角色要执行的任务task两部组成，一个playbook由一个或者多个角色(play)组成，一个角色(play)可以包含多个任务(task)。playbook的基本构成看下图：

![image.png](https://image.3001.net/images/20181022/1540190955_5bcd72eb918d1.png!small)  

调用playbook命令的格式：[root@root tmp]#ansible-playbook+参数[options]+playbook文件路径。

栗子： 创建如下playbook：

![image.png](https://image.3001.net/images/20181022/1540190961_5bcd72f1af6a4.png!small)  

执行playbook，–tags可指定具体要执行的task：

[root@root tmp]# ansible-playbook –tags t2 playbook.yml

  
![image.png](https://image.3001.net/images/20181022/1540190968_5bcd72f8ca35b.png!small)  

验证执行情况：

![image.png](https://image.3001.net/images/20181022/1540190974_5bcd72fe65d5a.png!small)  

0x04 实际问题中自动化的思考

这里斗哥想从实际的需求以及遇到的问题出发来达到轻量级地实现自动化的目标。基于ansible这个开源神器，我们不用直接了解底层ssh的通信原理以及python实现的模块化。在使用ansible这个工具时我们要考虑的批量化需求详见下图分析。

![image.png](https://image.3001.net/images/20181022/1540190980_5bcd7304914cf.png!small)  

1.基础环境和条件

●基线检查脚本（漏斗公总号回复基线自动化运维可得，当然斗哥手上还有其他操作系统的、中间件、数据库等众多基线脚本，不同的节点运行的脚本的组合不同，这个也需做好分类）

●安装好ansible的主控端主机一台，安装在虚拟机的可以在0x02的step3保存快照。

●需要检查的节点清单（确保开放ssh端口，不是默认22端口的话另分类出来这里暂不做考虑、节点root权限的账号密码）

2.主控端的公钥需要批量下发

主控端通过ssh-keygen命令生成公私钥后，公钥需要下发到节点才可实现主控端对节点的控制，0x02中的是单个节点的公钥下发，并且需要人机交互键入节点ssh密码，显然不适合面对多个节点的下发。

这里斗哥的解决方案是通过expect来实现自动化的交互，以下脚本适用条件于节点无python环境，且节点密码一致的情况。

[root@root tmp]# ./demo

  
  

#!/bin/bash

#生成密钥

ssh-keygen -t rsa

#节点IP以及密码批量发下

SERVERS="192.168.159.88 192.168.159.89"

PASSWD="root"

function sshcopyid

{

expect -c "

set timeout -1;

spawn ssh-copy-id $1;

expect {

\"yes/no\" { send \"yes\r\";exp_continue; }

\"password:\" { send \"$PASSWD\r\";exp_continue; }

};

expect eof;

"

}

for server in $SERVERS

do

sshcopyid $server

done

  
3.基线检查脚本的批量

脚本适用范围：节点未安装python环境，主控端事先创建好要执行的基线脚本。这里斗哥只是使用了ansible的raw和script这两个模块。

  
![image.png](https://image.3001.net/images/20181022/1540191002_5bcd731a81803.png!small)  

以上就是斗哥梳理的整个自动化的流程，拆分每个步骤，针对各个坑点逐一击破，从而实现自动化过程和思考。其实ansible还可以跟其他工具相结合使用，比如和Jenkins结合实现可视化等。如果你有疑问或者不同的见解，欢迎给斗哥留言，期待和大家的交流。

 **  
**

**大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~**


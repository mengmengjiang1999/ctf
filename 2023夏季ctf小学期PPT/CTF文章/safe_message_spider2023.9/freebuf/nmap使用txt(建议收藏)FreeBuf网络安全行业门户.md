## 前言：

01，关于nmap的博客也看了不少，实际工作中用的命令也就那几个。但是要想学好安全，我们应该对自己有更高的要求。

02，经常用的，久了就熟，不经常用的，建议做到了解使用的程度就可以，很多知识现在就是一个：一听都懂，一做就蒙，学了就忘，的状态。

03，自问下对nmap的了解，有点尴尬，所以想写这篇文章。

04，理论其他博客介绍的够多了，这里仅记录一些工作中可能会用到的命令。

## nmap在工作中可能会用到的命令：

    
    
    ------------------------------------------------------------------    -A全面扫描，服务版本探测-sV，-O操作系统，-p端口，-v显示详细扫描内容
    nmap 单ip/多ip/ip段/网段
    nmap -p T:80,U:445 192.168.1.103
    nmap x.x.x.x --script=http-waf-detect.nse      Waf识别
    nmap -D x.x.x.1,x.x.x.2,x.x.x.3 目标IP    多IP扫描目标，迷惑目标管理员，避免封ip
    nmap -S 伪造IP -e eth0 目标IP       伪造源地址
    nmap x.x.x.x --spoof-mac 11:11:11:11:11:11             MAC地址欺骗
    nmap -sV --version-intensity (0-9) 192.168.1.103            设置扫描强度
    nmap -F 192.168.1.1.103    (快速扫描)
    
    nmap -sF -T4 192.168.0.105   探测防火墙状态
    nmap -iL D:\targets.txt
    nmap 192.168.0.100/24 -exclude 192.168.0.105  扫描除某一个目标地址之外的所有目标地址
    nmap 192.168.0.100/24 -exclude D:\targets.txt  扫描除某一文件中的目标地址之外的目标地址
    nmap --traceroute 192.168.0.105
    
    nmap -sS -p1-100 x.x.x.x --open    syn扫描，并只显示开放的端口（syn扫描：高效，隐蔽，不建立连接，不记录扫描行为）
    nmap -p445 x.x.x.x --srcipt=ipidseq.nse   判断是否可以做为僵尸机
    nmap 目标IP -sI 僵尸机IP -Pn -p1-100    使用僵尸机扫描目标
    
    nmap smtp.163.com -p25 --script=smtp-enum-users.nse --script-args=smtp-enum-users.methods={VRFY}    SMTP扫描（发现邮箱账号）
    
    nmap -sN 61.241.194.153(NULL扫描)
    nmap -sF 61.241.194.153(FIN扫描)
    nmap -sW -v -F  192.168.1.103  TCP 窗口扫描
    nmap -sI www.0day.co:80 192.168.1.103    空闲 扫描( 隐藏IP )
    
    =============防火墙/IDS逃逸=================
    1. 报文分段
    nmap -f -v 61.241.194.153
    2. 指定偏移大小
    nmap --mtu 16 192.168.1.104
    3. IP欺骗
    nmap -D RND:11 192.168.1.104
    nmap -D 192.168.1.104,192.168.1.103,192.168.1.101 192.168.1.104
    4. 源地址欺骗
    nmap -sI www.0day.cn:80 192.168.1.104
    5. 源端口欺骗
    nmap --source-port 902 192.168.1.104
    6. 指定发包长度
    nmap --data-length 30 192.168.1.104
    7. 目标主机随机排序
    nmap --randomize-hosts 192.168.1.104
    8. MAX地址欺骗
    nmap -sT -Pn --spoof-mac 0 192.168.1.104
    
    IP反查
    nmap -sn --script hostmap-ip2hosts www.pcos.cn
    
    =============================================
    nmap：扫端口，主机，操作系统，服务，漏洞。
    nmap扫描速度要比nc快
    nmap不加参数默认是SYN扫描
    
    漏洞验证：参考：https://www.cnblogs.com/-qing-/p/10658901.html
    使用nmap 检测多种漏洞，使用系列的nmap NSE 进行检查，如何新建一个nmap 脚本扫描。
    我用过：弱口令爆破，心脏滴血，MongoDB 未授权访问漏洞，SSL受戒礼攻击 ，SSL/TLS 服务器瞬时 Diffie-Hellman 公共密钥过弱﻿=============================================
    

## 其他：

了解nmap不同扫描方式的区别（有http基础）  
了解nmap不同扫描方式，返回的端口状态的差异。  
了解六种端口状态。


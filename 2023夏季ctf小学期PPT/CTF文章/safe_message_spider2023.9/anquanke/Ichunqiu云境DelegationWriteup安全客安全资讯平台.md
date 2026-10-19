# Ichunqiu云境 - Delegation Writeup

阅读量 **401983**

发布时间 : 2023-01-06 10:30:50

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t019d78555cf0e19a24.png)

## 0x1 Info

![](https://p3.ssl.qhimg.com/t019d78555cf0e19a24.png)

## 0x2 Recon

  1. Target external IP  
`39.98.34.149`

  2. Nmap results  

  3. 关注80端口的http服务，目录爆破（省略）找到 /admin  

  4. 使用弱口令登录进入后台，去到模板页面，编辑header.html，添加php一句话 
    
         用户名: admin, 密码：123456
    

![](https://p4.ssl.qhimg.com/t010ba6444eaff803fe.png)

  5. 命令执行  

## 0x03 入口点：172.22.4.36

  1. 弹shell  
  
快速过一下：

    * 入口机器没特别的东西
    * 没能提权到root权限（也不需要提权到root权限）
    * stapbpf suid利用失败  
找到diff suid  

  2. flag01  
`diff --line-format=%L /dev/null /home/flag/flag01.txt`  

  3. flag01 里面有提示用户名  
`WIN19\Adrian`

  4. 挂代理扫 445  
  
获取到三个机器信息172.22.4.19 fileserver.xiaorang.lab  
172.22.4.7 DC01.xiaorang.lab  
172.22.4.45 win19.xiaorang.lab

  5. 用 Flag01提示的用户名 + rockyou.txt 爆破，爆破出有效凭据 (提示密码过期)  
`win19\Adrian babygirl1`

  6. xfreerdp 远程登录上 win19 然后改密码  
  

## 0x04 Pwing WIN19 – 172.22.4.45

前言：当前机器除了机器账户外，完全没域凭据，需要提权到system获取机器账户

  1. 桌面有提示  

  2. 关注这一栏，当前用户Adrian对该注册表有完全控制权限  
  

  3. 提权  
msfvenom生成服务马，执行 sam.bat  
  
sam.bat  
  
修改注册表并且启用服务，然后桌面就会获取到 sam，security，system  

  4. 获取 Administrator + 机器账户 凭据Administrator:500:aad3b435b51404eeaad3b435b51404ee:ba21c629d9fd56aff10c3e826323e6ab:::  
$MACHINE.ACC:
aad3b435b51404eeaad3b435b51404ee:917234367460f3f2817aa4439f97e636  

  5. flag02  

  6. 使用机器账户收集域信息  

## 0x05 DC takeover – 172.22.4.7

  1. 分析 Bloodhound，发现 WIN19 + DC01都是非约束委派  

  2. 使用Administrator登录进入 WIN19，部署rubeus  

  3. 使用DFSCoerce强制触发回连到win19并且获取到DC01的TGT  
  

  4. Base64的tgt 解码存为 DC01.kirbi  

  5. DCSync 获取域管凭据  
![[]]

  6. psexec – flag04  

## 0x06 Fileserver takeover – 172.22.4.19

  1. psexec – flag03  

## 0x07 Outro

  * 感谢Alphabug师傅的提示（0x03 – 0x04），大哥已经把入口点都打完了，我只是跟着进来而已
  * 感谢九世师傅的合作
  * Spoofing已经打完了，walkthrough也写完了，等1000奖励到手后新年释出，个人感觉Spoofing更好玩，出题的思路很妙

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Gcow安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/284201](/post/id/284201)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t0143ca032175423a1f.png) Gcow安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


## **写在前面﻿**

补一下靶场环境

win7：192.168.0.102(桥接网卡）192.168.52.143（Nat网卡） VM1

win2003：192.168.52.141（Nat网卡） VM2

win2008r2：192.168.52.138（Nat网卡） VM3

![v2-b30f03b10d664151e53c652fc3d62145_720w.jpg](https://image.3001.net/images/20201217/1608171899_5fdac17b33566387f62dd.jpg!small)

拓扑图如上，上一篇已经拿到了VM1的shell，且进行了主机与域内信息收集，通过收集的信息已经确定了域控ip，和大致能描绘出内网基本拓扑图，如上期所说，此靶场难度为易，非常适合练习内网渗透各种姿势！

##  **横向移动**

开始整活

一开始通过VM1的phpmyadmin日志写马获取到了蚁剑shell，上传木马进行CS上线

![v2-643203a829eb19cd3a25550a417f98ee_720w.jpg](https://image.3001.net/images/20201217/1608171899_5fdac17b98c715e72bacc.jpg!small)

进程注入提权为system权限

![v2-cd2656df543f0ac962d352fab7f75962_720w.jpg](https://image.3001.net/images/20201217/1608171899_5fdac17bf0c0b675ce16f.jpg!small)

右键视图中第一个会话选择执行->转储Hash

![v2-e4928d6975009594183a1d6aa46c792f_720w.jpg](https://image.3001.net/images/20201217/1608171900_5fdac17c4496477b34729.jpg!small)

成功读取出win7这台主机的账号密码，点击凭据列表可知如下结果，因为此时域控就在win7登陆着，所以直接可以读出来域控的Administrator的明文密码。

![v2-360b42534a926907bc290834e9159397_720w.jpg](https://image.3001.net/images/20201217/1608171900_5fdac17cb25e5f771dfc8.jpg!small)

在上篇中，通过CS的会话net
view功能，探测出内网存活主机如下，确定了域控IP为192.168.52.138。那么此时就已经本次渗透测试结束了，有了域控账号密码还有其ip，当然这就是靶场的特殊性所在，练习为主。实战很难有这么顺利。

![v2-a7eff05aa9784b94ac5399cc47574ec4_720w.jpg](https://image.3001.net/images/20201217/1608171901_5fdac17d34d8e774aecbe.jpg!small)

这里就引出我们第一种方法，可以进行CS的psexec模块进行登录。

要进行账号密码登录域控win2008那台主机，直接本地CS起一个监听肯定是不行的，因为不通目标网，所以这里采用win7作为跳板的形式，起一个win7的派生smb
beacon。

关于smb beacon,使用windows命名管道进行流量封装，再通过父beacon进行通信，流量相对较隐蔽，对于绕过防火墙有奇效。

![v2-df0c392ece010595562986a162be8146_720w.jpg](https://image.3001.net/images/20201217/1608171901_5fdac17df242ee9a5bb7b.jpg!small)

再在目标视图内，右击目标选择 psexec，进行配置选项。

![v2-0281aef2807e360d395869e720d67af7_720w.jpg](https://image.3001.net/images/20201217/1608171902_5fdac17e512b3f795b89c.jpg!small)

显示成功获得域控主机OWA的beacon，且权限为system。

![v2-4e53ad035694c41f636c5a503121ee58_720w.jpg](https://image.3001.net/images/20201217/1608171902_5fdac17ee387656bfca91.jpg!small)

直接type查看域控桌面的flag即可。

![v2-ee32e07bce3baa556a61dab4cc7c6a7c_720w.jpg](https://image.3001.net/images/20201217/1608171903_5fdac17f6983918228e89.jpg!small)

##  **方法2 ：CS联动metasploit进行横向移动**

上面这种方法太过理想化

拿到win7shell后，有多种选择，弹到metasploit，CS上线，弹到Empire或者直接代理把内网代理出来硬撸，方法多多，但用工具辅助一定会提高渗透效率。

CS视图列表中有个主机和端口扫描，信息收集上篇已做

CS和metasploit联动，需要CS起一个foreign监听，然后metasploit加载监听模块，cs的beacon进行派生即可。

![v2-261c18c009c99e9a4f99ae9bd78e2d1e_720w.jpg](https://image.3001.net/images/20201217/1608171904_5fdac18015966856e4747.jpg!small)

弹到meterpreter以后，添加52网段的路由。

![v2-2bd669462e7a3615738a9fd8e67f2146_720w.jpg](https://image.3001.net/images/20201217/1608171904_5fdac180915c8922a33cf.jpg!small)

查看当前已经添加的路由

![v2-ee5bb8def48fb6ffb392ccdd1cd4d33f_720w.jpg](https://image.3001.net/images/20201217/1608171905_5fdac1810e319194044d4.jpg!small)

msf自带socket模块，但因为是S4的不稳定，这里我们通过蚁剑或者meterpreter上传ew进行socket5代理，在win7上执行下面语句

    
    
    netsh advfirewall set allprofiles state off 关闭防火墙
    ew_for_Win.exe -s ssocksd -l 9999 开启socket代理

![v2-f57235b06d654d31565f2bbed3d22b09_720w.jpg](https://image.3001.net/images/20201217/1608171905_5fdac1814c2d981f607e9.jpg!small)

socket代理：192.168.0.102 9999

那么此时攻击机可以选择 proxychains进行一些端口探测、访问其网站、打一些exp，注意ping命令不可以，因为socket协议不支持icmp

浏览器挂上socket5代理，访问域控可得到这个页面

![v2-56af2e410a1cb518171505d8edfa7114_720w.jpg](https://image.3001.net/images/20201217/1608171905_5fdac181bda1ffd636760.jpg!small)

这里直接ms17-010直接打域控即可，我们msf流量已经代理进了内网。这是最简单的一种方法。

![v2-b362897f44a9b099f6ffece41e0c1496_720w.jpg](https://image.3001.net/images/20201217/1608171906_5fdac18255fc0de8a0edd.jpg!small)

使用msf的auxiliary/admin/smb/ms17010command 模块进行读取flag操作。同样的域控权限就拿到了。

##  **总结**

此靶场票据注入、ms14-068、WMI等等均可获取域控服务器权限。很不错的综合域渗透基础靶场，后续会慢慢补全其他姿势。


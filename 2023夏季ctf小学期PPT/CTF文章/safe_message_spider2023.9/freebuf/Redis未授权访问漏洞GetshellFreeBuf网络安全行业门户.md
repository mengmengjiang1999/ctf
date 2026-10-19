  

![image.png](https://image.3001.net/images/20211110/1636532798_618b823ee2251d7c5e607.png!small)

## 【1】 **Redis漏洞简介**

 **Redis** 是一个开源的使用ANSI C语言编写、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库，并提供多种语言的API。

Redis因为配置不当，会导致未授权访问，在一定条件成立的情况下，Redis服务器以root身份运行，黑客就能够给root账户写入SSH公钥文件，然后直接通过SSH登录目标受害的服务器，就能够直接提权目标服务器，然后进行一系列的数据增删查改操作，甚至是泄露信息，勒索加密等等，会对日常业务造成恶劣的影响。

一般情况下，Redis服务会绑定在服务器的6379端口上面，Redis的默认配置是不会开启认证的，如果没有采取相关防御举措，如在防火墙添加规避举措，避免其他非信任的IP访问等，这将会把Redis的服务直接暴露在公网上。

最直接的影响就是其他用户能够直接在未授权的情况下直接访问Redis服务器并进行相关恶意操作：

未授权访问 → 写入公钥 → 变更Redis DB文件存放为公钥目录 → 使用私钥登录

## 【2】 **未授权访问检测**

Redis的默认配置是只允许本地访问，默认配置是空口令。

一般会使用Nmap对目标机器进行扫描。如果发现主机的6379端口是对外开放的，并且目标主机开放外网访问的情况下，就能够在本机使用redis-cli服务连接目标服务器，然后进行恶意操作，黑客能够在未授权访问Redis的情况下，利用Redis自身提供的config命令，进行写文件操作，然后攻击者就能够将自己的ssh公钥写入目标Redis服务器的/root/.ssh文件中的authotrized_keys文件中，进而直接使用公钥对应的私钥直接使用ssh服务登录目标Redis服务器。

## 【3】 **漏洞复现**

  * 配置Kali服务器172.16.35.109 为Redis靶机服务器

  * 配置Kali服务器172.16.35.110 为Redis攻击机

1）在Redis靶机上输入命令redis-server /etc/redis.conf ，以root身份启动Redis服务

![image.png](https://image.3001.net/images/20211110/1636532800_618b8240e960e158449a6.png!small)

2）在攻击机上的Redis服务文件夹路径下使用 ./redis-cli -h 172.16.35.109在Redis
默认没有配置密码的情况下可以直接成功连接目标Redis服务器

![image.png](https://image.3001.net/images/20211110/1636532802_618b8242f14d03b47c0c3.png!small)

3）连接验证，我们向靶机的目标路径下写入shell文件（这里的路径我们可以的通过phpinfo或者报错、查看源码、SQL注入，等一系列方法寻找出正确的物理路径）

![image.png](https://image.3001.net/images/20211110/1636532804_618b8244d82617716496f.png!small)

![image.png](https://image.3001.net/images/20211110/1636532806_618b8246ec2d84e84e60d.png!small)

至此，已证明Redis漏洞是存在的，能够进行未授权访问

## 【4】 **利用公钥与私钥认证，获取root权限**

先解释一下 **公钥** 与 **私钥** 的含义与作用：

公钥与私钥是一组生成的密钥，公钥是在生成后，拥有者公开发出去的加密方式，用外网中，用拥有者公钥加密的文件，只有拥有者相对应的私钥才能进行解密与配对，同样的，私钥加密的文件，只有相对应的公钥才能解密，公钥与私钥是成双成对的，它们互相解密。

1）确认靶机是开启Redis 服务的状态

![image.png](https://image.3001.net/images/20211110/1636532807_618b8247a775fcd7e06eb.png!small)

2）在靶机中执行mkdir /root/.ssh创建ssh公钥存放目录（靶机是作为ssh服务器使用的）

![image.png](https://image.3001.net/images/20211110/1636532810_618b824a4899495ca9d28.png!small)

3）然后在攻击机172.16.35.110中输入ssh-keygen -t rsa生成公钥和私钥，密码设置为空

![image.png](https://image.3001.net/images/20211110/1636532812_618b824c4edda7caa8050.png!small)

4）cd .ssh/ 进入.ssh目录，将生成的公钥保存为1.txt

![image.png](https://image.3001.net/images/20211110/1636532813_618b824dde5745e64ceb3.png!small)

（echo -e “\n\n”; cat id_rsa.pub;echo -e “\n\n”）> 1.txt

5）然后将保存为1.txt的公钥文件通过redis-cli服务写入靶机

![image.png](https://image.3001.net/images/20211110/1636532815_618b824f91e14ef9704b2.png!small)

6）使用redis-cli 服务连接靶机

![image.png](https://image.3001.net/images/20211110/1636532819_618b825330b831b5f1d52.png!small)

7）使用 CONFIG GET dir 查看Redis的备份路径

![image.png](https://image.3001.net/images/20211110/1636532821_618b825558061a23d204b.png!small)

8）更改redis备份路径为ssh公钥存放目录

![image.png](https://image.3001.net/images/20211110/1636532823_618b8257462381112f7b5.png!small)

9）设置上传公钥的备份文件名字为authorized_keys

![image.png](https://image.3001.net/images/20211110/1636532825_618b8259b16e9eecb9d57.png!small)

10）检查一下是否更新成功CONFIG GET dbfilename

![image.png](https://image.3001.net/images/20211110/1636532827_618b825badff5c2bac266.png!small)

![image.png](https://image.3001.net/images/20211110/1636532829_618b825d39b4dc80b0206.png!small)

11）在攻击机上使用ssh免密登录靶机172.16.35.109

![image.png](https://image.3001.net/images/20211110/1636532831_618b825f6bfdd02ff02df.png!small)

12）使用ifconfig查看是登录成功 ip已为172.16.35.109

![image.png](https://image.3001.net/images/20211110/1636532834_618b8262704dbfa8724de.png!small)

## 【5】 **防御方案**

 **（1）修改在Redis的目录下打开redis.conf文件**

之前在配置靶机环境的时候，对redis.conf文件进行了相应改动，现在反其道而行，即可防御漏洞。将bind
127.0.0.1前面的注释符去掉，这里的bind
127.0.0.1是只允许本机访问，可以改成允许访问的来访IP制作白名单。修改之后，我们在Redis服务器启动Redis服务的时候，就不能仅仅输入redis-server /etc/redis.conf 来启动服务了，需要改成：redis-server [redis配置文件所在目录]/redis.conf
，这种修改方法的缺陷是，只允许一台机器访问Redis服务器。

![image.png](https://image.3001.net/images/20211110/1636532837_618b826501623b608ee75.png!small)

 **（2）增加远程登录密码**

打开redis.conf文件找到requirepass，然后在后面增加登录验证的密码，这样，攻击者再尝试使用ssh登录也就无法执行命令了。

  


1.靶场配置

直接导入VM即可。

2.扫描iP![1633663079_615fb8672bbef7be72000.png!small](https://image.3001.net/images/20211008/1633663079_615fb8672bbef7be72000.png!small)

![1633663137_615fb8a1236754a29fc26.png!small](https://image.3001.net/images/20211008/1633663137_615fb8a1236754a29fc26.png!small)

3.访问靶场

![1633663169_615fb8c12ba997539867f.png!small](https://image.3001.net/images/20211008/1633663169_615fb8c12ba997539867f.png!small)

 **4.信息搜集**

需要对该网站进行信息搜集，一般信息搜集涉及到该网站的端口信息，服务信息，子域名，网站目录等。

首先，对其进行端口信息的扫描，端口对应着相应的服务。

1.端口扫描

![1633663438_615fb9ce296ae65b4f0cb.png!small](https://image.3001.net/images/20211008/1633663438_615fb9ce296ae65b4f0cb.png!small)

2.目录扫描

![1633663499_615fba0bd9c4cc54752bc.png!small](https://image.3001.net/images/20211008/1633663499_615fba0bd9c4cc54752bc.png!small)

3.使用nikto进行扫描，发现敏感文件；

![1633685182_61600ebeab9bdb53602a2.png!small](https://image.3001.net/images/20211008/1633685182_61600ebeab9bdb53602a2.png!small)

于是，就访问这个文件，如下图；

![1633685225_61600ee949517c7c17883.png!small](https://image.3001.net/images/20211008/1633685225_61600ee949517c7c17883.png!small)

  
  
4.使用smbmap对信息进行枚举

>
> ps:SMBMap允许用户枚举整个域中的samba共享驱动器。列出共享驱动器，驱动器权限，共享内容，上载/下载功能，文件名自动下载模式匹配，甚至执行远程命令。
>
> 命令：smbmap -H 192.168.1.110
>
>
> ![1633685495_61600ff710e6758372182.png!small](https://image.3001.net/images/20211008/1633685495_61600ff710e6758372182.png!small)

从中可以知道，smbdata 可以进行读写；  
使用smbclient来连接。  
![image.png](https://image.3001.net/images/20211008/1633685823_6160113f7957349b21d63.png!small)  
在连接之后，ls命令可以查看  
![image.png](https://image.3001.net/images/20211008/1633685894_616011868618ebeb86885.png!small)  
将其下载下来，分析有没有可用的信息；  
![image.png](https://image.3001.net/images/20211008/1633686007_616011f7acff3c1da7b31.png!small)

发现了新的用户名和密码，尝试一下进行ssh登录；  
![image.png](https://image.3001.net/images/20211008/1633686116_616012644fbc2fc89b985.png!small)  
发现是登录不了的，可能还需要其他密钥；

5.使用ftp进行远程登录  
![image.png](https://image.3001.net/images/20211008/1633686223_616012cf89fc58007d010.png!small)  
使用用户名：smbuser/rootroot1 ；就可以成功登录。  
查看ssh文件配置  
![image.png](https://image.3001.net/images/20211008/1633686358_61601356acd15f45d26f4.png!small)  
下载到本地，打开  
![image.png](https://image.3001.net/images/20211008/1633686409_6160138989eb181a22b0f.png!small)


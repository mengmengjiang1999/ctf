> 这几天在搭建hadoop平台，中间有个免密操作，然后呢想着把他稍稍总结一下。（多台免密的实质就是得到这几台的公钥，然后写到认证文件中）

ssh常见的文件| |  
---|---|---  
id_rsa| 私钥|  
id_rsa.pub| 公钥|  
known_hosts| 访问过计算机的公钥(public key)都记录在这里，连接的时候对比然后提示|  
config| 别名文件|  
authorized_keys| 存放授权过的无密登录服务器公钥|  
  
##
一、ssh（安全外壳协议），是一种通讯协议，可以实现远程安全登录linux设备。但是每次登录的时候都需要输入密码，这就使人很头疼。解决方法是配置ssh公钥和私钥来免密登录。

### ssh免密登录原理

![image](https://image.3001.net/images/20210417/1618654404_607ab4c4381d68fd5e758.png!small)

## 二、windows免密登录自己的云服务器

### （一）我们这里模拟自己的windows免密一台云服务器

#### 1.安装好git环境（这个可以百度）

    
    
    ssh-keygen  #生成秘钥对
    type id_rsa.pub >> authorized_keys  #写入到authorized_keys中
    
    
    
    C:\Users\admin\.ssh>ssh-keygen
    Generating public/private rsa key pair.
    Enter file in which to save the key (C:\Users\admin/.ssh/id_rsa):
    Enter passphrase (empty for no passphrase):
    Enter same passphrase again:
    Your identification has been saved in C:\Users\admin/.ssh/id_rsa.
    Your public key has been saved in C:\Users\admin/.ssh/id_rsa.pub.
    The key fingerprint is:
    SHA256:IEE9Pzy1Wp+jiniIgokDaHzcoqNerCerVpduf03BEyE admin@DESKTOP-001
    The key's randomart image is:
    +---[RSA 2048]----+
    |   .o.   E ..    |
    |     .o   o.     |
    |    . .+ ....    |
    |     . .= o+     |
    |o . . . S= .o.   |
    |oo.= +  .  .+    |
    |=.+++.    o. .   |
    |*=+..+.. ...     |
    |B*= o.o.o.       |
    +----[SHA256]-----+
    

然后使用xftp将秘钥传输到云服务的/root/.ssh目录下

然后 ssh@192.168.192.130即可免密登录

#### 2.ssh别名：别名的目的就是为了方便记忆的

在.ssh目录下创建名为config的文件

    
    
    Host aliyun
    HostName 192.168.192.130
    Port 22
    User root
    IdentitiesOnly yes
    

**HostName 指定登录的主机名或IP地址**  
 **Port 指定登录的端口号**  
 **User 登录用户名**  
 **IdentityFile 登录的公钥文件**  
 **IdentitiesOnly 只接受SSH key 登录**

### （二）我们这里模拟自己的windows免密多台云服务器

和以上一样，就是要将本地的公钥authorized_keys复制到多台linux中的.ssh文件下

别名文件（config）：windows的.ssh目录下

    
    
    Host 001
    HostName 192.168.192.130
    Port 22
    User root
    IdentitiesOnly yes
    
    Host 002
    HostName 192.168.192.131
    Port 22
    User root
    IdentitiesOnly yes
    
    Host 003
    HostName 192.168.192.132
    Port 22
    User root
    IdentitiesOnly yes
    

## 二、linux之间的免密登录（这里我使用的环境是centos7）

> linux之间的免密用的最多的就是相互免密。

### （一）linux免密登录一台（A单向免密B）

    
    
    ssh-keygen  #生成秘钥对
    cat id_rsa.pub >> authorized_keys  公钥写入到authorized_keys
    scp authorized_keys root@192.168.192.131 192.168.192.131:/root/.ssh  #传输到免密机器中
    

别名

    
    
    Host 002
    HostName 192.168.192.131
    Port 22
    User root
    IdentitiesOnly yes
    

### （二）linux两台互相免密（A和B相互免密）

#### 1.

    
    
    第一台
    ssh-keygen  #生成秘钥对
    cat id_rsa.pub >> authorized_keys  公钥写入到authorized_keys
    

cat authorized_keys

    
    
    ssh-rsa AAAAB30NOVqz5mGeC5(我这里不全) root@001
    
    
    
    scp authorized_keys root@192.168.192.131 192.168.192.131:/root/.ssh  #传输到第二台机器中
    

ssh root@192.168.192.131 #可以免密登录即为成功

#### 2.

    
    
    第二台
    ssh-keygen  #生成秘钥对
    cat id_rsa.pub >> authorized_keys  公钥写入到authorized_keys
    

cat authorized_keys（第二台的机器中有两台机器的公钥）

    
    
    ssh-rsa AAAAB0NOVqz5mGeC5 root@001
    ssh-rsa Al7BpXGABuUl0pHj root@002  #这时文件中有相互的公钥了
    
    
    
    scp authorized_keys root@192.168.192.130 192.168.192.130:/root/.ssh  #传输到第一台机器中（传输之前第一台的authorized_keys文件中只有自己的公钥，第二台传输到第一台后，覆盖第一台的authorized_keys文件，两台机器都有双方的公钥）
    

ssh root@192.168.192.130 #成功免密登录即为成功

### （三）linux三台互相免密（ABC之间相互免密）

    
    
    第一台192.168.192.130
    ssh-keygen
    cat id_rsa.pub >> authorized_keys
    scp authorized_keys root@192.168.192.131 192.168.192.131:/root/.ssh
    测试ssh root@192.168.192.131
    
    第二台192.168.192.131
    ssh-keygen
    cat id_rsa.pub >> authorized_keys
    scp authorized_keys root@192.168.192.132 192.168.192.132:/root/.ssh
    测试ssh root@192.168.192.132
    
    第三台192.168.192.132
    ssh-keygen
    cat id_rsa.pub >> authorized_keys
    scp authorized_keys root@192.168.192.130 192.168.192.130:/root/.ssh
    scp authorized_keys root@192.168.192.131 192.168.192.131:/root/.ssh
    测试
    ssh root@192.168.192.130
    ssh root@192.168.192.131
    即为三台之间互相免密登录
    

config（没有则创建，路径在.ssh下）

    
    
    Host 001
    HostName 192.168.192.130
    Port 22
    User root
    IdentitiesOnly yes
    
    Host 002
    HostName 192.168.192.131
    Port 22
    User root
    IdentitiesOnly yes
    
    Host 003
    HostName 192.168.192.132
    Port 22
    User root
    IdentitiesOnly yes
    


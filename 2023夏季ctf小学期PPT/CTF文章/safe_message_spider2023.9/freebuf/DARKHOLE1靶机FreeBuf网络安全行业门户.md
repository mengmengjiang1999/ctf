好久没打靶机了，随便下了一个靶机地址 <https://www.vulnhub.com/entry/darkhole-1,724/>

ip为192.168.1.9

## 常规信息收集

1：IP是已知的扫描下靶机端口

![1628676418_6113a142c2370c62227e6.png!small](https://image.3001.net/images/20210811/1628676418_6113a142c2370c62227e6.png!small)

开着常规端口首先访问下80吧

2：![1628676486_6113a18690c00e706fa0d.png!small](https://image.3001.net/images/20210811/1628676486_6113a18690c00e706fa0d.png!small)

做的还不错 F12也没发现什么就一个登录页面

3：接着扫描目录一下

![1628676552_6113a1c867013c5039afa.png!small](https://image.3001.net/images/20210811/1628676552_6113a1c867013c5039afa.png!small)

config看一看有什么好东西

![1628676578_6113a1e246dfd05816563.png!small](https://image.3001.net/images/20210811/1628676578_6113a1e246dfd05816563.png!small)

但是没有什么有用的，upload就一张图，看来只能从登录页面利用了

## 逻辑缺陷

4：登录页面有一个注册，注册一个看看

![1628678588_6113a9bc69bac9e4e40df.png!small](https://image.3001.net/images/20210811/1628678588_6113a9bc69bac9e4e40df.png!small)

这链接有点意思测试一下是否有sql注入，好家伙果然没有，但是我发现存在一个id=1的这可能就是管理员账户，但是看到靶机提示过别尝试暴力破解那么还得另辟蹊径

往旁边一看旁边还有一个修改密码的看到这让我想到了逻辑漏洞，我去试了试注册admin这个账户好家伙存在那我的试试改它的

![1628678680_6113aa18ad96392a2a96a.png!small](https://image.3001.net/images/20210811/1628678680_6113aa18ad96392a2a96a.png!small)

## 一波三折

5：打开Burp 测一把

![1628679058_6113ab927467c821a3205.png!small](https://image.3001.net/images/20210811/1628679058_6113ab927467c821a3205.png!small)

成功

![1628679058_6113ab92881b31909e34b.png!small](https://image.3001.net/images/20210811/1628679058_6113ab92881b31909e34b.png!small)

好家伙起飞了这不得getshell

上传一句话木马

然而我哭了

![u=1086793405,4071548656&fm=26&fmt=auto&gp=0.jpg](https://image.3001.net/images/20210811/1628688685_6113d12de43008125910b.jpg!small)

![1628679187_6113ac135f7e820630424.png!small](https://image.3001.net/images/20210811/1628679187_6113ac135f7e820630424.png!small)

这啥玩意还刁难我呢

我改你个后缀试试

![1628679480_6113ad38a645d67ff0fb9.png!small](https://image.3001.net/images/20210811/1628679480_6113ad38a645d67ff0fb9.png!small)

还是不行

![u=1256194039,1507300157&fm=26&fmt=auto&gp=0.jpg](https://image.3001.net/images/20210811/1628688686_6113d12e3d228a0ef2f2b.jpg!small)

![1628679480_6113ad38c70f92a2ff41a.png!small](https://image.3001.net/images/20210811/1628679480_6113ad38c70f92a2ff41a.png!small)

残忍,我再改改加个我上个shell.php1

成功了

![1628679488_6113ad40b4369149e3eff.png!small](https://image.3001.net/images/20210811/1628679488_6113ad40b4369149e3eff.png!small)

![1628679480_6113ad38c682fa0bdcd65.png!small](https://image.3001.net/images/20210811/1628679480_6113ad38c682fa0bdcd65.png!small)

但是感觉不妙啊这直接显示出来，果然不执行,那么就得使用php-reverse-shell来反弹一个shell,那么后缀是php加数字肯定是不行的那么试试phar试试

![1628682157_6113b7ad03ef8767d4c7b.png!small](https://image.3001.net/images/20210811/1628682157_6113b7ad03ef8767d4c7b.png!small)

这个phar文件会在打开后执行然后反弹一个shell那么我们kali监听

    
    
    nc -lvp 4444

直接拿到shell

![1628682164_6113b7b44da0ef4b5f27f.png!small](https://image.3001.net/images/20210811/1628682164_6113b7b44da0ef4b5f27f.png!small)

![u=2412006035,2897460664&fm=26&fmt=auto&gp=0.jpg](https://image.3001.net/images/20210811/1628688686_6113d12e9ed138a729208.jpg!small)

## 提权

6:现在权限还是很低的下面就得提权了

先获得一个交互式的shell吧

    
    
    python3 -c 'import pty;pty.spawn("/bin/bash")'

![1628682460_6113b8dca4701a80b6d0e.png!small](https://image.3001.net/images/20210811/1628682460_6113b8dca4701a80b6d0e.png!small)

发现了类似于账户密码的文件但是没有权限

![1628682677_6113b9b50967e65388c40.png!small](https://image.3001.net/images/20210811/1628682677_6113b9b50967e65388c40.png!small)

看了看suid也没有可以利用的，只有采用环境变量提权了

    
    
    echo 'bash' > /tmp/id;chmod +x /tmp/id; export PATH=/tmp:$PATH

![1628685284_6113c3e4918abfad4abdd.png!small](https://image.3001.net/images/20210811/1628685284_6113c3e4918abfad4abdd.png!small)

这里直接得到了john的权限

这样即可打开password文件

![1628685410_6113c4622f3222cfde34a.png!small](https://image.3001.net/images/20210811/1628685410_6113c4622f3222cfde34a.png!small)

这样拿到了密码了

![1628685432_6113c478cf40e6c1084e7.png!small](https://image.3001.net/images/20210811/1628685432_6113c478cf40e6c1084e7.png!small)

打开user.txt就一句鼓励的话

那么这个密码肯定就是john的密码了

ssh连接上

![1628685503_6113c4bf2cdf35b9993e5.png!small](https://image.3001.net/images/20210811/1628685503_6113c4bf2cdf35b9993e5.png!small)

7：拿到权限后还是那些文件

![1628685701_6113c585871a6cd3e23f4.png!small](https://image.3001.net/images/20210811/1628685701_6113c585871a6cd3e23f4.png!small)

但是存在这个file.py文件而且是空的那么久好办了直接写入执行提权

![1628685682_6113c572b4f79c7dbd771.png!small](https://image.3001.net/images/20210811/1628685682_6113c572b4f79c7dbd771.png!small)

    
    
    echo 'import os;os.system("/bin/bash")' > file.py

执行

![1628687037_6113cabd4874e961c9c29.png!small](https://image.3001.net/images/20210811/1628687037_6113cabd4874e961c9c29.png!small)

但是存在个问题没反应啊难道是没加sudo

![1628687163_6113cb3b6e529e08659bb.png!small](https://image.3001.net/images/20210811/1628687163_6113cb3b6e529e08659bb.png!small)

好家伙路径又不允许那我从home开始吧

![1628687206_6113cb66a4ad0755220e6.png!small](https://image.3001.net/images/20210811/1628687206_6113cb66a4ad0755220e6.png!small)

成功拿下root权限

![1628687223_6113cb777561280adaff8.png!small](https://image.3001.net/images/20210811/1628687223_6113cb777561280adaff8.png!small)

## 疑问

后面我也访问了这个toto文件

![1628688241_6113cf711e2bd7c8cd633.png!small?1628688254036](https://image.3001.net/images/20210811/1628688241_6113cf711e2bd7c8cd633.png!small?1628688254036)

发现是乱码的，大致就是输出了这台靶机当前用户拥有的权限


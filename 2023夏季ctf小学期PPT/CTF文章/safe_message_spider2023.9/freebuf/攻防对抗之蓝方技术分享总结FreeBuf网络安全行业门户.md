## 背景介绍

**08sec团队在2019年起每个月将会举行内部攻防对抗，并分享技术总结，为初、中级技术爱好者提供良好的学习环境，提升网络信息安全水平，这是首次活动，为期7天的红蓝对抗，攻防网络环境相对复杂，蓝方准备时间仅有1天，完全模拟了真实的攻防环境，并对采用的开源cms程序成功挖掘了漏洞。**

## 一、准备阶段

### 初步讨论

LINUX+CMS+mysql+tomcat关卡设计（时间原因无法实现）

 **1.服务搭建**

拉取源码：

    
    
    git clone https://github.com/ming-soft/MCMS

![图片
1.png](https://image.3001.net/images/20190409/1554782252_5cac182cb3cfa.png!small)

因为之前运⾏行行该项⽬目缺少库，所以将项⽬目导⼊入IDEA：

![图片
2.png](https://image.3001.net/images/20190409/1554782275_5cac1843ebda3.png!small)

重新编译添加 pom.xml，配置Maven：

![图片
3.png](https://image.3001.net/images/20190409/1554782291_5cac1853b5cf0.png!small)

同步Maven库，测试：

![图片
4.png](https://image.3001.net/images/20190409/1554782309_5cac18655af6d.png!small)

然后⽣生成war包,ms-mcms.war（这边我使⽤用的是我⾃自⼰己服务器的 mysql
服务器，编译的时候已经写进配置⽂文件了，所以后续没有关于mysql的部分）。

切换o0p低权⽤用户，下载tomcat7的java web运⾏行行环境，删除tomcat⾃自带的项⽬目录：

![图片
5.png](https://image.3001.net/images/20190409/1554782331_5cac187b4e639.png!small)

将该war包部署到服务器上上。重启tomcat服务器：

![图片
6.png](https://image.3001.net/images/20190409/1554782353_5cac1891c4325.png!small)

 **2.下载并部署openrasp**

![图片
7.png](https://image.3001.net/images/20190409/1554782370_5cac18a2ab9e0.png!small)

 **3.网站效果：**

![图片
8.png](https://image.3001.net/images/20190409/1554782385_5cac18b1d2fc0.png!small)

### 主机加固

 **1.系统加固**

1)除root外的用户无法登陆touch /etc/nologin；

2)密码文件用户权限等：

    
    
    chmod 644 /etc/passwd
    
    chmod 600 /etc/shadow
    
    chmod 644 /etc/group

3)创建文件权限umask=027；

4)日志等加固：

    
    
    chattr +a /var/log/messages （只能追加数据） chattr +i /var/log/messages.* （不能被删除） chattr +i /etc/shadow
    
    chattr +i /etc/passwd chattr +i /etc/group 5) 权限加固
    
    chmod -R 700 /etc/rc.d/init.d/*

仅仅root可以读，写，执行上述所有script file.

6)屏蔽登录banner信息：

    
    
    vi /etc/ssh/sshd_config banner NONE

7)秘钥增强：

    
    
    authconfig --passalgo=sha512 --update 启用 SHA512 替代 MD5

8)限制登录次数：

    
    
    auth required pam_tally2.so deny=3 unlock_time=5 even_deny_root root_unlock_time=120

登录3次锁定账号2分钟；

9)设置Bash保留历史命令的条数

    
    
    vi /etc/profile

修改HISTSIZE=5和HISTFILESIZE=20，即保留最新执行的20条命令。

 **2.web服务加固**

1)隐藏tomcat版本信息

修改conf/server.xml，在Connector节点添加server字段：

![图片
9.png](https://image.3001.net/images/20190409/1554782483_5cac1913c4cf3.png!small)

2)关闭自动部署：

修改/conf/server.xml 中的 host 字段，修改 unpackWARs=”false” autoDeploy=”false”；

3)自定义错误页面：

修改 web.xml,自定义 40x、50x 等容错页面，防止信息泄露。

4)禁止列目录

修改web.xml false；

5) 服务权限控制；

tomcat以非root权限启动，应用部署目录权限和tomcat服务启动用户分离，比如tomcat以tomcat用户启动，而部署应用的目录设置为nobody用户750。

6)启动cookie的httponly，修改/conf/context.xml，usehttponly=“true”

 **3.数据库加固**

1)禁用mysql历史命令Rm ~/.mysql_history；

2)运行mysql_secure_installation执行相关安全设置；

3)使用validate_password.so插件，进行安全加固；

4)重命名 ROOT 账户；

    
    
    Update user set user=”新用户名”where user=”root” 

5)控制最高权限只有管理员

    
    
    SELECT user, host FROM mysql.user WHERE (Select_priv = 'Y') OR (Insert_priv = 'Y') OR (Update_priv = 'Y') OR (Delete_priv = 'Y') OR (Create_priv = 'Y') OR (Drop_priv = 'Y');
    
    SELECT user, host FROM mysql.db WHERE db = 'mysql' AND ((Select_priv = 'Y') OR (Insert_priv = 'Y') OR (Update_priv = 'Y')OR (Delete_priv = 'Y') OR (Create_priv = 'Y') OR (Drop_priv = 'Y'));

6)删除默认test数据库，测试帐号，空密码、匿名帐号：

    
    
    bash drop database if exists ${dbname};
    
    bash drop user ''
    
    select user,host from mysql.user

7)关闭Old_Passwords：

    
    
    show variables like ‘%password%’； 

8)确保所有用户都要求使用非空密码登录：

    
    
    SELECT User,host FROM mysql.user WHERE (plugin IN('mysql_native_password', 'mysql_old_password') AND (LENGTH(Password)
    
    = 0 OR Password IS NULL)) OR (plugin='sha256_password' AND LENGTH(authentication_string) = 0);

9)禁止MySQL对本地文件存取Less /etc/my.cnf。

 **4.自我检测：AWVS、nessus、测试**

1)多线程扫描服务器均直接DOWN；

2)测试后得出如下：

a)首页搜索SQL注入，openrasp有拦截，注意拦截日志，openrasp绕过可能性大；

添加openrasp规则：

b)任意文件上传，目前openrasp有拦截jsp jspx拦截，增加xml后缀拦 截，防止替换配置文件，

增加拦截规则：

c)后台解压模板功能，zip文件直接解压获得shell，后台防护注意，模板路径禁止脚本执行权限：

取消执行权限。

## 二、对抗阶段

### 1.开始阶段：通过日志观察红方扫描信息收集、跑 sqlmap：

![图片
10.png](https://image.3001.net/images/20190409/1554782652_5cac19bc90f19.png!small)

![图片
11.png](https://image.3001.net/images/20190409/1554782706_5cac19f262b0a.png!small)

### 2\. 上传文件突破

![图片
12.png](https://image.3001.net/images/20190409/1554782741_5cac1a1574133.png!small)

![图片
13.png](https://image.3001.net/images/20190409/1554782762_5cac1a2aab5b7.png!small)

查看⽇日志，发现有个⾮非系统url，访问发现是个SHELL。

初步判断入侵路径：用户上传头像或者前台其他上传的地方、调用file/upload.do，
上传war包，穿透目录到webapps下，自动解压war包，得到shell：

![图片
14.png](https://image.3001.net/images/20190409/1554782796_5cac1a4c6cd20.png!small)

### 3\. 应对方案

1)修改文件执行权限；

2)上文件监控。

![图片
15.png](https://image.3001.net/images/20190409/1554782822_5cac1a66abb4d.png!small)

![图片
16.png](https://image.3001.net/images/20190409/1554782852_5cac1a84b7b20.png!small)

### 4.RASP 规则

![图片
17.png](https://image.3001.net/images/20190409/1554782887_5cac1aa773dda.png!small)

修改302重定向至福利网站吸引宅男红方注意力。

## 三、收尾阶段

![图片
19.png](https://image.3001.net/images/20190409/1554782957_5cac1aed9cd45.png!small)![图片
18.png](https://image.3001.net/images/20190409/1554782938_5cac1ada21755.png!small)

通过日志发现红方还是致力于上传漏洞和注入绕过rasp均无效。

## 四、总结

(一)前期业务部署由于不熟悉的缘故耽误太久，导致加固时间不足，仓促开始；

(二)网络结构复杂成功拖延了红方进攻步伐和思路；

(三)RASP意外的好用基本防住了注入否则开源CMS的注入点还是很多的；

(四)上传漏洞其实开始注意到了但是加固组员没能及时修补导致被get shell，否则我们一分不失；

(五)队员们都很给力，团队合作很重要。

 ***本文作者：08sec团队，转载请注明来自FreeBuf.COM**


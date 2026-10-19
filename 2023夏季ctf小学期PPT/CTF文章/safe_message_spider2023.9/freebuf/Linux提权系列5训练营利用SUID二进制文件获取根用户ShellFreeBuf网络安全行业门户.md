在上一篇文章中，已经解释了文件上的 suid 位，并通过 C++ 程序演示了它的用法。在本文中，将使用相同的知识利用 SUID 权限配置错误的漏洞来提权。

## 第一个实验

查看当前目录，发现有两个`root`用户的文件。

![图片](https://image.3001.net/images/20230419/1681889228_643f97cc3f15ddb7b3431.png!small)

运行欢迎文件只是打印一条消息。

通过`strings`命令来查看`welcome`文件，发现它执行`greetings`程序

![图片](https://image.3001.net/images/20230419/1681889240_643f97d8b758347d576eb.png!small)

任何设置了 SUID 位并从 PATH
环境变量调用另一个程序的二进制文件都是提权的明确标志。所能做的就是简单地在路径变量前面加上恶意可执行文件所在的路径，它就会出现一个root shell。

由于`greetings`程序就在`student`用户拥有的目录下，所以`PATH`环境变量不需要更改。只需要`rm -fr greetings`

![图片](https://image.3001.net/images/20230419/1681889251_643f97e3d59c161b3c3dc.png!small)

现在创建包含以下内容的`greetings`文件。执行此操作后，请确保使用`chmod +x ./greetings`使文件可执行

    
    
    #!/bin/bash  
      
    /bin/bash -i

重新运行`welcome`

![图片](https://image.3001.net/images/20230419/1681889276_643f97fcb7ea756ec257d.png!small)

获得了`root shell`啦

## 第二个实验

大多数情况下，不会像在上一个实验中那样幸运。需要首先找到易受攻击的二进制文件，然后利用它们

    
    
    find / -type f -perm -4001 -exec ls -h {} \; 2> /dev/null

上面的命令将在根目录（/）中找到设置了 `suid`位和全局可执行权限（`-perm -4001`）的文件（`-type f`）并执行 `ls
-l`（`-exec ls -l {} \;`) 显示每个匹配项，并把标准错误重定向到 `/dev/null`(`2> /dev/null`)
产生类似于下图的输出

![图片](https://image.3001.net/images/20230419/1681889287_643f98075ec7ccdd16071.png!small)

当打开 `vim.tiny /etc/shadow`时，不要让 `vim.tiny`中的 `[readonly]`欺骗了

  

![图片](https://image.3001.net/images/20230419/1681889295_643f980fabbec622bd6d3.png!small)

已经以 `root`用户身份运行`vim.tiny`，所需要做的就是从 `OpenSSL`工具创建密码并更新 `/etc/shadow`文件

![图片](https://image.3001.net/images/20230419/1681889307_643f981ba0df31b038bb3.png!small)

现在通过执行 `su - root`更改用户并使用刚才从 `OpenSSL`工具生成的密码登录

![图片](https://image.3001.net/images/20230419/1681889335_643f9837a7126fed83ba1.png!small)

获得了 root 用户的 shell

## 第三个实验

在查找 `SUID`二进制文件时，会发现 `/usr/bin/find`二进制文件与其他标准二进制文件不同。因此，这可能用于提升权限

![图片](https://image.3001.net/images/20230419/1681889373_643f985da8b943df397df.png!small)

现在已经熟悉了 `find`命令，对于每一项，都可以使用 `-exec`参数对其执行命令。在这种情况下，只需要使用 `-exec /bin/bash
-ip`参数来获得特权用户交互式 `bash shell`

![图片](https://image.3001.net/images/20230419/1681889390_643f986ed72759edcd679.png!small)

## 第四个实验

这是一个非常冗长的实验，因为先必须执行水平权限提升（获取另一个非特权用户的
shell）并获得对不同用户的访问权限，然后从该用户获取特权用户的`shell`（垂直权限提升）。

在搜索 `suid`二进制文件时，发现用户 `john`拥有一个二进制文件 `/userfiles/john/notebook`

![图片](https://image.3001.net/images/20230419/1681889404_643f987c4a4464c4f6cdd.png!small)

执行它生成了一个 `john`的 `shell`

![图片](https://image.3001.net/images/20230419/1681889418_643f988aba192c79576ef.png!small)

现在再次搜索 `suid`二进制文件并期待其他结果。在这种情况下，将看到 `/home/john/imroot`归 `root`用户所有

![图片](https://image.3001.net/images/20230419/1681889440_643f98a0f209a0e22d56e.png!small)

在执行程序文件时，它什么也没做，只是简单地打印`No root for you!!`。也许它需要一些参数

![图片](https://image.3001.net/images/20230419/1681889480_643f98c83bd7a22946000.png!small)

不幸的是，有一个`imroot.c`文件，但它只能由 `root`用户读取。

![图片](https://image.3001.net/images/20230419/1681889492_643f98d401a161adef1e0.png!small)

由于安装了`GDB`，在调试时首先发现它正在执行`strlen`函数并比较长度为`0x4`的字符串。所以得到命令参数的长度必须是 4 个字符的想法。

![图片](https://image.3001.net/images/20230419/1681889505_643f98e10b17766c50ec7.png!small)

进一步检查，发现它正在反复比较一些十六进制字符串 4 次，这是输入的长度。所以把它复制到某个地方

![图片](https://image.3001.net/images/20230419/1681889515_643f98eb1c30f34de8ea9.png!small)

得到`\x63\x6d\x64\x3d`的`ASCII`字符后，发现等于`cmd=`

![图片](https://image.3001.net/images/20230419/1681889524_643f98f4ea9f3b01a8e19.png!small)

当尝试 `cmd=<command>`时，它以 `root`用户身份执行。所以第二个命令是生成一个特权 `shell`

![图片](https://image.3001.net/images/20230419/1681889543_643f9907cba9f7b4591af.png!small)

以 root 用户身份获得特权 shell！


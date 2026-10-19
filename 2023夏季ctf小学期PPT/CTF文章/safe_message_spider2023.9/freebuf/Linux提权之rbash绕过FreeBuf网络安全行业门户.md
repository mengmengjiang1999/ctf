# RBASH 绕过

## 什么是 RBASH

  * RBASH 是 Restricted BASH 的缩写，意思是受限制的 BASH。

  * RBASH 是一种特殊的 shell，它限制了用户的一些操作和权限，例如：

    * 不能使用 cd 命令来改变当前目录。

    * 不能使用 set 命令来改变环境变量或 shell 选项。

    * 不能使用 unset 命令来取消环境变量或 shell 函数。

    * 不能使用任何包含 / 符号的命令，除非它们在 PATH 环境变量中指定了。

    * 不能重定向输入或输出，例如使用 >, <, >>, << 等符号。

    * 只能执行 PATH 环境变量中指定的命令，而且 PATH 环境变量通常只包含一些基本的命令，例如 ls, cat, echo 等。

  * RBASH 的目的是为了提高系统的安全性，防止用户执行一些危险或不合法的操作。

## 为什么要绕过 RBASH

  * RBASH 的限制可能会给用户带来一些不便或困难，例如：

    * 不能访问一些需要特定目录或权限的文件或程序。

    * 不能执行一些需要重定向或管道的复杂命令或脚本。

    * 不能使用一些有用或有趣的命令或工具，例如 vim, ssh, git 等。

  * RBASH 的限制也可能会给用户带来一些挑战或机会，例如：

    * 想要探索系统的更多信息或功能，例如查看系统版本，运行服务，修改配置等。

    * 想要提升自己的技能或知识，例如学习 Linux 命令行，编程语言，网络安全等。

    * 想要完成一些特定的任务或目标，例如参加 CTF 比赛，渗透测试，黑客攻防等。

## 如何绕过 RBASH

  * RBASH 绕过的方法有很多，主要取决于 RBASH 的限制程度和用户的目标是什么。一般来说，RBASH 绕过的目的是获得一个正常的 BASH shell，或者执行一些被禁止的命令或操作。

  * 在本文章中，我们将介绍以下几种常见的 RBASH 绕过的方法，并举例论证它们的具体操作方式：

    * 使用 / 符号

    * 使用 cp 命令

    * 使用 ftp, gdb, more, man, less, vim, rvim 等命令

    * 使用 awk, find, expect, python, php, perl, lua, ruby 等编程语言或工具

    * 使用 ssh 命令

    * 使用 git 命令

    * 使用 pico 命令

    * 使用 vi 命令

### 使用 / 符号

  * 如果 RBASH 没有完全禁止使用 / 符号，那么用户可以尝试直接运行 /bin/bash 或 /bin/sh 来获得一个正常的 shell。例如：

    
    
    rbash$ /bin/bash

  * 这个方法的原理是：RBASH 只限制了 PATH 环境变量中指定的命令，而不限制绝对路径的命令。因此，如果用户知道 bash 或 sh 的绝对路径，就可以直接运行它们，从而绕过 RBASH 的限制。

  * 这个方法的优点是：简单易用，不需要其他的命令或工具，只要有 / 符号就可以。

  * 这个方法的缺点是：容易被 RBASH 发现和阻止，只要 RBASH 禁止使用 / 符号，或者修改 bash 或 sh 的绝对路径，就可以防止这个方法的成功。

### 使用 cp 命令

  * 如果 RBASH 允许使用 cp 命令，那么用户可以把 /bin/bash 或 /bin/sh 复制到自己的目录下，然后运行它们。例如：

    
    
    rbash$ cp /bin/bash .  
    rbash$ ./bash

  * 这个方法的原理是：RBASH 只限制了 PATH 环境变量中指定的命令，而不限制用户自己的目录下的命令。因此，如果用户把 bash 或 sh 复制到自己的目录下，就可以运行它们，从而绕过 RBASH 的限制。

  * 这个方法的优点是：比较灵活，不需要知道 bash 或 sh 的绝对路径，只要能够复制它们就可以。

  * 这个方法的缺点是：需要使用 cp 命令，如果 RBASH 禁止使用 cp 命令，或者限制用户的目录权限，就无法使用这个方法。

### 使用 ftp, gdb, more, man, less, vim, rvim 等命令

  * 如果 RBASH 允许使用 ftp, gdb, more, man, less, vim, rvim 等命令，那么用户可以在它们的交互模式下使用 !/bin/bash 或 !/bin/sh 来执行一个外部命令。例如：

    
    
    rbash$ ftp  
    ftp> !/bin/bash  
    bash$ whoami

  * 这个方法的原理是：这些命令都有一个交互模式，可以让用户输入一些子命令或选项来控制它们的行为。其中，! 是一个特殊的子命令，表示执行一个外部命令，而不是这些命令本身的功能。因此，如果用户输入 !/bin/bash 或 !/bin/sh，就可以执行 bash 或 sh，从而绕过 RBASH 的限制。

  * 这个方法的优点是：比较隐蔽，不容易被 RBASH 发现和阻止，因为这些命令本身都是合法的，而且 ! 子命令不会在历史记录中显示。

  * 这个方法的缺点是：需要使用这些命令中的一个，如果 RBASH 禁止使用这些命令，或者修改它们的行为或选项，就无法使用这个方法。

  * 除了 ftp 命令之外，其他几种命令也可以用类似的方式来绕过 RBASH。以下是一些操作实例：

    
    
    rbash$ gdb -q  
    (gdb) !/bin/bash  
    ​  
    rbash$ more /etc/passwd  
    !/bin/bash  
    ​  
    rbash$ man man  
    !/bin/bash  
    ​  
    rbash$ less /etc/passwd  
    !/bin/bash  
    ​  
    rbash$ vim -Z -c ':!/bin/bash'

rvim - 命令是用来启动一个受限制的 vim 编辑器的。其中，- 选项表示从标准输入读取文本，-Z 选项表示启动受限制的模式，-c 选项表示执行一个
vim 命令。因此，如果用户输入 rvim - -Z -c ‘:!/bin/bash’，就可以在 vim 的命令模式下使用 :!/bin/bash
来执行一个外部命令，从而绕过 RBASH 的限制。例如：

    
    
    rbash$ rvim - -Z -c ':!/bin/bash'

### 使用 vi 命令

  * 如果 RBASH 允许使用 vi 命令，那么用户可以利用它的 :set shell=/bin/bash 命令来执行 /bin/bash。例如：

    
    
    rbash$ vi  
    :set shell=/bin/bash  
    :shell

  * 这个方法的原理是：vi 命令是一个经典的文本编辑器。其中，:set 命令表示设置一个选项的值，:shell 命令表示执行一个 shell。默认情况下，vi 会使用 RBASH 作为 shell，但是用户可以通过 :set shell=/bin/bash 来修改 shell 的值为 /bin/bash。因此，如果用户使用 :shell 命令，就可以运行 bash，从而绕过 RBASH 的限制。

  * 这个方法的优点是：比较简单，不需要复制或修改 bash，也不需要使用其他的命令或工具，只要有 vi 命令就可以。

  * 这个方法的缺点是：需要使用 vi 命令，如果 RBASH 禁止使用 vi 命令，或者限制它的选项或参数，就无法使用这个方法。

### 使用 awk, find, expect, python, php, perl, lua, ruby 等编程语言或工具

  * 如果 RBASH 允许使用 awk, find, expect, python, php, perl, lua, ruby 等编程语言或工具，那么用户可以利用它们的系统调用功能来执行 /bin/bash 或 /bin/sh。例如：

    
    
    rbash$ awk 'BEGIN {system("/bin/bash")}'  
    bash$ whoami  
    tom  
    bash$ pwd  
    /home/tom  
    bash$ cd /  
    bash$ pwd  
    /

  * 这个方法的原理是：这些编程语言或工具都有一些函数或方法，可以让用户在它们的环境中执行一个系统命令，并返回它的输出或状态。例如，awk 中的 system 函数，python 中的 os.system 函数，php 中的 shell_exec 函数等。因此，如果用户使用这些函数或方法来执行 /bin/bash 或 /bin/sh，就可以运行 bash 或 sh，从而绕过 RBASH 的限制。

  * 这个方法的优点是：比较灵活，可以使用不同的编程语言或工具来实现相同的效果，只要 RBASH 允许使用它们就可以。

  * 这个方法的缺点是：需要一定的编程知识和技巧，如果 RBASH 禁止使用这些编程语言或工具，或者限制它们的功能或参数，就无法使用这个方法。

### 使用 ssh 命令

  * 如果 RBASH 允许使用 ssh 命令，那么用户可以利用它的 -t 选项或 ProxyCommand 选项来执行 /bin/bash 或 /bin/sh。例如：

    
    
    rbash$ ssh -t localhost /bin/bash  
    tom@localhost's password:   
    bash$ whoami  
    tom  
    bash$ pwd  
    /home/tom  
    bash$ cd /  
    bash$ pwd  
    /

  * 这个方法的原理是：ssh 命令是一个用于远程登录和执行命令的工具。其中，-t 选项表示为远程命令分配一个伪终端（pseudo-terminal），ProxyCommand 选项表示使用一个代理程序来连接远程主机。因此，如果用户使用 -t 选项或 ProxyCommand 选项来执行 /bin/bash 或 /bin/sh，并指定 localhost 作为远程主机，就可以运行 bash 或 sh，并在本地显示它们的输出和交互界面，从而绕过 RBASH 的限制。

  * 这个方法的优点是：比较巧妙，不需要复制或修改 bash 或 sh，也不需要使用其他的命令或工具，只要有 ssh 命令就可以。

  * 这个方法的缺点是：需要使用 ssh 命令，如果 RBASH 禁止使用 ssh 命令，或者限制它的选项或参数，就无法使用这个方法。

### 使用 git 命令

  * 如果 RBASH 允许使用 git 命令，那么用户可以利用它的 help 子命令来执行 /bin/bash 或 /bin/sh。例如：

    
    
    rbash$ git help config  
    bash$ whoami  
    tom  
    bash$ pwd  
    /home/tom  
    bash$ cd /  
    bash$ pwd  
    /

  * 这个方法的原理是：git 命令是一个用于版本控制和协作开发的工具。其中，help 子命令表示显示 git 的帮助信息，它会调用一个指定的帮助查看器来显示文档。默认情况下，git 会使用 less 命令作为帮助查看器，而 less 命令是可以用来绕过 RBASH 的一个命令。因此，如果用户使用 git help config 来显示 git config 的帮助信息，就可以在 less 的交互模式下使用 !/bin/bash 或 !/bin/sh 来执行一个外部命令，从而绕过 RBASH 的限制。

  * 这个方法的优点是：比较隐蔽，不容易被 RBASH 发现和阻止，因为 git help config 看起来是一个合法的命令，而且 ! 子命令不会在历史记录中显示。

  * 这个方法的缺点是：需要使用 git 命令，如果 RBASH 禁止使用 git 命令，或者修改它的帮助查看器或文档，就无法使用这个方法。

### 使用 pico 命令

  * 如果 RBASH 允许使用 pico 命令，那么用户可以利用它的 -s 选项来执行 /bin/bash 或 /bin/sh。例如：

    
    
    rbash$ pico -s /bin/bash  
    bash$ whoami  
    tom  
    bash$ pwd  
    /home/tom  
    bash$ cd /  
    bash$ pwd  
    /

  * 这个方法的原理是：pico 命令是一个简单的文本编辑器。其中，-s 选项表示指定一个拼写检查程序来检查文档中的拼写错误。默认情况下，pico 会使用 spell 命令作为拼写检查程序，而 spell 命令是可以用来绕过 RBASH 的一个命令。因此，如果用户使用 -s 选项来指定 /bin/bash 或 /bin/sh 作为拼写检查程序，并打开一个空白的文档，就可以运行 bash 或 sh，并在本地显示它们的输出和交互界面，从而绕过 RBASH 的限制。

  * 这个方法的优点是：比较巧妙，不需要复制或修改 bash 或 sh，也不需要使用其他的命令或工具，只要有 pico 命令就可以。

  * 这个方法的缺点是：需要使用 pico 命令，如果 RBASH 禁止使用 pico 命令，或者修改它的拼写检查程序或选项，就无法使用这个方法。

## 总结

  * RBASH 是一种受限制的 shell，它限制了用户的一些操作和权限。

  * RBASH 绕过的目的是获得一个正常的 shell，或者执行一些被禁止的命令或操作。

  * RBASH 绕过的方法有很多，主要取决于 RBASH 的限制程度和用户的目标是什么。

  * 在本讲义中，我们介绍了以下几种常见的 RBASH 绕过的方法，并举例论证它们的具体操作方式：

    * 使用 / 符号

    * 使用 cp 命令

    * 使用 ftp, gdb, more, man, less, vim, rvim 等命令

    * 使用 awk, find, expect, python, php, perl, lua, ruby 等编程语言或工具

    * 使用 ssh 命令

    * 使用 git 命令

    * 使用 pico 命令

    * 使用 vi 命令


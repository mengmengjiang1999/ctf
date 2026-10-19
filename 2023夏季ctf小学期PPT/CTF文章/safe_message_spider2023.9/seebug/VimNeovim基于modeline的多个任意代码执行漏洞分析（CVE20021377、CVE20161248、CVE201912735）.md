**作者：fenix@知道创宇 404 实验室**  
**日期：2019 年 6 月 11 日**  
**英文版本：<https://paper.seebug.org/956/>**

# 前言

Vim 是从 vi 发展出来的一个文本编辑器。代码补全、编译及错误跳转等方便编程的功能特别丰富，在程序员中被广泛使用，和 Emacs 并列成为类 Unix
系统用戶最喜欢的文本编辑器。Neovim 是一个基于 vim 源代码的重构项目。

2019 年 06 月 04 日，Vim & neovim 被曝出任意代码执行漏洞。攻击者通过诱使受害者使用 vim 或者 neovim
打开一个精心制作的文件，可以在目标机器上执行任意命令。

该漏洞是由于启用了 modeline 模式导致的，Vim & neovim 历史上也多次曝出和 modeline 相关的漏洞。

原作者已经分析的很清楚了，本文权当总结一下，顺便对历史曝出的多个漏洞做一次完整的分析。（在 vim 环境下，neovim 类似）

# modeline 详解

既然都是和 modeline 相关的漏洞，那就有必要知道 modeline 是什么。

vim 一共有 4 种模式：正常模式、插入模式、命令模式、可视模式。

在正常模式中，按下 `:` 键，就可以进入命令模式。在命令模式中可以执行一些输入并执行一些 vim 或插件提供的指令，就像在 shell
里一样。这些指令包括设置环境、文件操作、调用某个功能、执行命令等等。例如设置不显示行号：

![](https://images.seebug.org/content/images/2019/06/d188636b-23c6-4fac-a466-cdfe5bd9fb2b.jpg-w331s)

如果有很多偏好设置，每次打开文件都手动设置就会显得很繁琐，这时候 `.vimrc` 就派上用场了，在启动 vim 时，当前用户根目录下的 .vimrc
文件会被自动加载。

![](https://images.seebug.org/content/images/2019/06/c1f9e1ac-d490-42b3-8013-69b96d807ede.jpg-w331s)

.vimrc 中的设置会对打开的所有文件生效，不便于对单个文件作个性化设置，modeline 应运而生。

vim 的 modeline 可以让你针对每个文件进行文件级别的设置，这些设置是覆盖当前用户的 .vimrc 中的设置的。vim 默认关闭了
modeline，在 .vimrc 末尾追加 `set modeline` 即可打开。

如果 modeline 打开，vim 在打开文件时会解析文件开头及末尾符合一定格式的设置行。

格式一：

![](https://images.seebug.org/content/images/2019/06/12e71724-b345-4e0a-8963-78187587e1d0.jpg-w331s)

格式二：

![](https://images.seebug.org/content/images/2019/06/d1a32a8b-34f9-4e7c-ae9d-3fb5ea3013a8.jpg-w331s)

为了安全考虑，在 modeline 的设置中只支持 set 命令。

![](https://images.seebug.org/content/images/2019/06/d66d5ef1-4da5-4e23-81c9-94d1d83d1504.jpg-w331s)

特殊的，foldexpr，formatexpr，includeexpr，indentexpr，statusline，foldtext
等选项的值可以是一个表达式，如果选项是在 modeline 中设置，表达式在沙箱中执行。沙箱实质上就是对表达式所能实现的功能做了限制，如在沙箱中不能执行
shell 命令、不能读写文件、不能修改缓冲区等等，如下：

![](https://images.seebug.org/content/images/2019/06/d5204780-90e4-4231-950d-cd6396d5f3cb.jpg-w331s)

vim 对于沙箱的实现也很简单。

沙箱检查函数 check_secure()：

![](https://images.seebug.org/content/images/2019/06/e1c3315f-45d5-420d-8714-b4e0a0efb16f.jpg-w331s)

在 libcall、luaeval 等危险指令的开头进行沙箱检查，如果发现在沙箱中调用，直接 return 掉。

![](https://images.seebug.org/content/images/2019/06/d36c9e97-323a-4637-8104-9cb05a9140c9.jpg-w331s)

历史曝出的几个 rce 漏洞中，CVE-2002-1377 和 CVE-2019-12735 都是由于存在部分指令没有检查沙箱，导致在 modeline
模式中被滥用从而任意命令执行。下面将一一分析。

# CVE-2002-1377

2002 年曝出的 vim 任意代码执行漏洞，影响 6.0、6.1 版本。太过古老，环境难以重现，简单说下原理。PoC 如下：

    
    
    /* vim:set foldmethod=expr: */
    /* vim:set foldexpr=confirm(libcall("/lib/libc.so.6","system","/bin/ls"),"ms_sux"): */

利用 libcall 指令调用 libc 库中的 system 函数实现任意命令执行。

![](https://images.seebug.org/content/images/2019/06/e961234e-a4c4-4685-8d48-abb7ee208ed7.jpg-w331s)

现在添加了沙箱检查，modeline 下已经用不了 libcall 了：

![](https://images.seebug.org/content/images/2019/06/cea0eaf2-18ec-411e-bcaf-a41c37d98379.jpg-w331s)

# CVE-2016-1248

8.0.0056 之前的 vim 未正确验证 filetype、syntax 、keymap 选项的值，受害者在 modeline
开启下打开特制的文件，则可能导致执行任意代码。

从 github 克隆代码，checkout 到 v8.0.0055 分支，编译安装。.vimrc 的配置如下：

![](https://images.seebug.org/content/images/2019/06/ccc3351a-35e9-409d-b381-6caf26e562d5.jpg-w331s)

验证 PoC ：

    
    
    00000000: 2f2f 2076 696d 3a20 7365 7420 6674 3d00  // vim: set ft=.
    00000010: 2165 6368 6f5c 2070 776e 6564 203a 200a  !echo\ pwned : .

`set verbose=20`开启所有日志，看下调用链：

![](https://images.seebug.org/content/images/2019/06/33bcbfd7-8833-4d5e-9f33-79e78097cd94.jpg-w331s)

autocommand 即“自动命令”，在发生某些事件时自动执行，类似于钩子函数。

比如我们在命令模式中输入 `:set syntax=python`, vim 就会在相应目录中寻找和 python syntax 相关的 vmscript
并加载。

![](https://images.seebug.org/content/images/2019/06/c3c87167-3021-4e1c-a049-40793fd39d82.jpg-w331s)

如果我们在 modeline 中设置了 filetype 或者 syntax，会执行 `au! FileType * exe "set syntax=" .
expand("<amatch>")` 自动完成上述过程。首先删除所有和 FileType 相关联的自动命令，然后调用 exe （即 execute） 执行
`set syntax=filetype`。execute 用于执行一个表达式字符串，由于未对 filetype 过滤，造成了命令注入。

相关代码在 /usr/local/share/vim/vim80/syntax/syntax.vim:

![](https://images.seebug.org/content/images/2019/06/e236c8e5-9466-4eb2-a68e-854ad7e714b0.jpg-w331s)

patch 8.0.0056 增加了对名称的校验。

![](https://images.seebug.org/content/images/2019/06/a34d540c-2ab2-44ea-be38-455684337e88.jpg-w331s)

# CVE-2019-12735

最近刚曝出来，影响 Vim < 8.1.1365，Neovim < 0.3.6。和 CVE-2002-1377
原理类似，找到了一个新的绕过沙箱执行命令的点。source 指定的定义如下：

![](https://images.seebug.org/content/images/2019/06/4d91e03d-e1a9-4f2c-b532-e8d68b8d8343.jpg-w331s)

`:so! filepath` 可以从一个文件加载 vim 命令。

![](https://images.seebug.org/content/images/2019/06/069090d7-52cb-4391-b522-8bde7f92596d.jpg-w331s)

构造 PoC，将待执行的命令放在 text 部分，`so! %` 加载当前文件。

[text]{white}{vi:|vim:|ex:}[white]{options}

![](https://images.seebug.org/content/images/2019/06/5cc50cb3-11e2-46dd-b1f6-3f419e51dd0b.jpg-w331s)

补丁对 source 指令添加了沙箱检查。

![](https://images.seebug.org/content/images/2019/06/bc961528-b2c4-40aa-946f-492b5726c5e4.jpg-w331s)

# 总结

Windows 记事本都任意代码执行了，Vim 怎么能被比下去 … 漏洞无处不在，谨慎打开任何来历不明文件。

# 参考链接

<https://github.com/numirias/security/blob/master/doc/2019-06-04_ace-vim-neovim.md>

<https://github.com/vim/vim/commit/d0b5138ba4bccff8a744c99836041ef6322ed39a>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/952/>


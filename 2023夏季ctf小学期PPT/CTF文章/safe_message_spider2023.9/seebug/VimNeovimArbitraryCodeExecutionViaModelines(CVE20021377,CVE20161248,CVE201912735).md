**Author: fenix@Knownsec 404 Team**  
**Chinese Version:<https://paper.seebug.org/952/>**

# Introduction

Vim is a terminal text editor, an extended version of vi with additional
features, including syntax highlighting, a comprehensive help system, native
scripting (vimscript), a visual mode for text selection, comparison of files
and so on. Vim and Emacs are the dominant text editors on Unix-like operating
systems, and have inspired the editor wars. Neovim is a reconstruction project
of Vim aiming to improve the user experience.

On June 4, 2019, an arbitrary code execution vulnerability has been discoverd
in Vim/neovim. The attacker can execute arbitrary commands on the target
machine by cheating the victim to open a specially crafted text file via vim
or neovim.

The vulnerability was caused by the implementation of the modeline. There have
been several other modeline-related vulnerabilities patched, such as
CVE-2002-1377, CVE-2016-1248.

Arminius has analyzed the CVE-2019-12735 very clearly. This article is a
summaryand a complete analysis of the multiple vulnerabilities discoverd in
the past(neovim is similar to the vim environment).

# About Modeline

Since all vulnerabilities are related to modeline, it is necessary to know
what modeline is.

There are four modes in vim: normal mode, insert mode, command mode, and
visual mode.

In normal mode, press the `:` to enter command mode. In command mode you can
execute some commands provided by vim or plugin, just like in a shell. These
commands include setting the environment, operating files, calling a function,
executing a shell command, and so on. For example, we set it not display the
line number:

![](https://images.seebug.org/content/images/2019/06/d188636b-23c6-4fac-a466-cdfe5bd9fb2b.jpg-w331s)

If you have a lot of preferences, it will be extremely time-consuming to
manually set the environment each time. At this time, `.vimrc` comes in handy.
When vim is started, the .vimrc file in the current user root directory will
be loaded automatically.

![](https://images.seebug.org/content/images/2019/06/c1f9e1ac-d490-42b3-8013-69b96d807ede.jpg-w331s)

The settings in .vimrc take effect for all files that you open, making it
difficult to personalize individual files, which is why the modeline comes
into being.

Vim's modeline makes it possible for you to perform file-level settings for
each file, which overrides the settings of the current users .vimrc. Vim turns
off modeline by default, and appending `set modeline` to the end of .vimrc can
open it.

If modeline is turned on, vim will parse the setting lines that matches the
format at the beginning and end of the file when opening it.

There are two forms of modelines. The first form:

![](https://images.seebug.org/content/images/2019/06/12e71724-b345-4e0a-8963-78187587e1d0.jpg-w331s)

The second form:

![](https://images.seebug.org/content/images/2019/06/d1a32a8b-34f9-4e7c-ae9d-3fb5ea3013a8.jpg-w331s)

For security reasons, no other commands than "set" are supported(somebody
might create a Trojan text file with modelines).

![](https://images.seebug.org/content/images/2019/06/d66d5ef1-4da5-4e23-81c9-94d1d83d1504.jpg-w331s)

In particular, the values of options such as 'foldexpr', 'formatexpr',
'includeexpr', 'indentexpr', 'statusline', 'foldtext' can be an expression. If
the option is set in modeline, the expression can be executed in the sanbox.
The sanbox is essentially a limitation on what the expression can do, for
example, you cannot execute shell commands, read and write files, or modify
the buffer in the sanbox:

![](https://images.seebug.org/content/images/2019/06/d5204780-90e4-4231-950d-cd6396d5f3cb.jpg-w331s)

The implementaion of the sanbox in vim is also very simple.

Sanbox checks function `check_secure()`:

![](https://images.seebug.org/content/images/2019/06/e1c3315f-45d5-420d-8714-b4e0a0efb16f.jpg-w331s)

Sanbox checks at the beginning of dangerous commands such as libcall, luaevel,
etc.. If calling is found in the sanbox, the funcion will return diretly.

![](https://images.seebug.org/content/images/2019/06/d36c9e97-323a-4637-8104-9cb05a9140c9.jpg-w331s)

Among the several RCE vulnerabilities discoverd in the past, CVE-2002-1377 and
CVE-2019-12735 are due to the fact that some commands do not check the
sandbox, resulting in abuse in the modeline mode for arbitrary command
execution.

# CVE-2002-1377

The arbitrary code execution vulnerability discoverd in 2002 affects vim
versions 6.0 and 6.1. It has been such a long time that the enviroment is
difficult to reproduce.

Proof of Concept:

    
    
    /* vim:set foldmethod=expr: */
    /* vim:set foldexpr=confirm(libcall("/lib/libc.so.6","system","/bin/ls"),"ms_sux"): */

Achieving arbitrary commands execution by using the libcall feature in
modelines.

![](https://images.seebug.org/content/images/2019/06/e961234e-a4c4-4685-8d48-abb7ee208ed7.jpg-w331s)

Sanbox check has been added, and libcall cannot be called under modeline.

![](https://images.seebug.org/content/images/2019/06/cea0eaf2-18ec-411e-bcaf-a41c37d98379.jpg-w331s)

# CVE-2016-1248

Vim before patch 8.0.0056 does not properly validate values for the
'filetype', 'syntax' and 'keymap' options, which may result in the execution
of arbitrary code if a file with a specially crafted modeline is opened.

Clone the vim repository from github. Switch to the v8.0.055 branch, and then
compile and install. The content of .vimrc is as follows:

![](https://images.seebug.org/content/images/2019/06/ccc3351a-35e9-409d-b381-6caf26e562d5.jpg-w331s)

Proof of Concept：

    
    
    00000000: 2f2f 2076 696d 3a20 7365 7420 6674 3d00  // vim: set ft=.
    00000010: 2165 6368 6f5c 2070 776e 6564 203a 200a  !echo\ pwned : .

Generally debugging with Verbose. set verbose to 20, it gives you output that
everything vim is doing. Look at the call chain：

![](https://images.seebug.org/content/images/2019/06/33bcbfd7-8833-4d5e-9f33-79e78097cd94.jpg-w331s)

Autocommand is a way to tell Vim to run certain commands when certain events
happen. Let's dive right into an example.

If we type `:set syntax=python` in the command mode, vim will look for
vmscript related to python syntax in the corresponding directory and load it.

![](https://images.seebug.org/content/images/2019/06/c3c87167-3021-4e1c-a049-40793fd39d82.jpg-w331s)

If we set filetype or syntax in modeline, `au! FileType * exe "set syntax=" .
expand("<amatch>")` will be triggered to complete the above process. Remove
all autocommands associated with FileType firstly and then call exe (ie
execute) to execute `set syntax=filetype`. "exe" command is used to execute an
expression string, resulting in command injection because the filetype has not
been validated and sanitized.

Related code is in `/usr/local/share/vim/vim80/syntax/syntax.vim`.

![](https://images.seebug.org/content/images/2019/06/e236c8e5-9466-4eb2-a68e-854ad7e714b0.jpg-w331s)

Patch 8.0.0056 adds filetype check, only allowing valid characters in
'filetype', 'syntax' and 'keymap'.

![](https://images.seebug.org/content/images/2019/06/a34d540c-2ab2-44ea-be38-455684337e88.jpg-w331s)

# CVE-2019-12735

It has been disclosed recently, affecting Vim < 8.1.1365 and Neovim < 0.3.6.
Similar to the CVE-2002-1377, a new point used to bypass the sanbox has been
found. The definition of source command is as follows.

![](https://images.seebug.org/content/images/2019/06/4d91e03d-e1a9-4f2c-b532-e8d68b8d8343.jpg-w331s)

`:so! filepath` can read vim commands from filepath。

![](https://images.seebug.org/content/images/2019/06/069090d7-52cb-4391-b522-8bde7f92596d.jpg-w331s)

Construct the PoC: put the command to be executed in the text section, and use
`so! %` to load the current file.

[text]{white}{vi:|vim:|ex:}[white]{options}

![](https://images.seebug.org/content/images/2019/06/5cc50cb3-11e2-46dd-b1f6-3f419e51dd0b.jpg-w331s)

Patch 8.1.1365: checks for the sandbox when sourcing a file.

![](https://images.seebug.org/content/images/2019/06/bc961528-b2c4-40aa-946f-492b5726c5e4.jpg-w331s)

# Conclusion

A arbitrary code execution zero-day vulnerability was found in notepad some
days ago. It seems vim doesn't like falling behind either.

Vulnerabilities are everywhere, and be cautious to open any unknown files.

# Reference

https://github.com/numirias/security/blob/master/doc/2019-06-04_ace-vim-neovim.md

https://github.com/vim/vim/commit/d0b5138ba4bccff8a744c99836041ef6322ed39a

# About Knownsec & 404 Team

Beijing Knownsec Information Technology Co., Ltd. was established by a group
of high-profile international security experts. It has over a hundred frontier
security talents nationwide as the core security research team to provide
long-term internationally advanced network security solutions for the
government and enterprises.

Knownsec's specialties include network attack and defense integrated
technologies and product R&D under new situations. It provides visualization
solutions that meet the world-class security technology standards and enhances
the security monitoring, alarm and defense abilities of customer networks with
its industry-leading capabilities in cloud computing and big data processing.
The company's technical strength is strongly recognized by the State Ministry
of Public Security, the Central Government Procurement Center, the Ministry of
Industry and Information Technology (MIIT), China National Vulnerability
Database of Information Security (CNNVD), the Central Bank, the Hong Kong
Jockey Club, Microsoft, Zhejiang Satellite TV and other well-known clients.

404 Team, the core security team of Knownsec, is dedicated to the research of
security vulnerability and offensive and defensive technology in the fields of
Web, IoT, industrial control, blockchain, etc. 404 team has submitted
vulnerability research to many well-known vendors such as Microsoft, Apple,
Adobe, Tencent, Alibaba, Baidu, etc. And has received a high reputation in the
industry.

The most well-known sharing of Knownsec 404 Team includes: [KCon Hacking
Conference](http://kcon.knownsec.com/#/ "KCon Hacking Conference"), [Seebug
Vulnerability Database](https://www.seebug.org/ "Seebug Vulnerability
Database") and [ZoomEye Cyberspace Search Engine](https://www.zoomeye.org/
"ZoomEye Cyberspace Search Engine").

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/956/>


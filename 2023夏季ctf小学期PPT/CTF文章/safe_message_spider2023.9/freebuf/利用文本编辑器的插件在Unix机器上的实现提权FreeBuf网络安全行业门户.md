**近期，SafeBreach的安全研究人员发现，攻击者可利用Unix环境下多款当前热门的文本编辑器插件来在目标系统上实现权限提升。**

![1.png](https://image.3001.net/images/20180322/15217149133922.png!small)  

研究人员表示，他们对Sublime、Vim、Emacs、Gedit、Pico以及Nano（从Ubuntu设备克隆）等编辑器进行了安全测试，除了Pico和Nano之外，他们都可以利用其他文本编辑器加载插件过程中的安全漏洞来成功在目标主机中实现提权。

## 问题出在哪里？

这些文本编辑器主要通过第三方插件来扩展其功能，而这些插件都是由其他用户或开发者开发的，并且其中有很多都是开放了源代码的。

SafeBreach的安全研究人员Dor Azouri表示：

>
> “我们通过对这些文本编辑器进行了测试之后发现，它们一般有两种模式，即常规模式和提权模式。当它们在加载插件时，便会进入提权模式，但是由于它们对文件夹权限完整性的控制做得并不到位，因此仅拥有普通用户权限的攻击者将可以利用这个漏洞实现提权，并在目标主机上执行任意代码。
>
>
> 假设现在攻击者只能在目标主机上运行任意代码，但并没有实现提权。那么他们现在就可以向文本编辑器当前所使用的文件夹中写入恶意插件代码，然后等待编辑器切换到提权模式，而此时用户将需要输入设备的root密码。当然了，对于某些“高端”用户来说，攻击者可能只需要等一会儿就可以完成攻击了，因为这些用户往往需要安装各种功能扩展插件，或者通常需要使用sudo命令来打开各种文件。但是在某些情况下，攻击者可能得永远等待下去了…”

## 细节描述

注：本文以Sublime和VIM为例进行攻击讲解，所有的相关代码以及内容描述都可以在SafeBreach的GitHub代码库中找到【[传送门](https://github.com/SafeBreach-Labs/blog-snippets)】。

### Sublime

测试环境：

> Sublime Version: 3.0 Build 3143
>
> Ubuntu 14.04.5, Kernel 4.13.0

添加插件

Sublime插件主要有以下两种形式：

> 1\. 安装包（使用包管理工具直接安装）；
>
> 2\. 单独的Python插件文件；

第一种形式由Package Control负责管理（一般是sublime-package文件），目录路径一般为：

    
    
    /opt/sublime_text

第二种形式就是一种Python文件，路径地址为：

    
    
    ~/.confg/sublime-text-3/Packages/User

如果你想让插件来处理编辑器事件，你就需要实现sublime_plugin.EventListener类的子类，然后重写某些事件回调，你的首选一般是on_actvated_async。这种特殊的事件意思是“当一个视图获取到了输入焦点时便会调用该方法，然后程序将以单独的线程运行。”因此，每当用户切换编辑器标签tab时，或者当Sublime打开时，都需要调用这个回调方法【[API文档](https://www.sublimetext.com/docs/3/api_reference.html#sublime_plugin.EventListener)】。

接下来，攻击者只需要在完整的Python环境下实现恶意代码即可完成攻击。

### VIM

测试环境：

> Vim Versions: 7.4 & 8.0
>
> Ubuntu 14.04.5, Kernel 4.13.0

为了在VIM中复现攻击场景，我们需要定位相关插件的存储位置，而且我们还需要弄清楚如何在启动时加载插件。攻击的核心思想如下：

> 1\. 开发自己的Python攻击脚本。
>
> 2\. 将它存储在~/.vim/plugin/中。
>
> 3\.
> 在同一目录下创建一个新的*.vim文件，这个文件为实际的vim插件，它将会在编辑器启动过程中与其他插件一起加载。在我们的测试场景下，我们将演示如何使用Python脚本实现攻击（看起来有点像VimScript）：
    
    
    if !has('python') && !has('python3')
    
     finish
    
    endif
    
    function! RootWrite()
    
     If has('python')
    
     pyfile ~/.vim/plugin/write_root_file.py
    
     else
    
     py3file ~/.vim/plugin/write_root_file.py
    
              endif
    
    endfunc
    
    call RootWrite()

4.我们开发的write_root_file.py脚本会尝试向受保护的路径地址（只有root用户拥有写入权限）写入一份文件：

    
    
    try:
    
     f = open("/stub.file", "wb")
    
     f.close()
    
    except IOError as e:
    
     pass

关于这种攻击技术的更多细节描述，请参考研究人员发布的【[研究报告](https://go.safebreach.com/rs/535-IXZ-934/images/Abusing_Text_Editors.pdf)】。

## 缓解方案

研究人员已经将他们所发现的问题提交给了Sublime、Vim、Emacs和Gedit的开发人员，但是报告中并没有提到相关的缓解方案。

对此，研究人员的建议是：完善文件/文件夹权限模型，并且保证编辑器可以正常地在常规模式和提权模式之间切换。他们也可以让编辑器在提权模式下运行时，阻止加载第三方插件。或者说，给用户提供一个手动接口来以提权模式加载插件。当然了，他们也可以使用类似sudoedit这样的内置命令（而不是以root权限）来允许普通用户安全地编辑文件内容。

除此之外，研究人员还给广大管理员提供了一份[OSSEC](https://en.wikipedia.org/wiki/OSSEC)
syscheck配置规则【[点我获取](https://github.com/SafeBreach-Labs/blog-snippets/blob/master/editors_plugins_fifth_column/ossec.conf)】，大家可以利用这份配置文件来监控文件或文件夹的修改情况。

### OSSEC监控规则

监控你设备中关键文件以及文件夹的修改情况，比如说，你可以将下列规则添加到OSSEC syscheck配置文件之中：

    
    
    /var/ossec/etc/ossec.conf：
    
    <syscheck>
    
          <directoriescheck_all="yes" realtime="yes"report_changes="yes">
    
     ~/.config/sublime-text-3/Packages/User
    
     </directories>
    
     <directories check_all="yes"realtime="yes" report_changes="yes">
    
     ~/.vim/plugin/
    
     </directories>
    
     <directories check_all="yes"realtime="yes" report_changes="yes">
    
     ~/.emacs,
    
     ~/_emacs,
    
     ~/.emacs.d/init.el,
    
     ~/.xemacs,
    
     ~/.xemacs/init.el,
    
                 ~/Library/Preferences/AquamacsEmacs/Preferences.el
    
          </directories>
    
     <directories check_all="yes"realtime="yes" report_changes="yes">
    
     ~/.local/share/gedit/plugins
    
     </directories>
    
    </syscheck>

修改之后，别忘了使用下列命令重启OSSEC：

    
    
    sudo /var/ossec/bin/ossec-control restart

 ***
参考来源：[helpnetsecurity](https://www.helpnetsecurity.com/2018/03/20/privilege-escalation-unix/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


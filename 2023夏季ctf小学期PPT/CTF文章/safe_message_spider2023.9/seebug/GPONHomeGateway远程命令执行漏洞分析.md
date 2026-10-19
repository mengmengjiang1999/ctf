**作者：dawu@知道创宇404实验室**  
**日期：2018/05/04**  
**英文版本：<https://paper.seebug.org/983/>**

#### 0x00 前言

2018/04/30，`vpnMentor`公布了 `GPON`
路由器的高危漏洞：验证绕过漏洞(CVE-2018-10561)和命令注入漏洞(CVE-2018-10562)。将这两个漏洞结合，只需要发送一个请求，就可以在
`GPON路由器` 上执行任意命令。本文在复现该漏洞的基础上，分析了相关漏洞形成的原因。

#### 0x01 漏洞文件定位

在有回显的远程命令执行漏洞中，使用 `ps` 命令往往能够很好地定位到漏洞点。

![](https://images.seebug.org/content/images/2018/05/9266f108-cbb4-41f6-a873-7b9de36b318f.png-w331s)

可以很明显地看到，进程14650执行了我们的命令，找到上一个进程`14649 root /bin/WebMgr -p 20 -s 0`。因为 `pid`
是递增的，所以很可能是 `/bin/WebMgr` 这个文件存在漏洞。

#### 0x02 漏洞分析

在获取到某设备的 `/bin/WebMgr` 和 `/lib/` 文件后，我们开始分析。

##### 2.1 分析前

分析前研究了这个漏洞的利用，发现了该web服务器是 `GoAhead-webs`

![](https://images.seebug.org/content/images/2018/05/2a5f7016-fc3e-4c50-ba6b-dc53d37f5376.png-w331s)

根据 `Server`字段判断，该web服务器的版本 <= `GoAhead 2.5.0`（`GoAhead 3.x` 版本的 `Server` 默认为
`GoAhead-http`）

在尝试 `https://www.seebug.org/search/?keywords=goahead&page=2`已有的 `GoAhead 2.x`
系列的漏洞无果，推测该web服务器可能基于 `GoAhead2.5.0`版本进行了二次开发。

### 2.2 验证绕过漏洞

用 `ida` 打开 `WebMgr` 后发现函数流程并不完整，所以使用了简单粗暴的方式，直接搜索 `images/`，定位到函数
`webLoginCheck`

![](https://images.seebug.org/content/images/2018/05/7e7e318c-07d3-40e3-b7f1-507abcf7a103.png-w331s)

![](https://images.seebug.org/content/images/2018/05/3467c6cd-585c-4be4-aae6-9aa39ce2fb59.png-w331s)

但是该函数在 `WebMgr` 中并没有被调用，故这里我们结合漏洞作出合理猜测：

**当该函数 return 0时表示不需要验证**

结合函数逻辑，我们可以知道：当 `url` 中含有 `style/`,`script/`时也可以绕过验证。
![](https://images.seebug.org/content/images/2018/05/d9333728-4a68-4ae0-a6fd-48b76b40fc15.png-w331s)

##### 2.3 命令执行漏洞

由于之前读过 `GoAhead 2.1.8`的源码，所以知道 `WebMgr` 中定义 `cgi` 的逻辑为：

**先通过 websFormDefine 定义不同的cgi接口要调用的函数，然后再通过 websUrlHandlerDefine 加载
websFormHandler**

举个例子：

    
    
    websFormDefine((int)"FLoidForm", (int)sub_1C918);
    websUrlHandlerDefine("/GponForm", 0, 0, &websFormHandler, 0);

这意味着当 `url` 中的 `path` 以 `/GponForm` 开头时，会使用 `websFormHandler` 去处理，然后
`websFormHandler` 会寻找通过 `websFormDefine()` 定义的各种路径，然后调用对应的函数。 在这里，就是访问
`/GponForm/FloidForm` 时会调用 `sub_1C918` 完成相关操作。

在 `exp` 中，通过对 `/GponForm/diag_Form` 发送请求最终实现了命令执行。根据上文，可以找到
`/GponForm/diag_Form` 调用了函数 `sub_1A390`，结合 `system()` 的调用流程，我们可以知道 `sub_1A390`
调用了 `sub_1A684`，最终通过 `system()` 执行命令。

![](https://images.seebug.org/content/images/2018/05/50dd44b3-8df2-4df5-a43b-07a2ad6f57de.png-w331s)

按照流程分析入下图：

![](https://images.seebug.org/content/images/2018/05/f523e911-c87c-4244-a028-13f95ec97e20.png-w331s)

在 `sub_1A684`中， 主要还是判断传入的 `dest_host` 是否合法。如果不合法或者无法解析，将会进行如下处理：

![](https://images.seebug.org/content/images/2018/05/f1d6929b-bced-4beb-844a-b6c1edbfd9e9.png-w331s)

这也可以从我们第一张图：执行 `ps` 命令的结果中得到验证。

![](https://images.seebug.org/content/images/2018/05/6c261da3-a93d-4e4c-a68b-76746b0d174c.png-w331s)

#### 0x03 影响范围

根据 `ZoomEye网络空间搜索引擎` 的探测结果，一共有 `2141183` 台路由器可能受该漏洞影响。

![](https://images.seebug.org/content/images/2018/05/7d49fe7d-f658-4291-9e07-cf580f177975.png-w331s)

相关国家分布如图所示：

![](https://images.seebug.org/content/images/2018/05/293548a8-623f-41a4-8fb7-cdb589544714.png-w331s)

#### 0x04 结语

在分析漏洞后，我们尝试寻找该类路由器所属的厂商。在 `/web/images/`下，我们找到了多个国内外厂商的
`logo`,但是未有其它证据证明这些路由器属于这些厂商。

![](https://images.seebug.org/content/images/2018/05/c29cb59f-57e1-42dd-93d3-c4445f08b60a.png-w331s)

在查阅其它资料后，我们更倾向于这些路由器是 `OEM` 或者 `ODM`
出来的产品。因为很难找到生产厂商，所以修复工作将会更加困难。由于该漏洞影响范围广，利用简单，危害巨大，各大僵尸网络家族很可能会将该漏洞列入其利用库，需要警惕。

#### 0x05 参考链接

  1. `vpnMentor`公布的 `GPON` 路由器的漏洞  
<https://www.vpnmentor.com/blog/critical-vulnerability-gpon-router/>

  2. `Seebug漏洞平台` 收录该漏洞  
<https://www.seebug.org/vuldb/ssvid-97258>

  3. `ZoomEye网络空间搜索引擎` 搜索结果  
<https://www.zoomeye.org/searchResult?q=%22GPON%20Home%20Gateway%22>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/593/>


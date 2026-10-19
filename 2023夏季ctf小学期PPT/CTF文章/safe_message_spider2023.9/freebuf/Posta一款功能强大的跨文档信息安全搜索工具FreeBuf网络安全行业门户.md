![](https://image.3001.net/images/20210427/1619531953_608818b154c62103d9ac2.png!small)

## 关于Posta

Posta是一款功能强大的跨文档信息安全搜索工具，广大研究人员可以使用Posta来研究跨文档的信息通信，它允许我们跟踪、探测和利用postMessage漏洞，而且还可以重放任何绑定窗口和浏览器之间的消息。

![](https://image.3001.net/images/20210427/1619531969_608818c159926fba45883.png!small)

## 工具要求

> Chrome Chrome / Chromium
>
> Node.js（可选）

## 工具安装

### 开发环境

我们可以在专用浏览器（Chromium）中以完整的开发环境运行Posta。

首先，我们需要运行下列命令来安装Posta：

    
    
    git clone https://github.com/benso-io/posta
    
    cd posta
    
    npm install

接下来，使用下列命令启动专用Chromium会话：

    
    
    node posta <URL>

最后，点击Posta扩展并导航至工具用户UI界面。

开发模式包含一台本地Web服务器，它负责托管一个小型的测试网站和漏洞利用页面。以开发模式运行时，我们可以访问http://localhost:8080/exploit/来访问漏洞利用页面。

### Chrome扩展

我们还能够以Chrome / Chromium扩展的形式来运行Posta。

首先，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/benso-io/posta.git

接下来，访问chrome://extensions，此时需要确保浏览器为开发者模式。然后点击“Load upacked”，选择Posta中的chrome-extension目录，并将其上传至你的浏览器中，最后加载扩展。

将扩展与浏览器绑定之后，访问我们需要测试的网站，点击Posta扩展导航至UI界面即可。

## 工具使用

### Tabs

在Tabs下，你可以找到我们的源地址，其中包含对应的iframe和通信会话。我们可以选择指定的frame，并观察跟该frame相关的postMessages：

![](https://image.3001.net/images/20210427/1619532034_60881902a08a26038ff94.png!small)

### Messages

在Messages中，我们可以检查所有从源地址发送至iframes的postMessage流量。我们可以选择需要深入分析的通信会话，监听器部分会显示负责处理通信的相关代码，点击之后还可以直接拷贝代码内容：

![](https://image.3001.net/images/20210427/1619532041_60881909ea934a3433ad3.png!small)

![](https://image.3001.net/images/20210427/1619532049_60881911ade43337fb5de.png!small)

### Console

在Console部分，我们可以修改原始的postMessage流量，并使用篡改后的内容重放消息，这些信息将通过源地址发送至iframe。

我们可以通过修改postMessage的内容来查看目标站点是否会受这种攻击方式的影响。如果成功了，我们就可以尝试去从不同的源来利用该漏洞了，这一步可以通过点击“Simulate
exploit”实现：

![](https://image.3001.net/images/20210427/1619532058_6088191ac47f94342d325.png!small)

![](https://image.3001.net/images/20210427/1619532068_6088192402b196cfab24d.png!small)

### Exploit

点击“host”按钮即可导航至漏洞利用窗口：

![](https://image.3001.net/images/20210427/1619532081_608819313acaf5957079c.png!small)

在Exploit部分，Posta将会尝试并将特定源托管为iframe来初始化postMessage通信。但如果源网站启用了X-Frame-Options的话，我们大多数时候都无法执行攻击了。

因此，为了实现漏洞利用，我们还需要通过初始化window.open方法来获取到跟源地址绑定的通信引用，这里可以点击“Open as tab”来实现。

接下来，我们就可以点击“Exploit”按钮，并指定Payload进行跨源通信测试了：

![](https://image.3001.net/images/20210427/1619532109_6088194dec2e55f514d87.png!small)

## 项目地址

 **Posta：** https://github.com/benso-io/posta


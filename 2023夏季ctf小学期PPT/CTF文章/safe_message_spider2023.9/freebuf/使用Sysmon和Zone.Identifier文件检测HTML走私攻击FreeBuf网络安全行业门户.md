## 介绍

在此博客文章中，我将如何使用Sysmon检测HTML Smuggling攻击。

前提条件：熟悉NTFS的概念，以及如何使用Zone.Identifier
ADS标记从Internet下载的文件。如果不是的话，参考这篇入门[文章](https://textslashplain.com/2016/04/04/downloads-and-the-mark-of-the-web/)。

HTML走私是一种绕过外围防御（例如Web代理和安全电子邮件网关）的技术。文件被“走私”到HTTP响应的主体中，并使用JavaScript下载到用户的计算机上。这意味着监控软件只会看到网页，而不会看到走私的文件。[Outflank](https://outflank.nl/blog/2018/08/14/html-smuggling-explained/)和[NCC Group](https://www.nccgroup.com/uk/about-us/newsroom-and-events/blogs/2017/august/smuggling-hta-files-in-internet-exploreredge/)已更详细地介绍了该技术。

## Sysmon ID 15（FileCreateStreamHash）

从版本[11.10开始](https://blog.knogin.com/sysmon-11.10-threat-detection)，Sysmon可以记录ADS的内容。因此，如果HTML Smuggling在Zone.Identifier
ADS中工件，那么我们可以使用Sysmon来检测到发生了HTML Smuggling。

## 测试方法

为了测试每个浏览器，我使用了[Outflank.nl中的](https://outflank.nl/)[此](https://www.outflank.nl/demo/html_smuggling.html)文档。在浏览器中，我都是通过原始URL和本地保存的副本打开文档的。这是为了确定浏览器是否根据所使用的协议（`http://`或`https://`和`file://`）对下载的文件进行了不同的处理。

## 结果

### 浏览器版本经过测试

> Google Chrome版本88.0.4324.96（正式版本）（64位）
>
> Mozilla Firefox版本84.0.2（64位）
>
> Microsoft Edge（Chromium）版本88.0.705.50（官方版本）（64位）
>
> Microsoft Edge（旧版）版本44.18362.449.0

注意：通过“smuggling页面”，我的意思是例如https://www.outflank.nl/demo/html_smuggling.html或C:\Users\Joshua\Downloads\html_smuggling.html

Google Chrome，Firefox和Chromium Edge都表现出相同的行为。对于托管和本地走私页面，都创建了Zone.Identifier
ADS，但是HostUrl属性设置为 **about：internet** ，而不是原始页面。

![Sysmon HTML走私活动-Chrome，Firefox和Chromium
Edge](https://image.3001.net/images/20210226/1614348635_6039015bce576efeaf86c.png!small)

另一方面，Legacy Edge对这些文件的处理方式有所不同。通过HTTP(S)为走私页面提供服务时，将创建Zone.Identifier
ADS，并将HostUrl属性设置为原始页面，并以**blob：**开头。

![Sysmon HTML走私事件-旧版边缘-http：//](https://image.3001.net/images/20210226/1614348640_60390160897d63f7a5e5f.png!small)

当在本地提供走私页面时，则旧版Edge只会为下载的文档创建一个Zone.Identifier
ADS。现代电子邮件客户端将为来自互联网的电子邮件创建附件的Zone.Identifier
ADS，因此Sysmon仍应检测通过电子邮件发送的走私页面下载并在旧版边缘中打开的文件。

在这种情况下，HostUrl属性的原点为空，但是ReferrerUrl将指向走私页面。

![Sysmon HTML走私事件-旧版边缘-file：//](https://image.3001.net/images/20210226/1614348643_603901632c22c855e5360.png!small)

## 总结

  
| MOTW Created (http://)| MOTW Created (file://)| 流包含文档URL| 可识别的HTML走私  
---|---|---|---|---  
谷歌浏览器| 是的| 是的| 不| 是的  
火狐浏览器| 是的| 是的| 不| 是的  
Chromium Edge| 是的| 是的| 不| 是的  
旧版Edge| 是的| 这取决于*| 是的| 对于http://，是的，对于file://，取决于*  
  
对于本地走私页面（file://），如果走私页面只有一个，旧版Edge只会为下载的文件创建一个Zone.Identifier ADS。

## Sysmon规则

从以上结果中，我们可以看到Sysmon可以通过查找包含以下两个值之一的Zone.Identifier备用数据流来检测HTML Smuggling攻击：

> HostUrl=about:internet
>
> HostUrl=blob:

### Sysmon XML

    
    
    <RuleGroup name="" groupRelation="or">
        <FileCreateStreamHash onmatch="include">
    	<Rule name="HTML_Smuggling" groupRelation="and">
    	    <TargetFilename condition="end with">:Zone.Identifier</TargetFilename>
    	    <Contents condition="contains any">blob:;about:internet</Contents>		
    	</Rule>
        </FileCreateStreamHash>
    </RuleGroup>﻿


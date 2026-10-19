# 检测攻击的基础日志服务器 Part 3-4:Graylog仪表板&日志警报

阅读量 **201840**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-04-19 14:34:51

 **x**

##### 译文声明

本文是翻译文章，文章来源：https://thevivi.net/

原文地址：<https://thevivi.net/2018/03/23/attack-infrastructure-logging-part-3-graylog-dashboard-101/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01ac19abe63f09b83a.png)

## 一.写在前面的话

在这个博客系列的最后我会介绍如何设置一个日志服务器，并且从我们的各种攻击基础设施资产中收集日志。本文将介绍如何设置一个将这些日志数据可视化的仪表板，并创建一个日志报警系统。

## 二.Graylog仪表板

Graylog仪表板允许导入日志文件来构建可视汇总或快速统计数据。更厉害的是仪表板几乎可以显示任何一种数据类型。

**设置仪表板：**

进入仪表板菜单，点击“创建指示板”。创建一个新名字，然后添加描述并保存。

![](https://p2.ssl.qhimg.com/t01fe72bfb785a0ca63.png)

很好，我们现在已经创建了一个仪表板。接下来，我们为其添加一些小部件。

## 三.在仪表板中添加小部件:

小部件可以从通过Graylog的Search菜单添加到您的仪表板。您可以添加如统计值，搜索结果数量，IP地址地理位置信息（稍后详细介绍）等等小部件。

进入搜索菜单，在搜索框中输入“ssource：payload_server_hostname
”，选择一个时间段，然后点击进入。在下面的示例中，我的净载荷服务器的主机名为“payload”，并且搜索最后一天的日志。

![](https://p0.ssl.qhimg.com/t01da52ba1a059cad47.png)

接下来，滚动到搜索框下面的字段菜单中的“request”复选框，展开它并单击“Quick values”

![](https://p4.ssl.qhimg.com/t01010ddd08ea11eb91.png)

Graylog将自动为您生成数值，包括完整的饼形图和百分比。如图，我们可以看到evil.hta在过去24小时内已经下载了18次。

![](https://p0.ssl.qhimg.com/t013a037561f65c53ea.png)

如果你要将其添加到仪表板，只需点击小部件右上角的添加至仪表板按钮即可。

您可以根据需求对多个字段和日志重复此过程。例如，如果您希望看到由您的一个redirector生成的HTTP响应，只需搜索特定的redirector(例如，source:redirector1)即可。

![](https://p2.ssl.qhimg.com/t0187223fc6daf3c006.png)

再次单击Quick值，并让Graylog为您完成所有的工作。

![](https://p0.ssl.qhimg.com/t0103fddfd2ffc1d173.png)

稍微发挥一点脑洞，你可以打造一个高颜值的仪表盘，惊艳一下你的同事和客户们。

**小部件常见功能：**

1.TOP IP地址与您的web服务器的交互操作。  
2.统计邮件服务器信息，例如邮件发送。  
3.成功的网络钓鱼攻击日志。  
4.SSH登录记录。  
5.失败的登录尝试/暴力攻击记录。

## 四.地理位置:

请问在交互式世界地图上实时地定位IP地址是不是件非常酷的事？我不得不承认这是我建立中央日志的主要动机之一，谁不想让自己看起来像电影里的黑客呢？接下来我就介绍如何使用Graylog的地理定位功能，将世界地图添加到仪表板中。

您首先需要下载MaxMind的Geolite2城市数据库:

`cd / etc / graylog / server  
sudo wget
http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz  
sudo tar xvf GeoLite2-City.tar.gz`

注意:确保数据库文件可以通过Graylog读取。

接下来，我们需要启用Graylog的地理定位功能。进入系统“配置”菜单，点击“地理位置处理器插件”部分的“更新”按钮。

![](https://p1.ssl.qhimg.com/t015bfff681c133e458.png)

启用地理定位处理器，并将完整的路径输入到您的地理位置数据库中。

![](https://p0.ssl.qhimg.com/t010441b5f4edcad03f.png)

一旦你启用了位置处理器;在消息处理器配置部分点击Update。

![](https://p3.ssl.qhimg.com/t01e27d4dbac1d8f1b8.png)

启动GeoIP Resolver把它的标签拖到消息处理器列表的底部。您的配置应该与下图的配置类似:

![](https://p0.ssl.qhimg.com/t01b192e02aadd066e8.png)

如果你都按上面的操作。Graylog应该自动开始从包含IP地址的日志字段中提取地理位置信息。

你也可以按照以下方式进行测试是否成功，访问“搜索”菜单，然后搜索日志，这些日志将包含一个IP地址，例如apapweb请求。您应该可以在Fields菜单中看到IP_geolocation复选框。展开它并点击世界地图。

![](https://p5.ssl.qhimg.com/t018e41690d9ca73ffe.png)

然后您应该可以在世界地图上看到所有与您的日志源交互的IP地址。您也可以像其他小部件一样将其添加到仪表板。

![](https://p1.ssl.qhimg.com/t0113d113e6cbe6f2fa.png)

## 五.Slack支持

默认情况下，Slack
alerting并没有内置在Graylog中，你需要花费几秒钟的时间安装这个插件。插件你可以在Graylog市场下载。插件目录在Graylog中的jar文件下(/usr/share/
Graylog -server/plugin/默认),下载完成后记得重新启动Graylog服务哦。  
`cd /usr/share/graylog-server/plugin/  
sudo wget https://github.com/graylog-labs/graylog-plugin-slack/releases/download/3.0.1/graylog-plugin-slack-3.0.1.jar  
sudo service graylog-server restart`  
Graylog重新启动之后，插件就会被安装。

## 六.设置Slack通知

假设我们现在已经有一个Slack工作区。然后就需要创建一个用于基础架构警报的渠道。我将用下图的频道作为演示：

![](https://p2.ssl.qhimg.com/t01c9f602aa8b873445.png)

通过访问下面的URL创建一个新的Slack并传入Webhook：  
`https://[YOUR_WORKSPACE].slack.com/services/new/incoming-webhook`  
它会提示您选择为基础设施提醒创建一个Slack频道。

![](https://p1.ssl.qhimg.com/t01cb825df5a10fc714.png)

复制生成的Webhook，并将其保存在某处供以后使用。如果您愿意，也可以更改Web集成用户名和图标。完成后，点击页面底部的保存设置.  
准备好webhook后，回到Graylog，导航到Alerts菜单并单击Manage notifications按钮。

![](https://p0.ssl.qhimg.com/t0163bd2cb286c48911.png)

点击添加新通知，你可以在下拉菜单中看到Slack Alarm Callback选项。

![](https://p3.ssl.qhimg.com/t015cdb9535d928a6ef.png)

为你刚才的警报设置一个新名字，输入你的Slack频道的名字并粘贴你之前保存的webhook值。

![](https://p4.ssl.qhimg.com/t011db8d23725a70666.png)

完成后点击保存。您现在就可以测试是否成功了。如果一切顺利，您的基础设施Slack频道中应该会收到一个新的虚拟通知。

![](https://p5.ssl.qhimg.com/t017cae350236b8ffca.png)

## 七.创建一个警报条件：

我将下载一个payload来演示Slack警报功能，但您可以设置其他类型的可疑活动来触发警报。我将演示下载我的Web服务器“payloads”
目录中存储的“ evil.hta ” 文件。  
前往警报菜单并点击管理条件。点击在页面上添加新条件。选择下一个菜单中的All messages stream和Field Content Alert
Condition作为条件类型。

![](https://p1.ssl.qhimg.com/t011d50aaf6577a5385.png)

在下一个菜单中，为您的新条件设置一个标题，在字段框中输入请求，在Value域中输入/payloads/evil.hta（或任何payload目录和名称）。完成后保存条件。  
  
注：如果您希望将下载的Apache日志条目追加到Slack警报消息中，请将 Message Backlog设置为1。

**测试：**

如果您已经适当地配置了您的条件和通知，您应该能够测试payload下载警报。转到浏览器/终端，下载你payload。您应该会收到一个新的Slack通知。  
  
这可能会有轻微的延迟，稍微等下。报警将会显示在“Graylog的警告”菜单中。

  
现在，您只需添加其他的新条件来做到随时提醒。  
一些常见条件：  
成功的钓鱼。  
来自IR用户代理(例如wget、nc、curl、python等)的有效载荷下载/ web请求。  
来自已知“不良IPs”的Web请求(例如，AV供应商IP地址)。  
成功登录到您的基础设施。  
结论：

在这里，基础设施日志记录系列就要结束了。在长期参与的渗透测试中设置集中式日志记录可能有点困难，但从长远的角度来看可以为您节省更多的时间和精力，并为您提供重要的运营优势，感谢您的阅读。

## 参考

<http://docs.graylog.org/en/2.4/pages/streams/alerts.html>  
<http://docs.graylog.org/en/2.4/pages/plugins.html#plugins>  
<https://marketplace.graylog.org>  
<https://github.com/bluscreenofjeff/Red-Team-Infrastructure-Wiki>  
<http://docs.graylog.org/en/2.4/pages/dashboards.html>  
<http://docs.graylog.org/en/2.4/pages/geolocation.html>  
<http://docs.graylog.org/en/2.4/pages/dashboards.html#widget-types>  
<http://docs.graylog.org/en/2.4/pages/queries.html>

## 本文翻译

<https://thevivi.net/2018/03/23/attack-infrastructure-logging-part-3-graylog-dashboard-101/>  
<https://thevivi.net/2018/03/23/attack-infrastructure-logging-part-4-log-event-alerting/>

本文翻译自https://thevivi.net/ [原文链接](https://thevivi.net/2018/03/23/attack-infrastructure-logging-part-3-graylog-dashboard-101/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **无名小卒** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/103820](/post/id/103820)

安全客 - 有思想的安全新媒体

本文转载自: [https://thevivi.net/](https://thevivi.net/2018/03/23/attack-infrastructure-logging-part-3-graylog-dashboard-101/)

如若转载,请注明出处： <https://thevivi.net/2018/03/23/attack-infrastructure-logging-part-3-graylog-dashboard-101/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [基础设施](/tag/基础设施)
  * [日志记录](/tag/日志记录)
  * [服务器日志](/tag/服务器日志)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t013aa021a06d47a307.png) 无名小卒

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


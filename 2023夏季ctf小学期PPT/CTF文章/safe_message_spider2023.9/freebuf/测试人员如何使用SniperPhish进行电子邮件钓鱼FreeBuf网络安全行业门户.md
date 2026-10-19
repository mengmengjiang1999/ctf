![](https://image.3001.net/images/20210501/1619852480_608cfcc09a25a4dd47c5c.jpg!small)

## 关于SniperPhish

[
_SniperPhish_](https://sniperphish.com/)是一款专为渗透测试人员以及安全研究专家设计的网络钓鱼研究工具，其主要目的是为了通过模拟真实场景中的网络钓鱼攻击来提升用户的安全保护意识。SniperPhish可以将研究人员创建的钓鱼网站和钓鱼邮件绑定在一起，以实现集中跟踪用户的行为。该工具的设计是为了帮助执行专业的网络钓鱼活动，因此请广大用户在获取到目标组织许可的情况下使用SniperPhish。

## 主要功能

> 网页跟踪器代码生成-独立跟踪网站访问和表单提交；
>
> 创建和计划网络钓鱼邮件活动；
>
> 将钓鱼网站与电子邮件活动结合起来进行集中跟踪；
>
> 一个独立的“简单跟踪器”模块，用于快速跟踪电子邮件或网页访问；
>
> 高级报告生成，根据所需的跟踪数据生成报告；
>
> 自定义跟踪消息中的图像和动态二维码；
>
> 跟踪钓鱼邮件回复；

## 工具安装

首秀按，我们需要使用下列命令将该项目源码克隆至本地，并将其放入Web服务器的根目录下：

    
    
    git clone https://github.com/GemGeorge/SniperPhish.git

接下来，在浏览器中打开下列地址：

    
    
    http://localhost/install

按照操作步骤安装完成之后，打开下列地址即可登录SniperPhish（用户名：admin，密码：sniperphish）：

    
    
    http://localhost/spear

## 创建Web钓鱼邮件活动

### 创建一个Web跟踪器

> 使用你喜欢的编程语言设计你的钓鱼网站，确保HTML字段中有唯一的“id”和“name”值，比如说text字段和checkbox等。
>
> 点击“Web Tracker -> New Tracker”生成Web跟踪器代码，“Web Pages”标签页中会列出你需要跟踪的页面。
>
> 从输出结果中拷贝生成好的JavaScript链接，并将其添加至每一个Web页面的相应位置。
>
> 最后，保存创建好的跟踪器。此时跟踪器将被激活并在后台执行监听。

### 创建一个网络钓鱼活动

> 点击“Email Campaign -> User Group”并添加目标用户。
>
> 点击“Email Campaign -> Sender List”并配置邮件服务器信息。
>
> 点击“Email Campaign -> Email
> Template”并创建钓鱼邮件模板。添加好钓鱼网站链接之后，确保在结尾处添加“?cid={{CID}}”，这样做是为了区分目标用户，比如说：http://yourphishingsite.com/login?cid={{CID}}。
>
> 点击“Email Campaign -> Campaign List -> New Mail Campaign”，并填写完相关信息以创建钓鱼活动。
>
> 完成上述操作之后，开启钓鱼邮件活动即可。

### 查看绑定的Web钓鱼邮件结果

打开“Web-MailCamp Dashboard -> Select Campaign”，选择“Mail Campaign”以及我们所创建的“Web
Tracker”：

![](https://image.3001.net/images/20210501/1619852536_608cfcf89882067a4c63f.png!small)

## 工具运行截图

![](https://image.3001.net/images/20210501/1619852576_608cfd20ca9bd76fd019e.png!small)

![](https://image.3001.net/images/20210501/1619852583_608cfd27c652c4dcfb251.png!small)

## 项目地址

 **SniperPhish：** https://github.com/GemGeorge/SniperPhish

## 参考资料

> [ _https://sniperphish.com/_](https://sniperphish.com/)
>
> [
> _https://demo.sniperphish.com/spear/﻿_](https://demo.sniperphish.com/spear/)


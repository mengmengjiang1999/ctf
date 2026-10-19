![](https://image.3001.net/images/20200605/1591346392_5eda04d8328ad.jpg!small)

**近期，作者注意到了Facebook的创作工作室（Facebook Creator Studio）中添加了系列视频创建功能（Series
Feature），出于对漏洞测试的敏感性，作者及时对该功能进行了测试，最终发现该功能中存在任意Facebook图片删除漏洞，漏洞获得了Facebook官方$10,000的奖励。**

## 漏洞发现过程

Facebook的创作工作室（Facebook Creator Studio）汇集了用户所需的各种工具，让用户能够跨所有 Facebook 主页和
Instagram 帐户发布内容、实现变现、衡量表现并与粉丝互动。系列视频创建是在 Facebook
内容分享中比较吸引人的方式，用户可以从个人上传内容中通过视频组合形成专辑影片，发布后供朋友圈和其他用户观看。

如下系列视频创建过程：

![](https://image.3001.net/images/20200605/1591346413_5eda04ed82bd7.png!small)

在创建系列视频的过程中，要求上传图片作为其宣传海报（"Poster Art"）和影片封面（"Cover Image" ），如下：

![](https://image.3001.net/images/20200605/1591346425_5eda04f928bda.png!small)

在上传图片的请求中，我发现其中包含了图片的id号（fbid），意思是只要是Facebook平台中任何具备id号（fbid）的图片都能把它填写于此作为封面图片，如下选择其他用户账户下的任一fbid图片（2467651590213206）作为封面：

![](https://image.3001.net/images/20200605/1591346486_5eda05362b654.png!small)

图片上传请求中原来的图片id（2903739103044967）：

![](https://image.3001.net/images/20200605/1591346512_5eda0550371ef.png!small)

替换为新的图片id（2467651590213206）作为封面：

![](https://image.3001.net/images/20200605/1591346797_5eda066d53ca3.png!small)

替换成功后，我再选择删除该系列视频集的操作，如下：

![](https://image.3001.net/images/20200605/1591346821_5eda068556107.png!small)

删除成功：

![](https://image.3001.net/images/20200605/1591346841_5eda0699e5cf7.png!small)

此时，原来作为封面的其他用户账户下的图片（2467651590213206）也即被删除，不可访问：

![](https://image.3001.net/images/20200605/1591346860_5eda06ac55881.png!small)

![](https://image.3001.net/images/20200605/1591346866_5eda06b2e22b9.png!small)

及时上报给Facebook后，Facebook安全团队及时给出了反馈：

![](https://image.3001.net/images/20200605/1591346887_5eda06c737932.png!small)

## 漏洞上报和处理进程

> 2020.5.2 09:10 – 漏洞初报
>
> 2020.5.2 10:39 – 漏洞分类
>
> 2020.5.2 22:46 – 漏洞修复
>
> 2020.6.2 – $10,000赏金发放

 ***参考来源：[darabi](https://blog.darabi.me/2020/06/image-removal-vulnerability-on-facebook.html)，clouds 编译整理，转载请注明来自 FreeBuf.COM**


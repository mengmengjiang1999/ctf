***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![01.jpeg](https://image.3001.net/images/20181110/1541847419_5be6b97b96d82.jpeg!small)
**大家好，我是Sarmad
Hassan，今天我要和大家分享的是一个关于Instagram的漏洞，这个漏洞很有意思，我可以利用它来在其它Instagram用户的发贴中添加描述，最终也获得了Instagram官方$6500美金的奖励。**

## 漏洞端倪

Instagram为Facebook旗下的图片视频分享应用，为方便用户的分享服务，Facebook中可以关联登录Instagram。8月的一天，当我看到Facebook页面中有一个可以管理
Instagram
应用的选项时（具体可[查看此处说明](https://www.facebook.com/business/help/898752960195806)），我就突发奇想，想尝试在Facebook网页中来绕过Instagram的双因素认证（2FA）机制。

于是，我想在Facebook网页中进行测试，我先找到了Instagram选项按钮，想用我之前老的Instagram账户进行登录，但不巧的是，我把密码给忘记了。

![02.jpeg](https://image.3001.net/images/20181110/1541847102_5be6b83e746bd.jpeg!small)由于在此之前我曾对Instagram网页应用做过一些测试，为了方便新功能的提醒，我开启了密码登录记忆功能，所以接下平，我就直接在浏览器中输入了Instagram网站
<https://www.instagram.com/> 想看看我之前的账户是否存在。很好，竟然能登录进入：

![03.png](https://image.3001.net/images/20181110/1541847117_5be6b84da378a.png!small)这是我Instagram测试账户登入后的样子，初看可能发现不了什么异常，但仔细观察我发现了其中有一个名为IGTV的选项，这是什么呢？What
is IGTV：

原来，IGTV是Instagram的一个新功能，它可以让用户观看其他人创建的一些竖屏的长格式视频（Vertical
Video），具体功能说明[点此查看](https://instagram-press.com/blog/2018/06/20/welcome-to-igtv/)。从 Instagram的信息中心简介中，我对这个IGTV研究了好半天，最终我决定测试测试它。

首先，我自己创建了一个IGTV视频，创建完成后，在BurpSuite的配合下，我点击视频的编辑（Edit）选项操作，想看看其中存在些什么传输参数，执行的POST请求如下：

> POST /media/1887820989027383407/edit/
>
> caption=test&publish_mode=igtv&title=test

分析以上请求，可以得到以下信息：

1、其 media id号 为
1887820989027383407，它应该是我IGTV视频的ID编号，之后，我查询发现，Instagram对所有的用户发贴（包括图片、视频和IGTV视频），都是用这个
media id的ID号来标记的，这样，也就是说，我可以在其他用户的发贴中，检查其中的源代码来提取到其发贴media id号。如下：

![04.png](https://image.3001.net/images/20181110/1541847184_5be6b89073f33.png!small)2、另一种获取media
id号的方法还有，就是访问其他用户的发贴，在BurpSuite配合下，点击“赞”（Like），以此也可抓取到media
ID号（文末的PoC验证视频中就是这种方式）；

3、还有另外两个参数：caption（说明） 和 title（标题）；

4、当我们在Instagram网页应用中创建任意图片或视频发贴时，Instagram都会询问你是否要加上一段图片或视频说明，当然这是可选的，大多数人都不会填，直接留白。当然了，在IGTV视频中，这里的caption（说明）就代表了视频说明的意思。

好了，有了以上基本的分析之后，接下来，我们来看看如何利用！

对于大多数Bug Hunter来说，肯定要围绕这个media ID号来做点事情咯，可以把它改成其他用户发贴的media
ID号来试试，看看能不能骗过Instagram后台系统，或者深入点说，能不能骗过Instagram，以其他用户身份，在其他用户的图片视频发贴中添加一段说明呢？

## 漏洞测试

我用我另外一个Instagram账户做Victim账户之后，经过测试，有了以下发现：

> 1、如果Victim账户发贴中未发说明描述文字，之后，当把我自己当前的media ID号用Victim账户发贴的media
> ID号替换后，我就能在caption参数中做手脚，在Victim账户发贴中添加说明描述文字；
>
> 2、这种添加说明描述文字的操作，适用于Instagram账户中的任何发贴，包括图片、视频和IGTV视频发贴；
>
> 3、当然了，这只限于针对一些有发贴查看权限的公开用户；
>
> 奇怪的是，在以上的漏洞利用操作之后，响应消息会返回一个名为“Oops an error
> occurred”的内部服务器错误，但是，操作最终是有效的，具体可在文末的PoC视频中查看。

## 漏洞危害性

很多Instagram用户，甚至是数百万的Instagram用户都是公开的；那么，找到这些公开用户之后，我们查看他们的最近一次无说明描述的发贴，就可以伪装其他用户，用该漏洞来一波添加说明描述文字的恶意操作了；如果这个漏洞被坏人利用，那么他们就会对那些Instagram中的大V人物下手，随便添加一段描述说明，可能就会造成不小的舆论影响。

当然，可以想到的是，有很多在Instagram上的名人账户也会存在该漏洞影响，很多时候这些名人也会创建一些无描述说明的发贴，那么，这个漏洞就有可利用的机会了。如下：

> 马克·扎克伯格 ===> 460万粉丝
>
> 赛琳娜·戈麦斯 ===> 1.4亿粉丝
>
> 爱莉安娜·格兰德 ====> 1.25亿粉丝
>
> 碧昂丝 =====> 1.17亿粉丝
>
> 金·卡戴珊 ===> 1.15亿粉丝
>
> 梅西 ====> 9700万粉丝
>
> ......

还有太多名流Instagram用户就不一一罗列了，你可以想像利用这个漏洞制造的舆论风波多么可怕，当然还可用于各大公司之间的恶意宣传诋毁。

## 漏洞上报进程

由于Instagram属Facebook旗下应用，之后，我迅速向Facebook安全团队报告了这个漏洞，他们仅在一天内就修复了它。基于漏洞严重的危害性，Facebook向我奖励$6500美元的奖金。

>
> ![05.png](https://image.3001.net/images/20181110/1541847315_5be6b9134329e.png!small)2018.8.6
> 漏洞初报
>
> 2018.8.14 漏洞分类
>
> 2018.8.15 漏洞修复
>
> 2018.8.15 修复确认
>
> 2018.10.10 $6500发放

## PoC视频

 ***参考来源：[medium](https://medium.com/bugbountywriteup/add-description-to-instagram-posts-on-behalf-of-other-users-6500-7d55b4a24c5a)，clouds编译，转载请注明来自FreeBuf.COM**


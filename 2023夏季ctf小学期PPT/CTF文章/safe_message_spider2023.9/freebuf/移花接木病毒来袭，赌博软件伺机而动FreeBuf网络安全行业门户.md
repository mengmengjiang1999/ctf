##  一、背景

 **移花接木，指暗中使用巧计在事情进行过程中更换人或事物来欺骗别人。**

近期腾讯安全反诈骗实验室发现了一款网络赌博病毒DownloadGambling。该病毒使用移花接木技术手段，通过“安全的”母包下载赌博软件，从而达到欺骗各大应用商店、安全系统的目的。该病毒首先会判断用户是否为中国用户，如果是中国用户则会私自下载并安装指定的赌博软件，赌博软件从云端下载安装，不需要上架各大应用市场，躲避安全机构的查杀；如果不是中国用户则运行软件本身的功能界面，进行超级伪装。

病毒特点：

> 软件本身作为载体是安全的，可以轻松绕过各大应用市场的安全检测机制，便于软件上架；
>
> 通过载体从云端下载网络赌博软件，用户和监察机构不易发现，增加赌博软件的存活时长；
>
> 启动安全的载体软件便会启动赌博软件，增大了与用户接触的几率，间接增加赌博软件的用户量，可能会使更多的用户使用；

受到移花接木影响的主要应用程序感染列表：

![](https://image.3001.net/images/20200228/1582879018_5e58d12ae92e7.png!small)

![](https://image.3001.net/images/20200228/1582879055_5e58d14f6ee2b.png!small)

病毒运行流程图：

![](https://image.3001.net/images/20200228/1582879086_5e58d16ec2283.png!small)

病毒运行截图：

![](https://image.3001.net/images/20200228/1582879106_5e58d182b3bc7.png!small)

##  二、病毒影响范围

DownloadGambling病毒感染用户趋势：

随着打击力度增加，感染用户数呈下降趋势

![](https://image.3001.net/images/20200228/1582879281_5e58d23122ac7.png!small)

DownloadGambling病毒感染用户分布图：

感染用户最多的省市为：云南省、广东省、四川，分别占比8.5%、7.8%和5.5%

##  三、病毒详细分析

作为赌博软件载体的样本信息：

![](https://image.3001.net/images/20200228/1582879318_5e58d256af8bf.png!small)

网络赌博软件样本信息：

![](https://image.3001.net/images/20200228/1582879344_5e58d2704e43c.png!small)

1、软件启动后，通过访问网址获取网络IP地址信息并发送Message信息

![](https://image.3001.net/images/20200228/1582879385_5e58d29987a53.png!small)

>
> 获取IP地址信息网址：[http://p******.com/c*****n?ie=utf-8](http://pv.sohu.com/cityjson?ie=utf-8)

![](https://image.3001.net/images/20200228/1582879408_5e58d2b04eb76.png!small)

发送Message信息

![](https://image.3001.net/images/20200228/1582879585_5e58d361a0db6.png!small)

2、
在主界面SplashUpdateActivity中对Message信息进行判断处理，当满足IP地址是在中国时，替换软件背景图片并私自下载赌博类软件；到不满足条件时启动MainActivity，运行软件自身功能界面，以此来达到欺骗用户的目的

![](https://image.3001.net/images/20200228/1582879610_5e58d37ab1413.png!small)

当满足条件时，调用initNewNetWork方法替换软件背景图片并私自下载指定的赌博软件

![](https://image.3001.net/images/20200228/1582879624_5e58d38824f40.png!small)

当不满足条件时，启动符合软件自身功能的Activity

![](https://image.3001.net/images/20200228/1582879657_5e58d3a93a8c6.png!small)

通过downloadLayout方法替换软件背景图片

背景图片下载地址：[https://img.x](https://img.x/)******ver.com/u****9/201908/p****2.jpg

![](https://image.3001.net/images/20200228/1582879671_5e58d3b712101.png!small)

![](https://image.3001.net/images/20200228/1582879711_5e58d3df41e81.png!small)

3、 在initJumpStateJudge方法中判断是否已安装赌博软件，若已安装，则

直接启动赌博软件，若没有安装，则下载赌博软件并安装

![](https://image.3001.net/images/20200228/1582879698_5e58d3d23e7e5.png!small)

存储在本地SharedPreferences中的赌博软件包名

![](https://image.3001.net/images/20200228/1582879743_5e58d3ff72489.png!small)

4、 通过autoUpdate方法下载赌博软件

![](https://image.3001.net/images/20200228/1582879757_5e58d40d8ba4f.png!small)

下载赌博软件

![](https://image.3001.net/images/20200228/1582879768_5e58d418c6139.png!small)

安装下载完的赌博软件

![](https://image.3001.net/images/20200228/1582879785_5e58d429920b7.png!small)

##  四、建议及手机管家查杀截图

腾讯安全反诈骗实验室建议：

1、不安装来源不明的应用，该类应用可能会危害您的手机安全；

2、 安装腾讯手机管家，可准确有效的保护您的手机安全；

3、从正规渠道下载安装所需的应用，可有效避免病毒软件；

![](https://image.3001.net/images/20200228/1582879820_5e58d44c87a37.png!small)

受感染应用程序MD5列表:

> 7704c9f96faf4dda339b7f9bc4028c58
>
> 47fe89e3d936f47cc8e73de6269de4b2
>
> 560d5f491fb817d26181e76b84974fae
>
> d5561bc8a3f4dd90792069f5cad3fc67
>
> 9898cf3a588a9546092c036ee81b56ac

 ***本文作者： 腾讯手机管家，转载请注明来自FreeBuf.COM**  
  


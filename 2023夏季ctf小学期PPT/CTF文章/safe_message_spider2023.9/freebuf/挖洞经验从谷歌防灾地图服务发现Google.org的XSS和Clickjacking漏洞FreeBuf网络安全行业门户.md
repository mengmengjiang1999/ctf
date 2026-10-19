![](https://image.3001.net/images/20190815/1565860557_5d5522cd51591.jpg!small)

**除了谷歌地图之外，可能很少有人知道[谷歌的在线防灾地图](https://google.org/crisismap)（Google Crisis
Map），它创建于2012年，Web架构更新缓慢，网站访问量相对较少。而作者就是通过在这个“老旧”的地图服务中，发现了XSS和依托其服务的google.org点击劫持漏洞。该篇Writeup也算是在“犄角旮旯”角落里发现漏洞的典型，我们一起来看看。**

##  谷歌防灾地图（Google Crisis Map）介绍

[谷歌防灾地图](https://google.org/crisismap)创建于2012年，目的在于帮助人们发现和预警重要的灾害活动，网站访问量较少，它托管于谷歌旗下域名google.org，从客户漏洞角度来说，虽然没有google.com那么引人注目，但好歹也是属于谷歌域名。

###  登录

我们可以通过<https://google.org/crisismap>主页进行浏览，其中右上角显示出“天气，灾害，应急准备”，此时，我们能做的仅只是简单浏览这个防灾地图。

![](https://image.3001.net/images/20190815/1565859911_5d5520478e08c.png!small)

经测试，我们可以在其URL后面添加一个.maps来创建自己的地图，也就是<https://google.org/crisismap/.maps>打开该链接之后，就会以谷歌账号登录进入，其中可以看到三幅默认地图，这三幅地图对任意用户都可见，如下：

![](https://image.3001.net/images/20190815/1565859928_5d5520588899c.png!small)

点击Published Map下的地图名称即可查看相应地图。

###  创建地图

来到左上角，点击 “Create Map” 按钮之后，会跳出以下的提示框告知Gmail账号不能创建地图，只有个人或企业定制域名身份才具备地图创建权限：

![](https://image.3001.net/images/20190815/1565859954_5d5520726ce83.png!small)

也就是说，我们需要以谷歌关联的个人或组织机构邮箱身份才能创建地图，这里，可以通过GSuite账户或其它非gmail.com后缀邮箱登录即可。之后，创建地图开始，点击下图Continue之后就行：

![](https://image.3001.net/images/20190815/1565859968_5d552080975fe.png!small)

##  发现XSS漏洞

在创建地图的过程中，点击'Add
layer'我们可以向其中添加新的图层（layer），之后，会跳出图层对话框，其中包含了图层标题、描述、属性、图例、缩放坐标、来源URL（Source
URL）等填写项。

![](https://image.3001.net/images/20190815/1565860015_5d5520af32459.png!small)

![](https://image.3001.net/images/20190815/1565860032_5d5520c01ec9e.png!small)

当我们简单填写了图层标题，选择了图层类型，并在来源URL（Source
URL）中填入javascript:alert(document.domain)的XSS Payload，提交保存后，它会反应出错提示：

    
    
    Invalid URL – please include a protocol (e.g. http:// or https://)

这看似是在图层保存之前，后端会检查其Source URL的合法性，其检查逻辑可能如下：

    
    
    if (url && !url.toLowerCase().match("^\\s*(http://|https://|docs://|$)")) {  showError("Invalid URL - please include a protocol (e.g. http:// or https://)");}

更关键的是，该合法性验证貌似是请求提交到后端服务前，对客户端的唯一一项验证措施。

在此，我们可以用BurpSuite代理工具来对请求抓包分析，并对请求进行相应更改提交给后端服务。首先，我们可以把代表Source
URL的值进行一个替换，这里我们把它替换成[https://example.com](https://example.com/)，然后点击OK并保存，在此过程中的请求如下：

> POST <https://google.org/crisismap/.api/maps/1234>
    
    
    {  "id": "1234",  "title": "Untitled map",  "base_map_type": "GOOGLE_ROADMAP",  "layers": [{    "id": "1",    "title": "Test layer",    "visibility": "DEFAULT_ON",    "type": "KML",    "source": {      "kml": {        "url": "https://example.com"      }    }  }]}

在此，我们把其中代表Source URL的[https://example.com](https://example.com/)替换成之前的XSS
Payload -javascript:alert(document.domain)，然后转发请求。请求竟然可以成功被提交保存！之后，我们打开图层选项，点击下载按钮“Download
KML”，就能完美触发XSS Payload:

![](https://image.3001.net/images/20190815/1565860143_5d55212fd54f0.png!small)![](https://image.3001.net/images/20190815/1565860152_5d5521380782e.png!small)

这个XSS漏洞原因是什么呢？原来那个Source URL合法性验证只会发生在前端（
frontend），而与谷歌防灾地图的数据库进行交互的后端（backend）却没有该URL验证。其漏洞的危害就是，任意用户可以创建地图并公开发布，比如我们以后缀example.com的邮箱进行创建地图并发布，那么该地图的URL就是：

> <http://google.org/crisismap/example.com/test>

![](https://image.3001.net/images/20190815/1565860197_5d5521659cbc8.png!small)

那么，任何查看下载该地图的用户，由于其中存在 javascript: URI 的XSS Payload，点击相应的“Download
KML”下载按钮之后，就会成功触发XSS Payload，当然，有效的漏洞利用还需要更多深入的构造。

##  点击劫持（Clickjacking）

在与后端交互过程中，如果我们查看一下响应中的HTTP消息头，发现google.org并没有要求X-Frame-Options设置。 X-Frame-Options 的HTTP 响应头是用来给浏览器指示允许一个页面可否在 <frame>、<iframe>、<embed> 或者 <object>
中展现的标记。应用该设置的站点可以通过确保网站没有被嵌入到别人的站点里面，从而避免 clickjacking 攻击。

![](https://image.3001.net/images/20190815/1565860269_5d5521ad2ff67.png!small)

那么，也就是说，我们可以把上述创建发布的地图以iframe方式嵌入到我们控制的网站中去，又能触发XSS，也能证明Clickjacking，如下：

    
    
    <iframe src="<https://google.org/crisismap/example.com/test>"></iframe>

![](https://image.3001.net/images/20190815/1565860387_5d552223e9eee.png!small)

但受害者还需点击“Layers” > “Download
KML“才能触发XSS。所以，我又想到用背景为黑色的DIV标签来把iframe伪装成一个点击链接，不好的是，还是需要两次点击才能触发，如下：

这是<[点击我](https://samples.appio.dev/google-crisis-map-clickjacking/)>一个POC
demo，它把iframe缩放了50倍，并将其移动到我们希望受害者用户单击的位置。两次连续点击之后，会出现我创建发布的地图，大家可以试试。

![](https://image.3001.net/images/20190815/1565860455_5d5522676c320.jpg!small)

##  总结

> 1、任何用户输入点都值得怀疑。对厂商来说，需要在保存提交数据之前进行一些必要的验证措施；
>
> 2、考虑Clickjacking时，可检查X-Frame-Options ；
>
> 3、寻找漏洞时，尽量去实现最坏的漏洞危害，或综合利用；
>
> 4、尽量在测试范围内的一些“老旧”系统中多做挖掘。

##  漏洞上报进程

> 2018.9.12 漏洞上报
>
> 2018.10.12 漏洞被分类为P1级别
>
> 2018.10.12 谷歌深入调查并给予肯定（Nice Catch）
>
> 2018.11.12 得到一笔赏金

***参考来源：appio，clouds编译整理，转载请注明来自FreeBuf.COM** ****

  


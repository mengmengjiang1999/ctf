***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言  

 **我来分享一个Facebook旗下公司Oculus网站存在的类似XSS漏洞，该漏洞最终获得了Facebook官方$1500美金的奖励。**  

Facebook在2014年3月宣布以20亿美元收购虚拟现实（VR）头戴设备制造商[Oculus](https://www.oculus.com/)，Facebook计划将Oculus的VR技术优势扩大至新的垂直领域，如通信、媒体和娱乐、教育及其他领域等。

Oculus发布了定制化开源的开发者项目（ Custom Developer
Items），这项功能已向社区开发者推送。无论你是开发虚拟现实游戏、社交体验、娱乐还是教育类应用，都可以使用自己最喜欢的游戏引擎或我们的原生 SDK
轻松地在整个 Oculus 平台上进行开发。它覆盖了Oculus Rift + Touch 、Oculus Go 和 Samsung Gear VR +
控制器的VR产品，与主流开源的VR开发工具Unity结合，用户可以定制化地开发属于自己的应用。

 ** **
**![c7d2e0e415ea4a7387daf1f35390a339.jpeg](https://image.3001.net/images/20181214/1544763461_5c1338455dfd5.jpeg!small)******

## 漏洞发现及PoC

在Oculus网站的账户管理页面<https://dashboard.oculus.com/>，注册并登录账户后，有一个服务端功能允许开发者上传应用相关的asset资源文件，且所有asset资源文件都储存在了"oculuscdn.com"网站中。例如，我们用该服务端功能上传一个图片文件时，其发送的POST请求如下：

    
    
    POST /upload_image/ HTTP/1.1
    
    Host: graph.oculus.com
    
    multipart/form-data

之后，oculuscdn.com返回的响应如下：

    
    
    HTTP/1.1 200 OK
    
    {
    
    “id”: “1234567890012345”,
    
    “handle”: “HANDLE_TO_THE_IMAGE”,
    
    “uri”: “[https://scontent.oculuscdn.com/v/t64.5771-25/12410200_1905973632996555_3168227744525844480_n.png?_nc_cat=0&oh=6163326b2eb5e87c16c6949f1e734611&oe=5AD840C8](https://scontent.oculuscdn.com/v/t64.5771-25/12410200_1905973632996555_3168227744525844480_n.png?_nc_cat=0&oh=6163326b2eb5e87c16c6949f1e734611&oe=5AD840C8)”
    
    }

其中包含了图片的ID号，称呼Handle和具体的访问链接URL。可以看到，我们POST请求主机graph.oculus.com，Response中响应的主机为scontent.oculuscdn.com。这里存在的漏洞就比较简单了，不需要像之前facebook
cdn的那样需要进行cname域名替换，这里直接把 /v/ 和HASH串去掉，就能访问到目标图片了。整个测试过程如下：

> 上传PNG图片，用BurpSuite拦截抓包；
>
> 拦截到上传的PNG图片内容，把恶意的带XSS Payload的js外链添加在其末尾；
>
> 成功上传后，从响应内容中提取出图片上传后的具体访问URL链接；
>
> 然后，把URL中的 "/v/" 和
> HASH串去掉去掉，再把上传图片的后缀格式由.jpg改为.html，就能成功加载之前添加进入的js恶意Payload了。

这里，我用到的带XSS Payload的js外链为：

> <https://www.amolbaikar.com/wp/js/oculus.js>

最终的请求链接如下：

>
> <https://scontent.oculuscdn.com/t64.5771-25/12410200_1905973632996555_3168227744525844480_n.html>

## PoC视频：

## 漏洞影响

该漏洞允许攻击者在Oculus
CDN服务器上执行任意JS文件，好在有沙盒防护机制，其不能读取用户的cookies/session信息，但应用在实际的攻击场景中，该漏洞可以绕过Facebook的链接黑名单系统
Linkshim，也能用其实施钓鱼行为。

## 漏洞上报进程

> 2018.3.19: 漏洞初报
>
> 2018.3.22: 技术详情提供
>
> 2018.3.22: Payload测试
>
> 2018.3.23: 漏洞有效性认可
>
> 2018.5.25: 漏洞修复
>
> 2018.6.1: $1500赏金发放

 ***参考来源：[amolbaikar](https://www.amolbaikar.com/xss-on-facebooks-acquisition-oculus-cdn/)，clouds编译，转载请注明来自FreeBuf.COM**


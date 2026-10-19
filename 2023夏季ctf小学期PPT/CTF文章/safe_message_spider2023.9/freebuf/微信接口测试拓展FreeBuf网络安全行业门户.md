# 背景

最近收到一个SRC提交的漏洞，泄露了微信小程序的appkey和appSecret；于是乎为了搞清楚影响，漏洞风险和利用方式，便有了这篇文章；

在了解漏洞风险之前先来了解一下微信的几个平台；

# 微信公众号平台

[微信公众平台开发概述 | 微信开放文档
(qq.com)](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)

[微信公众平台接口调试工具
(qq.com)](https://mp.weixin.qq.com/debug?token=985399073&lang=zh_CN)

这个界面是微信公众号平台提供的在线接口调试工具，可以看到功能挺丰富的，公众号后台的大部分功能都可以通过接口的方式调用，第一个接口就是通过appid和secret兑换access_token，然后后面的接口都是通过access_token来请求数据；  
![Untitled
1.png](https://image.3001.net/images/20230510/1683703495_645b46c795ca30fd97497.png!small)  
![image](https://image.3001.net/images/20230510/1683703554_645b470211393811c19a4.png!small)  
我这边登录自己的公众号后台，在APPSecret这里可以看到官方对于这个APPSecret的描述，也就是=密码；

![Untitled
3.png](https://image.3001.net/images/20230510/1683703575_645b47171a5f96e36c01a.png!small)![Untitled
4.png](https://image.3001.net/images/20230510/1683703579_645b471b307c536c1e7d5.png!small)![Untitled
5.png](https://image.3001.net/images/20230510/1683703587_645b4723ca586b786d83b.png!small)

但是我们配置到后面，可以看到需要配置ip白名单，才可以成功调用，下面的调用情况对比，就是把当前ip配置到白名单前后的对比；也就是说即使拿到了公众号的id和secret，但是不是白名单中的请求ip也是无法成功调用；

我这里是重置后必须要配置白名单才可以调用成功，但是我以前也遇到过拿到了id和secret确实可以调用成功的，不过这个不晓得对应公众号后台是怎么配置的；

![Untitled
6.png](https://image.3001.net/images/20230510/1683703616_645b47407a0347be94cac.png!small)

然后自己以前也是跟这个白帽子类似，弄了个脚本拿到数据测试一下，能换token，哦吼，也就是数据有效存在风险，但是自己其实没有使用过，也不清楚具体风险是啥；然后白帽子提到的2000次调用限制，这个也确实有的，我自己测试了之后调用一次使用次数就少一次了；
**但是这里是公众号的id、secret；**

![Untitled
7.png](https://image.3001.net/images/20230510/1683703633_645b4751d3cb7cc3cee8b.png!small)

# 微信开放平台

[微信调试工具 (qq.com)](https://developers.weixin.qq.com/apiExplorer)

[微信登录](https://dev.weixin.qq.com/docs/framework/dev/jsapi/diffapi/WeChatLogin.html?utm_source=open)

本来还想注册到后台看一下，测试一下开放平台的接口情况；结果白忙活，注册了半天要花300才给用；  
![Untitled
8.png](https://image.3001.net/images/20230510/1683703645_645b475d983ed3d2ea327.png!small)

[微信登录](https://qin.tuyacn.com/iot-doc-center/zh/K8uhkjmexe9f8/goat/20190822/8202b08e00f84265845733d8c66e7346.html#%E9%85%8D%E7%BD%AE%E5%BA%94%E7%94%A8)

具体还是看这篇指导文章里边描述的；可以看到创建应用或者其他程序以调用微信开放平台提供的能力；能力包含了微信登录、分享、发朋友圈等，具体可以参考官方文档或者接口调试工具；  
![Untitled
9.png](https://image.3001.net/images/20230510/1683703824_645b481041f4c7b33b88a.png!small)  
![Untitled
10.png](https://image.3001.net/images/20230510/1683703817_645b48095354a65737f70.png!small)  
![Untitled
11.png](https://image.3001.net/images/20230510/1683703805_645b47fd2a7c2f2299113.png!small)  
这里的Android证书和包名以及iOS的Bundile
ID，会成为id和secret调用时候的凭据，应用配置完成后会生成对应的id和secret，不知道这里会不会提示这个数据的重要，目前在官方文档和后台都没有看到对于此数据的重要性描述；看接口文档也是直接写到代码里，没有提示需要额外处理；  
![Untitled
12.png](https://image.3001.net/images/20230510/1683703780_645b47e4015681a468c2f.png!small)  
![Untitled
13.png](https://image.3001.net/images/20230510/1683703756_645b47cc45569ce3c9a25.png!small)  
通过获取的应用id和secret直接调用对应的接口，会提示如下；  
![Untitled
14.png](https://image.3001.net/images/20230510/1683703742_645b47bedf6c2b9e9a2e6.png!small)  
看到这里其他大概已经知道泄露的id和secret可以造成的风险了，然后我们再来了解一下调用微信三方的登录流程；

# 微信auth2认证流程

[准备工作 |
微信开放文档](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/WeChat_Login/Development_Guide.html)  
这里官方提供的auth2认证流程，可以看到需要三方应用带上微信用户的临时票据（code）加上appid和appsecret来跟微信开放平台兑换access_token，然后这里就有个疑问了，我接口请求也能兑换access_token，但是后续的接口请求就提示api未授权了，后面的接口不允许访问可能是因为code也可能是因为绑定了应用，还有一种可能是没有带上code参数，虽然给token，但是是无效token；不过这里没有看到相关描述，是微信开放平台的后台进行验证的，这里只能确定开放平台的appid和appsecret是无法直接拿来使用的。  
![Untitled
15.png](https://image.3001.net/images/20230510/1683703725_645b47ad8101fce8b67c7.png!small)

# 漏洞影响

通过以上分析，可以得出结论，如果泄露公众号后台的id、secret并且没有配置白名单ip访问的情况下，也就相当于后台账号密码泄露，风险等级较高；  
如果配置了访问ip白名单，可以利用access_token兑换接口的请求量消耗，造成服务不可用，不过可利用风险等级较低；  
因为泄露的是开发平台的应用id、secret，可以确定漏洞风险影响有限；

# 测试脚本

下面为文章中使用的测试脚本，也是以前测试时候用的脚本。

    
    
    # /usr/bin/env python3
    # author:samli
    # date:20220107
    # -*- coding: utf-8 -*
    
    import os
    import sys
    import re
    import requests
    import json
    
    def main(appId, appSecret):
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (appId, appSecret)
        r = requests.get(url, timeout=10)
        #print (r.json())
        token = r.json().get('access_token')
        print (type(token))
    
        url = "https://api.weixin.qq.com/cgi-bin/get_api_domain_ip?access_token=%s" % (token)
        api_domain_ip = requests.get(url, timeout=10)
        print("Domain ip:\n")
        print( api_domain_ip.json())
    
        url = "https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token=%s" % (token)
        get_current_selfmenu_inf = requests.get(url, timeout=10)
        print("Current menu:\n")
        print(get_current_selfmenu_inf.json())
    
    if __name__ == '__main__':
        print ("Usage:checkWXSDK.py AppId AppSecret \n")
    
        appId = sys.argv[1]
        appSecret = sys.argv[2]
        print ("You AppId:" + appId)
        print ("You AppSecret:" + appSecret)
        main(appId , appSecret)
    

**漏洞悬赏计划：涂鸦智能安全响应中心（https://src.tuya.com）欢迎白帽子来探索。**


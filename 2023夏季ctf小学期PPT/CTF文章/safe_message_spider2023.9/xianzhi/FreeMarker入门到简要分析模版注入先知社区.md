##### FreeMarker简介

FreeMarker 是一款 _模板引擎_ ： 即一种基于模板和要改变的数据， 并用来生成输出文本(HTML网页，电子邮件，配置文件，源代码等)的通用工具。
它不是面向最终用户的，而是一个Java类库，是一款程序员可以嵌入他们所开发产品的组件。

模板编写为FreeMarker Template Language (FTL)。它是简单的，专用的语言， _不是_ 像PHP那样成熟的编程语言。
那就意味着要准备数据在真实编程语言中来显示，比如数据库查询和业务运算， 之后模板显示已经准备好的数据。在模板中，你可以专注于如何展现数据，
而在模板之外可以专注于要展示什么数据。

##### FreeMarker语法

说白了FreeMarker和JSP的EL表达式差不多 或者 跟thymleaf的语法是差不多的。

都是使用${} 或者标签。

##### FreeMarker的简单使用

首先我这里的环境是SpringBoot整合的freemarker

  1. 引入依赖:

    
    
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-freemarker</artifactId>
    </dependency>
    

  1. 添加配置文件: 这里的数据库配置可以不添加，这里是为了测试其他东西加的数据库的配置。这里指定了template-loader-path表示模版加载的路径在templates目录下。以及他的后缀名suffix，设置为了.html 也可以设置为.ftl 官方标准可以设置为.ftl。
    
        server:
      port: 8081
    spring:
      datasource:
        #数据库名称与密码
        username: root
        password: 123456
        driver-class-name: com.mysql.cj.jdbc.Driver
        url: jdbc:mysql://localhost:3306/crm?useSSL=false&serverTimezone=Asia/Shanghai&useUnicode=true&characterEncoding=utf-8&allowPublicKeyRetrieval=true
      freemarker:
        #指定HttpServletRequest的属性是否可以覆盖controller的model的同名项
        allow-request-override: false
        #req访问request
        request-context-attribute: req
        #后缀名freemarker默认后缀为.ftl，当然你也可以改成自己习惯的.html
        suffix: .html
    
        #设置响应的内容类型
        content-type: text/html;charset=utf-8
        #是否允许mvc使用freemarker
        enabled: true
        #是否开启template caching
        cache: false
        #设定模板的加载路径，多个以逗号分隔，默认: [“classpath:/templates/”]
        template-loader-path: classpath:/templates/
        #设定Template的编码
        charset: UTF-8
    #显示日志
    logging:
      level:
        com.zxy.code.mapper: debug

  2. 创建Controller,在域中存储几条数据。比如msg对应的就是你好，老铁，最后通过return "index" 跳转到index.html的页面
    
        @GetMapping
        public String index(Model model){
            model.addAttribute("msg","你好，老铁");
            model.addAttribute("msg","nihao");
    
            model.addAttribute("flag",true);
            model.addAttribute("createData",new Date());
            return "index";
        }
    

  3. 创建index.html
    
        <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title></title>
    </head>
    <body>
    <h1>hello,家人们</h1>
    <h1>msg:${msg}</h1>
    <!--表达式，此时变成字符创类型-->
    <h1>f1:${flag?string}</h1>
    <!--?string 和 ?c是一样的-->
    <!--相当于三元运算符，针对类型转换-->
    ${flag?string("yes","no")}
    <!--        ${flag?string("yes","no")}
        转换flag为string类型 判断如果是true 那么输出yes 如果是false 那么输出no
    -->
    
    <!--日期类型
        在freemarker中日期类型不能直接输出 需要转换成日期型字符串
        1.年月日 ? date
        2.时分秒 ? time
        3 年月日时分秒 ?datetime
        4 自定义格式 ?string("自定义")
    -->
    ${createData?date}
    ${createData?time}
    ${createData?datetime}
    ${createData?string("yyyy/MM/dd HH")}
    <br>
    <!--字符串类型-->
    <h5>字符串类型</h5>
    ${msg} --    <!--截取字符串-->
    ${msg?substring(0,1)}
    <!--首字母小写输出-->
    ${msg?uncap_first}
    <!--首字母大写输出-->
    ${msg?cap_first}
    
    </body>
    </html>
    

  4. 运行结果:这里从运行结果得出我们可以使用${msg} 从域中取出数据以及使用?来转换类型以及可以使用一些substring函数来截取字符串等等。

![](./img/8174476266758418106.png)

##### FreeMarker可能产生的漏洞

我们如果给域中存储的数据如果是一个 <script>alert(1)</script> 恶意字符串 他会不会解析呢？

  1. 可能产生的XSS漏洞:我们给域中存储一个<script>alert(1)</script>字符串，在页面进行取数据的时候会不会造成XSS呢？

![](./img/8443688716783593120.png)  
![](./img/4700648123155832286.png)  
可以看到成功解析了script标签

![](./img/2177895648371110856.png)

  1. 可能产生的RCE漏洞

payload:

    
        <#assign value="freemarker.template.utility.Execute"?new()>${value("open -a Calculator")}
    

将这个payload存储到域数据中进行取出我们会发现成功弹出了计算器。

![](./img/375113688376678977.png)

##### 漏洞分析

我们来分析一下这个payload为什么会造成这个漏洞。

<#assign value="freemarker.template.utility.Execute"?new()>${value("open -a
Calculator")}

这个assign在freemarker中表示指令，value就是键 后面的就是值。

比如我们定义了一个aa 他的值就是hello 我们可以通过${aa} 将hello这个值进行取出。

![](./img/3208088455515587979.png)  
可以看到这里是成功取出的。

![](./img/4936754112575501219.png)  
接下来我们来看下这个payload,这个payload我们现在可以看到value键
值就是freemarker.template.utility.Execute"?new()

<#assign value="freemarker.template.utility.Execute"?new()>${value("open -a
Calculator")}

那么我们参考官方文档来可以看到，这条语句是什么意思。其实在Freemarker2.3.17开始之后就只吃TemplateModel了。

所有实现了了TemplateModel的都可以进行调用。

也就是说我们可以调用实现了TemplateModel这个接口的所有类的构造方法。

![](./img/2867086429770670288.png)  
我们来看一下我这里创建了一个Test测试的一个类。这个类中没有什么特别的地方只有一个空参构造器和一个hello方法。我们尝试使用freemarker的assign指令来进行调用他的构造方法。

![](./img/5146464825763165588.png)  
<#assign value="com.springboot.pojo.Test"?new()>  
我们来看到是否会输123，可以发现成功调用了构造方法。

![](./img/5123347235432339833.png)  
那我们现在再来看payload,我们可以发现他调用的是Execute类的空参构造方法。

<#assign value="freemarker.template.utility.Execute"?new()>${value("open -a
Calculator")}

那我们可以发现他也实现了TemplateModel接口。

这里他实现了TemplateMethodModel接口 TemplateMethodModel接口实现了TemplateModel。

这样就符合官网所说的条件了。

![](./img/8672689965436384020.png)  
那我们继续来看payload,可以发现后面还有一条语句也就是${value("open -a Calculator")} 这个其实就是我们给他传递的参数。

    
    
    <#assign value="freemarker.template.utility.Execute"?new()>
    ${value("open -a Calculator")}
    

具体分析的一个流程有点繁琐，大家可以看这位师傅的文章。

    
    
    https://blog.csdn.net/qq_38154820/article/details/127982704?utm_medium=distribute.pc_relevant.none-task-blog-2~default~baidujs_baidulandingword~default-1-127982704-blog-126931749.235^v38^pc_relevant_anti_vip&spm=1001.2101.3001.4242.2&utm_relevant_index=2
    

我们在Execute类中下一个断点来看他是不是传递的这个参数。可以看到这里正是我们传递的参数，他其实传递过去的是一个List集合，然后从List集合中取出0下标的也就是open
-a Calculator 然后进行命令执行。

![](./img/1606688666058250582.png)

那么我们以后在代码审计中的时候可以注意注意freemarker这个点。

好啦这个基本上就结束了，大家想去跟具体的流程的话可以访问上面的文章一个一个断点去跟。


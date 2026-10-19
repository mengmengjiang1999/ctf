![](https://image.3001.net/images/20210322/1616392853_605832956c4e7247c020c.jpg!small)

## 写在前面的话

在这篇文章中，我们将讨论我们在内部网络渗透测试期间在戴尔OpenManage Server
Administrator（OMSA）中发现的一个文件读取漏洞，漏洞编号为[
_CVE-2020-5377_](https://nvd.nist.gov/vuln/detail/CVE-2020-5377)，以及一个针对[
_CVE-2021-21514_](https://www.dell.com/support/kbdoc/en-us/000183670/dsa-2021-040-dell-emc-openmanage-server-administrator-omsa-security-update-for-multiple-vulnerabilities)漏洞修复程序的绕过方案。

根据研究人员的分析，结合该漏洞以及身份认证绕过，未经身份验证的用户将能够实现任意文件读取，受该漏洞影响的OMSA版本为9.4.0.0和9.4.0.2。

除此之外，在发现这些漏洞的过程中，我们还发现曾在[ _2016年披露_](https://www.exploit-db.com/exploits/39486)的一个任意文件读取漏洞仍然存在于OMSA的最新版本中，也有可能是因为这个漏洞从来没有被修复过。

目前，研究人员已将漏洞信息上报给了戴尔公司，但戴尔方面表示，这是应用程序的预期功能，并且不会修复该问题。

## OpenManage Server Administrator（OMSA）是什么？

 **根据OMSA的官方文档描述：**

> “OpenManage Server
> Administrator（OMSA）是一个软件代理，它通过两种方式提供全面的一对一系统管理解决方案：即基于Web浏览器的图形用户接口，以及操作系统端的命令行接口。”

换句话说，OMSA可以帮助开发人员对安装了OMSA的服务器进行中央监控。OMSA还支持通过中央Web接口和分布式Web服务器（DWS），以及“管理系统登录”功能来管理远程系统。

## OMSA中的身份认证绕过

为了简要概述绕过身份验证的工作方式，OMSA提供了使用中央服务器登录远程系统的功能，以便利用分布式Web服务器（DWS）并通过单个Web界面对远程系统进行管理。默认配置下系统会自动启用该功能。

接下来，我们就可以通过托管一个恶意远程节点来绕过身份验证，该节点响应来自OMSA服务器的身份验证请求并验证登录，从而导致OMSA服务器为用户发出一个Web会话。这个Web会话仅用于在集中式Web界面中呈现来自远程节点的内容。但是，我们发现在OMSA的9.4.0.0和9.4.0.2版本中，此会话将允许用户对底层API进行特权访问。

下图显示的是设置界面中管理系统登录功能的开启和关闭：

![](https://image.3001.net/images/20210322/1616392873_605832a9da29af743d9fe.png!small)

下图显示的是OMSA身份认证绕过步骤的流程图：

![](https://image.3001.net/images/20210322/1616392880_605832b06c712416f9fff.png!small)

在第四步中，服务器会发送一个JSESSIONID cookie和一个VID，并授权一个特权会话发送给OMSA
Web接口，接下来我们就可以用它直接向OMSA服务器发出后续的特权API请求。

## 文件读取漏洞细节

OMSA Web接口使用的是Apache Tomcat，通过分析web.xml，我们会发现身份认证servlet会暴露在/DownloadServlet：

    
    
    <servlet><servlet-name>DownloadServlet</servlet-name><servlet-class>com.dell.oma.servlet.secure.DownloadServlet</servlet-class></servlet>

反编译OMSA.jar文件并分析类文件后，我们发现了一个明显的文件读取漏洞：

    
    
    string str1 = paramHttpServletRequest.getParameter("file");
    
    <SNIP ----->
    
    File file = new File(str1);
    
        if (false == oMAWPUtil.checkUserRights(paramHttpServletRequest, 7)) {
    
          String str4 = file.getCanonicalPath();
    
          String str5 = "apache-tomcat" + File.separator + "temp";
    
          OMALogging.getInstance().write(9, "DownloadServlet : Canonical path :" + str4);
    
          if (!str4.contains(str5)) {
    
            OMALogging.getInstance().write(9, "DownloadServlet : access denied to file :" + str1);
    
            return;
    
          }
    
        }
    
     
    
    <SNIP--->
    
     
    
        FileInputStream fileInputStream = null;
    
        String str3 = getServletContext().getMimeType(str1);
    
        paramHttpServletResponse.setContentType(str3);
    
        paramHttpServletResponse.setHeader("Content-Disposition", "attachment; filename=\"" + str2 + "\";");
    
        paramHttpServletResponse.setContentLength((int)file.length());
    
        ServletOutputStream servletOutputStream = paramHttpServletResponse.getOutputStream();
    
        try {
    
          fileInputStream = new FileInputStream(str1);
    
          int j = 0;
    
          while ((j = fileInputStream.read()) != -1)
    
            servletOutputStream.write(j);
    
    }

我们可以看到，“file”这个GET参数被设置为了“str1”，并被传递给了FileInputStream，然后读取进了应用程序的响应之中。这里唯一的检测就是我们Web会话的“用户权限”为“7”，这也是通过身份认证绕过获取到的会话所满足的条件，这将允许我们在目标文件系统上读取任何我们想要的路径。

 **存在漏洞的请求如下：**

    
    
    https://omsa.server/{VID}/DownloadServlet?help=Certificate&app=oma&vid={VID}&file=C:\some\file

## 戴尔漏洞CVE-2021-21514：安全过滤器绕过

CVE-2020-5377漏洞修复后，开发人员引入了一个安全过滤器，目的就是为了保护DownloadServlet这个servlet免受任意文件读取漏洞的影响，但并没有什么效果。

调用DownloadServlet时，程序会使用过滤器查找传递到DownloadServlet的恶意路径，恶意请求将会被拒绝。

过滤器如下：

    
    
    <filter-name>PathManipulationFilter</filter-name>
    
    <filter-class>security.web.PathManipulationFilter</filter-class>

相关的反编译类代码段如下：

    
    
    public static boolean isFileHandlerRequest(String paramString) {
    
        boolean bool = false;
    
        Set<String> set = a.keySet();
    
        Iterator<String> iterator = set.iterator();
    
        String str = null;
    
        while (iterator.hasNext()) {
    
          str = iterator.next();
    
          if (StringUtil.trim(paramString).contains(str)) {
    
            bool = true;
    
            break;
    
          }
    
        }
    
        return bool;
    
      }
    
     
    
    <SNIP>
    
     static {
    
        a = new HashMap<>();
    
        HashMap<Object, Object> hashMap1 = new HashMap<>();
    
        hashMap1.put("file_1", "oma_\\d+.(log|html|zip)$");
    
        hashMap1.put("file_2", "\\.*(\\.cer|\\.CER)$");
    
        a.put("DownloadServlet", hashMap1);
    
        HashMap<Object, Object> hashMap2 = new HashMap<>();
    
        hashMap2.put("file_1", ".*");
    
        a.put("UploadServlet", hashMap2);
    
        HashMap<Object, Object> hashMap3 = new HashMap<>();
    
        hashMap3.put("file_1", ".*");
    
        a.put("UploadCertServlet", hashMap3);
    
        HashMap<Object, Object> hashMap4 = new HashMap<>();
    
        hashMap4.put("path_1", "(\\\\|\\/)(oma|upload)(\\\\|\\/)\\d+");
    
        hashMap4.put("path_2", "(\\\\|\\/)temp");
    
        a.put("ViewFile", hashMap4);
    
      }

上面的代码显示了过滤器代码的一个片段，每个请求的URL都会被传递给isFileHandlerRequest方法，以测试URL是否包含HashMap
“a”中列出的任何字符串。由于“a”只包含文本字符串，因此不用考虑任何类型的编码。只需对URL路径的一部分进行URL编码，即可完全绕过此过滤器，从而导致isFileHandlerRequest方法返回false。

 **现在的URL如下：**

    
    
    https://omsa.server/{VID}/DownloadServle%74?help=Certificate&app=oma&vid={VID}&file=C:\some\file

其中的t被URL编码后为%74，请求将成功。

## 漏洞概念验证PoC

为了验证漏洞的有效性，我们创建了一个【[
_漏洞利用PoC_](https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2020-5377_CVE-2021-21514)】，其中包含一个有效的会话Cookie，并且可以使用这个会话从服务器端读取一个文件。

 **演示Gif地址：** 【[点我查看](https://rhinosecuritylabs.com/wp-content/uploads/2021/03/OpenManage.gif)】

## 漏洞缓解

为此，戴尔还是发布了一个漏洞修复方案。但是，们确定使用远程管理登录绕过身份验证是预期的功能。这也就意味着，即使在安装了修复补丁之后，我们仍然可以使用本文所介绍的身份认证人熬过漏洞来获得API的有效会话cookie。如果你不需要使用远程管理登录功能的话，则应该禁用该功能以消除相关攻击面。

我们可以通过以下步骤禁用托管系统登录功能：

> 在登录屏幕上，单击“管理Web服务器”；
>
> 使用系统管理员凭据进行登录；
>
> 单击“首选项”；
>
> 将“管理系统登录”切换为“禁用”；

## 总结

利用这种身份认证绕过技术，将为我们提供很多的可能性，比如说利用API来实现一些恶意操作等等，例如本文所介绍的任意文件读取。

一旦获得了有效的会话cookie，就可以访问其他危险的功能。因此，如果您不使用OMSA
Web界面访问远程系统，我们强烈建议您禁用“托管系统登录”功能。如果您根本不使用OMSA，则应完全卸载或禁用该服务。如果它正在使用中，当然，我们建议广大用户保持运行OMSA的最新版本，或安装最新的漏洞修复补丁。

## 参考资料

> [
> _https://nvd.nist.gov/vuln/detail/CVE-2020-5377_](https://nvd.nist.gov/vuln/detail/CVE-2020-5377)
>
> [ _https://www.dell.com/support/kbdoc/en-us/000183670/dsa-2021-040-dell-emc-> openmanage-server-administrator-omsa-security-update-for-multiple-> vulnerabilities_](https://www.dell.com/support/kbdoc/en-> us/000183670/dsa-2021-040-dell-emc-openmanage-server-administrator-omsa-> security-update-for-multiple-vulnerabilities)
>
> [ _https://www.exploit-db.com/exploits/39486_](https://www.exploit-> db.com/exploits/39486)
>
> [
> _https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2020-5377_CVE-2021-21514_](https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2020-5377_CVE-2021-21514)
>
>  _<https://www.dell.com/support/article/en-us/sln322304/dsa-2020-172-dell-> emc-openmanage-server-administrator-omsa-path-traversal-> vulnerability?lang=en>_


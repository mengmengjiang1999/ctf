## 漏洞概述

Ignite Realtime Openfire是Ignite
Realtime社区的一款采用Java开发且基于XMPP（前称Jabber，即时通讯协议）的跨平台开源实时协作（RTC）服务器，它能够构建高效率的即时通信服务器，并支持上万并发用户数量。

近期，Openfire被曝存在认证绕过漏洞，未经身份认证的远程攻击者可以构造恶意请求访问受限界面，最终上传恶意文件实现远程代码执行。

  

## 受影响版本

受影响版本：3.10.0 <= Openfire < 4.6.8，4.7.0 <= Openfire < 4.7.5

  

## 漏洞分析

问题关键在于Openfire内置的Jetty Web服务器 **支持对%u002e这类非标准unicode uri的解析**
，导致之前的路径穿越漏洞（CVE-2008-6508）再次出现。

  

这里我们采用打补丁前的最新版本（4.7.4）进行分析，具体链接如下：  
https://codeload.github.com/igniterealtime/Openfire/zip/refs/tags/v4.7.4

  

先从xmppserver/src/main/webapp/WEB-INF/web.xml开始分析，这段配置定义了一个AuthCheck
filter，用于排除对部分url的权限检查，包括登录/注销页面、系统设置及其子页面、静态资源文件等：

    
    
    <filter>
        <filter-name>AuthCheck</filter-name>
        <filter-class>org.jivesoftware.admin.AuthCheckFilter</filter-class>
        <init-param>
            <param-name>excludes</param-name>
            <param-value>
                login.jsp,index.jsp?logout=true,setup/index.jsp,setup/setup-*,.gif,.png,error-serverdown.jsp,loginToken.jsp
            </param-value>
        </init-param>
    </filter>

接着查看filter，xmppserver/src/main/java/org/jivesoftware/admin/AuthCheckFilter.java

这里的excludes就是AuthCheck
filter配置的部分，然后就去调用testURLPassesExclude()，若返回true，则break，也就说明请求路径无需鉴权。

    
    
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException
    {
        ...
        // See if it's contained in the exclude list. If so, skip filter execution
        boolean doExclude = false;
        for (String exclude : excludes) {
            if (testURLPassesExclude(url, exclude)) {
                doExclude = true;
                break;
            }
        }
        if (!doExclude) {
            WebManager manager = new WebManager();
            manager.init(request, response, request.getSession(), context);
            boolean haveOneTimeToken = manager.getAuthToken() instanceof AuthToken.OneTimeAuthToken;
            User loggedUser = manager.getUser();
            boolean loggedAdmin = loggedUser == null ? false : adminManager.isUserAdmin(loggedUser.getUsername(), true);
            if (!haveOneTimeToken && !loggedAdmin && !authUserFromRequest(request)) {
                response.sendRedirect(getRedirectURL(request, loginPage, null));
                return;
            }
        }
        chain.doFilter(req, res);
    }
    

**显然，testURLPassesExclude()起到了关键作用。**

    
    
    public static boolean testURLPassesExclude(String url, String exclude) {
        ......
        if (exclude.endsWith("*")) {
            if (url.startsWith(exclude.substring(0, exclude.length()-1))) {
                // Now make sure that there are no ".." characters in the rest of the URL.
                if (!url.contains("..") && !url.toLowerCase().contains("%2e")) {
                    return true;
                }
            }
        }
        ......
    }

可以先尝试历史payload理清代码逻辑：  
payload1：/setup/setup-/../../log.js  
payload2：/setup/setup-/%2e%2e/%2e%2e/log.jsp

  

因为匹配到excludes存在的setup/setup-*，进入url检测，这里已经对”..”以及”%2e”进行了过滤，所以普通的路径遍历特征都会被拦截，但新版本中的Jetty
Web服务器支持对%u002e这类非标准unicode uri的解析，也就又给攻击者提供了一种利用方式。

  

还是以4.7.4为例，我们来分析一下其解码逻辑：

    
    
    <jetty.version>9.4.43.v20210629</jetty.version>

  

首先看org.eclipse.jetty.http.HttpURI#parse()
，这是Jetty中用于解析HTTP请求URI的方法。它的作用是将HTTP请求URI字符串解析为一个包含多个属性的Java对象，以便Jetty可以根据这些属性来处理HTTP请求，我们需要关注的是URI的路径部分是如何处理的：

    
    
    if (!encodedPath && !dot)
    {
        if (_param == null)
            _decodedPath = _path;
        else
            _decodedPath = _path.substring(0, _path.length() - _param.length() - 1);
    }
    else if (_path != null)
    {
        // The RFC requires this to be canonical before decoding, but this can leave dot segments and dot dot segments
        // which are not canonicalized and could be used in an attempt to bypass security checks.
        String decodedNonCanonical = URIUtil.decodePath(_path);
        _decodedPath = URIUtil.canonicalPath(decodedNonCanonical);
        if (_decodedPath == null)
            throw new IllegalArgumentException("Bad URI");
    }

这里给出了两个判断条件，第一，如果URI的路径部分既没有进行编码，也没有包含点或双点符号，则说明路径是正确的，可以直接使用；第二，如果URI的路径部分不为空，则需要对它进行解码和规范化操作，着重关注第二个条件，代码先使用了URIUtil.decodePath()方法对_path进行解码，得到解码后的路径字符串。然后，又使用URIUtil.canonicalPath()方法对解码后的路径字符串进行规范化，得到规范化后的路径字符串。最后，如果规范化后的路径字符串为null，则抛出IllegalArgumentException异常。

  

跟进org.eclipse.jetty.util.URIUtil#decodePath()，进一步分析%uxxxx的解码流程：

    
    
    for (int i = offset; i < end; i++)
    {
        char c = path.charAt(i);
        switch (c)
        {
            case '%':
                if (builder == null)
                {
                    builder = new Utf8StringBuilder(path.length());
                    builder.append(path, offset, i - offset);
                }
                if ((i + 2) < end)
                {
                    char u = path.charAt(i + 1);
                    if (u == 'u')
                    {
                        // 解码%uxxxx形式的Unicode字符
                        builder.append((char)(0xffff & TypeUtil.parseInt(path, i + 2, 4, 16)));
                        i += 5;
                    }
                    else
                    {
                        // 解码%xx形式的ASCII字符
                        builder.append((byte)(0xff & (TypeUtil.convertHexDigit(u) * 16 + TypeUtil.convertHexDigit(path.charAt(i + 2)))));
                        i += 2;
                    }
                }
                else
                {
                    throw new IllegalArgumentException("Bad URI % encoding");
                }
                break;
            ......
        }
    }

主要的解码逻辑写在了for循环里，它会遍历整个路径字符串，并对编码字符进行解码。其中，builder用于存储解码后的路径字符串，如果遇到%，会检查builder是否为null，如果是的话，就说明还没有解码过任何字符，需要先将%前面的字符拷贝到builder中，这样做的目的是保证解码后的uri路径完整。然后，再根据后面的字符决定unicode/ascii解码，得到解码后的路径字符串，最后由org.eclipse.jetty.util.URIUtil#canonicalPath()进行规范处理。

  

以绕过的payload为例，处理流程如下：

/setup/setup-/%u002e%u002e/%u002e%u002e/log.jsp

-> /setup/setup-/../../log.jsp

-> /log.jsp

  

此外，CVE-2021-34429的绕过逻辑也与之类似

<https://github.com/eclipse/jetty.project/security/advisories/GHSA-vjv5-gp2w-65vm>

  

## 漏洞复现

通过以上分析，攻击者仅需向受害站点发送满足漏洞触发条件的unicode uri再拼接Openfire管理后台敏感路径，即可进行权限绕过。

最常见的利用方式当然是新建账户进而接管后台：

![](https://image.3001.net/images/20230825/1692947505_64e85431179172780e9d7.png!small)

接着修改开源插件，https://github.com/igniterealtime/openfire-fastpath-plugin

 **添加恶意代码并打包为jar后上传，即可实现getshell。**

  


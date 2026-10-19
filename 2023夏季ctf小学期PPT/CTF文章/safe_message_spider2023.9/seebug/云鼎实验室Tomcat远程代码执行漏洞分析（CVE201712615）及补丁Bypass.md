作者：RicterZ@云鼎实验室

9 月 19 日，腾讯云安全中心监测到 Apache Tomcat 修复了2个严重级别的漏洞， 分别为：
信息泄露漏洞（CVE-2017-12616）、远程代码执行漏洞（CVE-2017-12615），在某些场景下，攻击者将分别能通过这两个漏洞，获取用户服务器上
JSP 文件的源代码，或是通过精心构造的攻击请求，向用户服务器上传恶意 JSP 文件，通过上传的 JSP 文件 ，可在用户服务器上执行任意代码。

云鼎实验室通过对于漏洞描述，搭建漏洞环境，并对其进行复现。此漏洞为高危漏洞，即使是非默认配置，但是一旦存在漏洞，那么攻击者可以成功上传
Webshell，并控制服务器。

#### 复现

根据描述，在 Windows 服务器下，将 readonly 参数设置为 false 时，即可通过 PUT 方式创建一个 JSP 文件，并可以执行任意代码。

通过阅读 conf/web.xml 文件，可以发现：

![](https://images.seebug.org/content/images/2017/09/d1c61c93-0988-412c-acbd-6ade8d200e39.jpg-w331s)

默认 readonly 为 true，当 readonly 设置为 false 时，可以通过 PUT / DELETE 进行文件操控。

配置 readonly 为 false：

![](https://images.seebug.org/content/images/2017/09/a4cb7120-fd98-4a2a-91f6-f1e298a675b4.jpg-w331s)

启动 Tomcat，利用 PUT 请求创建文件：

![](https://images.seebug.org/content/images/2017/09/6e5af0f6-54c7-4797-b26d-8e564e78c7c3.png-w331s)

提示 404。通过描述中的 Windows 受影响，可以结合 Windows 的特性。其一是 NTFS 文件流，其二是文件名的相关限制（如 Windows
中文件名不能以空格结尾）来绕过限制：

![](https://images.seebug.org/content/images/2017/09/e6d4db09-139b-4db7-8702-e6c98ca0cebf.png-w331s)
![](https://images.seebug.org/content/images/2017/09/cbd7e6e9-e578-468c-b35d-218f133bd176.png-w331s)

访问发现可以正常输出：
![](https://images.seebug.org/content/images/2017/09/eac5bc49-7a03-4f49-9f78-321691efaabb.png-w331s)

#### 分析

Tomcat 的 Servlet 是在 conf/web.xml 配置的，通过配置文件可知，当后缀名为 .jsp 和 .jspx 的时候，是通过
JspServlet 处理请求的：

![](https://images.seebug.org/content/images/2017/09/d09c3b1e-2e4e-43f4-bf22-bb96b12c3e21.jpg-w331s)

而其他的静态文件是通过 DefaultServlet 处理的：

![](https://images.seebug.org/content/images/2017/09/2aa8bb00-3787-478b-9d29-2c895a2c7ade.jpg-w331s)

可以得知，“1.jsp ”（末尾有一个和空格）并不能匹配到 JspServlet，而是会交由 DefaultServlet 去处理。当处理 PUT 请求时：

![](https://images.seebug.org/content/images/2017/09/d60d84b4-5312-4fcd-b454-cfe63f8fbe79.jpg-w331s)

会调用 `resources.bind`：

![](https://images.seebug.org/content/images/2017/09/568604e2-943e-4881-95b7-e2536da20f66.jpg-w331s)

dirContext 为 FileDirContext：

![](https://images.seebug.org/content/images/2017/09/f6b7f6bb-35dc-4fc2-bc32-af10751e1c71.jpg-w331s)

调用 rebind 创建文件：

![](https://images.seebug.org/content/images/2017/09/1a974543-9fdd-469b-a0b8-2bb6c0afce68.jpg-w331s)

又由于 Windows 不允许“ ”作为文件名结尾，所以会创建一个 `.jsp` 文件，导致代码执行。

#### Bypass 分析

然而，经过黑盒测试，当 PUT 地址为/1.jsp/时，仍然会创建 JSP，会影响 Linux 和 Windows 服务器，并且 Bypass
了之前的补丁，分析如下。

在进入 bind 函数时，会声明一个 File 变量：

![](https://images.seebug.org/content/images/2017/09/1c47b685-ac45-4cac-80fd-c1afbd08cf23.jpg-w331s)

进入 File 后，会对 name 进行 normalize

![](https://images.seebug.org/content/images/2017/09/4bb74da5-2159-405a-8fc1-84f9b2da992c.jpg-w331s)

最后得到的 path 就是没有最后 / 的 path 了:

![](https://images.seebug.org/content/images/2017/09/9f8ea051-d80a-43e4-a873-5a65ad7dee50.jpg-w331s)

#### 影响

由于存在去掉最后的 / 的特性，那么这个漏洞自然影响 Linux 以及 Windows 版本。而且经过测试，这个漏洞影响全部的 Tomcat 版本，从
5.x 到 9.x 无不中枪。目前来说，最好的解决方式是将 conf/web.xml 中对于 DefaultServlet 的 readonly 设置为
true，才能防止漏洞。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/398/>


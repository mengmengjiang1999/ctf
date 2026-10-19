作者：云鼎实验室

#### 一、漏洞背景

漏洞编号：CVE-2018-1999002  
漏洞等级：高危

Jenkins 7 月 18 日的安全通告修复了多个漏洞，其中 SECURITY-914 是由 Orange
（博客链接：http://blog.orange.tw/）挖出的 Jenkins 未授权任意文件读取漏洞。

腾讯安全云鼎实验室安全研究人员对该漏洞进行分析发现，利用这个漏洞，攻击者可以读取 Windows 服务器上的任意文件，对于
Linux，在特定条件下也可以进行文件读取。利用文件读取漏洞，攻击者可以获取到 Jenkins
的凭证信息，从而造成敏感信息泄露。另外，在很多时候，Jenkins 的部分凭证和其内用户的帐号密码相同，获取到凭证信息后也可以直接登录 Jenkins
进行命令执行操作等。

#### 二、漏洞分析

Jenkins 在处理请求的时候是通过 Stapler 进行处理的，Stapler 是一个 Java Web 框架。查看 web.xml
可知，Stapler 拦截了所有请求：

![](https://images.seebug.org/content/images/2018/07/58d73779-f22d-4a06-bb94-1b987307447f.png-w331s)

单步跟入 `hudson.util.PluginServletFilter`，最后会跟到
`jenkins\core\src\main\java\hudson\Plugin.java` 的 `doDynamic` 方法：

![](https://images.seebug.org/content/images/2018/07/cd0159b5-d999-4451-af5e-37c3840a62cf.png-w331s)

可以发现，Jenkins 在 serve `/plugin/SHORTNAME` 这个 URL 的时候，调用的是 StaplerResponse 的
serveLocalizedFile 方法处理静态文件的，继续跟入这个方法：

![](https://images.seebug.org/content/images/2018/07/356ba735-b474-460d-a05a-6b3bb9220567.png-w331s)

其中 request.getLocale() 是 `jetty-server-9.4.5.v20170502-sources.jar!\org\eclipse\jetty\server\Request.java`
内的，其实现为：

![](https://images.seebug.org/content/images/2018/07/9d0ed394-0fac-45f3-a86a-5236b511d2d5.png-w331s)

非常明显，Jetty 在获取 Locale 的时候直接从 HTTP Headers 里取出 Accept-Language 头，用 `-` 分割后返回了一个
Locale 对象。也就是我传入`Accept-Language: ../../../aaaa-bbbbbb` 时，那么我将会得到一个
`Locale("../../../aaaa", "BBBBBB")`对象。

最后到跟入 `stapler-1.254-sources.jar!\org\kohsuke\stapler\Stapler.java`：

![](https://images.seebug.org/content/images/2018/07/072b6236-5bb0-43db-949a-47ebe3817bfa.png-w331s)

我们可以发现，Stapler 首先将后缀名单独取出，接着将 Jenkins 目录和传入的 locale 的 language
以及后缀名拼接，然后打开这个路径。那么攻击者只需要构造出如下 HTTP 请求即可造成文件读取：

![](https://images.seebug.org/content/images/2018/07/58fd850c-69ff-4858-8bbd-20eb963d0059.png-w331s)

最后 URL 拼接的现场为：

![](https://images.seebug.org/content/images/2018/07/440048ee-a3ce-4d5b-bb26-299ca9fb4051.png-w331s)

在 Windows 下，不存在的目录可以通过 ../ 遍历过去的，而对于 Linux 则不行。那么这个漏洞在 Windows 下是可以任意文件读取的，而在
Linux 下则需要在 Jenkins plugins 目录下存在一个名字中存在 `_` 的目录才可以。

![](https://images.seebug.org/content/images/2018/07/2dd4fb7f-015c-444b-9351-fd4f5a175c0f.png-w331s)

#### 三、利用方式

一般来说，文件读取漏洞很难转化为命令执行，对于 Jenkins 也是如此。不过 Jenkins 有一个 Credentials 模块，这个模块储存了
Jenkins 的一些凭证信息，很多时候，其凭证的帐号密码是和 Jenkins
的帐号密码相同的。无论如何，在成功利用文件读取漏洞后，都要将凭证信息读取并解密，以收集更多的信息。

如果我们想获取 Jenkins 的凭证信息的话，需要以下几个文件：

  * credentials.xml
  * secrets/hudson.util.Secret
  * secrets/master.key

很幸运的是这几个文件我们都可以利用文件读取漏洞读取出来。在 Shodan 上尝试获取国外 real world 的 Jenkins 的帐号密码：

![](https://images.seebug.org/content/images/2018/07/15c96fb3-6e9f-490a-9a60-a8349c402b19.png-w331s)

当然，获取到的帐号密码是不能直接登录的，但是稍微修改一下用户名就可以成功的登录进去了：

![](https://images.seebug.org/content/images/2018/07/e8d30038-ab6e-40ba-a38a-6fb6b8ac44a7.png-w331s)

#### 四、修复方案

虽然这个漏洞危害较大，但是用户不必太过担心，因为默认安装 Jenkins 的时候匿名用户是没有可读权限的。并且此漏洞在 Linux
上被利用的可能性较小。以下为推荐的修复方案：

  * 针对此高危漏洞利用，腾讯云网站管家 WAF AI 引擎可检测并拦截，如果需要，可在腾讯云官网进一步了解
  * 在全局安全配置中将匿名用户的可读权限去掉 ![](https://images.seebug.org/content/images/2018/07/31ef24c6-06ce-496b-b6dd-f1336516fc64.png-w331s)
  * 升级到最新版本的 Jenkins（2.121.2）
  * 使用 Linux

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/648/>


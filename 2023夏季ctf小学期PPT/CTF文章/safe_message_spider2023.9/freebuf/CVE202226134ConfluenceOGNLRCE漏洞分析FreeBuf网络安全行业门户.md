## **漏洞描述**

最近 Confluence 官方通报了一个严重漏洞
CVE-2022-26134，远程攻击者在未经身份验证的情况下，可构造OGNL表达式进行注入，实现在Confluence Server或Data
Center上执行任意代码。

##  **利用范围**

Confluence Server and Data Center >= 1.3.0

Confluence Server and Data Center < 7.4.17

Confluence Server and Data Center < 7.13.7

Confluence Server and Data Center < 7.14.3

Confluence Server and Data Center < 7.15.2

Confluence Server and Data Center < 7.16.4

Confluence Server and Data Center < 7.17.4

Confluence Server and Data Center < 7.18.1

##  **环境搭建**

使用docker-compose文件进行漏洞环境搭建。

    
    
    version: '2'
    services:
      web:
        image: vulhub/confluence:7.13.6
        ports:
          - "8090:8090"
          - "5050:5050"
        depends_on:
          - db
      db:
        image: postgres:12.8-alpine
        environment: 
        - POSTGRES_PASSWORD=postgres
        - POSTGRES_DB=confluence

使用命令docker-compose up -d成功启动环境后，查看容器id等相关信息（5050为远程调试端口）。

![](https://image.3001.net/images/20220608/1654681803_62a070cb191a7db5a3fe5.png!small)进入容器后将/opt/atlassian目录下的confluence源码使用docker
cp命令复制到本地。

![](https://image.3001.net/images/20220608/1654682238_62a0727e7042af96ef96a.png!small)使用IDEA将/confluence/WEB-INF下的atlassian-bundled-plugins、atlassian-bundled-plugins-setup、lib文件拉取为依赖文件。

![](https://image.3001.net/images/20220608/1654682344_62a072e84b9db42991f32.png!small)IDEA中配置远程调试。

![](https://image.3001.net/images/20220608/1654682407_62a073270ea478a8ab9f4.png!small)在容器中/opt/atlassian/confluence/bin目录下修改setenv.sh文件，加入远程调试配置。

![](https://image.3001.net/images/20220608/1654682425_62a07339948275902d3fd.png!small)![](https://image.3001.net/images/20220608/1654682434_62a0734283c61698dafd8.png!small)访问http://IP:8090，进行相关配置（需要登录confluence官网进行证书申请）。

![](https://image.3001.net/images/20220608/1654682475_62a0736ba8d9bd12a471f.png!small)

漏洞分析环境成功搭建。

##  **漏洞复现**

成功命令执行

![](https://image.3001.net/images/20220608/1654682562_62a073c257b62a4a5d481.png!small)

##  **漏洞分析**

以登录请求为例，对confluence请求处理流程进行调试分析。

![](https://image.3001.net/images/20220608/1654682570_62a073cad827c29409f0c.png!small)

首先访问/login.action，经过一系列Filter处理后，将进入Servlet 的分发器 ServletDispatcher。

com.opensymphony.webwork.dispatcher.ServletDispatcher

![](https://image.3001.net/images/20220608/1654682589_62a073dda8a8641bb5760.png!small)在ServletDispatcher中，通过getNameSpace
、getActionName 、 getRequestMap 、 getSessionMap 、 getApplicationMap函数
，分别去获取对应的值。（使用payload=/${4*4}/）。

![](https://image.3001.net/images/20220608/1654682643_62a0741365aeb8d9a11f2.png!small)

重点分析getNamespace函数，其对应的值为namespace。

在com.opensymphony.webwork.dispatcher.ServletDispatcher#getNamespace中。

![](https://image.3001.net/images/20220608/1654682660_62a07424216fc575fa16a.png!small)通过调用com.atlassian.plugin.servlet.PluginHttpRequertWrapper#getServletPath函数，获取了请求servletPath的值。

![](https://image.3001.net/images/20220608/1654682675_62a07433a9b4f975bed44.png!small)随后进入回到com.opensymphony.webwork.dispatcher.ServletDispatcher中进入getNamespaceFromServletPath函数。

![](https://image.3001.net/images/20220608/1654682692_62a074449e644e233b468.png!small)通过对字符串的截取
，使得namespace 的取值为请求 servletPath 最后一个 / 之前的部分。

![](https://image.3001.net/images/20220608/1654682707_62a07453484fa0f18f28b.png!small)根据com.opensymphony.webwork.dispatcher.ServletDispatcher#serviceAction函数。

![](https://image.3001.net/images/20220608/1654682745_62a0747976c6e322b4247.png!small)到com.opensymphony.xwork.DefaultActionProxy#execute，实例化
DefaultActionProxy 对象，调用其execute函数。

![](https://image.3001.net/images/20220608/1654682767_62a0748f6c457499fd98b.png!small)随后进入com.opensymphony.xwork.DefaultActionlnvocation#invoke函数，通过Next获取拦截器对象。

![](https://image.3001.net/images/20220608/1654682785_62a074a1ed33b532ad764.png!small)继续跟进来到com.opensymphony.xwork.interceptor.Aroundlnterceptor#intercept，发现invoke函数通过调用intercept方法，形成迭代循环。

![](https://image.3001.net/images/20220608/1654682801_62a074b180aff401031f9.png!small)通过不断调试，发现在满足一定条件之后，将不会继续调用invoke函数，而是将返回
notpermitted 并赋值给 resultCode，跳出循环。

![](https://image.3001.net/images/20220608/1654682816_62a074c0c53a9daa37650.png!small)随后进入com.opensymphony.xwork.ActionChainResult#execute函数。

![](https://image.3001.net/images/20220608/1654682837_62a074d51b0b01bc3cfa1.png!small)这里通过getNamespace获取namespace的值，前面我们已经分析出来：namespace的取值为请求servletPath最后一个/之前的部分。

![](https://image.3001.net/images/20220608/1654682851_62a074e3b1fec24e9d3d0.png!small)继续跟进，在com.opensymphony.xwork.ActionChainResult中，会调用translateVariables函数对OGNL表达式进行解析，表达式的值为namespace的取值。

![](https://image.3001.net/images/20220608/1654682889_62a075090d967144f7bc2.png!small)在com.opensymphony.xwork.util.TextParseUtil#translateVariables中。

![](https://image.3001.net/images/20220608/1654682905_62a0751935d81b06072cd.png!small)调用了com.opensymphony.xwork.util.OgnlValueStack#findValue函数对表达式进行解析。

![](https://image.3001.net/images/20220608/1654682921_62a07529b9c73dd225af5.png!small)一系列操作之后，findValue返回的字符串为16。

![](https://image.3001.net/images/20220608/1654682936_62a0753802db2c52b28f7.png!small)成功触发
OGNL 表达式注入。

![](https://image.3001.net/images/20220608/1654682952_62a0754808b2697040a85.png!small)

##  **修复建议**

建议升级到Atlassian Confluence Server and Data Center至安全版本。

下载链接：

https://www.atlassian.com/software/confluence/download-archives

##  **沙箱绕过**

从 v7.15 系列开始，Confluence 在 OGNL 表达式解析时加入了沙箱限制，采取了黑名单、白名单等方式。

绕过的技巧：白名单（限制为静态方法调用）中，仍然有一些静态方法可绕过沙箱限制或者沙箱本身逻辑上也存在相关缺陷可实现方法调用。

##  **参考材料**

1\. https://www.little2pig.work/archives/cve-2022-26134

2\. https://my.atlassian.com/products/index

3\. https://attackerkb.com/topics/BH1D56ZEhs/cve-2022-26134/rapid7-analysis

4\. https://cve.mitre.org/cgi-bin/cvename.cgi?name=2022-26134

5\. https://www.tarlogic.com/blog/cve-2022-26134-zero-day-vulnerability-affecting-atlassian-confluence/


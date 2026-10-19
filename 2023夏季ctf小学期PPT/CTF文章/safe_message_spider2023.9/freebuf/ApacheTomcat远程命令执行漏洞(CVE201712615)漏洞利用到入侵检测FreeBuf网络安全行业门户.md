>
> **[本文作者：i春秋作家——Anythin9](https://bbs.ichunqiu.com/thread-33171-1-1.html?from=beef)**  
>

 **1.漏洞简介**

 ****当 Tomcat运行在Windows操作系统时，且启用了HTTP PUT请求方法（例如，将 readonly 初始化参数由默认值设置为
false），攻击者将有可能可通过精心构造的攻击请求数据包向服务器上传包含任意代码的 JSP 文件，JSP文件中的
**[恶意代码](https://bbs.ichunqiu.com/thread-33171-1-1.html?from=beef)**
将能被服务器执行。导致服务器上的数据泄露或获取服务器权限。

影响范围

Apache Tomcat 7.0.0 - 7.0.81

 **2.漏洞分析** **2.1环境介绍** 服务端 Windows7 IP: 192.168.116.128

攻击端 Kali Linux IP:192.168.116.137

Apache Tomcat 7.0.79

  

 **2.2. 实验环境搭建**

 **** **2.2.1 java环境安装**  

1.官网下载jdk安装包[
**http://www.oracle.com/technetwork/java/javase/downloads/index.html**](https://bbs.ichunqiu.com/thread-33171-1-1.html?from=beef)[](http://www.oracle.com/technetwork/java/javase/downloads/index.html)

2.根据提示安装jdk

  
![1.jpg](https://image.3001.net/images/20180125/15168694178847.jpg!small)  

  
3.配置路径，我的电脑->属性->高级系统设置->环境变量->ath 添加jdk和jre路径

![2.png](https://image.3001.net/images/20180125/15168694833724.png!small)  

4.配置成功后如图：

  
![3.png](https://image.3001.net/images/20180125/15168694962083.png!small)  

 **2.2.2 Apache Tomcat安装** 1．下载地址：

**[http://www.liangchan.net/soft/download.asp?softid=9366&downid=8&id=9430](https://bbs.ichunqiu.com/thread-33171-1-1.html?from=beef)**

2.按照步骤提示，安装

![4.png](https://image.3001.net/images/20180125/15168695123834.png!small)  

3.安装成功后，访问
**[http://127.0.0.1:8080](https://bbs.ichunqiu.com/thread-33171-1-1.html?from=beef)**

  
![5.jpg](https://image.3001.net/images/20180125/15168695218785.jpg!small)  

 **2.2.3 配置Apache Tomcat服务器**
1．打开Tomcat安装目录的Tomcat7.0\conf\web.xml添加如下配置，在Tomcat7.0版本下默认配置是开启readonly的，需要手动配置readonly为false才可以进行漏洞利用

  
![6.jpg](https://image.3001.net/images/20180125/15168695391524.jpg!small)  

 **2.3 漏洞利用** **  
**

 **2.3.1 远程命令执行漏洞利用**  

1.利用PUT方法上传构造好的shell

  
![7.jpg](https://image.3001.net/images/20180125/15168718193453.jpg!small)  

查看服务器上已经存在test.jsp

  
![8.jpg](https://image.3001.net/images/20180125/15168718286937.jpg!small)  

在构造上传方法时有三种

PUT /test.jsp%20

PUT /test.jsp/

通过构造特殊的后缀来绕过，Tomcat的检测，将jsp的shell上传到服务器中。

2.利用上传的shell来进行命令执行

  
![9.jpg](https://image.3001.net/images/20180125/15168718757410.jpg!small)  

攻击成功。

  

 **2.3.2 漏洞主要攻击特征**

1.攻击方法 PUT

2.主要攻击方法 .jsp:DATA .jsp%20 .jsp/

 **3．入侵检测规则编写**

 **3.1 CVE-2017-12615漏洞入侵检测规则**

alert tcp any any -> any any (msg:"
CVE-2017-12615";flow:to_server,established;content:"UT";nocase;content:".jsp/";nocase;reference:cve,2017-12615;sid:2000015;rev:1;)

alert tcp any any -> any any
(msg:"CVE-2017-12615";flow:to_server,established;content:"UT";nocase;content:".jsp:DATA";nocase;reference:cve,2017-12615;sid:2000015;rev:1;)

alert tcp any any -> any any
(msg:"CVE-2017-12615";flow:to_server,established;content:"UT";nocase;content:".jsp%20";nocase;reference:cve,2017-12615;sid:2000015;rev:1;)

  

 **4\. 入侵检测效果验证**

 **** **4.1 CVE-2017-12615漏洞入侵检测验证**

 ****回放包cve-2017-12615.tcap

  
![10.png](https://image.3001.net/images/20180125/15168718997234.png!small)

![11.png](https://image.3001.net/images/20180125/15168719144260.png!small)

  

 **[>>>>>>黑客入门必备技能](https://www.ichunqiu.com/zhihu?from=beef)
带你入坑和逗比表哥们一起聊聊黑客的事儿他们说高精尖的技术比农药都好玩  
**


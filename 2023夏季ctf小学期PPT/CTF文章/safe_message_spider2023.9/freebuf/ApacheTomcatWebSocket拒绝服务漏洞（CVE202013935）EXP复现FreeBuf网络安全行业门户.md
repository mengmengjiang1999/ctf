## 背景

最近看到很多利用Weblogic未授权命令执行漏洞（CVE-2020-14882/14883）而产生的新的挖矿姿势和webshell上传的姿势，使得笔者在看到Apache
Tomcat WebSocket拒绝服务漏洞（CVE-2020-13935）这个时，不禁想去EXP复现下。

## 环境搭建

通过docker快速搭建tomcat9.0.36版本，效果如下：

![1604742861_5fa66ecdb9768ff36c8c9.png!small?1604742862589](https://image.3001.net/images/20201107/1604742861_5fa66ecdb9768ff36c8c9.png!small?1604742862589)

## EXP复现

根据<https://github.com/RedTeamPentesting/CVE-2020-13935>  

运行命令  
go run main.go ws://localhost/examples/websocket/echoProgrammatic  

可以看到cpu立即被占满

![1604743062_5fa66f965a2432f779e49.png!small?1604743063205](https://image.3001.net/images/20201107/1604743062_5fa66f965a2432f779e49.png!small?1604743063205)

## 受影响的版本：

Apache Tomcat 10.0.0-M1~10.0.0-M6  
Apache Tomcat 9.0.0.M1~9.0.36  
Apache Tomcat 8.5.0~8.5.56  
Apache Tomcat 7.0.27~7.0.104

## 漏洞修复方案：

-升级到Apache Tomcat 10.0.0-M7+   
-升级到Apache Tomcat 9.0.37+   
-升级到Apache Tomcat 8.5.57+


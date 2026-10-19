## 风险说明

spring-boot-actuator-logview 是一个简单的日志文件查看器作为Spring Boot执行器端点，在 0.2.13
版本之前存在着目录遍历漏洞，编号 CVE-2021-21234。漏洞本质是Spring Boot
执行器通过请求的参数来指定文件名和文件夹路径，经过组合拼接达到目录遍历，虽然源码中检查了文件名（filename）参数来防止目录遍历，但是没有检查文件夹（base）参数，造成了目录遍历

## 漏洞分析

环境下载:https://github.com/cristianeph/vulnerability-actuator-log-viewer

下载启动后，访问：http://localhost:8887/manage/log，如下图所示：

![](https://image.3001.net/images/20211028/1635432390_617ab7c66c20ba3a0829f.png!small)

多么熟悉的小黄叶啊～～～

通过访问不存在的文件报错，可以定位到漏洞触发的点：

eu.hinsch.spring.boot.actuator.logview.LogViewEndpoint.view

![](https://image.3001.net/images/20211028/1635432455_617ab80780100749c6f10.png!small)

定位到源码处：

![](https://image.3001.net/images/20211028/1635432487_617ab82735c0a770ddfca.png!small)

看到view方法接收了文件名（filename）和路径（base）参数，通过securityCheck方法对文件名进行了安全检查，定位到该方法：

![](https://image.3001.net/images/20211028/1635432539_617ab85b7ca89b0ab5a06.png!small)

Assert断言filename中是否存在"..",有则报错，无则通过，神奇的检查！

通过Debug看到并没有对base的检查，检查了个寂寞！

![](https://image.3001.net/images/20211028/1635432659_617ab8d3c1101e383bb02.png!small)

![](https://image.3001.net/images/20211028/1635432705_617ab901cf18c7c658508.png!small)

复现就很简单了：

![](https://image.3001.net/images/20211028/1635432758_617ab9361e1d127424efe.png!small)

    
    
    PayloadWindows:- http://<target_url>/manage/log/view?filename=/windows/win.ini&base=../../../../../../../../../../ - http://<target_url>/log/view?filename=/windows/win.ini&base=../../../../../../../../../../ Linux:- http://<target_url>/manage/log/view?filename=/etc/passwd&base=../../../../../../../../../../- http://<target_url>/log/view?filename=/etc/passwd&base=../../../../../../../../../../

## 处置建议

spring-boot-actuator-logview 升级到0.2.13版本

  

最后，对于用户的任何输入都应该进行严格的安全检查，做到零信任。

  

> 本文章仅供学习交流，不得用于非法用途！

## 关注我们

![](https://image.3001.net/images/20211028/1635433136_617abab0620206e90f774.jpeg!small)


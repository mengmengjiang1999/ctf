## 漏洞简介

> Apache Spark UI 提供了通过配置选项 spark.acls.enable。
> 使用身份验证过滤器，这检查用户是否有访问权限来查看或修改应用。如果启用了 ACL，则 HttpSecurityFilter
> 中的代码路径可以允许某人通过提供任意用户名来执行模拟。然后恶意用户可能能够访问权限检查功能，最终将根据他们的输入构建一个 Unix shell
> 命令，并且执行它。这将导致任意 shell 命令执行。

> 影响版本：Apache Spark 版本 3.0.3 及更早版本，版本 3.11 至 3.1.2 ，以及版本 3.2.0 至 3.2.1

## 漏洞复现

下载 Apache Spark 3.2.1 <https://archive.apache.org/dist/spark/>

<https://archive.apache.org/dist/spark/spark-3.2.1/spark-3.2.1-bin-hadoop2.7.tgz>

根据描述是需要开启 acl 功能才可以触发漏洞

开启 ACL 可以通过设定启动时的参数 `./spark-shell --conf spark.acls.enable=true`或者在
`conf/spark-defaults.conf`中添加 `spark.acls.enable true`

![image-20221013161457-mxsnri7.png](https://image.3001.net/images/20221018/1666077479_634e5327bf3ef0fb1ae86.png!small)

![image-20221013161619-irqrkdz.png](https://image.3001.net/images/20221018/1666077480_634e5328b3028a0a21dcb.png!small)

‍

构造 poc

> <http://localhost:4040/?doAs=>`[command injection here]`

![image-20221013161849-de34vw5.png](https://image.3001.net/images/20221018/1666077481_634e5329b968194d72fa4.png!small)

![image-20221013162104-il66bvk.png](https://image.3001.net/images/20221018/1666077482_634e532ad0c54a338beff.png!small)

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 漏洞分析

为了方便调试在启动脚本中添加上调试参数

    
    
    export SPARK_SUBMIT_OPTS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005"

![image-20221013163517-wmlbvvf.png](https://image.3001.net/images/20221018/1666077483_634e532bce597c7778dc8.png!small)

输入错误的执行语句时的报错信息

![image-20221013163618-0eqytla.png](https://image.3001.net/images/20221018/1666077484_634e532ccbf5094764e0a.png!small)

‍

漏洞的触发大概就在
`org.apache.spark.security.ShellBasedGroupsMappingProvider.getUnixGroups`

漏洞的调用栈应该为

    
    
    org.apache.spark.ui.HttpSecurityFilter.doFilter(HttpSecurityFilter.scala:71)  
    org.apache.spark.SecurityManager.checkUIViewPermissions(SecurityManager.scala:238)  
    org.apache.spark.SecurityManager.isUserInACL(SecurityManager.scala:381)  
    org.apache.spark.util.Utils$.getCurrentUserGroups(Utils.scala:2523)  
    org.apache.spark.security.ShellBasedGroupsMappingProvider.getGroups(ShellBasedGroupsMappingProvider.scala:34)  
    org.apache.spark.security.ShellBasedGroupsMappingProvider.getUnixGroups(ShellBasedGroupsMappingProvider.scala:43)

加上断点进行调试分析

`org.apache.spark.ui.HttpSecurityFilter#doFilter`

![image-20221013165916-i5peae7.png](https://image.3001.net/images/20221018/1666077485_634e532dd2dc851f6d697.png!small)

获取到参数 `doAS`赋值为 `effectiveUser`传到函数 `checkUIViewPermissions`

`org.apache.spark.SecurityManager#checkUIViewPermissions`

![image-20221013170121-owq0l5o.png](https://image.3001.net/images/20221018/1666077487_634e532f47742b1683898.png!small)

`org.apache.spark.SecurityManager#isUserInACL`

![image-20221013172020-cy6f107.png](https://image.3001.net/images/20221018/1666077488_634e53302cea15ca68cf1.png!small)

`org.apache.spark.util.Utils$#getCurrentUserGroups`

![image-20221013172100-47g5rlk.png](https://image.3001.net/images/20221018/1666077489_634e53314a0b9379799eb.png!small)

`org.apache.spark.security.ShellBasedGroupsMappingProvider#getGroups`

![image-20221013172123-6e2rq2q.png](https://image.3001.net/images/20221018/1666077490_634e5332449062fdad285.png!small)

`org.apache.spark.security.ShellBasedGroupsMappingProvider#getUnixGroups`

![image-20221013172259-qmm5tr2.png](https://image.3001.net/images/20221018/1666077491_634e533330d4f0d6154a2.png!small)

通过反引号将想要执行的命令包含起来，拼接到原本的命令执行语句中

`org.apache.spark.util.Utils$#executeAndGetOutput`

![image-20221013173000-fx5t318.png](https://image.3001.net/images/20221018/1666077492_634e533432791bb017787.png!small)

`org.apache.spark.util.Utils$#executeCommand`

![image-20221013173040-yfmn5ev.png](https://image.3001.net/images/20221018/1666077493_634e533551e35097d9f9d.png!small)

  

## 漏洞补丁

![image-20221013172721-42bkifq.png](https://image.3001.net/images/20221018/1666077494_634e53366e8de434071b1.png!small)

新版本的修复 删除了 `ShellBasedGroupsMappingProvider`中的
`bash`的调用，最后执行命令的语句应该变为`/usr/bin/id -Gn`\+ 传入参数

 **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

  


## 前言

 **研发** : 这漏洞都是全英文的呀？？？有没有中文版的？！

 **运维** ：本次扫描扫了多少个主机？漏洞总数多少啊？

 **安全** : 哪些漏洞是出现比较多的？把Critical、High跟踪起来！

 **领导** ：漏洞都修复完了吗？

使用Nessus完成主机漏洞扫描的甲方同学，可能对上面的问题不陌生。

Nessus 是目前全世界最多人使用的系统漏洞扫描与分析软件。总共有超过75,000个机构使用Nessus 作为扫描该机构电脑系统的软件。

将Nessus以默认字段导出的CSV报表转为中文报表(XLSX)，包含以下sheet（端口统计、是否存在EXP
可考虑加入），各位可按需自行修改代码实现，当然也欢迎留言。

> 扫描信息
>
> 扫描资产
>
> 漏洞统计
>
> Critical漏洞统计
>
> High漏洞统计
>
> 漏洞详情

## 用法

Nessus扫描完毕后，导出csv报表

![](https://image.3001.net/images/20210605/1622859578_60badf3add84dfc8e4e64.jpg!small)

以默认字段导出

![](https://image.3001.net/images/20210605/1622859633_60badf71069917081705e.jpg!small)

转换前

![](https://image.3001.net/images/20210605/1622859699_60badfb316ce11127a497.jpg!small)

Python3下执行:

 **python NessusCsvReport.py nessustest.csv result1.xlsx**

其中：

 **nesssustest.csv为导出的Nessus原始报表（自定义文件名）**

 **result.xlsx为生成的中文报表（自定义文件名）**

![](https://image.3001.net/images/20210605/1622859405_60bade8d73c2a559d3be1.jpg!small)

## 结果

###  **扫描信息**

显示扫描任务的Nessus版本、扫描插件、扫描策略等信息（Plugin ID:19506）

![](https://image.3001.net/images/20210605/1622859830_60bae03699a7b80a25ff0.jpg!small)

###  **扫描资产**

统计CSV中的所有IP（自动去重）

![](https://image.3001.net/images/20210605/1622859873_60bae061a3d076abd43e0.jpg!small)

###  **漏洞统计**

统计Critical/High/Medium/Low的数量（可自定义修改脚本显示info级别）

![](https://image.3001.net/images/20210605/1622859950_60bae0ae89c03491cf331.jpg!small)

###  **Critical漏洞统计**

统计Critica漏洞数量（不同CVE编号算多个）

![](https://image.3001.net/images/20210605/1622860004_60bae0e483f3858b69734.jpg!small)

###  **High漏洞统计**

统计High漏洞数量（不同CVE编号算多个）

![](https://image.3001.net/images/20210605/1622860021_60bae0f579c84555c9f77.jpg!small)

###  **漏洞详情**

中文漏洞详情（自动以Critical、High、Medium、Low排序）

![](https://image.3001.net/images/20210605/1622860698_60bae39a0948bcec53266.jpg!small)

## 传送门

<https://github.com/jeansgit/NessusReport>


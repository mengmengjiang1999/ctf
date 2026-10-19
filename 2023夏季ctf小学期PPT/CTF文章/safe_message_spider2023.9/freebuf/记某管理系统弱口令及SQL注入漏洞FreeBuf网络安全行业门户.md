## 前言

此次演练来源于使用谷歌搜索引擎偶然得到的站点。漏洞已上报CNVD，全程打码。本人萌新一枚，大佬勿喷。

## 实战过程

1.谷歌语法“inurl:manager”,找到此站点。  
![image.png](https://image.3001.net/images/20210601/1622530962_60b5db92a627a5d6c5cc1.png!small)

2.尝试使用一些常用的弱口令进行登录，无果。“忘记密码”处也没有利用的地方。尝试新用户激活。这里是尝试注册/激活awbb这个账号。  
![image.png](https://image.3001.net/images/20210601/1622531101_60b5dc1d1697e0365c84d.png!small)

3.但是却显示awbb这个账号已经激活了，表示此账号存在，尝试暴力破解。  
![image.png](https://image.3001.net/images/20210601/1622531154_60b5dc52794e96e0daa8a.png!small)

4.这里程序员的锅，哈哈哈。直接尝试了一下awbb/XXXXXX，成功进入后台。  
![image.png](https://image.3001.net/images/20210601/1622531252_60b5dcb448d4c8bfe9bbb.png!small)

5.登入后台之后，尝试继续寻找其他突破口。在某一处搜索框寻找到一处SQL注入。这里大意了，忘记截图了。手残党直接使用工具sqlmap来一波。得到了数据库信息。  
![image.png](https://image.3001.net/images/20210601/1622531465_60b5dd8961aa401f78109.png!small)

6.继续尝试查询XXXX里面的列名。  
![image.png](https://image.3001.net/images/20210601/1622531554_60b5dde277df973782e7e.png!small)

为了企业的数据安全，就不再做后续操作了。

## 总结

程序员在开发过程中，希望密码不要设置的过于简单，这样很容易让一些人有可乘之机。


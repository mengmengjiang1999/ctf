***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

近日在谷歌引擎查找到一个站点。是某市的某报到系统。 **漏洞已经上报CNVD，这里就当是记录分享了。**

## 过程记录

1.进来是一个管理员登陆入口，进去了之后尝试用一些弱口令进行登录。无果，这里就暂时放弃暴力破解。尝试寻找其他突破口。  
![image.png](https://image.3001.net/images/20210603/1622732804_60b8f004ac3698acec137.png!small)2.进入网站的主界面，有一处查询框。一般这样的搜索查询框可能会有SQL注入。  
![image.png](https://image.3001.net/images/20210603/1622732816_60b8f01000382d9224cb9.png!small)3.尝试能不能进行SQL注入。直接随便输入，然后在后面加上单引号进行验证。果然不出所料报错了，报错信息可以看出是access数据库，真让人头大。  
![image.png](https://image.3001.net/images/20210603/1622732826_60b8f01aacd8892586bde.png!small)4.由于url上没有明确显示可以注入的参数，怀疑可能是POST传参，于是打开Burp抓包看看。  
![image.png](https://image.3001.net/images/20210603/1622732839_60b8f027ebd86213d7182.png!small)5.是GET类型的传参，只是被隐藏了。直接使用工具sqlmap进行注入。首先是简单查询一些服务器的信息。确定能够进行SQL注入。这里保险起见，加上了“delay”参数。  
SqlMap语句：

    
    
    python sqlmap.py -u "http://XXXX//report/reportsearch.asp?XXXX&username=admin&XXXX" --delay 1 --batch -random-agent -p "username"

![image.png](https://image.3001.net/images/20210603/1622732852_60b8f03490773b75058d3.png!small)6.access数据库是没有数据库，只有表结构。所以直接查询所有的表名（与其说是查询不如说是爆破）。指定注入的参数为“username”，这里是查询到了管理员表。  
![image.png](https://image.3001.net/images/20210603/1622732985_60b8f0b94e361b59179c1.png!small)7.继续查询管理员表的列名，并且查询其值。  
![image.png](https://image.3001.net/images/20210603/1622732994_60b8f0c271c34843cbfb8.png!small)这里得到的账号密码并不能登陆管理后台。前面我也试过了，白白等了那么久。嘶......  
8.前面有看到有个表叫做login，那好吧，最后查一个，因为access数据库太慢了。成功查询到后台账号密码了。试试登陆。  
![image.png](https://image.3001.net/images/20210603/1622733050_60b8f0fa9fbc1fdca7ed3.png!small)9.成功进入后台，到此就差不多了。新手不敢做太多事情，害怕。溜了溜了。  
![image.png](https://image.3001.net/images/20210603/1622733063_60b8f10737dda48778265.png!small)

## 总结

程序员在开发过程中，难免出错，但是一些基础的防注入措施还是挺有必要的。

> （1）对进入数据库的特殊字符（’”&*;等）要进行处理。  
> （2）应严格规定数据长度，以防在一定程度上正确执行较长的SQL注入语句。


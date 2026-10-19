**前言：** Apache
Tomcat默认安装包含examples目录，里面存着众多的样例，其中session样例(目标/examples/servlets/servlet/SessionExample)允许用户对session进行操纵，因为session是全局通用的，所以用户可以通过操纵session获取管理员权限。

## 0x001 准备

###  **1.1 编写准备**

Goby

漏洞相关资料

###  **1.2 编写区域**

漏洞-PoC管理-自定义PoC

![](https://image.3001.net/images/20210119/1611044841_600697e9b31dbc5fcd32d.png!small)![](https://image.3001.net/images/20210119/1611044856_600697f8ad28fca52f93b.png!small)

自定义PoC截图

![](https://image.3001.net/images/20210119/1611045014_60069896debf79362d447.png!small)

###  **1.3 注意事项**

名称不可填写中文，否则生成会出错，但后期可修改（只支持字母、数字、下划线）。

若漏洞危害使用中文编写，会导致解决方案显示异常。

![](https://image.3001.net/images/20210119/1611045042_600698b24e18f21a990b0.png!small)

## 0x002 漏洞观察

![](https://image.3001.net/images/20210119/1611045071_600698cf1c8d647075bf1.png!small)![](https://image.3001.net/images/20210119/1611045083_600698db2f743e4367b72.png!small)

    
    
    地址：/examples/servlets/servlet/SessionExample
    标题：Apache Tomcat
    信息：Value of Session Attribute:
    信息：Name of Session Attribute:

## 0x003 填写内容

###  **3.1 漏洞信息**

根据内容填写就好，但要注意名称需英文，若需填写其它信息点击[高级配置]。

![](https://image.3001.net/images/20210119/1611045151_6006991fd4ceb44560dcc.png!small)

###  **3.2 测试**

根据请求与响应信息进行填写，需注意响应测试内容想多添加内容需鼠标左键点击第一个group（根据需求进行增加）或单独编辑PoC文件添加。

###
![](https://image.3001.net/images/20210119/1611045170_60069932a971fb68b44ae.png!small)

###  **3.3 点击提交**

![](https://image.3001.net/images/20210119/1611045186_60069942b295c4f02774c.png!small)

###  **3.4 写入监控**

通过火绒剑监控到PoC写入位置，为后期修改做准备。

![](https://image.3001.net/images/20210119/1611045203_600699532dc382ed5d4c3.png!small)

> Goby安装目录\golib\exploits\user\English_name.json

## 0x004 PoC修改

"Name": "English name" 对应显示名称

![](https://image.3001.net/images/20210119/1611045256_60069988e3de257acf7eb.png!small)根据规则添加关键信息

![](https://image.3001.net/images/20210119/1611045278_6006999ecdeb79761d114.png!small)

    
    
    {
          "type": "item",
          "variable": "$body",
          "operation": "contains",
          "value": "Value of Session Attribute:",
          "bz": ""
    }

![](https://image.3001.net/images/20210119/1611045302_600699b63032eb5583548.png!small)

## 0x005 扫描测试

![](https://image.3001.net/images/20210119/1611045349_600699e52cc652e14f53f.png!small)

> 注意：此漏洞常用于安服项目漏洞提交，实战很少应用。

## 0x006 查缺补漏

测试发现有些站点的界面语言不同，导致关键字没有价值了。

![](https://image.3001.net/images/20210119/1611045402_60069a1a4a549da6b8b8f.png!small)后发现一个不错的关键字可进行替换：SessionExample。

![](https://image.3001.net/images/20210119/1611045418_60069a2a061d70f9b737d.png!small)

> 文章来自Goby社区成员：梦幻的彼岸，转载请注明出处。


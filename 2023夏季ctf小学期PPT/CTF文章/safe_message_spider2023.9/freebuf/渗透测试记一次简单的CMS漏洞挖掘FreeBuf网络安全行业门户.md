## 前言

时光荏苒，岁月如梭。去年简单审计了某某`CMS`，本想混个证书结果却遇`CNVD`改变规则，无奈只混了一个漏洞编号，呜呜呜 ┭┮﹏┭┮ 。

## 0x01-环境&工具

    
    
    PHP 5.4.45
    
    Mysql 5.5.53
    
    BurpSuite
    
    Sublime Text
    
    phpStudy
    
    Seay源代码审计系统
    

## 0x02-基本信息

版本：逍遥商城系统`V1.1.1`

官网：http://www.qiye1000.com/xyshop/

漏洞类型：后台延时盲注

目录结构：

文件| 名称  
---|---  
admin| 后台管理目录  
api.php| api入口文件  
attachment| 图片等文件存放目录  
cache| 缓存文件目录  
config.php| 配置文件  
data| 备份文件等目录  
hook| hook文件  
index.php| 主页入口  
install| 安装文件  
module| 主页模块文件  
public| 公共资源  
template| 前端文件  
user.php| user模块入口  
  
本地环境搭建-前台界面：http://10.211.55.4/xyshop/

![image](https://image.3001.net/images/20210726/1627262897_60fe0fb13cdec8949f37d.png!small)

本地环境搭建-后台界面：http://10.211.55.4/xyshop/admin/webadmin.php

![image](https://image.3001.net/images/20210726/1627262916_60fe0fc46bbf716b64571.png!small)

本地环境搭建-网站数据库：`xyshop`

![image](https://image.3001.net/images/20210726/1627262937_60fe0fd9c4f8d6c703837.jpg!small)

## 0x03-漏洞验证

### 3.1 确定数据库长度

经测试在后台用户中心模块中的会员列表功能处，存在一处搜索功能该功能点存在`SQL`注入漏洞。

![image](https://image.3001.net/images/20210726/1627263359_60fe117f2656fb6a215f3.png!small)

在搜索框中输入想要搜索的信息，抓取数据包。

![image](https://image.3001.net/images/20210726/1627263370_60fe118ad64c0940dfac2.png!small)

经测试发现存在延时盲注。漏洞存在`name`字段中，构造的`payload`如下：

`'and(select*from(select+1)a/**/union/**/select+if(length(database())=6,sleep(5),1))='`

该`payload`会判断数据库的长度，如果数据库的长度等于6就会产生5秒的页面延时；如果不等于6就会立马返回页面。从基本信息得知我们创建的数据库名称是`xyshop`，长度等于6。  
构造好如下`URL`在浏览器中进行访问，页面会产生延时并且会有报错信息。

    
    
    URL：
    http://10.211.55.4/xyshop/admin/webadmin.php?mod=user&userlevel_id=&name=%27and(select*from(select+1)a/**/union/**/select+if(length(database())=6,sleep(5),1))=%27☎=&email=&orderby=point%7Cdesc
    

![image](https://image.3001.net/images/20210726/1627263388_60fe119c778037a340c68.jpg!small)

修改数据库的长度，页面立即返回并且没有错误信息提示。说明此长度不是数据库的长度。

    
    
    URL：
    http://10.211.55.4/xyshop/admin/webadmin.php?mod=user&userlevel_id=&name=%27and(select*from(select+1)a/**/union/**/select+if(length(database())=2,sleep(5),1))=%27☎=&email=&orderby=point%7Cdesc
    

![image](https://image.3001.net/images/20210726/1627263475_60fe11f366836327fa3dd.jpg!small)

除此之外，我们还可以利用`burpsuite`进行漏洞验证，我们设置数据库的长度为变量。根据响应包的长度不同我们可以确定数据库的长度，数据库的长度是6。

![image](https://image.3001.net/images/20210726/1627263529_60fe1229752ada3f8bb42.jpg!small)

![image](https://image.3001.net/images/20210726/1627263551_60fe123f082ccfe9852b9.jpg!small)

通过上面的操作我们可以确定出数据库的长度为6。

### 3.2 确定数据库名称

构造如下`payload`我们可以跑出数据库的名称。

`'and(select*from(select+1)a/**/union/**/select+if(ascii(substr(database(),1,1))=120,sleep(5),1))='`

在`burpsuite`中设置截取字符串的指定开始位置和字符的`ascii`值为变量。

![image](https://image.3001.net/images/20210726/1627263655_60fe12a7f1e0426430680.jpg!small)

从`Intruder`模块的结果显示，有6个数据包的长度明显与别的不同，通过查看对应的`ascii`码，我们确定出是`xyshop`。

![image](https://image.3001.net/images/20210726/1627263665_60fe12b1c4ca2b0c59d01.jpg!small)

## 0x04 代码审计

我们先抓包拿到漏洞点（后台用户中心模块中的会员列表的搜索功能处）的操作路径，如下：

    
    
    http://10.211.55.4/xyshop/admin/webadmin.php?mod=user&userlevel_id=&name=☎=&email=&orderby=point%7Cdesc
    

定位到`webadmin.php`的39行，`mod`参数值是`user`。

![image](https://image.3001.net/images/20210726/1627263679_60fe12bfe9aa7e0e4008f.png!small)

此时引入了`module`中的`user.php`。

![image](https://image.3001.net/images/20210726/1627263691_60fe12cb2e6acc5e40147.png!small)

在`user.php`中找到会员列表功能源码。获取到用户输入的内容后直接进入`db->pe_selectall`操作中，没有任何过滤防护措施。

![image](https://image.3001.net/images/20210726/1627263704_60fe12d8050d7549fd101.png!small)

继续跟进`db->pe_selectall`，在`db.class.php`的208行。

![image](https://image.3001.net/images/20210726/1627263713_60fe12e1d37c0b03baee0.png!small)

`pe_selectall`会将参数抛向`sql_selectall`，继续跟进一下。

![image](https://image.3001.net/images/20210726/1627263727_60fe12ef36381a198d4c2.png!small)

此时我们输入的数据会被直接拼接在语句中执行，造成`SQL`注入漏洞。  
综上所示，后台用户中心模块中的会员列表搜索功能处存在延时盲注漏洞。不仅`name`字段存在该漏洞，`phone`、`email`、`userlevel`等字段均存在延时盲注漏洞。  
需开发人员对用户的输入进行过滤。

## 0x05-总结

漏洞挖掘流程：

（1） 下载源码：`A5`源码、站长之家、源码之家、系统官网等。

（2） 安装网站：`PhpStudy`。

（3） 漏洞扫描、代码扫描：`awvs`、`xray`、`fortify`、`Seay`源代码审计系统。

（4） 了解程序的大致目录，比如：入口文件、配置文件、公共函数文件等。

入口文件：

`index.php`、`admin.php`文件一般是整个程序的入口，通过`index`文件可以知道程序的架构、运行流程、包含哪些配置文件，包含哪些过滤文件以及包含哪些安全过滤文件，了解程序的业务逻辑。

配置文件：

一般类似`config.php`等文件，保存一些数据库相关信息、程序的一些信息。

公共函数文件：

通过阅读该文件，可以清晰掌握用户输入的数据，哪些被过滤，哪些没有过滤等信息。

（5） 通读全文法：纯粹的白盒审计，根据入口文件，进入各个功能进行审计，比较费时费力。

（6) 定向功能分析：该方法主要是根据程序的业务逻辑来审计。常见的功能漏洞：程序初始安装、文件上传、查询、删除等等。

(7)
敏感函数分析：大多数漏洞的产生是因为函数的使用不当导致的。我们只要找到这样的一些使用不当的函数，就可以快速挖掘想要的漏洞。可以使用`Seay`源代码审计系统
这款工具，主要是利用正则匹配一些高危函数、关键函数以及敏感关键字。然后，我们就可以分析判断敏感函数的上下文，追踪参数源头。

作者：hdsec


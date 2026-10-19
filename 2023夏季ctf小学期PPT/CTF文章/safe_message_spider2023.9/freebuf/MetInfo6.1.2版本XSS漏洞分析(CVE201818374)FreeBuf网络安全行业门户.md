## 1.1 分析环境准备

 **IDE：** PhpStorm

 **MetInfo版本：** 6.1.2

 **Web环境：** phpstudy集成环境

 **PHP版本：** 5.4.45

## 1.2 漏洞概述

 **漏洞类型：** XSS漏洞

 **危险等级：** 中

 **CVE编号：** CVE-2018-18374

 **利用条件：** 该漏洞需要管理员在登录状态下访问攻击者构造的恶意链接。

 **漏洞位置：** head.php中的第20行echo输出语句

 **漏洞产生原因：** echo输出的script标签代码中，anyid值由外部输入获得，且没有做很好过滤

 **受影响版本：** 全部版本

 **修复版本：** 无

## 1.3 漏洞复现

### 1.3.1 管理员登录管理后台

使用firefox访问localhost/met/admin/登录管理后台

![image.png](https://image.3001.net/images/20181023/1540286050_5bcee66212c8a.png!small)

登录管理后台

### 1.3.2 管理员访问构造的恶意链接

使用firefox访问[http://localhost/met/admin/index.php?lang=cn&anyid=47%3Cscript%3Ealert(1)%3C/script%3E&n=admin&c=admin_admin&a=doadd，](http://localhost/met/admin/index.php?lang=cn&anyid=47%3Cscript%3Ealert\(1\)%3C/script%3E&n=admin&c=admin_admin&a=doadd%EF%BC%8C)
触发漏洞

![image.png](https://image.3001.net/images/20181029/1540784690_5bd6823247b70.png!small)

触发漏洞

## 1.4 漏洞分析

### 1.4.1 漏洞代码分析

漏洞代码在app/system/include/public/ui/admin/head.php文件20行的echo输出语句中

![image.jpg](https://image.3001.net/images/20181029/1540782330_5bd678fa65ab8.jpg!small)

危险输出

阅读代码可知，anyid的内容将直接被输出到script标签中，变量值来自$_M['form']['anyid'],看下$_M['form']['anyid']变量值来源，在app/system/include/class/common.class.php中的load_form()方法里，可以看到$_COOKIE、$_POST、$_GET变量的key为$_M['form']的key，value需要经过daddslashes函数处理。

![image.png](https://image.3001.net/images/20181029/1540782467_5bd67983ade79.png!small)

$_M[>$_M['form']['anyid']值来源

![image.png](https://image.3001.net/images/20181029/1540782537_5bd679c90dd87.png!small)

daddslashes过滤函数

第59行代码中，如果未定义"IN_ADMIN"，会使用addslashes、sqlinsert函数对传入变量进行处理，如果定义"IN_ADMIN"，只使用addslashes进行处理。全局搜索下IN_ADMIN的定义位置，在admin/index.php文件中有定义

![image.png](https://image.3001.net/images/20181029/1540782665_5bd67a49bf924.png!small)

IN_ADMIN定义

我们就是从admin/index.php文件入口进行利用的，所以对于$_GET、$_POST、$_COOKIE传入的变量值只会进行addslashes处理。

1.4.2 回溯触发路径

此处使用PhpStorm xdebug调试方式进行动态调试。在app/system/include/public/ui/admin/head.php
19行设置断点

![image.png](https://image.3001.net/images/20181029/1540782810_5bd67adad5bb4.png!small)

head.php断点

管理员登录后台后访问[http://localhost/met/admin/index.php?lang=cn&anyid=47%3Cscript%3Ealert(1)%3C/script%3E&n=admin&c=admin_admin&a=doadd，](http://localhost/met/admin/index.php?lang=cn&anyid=47%3Cscript%3Ealert\(1\)%3C/script%3E&n=admin&c=admin_admin&a=doadd%EF%BC%8C)
触发断点

![image.png](https://image.3001.net/images/20181023/1540286132_5bcee6b462703.png!small)

head.php断点触发

左下方为调用过程

![image.png](https://image.3001.net/images/20181023/1540286138_5bcee6bab29fa.png!small)

命中head.php断点调用过程

在app/system/include/class/load.class.php的243行代码下断点，重新调试

![image.png](https://image.3001.net/images/20181029/1540783045_5bd67bc558e7d.png!small)

命中call_user_func

$newclass是一个类对象，我们F7跟踪call_user_func函数调用,进入admin_admin的doadd方法，类admin_admin存在构造函数，会调用父类的构造方法，父类为admin

![image.png](https://image.3001.net/images/20181029/1540783110_5bd67c06abff9.png!small)

admin_admin.class.php

![image.png](https://image.3001.net/images/20181029/1540783181_5bd67c4d3f616.png!small)

admin.class.php

类admin继承common类，查看common类，构造函数调用load_form方法，完成对$_M['form']赋值过程

![image.png](https://image.3001.net/images/20181029/1540783285_5bd67cb5b9e2b.png!small)

common.class.php

我们再看下类admin的构造过程，其中有一步会调用check()方法，在此处下一断点，重新调试，并使用F7跟进该调用过程

![image.png](https://image.3001.net/images/20181029/1540783376_5bd67d10aafcd.png!small)

check()方法

阅读代码可知，会从cookie中取metinfo_admin_name，met_info_admin_pass进行判断，若判断未通过，则重定向到登录页面。

F8回到admin_admin.class.php的doadd方法调用

![image.png](https://image.3001.net/images/20181029/1540783435_5bd67d4bb416d.png!small)

doadd方法断点>doadd方法断点

运行到39行F7步入

![image.png](https://image.3001.net/images/20181029/1540783568_5bd67dd0db976.png!small)

template方法

发现template方法是用于模板寻址，此处我们寻址地址为template/admin_add.php。F8跳出，进入admin_add.php文件

![image.png](https://image.3001.net/images/20181029/1540783641_5bd67e1980ed6.png!small)

admin_add.php

第7行调用后进入head.php文件，触发漏洞执行

![image.png](https://image.3001.net/images/20181029/1540783849_5bd67ee96a4f4.png!small)

漏洞触发

## 1.5 漏洞分析总结

当管理员登录后台后，通过url传递的参数值anyid不会经过sqlinsert函数过滤，只经过addslashes处理后就返回到前台页面script标签中。

提供另一个触发链接：[http://localhost/met/admin/index.php?lang=cn&n=system&c=news&a=doindex&anyid=12%3Cscript%3Ealert(1)%3C/script%3E](http://localhost/met/admin/index.php?lang=cn&n=system&c=news&a=doindex&anyid=12%3Cscript%3Ealert\(1\)%3C/script%3E)

## 1.6 修复方法

修改app/system/include/function/common.func.php的daddslashes方法，当IN_ADMIN为true时，对$string进行标签过滤


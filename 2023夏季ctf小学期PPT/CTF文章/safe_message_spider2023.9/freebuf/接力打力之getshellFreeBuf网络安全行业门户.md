原创： mosi  合天智汇

##

“

前几天刚稍微学了sqlmapgetshell的一些命令

利用--os-shell写shell

利用--sql-shell执行查询语句写shell

在本地基本测试成功

找一个站试试，没想到理想总比现实好

”

##  

![图片.png](https://image.3001.net/images/20181025/1540446952_5bd15ae89eedd.png!small)  

随便点击下，猜测可能存在sql注入，首挑新闻模块测试一波（and1=1# 和and1=2#）

  
![图片.png](https://image.3001.net/images/20181025/1540446936_5bd15ad867359.png!small)  

出现不同页面，确定是布尔型盲注，并且还爆了绝对路径（ps:后面可以尝试sqlmap--os-shell写shell一波）

继续手工注入

爆数据库长度：length（database()）数据库长度为14

爆数据库名：andascii(substr(database(),1,1))>113

  
![图片.png](https://image.3001.net/images/20181025/1540446962_5bd15af28b5e7.png!small)  

利用二分法以此类推得出数据库”qmuiqihzgb_wlw”

  
![图片.png](https://image.3001.net/images/20181025/1540446970_5bd15afaad6ad.png!small)  

  
![图片.png](https://image.3001.net/images/20181025/1540446979_5bd15b038b3e3.png!small)  

  

想到利用sqlamp的teamper脚本尝试绕过

base64encode.py

apostrophemask.py

multiplespaces.py

securesphere.py

都是提示没发现表

  
![图片.png](https://image.3001.net/images/20181025/1540446992_5bd15b106f0cb.png!small)  

怀疑人生中，发现一处错误地方

这是它其中的一个表，按照命名规则，这个数据库的其他表名也有可能是‘php_’这个格式

那之前使用sqlmap没跑出表，是sqlmap内部的字典没有这些表名

  
![图片.png](https://image.3001.net/images/20181025/1540446998_5bd15b16efba2.png!small)  

确实只有一条，那我添加一些常见的上去php_admin,php_admins,php_news,php_uoloads等

嘿嘿，期待的再跑一遍，还是没发现表。。。

##

  

##  

直接爆账号密码看来是没戏了，整理下思路，之前有爆出它的绝对路径的，--os-shell试试

![图片.png](https://image.3001.net/images/20181025/1540447008_5bd15b20bbaa4.png!small)  

没有反弹shell

再试试--sql-shell

  
![图片.png](https://image.3001.net/images/20181025/1540447014_5bd15b26c6bd9.png!small)  

倒是反弹了，可是写入一句话失败

纠结了很久，才发现是权限问题，白忙活了

前面两个都需要root权限才可以

\--ia-dba

  
![图片.png](https://image.3001.net/images/20181025/1540447022_5bd15b2ef0109.png!small)  

确实不是root权限

##

  
  

##

陷入迷茫中

还是扫它一波吧

Webrobot,没得到啥有用东西

御剑倒发现了很有趣的东西

![图片.png](https://image.3001.net/images/20181025/1540447034_5bd15b3a01637.png!small)  

一个网站后台admin/login.php

另一个是/include目录，熟悉的身影，嘿嘿。被前人日过了，留下的大马。

感觉有戏，弱口令不正确。立马百度破解大马密码方法，找工具，破解这个大马的密码

  
![图片.png](https://image.3001.net/images/20181025/1540447044_5bd15b44c1b60.png!small)  

不过先确认该大马的文件名，很幸运，一扫直接出现

  
![图片.png](https://image.3001.net/images/20181025/1540447051_5bd15b4bf3931.png!small)  

  

msf利用caidao模块爆破木马密码(纯粹学习一下msf)

百度说可以利用msf的菜刀模块进行破解木马密码，打开我的msf

![图片.png](https://image.3001.net/images/20181025/1540447078_5bd15b66f3e57.png!small)  

查询菜刀模块并使用该模块

  
![图片.png](https://image.3001.net/images/20181025/1540447083_5bd15b6bde90e.png!small)  

Showoptions 看下参数设置

  
![图片.png](https://image.3001.net/images/20181025/1540447088_5bd15b70d3ba5.png!small)  

1.pass_file爆破字典

2.Rhosts目标ip

爱站一查只有一条，确实是真实ip

  
![图片.png](https://image.3001.net/images/20181025/1540447095_5bd15b7773ec6.png!small)  

3.Targeturi木马地址

设置这三个参数

![图片.png](https://image.3001.net/images/20181025/1540447100_5bd15b7c28317.png!small)  

设置完后，直接run

  
![图片.png](https://image.3001.net/images/20181025/1540447104_5bd15b80a1011.png!small)  

居然没跑出来，重复了好几遍，才突然想起，菜刀模块是破解一句话的，我这个是大马，有点尴尬。安慰自己下，权当提前学习了msf的皮毛吧

##

  
  

##

找到一个破解大马的工具

项目地址:

<https://github.com/sunnyelf/cheetah>

dump下来直接爆破密码

  
![图片.png](https://image.3001.net/images/20181025/1540447114_5bd15b8a87080.png!small)  

得到密码heiyan

  

##  

成功getshell

  
![图片.png](https://image.3001.net/images/20181025/1540447121_5bd15b919a000.png!small)  

看了一下网站结构，是个虚拟主机。就到这里就好了

通过conn文件找到数据库账号密码连接数据库，数据表确实如之前猜测一样都是php_格式

  
![图片.png](https://image.3001.net/images/20181025/1540447129_5bd15b99e1bfd.png!small)  

本来还想看下管理后台，找到网站管理员的账号密码

  
![图片.png](https://image.3001.net/images/20181025/1540447135_5bd15b9f56cab.png!small)  

可惜密码解密不了，更新它的密码，登陆一样登不上。不知咋了。over，出去透透气。

  
  


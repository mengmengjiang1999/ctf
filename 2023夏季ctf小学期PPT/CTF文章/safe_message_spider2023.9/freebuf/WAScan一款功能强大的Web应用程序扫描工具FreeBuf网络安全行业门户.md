**今天给大家介绍的是一款名叫WAScan的Web应用程序扫描工具。**

WAScan是一款开源工具，该工具采用的是基于黑盒的漏洞挖掘方法，这也就意味着研究人员无需对Web应用程序的源代码进行研究，它可以直接被当作成一种模糊测试工具来使用，并且能够对目标Web应用的页面进行扫描，提取页面链接和表单，执行脚本攻击，发送Payload或寻找错误消息等等。

WAScan基于Python 2.7开发，能够跨平台使用。

![1.png](https://image.3001.net/images/20180810/1533897045_5b6d6955d1dd2.png!small)

## 功能介绍

### 指纹识别

> -内容管理系统 (CMS) -> 6
>
> -Web框架 -> 22
>
> -Cookies/Headers
>
> -语言 -> 9
>
> -操作系统 (OS) -> 7
>
> -服务器 -> ALL
>
> -Web应用程序防火墙 (WAF) -> 50+

### 攻击方式

> -Bash命令注入
>
> -SQL盲注
>
> -缓冲区溢出
>
> -SQL注入
>
> -XSS跨站脚本
>
> -HTML注入
>
> -LDAP注入
>
> -本地文件包含
>
> -执行操作系统命令
>
> -PHP代码注入
>
> -服务器端注入
>
> -XPath注入
>
> -XML外部实体攻击

### 代码审计

> -Apache状态页面
>
> -开放重定向
>
> -PHPInfo
>
> -Robots.txt
>
> -XST

### 暴力破解攻击

> -管理员控制面板
>
> -常见后门
>
> -常见备份目录
>
> -常见备份文件
>
> -常见目录
>
> -常见文件
>
> -隐藏参数

### 数据收集

> -信用卡数据
>
> -电子邮件
>
> -私人IP
>
> -错误信息
>
> -SSN

## 工具安装

    
    
    $ git clone <https://github.com/m4ll0k/WAScan.git> wascan
    
    $ cd wascan 
    
    $ pipinstall BeautifulSoup
    
    $python wascan.py

## 工具使用

指纹识别：

    
    
    $python wascan.py --url http://xxxxx.com/ --scan 0

![2.png](https://image.3001.net/images/20180810/1533897135_5b6d69af5a984.png!small)  

攻击执行：

    
    
    $python wascan.py --url http://xxxxx.com/index.php?id=1 --scan 1

![3.png](https://image.3001.net/images/20180810/1533897141_5b6d69b5c546e.png!small)

审计：

    
    
    $python wascan.py --url http://xxxxx.com/ --scan 2

  
  

暴力破解攻击：

    
    
    $python wascan.py --url http://xxxxx.com/ --scan 3

  
![5.png](https://image.3001.net/images/20180810/1533897157_5b6d69c5e6489.png!small)

信息收集：

    
    
    $python wascan.py --url http://xxxxx.com/ --scan 4

![6.png](https://image.3001.net/images/20180810/1533897165_5b6d69cd4b74c.png!small)

完整扫描：

    
    
    $python wascan.py --url http://xxxxx.com --scan 5

![7.png](https://image.3001.net/images/20180810/1533897173_5b6d69d52cac3.png!small)

爆破隐藏参数：

    
    
    $python wascan.py --url http://xxxxx.com/test.php --brute

![8.png](https://image.3001.net/images/20180810/1533897181_5b6d69dd45d83.png!small)

## 高级命令参考

    
    
    $python wascan.py --url <http://xxxxx.com/test.php> --scan 5 --auth"admin:1234"
    
    $python wascan.py --url <http://xxxxx.com/test.php> --scan 5 --data"id=1" --method POST
    
    $python wascan.py --url <http://xxxxx.com/test.php> --scan 5 --auth"admin:1234" --proxy xxx.xxx.xxx.xxx 
    
    $python wascan.py --url <http://xxxxx.com/test.php> --scan 5 --auth"admin:1234" --proxy xxx.xxx.xxx.xxx --proxy-auth"root:4321"
    
    $python wascan.py --url <http://xxxxx.com/test.php> --scan 5 --auth"admin:1234" --proxy xxx.xxx.xxx.xxx --proxy-auth "root:4321--ragent -v

***参考来源：[WAScan](https://github.com/m4ll0k/WAScan)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


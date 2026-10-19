![51.png](https://image.3001.net/images/20180820/1534702676_5b79b454a29d0.png!small)

## OWASPJoomScan项目

 **OWASPJoomla！漏洞扫描器（JoomScan）是一个开源项目，其主要目的是实现漏洞检测的自动化，以增强Joomla
CMS开发的安全性。该工具基于Perl开发，能够轻松无缝地对各种Joomla项目进行漏洞扫描，其轻量化和模块化的架构能够保证扫描过程中不会留下过多的痕迹。它不仅能够检测已知漏洞，而且还能够检测到很多错误配置漏洞和管理权限漏洞等等。除此之外，OWASP
JoomScan使用起来非常简单，不仅提供了非常友好的用户界面，而且还能够以HTML或文本格式导出扫描报告。**

目前，OWASP JoomScan已集成到了Kali Linux发行版之中。

## 为什么要用OWASP JoomScan

> *自动化
>
> *版本枚举
>
> *漏洞枚举（基于版本）
>
> *组件枚举（支持1209款热门组件）
>
> *组件漏洞枚举（基于版本，1030+漏洞利用）
>
> *防火墙检测
>
> *文本或HTML格式导出数据
>
> *查找常见日志文件
>
> *查找常见备份文件

## 工具安装

    
    
    git clone <https://github.com/rezasp/joomscan.git>
    
    cd joomscan
    
    perl joomscan.pl

### JoomScan参数

![52.png](https://image.3001.net/images/20180820/1534702714_5b79b47a7c89c.png!small)

## OWASPJoomScan使用样例

执行默认检测：

    
    
    perl joomscan.pl --url [www.example.com](http://www.example.com)
    
    perl joomscan.pl -u [www.example.com](http://www.example.com)

[](http://www.example.com)

枚举已安装的组件：

    
    
    perl joomscan.pl --url [www.example.com](http://www.example.com) --enumerate-components
    
    perl joomscan.pl -u [www.example.com](http://www.example.com) –ec

设置cookie：

    
    
    perl joomscan.pl --url www.example.com --cookie "test=demo;"

设置user-agent：

    
    
    perl joomscan.pl --url [www.example.com](http://www.example.com) --user-agent "Googlebot/2.1(+<http://www.googlebot.com/bot.html>)"
    
    perl joomscan.pl -u [www.example.com](http://www.example.com) -a "Googlebot/2.1(+<http://www.googlebot.com/bot.html>)"

设置随机user-agent

    
    
    perl joomscan.pl -u [www.example.com](http://www.example.com) --random-agent
    
    perl joomscan.pl --url [www.example.com](http://www.example.com) -r

更新JoomScan：

    
    
    perl joomscan.pl –update

### OWASP文档

【[传送门](https://www.owasp.org/index.php/Category:OWASP_Joomla_Vulnerability_Scanner_Project)】

### GIT仓库

【[传送门](https://github.com/rezasp/joomscan)】

### ISSUES

【[传送门](https://github.com/rezasp/joomscan/issues)】

### OWASP JoomScan介绍

***参考来源：[joomscan](https://github.com/rezasp/joomscan)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


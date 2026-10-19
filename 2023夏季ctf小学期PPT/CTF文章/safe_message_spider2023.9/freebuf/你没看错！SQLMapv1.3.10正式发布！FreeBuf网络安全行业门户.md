![](https://image.3001.net/images/20191007/1570425399_5d9aca379d70e.jpg!small)

**是的，大家没有看错，SQLMap又更新啦，此次更新的版本是v1.3.10，我们一起来看一看这一次更新又增加了哪些新的特性吧！**

对于广大渗透测试和网络安全研究人员来说，SQLMap想必是大家非常熟悉的东西了。SQLMap是一个开源的渗透测试工具，可以用来对目标应用进行自动化的SQL注入漏洞检测，并且利用已发现的SQL注入漏洞，从而帮助渗透测试人员获取到目标应用背后数据库服务器的访问权限。

SQLMap带有功能强大的漏洞扫描与检测引擎，可以针对各种不同类型数据库进行渗透测试，并且还提供了大量的渗透测试功能选项，其中包括获取数据库中存储的数据，访问目标服务器的操作系统文件，甚至还可以通过外带数据连接的方式执行操作系统命令。

## 工具官方地址

> SQLMap v1.3.10：【[ _GitHub传送门_](https://github.com/sqlmapproject/sqlmap)】

## 演示截图

![](https://image.3001.net/images/20191007/1570425414_5d9aca46ccd07.png!small)

Verbose输出（-v设置为3）

![](https://image.3001.net/images/20191007/1570425422_5d9aca4e68815.png!small)

对注入的SQLPayload进行混淆处理

![](https://image.3001.net/images/20191007/1570425431_5d9aca576e78c.png!small)

破解用户密码哈希

![](https://image.3001.net/images/20191007/1570425438_5d9aca5e820ff.png!small)

枚举数据库表中的列名

![](https://image.3001.net/images/20191007/1570425445_5d9aca65d0f29.png!small)

DNS渗透

![](https://image.3001.net/images/20191007/1570425453_5d9aca6db636a.png!small)

识别WAF/IDS/IPS保护

![](https://image.3001.net/images/20191007/1570425460_5d9aca744b7b2.png!small)

## 工具安装

广大用户可以点击【[
_这里_](https://github.com/sqlmapproject/sqlmap/tarball/master)】下载SQLMap最新的tar打包源码文件，或者点击【[
_这里_](https://github.com/sqlmapproject/sqlmap/zipball/master)】下载最新的zip打包源码文件。

但是我们建议广大用户使用git命令直接从SQLMap的[
_GitHub_](https://github.com/sqlmapproject/sqlmap)库将源码克隆至本地：

    
    
    git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev

注意：SQLMap可以在安装了[
_Python_](http://www.python.org/download/)v2.6、v2.7和3.x版本的任何操作系统平台上运行。

## 工具使用

广大用户可以使用下列命令查看SQLMap工具的基本用法及命令行参数:

    
    
    python sqlmap.py -h

广大用户可以使用下列命令查看SQLMap所有支持的使用方法及命令行参数:

    
    
    python sqlmap.py -hh

广大用户可以点击【[ _这里_](https://asciinema.org/a/46601)】查看更多的SQLMap使用样例。

除此之外，如需获取SQLMap所有支持的特性、参数、命令行选项及说明的使用帮助，请查阅这份【[
_使用手册_](https://github.com/sqlmapproject/sqlmap/wiki/Usage)】。

## 项目官网

> SQLMap：【[ _官网传送门_](http://sqlmap.org/)】
>
> 工具使用手册：【[ _WiKi传送门_](https://github.com/sqlmapproject/sqlmap/wiki)】
>
> SQLMap v1.3.10：【[ _GitHub传送门_](https://github.com/sqlmapproject/sqlmap)】

 *** 参考来源：[
_kitploit_](https://amp.kitploit.com/2019/10/sqlmap-v1310-automatic-sql-injection.html?amp=1&m=1)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


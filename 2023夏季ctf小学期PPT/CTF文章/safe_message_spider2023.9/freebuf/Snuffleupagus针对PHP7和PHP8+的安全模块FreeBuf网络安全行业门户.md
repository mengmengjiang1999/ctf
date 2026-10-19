![](https://image.3001.net/images/20210517/1621258106_60a26f7a4a3b4554f4e53.png!small)

## 关于Snuffleupagus

Snuffleupagus是一款针对针对[ _PHP 7和PHP
8+_](https://secure.php.net/)的安全模块，可以帮助广大研究人员通过封杀存在安全漏洞的整个类来大幅提高对网站的攻击成本。除此之外，它还提供了一个强大的虚拟补丁系统，允许管理员修复特定的漏洞以及审计可疑行为，而不必接触PHP代码。

## 功能介绍

> 无显著性能影响；
>
> 轻松编写虚拟补丁规则；
>
> 封杀存在漏洞的类：基于未序列化的代码执行、基于邮件的代码执行、Cookie窃取型XSS、基于文件上传的代码执行、弱伪随机数、XXE；
>
>
> 多种安全强化功能：自动设置secure和samesite等cookie标记、绑定多种规则来检测后渗透行为、全局限制模式和类型判断预防、流封装器白名单、预防可写文件执行、eval白名单/黑名单、使用curl时强制执行TLS证书验证等；
>
> 相对健全的代码库：复杂的测试用例接近100%覆盖率、clang-format代码风格、完整的参考文档；

## 工具下载

广大研究人员可以点击【[
_这里_](https://snuffleupagus.readthedocs.io/download.html)】访问该工具的下载页面，并寻找对应操作系统版本的代码包。当然了，你也可以使用下列命令将该项目源码克隆至本地，或访问该项目的【[
_Releases页面_](https://github.com/jvoisin/snuffleupagus/releases)】：

    
    
    git clone https://github.com/jvoisin/snuffleupagus.git

## 工具使用样例

我们已经在项目代码种给大家提供了多种样例规则可供大家使用，比如说：

    
    
    # 强化`chmod`函数
    
    sp.disable_function.function("chmod").param("mode").value_r("^[0-9]{2}[67]$").drop();
    
     
    
    # 缓解跟`system`相关的命令注入
    
    sp.disable_function.function("system").param("command").value_r("[$|;&`\\n]").drop();

一旦检测到了违反规则的行为，我们将会在日志中看到下列内容：

    
    
    [snuffleupagus][0.0.0.0][disabled_function][drop] The execution has been aborted in /var/www/index.php:2, because the return value (0) of the function 'strpos' matched a rule.

## 项目地址

Snuffleupagus：【[ _GitHub传送门_](https://github.com/jvoisin/snuffleupagus)】

## 参考资料

[ _https://secure.php.net/_](https://secure.php.net/)

[ _https://www.owasp.org/images/9/9e/Utilizing-Code-Reuse-Or-Return-Oriented-Programming-In-PHP-Application-Exploits.pdf_](https://www.owasp.org/images/9/9e/Utilizing-Code-Reuse-Or-Return-Oriented-Programming-In-PHP-Application-Exploits.pdf)

[ _https://blog.ripstech.com/2016/roundcube-command-execution-via-email/_](https://blog.ripstech.com/2016/roundcube-command-execution-via-email/)

[ _https://secure.php.net/manual/en/migration70.new-features.php#migration70.new-features.scalar-type-declarations_](https://secure.php.net/manual/en/migration70.new-features.php#migration70.new-features.scalar-type-declarations)

[
_https://secure.php.net/manual/en/intro.stream.php_](https://secure.php.net/manual/en/intro.stream.php)

[
_https://secure.php.net/manual/en/book.curl.php_](https://secure.php.net/manual/en/book.curl.php)

[
_https://coveralls.io/github/jvoisin/snuffleupagus?branch=master_](https://coveralls.io/github/jvoisin/snuffleupagus?branch=master)

[
_https://gitlab.com/jvoisin/snuffleupagus/pipelines_](https://gitlab.com/jvoisin/snuffleupagus/pipelines)

[ _https://snuffleupagus.rtfd.io/_](https://snuffleupagus.rtfd.io/)

[ _https://scan.coverity.com/projects/jvoisin-snuffleupagus_](https://scan.coverity.com/projects/jvoisin-snuffleupagus)

[
_https://github.com/jvoisin/snuffleupagus/tree/master/config_](https://github.com/jvoisin/snuffleupagus/tree/master/config)

[
_https://snuffleupagus.readthedocs.io/﻿_](https://snuffleupagus.readthedocs.io/)


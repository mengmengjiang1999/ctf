![Sitadel：一款功能强大的Web
应用扫描器](https://image.3001.net/images/20190122/1548088191_5c45f37f43b4f.png!small)

**Sitadel实际上是WAScan的升级版，不过是Python版本（ >=
3.4）的，这样有助于研究人员根据自己的需要去进行自定义开发，并引入新的功能模块。**

目前，Sitadel可实现扩展的功能如下：

> 前端框架检测；
>
> 内容分发网络检测；
>
> 定义扫描风险等级；
>
> 插件系统；
>
> 可使用Docker镜像进行构建和运行；

## 工具安装

    
    
    $ git clone https://github.com/shenril/Sitadel.git
    $ cd Sitadel
    $ pip install .
    $ python sitadel.py –help

## 功能介绍

### 1\. 指纹识别

> a) 服务器
>
> b) Web框架（CakePHP、CheeryPy......）
>
> c) 前端框架（AngularJS、MeteorJS、VueJS......）
>
> d) Web应用程序防火墙（Waf）
>
> e) 内容管理系统（CMS）
>
> f) 操作系统（Linux、Unix......）
>
> g) 编程语言（PHP、Ruby......）
>
> h) Cookie安全
>
> i) 内容分发网络（CDN）

### 2\. 攻击

 **（1）暴力破解**

> 管理接口
>
> 常用后门
>
> 常用备份目录
>
> 常用备份文件
>
> 常用目录
>
> 常用文件
>
> 日志文件

 **（2）注入攻击**

> HTML注入
>
> SQL注入
>
> LDAP注入
>
> XPath注入
>
> 跨站脚本（XSS）
>
> 远程文件披露（RFI）
>
> PHP代码注入

 **（3）其他攻击**

> HTTPAllow方法
>
> HTML对象
>
> 多重引用
>
> Robots路径
>
> WebDav
>
> 跨站追踪（XST）
>
> PHPINFO
>
> Listing

 **（4）漏洞利用**

> ShellShock
>
> 匿名密码（CVE-2007-1858）
>
> SPDY（CVE-2012-4929）
>
> Struts-Shock

## 参考命令

简单运行：

    
    
    python sitadel http://website.com

以“高危”风险等级运行扫描，不支持重定向：

    
    
    python sitadel http://website.com -r 2 --no-redirect

运行指定模块（查看运行日志）：

    
    
    python sitadel http://website.com -a admin backdoor -f header server –vvv

### Docker运行：

    
    
    docker build -t sitadel .
    docker run sitadel http://example.com

Sitadel项目地址：【[GitHub传送门](https://github.com/shenril/Sitadel)】

 ***参考来源：[kitploit](https://www.kitploit.com/2019/01/sitadel-web-application-security-scanner.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


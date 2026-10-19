****

[](https://youtu.be/ug5ZuezbD3c)

**password_pwncheck是一款用于帮助提升企业密码安全性的工具。它会通过大量公开的哈希数据源来匹配，你当前所使用的账户密码是否已被泄露（例如HaveIBeenPwned列表等）。同时，password_pwncheck还支持NIST
800-63B特性，例如密码最小长度检测（默认值为15），是否存在密码重用，以及密码是否命中违规列表等。**

该项目包含两个部分：

>   * 密码服务器 - 一个简单易扩展的python脚本，该脚本包含了所有密码测试的逻辑。
>   * 密码插件客户端 -> Windows密码过滤器DLL，Kerberos模块和PAM模块在管道中工作。这应该可以满足大多数现代企业可扩展密码管理解决方案。如果你觉得这还不够，那么你也自己编写代码并Pull
> Request到主项目。
>

##  **安装**

这款工具的功能和使用均已经过验证。但安装和配置则需要一定程度的知识，例如对于配置脚本中变量值作用的理解，以及Kerberos/PAM/AD如何执行密码更改管理的专业知识。而我并不是这方面的技术专家，因此在这里我只能向大家大致描述其使用方法。

##  **密码服务器**

>   *
> 密码服务器需要下载提供给它的密码哈希列表。它们应该位于./db文件夹中。推荐一个不错的查询泄露密码的网站[<https://haveibeenpwned.com/Passwords>]，感谢Troy
> Hunt所做的努力（他也是我该项目的主要灵感来源）。
>   * 另外，请确保你的密钥/证书链有效。这两个文件的路径应该与SSLCertFile和SSLKeyFile变量匹配。
>   * 该项目是用python 2.7编写的。你可以通过该命令运行python-2.7 ./pwned-password-server.py
>

##  **AD密码过滤器DLL**

>   * 从Dev Studio命令行，在ad-password-pwncheck项目的目录中运行resbuilder.bat
>   * 构建解决方案，特别是ad_password_pwncheck项目。
>   * 将生成的ad_password_pwncheck.dll复制到域中，所有域控制器上的％windir％\system32文件夹中。
>   * 运行wevtutil im Resources.man
> /rf:"%windir%\system32\ad_password_pwncheck.dll"
> /mf:"%windir%\system32\ad_password_pwncheck.dll"来正确注册Windows事件日志
>   * 运行包含的注册表文件以启用注册表设置
>

##  **Kerberos过滤器DLL**

>   * 运行./build.sh，确保openssl-devel和curl-devel模块已被加载到你的SLES/RedHat/Debian衍生版本中。
>   * 将/lib/security/krb_password_pwncheck.so库复制到kerberos plugins/pwqual文件夹。
>   * 配置krb5.conf文件正确路径：
>

 ***参考来源：[github](https://github.com/CboeSecurity/password_pwncheck)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**


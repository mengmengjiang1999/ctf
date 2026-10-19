**WordPress是一个著名的开源内容管理系统（CMS），用于创建网站和个人博客，据估计，目前35%的网站都在使用CMS。**

针对CMS平台的攻击时有发生，本文分析了针对WordPress的不同类型的攻击，以及管理访问、API、Shell部署和SEO等攻击特点。

##  通过黑客管理访问攻击WordPress站点

此方法可获得WordPress网站的管理员访问权限。攻击者可以利用漏洞或泄露的凭据进行攻击，向目标网站上的/wp-log
in.php发送POST请求来完成。

![](https://image.3001.net/images/20200106/1578271472_5e1282f0a2a4f.png!small)

成功登录后，攻击者可具有管理员权限，并进行如下操作：

> 安装带有后门的自定义主题
>
> 安装插件以上传文件

这两个操作通常在成功获得管理员权限后使用，可以选择更改管理员密码或创建新的管理员帐户。常见的方法是使用公共主题并嵌入带有远程代码执行（RCE）功能的自定义后门，文件上传插件允许攻击者直接上传有效负载。

利用一个后门部署另一个具有类似功能的后门是常见操作。当有效负载/命令/代码编码在COOKIES或POST数据中时，通过使用GET或POST请求来完成部署。解码程序会部署在先前的后门中。还观察到攻击者会patch已经存在的.php文件使恶意请求更加隐蔽。首先，记录所有可写路径，随机选择合适的路径，然后patch所选文件。

![](https://image.3001.net/images/20200106/1578277779_5e129b93d2afe.png!small)在本例中，将修补程序功能应用于index.php，以在Unix隐藏文件（点文件）中包含恶意脚本，扩展名为.ico。

![](https://image.3001.net/images/20200106/1578277826_5e129bc228681.png!small)另一个值得注意的特性是能够感染邻居域（前提是web服务器正在处理多个域，并且当前用户对其目录具有写访问权限）。

![](https://image.3001.net/images/20200106/1578277876_5e129bf4dd5ab.png!small)

##  在受感染的WordPress站点中部署Alfa Shell

攻击者会将Web shell部署在受感染的WordPress网站上。

![](https://image.3001.net/images/20200106/1578277959_5e129c47ac1c6.png!small)![](https://image.3001.net/images/20200106/1578277974_5e129c56a898b.png!small)web
shell为RCE提供了一个用户友好的界面（例如，注册CGI处理程序，允许执行Perl、Python和Bash脚本）。alfashell还能够从WordPress配置文件中获取数据库凭据，转储数据库，以及获取所有虚拟域和DNS设置。![](https://image.3001.net/images/20200106/1578278018_5e129c820322e.png!small)web
shell还支持多种平台，它能够从开发人员网站下载并执行反向shell。

![](https://image.3001.net/images/20200106/1578278058_5e129caacdfab.png!small)受感染的WordPress还可以充当广告重定向程序，通过修改JavaScript文件或页眉/页脚生成器函数（例如wp
content\theme s\twenty17\functions.php）。修改后的JavaScript将用户重定向到攻击者指定的网站。

![](https://image.3001.net/images/20200106/1578278166_5e129d1654f7d.png!small)

##  感染WordPress网站的搜索引擎优化（SEO）

受感染的WordPress站点的另一个实例是搜索引擎优化（SEO），已发现部署的PHP脚本在GET请求中接受关键字。

![](https://image.3001.net/images/20200106/1578278280_5e129d88ce805.png!small)脚本首先检查用户代理是否与正则表达式之一匹配，或者SERVER[“REMOTE_ADDR”]（发出HTTP请求的IP地址）的反向DNS查找是否包含Google子字符串。如果符合，则将$isbot变量设置为1。![](https://image.3001.net/images/20200106/1578278359_5e129dd7ed728.png!small)如果$isbot不为零，则将使用相同的关键字向程序中硬编码的URL地址发出另一个HTTP请求。如果$isbot未设置，而HTTP_REFERER包含Google、Bing或Yahoo等字符串，则会将其重定向到另一个服务网站。

![](https://image.3001.net/images/20200106/1578278417_5e129e11cc64f.png!small)如果返回的文本长度小于1000个字符，则将使用Bing搜索引擎执行其他查询，并将匹配指定正则表达式的结果附加到$text中。

如果再次执行相同的查询，则返回最终的HTML页面并将其保存在服务器上。

![](https://image.3001.net/images/20200106/1578278479_5e129e4f8360d.png!small)

如上图Cockeysville Eagle的Football网页中有一些部分包含明显不相关的JavaScript框架的文本，从而导致SEO中毒。

![](https://image.3001.net/images/20200106/1578278540_5e129e8c65450.png!small)

##  散布虚假或误导性文章

被黑客攻击的WordPress网站也可被用来传播虚假或误导性的文章，其中的内容很少或没有真实的细节，取而代之的是吸引眼球的头条和报道。

![](https://image.3001.net/images/20200106/1578278625_5e129ee1a41df.png!small)

如上面例子所示，被破坏的网站发布的故事有明显的语法错误。攻击者通过WordPress的XML-RPC接口（API）实现，API允许数据传输并执行任务，如上传新文件、编辑和发布帖子。

##  WordPress网站的安全建议

上述示例只是已知攻击者使用的技术。易受攻击的WordPress网站如果没有适当的保护，很容易被利用。为了降低风险，建议使用双因素身份验证（2FA）插件来防止凭据泄露，并及时扫描是否存在未修补的漏洞。以下是用户和站点管理员可以采取的其他措施：

> 采用基本的安全措施来减少网站的攻击面
>
> 禁用或删除过时或易受攻击的插件
>
> 使用virtual patch来解决尚未提供修补程序的漏洞
>
> 执行最小特权原则
>
> 定期更新CMS到最新版本，包括插件

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/looking-into-attacks-and-techniques-used-against-wordpress-sites/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  


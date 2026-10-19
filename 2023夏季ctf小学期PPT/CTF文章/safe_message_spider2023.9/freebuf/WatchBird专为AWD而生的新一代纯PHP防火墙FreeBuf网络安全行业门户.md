**Watchbird是一个专门为AWD而生的PHP防火墙,采用纯PHP+JS+CSS编写而成,单文件设计模式,无任何外部依赖,其特点有将原始请求包拼凑出来而实现的内网转发,基于putenv和ld_preload的命令执行保护,一个漂亮的前端以及流量重放功能.**

##  工具安装

广大研究人员可以使用下列命令直接将项目源码克隆至本地

    
    
    git clone https://github.com/leohearts/awd-watchbird.git

##  工具部署

> 1.进入下载好的文件夹目录
>
> 2.编译waf.c生成.so文件,参考命令:gcc waf.c -shared -fPIC -o waf.so
>
> 3.将waf.so,watchbird.php文件存放在/var/www/html或其他目录中
>
> 4.访问任意启用了waf的文件, 参数?watchbird=ui打开watchbird控制台, 创建一个初始密码并进行相关配置
>
> 5.将以下代码放入需要启用waf的php脚本的第一行 <?php include_once "/var/www/html/watchbird.php"
> ?>6.enjoy it!

##  功能介绍

易于配置(单文件, 无需加载外部js/css)

可以随时开启/关闭某项防御

基本防御:

> 数据库注入(sql injection)
>
> 文件上传(upload)
>
> 文件包含(lfi)
>
> flag关键字
>
> PHP反序列化(unserialize)
>
> 命令执行(rce)
>
> 分布式拒绝服务攻击(ddos)
>
> 请求头,请求参数(GET/POST)关键字
>
> 特殊字符

深度防御:

> 响应检测/反向代理(默认将流量发送至本地服务器自检,可配置代理服务器IP及端口实现反代功能)
>
> 响应flag检测并返回虚假flag

基于open_basedir的PHP文件操作保护

基于LD_PRELOAD的指令执行保护

网页控制台:

> 功能开关及配置
>
> 实时日志查看
>
> 日志流量重放, 可广播流量至指定网段
>
> RCE/文件上传/深度检测
> 防御通知(由于chrome无法允许不安全的网站(无SSL证书)显示通知,请使用Firefox并修改about:config中dom.webnotifications.allowinsecure为true)

##  工具起源

一开始做这个工具是因为即将参加awd的线下赛而又没有好用的waf,网上的waf无法满足自己的需求于是就开始着写自己的waf,一开始的构想很简单,我从网上找到了一份awd的简单waf(所以你可能会在源码的某处发现似曾熟悉的代码),然后实现了GET/POST/请求头关键字检测,文件上传检测的功能(留了个trick,上传php等恶意文件会提示上传成功),后面又加入了防ddos的功能(原理很简陋,就是记录每秒某个IP的访问次数,超过某个次数就直接die)

到后来leohearts看到了我的waf并且开始参与这个waf的编写工作,我们构想通过纯PHP的代码将原始请求包重新拼凑起来,最后将这个请求包发给自身完成自检或发送到其他靶机实现内网转发的功能,这个功能一旦实现,无疑会非常强大,我们经历了很多问题,比如BOM头,分块运输,如何获取原始的multipart/form-data等等,幸好我们最终成功实现了这个功能,也是本waf最亮眼的功能--内网转发.

过了一段时间后,leohearts的一个提议让我们重新回到waf的编写工作:基于putenv和ld_preload的命令执行保护.经由他手这个waf又实现了一个漂亮的前端方便使用人员对waf的控制,我们的灵感不断迸发,又相继实现了基于open_basedir的文件操作保护(防止使用php读取/flag),与命令执行保护构成了内外的双重防护,最后我们实现了流量重放与批量提交flag的功能.

##  工具预览

![](https://image.3001.net/images/20200420/1587379147_5e9d7bcb7c4ac.png!small)  
![](https://image.3001.net/images/20200420/1587379182_5e9d7bee339a9.jpg!small)![](https://image.3001.net/images/20200420/1587379147_5e9d7bcb9743d.png!small)

##  工具缺点

正如你所见,这个waf虽然对外很强大,但并非没有缺点,它自身仍然存在许多问题,例如open_basedir,ld_preload可以被绕过,灵活多变的PHP可以绕过关键字检测,还有由于自检可能带来的安全问题,而waf本身的安全问题由于在awd中只有ctf和www-data权限的情况下很难对waf的功能与自身安全进行增强,所以我们本着学习与交流的态度开源了本waf

##  项目地址

> [Github传送门](https://github.com/leohearts/awd-watchbird)

 ***本文作者： goodclid，转载请注明来自FreeBuf.COM**  
  


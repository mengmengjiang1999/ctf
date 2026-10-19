本文原载于公众号：[ChaBug ](https://mp.weixin.qq.com/s/_4ACLzaImDMQbZWfhSHnwg)

作者：BeichenDream

**期间，各大厂商的waf不断，在静态查杀、流量通信等方面对webshell进行拦截，众红队急需一款优秀的权限管理工具，冰蝎3.0的发布可能缓解了流量加密的困境，但是冰蝎3.0的bug众多，很多朋友甚至连不上冰蝎的shell，于是@BeichenDream决定公开他所开发的一款shell权限管理工具，名为“哥斯拉”。

# 简单使用方法

在哥斯拉安装之前，你需要安装jdk1.8的环境。双击Godzilla.jar打开，此时会在同目录下生成data.db数据库存放数据。首页长这样

![1597734585.png!small](https://image.3001.net/images/20200818/1597734585.png!small)

点击 **管理** - **添加**
生成所需的webshell，哥斯拉支持jsp、php、aspx等多种载荷，java和c#的载荷原生实现AES加密，PHP使用亦或加密。生成时需要记住自己的生成配置用以链接时用。

![1597734592.png!small](https://image.3001.net/images/20200818/1597734592.png!small)

![1597734600.png!small](https://image.3001.net/images/20200818/1597734600.png!small)

![1597734607.png!small](https://image.3001.net/images/20200818/1597734607.png!small)选中shell右键选择
**进入** 即可进入shell管理界面。

![1597734629.png!small](https://image.3001.net/images/20200818/1597734629.png!small)

jsp/jspx的shell功能如图

![1597734640.png!small](https://image.3001.net/images/20200818/1597734640.png!small)

php的功能如图

![1597734644.png!small](https://image.3001.net/images/20200818/1597734644.png!small)

aspx/ashx/asmx的功能如图

![1597734648.png!small](https://image.3001.net/images/20200818/1597734648.png!small)

简单使用介绍就到这里。

# 一些特性

为什么我放着冰蝎、蚁剑还有什么天蝎不用而要用你的哥斯拉？

> 哥斯拉全部类型的shell均过市面所有静态查杀
>
> 哥斯拉流量加密过市面全部流量waf
>
> 哥斯拉的自带的插件是冰蝎、蚁剑不能比拟的

静态免杀就不说了，工具放出来之后可能会免杀一段时间就不行了，当然随便改改就能继续过。重点是看流量加密和一些自带的插件。

## 流量加密

先来看流量加密，仍然以jsp为例，修改链接配置里的代理选项为http代理，让流量代理到Burp中。

![1597734670.png!small](https://image.3001.net/images/20200818/1597734670.png!small)

执行dir命令的请求包

![1597734687.png!small](https://image.3001.net/images/20200818/1597734687.png!small)

响应包

![1597734691.png!small](https://image.3001.net/images/20200818/1597734691.png!small)

或许你说headers里的一些ua和Accept太扎眼了，别担心，这些可以自己配置。在shell编辑的请求配置中修改

![1597734716.png!small](https://image.3001.net/images/20200818/1597734716.png!small)

或者在 **配置** - **全局配置** 中修改

![1597734726.png!small](https://image.3001.net/images/20200818/1597734726.png!small)

此时在看请求包和响应包完全没有特征

![1597734736.png!small](https://image.3001.net/images/20200818/1597734736.png!small)

![1597734754.png!small](https://image.3001.net/images/20200818/1597734754.png!small)

并且在请求包的thisisleftData和thisisrightData可以修改为其他杂乱数据来进行干扰。到这里还不说一句 **哥斯拉天下第一** ？

## 插件模块

一些基本的模块比如：基本信息、文件管理、命令执行我这里就不再赘述了。

### 数据库管理

相信大家在使用蚁剑的时候没少碰到过连不上数据库的情况，我自己碰到过一个环境就是shell所在的tomcat
container没有jdbc的jar包依赖导致连不上数据库，偏偏蚁剑没什么好办法。而在哥斯拉中就不必担心这个问题，在数据库管理中哥斯拉会先从容器中加载可用的jdbc，如果没有就通过内存加载jar驱动来链接数据库。

### 内存shell

内存shell模块实现了在tomcat中注册、卸载内存马

![1597734767.png!small](https://image.3001.net/images/20200818/1597734767.png!small)

你可以直接注册一个哥斯拉的马或者冰蝎、菜刀的马，甚至是regeorg。

![1597734778.png!small](https://image.3001.net/images/20200818/1597734778.png!small)

比如注册一个/Godzillashell进去

![1597734785.png!small](https://image.3001.net/images/20200818/1597734785.png!small)

访问发现存在

![1597734795.png!small](https://image.3001.net/images/20200818/1597734795.png!small)

直接哥斯拉链接就行了。 **内存shell 无日志，会在tomcat重启后消失。**

### 屏幕截图

点截图会自动保存预览，在windows上需要shell权限够大。

![1597734806.png!small](https://image.3001.net/images/20200818/1597734806.png!small)

### 虚拟终端

这个功能其实是在本地监听端口，通过shell与服务器交互实现cmdshell。点击start之后执行nc 127.0.0.1
4444链接本地4444获取cmdshell。

![1597734818.png!small](https://image.3001.net/images/20200818/1597734818.png!small)

如果不使用nc链接的话会一直占用本地4444端口。用完请exit或点击stop。

### JMeterpreter

![1597734830.png!small](https://image.3001.net/images/20200818/1597734830.png!small)

不用说了 看图就会

### ServletManage

![1597734853.png!small](https://image.3001.net/images/20200818/1597734853.png!small)

用来管理servlet，方便管理内存shell。

### JarLoader

![1597734864.png!small](https://image.3001.net/images/20200818/1597734864.png!small)

用其加载jar包，主要用途就是加载jdbc。

### JZip

![1597734874.png!small](https://image.3001.net/images/20200818/1597734874.png!small)

打包全站的好助手。

### ByPassOpenBasedir

![1597734883.png!small](https://image.3001.net/images/20200818/1597734883.png!small)

### BypassDisableFunctions

![1597734893.png!small](https://image.3001.net/images/20200818/1597734893.png!small)

### 笔记

笔记模块是jsp\php\aspx都有的模块

![1597734902.png!small](https://image.3001.net/images/20200818/1597734902.png!small)

### ShellCodeLoader

直接通过shell来加载shellcode，或者弹meterpreter

![1597734909.png!small](https://image.3001.net/images/20200818/1597734909.png!small)

### SafetyKatz

mimikatz 需要高权限

![1597734921.png!small](https://image.3001.net/images/20200818/1597734921.png!small)

### lemon

抓常用软件密码

![1597734937.png!small](https://image.3001.net/images/20200818/1597734937.png!small)

### BadPotato

![1597734945.png!small](https://image.3001.net/images/20200818/1597734945.png!small)

提权模块，源于 https://github.com/BeichenDream/BadPotato

### SharpWeb

![1597734952.png!small](https://image.3001.net/images/20200818/1597734952.png!small)

参考 https://github.com/djhohnstein/SharpWeb

### SweetPotato

![1597734979.png!small](https://image.3001.net/images/20200818/1597734979.png!small)

提权模块

# 其他选项

配置-程序配置中可以修改字体大小，重启后生效。

![1597734986.png!small](https://image.3001.net/images/20200818/1597734986.png!small)

关闭提示语不解释了，上帝模式开启会使文件管理复杂化。

![1597734993.png!small](https://image.3001.net/images/20200818/1597734993.png!small)

# 免责声明

> 程序仅限服务器管理使用，切勿用于非法用途，非法使用造成的一切后果由自己承担，与作者无关。
>
> 由于用户滥用造成的一切后果与作者无关。
>
> 使用本程序请自觉遵守当地法律法规，出现一切后果均与作者无关。
>
> 本程序及代码均不得用于商业用途，仅作学习交流，违者必究。

# 下载地址

> https://github.com/BeichenDream/Godzilla/releases/tag/v1.00-godzilla


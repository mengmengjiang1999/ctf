**最近买了一个TP-Link的摄像头，顺便下载的它配套的安卓应用，想看看这个应用在与服务器交互的时候都发了些啥，因此准备抓包。当我把姿势都摆好了之后，却发现它的流
量在Burpsuite里完全没出现。**

掏出祖传的`XPosed`插件`SSL
Unpinning`，竟然没用。emmmm，那可能是进行了混淆，XPosed在Hook的时候需要特定的包名，如果包名被混淆了自然是Hook不到的嘛。

## 代理流量

在系统里配置了代理却抓不到包，很有可能是因为APP有限制，禁止流量走代理。因为我是在模拟器上安装了这个APP，因此想到了强行代理这个模拟器的流量，看看会怎样。

测试中用的是`雷电模拟器`，流量转发用的是`Proxifier`。因此在`Proxifier`中配置需要拦截流量的进程名为`LdBoxHeadless.exe`的进程，来强行转发流量到我们的Burp上：

![image-20200409202521746.png](https://image.3001.net/images/20200410/1586509606_5e903726aedd2.png!small)

转发成功，现在尝试一下请求，比如找回密码功能，点击“完成”后，返回的提示竟然是“网络连接失败”？？？

![image-20200409202728285.png](https://image.3001.net/images/20200410/1586509623_5e903737d30b0.png!small)

同时，Burp收到警告，提示`Failed to negotiate a TLS connect to xxx`，表示HTTPS握手过程失败。

好吧，果然是限制了流量同时也校验了证书。

## 查看日志

既然发生了错误，那应该会有相应的报错日志，看看能不能从日志里看出点端倪。

进入`adb shell`，先输入`ps`命令查看对应进程的pid，比如这里是 `2035` ，在用`logcat | grep
2035`来过滤出该进程的日志即可。

![image-20200410143906742.png](https://image.3001.net/images/20200410/1586509630_5e90373e8dac9.png!small)

此时再点击完成按钮，提示“网络连接失败”，查看logcat打出来的日志，发现了证书错误的信息：

![image-20200410144046644.png](https://image.3001.net/images/20200410/1586509637_5e903745775fd.png!small)

## 反编译dex

看到相关的报错日志，如果有反编译出来的伪代码，看看能不能搜到相关报错的日志的语句来定位到相关代码段，顺藤摸瓜找到校验的函数，再去Hook岂不美滋滋~

先尝试一下反编译，来看看是不是被混淆过。解压`apk`，使用`dex2jar`将`classes.dex`转换成`.jar`格式，再用`Java
Decompiler`查看。看到包名的时候，发现它确实进行了混淆。

![image-20200409201406531.png](https://image.3001.net/images/20200410/1586509645_5e90374d26da6.png!small)

但是并没有看到和常见的 HTTP 相关的组件（比如`OKHttp3`）相关的包。

将报错日志的部分拆成关键词来搜索也完全搜不到相关的地方，非常让人怀疑实际上这部分逻辑就没写在Java层，很有可能在so里。

## 分析so

既然如此，进入apk包中的lib文件夹，看看它加载的so里有没有什么特别之处。从so文件的大小和名称中，第一眼就识别到了`libIPCAppContextJNI.so`文件。果断拖到ida中看看里面有什么。

在ida中加载完之后，果断的打开Strings Window来暴搜字符串。输入`verify error:num`，看看我发现了什么！

![image-20200410144726512.png](https://image.3001.net/images/20200410/1586507636_5e902f742110b.png!small)

跟进这个字符串的调用，F5，顺利找到打出这句日志的代码：

![image-20200410144929216.png](https://image.3001.net/images/20200410/1586507640_5e902f78523d3.png!small)

但是，这个函数是一个回调函数，函数名为`TPSSLManager::SSLCtxVerifyCallback`，追踪它的调用也没有找到有验证证书相关的操作，似乎又陷入僵局……

因为对证书校验的实现不是很熟悉，打破僵局的方法只能求助于度娘。看到那句日志打印的上一行`X509_verify_cert_error_string`函数，抱着死马当活马医的心态，扔进搜索引擎，竟然搜到了一堆OPENSSL的证书校验的示例代码！

通过示例代码的注释，发现OPENSSL校验证书的函数名为`X509_verify_cert`，回到ida里搜了一下，Bingo！

![image-20200410150004769.png](https://image.3001.net/images/20200410/1586507645_5e902f7d192c0.png!small)

跟进这个函数被调用的地方看了下，和示例代码一样，都是在用`if`语句在判断这个函数的返回值是1还是0，那初步确认证书校验的点就在此处。

## Frida Hook

由于测试是在雷电模拟器里做的，因此需要下载并运行x86版本的`Frida-server`。给萌新的一个小提示：Frida运行需要关闭SELinux，可以在adb shell中输入`setenforce 0`来关闭它。

### 确认函数地址

在写JS脚本之前，先使用Frida的命令行来确认一下要Hook的模块和函数是否可用（个人觉得这样便于调试）。在PC端的命令行输入`frida -U
com.tplink.ipc`连接.

进入后输入`Module.findExportByName("libIPCAppContextJNI.so",
"X509_verify_cert")`应该能打印出`X509_verify_cert`函数的入口地址，但是竟然返回的是`null`。此时有点慌了，难道我的判断出错了吗？

![image-20200410151702592.png](https://image.3001.net/images/20200410/1586507650_5e902f82301cd.png!small)

果断使用`Process.enumerateModules()`命令，会在命令行中打印出所有的模块（即加载的so），找了一下发现也没有`libIPCAppContextJNI.so`，甚至路径几乎都是`/system/lib`这样系统路径下的文件。

在这里我卡了很久，搜了很多文章，都没有发现问题出在哪了，简直一度就要放弃了，直到我想要不要换真机试一下……简直峰回路转！全都成功了，顺利打印出地址：

![image-20200410151802418.png](https://image.3001.net/images/20200410/1586507655_5e902f87cffe3.png!small)

如果在模拟器环境里找不到so，搜不到函数，一定要赶快换真机试一下，一定要啊！血的教训！！！

### 脚本编写 & Hook

接下来就可以编写JS代码来进行Hook了，代码内容也很简单，就是修改这个函数的返回值，让它永远等于1即可：

    
    
    Java.perform(function(){  
        var nativePointer = Module.findExportByName("libIPCAppContextJNI.so", "X509_verify_cert");  
        console.log("-------------Start-------------");  
        Interceptor.attach(nativePointer, {  
            onEnter: function(args){  
                // 此处是修改入参要做的逻辑，在这里不需要修改，留空即可  
            },  
            onLeave: function(retval){  
                console.log("----------leaving-------------")  
                // 打印原始的返回值  
                console.log(retval);  
                // replace修改返回值  
                retval.replace(0x1)  
                // 再次打印出来验证一下修改是否成功  
                console.log(retval);  
            }  
        });  
    });

把这个文件保存，我命名为`hook.js`。开启Frida，在忘记密码那里点几下：

    
    
    (frida) pentest@DESKTOP-2AE07FJ:~/frida$ frida -U com.tplink.ipc -l hook.js  
         ____  
        / _  |   Frida 12.8.17 - A world-class dynamic instrumentation toolkit  
       | (_| |  
        > _  |   Commands:  
       /_/ |_|       help      -> Displays the help system  
       . . . .       object?   -> Display information about 'object'  
       . . . .       exit/quit -> Exit  
       . . . .  
       . . . .   More info at https://www.frida.re/docs/home/  
    Attaching...  
    -------------Start-------------  
    [MI 5s::com.tplink.ipc]-> ----------leaving-------------  
    0x1  
    0x1

Nice！成功Hook到并打印了返回值。

## 配置代理

到这一步，已经接近成功了，但是在系统里设置代理之后它并不会走，判断应该是做了代理上的限制，导致APP的流量不跟随代理。

那这一步的目标，就是让APP的流量顺利走到PC的Burpsuite上，来帮助我们进行分析。

第一种思路自然是找出限制代理的部分，一并Hook掉，但是我实在是不想再去找了，于是果断放弃；

第二种思路是通过无线网卡共享一个热点，再配置转发达到抓包的目的。这种方法在Windows系统下配置很麻烦，放弃；

第三种思路是PC端配置反向代理，手机端通过修改`hosts`文件强行转流量，因为之前的测试中配置过（详细的原理和配置可参见[《泄露的网站证书和私钥？来做些有趣的事吧！》](https://www.freebuf.com/column/231634.html)），且配置也简单（就是操作步骤有点复杂，好在环境都在），就果断用了。

反向代理是要配置证书的，但是因为Hook掉了校验，所以配置什么证书也无所谓了~

### 配置Hosts

配置hosts文件需要知道域名，在分析校验的部分看到了对于`*.tplinkcloud.com.cn`域名的校验。因此再次用Strings暴搜：

![image-20200410160228733.png](https://image.3001.net/images/20200410/1586507740_5e902fdce6b29.png!small)

因为考虑到可能不同的功能会访问不同的域名，为了方便起见，一次性把这些域名都添加到`hosts`文件里。

在修改`hosts`文件的时候，需要注意编写的格式。可以先通过`adb pull
/etc/hosts`将原始的hosts文件下载到PC，再在这个基础上修改。在“回车”符号上一定要注意，Android只识别`\n`而无法识别`\r\n`，因此在编辑的时候一定要注意回车符。

我使用的是`Notepad++`来进行编辑，注意右下角：

![image-20200410160643053.png](https://image.3001.net/images/20200410/1586507745_5e902fe13ee7d.png!small)

如果不是LF的话，可以双击这个位置选择“转换为Unix格式”即可。

编辑完后再`adb push`回原位并重启即可生效。

### 开始抓包！

终于在经过无数失败之后，可以开始抓包了。

如果以上步骤都配置正确的话，此时打开APP，在PC上输入命令`frida -U com.tplink.ipc -l
hook.js`后，点击相应的按钮，在命令行里会出现一串这样的输出：

![image-20200410161021863.png](https://image.3001.net/images/20200410/1586507749_5e902fe552d28.png!small)

每一个输出都代表一个请求的证书校验被绕过了。

打开Burpsuite，终于能看到熟悉的请求了：

![image-20200410161204206.png](https://image.3001.net/images/20200410/1586507754_5e902fea008db.png!small)

接下来就可以尽情的发挥脑洞开始测试了！

## 总结

整个思路其实非常简单，顺利转到包还是因为这个APP没有进行过加固，so里的函数名都很全，所以在分析这一步中并没有太大难度。总体思路总结如下：

  1. 通过反编译等方式确定证书绑定的核心函数的位置；

  2. 使用Frida对该核心函数进行Hook；

  3. 如果遇到无法代理的情况，嫌麻烦可以用反向代理的方式抓包。


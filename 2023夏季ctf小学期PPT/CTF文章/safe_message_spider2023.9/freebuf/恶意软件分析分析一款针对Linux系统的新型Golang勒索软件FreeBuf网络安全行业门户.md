![](https://image.3001.net/images/20191010/1570690163_5d9ed473d23a2.jpg!small)

**在过去的两个月，我们一直在对一款采用Golang开发的恶意软件进行逆向分析。Golang，即Go语言，它是一种静态类型的编译语言，由Google设计和维护，而且在恶意软件开发社区中，这种语言开始变得越来越流行了。在这篇文章中，我们将对一款新发现的针对Linux系统的Golang勒索软件进行分析。**

## 0x01 Go代码概览

我们要分析的样本是一个从恶意软件中单独剥离出来的ELF可执行文件，剥离出来的可执行文件会增加逆向分析的难度，因为我们还需要做很多额外的工作来还原二进制文件中的符号。不过还好有redress工具可以帮助到我们，redress软件是一款专门用来分析Go代码的工具，它可以从代码中提取出数据，然后利用这些数据来重构符号并执行分析。

下面是我们使用该工具和参数“-src”分析后得到的输出结果：

![](https://image.3001.net/images/20191010/1570690173_5d9ed47d7edbd.png!small)

从上图中我们可以看到，恶意软件的源代码包含了三个Go文件，里面都是代码所实现的功能函数以及对应的代码行数。通过对比某些函数名称，我们可以知道这个恶意软件大概率是一个勒索软件。但是，源代码的行数大概只有300行，所以这个勒索软件应该不是很复杂，而且很有可能还处于初始开发阶段。

接下来，我们在调试器中进行动态调试。这里我使用了Radare2作为调试器，Radare2可以分析Go源码，并通过分析命令来恢复代码中的符号，这也是我选择Radare2作为调试器而不选择GDB的原因。

## 0x02 Go源码动态分析

Radare2中的命令“aaa”可以执行一次自动化分析任务，从下图中我们可以看到，Radare2恢复并识别出了函数名称以及符号名称：

![](https://image.3001.net/images/20191010/1570690178_5d9ed482201e9.png!small)

我们可以看到，函数init()会在main函数前执行，int()会调用函数check()。在check()中，恶意软件首先会通过向hxxps://ipapi.co/json/发送一个http请求来获取受感染设备的信息。接下来，它会过滤掉白俄罗斯(BY),
俄罗斯(RU)和乌克兰(UA)这三个国家来避免恶意软件在这三个国家的用户设备上运行。

![](https://image.3001.net/images/20191010/1570690181_5d9ed485c2dcc.png!small)

在main()函数中，首先会删除掉Go代码，然后调用函数randSeq()来生成一个大小为0x20字节的随机AES秘钥：

![](https://image.3001.net/images/20191010/1570690185_5d9ed48941496.png!small)

接下来，它会调用函数makesecret()，它主要用来利用代码中硬编码的RSA公钥来加密AES秘钥。在这个函数中，代码会调用函数EncryptPKCS1v15()并使用RSA加密算法来加密给定的AES秘钥。

![](https://image.3001.net/images/20191010/1570690189_5d9ed48d03fee.png!small)

下面就是RSA算法加密后的秘钥数据：

![](https://image.3001.net/images/20191010/1570690192_5d9ed4909b16e.png!small)

然后，它会调用函数EncodeToString()来对之前的加密数据进行Base64编码：

![](https://image.3001.net/images/20191010/1570690200_5d9ed498763b5.png!small)

接下来，它会为解密后的READEME文件分配一个缓冲区：

![](https://image.3001.net/images/20191010/1570690208_5d9ed4a0ad00a.png!small)

加密后的AES秘钥已经以Base64编码格式写入到了解密后的README文件中。

在勒索软件加密文件之前，它会使用“service stop [pname]”或“systemctl stop [pname]”命令来终止下列进程的运行：

![](https://image.3001.net/images/20191010/1570690213_5d9ed4a5d858f.png!small)

当它尝试终止apache2.service时，会弹出一个标题为“Authentication
Required”的对话框，此时需要用户输入系统密码来完成操作。

![](https://image.3001.net/images/20191010/1570690220_5d9ed4ac73bb1.png!small)

最后，恶意软件会调用函数Walk(root string, walkFn WalkFunc)来从根目录“/”处开始遍历文件，并对这些文件进行加密处理。

![](https://image.3001.net/images/20191010/1570690224_5d9ed4b0d39c8.png!small)

这款恶意软件使用了AES-256-CFB算法来加密目标文件，加密后的文件后缀会添加一个“.encrypted”字符串。README文件内容如下：

![](https://image.3001.net/images/20191010/1570690228_5d9ed4b48232e.png!small)

EncFile()函数主要负责对文件进行加密，它首先会获取待加密文件的大小，如果文件大小不超过0x986880(1,000,000)字节，它就会选择使用AES-256-CFB算法来对全部的文件数据进行加密。否则，它会读取目标文件的前0x986880(1,000,000)个字节的数据进行加密，然后将源文件中剩下的数据追加到加密文件数据的结尾处。

![](https://image.3001.net/images/20191010/1570690241_5d9ed4c14bda1.png!small)

![](https://image.3001.net/images/20191010/1570690244_5d9ed4c4eecbc.png!small)

  

## 0x03 总结

根据我们的分析，这款恶意软件其实并不复杂，而且很可能仍处于前期开发阶段。在将来，我们可能会看到越来越多采用Go语言开发的恶意软件，我们也会持续监控和过滤采用Go语言开发的恶意软件。

### 入侵威胁标识符IoC

    
    
    SHA256: 50470f94e7d65***bf00d7416a9634d9e4141c5109a78f5769e4204906ab5f0b
    
    IoC: fullofdeep<at>protonmail.com

### 工具下载

> REDRESS：【[ _下载地址_](https://go-re.tk/redress/)】
>
> Radare2：【[ _下载地址_](https://rada.re/r/)】

 *** 参考来源：[ _fortinet_](https://www.fortinet.com/blog/threat-research/new-golang-ransomware-targeting-linux-systems.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+fortinet%2Fblog%2Fthreat-research+%28Fortinet+Threat+Research+Blog%29)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


在花了大量时间分析各种maldoc之后，我意识到它们有一个共同点。看看下面这张图表：  
![2018-11-07_01.png](https://image.3001.net/images/20181216/1544972894_5c166a5e4f47a.png!small)  
我意识到许多maldoc使用CMD来启动下一个阶段。当然，并不是所有的maldoc都遵循这个图表。有一些maldocs直接从VBA请求(或其变体)恶意软件，而CMD根本没有使用。所以我想，如果我监视CMD进程并从命令行提取数据会怎么样呢?这样，我就可以从VBA宏中获得没有被混淆的输出，而不必遍历代码并手动转储内容。又如果我监视CMD进程，挂起它，提取命令行数据，然后杀掉它，会怎么样呢?我不仅能够快速、轻松地获得VBA宏输出，而且还可以避免机器损坏。CMD观察者就是这样诞生的。我去了恶意软件流量分析站点，抓了几个maldocs，启动了[CMD监视器](a%20href=)，开始打开每个文档，同时允许宏运行。看起来它在工作……![2018-11-07_02.png](https://image.3001.net/images/20181216/1544972907_5c166a6b7a128.png!small)这是Emotet
maldoc。  
![2018-11-07_03.png](https://image.3001.net/images/20181216/1544972914_5c166a72b83ab.png!small)这是Hancitor  
![2018-11-07_04.png](https://image.3001.net/images/20181216/1544972922_5c166a7a496ab.png!small)这是Trickbot。  
![2018-11-07_05.png](https://image.3001.net/images/20181216/1544972930_5c166a822a981.png!small)我将写一篇关于如何去混淆DOSfuscated脚本的后续文章。如果您对CMD
Watcher感兴趣，可以从Tools页面下载它。

***参考来源[kahusecurity](http://www.kahusecurity.com/posts/cmd_watcher_and_maldocs.html)，由周大涛编译，转载请注明来自FreeBuf.COM**


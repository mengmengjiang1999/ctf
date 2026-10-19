还是以大神apk为例，通过前面[分析app解密lua脚本](http://www.freebuf.com/column/173230.html)，我们能够解密大神apk的lua脚本，现在我们来解密其资源（配置文件和图片等）。我们以比较重要的配置文件为例，未解密之前：  
![图片.png](https://image.3001.net/images/20180529/15275620257341.png!small)
文件头部也有签名值：fuckyou!。看到这，我们首先就想到是不是也是用xxtea加密的，我们用上面的方法，先xxtea解密，再解压，发现依旧是乱码，在操作的过程中就出现了错误，显然，要否定我们刚才的猜想。我们继续按部就班的解密配置文件。

稍微思考一下，文件头部是：fuckyou！如果想对文件进行解密，那么不可避免的需要处理字符串：fuckyou！，所以，我们应该能在idaPro中搜到fuckyou字符串，然后以fuckyou字符串所在代码段处的函数分析调试解密即可。验证一下我们的猜想，打开idaPro，打开string视图，搜索fuckyou：

![图片.png](https://image.3001.net/images/20180529/15275622601513.png!small)
居然啥也没有！猜测应该是做过优化，在某个地方把字符串优化掉了。

线索断了，但是好奇心还是让我们继续，这时候，我们可以浏览cocos2d框架源码，结合网上一些资料，发现cocos2d对文件的处理封装到了CCFileUtils类中：

![图片.png](https://image.3001.net/images/20180529/15275623747152.png!small)
函数有些多，不一一贴了，从网上也找到了前辈的经验：

![图片.png](https://image.3001.net/images/20180529/15275623992893.png!small)
好了，我们现在回到idaPro，在export窗口，搜索getData：

![图片.png](https://image.3001.net/images/20180529/15275624502127.png!small)
进这两个函数，反编译看下，长得不大像，略过，但是先记下，在动态调式时，我们可以在此下个断。

我们再来看getFileData：

![图片.png](https://image.3001.net/images/20180529/1527562475540.png!small)
由于app运行在Android平台上，我们看Android平台的CCFileUtilsAndroid::getFileData：

![图片.png](https://image.3001.net/images/20180529/15275624922439.png!small)
我们接着跟踪：

![图片.png](https://image.3001.net/images/20180529/15275625057262.png!small)
代码很长，就不全贴了，贴此函数关键的部分：

![图片.png](https://image.3001.net/images/20180529/15275625192570.png!small)
看到上图，感觉就是它了，呵呵！但是我们还是需要继续分析验证。函数处理文件头部sign时，并不是直接与字符比较而是与其ASCII值一个一个比较，所以我们在字符串窗口是搜不到fuckyou！的。接着往下看，当函数判断完是符合加密格式的文本时，会移除前8个字节（fuckyou！），然后与异或表中的值进行异或操作，每256个字节循环操作。

我们可以看下byte_A1C55F:

![图片.png](https://image.3001.net/images/20180529/15275626975298.png!small)
至此，我们已基本可以确定文件解密函数及过程了，我们可以动态调试，再确认一下，当app调用完这个函数后，内存中应该是明文内容了。当我们调试时，分别在getData、CCFileUtilsAndroid:doGetFileData函数开始和结束时下断，GetData函数下断：

![图片.png](https://image.3001.net/images/20180529/15275627028489.png!small)
doGetFileData函数下断：

![图片.png](https://image.3001.net/images/20180529/15275627183891.png!small)
虽然两个函数都下断了，但是只在doGetFileData断点出暂停，说明解密过程中是走的doGetFileData函数，符合我们的预期，看下寄存器及内存：

![图片.png](https://image.3001.net/images/20180529/15275627415761.png!small)

![图片.png](https://image.3001.net/images/20180529/15275627855430.png!small)
我们看到内容在doGetFileData之前是密文，函数返回之前已经解密成明文了，这说明我们之前的分析是对的。

好了，现在，我们可以将异或表byte_A1C55F拷贝出来，然后模仿app的解密过程（可从GitHub上找个xor解码脚本，稍作修改即可）写一个小工具，对大神.apk的所有资源进行解密了：

![图片.png](https://image.3001.net/images/20180529/15275628319652.png!small)  


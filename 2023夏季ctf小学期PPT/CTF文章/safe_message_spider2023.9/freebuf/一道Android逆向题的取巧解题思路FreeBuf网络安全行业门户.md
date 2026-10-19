## 前言

最近朋友发来一道Android逆向题，挺有意思，花时间研究了一下，在算法逆不出来的情况下（我太菜），用frida取巧解出了题目，记录下学习的过程。

## 抛出问题

安装打开题目发现是要求输入字符串。
![1](https://image.3001.net/images/20221021/1666330881_63523101b1f5d667e959b.png!small)随便输入提示错误。
![2](https://image.3001.net/images/20221021/1666330909_6352311d6574b2c752043.png!small)

## Java层静态分析

拖进jadx，先分析下java层。里面类有点多，估计是垃圾代码，直接看Androidmanifest文件找到启动的Activity去分析。
![3](https://image.3001.net/images/20221021/1666330926_6352312e7bae14d7eaded.png!small)找到对应的类，一看上面就是一个byte数组，一个loadLibrary，一个native函数，so逆向跑不了。
下面看到对应的按钮点击事件。
![4](https://image.3001.net/images/20221021/1666331172_635232247eb64a432e5b2.png!small)继续跟进去看，找到了核心的逻辑，是通过encry函数处理输入字符串，返回一个byte数组，然后和前面的byte数组比较是否相等，那前面的byte数组应该就是加密后的flag，我们要做的就是逆出来。
![6](https://image.3001.net/images/20221021/1666331206_63523246edee37fc3a09a.png!small)

## Native层静态分析

encry是写在native层，对apk解包，取出对应的so（libencry.so）拖进ida。 可以看到是静态注册的，直接能在导出函数里找到。
![7](https://image.3001.net/images/20221021/1666331253_6352327536ccc60a063d1.png!small)转成C伪码，看一下，我还是太菜，不会。
![8](https://image.3001.net/images/20221021/1666331288_63523298f34cf17005fae.png!small)动态调了下，也没调明白，我太菜了。

## Frida动态hook

关掉ida，直接上frida，先来hook一下这个函数，看看输入输出。 可以hook到，输入的参数以及输出的byte数组
![9](https://image.3001.net/images/20221021/1666331308_635232ac4ff910802b85d.png!small)这里开始测试（猜），flag格式一般就是flag{xxxxxx},我输入“flag{”进行测试，hook结果如下：
![10](https://image.3001.net/images/20221021/1666331323_635232bb12278354cc67b.png!small)对比Java层中的byte数组，发现前几位已经能对上了，但是最后一位对不上，应该是因为so层中的加密算法后一位会影响前一位。
到这里就已经可以get到一个比较取巧的思路了，写个rpc脚本调用一位一位爆破flag。

## Frida rpc调用

直接hook encry函数，主动调用。 js部分如下：
![11](https://image.3001.net/images/20221021/1666331336_635232c82fc929dfc882b.png!small)python调用，爆破部分如下：
![12](https://image.3001.net/images/20221021/1666331346_635232d2f3b7007fc5987.png!small)一位一位遍历所有可打印字符跑起来。
成功获取（爆出）到flag。
![13](https://image.3001.net/images/20221021/1666331363_635232e3aff28eeda0015.png!small)

## 总结

常规做法做不出来，只能取巧，题目设置也刚好，最终还是以结果为导向，能解题的方法总是好方法。这里只是举例了用frida，实际上也可以使用unidbg去主动调用so进行爆破，原理是差不多的。


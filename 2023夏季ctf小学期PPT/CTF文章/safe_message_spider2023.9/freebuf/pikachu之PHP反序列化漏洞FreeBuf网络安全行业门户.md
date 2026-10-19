## **PHP反序列化漏洞**

###  **简介：**

php程序为了保存和转储对象，提供了序列化的方法，php序列化是为了在程序运行的过程中对对象进行转储而产生的。序列化可以将对象转换成字符串，但仅保留对象里的成员变量，不保留函数方法。

###  **PHP serialize() 函数**

serialize() 函数用于序列化对象或数组，并返回一个字符串。

serialize() 函数序列化对象后，可以很方便的将它传递给其他需要它的地方，且其类型和结构不会改变。如果想要将已序列化的字符串变回 PHP
的值，可使用 unserialize()。

###  **PHP unserialize() 函数**

unserialize() 函数用于将通过 serialize() 函数序列化后的对象或数组进行反序列化，并返回原始的对象结构。

###  **序列化serialize()**

通俗点讲就是把一个对象变成可以传输的字符串

![1615450019_6049cfa3a485d3cceb7eb.png!small](https://image.3001.net/images/20210311/1615450019_6049cfa3a485d3cceb7eb.png!small)

###  **反序列化unserialize()**

就是把被序列化的字符串还原为对象,然后在接下来的代码中继续使用。

![1615450028_6049cfac33d738e57595a.png!small](https://image.3001.net/images/20210311/1615450028_6049cfac33d738e57595a.png!small)

###  **产生原因：**

序列化和反序列化本身没有问题,但是如果反序列化的内容是用户可以控制的,且后台不正当的使用了PHP中的魔法函数,就会导致安全问题

![1615450038_6049cfb68c6793eed7aa5.png!small](https://image.3001.net/images/20210311/1615450038_6049cfb68c6793eed7aa5.png!small)

输入payload：O:1:"S":1:{s:4:"test";s:29:"<script>alert('xss')</script>";}
会进行XSS弹窗

**![1615450045_6049cfbd750e734609e4b.png!small](https://image.3001.net/images/20210311/1615450045_6049cfbd750e734609e4b.png!small)**

 **PHP反序列化一般是在代码审计的时候发现，其他的情况并不容易被发现。**


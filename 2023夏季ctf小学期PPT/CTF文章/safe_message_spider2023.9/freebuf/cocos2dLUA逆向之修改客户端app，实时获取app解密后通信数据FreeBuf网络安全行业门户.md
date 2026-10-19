本文中，将以宝博.apk为例。基于前面[解密lua脚本](http://www.freebuf.com/column/173230.html)与[解密lua资源](http://www.freebuf.com/column/173234.html)，我们为实现修改客户端app，实时获取app解密后通信数据，应分析修改app端的lua脚本，然后按原app加密方式打包修改后的lua脚本，覆盖原始安装文件，从而达到修改app的目的。

参照前面分析，获取宝博.apk的xxtea解密key，同时可以分析出其对lua脚本的加密方式，是将lua脚本以字节码的形式，再经xxtea加密。所以我们解密lua脚本时，经过xxtea解密之后，得到的是lua字节码而不是源码，lua字节码类似java、
.net的中间文件，是可以被翻译成源码的，可以从网上下载一个lua字节码还原工具，将lua字节码还原成lua源码，最后得到lua源码目录如下：

![图片.png](https://image.3001.net/images/20180529/15275640095509.png!small)
我们分析源码几处关键的地方:

![图片.png](https://image.3001.net/images/20180529/1527564031701.png!small)![图片.png](https://image.3001.net/images/20180529/15275640502965.png!small)
我们现在从修改app
lua脚本的角度，想解密app与服务器的通信数据并不难，因为并不需要再分析底层so库中的加解密函数了。我们是处于上层，有源码，所以如果想记录所有app
通信的明文数据，可以在消息接口处，将解密后的消息全部写入文件即可。但是我们想实时显示解密后的通信消息，并在适当的地方能够伪造消息发往服务器。

为了达到这个目的，我们可以在电脑端建立tcp服务开放端口，用adb将端口映射进手机，app用lua socket
连接端口，然后这样就在电脑端与手机（模拟器）端app建立了通信链路，app端接收的服务器消息解密后可以通过socket发送至电脑，电脑也可以将想要发送的消息，发送至app，然后由app加密后发送至服务器。架构如下：

![图片.png](https://image.3001.net/images/20180529/15275643482459.png!small)
具体实现不在多述。

这里对如何将修改了的lua源码回编至app提供两个方案。

一是，利用quick-cocos2d提供的打包脚本文件。

![图片.png](https://image.3001.net/images/20180529/15275644113539.png!small)
帮助命令如下：

![图片.png](https://image.3001.net/images/20180529/15275644279944.png!small)
可以将修改好的lua源码目录打包成一个加密的zip文件：

compile_scripts -i fishgame2d -o fishgame2d.zip -m zip -exxtea_chunk -ek “app
xxtea 密码” -es “app xxtea 头部sign”

命令成功执行应该出现fishgame2d.zip文件，将打包好的文件，覆盖掉原安装包内的文件即可。

二是，按照app的lua脚本的目录结构，直接将改好的明文lua脚本覆盖掉原先的lua密文文件，cocos2d引擎会自动判断文件是否加密，对于未加密的cocos2d引擎也会正确处理。

最后看下手机端app实时传回解密后的消息到电脑端的结果：

![图片.png](https://image.3001.net/images/20180529/1527564509989.png!small)

另外，还有一种方案就是直接破解app与服务器通信的加密算法，在电脑端模拟app的socket通信，这样更直接一些。根据自己的目的选择适合自己的技术方案。（结束）

  
  


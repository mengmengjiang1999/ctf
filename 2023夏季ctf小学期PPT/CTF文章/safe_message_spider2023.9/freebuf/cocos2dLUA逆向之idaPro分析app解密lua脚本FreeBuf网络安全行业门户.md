通过前面[](http://www.freebuf.com/column/173217.html)[idaPro调试](http://www.freebuf.com/column/173217.html)或[hook](http://www.freebuf.com/column/173221.html)，我们可以获取到xxtea解密key，对于sign我们可以直接打开原文件：

![图片.png](https://image.3001.net/images/20180529/15275606277075.png!small)
可以看到sign值：byds。所以，我们可以同过xxtea解密工具（可从GitHub上下源码自己编译）试着解密：

![22.png](https://image.3001.net/images/20180529/15275612594290.png!small)
以index.luac为例，我们看index.luac解密前后变化：

![图片.png](https://image.3001.net/images/20180529/15275607842519.png!small)

我们看到经过xxtea解密后的lua脚本仍然不是明文！我们之前根据cocos2d框架源码及大神apk反编结果确定就是用的xxtea加密，而且app的lua脚本也有签名值，这也印证了就是xxtea加密方式，但是我们解密出来的结果仍然不是明文，这说明我们解密可能不完全，到底是不是还得再回到idapro一探究竟。

用idapro打开libgame.so,在export窗口中搜索byds，找到byds_d函数，双击进去：

![图片.png](https://image.3001.net/images/20180529/15275608786929.png!small)
直接F5会显示反编代码：

![图片.png](https://image.3001.net/images/20180529/15275609159661.png!small)
这没有什么特别的，和我们框架源码中的代码是等效的。如果是解密未完成的话，应该会再调用此函数的上一级继续解密过程，我们jump xrefs跟踪一下此函数调用：

![图片.png](https://image.3001.net/images/20180529/15275609302969.png!small)
出来两个，其中一个是got表，肯定不是，我们双击第一个：

![图片.png](https://image.3001.net/images/20180529/15275609401708.png!small)
只是一个包装函数，我们继续跟踪：

![图片.png](https://image.3001.net/images/20180529/15275609483449.png!small)
双击进去：

![图片.png](https://image.3001.net/images/20180529/152756095716.png!small)
我们看到这个函数名称和源码中调用xxtea_decrypt是一样的，我们一开始也将这个函数列入突破口了。现在可以很清晰的看到脚本经过byds_d解密之后，又进行了一次uncompress解压，到现在应该基本清晰了，lua脚本应该是经过压缩又进行加密，所以要想还原，应该是先xxtea解密，再解压缩。我们可以从GitHub上找个解压zlib的脚本，对解密后的文本再一次解压：

![图片.png](https://image.3001.net/images/20180529/15275609976132.png!small)
然后再看index.lua:

![图片.png](https://image.3001.net/images/20180529/15275610062578.png!small)
可以看到现在已经变成明文了。


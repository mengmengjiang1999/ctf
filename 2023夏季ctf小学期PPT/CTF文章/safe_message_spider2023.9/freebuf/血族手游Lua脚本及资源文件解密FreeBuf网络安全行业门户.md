**之前一直和朋友在玩手游血族，有一天朋友问我能不能把里面某个角色的立绘拿下来，当时没多想就答应了，以为只要解压找到图片就行了。但是万万没想到，图片竟然打不开（被加密了）。**

## 快速分析

下载最新的血族apk并解压之后看到assets\lua可以猜测这个游戏是由cocos2d-lua开发的。打开其中的一个lua脚本看到里面都是乱码而且开头也没有特征值，应该不是使用xxtea加密的。

![1.png](https://image.3001.net/images/20180302/1519977227628.png!small)  

story Lua.png

打开png图片提示无法读取该文件。

![2.png](https://image.3001.net/images/20180302/15199772388753.png!small)  

png报错.png

打开 **lib\armeabi** 文件夹，libgame.so是最大的也是等一下分析的重点文件。

![3.png](https://image.3001.net/images/20180302/15199772456727.png!small)  

libgame.png

快速分析小结

> 1.血族使用cocos2d-lua开发；
>
> 2.lua脚本和一些重要资源都已经被加密，但不是用官方的xxtea；
>
> 3.加解密是由libgame.so进行。

## 静态分析libgame.so

用IDA打开libgame.so，文件较大打开时间比较长。打开字符串窗口可以快速获得一些重要信息。比如LuaJIT2.0.1、Lua5.1等等。

lua脚本由cocos2dx_lua_loader加载，最后由lua_loadbuffer函数加载到内存中。动态分析一般会在这两个地方下断点，然后将lua脚本dump下来。

## cocos2dx_lua_loader分析

找到cocos2dx_lua_loader之后f5查看反汇编代码。根据之后的动态调试分析可以知道，lua脚本是在第一个红色方框处进行解密操作。

![4.png](https://image.3001.net/images/20180302/1519977253801.png!small)  

Lua_load.png

 **lua_load** 调用了 **CCFileUtilsAndroid::getFileData** ,接着调用
**CCFileUtilsAndroid::doGetFileData** ，然后调用 **decryptFile** 。其实所有的资源都是在
**decryptFile** 中进行解密操作。根据文件类型主要分为三大类：png、jpg、其他加密文件（Lua,csv,xml）。

![5.png](https://image.3001.net/images/20180302/15199772637203.png!small)  

decryptFile.png

##  **cocos2d::decryptTxt** **分析**

在接下去分析会发现这三个类型的解密过程都是大同小异，先是判断该文件是否已经加密，如果加密了就调用了 **cocos2d::decryptData**
进行真正的解密，只是传入的参数有所差异。下面用 **cocos2d::decryptTxt** 作为例子。

![6.png](https://image.3001.net/images/20180302/15199772728796.png!small)  

decryptTxt特征.png

1.判断文件最后第4个字节到最后第2个字节是否为 **0x53 0x44 0x47**  
2.调用 **cocos2d::decryptData**
进行解密操作，传入的参数只用到了前三个。第一个：开始解密的位置。第二个：需要解密的大小。第三个：用于后续解密的“密钥”。

![7.png](https://image.3001.net/images/20180302/15199772837906.png!small)  

lua特征.png

##  **cocos2d::decryptData** **分析**

解密的步骤如下：

> 1.将需要解密的第一个字节和“密钥”异或；
>
> 2.将需要解密的最后一个字节和“密钥”异或；
>
> 3.将第一个字节和最后一个字节交换；
>
> 4."密钥" =（"密钥"+1）%0xff。

解密的步骤还是比较简单的稍微花点时间就能看懂。

![8.png](https://image.3001.net/images/20180302/15199773131748.png!small)

decryptData.png

## 静态分析小结

函数调用的顺序是:

> 1.cocos2dx_lua_loaderlua脚本加载函数；
>
> 2.cocos2d::CCFileUtilsAndroid::GetFileData；
>
> 3.cocos2d::CCFileUtilsAndroid::doGetFileData；
>
> 4.cocos2d::decryptFile选择对应的解密函数；
>
> 5.cocos2d::decryptTxt判断是否需要解密；
>
> 6.cocos2d::decryptData解密完成。

## 动态分析

在lua_load和loadbuffer下断点。

![9.png](https://image.3001.net/images/20180302/15199773267413.png!small)  

lua_load断点.png

![10.png](https://image.3001.net/images/20180302/1519977337183.png!small)

loadbuffer断点.png

点击游戏里的一些按钮触发断点，当运行到loadbuffer断点的时候，lua脚本源码已经出现在内存中了。

![11.png](https://image.3001.net/images/20180302/15199773501928.png!small)

loadbuffer动态调试.png

> R1:脚本的起始位置；  
> R2:脚本的长度。

可以使用IDC脚本将lua代码保存到本地。

![12.png](https://image.3001.net/images/20180302/15199773705336.png!small)  

idc脚本.png

效果源码如下图。

![13.png](https://image.3001.net/images/20180302/15199773856860.png!small)

storyLua源码.png

## 动态调试总结

在loadbuffer关键函数下断点可直接获得解密后的代码。

使用IDC脚本将代码保存下来：

> 优点：省略分析加解密算法的步骤，配合hook框架可以将运行过的代码都获取到；
>
> 缺点：没运行到的代码依然得不到。

最后放几张jpg,png解密后的图片和解密脚本的效果。

![14.png](https://image.3001.net/images/20180302/15199774011864.png!small)

png解密.png

![15.png](https://image.3001.net/images/20180302/15199774117539.png!small)  

解密脚本效果.png

 **详细代码已经上传github：**[脚本代码链接](https://github.com/bigkan/decrypt-xuezu)

##  **参考文章链接**

> [浅析android手游lua脚本的加密与解密](https://bbs.pediy.com/thread-216969.htm)
>
> [Lua游戏逆向及破解方法介绍](http://gad.qq.com/article/detail/21645)

 ***本文作者：网络安全通，转载请注明来自FreeBuf.COM**


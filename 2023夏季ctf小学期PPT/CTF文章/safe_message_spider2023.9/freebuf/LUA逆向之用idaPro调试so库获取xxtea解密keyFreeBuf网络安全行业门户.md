以一个棋牌类app **大神.apk** 为例，，首先我们需要获取apk里面的脚本资源，可以直接用360好压解压缩apk安装包，会得到如下目录：

![图片.png](https://image.3001.net/images/20180528/1527522670845.png!small)  
其中，lib目录含有我们需要调试的so库文件，文件名一般是libcocos2dlua.so或带有cocos字样，当然也有例外，我们需要破解的这个app就有些不一样，名字为libgame.so，不论名字如何变化，拖到idaPro中便知是否用的cocos2dlua框架了。assets目录中含有lua加密脚本及资源。

动态调试app，需要准备app运行环境，真机或模拟器，不建议用模拟器，坑太多，我试用过几个模拟器（雷电、天天、mumu）进行调试环境的搭建几乎都是失败的，但是安卓官方模拟器是可以的（有几次是成功的，也有失败的），需要安装Android-sdk、Android-ndk，但是速度非常慢，所以建议直接上真机，真机需要root权限。

接下来，需要下载adb Android调试工具
并将其加入path变量，手机通过usb连接后，可通过adb命令操作手机，打开cmd，输入adb即可看到帮助命令：

![图片.png](https://image.3001.net/images/20180528/15275227055315.png!small)  

找到电脑idaPro的安装路径中android_server文件，用adb将其拷贝至手机并赋权：

![图片.png](https://image.3001.net/images/20180528/15275227249285.png!small)  

如果程序运行后附加进程调式，需要手机端运行idaPro的 android_server，并
用adb将端口映射至电脑，如果电脑与手机在同一局域网内，则可不用映射。如下图：

![图片.png](https://image.3001.net/images/20180528/15275227496156.png!small)  
手机端运行大神app ：

![图片.png](https://image.3001.net/images/20180528/15275227665445.png!small)  

idaPro远程调试附加进程：

![图片.png](https://image.3001.net/images/20180528/15275227761098.png!small)  

如果是局域网内调试，没有用到adb forward映射，则将ip地址换成你手机ip地址：

![图片.png](https://image.3001.net/images/20180528/15275227879131.png!small)双击选中线程进行调试：

![图片.png](https://image.3001.net/images/20180528/15275228028866.png!small)然后，在模块视图中选择要调试下断的模块，这里是libgame.so,下面的程序内存视图可以选择与上面的反汇编视图同步：

![图片.png](https://image.3001.net/images/20180528/15275228156943.png!small)

  
![图片.png](https://image.3001.net/images/20180528/15275228261163.png!small)
有的app破解时，需要在程序入口处就调试，则要多做一些操作，网上大多是先需要以下几个步骤：首先确保apk内的mainframexml文件的application节点的android:debuggable属性值为1，这就需要将apk先反编，修改值之后再编译进去，并找到app的包名及入口函数，以上这些可以用有现成的工具，当也可以用命令（eg：查看aapt
dump xmltree dashen.apk AndroidManifest.xml >manifest.xml 回编译：java -jar
apktool.jar b -d out -o dashen.apk）；之后需要以调试模式开启app（ **adb shell am start -D
-ncom.yaotong.crackme/.MainActivity** **），手机会出现调试界面：**

![图片.png](https://image.3001.net/images/20180528/15275228617323.png!small)  

此时，程序停在程序入口，之后用idapro附加调试，然后用jdb -connect
com.sun.jdi.SocketAttach:hostname=127.0.0.1,port=8700通知程序继续运行，idapro这边就可以继续调试了。

**这里提供另一种方法，将Android
根目录下的default.prop的ro.debuggable设置为1（getprop、setprop），强制所有app都可以进行调试，这样就不用修改app并重新打包了。这里要说明一点，jdbconnect失败时，如图所示：**

![图片.png](https://image.3001.net/images/20180528/15275228841441.png!small)
**有说是** **apk** **android:debuggable** **属性的原因，我这边测试，其真正的原因应该是没有开启**
**DDMS(DalvikDebug Monitor Service)** **虚拟机调试监控服务，端口号** **8700**
**是其默认服务端口号，服务不开当然连不上** **VM** **，所以需要开启** **DDMS** **，** **Android sdk
tools** **目录下有开启** **DDMS** **的脚本，我们打开** **DDMS** **：**

![图片.png](https://image.3001.net/images/20180528/1527522900588.png!small)
**我们要调试的进程端口号有** **8626/8700,** **所以我们用** **jdb** **连接这两个任一端口都是可以的。**

![图片.png](https://image.3001.net/images/20180528/15275229213410.png!small)
**调试过程中，还需要注意一点，要关闭** **SELinux** **，** **setenforce 0**

idaPro调试就说到这里，接下来我们利用idaPro破解大神app，大神app是基于cocos2dlua，cocos2dlua用的xxtea加密，我们可以下载源码，用vs打开：

![图片.png](https://image.3001.net/images/20180528/1527522941351.png!small)
我们在vs中，Shift+F12追踪xxtea_decrypt的调用:

![图片.png](https://image.3001.net/images/20180528/15275229551828.png!small)
可以看到一个是在luaLoadChunksFromZIP中：

![图片.png](https://image.3001.net/images/20180528/15275229673049.png!small)
一个是在luaLoadBuffer中：

![图片.png](https://image.3001.net/images/20180528/15275229838329.png!small)
从函数名，我们应该可以猜到一个是在解压zip文件是进行解密，一个是在解压字符串buffer是解密，这个我们不讨论，我们只须在这两个函数下断，在函数调用xxtea_decrypt时即可破解xxtea解密用的key，现在我们已经知道破解大神app的关键了，就是xxtea_decrypt及直接相关的luaLoadBuffer、luaLoadChunksFromZIP函数。

接下来，我们来看大神apk，解压大神apk，将lib目录下的libgame.so拖拽至idaPro打开:

![图片.png](https://image.3001.net/images/20180528/1527523002105.png!small)
一般cocos2dluaapp不对xxtea加密强化的话，有一种取巧获取xxtea解密key的方法，按照网上说的，直接打开加密的lua文件，得到sign，然后打开idaPro的string视图，搜索sign，双击进去，在sign附近会有xxtea的key，可以试出来，网上有详细的步骤，在此我们就不再多述。我们破解的大神app是经过安全优化的，上面的方法不适用。

继续，刚才我们看cocos2d源码了解到破解大神app的突破口函数xxtea_decrypt及直接相关的luaLoadBuffer、luaLoadChunksFromZIP，我们在idaPro中查看函数导出表，确认函数名是否与源码中一致。导出表如下：

![图片.png](https://image.3001.net/images/20180528/15275230375315.png!small)
没有与xxtea相关的导出函数。我们再搜LoadChunk：

![图片.png](https://image.3001.net/images/20180528/15275230883961.png!small)
发现也没有，进一步确认是经过安全优化的，我们在来看loadbuf：

![图片.png](https://image.3001.net/images/20180528/15275231012003.png!small)
我们看到有三个，很明显第一个与我们在源码中看到的那个长得像：

![图片.png](https://image.3001.net/images/20180528/15275231165246.png!small)  
![图片.png](https://image.3001.net/images/20180528/15275231275534.png!small)
我们在前面了解到，luaLoadBuffer这个函数会调用xxtea_decrypt来解密脚本，虽然这个app经过安全优化，已经看不到xxtea_decrypt函数名了，但是必然会有与xxtea_decrypt等效的解密函数，我们F5反编译，进去详细看看：

![图片.png](https://image.3001.net/images/20180528/15275231403129.png!small)
很明显_byds_d_就是我们要找的与xxtea_decrypt等效的加密函数，我们在进_byds_d_函数看，

![图片.png](https://image.3001.net/images/20180528/1527523155988.png!small)
再结合coco2dlua源码看一下xxtea_decrypt函数源码：

![图片.png](https://image.3001.net/images/20180528/15275231709690.png!small)
很显然，函数体效果是相同的，至此，我们已经确定下调试app时突破口：_byds_d_、luaLoadBuffer，在动态调试时，在这两个函数下断，不出意外的话，应该是能得到破解xxtea的key的。我们知道在cocos2dlua中，与app交互主要考lua，lua运行时加载，所以，手机端运行app后直接附加调试即可。

依照前面所讲，用idaPro对大神app进程（com.qipai.n1）附加调试，并在modules窗口搜索libgame模块：

![图片.png](https://image.3001.net/images/20180528/15275231949082.png!small)
双击进入，会显示此模块内的函数表，搜索luaLoadBuffer、_byds_d_:

![图片.png](https://image.3001.net/images/20180529/15275232179919.png!small)![图片.png](https://image.3001.net/images/20180529/15275232271154.png!small)

分别点进去下断，并设置内存窗口与程序窗口同步：

![图片.png](https://image.3001.net/images/20180529/15275232384830.png!small)
然后手机端操作程序，我们来看，_byds_d_的实参值：

![图片.png](https://image.3001.net/images/20180529/15275232524360.png!small)
我们知道函数的第三个参数即a3是我们要的key值，而c++调用规范中，参数是从右至左，寄存器R2就是存放我们key的地方，我们看到R2是一个内存地址，所以我们需要查看R2所代表的内存去看值。其实我们把鼠标放在R2上会自动出现其内存中存放的值，但是不全，所以我们通过内存窗口同步到R2，即可查看R2地址处的值了：

![图片.png](https://image.3001.net/images/20180529/15275233173518.png!small)

  
![图片.png](https://image.3001.net/images/20180529/15275233299191.png!small)
至此，我们已经将xxtea解密lua脚本的key获取到了，可以用xxtea解密算法解密lua脚本了。


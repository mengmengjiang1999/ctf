首先讲一下Androidhook，Android 基于Linux内核，提供ptrace系统函数，下图有一个简单说明：

![图片.png](https://image.3001.net/images/20180529/15275561412884.png!small)
Android inline
hook一般基于这个函数，使用ptrace函数attach一个目标进程，注入定制的so库进入目标进程的地址空间，然后用so里边的函数地址替换目标进程地址空间里原有的函数地址，目标进程运行到原有函数地址时，就会进入你的so库中的函数，而你的函数一般需要将当时目标进程现场保存起来（原函数地址、寄存器值），待自己的函数跑完后，再恢复现场，目标进程继续运行。

细节我们不在多述，资料也很多，这里我们直接基于一个GitHub上的开源项目Android
EagleEye（<https://github.com/MindMac/AndroidEagleEye>），来实现我们对大神app的hook。AndroidEagleEye的中文说明：

![图片.png](https://image.3001.net/images/20180529/15275561551738.png!small)
我们需要按照“hook更多native方法”的说明，增修hook_apis.c中的相关代码并设置系统属性：

1.声明目标方法的替代方法

参数类型、返回值类型需要和目标方法保持一致

![图片.png](https://image.3001.net/images/20180529/15275562643797.png!small) 2\.
初始化**HOOK_INFO**结构体

我们是Hook应用程序自身Native库中的方法，该变量应该以**custom_hook_info**开头。该结构体的第2个成员为目标库的名称（开头的lib是必需的）；第3个成员为目标方法名称；第4和最后一个成员为第1步中声明的方法名。第2、4个成员很明确，但是第3个成员目标方法名称，我们还需要idaPro来确定。我们上面讲到大神app解密lua脚本的关键函数在idaPro导出窗口中的名称是_byds_d_：

![图片.png](https://image.3001.net/images/20180529/1527556287659.png!small)
这里有一点需要特别注意，由于寻找函数时， **寻找的是app got表函数名称而不是导出函数窗口内的函数名称** 。

![图片.png](https://image.3001.net/images/20180529/15275562999621.png!small)

![图片.png](https://image.3001.net/images/20180529/152755630968.png!small)
所以函数名称一定不要弄错了，不然找不到函数，导致hook不成功。

现在，我们可以写**HOOK_INFO**结构体了：

![图片.png](https://image.3001.net/images/20180529/15275563217536.png!small) 3\.
实现步骤1中声明的方法

![图片.png](https://image.3001.net/images/20180529/15275563306459.png!small)
4.ndk重新编译，并安装至手机

打开cmd，直接进入EagleEye/jni目录，ndk-build编译：

![图片.png](https://image.3001.net/images/20180529/15275563461909.png!small)
这里不用再重新打包apt，从github上下载下来的目录结构是这样的：

![图片.png](https://image.3001.net/images/20180529/15275563564501.png!small)
里面就有EagleEye.apk,安装这个apk，之后再将刚才新编译的libeagleeyenative.so覆盖掉刚才apk中带的so库（/data/data/com.mindmac.eagleeye/lib中）即可:

![图片.png](https://image.3001.net/images/20180529/15275563696869.png!small)
5.配置文件**native_lib.config**

该配置文件用以设置目标库的名称，一个库名称一行，且库名称以**lib**开头，**.so**不需要:

![图片.png](https://image.3001.net/images/20180529/15275564021243.png!small)
并将该配置文件推送到目标应用程序的**data**目录下,/data/data/\<package name ofthe application you
want to hook\>,本例中是/data/data/com.qipai.n1，要确保该文件可读:

![图片.png](https://image.3001.net/images/20180529/15275564118477.png!small)
6.设置Android 系统属性rw.eagleeye.nt.uids

![图片.png](https://image.3001.net/images/20180529/15275564276511.png!small)
最后，运行测试，首先运行xposed并激活eagleeye模块：

![图片.png](https://image.3001.net/images/20180529/15275564477012.png!small)
运行EagleEye：

![图片.png](https://image.3001.net/images/20180529/15275564572919.png!small)
运行大神app：

![图片.png](https://image.3001.net/images/20180529/15275564665826.png!small)
结果（模拟器）：

![图片.png](https://image.3001.net/images/20180529/15275564758260.png!small)
结果（真机）：

![图片.png](https://image.3001.net/images/20180529/15275564828114.png!small)
这种hook方式，测试的模拟器（雷电）和真机都是可以的。在这里也多谢AndroidEagleEye作者。


**最近瞅着测APP的空档，翻了翻之前买的一本讲Android安全的书，书快要翻完了，但是里面还有实际操作的部分，书里面提到的工具跟目前用到的有一些出入，借着google总算把最简单的一部分搞定了，做个记录~**

> 操作系统：win10

先从一个很简单的apk包入手，一个假登录页面：

![页面1.png](https://image.3001.net/images/20190525/1558745376_5ce89120b13fc.png!small)点击登录的时候弹出提示：![页面2.png](https://image.3001.net/images/20190525/1558745388_5ce8912c4f403.png!small)

代码用得是Android Studio3.5的版本，Android
Studio的版本更新后，代码的书写方式也跟以前不一样了：![代码.png](https://image.3001.net/images/20190525/1558746229_5ce8947541c7e.png!small)

主页面完成后，打包成apk文件，这里我试了三种打包方式，结果都是一样的：

未签名打包：

![打包1.png](https://image.3001.net/images/20190525/1558745400_5ce89138f16be.png!small)

V1方式签名的正式包：

![打包2.png](https://image.3001.net/images/20190525/1558745411_5ce8914354fe7.png!small)![打包2-1.png](https://image.3001.net/images/20190525/1558745418_5ce8914a17e0e.png!small)

V2方式签名的正式包：![打包3.png](https://image.3001.net/images/20190525/1558745434_5ce8915a9447e.png!small)

打包完成后，找到apk包文件，![打包成功.png](https://image.3001.net/images/20190525/1558745448_5ce891682c7f7.png!small)

使用apktool直接反编译：![反编译.png](https://image.3001.net/images/20190525/1558745504_5ce891a039e93.png!small)

> .\apktool.bat d -f .\app-release.apk -o test
>
> 解释：
>
> d表示decode，意思是反编译，与之对应的是b ，building，编译
>
> -f 表示force，强制删除目标目录
>
> -o 表示输出地址

反编译后进入到test文件夹下的/smali/com/example/hellosmali中，可以看到有两个MainActivity的smali文件：![反编译结果.png](https://image.3001.net/images/20190525/1558745520_5ce891b070c44.png!small)

其中MainActivity$onCreate$1.smali文件中有我们希望修改的onclick操作：  

![反编译代码.png](https://image.3001.net/images/20190525/1558745543_5ce891c74047a.png!small)

修改const-string v1值为：hello smali

![反编译后修改代码.png](https://image.3001.net/images/20190525/1558745554_5ce891d2f2d3b.png!small)

这里修改完成后需要重新回编译为apk包，书上说的是用Android逆向助手，但是我试过后并没有打包成功：![Android逆向助手.png](https://image.3001.net/images/20190525/1558745569_5ce891e1bac8e.png!small)

apktool也可以进行回编译：![apktool打包报错.png](https://image.3001.net/images/20190525/1558745584_5ce891f099d2c.png!small)

这里报错了，因为高版本的Android
Studio和Gradle使用了aapt2打包apk，但是apktool却是使用的aapt1打包。按照网上教的办法在gradle.properties文件添加了android.enableAapt2=false：![禁用aapt2.png](https://image.3001.net/images/20190525/1558745603_5ce892039847a.png!small)

重新编译apk包，继续报错：![还是打包报错.png](https://image.3001.net/images/20190525/1558745651_5ce8923361ce2.png!small)

这里点报错信息后定位到了minSdkVersion，我还以为是最低版本的问题，改为20后，还是报错……

想了想，又将apktool升级到了最新版本，重新回编译，还是报错，但是错误提示已经跟之前不一样了：![重新回编译.png](https://image.3001.net/images/20190525/1558745678_5ce8924e86cfe.png!small)

删除了报错的xml文件后，又继续提示其他文件报错T_T……

本来打算下个3.0以下版本的android
studio再重新打包个apk，不过后来在网上看到一个回答说可以把C:\Users\XX\AppData\Local\apktool\framework\1.apk删掉试试，抱着试试的心态删掉了1.apk，再重新回编译：

> .\apktool.bat b .\test\

![回编译成功.png](https://image.3001.net/images/20190525/1558745825_5ce892e19fb7d.png!small)

看着成功了，去dist目录下看果然有了新包：![有了新包.png](https://image.3001.net/images/20190525/1558745862_5ce89306c3d78.png!small)

将新打的包安装到Android机上，又报错：![未签名报错.png](https://image.3001.net/images/20190525/1558745900_5ce8932cd0236.png!small)

NO_CERTIFICATES，没有签名，不能安装，那就先给apk包签个名好了，用得是jdk自带的keytool和jarsigner工具。

使用keytool工具先生成签名文件：![keytool位置.png](https://image.3001.net/images/20190525/1558745924_5ce893440119c.png!small)![生成签名文件.png](https://image.3001.net/images/20190525/1558745945_5ce893595f4b1.png!small)

> .\keytool.exe -genkey -alias "test" -keyalg "RSA"
>
> 解释：
>
> -genkey 创建新密钥
>
> -alias 密钥别名
>
> -keyalg 生成密钥对的算法
>
> -validity ，后面跟天数，代表创建的证书有效期，也可默认

再使用jarsigner工具进行签名：![jarsigner工具.png](https://image.3001.net/images/20190525/1558745958_5ce89366572cc.png!small)![jarsigner成功.png](https://image.3001.net/images/20190525/1558746046_5ce893be5a944.png!small)

> .\jarsigner.exe -verbose -keystore C:\
>
> Users\xxx\\.keystore -signedjar C:\Users\xxx\app-debug-signed.apk
> C:\Users\xxx\app-debug.apk "test"
>
> 解释：
>
> -verbose 签名/验证时输出详细信息
>
> -keystore 密钥库位置
>
> -signedjar 已签名的jar文件的名称

注意最后跟的是别名（alias），写错了会报错的：![jarsigner报错.png](https://image.3001.net/images/20190525/1558746073_5ce893d932116.png!small)

最后终于生成了一个签名包：![签名包生成.png](https://image.3001.net/images/20190525/1558746085_5ce893e563531.png!small)

再次安装：![已存在报错.png](https://image.3001.net/images/20190525/1558746117_5ce8940552c4d.png!small)

提示已经存在这个包了，删除手机上的原来的app，重新安装，成功：![再安装成功.png](https://image.3001.net/images/20190525/1558746129_5ce89411b9b57.png!small)

再点击登录按钮时，可以看到提示语已经被修改过了：

###
![更改登录.png](https://image.3001.net/images/20190525/1558746144_5ce894202b3b4.png!small)后记：

这是Android静态分析的开始，入门级的入门级，虽然简单，但是对于我这种菜鸟级的还是有不少的坑，看到预期的结果出现后还是有那么一丢丢成就感的^_^

 ***本文作者：梦里不知哪儿是哪儿，转载请注明来自FreeBuf.COM**


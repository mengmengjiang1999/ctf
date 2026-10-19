cocos2d-js中jsc逆向为js文件或字节码。

 **源码：**<https://github.com/zzwlpx/jsc-decompile-mozjs-34>（fork）

 **用法：**

1、需要先安装php7.0

下载php7.0 加入环境变量

2、修改php.ini

memory_limit = 512M #大小可根据自己内存大小调节，值如果设置太小，逆向解析较大jsc文件时，会崩溃。

3、反编译成js文件

$ php jsc2js.php *.jsc > test.js

4、反汇编成js 字节码文件

$ php jsc-byte.php > test.bytecode

```

 **效果：**

还原之后，可读，无法能运行。 **  
**

![微信截图_20181227124110.png](https://image.3001.net/images/20181227/1545886193_5c2459f1469b0.png!small)  


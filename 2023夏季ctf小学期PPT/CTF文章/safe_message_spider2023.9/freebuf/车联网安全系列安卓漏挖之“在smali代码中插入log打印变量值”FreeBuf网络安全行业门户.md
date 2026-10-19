**摘要**

安卓漏挖第三步，学会smali代码中插入log打印变量值。本文跟着师傅文章(https://www.52pojie.cn/thread-665362-1-1.html）走。

 **简单尝试**

 **01** **编写JAVA程序**

打开AndroidStudio，新建一个项目，在MainActivity里面写一段switch case语句。

    
    
    package com.example.myapplication2;import androidx.appcompat.app.AppCompatActivity;import android.os.Bundle;import android.util.Log;public class MainActivity extends AppCompatActivity {String name;@Overrideprotected void onCreate(Bundle savedInstanceState) {super.onCreate(savedInstanceState);setContentView(R.layout.activity_main);name = "zjj";switch (name) {case "zjj":Log.i("hello", "zjj");break;case "zjj1":Log.i("hello", "zjj1");break;case "zjj2":Log.i("hello", "zjj2");break;default:Log.i("hello", "no match name");break;}}}

还是那个建议，不需要自己写import，像下图的情况，Log出现下划线后，按alt+enter来自动生成。

![1670401571_63904e239ae1508252d2a.png!small](https://image.3001.net/images/20221207/1670401571_63904e239ae1508252d2a.png!small)

打开雷电模拟器，在AS中连接到模拟器

![1670401593_63904e390fc6831c653f4.png!small](https://image.3001.net/images/20221207/1670401593_63904e390fc6831c653f4.png!small)

编译后，打开雷电模拟器安装并运行程序，log有点多，可以搜索一下，就把自己添加的Log打印出来了。

![1670401612_63904e4c217e9d7cef328.png!small](https://image.3001.net/images/20221207/1670401612_63904e4c217e9d7cef328.png!small)

 **02** **反编译后分析smali代码**

把程序用AndroidKiller反编译，并对switch case语句的smali代码进行分析。

![1670401626_63904e5a73545129a93d0.png!small](https://image.3001.net/images/20221207/1670401626_63904e5a73545129a93d0.png!small)

找到高亮，可以看到执行的是显示log的函数。并且打印的值是v4，v2，对应hello，zjj2，所以pswicth0是我们编写的源码的第三个分支。（PS：鼠标悬停在字符串上会自动显示出汉字）

![1670401641_63904e6922c0875293004.png!small](https://image.3001.net/images/20221207/1670401641_63904e6922c0875293004.png!small)

我把原来要打印的“zjj"，改成了"zjj我是添加的smali代码"

![1670401668_63904e840f6e906f64dc4.png!small](https://image.3001.net/images/20221207/1670401668_63904e840f6e906f64dc4.png!small)

Ctrl+S保存好后，卸载-->编译-->安装打开Android Monitor看Log

 **03** **解决AK报错**

更改完smali代码后，发现AK编译报错，NO RESOURCE IDENTIFIER FOUND FOR ATTRIBUTE
。于是找到了这篇文章（https://www.freesion.com/article/3978416384/）,首先去ApkTool官网（https://ibotpeaches.github.io/Apktool/）,下载最新版本的ApkTool，这里我下载的是最新的2.6.1，添加后设为默认。

![1670401684_63904e9458c1b33bd616c.png!small](https://image.3001.net/images/20221207/1670401684_63904e9458c1b33bd616c.png!small)

打开命令行cmd进入刚才 apktool_2.6.1.jar 所在的目录，接着执行以下命令:

    
    
    java -jar apktool_2.6.1.jar empty-framework-dir

执行完上面的命令后，再次回编译就ok了.编译后在雷电模拟器上安装，在AS中查看打印的log，这里把原本的输出改变了，大家可以自己随意的尝试改变smali代码。

![1670401702_63904ea66114b43b2aff8.png!small](https://image.3001.net/images/20221207/1670401702_63904ea66114b43b2aff8.png!small)

 **2 打印变量的值**

通常在实战中插入一句话Log是为了打印出程序中某个变量的值。

 **01** **创建一个demo**

这里我编写了一个Demo,从下面的代码中可以出我在onCreate方法中执行了三个函数，函数名分别是fun1 fun2和fun3。并且在下面加入一条Log
目的是为了打印出函数fun1的返回值，因为Log.i的两个参数都必须是String类型，所以这里把int类型的fun1这个函数通过String.valueOf函数转换成String类型。

MainActivity.java如下：

    
    
    package com.example.a03;import androidx.appcompat.app.AppCompatActivity;import android.os.Bundle;import android.util.Log;public class MainActivity extends AppCompatActivity {@Overrideprotected void onCreate(Bundle savedInstanceState) {super.onCreate(savedInstanceState);setContentView(R.layout.activity_main);fun1();fun2();fun3();Log.i("这个值是",String.valueOf(fun1()));}public int fun1(){int value = Test.value;return value;}public int fun2(){int value2 = Test.value2;return value2;}public String fun3(){String str = Test.str;String str2 = Test.str2;int value3 = Test.value3;return str2;}}

创建个新文件，Test.java，内容如下：

    
    
    package com.example.a03;public class Test {public static int value = 888;public static int value2 = 777;public static int value3 = 666;public static String str = "zjj";public static String str2 = "码完代码去看东方明珠";}

编译完运行后，应该会把888打印出来。

![1670401760_63904ee0883436952c3e9.png!small](https://image.3001.net/images/20221207/1670401760_63904ee0883436952c3e9.png!small)

 **02** **完成任务1一添加Log打印出fun2,fun3的值**

思路：原函数中有个Log是打印fun1的值的，我只要找到打印fun1的这条log反编译成的smali代码，把里面的fun1改成fun2，复制一份。

![1670401775_63904eefbd6c33dafc72b.png!small](https://image.3001.net/images/20221207/1670401775_63904eefbd6c33dafc72b.png!small)![1670401787_63904efbacf415fa600b0.png!small](https://image.3001.net/images/20221207/1670401787_63904efbacf415fa600b0.png!small)

把fun2的值打印了出来，那么fun3的值怎么打印呢？可以看到fun2和fun3函数都是int类型，然后通过String.valueOf这个函数转换成的String类型。但是fun3这个函数本身就是String类型，这里如果还通过String.valueOf函数转换的话程序会报错的。

分析下smali代码，重新插一条Log去打印fun3函数的返回值

![1670401803_63904f0b0203edb7f55a5.png!small](https://image.3001.net/images/20221207/1670401803_63904f0b0203edb7f55a5.png!small)![1670401814_63904f165de9497ea78ea.png!small](https://image.3001.net/images/20221207/1670401814_63904f165de9497ea78ea.png!small)

 **03** **完成任务2一添加Log打印出fun3里面String** **类型str的值**

首先从smali代码中找到fun3方法所在的位置，然后在方法里面找到str的值，一般来说程序都会把这个值储存到寄存器中，可以找到这个寄存器，然后把寄存器作为变量给打印出来。

![1670401824_63904f20c85cf65b3c898.png!small](https://image.3001.net/images/20221207/1670401824_63904f20c85cf65b3c898.png!small)![1670401840_63904f3051b6b58110a06.png!small](https://image.3001.net/images/20221207/1670401840_63904f3051b6b58110a06.png!small)

 **04** **完成任务3一添加Log打印出fun3里面int** **类型value3的值**

思路：找到int类型value3的值，用到函数String.valueOf，通过Log打印出来。

![1670401856_63904f40ae0d7f58b2c72.png!small](https://image.3001.net/images/20221207/1670401856_63904f40ae0d7f58b2c72.png!small)![1670401865_63904f49a72cdce6176f2.png!small](https://image.3001.net/images/20221207/1670401865_63904f49a72cdce6176f2.png!small)

 **参考链接**

[https://www.52pojie.cn/thread-665362-1-1.html
](https://www.52pojie.cn/thread-665362-1-1.html)

<https://www.freesion.com/article/3978416384/>

<https://ibotpeaches.github.io/Apktool/>


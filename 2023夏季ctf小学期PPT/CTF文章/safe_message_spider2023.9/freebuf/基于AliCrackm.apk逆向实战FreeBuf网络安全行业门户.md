本篇文章主要针对AliCrackm.apk程序逆向分析实战进行了描述，也是针对Android逆向中的动态调试以及反反调试技术的一个练习和实战。

打开程序，输入验证码提交后提示校验失败,![](https://image.3001.net/images/20211026/1635246747_6177e29bb540aea052f68.png!small)

利用jadx_gui打开，代码逻辑为输入验证码传入so库，校验成功加载ResultActivity，否则弹出验证码校验失败,![](https://image.3001.net/images/20211026/1635246804_6177e2d46f7f6f6b87807.png!small)

将apk文件后缀修改为zip，解压后将lib下的so文件拖入IDA分析,![](https://image.3001.net/images/20211026/1635246838_6177e2f66e0b91a566e4e.png!small)

先看Java_com_yatong_crackme_MainActivity_securityCheck,![](https://image.3001.net/images/20211026/1635246918_6177e3460bad19266963f.png!small)

查看代码逻辑上边两个if循环中byte_6359和byte_635A，没有什么重要的逻辑，下边GetStringUTFChars将string类型转换为char，将返回值给v5，下边是off_628C的返回值给v6和一个while循环，

查看代码逻辑上边两个if循环中byte_6359和byte_635A，没有什么重要的逻辑，下边GetStringUTFChars将string类型转换为char，将返回值给v5，下边是off_628C的返回值给v6和一个while循环，![](https://image.3001.net/images/20211026/1635246990_6177e38e2adcd9f791c86.png!small)

发现字符串“aWojiushidaan”，提交测试发现不是答案，对while分析发现是一死循环，因此初步判断可能off_628C可能是验证码校验逻辑，查看地址为12A4,![](https://image.3001.net/images/20211026/1635247016_6177e3a8c8e6d14b83f4c.png!small)

该静态注册分析完发现还有一个JNI_Onload动态注册，继续分析,![](https://image.3001.net/images/20211026/1635247059_6177e3d3b33ed912835e3.png!small)

可以看到一个if循环，下边有sub_16A4和sub_17F4两个函数，继续分析sub_17F4,![](https://image.3001.net/images/20211026/1635247095_6177e3f7861831f3e1e46.png!small)

可以看出一些字段都进行了加密，无法看出其中内容，继续查看sub_16A4，发现分别有sub_130C和dword_62B0，进行查看也进行加密，![](https://image.3001.net/images/20211026/1635247139_6177e42358799b7e9e8c3.png!small)

因为该动态注册中的字段都进行了加密，无法查看，因此可能程序运行后会进行解密，接下来考虑动态调试。

因为要动态调试，因此利用AndroidKiller打开apk，在AndroidManifest.xml中添加android:debuggable="true"，然后进行重新编译，这个时候就支持调试了，

安装重新编译后的apk，

![](https://image.3001.net/images/20211026/1635247186_6177e4528369e5d3a45a9.png!small)

将IDA中的android_server push到模拟器上，

![](https://image.3001.net/images/20211026/1635247219_6177e4731f34514f18511.png!small)

adb连接模拟器，并切换root账号，

![](https://image.3001.net/images/20211026/1635247250_6177e492caeccb406a800.png!small)

进入/data/loacal/tmp下给android_server修改权限，

![](https://image.3001.net/images/20211026/1635247283_6177e4b32e967f9c3589e.png!small)

运行android_server，

![](https://image.3001.net/images/20211026/1635247312_6177e4d0800ee74cb584a.png!small)

端口转发，并挂起该程序，

![](https://image.3001.net/images/20211026/1635247345_6177e4f19df0847d39ad7.png!small)

打开IDA，Attach该程序，

![](https://image.3001.net/images/20211026/1635247375_6177e50f1e9827bf8786c.png!small)

点击ok，

![](https://image.3001.net/images/20211026/1635247415_6177e537926018ee4e6bc.png!small)

选择该程序包名，点击ok，加载完成后勾选对应的选项，

![](https://image.3001.net/images/20211026/1635247449_6177e5593fd9de50b474a.png!small)

F9运行，并加载该程序，

![](https://image.3001.net/images/20211026/1635247476_6177e57416505fbaee3e1.png!small)

Module list查看加载so库，

![](https://image.3001.net/images/20211026/1635247512_6177e5983992e12be7cee.png!small)

Libcrackme.so加载完成，选择静态注册调试，

![](https://image.3001.net/images/20211026/1635247604_6177e5f45eb0ff984cbd1.png!small)

F9进行运行程序，

![](https://image.3001.net/images/20211026/1635247556_6177e5c42af21652f75e2.png!small)

程序崩溃，那么可以判断该程序有反调试，可以判断JNI_Onload则为反调试代码逻辑，

![](https://image.3001.net/images/20211026/1635247649_6177e621d3bc6229944cf.png!small)

选择JNI_Onload进行加载，

![](https://image.3001.net/images/20211026/1635247681_6177e6415d0b3d0ded99f.png!small)

在JNI_Onload处下断点，![](https://image.3001.net/images/20211026/1635247725_6177e66dadf018d8069af.png!small)

F9运行到该断点处F8向下执行，在静态分析时可以判断处有个if循环跳转，因此当向下执行到BLX
R0时则F7进入，看一下内部的代码逻辑，![](https://image.3001.net/images/20211026/1635247758_6177e68eae004c163142d.png!small)

数据窗口跟随R0，

![](https://image.3001.net/images/20211026/1635247794_6177e6b2d9ee9008e5f40.png!small)

F8单步向下执行，可以看到dlsym以及getpid，因此可以判断是对字段进行解密，![](https://image.3001.net/images/20211026/1635247824_6177e6d08300f2dd2a7de.png!small)

继续向下，可以看到创建线程以及杀死进程一些列字段，那么这边便可以判断该so库代码该so库中是一个检测程序是否被调试，如果调试则中断程序的作用，

![](https://image.3001.net/images/20211026/1635247864_6177e6f821da942b50612.png!small)

再向下便跳出了给函数，

![](https://image.3001.net/images/20211026/1635247902_6177e71e577931ce1acf3.png!small)

至此该if循环代码分析完成，![](https://image.3001.net/images/20211026/1635247946_6177e74ae079bae97f327.png!small)

继续向下可以看到sub_16A4和sub_17F4，![](https://image.3001.net/images/20211026/1635247980_6177e76c7a01ae8467bb9.png!small)

那么在动态调试窗口向下翻便可以看到sub_AB85B7F4，因此BLX和BL对应静态分析中的sub_16A4和sub_17F4，那么在BLX
R7下断点，![](https://image.3001.net/images/20211026/1635248014_6177e78eee391d2f1849e.png!small)

将程序执行到该断点处，![](https://image.3001.net/images/20211026/1635248046_6177e7ae200d0d924bb52.png!small)

进入其内部代码逻辑，可以看到sub_AB85B6A4和loc_AB85B6B8，![](https://image.3001.net/images/20211026/1635248084_6177e7d4a1d8906f29a0a.png!small)

那便是静态分析中对应的sub_130C和dword_62B0，![](https://image.3001.net/images/20211026/1635248118_6177e7f6726fffc2d0d3f.png!small)

通过调试验证该loc_AB85B6B8中的BL便是不断的执行进程检测调试的关键，![](https://image.3001.net/images/20211026/1635248150_6177e81665958001059a9.png!small)

因此将该BL处直接NOP掉，![](https://image.3001.net/images/20211026/1635248182_6177e83653735f4c79626.png!small)

F2修改完成之后继续进入静态注册进行校验逻辑调试，![](https://image.3001.net/images/20211026/1635248217_6177e859953aa20c308d9.png!small)

进入后P一下代码逻辑，![](https://image.3001.net/images/20211026/1635248245_6177e87543bfa392e7ed6.png!small)

通过之前的静态分析判断处该校验逻辑在B2A4处，那么在该地址上一处下断，![](https://image.3001.net/images/20211026/1635248278_6177e8965e2638764fa14.png!small)

F9运行到该断点，程序启动，随意输入一串字符，进行验证，![](https://image.3001.net/images/20211026/1635248309_6177e8b57f738395f3319.png!small)

F8单步向下执行，![](https://image.3001.net/images/20211026/1635248344_6177e8d892679d99297ca.png!small)

单步过之后进入可以看到将值给了R2，因此进入R2查看数据，看到一串字符aiyou,bucuoo，![](https://image.3001.net/images/20211026/1635248377_6177e8f92a9cab966bee9.png!small)

在程序输入验证，![](https://image.3001.net/images/20211026/1635248407_6177e9174f2978af82424.png!small)

程序校验成功，成功获取到flag，![](https://image.3001.net/images/20211026/1635248445_6177e93d4f3482570465a.png!small)至此针对该app的逆向分析就完成了，在本次分析中涉及
到smali代码的分析、so层代码的静态分析、IDA的动态调试以及反调试等方面的知识，也是对多方面知识的一个练习和 实战巩固。


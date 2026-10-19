原创 萌新 合天智汇

前情提要：<https://www.freebuf.com/column/229237.html>

0x04flag

![v2-e0b6f9e17e5f6656a6edde31a5a74183_720w](https://pic2.zhimg.com/80/v2-e0b6f9e17e5f6656a6edde31a5a74183_720w.jpg)

看题目描述似乎是一个和脱壳相关的逆向题目

按照给出的地址先下载过来

![v2-e3c5b4a5033d1f9946eb908d1fed9d85_720w](https://pic3.zhimg.com/80/v2-e3c5b4a5033d1f9946eb908d1fed9d85_720w.jpg)

file看看

![v2-b16fbd8179b3ee7d8a2c9f6613de3c30_720w](https://pic4.zhimg.com/80/v2-b16fbd8179b3ee7d8a2c9f6613de3c30_720w.jpg)

是个可执行文件

执行之

![v2-ff5893aee563c28c553ae06a7eaf7a26_720w](https://pic2.zhimg.com/80/v2-ff5893aee563c28c553ae06a7eaf7a26_720w.jpg)

emm什么都看不出来，又没有源码

那载入gdb吧

![v2-870844dc59adc50ce34b986c85f8db7a_720w](https://pic4.zhimg.com/80/v2-870844dc59adc50ce34b986c85f8db7a_720w.jpg)

emmm，没有符号表，无法反汇编

哦，对了，根据题目的提示这是加了壳的，所以先脱壳

这是什么壳呢？

Strings看看

![v2-9c1aa931ee625b1c113057d0455bf384_720w](https://pic2.zhimg.com/80/v2-9c1aa931ee625b1c113057d0455bf384_720w.jpg)

upx的

这里简单介绍下upx：

UPX是一个著名的压缩壳,主要功能是压缩PE文件(比如exe,dll等文件),有时候也可能被病毒用于免杀.壳upx是一种保护程序。一般是EXE文件的一种外保护措施，主要用途
：

1、让正规文件被保护起来，不容易被修改和破解。

2、使文件压缩变小。

3、保护杀毒软件安装程序，使之不受病毒侵害。

4、木马，病毒的保护外壳，使之难以为攻破

和很多壳比起来upx的手动脱壳也比较简单，但是本文主要学习pwn而不是脱壳，如果有对upx手动脱壳有兴趣的话这里推荐一篇文章：https://blog.csdn.net/fawdlstty/article/details/8332227

我们这里直接自动脱壳就可以了

![v2-f47321ac161204bad8ef274c30161e45_720w](https://pic3.zhimg.com/80/v2-f47321ac161204bad8ef274c30161e45_720w.jpg)

接下来再载入gdb

![v2-5e7396a00a816841b12d006efbeb0034_720w](https://pic4.zhimg.com/80/v2-5e7396a00a816841b12d006efbeb0034_720w.jpg)

反汇编main后看到了一个地址

打印出来

![v2-f63b8f7b02c8e3c1ea5c736cade431c9_720w](https://pic4.zhimg.com/80/v2-f63b8f7b02c8e3c1ea5c736cade431c9_720w.jpg)

这就是flag了

加壳与脱壳技术：

http://www.hetianlab.com/cour.do?w=1&c=CCIDe9a2-7038-4d4f-951e-c5b068d31798​www.hetianlab.com

复制上方链接做实验哦。

0x05passcode

![v2-837142e687eaa3739080832c789f49c1_720w](https://pic1.zhimg.com/80/v2-837142e687eaa3739080832c789f49c1_720w.jpg)

看题目描述，编译时没有报error，那是不是会报warning呢

连上机器后先看看源码

![v2-2790d977d0f5d85cc606b1adb96f1f11_720w](https://pic2.zhimg.com/80/v2-2790d977d0f5d85cc606b1adb96f1f11_720w.jpg)

从源码中可以看到

1.程序功能是先输入name，然后输入passcode1,passcode2，相当于输入一个用户名，两个密码

2，main中接连执行welcome,login，中间没有push,pop，二者ebp相同

3，login()中scanf接收输入的时候，passcode1，passcode2没有加上&取地址，又由于passcode1,passcode2没有被初始化，所以我们scanf输入数据时，数据被保存到哪儿是未知的，只是知道数据被保存到passcode1,passcode2的值指向的地址中去了。

考虑2和3，我们猜想是否可以通过控制name的内容进而控制passcode1，passcode2呢？毕竟name取100字节，三者的ebp又是相同的

不过具体是否可行，我们上gdb试试

![v2-e5f669ab4f2ce22261c071ddf0ce190d_720w](https://pic3.zhimg.com/80/v2-e5f669ab4f2ce22261c071ddf0ce190d_720w.jpg)

![v2-6f6b5a2a1ebb431c2a96c7ae1c58073d_720w](https://pic3.zhimg.com/80/v2-6f6b5a2a1ebb431c2a96c7ae1c58073d_720w.jpg)

图x

可以看到name地址为%ebp-0x70,passcode1地址为ebp-0x10,二者差0x70-0x10=96个字节。Passcode2地址为%ebp-0xc,.name和passcode2从差0x70-0xc=100个字节，我们只能通过写name控制passcode1，但是不能控制passcode2

既然可以控制passcode1，那么思路就清楚了。

由源码逻辑可知，printf,scanf,fflush

我们控制passcode1的地址（name的最后4字节）为ffliush地址，在随后scanf(“%d”,passcode1)接收输入时我们输入system(“/bin/cat
flag)的地址

这样当执行fflush时，将会执行system，从而读到flag

通过GOT表获取flush地址

![v2-fa425f0c701ebf1a5b714118bc936367_720w](https://pic3.zhimg.com/80/v2-fa425f0c701ebf1a5b714118bc936367_720w.jpg)

在图x中可以看到调用system的地址为080485ea，不过在此之前还有传参的操作，所以实际上，地址应该为0x080485e3,十进制为134514147

从而构造出exp

![v2-eaac47786df50b5eda262d0b93e26d51_720w](https://pic3.zhimg.com/80/v2-eaac47786df50b5eda262d0b93e26d51_720w.jpg)

总结一下，这里用到的技术叫做GOT覆写，就本题而言，是这样子的：

我们通过控制nane的最后四个字节，将passcode1的值改为fflush的地址，而在程序中，scanf后会调用fflush，而我们已经把system(“bin/cat
flag”)的地址写到fflush中，覆盖了fflush在GOT表中的内容，所以当scanf调用时，会直接执行system打印flag，绕过了后面比较passcode1,passcode2的逻辑。

0x06random

![v2-b0811c4d4a8179c436de829940b992f5_720w](https://pic1.zhimg.com/80/v2-b0811c4d4a8179c436de829940b992f5_720w.jpg)

看描述，是和随机数有关系

![v2-72f9784099b8874358686b4c8aa9dc08_720w](https://pic3.zhimg.com/80/v2-72f9784099b8874358686b4c8aa9dc08_720w.jpg)

由源码可知，当满足key与random异或得0xdeadbeef时才打印flag

而random的值由rand函数产生，key的值由我们输入

那么本题的关键就是找到random的值是多少

我们知道，rand函数产生的实际是伪随机数，所以我们可以写个程序，先由rand生成一个数，将其与0xdeadbeef相异或，得到的值就是我们输入的key

这是一种思路

或者我们也可以用gdb调试，在程序判断if条件是否成立的地方下断点，观察内存布局，也是可以得到random的值的

![v2-3361ffed221554202a62ae32578de913_720w](https://pic2.zhimg.com/80/v2-3361ffed221554202a62ae32578de913_720w.jpg)

下了断点后输入2，然后命中

![v2-82e133030c660c19f096bcc3487b26e0_720w](https://pic3.zhimg.com/80/v2-82e133030c660c19f096bcc3487b26e0_720w.jpg)

可以看到，2是我们的输入，而0x6b8b4567则是random

那么我们将该值与random异或即可得到输入的key

![v2-d3123b4600d8a4a9a74cbf6942daa26e_720w](https://pic2.zhimg.com/80/v2-d3123b4600d8a4a9a74cbf6942daa26e_720w.jpg)

0x07leg

![v2-74fa94dc0a0a99b967c2b4c9512e5b9b_720w](https://pic4.zhimg.com/80/v2-74fa94dc0a0a99b967c2b4c9512e5b9b_720w.jpg)

看题目这题是和arm、汇编相关的

把源程序下过来看看

![v2-e74acb9f792590235ee700d447afaa2d_720w](https://pic2.zhimg.com/80/v2-e74acb9f792590235ee700d447afaa2d_720w.jpg)

看到main中需要满足key1()+key2()+key3（）=key才可打印出flag

key是我们需要输入的

key1()等表示的相关函数的返回值

那么本题就是要求出相关函数的返回值并相加

而c源码中这三个函数都是内联汇编的形式

还是直接用gdb看看吧

题目和我们说了这是arm

通常情况下，arm以r0寄存器存返回值，对应在x86中就是eax

这一点从汇编中也可以看出

![v2-53680cd3511c37c0631a836b438f77e3_720w](https://pic4.zhimg.com/80/v2-53680cd3511c37c0631a836b438f77e3_720w.jpg)

那么在每个函数中r0的值是多少呢

一一看过来

先看key1

![v2-35e5e61bc0def66e4749b2a4d18e298c_720w](https://pic2.zhimg.com/80/v2-35e5e61bc0def66e4749b2a4d18e298c_720w.jpg)

可以看到，pc->r3->r0，也就是说r0的值为pc寄存器的值

这里有个知识点

ARM属于RISC，精简指令及，分三段流水，取指、译码、执行

当mov r3,pc执行时，此时的pc为当前指令地址+0x8，及0x8cdc+0x8

再看key2

![v2-f44bb8a7528da22d31fadf8e7ead8b96_720w](https://pic1.zhimg.com/80/v2-f44bb8a7528da22d31fadf8e7ead8b96_720w.jpg)

add r6,pc,#1的意思是r6=pc+1,由key1的知识知，r6=0x8cfc+8+1,该值最低位为1

为什么要强调最低位

因为后面一条指令bx r6

bx指令用于切换处理器状态模式，最低位为1时，切换到Thumb指令执行，为0时，解释为ARM指令执行

所以执行该指令后就切换到了thumb模式下

而thumb模式下pc值为当前指令地址+4

所以执行r3，pc时，r3的值为0x8d04+4

再执行adds,r3,#4后r3的值Wie0x8d04+4+4

执行mov r0,r3后，r0的值也同r3

再看看key3

![v2-5cf8a901f7180505f492e06a9915bcfb_720w](https://pic3.zhimg.com/80/v2-5cf8a901f7180505f492e06a9915bcfb_720w.jpg)

执行红框中的两条指令后,r0的值等于lr的值

lr即r14，存放是函数返回地址

具体的值在main中可以看到，为0x8d80

综上，得key值为108400

![v2-95b563cde0bc77cb8beb26210551102a_720w](https://pic1.zhimg.com/80/v2-95b563cde0bc77cb8beb26210551102a_720w.jpg)

欲知后续，请留意每日文章推送！

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  


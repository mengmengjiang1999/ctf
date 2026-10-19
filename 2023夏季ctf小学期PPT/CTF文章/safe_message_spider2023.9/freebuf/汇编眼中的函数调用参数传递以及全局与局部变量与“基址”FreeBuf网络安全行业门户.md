作为刚往底层方向走的一只菜鸟，今天为各位分享一篇名为汇编眼中的函数调用参数传递以及全局、局部变量与“基址”，好了，废话不多说，先来看看C语言代码：

![879321_P68NEHNG7YR3W7A.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_P68NEHNG7YR3W7A.jpg)  

本次的分享主要以画堆栈图为主，通过画图的方式来看看这段代码是如何运作的

![879321_B2YWM9V8YWE4RZX.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_B2YWM9V8YWE4RZX.jpg)  

我们先写一句汇编代码，mov
eax,eax其实这句代码并没有什么用，也就是将eax的值移入eax中，这句代码对于我们的作用仅作为断点，我们F5运行下程序并且切换到反编译界面

![879321_RY9BQB6F4J3SHBG.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_RY9BQB6F4J3SHBG.jpg)  

右键之后点击Go To Disassemble，也就是进入反编译界面，我们来看看反编译的代码

![879321_9W5K2X75Z72KTW7.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_9W5K2X75Z72KTW7.jpg)  

这就是咱们main函数反编译后的结果，那么现在我们记录一下ebp，esp的值，并且画出现在的堆栈图

![879321_KZJ8YBFHJBKD6NC.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_KZJ8YBFHJBKD6NC.jpg)  

ESP = 0019FEF4

EBP = 0019FF40

![879321_ZWFYK44AR4F8JYN.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_ZWFYK44AR4F8JYN.jpg)

黄色=ebp~esp初始的内存

那好，我们继续来看代码

![879321_U6MFFGAEK4C2NH7.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_U6MFFGAEK4C2NH7.jpg)  

这里是我们自己写的汇编代码，编译器也没有改动过可以说是本色出演，这里内存没有变化，好，那么我们接着来看add函数这里的调用

![879321_FCMMDSJ6C7BU3XR.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_FCMMDSJ6C7BU3XR.jpg)  

可以看到函数调用的时候首先是将3、1这两个值推入栈中，但是又有疑问了“add函数的调用是这样的add(1,3)，为啥首先推入栈中的是3而不是1呢？”之所以这样是因为栈中是先进后出的，所以参数进入栈中的顺序是从右向左的，当然这里也可以看到函数中的参数是压入栈中然后取出来而不是通过通用寄存器eax，edx，ebx这些来传送参数的，其实这也好理解，因为通用寄存器只有八个，像esp，eip，ebp这样的寄存器还不能随便改，能用的也只有剩下的几个，参数超过剩下的几个咋办？那就只能用堆栈了。我们继续来看F10单步执行一下，看看堆栈的变化

![879321_KQE3J2GHBYND7GK.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_KQE3J2GHBYND7GK.jpg)  

我们再看看EBP和ESP

![879321_6WMVFZ9N3Q2SE44.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_6WMVFZ9N3Q2SE44.jpg)  

这里可以看到压入一个3后栈顶指针减去了4h，至于为啥减去4h呢？是因为一个int类型的数据宽度是4Byte=32Bit，能存入的最大数也就是0xFFFFFFFF，16进制数又是2进制数的简写形式，一个二进制数需要4Bit来存储，所以4位二进制数最大的值为1111转换为16进制后刚好为F，这样也方便了开发者，存储空间中我们看到的数据都是16进制数

十六进制 二进制

0h 0b

1h 1b

2h 10b

3h 11b

4h 100b

5h 101b

6h 110b

7h 111b

8h 1000b

9h 1001b

Ah 1010b

Bh 1011b

Ch 1100b

Dh 1101b

Eh 1110b

Fh 1111b

可能以上讲得有些出入，如有错误，请帮忙纠正，好了，我们接着来看，接下来push 1进去，我们来看看现在的堆栈图：

![879321_PH5KNK5AHUASVCM.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_PH5KNK5AHUASVCM.jpg)  

![879321_D8W2X8QBZ3CU98S.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_D8W2X8QBZ3CU98S.jpg)

继续看下面的代码：

![879321_R27JTFB33ZT8SPA.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_R27JTFB33ZT8SPA.jpg)  

接着是call，call指令在汇编中多用于函数调用，call指令做了两个操作，

1、Push 00401103（下一行代码地址）

2、Jmp 0040100A（函数地址）

这里我们F11一下，遇到call指令后按F11进入函数即可，这样我们就可以看到函数体中的指令

![879321_G394A5CJF84MBUG.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_G394A5CJF84MBUG.jpg)  

这里CALL之后看看堆栈中的变化：

![879321_7GQRE3STQRDRXQE.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_7GQRE3STQRDRXQE.jpg)

继续向下走，F11后跳转到的结果如下

![879321_46ADVGHWDXEC3P3.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_46ADVGHWDXEC3P3.jpg)  

这里是编译器决定的，不是所有编译器call后会进入一个jmp指令中转，再F11一下

![879321_9JF7QRXC25Z6C92.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_9JF7QRXC25Z6C92.jpg)  

Jmp执行之后直接进入了函数体，这里将通用寄存器ebp的值存入栈中，之所以存入栈中是因为每一个函数中都要使用ebp来寻址，所以需要将ebp的原始值存入栈中，随后将esp栈顶指针的值移入ebp中，sub
esp,40h是将栈顶指针加到40h这个位置，之所以是减40h是因为栈空间是从高到低的，现在我们单步执行一下看看栈中的变化

![879321_AN22J2E3XSCDBHM.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_AN22J2E3XSCDBHM.jpg)  
![879321_PCMSNVDZFT4YHV2.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_PCMSNVDZFT4YHV2.jpg)

  

这里40h移动的位置=40h/4h=10h=16，我们看看现在堆栈的变化

![879321_FXEKTGG4W69KGW7.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_FXEKTGG4W69KGW7.jpg)

Sub esp,40h这段代码我们是为函数开辟一块栈空间出来供函数存取值的，也就是我们常说的缓冲区，通常用来存储函数中的局部变量，我们接着往下看

![879321_K5PU3UHDMTPNXR6.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_K5PU3UHDMTPNXR6.jpg)  

接着向栈中推入了ebx，esi，edi，栈顶指针[esp-Ch]，然后lea指令将[ebp-40h]的地址放入edi中，给ecx赋值为10h=16，也就是循环16次又将0xCCCCCCCCh赋给eax，这也被称为断点字符，然后使用rep指令将缓冲区中的值赋值为0xCCCCCCCCh，现在我们再来看看堆栈中的变化

![879321_G2S98CPTGE4GBTF.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_G2S98CPTGE4GBTF.jpg)

我们看一下单步执行后的esp和ebp的结果

![879321_8PAWFU7TMQV8BTQ.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_8PAWFU7TMQV8BTQ.jpg)  

好勒，咱们接着往下走

![879321_89623KSF58RYCE9.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_89623KSF58RYCE9.jpg)  

这里可以看到首先是将栈中的[ebp+8]=0019FEE4+8=0019FEEC地址中的值移动到eax中，然后将eax与[ebp+Ch]=0019FEE4+Ch=0019FEF0地址中的值相加，并且将相加后的值存入eax中，栈空间无任何变化，变化的仅仅是eax，咱们单步执行看下

![879321_7ZC54SCTDSS5HCR.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_7ZC54SCTDSS5HCR.jpg)  

好了，我们接着往下看

![879321_G4VCQSGYZX6TSGZ.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_G4VCQSGYZX6TSGZ.jpg)  

首先将edi,esi,ebx中的值取出来，这里可以看到，我们推入和取出的顺序刚好相反，先进后出的道理，随后将ebp的值移动到esp中，这里也就改变了栈顶指针，然后pop
ebp，最后ret，ret的做的操作：

pop eip（这里取出的是返回地址）

咱们单步执行一下

![879321_XUM4V43UFEFCR5H.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_XUM4V43UFEFCR5H.jpg)  

![879321_MRRU9RSJA7WGTK5.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_MRRU9RSJA7WGTK5.jpg)

我们接着来看代码

![879321_CRQPE2UWEMGF467.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_CRQPE2UWEMGF467.jpg)  

这里esp+8是为了堆栈平衡，恢复最初的堆栈，我们单步一下

![879321_5ZJHTDFV6C67MAB.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_5ZJHTDFV6C67MAB.jpg)  

堆栈的变化如下：

![879321_V6256VQ75B5ABKC.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_V6256VQ75B5ABKC.jpg)

这样就和我们没进入函数之前的堆栈一样了，程序到这里就解释了函数调用以及传参的问题。我们接着往下走

![879321_9GNM24EDQMPHDAY.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_9GNM24EDQMPHDAY.jpg)  

函数调用又是一个call，call的两个操作：

1、Push 0040110B（下一行代码地址）

2、Jmp 00401005（函数地址）

单步会遇到jmp，我们直接单步进入函数体

![879321_UZVW6WXSC85KDZZ.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_UZVW6WXSC85KDZZ.jpg)  

对于这里的堆栈就不画了，主要讲解一下这里的全局变量以及“基址”是啥，这里我们的全局变量z是由变量定义的时候分配指定的内存地址，在每一个函数中都可以找到，每一个全局变量都有一个唯一的内存地址，有且只有一个，在游戏外挂中经常会听到找“基址”，然而这个“基址”就是全局变量的地址，只要程序被编译那么就只有这么一个指定的地址，我们这个程序中z的地址[00424a30],打开CE

![879321_76X3S629Y53J38S.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_76X3S629Y53J38S.jpg)  

首先我们运行一下我们写好的程序

![879321_FGUYJK644FJ9FPN.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_FGUYJK644FJ9FPN.jpg)  

![879321_SQVU4YQBFWTQF64.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_SQVU4YQBFWTQF64.jpg)  

选择我们刚才运行的程序，点击加入地址，我们将00424a30这个内存地址加入进去

![879321_VDGE3DNK4RHD8QP.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_VDGE3DNK4RHD8QP.jpg)  

点击ok，我们看看它的初始值

![879321_WCKUBGUV7GA2NUE.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_WCKUBGUV7GA2NUE.jpg)  

这里完全没有自己输入值，我们改一下值，看看程序的输出

![879321_FPGYC3EP6JMCS7Z.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_FPGYC3EP6JMCS7Z.jpg)  

点击OK，再看一下改了之后输出的值

![879321_EVMM95R75YWVCZE.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_EVMM95R75YWVCZE.jpg)  

总结：

1、全局变量是编译后分配的一个指定内存空间，因为是公共的所以任何程序或者程序中的函数都可以调用以及修改。

2、局部变量的地址是随机的，因为每次进入函数都会随机分配一段地址给函数，这段分配的地址称为缓冲区，缓冲区也是用来存储局部变量的。

3、“基址”就是全局变量，这是外挂开发中常用到的一个词汇。

4、函数调用使用call，call指令做的两个操作：

（1）push call指令下一行地址

（2）Jmp 函数地址（编译器决定，可能先跳转到中转地址，然后跳转到函数地址）

5、汇编中的函数就是指令的**，唯一不同的是函数最后都会用ret返回

6、函数中的参数传递是使用堆栈来传递的。

  
  


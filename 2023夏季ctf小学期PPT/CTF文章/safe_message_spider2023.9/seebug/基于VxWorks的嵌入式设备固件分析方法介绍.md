**作者：小黑猪（朱文哲）@银河安全实验室  
公众号：[银河安全实验室](https://mp.weixin.qq.com/s/lDZWjgAoJmD141ppd8DjgA "银河安全实验室")**

VxWorks
操作系统是美国WindRiver公司于1983年设计开发的一种嵌入式实时操作系统（RTOS），它以其良好的可靠性和卓越的实时性被广泛地应用在通信、军事、航空及航天等高精尖技术领域中。2012年8月登陆的好奇号，以及近日成功降落火星的洞察号均使用了VxWorks系统。

本文将以施耐德昆腾系列PLC的NOE-711以太网模块的固件为例，讲解一下基于VxWorks操作系统的嵌入式设备固件的一些常用分析方法。

### 1\. 固件提取

通常我们能够通过设备厂商的官网获取到设备固件的升级包，从该升级包中将真正的固件进行提取后才能进行分析。提取固件的常用方法是使用Binwalk等二进制分析工具对固件升级包进行自动化分析，待确认升级包类型后再进行固件提取或其他操作。

通过Binwalk进行自动分析可以发现，NOE 771模块的升级包NOE77101.bin中内嵌了一个使用zlib压缩的文件。

![
](https://images.seebug.org/content/images/2018/12/3b98fd02-d276-413d-8ed3-9b1ff2a68fc3.jpg)

通过调用Binwalk的-e参数进行自动提取后，Binwalk会把自动提取后的文件以偏移地址命名并存储在特定的目录中。

![
](https://images.seebug.org/content/images/2018/12/47acedbf-0f8d-49fe-a9f0-15df6a5a1ae4.jpg)

继续使用Binwalk对提取的385文件进行分析可以确认，该文件的确是我们所需要分析的VxWorks固件，因此提取的385文件也就是我们需要分析的固件文件了。

![
](https://images.seebug.org/content/images/2018/12/da4afc8e-b8a2-4bd7-8d25-e780eac63594.jpg)

### 2\. 分析固件内存加载地址

为了对VxWorks系统固件进行逆向分析，我们首先必须要知道固件在内存中的加载地址。加载地址的偏差会影响到一些绝对地址的引用例如跳转函数表、字符串表的引用等。

下图是VxWorks系统在PowerPC架构下的内存分布图，如图所示VxWorks的系统固件将会被加载到一个由BSP (Board Support
Package)定义的内存地址中。

![
](https://images.seebug.org/content/images/2018/12/49d18eaf-9a0e-4e06-8b00-2e4fcab995c2.jpg)

#### 2.1 方法一：通过封装的二进制文件头直接识别加载地址

某些设备的固件会使用某种格式进行封装，比较常见的是使用ELF(executable and linkable
format)格式进行封装。采用ELF格式封装后的文件头部有特定的数据位记录了该固件的加载地址，因此针对该情况我们可以直接使用greadelf等工具直接读取ELF文件头，从而直接获取到固件的加载地址，此外IDA也能直接识别ELF格式封装的VxWorks固件，无需额外处理即可进行自动化分析。

![
](https://images.seebug.org/content/images/2018/12/1a4a267e-4ca4-4aaf-b572-63918c0bc375.jpg)

#### 2.2 方法二：分析固件头部的初始化代码，寻找加载地址的特征

在很多情况下我们拿到的固件是没有采用ELF格式封装的，这时就需要我们通过对固件的某些特征进行分析来判断具体的加载地址。还是以施耐德的NOE 711固件为例,
在具体分析某个固件时首先我们需要知道目标设备的CPU架构，具体可以如下图所示通过 **binwalk -A**
指令来对固件的CPU架构进行分析，此外也可以用 **binwalk -Y**
指令来调用capstone反汇编引擎来进行辅助判断，不过我实际测试下来存在一些误报的情况会把NOE 711的固件识别成arm架构的。

![
](https://images.seebug.org/content/images/2018/12/a378f74a-0bd3-4912-91f0-e5eeb280bdc3.jpg)

在得知目标CPU架构后就可以使用IDA加载固件并对其代码进行初步分析。

![
](https://images.seebug.org/content/images/2018/12/c6adc90c-8da6-4bde-b9cc-4a232e71fdc7.jpg)

![
](https://images.seebug.org/content/images/2018/12/745a1452-aeb2-40e2-abfc-d1ec174ab130.jpg)

下图是默认加载后的IDA界面，仅仅分析出了极少数的函数。接下来就需要根据固件头部的这段代码来寻找加载地址的特征。

![
](https://images.seebug.org/content/images/2018/12/0efc16f4-e3ae-4d81-8e6c-28a9d15dc5d7.jpg)

在固件头部有如下图所示的一段有趣的代码，在对r1和r3寄存器进行赋值后进行了跳转。

![
](https://images.seebug.org/content/images/2018/12/fd07f3ea-3198-4c1f-9ba9-0ed4af9a02e1.jpg)

下图是PowerPC的寄存器用途说明，从图中可以看到R1寄存器是栈指针，而R3寄存器则是第一个参数。

![
](https://images.seebug.org/content/images/2018/12/e0da9f6e-8f70-431f-8850-c412d05eba35.jpg)

现在回到我们之前看的固件头部代码处，这段代码相当于是先将栈地址设置为0x10000，将第一个参数(r3寄存器)设置为0x0，随后在栈上开辟0x10个字节的空间后跳转到当前地址+0x1cd34处执行。

![
](https://images.seebug.org/content/images/2018/12/f31c807e-3009-4962-b8e1-cd4b42e9a731.jpg)

根据VxWorks官网文档对对内存布局的描述， **Initial Stack** 是 **usrInit** 函数的初始化栈。

![
](https://images.seebug.org/content/images/2018/12/1ded37b5-6408-4651-9b14-173a71a4881b.jpg)

而 **usrInit** 函数则是VxWorks系统引导后运行的第一个函数，再结合之前我们分析的那段代码，可以基本确定在大部分情况下第一个跳转的地址就是
**usrInit** 这个函数的地址。

![
](https://images.seebug.org/content/images/2018/12/34033440-ce1a-4759-8529-6dab27f3684d.jpg)

随后我们再回忆一下之前看到的VxWorks
PowerPC内存布局图可以发现，初始化栈的地址同时也是固件的内存加载地址，因此r1寄存器指向的0x10000就是我们所寻找的固件加载地址。

![
](https://images.seebug.org/content/images/2018/12/fabc2a8e-b89a-4f4d-909a-e2c17586371d.jpg)

#### 2.3 方法三：基于bss区数据初始化代码的特征，计算加载地址

另一个分析固件加载地址的常用方法是，找到bss区域的初始化代码后间接计算出固件加载地址。bss(Block Started by
Symbol)区在VxWorks系统中主要用于存储一些当前未赋值的变量,在系统启动过程中VxWorks会使用 **bzero**
函数对bss区的数据进行清零 。

如下图所示我们可以得知VxWorks固件自身有三个section， **text、 ** _*data_
*以及**bss**这三个部分共同组成了VxWorks固件。

![
](https://images.seebug.org/content/images/2018/12/e88813af-3e00-433d-93c1-2dfbe4f0ec69.jpg)

从下图所示的内存布局中可以看到bss区紧跟着固件的text和data段之后，因此只要我们找到bss区清零的函数，分析出清零函数的结束位置及后将其减去固件文件的大小即可获得固件的内存加载地址。

![
](https://images.seebug.org/content/images/2018/12/330e73a4-15c7-4267-8efa-5f0f17a27826.jpg)

接下来我们再看一下VxWorks中的 **userInit** 函数，从下图可以看到 **usrInit**
除了是系统引导后执行的第一个函数外，在这个函数中还会首先对bss区的数据进行清理。

![
](https://images.seebug.org/content/images/2018/12/be2ccd4d-837b-4603-87dd-35789c816068.jpg)

对 **usrInit** 这个函数进行查看后，可以发现其中有不少的bl跳转函数。根据 **usrInit**
的描述，第一个跳转的函数就是负责初始化BBS区的函数。

![
](https://images.seebug.org/content/images/2018/12/4b9be823-c80f-4804-9190-6a17de280ecd.jpg)

下图是BSS初始化函数的代码，结合PowerPC的寄存器用途可知r3和r4寄存器分别是函数 **sub_18D59C** 的两个参数。r3的值为
**0x339418** , r4的值为 **0x490D2C - 0x339418 = 0x157914** 相当于长度。因此我们可以得知
**0x339418** 就是bss区的起始地址， **0x490D2C** 就是bss区的结束地址。

![
](https://images.seebug.org/content/images/2018/12/40e96b46-88d2-4e05-ba0b-0d1ef81e38e6.jpg)

在得到bss区结束地址后，我们就可以进一步的计算出固件的加载地址，不过使用这个方法有一个前提条件就是提取出的固件文件本身是完整的，如果提取出的固件文件不完整这个方法则会失效。

![
](https://images.seebug.org/content/images/2018/12/5b3e0a92-ba9f-447d-a3c6-d22198961963.jpg)

上面介绍了三种比较常用的VxWorks固件加载地址分析方法，此外还有通过焊接UART接口查看系统引导过程的串口输出等各种其他非常规手段。在分析出固件加载地址后就可以使用新的加载地址重新加载固件进行分析了

![ ](https://images.seebug.org/content/images/2018/12/a7654a8a-04d2-46cc-afd7-0115ad6e84d9.jpg)

下图是Windows下的IDA6.8中重新加载后固件的对比图，Mac下的IDA 在修复了加载地址后还是只能关联识别出很少的函数。

![
](https://images.seebug.org/content/images/2018/12/d5577f55-8f69-4fd2-9890-9d840bb19370.jpg)

### 3\. 利用符号表修复函数名

虽然IDA此时能够正确的识别函数及其调用关系，但依然无法自动识别出函数名，这对固件的分析工作造成了很大的阻碍。
此时可以查看固件在编译时是否编入了符号表，如固件编入了符号表那么我们就可以利用符号表中的内容来修复IDA中所显示的函数名。

通过使用binwalk可以帮助我们辅助分析VxWorks固件中是否编入了符号表，并识别出符号表在固件中的位置。如下图所示binwalk识别出的符号表地址在文件偏移
**0x301E74** 处。

![
](https://images.seebug.org/content/images/2018/12/fe25e304-82ef-4338-a9ef-b2c9df8aaab1.jpg)

如下图所示，VxWorks
5系列的符号表有他独特的格式，他以16个字节为一组数据，前4个字节是0x00，之后是符号名字符串所在的内存地址，后4个字节是符号所在的内存地址，最后4个字节是符号的类型，例如0x500为函数名。

![
](https://images.seebug.org/content/images/2018/12/7ec6d9f9-7393-4ee2-bd45-c13c46c8abcb.jpg)

基于符号表的特征，我们能够轻松的获取到固件中符号表的起始及结束位置。此时我们就可以使用IDA的api来修复函数名，使用加载地址0x00重新加载固件后使用如下图所示的Python脚本即可进行修复。

![
](https://images.seebug.org/content/images/2018/12/613e7443-9b62-4759-94d9-3b3a7fe09c80.jpg)

完成函数名修复后的IDA界面如下图所示，通过修复符号表IDA识别出了8000多个函数。至此VxWorks系统固件的预处理工作就全部完成了，现在我们就可以根据函数名来对一些关键服务的代码进行静态分析了。

![
](https://images.seebug.org/content/images/2018/12/7161c5d4-b9b7-4be5-86b3-ab93be723e1f.jpg)

### 4\. 固件分析

在完成上述的一些预处理工作后，一个固件分析的入手点就是查看例如 **loginUserAdd** 等关键函数的调用关系。如下图所示
**loginUserAdd** 函数的用途是在登录表中添加一个用户，这个账号可以用于登录例如telnet及ftp等服务。

![
](https://images.seebug.org/content/images/2018/12/24db80bb-7210-4040-8b30-a4a5dc63bd38.jpg)

通过分析 **loginUserAdd** 函数的调用，可以看到在 **usrAppInit** 等函数中均调用了 **loginUserAdd** 函数。

![
](https://images.seebug.org/content/images/2018/12/cc766dcb-66c2-402f-b1c0-9ea3ffa63764.jpg)

再进一步查看 **usrAppInit** 函数可以发现在这个函数中所添加的用户及密码哈希。此类方法也是发现后门账号的有效手段之一。

![
](https://images.seebug.org/content/images/2018/12/f0444e1e-443f-4867-9310-a52b07fcbdb0.jpg)

此外还可以关注某些服务的初始化函数，例如在 **usrNetAppInit** 函数中就可以发现许多网络服务的初始化函数调用。

![
](https://images.seebug.org/content/images/2018/12/6bf9d69a-53e0-4bb9-9d44-1ce9e5c7006c.jpg)

至此VxWorks固件分析的常用方法就介绍完毕了，通过使用类似的分析方法，我们也能够在基于VxWorks的其他嵌入式设备的固件中发现一些有趣的信息，下面是其中的两个例子。

![
](https://images.seebug.org/content/images/2018/12/4ad58c49-d9d1-4adf-b68e-7ef1c5941d99.jpg)

![
](https://images.seebug.org/content/images/2018/12/3ac28aa4-993e-44a2-a5d8-f236fd30703e.jpg)

### 5\. 引用

  * [测试附件下载地址](https://download.schneider-electric.com/files?p_enDocType=Firmware+-+Updates&p_File_Name=140NOE77101+For+Non+Unity+Users+V6.4.zip&p_Doc_Ref=140NOE77101+Exec+and+Release+Notes+For+Non+Unity+Users)
  * [Developing PowerPC Embedded Application Binary Interface (EABI) Compliant Programs](http://101.96.10.63/class.ece.iastate.edu/arun/CprE281_F05/lab/labw11a/Labw11a_Files/eabi_app.pdf)
  * [Reference Materials VxWorks for PowerPC](http://www.vxdev.com/docs/vx55man/vxworks/ppc/powerpc.html)
  * [usrConfig](http://www.vxdev.com/docs/vx55man/vxworks/ref/usrConfig.html)
  * [loginLib](http://www.vxdev.com/docs/vx55man/vxworks/ref/loginLib.html#loginUserAdd)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/771/>


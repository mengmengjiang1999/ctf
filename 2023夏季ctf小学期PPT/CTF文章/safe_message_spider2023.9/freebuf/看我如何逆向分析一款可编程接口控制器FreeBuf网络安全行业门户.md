![](https://image.3001.net/images/20200303/1583224584_5e5e1708433a5.jpg!small)

**在AeroCTF中，有一类挑战是以分析可编程接口控制器（PIC）为主要内容的。**

在挑战比赛中，我们会拿到待分析的PIC导出代码，而我们的任务就是需要从中想办法提取出Flag。一般来说，我们所拿到的ROM导出数据为十六进制文件，我们此次拿到的是一个名为“Beginning.hex”的文件，以及下面这个是示意图：

![](https://image.3001.net/images/20200303/1583224592_5e5e17100ecc8.png!small)

下面给出的是Beginning.hex文件的部分代码段：

![](https://image.3001.net/images/20200303/1583224605_5e5e171dc4d83.png!small)

> Beginning.hex：【[
> _文件下载_](https://drive.google.com/file/d/1rY4wX3y5b5qgF2UqhzylmmB-z9E_X7uu/view?usp=sharing)】

经过分析之后，我发现我们可以使用MPLab IDE
v8.92来分析这个内存导出数据。除此之外，我们还可以从文件示意图中了解到待分析的可编程接口控制器的型号：PIC16F877。

![](https://image.3001.net/images/20200303/1583224618_5e5e172ab921c.png!small)

首先，我打算使用静态分析技术来对其进行分析，并从阅读数据表中的数据本身来开始【[
_数据表PDF_](http://ww1.microchip.com/downloads/en/DeviceDoc/30292D.pdf)】：

![](https://image.3001.net/images/20200303/1583224623_5e5e172fa4a48.png!small)

![](https://image.3001.net/images/20200303/1583224630_5e5e17369ddbb.png!small)

从反汇编结果中我们可以看到，其中的大多数指令貌似都写在PORTC和PORTD中：

![](https://image.3001.net/images/20200303/1583224637_5e5e173dc755f.png!small)

movlw（将参数移动至W寄存器）和movwf（将W寄存器移动至参数）结合起来相当于write！

我们可以从上面给出的芯片图中了解到，PortC为RC0-RC7，而PortD则是RD0-RD7。

![](https://image.3001.net/images/20200303/1583224660_5e5e1754f284c.png!small)

这些阵脚可以将输入数据传递给LCD。我们需要获取到数据信号的映射表以及相关联的ACSII字符。在这里，[ _Vaibhav
Jayant_](https://medium.com/u/d35eea5516ec?source=post_page-----e835c0471ebb----------------------)给我提供了很大帮助，我成功模拟出了“Proteus 8
professional”的电路图表。

![](https://image.3001.net/images/20200303/1583224688_5e5e17704a481.png!small)

> 项目文件获取：【[ _点我下载_](https://drive.google.com/file/d/1jYaWD244SEY4cuv4BTGj-> _HRkklgRlju/view?usp=sharing)】

获取到这个电路图之后，那么模拟出整个PIC结构也就不难了。按下“Play按钮”之后，我们就可以看到芯片以动画的形式再给我们播放最终的Flag。

![](https://image.3001.net/images/20200303/1583224701_5e5e177dad3b2.gif!small)

最后，我们成功拿到了隐藏在其中的Flag：AERO{PIC_IS_SIMPLE_Q4A8K1L7}。

 *** 参考来源：[ _anee_](https://anee.me/reversing-programmable-interface-controllers-e835c0471ebb)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


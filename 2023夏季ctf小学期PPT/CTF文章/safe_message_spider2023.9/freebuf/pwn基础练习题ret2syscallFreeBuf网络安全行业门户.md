首先用IDA按F5，将汇编代码生成伪C语言，具体内容如下：

![](https://image.3001.net/images/20221205/1670228897_638daba1e545678c58e03.jpg!small)gets函数作用是读取用户的输入，并且用户输入多长的字符，它就向内存写入多长的数据，那么此处存在溢出的可能，查看二进制文件的保护机制，发现开启NX保护（栈不可执行）。

![](https://image.3001.net/images/20221205/1670228888_638dab987f6b391a65da6.jpg!small)那可执行的还有.text节，那么可以查找gadget片段来试试是否能组成完整的系统调用（即将各个寄存器赋予对应的值，并且定义系统中断号码为0x80,调用函数号为0xb）

![](https://image.3001.net/images/20221205/1670228874_638dab8ad64d6e80ae976.jpg!small)系统调用的定义

如下图：地址0x080bb196的代码片段可以实现为eax寄存器赋值，地址0x0806eb90可为edx、ecx、ebx赋值，并且两个地址对应代码段都有ret，那么就可以将程序的执行流控制并串起来。

![](https://image.3001.net/images/20221205/1670228864_638dab8006c6709025da4.jpg!small)此时还缺int
0x80和字符串“/bin/sh”的地址，可通过如下方式查找（亦可通过IDA找寻）

![](https://image.3001.net/images/20221205/1670228850_638dab7238aef458f517b.jpg!small)  

## 解题思路

当程序执行完了gets函数ret到返回地址，这时我们将返回地址覆盖为pop eax
ret指令的地址，那么eip寄存器保存了我们覆盖后的地址，eip寄存器执行pop
eax，将栈顶的0xb弹出，并赋值给eax，再执行ret，此时0xb已经被弹出栈，那么ret指令则是将pop_edx_ecx_ebx_ret这行指令的地址保存在eip寄存器中，然后弹出该地址，随后执行该行指令，分别将0弹出栈赋值给edx寄存器，0出栈并保存在ecx，将地址0x80be408对应的值：“/bin/sh”保存在ebx，这样就完成了一个系统调用以及获得一个交互的shell。

![](https://image.3001.net/images/20221205/1670228832_638dab60b02431eb28b98.jpg!small)![](https://image.3001.net/images/20221205/1670228818_638dab52707b96f5bd91c.jpg!small)解题脚本和成功后执行命令测试


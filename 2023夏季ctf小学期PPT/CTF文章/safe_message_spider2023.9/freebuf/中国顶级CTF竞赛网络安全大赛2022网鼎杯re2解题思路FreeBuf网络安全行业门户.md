# 一、脱壳

PEID查不出来，用了die，显示是UPX3.96的壳，用了脱壳机，脱不了，只能手动脱壳，拖入x64dbg，F9运行到程序领空，很明显的特征，push：

![](https://image.3001.net/images/20221020/1666261655_63512297c9ebfb025f059.png!small)

无脑使用ESP定律大法，对ESP下硬件访问断点：

![](https://image.3001.net/images/20221020/1666261657_635122995044310c90b46.png!small)

F9运行，在pop处停下：

![](https://image.3001.net/images/20221020/1666261658_6351229a7772b53aeb0c9.png!small)F4运行到下面第一个jmp，F8，进去又是一个jmp，继续F8，到达OEP：

![](https://image.3001.net/images/20221020/1666261659_6351229b5ebdc01694734.png!small)使用x64dbg插件dump：

![](https://image.3001.net/images/20221020/1666261660_6351229ccc2a3eb7e3ef2.png!small)第一步先dump保存，然后第二步，第三步，第四步选择刚才dump保存的程序：

![](https://image.3001.net/images/20221020/1666261661_6351229da83f941262267.png!small)脱壳成功，但是运行一闪而过，这是动态基址搞的鬼，手法很多，有脱壳机有禁用动态基址选项，这里我们直接把程序拖入010Editor修改标志位，改为20即关闭动态基址，保存退出：

![](https://image.3001.net/images/20221020/1666261662_6351229e8746ad78c33d3.png!small)可正常运行，接下来分析算法。

# 二、算法分析

1、进入主函数（很明显是vs写的程序，根据步骤找主函数就行）  
F9进入程序领空，进入第一个call：

![](https://image.3001.net/images/20221020/1666261663_6351229fc6f1d31c8c505.png!small)再进入第二个call：

![](https://image.3001.net/images/20221020/1666261664_635122a0b6c1e86fdf7fc.png!small)找特征码，进入标记的call：

![](https://image.3001.net/images/20221020/1666261665_635122a1b813174be72d0.png!small)进入第四个call：  
![](https://image.3001.net/images/20221020/1666261666_635122a29dd7b9a9ace07.png!small)走过一个跳转，进入主函数：

![](https://image.3001.net/images/20221020/1666261667_635122a393953591ee3b6.png!small)

2.动态调试  
标记的函数是输入flag后第一个call，并且传参进去，所以这里可以跟进去看一看：  
![](https://image.3001.net/images/20221020/1666261668_635122a4822a87d168613.png!small)随便输入一部分数,回车并跟进标记函数：

![](https://image.3001.net/images/20221020/1666261669_635122a56bad34e2ce7b7.png!small)

![](https://image.3001.net/images/20221020/1666261670_635122a6080d6baddbb84.png!small)

从下面可以看到这边传入我们输入flag，是关键函数，跟进去：  
![](https://image.3001.net/images/20221020/1666261670_635122a6e6a6208c054a8.png!small)分析函数：  
![](https://image.3001.net/images/20221020/1666261672_635122a88ff9c2188b057.png!small)可以猜到flag的长度为20，如果不是20，直接到打印错误的地方，继续向下看，下面对字符串进行第一次处理。亦或66，继续看下去，又是一个比较长度函数，之后没什么了，这个函数结束，直到返回主函数：  
![](https://image.3001.net/images/20221020/1666261673_635122a98b0ac172e4f48.png!small)下面就是打印wrong，长度为20会跳过这个打印：  
![](https://image.3001.net/images/20221020/1666261674_635122aa771e465a3ff86.png!small)我们看当前标记的函数，传入参数是我们flag亦或66之后的字符串，绝对关键函数，跟进去，F8一直运行：

![](https://image.3001.net/images/20221020/1666261675_635122ab58a5b0add1f3f.png!small)我们发现又对字符串处理，先+A，再亦或50：

![](https://image.3001.net/images/20221020/1666261676_635122ac3603418e645fd.png!small)继续运行发现关键函数，F8走过直接失败，重新到这个位置，发现传入处理后的第一个字符，跟进去：  
![](https://image.3001.net/images/20221020/1666261677_635122ad294866df2be72.png!small)我们发现一个cmp，和我们字符串第一个字母比较：  
![](https://image.3001.net/images/20221020/1666261678_635122ae43b1a1469ff1b.png!small)查看另一个地址的值：  
![](https://image.3001.net/images/20221020/1666261679_635122af1754e43570abc.png!small)继续跟，会发现直接退出，所以这里是比较函数，直接写脚本：

#include  
int main()  
{  
unsigned int dword_14001D000[20] = {  
0x0000004B, 0x00000048, 0x00000079, 0x00000013, 0x00000045, 0x00000030,
0x0000005C, 0x00000049,  
0x0000005A, 0x00000079, 0x00000013, 0x00000070, 0x0000006D, 0x00000078,
0x00000013, 0x0000006F,  
0x00000048, 0x0000005D, 0x00000064, 0x00000064  
};  
  
char flag[21] = { 0 };  
  
for (int i = 0; i < 20; i++)  
{  
flag[i] = ((dword_14001D000[i] ^ 0x50) - 10) ^ 0x66;  
}  
  
printf(flag);  
  
return 0;  
}

![](https://image.3001.net/images/20221020/1666261679_635122afd3604a468e449.png!small)flag：why_m0dify_pUx_SheLL


  
  

首先来看看C语言溢出小程序

![图片.png](https://image.3001.net/images/20200202/1580645120_5e36bb00e0c57.png!small)

这个程序看着好像是没有任何问题，运行是这样的：

![图片.png](https://image.3001.net/images/20200202/1580645129_5e36bb0962b05.png!small)

我们主要关注这个check函数，首先定义了一个int类型的数组且其中个数为8个，下一行将fun函数地址存入arr[9]中，其实这里我们可以看到定义数组的时候个数也就是8，实际到达的下标是7，所以我们最多能取数组的值为arr[7]，连8都不到，这里我们获取fun函数地址的时候却存到了下标为9的地址，跳了一个下标。首先来了解下数组的存储方式

![图片.png](https://image.3001.net/images/20200202/1580645184_5e36bb4002e1e.png!small)
高地址 低地址

  

这是我简单画的数组存储的堆栈图，数组是使用连续的内存空间来存储的，说白了和局部变量的存储差异不大，我们现在开始分析代码：

![图片.png](https://image.3001.net/images/20200202/1580645225_5e36bb699e7d9.png!small)

现在我们记住ebp和esp的值

![图片.png](https://image.3001.net/images/20200202/1580645232_5e36bb70b79e4.png!small)

现在我们来把这个堆栈图画一下

|  |  |  
---|---|---|---  
|  |  |  
|  |  |  
|  |  |  
|  |  |  
esp| 0019FEF4|  |  
|  |  | 初始内存  
ebp| 0019FF40|  |  
  
这里按F11进入函数体中，call进函数会将它下一行地址压入栈中，然后调到函数体，这时再来看看堆栈的变化：

![图片.png](https://image.3001.net/images/20200202/1580645271_5e36bb97f2f69.png!small)

|  |  |  
---|---|---|---  
|  |  |  
|  |  |  
|  |  |  
esp| 0019FEF0| 0040D75D| 返回地址  
| 0019FEF4|  |  
|  |  | 初始内存  
ebp| 0019FF40|  |  
  
接着往下走，我们看看函数体中的代码：

![图片.png](https://image.3001.net/images/20200202/1580645302_5e36bbb6ce065.png!small)

进入函数后将ebp压入栈中，然后将esp中的值移动到ebp中，之后esp-60h（60h/4h=18h=24）提升栈空间，再来看看此时的堆栈：

esp| 0019FE8C|  |  
---|---|---|---  
| 0019FE90|  |  
| 0019FE94|  |  
| 0019FE98|  |  
| 0019FE9C|  |  
| 0019FEA0|  |  
| 0019FEA4|  | 缓冲区  
| 0019FEA8|  |  
| 0019FEAC|  |  
| 0019FEB0|  |  
| 0019FEB4|  |  
| 0019FEB8|  |  
| 0019FEBC|  |  
| 0019FEC0|  |  
| 0019FE**|  |  
| 0019FEC8|  |  
| 0019FECC|  |  
| 0019FED0|  |  
| 0019FED4|  |  
| 0019FED8|  |  
| 0019FEDC|  |  
| 0019FEE0|  |  
| 0019FEE4|  |  
| 0019FEE8|  |  
ebp| 0019FEEC| 0019FF40| 原ebp值  
| 0019FEF0| 0040D75D| 返回地址  
| 0019FEF4|  |  
|  |  | 初始内存  
| 0019FF40|  |  
  
接下来将ebx，esi，edi依次推入栈中，下面的代码到rep指令是将缓冲区填充为CCCCCCCCCh，再来看看堆栈的变化：

![图片.png](https://image.3001.net/images/20200202/1580645316_5e36bbc4c74f6.png!small)

esp| 0019FE80| edi|  
---|---|---|---  
| 0019FE84| esi| 原寄存器值  
| 0019FE88| ebx|  
| 0019FE8C| CCCCCCCCCh|  
| 0019FE90| CCCCCCCCCh|  
| 0019FE94| CCCCCCCCCh|  
| 0019FE98| CCCCCCCCCh|  
| 0019FE9C| CCCCCCCCCh|  
| 0019FEA0| CCCCCCCCCh|  
| 0019FEA4| CCCCCCCCCh|  
| 0019FEA8| CCCCCCCCCh|  
| 0019FEAC| CCCCCCCCCh|  
| 0019FEB0| CCCCCCCCCh|  
| 0019FEB4| CCCCCCCCCh| 缓冲区  
| 0019FEB8| CCCCCCCCCh|  
| 0019FEBC| CCCCCCCCCh|  
| 0019FEC0| CCCCCCCCCh|  
| 0019FE**| CCCCCCCCCh|  
| 0019FEC8| CCCCCCCCCh|  
| 0019FECC| CCCCCCCCCh|  
| 0019FED0| CCCCCCCCCh|  
| 0019FED4| CCCCCCCCCh|  
| 0019FED8| CCCCCCCCCh|  
| 0019FEDC| CCCCCCCCCh|  
| 0019FEE0| CCCCCCCCCh|  
| 0019FEE4| CCCCCCCCCh|  
| 0019FEE8| CCCCCCCCCh|  
ebp| 0019FEEC| 0019FF40| 原ebp值  
| 0019FEF0| 0040D75D| 返回地址  
| 0019FEF4|  |  
|  |  | 初始内存  
| 0019FF40|  |  
  
接着往下走![图片.png](https://image.3001.net/images/20200202/1580645347_5e36bbe3edbac.png!small)

这里是将数组存到缓冲区中，从低地址向高地址存储，20h/4h=8h=8从esp的位置向上数八格就是存储1的位置，依次存储下来，再来看看栈中的变化：

esp| 0019FE80| edi|  
---|---|---|---  
| 0019FE84| esi| 原寄存器值  
| 0019FE88| ebx|  
| 0019FE8C| CCCCCCCCCh|  
| 0019FE90| CCCCCCCCCh|  
| 0019FE94| CCCCCCCCCh|  
| 0019FE98| CCCCCCCCCh|  
| 0019FE9C| CCCCCCCCCh|  
| 0019FEA0| CCCCCCCCCh|  
| 0019FEA4| CCCCCCCCCh|  
| 0019FEA8| CCCCCCCCCh|  
| 0019FEAC| CCCCCCCCCh|  
| 0019FEB0| CCCCCCCCCh|  
| 0019FEB4| CCCCCCCCCh| 缓冲区  
| 0019FEB8| CCCCCCCCCh|  
| 0019FEBC| CCCCCCCCCh|  
| 0019FEC0| CCCCCCCCCh|  
| 0019FE**| CCCCCCCCCh|  
| 0019FEC8| CCCCCCCCCh|  
| 0019FECC| 1|  
| 0019FED0| 2|  
| 0019FED4| 3|  
| 0019FED8| 4|  
| 0019FEDC| 5|  
| 0019FEE0| 6|  
| 0019FEE4| 7|  
| 0019FEE8| 8|  
ebp| 0019FEEC| 0019FF40| 原ebp值  
| 0019FEF0| 0040D75D| 返回地址  
| 0019FEF4|  |  
|  |  | 初始内存  
| 0019FF40|  |  
  
![图片.png](https://image.3001.net/images/20200202/1580645358_5e36bbee9ba92.png!small)

![图片.png](https://image.3001.net/images/20200202/1580645364_5e36bbf4e7e79.png!small)

这里是取fun的地址出来并转换为int类型，然后存入数组下标为9的地方，我们看看ebp+4这个地址执行前后的变化

执行前

esp| 0019FE80| edi|  
---|---|---|---  
| 0019FE84| esi| 原寄存器值  
| 0019FE88| ebx|  
| 0019FE8C| CCCCCCCCCh|  
| 0019FE90| CCCCCCCCCh|  
| 0019FE94| CCCCCCCCCh|  
| 0019FE98| CCCCCCCCCh|  
| 0019FE9C| CCCCCCCCCh|  
| 0019FEA0| CCCCCCCCCh|  
| 0019FEA4| CCCCCCCCCh|  
| 0019FEA8| CCCCCCCCCh|  
| 0019FEAC| CCCCCCCCCh|  
| 0019FEB0| CCCCCCCCCh|  
| 0019FEB4| CCCCCCCCCh| 缓冲区  
| 0019FEB8| CCCCCCCCCh|  
| 0019FEBC| CCCCCCCCCh|  
| 0019FEC0| CCCCCCCCCh|  
| 0019FE**| CCCCCCCCCh|  
| 0019FEC8| CCCCCCCCCh|  
| 0019FECC| 1|  
| 0019FED0| 2|  
| 0019FED4| 3|  
| 0019FED8| 4|  
| 0019FEDC| 5|  
| 0019FEE0| 6|  
| 0019FEE4| 7|  
| 0019FEE8| 8|  
ebp| 0019FEEC| 0019FF40| 原ebp值  
| 0019FEF0| 0040D75D| 返回地址  
| 0019FEF4|  |  
|  |  | 初始内存  
| 0019FF40|  |  
  
执行后

esp| 0019FE80| edi|  
---|---|---|---  
| 0019FE84| esi| 原寄存器值  
| 0019FE88| ebx|  
| 0019FE8C| CCCCCCCCCh|  
| 0019FE90| CCCCCCCCCh|  
| 0019FE94| CCCCCCCCCh|  
| 0019FE98| CCCCCCCCCh|  
| 0019FE9C| CCCCCCCCCh|  
| 0019FEA0| CCCCCCCCCh|  
| 0019FEA4| CCCCCCCCCh|  
| 0019FEA8| CCCCCCCCCh|  
| 0019FEAC| CCCCCCCCCh|  
| 0019FEB0| CCCCCCCCCh|  
| 0019FEB4| CCCCCCCCCh| 缓冲区  
| 0019FEB8| CCCCCCCCCh|  
| 0019FEBC| CCCCCCCCCh|  
| 0019FEC0| CCCCCCCCCh|  
| 0019FE**| CCCCCCCCCh|  
| 0019FEC8| CCCCCCCCCh|  
| 0019FECC| 1|  
| 0019FED0| 2|  
| 0019FED4| 3|  
| 0019FED8| 4|  
| 0019FEDC| 5|  
| 0019FEE0| 6|  
| 0019FEE4| 7|  
| 0019FEE8| 8|  
ebp| 0019FEEC| 0019FF40| 原ebp值  
| 0019FEF0| 00401014| 返回地址  
| 0019FEF4|  |  
|  |  | 初始内存  
| 0019FF40|  |  
  
![图片.png](https://image.3001.net/images/20200202/1580645375_5e36bbffe2904.png!small)

经过这个对比之后，ebp+4刚好是这个存储返回地址的地方，我们继续往下走

![图片.png](https://image.3001.net/images/20200202/1580645381_5e36bc058d3bf.png!small)

异或eax之后，依次取出edi,esi,ebx，然后将ebp的值移动到esp中，随后取出ebp，再来看看堆栈变化：

![图片.png](https://image.3001.net/images/20200202/1580645391_5e36bc0fc3d4d.png!small)

| 0019FE8C| CCCCCCCCCh|  
---|---|---|---  
| 0019FE90| CCCCCCCCCh|  
| 0019FE94| CCCCCCCCCh|  
| 0019FE98| CCCCCCCCCh|  
| 0019FE9C| CCCCCCCCCh|  
| 0019FEA0| CCCCCCCCCh|  
| 0019FEA4| CCCCCCCCCh|  
| 0019FEA8| CCCCCCCCCh|  
| 0019FEAC| CCCCCCCCCh|  
| 0019FEB0| CCCCCCCCCh|  
| 0019FEB4| CCCCCCCCCh| 缓冲区  
| 0019FEB8| CCCCCCCCCh|  
| 0019FEBC| CCCCCCCCCh|  
| 0019FEC0| CCCCCCCCCh|  
| 0019FE**| CCCCCCCCCh|  
| 0019FEC8| CCCCCCCCCh|  
| 0019FECC| 1|  
| 0019FED0| 2|  
| 0019FED4| 3|  
| 0019FED8| 4|  
| 0019FEDC| 5|  
| 0019FEE0| 6|  
| 0019FEE4| 7|  
| 0019FEE8| 8|  
| 0019FEEC|  | 原ebp值  
esp| 0019FEF0| 00401014| 返回地址  
| 0019FEF4|  |  
|  |  | 初始内存  
ebp| 0019FF40|  |  
  
上面的操作是使堆栈平衡，接着来看

![图片.png](https://image.3001.net/images/20200202/1580645400_5e36bc18a2f13.png!small)

接着执行了一个ret，ret的操作相当于push eip，F11一下，看看eip

![图片.png](https://image.3001.net/images/20200202/1580645411_5e36bc2377d57.png!small)![图片.png](https://image.3001.net/images/20200202/1580645415_5e36bc279361e.png!small)

| 0019FE8C| CCCCCCCCCh|  
---|---|---|---  
| 0019FE90| CCCCCCCCCh|  
| 0019FE94| CCCCCCCCCh|  
| 0019FE98| CCCCCCCCCh|  
| 0019FE9C| CCCCCCCCCh|  
| 0019FEA0| CCCCCCCCCh|  
| 0019FEA4| CCCCCCCCCh|  
| 0019FEA8| CCCCCCCCCh|  
| 0019FEAC| CCCCCCCCCh|  
| 0019FEB0| CCCCCCCCCh|  
| 0019FEB4| CCCCCCCCCh| 缓冲区  
| 0019FEB8| CCCCCCCCCh|  
| 0019FEBC| CCCCCCCCCh|  
| 0019FEC0| CCCCCCCCCh|  
| 0019FE**| CCCCCCCCCh|  
| 0019FEC8| CCCCCCCCCh|  
| 0019FECC| 1|  
| 0019FED0| 2|  
| 0019FED4| 3|  
| 0019FED8| 4|  
| 0019FEDC| 5|  
| 0019FEE0| 6|  
| 0019FEE4| 7|  
| 0019FEE8| 8|  
| 0019FEEC|  | 原ebp值  
| 0019FEF0|  | 返回地址  
esp| 0019FEF4|  |  
|  |  | 初始内存  
ebp| 0019FF40|  |  
  
就这样进入了fun函数

![图片.png](https://image.3001.net/images/20200202/1580645426_5e36bc32a012d.png!small)![图片.png](https://image.3001.net/images/20200202/1580645434_5e36bc3a84865.png!small)

本次分析就是分析缓冲区都溢出了为何还能执行fun函数，到这里我们可以知道溢出之后覆盖掉了程序的返回地址，所以导致程序进入了fun函数中。溢出并不可怕，可怕的是不会调试啊！


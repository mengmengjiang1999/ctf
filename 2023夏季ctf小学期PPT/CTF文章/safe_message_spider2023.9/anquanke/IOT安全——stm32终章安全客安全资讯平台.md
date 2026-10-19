# IOT安全——stm32终章

阅读量 **172568**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-04 10:00:55

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

上一篇中我们解释了stm32的时钟与中断机制，这篇文章中我们将进一步探究dma、usart、tim的原理，并最终完整的复现题目。

对于诸如usb、看门狗等内容大家可以进行类比，为了节约篇幅，我就不再文章中一一进行学习了。希望大家在这篇文章后能够自己动手完整复现题目。

## 时常要用到的定时器

TIM，定时器，最主要的功能就是定时，这么一说你可能会觉得它用处不是很大，但实际上，TIM绝对是stm32最关键的部件之一，举个最简单的栗子，现在我们希望能够输出pwm脉冲进而控制某个外接的工业设备（对于工业设备来说，pwm控制是最最常见的一种形式，而stm32也完全可以在工业领域使用），或者说我们想每秒采集外部输入的电平进而计算出波形或是推算采集信息，都得用到TIM来定时来起到”有序“的作用，否则我们没有规律没有时钟收到的数据就是一堆乱码。在usart发送数据时，我们也可以采取定时发送的形式来实现一些功能，因此，TIM是个不得不学的重点。

在我们所学的stm32f103c8t6中，有8个定时器，其中：

  * TIM1为高级定时器，16 位的可以向上/下计数的定时器，可以定时，可以输出比较，可以输入捕捉，还可以有三相电机互补输出信号，每个定时器有 8 个外部 IO，这个定时器在我们现在的学习中并不会使用，因此我们不做讲解
  * TIM6 和 TIM7为基本寄存器，16 位的只能向上计数的定时器，只能定时，没有外部 IO，其实是简单版的通用定时器。
  * TIM2、3、4、5为通用定时器，16 位的可以向上/下计数的定时器，可以定时，可以输出比较，可以输入捕捉，每个定时器有四个外部 IO

TIM主要有以下几个重点组成：

  * 时钟，基本定时器的时钟只能来自内部时钟，其他则没有这个限制，从上一篇文章中时钟树的图我们可以看到它有APB预分频得到，最终叫做TIMxCLK，有些地方也用CK_CLK，定义上有所不同，但实际上是一样的。如果APB1 预分频系数等于 1，则频率不变，否则频率乘以 2，通过这个规则我们即可计算出PCLK的时钟频率。这是非常重要的点，大家要留意。
  * PSC，即预分频器可，以将计数器的时钟频率按 1 到 65536 之间的任意值分频。它是基于一 个(在 TIMx_PSC 寄存器中的)16 位寄存器控制的 16 位计数器，我们需要根据我们想要的定时来计算出相应的PSC的值。因为这个寄存器带有缓冲器，它能够在工作时被改变。新的预分频器的参数在下一次更新事件到来时被采用。
  * CNT ，即计数器是一个 16 位的计数器，只能向上计数，最大为 65535。当计数达到自动重装载寄存器的时候产生更新事件，并清零从头开始计数。计数器的最终的时钟频率还需要经过PSC预分频计算才能得，公式为CK_CNT=TIMxCLK/(PSC+1)
  * ARR，即自动重装载寄存器，保存着计数器的最大值，如果计数器的值达到最大值，会触发溢出中断

我们如果要进行定时的话，依靠的主要就是TIMx_PSC 和
TIMx_ARR两个寄存器，也就是上面说的PSC预分频和ARR，这俩是最重要的部件。我们要设置的定时时间就等于中断周期乘以中断的次数，说明是中断周期？就是上面所说的CNT计数到达ARR设置的最大值所需要的时间，一个时钟他会加一次，也就是说最终加的次数
_时钟一次的时间就得到了结果，CNT计数的周期即1/（TIMxCLK/(PSC+1)），则产生一次中断的时间即1/（TIM_CLK_ ARR）。

假设我们定义一个一秒的定时器，我们设置TIMx_ARR寄存器值为 9999，即CNT计数每次为10000，根据公式即可得知，只要我们把周期设置为
100us即可得到刚好 1s的定时周期，在根据上述计算频率的公式就可以知道，只需要设置 TIMx_PSC寄存器值为90MHz使得 CK_CNT 输出为
100us即可满足我们的需要。

这一段计算有些绕，特别是涉及到频率、时间、周期的转换，让人有些头疼，大家根据自己的需要灵活掌握即可，不需要一口吃成大胖子。

对于TIM来说，配置工作比USART简单很多：

  * 配置相关的时钟
  * 初始化TIMx，主要是TIMx_ARR和TIMx_PSC的值，还要设置TIMx_DIER允许更新中断
  * 使能TIMx

    
    
    TIM_TimeBaseStructure.TIM_Prescaler =9000;     // 预分频器,设置预分频 
    TIM_TimeBaseStructure.TIM_Period  = 9999;        //定时器周期，设置在下一个更新事件装入活动的自动重装载寄存器周期的值
    TIM_TimeBaseStructure.TIM_ClockDivision = 0;    //设置时钟分频
    TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;  //计数模式，在这里是TIM使用向上计数模式
    TIM_TimeBaseInit(TIM3, &TIM_TimeBaseStructure); //初始化
    TIM_ITConfig(TIM3, TIM_IT_Update,ENABLE);
    

  * 配置相关的中断

最后编写中断服务函数即可

    
    
     void BASIC_TIM_IRQHandler (void)
     {
     if ( TIM_GetITStatus( BASIC_TIM, TIM_IT_Update) != RESET ) { //判断TIM是否准备就绪
             time++;   //计数++
             TIM_ClearITPendingBit(BASIC_TIM , TIM_FLAG_Update); //清空等待
     }
     }
    

当然并不止这一种，TIM1高级定时器还有其他许多功能，大家可以根据需要自行学习，只要掌握了设备的基本初始化流程与中断机制，这些设备的使用其实都是大同小异的。

## 课本中经常出现的DMA

说起DMA，很多人第一反应就是万恶的《计算机组成原理》中，和程序中断方式并列的“难点”，课本上铺天盖地给了一堆概念性的知识，但最后也没个实例说明DMA到底是咋个在现代计算机上打下一片天的，其实DMA作为一项优秀的技术，早早就确定了它的王者地位，在stm32中，DMA更是我们学习绕不开的坎，usart也是DMA的”忠实用户“。

DMA说白了就是雇来专门进行数据传输的小弟，让cpu这位大老板不用去干搬运数据的苦活，把精力放在计算、控制等工作上。本质上进行的工作是某片存储区域的数据转移到另一篇存储区域（主要是外设与内存之间），而工作流程也非常简单：

  * dma request，发起dma请求交给dma控制器，同意即进入传输
  * dma 数据传输，传输结束进入下一步
  * 发出中断请求给cpu，进行下一步处理。

这是课本上给我们的基本流程，在具体的应用上还有有些不同，比如中断的触发不仅仅是在数据传输完毕，之后我们会提到DMA多样的中断处理。

![](https://i.loli.net/2021/02/15/he7OoGlqSyiLjKN.png)

先来看看stm32中dma的框图，可以看到有一个dma设备（我们使用的是stm32f103c8t6只有一个dma设备，有些有两个，分析方法相同），它属于AHB下面的slave，上一篇我们说过AHB用来挂载的都是高速设备，可见dma速度之快可以与内存、cpu同台竞技了。接着我们注意到它有7个channel经过一个选择器，这和中断类似，同样是根据优先级决定哪个通道先进行处理。其余还有一些组成部件，但是不涉及到核心原理，就不再赘述了。

![](https://i.loli.net/2021/02/17/29pYsbHqIxJkCzV.png)

各个通道都已经分配好了任务，我们的USART1主要是通道4和通道5负责，除了优先级外，通道还有如下几个作用：

  * 支持循环的缓冲区管理
  * 控制数据宽度，支持字节、半字、全字
  * 触发事件，有dma传输一半、dma传输完成、dma传输失败三种事件

关键来了，控制数据宽度，在题目中我们不难得到flag的字符串，但是怎么交都不对，实际上就和数据的传输宽度有关，因为数据宽度的限制，高位部分就被舍弃了，固我们的flag发生了变化，在题目中我们就需要找到控制数据宽度的寄存器，进而确定数据宽度，当然，实际比赛我们与其耗费时间去找dma的寄存器，不如干脆都试试，反正就三种情况。

对于dma的编程来说，由于存在两方设备，所以需要遵循一定的逻辑：

  * 配置相关的时钟（参考上一篇文章）
  * 需要设置目的地址和源地址，传输的地址存放在DMA_CPARx （为外设地址）与DMA_CMARx（为存储器地址）
  * 需要设置大小与自增，每次传输完数据后，目的和源地址自增，而自增的次数就是设置的大小，进而实现数据的传输，设置DMA_CCRx寄存器中的PINC和MINC标志位，DMA_CNDTRx寄存器中设置要传输的数据量
  * 在DMA_CCRx寄存器的PL来设置优先级
  * 选择dma的模式，DMA_CCRx寄存器中设置数据传输的方向、循环模式、数据宽度 
    * 一次性模式，数据传输完时会触发中断，在中断处理函数中我们失能对应的dma通道
    * 循环模式，即数据发送完毕后回复最初的状态，就可以继续发送了，设置DMA_CCRx寄存器中的CIRC
    * 内存模式，即不从外设获取数据，单纯内存到内存传输，设置DMA_CCRx寄存器中的MEM2MEM位
  * 使能通道，DMA_CCRx寄存器的ENABLE位

    
    
    void DMA_Mem2Mem_Config(void)
    {
            DMA_InitTypeDef DMA_InitStructure;
    
            //设置DMA发送的原地址
            DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)SendBuff;
            //设置DMA发送的目的地址
            DMA_InitStructure.DMA_PeripheralBaseAddr =  (uint32_t)ReceiveBuff;       
            //设置发送的方向   
            DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralDST;    
            //设置发送的大小  
            DMA_InitStructure.DMA_BufferSize = SENDBUFF_SIZE;
            //目的地址自增    
            DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Enable; 
            //源地址自增
            DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;    
            //设置接收的单位大小    
            DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte;
            //设置发送的单位大小
            DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_Byte;     
            //设置dma模式
            DMA_InitStructure.DMA_Mode = DMA_Mode_Normal ;
            //设置dma的优先级   
            DMA_InitStructure.DMA_Priority = DMA_Priority_Medium;  
            //使能
            DMA_InitStructure.DMA_M2M = DMA_M2M_Enable;
            //初始化通道       
            DMA_Init(DMA1_Channel4, &DMA_InitStructure);        
            DMA_Cmd (DMA1_Channel4,DISABLE); 
    }
    

另外，我们知道dma最后一步需要借助中断来触发对应的事件，所以配置dma还需要配置相应的NVIC，这部分生成的代码较为简单，我就不再一一说明了。

最终我们只需要编写中断服务函数即可完成dma的使用。

## 简单易学的usart

说起数据传输，似乎很简单，就是一人收一人发，TX表示的就是数据发送，RX表示数据接收，这俩看上去花里胡哨，实际上就是我们第一篇中说过的引脚”进化“来了，我们在stm32cube中设置好了usart开启，软件就会帮我们搞定，最终即可轻松利用中断处理函数来编写代码。

看上去不难，但实际上需要协调的地方很多，用起来简单，学明白还是需要时间的。标准的usart全双工的异步串行通信（当然有标准的就有不标准的），NRZ
标准格式，还需要有同步的波特率，我们一个个来解释这些概念

  * 全双工即收发双方可以同时发送数据，半双工是可以一边发完另一边发，单工就是永远只能有一边发送
  * 串行就是数据像是穿成一根线，一个一个的发送，并行就是好几根线，一块发送
  * 异步是双方时钟不同，你玩你的我玩我的，同步则是双方严格按照时钟
  * NRZ标准格式即Non-return-to-zero Code，就是传输每一位数据都不用归零，比如刚传输一个1，那么之后就一直是1，直到下一个传输为0，除了NRZ，还有RZ格式，即每次传输完一个数据，就变回0，等待下一次传输。这两种方式各有利弊，RZ最突出的特点就是自同步性，它不需要其他时钟就可以实现同步，因为接收者只需要接收归零状态之后的即可，缺点也显而易见——带宽浪费了，而NRZ则恰好相反，它没有了自同步性，但是对于带宽的利用大大增加了。
  * 波特率是每秒钟传输的数据位数，说白了就是双方一个同步的约定，一旦破了这个约定，数据还是那些数据，但就会出现乱码等现象。

看完了这些我们再看一下USART的格式

![](https://i.loli.net/2021/02/17/gYIDxGyuBF4cMl5.png)

可以看到它以frame来组织数据，也就是帧。每一个数据帧以start
bit为起始，是一个低电平信号，如果开始就是一个高电平信号就直接说明这个帧不是数据帧，接着就是数据位，一般是低位在前，高位在后，然后是奇偶校验位，奇校验就是1出现次数为奇数次，偶校验就是1出现的次数为偶数次，这些都非常简单。

最后是停止位，这里的停止位非常有讲究，它的主要功能其实是为了消除累积误差的，我们在上一篇文章就知道了，多个设备都是在以自己的时钟频率运行的，虽说有各种各样的机制，但还是免不了会出现轻微的误差现象，这时，有一个停止位，各设备可以在接收停止位时进行时钟的校正同步，由此可知，停止位越多，各设备之间的”误差“就可以越大，但是同样会导致带宽的浪费。

usart支持三种方式的传输：

  * 轮询式，即cpu不断的查询io设备，有请求就处理，效率低到可怕，对应的库函数为HAL_UART_Transmit()和HAL_UART_Receive()，由于cpu不可能一直在这等待发送，它采取了超时管理的机制。
  * 中断式，即io设备完成操作时发送请求给cpu，调用中断处理函数进而处理，对应的库函数为HAL_UART_Transmit_IT()和HAL_UART_Receive_IT()
  * dma式，即我们上面详细说明的方式，也是效率最高的方式，对应的库函数为HAL_UART_Transmit_DMA()和HAL_UART_Receive_DMA()

usart同样利用中断来触发事件，包括：

  * HAL_UART_TxHalfCpltCallback()，发送一半数据触发
  * HAL_UART_TxCpltCallback()，发送全部数据触发
  * HAL_UART_RxHalfCpltCallback()，接收一般数据触发
  * HAL_UART_RxCpltCallback()，接收全部数据后触发
  * HAL_UART_ErrorCallback()，传输出现错误触发

了解了上面的基础知识，我们就可以开始梳理usart的编写逻辑了

  * 配置相关的时钟（包括设备、对应的IO引脚，参考上一篇文章）
  * 配置TX、RX并使能
  * 配置波特率
  * usart设备使能
  * 配置usart相关的中断

    
    
    //配置波特率  
    USART_InitStructure.USART_BaudRate = 115200;  
    //配置数据宽度
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;  
    //配置停止位宽度
    USART_InitStructure.USART_StopBits = USART_StopBits_1;  
    USART_InitStructure.USART_Parity = USART_Parity_No;  
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;  
    USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
    

最后编写中断函数进行数据发送

    
    
    void USART3_IRQHandler(void)  
    {  
      static int tx_index = 0;  
      static int rx_index = 0;  
      //判断usart发送是否准备就绪
      if (USART_GetITStatus(USART3, USART_IT_TXE) != RESET) 
      {  
        //发送数据
        USART_SendData(USART3, String[tx_index++]);  
        if (tx_index >= (sizeof(String) - 1))  
          tx_index = 0;  
      }  
      //判断usart接收是否准备就绪
      if (USART_GetITStatus(USART3, USART_IT_RXNE) != RESET) 
      {  
        String[rx_index++] = USART_ReceiveData(USART3);  
    
        if (rx_index >= (sizeof(String) - 1))  
          rx_index = 0;  
      }  
    }
    

我们还可以重定向printf函数来实现printf利用usart发送数据，我们知道，printf是fputc的进一步封装，因此我们重写相应函数即可

    
    
    int fputc(int ch,FILE *f)
    {
        USART_GetFlagStatus(USART1, USART_FLAG_TC)///判断usart是否准备就绪
        //发送字符
        USART_SendData(USART1, (unsigned char) ch);
        //等待发送完成
        while(USART_GetFlagStatus(USART1,USART_FLAG_TC)!=SET);
    
        return(ch);
    }
    

## 总结

到这里我们已经可以完整复现整个题目的流程了，相信大家也完全可以解答一开始我在[《IOT安全—— _stm32_
从做题到复现》](https://www.anquanke.com/post/id/229321)中提出的几个问题，也完全可以自己出一些简单的stm32固件题目。

作为一个物联网安全的小白，第一次接触这类题目真的是会感觉到异常的”难“，不仅仅是对题目、知识点的陌生，更多的是对于硬件设备、底层代码编写的恐惧，希望大家在这几篇文章后能多少得到一些物联网学习的知识，也能借助这些知识举一反三，慢慢走出这份恐惧，在未来越来越多的物联网安全问题中更快进步。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Asa9ao** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231586](/post/id/231586)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [IoT](/tag/IoT)
  * [物联网安全](/tag/物联网安全)

 **+1** __1赞

 __收藏

![](https://p1.ssl.qhimg.com/t01898082a58ca4c715.png) Asa9ao

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


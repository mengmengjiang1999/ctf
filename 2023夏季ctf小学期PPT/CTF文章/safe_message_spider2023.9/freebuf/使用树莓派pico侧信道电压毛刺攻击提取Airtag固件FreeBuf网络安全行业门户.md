## 项目概述

本项目为电压故障注入攻击apple airtag。参考了众多开源项目，主要特点如下：

1.1 攻击硬件便宜，成本在100人民币左右

1.2 使用树莓派pico，支持python

1.3 对airtag实现免焊接，只需要对好位置

1.4 项目开源地址：https://github.com/Question-h/side-channel-lab.git

## 电压故障注入

​
关于电压故障注入，个人的理解就是通过人为制造不稳定的供电电压使得芯片在执行代码的时候“跑飞”。本次项目使用这个原理攻击airtag的蓝牙芯片nrf52832，使其在启动检测安全启动的时候出错，从而绕过APPROTECT的保护机制，使得我们能通过jtag对芯片进行操作。

关于更多的知识大家可以看下海栗大佬的视频：https://live.freebuf.com/detail/2354a4f59d764b1c954b9794d8d151ca

B站也有很多牛逼的大神免费分享过好多视频：

https://www.bilibili.com/video/BV1Eg4y1B7c7?share_source=copy_web

https://www.bilibili.com/video/BV1PT4y137cG?share_source=copy_web

有兴趣的小伙伴可以自行学习，因为本次主要讲的是这个开源的攻击板子所以上面的入门就不做过多的概述了，主要本人对这些也是刚入门。

## 攻击板的原理

### airtag 供电控制

![](https://image.3001.net/images/20220323/1648027921_623ae9110138813eb3ef3.png!small)  
使用pico的gpio22 对airtag上电进行控制，测试过程需要多次重新上电。

### 毛刺攻击

![](https://image.3001.net/images/20220323/1648027937_623ae92164f4587df9b0b.png!small)

电压毛刺攻击主要原理就是瞬间将电压拉低，使得程序出现错误。这部分电路参考了chipwhisperer，这部分原理很简单，gpio口控制Q1
通断，使得电压瞬间降低，注意下不能长时间导通，轻则烧毁Q1，重则烧毁设备。这次攻击并未使用Q2，Q2的功率更大这里使用Q1 就可以了。

## 板子上其他功能说明

### u1 spiflash读取

这次设计的攻击板除了电压毛刺注入功能外还设计了U1芯片外置spiflash读取的部分电路，这部分电路如下

  

![](https://image.3001.net/images/20220323/1648027951_623ae92f15f2048f5acc4.png!small)![](https://image.3001.net/images/20220323/1648027992_623ae95863a07a54446f9.png!small)

这里为啥会给spiflash一个独立的供电控制功能呢，主要是我们在测试的过程中发现，给整个airtag供电一段时间后，spiflash的供电就断开了，应该是处于低功耗考虑。如果我们使用airtag的供电读取spiflash，会出现读取到一半就无响应，所以这边使用了一个独立供电来给spiflash供电。也是可以通过pico的gpio进行控制。

### swd调试器功能

![](https://image.3001.net/images/20220323/1648027969_623ae941cc8f784b6a3dc.png!small)

pico是可以作为jtag或者swd调试器的，所以这里把nrf52的swd功能连接到pico对应的引脚，使用r5
r6两个电阻来做功能选择，当然如果你有jtag调试器，我们推荐你使用单独的jtag调试器。

### 测试点

![](https://image.3001.net/images/20220323/1648028010_623ae96a14b700ae01b3c.png!small)

R10是泄压电阻，在airtag上有好多大电容，加上这个电阻能在断电后不需要等待太长时间就能立马上电重新攻击。

还有三个测试点，分别是3v的vcc，1.8v的nrf52供电，vcore是nrf的核心电压测试点。其中1.8v和vcore都接入到了pico的adc上，可以通过pico的adc拿到电压曲线图，如下图。

![](https://image.3001.net/images/20220323/1648028021_623ae9750d48c450c9533.png!small)

# 硬件连接

airtag拆解，可以使用100度左右加热20分钟，用金属吉他拨片就能撬开了。

![](https://image.3001.net/images/20220323/1648028181_623aea15a7f682044a1b7.png!small)

我这个没加热够时间所以还是断一个脚

![](https://image.3001.net/images/20220323/1648028209_623aea3130ef78e3c69c3.png!small)

攻击板子焊接好后，底部是pogo的探针。（我这里是老板子的照片大家根据需要把探针焊接好）

![](https://image.3001.net/images/20220323/1648028231_623aea47af62c4f8622d5.png!small)

pogopin的参数如下，某宝有卖

![](https://image.3001.net/images/20220323/1648037644_623b0f0ce7b4545b74372.png!small)

就和下图一样 用一片乐高的底板垫上一张抽纸，把airtag放上去，可以拆外壳也可以不拆外壳，都能完美接触好的。

![](https://image.3001.net/images/20220323/1648028262_623aea668ab4b0496b78e.png!small)

中间的洞是用来对位的。用镊子慢慢推对准就行。

![](https://image.3001.net/images/20220323/1648028283_623aea7b7a619bebe3129.png!small)

对好了之后用万用表的二极管档打下阻值，看下是否管脚都接触良好。测量的时候pico不要装。

![](https://image.3001.net/images/20220323/1648028300_623aea8ccaec7f0d0320a.png!small)

## 代码

目前只写了adc和故障注入曲线采集代码，其他都没写（其实是懒）

### adc曲线采集

    
    
    from machine import Pin, PWM, Signal,ADC
    import utime
    import time
    import _thread
    trigger=Pin(0,Pin.OUT)
    led=Pin(25,Pin.OUT)
    trigger.value(0)
    #核心电压adc
    vcore=ADC(2)
    #1.8v电压adc
    vcc18=ADC(1)
    #3.3v供电开关
    power33=Pin(22,Pin.OUT)
    
    vcore_list=[]
    vcc18_list=[]
    def adc_thread(times):
    
        global vcore_list
        global vcc18_list
        vcore_list.clear()
        vcc18_list.clear()
        #while START_ADC:
        for i in range(1,times):
            vc=vcore.read_u16()
            v1=vcc18.read_u16()
            vcore_list.append(vc)
            vcc18_list.append(v1)
    
    cmd=''
    
    while True:
        cmd=input()
        if cmd=="START":
            power33.value(1)
            adc_thread(500)
            print(len(vcore_list),len(vcc18_list))
    
        if cmd == "STOP":
            power33.value(0)
           
        if cmd == "ADC":
            for i in  range(0,len(vcore_list)):
                print(3.3*vcc18_list[i]/65535,3.3*vcore_list[i]/65535)
    

效果如下图，分别监控了1.8v的电压曲线和1v左右的核心电压曲线，橙色的曲线有一个下落，攻击点其实就在这附近

![](https://image.3001.net/images/20220323/1648028034_623ae982d00c8ecd715d4.png!small)

### 故障注入

    
    
    from machine import Pin, PWM, Signal,ADC
    import utime
    import time
    import _thread
    trigger=Pin(0,Pin.OUT)
    led=Pin(25,Pin.OUT)
    trigger.value(0)
    #核心电压adc
    vcore=ADC(2)
    #1.8v电压adc
    vcc18=ADC(1)
    #3.3v供电开关
    power33=Pin(22,Pin.OUT)
    #核心电压glitch攻击
    GLITCH = Pin(20,Pin.OUT)
    
    lock = _thread.allocate_lock()
    
    START_ADC = False
    glitch_times=1
    vcore_list=[]
    vcc18_list=[]
    def glitch_thread(times,glitchdelay,glitchtime):    
        print('start')
        led.value(0)
        power33.value(1)
        #while True:
        for i in range(0,100):
            vc=vcore.read_u16()
            if vc >17000 and times >0:
                GLITCH.value(1)
                #utime.sleep_us(10)
                vc=vcore.read_u16()
                GLITCH.value(0)
                times=times-1
            print(times,3.3*vc/65535)
        
    
    
    
    while True:
        cmd=input()
        if cmd=="START":
            glitch_thread(1,2,3)
        if cmd == "STOP":
            print("stop")
            power33.value(0)
            
    
    
    

![](https://image.3001.net/images/20220323/1648028065_623ae9a10f3328104fcef.png!small)

![](https://image.3001.net/images/20220323/1648028075_623ae9abd17fffa40f3cd.png!small)这里持续拉低时间大于50ns，原因是因为pico使用python对gpio操作是有延时的，经过验证这个延时不影响攻击效果，如果对这个有要求可以使用pico的pio对着进行操作

![](https://image.3001.net/images/20220323/1648028085_623ae9b55974d2547c17c.png!small)

  

# 攻击流程

![](https://image.3001.net/images/20220323/1648036852_623b0bf4dc6e09ca05f19.png!small)

攻击过程主要是通过串口给攻击板下达攻击参数，然后开始攻击，攻击结束后。使用jtag尝试连接airtag，如果失败就断电，重新配置攻击参数。如果攻击成功这时dump出固件就好了。

### 攻击成功

![](https://image.3001.net/images/20220323/1648037315_623b0dc30ff20eda0571f.png!small)

![](https://image.3001.net/images/20220323/1648037333_623b0dd55044c4cdf80fb.png!small)

参考资料：

https://github.com/newaetech/chipwhisperer

https://github.com/colinoflynn/airtag-re


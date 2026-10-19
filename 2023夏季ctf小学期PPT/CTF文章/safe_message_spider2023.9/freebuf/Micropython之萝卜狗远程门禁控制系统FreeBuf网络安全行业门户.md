*** 本文作者：_橙子 ゝ，本文属FreeBuf原创奖励计划，未经许可禁止转载**

严正声明：本文仅限于技术讨论与分享，严禁用于非法用途

 **当代社会，我们进公司需要门禁卡，出入小区需要门禁卡，门禁系统又称出入管理控制系统(ACCESS CONTROL SYSTEM)，
是一种管理人员进出的智能化管理系统，它集微机自动识别技术和现代安全管理措施为一体，它涉及电子，机械，光学，计算机技术，通讯技术，生物技术等诸多新技术。它是解决重要部门出入口实现安全防范管理的有效措施。适用各种机要部门，如银行、宾馆、机房、军械库、机要室、办公间、智能化小区、工厂等。**

**![timg.jpg](https://image.3001.net/images/20180510/15259413604066.jpg!small)**

**最近发现一个新好玩的Micropython开发板-萝卜狗(TurnipDog)，比TPYBoard
v102更牛掰，可能是个升级版吧，然后果断买了一个抓紧玩玩，发现这个的魅力在于支持远程控制，这个Micropython开发板，不是利用Wifi远程控制，而是利用红外线控制的，控制距离大约在15米左右，于是就想用它来做个远程的门禁控制系统。**

## 材料准备

> 萝卜狗(TurnipDog)开发板 1个
>
> 12864液晶显示屏 1个
>
> MF RC522射频IC卡 1个
>
> 中文文字转语音播报模块 1个
>
> 杜邦线若干

实验的器件都是一些通用的东西，很多地方都能买的到，我就不一一介绍啦，不过它的核心是我们的萝卜狗-TurnipDog。

**![萝卜狗.png](https://image.3001.net/images/20180510/15259421939212.png!small)**

萝卜狗

MF
RC522是应用于13.56MHz非接触式通信中高集成度的读写卡芯片，是一款低电压、低成本、体积小的非接触式读写卡芯片，是智能仪表和便携式手持设备研发的较好选择。
MF
RC522利用了先进的调制和解调概念，完全集成了在13.56MHz下所有类型的被动非接触式通信方式和协议。支持14443A兼容应答器信号。数字部分处理ISO14443A帧和错误检测。此外，还支持快速CRYPTO1加密算法，用语验证MIFARE系列产品。MFRC522支持MIFARE系列更高速的非接触式通信，双向数据传输速率高达424kbit/s。
作为13.56MHz高集成度读写卡系列芯片家族的新成员，MF RC522与MF RC500和MF
RC530有不少相似之处，同时也具备许多特点和差异。它与萝卜狗之间通信采用SPI模式，萝卜狗通过SPI接口来读取传输数据，以前用的是C语言，现在我们用的Micropython语言。

##
**![图片.png](https://image.3001.net/images/20180510/15259423706130.png!small)**

MF RC522射频IC卡

## 硬件接线方法

下面我们将萝卜狗和12864液晶显示屏、MF RC522射频卡和语音播报模块接起来，实物图我就不拍了，太丑了，大家根据下面的列表就可以接起来：

12864液晶显示屏 | 萝卜狗 | MF RC522射频卡 | 语音播报模块  
---|---|---|---  
GND | GND |  |  
VCC | VIN |  |  
RS | X11 |  |  
R/W | GND |  |  
E | X18 |  |  
DB0 | X1 |  |  
DB1 | X2 |  |  
DB2 | X3 |  |  
DB3 | X4 |  |  
DB4 | X5 |  |  
DB5 | X6 |  |  
DB6 | X7 |  |  
DB7 | X8 |  |  
PSB | 3V3 |  |  
RST | 3V3 |  |  
BLA | 3V3 |  |  
BLK | 3V3 |  |  
| Y4 | SDA |  
| Y6 | SCK |  
| Y8 | MOSI |  
| Y7 | MISO |  
| GND | GND |  
| Y3 | RST |  
| 3V3 | 3.3V |  
| Y2 |  | TXD  
| Y1 |  | RXD  
| +5V |  | VDD  
| GND |  | GND  
  
## 程序编程

下面是main.py的主程序代码，可以直接复制使用 ，这个类库太多了，我就不一一粘贴了，有需要的留下邮箱告诉我，我发给大家 (* ￣3)(ε￣ *)

    
    
    # main.py -- put your code here!
    
    import pyb
    
    import LCD12864
    
    import mfrc522
    
    import syn6288
    
    
    
    from pyb import UART
    
    from necir import NecIr
    
    from bm import necbm
    
    from bm import nec_cs
    
    from bm import nec_cb
    
    led=pyb.Pin('X10',pyb.Pin.OUT_PP)
    
    lcd=LCD12864.lcd12864()
    
    lcd.init_12864()
    
    led.value(1)
    
    SPI=pyb.SPI(2)    
    
    RC522_SDA='Y4'
    
    RC522_RST='Y3'
    
    rc52=mfrc522.MFRC522()
    
    rc52.init_spi(SPI,RC522_RST,RC522_SDA)
    
    tab_id=[45,162,222,43,122]
    
    buf=[0xFD,0x00,0x07,0x01,0x01,0x5B,0x74,0x35,0x5D,0xBD]
    
    u6=UART(6,9600)
    
    u6.write(bytearray(buf))
    
    def    lcdsleep():
    
        led.value(1)
    
        lcd.qp_12864()
    
    def    pdlcd(ok):
    
        lcd.qp_12864()
    
        if ok:
    
            lcd.lcd_write_string(0x89,"Allow entry",0)
    
            lcd.lcd_write_string(0x92,"允许进入",4)
    
        else :
    
            lcd.lcd_write_string(0x89,"Access Denied",0)
    
            lcd.lcd_write_string(0x92,"拒绝进入",4)
    
    def lcdsd():
    
        lcd.lcd_write_string(0x92,"请稍后",3)    
    
    def pdcard(id):
    
        for i in range(5):
    
            if(id[i]!=tab_id[i]):
    
                return 0
    
        return 1
    
    def main():
    
        while True:
    
            (status,backBits)=rc52.SeekCard(0x52)
    
            if(status==0):
    
                (status,id,)=rc52.Anticoll()
    
                led.value(0)
    
                if pdcard(id):
    
                    syn6288.sendspeak(6,9600,'张三来访'.encode('utf-16'))
    
                else :
    
                    syn6288.sendspeak(6,9600,'陌生人来访'.encode('utf-16'))
    
                lcdsd()
    
                pyb.Pin('X4',pyb.Pin.IN)
    
                nec = NecIr()
    
                while True:
    
                    nec.callback(nec_cb)
    
                    if necbm()==0xa0:
    
                        pdlcd(1)
    
                        syn6288.sendspeak(6,9600,'门已打开'.encode('utf-16'))
    
                        break
                    if necbm()==0xa1:
    
                        pdlcd(0)
    
                        syn6288.sendspeak(6,9600,'拒绝访问'.encode('utf-16'))
    
                        break
    
                pyb.delay(3000)
    
                nec_cs()<
    
                lcd.init_12864()
    
                lcdsleep()
    if __name__ == '__main__':
    
        main()

  

## 成果分享

我们把程序写入后，工作就完成啦，下面是我录的一个小视频，大家可以see一下，视频的地址：

效果还是不错的哦，由于我为了录制视频，距离比较近，大家可以远程控制哦！！！  

*** 本文作者：_橙子 ゝ，本文属FreeBuf原创奖励计划，未经许可禁止转载**


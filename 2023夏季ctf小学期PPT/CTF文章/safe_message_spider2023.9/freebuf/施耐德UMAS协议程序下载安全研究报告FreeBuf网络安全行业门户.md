## ****一. 施耐德UMAS协议简介****

UMAS基于旧的Telemechanique PLC使用的旧的Xway Unite协议。Umas协议用于配置和监视Schneider-Electric
PLC。它基于众所周知的Modbus协议，并使用Modbus协议规范中指定的保留功能代码之一
（十六进制功能代码0x5A）。施耐德电气PLC收到Modbus数据包时，将检查功能代码是否为0x5A（即功能码90），如果是，则使用某些特定的库，否则，将正常处理modbus请求，返回或修改指定的寄存器或PLC的线圈。（Nmap等工具探测PLC信息使用的功能码是43，即0x2b）

![1622513580_60b597ac5fccf4a531052.png!small](https://image.3001.net/images/20210601/1622513580_60b597ac5fccf4a531052.png!small)

##  ** **二. 研究目的****

 **
**上一篇文章主要研究了从PLC获取工程文件的安全性****。本次研究下载程序到PLC的安全性，然后尝试不通过上位机，直接通过代码的方式下载程序到PLC是否能正常运行。

##  ** **三. 研究内容****

###  ** **3.1. 研究环境****

研究对象不变，依旧使用的是施耐德型号为M340的PLC：

组态软件是Unity Pro XL：

![1622513640_60b597e8e36fc32d09e3d.png!small](https://image.3001.net/images/20210601/1622513640_60b597e8e36fc32d09e3d.png!small)

上位机的IP：10.45.115.27（Windows 7 旗舰版）

PLC的IP：10.45.115.24（M340）

###  ** **3.2. 具体步骤****

 ** **3.2.1. 抓包分析****

首先还是从组态软件下载PLC程序到PLC，抓取上位机和PLC交互的数据包。此过程比从PLC获取程序要复杂许多，抓取多个数据包进行分析。

![1622513654_60b597f63b15f1b3d1dca.png!small](https://image.3001.net/images/20210601/1622513654_60b597f63b15f1b3d1dca.png!small)

![1622513665_60b59801b314eb1fb91b6.png!small](https://image.3001.net/images/20210601/1622513665_60b59801b314eb1fb91b6.png!small)

 ** **通过多个数据包的对比分析，可以确定下载程序的过程也有3个状态，如下：****

    
    
    * UMAS Function Code 0x30 - INITIALIZE_UPLOAD: Initialize Strategy upload
    
    * UMAS Function Code 0x31 - UPLOAD_BLOCK: Upload strategy block to the PLC
    
    * UMAS Function Code 0x32 - END_STRATEGY_UPLOAD: Finish strategy Upload

0x30初始化下载，0x31是下载过程中，0x32是下载结束最后的确认数据包。

![1622513678_60b5980ed122292528ecb.png!small](https://image.3001.net/images/20210601/1622513678_60b5980ed122292528ecb.png!small)

![1622513689_60b59819ae7ea2ae7e1f6.png!small](https://image.3001.net/images/20210601/1622513689_60b59819ae7ea2ae7e1f6.png!small)

5a是正常功能码，66是本次会话的ID，后面的30，31，32就是状态码。

从第一张截图可以看到，从第一个0x30的包开始，中间还穿插了几个校验的包，经过多次抓包对比确认其是始终存在的，在写脚本时也要把这两个包加进去。

现在确认了其通信过程，然后就需要对传输的Payload进行对比，确认传输是APX文件的内容。这里使用Winhex软件打开APX文件：

![1622513699_60b59823733e04808227d.png!small](https://image.3001.net/images/20210601/1622513699_60b59823733e04808227d.png!small)

为了方便对比，把Wireshark的显示也切换为Hex模式：

![1622513711_60b5982f0e02ea80d9ff0.png!small](https://image.3001.net/images/20210601/1622513711_60b5982f0e02ea80d9ff0.png!small)

经过对比可以确认传输的文件是完全一致的。Wireshark数据包的前面16个字节包含了Modbus/TCP的头部和UMAS的头部，可以看到数据包的长度字段1022字节，减掉10字节就是APX文件切片的长度。

![1622513724_60b5983c8292713fe330f.png!small](https://image.3001.net/images/20210601/1622513724_60b5983c8292713fe330f.png!small)

可以看到APX文件的头部就是ASCII码16进制的41 50 58的APX。

 ** **3.2.2. 编写脚本****

 ** **首先总结一下前面抓包分析的内容：****

*建立会话的过程需要会话ID，会话ID可以通过发送特定的握手包取得；

*下载程序分为三个过程，分别对应3种状态码，30状态码的包发送之后还有一次校验；

*发送数据包过程中的transid和UMAS id是递增的；（transid并不重要）

*APX文件的切片大小为1012字节；

 ** **文件处理模块：****

![1622513742_60b5984e4ca0ca7d8bac2.png!small](https://image.3001.net/images/20210601/1622513742_60b5984e4ca0ca7d8bac2.png!small)

 ** **发包的代码：****

![1622513761_60b5986126ff6b5227ccf.png!small](https://image.3001.net/images/20210601/1622513761_60b5986126ff6b5227ccf.png!small)

里面还涉及到字节序处理的问题，多注意一下就好。

 ** **3.2.3. 测试****

准备了两个APX文件，一个是通过前文脚本的方式获取的，一个是通过组态软件的项目文件改后缀解压后得到的。通过winHex打开是可以看到工程文件的原文件名的，见下图：

![1622513769_60b59869626b7b74be441.png!small](https://image.3001.net/images/20210601/1622513769_60b59869626b7b74be441.png!small)

![1622513782_60b598760c6481c4534a1.png!small](https://image.3001.net/images/20210601/1622513782_60b598760c6481c4534a1.png!small)

 ** **下图是组态软件里面显示的PLC程序当前版本：****

![1622513800_60b5988863779332f371e.png!small](https://image.3001.net/images/20210601/1622513800_60b5988863779332f371e.png!small)

现在直接通过脚本下载文件到PLC，然后再到组态软件里面确认。

这时候通过组态软件连接PLC会提示使用监控模式，因为脚本与PLC建立了会话，使用的机器名就是WIN-VOJE6I12LCK。

![1622513808_60b59890950b037df03f8.png!small](https://image.3001.net/images/20210601/1622513808_60b59890950b037df03f8.png!small)

稍等一会再进行连接即可，然后选择从PLC中上传项目，会显示如下对话框：

![1622513816_60b59898788762ba82e8d.png!small](https://image.3001.net/images/20210601/1622513816_60b59898788762ba82e8d.png!small)

可以看到项目版本已经变了，从0.0.66变成了0.0.65。运行起来跑的也是我下发的程序的结果，PLC的启动、停止、运行等功能也可以通过脚本来实现。

![1622513884_60b598dc484587b73fba5.png!small](https://image.3001.net/images/20210601/1622513884_60b598dc484587b73fba5.png!small)

###  ** **3.3. 总结****

至此整个环节已形成闭环，从程序获取、修改后重新下发、PLC启动、停止、运行等都可以用脚本来实现。

##  ** **四. 防御建议****

协议本身目前没有提供任何防护措施，建议从安全管理和整体的安全防护方案角度来降低安全风险，保障企业的安全生产和运营。

##  ** **五. 参考链接****

https://community.checkpoint.com/t5/IoT-Protect/UMAS-Protocol-visibility-of-Engineering-and-configuration/td-p/40145


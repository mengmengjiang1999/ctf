作者：selph

目录：

• 011-wocy.11

• 012-ACG-crcme12

• 013--Acid_burn3

• 014-Splish4

• 015-BradSoblesky.15

• 016-fly_crkme36

• 017-Cabeca7

• 018-crackme_00068

• 019-Acid_Byte.39

• 020-cosh.310

011-015请看上期

# 1\. 016-fly_crkme3

算法难度：⭐⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220908/1662610068_63196a940dbe5b402deef.png!small)

### 查壳与脱壳：

UPX壳，直接ESP定律脱壳即可

![](https://image.3001.net/images/20220908/1662610068_63196a94a6cb2b7534fc3.png!small)

## 调试分析

Delphi程序，截图不方便注释，之后用IDR直接复制代码到everEdit里写注释了：

找到校验按钮，分析校验函数sub_00444B30：

首先是判断用户是否有输入，无输入则弹窗，有输入则跳转到00444B78：

![](https://image.3001.net/images/20220908/1662610069_63196a955106f00b03f0b.png!small)

接下来校验输入的数据，输入的内容必须是0x30~0x39之间，也就是纯数字:

![](https://image.3001.net/images/20220908/1662610069_63196a95efc3a48277c46.png!small)

接下来校验字符串长度：这个cm允许的输入是9，10，11字符，对于每种输入都有单独的计算，这里以输入长度为9位为例：输入格式是xx-xxx-xx

![](https://image.3001.net/images/20220908/1662610070_63196a96949fbab1b7674.png!small)

接下来进行了一个取数字的操作：进行了7段，总之就是把字符串中间的-去掉，把数字拼接在一起

![](https://image.3001.net/images/20220908/1662610071_63196a974ffb04fcc6a1d.png!small)

取完数字之后，转换成Int类型保存起来：

![](https://image.3001.net/images/20220908/1662610072_63196a983ce6a35601b9e.png!small)

接下来又进行了7段运算，运算出结果累加起来：

![](https://image.3001.net/images/20220908/1662610072_63196a98d0545576c6ceb.png!small)

这里调用了一个00444B20的函数，功能类似C的pow函数，对一个数（eax）求n（edx）次方，这里Delphi函数调用约定是fastcall：

![](https://image.3001.net/images/20220908/1662610073_63196a99ad1b67cb7d85d.png!small)

累加完成之后会进行对比：累加的值和输入的数字是否一样

![](https://image.3001.net/images/20220908/1662610074_63196a9a343a54bf72847.png!small)

相同则跳转到成功提示上：

![](https://image.3001.net/images/20220908/1662610074_63196a9ab3e9221a31145.png!small)

然后再往下就是10字节长度和11字节长度的运算对比了，方法类似，都是分别计算一个次方，然后和原数比较，相同则成

### 算法分析

注册码生成算法：

#define _CRT_SECURE_NO_WARNINGS  
#include  
#include  
  
int main()  
{  
for (int i = 1000000; i < 9999999; i++)  
{  
int sum = 0;  
char tmp[8] = { 0 };  
_itoa(i, tmp, 10);  
  
for (int j = 0; j < 7; j++) sum += pow(tmp[j]-'0',7);  
if (i == sum)std::cout << i << std::endl;  
}  
}

## 总结

难得一次性分析了这么长的反汇编，很多可以写成函数来方便调用的地方都直接内联了，可能是为了提高效率，这样一来就出现了大量重复代码段，分析花了挺多时间

# 2\. 017-Cabeca

算法难度：⭐⭐

爆破难度：⭐⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220908/1662610075_63196a9b408e04975be30.png!small)

### 查壳与脱壳：

无壳，Delphi程序，那个年代很流行Delphi啊

![](https://image.3001.net/images/20220908/1662610075_63196a9bd5d318970139e.png!small)

### 查字符串：

存在一些提示字符

![](https://image.3001.net/images/20220908/1662610076_63196a9c5c802d2096873.png!small)

## 调试分析

依然是拖IDR，复制出来在编辑器里写注释

窗口里有两个事件，一个是Name编辑框键入的时候触发的，一个是点击Try按钮触发的

![](https://image.3001.net/images/20220908/1662610076_63196a9cea7b6a5ba83e9.png!small)

直接看按钮的验证逻辑：经过函数初始化部分之后，判断了两个数字，不为0则向下进行，然后一系列获取编辑框的值，判空

这一段主要是判断三个编辑框是否有输入，无输入就骂你傻子，然后清空编辑框

![](https://image.3001.net/images/20220908/1662610077_63196a9d8e5146c4e7457.png!small)

接下来判断序列号，第一个数字和序列号1对比，第二个数字和序列号2对比，如果都对比上了，则提示成功

![](https://image.3001.net/images/20220908/1662610078_63196a9eafcec04dbfb5d.png!small)

后面就是验证失败的逻辑了，到这里问题来了，这两个数字是哪来的？刚刚看到界面还有个键入事件，去看看这个函数：

首先校验键入的值的合法性，是否小于0x80，也就是是否是ascii字符，不是就跳转，是就往下走

对字符减去8作为索引，从数组中取一个值，以这个值作为新的索引去跳转表中去跳转执行

![](https://image.3001.net/images/20220908/1662610079_63196a9f711f4882e0407.png!small)

看看跳转表跳转地址的功能：就是操作这两个值，然后返回

这两个数字是在键入Name的时候生成的

![](https://image.3001.net/images/20220908/1662610080_63196aa015b10c9b24c38.png!small)

### 暴力破解

爆破思路就是去改校验时候的那几个跳转，比如判空跳转，对比跳转等

### 算法分析

写注册机逻辑也很清晰了，对于每一个Name的字符，都进行一个指定的操作，就是对两个数字进行add，但是要录入很多数字，麻烦，这里直接手算一个输入：

Name = s  
Serial1 = 2224  
Serial2 = 1

结果：

![](https://image.3001.net/images/20220908/1662610080_63196aa0d7c9e87f8e29d.png!small)

## 总结

新160个CM里第一次见到的新姿势：通过键入事件在输入时自动生成校验码

# 3\. 018-crackme_0006

算法难度：⭐⭐⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220908/1662610082_63196aa20899d21320c80.png!small)

### 查壳与脱壳：

汇编写的程序，无壳

![](https://image.3001.net/images/20220908/1662610082_63196aa2bc227757e4030.png!small)

### 查字符串：

存在提示字符串：

![](https://image.3001.net/images/20220908/1662610083_63196aa34c09f4508f5a3.png!small)

## 调试分析

这个程序计算比较复杂，这里通过x86dbg+IDA结合进行分析

### 找到验证逻辑

直接从oep开始分析：

汇编写的程序，这里是一个窗口过程，参数里这个是过程函数，处理窗口消息的函数

![](https://image.3001.net/images/20220908/1662610083_63196aa3c81ecfc9d1ceb.png!small)

一般自己创建窗口写窗口过程函数都是类似这样的：参数uMsg是消息号，根据消息来进行不同的操作

LRESULT CALLBACK MyWndProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM
lParam){  
switch(uMsg){  
case WM_CREATE:  
//content  
return 0;  
case WM_DESTORY:  
//content  
return 0;  
default:  
return DefWindowProc(hwnd,uMsg,wParam,lParam);  
}  
return 0;  
}

分析思路很简单，找到Check的那个分支，下断点向下分析

首先这是消息号0x111的分支，0x111是WM_COMMAND消息，对于这个消息，它的参数是命令号，也就是反汇编里的这个arg_8，然后根据命令号进行下一层的跳转

这里需要跳转，跳转之后就是在判断命令号，命令号在eax里，这里如果eax=0x3f0，则是about按钮的事件，check按钮事件位于命令号0x3ee

![](https://image.3001.net/images/20220908/1662610084_63196aa49dfdaf024e62e.png!small)

所以直接在0x4011ca下一行0x4011d0下断点即可，从这里往下就是验证逻辑了

### 第一段运算

首先是第一段运算，基于机器特征的校验码：

通过自写函数去获取卷序列号，分别获取C盘和D盘的，然后进行一段浮点运算，中间经历的这些自写的位移函数在此处无意义

![](https://image.3001.net/images/20220908/1662610085_63196aa55f510ba8fa8e0.png!small)

这里来看一下这些自写函数：首先是获取卷序列号的：通过Win32 API获取信息，直接返回

![](https://image.3001.net/images/20220908/1662610086_63196aa63fa09f11e3958.png!small)

然后是左移函数：从参数获取值，然后左移指令进行运算，通过eax返回

![](https://image.3001.net/images/20220908/1662610087_63196aa7012c0ad3b2c78.png!small)

循环左移函数：使用循环位移运算指令实现的

![](https://image.3001.net/images/20220908/1662610087_63196aa7a5bc59f35376b.png!small)

然后Add就是两数相加，没啥好看的，最后这个浮点运算很关键：将获取到的两个卷序列号分别类型转换成浮点型，通过浮点运算，分别计算两个数的平方，然后开根号，最后转换回十进制：

![](https://image.3001.net/images/20220908/1662610088_63196aa8554acc10d1130.png!small)

### 第二段运算

第二段运算是基于用户名的运算，首先判断了用户名长度，必须大于4字节，然后调用了一个自写函数对用户名计算了一个结果，然后进行位移操作，与或操作之后得到一个新的值，这个值与第一段运算的结果有关，最后保存起来第二段计算的结果

![](https://image.3001.net/images/20220908/1662610089_63196aa917e922d7e5c46.png!small)

看看这个自写函数：循环遍历每一个字节，然后累乘起来，使用cld扩展指令，溢出32位的部分会保存到edx里，这里会把高32和低32位结果加起来

![](https://image.3001.net/images/20220908/1662610089_63196aa9c278983ac0e82.png!small)

### 第三段运算

第三段运算使用到了第二段运算计算的结果，对这个结果除以10取余数，用余数作为索引依次从固定字符串里取值，每次取值之后，再对刚刚那个结果除以4求商，并把商保存起来下次循环的时候用，这里的取余数和求商依然是自写函数，功能简单就不展开描述了

![](https://image.3001.net/images/20220908/1662610090_63196aaa7d824fe8ffdd1.png!small)

最后计算出来一个字符串就是真的序列号了

### 校验

最后就是拿第三段运算计算出来的字符串和用户输入比对，比对一样了就是成功

![](https://image.3001.net/images/20220908/1662610091_63196aab60d35e274ac2f.png!small)

### 暴力破解

验证流程图大概如下，红线标的是要走的路，在验证逻辑里，对于需要跳转的，就改jmp，对于不需要跳转的就清空改nop，对于这种简单的逻辑这么操作比较无脑可行hhhh

![](https://image.3001.net/images/20220908/1662610092_63196aac0a1dbe76d370c.png!small)

### 注册机编写

#include  
#include  
  
DWORD GetVolumeSerialNumber(const char* lpRootPathName) {  
CHAR FileSystemNameBuffer[128];  
DWORD FileSystemFlags;  
DWORD VolumeSerialNumber;  
CHAR VolumeNameBuffer[128];  
GetVolumeInformationA(  
lpRootPathName,  
VolumeNameBuffer,  
0x80u,  
&VolumeSerialNumber,  
(LPDWORD)0xFF,  
&FileSystemFlags,  
FileSystemNameBuffer,  
0x80u);  
return VolumeSerialNumber;  
}  
  
DWORD bit_move(DWORD val, int n) {  
DWORD size = sizeof(val) * 8;  
n = n % size;  
return (val >> (size - n) | (val << n));//左移  
}  
  
DWORD floatdeal(DWORD a1,DWORD a2) {  
int res = 0;  
__asm {  
fwait;  
fninit;  
fild dword ptr[a1];  
fld st(0);  
fmulp st(1), st(0);  
fild dword ptr[a2];  
fld st(0);  
fmulp st(1), st(0);  
faddp st(1), st(0);  
fsqrt;  
fistp dword ptr[res];  
  
}  
return res;  
// return (DWORD)sqrt((float)a1 * (float)a1 + (float)a2 * (float)a2);  
}  
  
int main()  
{  
DWORD volumeSerialNumber_C = 0;  
DWORD volumeSerialNumber_D = 0;  
DWORD tmp = 0;  
DWORD tmp2 = 1;  
LONGLONG tmp2_1 = 1;  
char name[20] = {0};  
char serial[20] = { 0 };  
const char* arr = "071362de9f8ab45c";  
  
std::cin >> name;  
if (strlen(name) < 4) return 0;  
// 第一段运算  
volumeSerialNumber_C = GetVolumeSerialNumber("C:\\\");  
volumeSerialNumber_D = GetVolumeSerialNumber("D:\\\");  
tmp = floatdeal(volumeSerialNumber_C, volumeSerialNumber_D);  
// 第二段运算  
for (int i = 0; name[i]; i++)  
{  
tmp2_1 *= name[i];  
tmp2 = tmp2_1 & 0x00000000FFFFFFFF;  
tmp2 += (tmp2_1 & 0xffffffff00000000) >> 32;  
}  
  
tmp2 = bit_move(tmp2,1);  
tmp2 |= tmp;  
tmp2 &= 0x0FFFFFFF;  
// 第三段运算  
DWORD i = 0;  
do  
{  
serial[i++] = arr[tmp2 % 0x10];  
tmp2 /= 4;  
  
} while (tmp2);  
std::cout << "序列号：";  
std::cout << serial << std::endl;  
system("pause");  
}  
  

### 结果

![](https://image.3001.net/images/20220908/1662610092_63196aaccf4997d403885.png!small)

## 总结

这是目前为止分析160个CM里遇到最复杂的校验算法了，分析了好久，这个程序主要有两个难点：

第一个难点在于程序直接启动了窗口过程，所以需要找到验证逻辑出现的地方才能开始下断点，分析程序执行流程即可去跟踪消息号即可

第二个难点在于使用了8个自写函数，要了解验证过程，需要知道自写函数做了什么事情，其中有的函数使用了浮点数运算，这一块不熟悉估计要查一会文档了

做完之后再回头看，嘛，也不过如此

## 参考资料

## – [1] (2条消息) GetVolumeInformationA获取磁盘卷标、文件系统,_上善若水pjf的博客-CSDN博客_getvolumeinformationa

## – [2] 汇编语言SHL（左移）指令：将操作数逻辑左移一位(biancheng.net)

## – [3] 汇编语言ROL（循环左移）指令：将操作数所有位都向左移(biancheng.net)

## – [4] (2条消息) C/C++实现循环左移，循环右移_子木呀的博客-CSDN博客_c++数组循环左移

# 4\. 019-Acid_Byte.3

算法难度：⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220908/1662610093_63196aada534f717045f9.png!small)

### 查壳与脱壳：

有UPX壳：无脑ESP定律即可

![](https://image.3001.net/images/20220908/1662610094_63196aae30ebea5ef195f.png!small)

## 调试分析

IDR分析，复制到编辑器里写注释，硬编码Name和Serial，没啥好说的

![](https://image.3001.net/images/20220908/1662610094_63196aaebe10c9fa53b00.png!small)

效果：

![](https://image.3001.net/images/20220908/1662610095_63196aaf6ef6743d529ab.png!small)

# 5\. 020-cosh.3

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220908/1662610095_63196aafe78dcc154fe4c.png!small)

### 查壳与脱壳：

无壳，MFC程序

![](https://image.3001.net/images/20220908/1662610096_63196ab0a32285c84b2a1.png!small)

### 字符串：

提示字符串

![](https://image.3001.net/images/20220908/1662610097_63196ab15047c52de69a0.png!small)

## 调试分析

静态分析从字符串入手或者从函数调用的交叉引用入手比较方便，可以查MessageBox函数的调用，也可以查提示信息字符串的交叉引用，这里从后者入手（方便），这个字符串大概率会出现在校验函数里

首先进行两个操作，判断编辑框输入的长度，用户名和序列号得是大于5，然后保存到局部变量里CString

![](https://image.3001.net/images/20220908/1662610098_63196ab222d6ef3b92b9d.png!small)

接下来保存Name和Serial，分别对这两个值进行了一个运算：

![](https://image.3001.net/images/20220908/1662610099_63196ab325589fb6566a7.png!small)

再往下就是strcmp了：两个计算后的结果相同，则跳转到成功分支

![](https://image.3001.net/images/20220908/1662610099_63196ab3d6675632e23ff.png!small)

### 注册机

#include  
int main()  
{  
char name[20] = "selph1";  
char serial[20] = { 0 };  
int Len = strlen(name);  
  
for (int i = 0; name[i]; i++) serial[i] = name[i] ^ (i + 1);  
for (int i = 0; serial[i]; i++) serial[i] = serial[i] ^ (i + 10);  
std::cout << serial;  
}

效果：

![](https://image.3001.net/images/20220908/1662610100_63196ab47ae99850cb425.png!small)

## 总结

感觉已经看这种反汇编越来越快了


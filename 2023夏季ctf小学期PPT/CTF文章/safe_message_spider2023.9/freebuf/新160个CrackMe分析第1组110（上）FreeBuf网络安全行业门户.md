视频课件下载，百度网盘：https://pan.baidu.com/s/1BaROP5e9UbJMSN1sgOOKbA 提取码：z2i6

## 前言

这位师傅整理了新160个CrackMe和配套的逆向视频来帮助新手练习逆向技能，逆向的基础便是阅读反汇编的能力，这正是本练习的核心所在以前我想过去坚持把160个做完，但没坚持下来，近期总想着每天多多少少做点逆向练习，于是我打算去再次挑战，本次以这个师傅整理的为准进行逆向的练习，去扎实自己的逆向功底这个师傅提供了逆向的讲解视频，主要是基于OD动态调试分析的以及VB版本的注册机编写这里我从另一个视角去完成本系列文章：以IDA静态分析为主，x86dbg动态分析为辅，完成程序的调试和分析，使用C++/C#
编写注册机欢迎有兴趣的童鞋来探讨交流~

## 本系列难度星级：

CM难度评星标准按视频里的走：算法：–⭐：明文字符串操作–⭐⭐：很容易看懂的算法–⭐⭐⭐：算法复杂但容易看懂，or
算法简单但不容易看懂–⭐⭐⭐⭐：算法难，看懂难–⭐⭐⭐⭐⭐：分析不出来，以后回来做爆破：–⭐：静态分析就能找到关键跳–⭐⭐：回追一层，或修改2个点的–⭐⭐⭐：回追二层以上，或修改超过2个点的–⭐⭐⭐⭐：回追多层，修改点难找且多–⭐⭐⭐⭐⭐：暂时无法破解，以后回来做

# 2\. 002-abexcm5

# 爆破难度：⭐

算法难度：⭐

## 信息收集

运行情况：输入序列号，输入错误会提示错误并退出程序，这是个验证序列号的程序

![](https://image.3001.net/images/20220901/1662032201_631099496735a102e30de.png!small)

查壳：无壳

![](https://image.3001.net/images/20220901/1662032202_6310994a2928237c137dd.png!small)

查字符串：有提示语，疑似硬编码的字符串

![](https://image.3001.net/images/20220901/1662032202_6310994ab6d4e17a44699.png!small)

查导入表：使用了字符串操作类的函数，以及GetVolumeInformationA函数，不知道序列号生成跟这个有无关系

![](https://image.3001.net/images/20220901/1662032204_6310994c4750fc2d6f025.png!small)

到现在已经知道了软件大概的运行流程：获取用户输入，对用户输入进行一些处理，然后弹框提示

## 逆向分析

IDA里选择MessageBoxA函数查交叉引用，跟踪到函数sub_401056中，这是CM的校验逻辑所在：首先先获取用户输入，然后生成两个字符串：（注释写错了，应该是do-while循环而不是while循环）

![](https://image.3001.net/images/20220901/1662032205_6310994d13f559b7fa759.png!small)

然后把刚刚生成的两个字符串拼接到一起，生成序列号，与用户输入进行比对，序列号几乎是硬编码

![](https://image.3001.net/images/20220901/1662032205_6310994dc09ddc8f7c4a3.png!small)

### 暴力破解

### 验证逻辑是：生成序列号，通过与用户输入的比对来进行验证

暴力破解的思路是：修改跳转条件即可，把jz改成jmp即可：

![](https://image.3001.net/images/20220901/1662032206_6310994e7ae9f33ead487.png!small)

算法分析注册码生成算法：#include  
#include  
  
int main()  
{  
char VolumeNameBuffer[MAX_PATH] = { 0 };  
DWORD VolumeSerialNumber = 0;  
DWORD MaximumComponentLength = 0;  
DWORD FileSystemFlags = 0;  
int i = 2;  
char Series[MAX_PATH] = { 0 };  
  
GetVolumeInformationA(  
0,  
VolumeNameBuffer,  
0x32u,  
&VolumeSerialNumber,  
&MaximumComponentLength,  
&FileSystemFlags,  
0,  
0);  
  
  
lstrcatA(VolumeNameBuffer, "4562-ABEX");  
  
do{  
VolumeNameBuffer[0]++;  
VolumeNameBuffer[1]++;  
VolumeNameBuffer[2]++;  
VolumeNameBuffer[3]++;  
} while (--i);  
  
lstrcatA(Series, "L2C-5781");  
lstrcatA(Series, VolumeNameBuffer);  
  
std::cout << Series << std::endl;  
system("pause");  
return 0;  
}效果：

![](https://image.3001.net/images/20220901/1662032207_6310994f1c26944fd6f26.png!small)

总结字符串拼接生成序列号，通过判断+跳转进行校验，很简单，没啥好说的

## 参考资料

–[1] GetVolumeInformationA获取磁盘卷标、文件系统,_上善若水pjf的博客-CSDN博客_getvolumeinformationa

# 3\. 003-CrueheadCM3

爆破难度：⭐⭐算法难度：⭐⭐

## 信息收集

运行情况：是一个空白界面，可能要经过某些操作才能让内容显示出来

![](https://image.3001.net/images/20220901/1662032207_6310994f97b9830d0cede.png!small)

查壳：无壳

![](https://image.3001.net/images/20220901/1662032208_631099502789b4d6284a1.png!small)

查字符串：看到了一些提示语

![](https://image.3001.net/images/20220901/1662032208_63109950a88f4c84d66a8.png!small)

查导入表：除去窗口绘制，消息循环用到的函数，这里还出现了文件操作相关函数，可能跟文件有关，结合上面的字符串搜索信息，应该需要一个CRACKME3.KEY的文件

![](https://image.3001.net/images/20220901/1662032209_631099513c9da3de79a29.png!small)

## 逆向分析

根据之前对文件进行静态的信息收集之后，这个文件操作很可疑，就从文件操作函数CreateFileA去搜索交叉引用看看这里在干嘛首先打开名为CRACKME3.KEY的文件，然后读取其中的内容保存到缓冲区

![](https://image.3001.net/images/20220901/1662032209_63109951ddc424935c796.png!small)

然后判断读取的字节数如果是0x12就往下走，对读取到的内容进行一顿操作，然后通过某种计算方法进行校验，然后把校验结果保存在al里入栈了

![](https://image.3001.net/images/20220901/1662032210_63109952829c3b7f7cc46.png!small)

然后经过一段窗口创建的操作之后，在进入消息循环之前，做了这样一个校验，校验文件内容是否正确，正确就弹框提示，正是通过刚刚push的al进行校验的

![](https://image.3001.net/images/20220901/1662032212_63109954bf90b4ceb3380.png!small)

暴力破解整个校验流程最后还是通过判断+跳转进行执行的，暴力破解老样子，直接修改跳转条件即可：

![](https://image.3001.net/images/20220901/1662032213_631099554d7dee3658be7.png!small)

前面还有个判断读取到的内容是否为0x12字节，把那个跳转也nop改掉即可，这里就不演示了

### 算法分析

这里的校验算法主要是这几行：

![](https://image.3001.net/images/20220901/1662032214_6310995615fdef9ed02be.png!small)

这里调用了两个自写的函数，首先是sub_401311：这里计算一个前14字节的校验和，然后对前14字节依次与ABCD...进行异或操作，将异或的结果保存起来，校验和也保存起来

![](https://image.3001.net/images/20220901/1662032214_63109956a83f3c5dc2dc8.png!small)

然后是下一个函数sub_40133C：就是取后4字节出来

![](https://image.3001.net/images/20220901/1662032215_6310995753068fe88b703.png!small)

现在这个校验算法已经清晰了起来：–计算一个校验和，校验和与0x12345678进行异或，得到的结果与输入里的最后4字节进行比较–对输入的前14字节进行异或操作，异或后的结果作为参数去调用显示验证成功提示框那么序列号的生成就是：a.随便输入一个14字节的字符串作为用户名b.对这14字节依次异或ABCD...，保存起来c.对校验和异或0x12345678，然后拼接到异或结果后面，即可完成生成注册码生成算法：#include  
#include  
  
void generateSeriesFile(const char* in_pwd) {  
char pwd[0x13] = { 0 };  
int i;  
char var_bl = 'A';  
unsigned int sum = 0;  
  
memcpy(pwd, in_pwd, 0x13);  
  
i = 0;  
do {  
sum += pwd[i];  
pwd[i] ^= var_bl;  
i++;  
var_bl++;  
if (!pwd[i])break;  
} while (var_bl != 'O');  
  
sum ^= 0x12345678;  
*(unsigned int *)&pwd[0xE] = sum;  
  
for (int k = 0; k < 18; k++)  
{  
unsigned char* tmp = (unsigned char*) & pwd;  
printf("%02x ",tmp[k]);  
}  
  
HANDLE hFile = CreateFileA("CRACKME3.KEY", GENERIC_ALL, 0, NULL, OPEN_ALWAYS,
FILE_ATTRIBUTE_NORMAL, NULL);  
DWORD retNum = 0;  
WriteFile(hFile, pwd, sizeof(pwd), &retNum, NULL);  
CloseHandle(hFile);  
}  
  
int main()  
{  
const char *pwd= "helloworld@qqq.com";  
generateSeriesFile(pwd);  
system("pause");  
return 0;  
}效果：

![](https://image.3001.net/images/20220901/1662032215_63109957cda3720f6c157.png!small)

  

## 总结

序列号算法和校验依然很简单，这里有意思的是：这个程序的校验逻辑位于窗口进入消息循环之前，校验行为发生在了软件正常运行之前，根据校验结果再选择是否正常运行程序

## 参考资料

–[1] ASCII码一览表，ASCII码对照表(biancheng.net)–[2] setz_ccboby的博客-CSDN博客_setz指令

# 4\. 004-AcidBytes.2

算法难度：⭐爆破难度：⭐脱壳难度：⭐

## 信息收集

### 运行情况：

依然是序列号验证，输入序列号点击Check，会显示提示信息

![](https://image.3001.net/images/20220901/1662032216_631099585ca699b659aa4.png!small)

### 查壳与脱壳：

出现壳了，Die查出来是Upx压缩壳

![](https://image.3001.net/images/20220901/1662032217_631099591657dd79a9b6a.png!small)

对于Upx壳使用ESP定律即可完成脱壳，过程相当简单，这里简述一下就不截图演示了：a.运行到OEP，运行到pushad的下一行（执行这个指令只有esp的值会被修改）b.在内存中查看esp指向的地址，对该地址下访问硬件断点，然后运行，此时会运行到popad指令的下一行，是跳转到真正OEP的jmp，跳转过去c.使用Scylla进行Dump和修复PE，得到脱壳后的程序再次查壳验证：

![](https://image.3001.net/images/20220901/1662032217_63109959b21ef1f9157e0.png!small)

查字符串：

有点帮助的字符串是这些，是验证提示信息

![](https://image.3001.net/images/20220901/1662032218_6310995a4a6a0fafa7098.png!small)

### 查导入表：

没有什么特别的点，看起来都是图形界面相关的内容，程序使用MessageBoxA弹窗提示

## 调试分析

这个程序的传参方式比较特别，根据查阅资料[1]，前三个数据保存在eax,edx,ecx寄存器里，超过三个参数部分放在堆栈传递这里以字符串作为入口进行突破，搜索字符串Congrats!...的交叉引用，找到按钮控件的处理例程：首先是注册了SEH异常链，然后获取用户输入

![](https://image.3001.net/images/20220901/1662032219_6310995b19366b4d2a790.png!small)

接下来就是比较+弹窗三连：输入字符串和硬编码字符串进行对比，如果相同，就弹窗提示成果如果不相同，就判断是否输入的有内容，如果无内容，提示输入为空，否则提示输入错误

![](https://image.3001.net/images/20220901/1662032219_6310995bbcd49dd2ad6c9.png!small)

### 暴力破解

直接Nop掉关键跳即可：

![](https://image.3001.net/images/20220901/1662032220_6310995c863ffeaecc07a.png!small)

### 算法分析

硬编码密码，无算法效果：

![](https://image.3001.net/images/20220901/1662032221_6310995d4d068d1e5a3cd.png!small)

## 总结

处理该CM的要点就是脱壳，脱壳之后就是硬编码判断跳转，算是个入门级脱壳练习

## 参考资料

–[1] Delphi的参数传递约定以及动态参数个数(转载笔记) - 不得闲\- 博客园(cnblogs.com)

# 5\. 005-Andrénalin.1

算法难度：⭐爆破难度：⭐

## 信息收集

### 运行情况：

功能就是输入密码，然后验证

![](https://image.3001.net/images/20220901/1662032221_6310995de9bed0eb6e13d.png!small)

### 查壳与脱壳：

无壳，是VB 编写的GUI 程序，需要使用VB 反编译工具进行逆向分析

![](https://image.3001.net/images/20220901/1662032222_6310995e86b7c037933bb.png!small)

## 调试分析

对于VB 程序，可以使用VB Decompiler 进行逆向，本例验证逻辑较为简单，估计主要是练习

![](https://image.3001.net/images/20220901/1662032223_6310995fc2989f1273587.png!small)

### 破解

硬编码校验密码，直接输入即可效果：

![](https://image.3001.net/images/20220901/1662032224_63109960402b662b28a48.png!small)

## 总结

本例没什么难度，主要是告诉初学者，对于VB，CSharp 这类的托管程序，可以使用专门的反编译软件进行代码还原分析逻辑


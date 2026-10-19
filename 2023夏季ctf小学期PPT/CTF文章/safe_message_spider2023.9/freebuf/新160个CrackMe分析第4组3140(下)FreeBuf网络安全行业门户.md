作者：selph

目录：

• 031-Cruehead.11

• 032-Bengaly-Crackme22

• 033-dccrackme13

• 034-fireworx54

• 035-Dope211225

• 036-Andrnalin.26

• 037-fireworx27

• 038-Eternal Bliss.38

• 039-eKH19

• 040-DaNiEI-RJ110

# 1\. 036-Andrnalin.2

算法难度：⭐⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220923/1663938510_632dafce335eabf4e0ae6.png!small)

### 查壳与脱壳：

无壳，VB程序！

![](https://image.3001.net/images/20220923/1663938510_632dafceb7a33a6ffe3b1.png!small)

## 调试分析

借助VB Decompiler辅助分析：

这里界面上有两个函数，一个是按钮，另一个是输入Name的时候的事件：

![](https://image.3001.net/images/20220923/1663938511_632dafcf4442267dd28ee.png!small)

首先看Text2_change函数：就是根据Name有无输入值来判断是否启用按钮

Private Sub Text2_Change() '4024F0  
Dim var_1C As Variant  
loc_0040259D: If (Form1.Text2.Text = global_00401DC4) + 1 Then // 如果输入的内容为空  
loc_004025AA: Set var_1C = Form1.Command1 // 按钮  
loc_004025B7: var_1C.Enabled = False // 不启用  
loc_004025BF: If var_1C >= 0 Then GoTo loc_004025F7  
loc_004025C1: GoTo loc_004025E5  
loc_004025C3: End If  
loc_004025CE: Set var_1C = Form1.Command1  
loc_004025DB: var_1C.Enabled = True // 有输入的内容则启用按钮  
loc_004025E3: If var_1C >= 0 Then GoTo loc_004025F7  
loc_004025E5: ' Referenced from: 004025C1  
loc_004025F1: var_1C = CheckObj(var_1C, global_00401DC8, 140)  
loc_0040260C: GoTo loc_00402621  
loc_00402620: Exit Sub  
loc_00402621: ' Referenced from: 0040260C  
End Sub

接下来看Click函数：

Private Sub Command1_Click() '401FF0  
loc_004020CA: var_44 = Form1.Text2.Text // Name编辑框的内容  
loc_00402126: For var_24 = 1 To Len(var_44) Step 1 // 遍历Name字符串  
loc_00402134: If var_108 Then //  
loc_00402170: var_8008 = Asc(CStr(Mid(var_44, CLng(var_24), 1))) //
取一个字节变成ASCII码  
loc_00402176: var_B4 = var_8008  
loc_004021A0: var_34 = var_34 + var_8008 // 累加到var_34  
loc_004021CB: Next var_24  
loc_004021D1: GoTo loc_00402132  
loc_004021D6: End If  
loc_00402204: var_34 = var_34 * 1234567890 // 累加结果乘以1234567890  
loc_00402254: Mid(var_34, 9, 1) = "-" // 修改其中一个值  
loc_004022CB: If (Form1.Text1.Text = var_34) Then // 如果输入的Key == var_34则成功  
loc_004022D1: Beep  
loc_00402374: var_54 = MsgBox(" RiCHTiG !!!! .... weiter mit dem Nächsten
!!!", 48, "RiCHTiG !", 10, 10)  
loc_00402391: Else  
loc_0040240F: var_8018 = MsgBox("Leider Falsch! Nochmal veruschen ! Wenn Du es
nicht schaffen solltest, schreib mir ! Andrenalin@gmx.net", 16, "LEiDER Falsch
! ", 10, 10)  
loc_0040242E: var_54 = var_8018  
loc_00402446: End If  
loc_00402459: GoTo loc_0040248F  
loc_0040248E: Exit Sub  
loc_0040248F: ' Referenced from: 00402459  
loc_004024C0: GoTo loc_00esi  
End Sub

按照上述代码的思路去写注册机：

#define _CRT_SECURE_NO_WARNINGS  
#include  
  
int main()  
{  
char name[100] = { 0 };  
char serial[100] = { 0 };  
int len = 0;  
long long check = 0;  
  
std::cin >> name;  
len = strlen(name);  
for (int i = 0; name[i]; i++) check += name[i];  
check *= 1234567890;  
  
sprintf(serial,"%lld",check);  
serial[8] = '-';  
std::cout << serial;  
}

得出的结果不对，当输入为selph的时候，输出为：66666666-600，动态调试查看真正是输出：

到这里生成-的时候，发现这里出现了两次，而反汇编软件只识别到了一个，故再加一个即可

![](https://image.3001.net/images/20220923/1663938511_632dafcfb87570aeb03a5.png!small)

然后这就是完整的注册码生成了

### 注册机

注册码生成算法：

#define _CRT_SECURE_NO_WARNINGS  
#include  
  
int main()  
{  
char name[100] = { 0 };  
char serial[100] = { 0 };  
int len = 0;  
long long check = 0;  
  
std::cin >> name;  
len = strlen(name);  
for (int i = 0; name[i]; i++)  
{  
check += name[i];  
}  
check *= 1234567890;  
  
sprintf(serial,"%lld",check);  
serial[3] = '-';  
serial[8] = '-';  
std::cout << serial;  
}

效果：换个Name测试

![](https://image.3001.net/images/20220923/1663938512_632dafd06faf29af58d64.png!small)

![](https://image.3001.net/images/20220923/1663938512_632dafd0d677309257e89.png!small)

2\. 037-fireworx2

#

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220923/1663938513_632dafd15278a064aae7e.png!small)

### 查壳与脱壳：

![](https://image.3001.net/images/20220923/1663938513_632dafd1cba5b2a229dd6.png!small)

## 调试分析

##  是Delphi程序，IDR哒：

硬编码序列号，这里获取了Name之后进行了push，2次，所以这里拼接了2个Name

![](https://image.3001.net/images/20220923/1663938514_632dafd2657c47dfe3277.png!small)

输入为selph，则最终的拼接结果是：selphselph625g72：

![](https://image.3001.net/images/20220923/1663938515_632dafd31a896a9dcf086.png!small)

## 总结

很基础，考察函数调用的传递参数理解

# 3\. 038-Eternal Bliss.3

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

啊这，看来又是VB

![](https://image.3001.net/images/20220923/1663938515_632dafd39e8bd057075e9.png!small)

### 查壳与脱壳：

无壳：

![](https://image.3001.net/images/20220923/1663938516_632dafd41e3b0be103eef.png!small)

## 调试分析

又是VB，真的太顶了，逆VB好恶心啊

首先VBDecompiler找到这个注册按钮事件的函数起始地址，然后x86dbg下断点开始分析（这个伪代码太恶心了，还是看反汇编吧）

![](https://image.3001.net/images/20220923/1663938516_632dafd4c7020f0b40acb.png!small)

首先输入1234567进行调试，VB的反汇编很恶心就是，很长一段代码，只有几句是跟代码逻辑相关的内容，大部分都是干扰

刚开始保存了一系列字符到栈里：

![](https://image.3001.net/images/20220923/1663938517_632dafd54dcbe4faf7b2b.png!small)

（大部分代码没啥用，主要看自动注释的内容，还有函数call，是否是处理我们输入的内容，如果是，大概率就是我们要看的地方，否则先跳过吧）

然后接下来计算了一下字符串长度，保存了起来，大概率是循环遍历字符要用到

![](https://image.3001.net/images/20220923/1663938517_632dafd5f087accd6e2a8.png!small)

再往下就是循环了，一个jmp跳转下去，然后又跳转上来，直接看循环的关键内容吧：

超级长的循环代码，实际有用的就这几行，取一个字节，然后转换成ascii码的值，然后累加起来，累加值保存在[ebp-40]

![](https://image.3001.net/images/20220923/1663938518_632dafd6706c3d4f67dde.png!small)

接下来跳出循环，然后就用上了函数开头保存的一堆字符：

这里就是第一处校验跳转了，这里累加Reverse每个字符的ascii的值，和输入的累加值做对比，如果相同则不跳转

![](https://image.3001.net/images/20220923/1663938518_632dafd6e6eb12f251140.png!small)

再往下就是第二次校验对比了，首先是获取第2，4，7个字符

![](https://image.3001.net/images/20220923/1663938519_632dafd775ae56dcb5327.png!small)

然后对这三个字符进行一系列计算：保存到了[ebp-150]里

![](https://image.3001.net/images/20220923/1663938519_632dafd7f3e316e95b175.png!small)

再往下就是对比了：判断刚刚计算的那个值是否为0，如果为0则表示失败

![](https://image.3001.net/images/20220923/1663938520_632dafd8ace49a2257053.png!small)

到这里已经分析的差不多了:

– 开始遍历字符累加，确保注册码是Reverse这7个字母的组合

– 后来取其中第2，4，7个字符拿来计算，确保这个字母组合的这几个位置的字母是固定的，这三个位置都是e

满足这两个条件即为正确的码，测试：veResre：

![](https://image.3001.net/images/20220923/1663938521_632dafd92649aff80d5af.png!small)

## 总结

逆Vb的时候不用一条一条看，很简单的几句话，可能会被VB填充成超级大一段

# 4\. 039-eKH1

算法难度：⭐⭐⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220923/1663938521_632dafd98c0a9c2fedd91.png!small)

### 查壳与脱壳：

无壳：

![](https://image.3001.net/images/20220923/1663938522_632dafda0e51ba64ab47a.png!small)

## 调试分析

首先看按钮的逻辑：

首先获取UserName，进行长度验证，然后获取Serial

接下来将获取的UserName和Serial作为参数，调用校验函数00427A20

如果得到的返回值是0x0BC614E则表示验证成功

![](https://image.3001.net/images/20220923/1663938522_632dafdaa3f5ef957270f.png!small)

接下来看这个校验函数：

首先是一些初始化操作，保存了参数到局部变量里

![](https://image.3001.net/images/20220923/1663938523_632dafdb97f94cb5c973b.png!small)

接下来对UserName进行处理：计算一个累加值

计算方法看注释，这里简述一下：

– 取一个字符到ebx

– ebx左移8位

– ebx进行或操作，或一个数组中的字符

– 如果ebx小于0了，则乘以-1

– 循环

![](https://image.3001.net/images/20220923/1663938524_632dafdc470668ccd337f.png!small)

最终将刚刚计算的值转换成字符串，计算字符串长度

这里的字符串长度就是接下来循环的次数，也就是这个累加值的位数

接下来的校验流程大概是：

a. 取ebx的最后一位作为索引，从新的数组中获取一个字符

b. 将新得到的字符拼接到正确序列号的字符串里

c. 然后删去最后一位，回到步骤1

###
![](https://image.3001.net/images/20220923/1663938525_632dafdd3c58ed67a39fc.png!small)

### 注册机

注册码生成算法：

#define _CRT_SECURE_NO_WARNINGS  
#include  
  
const char* arr = "LANNYDIBANDINGINANAKEKHYANGNGENTOT";  
const char* arr2 = "LANNY5646521";  
int main()  
{  
//char name[100] = { 0 };  
char name[] = "selph";  
char serial[100] = { 0 };  
int len = 0;  
int ebx = 0;  
  
for (int i = 0;name[i]; i++)  
{  
ebx += name[i];  
ebx <<= 8;  
  
ebx |= arr[i];  
if (ebx < 0) {  
ebx *= -1;  
}  
}  
ebx ^= 0x12345678;  
  
for (int i = 0; ebx; i++)  
{  
serial[i] = arr2[ebx % 10];  
ebx /= 10;  
}  
  
std::cout << serial << std::endl;  
}

效果：

![](https://image.3001.net/images/20220923/1663938526_632dafde1a8b0c8a309d1.png!small)

## 总结

比上一节看VB舒服多了，感觉这一节的难点在于分析理解这些反汇编是在干嘛的

# 5\. 040-DaNiEI-RJ1

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

怪怪的

![](https://image.3001.net/images/20220923/1663938526_632dafde8d66ab5bbf3ea.png!small)

点击File选项里的按钮才显示出来：

![](https://image.3001.net/images/20220923/1663938527_632dafdf14e32633ebd63.png!small)

### 查壳与脱壳：

##
![](https://image.3001.net/images/20220923/1663938527_632dafdf92186cb9e9037.png!small)

##

## 调试分析

Delphi程序：

常规的获取输入判断是否为空：

![](https://image.3001.net/images/20220923/1663938528_632dafe024dfc1ebff2f4.png!small)

然后是常规的根据Name计算校验码环节：

算法：遍历字符串，取每一个字节，+5

![](https://image.3001.net/images/20220923/1663938528_632dafe0dd4070f09627f.png!small)

然后是常规的比对环节

![](https://image.3001.net/images/20220923/1663938529_632dafe19c5cf2a896351.png!small)

### 注册机

注册码生成算法：（点快了创建成.NET6的了，干脆就用这个写了...）

string Name = Console.ReadLine();  
string Serial="";  
if (Name == null) return;  
  
for (int i = 0; i < Name.Length; i++)  
Serial += ((char)((int)Name[i] + 5)).ToString();  
  
Console.WriteLine(Serial);

效果：

##

##
![](https://image.3001.net/images/20220923/1663938530_632dafe253ea3ad17b7e9.png!small)

## 总结

普普通通，很基础


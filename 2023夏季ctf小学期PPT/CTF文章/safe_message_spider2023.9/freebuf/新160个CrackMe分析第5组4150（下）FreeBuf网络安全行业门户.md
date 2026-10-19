作者：selph

目录：

• 041-genocidel1

• 042-crackme2

• 043-riijj_cm_200411213

• 044-tsrh-crackme4

• 045-CyTom-crackme5

• 046-keyme16

• 047-surre7

• 048-monkeycrackme18

• 049-THraw-crackme89

• 050-daxxor10

## 参考资料

## – [1] WM_INITDIALOG消息(Winuser.h) - Win32 apps | Microsoft Docs

# 1\. 046-keyme1

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

真难得见到一次控制台程序：

![](https://image.3001.net/images/20221013/1665590811_6346e61bcc010c0254db3.png!small)

### 查壳与脱壳：

还带壳，ESP定律走起

![](https://image.3001.net/images/20221013/1665590812_6346e61c5691d2b496b38.png!small)

### 调试分析：

这里拿了一堆结构里的东西在做计算，直接F5看吧，方便一点：

刚开始拿结构里的东西计算了一个值，然后判断输入是否等于这个值，如果等于就成功

![](https://image.3001.net/images/20221013/1665590812_6346e61cec69836a4d9df.png!small)

这个VersionInformation结构体变量是在上面那个call401390里填充的：

![](https://image.3001.net/images/20221013/1665590813_6346e61d92a7e90a561f9.png!small)

### 注册机

注册码生成算法：

#define _CRT_SECURE_NO_WARNINGS  
#include  
#include  
#pragma warning(disable: 4996)  
  
int main()  
{  
OSVERSIONINFOA VersionInformation={0};  
VersionInformation.dwOSVersionInfoSize = 148;  
GetVersionExA(&VersionInformation);  
  
int key = VersionInformation.dwBuildNumber  
\+ VersionInformation.dwBuildNumber  
\+ VersionInformation.dwMajorVersion * VersionInformation.dwMinorVersion  
\- VersionInformation.dwMinorVersion  
\+ 3293 * VersionInformation.dwBuildNumber;  
printf("%d",key);  
system("pause");  
}  
  

效果：

![](https://image.3001.net/images/20221013/1665590814_6346e61e1f0d8ec6ffbb9.png!small)

2\. 047-surre

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

点击按钮会弹出打开文件的框

![](https://image.3001.net/images/20221013/1665590814_6346e61e98aa04d8fd7e5.png!small)

### 查壳与脱壳：

![](https://image.3001.net/images/20221013/1665590815_6346e61f30b1991786749.png!small)

调试分析

验证逻辑很简洁，就两件事：读取文件遍历每一个字符累加起来，判断累加和是否是20A9，是的话，表示验证成功，否则是失败

![](https://image.3001.net/images/20221013/1665590815_6346e61fbe39db2bd80ce.png!small)

### 注册机

注册码生成算法：

#include  
  
int main()  
{  
char serial[200] = { 0 };  
const int key = 0x20A9;  
for (int i = 0; i < key / 0x30; i++) serial[i] = '0';  
for (int i = 0; i < key % 0x30; i++) serial[i] += 1;  
std::cout << serial;  
}

效果：

![](https://image.3001.net/images/20221013/1665590816_6346e620a1d7e73298683.png!small)

# 3\. 048-monkeycrackme1

算法难度：⭐⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20221013/1665590817_6346e6213a76e75b5e2f7.png!small)

### 查壳与脱壳：

![](https://image.3001.net/images/20221013/1665590817_6346e621d4cf4b71b7334.png!small)

## 调试分析

程序验证逻辑很简单：

首先以硬编码0xce6d和0x58bf创建了一个对象结构，然后读取Name，计算一个字符串，然后读取Serial字符串，进行比对，一样则表示成功，否则表示失败

这里要注意，delphi使用的是32位的fastcall，传参顺序是eax，edx，ecx，栈，最后调用计算字符串的函数的时候，有一个栈中的参数

![](https://image.3001.net/images/20221013/1665590818_6346e622b1f015878a9eb.png!small)

计算逻辑也很简单：

首先保存变量，初始化输出缓冲区

然后计算Name长度，遍历每一个字符

对于每一个字符，和两字节变量右移8位后的结果异或一下，然后转换成十六进制（大写）拼接到输出缓冲区里

然后中间处理了一下两字节值，初值是4DE1是参数传入的，修改方式是使用异或后的一字节，加上原本的两字节值，然后乘以安全对象的第一个成员，最后加上安全对象的第二个成员的值（第一个成员的值和第二个成员的值可以通过动态调试得知，是固定值）

![](https://image.3001.net/images/20221013/1665590819_6346e623a66b90a365cc5.png!small)

### 注册机

注册码生成算法：

#define _CRT_SECURE_NO_WARNINGS  
#include  
typedef struct _TSecurity  
{  
_TSecurity(uint16_t a, uint16_t b) :vul1(a), vul2(b) {}  
uint16_t vul1;  
uint16_t vul2;  
}TSecurity,*PTSecurity;  
  
int main()  
{  
TSecurity obj(0xce6d,0x58bf);  
char name[100] = { 0 };  
short num = 0x4de1;  
char serial[100] = { 0 };  
char tmp[100] = { 0 };  
  
std::cin >> name;  
int len = strlen(name);  
for (int i = 0; i < len; i++)  
{  
uint8_t c = name[i] ^ (num >> 8);  
num = (c + num) * obj.vul1 + obj.vul2;  
sprintf(tmp, "%02X", c);  
strcat(serial, tmp);  
}  
  
std::cout << serial;  
  
}

效果：

![](https://image.3001.net/images/20221013/1665590820_6346e624b9d45e2bb351a.png!small)

# 4\. 049-THraw-crackme8

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20221013/1665590821_6346e62565acb15ec5ada.png!small)

### 查壳与脱壳：

UPX壳，ESP定律即可

![](https://image.3001.net/images/20221013/1665590821_6346e625ed5ad3503ab89.png!small)

## 调试分析

逻辑很简单，首先获取Name，然后处理一下

处理方式就是把每个字符的ascii转换成大写十六进制，然后拼接起来

![](https://image.3001.net/images/20221013/1665590822_6346e626a1705f8c7c946.png!small)

然后接下来使用一个全局变量，转换成字符串，然后再这个字符串之后拼接刚刚name转换的字符串，就是真码了

最后读取Serial，进行对比是否是真码，进行跳转

![](https://image.3001.net/images/20221013/1665590823_6346e627b5ddac03c06b5.png!small)

### 注册机

注册码生成算法：

var Serial = "1007689728";  
var Name = Console.ReadLine();  
for (int i = 0; i < Name.Length; i++)  
Serial += string.Format("{0:X2}", (int)Name[i]);  
Console.WriteLine(Serial);

效果：

![](https://image.3001.net/images/20221013/1665590824_6346e6287aad1df789548.png!small)

# 5\. 050-daxxor

算法难度：⭐⭐⭐

爆破难度：⭐⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20221013/1665590825_6346e629211aeeedad2af.png!small)

### 查壳与脱壳：

无壳：

![](https://image.3001.net/images/20221013/1665590825_6346e629a38d672c64a63.png!small)

## 调试分析

IDA打开程序分析，是个C++程序

搜索字符串发现提示信息：You solve it

然后根据提示信息定位到反汇编，F5一下偷个懒：

这里就是根据Name生成一个字符串，然后和Serial进行对比，只要按照生成顺序生成一个字符串，即是Serial

![](https://image.3001.net/images/20221013/1665590826_6346e62a4b1adf4a3f344.png!small)

注册机

###

注册码生成算法：

#include  
#include  
int main()  
{  
std::string name;  
  
std::cin >> name;  
for (int i = 0; i < name.length(); i++) name[i] -= 4;  
  
name.insert(3, "-");  
name.insert(5, "-");  
name.insert(6, "axd");  
  
std::cout << name;  
}

效果：

![](https://image.3001.net/images/20221013/1665590827_6346e62b07595126308a3.png!small)


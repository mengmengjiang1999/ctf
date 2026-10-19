## 1\. 051-Keygenning4newbies

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

  

![](https://image.3001.net/images/20221027/1666874663_635a7d279523431c4935f.png!small)

### 查壳与脱壳：

无壳。![](https://image.3001.net/images/20221027/1666874664_635a7d283d0d3fc5354a4.png!small)

## 调试分析

C++窗口程序：

首先跟进窗口函数。![](https://image.3001.net/images/20221027/1666874664_635a7d28d36dc4380f166.png!small)

然后是一段switch-case分支，或者是if-esle分支：根据消息码进入对应的处理，按钮的处理消息是WM_COMMAND，对应的值就是0x111。![](https://image.3001.net/images/20221027/1666874665_635a7d2990ee2430dc5ef.png!small)

然后wParam是控件的id号，这里通过xspy发现验证按钮的id号是0x69，跟进这个0x69的跳转。![](https://image.3001.net/images/20221027/1666874666_635a7d2a41cbfd7dbf80b.png!small)

这里调用了一个call就跳出了：

![](https://image.3001.net/images/20221027/1666874666_635a7d2ae0e609d602e86.png!small)

这个call
应该就是验证处理，前面初始化局部变量和获取控件值就不看了，这里两个红圈就是注册码生成逻辑，用Name计算一个值，然后变成十六进制字符串形式。![](https://image.3001.net/images/20221027/1666874667_635a7d2b8a3734911c255.png!small)

### 注册机

注册码生成算法：（CSharp）

string? Name = Console.ReadLine();  
if(Name!=null && Name.Length is > 3 and < 32)  
{  
int ebx=0;  
int eax=0;  
for (int i = 0; i < Name.Length; )  
{  
eax = (int)Name[i++];  
eax ^= i;  
ebx += eax;  
}  
  
eax *= 6;  
ebx <<= 7;  
eax += ebx;  
Console.WriteLine(string.Format("{0:X}", eax));  
}

效果：![](https://image.3001.net/images/20221027/1666874669_635a7d2d6cc0ae06fdbee.png!small)

## 2\. 052-tc.2

算法难度：⭐⭐⭐⭐

爆破难度：⭐⭐⭐

## 信息收集

###
运行情况：![](https://image.3001.net/images/20221027/1666874670_635a7d2e341f840ce23ef.png!small)

### 查壳与脱壳：

![](https://image.3001.net/images/20221027/1666874670_635a7d2ebeeed833195b4.png!small)

## 调试分析

老版本delphi看着就烦。

### 构造正确的keyfile

首先是打开文件，读取其中的内容，对比内容是否为这个固定值。

![](https://image.3001.net/images/20221027/1666874671_635a7d2f6d20b170a6d0a.png!small)

然后判断内容的长度，内容的长度为固定值0x17字节。

![](https://image.3001.net/images/20221027/1666874672_635a7d3024e06f6d37217.png!small)

条件满足了就会启用编辑框和注册按钮：

  

![](https://image.3001.net/images/20221027/1666874672_635a7d30d40959000c232.png!small)

### 校验算法分析

这个call里有一堆代码不知道在干嘛，可能是编译器自动生成的吧，这里就挑有用的看。

首先是这里，这里是个循环，这个ReadChar函数盲猜是读取Name的一个字节，然后保存到局部变量ebp-0D里。

然后取出读取的这一个字节，和初值是0的bl进行一系列计算，得到一个值，将这个值累加到si里，对于每个字符都这么操作。

最后判断si的值是否大于一个固定值，否则就加上一个固定值。![](https://image.3001.net/images/20221027/1666874673_635a7d31635b27c0ca8f8.png!small)

再往后就是生成真码和比较的过程了：

首先将计算出来的累加值si转字符串，然后往第3和第5个字符处插入-符号，然后就是比对和输入是否相同，不同就跳转，相同就提示成功。

![](https://image.3001.net/images/20221027/1666874674_635a7d3221fb877b1bec1.png!small)

### 注册机

注册码生成算法：（CSharp）

string? name = Console.ReadLine();  
byte bl = 0;  
var si = 0;  
for(byte i = 1; i <= name.Length; i++)  
{  
byte tmp = (byte)name[i-1];  
bl -= tmp;  
bl += i;  
si += bl;  
}  
  
while (si < 0x438D) si += 0x45e6;  
  
var serial = string.Format("{0:D}", si);  
serial = serial.Insert(2, "-");  
serial = serial.Insert(4, "-");  
  
Console.WriteLine(serial);

效果：![](https://image.3001.net/images/20221027/1666874674_635a7d32bedb5e5ea7dc8.png!small)总结

分析无意义的代码真是浪费时间！应该从判断条件开始自下往上去分析！

# 3\. 053-devilz KeyGen me#3

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20221027/1666874676_635a7d34c834e6a0a0b51.png!small)

### 查壳与脱壳：

有壳！Petite壳，第一次见，试着脱一下。

![](https://image.3001.net/images/20221027/1666874677_635a7d355b88ef4ad44f5.png!small)

首先跑到当前的OEP：

很明显这里有一个注册SEH异常处理程序的，然后就是保存当前寄存器环境，等壳解压解密完再恢复用

这里等pushf指令执行之后，对esp的地址下硬件访问断点。

![](https://image.3001.net/images/20221027/1666874677_635a7d35ce8e4f826a7c0.png!small)

因为这里用到了异常，所以这里在x86dbg设置里把异常处理设置成由debugee处理

然后跑起来，遇到异常了直接接着跑，跑到硬件断点处：

很显然，这可能应该就是真正的OEP了。

![](https://image.3001.net/images/20221027/1666874678_635a7d365d02977ca8f63.png!small)

跟进查看：

这就是一个注册窗口的函数和退出进程的函数，确定了，这就是真正的OEP，接下来用插件脱壳即可。

![](https://image.3001.net/images/20221027/1666874678_635a7d36ee76d03754bd9.png!small)

## 调试分析

ida打开继续分析：![](https://image.3001.net/images/20221027/1666874679_635a7d37761585e71dc97.png!small)

跟进DialogFunc，找到nMsg = 111，且arg_8 = 0x12c的分支（Unlock按钮ID）继续跟进：

显示判断输入是否为空，有些函数没识别全，应该是导入表没修复好。

![](https://image.3001.net/images/20221027/1666874681_635a7d39e42b4a3165ce7.png!small)

接下来是对Name的处理：

反转字符串，然后对每个字符进行异或0x30。

![](https://image.3001.net/images/20221027/1666874682_635a7d3a9f701e270e9f0.png!small)

然后是对UnlockCode的处理：

遍历每个字符，对每个字符异或0x20，最后和各个处理过的Name进行比对，相同即可。

![](https://image.3001.net/images/20221027/1666874683_635a7d3b6b5046df19c8d.png!small)

### 注册机

注册码生成算法：（CSharp）

string? name = Console.ReadLine();  
char[] UnlockCode = name.ToCharArray();  
Array.Reverse(UnlockCode);  
  
for (int i = 0; i < UnlockCode.Length; i++)  
{  
UnlockCode[i] = (char)(UnlockCode[i] ^ 0x30);  
UnlockCode[i] = (char)(UnlockCode[i] ^ 0x20);  
}  
  
Console.WriteLine(UnlockCode);

效果：![](https://image.3001.net/images/20221027/1666874684_635a7d3c4a00b37b16ba2.png!small)

## 4\. 054-vcrkme01

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20221027/1666874685_635a7d3d62c8d8f798ed1.png!small)

### 查壳与脱壳：

无壳：

![](https://image.3001.net/images/20221027/1666874686_635a7d3ee87016b30ba77.png!small)

## 调试分析

直接拖IDA：

一开始就看到创建窗口的函数。

![](https://image.3001.net/images/20221027/1666874688_635a7d40e4f9ddb90c59e.png!small)

接下来直接跟进DialogFunc找nMsg=0x111，arg_8=3eb的分支：

获取用户输入的两个值，调用了一个call，然后根据返回结果是否为1进行弹框。

![](https://image.3001.net/images/20221027/1666874689_635a7d418bedc28701335.png!small)

跟进这个call看看：

由于库函数的内联汇编看得头疼，直接F5看吧：

![](https://image.3001.net/images/20221027/1666874690_635a7d42c3908a1cec3d6.png!small)

### 注册机

注册码生成算法：（CSharp）

string? name = Console.ReadLine();  
int sum = 0;  
for (int i = 0; i < name.Length; i++) sum += name[i];  
  
sum += 0x6064;  
string? Buffer = string.Format("{0:D}", sum);  
char[] code = new char[1024];  
code[0] = name[0];  
code[1] = '-';  
code[2] = char.ToUpper(name[name.Length - 1]);  
  
var code_s = new string(code);  
code_s += Buffer;  
code_s += '-';  
code_s += string.Format("{0:D}", sum += 0x6064);  
  
Console.WriteLine(code_s);

效果：

![](https://image.3001.net/images/20221027/1666874691_635a7d437a69a4b3c4884.png!small)

# 5\. 055-BCG Crackme

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

意思是不能爆破，不能修改内存，并完成破解，意思就是通过给出正确的key文件呗。

![](https://image.3001.net/images/20221027/1666874692_635a7d44485d01d97fe92.png!small)

### 查壳与脱壳：

ASPack壳，ESP定律即可。

![](https://image.3001.net/images/20221027/1666874693_635a7d45464a530c20e54.png!small)

## 调试分析

不管是窗口启动还是点击注册按钮，都会跳转到同一段代码上，这里是个文件验证：打开文件[BCG].Key，然后读取前10个字节，和紧接着10个字节。![](https://image.3001.net/images/20221027/1666874693_635a7d45e2c07211df691.png!small)

读取成功后，往下走：

这里是处理前10个字节，每个字节异或一下0x58，直到遇到0为止。这意味着，我们构造的文件里需要出现00截断。

![](https://image.3001.net/images/20221027/1666874694_635a7d46df15f2922dceb.png!small)

###
Key文件![](https://image.3001.net/images/20221027/1666874695_635a7d47742f12a37139f.png!small)

效果：![](https://image.3001.net/images/20221027/1666874696_635a7d4805351260777e4.png!small)

  


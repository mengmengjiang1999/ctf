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

016-020请看下期

# 1\. 011-wocy.1

算法难度：⭐

爆破难度：⭐

信息收集

运行情况：

  

![](https://image.3001.net/images/20220908/1662608442_6319643aefc97c9465f0d.png!small)

  

  

### 查壳与脱壳：

MFC程序，无壳

  

![](https://image.3001.net/images/20220908/1662608443_6319643baeca208c3d379.png!small)

  

  

### 查字符串：

提示字符串：Registed

  

![](https://image.3001.net/images/20220908/1662608444_6319643c4a8d7b38eb361.png!small)

  

  

## 调试分析

老样子，从关键提示字符串入手，交叉引用查校验函数

这里函数里不知道这个[esi+60h]和[esi+64h]，通过动态调试执行可知，这里是分别获取的用户名和ID号，然后验证逻辑就很简单了，用户名和ID号需要是倒序的即可

  

![](https://image.3001.net/images/20220908/1662608444_6319643cccef406158613.png!small)

  

  

结果：

  

![](https://image.3001.net/images/20220908/1662608445_6319643d807df5b077193.png!small)

  

# 2\. 012-ACG-crcme1

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

  

![](https://image.3001.net/images/20220908/1662608446_6319643e4783f47eb2457.png!small)

  

### 查壳与脱壳：

无壳

  

![](https://image.3001.net/images/20220908/1662608446_6319643edd10436eeba3a.png!small)

  

### 查字符串：

有很多看不懂的提示语，还有个文件名

  

![](https://image.3001.net/images/20220908/1662608447_6319643f7bba5a04e2112.png!small)

  

## 调试分析

抄起IDA直接干，用户函数就3个，这么简洁这应该是纯汇编写的程序吧（猜的），从start开始分析

  

![](https://image.3001.net/images/20220908/1662608448_631964401c6ec19701288.png!small)

  

  

首先打开一个文件，读取其中的内容，该内容应该长度是12字节：

![](https://image.3001.net/images/20220908/1662608448_6319644096f202da570a3.png!small)

  

  

然后就像下面这样，对12个字节的每个字节进行一个运算，逐一校验结果

![](https://image.3001.net/images/20220908/1662608449_6319644156423d8afc16e.png!small)

  

  

然后接下来就是，如果验证全部通过，就弹窗提示ok，否则就直接启动窗口

### 暴力破解

把所有判断跳转都nop掉即可

### 算法分析

序列号运算的核心是异或，异或是可逆的，所以可以反着把序列号生成出来：

#include  
  
int main()  
{  
int arr[12] = {
0x168,0x160,0x170,0xec,0x13c,0x1cc,0x1f8,0xec,0x164,0x1f8,0x1a0,0x1bc };  
int serial[12] = { 0 };  
for (int i = 0; i < 12; i++)  
{  
serial[i] ^= arr[i];  
serial[i] >>= 2;  
serial[i] = serial[i]&0x000000FF ^ 0x1b;  
}  
for(char var : serial)  
{  
printf("%c",var);  
}  
}

计算结果是：ACG The Best

执行结果：

![](https://image.3001.net/images/20220908/1662608450_631964420b182ce798870.png!small)

  

  

  

  

  

  

## 总结

很简单无脑的一次算法分析

# 3\. 013--Acid_burn

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

原160个CM的第一个，以前做过一遍，老费劲了，现在再来一遍看看

暴力破解已经懒得介绍了，看得懂完整分析也肯定知道该改哪里了

### 运行情况：

启动的时候有Nag：

![](https://image.3001.net/images/20220908/1662608450_631964428185c7d6b1cfd.png!small)

  

  

提供了两种注册方法：用户名+序列号，序列号

  

![](https://image.3001.net/images/20220908/1662608451_63196443074967e5eea63.png!small)

  

### 查壳与脱壳：

无壳：Delphi程序

![](https://image.3001.net/images/20220908/1662608451_63196443c43c346220a5e.png!small)

  

## 调试分析

分析Delph GUI程序借助IDR辅助方便查看窗口事件（ **纯** **IDA** **分析的话，查字符串交叉引用定位也能找到这些函数** ）

首先是启动窗口：窗口启动的时候调用FromCreate函数里，执行流MessageBox，这就是所谓的NAG，烦人弹窗

  

![](https://image.3001.net/images/20220908/1662608452_631964445f4786fce77f7.png!small)

  

  

然后是序列号验证：

  

![](https://image.3001.net/images/20220908/1662608453_631964451bfbaddf70a1c.png!small)

  

  

接下来是用户名+序列号验证：

首先对用户名4个字节进行一顿处理，然后把值保存起来，用户名必须大于等于4个字符

这里开头往[431750]赋了个初始值：0x29

  

![](https://image.3001.net/images/20220908/1662608453_63196445e12abe461dded.png!small)

  

  

  

  

  

接下来计算序列号，然后跟用户输入比对

  

![](https://image.3001.net/images/20220908/1662608454_63196446e876376501852.png!small)

  

  

### 去除NAG

去除Nag只需要修改该函数直接返回即可：

  

![](https://image.3001.net/images/20220908/1662608455_63196447ddf100c86951b.png!small)

  

  

### 算法分析

序列号验证：硬编码验证，输入Hello Dude!即可

![](https://image.3001.net/images/20220908/1662608456_631964487b0b9f84cacde.png!small)

  

  

用户名+序列号验证，序列号可以写出注册机：

#include  
  
int main()  
{  
int res = 0x29;  
char name[20] = {0};  
  
std::cin >> name;  
res = name[0] * res * 2;  
  
std::cout <<"CW"<<"-" << res << "-" <<"CRACKED";  
}

  

![](https://image.3001.net/images/20220908/1662608457_6319644950740768d61b7.png!small)

  

## 总结

以前做半天，现在分析起来很快啊，对于特定语言的逆向，如果能有对应的工具帮助识别函数功能，那简直是帮大忙了

PS：用户名+序列号验证这里先校验了用户名长度，校验的时候计算了一堆中间值，真的一点用没有！！！

# 4\. 014-Splish

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

开始有个启动屏幕，然后进入程序主界面

按照说明，目标是禁用启动屏幕，完成硬编码校验，写用户名序列号注册机

![](https://image.3001.net/images/20220908/1662608458_6319644a3e67ac8d5dfa2.png!small)

![](https://image.3001.net/images/20220908/1662608458_6319644ab587c1fceee56.png!small)

  

  

  

  

查壳与脱壳：

###

无壳：

![](https://image.3001.net/images/20220908/1662608459_6319644b38d8da54ed077.png!small)

  

## 调试分析

用户函数比较少，直接从起点硬刚：

这个call应该就是程序的入口了

  

![](https://image.3001.net/images/20220908/1662608459_6319644bb8e4962d4ac34.png!small)

  

这个call里面就进入窗口消息循环了，在那之前调用了几个用户函数：

  

有一个是对参数进行处理的，有一个call的参数是实例句柄，很可疑，进入查看

、

![](https://image.3001.net/images/20220908/1662608460_6319644c53b6f816e8cc9.png!small)

  

  

  

  

这里头是创建了一个窗口，然后延时关闭，要去除NAG，直接把这个函数处理了就好：

  

![](https://image.3001.net/images/20220908/1662608461_6319644d1b2b90d4ed09e.png!small)

  

  

然后找到一个函数貌似是消息处理函数：这里根据参数的Msg号进行跳转执行

  

![](https://image.3001.net/images/20220908/1662608461_6319644dccfa64a41100c.png!small)

  

往下找，发现硬编码check分支：将用户输入和硬编码：HardCoded进行比对，一致了跳转

  

![](https://image.3001.net/images/20220908/1662608462_6319644e69031d35c367c.png!small)

  

  

一致了跳转的最终位置是，说明这里硬编码已经找到了：

  

![](https://image.3001.net/images/20220908/1662608463_6319644f1751e03e36c9f.png!small)

  

  

接下来找找用户名序列号验证：

验证会进行三次计算，首先是计算用户名得到一个结果：

  

![](https://image.3001.net/images/20220908/1662608463_6319644f9fa8dc90dc7a5.png!small)

  

  

  

  

然后计算序列号得到一个结果：

  

![](https://image.3001.net/images/20220908/1662608464_6319645043d7531228521.png!small)

  

  

最后将两个运算结果进行比对：

  

![](https://image.3001.net/images/20220908/1662608464_63196450dcc4266a1b36c.png!small)

  

### 算法分析

拿用户名计算一个结果，跟序列号计算一个结果进行比对的验证逻辑，写注册机的话则是先用用户名计算一个结果，然后用这个结果反推序列号

#include  
  
int main()  
{  
const char* num = "2345678901";  
char serial[20] = { 0 };  
char name[20] = { 0 };  
char name_res[20] = { 0 };  
int len = 0;  
  
std::cin >> name;  
len = strlen(name);  
//std::cin >> serial;  
  
for (int i = 0; i < len; i++)  
{  
name_res[i] = name[i] % 0xA;  
name_res[i] ^= i;  
name_res[i] += 2;  
if (name_res[i] > 0xA)name_res[i] -= 0xA;  
}  
  
//for (int i = 0; i < len; i++)  
//{  
// serial_res[i] = serial[i] % 0xA;  
//}  
  
for (int i = 0; i < len; i++)  
{  
serial[i] = num[name_res[i]];  
}  
  
std::cout << serial << std::endl;  
}

结果：

  

![](https://image.3001.net/images/20220908/1662608465_6319645192d07ba1e99cd.png!small)

  

  

  

## 总结

算是个编写注册机的练习，这个cm中练习了汇编转C的操作

# 5\. 015-BradSoblesky.1

算法难度：⭐

爆破难度：⭐

## 信息收集

### 运行情况：

序列号验证：

![](https://image.3001.net/images/20220908/1662608466_631964523ffd1db3427f0.png!small)

  

### 查壳与脱壳：

MFC程序，无壳：

  

![](https://image.3001.net/images/20220908/1662608466_63196452e066b9f0f2ca4.png!small)

  

### 查字符串：

存在提示信息：

  

![](https://image.3001.net/images/20220908/1662608467_6319645369babd9ee2ebe.png!small)

  

## 调试分析

硬编码字符串和用户输入字符串比对，没啥好说的

  

![](https://image.3001.net/images/20220908/1662608467_63196453e6012a239cd12.png!small)

  

结果：

![](https://image.3001.net/images/20220908/1662608468_63196454cc562abbc99d9.png!small)​


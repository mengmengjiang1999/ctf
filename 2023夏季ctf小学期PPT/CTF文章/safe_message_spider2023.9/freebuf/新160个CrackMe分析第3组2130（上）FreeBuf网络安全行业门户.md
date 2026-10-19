**​作者：selph**

目录：

• 021-DIS-Serialme1

• 022-CM_22

• 023-TraceMe3

• 024-reverseMe4

• 025-CRC32crackme5

• 026-KeygenMe6

• 027-MexeliteCRK17

• 028-ArturDents-CrackMe38

• 029-figugegl19

• 030-AcidBytes410

下半篇请看下期

# 1\. 021-DIS-Serialme

爆破难度：⭐

算法难度：⭐⭐

## 信息收集

### 运行情况：

  

![](https://image.3001.net/images/20220914/1663165201_6321e31115d61ea94b7c7.png!small)

  

### 查壳与脱壳：

无壳，汇编程序

![](https://image.3001.net/images/20220914/1663165201_6321e311ba06f5baaeffb.png!small)

## 调试分析

使用xspy工具可以很方便的查看GUI程序的控件ID：

![](https://image.3001.net/images/20220914/1663165202_6321e312575539ea59421.png!small)

在窗口过程里，发现保存编辑框内容的部分：根据控件ID判断哪个接收的是哪个值，然后这里会判断NAME需要大于3字节

![](https://image.3001.net/images/20220914/1663165202_6321e312dc20331331d68.png!small)

然后接下来在验证逻辑里：

对于用户名的每个字节，取出来原字节保存在bl，然后保存一个该字符的索引+a的值到bh里

对于序列号，每次取出两个字节到cx

比对bx和cx，如果遍历完用户名全都相同，就是成功

![](https://image.3001.net/images/20220914/1663165203_6321e31396ec3f224945f.png!small)

### 注册机

注册码生成算法：

    
    
    #include
    int main()
    {
    char name[20] = "selph";
    char serial[20] = { 0 };
    int Len = strlen(name);
    
    for (int i = 0, j = 0; i < Len; i++, j+=2)
    {
    char bl=0, bh=0;
    bl = name[i];
    bh = i + 'a';
    serial[j] = bl;
    serial[j + 1] = bh;
    }
    std::cout << serial;
    }

结果：

![](https://image.3001.net/images/20220914/1663165204_6321e31471f73d7b31421.png!small)

## 总结

依然是很简单的算法分析

# 2\. 022-CM_2

算法难度：⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220914/1663165205_6321e31569ad2418ef063.png!small)

### 查壳与脱壳：

MFC程序，无壳：

![](https://image.3001.net/images/20220914/1663165206_6321e31610811854f7700.png!small)

### 字符串：

存在提示信息字符串：

![](https://image.3001.net/images/20220914/1663165206_6321e316a2a89b920d43b.png!small)

## 调试分析

通过字符串交叉引用搜索校验函数，看图，没啥好说的：

先获取用户名序列号长度，都得大于5，然后明文硬编码校验序列号：6287-A

![](https://image.3001.net/images/20220914/1663165207_6321e3173ab90588b7f15.png!small)

结果：

![](https://image.3001.net/images/20220914/1663165207_6321e317e63cc26a01447.png!small)

# 3\. 023-TraceMe

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

看标语，这是个来自看雪论坛的CM

![](https://image.3001.net/images/20220914/1663165208_6321e318a93955cdf011b.png!small)

### 查壳与脱壳：

C++的GUI程序，无壳

![](https://image.3001.net/images/20220914/1663165209_6321e31935141d75d120e.png!small)

## 调试分析

程序一进去就是WinMain，这里的这个参数是窗口过程，从这里找内容：

![](https://image.3001.net/images/20220914/1663165209_6321e319b599ae0b77605.png!small)

窗口过程函数里，往下面拉一点就能看到获取控件内容的API，分别获取Name和Serial，然后调用了函数sub_401340，这应该就是校验函数了

![](https://image.3001.net/images/20220914/1663165210_6321e31a5bad90a765a4a.png!small)

校验函数分析：这里有一个硬编码的字节数组，从索引0开始，每轮循环+1，遍历用户名的索引从3开始，每轮循环+1

每次索引到一个用户名中的值和一个硬编码字节数组的值，然后相乘，

把每轮的结果加起来，转换成字符串与输入的序列号进行对比，相同则表示校验成功

![](https://image.3001.net/images/20220914/1663165211_6321e31b00c8f9a9ec2ca.png!small)

注册码生成算法：

    
    
    #define _CRT_SECURE_NO_WARNINGS
    #include
    
    int main()
    {
    char name[10] = "selph";
    char arr[8] = { 0xC, 0xA, 0x13, 0x9, 0xC, 0xB, 0xA, 0x8 };
    char serial[20] = { 0 };
    int sum = 0;
    
    for (int i = 3,j=0; name[i]; i++,j++)
    {
    if (j > 7)j = 0;
    sum += name[i] * arr[j];
    }
    sprintf(serial, "%ld", sum);
    std::cout << serial;
    }

结果：

![](https://image.3001.net/images/20220914/1663165211_6321e31b9e53b8bd2002a.png!small)

# 4\. 024-reverseMe

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

弹窗说过期了，然后进程退出了

![](https://image.3001.net/images/20220914/1663165212_6321e31c3dc8c34688902.png!small)

### 查壳与脱壳：

无壳：

![](https://image.3001.net/images/20220914/1663165212_6321e31cc709155568c93.png!small)

## 调试分析

首先是打开一个文件，如果不存在就弹窗提示失败，存在的话就读取内容

![](https://image.3001.net/images/20220914/1663165213_6321e31d60920c0f303ed.png!small)

然后是校验环节，首先判断读取的字节数，文件的字节数应该超过16字节，然后遍历字符串计算G的数量，这个数量大于8即可成功

![](https://image.3001.net/images/20220914/1663165214_6321e31e3892dd961152e.png!small)

文件内容：GGGGGGGGGGGGGGGGGGGG，效果：

![](https://image.3001.net/images/20220914/1663165214_6321e31eed81833b52a41.png!small)

# 5\. 025-CRC32crackme

算法难度：⭐⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220914/1663165215_6321e31f76c44795516da.png!small)

### 查壳与脱壳：

依然是古老的程序

![](https://image.3001.net/images/20220914/1663165216_6321e3201bead16646eb4.png!small)

## 调试分析

因为拖到IDR识别不出来Form，我以为不是Delphi程序，导致在分析的时候发现各种奇怪不对劲，实际上这依然是个Delphi程序，使用eax，edx传参函数调用，字符串使用结构体保存，第一个成员是字符串长度，第二个成员才是字符串

通过搜索MessageBox函数的交叉引用定位到校验函数：刚好只有2个，对应两种情况的弹窗

![](https://image.3001.net/images/20220914/1663165216_6321e3209a83ddd165cdd.png!small)

接下来从头开始分析

### 对用户名的处理

首先是对Name的处理，这里是先获取Name长度初始化了一个字符串结构，然后读取字符串赋值，

如果字符串长度小于5，则跳转到失败分支，

字符串拼接：DiKeN拼接到Name前面，例如DiKeNselph

最后使用这个拼接后的结果，计算一个长度，去调用一个函数计算一个值，用于最后比对使用

![](https://image.3001.net/images/20220914/1663165217_6321e32118bbde3722080.png!small)

计算用户名校验值的函数进行的是CRC32算法，和这个CM的名称一样：

截图的底下是CRC32Table数组，用来简化计算使用的，就不完整复制了，具体算法下文实现注册机时给出高级语言实现，这里就不解释了

![](https://image.3001.net/images/20220914/1663165217_6321e321df63d618e7251.png!small)

### 对序列号的处理

对用户名的处理结果保存在了esi里

接下来是对序列号的处理：首先从控件读取用户输入的字符串，然后拼接了一个0到字符串前面，最后调用一个函数来计算序列号的校验值

![](https://image.3001.net/images/20220914/1663165218_6321e322b397d8495e3b5.png!small)

sub_404224，序列号的校验值计算：

获取字符串长度循环遍历，累加值sum初值为0，每一轮循环进行的操作是：

计算sum*2，然后计算sum+sum*4，获取字符串一个字符，字符数字变成数字（-'0'），然后加到sum里

![](https://image.3001.net/images/20220914/1663165219_6321e32393166343f98c3.png!small)

### 暴力破解

最后拿序列号计算的结果（eax）和用户名计算的结果（esi）进行比较，相同则弹窗成功，爆破的点也就在这里

![](https://image.3001.net/images/20220914/1663165220_6321e32433da03ec14f6d.png!small)

### 注册机

最近初学CSharp语言，用一次练练手：

 **本段有违规文字获取全部内容请移步到公众号——极安御信安全研究院查询**

效果：

![](https://image.3001.net/images/20220914/1663165220_6321e324e699a595abb2f.png!small)

## 总结

逆向一个程序的时候，如果能了解这个语言的各种基本操作都是怎么进行的，就会方便很多，还有就是函数调用约定

难倒是不难，就是乱七八糟的函数搞得人晕头转向


作者：selph

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

前半篇请看上集

# 1\. 026-KeygenMe

算法难度：⭐⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220914/1663168113_6321ee71e380a5eedb199.png!small)

### 查壳与脱壳：

识别的是UPX壳，实际上则无壳，识别错误应该是

![](https://image.3001.net/images/20220914/1663168114_6321ee72d953ef9755558.png!small)

## 调试分析

通过MessageBox函数交叉引用定位校验的位置，就分析主要逻辑吧，前面那些初始化无关紧要

前面省略了给Name和Serial赋值的API调用，直接从校验逻辑开始看

这里获取Name字符串长度遍历计算使用

然后一个循环，计算一个累加值到esi

每一轮取一个字符到ebx，累加ebx平方，累加ebx右移一位后+3后乘以ebx再减去ebx，然后esi乘以2（这样描述不清楚，具体看下文反汇编注释和注册机代码）

最后算出一个累加值和序列号字符串进行对比，没看错，是直接和字符串对比，输入的字符串会直接当成数字对待

![](https://image.3001.net/images/20220914/1663168115_6321ee7371381bfafb3d1.png!small)

输入的字符，这里esi是计算出来的累加和，下面那一行是输入的序列号，直接用ascii当数字来对比了！！！

![](https://image.3001.net/images/20220914/1663168116_6321ee745c1a6b9070d4b.png!small)

### 注册机

注册码生成算法：因为对输入的用户名有要求，太长太短都不行，还得是能满足要求的字符，所以这里就使用随机字符串来生成满足要求的Name：

    
    
    #define _CRT_SECURE_NO_WARNINGS
    #include
    #include
    #include
    #define Random(x)(rand()%x) // 生成x以内的随机数  
    // 参数：生成随机字符串长度  
    void GetRandomString(LPSTR str,SIZE_T nLength) {  
    srand((int)time(NULL)); // 随机数种子  
    for (size_t i = 0; i < nLength; i++) {  
    switch (Random(2)){  
    case 0: str[i] = 'a' + Random(26); break;  
    case 1: str[i] = 'A' + Random(26); break;  
    default: break;  
    }  
    }  
    }  
      
    bool SerialCheck(char* serial) {  
    bool res = true;  
    for (int i = 0; i < 3; i++) {  
    char tmp = serial[i];  
    if (0x21 <= tmp && tmp <= 0x7E) continue;  
    res = false;  
    break;  
    }  
    return res;  
    }  
      
    int main()  
    {  
    int esi = 0;  
    char name[20] = { 0 };  
    char serial[20] = { 0 };  
    bool flag = false;  
      
    while (!flag) {  
    memset(name, 0, sizeof(name));  
    GetRandomString(name, 7);  
    esi = 0;  
    for (int i = 0; name[i]; i++)  
    {  
    int ebx = name[i];  
    esi += ebx * ebx;  
    esi += ebx * ((ebx >> 1) + 2);  
    esi += esi;  
    }  
    *(int*)&serial = esi;  
    if (SerialCheck(serial)) {  
    std::cout << name << std::endl;  
    std::cout << serial;  
    break;  
      
    }  
    }  
    }

效果：

![](https://image.3001.net/images/20220914/1663168116_6321ee74dff85d98bcebc.png!small)

## 总结

算法不难，但写注册机还是有些麻烦的

# 2\. 027-MexeliteCRK1

算法难度：⭐

爆破难度：⭐

## 信息收集

### 运行情况：

输入序列号，下面那个框显示状态

![](https://image.3001.net/images/20220914/1663168117_6321ee758e493b1558769.png!small)

### 查壳与脱壳：

无壳，是Delphi程序

![](https://image.3001.net/images/20220914/1663168118_6321ee76136b84f8f2959.png!small)

## 调试分析

硬编码序列号验证

![](https://image.3001.net/images/20220914/1663168118_6321ee769cb1f6d5754ab.png!small)

效果：

![](https://image.3001.net/images/20220914/1663168119_6321ee7730f56b83515dd.png!small)

# 3\. 028-ArturDents-CrackMe3

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220914/1663168119_6321ee77a862cb28cf2d3.png!small)

### 查壳与脱壳：

一个没见过的壳出现了，Petite壳，老样子，依然是ESP定律可以解决

![](https://image.3001.net/images/20220914/1663168120_6321ee7839fbc6818bfb6.png!small)

## 调试分析

Delphi程序，通过IDR反汇编找到按钮控件事件，然后复制出来分析

首先是获取输入，Name长度和Serial长度不能为0

![](https://image.3001.net/images/20220914/1663168120_6321ee78c88ac9545e86f.png!small)

接下来紧接着是序列号生成：根据Name生成一个字符串

![](https://image.3001.net/images/20220914/1663168121_6321ee797803e65a16785.png!small)

最后是比对环节：

![](https://image.3001.net/images/20220914/1663168122_6321ee7a1d4d3e1a50676.png!small)

### 注册机

注册码生成算法：

    
    
    #define _CRT_SECURE_NO_WARNINGS
    #include
    
    int main()
    {
    char name[100] = { 0 };
    char num[100] = { 0 };
    
    std::cin >> name;
    for (int i = 0; i < strlen(name); i++)
    {
    char tmp_str[100] = { 0 };
    _itoa(name[i] / 3, tmp_str, 10);
    strcat(num, tmp_str);
    }
    
    std::cout << "ADCM3-" << num << std::endl;
    return 0;
    }

效果：

![](https://image.3001.net/images/20220914/1663168122_6321ee7abe7da4643a858.png!small)

# 4\. 029-figugegl1

算法难度：⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220914/1663168123_6321ee7bc108182f68bb6.png!small)

### 查壳与脱壳：

无壳

![](https://image.3001.net/images/20220914/1663168124_6321ee7c4b40fecc44fe6.png!small)

### 字符串：

存在提示信息：

![](https://image.3001.net/images/20220914/1663168125_6321ee7d12df496c3c232.png!small)

## 调试分析

从字符串提示入手，找到校验点开始分析

首先是获取输入，用户名需要长度大于等于5

![](https://image.3001.net/images/20220914/1663168125_6321ee7d8e95c456c7690.png!small)

然后是校验和对比了：

校验算法：Serial == Name[i]-i

![](https://image.3001.net/images/20220914/1663168126_6321ee7e30c3ed5151091.png!small)

简单到可以口算的序列号生成：12345：11111

效果：

![](https://image.3001.net/images/20220914/1663168126_6321ee7ecf59ccdaa764c.png!small)

### 注册机

注册码生成算法：

    
    
    #include
    
    int main()
    {
    char serial[100] = { 0 };
    char name[100] = { 0 };
    std::cin >> name;
    for (int i = 0; name[i]; i++)
    {
    serial[i] = name[i] - i;
    }
    std::cout << serial;
    }

# 5\. 030-AcidBytes4

算法难度：⭐⭐⭐

爆破难度：⭐

## 信息收集

### 运行情况：

![](https://image.3001.net/images/20220914/1663168127_6321ee7f65538e68f8a23.png!small)

### 查壳与脱壳：

UPX，无脑ESP定律即可

![](https://image.3001.net/images/20220914/1663168128_6321ee8012f3bbb5d882e.png!small)

## 调试分析

Delphi程序，IDR走起

首先是获取Name和Serial校验长度

![](https://image.3001.net/images/20220914/1663168128_6321ee80a0a5283ed7427.png!small)

然后是进行一个计算，根据Name计算Serial：

相同的操作会进行6次：取一个字节，乘以2，然后累加起来，会操作的就是Name的前6个字符

![](https://image.3001.net/images/20220914/1663168129_6321ee815a98306961745.png!small)

最后把这个累加值保存起来，给这个累加值加上个Name长度的两倍，转字符串（十进制，就是真码了

![](https://image.3001.net/images/20220914/1663168130_6321ee821151d6bfc68f5.png!small)

### 注册机

注册码生成算法：

    
    
    #include
    
    int main()
    {
    char name[100] = { 0 };
    int sum = 0;
    
    std::cin >> name;
    for (int i = 0; i < 6; i++) sum += name[i] * 2;
    sum += strlen(name)*2;
    
    if (sum >> 0x1f == 0)std::cout << sum;
    }

结果：

![](https://image.3001.net/images/20220914/1663168130_6321ee82d646ccab59f00.png!small)

## 总结

又是这种，把能写进循环的东西写了超级多段落，不难，只要有Delphi的符号，分析起来还是挺快的


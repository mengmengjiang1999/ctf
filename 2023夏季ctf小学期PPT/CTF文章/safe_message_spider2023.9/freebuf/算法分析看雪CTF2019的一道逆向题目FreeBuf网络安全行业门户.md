### 1.查看程序的基本运行逻辑

  

![](https://image.3001.net/images/20220324/1648107062_623c1e3679439aef1bfd9.png!small)

#### 出现一个窗口，有一个提示标签password、一个输入框，一个验证按钮

![](https://image.3001.net/images/20220324/1648107062_623c1e36c687b10c90b46.png!small)

#### 当再输入框内输入一些字符按下验证按钮后出现错误提示信息框

#### 其运行逻辑大概可视为下图

![](https://image.3001.net/images/20220324/1648107063_623c1e372ca999d80a75f.png!small)

### 2.查壳初探

#### MFC封装vc写的没壳

![](https://image.3001.net/images/20220324/1648107063_623c1e377978fd7e85f16.png!small)

### 3.使用IDA Pro进行静态分析

##### ①拖入程序，先打开函数调用情况窗口（方便函数跟踪）

![](https://image.3001.net/images/20220324/1648107063_623c1e37c88010fcd38d0.png!small)

##### ②shift+F12查看引用字符

看到了刚才错误的提示字符“错了”，还有嫌疑字符“pass!”，那我们找到pass字符所在的位置查看引用情况

![](https://image.3001.net/images/20220324/1648107064_623c1e38505e450a344fe.png!small)

##### ③查看引用，找到引用函数

##### 发现pass!字符的引用的函数是sub_401770,跟进去

![](https://image.3001.net/images/20220324/1648107064_623c1e38abe348c6137b1.png!small)

##### 跟进来看到的信息可以直接判断sub_401770这个函数就是输入提示我们输入的password是正确的函数

![](https://image.3001.net/images/20220324/1648107065_623c1e3917fd25f1ac084.png!small)

##### ④跟踪函数调用情况，直至找到最终调用者

#####
（1）做一个小提示：在ida中我们看到的函数都是一个以sub_函数地址值来命名这个函数，不便于我们分析，所以我们只用将光标放在函数名字上按下n键就可以更改为我们便于理解和记住的名字（不可以用中文）

#####
先将sub_401770改名为Tip_Success,通过函数调用表点击Caller字符函数名就会跳转Instruction字段函数的对应的调用者

![](https://image.3001.net/images/20220324/1648107065_623c1e395658428d4b62b.png!small)

##### （2）跟进发现sub_4017F0函数中有关键逻辑

![](https://image.3001.net/images/20220324/1648107065_623c1e3994d1c7c27af0e.png!small)

#####
将Str1与"KanXueCTF2019JustForhappy"作对比，如果相等则执行了提示成功的函数Tip_Success，那我们可以直接推测Str1就是Flag最后的变换值

##### （3）查找伪代码中的关于Str1的逻辑语句

##### 单机Str1看到了Str1是一个字符型数组局部变量，大小为28，经历了一个while中的计算

![](https://image.3001.net/images/20220324/1648107065_623c1e39df288a93e3032.png!small)

##### 代码中涉及了v4和a1,v4可以看到是一个初始化值为0的整型变量，a1则是一个该函数的形参，那说明此时我们要重点寻找a1.

##### 分析循环体

while ( *(_DWORD *)(a1 + 4 * v4) < 62 && *(_DWORD *)(a1 + 4 * v4) >= 0 )

{

Str1[v4] = aAbcdefghiabcde[*(_DWORD *)(a1 + 4 * v4)];

++v4;

}

##### 第二步我提到过Str1变量已经可以确定是Flag最后的变换值

##### 查看循环体内，其意思便是只要a1 + 4 v4这个地址里面的内容小于62并且大于等于0则将a1 + 4
v4地址的值作为aAbcdefghiabcde数组的下标，然后将对应的aAbcdefghiabcde数组内容赋值给Str1

##### 那么我们去查看一下aAbcdefghiabcde数组的元素是什么？算击aAbcdefghiabcde数组名字查看内容

##### 原来就是一串字符

![](https://image.3001.net/images/20220324/1648107066_623c1e3a4d6fbd3182527.png!small)

##### 此时分析到这里基本这个函数就分析完了，我们如果要继续分析则必须先找出a1到底是什么？

##### 继续通过函数调用表找到sub_4017F0（我们改名为Check_Encryption）函数的调用者

##### 跟进来以后看到了Check_Encryption函数中的形参就是此时函数sub_401890中的一个整型数组v5的首地址（该数组大小为26）

![](https://image.3001.net/images/20220324/1648107066_623c1e3a96195ae051ab6.png!small)

##### 那我们此时就重点跟踪v5的值了

![](https://image.3001.net/images/20220324/1648107067_623c1e3b0b08feaad8580.png!small)

##### 红框框住的就是一些mfc组件的代码，不用管，可以看到，v5的变化初始化和变化来自于Str数组，

#####
那么Str又是什么呢，仔细看从上往下第一个箭头指向的地方GetBuffer函数，这个函数会返回一个缓冲区指针，Str来接收了，说明Str很有可能就是我们输入的password所在的地址，再往GetBuffer下看一行遍看到了一个if语句

#####
判断Str长度是否为0，也就是判断是否空，空的话就执行了return语句，不为空的话就进行了一系列关于v5和Str的计算，那么此时可以直接肯定Str就是我们输入的字符所在地址

![](https://image.3001.net/images/20220324/1648107067_623c1e3b6ae0217c653aa.png!small)

#####
通过代码又可以看出我们输入的password存到Str后进行了一系列if判断后计算赋值给了v5,而v5的值又作为了Check_Encryption函数的唯一实参

if ( strlen(Str) )

{

for ( i = 0; Str[i]; ++i )

{

if ( Str[i] > 57 || Str[i] < 48 )

{

if ( Str[i] > 122 || Str[i] < 97 )

{

if ( Str[i] > 90 || Str[i] < 65 )

sub_4017B0();

else

v5[i] = Str[i] - 29;

}

else

{

v5[i] = Str[i] - 87;

}

}

else

{

v5[i] = Str[i] - 48;

}

}

result = Check_Encryption((int)v5);

}

else

{

result = CWnd::MessageBoxA(v8, "请输入pass!", 0, 0);

}

##### （4）梳理大概逻辑

![](https://image.3001.net/images/20220324/1648107067_623c1e3bc02dcc18ff89e.png!small)

##### 5）我们按照从头到尾的顺序来分析这个程序

#####
既然我们知道了我们输入的password是被Str指向（可以理解为Str是个字符数组存了我们输入的password），那么我们试试是否可以从sub_401890这个函数推出Str

![](https://image.3001.net/images/20220324/1648107068_623c1e3c31bbcbeef5c0b.png!small)

#####
阅读代码，可以得到Str[i]在此时可以有三种情况，所以此时我们不可以确定Str的唯一性，也就是我们不可以在这里得到Str（我们输入的）具体是多少，只能得到范围，那么就继续分析后面一步，跟进Check_Encryption函数

##### （6）分析Check_Encryption关键代码

v4 = 0;

v3 = 0;

while ( *(_DWORD *)(a1 + 4 * v4) < 62 && *(_DWORD *)(a1 + 4 * v4) >= 0 )

{

Str1[v4] = aAbcdefghiabcde[*(_DWORD *)(a1 + 4 * v4)];

++v4;

}

##### 阅读代码可知，(_DWORD )(a1 + 4 *
v4)的作用便是遍历上一个函数v5的每一个元素，若每一个元素满足小于62并且大于0的话则将v5对应的每一个元素作为aAbcdefghiabcde数组的下角标，将对应的aAbcdefghiabcde元素赋值给Str1，之前提过Str1是最后的Flag变换结果

while ( *(_DWORD *)(a1 + 4 * v4) < 62 && *(_DWORD *)(a1 + 4 * v4) >= 0 )

{

Str1[v4] = aAbcdefghiabcde[*(_DWORD *)(a1 + 4 * v4)];

++v4;

}

Str1[v4] = 0;

if ( !strcmp(Str1, "KanXueCTF2019JustForhappy") )

result = Tip_Success();

else

result = sub_4017B0();

##### 作者设计，如果最后的Flag遍结果等于“KanXueCTF2019JustForhappy”则提示成功，那由上我们就可以写脚本得到v5的值

char encryption[] = "KanXueCTF2019JustForhappy";

char text[] =
"abcdefghiABCDEFGHIJKLMNjklmn0123456789opqrstuvwxyzOPQRSTUVWXYZ";

for (int i = 0; i <= strlen(encryption); i++)

{

for (int j = 0; j <= strlen(text); j++)

{

if (encryption[i] == text[j])

{

//printf("%d--", j);

v5[i] = j;

}

}

##### 此时我们既然得到了v5的值那么就可以去分析上一个函数sub_401890得到Str(我们输入的password)了

for ( i = 0; Str[i]; ++i )

{

if ( Str[i] > 57 || Str[i] < 48 )

{

if ( Str[i] > 122 || Str[i] < 97 )

{

if ( Str[i] > 90 || Str[i] < 65 )

sub_4017B0();

else

v5[i] = Str[i] - 29;

}

else

{

v5[i] = Str[i] - 87;

}

}

else

{

v5[i] = Str[i] - 48;

}

}

#####
这个循环结构就是判断Strp[i]是否在一个规定的范围，通过Str[i]所属的范围来进行加密或者推=退出程序，因为v5是Str[i]-常数得到的，那么我们就可以用v5+常数来判断Str[i]的范围以及确却数值了，反推代码如下，input数组就是Str(用户输入)

for (int i = 0; i <= 26; i++)

{

if (48 <= (v5[i] + 48) && (v5[i] + 48) <= 57)

{

input[i] = v5[i]+48;

}

if (97 <= (v5[i] + 87) && (v5[i] + 87) <= 122)

{

input[i] = v5[i]+87;

}

if (65 <= (v5[i] + 29) && (v5[i] + 29) <= 90)

{

input[i] = v5[i] + 29;

}

}

##### 最后写出第一轮和第二轮的解密代码，即可得到flag

#include

#include

int main()

{

int input[26] = { 1 };

int v5[26] = {1};

int Str[26] = { 1 };

char encryption[] = "KanXueCTF2019JustForhappy";

char text[] =
"abcdefghiABCDEFGHIJKLMNjklmn0123456789opqrstuvwxyzOPQRSTUVWXYZ";

for (int i = 0; i <= strlen(encryption); i++)

{

for (int j = 0; j <= strlen(text); j++)

{

if (encryption[i] == text[j])

{

//printf("%d--", j);

v5[i] = j;

}

}

}

for (int i = 0; i <= 26; i++)

{

if (48 <= (v5[i] + 48) && (v5[i] + 48) <= 57)

{

input[i] = v5[i]+48;

}

if (97 <= (v5[i] + 87) && (v5[i] + 87) <= 122)

{

input[i] = v5[i]+87;

}

if (65 <= (v5[i] + 29) && (v5[i] + 29) <= 90)

{

input[i] = v5[i] + 29;

}

}

for (int i = 0; i < 26; i++)

{

printf("%c",input[i]);

}

return 0;


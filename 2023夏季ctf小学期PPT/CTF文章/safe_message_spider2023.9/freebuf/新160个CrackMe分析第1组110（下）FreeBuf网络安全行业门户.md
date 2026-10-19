## 6\. 006-ArturDents-CrackMe2

算法难度：⭐⭐

爆破难度：⭐

信息收集

运行情况：

经典的用户名序列号授权验证：

  

![](https://image.3001.net/images/20220903/1662171758_6312ba6e75d16711566e5.png!small)

查壳与脱壳：

无壳：

![](https://image.3001.net/images/20220903/1662171759_6312ba6f1357eb4687fa7.png!small)

查字符串：

有两个提示信息，可以作为分析的入口点：

![](https://image.3001.net/images/20220903/1662171759_6312ba6fa52e2a671c2f8.png!small)

查导入表：

很直观，获取用户输入，进行验证，然后弹出对话框提示信息![](https://image.3001.net/images/20220903/1662171760_6312ba7033e7bc881e421.png!small)

调试分析

首先获取Name，然后判断Name长度是否符合要求：

![](https://image.3001.net/images/20220903/1662171760_6312ba70c4613a83dd5a0.png!small)

然后获取输入的Serial，与使用Name生成的Serial进行比对验证，弹框提示

![](https://image.3001.net/images/20220903/1662171761_6312ba71747de397cc89c.png!small)

暴力破解

略

算法分析

注册码生成算法，没啥好说的

#include

int main()

{

char Buffer[100] = { 0 };

std::cin >> Buffer;

for (int i = strlen(Buffer),j=0; i >0; i--,j++)

{

Buffer[j] = Buffer[j] - i;

}

std::cout << Buffer << std::endl;

}

总结

平平无奇的最简单CM

## 7\. 007-reg

算法难度：⭐

爆破难度：⭐

信息收集

运行情况：

经典的用户名+序列号授权验证：

  

![](https://image.3001.net/images/20220903/1662171762_6312ba7252b137803f780.png!small)

查壳与脱壳：

Delphi编写的32位GUI程序，无壳

![](https://image.3001.net/images/20220903/1662171762_6312ba72e618583abd397.png!small)

查字符串：

大概看了一下，字符串里有个reg.dll，但CM文件只是单一的exe，可能存在释放文件

![](https://image.3001.net/images/20220903/1662171763_6312ba736cfc59ddfc32b.png!small)

调试分析

对于Delphi程序，除了直接强行分析之外，还可以借助Delphi辅助分析工具：IDR（吾爱论坛上有）

因为是窗口程序，所以查窗口的相关内容：

![](https://image.3001.net/images/20220903/1662171764_6312ba741d0dddb2483e5.png!small)

直接查看点击Ok按钮的内容：大概就是把用户输入的用户名和序列号写入到了reg.dll文件中，也就是说这是个dll后缀的文本文件

![](https://image.3001.net/images/20220903/1662171764_6312ba74a1644ef998c9f.png!small)

提示语是重启软件后验证注册码，说明这是一种重启验证，在启动的时候进行校验

那么接下来查看创建窗口时的代码：![](https://image.3001.net/images/20220903/1662171765_6312ba755915aa9f96c37.png!small)

这个调用的函数：sub_0045D0F4，这应该就是一个校验函数，根据返回al的值是否为0，来进行判断跳转，这个跳转应该是关键跳了

![](https://image.3001.net/images/20220903/1662171766_6312ba765f1bb918de91f.png!small)

暴力破解

修改关键跳：![](https://image.3001.net/images/20220903/1662171767_6312ba7709d2cded34595.png!small)

然后跑起来：![](https://image.3001.net/images/20220903/1662171767_6312ba777cec8504f17b0.png!small)

算法分析

接下来看看具体校验call做了哪些事情：sub_45D0F4

首先获取参数之后，计算SN长度，SN长度需要是16个字符：![](https://image.3001.net/images/20220903/1662171768_6312ba780129c02ea7f6c.png!small)

然后接下来是个循环，遍历SN每个字符，检查合法字符，这里允许的字符是0-9数字和A-F字母

![](https://image.3001.net/images/20220903/1662171768_6312ba78a16fcae3beef0.png!small)

然后紧接着进行一顿处理，处理用户名得到一个加密编码后的值

![](https://image.3001.net/images/20220903/1662171769_6312ba7947de6a308c8e7.png!small)

值通过x86dbg动态调试观察：计算的结果是8B45677A3AEBE84C

![](https://image.3001.net/images/20220903/1662171769_6312ba79f2c38f7aec6bd.png!small)

然后接下来，程序连续走了两趟相同的操作，分别是对刚刚通过用户名计算出来的结果和我们输入的SN，然后将结果进行对比，返回

![](https://image.3001.net/images/20220903/1662171770_6312ba7a93ca37743fce5.png!small)

这里具体生成用户名对应SN的代码过于复杂，暂时还写不出来注册机，但这里程序在分析过程中会出现SN真码明文，这里也就到此结束了，使用该SN打开程序：![](https://image.3001.net/images/20220903/1662171771_6312ba7b68e89de26aa28.png!small)

### 总结

Delphi程序逆向练习，借助工具IDR可以很方便的识别Delphi函数，这个CM使用了经典的重启验证，让验证函数在窗口创建前进行验证，注册机较为复杂，暂时还写不出来

### 参考资料

– [1] 新160个CrackMe算法分析-007-Reg_哔哩哔哩_bilibili

## 8\. 008-Afkayas.1

算法难度：⭐⭐

爆破难度：⭐

信息收集

运行情况：

输入用户名，序列号，点OK进行验证![](https://image.3001.net/images/20220903/1662171772_6312ba7c37c054d2343ea.png!small)

查壳与脱壳：

无壳，程序由VB5.0编写![](https://image.3001.net/images/20220903/1662171772_6312ba7ccb193114c4a06.png!small)

调试分析

这个程序以前做CM的时候分析过，以x86dbg+IDA进行逆向分析的，详情见参考

这次就直接拖VBDec里用专门的VB反编译软件进行分析

这个程序有用的代码就一个OK按钮的点击事件，总共就这么几行：

![](https://image.3001.net/images/20220903/1662171773_6312ba7d55d0edf798f91.png!small)

很神奇一点就是，这点之前没发现，这里藏了一个文本框，我就说代码里咋三个文本框呢，这个是用来保存数据的![](https://image.3001.net/images/20220903/1662171773_6312ba7dca91b78e1282f.png!small)

算法分析

有几行看不懂啥意思，直接x86dbg动态跟踪看看效果，整体注释：

Private Sub OK_Click() '402310

loc_004023D3: call var_8004 = var_C4(Me, Me, 0, 0, 0) // 获取用户名输入

loc_00402415: var_8008 = Len(var_C4(Me, Me, 0, 0, 0).MousePointer) // 计算用户名长度

loc_0040242D: var_800C = Asc(CrackMe.Text1.Text) // 取用户名首字符的ASCII码

loc_0040243F: call var_8010 = global_004040E0(var_8008*97531+var_800C) //
97531*用户名长度+首字符的ASCII码，结果转换成字符串

loc_00402458: CrackMe.RegSerial.Text = var_8010 // 设置这个文本框的值

loc_004024DE: call var_8014 = var_C0(Me)

loc_0040258B: If (CrackMe.Serial.Text = "AKA-" & var_C0(Me).MousePointer) + 1
Then // 判断输入的序列号是否为AKA-拼接刚刚计算的值

loc_004025C4: var_8028 = MsgBox("You Get It" & vbCrLf & "KeyGen It Now", 0,
var_4C, var_5C, var_6C)

loc_004025E5: Else

loc_0040261C: var_8034 = MsgBox("You Get Wrong" & vbCrLf & "Try Again", 0,
var_4C, var_5C, var_6C)

loc_0040263B: End If

loc_00402652: GoTo loc_0040269E

loc_0040269D: Exit Sub

loc_0040269E: ' Referenced from: 00402652

End Sub

### 总结

依然是很简单的一次VB逆向

## – [1] 160个Crackme系列-002-Afkayas.1 - 我可是会飞的啊 (kn0sky.com)

9\. 009-Boonz-KeygenMe1

算法难度：⭐⭐⭐

爆破难度：⭐

信息收集

运行情况：

神奇的审美，用户名+序列号验证程序![](https://image.3001.net/images/20220903/1662171774_6312ba7e762110ed05550.png!small)

查壳与脱壳：

无壳程序![](https://image.3001.net/images/20220903/1662171775_6312ba7f43fce9c676d91.png!small)

查字符串：

有一些提示字符串，提示输入正确失败的，还有错误提示：Name需要是4-50个字符长

![](https://image.3001.net/images/20220903/1662171775_6312ba7fbc5c6ef45039f.png!small)

调试分析

本次的目标是分析出算法写注册机，所以就没有爆破环节了

从提示字符串Hello，Mr. Goodboy入手开始分析，交叉引用找到校验函数：

![](https://image.3001.net/images/20220903/1662171776_6312ba804c01433c054df.png!small)

先后获取了用户输入的Name和Serial，然后进入校验函数

算法分析

校验函数就是算法的所在

首先判断用户名长度是否合法，长度4--50内

![](https://image.3001.net/images/20220903/1662171776_6312ba80ddf6176126928.png!small)

接下来进行第一组计算，结果保存起来

![](https://image.3001.net/images/20220903/1662171777_6312ba816ce00edc92752.png!small)

然后进行第二组运算：圈出来的三行纯属干扰，无用

![](https://image.3001.net/images/20220903/1662171778_6312ba820dd8210b0b834.png!small)

然后进行第三组运算：

![](https://image.3001.net/images/20220903/1662171778_6312ba82b3a28779faa28.png!small)

然后再往下就是拼接字符串进行比对的环节了：

![](https://image.3001.net/images/20220903/1662171779_6312ba83631c9171cae2b.png!small)

已经知道Serial是怎么算的了，接下来写注册机

注册机代码

#define _CRT_SECURE_NO_WARNINGS

#include

int main()

{

char name[50] = { 0 };

char serial[50] = { 0 };

int nameLength = 0;

std::cin >> name;

nameLength = strlen(name);

if (nameLength < 4 || nameLength > 50) {

std::cout << "Name Length Invalid" << std::endl;

return 0;

}

// 第一轮计算

unsigned int res_1 = 0;

for (auto a = 0; name[a];a++) {

char tmp = name[a];

tmp -= 0x19;

res_1 -= tmp;

}

// 第二轮计算

unsigned int res_2 = res_1 * res_1 * res_1;

// 第三轮计算

unsigned int res_3 = 0x40e0f8 * 0x40e0f8 - 0x40e0f8;

sprintf(serial, "Bon-%lX-%lX-%lX", res_1,res_2,res_3);

std::cout << serial << std::endl;

return 0;

}

计算结果：

Name = 1234

Serial = Bon-FFFFFF9A-FFEFCEA8-41720F48

程序运行结果：

![](https://image.3001.net/images/20220903/1662171780_6312ba843f9900a0ac80d.png!small)

### 总结

非常简单的序列号校验算法分析，中间的干扰是无用计算，忽视即可

## 10\. 010-ceycey

算法难度：⭐

爆破难度：⭐

信息收集

运行情况：

输入密码登录：![](https://image.3001.net/images/20220903/1662171781_6312ba853596b555848b9.png!small)

查壳与脱壳：

有UPX壳，使用ESP定律大法即可，这里不再啰嗦![](https://image.3001.net/images/20220903/1662171781_6312ba85b39fcb2ee6455.png!small)

脱壳后：可以看到是Delphi5写的GUI程序![](https://image.3001.net/images/20220903/1662171782_6312ba865a8cf7a1905e2.png!small)

调试分析

抄起IDR就是干，明文硬编码密码：ULTRADMA............................................................，如果输入错误，则点击按钮无事发生，输入正确会弹窗![](https://image.3001.net/images/20220903/1662171782_6312ba86efbaf8a352e65.png!small)

没啥可爆破和算法分析的：

![](https://image.3001.net/images/20220903/1662171783_6312ba878c73269ee9d7e.png!small)

### 总结

可以当成一次Upx脱壳练习。


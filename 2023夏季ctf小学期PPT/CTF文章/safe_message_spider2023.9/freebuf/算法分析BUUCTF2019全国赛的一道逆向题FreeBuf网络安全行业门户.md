### 1.对程序进行查壳，发现是个无壳vc编译的

![](https://image.3001.net/images/20220413/1649837681_62568671229557434cc5f.png!small)

  

2.运行程序，查看程序运行流程，在password中输入12345678，按下Crack按钮以后没有任何提示程序结束运行

![](https://image.3001.net/images/20220413/1649837681_62568671bf2ce6fa486b4.png!small)

###
3.依旧先让od跑一遍，以前说过的这种通过用户输入然后再按下按钮触发事件的先对GetDlgItemTextA函数断点看程序是否是用这个函数从输入框获取用户输入的

![](https://image.3001.net/images/20220413/1649837682_625686723013668069e26.png!small)

####
在输入框输入12345678按下Crack按钮后成功在GetDlgItemTextA函数断下，由于我们的断点是GetDlgItemTextA函数的入口点，属于系统领空，所以我们直接往下找到离GetDlgItemTextA函数入口点最近的retn断点跑完GetDlgItemTextA这个函数去查看按钮的其他逻辑事件

![](https://image.3001.net/images/20220413/1649837682_625686729ee5ddcf8d643.png!small)

### 4.查看按钮其他逻辑事件

![](https://image.3001.net/images/20220413/1649837683_625686732a3577ec07e9b.png!small)

####
跑完GetDlgItemTextA函数后发现往下有一个ExitProcess的函数，这让我们联想到了我们正常运行程序时候输入12345678程序结束运行，那可以肯定这个函数就是在我们输入12345678按下Crack按钮触发的，从这个函数往上看发现在这个函数之前有个jbe跳转，点击一看，如果跳转便是跳过这个ExitProcess的执行，说明这个jbe时一个关键点，那我们对jbe这个跳转的条件
cmp eax,0x6进行断点分析

![](https://image.3001.net/images/20220413/1649837683_625686739539e2c7b874c.png!small)

####
jbe的条件是对比eax的值是否小于等于0x6，如果满足则就跳过退出程序函数，我们一看eax的值便是我们输入12345678的长度，那我们重新输入六个数123456作为用户输入的值运行到这里

![](https://image.3001.net/images/20220413/1649837684_625686742c55b536f69b8.png!small)

####
果然，eax此时确实是用户输入的长度，而且jbe跳过了退出，ecx存入了我们输入的123456，但是是以字符串形式存入（这里要注意，后面会用到）那我们继续走跳过退出后的代码

![](https://image.3001.net/images/20220413/1649837684_62568674a531013e096f1.png!small)

####
经过这个函数后，eax的值变为了0x1e240,我们在看这个call的参数只有一个ecx,那在这个call之前我们知道ecx的值是字符串‘’123456“的地址，那说明这个0x1e240和这个123456有关系，一个是字符串一个是十六进制，这个我们就可以猜想是否这个0x1e240是”123456“转换的十六进制数，那我们用代码验证一下

#include

​ int main()

​ {

​ char num[6] = "123456";

​ int last = atol(num);

​ printf("%x",last);

​ }

![](https://image.3001.net/images/20220413/1649837685_625686751658f6c83bc0c.png!small)

#### 果然，我们的猜想是正确的，那继续往下走

####
![](https://image.3001.net/images/20220413/1649837685_625686756243d09fd764c.png!small)

####
这几行代码将eax的值赋值给了edx,而且edx还加1，此时还出现了一个对比jnz跳转，跳转的条件是edx的值是否等于0x7b，不等于则跳转，我测试了一下跳转后的流程是重复执行获取用户输入，所以我们为了不结束程序则要使得edx等于0x7b,也就是说需要eax+1
= 0x7b,我们刚才分析过eax是我们输入字符串的转16进制数，那我们此时可以得知eax=0x7b-1 =
(字符转十六进制数)用户输入，最后可以用代码算出我们要输入什么，这里要强调一个问题，从对GetDlgItemTextA断点以来，我们输入的变化情况：123456（整数）->”123456“（字符串）->0x1e240(十六进制数)，其实我们输入的就是经历了两个函数itoa->atol;所以这里我们可以直接得知我们输入要满足其等于0x7b-1,所以就是数字122,那我们从新程序断点在上图这个cmp

![](https://image.3001.net/images/20220413/1649837685_62568675da8f0a8e450a6.png!small)

####
![](https://image.3001.net/images/20220413/1649837686_625686766dd9e1776c0d1.png!small)

####
![](https://image.3001.net/images/20220413/1649837687_625686770195b8f231ff5.png!small)此时，下面又出现了三个接连的对比，分别是地址ss:[ebp-0x101]、ss:[ebp-0xFF]、ss:[ebp-0x100]的值分别和0x78、0x7a、0x79对比，这三个jnz经过测试都是跳转到重复执行获取用户输入和这一系列的判断，那此时我们来分析这三个地址的特殊性，发现我们刚才输入那三个数122的地址是ss:[ebp-0x108]，第一个地址在122地址往后3个字节，第二个地址在122地址往后1个字节，第三个地址在122地址往后2个字节，那这三个地址的值到底来自哪里呢？我们知道这个Crake的第一个要求便是用户输入的值小于等于6，说明我们可以输入6个长度的任意字符，那剩下的这三个字节加上122的长度刚好是六个。那还不简单？直接找出这三个不满足jnz跳转的值是多少就行了

#### 条件：

#### ss:[ebp-0x101] =0x78 字符：z

#### ss:[ebp-0xFF] = 0x7a 字符：x

#### ss:[ebp-0x100] = 0x79 字符：y

#### 按位置排序出来便是xyz,那我们重新打开输入122xyz断点最后一个jnz

###
5.运行到这里看到了flag字符，估计接下来就是出现flag的时候了，继续单步执行到正确flag提示信息出现前是这些代码，由于没有什么算法存在，这些代码知识用来拼接flag的所以就不分析了

004011E4 . A1 A02F4200 mov eax,dword ptr ds:[0x422FA0] ; flag

004011E9 . 8985 F4FDFFFF mov dword ptr ss:[ebp-0x20C],eax

004011EF . 8A0D A42F4200 mov cl,byte ptr ds:[0x422FA4]

004011F5 . 888D F8FDFFFF mov byte ptr ss:[ebp-0x208],cl

004011FB . B9 3F000000 mov ecx,0x3F

00401200 . 33C0 xor eax,eax

00401202 . 8DBD F9FDFFFF lea edi,dword ptr ss:[ebp-0x207]

00401208 . F3:AB rep stos dword ptr es:[edi]

0040120A . 66:AB stos word ptr es:[edi]

0040120C . AA stos byte ptr es:[edi]

0040120D . 6A 0A push 0xA ; /Arg3 = 0000000A

0040120F . 8D95 F0FCFFFF lea edx,dword ptr ss:[ebp-0x310] ; |

00401215 . 52 push edx ; |Arg2 = 00000079

00401216 . 8B85 F8FEFFFF mov eax,dword ptr ss:[ebp-0x108] ; |

0040121C . 50 push eax ; |Arg1 = 00000078

0040121D . E8 9E290000 call 1.00403BC0 ; \1.00403BC0

00401222 . 83C4 0C add esp,0xC

00401225 . 68 44204200 push 1.00422044 ; {

0040122A . 8D8D F4FDFFFF lea ecx,dword ptr ss:[ebp-0x20C]

00401230 . 51 push ecx

00401231 . E8 3A020000 call 1.00401470

00401236 . 83C4 08 add esp,0x8

00401239 . 8D95 F0FCFFFF lea edx,dword ptr ss:[ebp-0x310]

0040123F . 52 push edx

00401240 . 8D85 F4FDFFFF lea eax,dword ptr ss:[ebp-0x20C]

00401246 . 50 push eax

00401247 . E8 24020000 call 1.00401470

0040124C . 83C4 08 add esp,0x8

0040124F . 68 40204200 push 1.00422040 ; _

00401254 . 8D8D F4FDFFFF lea ecx,dword ptr ss:[ebp-0x20C]

0040125A . 51 push ecx

0040125B . E8 10020000 call 1.00401470

00401260 . 83C4 08 add esp,0x8

00401263 . 68 2C204200 push 1.0042202C ; Buff3r_0v3rf|0w

00401268 . 8D95 F4FDFFFF lea edx,dword ptr ss:[ebp-0x20C]

0040126E . 52 push edx

0040126F . E8 FC010000 call 1.00401470

00401274 . 83C4 08 add esp,0x8

00401277 . 68 28204200 push 1.00422028 ; }

0040127C . 8D85 F4FDFFFF lea eax,dword ptr ss:[ebp-0x20C]

00401282 . 50 push eax

00401283 . E8 E8010000 call 1.00401470

####
![](https://image.3001.net/images/20220413/1649837687_6256867757a1d182751ee.png!small)ok了，最后的信息框提示了flag


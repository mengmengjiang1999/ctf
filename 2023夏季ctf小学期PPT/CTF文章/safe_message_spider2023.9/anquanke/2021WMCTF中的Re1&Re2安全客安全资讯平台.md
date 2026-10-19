# 2021WMCTF中的Re1&Re2

阅读量 **170353**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-10 16:30:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01887bb845f37734bf.jpg)

## Re1

首先ida反编译main函数会报错，这个一般是程序中有花指令导致的。

![](https://p1.ssl.qhimg.com/t0137c30b8282ce52d7.png)

因为main函数比较大，用提示成功字符串定位到最后的汇编代码，向上翻翻便看见出问题的代码。

![](https://p2.ssl.qhimg.com/t011eeb08ce13bee19c.png)

双击该地址，可以发现ida将这段数据解析成了代码且最上面有一个设置的条件绝对跳转跳过了执行下面的错误带代码，这里可以直接把jnb改成jmp，并把下面垃圾代码nop掉。

![](https://p5.ssl.qhimg.com/t01a8d9550bf79c3baf.png)

继续向上翻又可以看见如下的花指令：不断跳转到下一条指令，统统nop掉即可。

![](https://p4.ssl.qhimg.com/t01bc069e6fde5ae769.png)

    
    
    from ida_bytes import *
    
    addr = 0x140002DEC
    while addr <= 0x140002DFF:
        patch_byte(addr, 0x90)
        addr += 1
    print('*'*100)
    

然后我们就可以反编译了。

先看到对输入的处理：

开始判断了flag长度范围[12, 45]，然后判断格式是否是WMCTF{}

![](https://p3.ssl.qhimg.com/t01d7c92bcf882ea262.png)

接着申请了576字节大小的空间block，并把输入的除去格式（WMCTF{}外）的前4个字节以如下方式填入block

![](https://p4.ssl.qhimg.com/t017280c7aa7bf53183.png)

再把输入的除去格式（WMCTF{}外）的4-20字节填入block+530开始的位置。

![](https://p5.ssl.qhimg.com/t01ab92659d5f9ab8e6.png)

最后就是将剩下的输入以 **_@#?!
&-$+**为区分，分别进行不同的处理。其中输入是hex形式，先把每4个hex转化两字节数据后，再用第一字节作为index，第二字节作为数据对block进行操作。

![](https://p1.ssl.qhimg.com/t01bdf3bd674161a974.png)

下面再看加密部分：

首先sub_7FF79BD33960()函数也是加了上面所说的花指令，去除后看到伪代码，用CRC算法生成256个4字节数据：

    
    
    __int64 sub_7FF79BD33960()
    {
      __int64 result; // rax
      unsigned int j; // [rsp+4h] [rbp-Ch]
      unsigned int i; // [rsp+8h] [rbp-8h]
      unsigned int v3; // [rsp+Ch] [rbp-4h]
    
      for ( i = 0; i < 0x100; ++i )
      {
        v3 = i;
        for ( j = 0; j < 8; ++j )
        {
          if ( (v3 & 1) != 0 )
            v3 = (v3 >> 1) ^ 0x8320EDB8;
          else
            v3 >>= 1;
        }
        dword_7FF79BD57A70[i] = v3;
        result = i + 1;
      }
      return result;
    }
    

然后对前4字节填充的block，用CRC生成的256个4字节数据，经过移位，异或运算生成4个4字节数据后与硬编码的数据比较：

![](https://p3.ssl.qhimg.com/t01db8b81889ff15e8d.png)

![](https://p2.ssl.qhimg.com/t01fbe91bf9373ef8f0.png)

最后使用最开始在block填充的 **0xDEAD** 改变 **vars88，vaes84, vaes80, v58**
后作为密钥对除去WMCTF{}格式外输入的4-20字节进行2个xtea加密。

![](https://p5.ssl.qhimg.com/t012229a645784cedc1.png)

下面开始解密：

首先用z3将vars88，vaes84, vaes80, v58四个值就求出来：

    
    
    from z3 import *
    
    s = Solver()
    
    key = [BitVec('x%d'%i, 32) for i in range(4)]
    s.add((key[0]+key[1]) == 0x11AB7A7A)
    s.add(key[1]-key[2] == 0x1CD4F222)
    s.add(key[2]+key[3] == 0xC940F021)
    s.add(key[0]+key[2]-key[3] == 0x7C7D68D1)
    
    if s.check() == sat:
        m = s.model()
        m = [m[key[i]].as_long() for i in range(4)]
        print(m)
    else: 
        print('Not Found!')
    #[2750330814, 1841087164, 1357369498, 2019106695]
    

再用上面4个数据依次爆破出对应的4字节明文数据：

    
    
    #include <stdio.h>
    
    unsigned int box[256];
    char res[5];
    int number[] = {0x100, 0x100, 0xf, 0x1c};
    unsigned enc[] = {2750330814, 1841087164, 1357369498, 2019106695};
    
    void gen_box()
    {
      unsigned int j; // [rsp+4h] [rbp-Ch]
      unsigned int i; // [rsp+8h] [rbp-8h]
      unsigned int v3; // [rsp+Ch] [rbp-4h]
    
      for ( i = 0; i < 0x100; ++i )
      {
        v3 = i;
        for ( j = 0; j < 8; ++j )
        {
          if ( (v3 & 1) != 0 )
            v3 = (v3 >> 1) ^ 0x8320EDB8;
          else
            v3 >>= 1;
        }
        box[i] = v3;
      }
    }
    
    unsigned int fun1(unsigned int a1, unsigned char a2[256], unsigned int a3)
    {
        unsigned int v4; // [rsp+4h] [rbp-1Ch]
        unsigned int v5; // [rsp+8h] [rbp-18h]
    
        v5 = 0;
        v4 = a1;
        while ( v5 < a3 )
            v4 = (v4 >> 8) ^ box[(unsigned char)(a2[v5++] ^ v4)];
        return a1 ^ v4;
    }
    
    unsigned int bp(int up, int number, unsigned int pre, unsigned int next)
    {
        for(int i = 0; i < 127; i++)
        {
            unsigned char block[256];
            for(int j = 0; j < number; j++)
            {
                block[j] = i+j+up;
            }
    
            if(fun1(pre, block, number) == next)
                return i;    
        }    
    }
    
    int main(void)
    {
        gen_box();
    
        for(int i = 0; i < 4; i++)
        {
            if(i == 0)
                res[i] = bp(i, number[i], -2, enc[i]);
            else
                res[i] = bp(i, number[i], enc[i-1], enc[i]);
        }
    
        puts(res);    
    }
    
    //Hah4
    

用满足前4字节的测试输入 **WMCTF{Hah41111111111111111}** 输入程序，然后在xtea加密前取出密钥：

![](https://p1.ssl.qhimg.com/t015431c679262c80c3.png)

但用这个密钥解密密文怎么都不正确。。还测试了自己的xtea解密好几遍，这里卡了好一会。

后面确定肯定是密钥的问题，但输入的前4字节是满足要求的，密钥是通过前4字节明文算出来的。但注意这里的密钥还用开始在block填充的 **0xDEAD**
的经过了变换的。这让我想到我忽略了输入的（WMCTF{}格式外）20字节后处理，开始闲麻烦懒得看直接跳过了。

所以问题现在应该就出在了有两个字节数据对密钥的影响。

爆破这2个字节，从解密结果中看像是flag的片段的：

    
    
    #include <stdio.h>
    #include <stdint.h>
    #include <stdlib.h> 
    
    unsigned int get_delat()
    {
        int i = 0;
        unsigned int ans = 0, delat = 0x667E5433;
    
        for(i = 0; i < 32; i++)
            ans -= delat;
    
        return ans;
    } 
    
    void decrypt1(unsigned int num_rounds, uint32_t v[2], uint32_t const key[4])
    {  
        unsigned int i;  
        uint32_t v0 = v[0], v1 = v[1], delta = 0x667E5433, sum = get_delat();
        //printf("%x", sum);  
        for(i = 0; i < num_rounds; i++)
        {  
            v1 -= (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + key[(sum>>11) & 3]);  
            sum += delta;  
            v0 -= (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + key[sum & 3]);  
        }  
        v[0]=v0, v[1]=v1;  
    }
    
    int check(unsigned a)
    {
        for(int i = 0; i < 4; i++)
        {
            if(((char *)&a)[i] < 32 || ((char *)&a)[i] > 127)
                return 0;
        }
    
        return 1;
    }
    
    int main(void)
    {
        //['a3eeb7be', '6dbcc2bc', '50e7d09a', '78591f87']
    
        uint32_t k[4]={0x78591FAD, 0x6DBCC2BC, 0xA3EEB7BE, 0x50E7DE9A};
        for(int i = 10; i < 0xff; i++)
        {
            for(int j = 0; j < 0xff; j++)
            {
                uint32_t v[2]={0x1989FB2B, 0x83F5A243};
                k[3] &= 0xFFFF00FF;
                k[3] |= i << 8;
                k[0] &= 0xFFFFFF00;
                k[0] |= j;
    
                unsigned int r=32;
                decrypt1(r, v, k);
    
                if(check(v[0]) && check(v[1]))
                {
                    for(int k = 0; k < 8; k++)
                    {
                        printf("%c", ((char *)v)[k]);
                    }
                    printf(" %x %x", i, j);
                    putchar(10);
                }
            }
    
        }
    
    
        return 0;  
    }
    /*
    pWRTPO{> 13 9f
    <<R|CJA< 24 c7
    \o{2%lSf 28 7f
    t<o.:RMY 2d 69
    b%AGkVTt 36 2d
    e.xQVP!| 53 0
    0bOMoJI8 54 b1
    "pWU3*@+ 73 d2
    >]zSE>?d 81 d7
    (sqF m# 8a 6b
    Z,wRg8T_ 92 76
    yOu_L1kE b7 ad
    !vta&K]M ba d3
    K?Gl@~Rw bf b5
    1C ="`~p c3 71
    ?&bqWg]_ cd b1
    SX|6u|v f4 43
    +zWv6`!C fb a2
    */
    

可以看到 **yOu_L1kE** ，满足要求的两个字节是 **0xb7 0xad**

然后解密2段密文再按一定顺序拼接一下得到： **_D0_yOu_L1kE_It!**

现在就是去求 **_@#?! &-$+**对应的处理函数怎么才能将 ** _((_WORD_ )Block + 273)**的0xDEAD的改为
**0xB7AD** 。

输入为hex，4字节为一组转化为2个byte，第一个byte是index，第二个byte是data

根据要求推算出这样一个顺序是满足b要求的：

首先 **@** 对应的处理函数将block[256] = 0xFE。注意下面是char a2，所以传入0xFF就是-1了，因此满足输入为：
**[@FFFE](https://github.com/FFFE "@FFFE")**

![](https://p5.ssl.qhimg.com/t01f09552abcee9a711.png)

然后 **#** 对应的处理函数将block[528] = 0x20，因此满足输入： **#0F20**

![](https://p2.ssl.qhimg.com/t010c2449b880fea57a.png)

最后 **–** 对应的处理函数将block[527] = 0xB7，也是我们最后的终点。因此满足输入： **-11B7**

![](https://p1.ssl.qhimg.com/t011ec95edaa184d849.png)

可以看到上面要能执行最后的 ** _(_BYTE_ )(a1 + 530 + a2) = a3;**要求是(*(unsigned __int16 *)(a1
+ 528) % 16) == 0，(unsigned int)(*(unsigned __int16 *)(a1 + 528) / 16) < 3

用这2个限制爆破得到：

    
    
    >>> a = [i for i in range(0xff) if i%16 == 0 and i/16 < 3]
    >>> a
    [0, 16, 32]
    

而我们的index为17且 **index < _(unsigned __int16_ )(a1 + 528)**，所以满足要求的就只有最后的32了，故上面
**#** 对应的处理函数要将block[528] = 0x20。

最后将我们的所有输入拼接起来得到flag：

**WMCTF{Hah4_D0_yOu_L1kE_It![@FFFE](https://github.com/FFFE
"@FFFE")#0F20-11B7}**

## Re2

jadx打开app，可以看到关键在native层。

![](https://p1.ssl.qhimg.com/t0138ef7e725bf058a8.png)

到so文件找到 **JNI_Onload**

![](https://p3.ssl.qhimg.com/t01ade0203edc64bc60.png)

其中，上面的JNI_Onload根据sub_7079FF9BBC函数的返回值注册不同的函数。

看到sub_7079FF9BBC：它通过查看 **/data/local/su** 是否存在，也就是判断我们的运行环境中有没有root

![](https://p0.ssl.qhimg.com/t011b33cf742fc1b40e.png)

所以JNI_Onload是根据运行环境是否root注册不同的函数来执行。

接着我把程序在root与非root手机运行来看一下，root下运行随便输入后显示： **fake branch**
，而在非root的手机上运行随便输入后显示： **failed,please try again!!!**
，以此可以得出，我们要分析的非root才注册的函数。

然后也去看了一下root下注册的假流程：经过上面一些加密后最终都是返回同一个字符串。

![](https://p0.ssl.qhimg.com/t0193dac48219ba15b4.png)

查看返回的字符串，发现并不是字符串数据，从交叉引用发现.init_array中一些初始化函数对其进行了解密。

![](https://p4.ssl.qhimg.com/t01434e842bf599178a.png)

并且.init_array中初始化函数动态解密了程序中很多数据：

![](https://p0.ssl.qhimg.com/t01f9addb08920e5358.png)

对上面假流程返回的字符串异或0x6d解密后得到：fake branch

![](https://p2.ssl.qhimg.com/t013fa32aeeae4ed4f8.png)

再看到正确分支流程：先异或解密一些数据后注册了如下的函数。

    
    
    jstring __fastcall sub_7079FF9134(JNIEnv *a1, __int64 a2, __int64 a3)
    {
      const char *v5; // x21
      _BYTE *v6; // x20
      char *v7; // x21
      __int64 v8; // x0
      char *v9; // x1
      __int64 v10; // x8
      size_t v11; // w0
      const char *v12; // x1
      const char *v13; // x1
      jstring v14; // x19
      _BYTE v16[56]; // [xsp-30h] [xbp-170h]
      unsigned __int64 v17[2]; // [xsp+8h] [xbp-138h] BYREF
      char *v18; // [xsp+18h] [xbp-128h]
      __int128 v19; // [xsp+20h] [xbp-120h] BYREF
      unsigned __int64 v20[2]; // [xsp+38h] [xbp-108h] BYREF
      char *v21; // [xsp+48h] [xbp-F8h]
      __int64 v22; // [xsp+F8h] [xbp-48h]
    
      v22 = *(_QWORD *)(_ReadStatusReg(ARM64_SYSREG(3, 3, 13, 0, 2)) + 40);
      strcpy_0(v17, (char *)&xmmword_707A02F0A0);
      v5 = (*a1)->GetStringUTFChars(a1, a3, 0LL);
      if ( (*a1)->GetStringLength(a1, (jstring)a3) == 32 )
      {
        v6 = (_BYTE *)operator new[](0x21uLL);
        __strcpy_chk(v6, v5, 33LL);
        v7 = (char *)operator new[](0x1EuLL);
        sub_7079FF9E80();
        v8 = __strlen_chk(v7, 0x1Eu);
        v7[(int)v8] = 102;
        v7[((v8 << 32) + 0x100000000LL) >> 32] = 108;
        v7[((v8 << 32) + 0x200000000LL) >> 32] = 103;
        v7[((v8 << 32) + 0x300000000LL) >> 32] = 0;
        v19 = xmmword_707A01E5D0;
        sub_7079FFA934((__int64)v20, v7, (long double *)&v19);
        sub_7079FFAE6C(v20, v6, 0x20uLL);
        strcpy_0(v20, (char *)&qword_707A02F058);
        if ( (v20[0] & 1) != 0 )
          v9 = v21;
        else
          v9 = (char *)v20 + 1;
        sub_7079FFA624((int)&v19, v9);
        v10 = 0LL;
        while ( v16[v10] == stru_707A02F000[0].n128_u8[v10] )
        {
          if ( ++v10 == 32 )
          {
            v11 = strlen((const char *)&aQpyl);
            sub_7079FF9670((int)v17, &aQpyl, v11);
            if ( (v17[0] & 1) != 0 )
              v12 = v18;
            else
              v12 = (char *)v17 + 1;
            goto LABEL_18;
          }
        }
        if ( (v17[0] & 1) != 0 )
          v12 = v18;
        else
          v12 = (char *)v17 + 1;
    LABEL_18:
        v14 = (*a1)->NewStringUTF(a1, v12);
        if ( (v20[0] & 1) != 0 )
          operator delete(v21);
      }
      else
      {
        if ( (v17[0] & 1) != 0 )
          v13 = v18;
        else
          v13 = (char *)v17 + 1;
        v14 = (*a1)->NewStringUTF(a1, v13);
      }
      if ( (v17[0] & 1) != 0 )
        operator delete(v18);
      return v14;
    }
    

先简单静态分析一下，开始是判断输入的长度是否为32。

然后sub_7B4933FE80函数读取某个文件内容经过对比后返回一串字符串：

![](https://p3.ssl.qhimg.com/t017caad336ab52ea4f.png)

后面接着对上面获取到的字符串进行如下赋值：

![](https://p4.ssl.qhimg.com/t01855d7d0d86dc2b4f.png)

其实就是在其末尾加上 **flg**

    
    
    len = strlen(init_key);
    init_key[len] = 'f';
    init_key[len+1] = 'l';
    init_key[len+2] = 'g';
    init_key[len+3] = '\x0';
    

接着sub_7B49340934函数传入两个参数，其中的sub_7B49340820函数用了传入的一个参数串进行aes的密钥扩展：字节替换（但是这里的sbox是替换过的），移位，轮常数异或。44/4
= 11，这也说明了是aes_128，因为密钥11组。

![](https://p4.ssl.qhimg.com/t01b4b392cf105d4b20.png)

再是将另外一个参数存放在扩展密钥的尾部：

![](https://p0.ssl.qhimg.com/t016a53df81568434b9.png)

接着的sub_7B49340E6C函数也是很明显的aes_128_cbc加密，sub_7B4934097C中清晰的初始轮（轮密钥加），重复轮（字节替换，行移位，列混合，轮密钥加），最终轮（字节替换，行移位，轮密钥加）结构：

![](https://p2.ssl.qhimg.com/t01c292d579758dad31.png)

最后sub_7B49340624函数rc4加密，但多异或了0x50：

![](https://p5.ssl.qhimg.com/t01771f2af4f75f5439.png)

所以整体上本题的加密就是aes_128_cbc与rc4，麻烦的是数据部分，如aes的密钥，iv，rc4密钥与密文等。因为开始说了在.init_array中进行了很多数据的解密，我在静态分析看到的大多数数据都是没有解密的。那我们现在要么对分析到的数据找到引用修改的.init_array中的函数按照相同的运算逻辑手动patch修改；要么就是把程序调试起来，分析起来会简单很多。

这里我选择了动态调试。

首先将AndroidMannifest.xml中的 **android:extractNativeLibs=”false“**
改为true或者删掉，默认为true。因为这个如果为false会让我们在调试时找不到so

![](https://p5.ssl.qhimg.com/t01139f1ac1930ae8e4.png)

然后因为我们调试的断点要断在 **JNI_OnLoad** 中（方便把注册的函数修改为正确的分支），那我们必须在程序还没执行
**System.loadLibrary(“native-lib”);** 之前就断下来，所以要程序要以调试模式启动。

首先我尝试了ida+jdb的组合：

> 运行环境中root模式启动好相应的服务程序，转发端口到本地。(停止转发端口： **adb forward —remove tcp:端口号`或`adb
> forward —remove-all**)
>
> 使用am命令以调试启动app：adb shell am start -D -n come.wmctf.crackme111/.MainActivity
>
> ida在JNI_OnLoad中下好断点，然后找到app对应的进程后附加，接着F9运行
>
> 打开ddms，用附加让app运行起来：jdb -connect
> com.sun.jdi.SocketAttach:hostname=127.0.0.1,port=8700

但是这样做在jdb附加app就报如下的错误。这好像是我手机的原因？

![](https://p5.ssl.qhimg.com/t01481369c82c5c697c.png)

我使用jeb来附加app同样也是报错，这都是在我先用IDA附加了进程的情况下，接着我尝试发现先jdb或jeb附加再IDA附加是可以的，但这样程序已经运行过
**System.loadLibrary(“native-lib”);** 了。

而还有一个方法，我们可以使用jeb附加调试断在 **System.loadLibrary(“native-lib”);** 之前再用IDA去附加进程呀。

![](https://p0.ssl.qhimg.com/t01f3a1d2f53d478ab6.png)

然后成功断在JNI_OnLoad中，在正确分支下好断点，修改检测环境是否root的返回值为false，但是这个在native层运行完JNI_OnLoad函数回到java层的时候app又崩溃了。

最后干脆直接改so得了，就是把根据检测运行环境是否有su的返回值后的条件跳转改一下。

![](https://p1.ssl.qhimg.com/t013a39a597543c6aaa.png)

上面修改完后，把app重编译一下，然后普通的附加调试就好了。这也是调试本程序最简单的方法，上面绕了一大圈😂。

现在再看一下内存中解密后的数据，一目了然：

![](https://p1.ssl.qhimg.com/t01b71b4dc434a36fb9.png)

看到上面静态分析说的sub_7B4933FE80函数用fopen()打开了一个系统文件，现在调试过去发现原来是进程的状态信息：

![](https://p2.ssl.qhimg.com/t0197b9480a12af450b.png)

再看到后面要匹配的内容。

![](https://p0.ssl.qhimg.com/t01c6dc268c1ef3e454.png)

自己手动查看一下：

![](https://p0.ssl.qhimg.com/t01cf75f688aac54564.png)

接着直接调试到最后看获取的结果，就是要获取 **TracerPid:**
字段那一行的内容加上flg，而app正常不调试运行这个TracerPid是0的，所以这里获取的正确值为：
**TracerPid:\x090\x0Aflg**

![](https://p5.ssl.qhimg.com/t01ce24220dcb875514.png)

接着看到下面与上面的静态分析结合可以知道：程序中aes_128的key： **TracerPid:\x090\x0Aflg** iv： **0, 1, 2,
3, 4, 5, 6, 7, 8, 9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF**

![](https://p4.ssl.qhimg.com/t0165f5e23963bc470f.png)

再就是这个aes加密的sbox果然是替换了的，正常的sbox开头为： **0x63, 0x7c, 0x77, 0x7b**

![](https://p3.ssl.qhimg.com/t0196d872128c921dde.png)

最后看到剩下的rc4加密，从传入参数看到密钥是 **Hello from C++**

下面开始解密。

首先rc4解密：

直接把输入的aes加密结果与最终经过rc4结果都提取出来异或一下得到异或序列，再将其与真正的密文异或一下得到真正的aes加密结果：

    
    
    >>> s = [0xA4, 0xCD, 0xDA, 0x34, 0xA9, 0xE8, 0xFF, 0x48, 0xD6, 0x74, 0xE7, 0x0F, 0x71, 0xF7, 0xED, 0xB7, 0xC2, 0xA8, 0xE1, 0xE1, 0x0E, 0x2D, 0xD0, 0x8D, 0xF8, 0x20, 0x0E, 0x85, 0x1D, 0xBC, 0xC1, 0x61]
    >>> t = []
    >>> t = [0x6C, 0xDB, 0xC6, 0x75, 0x4A, 0x94, 0xAA, 0xBD, 0xF5, 0x92, 0xCF, 0xB6, 0x4E, 0x0B, 0x38, 0x5B, 0x2E, 0x4F, 0x48, 0xFD, 0xE2, 0x7B, 0xE3, 0xFE, 0x64, 0x7E, 0xEA, 0xA7, 0xB5, 0x8D, 0x96, 0xF5]
    >>> ans = [s[i]^t[i] for i in range(len(s))]
    >>> ans
    [200, 22, 28, 65, 227, 124, 85, 245, 35, 230, 40, 185, 63, 252, 213, 236, 236, 231, 169, 28, 236, 86, 51, 115, 156, 94, 228, 34, 168, 49, 87, 148]
    >>> enc = [0x18, 0x76, 0xEB, 0x87, 0x76, 0x3E, 0x77, 0x08, 0xC0, 0x8D, 0x56, 0x25, 0x9E, 0x35, 0x0D, 0x16, 0x23, 0x65, 0x61, 0x6A, 0x14, 0x9D, 0x4F, 0x1C, 0x64, 0x21, 0x7D, 0x78, 0xBA, 0x53, 0x91, 0x22]
    >>> res = [ans[i]^enc[i] for i in range(len(enc))]
    >>> res
    [208, 96, 247, 198, 149, 66, 34, 253, 227, 107, 126, 156, 161, 201, 216, 250, 207, 130, 200, 118, 248, 203, 124, 111, 248, 127, 153, 90, 18, 98, 198, 182]
    

然后aes解密：

将之前自己写过的aes_cbc加解密中的sbox替换为程序中的，rsbox简单对sbox求一下逆，最后解密即可：

    
    
    //aes.h
    #ifndef AES_H
    #define AES_H
    
    #include <string.h>
    #include <stdio.h>
    #include <iostream> 
    
    #define Nk 4
    #define Nr 10
    #define Nb 4
    #define getSBoxValue(num) (sbox[(num)])
    
    class aes
    {
    public:
        struct ctx_
        {
            unsigned char RoundKey[11*16];
        }ctx;
    
    public:
        aes(char *Key);
        void xor_iv(char *a, char *b);
        void KeyExpansion(unsigned char *RoundKey, char *Key);
        void AddRoundKey(unsigned char (*state)[4], unsigned char *RoundKey);
        void SubBytes(unsigned char (*state)[4]);
        void ShiftRows(unsigned char (*state)[4]);
        unsigned char gfmultby(unsigned char a, unsigned char b);
        void MixColumns(unsigned char (*state)[4]);
        void getData(unsigned char (*data)[4], char *enc);
        void encryption_cbc(char *plaint, char *enc);
        void InvSubBytes(unsigned char (*state)[4]);
        void InvShiftRows(unsigned char (*state)[4]);
        void InvMixColumns(unsigned char (*state)[4]);
        void decryption_cbc(char *plaint, char *enc);
    };
    
    #endif // AES_H
    
    
    
    //main.cpp
    #include "aes.h"
    
    using namespace std;
    
    const unsigned char sbox[256] = {
      //0     1    2      3     4    5     6     7      8    9     A      B    C     D     E     F
      0x7C, 0xF2, 0x63, 0x7B, 0x77, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76, 0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0, 0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15, 0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75, 0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84, 0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF, 0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8, 0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2, 0x0C, 0xCD, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73, 0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB, 0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79, 0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0x08, 0xAE, 0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A, 0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E, 0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF, 0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16 };
    
    unsigned char rsbox[256] = {0}; 
    
    const unsigned char Rcon[11] = {
      0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36 };
    
    const unsigned char MixValue[4][4] = {{02, 03, 01, 01},
                                          {01, 02, 03, 01},
                                          {01, 01, 02, 03},
                                          {03, 01, 01, 02}
    };
    
    
    const unsigned char InvMixValue[4][4] = {{0xe, 0xb, 0xd, 0x9},
                                             {0x9, 0xe, 0xb, 0xd},
                                             {0xd, 0x9, 0xe, 0xb},
                                             {0xb, 0xd, 0x9, 0xe}
    };
    
    aes::aes(char *key)
    {
        this->KeyExpansion(ctx.RoundKey, key);
    
        for(int i = 0; i < 256; i++)
        {
            rsbox[sbox[i]] = i;
        }
    }
    
    void aes::xor_iv(char *data, char *iv)
    {
        for(int i = 0; i < 16; i++)
            data[i] ^= iv[i];
    }
    
    void aes::KeyExpansion(unsigned char *RoundKey, char *Key)
    {
        unsigned char i, j, k;
        unsigned char tempa[4];
    
        for (i = 0; i < Nk; ++i)
        {
            RoundKey[(i * 4) + 0] = Key[(i * 4) + 0];
            RoundKey[(i * 4) + 1] = Key[(i * 4) + 1];
            RoundKey[(i * 4) + 2] = Key[(i * 4) + 2];
            RoundKey[(i * 4) + 3] = Key[(i * 4) + 3];
        }
    
        for (i = Nk; i < Nb * (Nr + 1); ++i)
        {
            k = (i - 1) * 4;
            tempa[0]=RoundKey[k + 0];
            tempa[1]=RoundKey[k + 1];
            tempa[2]=RoundKey[k + 2];
            tempa[3]=RoundKey[k + 3];
    
            if (i % Nk == 0)
            {
                const unsigned char u8tmp = tempa[0];
                tempa[0] = tempa[1];
                tempa[1] = tempa[2];
                tempa[2] = tempa[3];
                tempa[3] = u8tmp;
    
                tempa[0] = getSBoxValue(tempa[0]);
                tempa[1] = getSBoxValue(tempa[1]);
                tempa[2] = getSBoxValue(tempa[2]);
                tempa[3] = getSBoxValue(tempa[3]);
    
                tempa[0] = tempa[0] ^ Rcon[i/Nk];
            }
    
            j = i * 4; k=(i - Nk) * 4;
            RoundKey[j + 0] = RoundKey[k + 0] ^ tempa[0];
            RoundKey[j + 1] = RoundKey[k + 1] ^ tempa[1];
            RoundKey[j + 2] = RoundKey[k + 2] ^ tempa[2];
            RoundKey[j + 3] = RoundKey[k + 3] ^ tempa[3];
        }
    }
    
    void aes::AddRoundKey(unsigned char (*state)[4], unsigned char *RoundKey)
    {
        int i, j;
    
        for(i = 0; i < 4 ;i++)
        {
            for(j = 0; j < 4; j++)
            {
                state[i][j] ^=  RoundKey[j*4+i];
            }
        }
    }
    
    void aes::InvSubBytes(unsigned char (*state)[4])
    {
        int i, j;
    
        for(i = 0; i < 4; i++)
        {
            for(j = 0; j < 4; j++)
            {
                state[i][j] = rsbox[state[i][j]];
            }
        }
    }
    
    void aes::InvShiftRows(unsigned char (*state)[4])
    {
        int i, j, cnt, tmp;
    
        for(i = 1; i < 4; i++)
        {
            cnt = 0;
            while(cnt++ < i)
            {
                tmp = state[i][3];
                for(j = 3; j > 0; j--)
                {
                    state[i][j] = state[i][j-1];
                }
                state[i][j] = tmp;
            }
        }
    }
    
    unsigned char aes::gfmultby(unsigned char a, unsigned char b)
    {
        unsigned char tmp = a >= 0x80 ? (unsigned char)((a<<1)^0x1b):(unsigned char)(a << 1);
        if(b == 1)
            return a;
        else if(b == 2)
            return tmp;
        else if(b == 3)
            return tmp^a;
        else if(b == 4)
            return gfmultby(tmp, 2);
        else if(b == 8)
            return gfmultby(gfmultby(tmp, 2), 2);
        else if(b == 9)
            return gfmultby(gfmultby(tmp, 2), 2)^a;
        else if(b == 10)
            return gfmultby(gfmultby(tmp, 2), 2)^tmp;
        else if(b == 11)
            return gfmultby(gfmultby(tmp, 2), 2)^tmp^a;
        else if(b == 12)
            return gfmultby(gfmultby(tmp, 2), 2)^gfmultby(tmp, 2);
        else if(b == 13)
            return gfmultby(gfmultby(tmp, 2), 2)^gfmultby(tmp, 2)^a;
        else
            return gfmultby(gfmultby(tmp, 2), 2)^gfmultby(tmp, 2)^tmp;
    }
    
    
    void aes::InvMixColumns(unsigned char (*state)[4])
    {
        int i, j, k;
    
        unsigned char output[4][4] = {{0}};
    
        for(i = 0; i < 4; i++)
        {
            for(j = 0; j < 4; j++)
            {
                for(k = 0; k < 4; k++)
                {
                    output[i][j] ^= gfmultby(state[k][j], InvMixValue[i][k]);
                }
            }
    
        }
    
        for(i = 0; i < 4; i++)
        {
            for(j = 0; j < 4; j++)
            {
                state[i][j] = output[i][j];
            }
        }
    }
    
    void aes::getData(unsigned char (*data)[4], char *plaint)
    {
        int i, j;
    
        for(i = 0; i < 4; i++)
        {
            for(j = 0; j < 4; j++)
            {
                data[j][i] = plaint[4*i+j];
            }
        }
    
    }
    
    
    void aes::decryption_cbc(char *enc, char *plain)
    {
        int i = 10, j = 0;
        unsigned char state[4][4] = {{0}}, output[4][4];
    
        aes::getData(state, enc);
    
        aes::AddRoundKey(state, ctx.RoundKey+i*16);
        for(i--; ; i--)
        {
            aes::InvShiftRows(state);
            aes::InvSubBytes(state);
            aes::AddRoundKey(state, ctx.RoundKey+i*16);
            if(i == 0)
                break;
            aes::InvMixColumns(state);
        }
    
        for(i = 0; i < 4; i++)
        {
            for(j = 0; j < 4; j++)
            {
                output[i][j] = state[j][i];
            }
        }
    
        for(i = 0; i < 16; i++)
            plain[i] = ((char *)output)[i];
    
    }
    
    int main(void)
    {
        char key[] = {84, 114, 97, 99, 101, 114, 80, 105, 100, 58, 9, 48, 10, 102, 108, 103};
        char iv[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF};
        char plain[100] = {0};
        char enc[] = {208, 96, 247, 198, 149, 66, 34, 253, 227, 107, 126, 156, 161, 201, 216, 250, 207, 130, 200, 118, 248, 203, 124, 111, 248, 127, 153, 90, 18, 98, 198, 182};
    
        aes *cry = new aes(key);
    
        for(int i = 0; i < 32; i += 16)
        {
            cry->decryption_cbc(enc+i, plain+i);
            if(i == 0)
                cry->xor_iv(plain+i, iv);
            else
                cry->xor_iv(plain+i, enc+(i-16));
        }
        puts(plain);
    
        return 0;
    }
    

最后解密得到： **wmctf{e78ce1a3ac4be37a96e27e98c}**

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Bxb0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/252318](/post/id/252318)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [逆向工程](/tag/逆向工程)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) Bxb0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


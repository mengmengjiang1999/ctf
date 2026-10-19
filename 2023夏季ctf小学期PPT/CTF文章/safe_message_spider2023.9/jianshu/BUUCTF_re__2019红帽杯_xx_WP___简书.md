BUUCTF re [2019红帽杯]xx WP

[ Du1in9](https://www.jianshu.com/u/32aab16373de)关注赞赏支持

# BUUCTF re [2019红帽杯]xx WP

使用findcrypt插件发现为tea系列，跟进知道加密算法为xxtea  

image

  
**分析代码**  
第一部分  

图片.png

  
第二部分，v4存放着Code的前4个字符和1个0  

图片.png

  
第三部分  

图片.png

  
第四部分，打乱顺序  

图片.png

  
第五部分，运算之后再与存储的数据做比较（v29，v29+1，v30，v31在栈上存放的位置相连，小端序存放，需将其反过来写）  

图片.png

  
**开始写脚本**  
逆运算再排序

    
    
    data0 = "CEBC406B7C3A95C0EF9B202091F70235231802C8E75656FA"#存储数据
    data = []
    for i in range(0,len(data0),2):
        data.append(int(data0[i]+data0[i+1],16))#16进制转换为10进制
    for i in range(len(data)-1,-1,-1):#逆运算
        for j in range(i//3):
            data[i] ^= data[j]
    biao = [2,0,3,1,6,4,7,5,10,8,11,9,14,12,15,13,18,16,19,17,22,20,23,21]#还原顺序
    shuju = [1]*24
    for i in range(24):
        shuju[biao[i]] = data[i]
    print(shuju)
    #[188, 165, 206, 64, 244, 178, 178, 231, 169, 18, 157, 18, 174, 16, 200, 91, 61, 215, 6, 29, 220, 112, 248, 220]
    

得到密钥

    
    
    #include <stdio.h>
    #include <string.h>
    #include <stdint.h>
    #include "encode.h"
    int main()
    {
        int i,j,data[] = { 188, 165, 206, 64, 244, 178, 178, 231, 169, 18, 157, 18, 174, 16, 200, 91, 61, 215, 6, 29, 220, 112, 248, 220 };
        for (i = 1; i <= 6; i++)//导出加密的数据，将其转换为十六进制并用小端序来表示
        {
            printf("0x");
            for (j = i * 4 - 1; j > (i - 1) * 4 - 1; j--)
                printf("%x", data[j]);
            printf(",");
        }
        printf("\n0x");
        int key[] = { 'f','l','a','g' };//导出密钥，将其转换为十六进制并用小端序来表示
        for (i = 3; i >= 0; i--)
            printf("%x", key[i]);
        printf(",");
        for (i = 0; i < 3; i++)//密钥为4个32位的数，1个字符4bit，4个字符为32bit，还差3个32bit的数
            printf("0x0,");
    }
    //0x40cea5bc,0xe7b2b2f4,0x129d12a9,0x5bc810ae,0x1d6d73d,0xdcf870dc,
    //0x67616c66,0x0,0x0,0x0,
    

xxtea解密

    
    
    #include <stdio.h>
    #include <string.h>
    #include <stdint.h>
    #include "encode.h"
    int main()
    {
    #if 0
        uint32_t enc[6] = { (unsigned int)0x40cea5bc,(unsigned int)0xe7b2b2f4,(unsigned int)0x129d12a9,(unsigned int)0x5bc810ae,(unsigned int)0x1d06d73d,(unsigned int)0xdcf870dc };
        int n = -6;
        uint32_t const key[4] = { (unsigned int)0x67616c66,(unsigned int)0x0,(unsigned int)0x0,(unsigned int)0x0 };
        btea(enc, n, key);
        for (int i = 0; i < 6; i++)
            printf("%x", enc[i]);
    #endif
        char string[] = "67616c665858437b646e615f742b2b5f7d6165";
        int i = 1,j=0;
        for (;i<6;i++)
        {
            for (j = 0; j < 8; j += 2)
            {
                if (j == 0 && i == 5)
                    continue;
                printf("%c%c", string[i * 8 - j - 2], string[i * 8 - j - 1]);
            }
        }
    }
    //666c61677b4358585f616e645f2b2b7465617d 
    

其中头文件encode.h：

    
    
    #define xxtea_DELTA 0x9e3779b9
    #define xxtea_MX (((xxtea_z>>5^xxtea_y<<2) + (xxtea_y>>3^xxtea_z<<4)) ^ ((xxtea_sum^xxtea_y) + (xxtea_key[(xxtea_p&3)^xxtea_e] ^ xxtea_z)))
    void xxtea(uint32_t* xxtea_origin, int xxtea_n, uint32_t const xxtea_key[4])
    {
        uint32_t xxtea_y, xxtea_z, xxtea_sum;
        unsigned xxtea_p, xxtea_rounds, xxtea_e;
        if (xxtea_n > 1)            /* Coding Part */
        {
            xxtea_rounds = 6 + 52 / xxtea_n;
            xxtea_sum = 0;
            xxtea_z = xxtea_origin[xxtea_n - 1];
            do
            {
                xxtea_sum += xxtea_DELTA;
                xxtea_e = (xxtea_sum >> 2) & 3;
                for (xxtea_p = 0; xxtea_p < xxtea_n - 1; xxtea_p++)
                {
                    xxtea_y = xxtea_origin[xxtea_p + 1];
                    xxtea_z = xxtea_origin[xxtea_p] += xxtea_MX;
                }
                xxtea_y = xxtea_origin[0];
                xxtea_z = xxtea_origin[xxtea_n - 1] += xxtea_MX;
            } while (--xxtea_rounds);
        }
        else if (xxtea_n < -1)      /* Decoding Part */
        {
            xxtea_n = -xxtea_n;
            xxtea_rounds = 6 + 52 / xxtea_n;
            xxtea_sum = xxtea_rounds * xxtea_DELTA;
            xxtea_y = xxtea_origin[0];
            do
            {
                xxtea_e = (xxtea_sum >> 2) & 3;
                for (xxtea_p = xxtea_n - 1; xxtea_p > 0; xxtea_p--)
                {
                    xxtea_z = xxtea_origin[xxtea_p - 1];
                    xxtea_y = xxtea_origin[xxtea_p] -= xxtea_MX;
                }
                xxtea_z = xxtea_origin[xxtea_n - 1];
                xxtea_y = xxtea_origin[0] -= xxtea_MX;
                xxtea_sum -= xxtea_DELTA;
            } while (--xxtea_rounds);
        }
    }
    

将666c61677b4358585f616e645f2b2b7465617d转为字符串，flag{CXX_and_++tea}

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [【BUUCTF】RE WP](https://www.jianshu.com/p/fe1baa5bb1e9)

题目地址：https://buuoj.cn/challenges 0x01 easyre 拖入ida看代码，得到f...

[Du1in9](https://www.jianshu.com/u/32aab16373de)阅读 2,487评论 0赞 2

  * [2019湖湘杯部分WP](https://www.jianshu.com/p/15f10490b0e7)

0x01 untar 直接访问题目可以看到源码 但是直接传马发现不解析，于是搜索了一下，发现 CVE-2018-1...

[708e8568411c](https://www.jianshu.com/u/708e8568411c)阅读 2,477评论 1赞 2

  * [【笔记】谢希仁—计网五版：chapter seven 网络安全 ](https://www.jianshu.com/p/fc8655685b50)

一、网络安全问题概述 1.计算机网络面临的安全性威胁 Ⅰ、主动攻击与被动攻击 有被动攻击和主动攻击，截获信息的称为...

[dmmy大印](https://www.jianshu.com/u/23a9dfe01541)阅读 969评论 0赞 2

  * [复盘 SUCTF 2019 Reverse](https://www.jianshu.com/p/c77eb3281a40)

Reverse SignIn exeinfope 载入查壳。一个64位的ELF程序，无壳。 先来静态分析一波，载入...

[PureT](https://www.jianshu.com/u/ce32205513b0)阅读 1,176评论 0赞 1

  * [情商-情商的运用](https://www.jianshu.com/p/68b0723f06bd)

印象深刻的部分、与现实的联系 1、爱与工作是标志着人全面成熟的双重能力，情绪力量是婚姻存亡的关键。防止夫妻反目的因...

[一坛子泡菜](https://www.jianshu.com/u/8cd8d806e50e)阅读 483评论 0赞 0

 
## 前言

提笔之前，先感谢一位师傅：来自先知社区的 **Badrer**
，师傅太强了，本菜狗re路途上的一盏明灯，附上师傅[先知首页](https://xz.aliyun.com/u/11261)。

再聊一聊这篇文章的由来：目前主要肩负两项任务，一是备战省赛，二是带师弟(bushi)(实际上是被师弟暴打)。备战比赛就要会做题，带师弟就要会出题，然鹅本菜鸡哪一项都不擅长，正巧这段时间准备研究一下CTF逆向涉及的各种加密算法（
**RC4/IDEA/DES/TEA/BASE64** 等)，那么就来边学加密算法边学逆向方法吧。

## rc4原理研究

在密码学中，RC4（来自Rivest Cipher 4的缩写）是一种流加密算法，密钥长度可变。它加解密使用相同的密钥，因此也属于 **对称加密算法**
。RC4是有线等效加密（WEP）中采用的加密算法，也曾经是TLS可采用的算法之一。RC4算法的原理非常简单，包括初始化算法（KSA）和伪随机子密码生成算法(PRGA)两大部分。

参数| 作用  
---|---  
S-box(S)| 256长度的char型数组，定义为: unsigned char sBox[256]  
Key(K)| 自定义的密钥，用来打乱 S-box  
pData| 用来加密的数据  
  
### RC4算法流程简单实现

 **1\. 1-256初始化S-Box和临时向量T**

    
    
    for i in range(0,255):  
    S[i]=i  
    T[i]=K[imodkeylen]

 **2.初始排列S-Box 并作乱序处理**

    
    
    j=0  
    for i in range(0,255):  
    j=(j+S[i]+T[i]) %256  
    swap(s[i],s[j])

 **3.生成密钥流 len:明文为len个字节**

    
    
    int i=0,j=0,t;  
    while(len--)  
    i=(i+1)%256;  
    j=(j+S[i])%256;  
    S[i]=S[i]+S[j];  
    S[j]=S[i]-S[j];  
    S[i]=S[i]-S[j];  
    t=(S[i]+S[j])%256;  
    k.push_back(S[t]);

  4. 将子密钥序列同明文进行异或得到密文

    
    
    Data[k]^=S[T]

### RC4算法流程简单总结

可能这样还是不便于理解，我们简单来写就是：

 **1、先初始化状态向量S（256个字节，用来作为密钥流生成的种子1）**

按照升序，给每个字节赋值0,1,2,3,4,5,6.....,254,255

 **2、初始密钥（由用户输入），长度任意**

如果输入长度小于256个字节，则进行轮转，直到填满

例如输入密钥的是1,2,3,4,5 , 那么填入的是1,2,3,4,5,1,2,3,4,5,1,2,3,4,5........

 **3、开始对状态向量S进行置换操作（用来打乱初始种子1）**

按照下列规则进行：

从第零个字节开始，执行256次，保证每个字节都得到处理,确保处理后的状态向量S带有一定的随机性。

    
    
    j = 0;  
    for (i = 0 ; i < 256 ; i++){  
    j = (j + S[i] + T[i]) mod 256;  
    swap(S[i] , S[j]);  
    }

 **4、密钥流的生成与加密**

假设我的明文字节数是datalength=1024个字节（当然可以是任意个字节）

    
    
    i=0;  
    j=0;  
    while(datalength--){//相当于执行1024次，这样生成的秘钥流也是1024个字节  
    i = (i + 1) mod 256;  
    j = (j + S[i]) mod 256;  
    swap(S[i] , S[j]);  
    t = (S[i] + S[j]) mod 256;  
    k = S[t];这里的K就是当前生成的一个秘钥流中的一位  
    //可以直接在这里进行加密，当然也可以将密钥流保存在数组中，最后进行异或就ok  
    data[]=data[]^k； //进行加密，"^"是异或运算符  
    }

### RC4算法逆向特征识别

我们在使用ida等逆向分析软件识别RC4算法时，应当注意哪些特征呢？主要有下述三条：

    
    
    S盒与T盒的数据填充过程：2个长度为256的For循环  
    S盒乱序时的数据交换  
    以及最后的异或加解密

#### S盒与T盒的数据填充过程：2个长度为256的For循环，填充1~255

![image-20220305111909615](https://image.3001.net/images/20220320/1647777896_6237186829c665763b713.png!small)

![image-20220305111941270](https://image.3001.net/images/20220320/1647777901_6237186d0fa05bec4fac2.png!small)

#### s盒乱序时的数据交换过程

![img](https://image.3001.net/images/20220320/1647777909_623718752a9e48b272d8d.png!small)

#### 异或/加解密操作

![img](https://image.3001.net/images/20220320/1647777911_62371877646b5146d7f05.png!small)

#### 软件辅助识别：

对于标准加密算法，也可以借助PEID的“Krypto ANALyzer”插件，或者IDA的“FindCrypt2”插件进行识别。

## RC4 算法出题与做题

### 出题：菜鸡的一次c++rc4加密尝试

通过上文介绍，我们对于RC4算法以及有了一个初步的认识，这样我们尝试使用c++写出一道简单的rc4加密逆向题目，源码如下

    
    
    #include<bits/stdc++.h>  
    #include<windows.h>  
    using namespace std;  
    char* base64Encode(char const* origSigned, unsigned origLength)   //由于rc4加密后多为不可见字符或乱码，采用base64做中介  
    {    
    static const char base64Char[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";   
    unsigned char const* orig = (unsigned char const*)origSigned;    
    if (orig == NULL) return NULL;    
      
    unsigned const numOrig24BitValues = origLength/3;    
    bool havePadding = origLength > numOrig24BitValues*3;    
    bool havePadding2 = origLength == numOrig24BitValues*3 + 2;    
    unsigned const numResultBytes = 4*(numOrig24BitValues + havePadding);    
    char* result = new char[numResultBytes+1];    
      
    // Map each full group of 3 input bytes into 4 output base-64 characters:    
    unsigned i;    
    for (i = 0; i < numOrig24BitValues; ++i)     
    {    
    result[4*i+0] = base64Char[(orig[3*i]>>2)&0x3F];    
    result[4*i+1] = base64Char[(((orig[3*i]&0x3)<<4) | (orig[3*i+1]>>4))&0x3F];    
    result[4*i+2] = base64Char[(((orig[3*i+1]&0x0f)<<2) | (orig[3*i+2]>>6))&0x3F];    
    result[4*i+3] = base64Char[(orig[3*i+2]&0x3f)&0x3F];    
    }    
      
    // Now, take padding into account.  (Note: i == numOrig24BitValues)    
    if (havePadding)     
    {    
    result[4*i+0] = base64Char[(orig[3*i]>>2)&0x3F];    
    if (havePadding2)    
    {    
    result[4*i+1] = base64Char[(((orig[3*i]&0x3)<<4) | (orig[3*i+1]>>4))&0x3F];    
    result[4*i+2] = base64Char[((orig[3*i+1]&0x0f)<<2)&0x3F];    
    }     
    else     
    {    
    result[4*i+1] = base64Char[((orig[3*i]&0x3)<<4)&0x3F];    
    result[4*i+2] = '=';    
    }    
    result[4*i+3] = '=';    
    }    
      
    result[numResultBytes] = '/0';    
    return result;    
    }   
    ​  
    ​  
    void mima_init(unsigned char *s,unsigned char *key,unsigned long Len)//初始化  
    {  
    char t[256]={0};  
    unsigned char tmp=0;  
    for(int i=0;i<256;i++)//初始化s盒   
    {  
    s[i]=i;  
    t[i]=key[i%Len];  
    }  
    for(int i=0;i<256;i++)//s盒乱序   
    {  
    int j=(j+s[i]+t[i])%256;  
    tmp=s[i];  
    s[i]=s[j];  
    s[j]=tmp;  
    }   
    }   
    //加解密共用函数  
    char mima_crypt(unsigned char *s,unsigned char *Data,unsigned long Len)  
    {  
    int i=0,j=0,t=0;  
    unsigned long k=0;  
    unsigned char tmp;  
    for(k=0;k<Len;k++)  
    {  
    //密钥流  
    i=(i+1)%256;  
    j=(j+s[i])%256;  
    tmp=s[i];  
    s[i]=s[j];  
    s[j]=tmp;  
    t=(s[i]+s[j])%256;  
    //异或加解密  
    Data[k]^=s[t];   
    }     
    }  
    ​  
    int getStr(char *buffer,int maxLen){  
    char c;  // 读取到的一个字符  
    int len = 0;  // 当前输入的字符串的长度  
    // 一次读取一个字符，保存到buffer  
    // 直到遇到换行符(\n)，或者长度超过maxLen时，停止读取  
    while( (c=getchar()) != '\n' ){  
    buffer[len++]=c;  // 将读取到的字符保存到buffer  
    if(len>=maxLen){  
    break;  
    }  
    }  
    buffer[len]='\0';  // 读取结束，在末尾手动添加字符串结束标志  
    fflush(stdin);  // 刷新输入缓冲区  
    return len;  
    }  
    ​  
    ​  
    int main(int argc,_TCHAR* argv[])  
    {  
    char key[256]={""};//可以自定义key  
    char flag[25];  
    uint8_t keyLen = 0;  
    char pData[256]={"f5pwXQlV5R9HMfFL6pt3YdVEeP5d9DA="};//密文  
    unsigned char s1[256]={0},s2[256]={0};  
    unsigned long len= strlen(pData);  
    printf("please input your flag:\n");  
    getStr(flag,23);  
    //初始化  
    //unsigned long len= strlen(flag2);  
    mima_init(s1, (unsigned char*)key, strlen(key));  
    mima_crypt(s1, (unsigned char*)flag, len);  
    //cout<<(unsigned char*)base64Encode(flag,strlen(flag));  
    if(!strcmp("rFZuHVPo6wTcVnbgu176lPOJWixo93wdm2ULsM5fFrc=0",base64Encode(flag,strlen(flag))))//判定机制写的不完善导致的暴力判定  
    printf("you are right good boy!\n");  
    else  
    printf("Try again!");  
    cout<<(unsigned char*)base64Encode(flag,strlen(flag));  
    } 

p.s:本菜鸡的第一次出题尝试，如有不妥之处，欢迎各位大佬评论指教

### 做题：[安恒杯2018-9月]NewDriver

老规矩，拿到re题目先查壳。无壳32位。ida打开。

好样的，上来就整个假flag欺骗我们的感情。

![Ujx53DSnEvhoq7w.png](https://image.3001.net/images/20220320/1647777914_6237187ad8706a7843a5c.png!small)

发现三个可疑的可能与加解密相关的函数

![image-20220308111037385](https://image.3001.net/images/20220320/1647777917_6237187d9659c3cb08c51.png!small)

显然是一个base64加密，且搜索字符串中找到了自定义的base64表，印证了我们的猜测。

![image-20220308111428149](https://image.3001.net/images/20220320/1647777922_623718820feba5722caae.png!small)

跟进剩下两个关键函数，发现rc4加密特征(异或，s盒初始化，处理密钥流过程中的%256)

![image-20220308110250407](https://image.3001.net/images/20220320/1647777924_62371884bfb850db1af6c.png!small)

![image-20220308110312290](https://image.3001.net/images/20220320/1647777927_6237188731f988382f381.png!small)

在ida中可以直接获取密文，获取key的话要使用动态调试从内存中读取

这个时候我们只需要模拟异或过程就可以了

    
    
    key = '7a a6 6a da cd 0f 16 74 8b be 29 67 aa 79 79 b2 42 64 b2 2c bc 93 18 07 19 6f b7 64 fd 52 59 4f 96 ea 49 3c 11 89 66 39 87 d3 59 84'  
    en_flag = '20 C3 1A AE 97 3C 7A 41 DE F6 78 15 CB 4B 4C DC 26 55 8B 55 E5 E9 55 75 40 3D 82 13 A5 60 13 3B F5 D8 19 0E 47 CF 5F 5E DE 9D 14 BD'  
    key = key.split(' ')  
    en_flag = en_flag.split(' ')  
    en_flags = []  
    keys = []  
    ​  
    g = ''  
    for i in key:  
    keys.append(int(i, 16))  
    for i in en_flag:  
    en_flags.append(int(i, 16))  
    ​  
    for q in range(len(key)):  
    g += chr(keys[q] ^ en_flags[q])  
    print(g)

运行脚本后再base64解密得到flag

![image-20220308112736129](https://image.3001.net/images/20220320/1647777932_6237188cdba5ce92c2c7c.png!small)

顺便存一手base64换表脚本准备不能联网的线下赛。

    
    
    import base64  
    import string  
    ​  
    str1 = "x2dtJEOmyjacxDemx2eczT5cVS9fVUGvWTuZWjuexjRqy24rV29q"  
    ​  
    string1 = "ZYXABCDEFGHIJKLMNOPQRSTUVWzyxabcdefghijklmnopqrstuvw0123456789+/"  
    string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"  
    ​  
    print (base64.b64decode(str1.translate(str.maketrans(string1,string2))))

  

## 参考文章

> <https://blog.csdn.net/kdsj_0030/article/details/82889826>
>
> <https://www.52pojie.cn/thread-800115-1-1.html>
>
> <https://www.cnblogs.com/SunsetR/p/12247041.html>
>
> [https://xz.aliyun.com/t/3753﻿](https://xz.aliyun.com/t/3753)
>
> <https://xz.aliyun.com/t/5644>
>
> <https://bbs.pediy.com/thread-262472.htm>
>
> <https://blog.csdn.net/CharlesGodX/article/details/90065683>
>
> <https://www.cnblogs.com/SunsetR/p/12247041.html>
>
> <https://www.cnblogs.com/iBinary/p/14023091.html>


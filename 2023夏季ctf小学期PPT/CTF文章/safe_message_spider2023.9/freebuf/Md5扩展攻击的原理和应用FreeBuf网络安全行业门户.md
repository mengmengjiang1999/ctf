**做CTF题目的过程中遇到了md5扩展攻击，参考了几篇文章，感觉写的都有些小缺陷，再发一篇文章，理解md5扩展攻击首先需要了解md5的工作原理。**

## 1）md5的工作原理

具体参考这两篇文章

<http://blog.csdn.net/adidala/article/details/28677393>，算法实现有误

<https://www.rfc-editor.org/rfc/pdfrfc/rfc1321.txt.pdf>，算法正确

md5的算法原理如下图所示

![](https://image.3001.net/images/20210828/1630150463_612a1f3f5443a7179a353.png!small)

Md5的算法步骤是

### 1、填充

将数据进行填充，首先添加0x80，接着添加0x00使得 （数据字节数 + 8）%64 = 0

### 2、增加长度

将数据的长度放入8字节的数组中，把低字节放到前面，例如长度为1,8字节的数据长度表示为00 00 00 00 00 00 00
01，把这个长度值转化为低字节在前面变成了01 00 00 00 00 00 00 00，将这个数据加入到整体的数据中。

### 3、进行轮次变换

以64个字节为1组进行轮次变换，这一组中以4字节为1个单位分成16个数字。

首先准备A，B,C,D四个32位的字符，其中， A = 0x67452301，B = 0xefcdab89

，C = 0x98badcfe,D = 0x10325476, 将ABCD作为种子，与16个数字进行一种复杂的运算（运算方式见后文），运算结果为A1 B1
C1 D1,以A1 B1 C1 D1为种子然后重复这个过程计算最后得到AnBnCnDn

### 4、输出hash值

将An进行类似于第二步的低字节顺序的排列An’，同理对Bn，Cn，Dn进行同样变换，An’，Bn’,Cn’,Dn’的简单拼接就是最后结果。

注：这里简单记录一下正确的复杂算法

文献1中的算法是错误的，正确的算法是

    
    
    定义其中几个子算法
    
    F = lambdax,y,z:((x&y)|((~x)&z))
    
    G = lambdax,y,z:((x&z)|(y&(~z)))
    
    H = lambdax,y,z:(x^y^z)
    
    I = lambdax,y,z:(y^(x|(~z)))
    
    defshift(a, count):return(((a << count) | (a >> (32-count)))&0xffffffff)
    
    常量表：
    
    T_func = lambdai: int(4294967296*abs(math.sin(i))) & 0xffffffffT = [T_func(i) fori inxrange(1, 65)]
    
    T.insert(0, 0)
    
    复杂算法为
    
            INPUT_A = A
    
            INPUT_B = B
    
            INPUT_C = C
    
            INPUT_D = D
    
            M = [ (myord[i * 64+ j + 3] <<24) +  (myord[i * 64+ j + 2] << 16)+ (myord[i * 64+ j + 1] << 8) + (myord[i * 64+ j + 0] )\
    
                 forj inxrange(0, 64, 4)]
    
            defshift(a, count):return(((a << count) | (a >> (32-count)))&0xffffffff)
    
            #第一轮A = (B+ shift((A+F(B,C,D)+M[0]+T[1]) &0xffffffff,7) ) & 0xffffffffD = (A+shift((D+F(A,B,C)+M[1]+T[2]) &0xffffffff,12) )& 0xffffffffC = (D+shift((C+F(D,A,B)+M[2]+T[3]) &0xffffffff,17) ) &0xffffffffB = (C+shift((B+F(C,D,A)+M[3]+T[4]) &0xffffffff,22) )&0xffffffffA = (B+shift((A+F(B,C,D)+M[4]+T[5]) &0xffffffff,7) )&0xffffffffD = (A+shift((D+F(A,B,C)+M[5]+T[6])&0xffffffff,12) )&0xffffffffC = (D+shift((C+F(D,A,B)+M[6]+T[7]) &0xffffffff,17) )&0xffffffffB = (C+shift((B+F(C,D,A)+M[7]+T[8]) &0xffffffff,22) )&0xffffffff
    
            A = (B+shift((A+F(B,C,D)+M[8]+T[9])&0xffffffff,7) )&0xffffffffD = (A+shift((D+F(A,B,C)+M[9]+T[10])&0xffffffff,12) )&0xffffffffC = (D+shift((C+F(D,A,B)+M[10]+T[11])&0xffffffff,17) )&0xffffffffB = (C+shift((B+F(C,D,A)+M[11]+T[12])&0xffffffff,22) )&0xffffffffA = (B+shift((A+F(B,C,D)+M[12]+T[13])&0xffffffff,7) )&0xffffffffD = (A+shift((D+F(A,B,C)+M[13]+T[14])&0xffffffff,12) )&0xffffffffC = (D+shift((C+F(D,A,B)+M[14]+T[15])&0xffffffff,17) )&0xffffffffB = (C+shift((B+F(C,D,A)+M[15]+T[16])&0xffffffff,22) )&0xffffffff#第二轮A = (B+shift((A+G(B,C,D)+M[1]+T[17])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[6]+T[18]) &0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[11]+T[19])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[0]+T[20])&0xffffffff,20) )&0xffffffffA = (B+shift((A+G(B,C,D)+M[5]+T[21])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[10]+T[22])&0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[15]+T[23])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[4]+T[24])&0xffffffff,20) )&0xffffffffA = (B+shift((A+G(B,C,D)+M[9]+T[25])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[14]+T[26])&0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[3]+T[27])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[8]+T[28])&0xffffffff,20) )&0xffffffffA = (B+shift((A+G(B,C,D)+M[13]+T[29])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[2]+T[30])&0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[7]+T[31])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[12]+T[32])&0xffffffff,20))&0xffffffff#第三轮A = (B+shift((A+H(B,C,D)+M[5]+T[33])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[8]+T[34])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[11]+T[35])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[14]+T[36])&0xffffffff,23) )&0xffffffffA = (B+shift((A+H(B,C,D)+M[1]+T[37])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[4]+T[38])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[7]+T[39])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[10]+T[40])&0xffffffff,23) )&0xffffffffA = (B+shift((A+H(B,C,D)+M[13]+T[41])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[0]+T[42])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[3]+T[43])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[6]+T[44])&0xffffffff,23) )&0xffffffffA = (B+shift((A+H(B,C,D)+M[9]+T[45])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[12]+T[46])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[15]+T[47])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[2]+T[48])&0xffffffff,23))&0xffffffff#第四轮A = (B+shift((A+I(B,C,D)+M[0]+T[49])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[7]+T[50])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[14]+T[51])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[5]+T[52])&0xffffffff,21) )&0xffffffffA = (B+shift((A+I(B,C,D)+M[12]+T[53])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[3]+T[54])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[10]+T[55])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[1]+T[56])&0xffffffff,21) )&0xffffffffA = (B+shift((A+I(B,C,D)+M[8]+T[57])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[15]+T[58])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[6]+T[59])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[13]+T[60])&0xffffffff,21) )&0xffffffffA = (B+shift((A+I(B,C,D)+M[4]+T[61])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[11]+T[62])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[2]+T[63])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[9]+T[64])&0xffffffff,21))&0xffffffffA = (A + INPUT_A) & 0xffffffffB = (B + INPUT_B) & 0xffffffffC = (C + INPUT_C) & 0xffffffffD = (D + INPUT_D) & 0xffffffff

Md5算法实现python版本见第三节的中的my_md5>函数实现

理解的md5算法的原理，下面开始讲解md5扩展攻击

## 2）Md5攻击扩展攻击

首先可以参考这篇文章（<http://www.freebuf.com/articles/web/69264.html>），本文将对这篇文章进行补充说明。

从md5算法原理可以知道，每一轮次计算的ABCD将作为下一轮次计算的初始值，假设我们已知一个数字x的md5值为y，其中x为未知量，即y=md5（x），同时已知x的长度，那么我们就能进行md5扩展攻击，因为我们知道y为md5（x）计算完毕后的ABCD值的简单组合，通过md5的算法可知y
= f（x + x的填充值），如果我们增加x1，计算y’=f( (x + x的填充值+x1 ) + (x + x的填充值+x1 ) 的填充值
)则变得可能，应为y’可以使用y转化的AB

CD值同(x1 + (x + x的填充值+x1 ) 的填充值)再进行一轮次的计算既可以得出。

下图阐述了上述算法原理

![](https://image.3001.net/images/20210828/1630150464_612a1f4025b071ec77567.png!small)

其中标号1为原始数据x，标号2位原始数据x的填充长度，标号3表示新增加的数据，标号4为标号1,2,3的填充和长度。如果我们已知一个计算出来的hash值，同时知道明文的长度，则我们可以构造标号2的数据，标号3，计算未知数md5值的函数（如服务器端的程序），拿到我们构造的标号2和标号3的数据，会自动添加标号4的数据，计算完标号1和和标号2产生ABCD，接着会产生hash值，这时这个hash值就是可以预测。

攻击者可以计算出标号3和标号4，以ABCD作为输入进行计算本地产出的hash值和服务端计算出的hash值是一致的。

攻击者的视角如下图所示。

![](https://image.3001.net/images/20210828/1630150464_612a1f40d0fdcb533cabe.png!small)

1、攻击者提供标号2，标号3，标号4的数据

2、服务端计算到标号2的位置刚好为ABCD这个已知数据

3、攻击者在本地根据标号3和标号4的数据和ABCD值计算hash值攻击成功

而服务端的视角是，攻击者提供了标号2和标号3的数据，服务端计算了标号4的数据，同时服务端产出ABCD，发现没有计算完成，接着运行md5算法，计算出的新的hash值和攻击者一致。

综上所述要想进行此类攻击需要知道两个条件

1、标号1数据的长度。

2、标号1数据的md5值。

最后总结一下攻击步骤

第一步：根据标号1的长度计算标号2的数据，提供标号3的数据，本地计算标号4 的数据，并计算加上标号3和标号4数据后的hash值。

第二步：发送计算出来的hash，和标号2，标号3的数据，攻击成功。

## 3）程序展示

展示python编写的MD5程序和md5扩展攻击的程序

    
    
    #-*- coding=utf-8 -*-importmath
    
    defmy_md5_extend(salt_hash,  salt_length, added_message):#计算需要填充的数据added_data = [0x80];
        x = salt_length + 1;
        while(x + 8) % 64!= 0:
            x += 1;
            added_data.append(0x00);
        salt_length *= 8;
        salt_length = salt_length  % (2** 64);
        salt_length = hex(salt_length);
        salt_length = salt_length[2:len(salt_length)-1].rjust(16, '0');
        salt_length = [int(format(salt_length[i:i+2]), 16) fori inxrange(0, len(salt_length), 2)][::-1]
        #下面的数据用于加在payload后面added_data.extend(salt_length); #important#打印payloadprint''.join(['%'+ hex(item).replace('0x', '').rjust(2,'0') foritem inadded_data])
        
        #增加新加的数据，然后使用已经md5的数据进行扩展计算，计算出来一个新的hash值myord = map(ord, added_message);
        myord.append(0x80);
        added_length = (x + 8+ len(added_message)) ;
        y = x + 8+ len(added_message) + 1;
        while(y + 8) % 64!= 0:
            y += 1;
            myord.append(0x00);
            
        added_length *= 8;
        added_length = added_length  % (2** 64);
        added_length = hex(added_length);
        added_length = added_length[2:len(added_length)-1].rjust(16, '0');
        added_length = [int(format(added_length[i:i+2]), 16) fori inxrange(0, len(added_length), 2)][::-1]
        myord.extend(added_length);
        
        #使用已经计算出来的hashmyA, myB, myC, myD = ( int(salt_hash[i +6: i + 8] +salt_hash[i + 4: i + 6] +salt_hash[i + 2:i + 4] +salt_hash[i + 0: i + 2], 16)  fori inxrange(0, len(salt_hash), 8));
        
        A = myA;
        B = myB;
        C = myC;
        D = myD;
        
        F= lambdax,y,z:((x&y)|((~x)&z))  
        G = lambdax,y,z:((x&z)|(y&(~z)))  
        H = lambdax,y,z:(x^y^z)  
        I = lambdax,y,z:(y^(x|(~z)))  
    
        T_func = lambdai: int(4294967296*abs(math.sin(i))) & 0xffffffffT= [T_func(i) fori inxrange(1, 65)]
        T.insert(0, 0)
        #进行hash计算fori inxrange(0, len(myord) / 64):
            INPUT_A = A
            INPUT_B = B
            INPUT_C = C
            INPUT_D = D
            
            M = [ (myord[i * 64+ j + 3] <<24) +  (myord[i * 64+ j + 2] << 16)+ (myord[i * 64+ j + 1] << 8) + (myord[i * 64+ j + 0] )\
                 forj inxrange(0, 64, 4)]
    
            defshift(a, count):return(((a << count) | (a >> (32-count)))&0xffffffff)
            
            #第一轮A = (B+ shift((A+F(B,C,D)+M[0]+T[1]) &0xffffffff,7) ) & 0xffffffffD = (A+shift((D+F(A,B,C)+M[1]+T[2]) &0xffffffff,12) )& 0xffffffffC = (D+shift((C+F(D,A,B)+M[2]+T[3]) &0xffffffff,17) ) &0xffffffffB = (C+shift((B+F(C,D,A)+M[3]+T[4]) &0xffffffff,22) )&0xffffffffA = (B+shift((A+F(B,C,D)+M[4]+T[5]) &0xffffffff,7) )&0xffffffffD = (A+shift((D+F(A,B,C)+M[5]+T[6])&0xffffffff,12) )&0xffffffffC = (D+shift((C+F(D,A,B)+M[6]+T[7]) &0xffffffff,17) )&0xffffffffB = (C+shift((B+F(C,D,A)+M[7]+T[8]) &0xffffffff,22) )&0xffffffffA = (B+shift((A+F(B,C,D)+M[8]+T[9])&0xffffffff,7) )&0xffffffffD = (A+shift((D+F(A,B,C)+M[9]+T[10])&0xffffffff,12) )&0xffffffffC = (D+shift((C+F(D,A,B)+M[10]+T[11])&0xffffffff,17) )&0xffffffffB = (C+shift((B+F(C,D,A)+M[11]+T[12])&0xffffffff,22) )&0xffffffffA = (B+shift((A+F(B,C,D)+M[12]+T[13])&0xffffffff,7) )&0xffffffffD = (A+shift((D+F(A,B,C)+M[13]+T[14])&0xffffffff,12) )&0xffffffffC = (D+shift((C+F(D,A,B)+M[14]+T[15])&0xffffffff,17) )&0xffffffffB = (C+shift((B+F(C,D,A)+M[15]+T[16])&0xffffffff,22) )&0xffffffff#第二轮A = (B+shift((A+G(B,C,D)+M[1]+T[17])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[6]+T[18]) &0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[11]+T[19])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[0]+T[20])&0xffffffff,20) )&0xffffffffA = (B+shift((A+G(B,C,D)+M[5]+T[21])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[10]+T[22])&0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[15]+T[23])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[4]+T[24])&0xffffffff,20) )&0xffffffffA = (B+shift((A+G(B,C,D)+M[9]+T[25])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[14]+T[26])&0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[3]+T[27])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[8]+T[28])&0xffffffff,20) )&0xffffffffA = (B+shift((A+G(B,C,D)+M[13]+T[29])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[2]+T[30])&0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[7]+T[31])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[12]+T[32])&0xffffffff,20))&0xffffffff#第三轮A = (B+shift((A+H(B,C,D)+M[5]+T[33])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[8]+T[34])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[11]+T[35])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[14]+T[36])&0xffffffff,23) )&0xffffffffA = (B+shift((A+H(B,C,D)+M[1]+T[37])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[4]+T[38])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[7]+T[39])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[10]+T[40])&0xffffffff,23) )&0xffffffffA = (B+shift((A+H(B,C,D)+M[13]+T[41])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[0]+T[42])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[3]+T[43])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[6]+T[44])&0xffffffff,23) )&0xffffffffA = (B+shift((A+H(B,C,D)+M[9]+T[45])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[12]+T[46])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[15]+T[47])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[2]+T[48])&0xffffffff,23))&0xffffffff#第四轮A = (B+shift((A+I(B,C,D)+M[0]+T[49])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[7]+T[50])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[14]+T[51])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[5]+T[52])&0xffffffff,21) )&0xffffffffA = (B+shift((A+I(B,C,D)+M[12]+T[53])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[3]+T[54])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[10]+T[55])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[1]+T[56])&0xffffffff,21) )&0xffffffffA = (B+shift((A+I(B,C,D)+M[8]+T[57])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[15]+T[58])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[6]+T[59])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[13]+T[60])&0xffffffff,21) )&0xffffffffA = (B+shift((A+I(B,C,D)+M[4]+T[61])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[11]+T[62])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[2]+T[63])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[9]+T[64])&0xffffffff,21))&0xffffffffA = (A + INPUT_A) & 0xffffffffB = (B + INPUT_B) & 0xffffffffC = (C + INPUT_C) & 0xffffffffD = (D + INPUT_D) & 0xffffffffdefshow_result(A, B, C, D):result = "";
            mya = [hex(A)[2:len(hex(A)[2:]) ifhex(A).find('L') == -1else-1].rjust(8, '0')[k:k+2] fork inxrange(0, 8, 2)][::-1]
            myb = [hex(B)[2:len(hex(B)[2:]) ifhex(B).find('L') == -1else-1].rjust(8, '0')[k:k+2] fork inxrange(0, 8, 2)][::-1]
            myc = [hex(C)[2:len(hex(C)[2:]) ifhex(C).find('L') == -1else-1].rjust(8, '0')[k:k+2] fork inxrange(0, 8, 2)][::-1]
            myd = [hex(D)[2:len(hex(D)[2:]) ifhex(D).find('L') == -1else-1].rjust(8, '0')[k:k+2] fork inxrange(0, 8, 2)][::-1]
            return''.join(mya + myb + myc + myd)
        returnshow_result(A, B, C, D);
        
            
    
    
    
    printmy_md5_extend('571580b26c65f306376d4f64e53cb5c7', 15+ len('adminadmin'), 'nb'); 
    
    
    defmy_md5(mystring):#第一步填充#mystring = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'myord =map(ord, mystring);#转化成为16进制的arraymyord_length = len(myord) * 8;
        myord.append(0x80);
    
        while(len(myord) * 8+ 64)% 512!= 0:
            myord.append(0x00);
    
    
        #第二步增加长度myord_length = myord_length % (2** 64);
        
        myord_length = hex(myord_length);
        
        myord_length = myord_length[2:len(myord_length)-1].rjust(16, '0');
        
        myord_length = [int(format(myord_length[i:i+2]), 16) fori inxrange(0, len(myord_length), 2)][::-1]
        
        myord.extend(myord_length)
    
    
        #对每一个512位做处理A = 0x67452301B = 0xefcdab89C = 0x98badcfeD = 0x10325476F= lambdax,y,z:((x&y)|((~x)&z))  
        G = lambdax,y,z:((x&z)|(y&(~z)))  
        H = lambdax,y,z:(x^y^z)  
        I = lambdax,y,z:(y^(x|(~z)))  
    
        T_func = lambdai: int(4294967296*abs(math.sin(i))) & 0xffffffffT= [T_func(i) fori inxrange(1, 65)]
        T.insert(0, 0)#错误的位置fori inxrange(0, len(myord) / 64):
            INPUT_A = A
            INPUT_B = B
            INPUT_C = C
            INPUT_D = D
            
            M = [ (myord[i * 64+ j + 3] <<24) +  (myord[i * 64+ j + 2] << 16)+ (myord[i * 64+ j + 1] << 8) + (myord[i * 64+ j + 0] )\
                 forj inxrange(0, 64, 4)]
    
            defshift(a, count):return(((a << count) | (a >> (32-count)))&0xffffffff)
            
            #第一轮A = (B+ shift((A+F(B,C,D)+M[0]+T[1]) &0xffffffff,7) ) & 0xffffffffD = (A+shift((D+F(A,B,C)+M[1]+T[2]) &0xffffffff,12) )& 0xffffffffC = (D+shift((C+F(D,A,B)+M[2]+T[3]) &0xffffffff,17) ) &0xffffffffB = (C+shift((B+F(C,D,A)+M[3]+T[4]) &0xffffffff,22) )&0xffffffffA = (B+shift((A+F(B,C,D)+M[4]+T[5]) &0xffffffff,7) )&0xffffffffD = (A+shift((D+F(A,B,C)+M[5]+T[6])&0xffffffff,12) )&0xffffffffC = (D+shift((C+F(D,A,B)+M[6]+T[7]) &0xffffffff,17) )&0xffffffffB = (C+shift((B+F(C,D,A)+M[7]+T[8]) &0xffffffff,22) )&0xffffffffA = (B+shift((A+F(B,C,D)+M[8]+T[9])&0xffffffff,7) )&0xffffffffD = (A+shift((D+F(A,B,C)+M[9]+T[10])&0xffffffff,12) )&0xffffffffC = (D+shift((C+F(D,A,B)+M[10]+T[11])&0xffffffff,17) )&0xffffffffB = (C+shift((B+F(C,D,A)+M[11]+T[12])&0xffffffff,22) )&0xffffffffA = (B+shift((A+F(B,C,D)+M[12]+T[13])&0xffffffff,7) )&0xffffffffD = (A+shift((D+F(A,B,C)+M[13]+T[14])&0xffffffff,12) )&0xffffffffC = (D+shift((C+F(D,A,B)+M[14]+T[15])&0xffffffff,17) )&0xffffffffB = (C+shift((B+F(C,D,A)+M[15]+T[16])&0xffffffff,22) )&0xffffffff#第二轮A = (B+shift((A+G(B,C,D)+M[1]+T[17])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[6]+T[18]) &0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[11]+T[19])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[0]+T[20])&0xffffffff,20) )&0xffffffffA = (B+shift((A+G(B,C,D)+M[5]+T[21])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[10]+T[22])&0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[15]+T[23])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[4]+T[24])&0xffffffff,20) )&0xffffffffA = (B+shift((A+G(B,C,D)+M[9]+T[25])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[14]+T[26])&0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[3]+T[27])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[8]+T[28])&0xffffffff,20) )&0xffffffffA = (B+shift((A+G(B,C,D)+M[13]+T[29])&0xffffffff,5) )&0xffffffffD = (A+shift((D+G(A,B,C)+M[2]+T[30])&0xffffffff,9) )&0xffffffffC = (D+shift((C+G(D,A,B)+M[7]+T[31])&0xffffffff,14) )&0xffffffffB = (C+shift((B+G(C,D,A)+M[12]+T[32])&0xffffffff,20))&0xffffffff#第三轮A = (B+shift((A+H(B,C,D)+M[5]+T[33])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[8]+T[34])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[11]+T[35])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[14]+T[36])&0xffffffff,23) )&0xffffffffA = (B+shift((A+H(B,C,D)+M[1]+T[37])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[4]+T[38])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[7]+T[39])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[10]+T[40])&0xffffffff,23) )&0xffffffffA = (B+shift((A+H(B,C,D)+M[13]+T[41])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[0]+T[42])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[3]+T[43])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[6]+T[44])&0xffffffff,23) )&0xffffffffA = (B+shift((A+H(B,C,D)+M[9]+T[45])&0xffffffff,4) )&0xffffffffD = (A+shift((D+H(A,B,C)+M[12]+T[46])&0xffffffff,11) )&0xffffffffC = (D+shift((C+H(D,A,B)+M[15]+T[47])&0xffffffff,16) )&0xffffffffB = (C+shift((B+H(C,D,A)+M[2]+T[48])&0xffffffff,23))&0xffffffff#第四轮A = (B+shift((A+I(B,C,D)+M[0]+T[49])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[7]+T[50])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[14]+T[51])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[5]+T[52])&0xffffffff,21) )&0xffffffffA = (B+shift((A+I(B,C,D)+M[12]+T[53])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[3]+T[54])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[10]+T[55])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[1]+T[56])&0xffffffff,21) )&0xffffffffA = (B+shift((A+I(B,C,D)+M[8]+T[57])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[15]+T[58])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[6]+T[59])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[13]+T[60])&0xffffffff,21) )&0xffffffffA = (B+shift((A+I(B,C,D)+M[4]+T[61])&0xffffffff,6) )&0xffffffffD = (A+shift((D+I(A,B,C)+M[11]+T[62])&0xffffffff,10) )&0xffffffffC = (D+shift((C+I(D,A,B)+M[2]+T[63])&0xffffffff,15) )&0xffffffffB = (C+shift((B+I(C,D,A)+M[9]+T[64])&0xffffffff,21))&0xffffffffA = (A + INPUT_A) & 0xffffffffB = (B + INPUT_B) & 0xffffffffC = (C + INPUT_C) & 0xffffffffD = (D + INPUT_D) & 0xffffffffdefshow_result(A, B, C, D):result = "";
            mya = [hex(A)[2:len(hex(A)[2:]) ifhex(A).find('L') == -1else-1].rjust(8, '0')[k:k+2] fork inxrange(0, 8, 2)][::-1]
            myb = [hex(B)[2:len(hex(B)[2:]) ifhex(B).find('L') == -1else-1].rjust(8, '0')[k:k+2] fork inxrange(0, 8, 2)][::-1]
            myc = [hex(C)[2:len(hex(C)[2:]) ifhex(C).find('L') == -1else-1].rjust(8, '0')[k:k+2] fork inxrange(0, 8, 2)][::-1]
            myd = [hex(D)[2:len(hex(D)[2:]) ifhex(D).find('L') == -1else-1].rjust(8, '0')[k:k+2] fork inxrange(0, 8, 2)][::-1]
            return''.join(mya + myb + myc + myd)
        returnshow_result(A, B, C, D);
        
    

## 4）结语

在做ctf题目的时候加强对原理的理解，和动手实践，文字总结的方式可以帮助记忆。

## 参考文献：

【1】<http://blog.csdn.net/adidala/article/details/28677393>

【2】<https://www.rfc-editor.org/rfc/pdfrfc/rfc1321.txt.pdf>

【3】<http://www.freebuf.com/articles/web/69264.html>

 ***本文原创作者：Guilty and Innocent，本文属FreeBuf原创奖励计划，未经许可禁止转载**


RSA算法(不要求支持大数)

[ 坪河夜雨](https://www.jianshu.com/u/67c77b3a585b)关注赞赏支持

# RSA算法(不要求支持大数)

# 题目描述

C++中数据的类型与长度参考：(这里没显示，大概告诉你64位机器longlong8字节）

因此，C++最大能支持的十进制是19位的整数。如果要支持更大的整数，需要实现Big
Number类。RSA目前比较安全的密钥长度是2048位二进制，即是617位的十进制。因此，C++自带的数据类型无法实现安全的RSA密钥加解密。

为了降低难度，该题不要求实现大数支持，因此只使用C++自带的long long 数据类型。

该实验主要包含三部分：1. 公私钥的生成。  
在公私钥生成中，有p、q、e三个参数是随机选择的，其中p、q要求是质数，因此需要实现一个函数检查一个整数是否是质数。  
由p、q的乘积可以得到n：n=p*q，以及n的欧拉函数: φ(n) = (p-1)*(q-1)。  

e是在(1, φ(n))之间随机选取的整数，需要满足gcd(e, φ(n)) =
1，因此，需要通过扩展欧几里得算法验证取得的e是与φ(n)互质的。d可以通过扩展欧几里得算法求得 。以满足

，即

公钥为（n, e）,私钥为（n,d）

检查一个整数是否为质数-Rabin-
Miller算法，请参考：[https://blog.csdn.net/ECNU_LZJ/article/details/72675595](https://links.jianshu.com/go?to=https%3A%2F%2Fblog.csdn.net%2FECNU_LZJ%2Farticle%2Fdetails%2F72675595)或[https://www.cnblogs.com/zwfymqz/p/8150969.html](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.cnblogs.com%2Fzwfymqz%2Fp%2F8150969.html)或[https://www.cnblogs.com/zwfymqz/p/8150861.html](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.cnblogs.com%2Fzwfymqz%2Fp%2F8150861.html)

扩展欧几里得算法：请参考：[https://blog.csdn.net/u014117943/article/details/108428551](https://links.jianshu.com/go?to=https%3A%2F%2Fblog.csdn.net%2Fu014117943%2Farticle%2Fdetails%2F108428551)

2\. 加密过程，使用加密算法c = m^e mod n，计算出密文c；

3.解密过程，使用私钥d和解密算法m = c^d mod n, ，计算m；

加密和解密过程需要做幂运算取余，如果直接先做幂运算再取余，则很容易出现溢出，因此，我们需要采用快速幂运算取余算法，请参考：[https://jlice.top/p/7tbs7/](https://links.jianshu.com/go?to=https%3A%2F%2Fjlice.top%2Fp%2F7tbs7%2F)

因此，该次实验主要难点在于以下三个算法的理解与实现：

1\. Rabin-Miller算法

2\. 扩展欧几里得算法

3\. 快速幂取余算法

根据前面的算法，我们知道明文和密文都不能大于n，假设n的长度为L，对于明文，我们需要按照L-1的长度对其分组然后再加密，每组的密文长度L。解密的时候使用L的长度对其进行分组然后解密，每组的明文长度为L-1。分组按照整数从低到高（即从右往左）

### 输入

第一行是p

第二行是q

第三行是e

第四行是待加密数据

第五行是待解密数据

### 输出

第一行输出p是否是质数

第二行输出q是否是质数

第三行打印n

第四行打印d

第五行显示输入第四行的加密结果

第六行显示输入第五行的解密结果

### 输入样例1

67  
43  
13  
281  
2154

### 输出样例1

Yes  
Yes  
2881  
853  
325  
54

### 输入样例2

67  
43  
13  
54281  
3252154

### 输出样例2

Yes  
Yes  
2881  
853  
21540325  
281054

### 输入样例3

11  
17  
7  
88  
11

### 输出样例3

Yes  
Yes  
187  
23  
11  
88

# 解题

题目就是一个精简的RSA算法，由于题目强调没有大数，所以甚至用不到Go的math/big  
最核心的三个算法在题目描述中已经告诉我们了

> 1\. Rabin-Miller算法，判断一个数是否为质数  
>  2\. 扩展欧几里得算法，算逆元  
>  3\. 快速幂取余算法，低于O(n)的求幂算法

其实，还有一块我得强调，也是我一开始没有看到的地方  
就是题目描述最后的地方，当待加密的内容m与待解密的内容c大于n时，需要分组。  
可以这样实现：

    
    
    func buwei(num, wei int64) string {
        return fmt.Sprintf("%0*d", wei, num)
    }
    

然后判断一个数是否为质数，用到的Miller-Rabin算法  
没错，我没打反，因为它就叫做这个名字

    
    
    func Prime(n, trials int64) bool {
        if n < 2 {
            return false
        }
    
        var i int64
        for ; i < trials; i++ {
            r := rand.Intn(int(n)-1) + 1
            if mrCompositeWitness(int64(r), n) {
                return false
            }
        }
        return true
    }
    func mrCompositeWitness(a, n int64) bool {
        theBits := bits(n - 1)
        var rem int64 = 1
        for i := len(theBits) - 1; i >= 0; i-- {
            x := rem
            rem = (rem * rem) % n
    
            if rem == 1 && x != 1 && x != n-1 {
                return true
            }
    
            if theBits[i] == 1 {
                rem = (rem * a) % n
            }
    
        }
        if rem != 1 {
            return true
        }
        return false
    }
    func bits(n int64) []int64 {
        var bits []int64
        for ; n > 0; n = n >> 1 {
            bits = append(bits, n%2)
        }
        return bits
    }
    

求逆元的拓展欧几里得算法，我写在函数里

    
    
    var exgcd func(a, b int64) (gcd, x, y int64)
    exgcd = func(a, b int64) (gcd, x, y int64) {
            if b == 0 {
                return a, 1, 0
            }
            gcd, y, x = exgcd(b, a%b)
            y -= a / b * x
            return
        }
    

快速幂取模

    
    
    func quic(c,d,n int64) int64 {
        var ans int64 = 1
        for d!=0 {
            if d&0x1!=0 {
                ans = (ans*c)%n
            }
            c = (c*c) %n
            d >>= 1
        }
        return ans
    }
    

完整的代码如下，我就不加注释了

    
    
    package main
    
    import (
        "bufio"
        "fmt"
        "io"
        "math/rand"
        "os"
        "strconv"
    )
    
    const DefaultTrials = 6
    
    func bits(n int64) []int64 {
        var bits []int64
        for ; n > 0; n = n >> 1 {
            bits = append(bits, n%2)
        }
        return bits
    }
    
    func mrCompositeWitness(a, n int64) bool {
        theBits := bits(n - 1)
        var rem int64 = 1
        for i := len(theBits) - 1; i >= 0; i-- {
            x := rem
            rem = (rem * rem) % n
    
            if rem == 1 && x != 1 && x != n-1 {
                return true
            }
    
            if theBits[i] == 1 {
                rem = (rem * a) % n
            }
    
        }
        if rem != 1 {
            return true
        }
        return false
    }
    
    func Prime(n, trials int64) bool {
        if n < 2 {
            return false
        }
    
        var i int64
        for ; i < trials; i++ {
            r := rand.Intn(int(n)-1) + 1
            if mrCompositeWitness(int64(r), n) {
                return false
            }
        }
        return true
    }
    func check(num int64) {
        if Prime(num,DefaultTrials) {
            fmt.Println("Yes")
        }else {
            fmt.Println("No")
        }
    }
    func qpow(a, b int64) int64 {
        var ans int64 = 1
        p := b+2
        a = (a%p + p) % p
        for ; b != 0; b >>= 1 {
            if b&1 != 0 {
                ans = (a * ans) % p
            }
            a = a * a % p
        }
        return ans
    }
    func buwei(num, wei int64) string {
        return fmt.Sprintf("%0*d", wei, num)
    }
    func make_Key(m, e, n int64) string {
        if m<n {
            return strconv.Itoa(int(quic(m,e,n)))
        }
        if m < n {
            return strconv.Itoa(int(quic(m, e, n)))
        }
        length := len(strconv.Itoa(int(n))) - 1
        var wei int64 = 1
        for i := 0; i < length; i++ {
            wei *= 10
        }
        ans := ""
        for m != 0 {
            ans = buwei(quic(m%wei, e, n), int64(length)+1) + ans
            m /= wei
        }
        return ans
    }
    func de_Key(c, d, n int64) string {
        if c<n {
            return strconv.Itoa(int(quic(c,d,n)))
        }
        length := len(strconv.Itoa(int(n)))
    
        var wei int64 = 1
        for i := 0; i < length; i++ {
            wei *= 10
        }
        ans := ""
        for c != 0 {
            ans = buwei(quic(c%wei, d, n),int64(length-1)) + ans
            c /= wei
        }
        return ans
    }
    func quic(c,d,n int64) int64 {
        var ans int64 = 1
        for d!=0 {
            if d&0x1!=0 {
                ans = (ans*c)%n
            }
            c = (c*c) %n
            d >>= 1
        }
        return ans
    }
    func id194(_r io.Reader, _w io.Writer) {
        in := bufio.NewReader(_r)
        out := bufio.NewWriter(_w)
        defer out.Flush()
    
        var p,q,e,m,c int64
        fmt.Fscan(in,&p,&q,&e,&m,&c)
        check(p)
        check(q)
        fmt.Println(p*q)
        fai_n := (p-1)*(q-1)
        var exgcd func(a, b int64) (gcd, x, y int64)
        exgcd = func(a, b int64) (gcd, x, y int64) {
            if b == 0 {
                return a, 1, 0
            }
            gcd, y, x = exgcd(b, a%b)
            y -= a / b * x
            return
        }
        _,d,_ := exgcd(e,fai_n)
        fmt.Println(d)
        fmt.Println(make_Key(m,e,p*q))
        fmt.Println(de_Key(c,d,p*q))
    }
    func main() {
        id194(os.Stdin, os.Stdout)
    }
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [密码学基础1：RSA算法原理全面解析](https://www.jianshu.com/p/6aa7b59be872)

网上写 RSA 算法原理的文章不少，但是基本上要么忽略了数学原理的说明，要么缺少实际的可运行的例子，为此特写了此文...

[__七把刀__](https://www.jianshu.com/u/4d4a2f26740b)阅读 13,833评论 12赞 26

  * [RSA加密解密算法—数论基础](https://www.jianshu.com/p/67b11d2ecd26)

本章涉及知识点1、素数的定义2、寻找素数算法—短除法3、寻找素数算法—筛选法4、互质关系5、欧拉函数的证明6、欧拉...

[PrivateEye_zzy](https://www.jianshu.com/u/e44ca8d7ec37)阅读 3,622评论 0赞 6

  * [常用加密算法分析和实现](https://www.jianshu.com/p/2028400d76a0)

一、前言 工作中有时候需要对数据进行加密，就笔者从事的Android开发来说， 上层开发语言为Java/Kotli...

[呼啸长风](https://www.jianshu.com/u/11d3f06afbcd)阅读 713评论 0赞 0

  * [CTF常见RSA相关问题的解决（复现）](https://www.jianshu.com/p/0272069cb936)

本文参考https://findneo.github.io/180727rsa-attack/ 为对其知识进行掌握...

[Zerek_W](https://www.jianshu.com/u/6a0ccc27068c)阅读 7,478评论 0赞 3

  * [2018-06-05](https://www.jianshu.com/p/d5955e29e2d1)

关于使用python实现RSA加密解密 一、非对称加密算法 1、乙方生成两把密钥（公钥和私钥）。公钥是公开的，任何...

[ttaymm](https://www.jianshu.com/u/810d1cbb547d)阅读 676评论 0赞 0

 
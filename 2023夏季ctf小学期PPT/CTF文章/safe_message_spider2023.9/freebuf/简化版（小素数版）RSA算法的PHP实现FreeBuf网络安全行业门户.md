##  0x00 前言

**我们这学期的课程《信息安全与保密》要求期末作业实现一个密码算法及对应的加解密系统，其中做RSA的要求实现加解密、数字签名。考虑到我因为太菜，当初遇到了不少问题，莆田搜索RSA算法实现想参考一下的时候找不到PHP版本的，所以我完成作业后打算自己整一篇以供有需要的后来者参考**

**考虑到我们期末作业主要任务是“实现RSA加解密、数字签名”，故没有采用大整数运算，受PHP的数据精度限制，素数范围在2的32到48次方(4.29E9~2.81E14)**
，标题中的“简化版”即此意

由于在学校的时候事情比较多，所以一直拖到了放假才开始写，时间有点久了，有些细节记得不大清楚，而且受限于自己的水平，应该会有不少错漏；当时时间比较紧迫，函数封装等也不甚合理

文中内容主要摘自段云所、卫仕民、唐礼勇、陈钟所编《信息安全概论》（高等教育出版社，2003.9）及我上课记的笔记（特别注明之处除外），我的笔记可能也会有错漏之处，烦请海涵并指正
*/

> 建立一个RSA密码体制的过程如下：
>
>   1. 选择两个大素数p和q
>
>   2. 计算乘积n=pq和fai(n)=(p-1)(q-1)
>
>   3. 选择大于1小于fai(n)的随机整数e，使得gcd(e, fai(n))=1
>
>   4. 计算d使得de与1mod fai(n)同余
>
>   5. 对每一个密钥k=(n,p,q,d,e)，定义加密变换为Ek(x)=x^e mod n，解密变换为Dk(x)=y^d mod
> n，这里x,y属于整数
>
>   6. 以{e,n}为公开密钥，{p,q,d}为私有密钥
>
>

//其中的fai(n)即欧拉函数，意为“和n互素的数的数量”

##  0x01 Miller-Rabin算法（素性检测）

密钥中的p和q须为素数，而素数选取需要用到素性检测，Miller-Rabin算法可以实现素性检测。由William
Stallings所著的《密码编码学与网络安全——原理与实践（第七版）》可知Miller-Rabin算法如下:

> 过程TEST输入整数n， **若n不是素数，则返回“合数”，若n可能是素数，也可能不是素数时，返回“不确定”**  
> TEST(n)
>
>   1. 找出整数k, q，其中k>0, q是奇数，使(n-1=(2^k)*q)
>
>   2. 随机选取整数a, 1<a<n-1
>
>   3. if a^q mod n=1, then 返回“不确定”
>
>   4. for j=0 to k-1 do
>
>   5. if a^((2^j)*q) mod n=n-1 then 返回“不确定”
>
>   6. 返回“合数”
>
>

而对合数n=13*17=221应用上述测试，若选取a=5，则算法返回“合数”；假设我们选取a=21，则21^55mod221=200,
(21^55)^2mod221=220，则测试算法返回“不确定”，意即221可能是素数

故我们需要 **重复使用Miller-Rabin算法** ：

>
> 对随机选取的a重复调用TEST(n)，如果某时刻TEST返回“合数”，则n一定不是素数；若TEST连续t次返回“不确定”，当t足够大时，我们可以相信n是素数

实现如下：

    
    
    function millerRabinAlgorithmV2($n)  //参照William Stallings所著的《密码编码学与网络安全——原理与实践（第七版）》实现的Miller-Rabin算法，素性检测
    {
        $k = 1;
        $q = ($n - 1) / 2;
        while (pow(2, $k) < $n - 1) {  //1.找 n-1 = 2^k *q 中的k和q
            $q = ($n - 1) / 2;
            while (pow(2, $k) * $q < $n - 1) {
                if (pow(2, $k) * $q == $n - 1) {  //若满足条件，说明找到了对应的k和q，终止循环，否则q减小，继续寻找对应的q
                    break;
                }
                $q -= 2;
            }
            if (pow(2, $k) * $q == $n - 1) {  //若满足条件，说明上面的内部循环找到了对应的k和q，则终止外部循环，否则说明没有找到对应的q，故k增大，继续寻找满足条件的k和q
                break;
            }
            $k++;
        }
        $flags = [];  //用数组存储重复调用Miller-Rabin算法产生的结果
        while (true) {
            $flags = [];
            for ($times = 0; $times < 10; $times++) {  //设t为10，重复调用10次
                $flag = false;  //6. 若下面的条件都不满足，$flag没有置true，则不是素数
                $a = mt_rand(2, $n - 2);  //2. 随机选取整数a, 1<a<n-1
                if (squareMultiAlgorithm($a, $q, $n) == 1) {
                    $flag = true;  //3. 有可能是素数
                }
                for ($j = 0; $j < $k; $j++) {  //4. for j=0 to k-1
                    $exponent = pow(2, $j) * $q;
                    if (squareMultiAlgorithm($a, $exponent, $n) == $n - 1) {
                        $flag = true;  //5. 有可能是素数
                    }
                }
                array_push($flags, $flag);  //把判断结果存入数组
            }
            $isTrue = true;
            foreach ($flags as $flag) {  //遍历结果数组，判断TEST是否连续t次返回“不确定”
                if ($flag != $flags[0]) {
                    $isTrue = false;  //如果数组中有结果与其他结果不一样，说明n一定不是素数
                    break;
                }
            }
            if ($isTrue) {
                break;
            }
        }
        return $flags[0];  //返回判断结果
    }

##  0x02 素数选取

实现了素性检测之后，就可以实现素数选取

> 为了防止敌手通过穷举方法发现p和q，p和q应该从很大的**中选取，因而要求p和q应该是大数

//考虑到我们期末作业主要任务是“实现RSA加解密、数字签名”，故没有采用大整数运算，受PHP的数据精度限制，素数范围在2的32到48次方(4.29E9~2.81E14)

> 目前我们并没有产生随机大素数的有效的方法。采用的方法是 **随机选取一个足够大的奇数并检验它是否是素数**

实现如下：

    
    
    function getBigPrimeNum()  //按照课本的方法实现的选取“大”素数（32到48位）
    {
        $n = 0;
        while (!($n % 2)) {  //随机选取一个奇数
            $n = mt_rand((int)pow(2, 32), (int)pow(2, 48));
        }
        while (!millerRabinAlgorithmV2($n)) {  //进行素性检测
            $n *= 2;
            while (!($n % 2)) {  //若素性检测返回false，说明不是素数，则再选取一个奇数进行素性检测
                $n = mt_rand((int)pow(2, 8), (int)pow(2, 12));
            }
            $i = 0;
        }
        return $n;
    }

##  0x03 辗转相除法（求gcd）

公钥选取过程中需要求gcd（最大公约数），需要用辗转相除法

实现如下：

    
    
    function gcd($e, $fai)  //辗转相除法，求两个参数的最大公约数
    {
        while (($fai % $e) != 0) {
            $faiOld = $fai;
            $fai = $e;
            $e = $faiOld % $e;
        }
        return $e;
    }

##  0x04 “平方-乘”算法（求 M^e mod n）

>
> 在RSA的加密和解密中都涉及求一个大整数的幂，然后模n。如果先对整数做幂运算然后再模n，中间结果将是天文数字。有一种计算模指数的有效算法“平方-乘”算法，
> **将e写成二进制形式b(k)b(k-1)...b(0)** ，则计算M^e mod n的算法：
>  
>  
>     d=1;
>     for i=k downto 0 do
>         d = d^2 mod n;
>         if b(i)=1 then d=(d*M) mod n;
>     return d;
>
>  
>

实现如下：

    
    
    function squareMultiAlgorithm($m, $e, $n)  //“平方-乘”算法，求 M^e mod n
    {
        $e = decbin($e);  //将e写成二进制形式
        $d = 1;
        for ($i = 0; $i < strlen($e); $i++) {
            $d = pow($d, 2) % $n;
            if ($e[$i] == 1) {
                $d = ($d * $m) % $n;
            }
        }
        return $d;
    }

##  0x05 加密

实现了平方乘算法后就可以实现加解密了

> 假设接收方B公开了他的公钥，而Alice（发送方）希望向他发送一个消息（明文）M，那么发送方A计算密文 **C=M^e mod n** 并将C传送给B

实现如下：

    
    
    function Ek($m, $pub)  //加密，pub即公钥，包含e和n
    {
        $e = $pub["e"];
        $n = $pub["n"];
        return squareMultiAlgorithm($m, $e, $n);
    }

##  0x06 解密

> B（接收方）收到密文后通过计算 **M=C^d mod n** 进行解密

//n=p*q

实现如下：

    
    
    function Dk($c, $pri)  //解密，pri即私钥，包含d、p、q
    {
        $d = $pri["d"];
        $n = $pri["p"] * $pri["q"];
        return squareMultiAlgorithm($c, $d, $n);
    }

##  0x07 密钥选取

本节的内容相当于主函数，不过我都写在了函数外，使声明的变量作为全局变量，以便其他函数调取

###  1\. 选择两个大素数p和q

    
    
    $p = getBigPrimeNum();
    $q = getBigPrimeNum();

###  2\. 计算乘积n=pq和fai(n)=(p-1)(q-1)

fai(n)即欧拉函数，意为“和n互素的数的数量”

    
    
    $n = $p * $q;
    $fai = ($p - 1) * ($q - 1);

###  3\. 选择大于1小于fai(n)的随机整数e，使得gcd(e, fai(n))=1

    
    
    $e = mt_rand(2, $fai);
    while (gcd($e, $fai) != 1) {  //选择e使得gcd(e, fai)=1 （即e与fai互素）
        $e = mt_rand(2, $fai);
    }

###  4\. 计算d使得de与1 mod fai(n) 同余

    
    
    $d = 2;
    while ((($d * $e) % $fai) != 1 && $d < $fai) {  //计算d使得de与1 mod fai 同余
        $d++;
    }

###  5\. 以{e,n}为公开密钥，{p,q,d}为私有密钥

    
    
    $pub = ["e" => $e, "n" => $n];  //公钥
    $pri = ["p" => $p, "q" => $q, "d" => $d];  //私钥

##  0x08 后记

加解密算法部分的内容就这么些，我都写在了同一个PHP文件SimplifiedRSA.php里以便其他php页面include

由于我们期末作业的要求是实现RSA算法，所以数字签名的哈希我用了PHP自带的hash函数，其他部分无非调用前面的加解密、补零和还原之类的内容，由于我水平有限，我的实现方法也比较原始（low），这里就不详写了，感兴趣的话可往GitHub浏览源码

> **源码**
> ：[github.com/NEPTLIANG/Web/tree/master/SimplifiedRSA](https://github.com/NEPTLIANG/Web/tree/master/SimplifiedRSA)

**源码文件目录结构** ：

    
    
    .
    ├── Client  前端页面
    │   ├── DigitalSignature  数字签名页面
    │   │   ├── DigitalSignature.html
    │   │   └── Style
    │   │       ├── index.css        
    │   │       └── Result.css       
    │   └── EncryAndDecry
    │       └── Style
    │           ├── index.css       
    │           └── Result.css      
    ├── index.html  主页，即加解密页面
    └── Server
        ├── DigitalSignature  数字签名部分
        │   ├── DigitalSignature.php  数字签名、验证等函数实现
        │   ├── SignatureResult.php  签名调用及结果页面
        │   └── VerifyResult.php  签名验证调用及结果页面
        └── EncryAndDecry  加解密部分
            ├── DecryptionResult.php  解密调用及结果页面
            ├── EncryptionResult.php  加密调用及结果页面
            └── SimplifiedRSA.php  素性检测、加解密等函数实现与密钥生成

**参考文献：**

> 1.《密码编码学与网络安全——原理与实践（第七版）》William Stallings,
>
> 2.《信息安全概论》段云所、卫仕民、唐礼勇、陈钟

//End of Article

 ***本文原创作者： NeptLiang，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  


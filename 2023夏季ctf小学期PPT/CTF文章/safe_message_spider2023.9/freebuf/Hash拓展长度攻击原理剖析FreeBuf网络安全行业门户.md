***本文原创作者：婷儿小跟班✧，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 前言

 **哈希长度扩展攻击(hash
lengthextensionattacks)是指针对某些允许包含额外信息的加密散列函数的攻击手段。次攻击适用于MD5和SHA-1等基于Merkle–Damgård构造的算法。**

### MD5扩展攻击介绍

![hash加密图解](https://image.3001.net/images/20180306/15203320396263.jpg!small)

我们需要了解以下几点md5加密过程：

> MD5加密过程中512比特（64字节）为一组，属于分组加密，而且在运算的过程中，将512比特分为32bit*16块，分块运算
>
>
> 关键利用的是MD5的填充，对加密的字符串进行填充(比特第一位为1其余比特为0)，使之(二进制)补到448模512同余，即长度为512的倍数减64，最后的64位在补充为原来字符串的长度，这样刚好补满512位的倍数，如果当前明文正好是512bit倍数则再加上一个512bit的一组。
>
> MD5不管怎么加密，每一块加密得到的密文作为下一次加密的初始向量。

举一个例子讲一下如何填充：比如字符串“Acker”
十六进制0x41636b6572这里与448模512不同余，需补位满足二进制长度位512的倍数，补位后的数据如下：

    
    
    0x61646d696e8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002800000000000000
    

此处补充：以十六进制表示一共是128个字符，十六进制每个字符能够转换成4位二进制，128*4=512这就是一组，正好是512bit。

![img](https://image.3001.net/images/20180306/15203320532282.png!small)

上图中的8是因为补位时二进制第一位要补1，那么1000转换成16进制就是8.后面都补上0.

![img](https://image.3001.net/images/20180306/15203320602395.png!small)

填充数据最后8字节长度，Acker长度为5*8=40bit，又因为0x28=40所以16进制显示为28.

为什么数据会在左端：MD5中储存的都是小端方式，比如0x12345678，那么md5存储顺序就是0x78563412

### MD5拓展攻击演示

下图为加密流程图，可以更直观看清楚整个流程。

![img](https://image.3001.net/images/20180306/15203320694308.png!small)

选一个字符串例如“Acker”MD5（“Acker”）= dee2fb2df156f4040f893d8a10ac1034

现在我们不需要知道字符串是什么。只需要知道其长度，并将字符串填充完，新加一个字符串如：addition，之前得到的“Acker”MD5值作为最后一块加密的初始向量，最后得到的结果和MD5（“Acker+addition”）是一样的。

## 实例

这种攻击方式最实际场景中并不多见，我曾在ctf题中见过一次。这种攻击方法还是要会滴，万一打ctf比赛时候出现了呢……

以实验吧上一道题为例，下面为源码：

    
    
    <?php 
    
    $flag = "flag{flag is here}";
    $secret = "aaaaabbbbbccccc"; // This secret is 15 characters long for security!
    
    @$username = $_POST["username"];
    @$password = $_POST["password"];
    if (!empty($_COOKIE["getmein"])) {
        if (urldecode($username) === "admin" && urldecode($password) != "admin") {
            if ($_COOKIE["getmein"] === md5($secret . urldecode($username . $password))) {
                echo "Congratulations! You are a registered user.\n";
                die ("The flag is ". $flag);
            }
            else {
                die ("Your cookies don't match up! STOP HACKING THIS SITE.");
            }
        }
        else {
            die ("You are not an admin! LEAVE.");
        }
    }
    
    setcookie("sample-hash", md5($secret . urldecode("admin" . "admin")), time() + (60 * 60 * 24 * 7));
    
    if (empty($_COOKIE["source"])) {
        setcookie("source", 0, time() + (60 * 60 * 24 * 7));
    }
    else {
        if ($_COOKIE["source"] != 0) {
            echo ""; // This source code is outputted here
        }
    }
    ?>
    

题目中可以得到：

> $secret的长度15
>
> md5($secret."adminadmin")的值为571580b26c65f306376d4f64e53cb5c7

使用hashpump，方法如下图：

![img](https://image.3001.net/images/20180306/15203320842369.png!small)

第一行是一个新签名作为getmein参数提交

第二行作为password提交即可。

![img](https://image.3001.net/images/20180306/1520332213809.png!small)

### 附：hashpump

HashPump是一个借助于OpenSSL实现了针对多种散列函数的攻击的工具，支持针对MD5、CRC32、SHA1、SHA256和SHA512等长度扩展攻击。而MD2、SHA224和SHA384算法不受此攻击的影响，因其部分避免了对状态变量的输出，并不输出全部的状态变量。

 **安装**

    
    
    git clone https://github.com/bwall/HashPump
    apt-get install g++ libssl-dev
    cd HashPump
    make
    make install
    

![img](https://image.3001.net/images/20180306/1520332092421.png!small)

**使用方法**

搜遍百度，无奈没有什么具体讲解方法只好hashpump
-h得到帮助，凑合看一下吧。简单总结一下就是知道前面字符总长度，知道下一组追加数据，程序就会自动算出前一组的填充数据。

    
    
    ➜  HashPump git:(master) ✗ hashpump -h           
    HashPump [-h help] [-t test] [-s signature] [-d data] [-a additional] [-k keylength]
         HashPump generates strings to exploit signatures vulnerable to the Hash Length Extension Attack.
         -h --help          Display this message.
         -t --test          Run tests to verify each algorithm is operating properly.
         -s --signature     The signature from known message.
         -d --data          The data from the known message.
         -a --additional    The information you would like to add to the known message.
         -k --keylength     The length in bytes of the key being used to sign the original message with.
         Version 1.2.0 with CRC32, MD5, SHA1, SHA256 and SHA512 support.
         <Developed by bwall(@botnet_hunter)>
    

***本文原创作者：婷儿小跟班✧，本文属FreeBuf原创奖励计划，未经许可禁止转载**


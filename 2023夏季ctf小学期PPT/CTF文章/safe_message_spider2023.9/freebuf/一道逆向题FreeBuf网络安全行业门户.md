查壳后程序是一个32位无壳的程序

拉到od和ida中分析一下

经过分析，

![](https://image.3001.net/images/20220324/1648106984_623c1de88328be94f1eda.png!small)

![](https://image.3001.net/images/20220324/1648106985_623c1de92c580c783c751.png!small)

首先分析第一个字符串比较的call

![](https://image.3001.net/images/20220324/1648106986_623c1dea0dd689241eb7b.png!small)

取字符串的第一个字符，循环字符串n次（n为字符串的长度），将第一个字符相加n次，然后这个值=550也就是0x226

所以这里只要满足 字符*n=550 就可以，经过后面的分析这里n需要填10（见下文）

也就是 7开头长度为10 的字符串

### 接下来调试程序

在段首004010770地址下个断点（ida中main函数开头的地址）

![](https://image.3001.net/images/20220324/1648106986_623c1deac7c205f50d943.png!small)

我们一路单步(F8)来到这里，这里必须跳转(可以修改标志寄存器的S位改变是否跳转)，不然程序是不会进行字符串比较的

下面那个call就是进行字符串比较的call了

![](https://image.3001.net/images/20220324/1648106987_623c1deb6cc42e405a188.png!small)

我们单步(F7)进入,发现这里面有两个跳转

第一个jnz就是==550的判断

第二个jnz是字符串是否相等的判断

![](https://image.3001.net/images/20220324/1648106988_623c1dec184c98600f492.png!small)

对应ida中

![](https://image.3001.net/images/20220324/1648106988_623c1decd9542c5f7db14.png!small)

这里我们看到一串类似base64的字符串

搜索字符串看一下

![](https://image.3001.net/images/20220324/1648106989_623c1ded4da3781ffc9a4.png!small)

猜测这里他自定义了base64编码表

![](https://image.3001.net/images/20220324/1648106990_623c1dee0409cacb08a82.png!small)

解密得到

因为这里解密到的长度是10，所以上面的n才为10，不然加密后的字符串长度是不够的

![](https://image.3001.net/images/20220324/1648106990_623c1dee803fca6b16c17.png!small)

此时我们测试一下,

当算法call执行完成后我们修改字符串为 上面解密到的，我们看能不能成功

![](https://image.3001.net/images/20220324/1648106990_623c1deed71695bffcea1.png!small)

在内存窗口中修改后

![](https://image.3001.net/images/20220324/1648106991_623c1def879ec64f89c2a.png!small)

然后来到字符串比较的地方

我们可以看到要进行比较的两个字符串是一样的

![](https://image.3001.net/images/20220324/1648106991_623c1defeb48a4eabbff3.png!small)

### 所以现在

只需要让我们输入的字符串经过算法call后等于 =>=:<2>?=2

然后分析一下算法的call

![](https://image.3001.net/images/20220324/1648106993_623c1df12432252dae11d.png!small)

算法call里主要就是这个call，然后这个call执行了4次，我们点进去

分析

第一次执行的是4

第二次1

第三次2

第四次3

![](https://image.3001.net/images/20220324/1648106993_623c1df17fdef35fa0515.png!small)

此时只需要将 =>=:<2>?=2 反推回来

也就是

先每一位+1，再除啦第一位后面每一位-3，再每一位xor9 就可以了

然后写脚本

![](https://image.3001.net/images/20220324/1648106993_623c1df1ce2f785260fee.png!small)

![](https://image.3001.net/images/20220324/1648106994_623c1df2216428b8422d1.png!small)


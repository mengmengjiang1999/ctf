# ****Python对于自定义字符表的Base64编码求解****

  

说到自定义字符表(Alphabet
Table)解码Base64，我们先得知道Base64是如何进行编码操作的。接下来我们先来介绍一下Base64是怎么进行编码的。

###  **
**首先我们先来引入ASCII码表：![1607223374_5fcc484e0c3f6ba47c72e.png!small?1607223374834](https://image.3001.net/images/20201206/1607223374_5fcc484e0c3f6ba47c72e.png!small?1607223374834)****

  

### 2、 ** **一个字节是8个比特，先找到对应的ASCII码，再将其转化为8位的二进制，转化如下：****

  

H 对应码值为72，它对应的二进制是 01001000

e对应码值为101，它对应的二进制是：01100101

l对应码值为108，它对应的二进制是：01101100

l对应码值为108，它对应的二进制是：01101100

o对应码值为111，它对应的二进制是：01101111

  

Base64的码值是0-63，所以用6位的二进制就可以完全表示Base64的码值（如：000000对应十进制0，111111对应的十进制为63），将上面8位一组的二进制变成6位一组的二进制，由于上面是5*8=40个二进制，不能被6整除，所以要加一组0将其变成48个二进制数（如果还是不能整除，还要继续补8个0，其实就是最小公倍数的倍数）。

  

原来：01001000 01100101 01101100 01101100 01101111 00000000

现在：010010 000110 010101 101100 011011 000110 111100 000000

  

### 3、 ** **然后将6位一组的二进制计算出十进制，再跟Base64的编码表做对比，再将最后补位的0变成=,即可得到Base64字符****

  

010010 对应二进制是：18，18对应Base64字符为：S

000110 对应二进制是：6， 6对应Base64字符为：G

010101 对应二进制是：21， 21对应Base64字符为：V

101100 对应二进制是：44， 44对应Base64字符为：s

011011 对应二进制是：27， 27对应Base64字符为：b

000110 对应二进制是：6， 6对应Base64字符为：G

111100 对应二进制是：18， 18对应Base64字符为：8

000000 补位的0变成=

所以Hello对应的Base64编码就是:SGVsbG8=

  

而我们在上述过程中多少数字对应的多少的Base64字符，这个就是使用了Base64标准的Alphab Table，标准的Table如下：

  

  

![1607223450_5fcc489a990c6d0e8406f.png!small?1607223451156](https://image.3001.net/images/20201206/1607223450_5fcc489a990c6d0e8406f.png!small?1607223451156)

我们在使用Python去解决自定义表的Base64编码的时候，我们该怎么去做呢？

接下来进行到我们的正题：

其实很简单，我们将自带的Base64中他的原始Table使用str中的maketrans类进行替换即可，为什么呢？

我们通过上述的编码过程可以进行分析，我们在编码的过程中只是在最后使用到了表，但是实际上表所对应的我们原始的数据信息是不变的，所以我们先对编码过的内容字符进行替换即可得到正常的Base64编码，我们在进行解码即可。

于是我们得到了如下的代码：

  

    
    
    import base64
    
    import string
     
    str1 = "NhFpbUihxvB="
    
    string1 = "ZYXABCDEFGHIJKLMNOPQRSTUVWzyxabcdefghijklmnopqrstuvw0123456789+/"
    
    string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    
    print (base64.b64decode(str1.translate(str.maketrans(string1,string2))))

上述代码是一个将表替换为：

“ZYXABCDEFGHIJKLMNOPQRSTUVWzyxabcdefghijklmnopqrstuvw0123456789+/”的代码。

我们再来看看如何进行编码

    
    
    str2='BB,yyds!'.encode()
    
    print(str(base64.b64encode(str2)).translate(str.maketrans(string2,string1)))

  

上述就是使用替换字符表的加密编码。

这次的代码很简单，但是要理解str字符串类中的translate方法是包含了maketrans这种子方法的。

  

黑客资讯 · CTF入门 · 网络安全培训 · 科技周报 · Young and Awesome!  
关注微信公众号： **云影安全**

接收我们的最新文章及消息~

![](https://image.3001.net/images/20201128/1606556690_5fc21c1240fba4b1f740e.jpg!small)


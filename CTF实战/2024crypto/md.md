扩展欧几里得算法：
https://zhuanlan.zhihu.com/p/100567253


---

### 古典密码

<style scoped>
section li {
    font-size: 30px;
}
</style>


##### 单表代换

单表代换：明密文一一对应

在密文长度足够长时：通用解法词频分析 http://quipqiup.com/

但是密文较短时不适用 -->

<!-- 古典密码可以分为单表代换和多表代换 -->

<!-- 我们首先看下单表代换。单表代换密码的特点呢，是明文和密文一一对应的。密文足够长的时候，不管用的什么方式，都可以使用通用解法就是词频分析。这里有现成的在线工具可以用。

不过如果密文长度较短，那么词频分析就不好用了。这种时候怎么办呢

-->


---

### 古典密码

<style scoped>
section li {
    font-size: 30px;
}
</style>

##### 单表代换

各种密码基本都有现成破解工具，逐一尝试暴力破解即可

+ 移位密码：https://planetcalc.com/1434/

+ 仿射密码：http://www.metools.info/code/affinecipher183.html

其实不算很特别的办法，直接暴力破译吧。

古典密码，尤其是单表代换，代换规则就几种常用的，直接对于各种代换规则挨个尝试即可。比如说移位密码，仿射密码，还有

---



##### 单表代换




<!-- 还有ROT密码等，直接遍历一下每种可能的破译方式，看看怎样能破译出有意义的文字。
另外就是各种各样的图形密码等，这个就不多赘述了。
-->

---

### 古典密码

<style scoped>
section li {
    font-size: 29px;
}
</style>

##### 多表代换

频率分析不适用。考虑对于可能的多表代换密码依次尝试

+ Playfair：http://www.metools.info/code/playfair_186.html

+ Vigenère cipher：https://planetcalc.com/2468/
或：https://www.mygeocachingprofile.com/codebreaker.vigenerecipher.aspx

+ Hill：http://www.practicalcryptography.com/ciphers/hill-cipher/

##### 总结

唯密文攻击，大力出奇迹


除了单表代换，常用的还有多表代换。

多表代换的话呢，频率分析就不适用了。多表代换密码并不算多，直接暴力破解即可。



 
---
### RSA常用攻击方式：获得了额外信息

假如我们能通过某种方式得到dp或dq，就可以得到n

- dp=d%(p-1)，dq=d%(q-1)
- dp\*e=d\*e%(p-1) -->


### RSA常用攻击方式：当p和q选取不当时



--- 

### RSA常用攻击方式：小公钥指数攻击

使用小加密指数可以加快公钥加密或签名验证。但e特别小时可能被攻击。

假设用户使用的密钥e=3，此时加密关系满足：

$c=m^3 mod N$

即存在正整数k使得 $m^3=c+k*N$
因此有$m=\sqrt[3]{c+k*N}$
攻击者可以从小到大枚举 k，依次开三次根，直到开出整数为止。
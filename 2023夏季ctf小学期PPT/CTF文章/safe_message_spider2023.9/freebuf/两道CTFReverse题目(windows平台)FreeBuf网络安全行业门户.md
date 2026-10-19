原创： iqiqiya  合天智汇

两道CTF Reverse题目(windows平台)

需要用到的工具：PEiD(查壳)，IDA，OllyDbg

 **第一道题（ISCC2018线下赛河南赛区的一道题）**

 ****

 ****

 ****

****

0x01

 ****

先运行一下 发现GetFlag按钮是灰色的 输入无反应

直接用灰色按钮克星激活（spy++也行） 点击后出现假的flag（当时还傻傻提交好多次。。。）

![640.png](https://image.3001.net/images/20180717/1531818816110.png!small)  

  
![640.jpg](https://image.3001.net/images/20180717/15318188237793.jpg!small)  

![640-1.jpg](https://image.3001.net/images/20180717/15318188297592.jpg!small)

 **  
**

 ****

0x02

 ****

 ****

PEiD查壳 发现无壳 VC编译的程序

![640.jpg](https://image.3001.net/images/20180717/15318188408294.jpg!small)  

 **  
**

 ****

0x03

 ****

 ****

既然没有加壳 直接IDA载入分析 shift+F12看看有没有可疑字符串

  
![640.png](https://image.3001.net/images/20180717/15318190627802.png!small)  

 ****

双击Flag进入

  
![640-1.png](https://image.3001.net/images/20180717/15318190695549.png!small)  

 ****

双击向上的箭头（是一个引用）

接着F5大法

分析之后 发现就是一个异或

  
![640.jpg](https://image.3001.net/images/20180717/15318190787431.jpg!small)  

 ****

Py大法好：

![640.png](https://image.3001.net/images/20180717/15318190884331.png!small)  

 ****

最后得到flag:{VEg46R4m04f7607c61e732732a0d4f737f34d674f}

 ****

 ****

****

****

**第二道题**

 ****

 ****

****

0x01

 ****

运行之后就提示让输入flag 如果输入不正确 就退出

 ****

  
![640-1.png](https://image.3001.net/images/20180717/153181923992.png!small)  

 **  
**

 ****

0x02

 ****

 ****

PEiD查壳发现没有加壳 VC的程序

 ****

 **  
**

 ****

0x03

 ****

 ****

IDA载入分析 关键字符串

  
![640.jpg](https://image.3001.net/images/20180717/15318192466767.jpg!small)  

 ****

双击进入

  
![640.png](https://image.3001.net/images/20180717/15318192528066.png!small)  

 ****

双击进入 F5大法 找到关键代码

  
![640.jpg](https://image.3001.net/images/20180717/15318192575974.jpg!small)  

 ****

既然关键在于sub_401480这个函数 那就双击进入一探究竟

  
![640-1.jpg](https://image.3001.net/images/20180717/15318192635514.jpg!small)  

 ****

现在就明白了 我们的input经过sub_401070这个函数运算之后是否等于v3
也就是nAdtxA66nbbdxA71tUAE2AOlnnbtrAp1nQzGtAQGtrjC7===

如果相等 sub_40148函数返回值=1 就输出yes

则input就是我们要得到的flag

一定要注意这个字母n IDA分析后默认是没有和其他在一块的（这是一个大坑 还好我提前OD动态调试了一波）

  
![640.png](https://image.3001.net/images/20180717/15318192719095.png!small)  

 ****

转换之后

![640-1.png](https://image.3001.net/images/20180717/15318192766265.png!small)  

![640.jpg](https://image.3001.net/images/20180717/15318192837601.jpg!small)

 ****

发现5个bit为一组，分别赋给8个值，每个值5位

就是base32呀

![640.png](https://image.3001.net/images/20180717/15318192921762.png!small)  

 ****

接着分析sub_401000()

一共有三步操作：

1\. 将ABCDEFGHIJKLMNOPQRSTUVWXYZ偶数位变为小写字母 也就是AbCdEfGhIjKlMnOpQrStUvWxYz

2\. 再将字符串进行逆序

3\. 后面加上765321

那么base32编码表从默认的ABCDEFGHIJKLMNOPQRSTUVWXYZ234567就变为了zYxWvUtSrQpOnMlKjIhGfEdCbA765321

所以我们需要用Python translate()
方法与maketrans()方法来将nAdtxA66nbbdxA71tUAE2AOlnnbtrAp1nQzGtAQGtrjC7===还原

在解一次base322即可

至此，关键代码分析完毕。

Py大法实现：

![640.jpg](https://image.3001.net/images/20180717/15318193002518.jpg!small)  

 ****

得到flag{f1ag_1s_enc0de_bA3e32!}

 ****

 ****

 **  
**

  
![640.png](https://image.3001.net/images/20180717/1531819306348.png!small)  

 ****  

 **  
**

 ****

对了，也有一个假flag

ZmxhZ3tmbGFnX2lzX25vdF9tZSF9

用base64解密一下（算是个彩蛋吧）

两道题目+idb分析文件+py脚本已全部打包

百度网盘下载链接: https://pan.baidu.com/s/1V-inJEXtPwopyKHtTqP02A 密码: qiu3

  


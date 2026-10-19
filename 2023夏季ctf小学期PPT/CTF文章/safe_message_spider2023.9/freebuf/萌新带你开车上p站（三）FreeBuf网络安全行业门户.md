原创 萌新 合天智汇  

前情提要：

<https://www.freebuf.com/column/229237.html>  
<https://www.freebuf.com/column/229330.html>

## 0x08  

题目给的提示是和运算符优先级有关

![v2-28c35a5a0ce7b8bece345e0955db52c1_r.jp](https://pic4.zhimg.com/v2-28c35a5a0ce7b8bece345e0955db52c1_r.jpg)

登录后直接看源码

  
  

![v2-692adbcee9a654223fc18def2680d21f_r.jp](https://pic2.zhimg.com/v2-692adbcee9a654223fc18def2680d21f_r.jpg)

将长度给len的字符串与1异或

main中的主要逻辑

![v2-cf9815b9e9a5906121ab1a786cda3cdc_r.jp](https://pic1.zhimg.com/v2-cf9815b9e9a5906121ab1a786cda3cdc_r.jpg)

从/home/mistake/password读10个字节数据放到pw_buf，我们手动输入10字节数据放在pw_buf2，如果pw_buf2与1异或的结果如果与pw_buf相等，则打印flag

那么关键就是pw_buf的数据，先直接读password看看

![v2-68af854a5d75e781a6ef7a9ca18547ec_r.jp](https://pic3.zhimg.com/v2-68af854a5d75e781a6ef7a9ca18547ec_r.jpg)

没有权限

题目的提示是和运算符优先级有关

我们仔细分析源码，看看问题出在哪里

问题在这里

if(fd=open("/home/mistake/password",O_RDONLY,0400) < 0){

open函数里权限检查是没问题的，O_RDONLY表示以只读方式打开

0400表示文件所有者具有可读取的权限

由于权限通过检查，所以open函数返回值为0

有因为0<0不成立

所有比较结果为0

然后赋值给fd

即fd为0，表示标准输入，也就是说fd现在是我们可控的

结合之前分析，pw_buf也为我们控制

那就很简单了

![v2-9984dc3b0b598bf88377974b30c70953_r.jp](https://pic4.zhimg.com/v2-9984dc3b0b598bf88377974b30c70953_r.jpg)

第一次输入10个1，存入pw_buf

第二次输入10个0，存入pw_buf2,与1异或后覆盖pw_buf2,此时buf2的值也为10个1，满足打印flag的逻辑

## 0x09shellshock  

查看权限

![v2-b64ebbe96af613d6cbccd44e2deb4ac9_r.jp](https://pic4.zhimg.com/v2-b64ebbe96af613d6cbccd44e2deb4ac9_r.jpg)

可以看到shellshock程序的所属组的权限位上有s，表示sgid,也就是说在执行shellshock时，用户将获得shellshcok所属组的权限，即执行shellshock后将获得root所在用户组的权限，而由flag这一行的权限位可知，该权限可以读取flag

这一点从源码中也可以看出来

![v2-777a5dad602d2d30e43e73945c02db1a_r.jp](https://pic4.zhimg.com/v2-777a5dad602d2d30e43e73945c02db1a_r.jpg)

getegid()返回进程执行有效组识别码。在这里getegid()返回的就是root所在用户组的id

setresuid用于设置ruid,euid,seuid，在这里就是统统都设置为进程当前的egid

setresgid用于设置rgid,egid,sgid，这里也是统统设置为进程当前的egid

因为s标志，所以egid实际上是root所在用户组的id

再根据题目提示的shellshock

这是著名的bash破壳漏洞

直接在网上找到poc修改下即可

![v2-42474bee7cd66fa4a440db1621a78730_r.jp](https://pic3.zhimg.com/v2-42474bee7cd66fa4a440db1621a78730_r.jpg)

解释一下发生了什么

首先在当前环境下定义了X函数，函数体由{}括起来，然后在函数体外加了一条额外的语句/bin/cat
./flag即打印flag的命令，这条语句会在后面执行./shellshock时被调用，由于执行shellshock时会有root权限，所以自然就有权限来打印flag了

## 0x10  

按照要求连接服务器

![v2-034902dc359758e4000cd1baf8fe15c5_r.jp](https://pic3.zhimg.com/v2-034902dc359758e4000cd1baf8fe15c5_r.jpg)

这是一个小游戏

大意是一堆货币里有真币假币，两者重量不同，真币10g，假币9g。给你N个硬币，C次机会，让你猜哪一个是假币。需要在30s的时间里才对100次。

这题其实考的是算法。

分治法解决

举个例子。

一共100个硬币，其中1个是假的，先称重1-49，如果结果整除10，则假币在50-100.

第二轮称50-75，如果不整除10，则假币在其中

第三轮称50-62.。。。。

其实就是简单的二分法

编程

![image.png](https://image.3001.net/images/20200306/1583483473_5e620a51916f0.png!small)

  
  

以上一关的shellshock登录服务器，在tmp目录下新建一个python 脚本

按照提示

用pwntools编写的时候，注意remote(‘0’,9007)

执行如下

![v2-5ae3e55dc74437625f32483f0700fc0c_r.jp](https://pic2.zhimg.com/v2-5ae3e55dc74437625f32483f0700fc0c_r.jpg)

![v2-e8f559044ecb0b3dad00e4b05f947675_r.jp](https://pic4.zhimg.com/v2-e8f559044ecb0b3dad00e4b05f947675_r.jpg)

## 0x11blackjack  

![v2-bf72f68d7fdb09ef4cf23c419cd071a2_r.jp](https://pic4.zhimg.com/v2-bf72f68d7fdb09ef4cf23c419cd071a2_r.jpg)

em

源码有点长，直接看关键部分

![v2-f06715b55aa38ecfd036fc550f4fad07_r.jp](https://pic3.zhimg.com/v2-f06715b55aa38ecfd036fc550f4fad07_r.jpg)

这里会校验我们输入的金额

如果比cash大则会报错，并要求再次输入

不过再次输入的时候不会报错了

考虑到要赚够1000000，而输的几率比较大

我们可以输入-的金额，比如-1000000，只要输了就可以拿到flag

![v2-805d19f570c13cb3d2f81b2c338ddf96_r.jp](https://pic3.zhimg.com/v2-805d19f570c13cb3d2f81b2c338ddf96_r.jpg)

然后选择y就打印出flag了

![v2-45c5ade23dc79bbc8779594104864ae1_r.jp](https://pic1.zhimg.com/v2-45c5ade23dc79bbc8779594104864ae1_r.jpg)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！


确认目标机IP：192.168.38.140

![](https://image.3001.net/images/20230713/1689235793_64afb1512708d307e1cc4.png!small)

进行端口扫描：

![](https://image.3001.net/images/20230713/1689235793_64afb151c36a809fa2188.png!small)

查看一下版本：

![](https://image.3001.net/images/20230713/1689235794_64afb152a8c8ac6d893c2.png!small)

没有查到关键信息，以80端口作为突破：

![](https://image.3001.net/images/20230713/1689235795_64afb153c1bf9b8a84d36.png!small)

拿到提示信息：

接下来尝试ftp登录，根据提示信息：

![](https://image.3001.net/images/20230713/1689235796_64afb154c24dc57007fe8.png!small)

登录之后，拿到lmao.zip文件

![](https://image.3001.net/images/20230713/1689235797_64afb1556d78b9fe5dc05.png!small)

尝试解压文件，需要密码：

![](https://image.3001.net/images/20230713/1689235798_64afb156110091a8fb7ef.png!small)

接下来对网址进行扫描爆破：

![](https://image.3001.net/images/20230713/1689235799_64afb157062879812b1c9.png!small)

打开robots.txt:

![](https://image.3001.net/images/20230713/1689235799_64afb157c1491f89406ee.png!small)

再次爆破：

![](https://image.3001.net/images/20230713/1689235800_64afb158772406c29dd26.png!small)

找到可疑地址：http://192.168.38.140//ok_this_is_it

![](https://image.3001.net/images/20230713/1689235801_64afb15932ebdadd8a211.png!small)

接下来下载照片，通过strings对图片进行分析：

![](https://image.3001.net/images/20230713/1689235802_64afb15a21a20a84be445.png!small)

没有关键信息，再找一个网址，同样的操作：http://192.168.38.140//dont_bother

![](https://image.3001.net/images/20230713/1689235803_64afb15b92f398d99e263.png!small)

深入此目录：

![](https://image.3001.net/images/20230713/1689235804_64afb15c76085c5bef483.png!small)

下载回来这个文件，通过base64解密：

![](https://image.3001.net/images/20230713/1689235805_64afb15d2507e1c70b891.png!small)

![](https://image.3001.net/images/20230713/1689235805_64afb15dae71920790bed.png!small)

使用此字典对lmao.zip进行爆破：

![](https://image.3001.net/images/20230713/1689235806_64afb15e562b35343613c.png!small)

完事之后解压lmao.zip，生成noop，查看一下是一个私钥：

![](https://image.3001.net/images/20230713/1689235807_64afb15f059f78c9263e0.png!small)

![](https://image.3001.net/images/20230713/1689235807_64afb15fc325d839560a1.png!small)

尝试链接ssh，链接失败：

![](https://image.3001.net/images/20230713/1689235808_64afb160ab486f7aed316.png!small)

这里利用了cve-2014-6271漏洞：

'() { :;};/bin/bash'

ssh -i noob noob@192.168.38.140 '() { :;};/bin/bash':

![](https://image.3001.net/images/20230713/1689235809_64afb16183220033b8ea7.png!small)

可以看到这里已经链接到：

![](https://image.3001.net/images/20230713/1689235810_64afb16254c71a4070ab9.png!small)

查找高权限文件：

![](https://image.3001.net/images/20230713/1689235811_64afb1630348da45e9ff9.png!small)

可以看到有root可疑文件，运行不同的root文件，发现需要传入参数，输入500个A，测试到door2中r00t会崩溃，是我们需要的，抠出来：

![](https://image.3001.net/images/20230713/1689235811_64afb163ca86d55aa912b.png!small)

接下来用ida打开分析一下：

![](https://image.3001.net/images/20230713/1689235812_64afb1648f738d4600b97.png!small)

可以看到这是一个缓冲区溢出漏洞，生成随机字符串：

![](https://image.3001.net/images/20230713/1689235813_64afb165ab570414dd22a.png!small)

Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq

又进行了一次链接，发现我们的文件已经更改了目录：

![](https://image.3001.net/images/20230713/1689235814_64afb1668c19e0b052fc1.png!small)

随后确认溢出点：

![](https://image.3001.net/images/20230713/1689235815_64afb167a0390add04d16.png!small)

出现段错误，需要进行调试：

![](https://image.3001.net/images/20230713/1689235817_64afb16900fecf358668b.png!small)

异常点位置确定：

![](https://image.3001.net/images/20230713/1689235818_64afb16a06a539808d64c.png!small)

也就是偏移268后+返回地址，首先是268个A+4个B进行测试：

![](https://image.3001.net/images/20230713/1689235819_64afb16b06095195178b1.png!small)

可以看到eip已经成功被覆盖。接下来就是构造我们的payload。填充滑板指令，确定esp地址：

![](https://image.3001.net/images/20230713/1689235819_64afb16bce30694522a22.png!small)

所以可以开始构造EXP，268+esp地址+16*0x90+shellcode：

![](https://image.3001.net/images/20230713/1689235820_64afb16caf9494b5e2154.png!small)

可以看到，提权成功。

![](https://image.3001.net/images/20230713/1689235821_64afb16d6caa7202491aa.png!small)

成功获取到flag：a70354f0258dcc00292c72aab3c8b1e4


## BugKu CTF(杂项篇MISC)—想要种子吗

提 示:

描 述:flag{}

题目下载后是一张图片，打开如下。

![1620475121_60967cf116c95b106ca70.png!small?1620475116882](https://image.3001.net/images/20210508/1620475121_60967cf116c95b106ca70.png!small?1620475116882)

## 一、工具

十六进制编辑器010 editor

kali系统文件分离工具binwalk或者foremost

维吉尼亚密码

STEGHIDE图片隐写工具

文章所需的软件下载地址

ARCHPR压缩包密码破解工具

## 二、解题思路

1.先看看图片属性，养成好的习惯，发现隐藏关键信息。STEGHIDE。这是一种图片隐写方法。

![1620475133_60967cfd2e47c1c811023.png!small?1620475128961](https://image.3001.net/images/20210508/1620475133_60967cfd2e47c1c811023.png!small?1620475128961)

2.我们可以在kali系统上安装STEGHIDE工具。安装步骤如下

apt-get install steghide

3.steghide的使用方法

查看帮助

steghide --help  
查看图片中嵌入的文件信息

steghide info FILENAME  
隐藏文件

steghide embed -cf COVERFILE -ef EMBEDFILE  
提取文件

steghide extract -sf STEGOFILE

4.先来查看一下这个文件有没有隐藏内容。发现图片里隐藏了123.txt文档。steghide info torrent.jpg

![1620475143_60967d07abced2c8a80bd.png!small?1620475139463](https://image.3001.net/images/20210508/1620475143_60967d07abced2c8a80bd.png!small?1620475139463)

5.把123.txt提取出来。steghide extract -sf torrent.jpg

![1620475150_60967d0e9021d7373bb2e.png!small?1620475146311](https://image.3001.net/images/20210508/1620475150_60967d0e9021d7373bb2e.png!small?1620475146311)

6.打开123.txt，发现一个百度网盘地址。https://pan.baidu.com/s/1oXOf-mKm5TOrbNWg0suWfg m6qn

7.文件得到一个压缩包，包含一个hint.txt和123.jpg文件。123.jpg是加密的。先看看hint.txt里有什么提示吧

![1620475157_60967d15c41a9fe35bb5b.png!small?1620475153551](https://image.3001.net/images/20210508/1620475157_60967d15c41a9fe35bb5b.png!small?1620475153551)

8.txt里是666，猜测解压密码应该是6位数字。

![1620475164_60967d1c575c8cc9bbedb.png!small?1620475160480](https://image.3001.net/images/20210508/1620475164_60967d1c575c8cc9bbedb.png!small?1620475160480)

9.用ARCHPR软件爆破密码，密码为666666。

![1620475170_60967d22b97e9ca73e19b.png!small?1620475166530](https://image.3001.net/images/20210508/1620475170_60967d22b97e9ca73e19b.png!small?1620475166530)

10.解压后得到1张图片。

![1620475177_60967d2931e2f8f35041d.png!small?1620475173006](https://image.3001.net/images/20210508/1620475177_60967d2931e2f8f35041d.png!small?1620475173006)

11.是不是想打死出题者。拖到010 editor编辑器里看看。发现有504B0304开头，有压缩包，应该是文件包含。打开kali系统用binwalk -e
文件名，分离文件。

![1620475183_60967d2f96f5f7a1e66cd.png!small?1620475179410](https://image.3001.net/images/20210508/1620475183_60967d2f96f5f7a1e66cd.png!small?1620475179410)

12.得到如下图片。

![1620475189_60967d35ae8a08b249bbc.png!small?1620475185515](https://image.3001.net/images/20210508/1620475189_60967d35ae8a08b249bbc.png!small?1620475185515)

13.再拖到010 editor编辑器里看看，看看有crc报错，一般这种都是高度有问题，直接把高度调到和宽度一样。怎么找高度和宽度，前面的文章已经讲过了。

![1620475195_60967d3bdf29189f2980f.png!small?1620475191618](https://image.3001.net/images/20210508/1620475195_60967d3bdf29189f2980f.png!small?1620475191618)

14.得到一个很奇怪的字符串fkyg{SfirgsXmuqRoqpemr}，题目提示flag的类型是flag{}，这个应该不是flag。再继续看010。

![1620475202_60967d423e93b175b4d35.png!small?1620475197998](https://image.3001.net/images/20210508/1620475202_60967d423e93b175b4d35.png!small?1620475197998)

![1620475208_60967d48bbf3e033034cb.png!small?1620475204669](https://image.3001.net/images/20210508/1620475208_60967d48bbf3e033034cb.png!small?1620475204669)

16.打开如下，查了一下这个叫维吉尼亚密码，不管三七二十一，先把刚才的密文放进去试试。

![1620475215_60967d4f52351b11aab34.png!small](https://image.3001.net/images/20210508/1620475215_60967d4f52351b11aab34.png!small)

17.保持默认选择，得到密码flas{ItisieNaurTagdent}，试了一下不对。

![1620475223_60967d57d2222cc2f1197.png!small?1620475219725](https://image.3001.net/images/20210508/1620475223_60967d57d2222cc2f1197.png!small?1620475219725)

18.换成英语，得到正确的flag。flag{ThisisYourTorrent} 如果觉得对你有帮助，收藏、点赞哦

![1620475231_60967d5f463b066d864e0.png!small?1620475227252](https://image.3001.net/images/20210508/1620475231_60967d5f463b066d864e0.png!small?1620475227252)

## 三、总结

本题需要掌握010 editor使用，文件头标识，文件分离，密码破解等基础知识。


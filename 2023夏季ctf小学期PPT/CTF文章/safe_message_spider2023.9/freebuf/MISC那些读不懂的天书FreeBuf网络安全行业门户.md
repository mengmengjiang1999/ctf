## **0x0：介绍**

Misc中的细节点，常常给我们带来快乐。杂项中常常出现的字符和编码就像天书一样晦涩难懂，但只要找准了方向一切都能迎刃而解，今天我们就来挑战它吧。

##  **0x1：无字天书**

###  **初始准备**

下载文件发现是一个流量包，放到kali，使用binwalk分离得到两个文件，一般用到需要分离文件的时候，binwalk肯定是少不了的。![](https://image.3001.net/images/20220302/1646211689_621f3269bad2ac469dd9f.png!small)

把两个文件放到winhex发现3B6A有ZIP文件头，将没用的删除，然后全选转换一下选块。![](https://image.3001.net/images/20220302/1646211769_621f32b9365198e4b6eca.png!small)

然后我们解压压缩包，用sublime打开flag.txt 。

打开后就发现了一堆点点的东西：![](https://image.3001.net/images/20220302/1646211791_621f32cf9bccacab0c3d2.png!small)

看着像Snow，这时候我们发现还有一个key.sw，使用sublime打开发现是whitespace加密。

###  **解密**

whitespace加密：

大多数的编程语言都会忽略代码中的空白字符，“Whitespace”是专门来弥补普通编程语言，它给予这些空白字符最重要的地位。

在“Whitespace”编程语言中，任何非空白的字符都是被忽略的，只有空格符、tab和换行符被认为是有效的语义字符。![](https://image.3001.net/images/20220302/1646211837_621f32fd96c19467a0379.png!small)

解密得到 XiAnWillBeSafe

##  **0x2：Steg**

stegosaurus的一些用法：![](https://image.3001.net/images/20220302/1646211890_621f33327a51eb2722763.png!small)

从网上下载下来发现就是加密的压缩包，并且有明确的提示就是爆破6位密码。

![](https://image.3001.net/images/20220302/1646211911_621f3347d5d5602648890.png!small)

解密发现是pyc名字有点像stegosaurus，使用stegosaurus解密一下：

![](https://image.3001.net/images/20220302/1646211930_621f335ae48bfde9bcb37.png!small)

然后我们就能够打开emojio.txt

![](https://image.3001.net/images/20220302/1646211986_621f33922ff79e50af01e.png!small)  
发现是颜文字，加上有密码的颜文字，那大概率就是emoji-aes了。

<https://aghorler.github.io/emoji-aes/>

解密即可。

![](https://image.3001.net/images/20220302/1646212018_621f33b203b62922186db.png!small)

##  **0x3：协议**

用wireshark导出所有http协议，发现又一个加密：![](https://image.3001.net/images/20220302/1646212051_621f33d3d51e26c465736.png!small)

用python写个脚本把其转成rar压缩包

脚本源码：

    
    
    import base64code="""文档内容"""r=base64.b64decode(code)test_file=open("test.rar","wb")test_file.write(r)test_file.close()

![](https://image.3001.net/images/20220302/1646212103_621f34074caf0256f3da6.png!small)

解压后发现图片上有字幕，然后利用ps进行拼接，得到了隐藏的内容。


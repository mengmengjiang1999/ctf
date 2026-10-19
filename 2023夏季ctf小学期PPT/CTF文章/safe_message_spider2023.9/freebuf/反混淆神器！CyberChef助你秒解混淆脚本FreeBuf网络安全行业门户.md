## 一、概述

**[CyberChef](https://gchq.github.io/CyberChef/)是一款强大的编码转换器，简单易懂易上手，它集成了多种编码转换的功能，如：base64加解密、hex转换、char转换、正则表达式等，能辅助大家方便快捷地解密出恶意的脚本。**

其界面如下图，最左边的Operations是转换工具集，把你挑选好的工具经过DIY组合及排序拖拽到Recipe中，就可以对Input中的字符串进行相应地解密操作了，工具很多，可以在Search框中搜索，输出结果会打印在Output窗口中。

![](https://image.3001.net/images/20190724/1563944602_5d37e69a994cb.png!small)

## 二、实战演示

多说无益，下面就来进行实战演示吧!

### 2.1 powershell脚本反混淆

首先来尝试使用CyberChef来解密一个经过混淆的powershell脚本，把样本下载下来，发现样本经过了高强度的混淆，无法直接分析其做了什么操作。

样本地址：<https://www.hybrid-analysis.com/sample/cc9c6c38840af8573b8175f34e5c54078c1f3fb7c686a6dc49264a0812d56b54?environmentId=120>

接下来将样本内容复制到Input窗口中，第一步，是要将其中的base64数据筛选出来，怎么筛选呢，当然是用正则表达式，好，那就把Regular
expression拖进来，然后在Regex框中编写规则。将红框中的Output format改为高亮，就可以清晰地看到规则匹配到了哪些字符串了。

![](https://image.3001.net/images/20190724/1563944677_5d37e6e564106.png!small)

通过上述的方式，成功写出了匹配base64的正则表达式：[0-9a-zA-Z/+=]{30,}，筛选长度在30以上的可视字符串，将Output
format改为List matches模式，就能截取这段base64了。

![](https://image.3001.net/images/20190724/1563944723_5d37e7138ef1c.png!small)

然后把From base64拖进来，成功解密出字符串。

![](https://image.3001.net/images/20190724/1563944828_5d37e77ce9485.png!small)

不对啊，怎么解密完还是一堆乱码？别急，注意看Input框中的脚本，在base加密前还有个DelfateStream加密操作呢，那就把Raw
Inflate拖进来，轻松解密，Output中已经显现出可以进行分析的恶意代码了。

![](https://image.3001.net/images/20190724/1563944747_5d37e72b0f964.png!small)

这还不够，CyberChef还有Generic Code
Beautify工具对代码进行美颜，能优化代码格式，看起来更友好，至此，解密工作就完成了，很简单吧。

![](https://image.3001.net/images/20190724/1563944770_5d37e7421d44c.png!small)

解密后的powershell脚本大致看了下是个下载木马的dropper，本文主要介绍工具的解密用法，就不对该样本进行深入分析了。

![](https://image.3001.net/images/20190724/1563944842_5d37e78a0f129.png!small)

发现没有，上面的解密方法（正则->base64->inflate）其实可以通用到大部分ps脚本解密步骤中，可以点击save
recipe按钮将它保存起来，命名为powershell-deflate-base64，后面遇到相似的混淆脚本就能使用该规则进行解密。

![](https://image.3001.net/images/20190724/1563944854_5d37e796b1a3d.png!small)

### 2.2 char型恶意脚本反混淆

仅次于base64，char字符的混淆方式也被常见于恶意脚本中，下面就来看看CyberChef

如何轻松解密char型字符串。

![](https://image.3001.net/images/20190724/1563944875_5d37e7ab23335.png!small)

样本地址：<https://gist.github.com/jonmarkgo/3431818>

首先使用正则表达式([0-9]{2,3}(,\s|))+筛选脚本中的char型字符串。

![](https://image.3001.net/images/20190724/1563944919_5d37e7d7cae5c.png!small)

然后使用From
Charcode对上述char型字符串进行转换，在转换前需要将间隔符Delimiter选为Comma（逗号），Base选为10进制，就可以解密出恶意代码了，恶意代码是一段JS代码，其中还隐藏有一段char型字符串。

![](https://image.3001.net/images/20190724/1563944929_5d37e7e182048.png!small)

再次重复上述操作，就可以解密出加载的核心恶意脚本的地址为：<https://examhome.net/stat.js?v=1.0.1xamhome>。

###  2.3 webshell反混淆

webshell跟powershell恶意脚本的混淆方式也大致相同，也常使用base64进行混淆，不过下面的这个webshell有点特别，它循环使用base64加密了二十多次（这种加密方式在某些APT攻击样本中也出现过），也就是说得对它进行二十多次的解密......

![](https://image.3001.net/images/20190724/1563944974_5d37e80eb46c5.png!small)

样本地址：<https://github.com/LordWolfer/webshells/blob/b7eefaff64049e3ff61e90c850686135c0ba74c4/from_the_wild1.php>

使用之前的powershell-deflate-base64规则进行解密，发现它解密出来还是一段base64加密脚本，那该怎么办呢，总不能重复手工重复操作吧，会累死的。

![](https://image.3001.net/images/20190724/1563944999_5d37e827e9ffc.png!small)

CyberChef提供了一种循环的方法，可以省去手工操作的工作。首先在powershell-deflate-base64的开头加个Label，自定义命名为start，意思指循环的开始。

![](https://image.3001.net/images/20190724/1563945021_5d37e83d63b9a.png!small)

然后在powershell-deflate-base64的末尾拖入Jump，Jump的地址为start，Maximum jumps填入要循环的次数。

![](https://image.3001.net/images/20190724/1563945038_5d37e84e9435d.png!small)

经过试验，发现循环解密21次后就能得到混淆前的恶意脚本了，这是一个PHP的文件上传webshell。

![](https://image.3001.net/images/20190724/1563945077_5d37e875271f1.png!small)

## 三、总结

CyberChef可以简单理解为是一个脚本解密工具的集合，除此之外，它其实还有很多黑科技，比如解析网络数据包里的数据、解析图片的地理位置及时间信息等等，工具之多，可能会看的眼花缭乱，挑选的时候也要找很久，所以你应当将常用的工具加入到Favourites栏中，方便使用。

![](https://image.3001.net/images/20190724/1563945087_5d37e87f8e674.png!small)

项目地址：<https://github.com/mattnotmax/cyber-chef-recipes#recipe-1---extract-base64-raw-inflate-and-code-beautify>

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**


![1.png](https://image.3001.net/images/20200614/1592118624_5ee5cd6090856.png!small)

## StegCloak

StegCloak是一款基于纯JavaScript开发的隐写功能模块，该工具采用函数式编程风格设计，StegCloak可以对文本中的机密信息进行压缩和加密，然后再使用特殊的Unicode不可见字符来隐藏它。除此之外，
该工具还可以用来安全设置水印字符串，在网页中设置不可见的脚本，或在社交媒体或其他需要涉及隐蔽通信的地方隐藏文本内容。

## 功能介绍

> 1、使用密码和HMAC完整性保护您的不可见的机密数据；
>
> 2、通过使用AES-256-CTR加密不可见的机密数据来实现加密安全；
>
> 3、在Unicode字符中使用了7个不可见的字符，这些字符在网页中无处不在；
>
> 4、支持最常见的Tweets、Gmail、Whatsapp、Telegram、Instagram、Facebook等社交媒体或网络应用；
>
> 5、减少Payload的最大压缩（LZ，Huffman）；
>
> 6、完全不可见，使用零宽度字符而不是空格或制表符；
>
> 7、速度非常快！可以在不到一秒钟的时间内，通过将隐写术在三个单词隐藏在****页面源（800行，205362个字符）的隐蔽文本中；
>
> 8、支持将文件上传到云端并在字符串中创建链接，可以实现在字符串中隐藏文件；
>
> 9、纯功能性开发；
>
> 10、可将其当作API模块、命令行接口或Web接口来使用；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/KuroLabs/stegcloak.git

## 工具安装

使用npm在线安装：

    
    
    $ npm install -g stegcloak

使用npm本地安装：

    
    
    $ npm install stegcloak

## 工具运行机制

##
![FlowDiagram.PNG](https://image.3001.net/images/20200614/1592118659_5ee5cd83a9ead.png!small)命令行接口使用

### 隐藏

    
    
    $ stegcloak hide

### 选项：

`hide [options] [secret] [cover]`

``

`-fc, --fcover <file> Extract cover text from file`

``

`-fs, --fsecret <file> Extract secret text from file`

``

`-n, --nocrypt If you don't need encryption (default: false)`

``

`-i, --integrity If additional security of preventing tampering is needed
(default: false)`

``

`-o, --output <output> Stream the results to an output file`

``

`-c, --config <file> Config file`

``

`-h, --help display help for command`

``

## 恢复``

    
    
    $ stegcloak reveal 

### 选项：

`reveal [message]`

``

`-f, --file <file> Extract message from file`

``

`-cp, --clip Copy message directly from clipboard`

``

`-o, --output <output> Stream the secret to an output file`

``

`-c, --config <file> Config file`

``

`-h, --help display help for command`

``

### 其他支持：``

> 1、STEGCLOAK_PASSWORD环境变量：如果设置，将使用默认密码；
>
> 2、Config文件：支持对Stegcloak命令行接口进行配置；

## API使用

`const StegCloak = require('stegcloak');`

``

`const stegcloak = new StegCloak(true, false); // Initializes with encryption
true and hmac false for hiding`

``

`// These arguments are used only during hide`

``

`// Can be changed later by switching boolean flags for stegcloak.encrypt and
stegcloak.integrity`

``

``

``

### 隐藏：

    
    
    stegcloak.hide(secret,password,cover) -> string

`const magic = stegcloak.hide("Voldemort is back", "mischief managed", "The
WiFi's not working here!");`

``

`// Uses stegcloak.encrypt and stegcloak.integrity booleans for obfuscation`

``

`console.log(magic); // The WiFi's not working here!`

``

### 恢复：

    
    
    stegcloak.reveal(data, password) -> string

`const secret = stegcloak.reveal(magic, "mischief managed");`

``

`// Automatically detects if encryption or integrity checks were done during
hide and acts accordingly`

``

`console.log(secret); // Voldemort is back`

``

## 工具运行演示``

![stegcloak.gif](https://image.3001.net/images/20200614/1592118731_5ee5cdcbb45e4.gif!small)许可证协议

该工具的开发与发布遵循[
_MIT开源许可证协议_](https://github.com/KuroLabs/stegcloak/blob/master/LICENSE.md)。

## 项目地址

StegCloak：【[ _GitHub传送门_](https://github.com/kurolabs/stegcloak)】

**参考来源**

> **[_kurolabs_](https://github.com/kurolabs/stegcloak)**


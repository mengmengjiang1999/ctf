![](https://image.3001.net/images/20201204/1607093171_5fca4bb350a708988cd47.png!small)

## Decoder++

Decoder++是一款专用于渗透测试的多数据格式编码解码工具，该工具是一款可扩展的工具，专为渗透测试人员和软件开发人员设计，可以将目标数据编码/解码为各种不同的数据格式。

## 功能介绍

> 用户接口：图形化用户接口和命令行接口；
>
> 预安装脚本和编码解码器：
>
> 支持的编码/解码格式：Base16、Base32、Base64、Binary、Gzip、Hex、Html、JWT、
> HTTP64、Octal、Url、Url+、Zlib；
>
> 哈希：Adler-32、Apache-Md5、CRC32、FreeBSD-NT、Keccak224、Keccak256、Keccak384、
> Keccak512、LM、Md2、Md4、Md5、NT、PHPass、RipeMd160、Sha1、Sha3 224、Sha3 256、Sha3
> 384、Sha3 512、Sha224、Sha256、Sha348、Sha512、Sun Md5
>
> 脚本：CSS-Minify、Caesar、Filter-Lines、Identify File Format、Identify Hash Format、
> JS-Beautifier、JS-to-XML、HTML-Beautifier、Little/Big-Endian Transform、Reformat
> Text、 Remove Newlines、Remove Whitespaces、Search and Replace、Split and
> Rejoin、 Unescape/Escape String
>
> 智能解码；
>
> 插件系统；
>
> 加载&存储当前会话；
>
> 支持的平台：Windows、Linux、macOS；

## 工具安装

Decoder++支持使用pip命令安装，安装命令如下：

    
    
    # Install using pip
    
    pip3 install decoder-plus-plus

除此之外，广大研究人员可以直接将该项目源码直接从其GitHub主页上克隆至本地：

    
    
    git clone https://github.com/bytebutcher/decoder-plus-plus.git

## 工具使用

接下来，我们将给大家演示如何使用Decoder++，并与其进行交互。

### 图形化用户接口

如果你更倾向于使用图形化用户接口来进行数据转换的话，Decoder++给我们提供了两个选项，即主窗口模式（main-window-mode）和对话框模式（dialog-mode）。

![](https://image.3001.net/images/20201204/1607093232_5fca4bf0c42ef17de55a5.png!small)

主窗口模式支持页面标签，而对话框模式能够将转换后的数据内容返回至stdout以备后续分析处理使用。如果你想要在类似BurpSuite这样的工具或其他脚本中来调用Decoder++的话，这种方式就非常方便了。

![](https://image.3001.net/images/20201204/1607093241_5fca4bf9c6543e5b1940a.png!small)

### 命令行接口

如果不想使用图形化界面，并且还想使用Decoder++所提供的更多数据转换方法的话，推荐大家使用Decoder++的命令行接口：

    
    
    $ python3 dpp.py -e base64 -h sha1 "Hello, world!"
    
    e52d74c6d046c390345ae4343406b99587f2af0d

命令行接口支持我们以一种更简单的方式来使用所有的可用编码解码方案。首先，我们可以使用-l参数来查看支持的编码解码格式：

    
    
    $ dpp -l base enc
    
    Codec                 Type
    
    -----                 ----    
    base16                encoder
    
    base32                encoder
    
    base64                encoder

Decoder++能够区分编码器、解码器、哈希器和脚本。跟图形化用户接口相似，命令行接口允许我们使用一行命令来进行多种格式的编码解码：

    
    
    $ dpp "H4sIAAXmeVsC//NIzcnJ11Eozy/KSVEEAObG5usNAAAA" -d base64 -d gzip
    
    Hello, world!

如需查看特定脚本的所有可用选项，可以使用help参数：

    
    
    $ dpp "Hello, world!" -s split_and_rejoin help
    
    Split & Rejoin
    
    ==============
    Name  Value  Group            Required  Description
    
    ----  -----  -----            --------  -----------    
    split_by_chars         split_behaviour  yes       the chars used at which to split the text
    
    split_by_length  0      split_behaviour  yes       the length used at which to split the text
    
    rejoin_with_chars                          yes       the chars used to join the splitted text

如需配置特定脚本，我们还需要以键值对的形式提供单独的选项：

    
    
    $ dpp "Hello, world!" -s search_and_replace search_term="Hello" replace_term="Hey"
    
    Hey, world!

## 插件开发

如需添加自定义的编码解码器，只需要将其拷贝至项目主目录下的$HOME/.config/dpp/plugins/文件夹中即可：

    
    
    from dpp.core.plugin.abstract_plugin import DecoderPlugin
    
    class Plugin(DecoderPlugin):
    
        """
        Possible plugins are DecoderPlugin, EncoderPlugin, HasherPlugin or ScriptPlugin.
    
        See AbstractPlugin or it's implementations for more information.
    
        """
        def __init__(self, context):
    
            plugin_name = "URL"
    
            plugin_author = "Your Name"
    
            # Python Libraries which are required to be able to execute the run method of this plugin.
    
            plugin_requirements = ["urllib"]
    
            super().__init__(plugin_name, plugin_author, plugin_requirements)
    
        def run(self, text):
    
            # Load the required libraries here ...
    
            import urllib.parse
    
            # Run your action ...
    
            return urllib.parse.unquote(text)

## 项目地址

Decoder++：【[ _GitHub传送门_](https://github.com/bytebutcher/decoder-plus-plus)】


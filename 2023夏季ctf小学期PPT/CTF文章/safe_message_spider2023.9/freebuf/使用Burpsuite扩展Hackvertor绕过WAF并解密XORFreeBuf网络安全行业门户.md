## 前言

**最近，我一直在忙于开发自己的一个Burp扩展[Hackvertor](https://portswigger.net/bappstore/65033cbd2c344fbabe57ac060b5dd100)。这是一个具有基于标签转换功能的编码器，相比起Burp内置的解码器它的功能要强大的多。通过标签的转换编码，可以让你轻松的将编码后的内容传递给下一个外部标签，从而执行多级编码操作。**

![33d33876d04a-article-hackvertor-article.png](https://image.3001.net/images/20181022/1540184367_5bcd592f5d9db.png!small)

例如，要将字符串编码为base64，只需使用base64标签：

    
    
    <@base64_0>test<@/base64_0>

你也可以进行多级编码，例如你想将字符串转换为十六进制，然后对其进行base64编码。只需先使用hex标签，然后再使用base64标签即可完成：

    
    
    <@base64_1><@hex_0(" ")>test<@/hex_0><@/base64_1>

hex标签有一个分隔符参数，用于分隔各个十六进制字符串 - "test"将被作为分隔符和空格传递给标签函数。

## Hackvertor 使用

当Hackvertor被成功加载后，会在Burp中创建一个名为Hackvertor的新Tab。Hackvertor中有一个输入框和一个输出框，你只需输入要转换的文本并单击选择相应的转换标签，转换结果就会出现在输出框中。

![Hackvertor
使用](https://image.3001.net/images/20181022/1540184441_5bcd597961d4f.png!small)

## 绕过 Cloudflare WAF

最近，我又改进了Hackvertor，以让其支持在repeater等工具的实际请求中使用。你只需右键单击repeater
request，并选择Hackvertor菜单在请求中添加标签，在发送请求之前它将自动进行转换。你也可以在Intruder中使用它们，首先在repeater中定义它们然后再将它们发送到Intruder。你甚至还可以在proxy中使用它们，但默认情况下是关闭的。如果你想要打开它，可以在Burp主菜单中选择Hackvertor菜单，然后单击“Allow
tags in Proxy”即可。

下面，我将为大家演示如何在repeater中使用标签来绕过Cloudflare
WAF。我们将以下网址发送给repeater：<https://waf.party/xss/xss.php?x=>

并在等号后输入以下代码：

    
    
    <img/src/onerror=alert(1)>

在repeater request中选中alert(1)，然后启用Hackvertor
BApp，右键单击所选文本，然后单击Hackvertor，[XSS](https://portswigger.net/kb/issues/00200300_cross-site-scripting-reflected)，以及throw_eval。这会将标签添加到请求中，现在你点击go按钮，将会看到响应包含：

    
    
    <img/src/onerror=window.onerror=eval;throw'=alert\x281\x29'>

如果你想检查它的实际工作情况，只需要右键单击request
editor并从上下文菜单和复制URL中选择Hackvertor，这将在转换所有标签后生成一个URL。如果你使用Burp的复制URL复制命令，那么它仅会复制带有标签的URL。

## rotN 解码

这个问题源于我可爱的女儿，自2016年以来我时常会穿着那件我最喜爱的[BSides
Manchester](https://www.bsidesmcr.org.uk/)T恤，在这件T恤的正面印有一大串密密麻麻的二进制数字，每当女儿看到这些数字的时候她都会问我：”爸爸这些数字是什么意思？”。我通常会告诉她这是二进制数字，并询问她是否要解码它们。然后，我会带着她开始在Hackvertor中输入这些数字进行解码。解码后我发现这是一个base64编码的字符串，看起来像是一个经过rot编码的字符串。我们对rot编码的字符串进行了爆破，并对消息进行了解码。但这引发了我的思考，是否可以让Hackvertor自动解码rot编码的字符串。

想要实现这个功能，Hackvertor就需要能够从随机混乱的组合字符中识别类似英语的单词。为此，我创建了一个is_like_english标签。起初，我以为只要使用bigrams（二元语法）和trigrams（三元语法）就可以轻松做到这点，但我发现这并没有我想象的那么简单。我开始在谷歌上搜索解决方案，经过一番搜索我找到了一个[非常棒的网站](http://practicalcryptography.com/cryptanalysis/text-characterisation/quadgrams/)，他们使用quadgrams（四元语法）来识别英语单词。此外，该网站还提供了一些
[简单的python代码](http://practicalcryptography.com/media/cryptanalysis/files/ngram_score_1.py)，它们会根据对单词和quadgrams的分析生成得分。我用Java重写了这些代码，并在Hackvertor中实现了它。

下一步要做的是改进自动解码器。自动解码器就是一个标签，可自动尝试确定字符串的编码方式并对其进行多次解码。我添加了一个简单的正则表达式，用于查找一个或多个a-z的字符，后面跟空格，逗号或连字符。然后循环25次爆破rot编码的字符串，并得到相应的分数。之后再根据得分计算它们的平均值，如果最佳分大于平均值加二十，那么它将自动解码rot编码的字符串。放心，我是不会告诉你们答案的，想知道的话就自己动手操作一遍。

![698fe025cc07-article-santi-bsides-t-shirt.jpg](https://image.3001.net/images/20181022/1540184410_5bcd595a7a7cc.jpg!small)

    
    
    <@auto_decode_0>01010111 01101101 00110101 01101000 01100011 01001000 01010110 01111001 01011010 01101101 01100100 01111001 01011010 01010011 01000010 01000111 01100101 01101101 00110101 00110101 01100101 01010011 00110001 01000111 01100011 01000111 00110101 00110101 01100011 01101001 01000010 01010011 01100001 00110010 01001110 01111001 01011010 01011000 01011010 00110110 01100011 01101101 01000110 01101110 01100010 01101110 01101011 01100111 01010111 01101101 00110101 01110111 01100100 01011000 01011010 01101000 01100011 01100111 00111101 00111101<@/auto_decode_0>

下面是另一件T恤上的二进制字符串，想要知道答案同样需要你自己动手。

    
    
    <@auto_decode_10>01011010 01101110 01100001 01110000 01110101 01110010 01100110 01100111 01110010 01100101 00101100 00100000 01100110 01100010 00100000 01111010 01101000 01110000 01110101 00100000 01100111 01100010 00100000 01101110 01100001 01100110 01101010 01110010 01100101 00100000 01110011 01100010 01100101<@/auto_decode_10>

## 解密 XOR repeating key 加密

为了完成James向我发起的解密repeating XOR加密的挑战，我在知名密码学站点[Practical
cryptography](http://practicalcryptography.com/)学习了所有关于XOR和频率分析的知识。第一步是确定key的长度，你可以为各个候选键使用频率分析来确定。这里我使用30作为最大猜测key长度。我将每个字符都存储在了频率表中，并每次当它们出现在密文中时递增它们。当你拥有所有频率时，你就可以计算出每个列和频率的重合因子（或汉明距离）。

我花了大量的时间尝试提高key猜测的准确性，并多次重写了相关代码。在[trusted signal
blog](https://trustedsignal.blogspot.com/2015/06/xord-play-normalized-hamming-distance.html)的这篇文章中提到，可以通过使用前5-6个候选键的最大公分母来提高准确性确定key长度。但在我的测试中，我无法做到这点。无论如何，一旦你获取到了key长度，你只需循环遍历密文和每个字符并进行xor加密，然后根据字符结果为其分配一个分数。这里我要感谢Alexey
Hellman，我的大部分代码都是基于他的[xortool](https://github.com/hellman/xortool)实现的。

最后，使用我的is_like_english函数来确定文本的分数。这仅适用于小文本，对于大文本是无效的。这是因为文本越大，得到的ngram分数就越低。因此我将固定值更改为平均值之间的差异百分比，这样一来无论密文长度是多少都将可以正常执行。但如果密文过小，XOR解密同样将失败，这是因为没有足够的密文来执行频率分析，无法确定解密的每个字符的key长度和分数导致的。如果你有更好的解决办法，请随时向我提交pull
request。

以下是一个演示示例，我xor加密了一个key，然后对其进行了hex编码。粘贴到输入框后，Hackvertor将自动解码十六进制，猜测key长度，然后自动解密XOR加密。

    
    
    <@auto_decode_8>1C090C1E05041C101C523D296324212F000D020C04061D001C216F36383668231619064521010606376F3724732E080D0F561617171A003B3B3A6B3630110C18031717074F1037292C39366808174C0545061B00523E2E372E7D68231A4B03161B1A0852313A373F3A26064E0E120217541C1133212D223D2F41170E150D1C1B031D35366F6B2A27144308170B521D0B173C3B2A2D2A68150B0E5613170616523E2E372E203C41151E1A0B17060E103B232A3F3A2D124D4B391000541D17212A22393020041118560300111E07372137272A68140D08191317064F10202E2D2F732604144B00101E1A0A00332D2A273A3C1843081A0401070A01723B2B2A276823161906451B074F063A2A632D3A3A12174B020A52060A023D3D3765<@/auto_decode_8>

 ** *参考来源：[portswigger](https://portswigger.net/blog/bypassing-wafs-and-cracking-xor-with-hackvertor) ，FB小编secist编译，转载请注明来自FreeBuf.COM**


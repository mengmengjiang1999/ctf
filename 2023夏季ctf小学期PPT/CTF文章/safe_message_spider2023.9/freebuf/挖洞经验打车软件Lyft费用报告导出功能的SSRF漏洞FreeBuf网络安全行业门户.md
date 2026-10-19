**![lyft.jpg](https://image.3001.net/images/20200604/1591263132_5ed8bf9c4adcf.jpg!small)**

**在外出参与某个安全会议的旅程中，我发现打车拼车应用Lyft能以PDF或CSV方式生成用户的行程消费报告，作为一个Lyft的老用户，这种功能非常方便，可以简化我繁琐的工作费用整理流程。但便利的同时，我也在想一个问题：它会存在安全漏洞吗？最终经过我与Cody
Brocious (@Daeken)的测试，发现Lyft在该功能上确实存在漏洞。该漏洞于2018年发现，直到最近才公开，我们一起来看看。**

## Lyft的消费报告导出功能

当完成了一次打车服务，缴费或给司机评分之后，在Lyft应用弹出的行程信息窗口中，用户可以在其中输入消费代码（expense
code）或其它信息，来对行程进行标识记录。比如，出于测试目的，我打车到机场后，在Lyft应用中的“行程历史”（Ride
History）下的行程信息窗口标识中，我输入了一个HTML标记(<h1>test)，之后，对应地它会提示我可以导出消费报告。点击导出之后，它会向我的邮箱发现两种报告模板：CSV和PDF，在我打开PDF版本的报告后，之前我输入的HTML标记(<h1>test)竟然成功在消费标识区域被加载了：

![lyft3.png](https://image.3001.net/images/20200604/1591262808_5ed8be583113a.png!small)这个可利用点引起了我们的注意，我们想可以尝试用其中的PDF生成机制（PDF
generator）来构造SSRF漏洞。

## 构造SSRF漏洞

从上可知，向PDF消费报告生成机制（PDF generator）中插入的HTML标记能有效加载，接下来可以考虑，利用该功能是否可让PDF
generator调用一些外部资源实现敏感信息收集（如user-agent类的用户信息等）。由于行程消费标识操作每次都需要启动Lyft应用，为此，我们在其中设置了几个包含外部链接的行程历史记录，其中嵌入了如<iframe>
和 <img>的外部资源标记，但是，经过测试发现，这种方式完全无效，没有任何反应。

数周之后，HackerOne在纽约举办了一场线下实时比赛，其中就包含了 Lyft APP，而且这种类似内测的比赛可以在Lyft
APP中添加大量行程历史记录，因此对我们来说，这算是一个非常好的漏洞测试机会。本次比赛，我们把关注点调整，首先需要了解为什么<h1> 和<u>
标记能正常加载，而<img> 和
<iframe>却不行。之前说过，在Lyft发来的消费报告中还存在一个CSV文件，经过对比其中的字符串集，我们发现其中包含的左右双引号是这样的 **“**
，而非正常的英打双引号 **"**
，之后，我们在PDF消费报告的Payload进行了校正，然后请求PDF报告，就能从Lyft应用中获取到报告生成服务端的User-Agent信息，其中包含了WeasyPrint服务，如下：

![lyft4.png](https://image.3001.net/images/20200604/1591262833_5ed8be7151596.png!small)

## WeasyPrint

WeasyPrint
是一个开源的智能WEB报告生成服务，用它可以方便地在WEB应用中制作生成PDF报告，它能把简单的HTML标记转变成华丽的**、票据、统计报告等，用户在相应的HTML模板或URL链接中填写好要求的字段后就能自动生成PDF报告，如用以下命令就能把一个填写好的HTML模板生成PDF报告：

> $> weasyprint input.html output.pdf

所以，接下来我们就把研究点放到了WeasyPrint服务上，经过分析，我们发现WeasyPrint的具体工作机制如下：

> 允许嵌入短小数字作为HTML标记
>
> 不允许执行Javascript脚本
>
> 不允许执行iframe或类似标记

通过对[WeasyPrint](https://weasyprint.org/)开源代码的分析查看之后，我们在[html.py](https://github.com/Kozea/WeasyPrint/blob/b7a9fe7dcc9d0755a3324b74d0965e806bb87378/weasyprint/html.py)中发现了一些有意思的地方，如WeasyPrint对img、embed和object等标签集都进行了重定义，由于其不支持Javascript脚本，所以当时我们对PDF生成机制的漏洞利用就没抱太大希望。但是，后来，我们在WeasyPrint开源代码的
[pdf.py](https://github.com/Kozea/WeasyPrint/blob/b7a9fe7dcc9d0755a3324b74d0965e806bb87378/weasyprint/pdf.py)文件中发现了<link>属性，该属性允许向PDF报告插入任意的网页形式或本地文件内容，如：

> <link rel=attachment href="file:///root/secret.txt">

最终，利用数据压缩函数库zlib 以及 python, 我们写了一个从PDF文件中解包本地文件的脚本，如下：

    
    
    import sys, zlib
    
    def main(fn):
    
        data = open(fn, 'rb').read()
    
        i = 0
    
        first = True
    
        last = None
    
        while True:
    
            i = data.find(b'>>\nstream\n', i)
    
            if i == -1:
    
                break
    
            i += 10
    
            try:
    
                last = cdata = zlib.decompress(data[i:])
    
                if first:
    
                    first = False
    
                else:
    
                    pass#print cdata
    
            except:
    
                pass
    
        print(last.decode('utf-8'))
    
    if __name__=='__main__':
    
        main(*sys.argv[1:])

## 最后一程

在本地环境测试中，我们把上述脚本结合Lyft的PDF生成机制设置了一个包含Payload的行程记录，在导出PDF报告的过程中，触发了其中的SSRF利用，获取到了相应的用户信息，确认了漏洞的存在，如下：

![lyft5.jpg](https://image.3001.net/images/20200604/1591262963_5ed8bef32751e.jpg!small)

## 致谢

感谢Lyft安全团队，Daeken的思路、@d0nutptr的漏洞验证，更多技术细节请查看HackerOne报告-[H-885975](https://hackerone.com/reports/885975)，或观看NahamSec频道YouTube视频：
[Exploiting a Server Side Request Forgery (SSRF) in WeasyPrint for Bug Bounty
& HackerOne’s $50M CTF ](https://www.*******.com/watch?v=t5fB6OZsR6c)

## 漏洞上报和处理过程  

> 2018.11.10 - 我初次发现漏洞
>
> 2018.11.29 - 在纽约比赛中与@Daeken合作完成POC
>
> 2018.11.29 - 报送Lyft安全团队
>
> 2018.11.29 - Lyft修复漏洞
>
> 2018.11.30 - Lyft告知漏洞已修复
>
> 2018.12.05 - Lyft按其最高众测标准给予漏洞赏金
>
> 2020.5.20 - 漏洞公开

 ***参考来源：[nahamsec](https://www.nahamsec.com/posts/my-expense-report-resulted-in-a-server-side-request-forgery-ssrf-on-lyft)，clouds 编译整理，转载请注明来自
FreeBuf.COM**


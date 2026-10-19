*****本文原创作者：geek痕，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

**谈到爆破，相信大部分网络安全从业者都并不陌生，爆破爆破，就是暴力破解嘛。通过枚举尝试尽可能多的可能解，再进行验证判断是否正确。在进行web的爆破时，我们通常会使用brupsuite等工具，那么，如果是二进制程序中的爆破呢？**

本文将介绍一种方法，通过动态插桩（hook）的方式，实现二进制程序中的爆破。最近在学习逆向，刷一些ctf的题目，遇到了一道拖进ida死活分析不出算法，因为实在是太菜了，目标程序大概长这样：

![image.png](https://image.3001.net/images/20180824/1535115865_5b8002592b334.png!small)

有兴趣的可以先试试：地址如下：<http://ctf5.shiyanbar.com/re/100w.exe>  

输入的口令正确则会弹出flag，输入错误则会弹出错误提示。

![image.png](https://image.3001.net/images/20180824/1535115875_5b80026331888.png!small)

看到提示说是6位数字，而且在逆向的过程中发现有这样一段文字：  

![image.png](https://image.3001.net/images/20180824/1535115903_5b80027f8435a.png!small)

行吧…那就爆破一个试试。之前就听说过Frida牛逼的不行，跨平台的动态插桩框架，不过之前一直没亲自动手玩过，这次就试试吧。在实践过程中发现Frida的相关资料本身并不多，而且大多是针对Android移动平台的应用，于是决定写一篇文章分享一些桌面端Frida应用的技术。先上一段Frida的介绍：  

> ## So what is Frida, exactly?
>
> It’s[Greasemonkey](https://addons.mozilla.org/en-> US/firefox/addon/greasemonkey/) for  
>  native apps, or, put in more technical terms, it’s a dynamic code  
>  instrumentation toolkit. It lets you inject snippets of JavaScript or your
> own  
>  library into native apps on Windows, macOS, GNU/Linux, iOS, Android, and
> QNX.  
>  Frida also provides you with some simple tools built on top of the Frida
> API.  
>  These can be used as-is, tweaked to your needs, or serve as examples of how
> to  
>  use the API.

Frida是一个动态插桩的工具包。它可以让你将js脚本或那你自己的一些库插入到win、macos、linux、android、ios等平台的应用中。跨平台的实现方案听起来很牛逼有木有，这意味着熟练掌握这一个工具的性价比是很高的。乱扯了那么多，先来看下Frida使用的基本代码框架。以下是python的代码。首先，用pip安装一下：

    
    
    pip install frida

然后下面这段代码是frida 的基本框架：

    
    
    import frida
    def on_message(message, data):
        print("[%s] => %s" % (message, data))
    session = frida.attach('100fw.exe')#附加frida到目标进程
    script = session.create_script('some js code here')
    script.on('message', on_message)
    script.load()
    sys.stdin.read()
    session.deatch()

代码比较简单，不多解释。重点是session.create_script里面的js代码。

首先，我们要能够模拟调用按钮点击后执行的函数。

找这个函数地址的思路有两个。一个，由于这个crackme是用易语言写的，所以用e-debug可以找到call的地址：

![image.png](https://image.3001.net/images/20180824/1535115912_5b8002881b8e3.png!small)

另外一个方法就是拖入od找字符串然后往上找到函数入口，下断点验证。不行再往上翻。

![image.png](https://image.3001.net/images/20180824/1535115917_5b80028d59275.png!small)

最后找到函数入口如下：

![图片.png](https://image.3001.net/images/20180825/1535155678_5b809ddecc4d7.png!small)

然后，我们用frida的js api写一个模拟调用的函数。  

    
    
    var f=new NativeFunction(ptr('0x0040173a'), 'void',[]);
    rpc.exports={
        once:function(){
            f();
        }
    };

NtiveFunction的后面两个参数中，第一个是返回值类型，第二个是参数列表的类型，这里都为空即可。

然后定义once模拟调用一次按钮点击事件。

最后，我们在python代码中调用frida为我们暴露出来的接口：

    
    
    while(True):
        script.exports.once()

以上代码可以不断模拟点击目标程序中按钮的过程。

再然后，我们需要模拟往输入中填入各个值。那么要做的就是hook获取控件数值的相关函数。找的方法嘛..我用的是先把断点下到按钮事件函数那里，然后单步走起。看哪个函数返回了输入值的指针。

![image.png](https://image.3001.net/images/20180824/1535115925_5b80029555a10.png!small)

ok，找到函数地址为0X00401CE7（最靠近结果的call）

接下来我们hook这个函数的返回结果，让它依次遍历每一个可能的值：

    
    
    var tmp=100000;
    var NeedAdd=true;
    var f3=ptr('0x00401CE7');
    Interceptor.attach(f3,{
        onLeave:function(result){
        /*
            console.log('----------')
            console.log(result.toInt32());*/
            Memory.writeAnsiString(ptr(result.toInt32()),tmp.toString())//result为输入值的指针指向
            
            if(NeedAdd){tmp=tmp+1;NeedAdd=false;}
            else{NeedAdd=true;}
            /*
            console.log(Memory.readAnsiString(ptr(result.toInt32())));*///输出修改后的结果
        }
    });

上面的代码有注释，这里解释下为什么用NeedAdd辅助来让tmp值每两次递增一次.因为...我比较菜hook点不是很合适，每一次调用都会有两次被hook到，所以..就出此下策了。

接下来，我们要hook掉消息框弹窗函数，获取提示内容以判断口令的正确与否。

眼看着这是最后一步了，但我却在这里踩了很多坑。

首先，获取信息框内容嘛，好啊，我hook
MessageBox不就好了，于是用OD插件给API下断一通乱搞，获取到了弹窗内容美滋滋。跑起来一看，等等！难道要我每一次都点一下确认把消息框弄掉才能进行下一次尝试吗？不行！要把这个信息框干掉。然后想着直接跳过对MessageBox的call，结果程序崩了，调试一番才发现，堆栈不平衡，hook了好几个都不行。

就在这里卡了好一会，后来觉得沿着api的调用栈一直往上翻，一定能找到用户态最初的call，那个call的调用关系应该相对简单，堆栈平衡问题也比较容易处理，然后就一直找啊找，发现就在搜到的字符串附近有这样一段代码，顿时两眼放光：

![image.png](https://image.3001.net/images/20180824/1535115931_5b80029be698d.png!small)

这就好办了，结果跟进去一看，发现这只是一个索引，hook这个会影响很多函数：

![image.png](https://image.3001.net/images/20180824/1535115937_5b8002a1ac074.png!small)

那不如..直接把这个call给nop掉吧..把这个嘴给塞住。

测试之后发现经过add esp，0x28后堆栈刚好平衡，很好，perfect！

现在，我们可以写出最后一段代码了：

    
    
    var f4=ptr('0x00401C03');
    Interceptor.attach(f4,{
        onEnter:function(args){
            //console.log(args[0]);
            send(Memory.readAnsiString(ptr(args[0])));//读取相应内容并发送给终端显示
            
            return;
        }
    });

这里解释一下，为什么把0x00401c03 nop掉之后仍然可以hook这里。

根据我的猜测，frida的hook应该是内存断点，获取的“参数”就是根据堆栈情况的相对位置确定的，所以我们可以“hook”这个地方，获取到前面push的内容，至于那个args[0]，多试几个就好了。

其实，成功的时候call的地方不在这里，而我们没有处理成功弹窗的相关代码，成功后自然会弹出来，这里的显示有些多余，当作实验就好了吧。

下面是完整代码：

    
    
    import frida
    import sys
    
    
    def on_message(message, data):
        print("[%s] => %s" % (message, data))
    
    
    session = frida.attach('100fw.exe')
    script = session.create_script('''
        var tmp=700000;
        var NeedAdd=true;
        var f1 = ptr('0x00401096');
        var f2 = ptr('0x0040169d');
        Interceptor.attach(f1, {
            onEnter:function(args){
                
            }
        });
        Interceptor.attach(f2, {
            onEnter:function(args){
                
            }
        });
        var f=new NativeFunction(ptr('0x0040173a'), 'void',[]);
        rpc.exports={
            once:function(){
                f();
            }
        };
        var f3=ptr('0x00401CE7');
        Interceptor.attach(f3,{
            onLeave:function(result){
            /*
                console.log('----------')
                console.log(result.toInt32());*/
                Memory.writeAnsiString(ptr(result.toInt32()),tmp.toString())
                
                if(NeedAdd){tmp=tmp+1;NeedAdd=false;}
                else{NeedAdd=true;}
                //console.log(Memory.readAnsiString(ptr(result.toInt32())));
                console.log(tmp);
            }
        });
        /*
        var f4=ptr('0x00401C03');
        Interceptor.attach(f4,{
            onEnter:function(args){
                //console.log(args[0]);
                send(Memory.readAnsiString(ptr(args[0])));
                
                return;
            }
        });
        */
        
    ''')
    script.on('message', on_message)
    script.load()
    while(True):
        script.exports.once()
    sys.stdin.read()
    session.deatch()

最好运行成功之后是酱紫的：

![image.png](https://image.3001.net/images/20180824/1535115946_5b8002aa3aa77.png!small)

再说几点注意吧，首先是运行的时候要先运行程序，再运行py脚本，不然会出现这个：

![image.png](https://image.3001.net/images/20180824/1535115949_5b8002adbf2d8.png!small)

然后是我们要先在输入框中输入一个随意的六位数，这样系统才会分配一个储存的空间。不然会出现这样：

![图片.png](https://image.3001.net/images/20180824/1535116533_5b8004f56c341.png!small)

这个解决方案有个地方不足就是效率还是低了点，完整爆破需要一些时间。

我尝试过减少调试性的输出来提升效率，还是有一定效果的。然后因为爆破的时候cpu并没有跑满，所以多开几个实例来分段跑估计也能快不少。看了正解算法的确比较复杂，orz。

最后，本文旨在探讨Frida的使用技巧。总的来说，Frida的可玩性还是很高的，还有很多js api接口没有介绍，有兴趣的可以去官网看看文档。

写文章的经验不多，还请各位dalao拍砖！

 ***本文原创作者：geek痕，本文属FreeBuf原创奖励计划，未经许可禁止转载**


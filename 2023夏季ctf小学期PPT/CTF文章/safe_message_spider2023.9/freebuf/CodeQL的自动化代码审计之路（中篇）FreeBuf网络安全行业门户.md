## **0x01 前言**

在上一篇文章中，我们已经了解了关于CodeQL的基本语法，从实际案例角度来体验了CodeQL在代码审计中的作用。从这篇文章开始，我们将开始真正打造基于CodeQL的自动化代码审计工具，由于这仅仅是来自于个人兴趣的研究，并非来自成熟项目，所以在文章中可能缺陷，各位大佬如果有更好的意见建议，请私信。

CodeQL的代码审计整体过程可以分成两个部分，如图1.1所示，分别是从源代码解析成CodeQL数据库和从数据库中查询出安全隐患。本次分享主要关注第二阶段的内容，假设我们已经有了CodeQL数据库之后，下一步基于数据库的自动化查询。![](https://image.3001.net/images/20221122/1669105038_637c858e661fbccb36c39.png!small)

图1.1 CodeQL代码审计过程阶段

为什么我们最终结果得到的是安全隐患，而不是漏洞呢？这是因为CodeQL并不是万能的，它只能帮我们找到可能的安全隐患，而不能一定确认漏洞存在，这在后面的文章中会说到原因。

当前的自动化代码审计工具将采用python3开发，针对的目标语言是java，后续如果有时间，也会陆续支撑其他语言。目前代码还不是特别完善，后期后继续对代码进行优化，见github地址：

<https://github.com/webraybtl/codeql>

##  **0x02 工具设计**

基于CodeQL的自动化代码审计工具流程其实和传统的漏洞扫描工具相似，所以我们还是按照传统漏扫的思路来设计工具。关于第一阶段源码转化为数据库的部分在下一篇文章来详述，这里还是只关注第二阶段数据库查询的内容，如图2.1所示。

![](https://image.3001.net/images/20221122/1669105081_637c85b91a0eaaaa9c452.png!small)图2.1
自动化工具设计流程

其实从流程中可以看出，工具的主要功能是基于ql插件的遍历，对插件结果的格式化输出。首先需要解决的问题是关于ql插件来源的问题，在上一篇文章中，我们有提到CodeQL官方给我们提供了很多测试用的demo实例[https://github.com/github/codeql/tree/main/java/ql/src/experimental/Security/CWE。](https://github.com/github/codeql/tree/main/java/ql/src/experimental/Security/CWE%E3%80%82)

官方按照CWE提供了多个不同类型的ql插件，部分插件是可以直接来用的，但是有的插件涉及到自定义qll库，需要进行一定的转化才能使用，如图2.2所以，FilePathInjection.ql脚本就是典型的有自定义库的脚本。![](https://image.3001.net/images/20221122/1669105116_637c85dc53d87c29cb55b.png!small)

图2.2 使用了qll自定义库的ql脚本

在我们设计的自动化工具中，为了方便会只查询单个ql脚本，需要把ql脚本中调用的qll库进行转化。转化的方式是显示的把qll库中定义的类和谓词直接定义到ql脚本中，我已经把官方提供的全部脚本都转化了一遍，后续会将完整的代码分享到github。

为了方便统一的对结果进行格式化输出，我们期待每一个ql文件最终返回的结果都是统一格式，所以还需要对每个ql文件最终的返回结果进行约束，典型的demo如下所示。其中select后面的值是ql脚本最终返回的数据。

    
    
    from DataFlow::PathNode source, DataFlow::PathNode sink, BeanShellInjectionConfig conf
    where conf.hasFlowPath(source, sink)
    select source.toString(),source.getNode().getEnclosingCallable(),source.getNode().getEnclosingCallable().getFile().getAbsolutePath(), 
          sink.toString(),source.getNode().getEnclosingCallable(), sink.getNode().getEnclosingCallable().getFile().getAbsolutePath(), "BeanShell injection"
    

表2.1 ql脚本输出规范约束

![](https://image.3001.net/images/20221122/1669105191_637c8627aa6d521d95c0e.jpg!small)由于CodeQL官方并不对引擎开源，我们只能直接使用官方编译好的版本，官方编译好的引擎并不支持python这些语言，只能从命令行进行调用，如图2.3所示。其中-d参数用于表示待查询的数据库路径，最后跟的是要查询的ql脚本路径。

![](https://image.3001.net/images/20221122/1669105213_637c863deebbe35a2770a.png!small)

图2.3 通过命令行调用codeql查询

由于CodeQL每次查询都需要使用ql脚本文件路径，如果每次查询都需要先生成一个文件，然后查询结束之后再删除文件，代码显得怪怪的。好在python给我们提供了tempfile库，可以稍微优雅的解决这个问题，如图2.4所示。这是一段我项目中检查环境是否准备好了的代码，通过tempfile生成临时的ql脚本，临时脚本在运行结束之后会自动自动删除。

![](https://image.3001.net/images/20221122/1669105237_637c8655007496d2a7376.png!small)图2.4
使用tempfile生成临时文件查询codeql

本来想自己封装了一个类来调用调用CodeQL运行，但是突然看到网上已经有大佬写好了一个相应的类https://github.com/AlexAltea/codeql-python，其实现思路和我之前的想法差不多，本质上还是从命令行调用的CodeQL。然而我直接运行大佬的代码却运行不成功，主要原因还是在于生成的临时文件必须要在ql
sdk所在测试路径，路径下必须有正确配置的qlpack.yml文件。所以我在原代码的基础上修改了一下，主要是固定sdk路径为配置好的路径。

这之后我们一个简易的基于CodeQL的自动化代码审计工具雏型就差不多了，后续会陆续在这个框架的基础上优化功能。

##  **0x03 插件优化**

官方虽然提供了大约59个java的ql查询插件，但是实际上还远不能满足我们的需求，我们希望有更多的白帽子参与进来提供更多的ql查询插件。当前阶段，我按照自己日常漏洞挖掘过程补充一些ql查询插件，如下所示，相关插件均在plugins/java_ext目录。

表3.1
新增的Java常见漏洞查询ql脚本![](https://image.3001.net/images/20221122/1669105276_637c867c32fe2b54cc853.jpg!small)

本次新增只是一个开端，并不能覆盖全部，自知还相差很远。但是不断的优化，总归会有好的效果。由于部分小伙伴对与CodeQL的语法了解甚少，我们用一个简单的脚本Unserialze.ql来说明完整的CodeQL脚本的写法。

反序列化漏洞是java中常见的漏洞，典型的漏洞代码写法如下。这是一段从某应用中提取的真实漏洞的部分代码。

    
    
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        ObjectInputStream objin = new ObjectInputStream(request.getInputStream()); //这里是获取用户输入
        response.setContentType("application/x-download");
        ServletOutputStream out = response.getOutputStream();
    
        try {
            String dsName = (String)objin.readObject(); //这里是反序列化的点
            System.out.println(dsName);
        } catch (Exception var11) {
            var11.printStackTrace();
        }
    
        out.close();
        objin.close();
    }
    

其中最关键的是用户可控的source点为request.getInputStream()，最后的危险操作sink点为objin.readObject()。也就是说外部传入的postdata直接进行了反序列化操作，则可能导致反序列化漏洞。对于CodeQL中，可以编写对应的查询脚本如下。

    
    
    import java
    import semmle.code.java.dataflow.FlowSources
    import semmle.code.java.dataflow.TaintTracking
    import semmle.code.java.dataflow.DataFlow
    
    class UnserializeSink extends DataFlow::Node {
        UnserializeSink(){
            exists(MethodAccess ma,Class c | ma.getMethod().hasName("readObject") and 
                    ma.getQualifier().getType() = c and 
                    c.getASupertype*().hasQualifiedName("java.io", "InputStream") and 
                    this.asExpr() = ma
            )
        }
    }
    
    class UnserializeSanitizer extends DataFlow::Node { 
        UnserializeSanitizer() {
          this.getType() instanceof BoxedType or this.getType() instanceof PrimitiveType
        }
      }
    
    class JavaUnserialize extends TaintTracking::Configuration {
        JavaUnserialize() { this = "Java Unsearialize" }
      
        override predicate isSource(DataFlow::Node source) { source instanceof RemoteFlowSource }
    
        override predicate isSink(DataFlow::Node sink) { sink instanceof UnserializeSink }
    
        override predicate isSanitizer(DataFlow::Node node) { node instanceof UnserializeSanitizer } 
      
      }
      
    
    from DataFlow::PathNode source, DataFlow::PathNode sink, JavaUnserialize conf
    where
      conf.hasFlowPath(source, sink)
    select source.toString(),source.getNode().getEnclosingCallable(),source.getNode().getEnclosingCallable().getFile().getAbsolutePath(), 
          sink.toString(),source.getNode().getEnclosingCallable(), sink.getNode().getEnclosingCallable().getFile().getAbsolutePath(), "Potential JAVA Unserialize Vulnerability"
    

其中source点直接使用CodeQL预定义的类RemoteFlowSource，而sink点则是通过下面的代码实现。判断的逻辑是存在一个方法名为readObject的调用，并且调用的主体继承自java.io.InputStream类。注意这些说的是反序列化漏洞，不涉及利用链，不一定就真的能导致RCE效果。

    
    
    exists(MethodAccess ma,Class c | ma.getMethod().hasName("readObject") and 
                    ma.getQualifier().getType() = c and 
                    c.getASupertype*().hasQualifiedName("java.io", "InputStream") and 
                    this.asExpr() = ma
            )
    

单独执行对应的脚本，则可以发现程序中可能存在的反序列化漏洞，如图3.1所示。

![](https://image.3001.net/images/20221122/1669105354_637c86ca309da556feedf.png!small)

图3.1 单独运行Unserialize.ql脚本的效果

其他脚本就不再依次讲解，如果有小伙伴感兴趣，非常期待小伙伴能为我们提供插件。如果小伙伴不知道怎么编写CodeQL脚本，可以把有漏洞的代码逻辑给私信我，由我来转化为CodeQL插件。

##  **0x04 工具使用**

回到工具本身，当前完整的代码我已经放在github，使用方式如下所示。

使用之前应该首先安装CodeQL,并配置config/config.ini，其中最关键的是配置临时生成的ql脚本保存的路径qlpath，如图4.1所示。确保qlpath当前目录下面有配置文件qlpack.yml。如果使用的过程中有问题，建议把debug配置为on。

![](https://image.3001.net/images/20221122/1669105384_637c86e8d81ee8085cb40.png!small)

图4.1 项目配置文件

运行python3 main.py -h，如图4.2所示。

其中参数-d代表数据库文件地址，必填。

参数-s代表是否跳过环境检查，不填默认为false，首次使用建议不跳过环境检测。

![](https://image.3001.net/images/20221122/1669105405_637c86fd8fa43bc7cbdc3.png!small)

图4.2 项目支持的参数列表

运行python3 main.py -d /Users/xxxx/CodeQL/databases/RuoYI/，通过若依源码来掩饰效果。

![](https://image.3001.net/images/20221122/1669105444_637c872477877f832fa3d.png!small)

图4.3 使用工具获取的扫描结果

最终的扫描结果是以csv文件保存在out/result/目录，打开相应的结果，如图4.4所示。

![](https://image.3001.net/images/20221122/1669105471_637c873f140a74e898fc1.png!small)

图4.4 对结果进行格式化输出到CSV文件中

关于结果的分析我们在上一篇文章中已经涉及到一些，这里就不再分析结论。

##  **0x05 工具不足**

在图4.4的结果中，有很多FilePathInjection插件扫描的结果，其中记过都很相似，以其中之一为例，我们基于文件的source和sink定位其中的问题。

定位到source文件和方法，com.ruoyi.web.controller.system.
SysProfileController类的updateAvatar方法，如图5.1所示。

![](https://image.3001.net/images/20221122/1669105499_637c875bf17e6c91d7ea6.png!small)

图5.1 Source类与方法

继续跟踪upload方法，就可以到sink点，如图5.2所示。

![](https://image.3001.net/images/20221122/1669105519_637c876f1484b76e5898c.png!small)

图5.2 Sink的类与方法

这里其实RuoYI已经对上传文件的文件扩展名进行了限制，然后CodeQL仍然把这里识别为漏洞，这是典型的误报行为，而这也是CodeQL的代码审计工具中最难解决的一个问题。

CodeQL可以跟踪Source和Sink流，但是毕竟仍然只是静态代码审计工具，无法自动解析代码中的一些过滤操作，导致可能会出现误报。而这也是文章开头提到的CodeQL只能作为辅助工具发现安全隐患，不能确定是否一定存在漏洞的原因。

##  **0x06 结论**

距离自动化的代码审计工具，我们仍然有很长的路要走，如果小伙伴能提供一些可用的ql插件或者提供有漏洞的代码样本由我们来编写ql插件，我们都将非常感激。

后续我们会陆续丰富工具的功能，特别是解决前一阶段生成数据库的问题。

[原文链接](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485489&idx=1&sn=166e44a1496dfa1e066b771065ac8120&chksm=c2a1dcb8f5d655ae1c0c76555ee00adc8e5177b9ec531bc986149865b882631f53911b28b5cf&token=1083887551&lang=zh_CN#rd)


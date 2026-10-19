本文首发于“合天智汇”公众号 作者：Fortheone

# 前言

最近学习java反序列化学到了weblogic部分，weblogic之前的两个反序列化漏洞不涉及T3协议之类的，只是涉及到了XMLDecoder反序列化导致漏洞，但是网上大部分的文章都只讲到了触发XMLDecoder部分就结束了，并没有讲为什么XMLDecoder会触发反序列化导致命令执行。于是带着好奇的我就跟着调了一下XMLDecoder的反序列化过程。

# xml序列化

首先了解一下java中的XMLDecoder是什么。XMLDecoder就是jdk中一个用于处理xml数据的类，先看两个例子。

这里引用一下浅蓝表哥的（强推浅蓝表哥的博客https://b1ue.cn/

    
    
    import java.beans.XMLEncoder;
    import java.io.IOException;
    import java.util.ArrayList;
    import java.util.HashMap;
    
    /**
     * @author 浅蓝
     * @email blue@ixsec.org
     * @since 2019/4/24 12:09
     */
    public class Test {
    
        public static void main(String[] args) throws IOException, InterruptedException {
    
            HashMap<Object, Object> map = new HashMap<>();
            map.put("123","aaaa");
            map.put("321",new ArrayList<>());
    
            XMLEncoder xmlEncoder = new XMLEncoder(System.out);
            xmlEncoder.writeObject(map);
            xmlEncoder.close();
    
        }
    }

![](https://image.3001.net/images/20200820/1597901982.png!small)

这样就把map对象变成了xml数据，再使用XMLDecoder解析一下。

    
    
    /**
     * @author 浅蓝
     * @email blue@ixsec.org
     * @since 2019/4/24 12:09
     */
    public class Test {
    
        public static void main(String[] args) throws IOException, InterruptedException {
            String s = "<java version=\"1.8.0_131\" class=\"java.beans.XMLDecoder\">\n" +
                    " <object class=\"java.util.HashMap\">\n" +
                    "  <void method=\"put\">\n" +
                    "   <string>123</string>\n" +
                    "   <string>aaaa</string>\n" +
                    "  </void>\n" +
                    "  <void method=\"put\">\n" +
                    "   <string>321</string>\n" +
                    "   <object class=\"java.util.ArrayList\"/>\n" +
                    "  </void>\n" +
                    " </object>\n" +
                    "</java>";
            StringBufferInputStream stringBufferInputStream = new StringBufferInputStream(s);
            XMLDecoder xmlDecoder = new XMLDecoder(stringBufferInputStream);
            Object o = xmlDecoder.readObject();
            System.out.println(o);
    
        }
    }

![](https://image.3001.net/images/20200820/1597901999.png!small)

就可以把之前的xml数据反序列化回map对象，那么如果对xml数据进行修改，使其变成一个执行命令的数据。比如说：

    
    
    <java version="1.7.0_80" class="java.beans.XMLDecoder">
     <object class="java.lang.ProcessBuilder">
      <array class="java.lang.String" length="1">
        <void index="0"><string>calc</string></void>
      </array>
      <void method="start"></void>
     </object>
    </java>

然后对其反序列化即可执行命令弹出计算器。

![](https://image.3001.net/images/20200820/1597902011.png!small)

现在我们知道了如果使用XMLDecoder去反序列化xml数据，数据中包含的命令会被执行。接下来就对其进行分析一下。

# XMLDecoder反序列化漏洞成因

# 一、XML数据解析前的函数处理

![](https://image.3001.net/images/20200820/1597902026.png!small)

在readObject处打上断点开始debug![](https://image.3001.net/images/20200820/1597902046.png!small)

进入了parsingComplete方法，跟进。![](https://image.3001.net/images/20200820/1597902061.png!small)

其中使用XMLDecoder的handler属性DocumentHandler的parse方法，并且传入了我们输入的xml数据，跟进。![](https://image.3001.net/images/20200820/1597902084.png!small)

这里调用了SAXParserImpl类的parse方法。![](https://image.3001.net/images/20200820/1597902126.png!small)

然后又进了xmlReader的parse方法。![](https://image.3001.net/images/20200820/1597902156.png!small)

这里又调用了xmlReader父类AbstractSAXParser的parser方法。![](https://image.3001.net/images/20200820/1597902175.png!small)

最后进入了XML11Configuration类的parse方法。

# 二、XML数据的处理![](https://image.3001.net/images/20200820/1597902192.png!small)

在XML11Configuration中进行了很多解析XML之前的操作，我们不去仔细研究，看到处理XML数据的函数scanDocument。跟进查看![](https://image.3001.net/images/20200820/1597902205.png!small)

这个函数通过迭代的方式对XML数据的标签进行解析，网上有些文章写道“解析至END_ELEMENT时跟进调试”，但是我看了一下我这里的END_ELEMENT。![](https://image.3001.net/images/20200820/1597902222.png!small)

里面没有函数可以跟进啊，然后搜了一些其他的文章，是因为jdk版本的问题，处理的逻辑放在了next函数里。在do
while循环里跳了大概十次，就开始解析了xml的标签。![](https://image.3001.net/images/20200820/1597902240.png!small)

跳到XMLDocumentScannerImpl中的next方法![](https://image.3001.net/images/20200820/1597902254.png!small)

跳到XMLDocumentFragmentScannerImpl中的next方法，解析到endtag时会走到scanEndElement方法里。

然后就到了网上说的endElement方法里，跟进。![](https://image.3001.net/images/20200820/1597902304.png!small)

这一部分的解析可以参考下图：![](https://image.3001.net/images/20200820/1597902334.png!small)

也就是说解析时会按照标签一个一个解析。

![](https://image.3001.net/images/20200820/1597902353.png!small)

这里调用了DocumentHandler的endElement方法。
**接下来就是很重要的部分![](https://image.3001.net/images/20200820/1597902548.png!small)**

![](https://image.3001.net/images/20200820/1597902560.png!small)

这里的handler是StringElementHandler，但是这个类没有重写endElement方法，所以调用的是父类ElementHandler的endElement方法，其中调用了getValueObject来获取标签中的value值，这里的标签是string标签，所以获取到的值是calc。

![](https://image.3001.net/images/20200820/1597902629.png!small)![](https://image.3001.net/images/20200820/1597902643.png!small)

然后将其添加到其父类标签VoidElementHandler的Argument属性中。

![](https://image.3001.net/images/20200820/1597902663.png!small)

然后将handler指向其父类VoidElementHandler。![](https://image.3001.net/images/20200820/1597902688.png!small)

继续解析到void标签，此时的handler就是VoidElementHandler，接着调用getValueObject。但是因为没有重写该方法，所以调用父类NewElementHandler的getValueObject。

![](https://image.3001.net/images/20200820/1597902725.png!small)

![](https://image.3001.net/images/20200820/1597902745.png!small)

继续跟进发现实现了反射调用invoke方法，也就是执行了set方法。接着再解析Array标签，按照上面的步骤解析，就完成了这一部分参数的解析。

    
    
    <array class="java.lang.String"length="1">
      <void index="0">
          <string>calc</string>
      </void>
    </array>

![](https://image.3001.net/images/20200820/1597902770.png!small)

那么再按照上面的步骤解析object标签，然后调用new 方法实例化 ProcessBuilder类。

![](https://image.3001.net/images/20200820/1597902786.png!small)

然后解析到void标签获取到start方法，然后通过调用start方法实现了命令执行，弹出计算器。

也就相当于最后拼接了 new java.lang.ProcessBuilder(new String[]{"calc"}).start();

![](https://image.3001.net/images/20200820/1597902796.png!small)

文章有说的不对的地方请师傅们指点，刚开始学java，大佬们轻喷。。。

# 参考文章

<https://b1ue.cn/archives/239.html>

<https://zhuanlan.zhihu.com/p/108754274>

<https://blog.csdn.net/SKI_12/article/details/85058040>

# 相关实验

Java反序列漏洞

<https://sourl.cn/Lknehk>

（本实验通过Apache Commons Collections 3为例，分析并复现JAVA反序列化漏洞。）


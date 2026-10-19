## 1 类文件数据结构类型

Class 文件结构主要有两种数据结构： **无符号数和表**

• **无符号数** ：用来表述数字，索引引用、数量值以及字符串等，比如 图 1 中类型为 u1,u2,u4,u8 分别代表 1 个字节，2 个字节，4
个字节，8 个字节的无符号数

• **表** ：表是有由多个无符号数以及其它的表组成的复合结构，比如图 1 中类型以_info 结尾的项为表类型。

## 2 类结构定义

Class 类文件是 **紧凑、顺序、无空隙** 的，魔数（MagicNumber）、Class
文件版本（Version）、常量池（Constant_Pool）、访问标记（Access_flag）、本类（This_class）、父类（Super_class）、接口（Interfaces）、字段集合（Fields）、方法集合（Methods
）、属性集合（Attributes）。其中因为 java 多继承所以 interfaces 接口类型为数组；attribute_info 则是方法表中定义的
code 索引，指向具体的方法体字节码。如图 1 所示。

![1686110344_64800088a739ddea032ac.png!small?1686110345453](https://image.3001.net/images/20230607/1686110344_64800088a739ddea032ac.png!small?1686110345453)

下面用一段程序做说明，此类有接口，有方法、类变量和实例变量，机器是如何识别字节码然后按照上面的规则来定义此 class 类呢？

    
    
    package com.jd.crm.Logback;
    
    public class TestClass implements Super{
    
        private static final int staticVar = 0;
    
        private int instanceVar=0;
    
        public int instanceMethod(int param) throws  Exception{
            return param ++;
        }
    }
    interface Super{ }
    

通过 javap 帮助解析 class 文件格式如下：

    
    
    Classfile /D:/spm-workspace/test/target/classes/com/jd/crm/Logback/TestClass.class
      Last modified 2023-4-14; size 597 bytes
      MD5 checksum 9d5dd9fc2145ac17393fee7a707d3b9c
      Compiled from "TestClass.java"
    public class com.jd.crm.Logback.TestClass implements com.jd.crm.Logback.Super
      minor version: 0
      major version: 52
      flags: ACC_PUBLIC, ACC_SUPER
    Constant pool:
       #1 = Methodref          #4.#26         // java/lang/Object."<init>":()V
       #2 = Fieldref           #3.#27         // com/jd/crm/Logback/TestClass.instanceVar:I
       #3 = Class              #28            // com/jd/crm/Logback/TestClass
       #4 = Class              #29            // java/lang/Object
       #5 = Class              #30            // com/jd/crm/Logback/Super
       #6 = Utf8               staticVar
       #7 = Utf8               I
       #8 = Utf8               ConstantValue
       #9 = Integer            0
      #10 = Utf8               instanceVar
      #11 = Utf8               <init>
      #12 = Utf8               ()V
      #13 = Utf8               Code
      #14 = Utf8               LineNumberTable
      #15 = Utf8               LocalVariableTable
      #16 = Utf8               this
      #17 = Utf8               Lcom/jd/crm/Logback/TestClass;
      #18 = Utf8               instanceMethod
      #19 = Utf8               (I)I
      #20 = Utf8               param
      #21 = Utf8               Exceptions
      #22 = Class              #31            // java/lang/Exception
      #23 = Utf8               MethodParameters
      #24 = Utf8               SourceFile
      #25 = Utf8               TestClass.java
      #26 = NameAndType        #11:#12        // "<init>":()V
      #27 = NameAndType        #10:#7         // instanceVar:I
      #28 = Utf8               com/jd/crm/Logback/TestClass
      #29 = Utf8               java/lang/Object
      #30 = Utf8               com/jd/crm/Logback/Super
      #31 = Utf8               java/lang/Exception
    {
      public com.jd.crm.Logback.TestClass();
        descriptor: ()V
        flags: ACC_PUBLIC
        Code:
          stack=2, locals=1, args_size=1
             0: aload_0
             1: invokespecial #1                  // Method java/lang/Object."<init>":()V
             4: aload_0
             5: iconst_0
             6: putfield      #2                  // Field instanceVar:I
             9: return
          LineNumberTable:
            line 3: 0
            line 7: 4
          LocalVariableTable:
            Start  Length  Slot  Name   Signature
                0      10     0  this   Lcom/jd/crm/Logback/TestClass;
    
      public int instanceMethod(int) throws java.lang.Exception;
        descriptor: (I)I
        flags: ACC_PUBLIC
        Code:
          stack=1, locals=2, args_size=2
             0: iload_1
             1: iinc          1, 1
             4: ireturn
          LineNumberTable:
            line 10: 0
          LocalVariableTable:
            Start  Length  Slot  Name   Signature
                0       5     0  this   Lcom/jd/crm/Logback/TestClass;
                0       5     1 param   I
        Exceptions:
          throws java.lang.Exception
        MethodParameters:
          Name                           Flags
          param
    }
    SourceFile: "TestClass.java"
    

以上是 javap 帮助我们生成的 class 文件解析结果，只是给人看，而非机器。

通过编译后生成 class 文件格式如下，因为 class 文件是以 8 位作为一个字节的二进制流。为了方便计算，用 16 进制表示二进制 (1 个字节 =
2 个十六进制的数，故下面每 2 个数就代表 1 个字节)

![1686110357_64800095bd7c2a2526328.png!small?1686110358478](https://image.3001.net/images/20230607/1686110357_64800095bd7c2a2526328.png!small?1686110358478)

### 2.1 魔法数

前四个字节 cafebabe 是固定值，任何语言编译成 jvm 认识的二进制流，前四位必须是固定的 cafebabe 字节。

### 2.2 版本号

紧接着 2 个字节 00 表示次版本号为 0 ；0034 代表主版本为 52（jdk 版本号对应的 jdk 版本为 1.8）参考 jdk 版本和 class
字节版本的对应关系

### 2.3 常量个数

常量个数 const_pool_count 字节码为 00 20 对应的说明常量个数为 32，实际为 31 个，因为首位 jvm 作为保留位使用。

### 2.4 常量池

常量池存放两大常量：字面量和符号引，字面量如文本字符串，被生命的 final
常量值等，而符号引用则包含类、接口的全限名称、字段、方法名称和描述符号等等。参考 javap 生成的类文件信息。

这里只分析下其中一个常量，在上面常量个数 2 个字节后面紧接着一个字节 0a 十进制为 10，参考常量池类型 10 代表类中方法的符号引用。继续参考方法类型
MethodRef_info 个格式定义：前两个字节 0004 代表方法所在类名称的索引，后两个字节 0001a 代表一个 NameAndType
类型的索引。

![1686110365_6480009d94122801d0710.png!small?1686110365988](https://image.3001.net/images/20230607/1686110365_6480009d94122801d0710.png!small?1686110365988)

### 2.5 类访问标志

紧接常量池定义完后的 u2 标识访问标志，本例标识为 0x0021 和下图标志位按位 **或计算** ，如 0x0001 为真，0x0020
也为真，其他为否 最终确认访问标志位 ACC_PUBLIC、ACC_SUPER

![1686110372_648000a4aed498ec678d7.png!small?1686110373178](https://image.3001.net/images/20230607/1686110372_648000a4aed498ec678d7.png!small?1686110373178)

### 2.6 本类、父类、接口索引集合

根据图 1 的规则，u2 两个字节 0003 标识当前类名的引用到，引用常量池数组下标为 #3，根据图 3 所示子项的类名为
com/jd/crm/Logback/TestClass；0004 代表父类类名的引用常量池数组下标为 #4，根据图 4 所示引用的父类类名为
java/lang/Object；紧接着 0001 标识接口个数，指明数量为 1,0005 标识第一个接口数组中接口的名称，指向常量池中下标为 5 的名称为
com/jd/crm/Logback/Super；

比如查找当前类索引如下图

![1686110377_648000a9c5646bf226402.png!small?1686110378240](https://image.3001.net/images/20230607/1686110377_648000a9c5646bf226402.png!small?1686110378240)

### 2.7 字段表集合

 **字段表以数组的形式定义存储在常量表中**

![1686110398_648000becbf358a46cf5c.png!small?1686110399590](https://image.3001.net/images/20230607/1686110398_648000becbf358a46cf5c.png!small?1686110399590)

以上图说明，0002 标识域个数为 2 个域标识，在本类中有两个，一个类的域字段 staticVar 一个是实例对象的域字段
instanceVar，如字段结构定义 (下图) 定义，前 2 个字节 001a 为访问标识，和类访问标识一样，分别用 001a
的二进制和下图字段域访问标识类型做位或运算，得出访问类型为 ACC_PRIVATE 类型。name_index 的占用两个字节 0006，指向常量表下标为
6 的引用，descriptor_index=0007 指向常量表下标为 7 的引用，此处为 I 标识为数据类型为
int，attributes_count=0001 为 1 个，值为 0008 指向常量表下标为 #8 的引用常量
ConstantValue，标识为静态变量，最终依次类推第二个域标识引用

![1686110406_648000c6b8b324705808d.png!small?1686110407298](https://image.3001.net/images/20230607/1686110406_648000c6b8b324705808d.png!small?1686110407298)

字段结构定义

 **字段域的访问标志请参考类访问标志，逻辑计算一致，只是规则不一样而已 如下图**

![1686110415_648000cf00856aed597e8.png!small?1686110415756](https://image.3001.net/images/20230607/1686110415_648000cf00856aed597e8.png!small?1686110415756)

### 2.8 方法表集合

和域字段集合表定义类似 也是数组方式定义在常量池中 ，其中方法的结构体第四个字段 attributes_count
代表方法的属性数量，attribute_info 就是属性的集合参考属性表集合

![1686110421_648000d53c79c2c8804b2.png!small?1686110421775](https://image.3001.net/images/20230607/1686110421_648000d53c79c2c8804b2.png!small?1686110421775)

![1686110428_648000dc9fe16d1b95c64.png!small?1686110429733](https://image.3001.net/images/20230607/1686110428_648000dc9fe16d1b95c64.png!small?1686110429733)

方法表访问标识类型

通过上面方法的访问标志、名称索引和描述索引定义方法的基本信息，方法的代码块则存放于类型为 Code 的属性表中。

### 2.9 属性表集合

类、字段表、方法表本身可包含属性表，属性表格结构体如下，属性表结构类型较多，比如有 Code 类型、Exception
类型、MethodParameters
类型等等，具体参考属性表类型。所有的属性都是引用常量池中的属性类型名称。然后根据属性的长度指定该属性的内容，根据属性的不同类型解析不同的属性值。格式定义如下

![1686110437_648000e575a61f6642c1a.png!small?1686110437876](https://image.3001.net/images/20230607/1686110437_648000e575a61f6642c1a.png!small?1686110437876)

以 Code 属性举例，Code 属性结构如下所示

![1686110443_648000ebc8065d85188b3.png!small?1686110444295](https://image.3001.net/images/20230607/1686110443_648000ebc8065d85188b3.png!small?1686110444295)

jvm 按属性获取 attribute_name_index 指向常量池一个字符串常量 Code, 紧接着 attribute_length 标识 Code
类型 Info 信息长度，这个 info 内容包括：max_stack 最大栈深，max_locals 局部变量槽数量，code_length
标识机器字节码长度，往后查询字节码如下图所示，其实就是 0/1/4/5/6/9 的指令集。Code 类型又嵌套异常属性表、行号表
LineNumberTable、LocaVariableTable 局部变量表等等信息。如下图 javap 生成的类定义信息

![1686110461_648000fdea620e029bb4f.png!small?1686110462581](https://image.3001.net/images/20230607/1686110461_648000fdea620e029bb4f.png!small?1686110462581)

1.Code1 方法执行过程：

构造方法：descriptor () V 标识无参无返回值为 Void 的方法索引，flags 可见性修饰符；

程序运行时，先将常量池、方法字节码、字符串常量池，静态变量加载到元数据区（ **1.8 后字符串常量池，静态变量放入了堆** ）；main
线程开始运行，分配栈帧内存，其中操作数栈 stack=2 表示运行该方法所需要的最大操作数栈的深度是 2；locals=1
表示该运行方法所需要的最大局部方法表的最大 slot 数据是 1；args_size 是该方法的形参个数，如果是实例方法 第一个形参是 this
引用。此例正是 this 引用。所以 args_size=1 + 实际的参数

aload_0: 加载 slot0 的局部变量，即 this, 作为下面的 invokespecial 构造方法调用的参数

invokespecial: 调用构造方法，常量池第 #1 项，即【Method java/lang/Object."<init>":() V】

aload_0 ：再次加载 slot0 的局部变量，即 this

iconst0: 将 int 类型为 0 的数值压入栈顶 (为什么要再放入栈顶，我个人人为可能是下面初始化实例会需要指定到当前的实例对象)

putfileld: 将常量池中 #2 也就是 com/jd/crm/Logback/TestClass.instanceVar 实例变量赋值为
0，并弹出栈。

通过以上指令操作，对象已经初始化，可发现在实例变量初始化之前是先调用的构造器方法，后才初始化实例变量。

1.Code2 方法 instanceMethod 执行过程：

descriptor 标识为 int 类型入参、int 类型出参

flags 标识方法问 public 类型

statck=2 代表栈深度为 2，locals=2 标识预留两个局部变量槽；args_size=2 标识两个参数，分别为隐藏的 this
和方法的形式参数，下标 [0]=this、 [1]=param 如下所示

LocalVariableTable:

Start Length Slot Name Signature

0 4 0 this Lcom/jd/crm/Logback/TestClass;

0 4 1 param I

0：iload_1 标识将上面局部变量槽 LocalVariableTable 下标为 1 的 param 参数压入栈

1：iconst_1 将 int 类型为 1 的常量数字压入栈

2: iadd 将当前栈顶的两个元素 param 和 1 相加

3: ireturn 返回

LineNumberTable:

line 10: 0

标识实际 java 源代码的行数

### 2.10 字节码指令简介

・加载和存储指令：

・运算指令

・类型转换指令

・对象创建和访问指令

・操作数栈管理指令

・控制转移指令

・异常处理指令

・同步指令

・方法调用和返回执行

invokervirtual: 调用对象的实例方法 invokerinterface
调用接口方法，自动运行期搜索一个实现接口的对象进行方法调用；invokerspeical: 调用 init、私有和父类调用的特殊方法调用；
**invokedynamic：运行时动态解析**

## 3 类文件加载

![1686110473_648001099a845a93dcf0f.png!small?1686110474126](https://image.3001.net/images/20230607/1686110473_648001099a845a93dcf0f.png!small?1686110474126)

### 3.1 加载

jvm 通过 classLoader (双亲委派) 将 class 类文件二进制流加载到元数据区内存，

将字节流所标识的静态存储结构转换为元数据区的动态存储

在堆内存创建一个 Class 对象，堆中的 Class
并不存储静态变量、常量、方法等实际信息（实际存储元空间），可以看做只是一个句柄，通过对象头的类指针指向元空间类信息。这样在强制转换或者 InstanceOf
判断时，会根据对象中的类指针指向元空间的类常量池进行判断是否为同一个类。

### 3.2 验证

1、文件格式验证

2、元数据验证

3、字节码验证

4、符号引用验证

### 3.3 准备

准备阶段是为类变量 (静态变量) 分配内存并设置类变量初始值的阶段，分配这些内存是在元数据区里面进行的，但是 **类变量 (无 final
修饰的静态变量)、字符串常量在 1.8 及以后都放入了堆区间** 。这个阶段有两点需要重点介绍以下的：

1、只有类变量（被 static 修饰的变量赋值初始值，static final
修饰的赋值为程序指定值）会分配内存，不包括实例变量，实例变量是在对象实例化的时候在堆中分配内存的。

2、设置类变量的初始值是数量类型对应的默认值，而不是代码中设置的默认值。例如 public static int number=111, 这类变量
number 在准备阶段之后的初始值是 0 而不是 111。而给 number 赋值为 111 是在类的初始化阶段。

### 3.4 解析

解析阶段是虚拟机将常量池内的符号引用替换为直接引用的过程，解析动作主要针对类或接口、字段、类方法、接口方法、方法类型、方法句柄和调用点限定符 7
类符号引用进行。

 **符号引用** ：常量池中类、字段的常量字符串表示方式

类和接口的解析举例：假如类 A 引用了类 B，加载阶段是静态解析，这时候 B 还没有被放到 JVM 内存中，这时候 A 引用的只是代表 B
的符号，这是符号引用。

 **直接引用:** 指向目标的指针或者相对偏移量

类和接口的解析举例：类 A 在解析阶段发现自己符号引用了 B，如果这个时候 B 还没被加载。就是直接触发 B 的类加载，加载后会在运行常量池存储 B
的有效类信息地址，并且直接引用。

・类和接口的解析

・字段解析根据常量池字段 filedrf_info
中的符号进行解析，首先在符号引用的类中根据简单名称和字段描述符查找，如果查到则返回这个字段的直接引用并结束，否则从下往上地柜各个父类查找，如果还未查到则抛出
NoSuckFieldError 异常

・方法解析

・接口方法解析

## 4 类实例初始化

初始化，为类的静态变量赋予正确的初始值，JVM 负责对类进行初始化，主要对类变量进行初始化 clinit 方法。在 Java
中对类变量进行初始值设定有两种方式： **定义静态变量并指定值、使用静态代码块**

对象初始化

![1686110488_64800118906ad05af49d3.png!small?1686110489328](https://image.3001.net/images/20230607/1686110488_64800118906ad05af49d3.png!small?1686110489328)

### 4.1 初始化对象前检查

jvm 碰到一个 new 指令，首先判断改指令指向的常量池的类全名是否被加载、解析初始化过，如果没有则进行类加载，参考类文件加载

### 4.2 内存分配

通过 jvm 内存分配机制，此分配机制取决回收机制，通过指针碰撞方法或者空闲列表方式进行堆内存分配；

1\. 指针碰撞法 假设 Java
堆中内存是完整的，已分配的内存和空闲内存分别在不同的一侧，通过一个指针作为分界点，需要分配内存时，仅仅需要把指针往空闲的一端移动与对象大小相等的距离。使用的
GC
收集器：Serial、ParNew，适用堆内存规整（即没有内存碎片）的情况下。这两种都是新生代垃圾收集器，因此都是使用复制算法，可以得到比较完整的内存区域。

2\. 空闲列表法 事实上，Java 堆的内存并不是完整的，已分配的内存和空闲内存相互交错，JVM
通过维护一个列表，记录可用的内存块信息，当分配操作发生时，从列表中找到一个足够大的内存块分配给对象实例，并更新列表上的记录。使用的 GC
收集器：CMS，适用堆内存不规整的情况下。从名字中的 Mark Sweep 这两个词可以看出，CMS 收集器是一种 “标记 - 清除”
算法实现的，因此会得到很多碎片因此和空闲列表配合使用。

内存分配并发问题

在创建对象的时候有一个很重要的问题，就是 **线程安全**
，因为在实际开发过程中，创建对象是很频繁的事情，作为虚拟机来说，必须要保证线程是安全的，通常来讲，虚拟机采用两种方式来保证线程安全：

・CAS： CAS 是乐观锁的一种实现方式。所谓乐观锁就是，每次不加锁而是假设没有冲突而去完成某项操作，如果因为冲突失败就重试，直到成功为止。虚拟机采用
CAS 配上失败重试的方式保证更新操作的原子性。

・TLAB (本地现成缓冲区)： 为每一个线程预先分配一块堆内存，JVM 在给线程中的对象分配内存时，首先在 TLAB 分配，当对象大于 TLAB
中的剩余内存或 TLAB 的内存已用尽时，再采用上述的 CAS 进行内存分配。

### 4.3 初始化 0 值

内存分配完成后，虚拟机需要将分配到的内存空间都初始化为零值（不包括对象头），这一步操作保证了对象的实例字段在 Java
代码中可以不赋初始值就直接使用，程序能访问到这些字段的数据类型所对应的零值。

### 4.4 对象头设置

初始化零值完成之后，虚拟机要对对象进行必要的设置，例如这个对象是哪个类的实例、如何才能找到类的元数据信息、对象的哈希码、对象的 GC
分代年龄等信息。这些信息存放在对象头中。另外，根据虚拟机当前运行状态的不同，如是否启用偏向锁等，对象头会有不同的设置方式。

### 4.5 实例构造器初始化

略

### 4.6 对象的内存布局

对象在对中的存储布局主要分为三部分，对象头、实例数据、对齐填充

![1686110501_64800125a85506321e004.png!small?1686110502920](https://image.3001.net/images/20230607/1686110501_64800125a85506321e004.png!small?1686110502920)

对象头：

主要两类：其主要包括两部分数据：Mark Word、Class 对象指针。特别地对于数组对象而言，其还包括了数组长度数据。在 64 位的 HotSpot
虚拟机下，Mark Word 占 8 个字节，其记录了 Hash Code、GC 信息、锁信息等相关信息；而 Class 对象指针则指向该实例的 Class
对象。

![1686110507_6480012b7871b4e7a1f55.png!small?1686110508313](https://image.3001.net/images/20230607/1686110507_6480012b7871b4e7a1f55.png!small?1686110508313)

HotSpot 对象头

实例数据：对象定义的实例变量，这部分数据存储受到虚拟机分配策略参数 (-XX:FieldsAllocationStype)
和字段定义的顺序影响。HotSpot 默认分配的策略是将相同宽度字段一起存放，父类的变量会出现在子类变量之前。

对齐填充:jvm 存储任何大小必须是 8 个字节的整数倍，不够补齐。这个和类二级制字节流一致。下面是个无锁状态的对象实例化后的数据结构，使用 jol
工具打印出的实例布局如下

![1686110519_64800137e1fa14e09af63.png!small?1686110520613](https://image.3001.net/images/20230607/1686110519_64800137e1fa14e09af63.png!small?1686110520613)

## 5 对象的访问

![1686110528_64800140444f152a15c72.png!small?1686110529003](https://image.3001.net/images/20230607/1686110528_64800140444f152a15c72.png!small?1686110529003)

### 5.1 句柄访问

Java 堆中将会划分出一块内存来作为句柄池，reference 中 存储的就是对象

的句柄地址，而句柄中包含了对象实例数据与类型数据各自的具体地址信 息

### 5.2 直接访问

直接访问是 reference 中直接存储的实例对象的地址，实例对象中包含了类对象的访问指针，也就是如果访问类对象需要多一层引用

优缺点

这两种对象访问方式各有优势，使用句柄来访问的最大好处就是 reference
中存储的是稳定的句柄地址，在对象被移动（垃圾收集时移动对象是非常普遍的行为）时只会改变句柄中的实例数据指针，而 reference 本身不需要修改。
使用直接指针访问方式的最大好处就是速度更快，它节省了一次指针定位的时间开销， 由于对象的访问在 Java
中非常频繁，因此这类开销积少成多后也是一项非常可观的执行成本。就本书讨论的主要虚拟机 Sun HotSpot
而言，它是使用第二种方式进行对象访问的，但从整个软件开发的范围来看，各种语言和框架使用句柄来访问的情况也十分常见

## 6 虚拟机字节码执行引擎

### 6.1 运行时栈帧结构

1\. 局部变量表：在 class 文件被编译时，就已知某个方法的局部变量槽有几个，主要存放方法参数和方法内部定义的局部变量

2\. 操作数栈：和局部变量表相似，编译时就明确了操作数栈的深度

3\. 动态链接：大部分类在类加载解析过程中，会将符号引用转为直接引用，也就是在类加载阶段清楚调用哪个类的哪个方法 (这些方法调用参考字节码指令简介中
invoke * 指令)，但是有一部分必须在运行期间才能确定目标的方法的直接引用。

4\. 方法返回地址

### 6.2 方法调用

1\. 解析：在内解析阶段，会将符号引用转换为直接引用，这种在解析阶段就能确定的调用方法版本称为解析，比如 invokesatic
invokespecial invokevirtual 等等指令指示的方法调用

2\. 静态分派：方法的重载，虚拟机需要根据方法的入参个数和类型方能定位到某个具体方法，发生在编译阶段，故也属于一种解析方式

3\. 重载方法匹配优先级：方法重载过程中，涉及方法的入参和个数，而入参存在自动类型转换，比如重载方法入参为 char 类型，如果不存在入参为 char
类型的方法匹配，则 char 进行自动类型转换为 int 类型，在最终匹配了 Int 入参类型的方法。 **方法重载的本质**

4\. 动态分配：如下图所示，man 和 women 和重新 man 引用指向 women 然后方法调用 sayHello，此时字节码显示的符号引用都是
Human#sayHello，但是实际执行结果和指令码不一致，这是因为 invokevirtual 指令，在指令调用之前都会 aload_x
来加载实际的数据类型， **这就是方法重写的本质**

![1686110535_64800147dc7a20ff117f4.png!small?1686110536555](https://image.3001.net/images/20230607/1686110535_64800147dc7a20ff117f4.png!small?1686110536555)

5.invokedynamic 指令：为了解决其他 invok * 指令方法分配规则完全固化在虚拟机中的问题，jvm
支持设计者更高的灵活度，将动态调用可以以 api 的方式直接使用。参考 java.lang.invoke 包的使用方式。

### 6.3 基于栈的字节码解释执行引擎

jvm 是基于栈的指令集合，这种指令自身不带参数，使用操作数栈的输入输出作为指令本身的参数。物理机一般是基于寄存器的指令集，指令本身携带参数并存放在寄存器。

下面是一个基于栈来展示在虚拟机中字节码是如何执行的。

![1686110543_6480014f2c18fcf061e2f.png!small?1686110543782](https://image.3001.net/images/20230607/1686110543_6480014f2c18fcf061e2f.png!small?1686110543782)

以上字节码执行过程如下

![1686110556_6480015cd36e5cf8028ec.png!small?1686110557418](https://image.3001.net/images/20230607/1686110556_6480015cd36e5cf8028ec.png!small?1686110557418)

## 7 容易混淆点

### 7.1 文件常量池

类加载后，类的域字段、方法和类描述信息会加载到元数据区，既属于类的静态常量池

### 7.2 运行时常量池

我们上面说的 class 文件中的常量池，它会在类加载后进入方法区中的运行时常量池。并非只有 Class
定义的文件常量合并处理后放入运行时常量池，在运行期间也可以将新的常量放入池中，比如 String 类的 intern 方法

![1686110568_64800168c51c75f14a084.png!small?1686110569177](https://image.3001.net/images/20230607/1686110568_64800168c51c75f14a084.png!small?1686110569177)

### 7.3 字符串常量池

字符串常量池存放在堆内存 (>=1.8) 中，堆里边的字符串常量池存放的是字符串的引用或者字符串 (两者都有)，如下图描述字符串创建的堆分布

![1686110578_648001726675ee8e22321.png!small?1686110578876](https://image.3001.net/images/20230607/1686110578_648001726675ee8e22321.png!small?1686110578876)

上图说明：

 **引用初始化** 初始化 s、s2 是先看常量池，有就返回对象引用，否则创建 abc 对象，然后创建 s1/s2Ref 常量引用返回

 **字符串相加** ：先创建 StringBuilder 对象，然后 apend 字符串 a、apend 字符串 b 然后 toString (new
方法) 生成字符串 ab 对象并在字符串常量池生成引用返回，为什么不要字符串相加，就是因为会生成大量 StringBuilder 对象

    
    
    String s = "a"+"b";//返回的是常量池的ab字符串的引用
    String s1 ="ab";
    System.out.println(s == s1);//因两个最终都指向字符串常量池，所以为true
    

**new 字符串** 相当于堆创建两个对象，一个 String 对象，然后创建字符串堆存储，然后 String 对象引用到字符串的堆存储，

    
    
    String s1 ="a";
    String s = new String ("a").intern();//强制生成字符串常量池引用
    System.out.println(s == s1);//返回true
    
    
    
    String s1 ="a";
    String s = new String ("a");
    System.out.println(s == s1);//返回false
    

## 8 附件

jvm 常量池类型和结构体定义

![1686110590_6480017e8ef6514958aef.png!small?1686110591714](https://image.3001.net/images/20230607/1686110590_6480017e8ef6514958aef.png!small?1686110591714)

常量池类型

![1686110642_648001b216df5eea65048.png!small?1686110643533](https://image.3001.net/images/20230607/1686110642_648001b216df5eea65048.png!small?1686110643533)

常量池类型结构定义

![1686110620_6480019c24fd1236a8880.png!small?1686110620718](https://image.3001.net/images/20230607/1686110620_6480019c24fd1236a8880.png!small?1686110620718)

常见的属性类型

![1686110649_648001b917df4823759b0.png!small?1686110649497](https://image.3001.net/images/20230607/1686110649_648001b917df4823759b0.png!small?1686110649497)

jdk 版本好 class 字节版本号对应关系

![1686110663_648001c7f3929c8a9d599.png!small?1686110664804](https://image.3001.net/images/20230607/1686110663_648001c7f3929c8a9d599.png!small?1686110664804)

属性表类型

> 作者：京东物流 王北永
>
> 来源：京东云开发者社区


Java虚拟机系列——检视阅读（二）

[ 卡斯特梅的雨伞](https://www.jianshu.com/u/6c58780a1a14)关注赞赏支持

# Java虚拟机系列——检视阅读（二）

#  **类索引,父类索引,接口索引集合** ——确定这个类的继承关系

**类索引(this_class)和父类索引(super_class)都是u2类型的数据，而接口索引(interfaces)是一组u2类型的数据集合，class文件中由这三项数据来确定这个类的继承关系**
。 **类索引用于确定这个类的全限定名，父类索引用于确定这个类的父类的全限定名。**
由于Java语言不允许多继承，所以父类索引只有一个，除了java.lang.Object之外，所有的Java类都有父类，因了除了java.lang.Object之外，所有Java类的父类索引都不为0。
**接口索引集合用来描述这个实现实现了哪些接口** ，这些被实现的接口将按照implements语句后的接口顺序从左到右排列在接口的索引集合中。

**类索引，父类索引和接口索引集合都按顺序排列在访问标志之后**
，类索引和父类索引用两个u2类型的索引值表示，它们各自指向一个类型为CONSTANT_Class_info的类描述符常量，通过CONSTANT_Class_info类型的常量中的索引可以找到定义在CONSTANT_Utf8_info类型的常量中的全限定名称字符串。
**对于接口索引集合，入口的第一项为u2类型的数据，表示接口计数器** (interfaces_count)， **表示索引表的容量**
。如果该类没有实现任何接口，那么该计数器值为0，后面接口的索引表不再占用任何字节。

# **字段表集合**

**字段表(field_info)用于描述接口或类中声明的变量。** 字段(field)包括了类级变量或实例变量，但不包括方法内部声明的变量。
**描述一个字段的信息有：字段的作用域(public,private,protected修饰符)，是类级变量还是实例级变量(static修饰符)，可变性(final)，并发可见性(volatile修饰符，是否强制从主内存读写)，是否可序列化(transient修饰符)，字段数据类型(基本数据类型，对象，数组)，字段名称。**
这些信息中，各个修改符都是布尔值，要么有某个修饰符，要么没有，很适合使用标志位来表示。而
**字段叫什么名字，字段被定义为什么数据类型，这些都是无法固定的，只能引用常量池中的常量来描述。** 下面是 **字段表的最终格式** 。

image

**字段修饰符放在access_flags项目中**
，它与类的access_flags项目是非常相似的，都是一个u2的数据类型，其中可以设置的标志位和含义如下表：

image

跟随access_flags标志的是两项索引值：
**name_index和descriptor_index。它们都是对常量池的引用，分别代表着字段的简单名称及字段的描述符**
。现在需要解释一下“简单名称”，“描述符”及前面出现过多次的“全限定名”这三种特殊字符串的概念。全限定名称和简单名称很好理解，如
**“org/fenixsoft/clazz/TestClass"就是一个类全限定名**
，仅仅是把类名中的”.“替换成了”/“而已，为了使连续的多个全限定名之间不产生混淆，在使用时最后一般会加上一个“;”号表示全限定名结束。
**简单名称就是指没有类型和参数修饰的方法或字段名称** 。相对于全限定名和简单名称来说，方法和字段的描述符就要复杂一些。
**描述符的作用是来用描述字段的数据类型，方法的参数列表(包括数量，类型及顺序)和返回值。**
根据描述符规则，基本数据类型(byte,char,double,float,int,long,short,boolean)及代表无返回值的void类型都使用一个大写字符来表示，而
**对象类型则用字符L加对象全限定名来表示** ，如下图：

image

**对于数组类型，每一维度使用一个前置的 [ 字符来描述** ，如一定义为
**java.lang.String[](#)类型的二维数组，将被记录为：“[[java/lang/String;”**
，一个整型数组“int[]”将被记录为“[I”。用 **描述符来描述方法时，按照先参数列表，后返回值的顺序描述**
，参数列表按照参数的严格顺序在一组小括号“()”之内。如方法void int()描述符为：”()V“， **方法java.lang.String
toString()描述符为：“()java/lang/String;”**
字段表都包含的固定数据项目到descriptor_index为止就结束了，但是在descriptor_index之后跟随着一个属性表集合用于存储一些额外的信息，
**字段都可以在属性表中描述0至多项额外的信息** 。字段表集合中不会列出超类或父接口中继承而来的字段，但有可能列出原来Java代码中不存在的字段，譬如在
**内部类中为了保持对外部类的访问性，会自动添加指向外部类实例的字段。** 另外，
**在Java语言中字段是无法重载的，两个字段的数据类型，修饰符不管是否相同，都必须使用不一样的名称（即名称必须不同，编译器限制）**
，但是对于字节码来讲，如果两个字段的描述符不一致，那字段重名就是合法的（即只有描述符不同就是合法的）。

##### 疑问：

Q: 字段(field)包括了类级变量或实例变量，但不包括方法内部声明的变量。类级变量是指static修饰的变量么？

A:
是的。描述一个字段的信息有：字段的作用域(public,private,protected修饰符)，是类级变量还是实例级变量(static修饰符)，可变性(final)，并发可见性(volatile修饰符，是否强制从主内存读写)，是否可序列化(transient修饰符)，字段数据类型(基本数据类型，对象，数组)，字段名称。

# **方法表集合**

**方法表的结构与字段表一样，依次包含了访问标志(access_flags)，名称索引(name_index)，描述符索引(descriptor_index)，属性表集合(attributes)几项**
，如下表所示：

image

因为volatile关键字和transient关键字不能修改方法，所以方法表的访问标志中没有了ACC_VOLATILE与ACC_TRANSIENT标志。与之相对的，synchronized,
native,
strictfp和abstract关键字可以修饰方法，所以方法表的访问标志中增加了ACC_SYNCHRONIZED，ACC_NATIVE，ACC_STRICTFP，ACC_ABSTRACT标志。对于方法表，所有标志位及取值如下表：

image

**方法里面的Java代码，经过编译器编译成字节码指令后，存放在方法属性表集合中一个名为“Code”的属性表中**
，属性表是class文件格式中最具扩展性的一种数据项目。

与字段表集合相对应的， **如果父类方法在子类中没有被重写(Override)，方法表集合中就不会出现父类的方法**
。但同样的，可能**会出现由编译器自动添加的方法，最典型的便是类构造器“<client>”方法和缺省实例构造器“<init>”方法。

在Java语言中，要重载(Overload)一个方法，
**除了要与原方法具有相同的简单名称之外，还要求必须拥有一个与原方法不同的特征签名，特征签名是一个方法中各个参数在常量池中的字段符号引用的集合**
，也就是因为 **返回值不会包在特征签名之中** ，因此Java语言里是无法仅仅依靠返回值的不同来对一个已有的方法进行重载的。

对于JVM的Class文件格式中，特征签名的范围更大一些，只要描述符不是完全一致的两个方法就可以共存。也就是说，
**如果两个方法有相同的名称和特征签名，但返回值不同，那么也是可以合法共存于同一个class文件中** 。

##### 疑问：

Q: 如果是默认没有访问范围修饰符的方法,如下，这方法访问标志里的值是什么样的呢？

<pre class="md-fences md-end-block" lang="" contenteditable="false" cid="n660"
mdtype="fences" style="box-sizing: border-box; overflow: visible; font-family:
Consolas, "Liberation Mono", Courier, monospace; font-size: 0.9em; white-
space: pre; text-align: left; break-inside: avoid; display: block; background-
image: inherit; background-position: inherit; background-size: inherit;
background-repeat: inherit; background-attachment: inherit; background-origin:
inherit; background-clip: inherit; background-color: rgb(248, 248, 248);
position: relative !important; border: 1px solid rgb(221, 221, 221); border-
radius: 3px; padding: 8px 1em 6px; margin-bottom: 15px; margin-top: 15px;
width: inherit; color: rgb(51, 51, 51); font-style: normal; font-variant-
ligatures: normal; font-variant-caps: normal; font-weight: normal; letter-
spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows:
2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style:
initial; text-decoration-color: initial;">  
void test(){  
/...  
}</pre>

#  **属性表集合** ——不理解

> 讲解得并不是很好，待翻看深入理解java虚拟机的书看，还有看看R大关于这方面的讲解，感觉书上说的也不是很好，每次看到这边都不是很理解

在Class文件，字段表，方法表中都可以携带自己的属性表集合，以用于描述某些场景专有的信息。与Class文件中其它的数据项目要求的顺序、长度和内容不同，属性表集合的限制稍微宽松一些，不再要求各个属性表具有严格的顺序，并且只要不与已有的属性名重复，任何人实现的编译器都可以向属性表中写入自己定义的属性信息，Java虚拟机运行时会忽略掉它不认识的属性。为了能正确地解析Class文件，《Java虚拟机规范(第二版)》中预定义了9种虚拟机实现应当能识别的属性，具体如下表所示：

image

对于每个属性，它的名称需要从常量池中引用一个CONSTANT_Utf8_info类型的常量表来表示，而属性值的结构则是完全自定义的，只要说明属性值所占用的位数长度即可。一个符合规则的属性表应该满足如下表定义的结构：

image

## 1.Code属性

Java程序方法体里的代码经过Javac编译器处理之后，最终变为字节码指令存储在Code属性内。Code属性出现在方法表的属性集合中，但并非所有方法都必须存在这个属性表，譬如接口或抽象类中的抽象方法就不存在Code属性，如果方法有Code属性表存在，那么它的结构如下表：

image

attribute_name_index是一项指向CONSTANT_Utf8_info常量表的索引，常量值固定为“Code”，它代表了该属性的属性名称，attribute_length指示了属性值的长度，由于属性名称索引与属性长度一共是6个字节，所以属性值的长度固定为整个属性表的长度减去6个字节。max_stack代表了操作数栈(Operand
Stacks)的最大深度。在方法执行的任意时刻，操作数栈都不会超过这个深度。虚拟机运行的时候需要根据这个值来分配栈帧(Frame)中的操作数栈深度。max_locals代表了局部变量表所需的存储空间。在这里，max_locals的单位是Slot，Slot是虚拟机为局部变量表分配内存所使用的最小单位。对于byte,char,float,int,shot,boolean,reference和returnAddress等长度不超过32位的数据类型，每个局部变量占1个Slot，而double与long这两种64位的数据类型而需要2个Slot来存放。方法参数(包括实例方法中的隐藏参数“this”)，显示异常处理器的参数(Exception
Handler Parameter,即try-
catch语句中catch块所定义的异常)，方法体中定义的局部变量都需要使用局部表来存放。另外，并不是在方法中使用了多个局部变量，就把这些局部变量所占的Slot之和作为max_locals的值，原因是局部变量表中的Slot可以重用，当代码执行超出一个局部变量的作用域时，这个局部变量所在的Slot就可以被其他局部变量所使用，编译器会根据变量的作用域来分类Slot并分配给各个变量使用，然后计算出max_locals的大小。

code_length和code用来存储Java源程序编译后生成的字节码指令。code_length代表字节码长度，code是用于存储字节码指令的一系列字节流。既然名为字节码指令，那么每个指令就是一个u1类型的单字节，当虚拟机读取到code中的一个字节码时，就可相应地找出这个字节码代表的是什么指令，并且可以知道这条指令后面是否需要跟随参数，以及参数应该如何理解。关于code_length还有一件值得注意的事情，虽然它是一个u4类型的长度值，理论上最大值可以达到2的32次方减1，但虚拟机规范中限制了一个方法不允许超过65535条字节码指令（64KB），如果超过这个限制，Javac编译器就会拒绝编译。一般来讲，只要我们写Java代码时不是刻意地编写超长的方法，就不会超过这个最大值限制。但是，在编译复杂的JSP文件中，可以会因为这个原因导致编译失败。Code属性是Class文件中最重要的一个属性，如果把一个Java程序中的信息分为代码(Code，方法体里的Java代码)和元数据(Metadata，包括类、字段、方法定义及其它信息)两部分，那么在整个Class文件里，Code属性用于描述代码，其它的所有数据项目就都用于描述元数据。在字节码指令之后的是这个方法的显示异常处理表，异常表对于Code属性表来说不是必须存在的。异常表的格式如下表：

image

异常表它包含4个字段，这些字段的含义为：如果字节码从第start_pc到end_pc行之间(不包含第end_pc)行出现了类型为catch_type或其子类的异常(catch_type为指向一个CONSTANT_Class_info型常量的索引)，则转到第handler_pc行继续处理。当catch_type的值为0时，代表任何的异常情况都需要转向到handler_pc行行进行处理。异常表实际上是Java代码的一部分，编译器使用异常表而不是简单的跳转命令来实现Java异常及finally处理机制。注：字节码的“行”是一种形象的描述，指的是字节码相对于方法体开始的偏移量，而不是Java源代码的行号。

## 2.Exceptions属性

这里的Exceptions属性是在方法表中与Code属性平级的一项属性，而不是Code属性表中的异常属性表。Exceptions属性表的作是列举出方法中可能抛出的受查检异常(Checked
Exception)，也就是在方法描述时在throws关键字后面列举的异常。它的结构如下表：

image

此属性表中的number_of_exceptions项表示访求可能抛出number_of_exceptions种受检查异常，每一种受检查异常使用一个exception_index_table项表示，attribute_name_index为指向常量池中CONSTANT_Class_info型常量表的索引，代表了该受检查异常的类型。

## 3.LineNumberTable属性

LineNumberTable属性用于描述Java源代码行号与字节码行号(字节码偏移量)之间的对应关系。它并不是运行时必须的属性，但默认会生成到Class文件之中，可以在Javac中使用-g:none或-g:lines选项来取消或要求生成这项信息。如果选择不生成LineNumberTable属性表，对程序运行产生的最主要的影响就是在抛出异常时，堆栈中将不会显示出错的行号，并且在调试程序的时候无法按照源码来设置断点。LineNumberTable属性表结构如下表：

image

line_number_table是一个数量为line_number_table_length，类型为line_number_info的集合，line_number_info表包括了start_pc和line_number两个u2类型的数据项，前者是字节码行号，后者是Java源码行号。

## 4.LocalVariableTable属性

LocalVariableTable属性表用于描述栈帧中局部变量表中的变量与Java源码中定义的变量之间的关系，它不是运行时必须的属性，默认也不会生成到Class文件之中，可以使用-g:none或-g:vars选项来取消或要求生成这项信息。如果没有生成这项属性，最大的影响就是当其它人引用这个方法时，所有参数名称都丢失，IDE可能会使用诸如arg0、arg1之类的占位符来替换原有的参数名称，这对程序运行没有影响，但是会给代码编写带来较大的不便，而且在调试期间无法根据参数名称从运行上下文件中获取参数值。LocalVariableTable属性表结构如下：

image

其中local_variable_info项目代表了一个栈帧与源码中的局部变量的关联，结构如下：

image

index是这个局部变量在栈帧局部变量表中的Slot位置。当这个变量的数据类型是64位时(double和long)，它占用的Slot为index和index+1两个位置。在JDK1.5引入了泛型之后，LocalVariableTable属性增加了一个“姐妹”属性：LocalVaiableTypeTable，这个新增加的属性结构与LocalVariableTable属性非常相似，仅仅是把记录字段描述符的descript_index替换成了字段的特征签名(Singnature)，对于非泛型类型来说，描述符的参数化类型被擦除掉了，描述符就不能准确地描述泛型类型了，因此出现了LocalVariableTypeTable属性。

## 5.SourceFile属性

SourceFile属性用于记录这生成这个Class文件的源码文件名称。这个属性也是可选的，可以使用-g:none或-g:source选项来取消或要求生成这项信息。在Java中，对于大多数的类来说，类名和文件是一致的，但有一些特殊情况(如内部类)例外。如果不生成这项属性，当招聘异常时，堆栈中半不会显示出错误代码所属性文件名。这个属性是一个室长的属性，结构如下：

image

sourcefile_index数据项是指向常量池中CONSTANT_Utf8_info型常量的索引，常量值是源文件的文件名。

## 6.ConstantValue属性

ConstantValue属性的作用是通知虚拟机自动为静态变量赋值。只有被static关键字修饰的变量才可以使用这项属性。在Java程序里类类似“int x
= 123“和”static int x =
123”这样的变量定义非常常见，但虚拟机对这两种变量赋值的方法和时刻有所不同。对于非static类型的变量(也就是实例变量)的赋值是在实例构造器方法中进行的；对于类变量，则有两种式可以选择：赋值在类构造器方法中进行，或者使用ConstantValue属性来赋值。目前Sun
Javac编译器的选择是：如果同时使用final和static来修改一个变量，并且这个变量的数据类型是基本类型或java.lang.String的话，就生成ConstantValue属性来进行初始化，如果这个变量没有被final修饰，或者并非基本类型或字符串，则选择在类构造器中进行初始化。ConstantValue属性表结构如下：

image

ConstantValue属性是一个定长属性，它的attribute_length数据项值必须为2。constantvalue_index数据项代表了常量池中一个字面常量的引用，根据字段类型不同，字面量可以是CONSTANT_Long_info,CONSTANT_Float_info,CONSTANT_Double_info,CONSTANT_Integer_info和CONSTANT_String_info常量中的一种。

## 7.InnerClasses属性

InnerClasses属性表用于记录内部类与宿主类之间的关联。如果一个类中定义了内部类，那么编译器将会为它及它所包含的内部类生成InnerClasses属性表。表结构如下：

image

数据项number_of_classes代表需要记录多少个内部类信息，每一个内部类的类的信息都由一个inner_class_info表进行描述。inner_class_info表结构如下：

image

inner_class_info_index和outer_class_info_index都是指向常量池中CONSTANT_Class_infon常量的索引，分别代表了内部类和宿主类的符号引用。inner_name_index是指向常量池中CONSTANT_Utf8_info型常量的索引，代表这个内部类的名称，如果是匿名内部类，则这项值为0。inner_class_access_flags是内部类的访问标志，类型于类的access_flags，它的取值范围如下表：

image

## 8.Deprecated及Synthetic属性

Deprecated及Synthetic属性都属性于标志类型的布尔值属性，只存在有和没有的区别，没有属性值的概念。Deprecated属性用于表示某个类，字段或方法，已经被程序作者定为不再推荐使用，它可以通过代码中使用@Deprecated注解进行设置。Synthetic属代表此字段或方法并不是由Java源码直接产生的，而是由编译器自行添加的，在JDK1.5之后，标识一个类，字段或方法是编译器自动产生的，也可以设置它们访问标志中的ACC_SYNTHETIC标志位，其中最典型的就是Bridge
Method。所有非用户代码生产的类，方法及字段都应当至少设置Synthetic属性和ACC_SYNTHETIC标志位中的一项，唯一的例外是实例构造器“”方法和类构造器“<clinit”方法。

Deprecated及Synthetic属性表结构如下：

image

其中attribute_length数据项的值必须为0，因为没有任何属性值需要设置。

在JDK1.5和JDK1.6中一共增加了10项属性，具体如下：

image

# **引用类型和对象是否死亡**

在JDK1.2以前， **Java中的引用定义得很传统：如果reference类型的数值代表的是另外一块内存的起始地址，就称这块内存代表着一个引用。**
这种定义很纯粹，但太过狭隘，一个对象 **在这种定义下只有被引用或者没有引用两种状态** ，对于如何描述一个“食之无味，弃之可惜”的对象就显得无能为力；
**如果内存在进行垃圾收集后还是非常紧张，则可以抛弃这些对象。很多系统的缓存功能都符合这样的应用场景。**
在JDK1.2之后，Java对引用的概念进行了扩充，将 **引用分为强引用(Strong Reference)，软引用(Soft
Reference)，弱引用(Weak Reference)，虚引用(Phantom Reference)四种，这四种引用强度依赖逐渐减弱。**

1. **强引用就是指在程序代码之中普遍存在的，类似“Object obj = new Object()”这类引用，只要强引用存在，垃圾收集器永远不会回收掉被引用的对象** 。

2. **软引用用来描述一些还有用，但并非必须的对象。对于软引用关联着的对象，在系统将要发生内存溢出之前，将会把这些对象列进回收范围之中，并进行第二次回收** 。如果这次回收还是没有足够的内存，才会抛出内存溢出错误。在JDK1.2之后，提供了SoftReference来实现软引用。

3.弱引用也是用来描述非必须对象的，但是它的强度比软引用更弱一点，
**被弱引用关联的对象只能生存到下一次垃圾回收之前。当垃圾收集器工作时，无论当前内存是否足够，都会回收掉被弱引用关联的对象**
。在JDK1.2之后，提供了WeakReference来实现弱引用。

4.虚引用它是最弱的一种引用关系。
**一个对象是否有虚引用存在，完全不会对其生存时间构成影响，也无法通过虚引用来取得一个对象的实例。为一个对象设置虚引用关联的唯一目的是希望能在这个对象被收集器回收时收到一个系统通知。**
在JDK1.2之后，提供了PhantomReference来实现虚引用。

在根搜索算法中不可达的对象，也并非是“非死不可的”，这时候它们暂时处于“缓刑”阶段，
**要真正宣告一个对象死亡，至少要经历两次标记过程：如果对象在进行根搜索后发现没有与GC Roots相连接的引用链，那它将会被第一次标记并进行一次筛选**
， **筛选的条件是此对象是否有必要执行finalize()方法** 。当对象
**没有覆盖finallize()方法或该对象的finalize()已经被调用过，虚拟机将这两种情况都视为“没有必要执行”。** 如果一个对象被判断为
**有必要执行finalize()方法，那么这个对象将会被放置在一个名为F-Queue的队列之中** ，并在稍后
**由一条虚拟机自动建立的，低优先级的Finalizer线程去执行。** 这里所谓的“执行”是指 **虚拟机会触发这个方法，但并不承诺会等待它运行结束**
。这样做的原因是，如果一个对象在fianlize()方法中 **执行缓慢，或者发生了死循环** ，将很可能会导致F-
Queue队列中的其它对象永久处于等待状态，甚至 **导致整个内存回收系统崩溃**
。finalize()方法是对象逃脱死亡命运的最后一次机会，稍后GC将对F-Queue中的对象进行第二次小规模的标记，如果
**对象在finalize()中成功拯救自己--只要重新与引用链上的任何一个对象建立关联既可**
，那在第二次标记时它将被移出“即将回收”集合；如果对象这时候还没有逃脱，那它就将被回收了。

# **类加载时机**

**类从被加载到虚拟机内存中开始，到缷载出内存为止，它的整个生命周期为：加载(Loading)，验证(Verification)，准备(Preparation)，解析(Resolution)，初始化(Initialization)，使用(Using)，缷载(Unloading)七个阶段。其中验证，准备，解析三个阶段统称为连接(Linking)阶段**
，这七个阶段的发生顺序如下图：

image

**`加载，验证，准备，初始化和缷载`这五个阶段的顺序是确定的**，类的加载过程必须按照这种顺序按部就班地开始，而
**解析阶段则不一定：在某些情况下可以在初始化阶段之后再开始，这是为了支持Java语言的运行时绑定** 。注意这里写的是按部就班地“开始”（
**意思是保证开始的顺序是确定的**
，但各个阶段间是互相交叉地混合式进行的，所以只能是开始的顺序是确定的），而不是按部就班地“进行”或“完成”，因为这些阶段通常都是互相交叉地混合式进行的，通常会在一个阶段执行的过程调用或激活另外一个阶段。

在什么情况下需要开始类的加载过程的第一个阶段：加载。虚拟机规范中并没有进行强制约束。但是对于初始化阶段，
**虚拟机规范则是严格规定了`有且只有`四种情况必须立即对类进行“初始化**”(而加载，验证，准备阶段自然需要在此之前开始):

  1. **遇到new,getstatic,putstatic或invokestatic这4条字节码指令时** ，如果类没有进行过初始化，则需要先触发其初始化。生成这4条指令最常见的Java代码场景是：使用new关键字实例化对象的时候，读取或设置一个类的静态字段（被final修饰、已在编译期把结果放入常量池的静态字段除外）的时候，以及调用一个类的静态方法的时候。

  2. **使用java.lang.reflect包的方法对类进行反射调用的时候** ，如果类没有进行过初始化，则需要先触发其初始化。

  3. **当初始化一个类的时候，如果发现其父类还没有进行过初始化** ，则需要先触发其父类的初始化。

  4. 当虚拟机启动时，用户需要指定一个要执行的主类( **包含main()方法的那个类** )，虚拟机会先初始化这个主类。

对于这四种会触发类进行初始化的场景，
**虚拟机规范中使用了一个很强烈的限定语：“有且只有”，这四种场景中的行为称为对一个类的主动引用。除此之外所有引用类的方法，都不会触发初始化，称为被动引用**
。下面是三个被动引用的例子：

**a.通过子类引用父类中的静态字段，不会初始化子类**

<pre class="md-fences md-end-block" lang="java" contenteditable="false"
cid="n808" mdtype="fences" style="box-sizing: border-box; overflow: visible;
font-family: Consolas, "Liberation Mono", Courier, monospace; font-size:
0.9em; white-space: pre; text-align: left; break-inside: avoid; display:
block; background-image: inherit; background-position: inherit; background-
size: inherit; background-repeat: inherit; background-attachment: inherit;
background-origin: inherit; background-clip: inherit; background-color:
rgb(248, 248, 248); position: relative !important; border: 1px solid rgb(221,
221, 221); border-radius: 3px; padding: 8px 1em 6px; margin-bottom: 15px;
margin-top: 15px; width: inherit; color: rgb(51, 51, 51); font-style: normal;
font-variant-ligatures: normal; font-variant-caps: normal; font-weight:
normal; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform:
none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-
decoration-style: initial; text-decoration-color: initial;">  
package com.xtayfjpk.jvm.chapter7;  
​  
/**

  * 被动使用类字段演示一：
  * 通过子类引用父类的静态字段，不会导致子类初始化
  * @author zj
  * 

*/  
public class SuperClass {  
public static int value = 123;  
​  
static {  
System.out.println("SuperClass Init");  
}  
}</pre>

<pre class="md-fences md-end-block" lang="java" contenteditable="false"
cid="n809" mdtype="fences" style="box-sizing: border-box; overflow: visible;
font-family: Consolas, "Liberation Mono", Courier, monospace; font-size:
0.9em; white-space: pre; text-align: left; break-inside: avoid; display:
block; background-image: inherit; background-position: inherit; background-
size: inherit; background-repeat: inherit; background-attachment: inherit;
background-origin: inherit; background-clip: inherit; background-color:
rgb(248, 248, 248); position: relative !important; border: 1px solid rgb(221,
221, 221); border-radius: 3px; padding: 8px 1em 6px; margin-bottom: 15px;
margin-top: 15px; width: inherit; color: rgb(51, 51, 51); font-style: normal;
font-variant-ligatures: normal; font-variant-caps: normal; font-weight:
normal; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform:
none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-
decoration-style: initial; text-decoration-color: initial;">  
package com.xtayfjpk.jvm.chapter7;  
​  
public class SubClass extends SuperClass {  
​  
static {  
System.out.println("SubClass Init");  
}  
}</pre>

<pre class="md-fences md-end-block" lang="java" contenteditable="false"
cid="n810" mdtype="fences" style="box-sizing: border-box; overflow: visible;
font-family: Consolas, "Liberation Mono", Courier, monospace; font-size:
0.9em; white-space: pre; text-align: left; break-inside: avoid; display:
block; background-image: inherit; background-position: inherit; background-
size: inherit; background-repeat: inherit; background-attachment: inherit;
background-origin: inherit; background-clip: inherit; background-color:
rgb(248, 248, 248); position: relative !important; border: 1px solid rgb(221,
221, 221); border-radius: 3px; padding: 8px 1em 6px; margin-bottom: 15px;
margin-top: 15px; width: inherit; color: rgb(51, 51, 51); font-style: normal;
font-variant-ligatures: normal; font-variant-caps: normal; font-weight:
normal; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform:
none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-
decoration-style: initial; text-decoration-color: initial;">  
package com.xtayfjpk.jvm.chapter7;  
​  
public class NotInitialization {  
​  
/**

  * @param args  
*/  
public static void main(String[] args) {  
//通过子类引用父类的静态字段，不会导致子类初始化  
System.out.println(SubClass.value);  
}  
​  
}</pre>

上述代码运行之后，只会输出“SuperClass init!”，而不会输出“SubClass init!”。
**对于静态字段，只有直接定义这个字段的类才会初始化，因此通过子类来引用父类中的静态字段，只会触发父类初始化而不不会触发子类的初始化。** 至于
**是否要触发子类的加载和验证，在虚拟机规范中并没有规定，这点取决于虚拟机的具体实现** 。对于Sun HotSpot虚拟机来说，可以通过-
XX:+TraceClassLoading参数看到此操作是否会导致子类的加载(事实上SubClass被加载了)。

**b.通过定义数组来引用类，不会触发此类的初始化**

<pre class="md-fences md-end-block" lang="java" contenteditable="false"
cid="n815" mdtype="fences" style="box-sizing: border-box; overflow: visible;
font-family: Consolas, "Liberation Mono", Courier, monospace; font-size:
0.9em; white-space: pre; text-align: left; break-inside: avoid; display:
block; background-image: inherit; background-position: inherit; background-
size: inherit; background-repeat: inherit; background-attachment: inherit;
background-origin: inherit; background-clip: inherit; background-color:
rgb(248, 248, 248); position: relative !important; border: 1px solid rgb(221,
221, 221); border-radius: 3px; padding: 8px 1em 6px; margin-bottom: 15px;
margin-top: 15px; width: inherit; color: rgb(51, 51, 51); font-style: normal;
font-variant-ligatures: normal; font-variant-caps: normal; font-weight:
normal; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform:
none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-
decoration-style: initial; text-decoration-color: initial;">  
package com.xtayfjpk.jvm.chapter7;  
​  
public class NotInitialization {  
​  
/**

  * @param args  
*/  
public static void main(String[] args) {  
​  
//通过数组定义来引用类，不会触发此类的初始化  
SuperClass[] sca = new SuperClass[10];  
​  
}  
​  
}</pre>

上述代码运行后(SuperClass重用上一例子代码)，并没有输出“SuperClass
init!”，说明并没有触发SuperClass的初始化阶段。但是这段代码触发
**另一个名为“[Lcom.xtayfjpk.jvm.chapter7.SuperClass;”的类的初始化阶段**
，对于用户代码来说，这并不是一个合法的类名称，它是一个由虚拟机自动生成，直接继承于java.lang.Object的子类，
**创建动作由字节码指令newarray触发** 。

**c.引用常量池中的常量，不会触发定义常量类的初始化** （static final修饰的字段）

<pre class="md-fences md-end-block" lang="java" contenteditable="false"
cid="n820" mdtype="fences" style="box-sizing: border-box; overflow: visible;
font-family: Consolas, "Liberation Mono", Courier, monospace; font-size:
0.9em; white-space: pre; text-align: left; break-inside: avoid; display:
block; background-image: inherit; background-position: inherit; background-
size: inherit; background-repeat: inherit; background-attachment: inherit;
background-origin: inherit; background-clip: inherit; background-color:
rgb(248, 248, 248); position: relative !important; border: 1px solid rgb(221,
221, 221); border-radius: 3px; padding: 8px 1em 6px; margin-bottom: 15px;
margin-top: 15px; width: inherit; color: rgb(51, 51, 51); font-style: normal;
font-variant-ligatures: normal; font-variant-caps: normal; font-weight:
normal; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform:
none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-
decoration-style: initial; text-decoration-color: initial;">  
package com.xtayfjpk.jvm.chapter7;  
​  
public class ConstClass {  
​  
public static final String HELLOWORLD = "hello world";  
​  
static {  
System.out.println("ConstClass Inited");  
}  
​  
}</pre>

<pre class="md-fences md-end-block" lang="java" contenteditable="false"
cid="n821" mdtype="fences" style="box-sizing: border-box; overflow: visible;
font-family: Consolas, "Liberation Mono", Courier, monospace; font-size:
0.9em; white-space: pre; text-align: left; break-inside: avoid; display:
block; background-image: inherit; background-position: inherit; background-
size: inherit; background-repeat: inherit; background-attachment: inherit;
background-origin: inherit; background-clip: inherit; background-color:
rgb(248, 248, 248); position: relative !important; border: 1px solid rgb(221,
221, 221); border-radius: 3px; padding: 8px 1em 6px; margin-bottom: 15px;
margin-top: 15px; width: inherit; color: rgb(51, 51, 51); font-style: normal;
font-variant-ligatures: normal; font-variant-caps: normal; font-weight:
normal; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform:
none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-
decoration-style: initial; text-decoration-color: initial;">  
package com.xtayfjpk.jvm.chapter7;  
​  
public class NotInitialization {  
​  
/**

  * @param args  
*/  
public static void main(String[] args) {  
​  
//常量在编译阶段会存入调用类的常量池中，本质上没有直接引用到定义常量的类，不会导致该类初始化  
System.out.println(ConstClass.HELLOWORLD);  
}  
​  
}</pre>

上述代码运行后，也没有输出“ConstClass init!”，这是因为虽然在Java源码中引用了ConstClass类中的常量HELLOWORLD，但是
**编译阶段将此常量值“hello
world”存储到了NotInitialization类的常量池中，对象常量ConstClass.HELLOWORLD的引用实际都转化为NotInitialization类对自身常量池的引用。**
也就是说实际上NotInitialization的Class文件之中并没有ConstClass类的符号引用入口，这两个类在编译成Class之后就不存在任何联系了。

接口的加载过程与类的加载过程稍有一些不同，针对接口需要做一些特殊说明：接口也有初始化过程，这点与类是一致的，上面的代码都是使用静态语句块“static
{}”来输出初始化信息的，而接口中不能有“static
{}”静态语句块，但编译器仍然会为接口生成“”类构造器，用于初始化接口中所定义的成员变量(也是常量)。 **接口与类真正有所区别的是**
前面讲述的四有“有且仅有”需要开始初始化阶段场景中的第三种
**：当一个类在初始化时，要求其父类全都已经初始化过了，但是一个接口在初始化时，并不要求其父接口也全部初始完成了，只有在真正用到父接口的时候(如引用到接口中定义的常量)才会初始化。**

##### 疑问：

Q:
**`加载，验证，准备，初始化和缷载`这五个阶段的顺序是确定的**，类的加载过程必须按照这种顺序按部就班地开始，而解析阶段则不一定：在某些情况下可以在初始化阶段之后再开始，这是为了支持Java语言的运行时绑定。那使用阶段不是确定的么？是指不一定使用？

# **类加载过程**

## 一、加载

“加载”(Loading)阶段是“类加载”(Class Loading)过程的一个阶段。在 **加载阶段，虚拟机需要完成以下三件事情** ：a.
**通过一个类的全限制名来获取定义此类的二进制字节流** 。b. **将这个字节流所代表的静态存储结构转化为方法区的运行时数据结构** 。c.
**在Java堆中生成一个代表这个类的java.lang.Class对象，作为方法区这些数据的访问入口** 。

虚拟机规范的这三点要求实际上并不具体，因此虚拟机实现与具体应用的灵活度相当大。例如“通过一个类的全限制名来获取定义此类的二进制字节流”，并没有指明二进制字节流要从一个Class文件中获取，
**准确地说是根本没有指明要从哪里获取及怎样获取**
。虚拟机设计团队加载阶段搭建了一个相当开放的，广阔的舞台，Java发展历程中，许多举足轻重的Java技术都建立在这一基础上，例如：a.
**从ZIP包中读取，这很常见，最终成为日后JAR,EAR,WAR格式的基础** b. **从网络中获取** ，这种场景最典型的应用就是Appletc.
**运行时计算生成，这种场景使用得最多的就是动态代理技术**
，在java.lang.reflect.Proxy中，就是用了ProxyGenerator.generatProxyClass来为特定接口生成
_$Proxy的代理类的二进制字节流。d._ _由其它文件生成，典型场景：JSP应用_ _。e._ _从数据库中读取_
*，这种场景相对少见些，有些中间件服务器(如SAP Netweaver)可以选择把程序安装到数据库中来完成程序代码在集群间的分发。f. .......

加载阶段与连接阶段的部分内容(如一部分字节码文件格式验证动作)是交叉进行的，加载阶段尚未完成，连接阶段可能已经开始，但这些夹在加载阶段之中进行的动作，仍然属性连接阶段的内容，这两阶段的开始时间仍然保持着固的先后顺序。

## 二、验证

验证是连接阶段的第一步，这一阶段的 **目的是为了确保Class文件的字节流中包含的信息符合当前虚拟机的要求，并且不会危害虚拟机自身的安全。**

尽管验证阶段是非常重要的，并且验证阶段的工作量在虚拟机的类加载子系统中占了很大一部分。如果验证到输入的字节流不符合Class文件的存储格式，就抛出一个java.lang.VerifyError错误或者其子错误。具体应当检查哪些方面，如何检查，何时检查，虚拟机规范都没有明确说明，所以不同的虚拟机对验证的实现可能会有所不同，但大致上都会完成
**四个阶段的验证过程：文件格式验证，元数据验证，字节码验证和符号引用验证** 。

## 三、准备

**准备阶段是正式为类变量分配内存并设置类变量初始值的阶段，这些内存都将在方法区中进行分配**
（注意是类变量即static修饰的字段，不是示例变量）。需要强调的是：
**首先是这时候进行内存分配的仅包括类变量，而不包括实例变量，实例变量将会在对象实例化时随着对象一起分配是Java堆中。其次是这里所说的初始值“通常情况“下是数据类型的零值**
，假设一个类变量定义为：public static int value =
123;那么变量value在准备阶段过后的初始值是0而不是123，因为这时候尚未开始执行任何Java方法，而把value赋值为123的putstatic指令是在程序被编译后，存放于类构造器”<clinit>“方法中的，所以把value赋值为123的动作将在初始化阶段才会被执行。

上面提到的”通常情况“下初始值为零值，但是，如果类字段的字段属性表中存在ConstantValue属性，那在准备阶段变量value就会初始初始化为ConstantValue属性所指定的值，假设上面类变量value被定义为：public
static **final** int value = 123;编译时Javac将会为value生成ConstantValue属性表，
**在准备阶段虚拟会就会根据ConstantValue的设置将value赋值为123。** （静态常量即static final 修饰的字段直接赋值）

## 四、解析

**解析阶段是虚拟机将常量池内的符号引用替换为直接引用的过程**
，在Class文件中它以CONSTANT_Class_info，CONSTANT_Fieldref_info，CONSTANT_Methodref_info等类型的常量出现。直接引用与符号引用的关联是：

a. **符号引用(Symbolic References)以一组符号来描述所引用的目标，符号可以是任何形式的字面量，只要使用时能无歧义地定位到目标即可**
。 **符号引用与虚拟机实现的内存布局无关** ，引用的目标并不一定已经加载到了内存中。

b. **直接引用可以是直接指向目标的指针，相对偏移量或是一个能间接定位到目标的句柄** 。 **直接引用与虚拟机实现的内存布局相关**
，同一个符号引用在不同的虚拟机实例上翻译出来的直接引用一般不会相同。如果有了直接引用，那引用的目标就必须已经在内存中存在。

**虚拟机规范中并未规定解析阶段发生的具体时间，只要求在执行了newarray，heckcast，getfield，etstatic，instanceof，invokeinterface，invokespecial，nvokestatic，invokevritual，multianewarray，new，putfield和putstatic这13个用于操作符号引用的字节码指令之前，先对它们所使用的符号引用进行解析。**
所以虚拟机实现会根据需要来判断，到底是在类加载器加载时就对常量池中的符号引用进行解析，还是等到一个符号引用将要被使用时才去解析它。

**同一个符号引用可能会进行多次解析请求**
，虚拟机实现可能会对第一次解析的结果进行缓存从而避免解析动作重复进行。无论是否真正执行了多次解析操作，虚拟机需要保证的都是在同一个实体中，如果一个符号引用被成功解析过，那么后续的解析请求就应当一直成功；同样的，如果第一次解析失败了，其它指令对这个符号引用的解析请求也应该收到相同的异常。

解析动作主要针对的是类或接口，字段，方法，接口方法四类符号引用进行的，分别对应于常量池的CONSTANT_Class_info，CONSTANT_Fieldref_info，CONSTANT_Methodref_info及CONSTANT_InterfaceMetodref_info四种常量类型。下面是这四种引用的解析过程。

**1.类或接口的解析过程**
假设当前代码所处的类为D，如果要把一个从未解析过的符号引用N解析为一个类或接口C的直接引用，那虚拟机完成整个解析过程需要包括以下3个步骤：

a.如果C不是一个数组类型，那虚拟机将会把代表N的全限定名传递给D类的加载器去加载这个类C。在加载过程中，
**由于元数据验证，字节码验证的需要，又将可能触发其它相关类的加载动作，例如加载这个类的父类或实现的接口**
。一旦这个加载过程出现了任何异常，解析过程就将宣告失败。

b.如果C是一个数组类型，并且数组的元素类型为对象，也就是N的描述符会是类似”[Ljava.lang.Integer"的形式，那么会按照第a点的规则加载数组元素类型。如果N的描述符如前面所假设的形式，需要加载的元素类型就是“java.lang.Integer”，接着由虚拟机生成一个代表此数组和元素的数组对象。

c.如果上面的步骤没有出现任何异常，那么C在虚拟机中实际上已经成为一个有效的类或接口了，但在解析完成之前还要进行符号引用验证，
**确认D是否具备对C的访问权限** ，如果发现不具体访问权限，将抛出java.lang.IllegalAccessError错误。

**2.字段解析**
——多态要解析一个未被解析过的字段符号引用，首先将会对字段表内class_index项中索引的CONSTANT_Class_info符号引用进行解析，也就是字段所属性的类或接口的符号引用。如果在解析这个类或接口符号引用过程中出现了任何异常，都会导致字段符号引用解析失败。如果解析成功完成，那么这个字段所属性的类或接口用C表示，虚拟机规范要求如下步骤对C进行后续字段的搜索：a.如果C本身就包含了简单名称和字段描述符都与目标相匹配的字段，则返回这个字段的直接引用，查找结束。b.否则，如果C中实现了接口，将会按照继承关系从上往下递归搜索各个接口和它的父接口，如果接口中包含了简单名称答字段描述符都与目标相匹配的字段，则返回该字段的直接引用，查找结束。c.否则，如果C不是java.lang.Object的话，将会按照继承关系从上往下递归搜索其父类，如果在父类中包含了简单名称和字段描述符都与目标匹配的字段，则返回这个字段的直接引用，查找结束。d.否则，查找失败，招抛出java.lang.NoSuchFieldError错误。

**3.类方法解析**
类方法解析的第一个步骤与字段解析一样，也是需要先解析出方法表的class_index项中索引的方法所属性类或接口的符号引用，如果解析成功，依然用C表示这个类，接下来虚拟机将会按照如下步骤进行后续的类方法搜索：a.类方法和接口方法符号引用的常量类型定义是分开的，
**如果在类方法表中发现了class_index中索引的C是个接口，那么直接就抛出java.lang.IncompatibleClassChangeError错误**
。b.如果通了第a步，在类C中查找是否有简单名称和描述符与目标相匹配的方法，如果有则返回这个方法的直接引用，查找结束。c.否则，在类C的父类中递归查找是否有简单名称和字段描述符都与目标匹配的方法，则返回这个方法的直接引用，查找结束。d.否则，
**在类C实现的接口列表及它们的父接口中递归查找否有简单名称和字段描述符都与目标匹配的方法，说明类C是一个抽象类，这时候查找结束，抛出java.lang.AbstractMethodError错误。**
e.否则，宣告查找失败，抛出java.lang.NoSuchMethodError错误。最后，如果查找过程成功返回了直接引用，将会对这个方法进行权限验证；如果发现不具务对此方法的访问权限，将抛出java.lang.IllegalAccessError错误。

**4.接口方法解析**
接口方法也需要先解析出接口方法表中的class_index项中索引的方法所属性的类或接口的符号引用，如果解析成功，依然用C表示这个接口，接下来虚拟机将会按照如下步骤进行后续的接口访求搜索：a.与类方法解析相反，如果在接口方法表中发现了class_index中索引的C是个类而不是接口，那么直接就抛出java.lang.IncompatibleClassChangeError错误。b.否则，在接口C中查找是否有简单名称的描述符都与目标相匹配的方法，如果有则返回这个方法的直接引用，查找结束。c.否中，在接口C的父接口中递归查找，直到java.lang.Object类为止，看是否有简单名称和描述符都与目标相匹配的方法，如果有则返回这个方法的直接引用，查找结束。d.否则，宣告查找失败，抛出java.lang.NoSuchMethodError错误。由于接口中的所有方法都默认是public的，所以不存在访问权限问题，因此接口方法的符号解析应该不会抛出java.lang.IllegalAccessError错误。

## 五、初始化

**类的初始化是类加载过程的最后一步，前面的类加载动作，除了在加载阶段用户应用程序可以通过自定义类加载器参与之外，其余动作完全由虚拟机主导和控制。到了初始化阶段，才真正执行类中定义的Java程序代码(或者说是字节码)。**

在准备阶段，变量已经赋过一次系统要求的初始值，而在初始化阶段，则是根据程序员通过程序制定的主观计划去初始化类变量和其它资源，或者可以从另外一个角度来表达：
**初始化阶段是执行类构造器 <clinit>()方法的过程。**<clinit>()方法执行过程可能会影响程序运行行为的一些特点与细节，如下：

  1. **< clinit>()方法是由编译器自动收集类中所有类变量的赋值动作和静态语句块(static{})中的语句合并产生的**，编译器收集的顺序是由语句在源文件中出现的顺序所决定的，静态语句块中只能访问到定义在静态语句块之前的变量，定义在它之后变量，在前面的静态语句块中可以赋值，但是不能访问。

  2. **< clinit>()方法与类的构造器<init>()不同，它不需要显示地调用父类类构造器，虚拟机会保证在子类的<clinit>()方法执行之前，父类的<clinit>()方法已经执行完毕。因此在虚拟机中第一个被执行<clinit>()方法的类肯定是java.lang.Object。**

  3. **由于父类的 <clinit>()方法先执行，所就意味着父类中定义的静态语句块要优先于子类的类变量赋值操作**。

  4. **< clinit>()方法对于类或接口来说并不是必须的，如果一个类中没有静态语句块，也没有对类变量的赋值操作，那么编译器可以不为这类生成<clinit>()方法。**

  5. 接口中不能使用静态语句块，但仍然可以有变量初始化的赋值操作，因此接口与类一样都会生成<clinit>()方法，但 **接口与类不同的是，执行接口的 <clinit>()方法不需要先执行父接口的<clinit>()方法。只有当父接口中定义的变量被使用时，父接口才会初始化。另外，接口的实现类在初始化时也不会执行接口的<clinit>()方法。**

  6. **虚拟机会保证一个类的 <clinit>()方法在多线程环境中被正确地加锁同步**，如果多个线程同时去初始化一个类，那么只会有一个线程去执行这个类的<clinit>()方法，其它线程都需要阻塞等待，直到活动线程执行<clinit>()方法完毕。如果在一个类的<clinit>()方法中有很耗时的操作，那就可能造成多个线程阻塞，在实际应用中这种阻塞往往是很隐蔽的。

##### 疑问：

Q: JVM的符号引用替换为直接引用什么意思？

A:
[参考](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.cnblogs.com%2Fshinubi%2Farticles%2F6116993.html)

**在JVM中类加载过程中，在解析阶段，Java虚拟机会把类的二进制数据中的符号引用替换为直接引用。**

1. **符号引用** （Symbolic References）：

**符号引用以一组符号来描述所引用的目标**
，符号可以是任何形式的字面量，只要使用时能够无歧义的定位到目标即可。例如，在Class文件中它以CONSTANT_Class_info、CONSTANT_Fieldref_info、CONSTANT_Methodref_info等类型的常量出现。符号引用与虚拟机的内存布局无关，引用的目标并不一定加载到内存中。在[Java](https://links.jianshu.com/go?to=http%3A%2F%2Flib.csdn.net%2Fbase%2Fjavaee)中，一个java类将会编译成一个class文件。
**在编译时，java类并不知道所引用的类的实际地址，因此只能使用符号引用来代替。**
比如org.simple.People类引用了org.simple.Language类，在编译时People类并不知道Language类的实际内存地址，因此只能使用符号org.simple.Language（假设是这个，当然实际中是由类似于CONSTANT_Class_info的常量来表示的）来表示Language类的地址。各种虚拟机实现的内存布局可能有所不同，但是它们能接受的符号引用都是一致的，因为符号引用的字面量形式明确定义在Java虚拟机规范的Class文件格式中。

2. **直接引用** ：

直接引用可以是：

（1） **直接指向目标的指针** （比如，指向“类型”【Class对象】、类变量、类方法的直接引用可能是指向方法区的指针）

（2） **相对偏移量** （比如，指向实例变量、实例方法的直接引用都是偏移量）

（3） **一个能间接定位到目标的句柄**

直接引用是和虚拟机的布局相关的，同一个符号引用在不同的虚拟机实例上翻译出来的直接引用一般不会相同。如果有了直接引用，那引用的目标必定已经被加载入内存中了。

# **双亲委派模型**

**站在虚拟机的角度上** ，只存在两种不同的类加载器： **一种是启动类加载器(Bootstrap ClassLoader)** ，这个类加载器
**使用C++语言实现，是虚拟机自身的一部分** ；另外一种就是
**其它所有的类加载器，这些类加载器都由Java语言实现，独立于虚拟机外部，并且全部继承自java.lang.ClassLoader** 。
**从Java开发人员的角度看** ，类加载器还可以划分得更细一些，如下：

  1. **启动类加载器(Bootstrap ClassLoader)：这个类加载器负责将放置在 <JAVA_HOME>\lib目录中的，或者被-Xbootclasspath参数所指定路径中的，并且是虚拟机能识别的**(仅按照文件名识别，如rt.jar， **名字不符合的类库即使放置在lib目录中也不会被加载** )类库加载到虚拟机内存中。启动类加载器无法被Java程序直接使用。

  2. **扩展类加载器(Extension ClassLoader)** ：这个类加载器由sun.misc.Launcher$ExtClassLoader实现，它 **负责加载 <JAVA_HOME>\lib\ext目录中的，或者被java.ext.dirs系统变量所指定的路径中的所有类库**，开发者可以直接使用扩展类加载器。

  3. **应用程序类加载器(Application ClassLoader)** ：这个类加载器由sum.misc.Launcher.$AppClassLoader来实现。由于这个类加载器是ClassLoader中的 **getSystemClassLoader()方法的返回值，所以一般也被称为系统类加载器** 。 **它负责加载用户类路径上所指定的类库** ，开发者可以直接使用这个类加载器，如果应用程序中没有自定义过自己的类加载器， **一般情况下这个就是程序中默认的类加载器** 。

应用程序由这三种类加载器互相配合进行加载的，如果有需要，还可以加入自己定义的类加载器。这些类加载器之间的关系一般如下图：

image

上图中展示的 **类加载器之间的层次关系，就称为类加载器的双亲委派模型(Parents Delegation Model)**
。双亲委派模型要求除了顶层的启动类加载器之外，其余的类加载器都应当有自己的父类加载器。这里的类加载器之间的父子关系一般
**不会以继承的关系来实现，而是使用组合关系来复用父加载器的代码** 。
**双亲委派模型的工作过程是：如果一个类加载器收到了类加载的请求，它首先不会自己去尝试加载这个类，而是把这个请求委派给父类加载器去完成，每一个层次的类加载器都是如此，因此所有的加载请求最终都应该传送到顶层的启动类加载器中，只有当父加载器反馈自己无法完全这个加载请求时，子加载器才会尝试自己去加载。**

双亲委派模型的破坏 **双亲委派模型的第一次“被破坏”其实发生在双亲委派模型出现之前**
\--即JDK1.2发布之前。由于双亲委派模型是在JDK1.2之后才被引入的，而类加载器和抽象类java.lang.ClassLoader则是JDK1.0时候就已经存在，面对已经存在
的用户自定义类加载器的实现代码，Java设计者引入双亲委派模型时不得不做出一些妥协。为了向前兼容，JDK1.2之后的java.lang.ClassLoader添加了一个新的protected方法findClass()，在此之前，用户去继承java.lang.ClassLoader的唯一目的就是重写loadClass()方法，因为虚拟在进行类加载的时候会调用加载器的私有方法loadClassInternal()，而这个方法的唯一逻辑就是去调用自己的loadClass()。

JDK1.2之后已
**不再提倡用户再去覆盖loadClass()方法，应当把自己的类加载逻辑写到findClass()方法中，在loadClass()方法的逻辑里，如果父类加载器加载失败，则会调用自己的findClass()方法来完成加载，这样就可以保证新写出来的类加载器是符合双亲委派模型的。**

**双亲委派模型的第二次“被破坏”是这个模型自身的缺陷所导致的**
，双亲委派模型很好地解决了各个类加载器的基础类统一问题(越基础的类由越上层的加载器进行加载)，基础类之所以被称为“基础”，是因为它们总是作为被调用代码调用的API。

但是，如果基础类又要调用用户的代码，那该怎么办呢。

这并非是不可能的事情，一个典型的例子便是JNDI（Java 命名与目录接口
）服务，它的代码由启动类加载器去加载(在JDK1.3时放进rt.jar)，但JNDI的目的就是对资源进行集中管理和查找，它需要调用独立厂商实现部部署在应用程序的classpath下的JNDI接口提供者(SPI,
Service Provider Interface)的代码，但启动类加载器不可能“认识”之些代码，该怎么办？

为了解决这个困境，Java设计团队只好引入了一个不太优雅的设计：线程上下文类加载器(Thread Context ClassLoader)。
**这个类加载器可以通过java.lang.Thread类的setContextClassLoader()方法进行设置，如果创建线程时还未设置，它将会从父线程中继承一个；如果在应用程序的全局范围内都没有设置过，那么这个类加载器默认就是应用程序类加载器。**
有了线程上下文类加载器，JNDI服务使用这个线程上下文类加载器去加载所需要的SPI代码，也就是 **父类加载器请求子类加载器去完成类加载动作**
，这种行为实际上就是打通了双亲委派模型的层次结构来逆向使用类加载器，已经违背了双亲委派模型，但这也是无可奈何的事情。
**Java中所有涉及SPI的加载动作基本上都采用这种方式，例如JNDI,JDBC,JCE,JAXB和JBI等。**

**双亲委派模型的第三次“被破坏”是由于用户对程序的动态性的追求导致的，例如OSGi的出现**
。在OSGi环境下，类加载器不再是双亲委派模型中的树状结构，而是进一步发展为 **网状结构** 。

##### 疑问：

Q: **启动类加载器(Bootstrap ClassLoader)：这个类加载器负责将放置在 <JAVA_HOME>\lib目录中的，或者被-
Xbootclasspath参数所指定路径中的，并且是虚拟机能识别的**(仅按照文件名识别，如rt.jar，
**名字不符合的类库即使放置在lib目录中也不会被加载** )类库加载到虚拟机内存中.什么叫能被虚拟机识别的类库,都有哪些？

# **运行时栈帧结构**

**栈帧(Stack Frame)是用于支持虚拟机进行方法调用和方法执行的数据结构** ，它是虚拟机运行时数据区的虚拟机栈(Virtual Machine
Stack)的栈元素。 **栈帧存储了方法的局部变量表，操作数栈，动态连接和方法返回地址等信息** 。第
**一个方法从调用开始到执行完成，就对应着一个栈帧在虚拟机栈中从入栈到出栈的过程**
。每一个栈帧都包括了局部变量表，操作数栈，动态连接，方法返回地址和一些额外的附加信息。
**在编译代码的时候，栈帧中需要多大的局部变量表，多深的操作数栈都已经完全确定了，并且写入到了方法表的Code属性中，因此一个栈帧需要分配多少内存，不会受到程序运行期变量数据的影响，而仅仅取决于具体虚拟机的实现。**

一个线程中的方法调用链可能会很长，很多方法都同时处理执行状态。对于执行引擎来讲，活动线程中，只有虚拟机栈顶的栈帧才是有效的，称为 **当前栈帧**
(Current Stack Frame)，这个栈帧所关联的方法称为当前方法(Current
Method)。执行引用所运行的所有字节码指令都只针对当前栈帧进行操作。栈帧的概念结构如下图所示：

image

## 1.局部变量表——存放方法参数和方法内部定义的局部变量

**局部变量表是一组变量值存储空间，用于存放方法参数和方法内部定义的局部变量。** 在Java程序编译为Class文件时，就在
**方法表的Code属性的max_locals** 数据项中确定了该方法需要分配的 **最大局部变量表的容量** 。

在方法执行时，虚拟机是使用局部变量表完成参数变量列表的传递过程，如果是
**实例方法，那么局部变量表中的每0位索引的Slot默认是用于传递方法所属对象实例的引用，在方法中可以通过关键字“this”来访问这个隐含的参数**
，其余参数则按照参数列表的顺序来排列，占用从1开始的局部变量Slot，参数表分配完毕后，再根据方法体内部定义的变量顺序和作用域来分配其余的Slot。局部变量表中的Slot是可重用的，方法体中定义的变量，其作用域并不一定会覆盖整个方法，如果当前字节码PC计算器的值已经超出了某个变量的作用域，那么这个变量对应的Slot就可以交给其它变量使用。

局部变量不像前面介绍的类变量那样存在“准备阶段”。
**类变量有两次赋初始值的过程，一次在准备阶段，赋予系统初始值；另外一次在初始化阶段，赋予程序员定义的值。**
因此即使在初始化阶段程序员没有为类变量赋值也没有关系，类变量仍然具有一个确定的初始值。但局部变量就不一样了，如果一个
**局部变量定义了但没有赋初始值是不能使用的。**

## 2.操作数栈——用于执行运算的后入先出栈

**操作数栈也常被称为操作栈，它是一个后入先出栈** 。同局部变量表一样，
**操作数栈的最大深度也是编译的时候被写入到方法表的Code属性的max_stacks数据项中。**
操作数栈的每一个元素可以是任意Java数据类型，包括long和double。
**32位数据类型所占的栈容量为1，64位数据类型所占的栈容量为2。栈容量的单位为“字宽”，对于32位虚拟机来说，一个”字宽“占4个字节，对于64位虚拟机来说，一个”字宽“占8个字节。**

当一个方法刚刚执行的时候，这个方法的操作数栈是空的，在方法执行的过程中，会有各种字节码指向操作数栈中写入和提取值，也就是入栈与出栈操作。例如，在做算术运算的时候就是通过操作数栈来进行的，又或者调用其它方法的时候是通过操作数栈来进行参数传递的。

另外，在概念模型中，两个栈帧作为虚拟机栈的元素，相互之间是完全独立的，但是大多数虚拟机的实现里都会作一些优化处理，令两个栈帧出现一部分重叠。
**让下栈帧的部分操作数栈与上面栈帧的部分局部变量表重叠在一起，这样在进行方法调用返回时就可以共用一部分数据，而无须进行额外的参数复制传递了**
，重叠过程如下图：

image

## 3.动态连接——保存栈帧所属方法的引用

**每个栈帧都包含一个指向运行时常量池中该栈帧所属方法的引用，持有这个引用是为了支持方法调用过程中的动态连接。**
在Class文件的常量池中存有大量的符号引用，字节码中的方法调用指令就以常量池中指向方法的符号引用为参数。
**这些符号引用一部分会在类加载阶段或第一次使用的时候转化为直接引用，这种转化称为静态解析。另外一部分将在每一次的运行期期间转化为直接引用，这部分称为动态连接。**

## 4.方法返回地址——调用方法的程序计数器的值作为返回地址

当一个方法被执行后，有两种方式退出这个方法。第一种方式是执行引擎遇到任意一个方法返回的字节码指令，这时候可能会有返回值传递给上层的方法调用者(调用当前方法的的方法称为调用者)，是否有返回值和返回值的类型将根据遇到何种方法返回指令来决定，这种退出方法方式称为
**正常完成出口** (Normal Method Invocation Completion)。

另外一种退出方式是，在方法执行过程中遇到了异常，并且这个异常没有在方法体内得到处理，无论是Java虚拟机内部产生的异常，还是代码中使用athrow字节码指令产生的异常，
**只要在本方法的异常表中没有搜索到匹配的异常处理器，就会导致方法退出** ，这种退出方式称为 **异常完成出口** (Abrupt Method
Invocation Completion)。一个方法使用 **异常完成出口的方式退出，是不会给它的调用都产生任何返回值的。**

无论采用何种方式退出，在方法退出之前，都需要返回到方法被调用的位置，程序才能继续执行，方法返回时可能需要在栈帧中保存一些信息，用来帮助恢复它的上层方法的执行状态。一般来说，
**方法正常退出时，调用者PC程序计数器的值就可以作为返回地址** ，栈帧中很可能会保存这个计数器值。而
**方法异常退出时，返回地址是要通过异常处理器来确定的，栈帧中一般不会保存这部分信息。**

方法退出的过程实际上等同于把当前栈帧出栈，因此退出时可能执行的操作有：恢复上层方法的局部变量表和操作数栈，把返回值(如果有的话)压入调用都栈帧的操作数栈中，调用PC计数器的值以指向方法调用指令后面的一条指令等。

## 5\. 附加信息

虚拟机规范允许具体的虚拟机实现增加一些规范里没有描述的信息到栈帧中，例如与高度相关的信息，这部分信息完全取决于具体的虚拟机实现。在实际开发中，一般会把动态连接，方法返回地址与其它附加信息全部归为一类，称为栈帧信息。

##### 疑问：

Q:
**32位数据类型所占的栈容量为1，64位数据类型所占的栈容量为2。栈容量的单位为“字宽”，对于32位虚拟机来说，一个”字宽“占4个字节，对于64位虚拟机来说，一个”字宽“占8个字节。**
意思是说，如果是64位虚拟机，对于像long这种数据类型，它的实际所占的栈容量为2，则占有2* 8 =16个字节。是么？那32位虚拟机是8个字节？

Q:
每个栈帧都包含一个指向运行时常量池中该栈帧所属方法的引用，持有这个引用是为了支持方法调用过程中的动态连接。也就是说每个栈帧都会持有这个栈帧对应调用方法的引用，这样在线程切换或者方法的连续调用中当要切换或者调用到这个栈帧时可以根据程序计数器（偏移量）结合这个引用，再次找到这个方法在内存中上次执行到的位置，继续执行代码。
是这样么？


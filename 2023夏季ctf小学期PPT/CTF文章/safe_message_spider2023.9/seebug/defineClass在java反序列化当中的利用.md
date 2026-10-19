作者：阿里安全归零实验室  
来源：<https://xz.aliyun.com/t/2272>

本文分享一下defineClass在反序列化漏洞当中的使用场景，以及在exp构造过程中的一些使用技巧

#### 0x00 前言

首先看一下defineClass的官方定义

![](https://images.seebug.org/content/images/2018/04/944f804e-efa8-4c17-9471-193547a082d7.png-w331s)

众所周知，java编译器会将.java文件编译成jvm可以识别的机器代码保存在.class文件当中。正常情况下，java会先调用classLoader去加载.class文件，然后调用loadClass函数去加载对应的类名，返回一个Class对象。而defineClass提供了另外一种方法，从官方定义中可以看出，defineClass可以从byte[]还原出一个Class对象，这种方法，在构造java反序列化利用和漏洞poc时，变得非常有用。下面总结我在实际分析漏洞和编写exp时的一点儿体会，具体有如下几种玩法.

#### 0x01 defineCLass构造回显

这里以java原生的java.io.ObjectInputStreamread的readObject()作为反序列化函数，以commons-collections-3.1作为payload，注入类文件代码如下

![](https://images.seebug.org/content/images/2018/04/2bbe4b6d-3ca3-4a85-9b4e-ccc3ddf03d7a.png-w331s)

常规的回显思路是用URLClassLoader去加载一个.class或是.java文件，然后调用loadClass函数去加载对应类名，返回对应的Class对象，然后再调用newInstance()实例出一个对象，最后调用对应功能函数，使用例如throw
new Exception("genxor");这样抛错的方法，将回显结果带出来。例如

![](https://images.seebug.org/content/images/2018/04/247002d2-607b-421e-97d4-82ae298cba7f.png-w331s)

回显结果如下所示：

![](https://images.seebug.org/content/images/2018/04/d4f2b66d-6365-4694-af3b-67d03db87f69.png-w331s)

但是前提是要先写入一个.class或是.jar文件(写入方法这里不描述，使用FileOutputStream类，方法大同小异)，这样显得拖泥带水，而且让利用过程变得很复杂。

那可不可以不写文件而直接调用我们的代码呢，使用defineClass很好的解决了这个问题。将我们编译好的.class或是.jar文件转换成byte[]放到内存当中，然后直接用defineClass加载byte[]返回Class对象。那怎么调用defineClass函数呢，因为默认的defineClass是java.lang.ClassLoader的函数，而且是protected属性，无法直接调用（这里暂且不考虑反射），而且java.lang.ClassLoader类也无法被transform函数加载，这里我们使用org.mozilla.classfile.DefiningClassLoader类，
代码如图

![](https://images.seebug.org/content/images/2018/04/4ef72666-6d8b-498d-bedd-67c7c87196ca.png-w331s)

他重写了defineClass而且是public属性，正好符合我们要求，这里我写个具体事例，代码如下

![](https://images.seebug.org/content/images/2018/04/40208c8f-4c30-4503-8be7-37538da9db0b.png-w331s)

回显结果如下所示

![](https://images.seebug.org/content/images/2018/04/ded3b4d0-4c36-4f66-935a-e25c9d062e36.png-w331s)

根据这个思路，我们构造transformerChain生成map对象，代码如图所示

![](https://images.seebug.org/content/images/2018/04/88f32361-c5ff-49f3-8b37-37b008760516.png-w331s)

#### 0x02 fastjson利用

fastjson早期的一个反序列化命令执行利用poc用到了
com.sun.org.apache.bcel.internal.util.ClassLoader，首先简单说一下漏洞原理，如下是利用poc的格式

![](https://images.seebug.org/content/images/2018/04/9e66ad51-3c04-4adf-bef5-8d5e354a2660.png-w331s)

fastjson默认开启type属性，可以利用上述格式来设置对象属性（fastjson的type属性使用不属于本文叙述范畴，具体使用请自行查询）。tomcat有一个tomcat-dbcp.jar组件是tomcat用来连接数据库的驱动程序，其中org.apache.tomcat.dbcp.dbcp.BasicDataSource类存在如下代码，如图所示

![](https://images.seebug.org/content/images/2018/04/c7349825-a019-462a-a6d0-3945b2f64130.png-w331s)

当com.alibaba.fastjson.JSONObject.
parseObject解析上述json的时候，代码会上图中Class.forName的逻辑，同时将driverClassLoader和driverClassName设置为json指定的内容，到这里简单叙述了一下fastjson漏洞的原理，一句话概括就是利用fastjson默认的type属性，操控了相应的类，进而操控Class.forName()的参数，可以使用任意ClassLoader去加载任意代码，达到命令执行的目的。

这里详细说一下利用Class.forName执行代码的方法，有两种方式：

  1. Class.forName(classname)
  2. Class.forName(classname, true, ClassLoaderName)

先说第一种，通过控制classname执行代码，这里我写了一个demo，如图所示

![](https://images.seebug.org/content/images/2018/04/8f42268a-84be-464f-b25f-9cf33e07a805.png-w331s)
![](https://images.seebug.org/content/images/2018/04/bbaeb5cb-d655-416f-8214-ad3955bc1e45.png-w331s)
![](https://images.seebug.org/content/images/2018/04/5fe3b87a-a4df-4268-8531-66473c893151.png-w331s)

这里利用了java的一个特性，利用静态代码块儿static{}来执行，当com.fastjson.pwn.run被Class.forName加载的时候，代码便会执行。

第二种，通过控制classname和classloader执行代码，我写了一个demo，以com.sun.org.apache.bcel.internal.util.ClassLoader这个类为例子，如图所示

![](https://images.seebug.org/content/images/2018/04/49715d32-e52a-4f68-ac17-0164fd9ee469.png-w331s)

这里用到了com.sun.org.apache.bcel.internal.util.ClassLoader这个classloader，而classname是一个经过BCEL编码的evil.class文件，这里我给出evil.java的源码，如图所示

![](https://images.seebug.org/content/images/2018/04/a1fb8944-e809-43ed-b389-58c13b71329e.png-w331s)

classloader会先把它解码成一个byte[]，然后调用defineClass返回Class，也就是evil

具体我们跟一下代码逻辑，如图所示

![](https://images.seebug.org/content/images/2018/04/28a1ad8c-8f2f-4b65-b52f-87a7fa05cc7b.png-w331s)

这里会开始调用com.sun.org.apache.bcel.internal.util.ClassLoader的loadClass加载类，如图所示

![](https://images.seebug.org/content/images/2018/04/a1785976-bcec-4471-ad2d-0e8464e526d7.png-w331s)

这里判断classname如果经过了BCEL编码，则解码获取Class文件，如图

![](https://images.seebug.org/content/images/2018/04/fdc1c973-ccea-4136-8879-d33b5febc8c9.png-w331s)

此刻内存中evil.class文件的结构，如图所示

![](https://images.seebug.org/content/images/2018/04/358984ea-7515-4c15-973b-a79381743ad5.png-w331s)

继续跟踪后面的逻辑，如图

![](https://images.seebug.org/content/images/2018/04/9debbfca-24da-4561-9dd5-d58fb0bd9c99.png-w331s)

这里调用defineClass还原出evil.class中的evil类，因为使用static{}，所以在加载过程中代码执行。

OK
回到fastjson漏洞逻辑，因为控制了Class.forName加载的类和ClassLoader，所以可以通过调用特定的ClassLoader去加载精心构造的代码，从而执行我们事先构造好的class文件，从而达到执行任意代码的目的。

#### 0x03 jackson利用

jackson的反序列化命令执行跟fastjson类似，也似注入一个精心构造的pwn.class文件，最后通过newInstance实例对象触发代码执行。这里先给出pwn.java的源码，如图所示：

![](https://images.seebug.org/content/images/2018/04/cef67dfa-4b8c-4af7-8a04-bdf43ec5fcd4.png-w331s)

然后写了一个Demo，触发漏洞，代码如下

![](https://images.seebug.org/content/images/2018/04/85159b3f-adf4-46bc-b435-91b8313b0c40.png-w331s)

jackson类似fastjson可以通过type属性，设置变量的值，但是不同时jackson默认不开启type，需要mapper.enableDefaultTyping()设置开启。

![](https://images.seebug.org/content/images/2018/04/677e90ef-9547-45ab-896c-5600275b223e.png-w331s)

当readValue这段json的时候，触发命令执行漏洞，下面调试一下关键步骤，如图

![](https://images.seebug.org/content/images/2018/04/a6206556-a592-4d84-bdf9-8a3862b5ebdd.png-w331s)

这里defineTransletClasses会解码transletBytecodes成byte[]，并执行defineClass得到foo.pwn这个类，然后在后面执行newInstance导致static{}静态代码块儿执行，如图

![](https://images.seebug.org/content/images/2018/04/90d684f0-2b16-4923-a19a-73af36c852f9.png-w331s)

成功触发，如图所示

![](https://images.seebug.org/content/images/2018/04/18d22e67-b5ad-4e31-9e39-08da4311fd13.png-w331s)

#### 0x04 总结

利用defineClass在运行时状态下，将我们精心构造的class文件加载进入ClassLoader，通过java的static{}特征，导致代码执行。

以上测试代码全部保存在： <https://github.com/genxor/Deserialize.git>

#### 0x05 关于我们

阿里安全归零实验室成立于2017年11月，实验室致力于对黑灰产技术的研究,愿景通过技术手段解决当前日益严重的网络违规和网络犯罪问题，为阿里新经济体保驾护航。实验室与寄生在阿里生态经济体的黑灰产直面技术对抗，以打造一流的以情报驱动的黑灰产情报体系能力，看清黑灰产风险、领先黑灰产、演练风险为愿景，重点研究业务安全和数据安全领域中黑灰产风险事件背后的产业链和手法，解决相关风险问题。以情报外部视角切入，在多个安全风险领域内均取得了不错的成绩；以蓝军真实黑灰产视角，模拟黑灰产进行演练攻击，检验防线，为阿里巴巴经济体保驾护航贡献了一份独特的力量。

目前团队也在不断的招聘各种优秀人才，研发专家、数据分析专家、情报分析与体系化专家等，欢迎加盟，联系邮箱
联系：back2zero@service.alibaba.com

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/572/>


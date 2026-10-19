Burp
Suite是每个web安全学习者都接触过的集成平台，包含集合了多种渗透测试组件，除了强大的功能外，官方还提供API支持使用者开发插件，满足你独特的需求。

 **0x00 Burp Suite扩展模块**

斗哥这里从Burp的Extender（扩展）模块为出发点，讲述Burp的扩展开发，其它模块功能的使用大家可以查看公众号Burp Suite使用的系列的文章。

Burp Extender的Extension页面中，可以手动添加开发好的插件，显示已添加的插件进行管理。

![管理.png](https://image.3001.net/images/20180514/15262793135944.png!small)

BApp
Store的页面中左边为各个插件的应用列表，当选中某个插件后，右侧显示的为该插件的描述信息和安装信息。如果我们需要使用某个插件，则点击右侧下方的【install】按钮，进行安装。描述信息中可能提供源码的地址可以阅读学习或者修改源码来实现想要的功能。

![功能.png](https://image.3001.net/images/20180514/15262793403337.png!small)

APls界面由左边的接口类和右边的接口定义和描述构成，其中左边的最下端有两个按钮，图中1按钮为保存接口类，图中2按钮为保存Javadocs。

![cs.png](https://image.3001.net/images/20180514/15262793799558.png!small)

保存接口类，当我们点击保存后，在指定的存储目录下，会生成一系列的jav文件如下图：

![下图.png](https://image.3001.net/images/20180514/15262794208298.png!small)

保存Javadocs,点击保存后，会在存储目录中存放与API相对应的JavaDocs文件。来说明API的使用，用浏览器打开则如下图所示：

![所示.png](https://image.3001.net/images/20180514/15262794509234.png!small)

**0x01 API简述**

我们可以把JAVA接口看成一个高级类，与普通类不同的是我们要实现它的所有方法，相当于burp定出的“规则”，我们在开发时一定要遵守“规则”才能实现接口方法功能，“规则”包括有接口的实例化（实现方法）、接口方法入参（参数类型和参数个数）、接口方法的返回值（返回值类型）。我们在JavaDocs可以查看这些“规则”。

接口类的使用说明除了上文说的，我们能导出JavaDocs到本地外，Burp官方也提供了一份在线文档，地址
为：<https://portswigger.net/burp/extender/api/index.html>

下面根据接口功能的不同对API 进行分类：

1\. 插件入口和帮助接口类：IBurpExtender、IBurpExtenderCallbacks、
IExtensionHelpers、IExtensionStateListener

IExtensionHelpers、IExtensionStateListener
IBurpExtender接口类是Burp插件的入口，所有Burp的插件均需要实现此接口，并且
类命名为BurpExtender。IBurpExtenderCallbacks接口类是IBurpExtender接口的实
现类与Burp其他各个组件（Scanner、Intruder、Spider......）、各个通信对象
（HttpRequestResponse、HttpService、SessionHandlingAction）之间的连接。
IExtensionHelpers、IExtensionStateListener这两个接口类是插件的帮助和管理操作的接口定义。

2\. UI相关接口类：IContextMenuFactory、IContextMenuInvocation、ITab、ITextEditor、
IMessageEditor、IMenuItemHandler 这类接口类主要是定义Burp插件的UI显示和动作的处理事件，主要是软件交互中使用。

3\. Burp工具组件接口类：IInterceptedProxyMessage、IIntruderAttack、
IIntruderPayloadGenerator、IIntruderPayloadGeneratorFactory、
IIntruderPayloadProcessor、IProxyListener、IScanIssue、IScannerCheck、
IScannerInsertionPoint、IScannerInsertionPointProvider、IScannerListener、IScanQueueItem、IScopeChangeListener
这些接口类的功能非常好理解，Burp在接口定义的命名中使用了的见名知意的规 范，看到接口类的名称，基本就能猜测出来这个接口是适用于哪个工具组件。

4\. HTTP消息处理接口类：ICookie、IHttpListener、IHttpRequestResponse、
IHttpRequestResponsePersisted、IHttpRequestResponseWithMarkers、IHttpService、
IRequestInfo、IParameter、IResponseInfo
这些接口的定义主要是围绕HTTP消息通信过程中涉及的Cookie、Request、
Response、Parameter几大消息对象，通过对通信消息头、消息体的数据处理，来达到控制HTTP消息传递的目的。

 **0x02 开发环境准备**

1.选择开发语言

Burp Suite插件开发模块支持Java、Python和Ruby三种语言，因Burp
Suite是由Java语言开发所以建议使用JAVA语言开发兼容性高可以避免许多奇怪的错误，斗哥这里选择JAVA进行开发讲解。

2.选择IDE

JAVA主流的IDE有MyEclipse、IDEA、还有Eclipse 这款强大的 IDE ，斗哥这里选择MyEclipse进行开发讲解。

如果选择Python或者Ruby，需要再配置环境Burp依靠Jython来提供其Python支持，Burp依靠JRuby来提供对Ruby的支持。

 **0x03 插件开发**

1.新建项目，将API的java文件引入Project中使用。

![使用.png](https://image.3001.net/images/20180514/15262796782084.png!small)

因下载时默认包名为burp，所以你的项目引入的包也要为burp，否则你要修改所有API的package后的包名。

2.IBurpExtender 接口Demo

●IBurpExtender 接口

解释：所有的插件必须实现此接口。实现的类名必须为“BurpExtender”。在 burp包中，必须申明为 public ,并且必须提供一个默认的构造器。

方法：void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks)

此方法将在扩展加载后被调用，它注册了一个 IBurpExtenderCallbacks 接口的实例， IBurpExtenderCallbacks
接口提供了许多在开发插件过程中常用的一些操作。

    
    
    public void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks)
    
       {
    
           // keep a reference to our callbacks object
    
           this.callbacks = callbacks;
    
           // set our extension name   设置扩展插件名
    
           callbacks.setExtensionName("Demo");
    
           // obtain our output stream  输出流，在burp输出内容，可用来调试代码
    
           stdout = new PrintWriter(callbacks.getStdout(), true);
    
           // register ourselves as an HTTP listener  注册IHttpListener接口
    
           callbacks.registerHttpListener(this);
    
       }
    

callbacks这个实例调用很多扩展 Burp 功能必需的方法。如：设置扩展插件的属性，操作 HTTP
请求和响应以及启动其他扫描功能等等。接口类属性通过get、set来与外界交互。

●IHttpListenerr 接口

解释：通过调用 IBurpExtenderCallbacks.registerHttpListener() 注册一个 HTTP 监听器。Burp
里的任何一个工具发起 HTTP 请求或收到 HTTP 响应都会通知此监听器。扩展可以得到这些交互的数据，进行分析和修改。

方法：void processHttpMessage(int toolFlag,boolean
messageIsRequest,IHttpRequestResponse messageInfo)

Parameters:

toolFlag - 指示了发起请求或收到响应的 Burp 工具的 ID，所有的 toolFlag 定义在 IBurpExtenderCallbacks
接口中。具体查看<https://portswigger.net/burp/extender/api/constant-values.html#burp.IBurpExtenderCallbacks>

messageIsRequest - 指示该消息是请求消息（值为True）还是响应消息（值为False）。

messageInfo - 被处理的消息的详细信息，是一个 IHttpRequestResponse 对象。

    
    
    //
    
       // implement IHttpListener
    
       //
    
       @Override
    
       public void processHttpMessage(int toolFlag, boolean messageIsRequest, IHttpRequestResponse messageInfo)
    
       {   
    
         byte[] ihttpreaust = messageInfo.getResponse();
    
           IHttpService service = messageInfo.getHttpService();
    
           byte[] ihttpreqpose = messageInfo.getResponse();
    
         if (toolFlag == callbacks.TOOL_PROXY) {     //burp的PROXY模块监听，未写时默认监听所有模块
    
             stdout.println("proxy1");
    
           }
    
         if (toolFlag == 4) {                          //burp的PROXY模块监听，PROXY的toolFlag值为4
    
             stdout.println("proxy2");
    
         }
    
         if (messageIsRequest){ //对请求包进行处理
    
               IRequestInfo IRequestInfoanalyzeRequest = helpers.analyzeRequest(messageInfo); 
    
             stdout.println("333333333");
    
             stdout.println("解析请求头"+IRequestInfoanalyzeRequest.getHeaders());
    
         }
    
         else {
    
            IResponseInfo IRequestInfoanalyzeresponse = helpers.analyzeResponse(ihttpreqpose); 
    
               stdout.println("解析返回包头"+IRequestInfoanalyzeresponse.getHeaders());
    
                 stdout.println("此方法用于获取 HTTP body 在响应消息中的起始偏移量."+IRequestInfoanalyzeresponse.getBodyOffset());
    
    }
    
           stdout.println(
    
                   (messageIsRequest ? "HTTP request to " : "HTTP response from ") +
    
                   messageInfo.getHttpService() +
    
                   " [" + callbacks.getToolName(toolFlag) + "]");
    
           stdout.println("请求"+ihttpreaust);//在burp窗口输出参数
    
           stdout.println("接收"+ihttpreqpose);
    
           stdout.println("服务主机名"+service.getHost());//在burp窗口输出service对象的Host属性
    
           stdout.println("服务主机接口"+service.getPort());//在burp窗口输出service对象的Port属性
    
           stdout.println("服务主机协议"+service.getProtocol());//在burp窗口输出service对象的tProtocol属性
    
       }
    

IHttpRequestResponse 对象提供了很多属性，在此不一一列举，具体的说明可以查看接口接口说明文档。

![文档.png](https://image.3001.net/images/20180514/15262798128397.png!small)

实现了此接口就可以操作数据包。

 **0x04 插件导入**

1.将开发完成的插件打包成jar包

MyEclipse

![se.png](https://image.3001.net/images/20180514/15262799097617.png!small)

IDEA：

![dea.png](https://image.3001.net/images/20180514/15262799482081.png!small)

2.将打包jar插件导入burp。

![burp.png](https://image.3001.net/images/20180514/15262800005162.png!small)

3.此插件监听PROXY模块，获取请求包与返回包进行操作。

![caozuo.png](https://image.3001.net/images/20180514/15262800534449.png!small)

 **小小总结**

本篇先起个开头，其实获取到请求包和响应包可以做很多事情，比如将请求包发给sqlmapAPI
进行被动扫描，也可以将返回包进行Unicode的解码操作等，期待后续的篇章与大家一起分享burp suite的api学习之路。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180514/15262800851264.jpg!small)


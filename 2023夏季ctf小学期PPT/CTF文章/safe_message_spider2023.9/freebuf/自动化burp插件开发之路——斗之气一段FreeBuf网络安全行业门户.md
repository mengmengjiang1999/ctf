作为一个安全从业人员，不会开发也就算了，要是连扫描器轮子也不会造，那么他一定是一个纯纯搬运工，不合格的安全er。平常我们对burp抓包用的最多，用burp插件扫描也是最快的，因此造一个属于自己的轮子出来也是我的目标之一。胖子不是一口就吃成的，这里我们一步步修炼，正式开启扫描气之路。

## 熟悉burp api

首先api（应用程序编程接口）在开发工具中的作用是不言而喻的，用于不同软件组件之间的通信和交互。Burp
Suite提供了一个功能强大的API，允许开发人员通过编写脚本或程序来扩展和自动化Burp
Suite的各种功能，我们在其Extender处看一下它的API有哪些。

![1692435290_64e0835aadaf0d180368b.png!small](https://image.3001.net/images/20230819/1692435290_64e0835aadaf0d180368b.png!small)

保存接口文件，将其保存在某一文件夹下，编辑器打开

![1692435310_64e0836e348080e38e030.png!small](https://image.3001.net/images/20230819/1692435310_64e0836e348080e38e030.png!small)![1692435328_64e083806621997ae6216.png!small](https://image.3001.net/images/20230819/1692435328_64e083806621997ae6216.png!small)

### 接口功能了解

所有的接口都提供了注释，那么我们就可以了解每一个接口它的功能是什么

 **接口名称**

|

 **接口关联**

|

 **作用**  
  
---|---|---  
  
IBurpCollaboratorClientContext

|  
|

表示Burp Collaborator客户端上下文的实例，可用于生成Burp
Collaborator载荷并轮询Collaborator服务器，以获取使用这些载荷导致的任何网络交互。  
  
IBurpCollaboratorInteraction

|  
|

表示与Burp Collaborator服务器发生的网络交互  
  
IBurpExtender

|  
|

所有扩展必须实现这个接口。实现类必须命名为BurpExtender，位于burp包中，必须声明为public，并且必须提供一个默认的（public、无参数的）构造函数。  
  
IBurpExtenderCallbacks

|  
|

这个接口被Burp Suite用来向扩展传递一组回调方法，扩展可以使用这些回调方法在Burp内执行各种操作。  
  
IContextMenuFactory

|  
|

扩展可以实现IBurpExtenderCallbacks接口，并调用其中的方法来添加自定义的上下文菜单项。这些菜单项可以为用户提供扩展自定义的操作，以满足特定的需求和场景。  
  
IContextMenuInvocation

|  
|

在Burp Suite中用于提供上下文菜单调用的详细信息。当用户在Burp
Suite界面中右键单击某个目标（例如请求、响应等），触发了一个由扩展提供的自定义上下文菜单时，Burp
Suite会将上下文菜单调用的相关信息传递给该接口的实现。  
  
ICookie

|  
|

用于保存关于一个HTTP cookie的详细信息  
  
IExtensionHelpers

|  
|

为扩展提供一组工具方法，以便于扩展能够更方便地处理一些常见任务，如解析HTTP请求、响应、处理URL、编码解码数据等。  
  
IExtensionStateListener

|  
|

这个接口的用途在于当扩展执行一些后台线程、打开系统资源（如文件或数据库连接）时，可以通过注册监听器，在扩展被卸载（unloaded）时，及时终止线程、关闭资源，以确保扩展的操作不会在不需要时持续执行，避免资源泄漏和不必要的开销。  
  
IHttpHeader

|  
|

用于保存关于一个HTTP/2头部的详细信息。  
  
IHttpListener

|  
|

允许扩展注册一个HTTP监听器，以便在Burp工具发出请求和响应时得到通知。通过注册这个监听器，扩展可以对这些消息执行自定义的分析或修改操作。这使得扩展能够更深入地观察和干预Burp工具处理的HTTP请求和响应，以满足特定的分析、安全性检查或其他定制需求。  
  
IHttpRequestResponse

|  
|

这个接口提供了方法，使扩展能够检索和更新HTTP消息的详细信息。在处理HTTP请求和响应的过程中，扩展可以使用这些方法来读取和修改消息的各种属性和内容。  
  
IHttpRequestResponsePersisted

|

extends IHttpRequestResponse

|

允许扩展为IHttpRequestResponse对象应用标记。标记可以用于在不同的情况下进行定位，例如在扫描中标记不同的信息，以便后续的处理或显示。

例如，标记可以用于标识在 Intruder 攻击中哪些部分需要替换为负载，或者标记 Scanner
问题中需要强调的部分。通过这种方式，扩展可以更精确地控制和处理不同的操作。  
  
IHttpService

|  
|

用于提供关于一个可以发送HTTP请求的HTTP服务的详细信息。  
  
IInterceptedProxyMessage

|  
|

这个接口允许扩展通过注册一个代理监听器，从 Burp Proxy 接收有关被拦截的 HTTP
消息的详细信息。扩展可以通过这些信息来分析、处理或修改代理的交互过程。  
  
IIntruderAttack

|  
|

用于保存有关 Intruder 攻击的详细信息。  
  
IIntruderPayloadGenerator

|  
|

这个接口允许扩展创建自定义的 Intruder 负载生成器，以便在 Intruder
攻击中生成定制的负载。扩展需要实现这个接口来定义如何生成负载，然后在注册的工厂中使用这个接口的实例来为新的 Intruder 攻击生成负载。  
  
IIntruderPayloadGeneratorFactory

|  
|

允许扩展创建自定义的 Intruder 负载生成器工厂。扩展可以通过实现这个接口并注册工厂，以便在 Intruder
攻击中生成定制的负载。通过这个机制，扩展可以为 Intruder 提供自定义的负载生成策略，以满足特定的攻击需求。  
  
IIntruderPayloadProcessor

|  
|

允许扩展创建自定义的 Intruder 负载处理器。通过实现这个接口并注册处理器，扩展可以在 Intruder
攻击过程中对生成的负载进行自定义的处理操作。这样，扩展可以实现特定的负载修改逻辑，以满足不同的攻击场景和需求。  
  
IMenuItemHandler

|

该接口被标记为过时

|

这个接口的作用是允许扩展注册自定义的上下文菜单项。但是由于这个接口已被标记为过时，不再建议使用它，而是建议使用 IContextMenuFactory
接口来实现相同的功能。  
  
IMessageEditor

|  
|

允许扩展获取Burp的HTTP消息编辑器实例，以便在扩展的用户界面中使用。通过这个编辑器，扩展可以展示和修改Burp的HTTP请求和响应，实现自定义的消息查看和编辑功能，以适应特定的需求和场景。  
  
IMessageEditorController

|  
|

允许在 Burp 的消息编辑器中获取有关当前显示的消息的详细信息，以便在进行自定义处理、导出或其他操作时使用。扩展可以通过实现
IMessageEditorController 接口来为编辑器提供有关当前消息的附加信息和操作。  
  
IMessageEditorTab

|  
|

对于注册了 IMessageEditorTabFactory 的扩展，必须返回这个接口的实例。Burp 将使用这些实例在其 HTTP
消息编辑器中创建自定义选项卡。  
  
IMessageEditorTabFactory

|  
|

这个接口允许扩展为 Burp 的 HTTP 消息编辑器注册一个自定义选项卡的工厂。通过实现这个接口和注册工厂，扩展可以在 Burp 的 HTTP
编辑器中提供自定义的渲染或编辑功能，以满足特定的消息处理需求。  
  
IParameter

|  
|

用于保存关于一个HTTP请求参数的详细信息。  
  
IProxyListener

|  
|

这个接口允许扩展注册一个自定义的代理监听器，以便在代理工具处理请求和响应时获得通知。通过注册这个监听器，扩展可以实现对请求和响应的自定义处理，还可以控制Burp界面中消息的拦截操作，以适应特定的需求和场景。  
  
IRequestInfo

|  
|

这个接口允许扩展分析HTTP请求并检索请求的关键详细信息。通过获取一个 IRequestInfo
对象，扩展可以了解请求的HTTP方法、URL、头部和参数等关键信息，以便在扩展中进行进一步的处理和分析。  
  
IResponseInfo

|  
|

这个接口允许扩展分析HTTP响应并检索响应的关键细节。通过获取一个 IResponseInfo
对象，扩展可以了解响应的状态码、头部、内容类型和长度等关键信息，以便在扩展中进行进一步的处理和分析。  
  
IResponseKeywords

|  
|

用于表示一组HTTP响应中出现的关键字的计数  
  
IResponseVariations

|  
|

用于表示一组HTTP响应之间在不同属性方面的变化。  
  
IScanIssue

|  
|

这个接口允许扩展获取Scanner问题的详细信息。扩展可以通过注册监听器或调用方法来获得已有问题的详细信息，还可以自定义问题并添加到扫描结果中。注意，扩展生成的问题描述和其他文本受到HTML白名单的限制，只允许格式化标签和简单的超链接。  
  
IScannerCheck

|  
|

这个接口允许扩展创建自定义的Scanner检查，以便在扫描过程中进行主动或被动扫描。

扩展可以通过实现这个接口并注册检查，来添加特定的扫描逻辑。在扫描时，Burp将会调用注册的检查来执行扫描操作，并根据检查的结果报告任何发现的扫描问题。  
  
IScannerInsertionPoint

|  
|

这个接口允许定义用于主动扫描检查的插入点。扩展可以通过注册扫描检查来获取这个接口的实例，然后在扫描中使用这些插入点来测试不同的漏洞情况。  
  
IScannerInsertionPointProvider

|  
|

这个接口的作用是允许扩展实现自定义的Scanner插入点提供者工厂。通过实现这个接口和注册工厂，扩展可以为Burp的扫描检查提供特定的插入点，以增加扫描的灵活性和适用性。  
  
IScannerListener

|  
|

允许扩展注册一个自定义的Scanner监听器，以便在Scanner工具报告新问题时获得通知。通过注册这个监听器，扩展可以执行自定义的问题分析、记录或其他操作，以满足特定的需求和场景。  
  
IScanQueueItem

|  
|

这个接口允许扩展获取Burp Scanner主动扫描队列中项目的详细信息。扩展可以通过调用扫描方法来触发主动扫描并获取项目的引用，以便进一步处理扫描结果。  
  
IScopeChangeListener

|  
|

允许扩展注册一个自定义的范围变更监听器。通过注册这个监听器，扩展可以在Burp的全局目标范围发生变更时获得通知。这使得扩展可以在范围变更时执行一些特定的操作，例如更新相关的设置或执行某些操作。  
  
ISessionHandlingAction

|  
|

这个接口的作用是允许扩展注册一个自定义的会话处理操作。通过注册这个操作，扩展可以在Burp的会话处理规则界面中创建自定义操作，供用户选择并在会话处理期间使用。这使得扩展可以为会话处理规则添加自定义的操作逻辑，以适应不同的会话处理需求。  
  
ITab

|  
|

用于向Burp提供自定义选项卡的详细信息，以便将其添加到Burp的用户界面中，使用类似于
IBurpExtenderCallbacks.addSuiteTab() 的方法。  
  
ITempFile

|  
|

用于保存通过调用 IBurpExtenderCallbacks.saveToTempFile() 创建的临时文件的详细信息。  
  
ITextEditor

|  
|

允许扩展获取Burp的原始文本编辑器实例，以便在扩展的用户界面中实现自定义的文本编辑功能。通过这个编辑器，扩展可以展示和修改文本内容，实现自定义的文本处理功能，以满足特定的需求和场景。  
  
## 插件编写

### 编写第一个 Burp Suite 插件

  * 新建burpExtender项目，把burp的api接口和要写的插件类都放在一个包下

![1692435582_64e0847e7093ed1f80742.png!small](https://image.3001.net/images/20230819/1692435582_64e0847e7093ed1f80742.png!small)

  * 既然了解了每一个api的作用，那么我们在编写插件的功能时想要实现什么功能就去实现对应的接口就可以了。下面这个代码就是一个框架，我们要编写的插件就是在框架里面去编写

    
    
    package burp;
    
    /*1.所有扩展必须实现IBurpExtender接口。
      2.实现类必须命名为BurpExtender，位于burp包中，必须声明为public，
    */
    
    public class BurpExtender implements IBurpExtender {
        //实现IBurpExtender就必须实现里面的registerExtenderCallbacks
        @Override
        public void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks) {
    
        }
    
    }
    

![1692435601_64e08491c652be1c25b38.png!small](https://image.3001.net/images/20230819/1692435601_64e08491c652be1c25b38.png!small)

### Hello World

  * 万事开头难，明知难就不要死磕，先copy经典的代码再尝试自己写一个简单的代码，让自己有点成就感才有学下去的动力。编写插件就和学编程语言一样，第一个代码大概率都是"hello world!"。

    
    
    package burp;
    
    import burp.IBurpExtender;
    import burp.IBurpExtenderCallbacks;
    
    import java.io.PrintWriter;
    
    /*1.所有扩展必须实现IBurpExtender接口。
      2.实现类必须命名为BurpExtender，位于burp包中，必须声明为public，
    */
    public class BurpExtender implements IBurpExtender {
        //实现IBurpExtender就必须实现里面的registerExtenderCallbacks
        @Override
        public void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks) {
            //设置扩展在burp中的名称
            callbacks.setExtensionName("Hello World");
    
            //获取输出和错误流
            PrintWriter stdout=new PrintWriter(callbacks.getStdout(),true);
            PrintWriter stderr=new PrintWriter(callbacks.getStderr(),true);
    
            //向输出和错误流写入信息
            stdout.println("Hello output");
            stderr.println("Hello errors");
    
            //发布警报到 Burp 的警报标签页
            callbacks.issueAlert("Hello alerts");
    
            //抛出运行时异常
            throw new RuntimeException("Hello exception");
        }
    }

### 导入burp插件

  * 然后我们把整个项目打成jar包

![1692435624_64e084a8c3d3fd3f25b9b.png!small](https://image.3001.net/images/20230819/1692435624_64e084a8c3d3fd3f25b9b.png!small)

* * *

![1692435642_64e084ba41226c8184d9f.png!small](https://image.3001.net/images/20230819/1692435642_64e084ba41226c8184d9f.png!small)

* * *

![1692435661_64e084cdc1de674e43695.png!small](https://image.3001.net/images/20230819/1692435661_64e084cdc1de674e43695.png!small)![1692435679_64e084df60938d9875ef3.png!small](https://image.3001.net/images/20230819/1692435679_64e084df60938d9875ef3.png!small)

* * *

  * 此时已经成功构建为jar包

![1692435703_64e084f7e4b6aa38853b7.png!small](https://image.3001.net/images/20230819/1692435703_64e084f7e4b6aa38853b7.png!small)![1692435716_64e08504ed5af261cf1e1.png!small](https://image.3001.net/images/20230819/1692435716_64e08504ed5af261cf1e1.png!small)

  * burp导入插件

![1692435789_64e0854d35c18d258690c.png!small](https://image.3001.net/images/20230819/1692435789_64e0854d35c18d258690c.png!small)

* * *

  * 输出处显示Hello output

![1692435805_64e0855dc96264e2e6f14.png!small](https://image.3001.net/images/20230819/1692435805_64e0855dc96264e2e6f14.png!small)

  * 错误报运行时异常

![1692435896_64e085b89b9cc5cd13110.png!small](https://image.3001.net/images/20230819/1692435896_64e085b89b9cc5cd13110.png!small)

## 参考链接+代码链接：

相关参考链接和自己的代码也都附上了。

https://portswigger.net/blog/writing-your-first-burp-suite-extension

https://github.com/Xiao-XuXu/burpExtender


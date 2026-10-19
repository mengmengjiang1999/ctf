# Jackson

Jackson是一个开源的Java序列化和反序列化工具，可以将Java对象序列化为XML或JSON格式的字符串，以及将XML或JSON格式的字符串反序列化为Java对象。由于其使用简单，速度较快，且不依靠除JDK外的其他库，被众多用户所使用。

**依赖**

    
    
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.7.9</version>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-core</artifactId>
        <version>2.7.9</version>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-annotations</artifactId>
        <version>2.7.9</version>
    </dependency>
    

## Jackson序列化与反序列化

Jackson提供了ObjectMapper.writeValueAsString()和ObjectMapper.readValue()两个方法来实现序列化和反序列化的功能。

**POJO**

    
    
    package Jackson;
    
    public class User {
        private String username;
        private String password;
        public User() {
        }
    
        public User(String username, String password) {
            this.username = username;
            this.password = password;
        }
    
        public String getUsername() {
            return username;
        }
    
        public String getPassword() {
            return password;
        }
    
        public void setUsername(String username) {
            this.username = username;
        }
    
        public void setPassword(String password) {
            this.password = password;
        }
    }
    

**测试**

    
    
    public class JacksonTest {
        public static void main(String[] args) throws IOException {
            User user = new User("Sentiment","123456");
            ObjectMapper mapper = new ObjectMapper();
            String json = mapper.writeValueAsString(user);
            System.out.println(json);
            User other = mapper.readValue(json,User.class);
            System.out.println(other);
        }
    }
    

**结果**

    
    
    {"username":"Sentiment","password":"123456"}
    Jackson.User@67b6d4ae
    

## 多态问题

和fastjson的一样，需要解决多态的问题，比如：Apple是苹果还是苹果手机等，在fastjson中引入了@type字段来解决该问题

而在Jackson中也有与之对应的方法，Jackson实现了JacksonPolymorphicDeserialization机制来解决这个问题，有两种方法：DefaultTyping和@JsonTypeInfo注解。

### DefaultTyping

Jackson提供一个enableDefaultTyping设置，其包含4个值，在`com.fasterxml.jackson.databind.ObjectMapper.DefaultTyping`能看到

  * JAVA_LANG_OBJECT
  * OBJECT_AND_NON_CONCRETE
  * NON_CONCRETE_AND_ARRAYS
  * NON_FINAL

默认情况下，即无参数的enableDefaultTyping是第二个设置，OBJECT_AND_NON_CONCRETE。

    
    
    public ObjectMapper enableDefaultTyping() {
        return enableDefaultTyping(DefaultTyping.OBJECT_AND_NON_CONCRETE);
    }
    

#### JAVA_LANG_OBJECT

当被序列化或反序列化的类里的属性被声明为一个Object类型时，会对该Object类型的属性进行序列化和反序列化，并且明确规定类名。（当然，这个Object本身也得是一个可被序列化的类）

**Demo**

添加一个User2类

    
    
    public class User2 {
        public String name="Tana";
    }
    

在User类里添加一个Object属性，并实现getter、setter、toString等方法

    
    
    private Object object;
    

**测试**

    
    
    public class JacksonTest {
        public static void main(String[] args) throws IOException {
            User user = new User("Sentiment","123456",new User2());
            ObjectMapper mapper = new ObjectMapper();
    
            //JAVA_LANG_OBJECT
            mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.JAVA_LANG_OBJECT);
    
            String json = mapper.writeValueAsString(user);
            System.out.println(json);
            User other = mapper.readValue(json,User.class);
            System.out.println(other);
        }
    }
    

结果

    
    
    //设置JAVA_LANG_OBJECT
    {"username":"Sentiment","password":"123456","object":["Jackson.User2",{"name":"Tana"}]}
    User{username='Sentiment', password='123456', object=Jackson.User2@1753acfe}
    //不设置JAVA_LANG_OBJECT
    {"username":"Sentiment","password":"123456","object":{"name":"Tana"}}
    User{username='Sentiment', password='123456', object={name=Tana}}
    

通过对比可以看出，设置JAVA_LANG_OBJECT后，会对Object属性对象进行了序列化和反序列化操作，会将对应的类名一并输出。

#### OBJECT_AND_NON_CONCRETE

默认选项。除了前面提到的特征，当类里有Interface、AbstractClass类时，对其进行序列化和反序列化。

后边就不举例子了

#### NON_CONCRETE_AND_ARRAYS

除了前面提到的特征外，还支持Array类型。

#### NON_FINAL

支持除声明为final之外的类型。

#### 总结

DefaultTyping类型 | 描述说明  
---|---  
JAVA_LANG_OBJECT | 属性的类型为Object  
OBJECT_AND_NON_CONCRETE | 属性的类型为Object、Interface、AbstractClass  
NON_CONCRETE_AND_ARRAYS | 属性的类型为Object、Interface、AbstractClass、Array  
NON_FINAL | 所有除了声明为final之外的属性  
  
### @JsonTypeInfo注解

@JsonTypeInfo注解是Jackson多态类型绑定的一种方式，支持下面5种类型的取值：

    
    
    @JsonTypeInfo(use = JsonTypeInfo.Id.NONE)
    @JsonTypeInfo(use = JsonTypeInfo.Id.CLASS)
    @JsonTypeInfo(use = JsonTypeInfo.Id.MINIMAL_CLASS)
    @JsonTypeInfo(use = JsonTypeInfo.Id.NAME)
    @JsonTypeInfo(use = JsonTypeInfo.Id.CUSTOM)
    

#### JsonTypeInfo.Id.NONE

NONE所以设不设值效果都一样

#### JsonTypeInfo.Id.CLASS

    
    
    public class User {
        private String username;
        private String password;
    
        @JsonTypeInfo(use = JsonTypeInfo.Id.CLASS)
        private Object object;
    

**结果**

    
    
    //设置前
    {"username":"Sentiment","password":"123456","object":{"name":"Tana"}}
    User{username='Sentiment', password='123456', object={name=Tana}}
    //设置后
    {"username":"Sentiment","password":"123456","object":{"@class":"Jackson.User2","name":"Tana"}}
    User{username='Sentiment', password='123456', object=Jackson.User2@5b275dab}
    

通过对比可以看出，@class方式能指定相关类，并进行相关调用。

#### JsonTypeInfo.Id.MINIMAL_CLASS

结果

    
    
    {"username":"Sentiment","password":"123456","object":{"@c":"Jackson.User2","name":"Tana"}}
    User{username='Sentiment', password='123456', object=Jackson.User2@29774679}
    

跟JsonTypeInfo.Id.CLASS基本一样就是将`@class`缩写成了`@c

#### JsonTypeInfo.Id.NAME

类似于fastjson，加上了@type字段，指明了类名，但是并没有指明包名，因此反序列化时抛出异常，所以此种方式不能进行反序列化

    
    
    {"username":"Sentiment","password":"123456","object":{"@type":"User2","name":"Tana"}}
    Exception in thread "main" com.fasterxml.jackson.databind.JsonMappingException: Could not resolve.......
    

#### JsonTypeInfo.Id.CUSTOM

直接抛出异常，需要用户自定义来使用

## 流程分析

该流程分析是对使用`DefaultTyping`方法的分析，但是用@JsonTypeInfo跟这个是一模一样的

跟fastjson类似，反序列化时会调用对应类的setter和无参构造器，而由于object属性是User2类型的，这里会分别调用User类和User2类的无参构造，简单看下：

### User类

根据一级级调用，到了`vanillaDeserialize()`中，先调用createUsingDefault()函数来调用指定类的无参构造函数来生成类实例：

![](./img/3231715105383561295.png)  
跟进，又调用了__call()方法

![](./img/2005306477947681778.png)  
跟进`call()`，通过newInstance进行了实例化，也就是将User类进行了实例化

    
    
    public final Object call() throws Exception {
        return _constructor.newInstance();
    }

所以继续跟进后，因为被实例化了所以调用了，user类的无参构造

![](./img/299020536096544573.png)  
接着回到`vanillaDeserialize()`，生成实例Bean后，就开始进入do
while循环来循环解析键值对中的属性值并调用deserializeAndSet()函数来解析并设置Bean的属性值：

![](./img/4712319135006141013.png)  
跟进后先调用了`deserialize()`

![](./img/3489748595864289170.png)  
继续跟进，其中第二个if会判断，反序列化内容是否携带类型，这里第一个属性是String类型所以调用到了下边

![](./img/6666934927289750699.png)  
跟进`deserialize()`后，嗲用了`p.getText()`，获取到了p的属性值

    
    
    public String deserialize(JsonParser p, DeserializationContext ctxt) throws IOException
    {
        if (p.hasToken(JsonToken.VALUE_STRING)) {
            return p.getText();
        }
    

最后通过invoke命令调用到了username的setter方法

![](./img/4806751954369424119.png)  
![](./img/5639489719178244862.png)  
password属性也是String类型的，所以通过前边的do
while循环，在调用`deserializeAndSet();`获取对应的值，跟username过程完全一样不看了

### User2类

获取到password的值后，接着进入下一轮循环调用`deserializeAndSet()`，接着调用`deserialize()`判断反序列化数据的携带类型，由于User类中的`object`属性值是user2类的实例化，所以它是一个数组类型调用到了`deserializeWithType()`这里

![](./img/8907823421529764004.png)  
跟进后又调用了`deserializeTypedFromAny()`

![](./img/2540300581607313990.png)  
又调用`_deserialize()`

    
    
    public Object deserializeTypedFromAny(JsonParser jp, DeserializationContext ctxt) throws IOException {
        return _deserialize(jp, ctxt);
    }

跟进后获取了`deser`的类型为BeanDeserializer，接着调用了该类的`deserialize()`

![](./img/6003997188920005392.png)  
接着就回到了流程分析最开始的部分，调用`vanillaDeserialize()`

![](./img/9140041585464883236.png)  
之后就是分别调用User2的构造器或Setter方法，不再往下看了

## Jackson反序列化

在流程分析中可以发现，在调用过程中会分别调用类的控制器和setter方法，所以如果在控制器或setter中构造恶意代码那么就会导致恶意代码执行，在执行前其实有一些前提条件需要满足：

### 前提条件

满足下面三个条件之一即存在Jackson反序列化漏洞：

  * 调用了ObjectMapper.enableDefaultTyping()函数；
  * 对要进行反序列化的类的属性使用了值为JsonTypeInfo.Id.CLASS的@JsonTypeInfo注解；
  * 对要进行反序列化的类的属性使用了值为JsonTypeInfo.Id.MINIMAL_CLASS的@JsonTypeInfo注解；

修改User2，执行calc

    
    
    package Jackson;
    
    public class User2 {
        public String name="Tana";
    
        public User2() {
            System.out.println("User2无参构造");
        }
    
        public void setName(String name) {
            System.out.println("User2.setName");
            this.name = name;
           try {
               Runtime.getRuntime().exec("calc");
           } catch (Exception e) {
               e.printStackTrace();
           }
        }
    }
    

运行后成功执行

![](./img/3791630349287715350.png)

# 总结

其实原理上很简单，就是在Jackson进行反序列化时执行了控制器和setter方法，造成恶意代码执行，但其实这种方式也只是本地调试并不适合作为实际攻击方式，真正的攻击还要看其它Jackson的调用链。


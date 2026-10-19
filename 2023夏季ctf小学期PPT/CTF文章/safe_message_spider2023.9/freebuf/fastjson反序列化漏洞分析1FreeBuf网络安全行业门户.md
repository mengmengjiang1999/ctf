#### 基础

##### 简介

FastJson是alibaba的一款开源JSON解析库，可用于将Java对象转换为其JSON表示形式，也可以用于将JSON字符串转换为等效的Java对象分别通过`toJSONString`和`parseObject/parse`来实现序列化和反序列化

加载依赖包

    
    
    //pom.xml
    <dependency>
        <groupId>com.alibaba</groupId>
        <artifactId>fastjson</artifactId>
        <version>1.2.24</version>
    </dependency>
    

##### 使用

对于序列化的方法`toJSONString()`有多个重载形式

![image-20220322194044636.png](https://image.3001.net/images/20220915/1663239589_632305a5c1bcffdda4b1d.png!small)

  1. `SerializeFeature`: 通过设置多个特性到`FastjsonConfig`中全局使用, 也可以在使用具体方法中指定特性
  2. `SerializeFilter`: 一个接口, 通过配置它的子接口或者实现类就可以以扩展编程的方式实现定制序列化
  3. `SerializeConfig`: 添加特点类型自定义的序列化配置

对于反序列化的方法`parseObject()`也同样有多个重载形式

![image-20220322194624870.png](https://image.3001.net/images/20220915/1663239597_632305ad6b071f3afc38f.png!small)

###### 序列化操作

![image-20220322201741481.png](https://image.3001.net/images/20220915/1663239605_632305b590b28f31e8244.png!small)

可以发现这两个的区别，如果使用了toJSONString()的属性值`SerializerFeature.WriteClassName`，就会在序列化的时候多写入一个`@type`后面跟着的是反序列化的类名

###### 反序列化操作

    
    
    package pers.fastjson;
    
    import com.alibaba.fastjson.JSON;
    import com.alibaba.fastjson.JSONObject;
    
    public class UnSerialTest {
        public static void main(String[] args) {
            String jsonStringWithType = "{\"@type\":\"pers.fastjson.Student\",\"name\":\"RoboTerh\"}";
            String jsonStringWithoutType = "{\"name\":\"RoboTerh\"}";
    
            System.out.println("use JSON.parse with type......");
            Object o1 = JSON.parse(jsonStringWithType);
            System.out.println(o1);
            System.out.println("------------------------------------");
    
            System.out.println("use JSON.parse without type....");
            Object o2 = JSON.parse(jsonStringWithoutType);
            System.out.println(o2);
            System.out.println("-------------------------------------");
    
            System.out.println("use JSON.parseObject with type.......");
            JSONObject o3 = JSON.parseObject(jsonStringWithType);
            System.out.println(o3);
            System.out.println("--------------------------------------");
    
            System.out.println("use JSON.parseObject without type.........");
            JSONObject o4 = JSON.parseObject(jsonStringWithoutType);
            System.out.println(o4);
            System.out.println("----------------------------------------");
    
            System.out.println("use JSON.parseObject without type but hava .Class");
            Student o5 = JSON.parseObject(jsonStringWithoutType, Student.class);
            System.out.println(o5);
        }
    }
    

![image-20220322223443427.png](https://image.3001.net/images/20220915/1663239614_632305be8181631ed9606.png!small)

可以通过结果发现1和5成功反序列化，没成功都是因为没有确定需要反序列化的类

我们可以发现，在引入了`@type`之后，`JSON.parseObject`调用了`getter/setter`方法，`JSON.parse`调用了`setter`方法

当然，其他的方式也是可以调用`getter`方法的，但是有条件限制：

    
    
    条件一、方法名需要长于4
    
    条件二、不是静态方法
    
    条件三、以get字符串开头，且第四个字符需要是大写字母
    
    条件四、方法不能有参数传入
    
    条件五、继承自Collection || Map || AtomicBoolean || AtomicInteger ||AtomicLong
    
    条件六、此getter不能有setter方法（程序会先将目标类中所有的setter加入fieldList列表，因此可以通过读取fieldList列表来判断此类中的getter方法有没有setter）
    

因为`fastjson`存在`autoType`机制, 当用户指定`@type`时, 存在调用恶意`setter`/`getter`的情况,
这就是`fastjson`反序列化漏洞.


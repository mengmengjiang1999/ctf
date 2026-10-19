  * 在进行序列化操作之前，我们还对系统进行压测，通过 `jvisualvm`分析 cpu，线程，垃圾回收情况等；运用火焰图 `async-profiler`分析系统性能，找出程序中占用 CPU 资源时间最长的代码块。
  * 代码放置 GitHub：[https://github.com/nateshao/leetcode/tree/main/source-code/src/main/java/com/nateshao/source/code/serializable](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fgithub.com%2Fnateshao%2Fleetcode%2Ftree%2Fmain%2Fsource-code%2Fsrc%2Fmain%2Fjava%2Fcom%2Fnateshao%2Fsource%2Fcode%2Fserializable)

## 1\. 什么是序列化与反序列化？

聊到序列化与反序列化，先看看这个这个是什么或者是干嘛的

![1688367450_64a2715a940c419f0d8d7.png!small?1688367451083](https://image.3001.net/images/20230703/1688367450_64a2715a940c419f0d8d7.png!small?1688367451083)

> 定义：序列化是指把`对象`转换为`字节序列`的过程；`反序列化`是指把`字节序列`恢复为`对象`的过程；

一般都会知道有两个目的：`对象持久化`和`网络传输`。

  1. 对象持久化。 **实现了数据的持久化，通过序列化可以把数据永久的保存在硬盘上；**
  2. 网络传输。我们知道网络传输的是字节序列，那么 **利用序列化实现远程通信，即在网络上传递对象的字节序列。** （序列化与反序列化则实现了 进程通信间的对象传送，发送方需要把这个 Java 对象转换为字节序列，才能在网络上传送；接收方则需要把字节序列再恢复为 Java 对象）

总结：序列化的目的是将对象变成字节序列，这样一来方便持久化存储到磁盘，避免程序运行结束后对象就从内存里消失，另外字节序列也更便于网络运输和传播

## 2\. 选择序列化技术有哪些维度

这里并不是说哪个是最好，只能说是各有千秋，所以面对不同的背景采用不同的技术方案。

在同等情况下， **编码后的字节数组越大，存储占空间，存储硬件成本高，网络传输时也占带宽，导致系统的吞吐量降低。**

  1. 开发工作量和难度。工作量越少越好对吧，发挥的价值最大。
  2. 性能：需要考虑性能需求，序列化的速度和性能越高越好。
  3. 是否支持跨语言，支持的语言种类是否丰富。
  4. 安全性：对于安全性的需要考量。JDK 序列化可能有卡死线程的漏洞。
  5. 占用空间大小：序列化的结果所占用的空间大小，序列化后的字节数据通常会持久化到硬盘（占用存储资源）或者在网络上传输给其他服务器（占用带宽资源），这个指标当然是越小越好。
  6. 可维护性：技术流行程序，越流行的技术可维护性就越高，维护成本会越低。

## 3\. 为什么采用字节序列 MessagePack，有什么依据？

这个要结合当时的项目背景了。当时的项目痛点是：

  1. 老项目的结构调整比较大，交易性能上不去，所以先采取细节方面的优化。 **MessagePack 是满足性能要求** 。
  2. 老系统业务变化不多， **MessagePack 是满足要求** 。
  3. 序列化反序列化效率高（比 json 快一倍），文件体积小，比 json 小一倍。 **MessagePack 是满足要求**

所以，存在 MessagePack 也有不好的地方，如果是针对业务变化比较多，那就不适合，需要比较不同的版本，然后选择不同版本去解析。

我在京东內部文章有看到，引用的 MessagePack 反序列化出现了一些线上的问题，原因是： **新增了一些字段导致反序列化失败** 。

这里对比了 **JDK (不支持跨语言)，JSON，Protobuf，MessagePack** 几种序列化的方式。

当然，还有其他的 XML、Hessian、Kryo（不支持跨语言）、FST（不支持跨语言）Thrift 等。

## 4.JDK 序列化

JDK 序列化是 Java 默认自带的序列化方式。在 Java 中，一个对象要想实现序列化，实现 `Serializable`接口或者
`Externalizable`接口即可。其中 `Externalizable`接口继承自 `Serializable`接口。

    
    
    public class Person implements Serializable {
        private static final long serialVersionUID = 1L;
        private String name = null;
        private Integer age = null;
        private SerializeDemo01.Sex sex;
    	//....
    }
    

`serialVersionUID`版本控制的作用

  1. 序列化的时候 `serialVersionUID`也会被写入二进制序列
  2. 反序列化时会检查 `serialVersionUID`是否和当前类的 `serialVersionUID`一致。不一致则会抛出 `InvalidClassException`异常（序列化之后给类增加字段再反序列化的时候就会报错）

 **serialVersionUID 必须保证实体类在序列化前后严格一致，否则将会导致无法反序列化。**

 **JDK 默认的序列化机制** 。需要实现 java.io.Serializable 接口

  1.  **序列化后的码流太大：jdk 序列化机制编码后的二进制数组大小竟然是二进制编码的 5.29 倍。**
  2. 不支持跨语言平台调用， 性能较差（序列化后字节数组体积大）
  3.  **序列化性能太低** ：java 序列化的性能只有二进制编码的 6.17% 左右，Java 原生序列化的性能实在太差。

JDK 默认的序列化机制很差。所以我们通常不会选择 Java 默认序列化这种

## 5.JSON 序列化

json 格式也是常见的一种，但是在 json 在解析的时候非常耗时，而且 json 结构非常占内存。JSON 不适合存数字，特别是 DOUBLE

这里基于 Fastjson ，加载 maven 依赖

    
    
    <dependency>
        <groupId>com.alibaba</groupId>
        <artifactId>fastjson</artifactId>
        <version>1.2.70</version>
    </dependency>
    

**序列化对象**

利用 JSON.toJSONString 方法序列化对象：

    
    
    UserVO user = ...;String text = JSON.toJSONString(user);
    

**序列化数组**

利用 JSON.toJSONString 方法序列化数组：

    
    
    UserVO[] users = ...;String text = JSON.toJSONString(users);
    

**序列化集合**

利用 JSON.toJSONString 方法序列化集合（继承至 Collection，比如 List、Set 等集合）：

    
    
    List<UserVO> userList = ...;String text = JSON.toJSONString(userList);
    

**序列化映射**

利用 JSON.toJSONString 方法序列化映射：

    
    
    Map<Long, UserVO> userMap = ...;String text = JSON.toJSONString(userMap, SerializerFeature.MapSortField);
    

其中，为了保证每次序列化的映射字符串一致，需要指定序列化参数 MapSortField 进行排序。

 **序列化模板对象**

利用 JSON.toJSONString 方法序列化模板对象：

    
    
    Result<UserVO> result = ...;String text = JSON.toJSONString(result);
    

#### 代码

    
    
    package com.nateshao.source.code.serializable.json_Serializable.serializable;
    
    import com.alibaba.fastjson.annotation.JSONField;
    /**
     * @date Created by 邵桐杰 on 2023/2/25 17:11
     * @微信公众号 千羽的编程时光
     * @博客 https://nateshao.gitlab.io
     * @GitHub https://github.com/nateshao
     * Description:
     */
    public class User {
        /**
         * @JSONField 作用：自定义对象属性所对应的 JSON 键名
         * @JSONField 的作用对象:
         * 1. Field
         * 2. Setter 和 Getter 方法
         * 注意：
         * 1. 若属性是私有的，必须要有 set 方法，否则反序列化会失败。
         * 2. 若没有 @JSONField 注解，则直接使用属性名。
         */
        @JSONField(name = "NAME")
        private String name;
        @JSONField(name = "AGE")
        private int age;
    
        public User(String name, int age) {
            this.name = name;
            this.age = age;
        }
    
        public String getName() {
            return name;
        }
    
        public void setName(String name) {
            this.name = name;
        }
    
        public int getAge() {
            return age;
        }
    
        public void setAge(int age) {
            this.age = age;
        }
    }
    

#### 序列化 ObjectTest

    
    
    package com.nateshao.source.code.serializable.json_Serializable.serializable;
    
    import com.alibaba.fastjson.JSON;
    import org.junit.jupiter.api.BeforeAll;
    import org.junit.jupiter.api.DisplayName;
    import org.junit.jupiter.api.Test;
    
    import java.util.ArrayList;
    import java.util.HashMap;
    import java.util.List;
    import java.util.Map;
    
    /**
     * @date Created by 邵桐杰 on 2023/2/25 17:12
     * @微信公众号 千羽的编程时光
     * @博客 https://nateshao.gitlab.io
     * @GitHub https://github.com/nateshao
     * Description:
     */
    public class ObjectTest {
        private static List<User> userList = new ArrayList<User>();
    
        @BeforeAll
        public static void setUp() {
            userList.add(new User("千羽", 18));
            userList.add(new User("千寻", 19));
        }
    
        @DisplayName("序列化对象")
        @Test
        public void testObjectToJson() {
            String userJson = JSON.toJSONString(userList.get(0));
            System.out.println(userJson);  // {"AGE":18,"NAME":"千羽"}
        }
    
        @DisplayName("序列化集合")
        @Test
        public void testListToJson() {
            String userListJson = JSON.toJSONString(userList);
            System.out.println(userListJson);  // [{"AGE":18,"NAME":"千羽"},{"AGE":19,"NAME":"千寻"}]
        }
    
        @DisplayName("序列化数组")
        @Test
        public void testArrayToJson() {
            User[] userArray = new User[5];
            userArray[0] = new User("zhangsan", 20);
            userArray[1] = new User("lisi", 21);
            String userArrayJson = JSON.toJSONString(userArray);
            System.out.println(userArrayJson);  // [{"AGE":20,"NAME":"zhangsan"},{"AGE":21,"NAME":"lisi"},null,null,null]
        }
    
        @DisplayName("序列化映射")
        @Test
        public void testMapToJson() {
            Map<Integer, User> userMap = new HashMap<Integer, User>();
            userMap.put(1, new User("xiaotie", 10));
            userMap.put(2, new User("xiaoliu", 11));
            String userMapJson = JSON.toJSONString(userMap);
            System.out.println(userMapJson);  // {1:{"AGE":10,"NAME":"xiaotie"},2:{"AGE":11,"NAME":"xiaoliu"}}
        }
    }
    

#### 反序列化 UN_ObjectTest

    
    
    package com.nateshao.source.code.serializable.json_Serializable.un_serializable;
    
    import com.alibaba.fastjson.JSON;
    import com.alibaba.fastjson.TypeReference;
    import org.junit.jupiter.api.DisplayName;
    import org.junit.jupiter.api.Test;
    
    import java.util.Arrays;
    import java.util.List;
    import java.util.Map;
    import java.util.Set;
    
    /**
     * @date Created by 邵桐杰 on 2023/2/25 17:16
     * @微信公众号 千羽的编程时光
     * @博客 https://nateshao.gitlab.io
     * @GitHub https://github.com/nateshao
     * Description:
     */
    public class UN_ObjectTest {
        @DisplayName("反序列化对象")
        @Test
        public void testJsonToObject() {
            String text = "{"age":18,"name":"千羽"}";
            User user = JSON.parseObject(text, User.class);
            System.out.println(user);  // User{name='千羽', age=18}
        }
    
        @DisplayName("反序列化数组")
        @Test
        public void testJsonToArray() {
            String text = "[{"age":18,"name":"千羽"}, {"age":19,"name":"千寻"}]";
            User[] users = JSON.parseObject(text, User[].class);
            System.out.println(Arrays.toString(users));  // [User{name='千羽', age=18}, User{name='千寻', age=19}]
        }
    
        @DisplayName("反序列化集合")
        @Test
        public void testJsonToCollection() {
            String text = "[{"age":18,"name":"千羽"}, {"age":19,"name":"千寻"}]";
            // List 集合
            List<User> userList = JSON.parseArray(text, User.class);
            System.out.println(Arrays.toString(userList.toArray()));  // [User{name='千羽', age=18}, User{name='千寻', age=19}]
            // Set 集合
            Set<User> userSet = JSON.parseObject(text, new TypeReference<Set<User>>() {
            });
            System.out.println(Arrays.toString(userSet.toArray()));  // [User{name='千寻', age=19}, User{name='千羽', age=18}]
        }
    
        @DisplayName("反序列化映射")
        @Test
        public void testJsonToMap() {
            String text = "{1:{"age":18,"name":"千羽"}, 2:{"age":19,"name":"千寻"}}";
            Map<Integer, User> userList = JSON.parseObject(text, new TypeReference<Map<Integer, User>>() {
            });
            for (Integer i : userList.keySet()) {
                System.out.println(userList.get(i));
            }
            /*
                User{name='千羽', age=18}
                User{name='千寻', age=19}
             */
        }
    }
    

json 序列化总结

  *  **好处**

    1. 简单易用开发成本低
    2. 跨语言
    3. 轻量级数据交换
    4. 非冗长性（对比 xml 标签简单括号闭环）
  *  **缺点**

    1. 体积大，影响高并发
    2. 无版本检查，自己做兼容
    3. 片段的创建和验证过程比一般的 XML 复杂
    4. 缺乏命名空间导致信息混合

## 6.Protobuf

Protobuf
是谷歌推出的，是一种语言无关、平台无关、可扩展的序列化结构数据的方法，它可用于通信协议、数据存储等。序列化后体积小，一般用于对传输性能有较高要求的系统。前期需要额外配置环境变量，学习他的语法也是需要时间。

但是要 **使用 Protobuf 会相对来说麻烦一些，因为他有自己的语法，有自己的编译器，如果需要用到的话必须要去投入成本在这个技术的学习中** 。

Protobuf 有个缺点就是传输的每一个类的结构都要生成相对应的 proto 文件，如果某个类发生修改，还要重新生成该类对应的 proto
文件。另外，Protobuf 对象冗余，字段很多，生成的类较大，占用空间。维护成本较高。

    
    
    // 声明语法，不显示声明默认是2.0的语法。
    syntax = "proto3";
    // 指定模板类的包路径
    option java_package = "com.test.basic.java.serialize.proto.dto";
    // 指定模板类的名称，名称必须是有实际业务意义的
    option java_outer_classname = "UserProto";
    
    // 定义用户对象
    message User {
      // 名字
      string name = 1;
      // 年龄
      int32 age = 2;
    }
    // 声明语法，不显示声明默认是2.0的语法。
    syntax = "proto3";
    // 指定模板类的包路径
    option java_package = "com\nateshao\source\code\serializable\protobuf_Serializable\User.proto";
    // 指定模板类的名称，名称必须是有实际业务意义的
    option java_outer_classname = "UserProto";
    
    // 定义用户对象
    message User {
      // 名字
      string name = 1;
      // 年龄
      int32 age = 2;
    }
    

## 7.MessagePack（推荐）

![1688367464_64a2716883e9233734eca.png!small?1688367465033](https://image.3001.net/images/20230703/1688367464_64a2716883e9233734eca.png!small?1688367465033)

  1. 序列化反序列化效率高（比 json 快一倍），文件体积小，比 json 小一倍。
  2. 兼容 json 数据格式
  3. 跨语言，多语言支持 (超多)

![1688367471_64a2716f2c0bb237050f8.png!small?1688367471759](https://image.3001.net/images/20230703/1688367471_64a2716f2c0bb237050f8.png!small?1688367471759)

不好的地方：

  1. 缺乏复杂模型支持。msgpack 对复杂的数据类型（List、Map）支持的不够，序列化没有问题，但是反序列化回来就很麻烦，尤其是对于 java 开发人员。
  2. 维护成本较高。msgpack 通过 value 的顺序来定位属性的，需要在不同的语言中都要维护同样的模型以及模型中属性的顺序。
  3. 不支持模型嵌套。msgpack 无法支持在模型中包含和嵌套其他自定义的模型（如 weibo 模型中包含 comment 的列表）。

#### 上手

通过配置 msgpack 的 maven 依赖

    
    
    <dependency>
        <groupId>org.msgpack</groupId>
        <artifactId>msgpack</artifactId>
        <version>0.6.12</version>
    </dependency>
    

封装 MsgPackTemplate 抽象类，对原有 msgpack 进行二次加工，比如 int，Short，Byte，BigDecimal 进行 read
和 write 处理

 **MsgPackTemplate.java**

    
    
    package com.nateshao.source.code.serializable.msgpack_Serializable;
    
    import java.io.IOException;
    import java.math.BigDecimal;
    import java.util.Date;
    
    import org.msgpack.packer.Packer;
    import org.msgpack.template.CharacterTemplate;
    import org.msgpack.template.Template;
    import org.msgpack.unpacker.Unpacker;
    /**
     * @date Created by 邵桐杰 on 2023/2/25 23:11
     * @微信公众号 千羽的编程时光
     * @博客 https://nateshao.gitlab.io
     * @GitHub https://github.com/nateshao
     * Description:
     */
    public abstract class MsgPackTemplate <T> implements Template<T> {
    
        public void write(Packer pk, T v) throws IOException {
            write(pk, v, false);
        }
    
        public T read(Unpacker u, T to) throws IOException {
            return read(u, to, false);
        }
    
        public BigDecimal readBigDecimal(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
    
            String temp = u.readString();
            if (temp != null) {
                return new BigDecimal(temp);
            }
            return null;
        }
    
        public Date readDate(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
    
            long temp = u.readLong();
            if (temp > 0) {
                return new Date(temp);
            }
            return null;
        }
    
        public String readString(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
            return u.readString();
        }
    
        public Integer readInteger(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
            return u.readInt();
        }
    
        public Byte readByte(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
            return u.readByte();
        }
    
        public Short readShort(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
            return u.readShort();
        }
    
        public Float readFloat(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
            return u.readFloat();
        }
    
        public Double readDouble(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
            return u.readDouble();
        }
    
        public Character readCharacter(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
            return u.read(CharacterTemplate.getInstance());
    
        }
    
        public Long readLong(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
            return u.readLong();
        }
    
        public Boolean readBoolean(Unpacker u) throws IOException {
            if (u.trySkipNil()) {
                return null;
            }
            return u.readBoolean();
        }
    
    
    
    
        public void writeBigDecimal(Packer pk, BigDecimal v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.toString());
            }
        }
    
        public void writeDate(Packer pk, Date v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.getTime());
            }
        }
    
        public void writeString(Packer pk, String v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v);
            }
        }
    
        public void writeInt(Packer pk, int v) throws IOException {
            pk.write(v);
        }
    
        public void writeInteger(Packer pk, Integer v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.intValue());
            }
        }
    
        public void writeByte(Packer pk, Byte v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.byteValue());
            }
        }
    
        public void writeShort(Packer pk, Short v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.shortValue());
            }
        }
    
        public void writeFloat(Packer pk, Float v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.floatValue());
            }
        }
    
        public void writeDouble(Packer pk, Double v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.doubleValue());
            }
        }
    
        public void writeCharacter(Packer pk, Character v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.charValue());
            }
    
        }
    
        public void writeLong(Packer pk, Long v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.longValue());
            }
        }
    
        public void writeLong(Packer pk, long v) throws IOException {
            pk.write(v);
        }
    
        public void writeBoolean(Packer pk, Boolean v) throws IOException {
            if (v == null) {
                pk.writeNil();
            } else {
                pk.write(v.booleanValue());
            }
        }
    }
    

然后针对实体类进行读和写的序列化与反序列化操作。

 **User.java**

    
    
    package com.nateshao.source.code.serializable.msgpack_Serializable;
    @Data
    @ToString
    @AllArgsConstructor
    @NoArgsConstructor
    public class User {
        private static final long serialVersionUID = 4719921525393585541L;
        protected String id;
        private String userID;
        private String type;
        private BigDecimal rate;
        private Date createTime;
        private Date UpdateTime;
    }
    

**UserTemplate.java**

    
    
    package com.nateshao.source.code.serializable.msgpack_Serializable;
    
    import org.msgpack.packer.Packer;
    import org.msgpack.unpacker.Unpacker;
    
    import java.io.IOException;
    
    /**
     * protected String id;
     * private String userID;
     * private String type;
     * private BigDecimal rate;
     * private Date createTime;
     * private Date UpdateTime;
     */
    public class UserTemplate extends MsgPackTemplate<User> {
        public void write(Packer packer, User user, boolean b) throws IOException {
            if (user == null) {
                packer.write(user);
                return;
            }
            // 字段保持一致
            writeString(packer, user.id);
            writeString(packer, user.getUserID());
            writeString(packer, user.getType());
            writeBigDecimal(packer, user.getRate());
            writeDate(packer, user.getCreateTime());
            writeDate(packer, user.getUpdateTime());
    
        }
    
        public User read(Unpacker unpacker, User user, boolean req) throws IOException {
            if (!req && unpacker.trySkipNil()) {
                return null;
            }
            if (unpacker == null) return new User();
            user.setId(readString(unpacker));
            user.setUserID(readString(unpacker));
            user.setType(readString(unpacker));
            user.setRate(readBigDecimal(unpacker));
            user.setCreateTime(readDate(unpacker));
            user.setUpdateTime(readDate(unpacker));
            return user;
        }
    }
    

参考文献：

  * 官网：MessagePack: It's like JSON. but fast and small：[https://msgpack.org/](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fmsgpack.org%2F))
  * msgpack-java：[https://github.com/msgpack/msgpack-java](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fgithub.com%2Fmsgpack%2Fmsgpack-java)
  * MessagePack for C＃译文：快速序列化组件 MessagePack 介绍 - 晓晨 Master - 博客园：[https://www.cnblogs.com/stulzq/p/8039933.html](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fwww.cnblogs.com%2Fstulzq%2Fp%2F8039933.html)
  * 原理分析和使用：[https://www.jianshu.com/p/8c24bef40e2f](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fwww.jianshu.com%2Fp%2F8c24bef40e2f)

  1. [https://blog.csdn.net/wzngzaixiaomantou/article/details/123031809](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fblog.csdn.net%2Fwzngzaixiaomantou%2Farticle%2Fdetails%2F123031809)
  2. [https://blog.csdn.net/weixin_44299027/article/details/129050484](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fblog.csdn.net%2Fweixin_44299027%2Farticle%2Fdetails%2F129050484)
  3. [https://www.cnblogs.com/juno3550/p/15431623.html](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fwww.cnblogs.com%2Fjuno3550%2Fp%2F15431623.html)
  4. Protobuf：[https://blog.csdn.net/wxw1997a/article/details/116755542](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fblog.csdn.net%2Fwxw1997a%2Farticle%2Fdetails%2F116755542)

> 作者：京东零售 邵桐杰
>
> 来源：京东云开发者社区


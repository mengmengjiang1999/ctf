### java反射

上次的java反射没怎么懂，再来学习一下。

###### 概念

Java反射是指在程序运行期间对于类的属性、方法、构造方法等进行动态访问和操作的机制。通过Java反射API，程序能够在运行期获取类的信息，操作类的属性、方法、构造方法，创建类的对象等。

不适用new创建对象而访问类中方法的过程即可成为反射

###### 包

java反射的相关类位于`java.lang.reflect.*;`包

###### 为什么要用反射

  * 获取任意类的名称、package信息、所有属性、方法、注解、类型、类加载器等
  * 获取任意对象的属性，并且能改变对象的属性
  * 调用任意对象的方法
  * 判断任意一个对象所属的类
  * 实例化任意一个类的对象
  * 通过反射我们可以实现动态装配，降低代码的耦合度,动态代理等。

#### Class类

###### 相关类

java.lang.Class 代表整个字节码。代表一个类型，代表整个类。  
java.lang.reflect.Method 代表字节码中的方法字节码。代表类中的方法。  
java.lang.reflect.Constructor 代表字节码中的构造方法字节码。代表类中的构造方法。  
java.lang.reflect.Field 代表字节码中的属性字节码。代表类中的成员变量（静态变量+实例变量）

注：必须先获取Class才能获取Method、Constructor、Field

那么如何获取Class实例呢？

###### 为什么要获取Class实例

  1. 实例化对象：通过 Class 对象可以创建一个类的实例，从而调用该类的属性和方法。
  2. 获取类的信息：通过 Class 对象可以获取类的修饰符、字段、方法、构造器、注解等信息，从而可以动态地获取类的信息并进行操作。
  3. 执行方法：通过 Class 对象可以获取类中的方法并调用，从而动态地执行方法。
  4. 进行类型检查：通过 Class 对象可以进行类型检查，从而保证程序的类型安全。

###### 获取Class类实例的三种方法

Class.forName(“完整类名带包名”)

    
    
    Class<?> cls = Class.forName("java.util.ArrayList");
    

对象.getClass()

    
    
    Object obj = new String("Hello World");
    Class<? extends Object> objClass = obj.getClass();
    

类名.class

    
    
    Class<String> strClass = String.class;
    

###### Class类常用方法

**getFields()——** 获得类的public类型的属性。

**getDeclaredFields()——** 获得类的所有属性

**getField(String name)——** 获得类的指定属性

**getMethods()——** 获得类的public类型的方法

**getMethod (String name,Class [] args)——** 获得类的指定方法

**getConstrutors()——** 获得类的public类型的构造方法

**getConstrutor(Class[] args)——** 获得类的特定构造方法

**newInstance()——** 通过类的无参构造方法创建对象

**getName()——** 获得类的完整名字

**getPackage()——** 获取此类所属的包

**getSuperclass()——** 获得此类的父类对应的Class对象

###### 通过反射实例化对象

    
    
    对象.newInstance()
    

没有公共的无参构造函数，newInstance()方法就会抛出InstantiationException异常

其他方法

使用getDeclaredConstructor()方法获取特定的构造函数，并使用newInstance(Object...
args)方法传递参数来创建对象实例

    
    
    Class<MyClass> cls = MyClass.class;
    Constructor<MyClass> constructor = cls.getDeclaredConstructor(int.class, String.class);
    MyClass myObj = constructor.newInstance(42, "Hello");
    

###### Class.forName导致类加载

如果你只是希望一个类的 **静态代码块** 执行，其它代码一律不执行，可以使用：

    
    
    Class.forName("完整类名");
    

这个方法的执行会导致 **类加载** ，类加载时，静态代码块执行。

##### 反射Filed【反射/反编译一个类的属性】

###### Class类方法

public T newInstance() 创建对象  
public String getName() 返回完整类名带包名  
public String getSimpleName() 返回类名  
public Field[] getFields() 返回类中public修饰的属性  
public Field[] getDeclaredFields() 返回类中所有的属性  
public Field getDeclaredField(String name) 根据属性名name获取指定的属性  
public native int getModifiers()
获取属性的修饰符列表,返回的修饰符是一个数字，每个数字是修饰符的代号【一般配合Modifier类的toString(int x)方法使用】  
public Method[] getDeclaredMethods() 返回类中所有的实例方法  
public Method getDeclaredMethod(String name, Class<?>… parameterTypes)
根据方法名name和方法形参获取指定方法  
public Constructor<?>[] getDeclaredConstructors() 返回类中所有的构造方法  
public Constructor getDeclaredConstructor(Class<?>… parameterTypes)
根据方法形参获取指定的构造方法

public native Class<? super T> getSuperclass() 返回调用类的父类  
public Class<?>[] getInterfaces() 返回调用类实现的接口集合

###### Field类方法

public String getName() 返回属性名  
public int getModifiers()
获取属性的修饰符列表,返回的修饰符是一个数字，每个数字是修饰符的代号【一般配合Modifier类的toString(int x)方法使用】  
public Class<?> getType() 以Class类型，返回属性类型【一般配合Class类的getSimpleName()方法使用】  
public void set(Object obj, Object value) 设置属性值  
public Object get(Object obj) 读取属性值

###### 给属性赋值和读

直接赋值

    
    
    对象.属性=值
    
    对象.属性

通过反射赋值

    
    
    属性.set(对象, 值);
    
    属性.get(对象);
    
    
    /*
    必须掌握：
        怎么通过反射机制访问一个java对象的属性？
            给属性赋值set
            获取属性的值get
     */
    class ReflectTest07{
        public static void main(String[] args) throws ClassNotFoundException, InstantiationException, IllegalAccessException, NoSuchFieldException {
            //不使用反射机制给属性赋值
            Student student = new Student();
            /**给属性赋值三要素：给s对象的no属性赋值1111
             * 要素1：对象s
             * 要素2：no属性
             * 要素3：1111
             */
            student.no = 1111;
            /**读属性值两个要素：获取s对象的no属性的值。
             * 要素1：对象s
             * 要素2：no属性
             */
            System.out.println(student.no);
    
            //使用反射机制给属性赋值
            Class studentClass = Class.forName("javase.reflectBean.Student");//首先获取Class类
            Object obj = studentClass.newInstance();//实例化为对象obj，obj就是Student对象。（底层调用无参数构造方法）
    
            // 获取no属性（根据属性的名称来获取Field）
            Field noField = studentClass.getDeclaredField("no");
            // 给obj对象(Student对象)的no属性赋值
            /*
                虽然使用了反射机制，但是三要素还是缺一不可：
                    要素1：obj对象
                    要素2：no属性
                    要素3：22222值
                注意：反射机制让代码复杂了，但是为了一个“灵活”，这也是值得的。
             */
            noField.set(obj, 22222);
    
            // 读取属性的值
            // 两个要素：获取obj对象的no属性的值。
            System.out.println(noField.get(obj));
        }
    

##### 反射Method【反射/反编译一个类的方法】

###### Method类方法

方法名 备注  
public String getName() 返回方法名  
public int getModifiers()
获取方法的修饰符列表,返回的修饰符是一个数字，每个数字是修饰符的代号【一般配合Modifier类的toString(int x)方法使用】  
public Class<?> getReturnType()
以Class类型，返回方法类型【一般配合Class类的getSimpleName()方法使用】  
public Class<?>[] getParameterTypes()
返回方法的修饰符列表（一个方法的参数可能会有多个。）【结果集一般配合Class类的getSimpleName()方法使用】  
public Object invoke(Object obj, Object… args) 调用方法

    
    
    方法.invoke(对象, 实参);
    
    
    /*
    重点：必须掌握，通过反射机制怎么调用一个对象的方法？
        五颗星*****
    
        反射机制，让代码很具有通用性，可变化的内容都是写到配置文件当中，
        将来修改配置文件之后，创建的对象不一样了，调用的方法也不同了，
        但是java代码不需要做任何改动。这就是反射机制的魅力。
     */
    class ReflectTest10{
        public static void main(String[] args) throws Exception {
            // 不使用反射机制，怎么调用方法
            // 创建对象
            UserService userService = new UserService();
            // 调用方法
            /*
                要素分析：
                    要素1：对象userService
                    要素2：login方法名
                    要素3：实参列表
                    要素4：返回值
             */
            System.out.println(userService.login("admin", "123") ? "登入成功！" : "登入失败！");
    
            //使用反射机制调用方法
            Class userServiceClass = Class.forName("javase.reflectBean.UserService");
            // 创建对象
            Object obj = userServiceClass.newInstance();
            // 获取Method
            Method loginMethod = userServiceClass.getDeclaredMethod("login", String.class, String.class);
    //        Method loginMethod = userServiceClass.getDeclaredMethod("login");//注：没有形参就不传
            // 调用方法
            // 调用方法有几个要素？ 也需要4要素。
            // 反射机制中最最最最最重要的一个方法，必须记住。
            /*
                四要素：
                loginMethod方法
                obj对象
                "admin","123" 实参
                retValue 返回值
             */
            Object resValues = loginMethod.invoke(obj, "admin", "123");//注：方法返回值是void 结果是null
            System.out.println(resValues);
        }
    }
    

##### 反射Constructor【反射/反编译一个类的构造方法】

###### Constructor类方法

public String getName() 返回构造方法名  
public int getModifiers()
获取构造方法的修饰符列表,返回的修饰符是一个数字，每个数字是修饰符的代号【一般配合Modifier类的toString(int x)方法使用】  
public Class<?>[] getParameterTypes()
返回构造方法的修饰符列表（一个方法的参数可能会有多个。）【结果集一般配合Class类的getSimpleName()方法使用】  
public T newInstance(Object … initargs) 创建对象【参数为创建对象的数据】

###### 通过反射机制调用构造方法实例化java对象

    
    
    /*
    
    通过反射机制调用构造方法实例化java对象。（这个不是重点）
     */
    class ReflectTest12{
        public static void main(String[] args) throws Exception {
            //不使用反射创建对象
            Vip vip1 = new Vip();
            Vip vip2 = new Vip(123, "zhangsan", "2001-10-19", false);
    
            //使用反射机制创建对象（以前）
            Class vipClass = Class.forName("javase.reflectBean.Vip");
            // 调用无参数构造方法
            Object obj1 = vipClass.newInstance();//Class类的newInstance方法
            System.out.println(obj1);
    
            //使用反射机制创建对象（现在）
            // 调用有参数的构造方法怎么办？
            // 第一步：先获取到这个有参数的构造方法
            Constructor c1 = vipClass.getDeclaredConstructor(int.class, String.class, String.class, boolean.class);//参数列表：Class对象的数组，这些对象按声明的顺序标识构造函数的形式参数类型
            // 第二步：调用构造方法new对象
            Object obj2 = c1.newInstance(321, "lsi", "1999-10-11", true);//Constructor类的newInstance方法
            System.out.println(obj2);
    
            // 获取无参数构造方法
            Constructor c2 = vipClass.getDeclaredConstructor();
            Object obj3 = c2.newInstance();
            System.out.println(obj3);
        }
    }
    

如果需要调用无参构造方法，getDeclaredConstructor()方法形参为空即可

###### 获取一个类的父类以及实现的接口

两个方法【Class类中的】

public native Class<? super T> getSuperclass()  
public Class<?>[] getInterfaces()

    
    
    /*
    重点：给你一个类，怎么获取这个类的父类，已经实现了哪些接口？
     */
    class ReflectTest13{
        public static void main(String[] args) throws Exception{
            // String举例
            Class vipClass = Class.forName("java.lang.String");
            // 获取String的父类
            Class superclass = vipClass.getSuperclass();
            // 获取String类实现的所有接口（一个类可以实现多个接口。）
            Class[] interfaces = vipClass.getInterfaces();
            System.out.println(superclass.getName());
            for (Class i : interfaces) {
                System.out.println(i.getName());
            }
        }
    }
    

##### 注意

  1. 属性最重要的是 **名字**
  2. 实例方法最重要的是 **名字** 和 **形参列表**
  3. 构造方法最重要的是 **形参列表**

`Class.forName(classname)` 获取classname类中的所有属性包括类名

`Class.newInstance()`实例化对象，并触发该类的构造方法

`Class.getMethod(method name,arg)`
获取一个对象中的public方法，由于java支持方法的重载，所以需要第二参数作为获取的方法的形参列表，这样就可以确定获取的是哪一个方法。还记得重载是什么吗？子类对父类中允许访问的方法进行重新编写，返回值和形参不能改变。

`Method.invoke`()
执行方法，如果是一个普通方法，则invoke的第一个参数为该方法所在的对象，如果是静态方法则第一个参数是null或者该方法所在的类
第二个参数为要执行方法的参数。

`obj.getClass()` 如果上下文中存在某个类的实例obj，那我们可以直接通过obj.getClass来获取它的类

`Y1.class`
如果已经加载了一个类Y1，只是想获取到它由java.lang.class所创造的对象，那么就直接使用这种方法获取即可，这种方法并不属于反射

`Class.Forname` 如果知道某个类的名字，想获取到这个类，就可以使用forName来获取

#### 其他问题

##### 形参和实参

java方法可以是无参的，也可以是有参的，而参数又分为了形参和实参。

形参：是指在定义函数时使用的参数，目的是用于接收调用该函数时传入的参数。简单理解，就是所有函数（即方法）的参数都是形参。

实参：在调用有参函数时，主调函数和被调函数之间有数据传递关系。在主调函数中调用一个函数时，函数名后面括号中的参数称为“实际参数”。

###### 变量赋值的方式

如果变量是基本数据类型，此时赋值的是变量所保存的数据值。  
如果变量是引用数据类型，此时赋值的是变量所保存的数据的地址值。

    
    
    public class ValueTransferTest {
    
        public static void main(String[] args) {
    
            System.out.println("***********基本数据类型：****************");
            int m = 10;
            int n = m;
    
            System.out.println("m = " + m + ", n = " + n);
    
            n = 20;
    
            System.out.println("m = " + m + ", n = " + n);
    
            System.out.println("***********引用数据类型：****************");
    
            Order o1 = new Order();
            o1.orderId = 1001;
    
            Order o2 = o1;//赋值以后，o1和o2的地址值相同，都指向了堆空间中同一个对象实体。
    
            System.out.println("o1.orderId = " + o1.orderId + ",o2.orderId = " +o2.orderId);
    
            o2.orderId = 1002;
    
            System.out.println("o1.orderId = " + o1.orderId + ",o2.orderId = " +o2.orderId);
    
        }
    
    }
    
    class Order{
    
        int orderId;
        }
    运行结果：
    ***********基本数据类型：****************
    m = 10, n = 10
    m = 10, n = 20
    ***********引用数据类型：****************
    o1.orderId = 1001,o2.orderId = 1001
    o1.orderId = 1002,o2.orderId = 1002
    

在Java中，对象变量存储的是对象的引用，而不是对象本身。在这个程序中，创建了两个Order对象o1和o2，并将o2指向了o1，即o2和o1引用了同一个对象。因此，当o2.orderId被赋值为1002时，也会同时改变o1.orderId的值，因为它们都引用了同一个对象，对这个对象的修改会影响所有引用它的变量。

###### 值传递机制

如果参数是基本数据类型，此时实参赋给形参的是实参真实存储的数据值。

如果参数是引用数据类型，此时实参赋给形参的是实参存储数据的地址值。

    
    
    public class ValueTransferTest1 {
        public static void main(String[] args) {
    
            int m = 10;
            int n = 20;
    
            System.out.println("m = " + m + ", n = " + n);
            //交换两个变量的值的操作
    //      int temp = m ;
    //      m = n;
    //      n = temp;
    
            ValueTransferTest1 test = new ValueTransferTest1();
            test.swap(m, n);
    
            System.out.println("m = " + m + ", n = " + n);
    
    
        }
    
    
        public void swap(int m,int n){
            int temp = m ;
            m = n;
            n = temp;
        }
    }
    

这里交换失败了

交换参数失败的原因是 Java 中的参数传递方式是值传递，即将参数值复制一份传递给方法，因此在 swap 方法中修改 m 和 n 的值并不会影响到 main
方法中的 m 和 n 的值，也就是说 swap 方法中的交换操作只是在其局部变量中完成的。所以，最终输出的结果与交换操作前是一样的。

如果想要在方法中修改传递进来的参数，可以通过将参数定义为一个对象（例如数组或类的实例）的方式来实现。或者也可以使用返回值来传递方法内修改后的值。

再来看个成功的

    
    
    public class ValueTransferTest2 {
    
        public static void main(String[] args) {
    
            Data data = new Data();
    
            data.m = 10;
            data.n = 20;
    
            System.out.println("m = " + data.m + ", n = " + data.n);
    
            //交换m和n的值
    //      int temp = data.m;
    //      data.m = data.n;
    //      data.n = temp;
    
            ValueTransferTest2 test = new ValueTransferTest2();
            test.swap(data);
    
    
            System.out.println("m = " + data.m + ", n = " + data.n);
    
        }
    
        public void swap(Data data){
            int temp = data.m;
            data.m = data.n;
            data.n = temp;
        }
    
    }
    
    class Data{
    
        int m;
        int n;
    
    }
    输出
    m = 10, n = 20
    m = 20, n = 10
    

在这个程序中，交换参数成功的原因是传递的参数是一个对象，而对象是引用类型，在 Java
中，引用类型变量存储的是对象的地址，也就是说，当对象传递给方法时，传递的是对象的地址，也就是引用，方法内部对对象引用的操作会影响到对象本身。

在 swap 方法中，参数 data 是一个对象的引用，通过操作该对象的属性 m 和 n 来实现参数的交换。因为 data 是一个对象的引用，所以 swap
方法内部修改 data 引用所指向的对象的属性时，会直接修改传递进来的对象 data 的属性，也就实现了参数的交换。

因此，交换参数成功的前提是传递的参数是对象或数组等引用类型变量，而不是基本数据类型。


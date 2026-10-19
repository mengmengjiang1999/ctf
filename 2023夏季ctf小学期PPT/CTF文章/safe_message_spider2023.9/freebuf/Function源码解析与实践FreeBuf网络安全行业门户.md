作者：陈昌浩

## 1 导读

if…else… 在代码中经常使用，听说可以通过 Java 8 的 Function 接口来消灭 if…else…！Function 接口是什么？如果通过
Function 接口接口消灭 if…else… 呢？让我们一起来探索一下吧。

## 2 Function 接口

Function 接口就是一个有且仅有一个抽象方法，但是可以有多个非抽象方法的接口，Function 接口可以被隐式转换为 lambda 表达式。可以通过
FunctionalInterface 注解来校验 Function 接口的正确性。Java 8
允许在接口中加入具体方法。接口中的具体方法有两种，default 方法和 static 方法。

    
    
    @FunctionalInterfaceinterface TestFunctionService{void addHttp(String url);}

那么就可以使用 Lambda 表达式来表示该接口的一个实现。

    
    
    TestFunctionService testFunctionService = url -> System.out.println("http:" + url);

### 2.1 FunctionalInterface

2.1.1 源码

    
    
    @Documented@Retention(RetentionPolicy.RUNTIME)@Target(ElementType.TYPE)public @interface FunctionalInterface {}

2.1.2 说明

![ae1c405fe277c43d03557d9664863630.png](https://image.3001.net/images/20221129/1669692143_63857aef9310749e4e485.png!small)

上图是 FunctionalInterface 的注解说明。通过上面的注解说明，可以知道 FunctionalInterface
是一个注解，用来说明一个接口是函数式接口。 函数式接口只有一个抽象方法。 可以有默认方法，因为默认方法有一个实现，所以不是抽象的。函数接口的实例可以用
lambda 表达式、方法引用或构造函数引用创建。

FunctionalInterface 会校验接口是否满足函数式接口：

  * 类型必须是接口类型，不能是注释类型、枚举或类。

  * 只能有一个抽象方法。

  * 可以有多个默认方法和静态方法。

  * 可以显示覆盖 java.lang.Object 中的抽象方法。

编译器会将满足函数式接口定义的任何接口视为函数式接口，而不管该接口声明中是否使用 FunctionalInterface 注解。

## 3 Function 接口主要分类

Function 接口主要分类:

  * Function：Function 函数的表现形式为接收一个参数，并返回一个值。

  * Supplier：Supplier 的表现形式为不接受参数、只返回数据。

  * Consumer：Consumer 接收一个参数，没有返回值。

  * Runnable：Runnable 的表现形式为即没有参数也没有返回值。

### 3.1 Function

Function 函数的表现形式为接收一个参数，并返回一个值。

3.1.1 源码

    
    
    @FunctionalInterfacepublic interface Function<T, R> {R apply(T t);default <V> Function<V, R> compose(Function<? super V, ? extends T> before) {Objects.requireNonNull(before);return (V v) -> apply(before.apply(v));}default <V> Function<T, V> andThen(Function<? super R, ? extends V> after) {Objects.requireNonNull(after);return (T t) -> after.apply(apply(t));}static <T> Function<T, T> identity() {return t -> t;}}

3.1.2 方法说明

  * apply：抽象方法。将此函数应用于给定的参数。参数 t 通过具体的实现返回 R。

  * compose：default 方法。返回一个复合函数，首先执行 fefore 函数应用于输入，然后将该函数应用于结果。如果任意一个函数的求值引发异常，则将其传递给组合函数的调用者。

  * andThen：default 方法。返回一个复合函数，该复合函数首先对其应用此函数它的输入，然后对结果应用 after 函数。如果任意一个函数的求值引发异常，则将其传递给组合函数的调用者。

  * identity：static 方法。返回一个始终返回其输入参数的函数。

3.1.3 方法举例

1）apply

测试代码：

    
    
    public  String upString(String str){Function<String, String> function1 = s -> s.toUpperCase();return function1.apply(str);}public static void main(String[] args) {System.out.println(upString("hello!"));}

通过 apply 调用具体的实现。执行结果：

![5cd0d080-825b-47fe-a2db-950cb842d9c620221012180435.png](https://image.3001.net/images/20221129/1669692144_63857af0507b02b9e3fbf.png!small)

2）compose

测试代码：

    
    
    public static void main(String[] args) {Function<String, String> function1 = s -> s.toUpperCase();Function<String, String> function2 = s -> "my name is "+s;String result = function1.compose(function2).apply("zhangSan");System.out.println(result);}

执行结果

![8c050b0a-5d91-41f8-a55e-2475618bdf4520221012180517.png](https://image.3001.net/images/20221129/1669692144_63857af0db7b88161d35f.png!small)

如结果所示：compose 先执行 function2 后执行 function1。

3）andThen

测试代码：

    
    
    public static void main(String[] args) {Function<String, String> function1 = s -> s.toUpperCase();Function<String, String> function2 = s -> "my name is "+s;String result = function1.andThen(function2).apply("zhangSan");System.out.println(result);}

执行结果：

![ae9775d9943637956ae36271c58590e7.png](https://image.3001.net/images/20221129/1669692145_63857af192a9da218d0b9.png!small)

如结果所示：

andThen 先执行 function1 后执行 function2。

  * identity

测试代码：

    
    
    public static void main(String[] args) {Stream<String> stream = Stream.of("order", "good", "lab", "warehouse");Map<String, Integer> map = stream.collect(Collectors.toMap(Function.identity(), String::length));System.out.println(map);}

执行结果:

![2ee8c6d6-0cf3-4af2-a618-dfc15e935cbe20221012180626.png](https://image.3001.net/images/20221129/1669692146_63857af21865e3014263a.png!small)

### 3.2 Supplier

Supplier 的表现形式为不接受参数、只返回数据。

3.2.1 源码

    
    
    @FunctionalInterfacepublic interface Supplier<T> {/*** Gets a result.** @return a result*/T get();}

3.2.2 方法说明

get：抽象方法。通过实现返回 T。

3.2.3 方法举例

    
    
    public class SupplierTest {SupplierTest(){System.out.println(Math.random());System.out.println(this.toString());}}public static void main(String[] args) {Supplier<SupplierTest> sup = SupplierTest::new;System.out.println("调用一次");sup.get();System.out.println("调用二次");sup.get();}

执行结果:

![b62af52e-67de-4165-848c-48b3f22848db20221012180711.png](https://image.3001.net/images/20221129/1669692146_63857af2a91846acb1722.png!small)

如结果所示：Supplier 建立时并没有创建新类，每次调用 get 返回的值不是同一个。

### 3.3 Consumer

Consumer 接收一个参数，没有返回值。

3.3.1 源码

    
    
    @FunctionalInterfacepublic interface Consumer<T> {void accept(T t);default Consumer<T> andThen(Consumer<? super T> after) {Objects.requireNonNull(after);return (T t) -> { accept(t); after.accept(t); };}}

3.3.2 方法说明

  * accept：对给定参数 T 执行一些操作。

  * andThen：按顺序执行 Consumer -> after , 如果执行操作引发异常，该异常被传递给调用者。

3.3.3 方法举例

    
    
    public static void main(String[] args) {Consumer<String> consumer = s -> System.out.println("consumer_"+s);Consumer<String> after = s -> System.out.println("after_"+s);consumer.accept("isReady");System.out.println("========================");consumer.andThen(after).accept("is coming");}

执行结果：![9e41d8a625b2382959d1820d2b75db6b.png](https://image.3001.net/images/20221129/1669692147_63857af369dc9bda58be8.png!small)

如结果所示：对同一个参数 T，通过 andThen 方法，先执行 consumer，再执行 fater。

### 3.4 Runnable

Runnable：Runnable 的表现形式为即没有参数也没有返回值。

3.4.1 源码

    
    
    @FunctionalInterfacepublic interface Runnable {public abstract void run();}

3.4.2 方法说明

run：抽象方法。run 方法实现具体的内容，需要将 Runnale 放入到 Thread 中，通过 Thread 类中的 start ()
方法启动线程，执行 run 中的内容。

3.4.3 方法举例

    
    
    public class TestRun implements Runnable {@Overridepublic void run() {System.out.println("TestRun is running!");}}public static void main(String[] args) {Thread thread = new Thread(new TestRun());thread.start();}

执行结果：

![41d0da65-c3e7-491b-88cf-f7a409320da820221012181059.png](https://image.3001.net/images/20221129/1669692147_63857af3e6d3183e05b9f.png!small)

如结果所示：当线程实行 start 方法时，执行 Runnable 的 run 方法中的内容。

## 4 Function 接口用法

Function 的主要用途是可以通过 lambda 表达式实现方法的内容。

### 4.1 差异处理

原代码：

    
    
    @Datapublic class User {/*** 姓名*/private String name;/*** 年龄*/private int age;/*** 组员*/private List<User> parters;}public static void main(String[] args) {User user =new User();if(user ==null ||user.getAge() <18 ){throw new RuntimeException("未成年！");}}

执行结果：

![264bf868-f7bf-44ca-aa61-27c09f707ae620221012181144.png](https://image.3001.net/images/20221129/1669692148_63857af46e1115f98b797.png!small)

使用 Function 接口后的代码：

    
    
    @FunctionalInterfacepublic interface testFunctionInfe {/*** 输入异常信息* @param message*/void showExceptionMessage(String message);}public static testFunctionInfe doException(boolean flag){return (message -> {if (flag){throw new RuntimeException(message);}});}public static void main(String[] args) {User user =new User();doException(user ==null ||user.getAge() <18).showExceptionMessage("未成年！");}

执行结果：![1fdf65b29c7d8c451c360304d1cfeb74.png](https://image.3001.net/images/20221129/1669692149_63857af524bd63917f5b3.png!small)

使用 function 接口前后都抛出了指定的异常信息。

### 4.2 处理 if…else…

原代码:

    
    
    public static void main(String[] args) {User user =new User();if(user==null){System.out.println("新增用户");}else {System.out.println("更新用户");}}

使用 Function 接口后的代码：

    
    
    public static void main(String[] args) {User user =new User();Consumer trueConsumer = o -> {System.out.println("新增用户");};Consumer falseConsumer= o -> {System.out.println("更新用户");};trueOrFalseMethdo(user).showExceptionMessage(trueConsumer,falseConsumer);}public static testFunctionInfe trueOrFalseMethdo(User user){return ((trueConsumer, falseConsumer) -> {if(user==null){trueConsumer.accept(user);}else {falseConsumer.accept(user);}});}@FunctionalInterfacepublic interface testFunctionInfe {/*** 不同分处理不同的事情* @param trueConsumer* @param falseConsumer*/void showExceptionMessage(Consumer trueConsumer,Consumer falseConsumer);}

执行结果：

![6a6ef345-f651-42b1-aa03-b8977172278820221012181311.png](https://image.3001.net/images/20221129/1669692149_63857af5b5b62206556e1.png!small)

### 4.3 处理多个 if

原代码：

    
    
    public static void main(String[] args) {String flag="";if("A".equals(flag)){System.out.println("我是A");}else if ("B".equals(flag)) {System.out.println("我是B");}else if ("C".equals(flag)) {System.out.println("我是C");}else {System.out.println("没有对应的指令");}}

使用 Function 接口后的代码：

    
    
    public static void main(String[] args) {String flag="B";Map<String, Runnable> map =initFunctionMap();trueOrFalseMethdo(map.get(flag)==null).showExceptionMessage(()->{System.out.println("没有相应指令");},map.get(flag));}public static   Map<String, Runnable> initFunctionMap(){Map<String,Runnable> result  = Maps.newHashMap();result.put("A",()->{System.out.println("我是A");});result.put("B",()->{System.out.println("我是B");});result.put("C",()->{System.out.println("我是C");});return result;}public static testFunctionInfe trueOrFalseMethdo(boolean flag){return ((runnable, falseConsumer) -> {if(flag){runnable.run();}else {falseConsumer.run();}});}

执行结果:

![055fb0332e4e04620006259dade5167b.png](https://image.3001.net/images/20221129/1669692150_63857af667c5fa2171499.png!small)

## 5 总结

Function 函数式接口是 java 8 新加入的特性，可以和 lambda 表达式完美结合，是非常重要的特性，可以极大的简化代码。


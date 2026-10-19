###### **作者：陈昌浩**

### 1 背景

随着数据量的增长，发现系统在与其他系统交互时，批量接口会出现超时现象，发现原批量接口在实现时，没有做分片处理，当数据过大时或超过其他系统阈值时，就会出现错误。由于与其他系统交互比较多，一个一个接口做分片优化，改动量较大，所以考虑通过AOP解决此问题。

### 2 Spring-AOP

AOP （Aspect Orient Programming）,直译过来就是 面向切面编程。AOP
是一种编程思想，是面向对象编程（OOP）的一种补充。面向对象编程将程序抽象成各个层次的对象，而面向切面编程是将程序抽象成各个切面。

Spring 中的 AOP 是通过动态代理实现的。 Spring AOP 不能拦截对对象字段的修改，也不支持构造器连接点,我们无法在 Bean
创建时应用通知。

### 3 功能实现

自定义分片处理分三个部分：自定义注解（MethodPartAndRetryer）、重试器（RetryUtil）、切面实现(RetryAspectAop)。

#### 3.1 MethodPartAndRetryer

源码

  1. `@Target(ElementType.METHOD)`
  2. `@Retention(RetentionPolicy.RUNTIME)`
  3. `@Documented`
  4. `public @interface MethodPartAndRetryer {`
  5. `/**`
  6. `* 失败重试次数 `
  7. `* @return`
  8. `*/`
  9. `int times() default 3;`
  10. `/**`
  11. `* 失败间隔执行时间 300毫秒`
  12. `* @return`
  13. `*/`
  14. `long waitTime() default 300L;`
  15. `/**`
  16. `* 分片大小 `
  17. `* @return`
  18. `*/`
  19. `int parts() default 200;`
  20. `}`

[@interface](https://github.com/interface "@interface")说明这个类是个注解。  
[@Target](https://github.com/Target "@Target")是这个注解的作用域

  1. `public enum ElementType {`
  2. `/** 类、接口(包括注释类型)或枚举声明 */`
  3. `TYPE,`
  4. `/** 字段声明(包括枚举常量) */`
  5. `FIELD,`
  6. `/** 方法声明 */`
  7. `METHOD,`
  8. `/** 正式的参数声明 */`
  9. `PARAMETER,`
  10. `/** 构造函数声明 */`
  11. `CONSTRUCTOR,`
  12. `/** 局部变量声明 */`
  13. `LOCAL_VARIABLE,`
  14. `/** 注释类型声明*/`
  15. `ANNOTATION_TYPE,`
  16. `/** 程序包声明 */`
  17. `PACKAGE,`
  18. `/**类型参数声明*/`
  19. `TYPE_PARAMETER,`
  20. `/**类型的使用*/`
  21. `TYPE_USE`
  22. `}`

[@Retention](https://github.com/Retention "@Retention")注解的生命周期

  1. `public enum RetentionPolicy {`
  2. `/** 编译器处理完后不存储在class中*/`
  3. `SOURCE,`
  4. `/**注释将被编译器记录在类文件中，但不需要在运行时被VM保留。 这是默认值*/`
  5. `CLASS,`
  6. `/**编译器存储在class中，可以由虚拟机读取*/`
  7. `RUNTIME`
  8. `}`

  * times()：接口调用失败时，重试的次数。
  * waitTime():接口调用失败是，间隔多长时间再次调用。
  * int parts()：进行分片时，每个分片的大小。

3.2 RetryUtil

源码

  1. `public class RetryUtil<V> {`
  2. ``
  3. `public Retryer<V> getDefaultRetryer(int times,long waitTime) {`
  4. `Retryer<V> retryer = RetryerBuilder.<V>newBuilder()`
  5. `.retryIfException()`
  6. `.retryIfRuntimeException()`
  7. `.retryIfExceptionOfType(Exception.class)`
  8. `.withWaitStrategy(WaitStrategies.fixedWait(waitTime, TimeUnit.MILLISECONDS))`
  9. `.withStopStrategy(StopStrategies.stopAfterAttempt(times))`
  10. `.build();`
  11. `return retryer;`
  12. `}`
  13. `}`

说明

  * RetryerBuilder：是用于配置和创建Retryer的构建器。
  * retryIfException：抛出runtime异常、checked异常时都会重试，但是抛出error不会重试。
  * retryIfRuntimeException：只会在抛runtime异常的时候才重试，checked异常和error都不重试。
  * retryIfExceptionOfType：允许我们只在发生特定异常的时候才重试。
  * withWaitStrategy:等待策略，每次请求间隔。
  * withStopStrategy:停止策略，重试多少次后停止。

#### 3.3 RetryAspectAop

源码：

  1. `public class RetryAspectAop {`
  2. `public Object around(final ProceedingJoinPoint point) throws Throwable {`
  3. `Object result = null;`
  4. `final Object[] args = point.getArgs();`
  5. `boolean isHandler1 = isHandler(args);`
  6. `if (isHandler1) {`
  7. `String className = point.getSignature().getDeclaringTypeName();`
  8. `String methodName = point.getSignature().getName();`
  9. `Object firstArg = args[0];`
  10. `List<Object> paramList = (List<Object>) firstArg;`
  11. `//获取方法信息`
  12. `Method method = getCurrentMethod(point);`
  13. `//获取注解信息`
  14. `MethodPartAndRetryer retryable = AnnotationUtils.getAnnotation(method, MethodPartAndRetryer.class);`
  15. `//重试机制`
  16. `Retryer<Object> retryer = new RetryUtil<Object>().getDefaultRetryer(retryable.times(),retryable.waitTime());`
  17. `//分片`
  18. `List<List<Object>> requestList = Lists.partition(paramList, retryable.parts());`
  19. `for (List<Object> partList : requestList) {`
  20. `args[0] = partList;`
  21. `Object tempResult = retryer.call(new Callable<Object>() {`
  22. `@Override`
  23. `public Object call() throws Exception {`
  24. `try {`
  25. `return point.proceed(args);`
  26. `} catch (Throwable throwable) {`
  27. `log.error(String.format("分片重试报错,类%s-方法%s",className,methodName),throwable);`
  28. `throw new RuntimeException("分片重试出错");`
  29. `}`
  30. `}`
  31. `});`
  32. `if (null != tempResult) {`
  33. `if (tempResult instanceof Boolean) {`
  34. `if (!((Boolean) tempResult)) {`
  35. `log.error(String.format("分片执行报错返回类型不能转化bolean,类%s-方法%s",className,methodName));`
  36. `throw new RuntimeException("分片执行报错!");`
  37. `}`
  38. `result = tempResult;`
  39. `} else if (tempResult instanceof List) {`
  40. `if(result ==null){`
  41. `result =Lists.newArrayList();`
  42. `}`
  43. `((List) result).addAll((List) tempResult);`
  44. `}else {`
  45. `log.error(String.format("分片执行返回的类型不支持,类%s-方法%s",className,methodName));`
  46. `throw new RuntimeException("不支持该返回类型");`
  47. `}`
  48. `} else {`
  49. `log.error(String.format("分片执行返回的结果为空,类%s-方法%s",className,methodName));`
  50. `throw new RuntimeException("调用结果为空");`
  51. `}`
  52. `}`
  53. `} else {`
  54. `result = point.proceed(args);`
  55. `}`
  56. `return result;`
  57. `}`
  58. `private boolean isHandler(Object[] args) {`
  59. `boolean isHandler = false;`
  60. `if (null != args && args.length > 0) {`
  61. `Object firstArg = args[0];`
  62. `//如果第一个参数是list 并且数量大于1`
  63. `if (firstArg!=null&&firstArg instanceof List &&((List) firstArg).size()>1) {`
  64. `isHandler = true;`
  65. `}`
  66. `}`
  67. `return isHandler;`
  68. `}`
  69. `private Method getCurrentMethod(ProceedingJoinPoint point) {`
  70. `try {`
  71. `Signature sig = point.getSignature();`
  72. `MethodSignature msig = (MethodSignature) sig;`
  73. `Object target = point.getTarget();`
  74. `return target.getClass().getMethod(msig.getName(), msig.getParameterTypes());`
  75. `} catch (NoSuchMethodException e) {`
  76. `throw new RuntimeException(e);`
  77. `}`
  78. `}`
  79. `}`

说明：

getCurrentMethod：获取方法信息即要做分片的批量调用的接口。  
isHandler1：判断是否要做分片处理，只有第一参数是list并且list 的值大于1时才做分片处理。  
around：具体分片逻辑。

  1. 获取要分片方法的参数。
  2. 判断是否要做分片处理。
  3. 获取方法。
  4. 获取重试次数、重试间隔时间和分片大小。
  5. 生成重试器。
  6. 根据设置的分片大小，做分片处理。
  7. 调用批量接口并处理结果。

### 4 功能使用

#### 4.1 配置文件

![](https://image.3001.net/images/20221122/1669084021_637c33757e2ced1d3ca13.png!small)

#### 4.2 代码示例

  1. `@MethodPartAndRetryer(parts=100)`
  2. `public Boolean writeBackOfGoodsSN(List<SerialDTO> listSerial,ObCheckWorker workerData)`

只要在需要做分片的批量接口方法上，加上MethodPartAndRetryer注解就可以，重试次数、重试间隔时间和分片大小可以在注解时设置，也可以使用默认值。

### 5 小结

通过自定义分片工具，可以快速的对老代码进行分片处理，而且增加了重试机制，提高了程序的可用性，提高了对老代码的重构效率。

  

######  


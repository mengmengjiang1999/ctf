### 如下内容如有不正确之处请指正

## 漏洞分析：

Diff：https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f  
先通过对diff的分析，发现本次Fix版本针对RoutingFunction.java中的functionFromExpression方法做了调整，增加了一个boolean类型的参数，截图如下：  
![image](https://image.3001.net/images/20221126/1669433668_63818944253f6d268c006.png!small)  
functionFromExpression方法在该类中被route方法调用，因此我们先来查看route方法中的内容：  
1、首先route方法包含两个参数，一个类型为Object ，一个类型为Boolean  
![image](https://image.3001.net/images/20221126/1669433694_6381895e83cff6d549510.jpg!small)  
2、声明了一个Function  
![image](https://image.3001.net/images/20221126/1669433747_6381899393939b634b50f.png!small)  
3、通过如下可知，代码中判断input是否与Message类型相同或是与其具有父子关系，当值为true时进入该逻辑，同时将input赋值给Message。此时我们发送请求的请求头，请求体由input赋给Message，由于请求中未设置请求体因此请求体为null，但可通过Message的getHeader方法获取到请求头数据，然后通过MessageHeaders的get方法获取到某一请求头的值  
![image](https://image.3001.net/images/20221126/1669433805_638189cd67820ed69488a.png!small)  
![image](https://image.3001.net/images/20221126/1669433812_638189d4872f2697867fa.png!small)  
4、其次我们关注route方法上的注释：  
通过阅读注释及下方的代码，可知：  
spring.cloud.function.definition、pring.cloud.function.routing-expression这两个值可以从header中获取，或者从配置文件获取，此处的header就是通过MessageHeaders对象获取的，也就说是数据来自于用户请求的请求头中，并且经过非空判断后传入functionFromDefinition方法中。  
![image](https://image.3001.net/images/20221126/1669433889_63818a21147547a42bfff.png!small)  
5、由于开头说到，diff中修改了functionFromExpression方法中的代码，回过头来我们在RoutingFunction中找到functionFromExpression方法，但发现存在一个重载方法。  
![image](https://image.3001.net/images/20221126/1669433921_63818a418489d5dab51cb.png!small)  
但该漏洞描述为SpEL表达式注入，因此应关注functionFromExpression方法中存在SpEL表达式解析的那一个。所以此处我们可以想到，在第4点中我们发现取值可以从请求头中取，也可以从配置文件中取，可以取definition也可以取routing-expression，那么是否都可以针对该漏洞进行漏洞，这点要判断它调用的functionFromExpression方法是Function
functionFromDefinition(String definition)，还是Function
functionFromExpression(String routingExpression, Object
input)，如果是前者显然并不能触发SpEL解析，无法进行漏洞利用。  
![image](https://image.3001.net/images/20221126/1669433969_63818a71633d7930e1f8d.png!small)  
6、仍然把关注点放在Function functionFromExpression(String routingExpression, Object
input)  
![image](https://image.3001.net/images/20221126/1669434005_63818a952d82c1f1cbeab.png!small)  
该方法的两个参数String routingExpression, Object
input，根据上下文可知其中routingExpression是spring.cloud.function.routing-expressionspring.cloud.function.routing-expression请求头的值，input是Message。通过向SpelExpressionParser的parseExpression方法传入routingExpression获得了Expression对象，然后调用getValue方法，在这里调用的getValue方法是Expression的实现类SpelExpression中的方法。  
在getValue方法中可以看到要求传入EvaluationContext
、Object、Class三个参数，根据前文可知其中Object是Message；该方法返回值类型是一个泛型，第三个参数是当执行了SpEL表达式后预期结果的类型，前文设定为String类型。而重要的是EvaluationContext
，  
EvaluationContext
是一个接口，他有一个默认的实现类是StandardEvaluationContext。并且从上文中可知此处也确实传入StandardEvaluationContext对象，看到此处，如果了解SpEL表达式注入漏洞，也即可知道走到getValue后即可触发SpEL表达式解析，并触发漏洞。  
![image](https://image.3001.net/images/20221126/1669434073_63818ad988b59679455a2.png!small)  
![image](https://image.3001.net/images/20221126/1669434080_63818ae0c633dd65e5062.png!small)  
![image](https://image.3001.net/images/20221126/1669434087_63818ae78f23613ee4ec9.png!small)

## 漏洞是如何修复的：

1、仍然是观察diff，官方并未删除StandardEvaluationContext对象，而是增加了SimpleEvaluationContext对象，且通过DataBindingPropertyAccessor设置只读属性  
![image](https://image.3001.net/images/20221126/1669434193_63818b512d5ca16365d94.png!small)  
![image](https://image.3001.net/images/20221126/1669434213_63818b650133b044b9f7a.png!small)  
![image](https://image.3001.net/images/20221126/1669434221_63818b6d63ddbd376fb27.png!small)  
2、其次functionFromExpression方法，增加一个boolean类型参数  
![image](https://image.3001.net/images/20221126/1669434251_63818b8badc3ad64149a1.png!small)  
3、中间toCaseInsensitiveHeadersStructure部分代码不用看，根据官方注释可知并没有什么用  
![image](https://image.3001.net/images/20221126/1669434298_63818bba2502fe8a9da64.png!small)  
4、继续根据代码，上文可知functionFromExpression方法中的默认boolean类型参数为true，  
因此isViaHeader 为true，程序会走expression.getValue(this.headerEvalContext, input,
String.class)，而不是expression.getValue(this.evalContext, input, String.class);  
这点是与漏洞版本存在差异的地方，通过观察我们发现仍然是调用getValue方法，但是EvaluationContext的实现类由StandardEvaluationContext变成了SimpleEvaluationContext。  
从而规避漏洞。  
![image](https://image.3001.net/images/20221126/1669434347_63818bebbd126a9dca82e.png!small)  
![image](https://image.3001.net/images/20221126/1669434354_63818bf244e7bfcf1c69b.png!small)  
5、通过MessageHeader（也就是用户可控的请求头中）获取的任何SpEL表达式，都不会由StandardEvaluationContext进行解析。  
![image](https://image.3001.net/images/20221126/1669434385_63818c11c6bcfdeea58f0.png!small)  
6、按照修复方案，我们写一个demo  
![image](https://image.3001.net/images/20221126/1669434427_63818c3bd9627fffa1122.png!small)  
7、在getValue打一个断点  
![image](https://image.3001.net/images/20221126/1669434466_63818c62a0a521744c89b.png!small)  
8、debug到TypeReference类的getValueInternal方法，可以看到此处判断T()中是否包含“.”，如果包含即抛出异常  
![image](https://image.3001.net/images/20221126/1669434520_63818c98d05e7faf0e4d8.png!small)  
![image](https://image.3001.net/images/20221126/1669434526_63818c9eebed4e70c51cf.png!small)


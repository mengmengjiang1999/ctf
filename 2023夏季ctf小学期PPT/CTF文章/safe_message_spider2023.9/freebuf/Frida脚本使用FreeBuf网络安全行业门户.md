### 准备工作

#### Frida

在[这里](https://mp.weixin.qq.com/s?__biz=MzI1NjEyMzgxMw==&mid=2247484206&idx=1&sn=74c6811da70949b61375684635c9e4a4&chksm=ea2a35e4dd5dbcf24b800f3a53dd7f341b30995914c65e41076adac799fb86531e7a266bed24&token=2144849109&lang=zh_CN#rd)对Frida进行了简单的介绍。

#### 设备

设备: Android 10 ROOT

PC: Ubuntu18.04

#### Python切换

有些时候，需要使用Python的2.x版本，而有些时候又需要使用python的3.x版本，这个时候就需要能够灵活设置python版本
使用下面的命令设置Python2是默认：

    
    
    

  1. `sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 100`

使用下面的命令设置Python3是默认

    
    
    

  1. `sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 150`

使用`sudo update-alternatives--config python`命令切换到制定的版本
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)由于Frida建议使用Python3.x，因此这里切换到3的版本。在二进制漏洞中，exploit使用的基本都是Python2.7。

#### Frida脚本

FRIDA脚本就是利用FRIDA动态插桩框架，使用FRIDA导出的API和方法，对内存空间里的对象方法进行监视、修改或者替换的一段代码。FRIDA的API是使用JavaScript实现的，所以我们可以充分利用JS的匿名函数的优势、以及大量的hook和回调函数的API。

##### Hello world

Hello world经典的入门程序，frida版本的来一个。

    
    
    

  1. `setTimeout(function (){`
  2. ` Java.perform(function (){`
  3. ` console.log("Hello world");`
  4. ` });`
  5. `});`

##### 使用的API

setTimeout(func, delay[, ...parameters]): **call func after delay
milliseconds** , optionally passing it one or more parameters. Returns an id
that can be passed to clearTimeout to cancel it.

clearTimeout(id): **cancel id returned by call to setTimeout**.

Java.perform(fn): **ensure that the current thread is attached to the VM and
call fn**. (This isn’t necessary in callbacks from Java.) Will defer calling
fn if the app’s class loader is not available yet. Use Java.performNow() if
access to the app’s classes is not needed.

console.log(line), console.warn(line), console.error(line): **write line to
the console of your Frida-based application**.

##### JavaScript匿名函数

匿名函数：就是没有函数名的函数。这怎么可能，一个函数居然没有函数名，但JavaScript就是支持这种语法的，这和Java等编译型语言又很大的区别。匿名函数最大的用途是创建闭包。闭包是JavaScript的精髓，后续会专门讲解。

    
    
    

  1. `<script>`
  2. ` var fun = function (){`
  3. ` alert("欢迎关注我的微信公众号:无情剑客")`
  4. ` }`
  5. ` fun();`
  6. `</script>`

![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

##### 运行程序

通过前面的分析，可知这个程序最终调用`console.log("Hello world");`

在手机端开启frida-server.
![在这里插入图片描述](https://image.3001.net/images/20200802/1596348243.png!small)
然后在PC端运行下面的命令:

    
    
    

  1. `frida -U -l hello.js android.process.media`

运行后的结果如下
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

##### 枚举所有的类

    
    
    

  1. `setTimeout(function (){`
  2. ` Java.perform(function (){`
  3. ` console.log("n[*] enumerating classes...");`
  4. ` Java.enumerateLoadedClasses({`
  5. ` onMatch: function(_className){`
  6. ` console.log("[*] found instance of '"+_className+"'");`
  7. ` },`
  8. ` onComplete: function(){`
  9. ` console.log("[*] class enuemration complete");`
  10. ` }`
  11. ` });`
  12. ` });`
  13. ` });`

其中： Java.enumerateLoadedClasses(callbacks): enumerate classes loaded right
now, where callbacks is an object specifying:

  * onMatch: function (name, handle): called for each loaded class with name that may be passed to use() to get a JavaScript wrapper. You may also Java.cast() the handle to java.lang.Class.

  * onComplete: function (): called when all classes have been enumerated.

运行js代码，同上，结果如下
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

##### 枚举蓝牙类和实例

    
    
    

  1. `setTimeout(function (){`
  2. ` Java.perform(function (){`
  3. ` console.log("n[*] enumerating classes...");`
  4. ` Java.enumerateLoadedClasses({`
  5. ` onMatch: function(_className){`
  6. ` if(_className.split(".")[1] == bluetooth){`
  7. ` console.log("[*] found instance of '"+_className+"'");`
  8. ` }`
  9. ` },`
  10. ` onComplete: function(){`
  11. ` console.log("[*] class enuemration complete");`
  12. ` }`
  13. ` });`
  14. ` });`
  15. ` });`

运行后，可以看出有关bluetooth相关的类和实例都被枚举出来了。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)选定"android.bluetooth.BluetoothDevice"，获取peer
device的实例信息。

    
    
    

  1. ` Java.choose("android.bluetooth.BluetoothDevice",{`
  2. ` onMatch: function (instance){`
  3. ` console.log("[*] "+" android.bluetooth.BluetoothDevice instance found"+" :=> '"+instance+"'");`
  4. ` //这里是类型转化的用法`
  5. ` //console.log(Java.cast(instance,Java.use("android.bluetooth.BluetoothDevice") ).getName());`
  6. ` console.log(instance.getName());`
  7. ` // bluetoothDeviceInfo(instance);`
  8. ` },`
  9. ` onComplete: function() { console.log("[*] -----");}`
  10. ` });`

其中： Java.choose(className, callbacks): **enumerate live instances of the
className class by scanning the Java heap** , where callbacks is an object
specifying:

  * onMatch: function (instance): called with each live instance found with a ready-to-use instance just as if you would have called Java.cast() with a raw handle to this particular instance. This function may return the string stop to cancel the enumeration early.
  * onComplete: function (): called when all instances have been enumerated

运行脚本，打印出peer device的名字和地址。

    
    
    

  1. `frida -U -l hello.js com.android.bluetooth`

![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

##### 枚举所有方法

    
    
    

  1. ` function enumMethods(targetClass)`
  2. ` {`
  3. ` var hook = Java.use(targetClass);`
  4. ` var ownMethods = hook.class.getDeclaredMethods();`
  5. ` hook.$dispose;`
  6. ``
  7. ` return ownMethods;`
  8. ` }`
  9. ``
  10. ` var a = enumMethods("android.bluetooth.BluetoothDevice")`
  11. ` a.forEach(function(s) {`
  12. ` console.log(s);`
  13. ` });`

其中： Java.use(className): **dynamically get a JavaScript wrapper for className
that you can instantiate objects from by calling $new() on it to invoke a
constructor**. Call $dispose() on an instance to clean it up explicitly (or
wait for the JavaScript object to get garbage-collected, or script to get
unloaded). Static and non-static methods are available, and you can even
replace a method implementation and throw an exception from it:

    
    
    

  1. `Java.perform(function () {`
  2. ` var Activity = Java.use('android.app.Activity');`
  3. ` var Exception = Java.use('java.lang.Exception');`
  4. ` Activity.onResume.implementation = function () {`
  5. ` throw Exception.$new('Oh noes!');`
  6. ` };`
  7. `});`

使用下面的命令运行脚本，枚举android.bluetooth.BluetoothDevice声明的所有方法。

    
    
    

  1. `frida -U -l hello.js com.android.bluetooth`

![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)通过frida
hook就能够对想要hook的方法进行控制了。这里举一个简单的例子，我想让所有的getName()都返回"Redmi"。

    
    
    

  1. `setTimeout(function (){`
  2. ` Java.perform(function (){`
  3. ` console.log("n[*] enumerating classes...");`
  4. ` var targetClass = Java.use("android.bluetooth.BluetoothDevice");`
  5. ` targetClass.getName.implementation=function(){`
  6. ` var x = this.getName(); `
  7. ` return 'Redmi';`
  8. ` }`
  9. ` Java.choose("android.bluetooth.BluetoothDevice",{`
  10. ` onMatch: function (instance){`
  11. ` console.log("[*] "+" android.bluetooth.BluetoothDevice instance found"+" :=> '"+instance+"'");`
  12. ` // console.log(Java.cast(instance,Java.use("android.bluetooth.BluetoothDevice") ).getName());`
  13. ` console.log(instance.getName());`
  14. ` // bluetoothDeviceInfo(instance);`
  15. ` },`
  16. ` onComplete: function() { console.log("[*] -----");}`
  17. ` });`
  18. ``
  19. ` });`
  20. ` });`

或者

    
    
    

  1. `import frida,sys`
  2. ``
  3. `def on_message(message, data):`
  4. ` if message['type'] == 'send':`
  5. ` print(" {0}".format(message['payload']))`
  6. ` else:`
  7. ` print(message)`
  8. `pass`
  9. ``
  10. `session = frida.get_usb_device().attach("com.android.bluetooth")`
  11. ``
  12. `jscode = """`
  13. `if(Java.available){`
  14. ` Java.perform(function(){`
  15. ` var targetClass = Java.use("android.bluetooth.BluetoothDevice");`
  16. ` targetClass.getName.implementation=function(){`
  17. ` x = this.getName(); `
  18. ` sned(x); `
  19. ` return 'Redmi';`
  20. ` }`
  21. ` });`
  22. ``
  23. `}`
  24. `"""`
  25. ``
  26. `script = session.create_script(jscode)`
  27. `script.on("message", on_message)`
  28. `print(' Start attach')`
  29. `script.load()`
  30. `sys.stdin.read()`

前者的运行结果：
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)微信运动的步数，支付宝的总金额等都可以用类似的方式进行修改。

#### 完整的代码

    
    
    

  1. `setTimeout(function (){`
  2. ` Java.perform(function (){`
  3. ` console.log("n[*] enumerating classes...");`
  4. ` Java.enumerateLoadedClasses({`
  5. ` onMatch: function(_className){`
  6. ` if(_className.split(".")[1] == "bluetooth"){`
  7. ` console.log("[*] found instance of '"+_className+"'");`
  8. ` }`
  9. ` },`
  10. ` onComplete: function(){`
  11. ` console.log("[*] class enuemration complete");`
  12. ` }`
  13. ` });`
  14. ` Java.choose("android.bluetooth.BluetoothDevice",{`
  15. ` onMatch: function (instance){`
  16. ` console.log("[*] "+" android.bluetooth.BluetoothDevice instance found"+" :=> '"+instance+"'");`
  17. ` // console.log(Java.cast(instance,Java.use("android.bluetooth.BluetoothDevice") ).getName());`
  18. ` console.log(instance.getName());`
  19. ` // bluetoothDeviceInfo(instance);`
  20. ` },`
  21. ` onComplete: function() { console.log("[*] -----");}`
  22. ` });`
  23. ``
  24. ` function enumMethods(targetClass)`
  25. ` {`
  26. ` var hook = Java.use(targetClass);`
  27. ` var ownMethods = hook.class.getDeclaredMethods();`
  28. ` hook.$dispose;`
  29. ``
  30. ` return ownMethods;`
  31. ` }`
  32. ``
  33. ` var a = enumMethods("android.bluetooth.BluetoothDevice")`
  34. ` a.forEach(function(s) {`
  35. ` console.log(s);`
  36. ` });`
  37. ``
  38. ` });`
  39. ` });`

#### 参考

https://frida.re/docs/javascript-api/

#### 公众号

更多Frida相关的文章，欢迎关注我的公众号：无情剑客。
![在这里插入图片描述](https://image.3001.net/images/20200802/1596348246.jpg!small)


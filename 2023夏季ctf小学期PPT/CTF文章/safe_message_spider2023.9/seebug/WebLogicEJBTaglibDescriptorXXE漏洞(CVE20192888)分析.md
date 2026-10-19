**作者：Longofo@知道创宇404实验室**  
**时间：2019年10月16日**  
**英文版本：<https://paper.seebug.org/1068/>**

这个漏洞和之前@Matthias
Kaiser提交的几个XXE漏洞是类似的，而`EJBTaglibDescriptor`应该是漏掉的一个，可以参考之前几个XXE的[分析](https://paper.seebug.org/906/)。我和@Badcode师傅反编译了WebLogic所有的Jar包，根据之前几个XXE漏洞的特征进行了搜索匹配到了这个EJBTaglibDescriptor类，这个类在反序列化时也会进行XML解析。

Oracle发布了10月份的补丁，详情见链接(<https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html>)

### 环境

  * Windows 10
  * WebLogic 10.3.6.0.190716(安装了19年7月补丁)
  * Jdk160_29（WebLogic 自带的JDK）

### 漏洞分析

`weblogic.jar!\weblogic\servlet\ejb2jsp\dd\EJBTaglibDescriptor.class`这个类继承自`java\io\Externalizable`

![](https://images.seebug.org/content/images/2019/10/30/1572427265000-6.png-w331s)

因此在序列化与反序列化时会自动调用子类重写的`writeExternal`与`readExternal`

看下`writeExternal`的逻辑与`readExternal`的逻辑，

![](https://images.seebug.org/content/images/2019/10/30/1572427266000-7.png-w331s)

在`readExternal`中，使用`ObjectIutput.readUTF`读取反序列化数据中的String数据，然后调用了load方法，

![](https://images.seebug.org/content/images/2019/10/30/1572427266000-8.png-w331s)

在load方法中，使用`DocumentBuilder.parse`解析了反序列化中传递的XML数据，因此这里是可能存在XXE漏洞的

在`writeExternal`中，调用了本身的`toString`方法，在其中又调用了自身的`toXML`方法

![](https://images.seebug.org/content/images/2019/10/30/1572427266000-9.png-w331s)

![](https://images.seebug.org/content/images/2019/10/30/1572427266000-10.png-w331s)

`toXML`的作用应该是将`this.beans`转换为对应的xml数据。看起来要构造payload稍微有点麻烦，但是序列化操作是攻击者可控制的，所以我们可以直接修改`writeExternal`的逻辑来生成恶意的序列化数据：

![](https://images.seebug.org/content/images/2019/10/30/1572427266000-11.png-w331s)

### 漏洞复现

  1. 重写 `EJBTaglibDescriptor`中的`writeExternal`函数，生成payload

![
](https://images.seebug.org/content/images/2019/10/5546d729-24f7-40c2-bbfb-0bff6e03386a.png-w331s)

  2. 发送payload到服务器

![
](https://images.seebug.org/content/images/2019/10/6bb31bcc-d21e-430e-9452-2f75d5373606.png-w331s)

在我们的HTTP服务器和FTP服务器接收到了my.dtd的请求与win.ini的数据

![
](https://images.seebug.org/content/images/2019/10/a691da5f-964f-489a-ae51-979e0f817148.png-w331s)

  3. 在打了7月份最新补丁的服务器上能看到报错信息

![
](https://images.seebug.org/content/images/2019/10/a2993437-edfd-4f7e-a0b1-bba0ed9d0de5.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1067/>


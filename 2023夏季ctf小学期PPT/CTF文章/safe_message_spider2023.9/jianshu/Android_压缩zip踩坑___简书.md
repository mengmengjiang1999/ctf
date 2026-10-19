Android 压缩zip踩坑

[ 普通的程序员](https://www.jianshu.com/u/38b409cda5af)关注赞赏支持

# Android 压缩zip踩坑

推荐几个zip库

[https://github.com/zeroturnaround/zt-
zip](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fzeroturnaround%2Fzt-
zip)  
1.2k star  
优点：同步，一行代码搞定  
缺点：不支持单个文件的压缩进度上报，只能用文件/文件夹 的方式来计算进度

[https://github.com/srikanth-
lingala/zip4j](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fsrikanth-
lingala%2Fzip4j)  
302star 但是3.2k个git再引用  
优点：链式调用，同步，支持加密压缩，支持单个进度  
缺点：进度监听不灵活

干脆自己写一个ZipUtil

# 关于Android zip压缩的概念入门

<https://www.jianshu.com/p/7827e275d482>  

image.png

# 使用到的核心类

## ZipFile

此类用于从 ZIP 文件读取条目ZipEntry，在解压时用到

## ZipEntry

此类用于表示 ZIP 文件条目

## ZipOutputStream

此类为以 ZIP 文件格式写入文件实现输出流过滤器

## Enumeration

实现 Enumeration 接口的对象，它生成一系列元素，一次生成一个。连续调用 nextElement 方法将返回一系列的连续元素，在解压缩时会用到

## CheckedOutputStream

需要维护写入数据校验和的输出流。校验和可用于验证输出数据的完整性。

## CRC32

可用于计算数据流的 CRC-32 的类

# 关键代码

    
    
    public static void ZipFiles(File sourceDir, File targetZip, int compressLevel, OnZipProgressCallback callback) {
        try {
            if (!sourceDir.exists()) {
                throw new RuntimeException("source file not exists");
            }
            if (!targetZip.exists()) {
                targetZip.createNewFile();
            }
    
            int len;
            byte[] buffer = new byte[4096];
            FileOutputStream fos = new FileOutputStream(targetZip);
            //用于校验,不加这个校验的话，解压会报错
            CheckedOutputStream cos = new CheckedOutputStream(fos, new CRC32());
            ZipOutputStream zipOutputSteam = new ZipOutputStream(cos);
            zipOutputSteam.setLevel(compressLevel);
    
            FileInputStream inputStream = null;  // 定义文件输入流
            List<File> list = new LinkedList<>();
            list = getFileList(sourceDir, list);// 计算总文件个数，最终目标是压缩到一个文件
            int fileTransedCount = 0;//进度的计算按照压缩的个数/总个数算，日志压缩单个大文件的情况太少了
            int totalFilesNum = list.size();
    
            for (File file : list) {
                String name = file.getAbsolutePath();
                ZipEntry zipEntry = new ZipEntry(name);
                zipOutputSteam.putNextEntry(zipEntry);
                inputStream = new FileInputStream(name);
                while ((len = inputStream.read(buffer)) != -1) {
                    zipOutputSteam.write(buffer, 0, len);
                }
                inputStream.close();
                zipOutputSteam.flush();
                if (callback != null) {
                    fileTransedCount++;
                    //进度的计算，因为可以知道每个文件的流长度，可以用总写入流/总文件大小，这里图方便，直接用已完成个数/总个数
                    callback.onZipProgress(fileTransedCount * 100 / totalFilesNum);
                }
            }
            zipOutputSteam.close();
        } catch (Exception e) {
            throw new RuntimeException("zip failed");
        }
    }
    
    

有几个坑  
如果不加CRC32校验，可能会遇到，使用方法压缩了文件之后，解压报错，但是文件能正常达开。  
原因是

  

image.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [2018-05-29](https://www.jianshu.com/p/5de053887c0c)

WinRAR - 最新版本的更新 版本 5.50 1. WinRAR 和命令行 RAR 默认使用 RAR ...

[王舒璇](https://www.jianshu.com/u/ab1e69df7d40)阅读 1,706评论 0赞 2

  * [Android下文件的压缩和解压（Zip格式）](https://www.jianshu.com/p/7827e275d482)

Zip文件结构 ZIP文件结构如下图所示， File Entry表示一个文件实体,一个压缩文件中有多个文件实体。 ...

[卡咔喀](https://www.jianshu.com/u/679b178482a6)阅读 11,585评论 0赞 9

  * [10.8 压缩](https://www.jianshu.com/p/a5c4572c354d)

10.8 压缩 Java 1.1也添加一个类，用以支持对压缩格式的数据流的读写。它们封装到现成的IO类中，以提供压...

[5e0g](https://www.jianshu.com/u/87966f0d5938)阅读 72评论 0赞 2

  * [有关ZIP压缩包的破解](https://www.jianshu.com/p/2f9431b21003)

在设计泛CTF有关压缩包破解的某个题目（主要涉及伪加密和已知明文攻击）过程中，遇到了有关zip格式压缩的一些问题，...

[一川淡月疏星](https://www.jianshu.com/u/b1c4f6d2b525)阅读 5,733评论 1赞 5

  * [(转)java压缩解压缩rar、zip文件](https://www.jianshu.com/p/f230e7a27d8c)

转自http://www.open-open.com/lib/view/open1363592512046.htm...

[Feng_Sir](https://www.jianshu.com/u/9bee7eec49fb)阅读 2,327评论 0赞 4

 
作者：spoock  
作者博客：<https://blog.spoock.com/2018/10/15/cve-2016-1000031/>

### 说明

前几天刚刚分析了Apache Commons
FileUpload的Dos的漏洞，无意间发现了还存在反序列化的漏洞。网上只存在[cve-2016-1000031 Apache Commons
FileUpload
反序列化漏洞深入分析](https://blog.csdn.net/raintungli/article/details/56008382)。这篇文章只是简要地分析了一下，但是对于原理还是不理解。后来发现在`ysoserial`中存在这个漏洞的Payload，于是就根据ysoserial中的Payload对这个漏洞进行分析。

### 漏洞说明

漏洞的来源是在于`DiskFileItem`中的`readObject()`进行文件写入的操作，这就意味着如果我们对已经序列化的`DiskFileItem`对象进行反序列化操作就能够触发`readObject()`执行从而触发这个漏洞。

这个漏洞的危害是能够任意写、读文件或者目录。但是具体是对文件还是目录操作与FileUpload以及JDK的版本有关。不同的漏洞环境能够达到的效果不一样。

  1. FileUpload的1.3.1之前的版本配合JDK1.7之前的版本，能够达到写入任意文件的漏洞;
  2. FileUpload的1.3.1之前的版本配合JDK1.7及其之后的版本，能够向任意目录写入文件;
  3. FileUpload的1.3.1以及之后的版本只能向特定目录写入文件，此目录也必须存在。(文件的的命名也无法控制);

下面将进行详细地分析

### Payload构造

我们首先测试的版本是1.3的版本，JDK是1.8版本，所以这种组合只能达到向任意目录的文件写入的漏洞效果。

我们测试的payload是`{"write;cve1000031;123456"}`，表示的含义就是向目录`cve1000031`中写入`123456`的内容。在`ysoserial`中最终是由`ysoserial.payloads.FileUpload1::makePayload()`来构建payload。代码如下：

    
    
    private static DiskFileItem makePayload ( int thresh, String repoPath, String filePath, byte[] data ) throws IOException, Exception {
        // if thresh < written length, delete outputFile after copying to repository temp file
        // otherwise write the contents to repository temp file
        File repository = new File(repoPath);
        DiskFileItem diskFileItem = new DiskFileItem("testxxx", "application/octet-stream", false, "testxxx", 100000, repository);
        File outputFile = new File(filePath);
        DeferredFileOutputStream dfos = new DeferredFileOutputStream(thresh, outputFile);
        OutputStream os = (OutputStream) Reflections.getFieldValue(dfos, "memoryOutputStream");
        os.write(data);
        Reflections.getField(ThresholdingOutputStream.class, "written").set(dfos, data.length);
        Reflections.setFieldValue(diskFileItem, "dfos", dfos);
        Reflections.setFieldValue(diskFileItem, "sizeThreshold", 0);
        return diskFileItem;
    }

当我们输入我们的Payload，`{"write;cve1000031;123456"}`,其中的赋值情况是：

![ ](https://images.seebug.org/content/images/2018/10/f70a26aa-fec6-4fef-856d-6c27d9adb40e.jpg-w331s)

而`thresh`的值就是我们需要写入的内容的长度加1，即`len(123456)+1`结果就是7。其中还有`filePath`是`cve1000031/whatever`是因为在这个漏洞环境中我们最终是向`cve1000031`目录写入，所以后面是什么就没有意义了。

最后在代码中还存在几个反序列化的操作：

    
    
    Reflections.getField(ThresholdingOutputStream.class, "written").set(dfos, data.length);
    Reflections.setFieldValue(diskFileItem, "dfos", dfos);
    Reflections.setFieldValue(diskFileItem, "sizeThreshold", 0);

发序列化的意义是在于我们无法通过`DiskFileItem`的示例进行设置，只能通过反射的方式设置，这几个属性也是我们触发漏洞的必要条件。

之后对我们构造的这个进行序列化操作，反序列化之后就会触发DiskFileItem的`readObject()`从而触发漏洞。

### 漏洞分析-1

漏洞环境： `FileUpload 1.3`+`JDK1.7`

当对`DiskFileItem`的对象进行反序列化操作时，由`org.apache.commons.fileupload.disk.DiskFileItem::readObject()`处理。

    
    
    private void readObject(ObjectInputStream in)
            throws IOException, ClassNotFoundException {
        // read values
        in.defaultReadObject();
    
        OutputStream output = getOutputStream();
        if (cachedContent != null) {
            output.write(cachedContent);
        } else {
            FileInputStream input = new FileInputStream(dfosFile);
            IOUtils.copy(input, output);
            dfosFile.delete();
            dfosFile = null;
        }
        output.close();
    
        cachedContent = null;
    }

跟进`getOutputStream()`，进入到:

    
    
    public OutputStream getOutputStream()
        throws IOException {
        if (dfos == null) {
            File outputFile = getTempFile();
            dfos = new DeferredFileOutputStream(sizeThreshold, outputFile);
        }
        return dfos;
    }

由于`dfos == null`满足条件，会执行`File outputFile =
getTempFile();`方法。跟踪进入`getTempFile()`到中

![
](https://images.seebug.org/content/images/2018/10/8961c0fa-239a-47e0-9ae1-fa54e3ec2b98.jpg-w331s)

其中的`tempDir`就是我们设置的`repository`，即`cve1000031`。`tmpFileName`是由`DiskFileItem`是自动生成的。最终和`tempDir`组合得到的文件路径就是`cve1000031\upload_7b496a67_4fc4_4b14_a4e7_ff5aceb82aaf_00000000.tmp`。

最后返回至`readObject()`方法中写入文件，如下：

![
](https://images.seebug.org/content/images/2018/10/c2432ebb-634c-4af3-9cec-0700ab119f42.jpg-w331s)

其中的`cachedContent`就是我们之前在Payload中设置的`123456`。那么Payload的最终的效果就是在`cve1000031\upload_7b496a67_4fc4_4b14_a4e7_ff5aceb82aaf_00000000.tmp`文件中写入了`123456`的内容。

![
](https://images.seebug.org/content/images/2018/10/ae03da3b-34e1-438e-af29-0c6c53025213.jpg-w331s)

### 漏洞分析-2

由于前面的一个漏洞分析是向任意目录写文件的功能，本次分析的是任意文件写入的功能。本次的漏洞环境是`FileUpload 1.3`+`JDK1.6`。

#### Payload构造

构造的Payload是`{"writeOld;cve1000031.txt;123456"}`。同样会调用`makePayload()`构造Payload。

![
](https://images.seebug.org/content/images/2018/10/fc116c8e-930a-46fa-b5a2-b174ed262e59.jpg-w331s)

但是其中的`repoPath`最后一位是`\0`，这个就类似于PHP中的截断，用于截断后面的路径，这样就可以达到任意文件写入的效果。具体的原理说明如下：

> JDK7以上在Java的file相关的基础类中都做了空字符的保护，这也是在针对java的string 和 c
> char的结束方式不一致，在Java中文件的操作中使用String这种char 数组，而C中的char
> 是以空字符为结束符，所以java操作的文件中很容易通过注入空字符来操作完全不同的文件。比如`Java File file = new
> File("/test/test.txt\0.jsp")`
> 看起来再操作`test.txt\0.jsp`实际上在底层调用的（本质还是c读写文件）是在操作test.txt。在JDK7以后的版本File
> 里面会有一个判断是否有空字符的函数

这个意思就是在JDK7之前可以利用`\0`进行目录截断，和php在5.3.4版本之前也可以进行目录截断是一样的道理。所以这个任意文件写入为什么要求是JDK7以下的版本才可以的原因。

漏洞的执行流程和前面分析的漏洞流程一样，不同是在`getTempFile()`中:

![
](https://images.seebug.org/content/images/2018/10/a5a91a69-8db4-4453-b061-8cef1b81c83f.jpg-w331s)

其中`this.tempFile`的路径是`cve1000031.txt
\upload_6982dc32_8ca4_4d7c_b658_0a9b44a60741_00000000.tmp`。由于是在JDK1.6的环境下，后面的`\upload_6982dc32_8ca4_4d7c_b658_0a9b44a60741_00000000.tmp`在写入文件时会被忽略，所以最终是向`cve1000031.txt`文件中写入内容。

![
](https://images.seebug.org/content/images/2018/10/71c3012e-28de-43a7-a0a2-f2f12fd27425.jpg-w331s)

### 漏洞分析-3

漏洞环境： `FileUpload 1.3.1`+`JDK1.7` 在`FileUpload
1.3.1`中对`readObject()`的功能进行了修改。修改主要是对`repository`进行了校验。

    
    
    private void readObject(ObjectInputStream in)
            throws IOException, ClassNotFoundException {
        // read values
        in.defaultReadObject();
        /* One expected use of serialization is to migrate HTTP sessions
            * containing a DiskFileItem between JVMs. Particularly if the JVMs are
            * on different machines It is possible that the repository location is
            * not valid so validate it.
            */
        if (repository != null) {
            if (repository.isDirectory()) {
                // Check path for nulls
                if (repository.getPath().contains("\0")) {
                    throw new IOException(format(
                            "The repository [%s] contains a null character",
                            repository.getPath()));
                }
            } else {
                throw new IOException(format(
                        "The repository [%s] is not a directory",
                        repository.getAbsolutePath()));
            }
        }
    
        OutputStream output = getOutputStream();
        if (cachedContent != null) {
            output.write(cachedContent);
        } else {
            FileInputStream input = new FileInputStream(dfosFile);
            IOUtils.copy(input, output);
            dfosFile.delete();
            dfosFile = null;
        }
        output.close();
    
        cachedContent = null;
    }

通过对`repository.isDirectory()`和`repository.getPath().contains("\0")`的判断，就阻止了任意的文件写入的漏洞了。所以在这种环境下只能下特定的目录写入文件了。但是这种情况下，你也只能向临时目录写入文件。

### 总结

分析这个漏洞学习到了JDK1.6的截断同时也感慨`ysoserial`的强大。

以上

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/731/>


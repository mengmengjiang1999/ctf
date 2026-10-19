## **引言**

**JFinal是国产优秀的web框架，短小精悍强大,易于使用。近期团队内一名小伙伴（LuoKe）在安全测试的时候报了一个很玄学的任意文件上传，笔者本着知其然必知其所以然的态度去跟进了一下问题代码，发现问题系统在处理上传文件功能的时候使用了JFinal框架，于是去对该框架上传文件处的代码做了一下审计，发现了JFinal上传文件的黑名单机制的存在被绕过的风险。目前该漏洞已上报至厂商并修复，本文章意在和各位看官分享一下该漏洞的原理和发现过程。**

##  **关键函数**

isSafeFile(UploadFileuploadFile) //jfinal黑名单检测函数，负责对jsp与jspx类型文件进行过滤

com.oreilly.servlet.MultipartRequest(request, uploadPath, maxPostSize,
encoding,fileRenamePolicy) //jfinal处理上传文件请求类，负责处理上传请求中的文件与参数

##  **漏洞发现**

 **注：漏洞发现场景由我这边搭建的测试环境模拟，并非当时爆出漏洞的实际场景，如有疏漏，还请见谅。**

某日下午，团队内的安全测试组的LuoKe同学分享了一个很有意思的任意文件上传大体情况如下

1、上传txt类型文件，提示上传成功。

![](https://image.3001.net/images/20190814/1565763380_5d53a734c5d24.png!small)

2、上传jsp文件，显示上传失败。

![](https://image.3001.net/images/20190814/1565763417_5d53a759573b3.png!small)

3、提交如下数据包，显示上传失败，但是给上传目录下，可以发现上传成功。

![](https://image.3001.net/images/20190814/1565763457_5d53a781ad5b1.png!small)

刚看到这种情况，还是比较懵，因为但是比对了一下3个数据包，立马可以明白一个问题，第三个数据包是不完整的，它的最末行缺少分割的boundary，为了验证这个想法，我试了一下如下形式的数据包，

![](https://image.3001.net/images/20190814/1565763490_5d53a7a24a762.png!small)

果然是上传失败，那就说明一个道理，此次绕过黑名单一定是和程序报错有关系的。那接下来就是去跟进一下系统代码，确认一下我们的猜想。

##  **漏洞分析**

跟进代码的时候发现，系统中处理上传文件的代码是如下形式：

    
    
    UploadFile file = getFile("file", "test");
    

看了一下lib，发现这个函数是JFinal框架处理上传文件的函数，那是不是代表这种利用方式是在JFinal框架中是具有通用性的，所以直接在本地搭了一个JFinal框架去看一下上传文件的代码。

首先去看一下黑名单处理函数

Upload/MultipartRequest.class 100-107

    
    
    isSafeFile(UploadFile uploadFile) {
         String fileName = uploadFile.getFileName().trim().toLowerCase();
         (!fileName.endsWith() && !fileName.endsWith()) {
             ;
         } {
             uploadFile.getFile().delete();
             ;
         }
     }
    

可以发现在处理后缀为jsp和jspx类型的文件的时候，会做一步删除操作“uploadFile.getFile().delete();
“，看到这一步的时候我就基本心如明镜了，在这个地方做了删除操作是不是就代表了，代码在处理上传文件的时候先是什么都不管的，上传完成后再对有问题的文件做删除。

那我们先去跟一下上传文件的代码

Servlet/MultipartRequest.class 84-108

    
    
    ((part = parser.readNextPart()) != ) {
         String name = part.getName();
         (name == ) {
             IOException();
         }
         String fileName;
         (part.isParam()) {
             ParamPart paramPart = (ParamPart)part;
             fileName = paramPart.getStringValue();
             existingValues = (Vector).parameters.get(name);
             (existingValues == ) {
                 existingValues = Vector();
                 .parameters.put(name, existingValues);
             }
             existingValues.addElement(fileName);
         } (part.isFile()) {
             FilePart filePart = (FilePart)part;
             fileName = filePart.getFileName();
             (fileName != ) {
                 filePart.setRenamePolicy(policy);
                 filePart.writeTo(dir);
                 .files.put(name, UploadedFile(dir.toString(), filePart.getFileName(), fileName, filePart.getContentType()));
             }
    

可以看到代码会去轮询上传时候传的每个参数，一旦是文件，就会直接上传到给定的dir。

现在我们已经明确了，无论什么类型的文件都会上传，但是在抵达黑名单函数后就会对jsp和jspx文件进行删除，所以我们接下来要思考的问题就是：

> 如何让代码执行到上传文件后，而又不去执行黑名单处理代码。

总结刚刚我们在测试阶段的分析，比较良好的做法就是想办法让程序执行到黑名单函数之前报错，这样代码就会停止执行到黑名单函数。那我们去看一下代码，

Upload/MultipartRequest.class 76-87

    
    
    .multipartRequest = com.oreilly.servlet.MultipartRequest(request, uploadPath, maxPostSize, encoding, fileRenamePolicy);
     Enumeration files = .multipartRequest.getFileNames();(files.hasMoreElements()) {
         String name = (String)files.nextElement();
         String filesystemName = .multipartRequest.getFilesystemName(name);
         (filesystemName != ) {
             String originalFileName = .multipartRequest.getOriginalFileName(name);
             String contentType = .multipartRequest.getContentType(name);
             UploadFile uploadFile = UploadFile(name, uploadPath, filesystemName, originalFileName, contentType);
             (.isSafeFile(uploadFile)) {
                 .uploadFiles.add(uploadFile);
             }
         }
     }
    

从上传文件

 **this**.multipartRequest = **new**
com.oreilly.servlet.MultipartRequest(request,uploadPath, maxPostSize,
encoding, fileRenamePolicy);

到删除黑名单文件

 **this**.isSafeFile(uploadFile)

这段代码之间我们还是有很多操作可以去做的。

我这边的思路就是，首先保证上传文件的参数正常，再在文件参数后去给一个该接口不存在的参数，于是在轮询上传参数的时候，第一个参数是文件，直接会被上传到服务器，而去轮询第二个参数的时候，系统就会“报参数不存在“的异常，从而停止程序的执行，绕过黑名单机制。

看到这些代码也可以明白，第一版的时候LuoKe同学绕过黑名单成功的原因是因为提交的第二个参数缺少分割boundary导致的报错，思路同样可行。

下图给出poc：

![](https://image.3001.net/images/20190814/1565763743_5d53a89fe640b.png!small)

看一下后台抛的异常：

![](https://image.3001.net/images/20190814/1565763773_5d53a8bddfba5.png!small)

##  **总结**

> 1、
> 其实我猜测这个漏洞也还有其他可能的利用方式，比如我们常提到的资源竞争（写一个写木马文件的jsp，在上传的同事疯狂访问该上传路径，这样就有可能在删除文件之前访问到jsp文件，并写入木马成功）。
>
> 2、 该漏洞归根到底还是开发意识的问题，无论如何，处理上传文件的时候还是应该牢记先校验，再上传。

 ***本文作者：Glassy@平安银行应用安全团队，转载须注明来自FreeBuf.COM**


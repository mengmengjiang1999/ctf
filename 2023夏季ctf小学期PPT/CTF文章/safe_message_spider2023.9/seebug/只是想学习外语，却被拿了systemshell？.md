**作者： Flanker  
公众号：[Flanker论安全](https://mp.weixin.qq.com/s?__biz=MzI3ODI4NDM2MA==&mid=2247483711&idx=1&sn=3635a0ff95834325c1780e0af9d34581&chksm=eb581018dc2f990e1a1633774452891777c7d143c1ce1a58533a413015732feec25bb98ed1ac&mpshare=1&scene=1&srcid=1104EqiniorjYLdrlgiVIhor&sharer_sharetime=1572834933314&sharer_shareid=bafb2678ed1f77a340809d0b35c3d277&key=e16964c072f0d5a7263fb09b2b124c9ba5219b87674100d6d7069cfb98bf78c7d399080aa12d10e93ebe0720e35348f25bd60dd38f319f09bb2ef8a28cf63d5f94fb5e4fb786875f358da09ad6efb4e3&ascene=1&uin=MzM5ODEzOTY3MQ%3D%3D&devicetype=Windows+10&version=62060833&lang=zh_CN&pass_ticket=f4E9eroPAnE%2FsCon3%2FgpDYBabRgpFy6Vqy1paT7qjGPs6ju5ZSUpR1BCoOVC8qYo
"只是想学习外语，却被拿了system shell？")**

Text-To-Speech多国语言翻译引擎引擎是Android系统的标配，上溯到Android 1.5
HTC时代就已经存在的卖点。有些小伙伴可能会用来在自己手机上学习外语，看起来比陈秘书长学外语的方式安全多了。

![](https://images.seebug.org/content/images/2019/11/df13184e-e7ff-406b-89fa-d444658d850e.jpg-w331s)

但在各式各样的厂商实现中，总能找到一些奇葩的事情，例如。。。一个看起来无任何权限的普通语言包，就能获得一个system权限持久性后门？(a.k.a
CVE-2019-16253)

![](https://images.seebug.org/content/images/2019/11/4081a35b-6181-4250-9be7-18fa1c324b72.jpg-w331s)

# 漏洞概述

概述：SamsungSMT应用是一个具有system权限的，负责对TTS功能进行综合管理的系统进程。该进程存在本地权限提升漏洞（或者feature，或者后门？），导致本地无权限应用可以以此提升至system-uid权限。

SMT应用声明了一个动态的导出receiver `com.samsung.SMT.mgr.LangPackMgr$2`, 在
`SamsungTTSService->onCreate=>LangPackMgr->init` 中启用，其监听的action是
`com.samsung.SMT.ACTION_INSTALL_FINISHED`. 这个receiver接受的broadcast有一个很有意思的参数
`SMT_ENGINE_PATH`, 该参数在经过一些预处理后被 `LangPackMgr.updateEngine`创建的线程所使用.

`com.samsung.SMT.engine.SmtTTS->reloadEngine` 最终调用了 `System->load`,
无论你相信不相信，SMT将传入的path直接在自己的进程里做了加载，反正我是信了。这造成了一个非常典型的权限提升。

值得注意的是，利用该漏洞并不需要恶意的语言包被打开或者进行其他操作。在精心构造特定的参数后，只要安装该看似无害的应用，漏洞即会被触发。这是因为
`SamsungTTSService`注册了一个receiver来监听包安装事件。只要被安装的包名满足特定的条件（最关键的条件是以com.samsung.SMT.lang开头即可，并没有签名之类的其他强校验），结合其他构造参数，该漏洞即会在安装后被立即触发。此外，由于SMT会在每次启动时重新加载所有存储的库，也就意味着该漏洞是一个持续性的，攻击者可以无感知获得一个持久性的system后门。

想象一下如果有攻击者在各大应用市场中发布了一个看似正常的语言包或者伪装成其他形式，不需要任何权限，但事实上含有攻击代码的应用。只要用户下载安装，即会被植入一个持久性提权后门。

# 漏洞分析

相关的漏洞代码如下所示：

    
    
    package com.samsung.SMT.mgr;
    
    class LangPackMgr$2 extends BroadcastReceiver {
    //...
        public void onReceive(Context arg10, Intent arg11) {
            int v7 = -1;
            if(arg11.getAction().equals("com.samsung.SMT.ACTION_INSTALL_FINISHED")) {
               //...
                int v0_1 = arg11.getIntExtra("SMT_ENGINE_VERSION", v7);
                String v2 = arg11.getStringExtra("SMT_ENGINE_PATH");
                if(v0_1 > SmtTTS.get().getEngineVersion() && (CString.isValid(v2))) {
                    if(CFile.isExist(v2)) {
                        LangPackMgr.getUpdateEngineQueue(this.a).add(new LangPackMgr$UpdateEngineInfo(v0_1, v2));
                        CLog.i(CLog$eLEVEL.D, "LangPackMgr - Add candidate engine [%d][%s]", new Object[]{Integer.valueOf(v0_1), v2});
                    }
                    else {
                        CLog.e("LangPackMgr - Invalid engine = " + v2);
                    }
                }
    //...
                LangPackMgr.decreaseTriggerCount(this.a);
                if(LangPackMgr.getTriggerPackageCount(this.a) != 0) {
                    return;
                }
    
                if(LangPackMgr.getUpdateEngineQueue(this.a).size() <= 0) {
                    return;
                }
    
                LangPackMgr.doUpdateEngine(this.a);
            }
        }
    }

在经过一些检查后， `doUpdateEngine`就将一个新的 `LangPackMgr.UpdateEngineInfo`加入到
`Queue`中排队处理：

    
    
    private void updateEngine() {
            if(this.mThreadUpdateEngine == null || !this.mThreadUpdateEngine.isAlive()) {
                this.mThreadUpdateEngine = new LangPackMgr$EngineUpdateThread(this, null);
                this.mThreadUpdateEngine.start();
            }
        }      
    
            LangPackMgr$EngineUpdateThread(LangPackMgrarg1, LangPackMgr$1arg2) {
        this(arg1); 
        } 
    
        public void run() {
        //...     
            if(LangPackMgr.getUpdateEngineQueue(this.a).size() <= 0) {
                return;     
            }
    
            try {
                v1 = LangPackMgr.getUpdateEngineQueue(this.a).poll();
                while(true) {
                    if(LangPackMgr.getUpdateEngineQueue(this.a).size() <= 0) {
                        gotolabel_20;             
                    }
    
                    v0_1 = LangPackMgr.getUpdateEngineQueue(this.a).poll(); 
    //...         
                if(v1 != null && ((LangPackMgr$UpdateEngineInfo)v1).VERSION > SmtTTS.get().getEngineVersion()) {
                    CHelper.get().set_INSTALLED_ENGINE_PATH(((LangPackMgr$UpdateEngineInfo)v1).PATH); 
                    if(SmtTTS.get().reloadEngine()) {
    ----- 
        public booleanreloadEngine() {
    //...     
            this.stop();     
            try {
                Stringv0_2 = CHelper.get().INSTALLED_ENGINE_PATH();
                if(CString.isValid(v0_2)) {
                    System.load(v0_2); //<- triggers load         
                }         
                else {            
                    gotolabel_70;         
                }    
    }

`SmtTTS.reloadEngine`最终调用 `System.load`，参数即由传入的Intent中决定。

当然，为了能成功到达这个路径，在构造POC Intent的时候仍需要考虑如下几点：

  * `SMT_ENGINE_VERSION`参数需要比内置的版本高（361811291）
  * `mTriggerCount`需要先被增加才能触发漏洞。如同上面介绍的一样， `com.samsung.SMT.SamsungTTSService`注册的receiver会去扫描包名以 `com.samsung.SMT.lang`开头的安装事件，并自增 `mTriggerCount`

但是如何静默发送出恶意Intent呢？注意SMT中以下的代码会在检查通过后，静默启动攻击者所指定的service，攻击者可以在其中触发真正的提权漏洞

    
    
    package com.samsung.SMT.mgr;
    //...
    class LangPackMgr$1 extends BroadcastReceiver {
        LangPackMgr$1(LangPackMgr arg1) {
            this.a = arg1;
            super();
        }
    
        public void onReceive(Context arg4, Intent arg5) {
            String v0 = arg5.getAction();
            String v1 = arg5.getData().getSchemeSpecificPart();
            if(((v0.equals("android.intent.action.PACKAGE_ADDED")) || (v0.equals("android.intent.action.PACKAGE_CHANGED")) || (v0.equals("android.intent.action.PACKAGE_REMOVED"))) && (v1 != null && (v1.startsWith("com.samsung.SMT.lang")))) {
                this.a.syncLanguagePack();
            }
        }
    }
    //...
        private void triggerLanguagePack() {
            if(this.mThreadTriggerLanguagePack == null || !this.mThreadTriggerLanguagePack.isAlive()) {
                this.mThreadTriggerLanguagePack = new LangPackMgr$LanguagePackTriggerThread(this, null);
                this.mThreadTriggerLanguagePack.start();
            }
        }

The checking thread reaches here:

    
    
    package com.samsung.SMT.mgr;
    //...
    
    class LangPackMgr$LanguagePackTriggerThread extends Thread {
      //...
    
        public void run() {
            Object v0_1;
            HashMap v3 = new HashMap();
            HashMap v4 = new HashMap();
            try {
                Iterator v5 = LangPackMgr.f(this.langpackmgr).getPackageManager().getInstalledPackages(0x2000).iterator();
                while(true) {
            //...
                    if(!((PackageInfo)v0_1).packageName.startsWith("com.samsung.SMT.lang")) {
                        continue;
                    }
    
                    break;
                }
            }
            catch(Exception v0) {
                goto label_53;
            }
    
            try {
                Intent v1_1 = new Intent(((PackageInfo)v0_1).packageName);
                v1_1.setPackage(((PackageInfo)v0_1).packageName);
                LangPackMgr.f(this.langpackmgr).startService(v1_1);
                LangPackMgr.increaseTriggerCount(this.langpackmgr);

此外，SMT所加载的so对部分导出函数也有一定要求，这些可以通过逆向来实现解决。

# POC总结

虽然最初只是想

![](https://images.seebug.org/content/images/2019/11/e2b9a3a4-6a5b-4f53-b03d-9dc2a88d5a1a.jpg-w331s)

但实际上却被提权了。

本文附带的POC视频展现了一个安装后获取system反弹shell的效果，如下。

同时在logcat中会出现如下日志：

    
    
    ?  ~ adb logcat | grep -i mercury   
    16:29:48.816 24289 24317 E mercury-native: somehow I'm in the library yah, my uid is 1000     
    16:29:48.885 24318 24318 E mercury-native: weasel begin connect   

日志中可以看到，我们已经获得了uid=1000，即system的权限

POC代码稍后会放在<https://github.com/flankerhqd/vendor-android-cves> 上。

不过可以放心的是，该漏洞已通过Samsung Mobile Security Rewards Program报告并修复，定级为High
Severity，厂商已经发布了补丁。在对应的应用市场更新Samsung Text-To-Speech应用至修复的版本，并检查之前安装过的SMT语言包。

对于所有的受影响厂商设备，

  * Android N,O or older的版本，请升级SMT到3.0.00.101或更高
  * Android P的系统版本：请升级SMT至3.0.02.7

该漏洞分配的编号是CVE-2019-16253。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1070/>


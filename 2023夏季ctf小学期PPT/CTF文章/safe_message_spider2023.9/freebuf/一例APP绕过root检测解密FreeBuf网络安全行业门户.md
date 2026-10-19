# 一例APP绕过root检测解密

## 前言

最近在分析一款app时遇见了root检测，数据包加密，花了时间简单研究了一下，记录下学习的过程。

## 抛出问题

打开app发现提示检测到设备为root设备，闪退。能看到提示，推测应该是java层的检测。

![](https://image.3001.net/images/20220915/1663227532_6322d68cef7fcb7d8e232.png!small)  

拖进jadx发现是加固的。

![](https://image.3001.net/images/20220915/1663227546_6322d69a9a372fa63b3a4.png!small)  

## 通过frida绕过检测

java层常见root检测大多是通过检测系统文件：一些路径下的su文件，一些root的app相关文件。

    
    
      "/data/local/bin/su",  
      "/data/local/su",  
      "/data/local/xbin/su",  
      "/dev/com.koushikdutta.superuser.daemon/",  
      "/sbin/su",  
      "/system/app/Superuser.apk",  
      "/system/bin/failsafe/su",  
      "/system/bin/su",  
      "/su/bin/su",  
      "/system/etc/init.d/99SuperSUDaemon",  
      "/system/sd/xbin/su",  
      "/system/xbin/busybox",  
      "/system/xbin/daemonsu",  
      "/system/xbin/su",  
      "/system/sbin/su",  
      "/vendor/bin/su",  
      "/cache/su",  
      "/data/su",  
      "/dev/su",  
      "/system/bin/.ext/su",  
      "/system/usr/we-need-root/su",  
      "/system/app/Kinguser.apk",  
      "/data/adb/magisk",  
      "/sbin/.magisk",  
      "/cache/.disable_magisk",  
      "/dev/.magisk.unblock",  
      "/cache/magisk.log",  
      "/data/adb/magisk.img",  
      "/data/adb/magisk.db",  
      "/data/adb/magisk_simple",  
      "/init.magisk.rc",  
      "/system/xbin/ku.sud"

检测一些root的app如magisk等。

    
    
      "com.noshufou.android.su",  
      "com.noshufou.android.su.elite",  
      "eu.chainfire.supersu",  
      "com.koushikdutta.superuser",  
      "com.thirdparty.superuser",  
      "com.yellowes.su",  
      "com.koushikdutta.rommanager",  
      "com.koushikdutta.rommanager.license",  
      "com.dimonvideo.luckypatcher",  
      "com.chelpus.lackypatch",  
      "com.ramdroid.appquarantine",  
      "com.ramdroid.appquarantinepro",  
      "com.topjohnwu.magisk",  
      "com.kingroot.kinguser",  
      "com.kingo.root",  
      "com.smedialink.oneclickroot",  
      "com.zhiqupk.root.global",  
      "com.alephzain.framaroot",  
      "com.android.vending.billing.InAppBillingService.COIN",  
      "com.android.vending.billing.InAppBillingService.LUCK",  
      "com.chelpus.luckypatcher",  
      "com.blackmartalpha",  
      "org.blackmart.market",  
      "com.allinone.free",  
      "com.repodroid.app",  
      "org.creeplays.hack",  
      "com.baseappfull.fwd",  
      "com.zmapp",  
      "com.dv.marketmod.installer",  
      "org.mobilism.android",  
      "com.android.wp.net.log",  
      "com.android.camera.update",  
      "cc.madkite.freedom",  
      "com.solohsu.android.edxp.manager",  
      "org.meowcat.edxposed.manager",  
      "com.xmodgame",  
      "com.cih.game_cih",  
      "com.charles.lpoqasert",  
      "catch_.me_.if_.you_.can_"

这里通过一些公开的脚本去绕过，直接可以绕过。

    
    
    frida -U -f com.xxxx.xxxx -l anti_root.js --no-pause

![3](https://image.3001.net/images/20220915/1663228931_6322dc036f6cb222d86c4.png!small)此时不再闪退。
![4](https://image.3001.net/images/20220915/1663228954_6322dc1ac46a42569726b.png!small)

## 数据包测试

挂上代理进行测试抓包，发现存在参数加密。

![](https://image.3001.net/images/20220915/1663228984_6322dc3863aa830807e2a.png!small)  

还是需要脱壳进行分析。 这里已经绕过了root检测，没有frida检测，直接上frida-dexdump就行。

    
    
    frida-dexdump -FU

分析后定位到类：com.xxxx.xxxx.utils.http.DESHelp 直接hook就行。

## frida rpc

只是hook加解密还是用很多不方便的地方，有时候需要去主动调用对应的加解密函数。 这里可以用brida，或者是httpdecrypt等工具。
这里提供一个通过python frida交互，使用rpc来完成主动调用。
调用也很简单，只是代码写死在了js脚本中，所用使用rpc.exports开启RPC调用接口，后面使用python来调用。

    
    
     function htddecrypt(param,key){  
          var result;  
          Java.perform(function () {  
                
              var hclass = Java.use("com.xxxx.xxxx.utils.http.DESHelp");  
              var hexarry = hclass.parseHexStr2Byte(param);  
              param = byteToString(hexarry);  
              console.log("[*] Hooking ...");  
              result = hclass.decrypt(param, key);  
              //console.log(result);   
          });  
          return result;  
      }  
    ​  
      function htdencrypt(param,key){  
          var result;  
          var enc  
          Java.perform(function () {  
              var hclass = Java.use("com.xxxx.xxxx.utils.http.DESHelp");  
              console.log(param);  
              enc = hclass.encrypt(param, key);  
              //console.log(result);   
              var hexarry = stringToByte(enc);  
              result = hclass.parseByte2HexStr(hexarry);  
          });  
          return result;  
      }      
    ​  
      rpc.exports = {    
          rpcfunc: htdencrypt,  
          rpcfunc1: htddecrypt  
    ​  
      }

通过python中代码:

    
    
    session = frida.get_usb_device().attach("com.xxxx.xxxx")     
    script = frida_rpc(session)  
    param = str(sys.argv[2])  
    ret = script.exports.rpcfunc(param,"CCCk+H%b6.MMMMkoKKK")  
    print(ret)   
    ​

![](https://image.3001.net/images/20220915/1663231913_6322e7a9210c43dd46834.png!small)

## 总结

还是一个简单的例子，现在常规的app大体思路都是这样，只能碰到问题花时间研究去解决，不能迷信通杀方案。


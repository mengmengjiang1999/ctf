***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

## 关于appdecrypt

一直以来，iOS程序逆向分析的第一步是先寻找一台越狱的iOS或iPad OS设备，然后使用frida-ios-dump等工具进行动态脱壳。而动态脱壳必须要运行APP，如果APP里进行了越狱检测，那么很有可能无法进行脱壳。

appdecrypt是一款可以运行在iOS和macOS上的脱壳程序，该工具基于Swift
5实现其主要功能。可以在越狱的iPhone或者iPad上进行静态脱壳（无需运行APP）。

但appdecrypt强大的地方在于可以在装有M1芯片的Mac上对app进行脱壳，并且Mac无需关闭SIP，这样一来就完全不需要考虑越狱检测的事情，脱壳成功率大大提高。

## 功能介绍

    
    
    Version 2.0
    
    appdecrypt is a tool to make decrypt application encrypted binaries on macOS when SIP-enabled.
    
    Examples:
        mac:
            appdecrypt /Applicaiton/Test.app /Users/admin/Desktop/Test.app
        iPhone:
            appdecrypt /var/containers/Bundle/Application/XXXXXX /tmp
    
    USAGE: appdecrypt encryptMachO_Path decryptMachO_Path
    
    ARGUMENTS:
      <encryptApp_Path>     The encrypt app file path.
      <decrypt_Path>        The path output file.
    
    OPTIONS:
      -h, --help              Show help information.
    

## 使用方法

### 在装有 M1 CPU的Mac上

    
    
    > git clone https://github.com/paradiseduo/appdecrypt.git
    > cd appdecrypt
    > chmod +x build-macOS_arm.sh
    > ./build-macOS_arm.sh
    > cd .build/release
    > ./appdecrypt /Applicaiton/Test.app /Users/admin/Desktop/Test.app
    Success to copy file.
    Dump /Applications/Test.app/Wrapper/Test.app/Test Success
    Dump /Applications/Test.app/Wrapper/Test.app/PlugIns/TestNotificationService.appex/TestNotificationService Success
    Dump /Applications/Test.app/Wrapper/Test.app/Frameworks/trackerSDK.framework/trackerSDK Success
    Dump /Applications/Test.app/Wrapper/Test.app/Frameworks/AgoraRtcKit.framework/AgoraRtcKit Success
    > cd /Users/admin/Desktop/Test.app
    > ls
    WrappedBundle Wrapper
    > cd Wrapper
    > ls
    BundleMetadata.plist Test.app            iTunesMetadata.plist
    

### 在越狱的iPhone上

    
    
    > git clone https://github.com/paradiseduo/appdecrypt.git
    > cd appdecrypt
    > chmod +x build-iOS.sh
    > ./build-iOS.sh
    > scp -P 2222 global.xml root@127.0.0.1:/tmp
    > cd .build/release
    > scp -P 2222 appdecrypt root@127.0.0.1:/tmp
    
    // In iPhone shell
    > cd /tmp
    > ldid -Sglobal.xml appdecrypt 
    > ./appdecrypt /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8 /tmp
    Success to copy file.
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/Aweme Success
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/PlugIns/AwemeDYShareExtension.appex/AwemeDYShareExtension Success
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/PlugIns/AwemeNotificationService.appex/AwemeNotificationService Success
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/PlugIns/AwemeWidgetExtension.appex/AwemeWidgetExtension Success
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/PlugIns/AWEVideoWidget.appex/AWEVideoWidget Success
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/PlugIns/AwemeBroadcastExtension.appex/AwemeBroadcastExtension Success
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/PlugIns/AWEFriendsWidgets.appex/AWEFriendsWidgets Success
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/PlugIns/AwemeVideoNotification.appex/AwemeVideoNotification Success
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/Frameworks/ByteRtcEngineKit.framework/ByteRtcEngineKit Success
    Dump /var/containers/Bundle/Application/23E4B0B4-7275-46CE-8EEA-18CADE61FDB8/Aweme.app/Frameworks/byteaudio.framework/byteaudio Success
    > ls
    Payload/
    > cd Payload
    > ls
    Aweme.app/  BundleMetadata.plist  iTunesMetadata.plist
    

# 项目地址

[https://github.com/paradiseduo/appdecrypt﻿](https://github.com/paradiseduo/appdecrypt)


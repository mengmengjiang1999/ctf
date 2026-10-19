**今天给大家介绍的是一款名叫Scrounger
的工具，广大研究人员可以使用这款工具来对移动端应用程序的安全性进行测试。首先，这款工具参考和借鉴了很多目前安全社区里优秀的测试工具，其次就是它能够有效地找出移动端应用程序中存在的安全漏洞。**

![11111111111111111111.png](https://image.3001.net/images/20181013/1539437555_5bc1f3f3b8b9c.png!small)

虽然现在社区里有很多其他的移动端应用程序分析工具，但是没有一款是能够同时适用于Android和iOS端的。Scrounger这款类似于Metasploit的工具虽然不能完全自动化地对目标进行渗透测试，但是它可以帮助渗透测试人员完成各种安全评估工作。

## 区别

Scrounger跟其他工具的区别主要在于：

> 1\. 适用于Android和iOS；
>
> 2\. 提供了类似Metasploit的命令控制台和模块；
>
> 3\. 提供了多种功能模块；
>
> 4\. 可轻松扩展其他功能；

## 技术细节

首先提醒大家，所有由Scrounger发现并识别的内容大家都需要进行人工二次确认。

在使用功能模块时，需要用到Android或iOS设备，Scrounger要求目标设备已root或已越狱。

Scrounger已在iOS 11和Android 8.1上进行过测试，并且只支持Python 2.7。

## 工具安装

    
    
    git clone <https://github.com/nettitude/scrounger.git>
    
    cd scrounger
    
    bash setup.sh
    
    pip install -r requirements.txt
    
    python setup.py install

## 开发环境

    
    
    git pull <https://github.com/nettitude/scrounger.git>
    
    cd scrounger
    
    bash setup.sh
    
    pip install -r requirements.txt
    
    python setup.py develop

## 工具更新

    
    
    cd scrounger
    
    git pull
    
    python setup.py install –upgrade

## 依赖库

### Android模块

> 1\.
> java(<http://www.oracle.com/technetwork/java/javase/downloads/index.html>)
>
> 2\. jd-cli(<https://github.com/kwart/jd-cmd>)
>
> 3\. apktool(<https://ibotpeaches.github.io/Apktool/>)
>
> 4\. d2j-dex2jar(<https://github.com/pxb1988/dex2jar>)
>
> 5\. adb(<https://developer.android.com/studio/releases/platform-tools>)
>
> 6\. avdmanager(可选): (<https://developer.android.com/studio/#downloads>)

### iOS模块

> 1\. jtool(Linux) (<http://www.newosxbook.com/tools/jtool.html>)
>
> 2\. otool(MacOS) (<https://developer.apple.com/xcode/>)
>
> 3\. ldid(<https://github.com/daeken/ldid.git>)
>
> 4\. iproxy(Package: libimobiledevice)
>
> 5\. lsusb(Package: usbutils)
>
> 6\. unzip

### iOS库

    
    
    dump_backup_flag
    
    dump_file_protection
    
    dump_keychain
    
    dump_log
    
    listapps

## 安装脚本

### Linux

    
    
    #install iproxy lsusb
    
    sudoapt-get install libimobiledevice usbutils
    
     
    
    #install jd-cli
    
    if [! -x "$(which jd-cli)" ]; then
    
        curl -L -o /tmp/jdcli.zip<https://github.com/kwart/jd-cmd/releases/download/jd-cmd-0.9.2.Final/jd-cli-0.9.2-dist.zip>
    
        unzip /tmp/jdcli.zip/usr/local/share/jd-cli
    
        ln -s /usr/local/share/jd-cli/jd-cli/usr/local/bin/jd-cli
    
        ln -s /usr/local/share/jd-cli/jd-cli.jar/usr/local/bin/jd-cli.jar
    
        rm -rf /tmp/jdcli.zip
    
    fi
    
    
    #install apktool
    
    if [! -x "$(which apktool)" ]; then
    
        mkdir /usr/local/share/apktool
    
        curl -L -o /usr/local/share/apktool/apktool<https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/osx/apktool>
    
        curl -L -o/usr/local/share/apktool/apktool.jar <https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.3.3.jar>
    
        chmod +x /usr/local/share/apktool/usr/local/share/apktool/apktool.jar
    
        ln -s /usr/local/share/apktool/usr/local/bin/apktool
    
        ln -s /usr/local/share/apktool.jar/usr/local/bin/apktool.jar
    
    fi
    
    
    #install dex2jar
    
    if [! -x "$(which d2j-dex2jar)" ]; then
    
        curl -L -o /tmp/d2j.zip<https://github.com/pxb1988/dex2jar/files/1867564/dex-tools-2.1-SNAPSHOT.zip>
    
        unzip /tmp/d2j.zip -d /tmp/d2j
    
        dirname=$(ls --color=none /tmp/d2j)
    
        mv /tmp/d2j/$dirname/usr/local/share/d2j-dex2jar
    
        ln -s/usr/local/share/d2j-dex2jar/d2j-dex2jar.sh /usr/local/bin/d2j-dex2jar.sh
    
        ln -s/usr/local/share/d2j-dex2jar/d2j-apk-sign.sh /usr/local/bin/d2j-apk-sign.sh
    
        rm -rf /tmp/d2j.zip
    
    fi
    
    if [! -x "$(which d2j-dex2jar)" ]; then
    
        ln -s /usr/local/bin/d2j-dex2jar.sh/usr/local/bin/d2j-dex2jar
    
    fi
    
    
    #install adb
    
    if [! -x "$(which adb)" ]; then
    
        curl -L -o /tmp/platform-tools.zip<https://dl.google.com/android/repository/platform-tools-latest-linux.zip>
    
        unzip /tmp/platform-tools.zip -d /tmp/pt
    
        mv /tmp/pt/platform-tools /usr/local/share/
    
        ln -s /usr/local/share/platform-tools/adb/usr/local/bin/adb
    
        ln -s/usr/local/share/platform-tools/fastboot /usr/local/bin/fastboot
    
    fi
    
    
    #install ldid
    
    if [! -x "$(which ldid)" ]; then
    
        git clone<https://github.com/daeken/ldid.git> /tmp/ldid
    
        cd /tmp/ldid
    
        ./make.sh
    
        mv ldid /usr/local/bin/
    
        cd /tmp
    
        rm -rf /tmp/ldid
    
    fi
    
    
    #install jtool
    
    if [! -x "$(which jtool)" ]; then
    
        curl-L -o /tmp/jtool.tar <http://www.newosxbook.com/tools/jtool.tar>
    
        mkdir /tmp/jtool
    
        tar xvf /tmp/jtool.tar -C /tmp/jtool
    
        mv /tmp/jtool/jtool.ELF64/usr/local/bin/jtool
    
        rm -rf /tmp/jtool.tar /tmp/jtool
    
    fi
    
    
    #install scrounger
    
    gitclone git@github.com:nettitude/scrounger.git
    
    cdscrounger
    
    pipinstall -r requirements.txt
    
    pythonsetup.py install
    
    MacOS
    
    
    #install iproxy ldid lsusb
    
    brewtap jlhonora/lsusb && brew install lsusb libimobiledevice ldid
    
    
    #install jd-cli
    
    if [! -x "$(which jd-cli)" ]; then
    
        curl -L -o /tmp/jdcli.zip<https://github.com/kwart/jd-cmd/releases/download/jd-cmd-0.9.2.Final/jd-cli-0.9.2-dist.zip>
    
        unzip /tmp/jdcli.zip/usr/local/share/jd-cli
    
        ln -s /usr/local/share/jd-cli/jd-cli/usr/local/bin/jd-cli
    
        ln -s /usr/local/share/jd-cli/jd-cli.jar/usr/local/bin/jd-cli.jar
    
        rm -rf /tmp/jdcli.zip
    
    fi
    
    
    #install apktool
    
    if [! -x "$(which apktool)" ]; then
    
        mkdir /usr/local/share/apktool
    
        curl -L -o /usr/local/share/apktool/apktool<https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/osx/apktool>
    
        curl -L -o/usr/local/share/apktool/apktool.jar<https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.3.3.jar>
    
        chmod +x /usr/local/share/apktool/usr/local/share/apktool/apktool.jar
    
        ln -s /usr/local/share/apktool/usr/local/bin/apktool
    
        ln -s /usr/local/share/apktool.jar/usr/local/bin/apktool.jar
    
    fi
    
    
    #install dex2jar
    
    if [! -x "$(which d2j-dex2jar)" ]; then
    
        curl -L -o /tmp/d2j.zip<https://github.com/pxb1988/dex2jar/files/1867564/dex-tools-2.1-SNAPSHOT.zip>
    
        unzip /tmp/d2j.zip -d /tmp/d2j
    
        dirname=$(ls --color=none /tmp/d2j)
    
        mv /tmp/d2j/$dirname/usr/local/share/d2j-dex2jar
    
        ln -s/usr/local/share/d2j-dex2jar/d2j-dex2jar.sh /usr/local/bin/d2j-dex2jar.sh
    
        ln -s /usr/local/share/d2j-dex2jar/d2j-apk-sign.sh/usr/local/bin/d2j-apk-sign.sh
    
        rm -rf /tmp/d2j.zip
    
    fi
    
    if [! -x "$(which d2j-dex2jar)" ]; then
    
        ln -s /usr/local/bin/d2j-dex2jar.sh/usr/local/bin/d2j-dex2jar
    
    fi
    
    
    #install adb
    
    if [! -x "$(which adb)" ]; then
    
        curl -L -o /tmp/platform-tools.zip<https://dl.google.com/android/repository/platform-tools-latest-darwin.zip>
    
        unzip /tmp/platform-tools.zip -d /tmp/pt
    
        mv /tmp/pt/platform-tools /usr/local/share/
    
        ln -s /usr/local/share/platform-tools/adb/usr/local/bin/adb
    
        ln -s/usr/local/share/platform-tools/fastboot /usr/local/bin/fastboot
    
    fi
    
    
    #install Xcode / command line tools
    
    xcode-select--install
    
    
    #install scrounger
    
    gitclone git@github.com:nettitude/scrounger.git
    
    cdscrounger
    
    pipinstall -r requirements.txt
    
    pythonsetup.py install

### 添加自定义模块

在安装该工具时，会自动创建一个文件夹“~/.scrounger”，该文件夹中会有一个名叫“modules/custom”的文件夹，该文件夹负责存储相应的Scrounger模块，其结构例如：analysis/android/module_name。

## 示例

添加下列模块（~/.scrounger/modules/custom/misc/test.py）：

    
    
    from scrounger.core.module import BaseModule
    
     
    
    class Module(BaseModule):
    
        meta = {
    
            "author": "RDC",
    
            "description":"""Just a Test module""",
    
            "certainty": 100
    
        }
    
     
    
        options = [
    
            {
    
                "name":"output",
    
                "description":"local output directory",
    
                "required": False,
    
                "default": None
    
            },
    
        ]
    
     
    
        def run(self):
    
     
    
            print("This is a print from thecustom module")
    
     
    
            return {
    
                "print": "This willbe print by scrounger's console."
    
            }

## 执行

    
    
    $scrounger-console
    
    Starting Scrounger console...
    
     
    
    scrounger> list custom/misc
    
     
    
    Module            Certainty  Author Description
    
    ------            ---------  ------ -----------    
    custom/misc/test  100%      RDC     Just a Test module
    
     
    
    scrounger> use custom/misc/test
    
     
    
    scroungercustom/misc/test > options
    
     
    
    GlobalOptions:
    
     
    
        Name   Value
    
        ----   -----    
        device
    
        output /tmp/scrounger-app
    
     
    
    ModuleOptions (custom/misc/test):
    
     
    
        Name   Required  Description             Current Setting
    
        ----   --------  -----------             ---------------    
        output False     local outputdirectory  /tmp/scrounger-app
    
     
    
    scroungercustom/misc/test > run
    
    Thisis a print from the custom module
    
    [+]This will be print by scrounger's console.
    
     
    
    scroungercustom/misc/test >

## 示例

### 列举/搜索模块

    
    
    $scrounger-console
    
    StartingScrounger console...
    
     
    
    >help
    
     
    
    Documentedcommands (type help <topic>):
    
    ========================================
    
    add_device  devices list     print  results set   unset
    
    back        help    options  quit   run     show  use
    
     
    
     
    
    >help list
    
    Listsall available modules
    
     
    
    >list ios
    
     
    
    Module                                  CertaintyAuthor Description
    
    ------                                  --------------- -----------    
    analysis/ios/app_transport_security     90%      RDC    Checks if there are anyApplication Transport Security misconfigurations
    
    analysis/ios/arc_support                90%       RDC   Checks if a binary was compiled with ARC support
    
    analysis/ios/backups                    90%       RDC   Checks the application's files have the backup flag on
    
    analysis/ios/clipboard_access           75%       RDC   Checks if the application disables clipboard access
    
    analysis/ios/debugger_detection         75%       RDC   Checks if the applicationdetects debuggers
    
    analysis/ios/excessive_permissions      90%      RDC    Checks if the applicationuses excessive permissions
    
    analysis/ios/file_protection            90%       RDC   Checks the application's files specific protection flags
    
    analysis/ios/full_analysis              100%      RDC   Runs all modules in analysis and writes a report into the outputdirectory
    
    analysis/ios/insecure_channels          50%       RDC   Checks if the application uses insecure channels
    
    analysis/ios/insecure_function_calls    75%      RDC    Checks if the applicationuses insecure function calls
    
    analysis/ios/jailbreak_detection        60%       RDC   Checks if the application implements jailbreak detection
    
    analysis/ios/logs                       60%      RDC    Checks if the applicationlogs to syslog
    
    analysis/ios/passcode_detection         60%       RDC   Checks if the application checks for passcode being set
    
    analysis/ios/pie_support                100%      RDC   Checks if the application was compiled with PIE support
    
    analysis/ios/prepared_statements        60%       RDC   Checks if the application uses sqlite calls and if so checks if it alsouses prepared statements
    
    analysis/ios/ssl_pinning                60%       RDC   Checks if the application implements SSL pinning
    
    analysis/ios/stack_smashing             90%       RDC   Checks if a binary was compiled stack smashing protections
    
    analysis/ios/third_party_keyboard       65%      RDC    Checks if an applicationchecks of third party keyboards
    
    analysis/ios/unencrypted_communications80%       RDC    Checks if the application implementscommunicates over unencrypted channels
    
    analysis/ios/unencrypted_keychain_data  70%      RDC    Checks if the applicationsaves unencrypted data in the keychain
    
    analysis/ios/weak_crypto                60%       RDC   Checks if the application uses weak crypto
    
    analysis/ios/weak_random                50%       RDC   Checks if a binary uses weak random functions
    
    analysis/ios/weak_ssl_ciphers           50%       RDC   Checks if a binary uses weak SSL ciphers
    
    misc/ios/app/archs                      100%      RDC   Gets the application's available architectures
    
    misc/ios/app/data                       100%      RDC   Gets the application's data from the remote device
    
    misc/ios/app/entitlements               100%      RDC   Gets the application's entitlements
    
    misc/ios/app/flags                      100%      RDC   Gets the application's compilation flags
    
    misc/ios/app/info                       100%      RDC   Pulls the Info.plist info from the device
    
    misc/ios/app/start                      100%      RDC   Launches an application on the remote device
    
    misc/ios/app/symbols                    100%      RDC   Gets the application's symbols out of an installed application    on thedevice
    
    misc/ios/class_dump                     100%      RDC   Dumps the classes out of a decrypted binary
    
    misc/ios/decrypt_bin                   100%      RDC   Decrypts and pulls a binary application
    
    misc/ios/install_binaries               100%      RDC   Installs iOS binaries required to run some checks
    
    misc/ios/keychain_dump                  100%      RDC   Dumps contents from the connected device's keychain
    
    misc/ios/local/app/archs                100%      RDC   Gets the application's available architectures
    
    misc/ios/local/app/entitlements         100%      RDC   Gets the application's entitlements from a local binary and saves themto file
    
    misc/ios/local/app/flags                100%      RDC   Gets the application's compilation flags using local tools. Will lookfor otool and    jtool in the PATH.
    
    misc/ios/local/app/info                 100%      RDC   Pulls the Info.plist info from the unzipped IPA file and saves an XMLfile with    it's contents to the output folder
    
    misc/ios/local/app/symbols              100%      RDC   Gets the application's symbols out of an installed application on thedevice
    
    misc/ios/local/class_dump              100%      RDC   Dumps the classes out of a decrypted binary
    
    misc/ios/pull_ipa                       100%      RDC   Pulls the IPA file from a remote device
    
    misc/ios/unzip_ipa                      100%      RDC   Unzips the IPA file into the output directory

## 使用Misc模块

    
    
    $scrounger-console
    
    StartingScrounger console...
    
     
    
    >use misc/android/decompile_apk
    
     
    
    misc/android/decompile_apk> options
    
     
    
    GlobalOptions:
    
     
    
        Name  Value
    
        ----  -----    
        device
    
        output /tmp/scrounger-app
    
     
    
    ModuleOptions (misc/android/decompile_apk):
    
     
    
        Name  Required Description               Current Setting
    
        ----  -------- -----------               ---------------    
        output True     local output directory     /tmp/scrounger-app
    
        apk   True     local path to the APKfile
    
     
    
    misc/android/decompile_apk> set output scrounger-demo-output
    
     
    
    misc/android/decompile_apk> set apk ./a.apk
    
     
    
    misc/android/decompile_apk> options
    
     
    
    GlobalOptions:
    
     
    
        Name  Value
    
        ----  -----    
        device
    
        output /tmp/scrounger-app
    
     
    
    ModuleOptions (misc/android/decompile_apk):
    
     
    
        Name  Required Description               Current Setting
    
        ----  -------- -----------               ---------------    
        output True     local output directory     scrounger-demo-output
    
        apk   True     local path to the APKfile ./a.apk
    
     
    
    misc/android/decompile_apk> run
    
    2018-05-0110:29:53 -                  decompile_apk: Creating decompilation directory
    
    2018-05-0110:29:53 -                  decompile_apk : Decompiling application
    
    2018-05-0110:29:59 -                       manifest: Checking for AndroidManifest.xml file
    
    2018-05-0110:29:59 -                       manifest: Creating manifest object
    
    [+]Application decompiled to scrounger-demo-output/com.eg.challengeapp.decompiled

## 使用其他模块输出的结果

    
    
    misc/android/decompile_apk> show results
    
     
    
    Results:
    
     
    
        Name                             Value
    
        ----                             -----    
        com.eg.challengeapp_decompiledscrounger-demo-output/com.eg.challengeapp.decompiled
    
     
    
    misc/android/decompile_apk> use analysis/android/permissions
    
     
    
    analysis/android/permissions> options
    
     
    
    GlobalOptions:
    
     
    
        Name  Value
    
        ----  -----    
        device
    
        output /tmp/scrounger-app
    
     
    
    ModuleOptions (analysis/android/permissions):
    
     
    
        Name           Required Description                                           CurrentSetting
    
        ----           -------- -----------                                       ---------------    
        decompiled_apk True     local folder containing the decompiled apkfile
    
        permissions    True    dangerous permissions to check for, seperated by ;android.permission.GET_TASKS;android.permission.BIND_DEVICE_ADMIN;android.permission.USE_CREDENTIALS;com.android.browser.permission.READ_HISTORY_BOOKMARKS;android.permission.PROCESS_OUTGOING_CA
    
     
    
    analysis/android/permissions> print option permissions
    
     
    
    OptionName: permissions
    
    Value:android.permission.GET_TASKS;android.permission.BIND_DEVICE_ADMIN;android.permission.USE_CREDENTIALS;com.android.browser.permission.READ_HISTORY_BOOKMARKS;android.permission.PROCESS_OUTGOING_CALLS;android.permission.READ_LOGS;android.permission.READ_SMS;android.permission.READ_CALL_LOG;android.permission.RECORD_AUDIO;android.permission.MANAGE_ACCOUNTS;android.permission.RECEIVE_SMS;android.permission.RECEIVE_MMS;android.permission.WRITE_CONTACTS;android.permission.DISABLE_KEYGUARD;android.permission.WRITE_SETTINGS;android.permission.WRITE_SOCIAL_STREAM;android.permission.WAKE_LOCK
    
     
    
    analysis/android/permissions> set decompiled_apk result:com.eg.challengeapp_decompiled
    
     
    
    analysis/android/permissions> options
    
     
    
    GlobalOptions:
    
     
    
        Name  Value
    
        ----  -----    
        device
    
        output /tmp/scrounger-app
    
     
    
    ModuleOptions (analysis/android/permissions):
    
     
    
        Name           Required Description                                           CurrentSetting
    
        ----           -------- -----------                                       ---------------    
        decompiled_apk True     local folder containing the decompiled apkfile   result:com.eg.challengeapp_decompiled
    
        permissions    True    dangerous permissions to check for, seperated by ;android.permission.GET_TASKS;android.permission.BIND_DEVICE_ADMIN;android.permission.USE_CREDENTIALS;com.android.browser.permission.READ_HISTORY_BOOKMARKS;android.permission.PROCESS_OUTGOING_CA
    
     
    
    analysis/android/permissions> run
    
    2018-05-0110:54:58 -                       manifest: Checking for AndroidManifest.xml file
    
    2018-05-0110:54:58 -                       manifest: Creating manifest object
    
    2018-05-0110:54:58 -                    permissions: Analysing application's manifest permissions
    
    [+]Analysis result:
    
    TheApplication Has Inadequate Permissions
    
        Report: True
    
        Details:
    
    *android.permission.READ_SMS

## 使用设备

    
    
    $scrounger-console
    
    StartingScrounger console...
    
     
    
    >show devices
    
     
    
    AddedDevices:
    
     
    
        Scrounger ID Device OS Identifier
    
        ------------ --------- ----------    
     
    
    >add_device
    
    android  ios
    
     
    
    >add_device android 00cd7e67ec57c127
    
     
    
    >show devices
    
     
    
    AddedDevices:
    
     
    
        Scrounger ID Device OS Identifier
    
        ------------ --------- ----------    
        1           android   00cd7e67ec57c127
    
     
    
    >set global device 1
    
     
    
    >options
    
     
    
    GlobalOptions:
    
     
    
        Name  Value
    
        ----  -----    
        device 1
    
        output /tmp/scrounger-app
    
     
    
    >use misc/list_apps
    
     
    
    misc/list_apps> options
    
     
    
    GlobalOptions:
    
     
    
        Name  Value
    
        ----  -----    
        device 1
    
        output /tmp/scrounger-app
    
     
    
    ModuleOptions (misc/list_apps):
    
     
    
        Name  Required Description           Current Setting
    
        ----  -------- -----------           ---------------    
        output False    local output directory /tmp/scrounger-app
    
        device True     the remote device      1
    
     
    
    misc/list_apps> unset output
    
     
    
    misc/list_apps> options
    
     
    
    GlobalOptions:
    
     
    
        Name  Value
    
        ----  -----    
        device 1
    
        output /tmp/scrounger-app
    
     
    
    ModuleOptions (misc/list_apps):
    
     
    
        Name  Required Description           Current Setting
    
        ----  -------- -----------           ---------------    
        output False    local output directory
    
        device True     the remote device      1
    
     
    
    misc/list_apps> run
    
    [+]Applications installed on 00cd7e67ec57c127:
    
     
    
    com.android.sharedstoragebackup
    
    com.android.providers.partnerbookmarks
    
    com.google.android.apps.maps
    
    com.google.android.partnersetup
    
    de.codenauts.hockeyapp
    
    ...

## 命令行帮助

    
    
    $scrounger --help
    
    usage:scrounger [-h] [-m analysis/ios/module1;analysis/ios/module2]
    
                     [-aargument1=value1;argument1=value2;]
    
                     [-f/path/to/the/app.[apk|ipa]] [-d device_id] [-l] [-o]
    
                     [-p /path/to/full-analysis.json] [-V][-D]
    
     
    
       _____
    
      / ____|
    
     | (___  ___ _ __ ___  _   _ _ __  __ _  ___ _ __
    
      \___ \ / __| '__/ _ \| | | | '_ \ / _` |/ _ \'__|
    
      ____) | (__| | | (_) | |_| | | | | (_| |  __/ |
    
     |_____/ \___|_|  \___/ \__,_|_| |_|\__, |\___|_|
    
                                         __/ |
    
                                        |___/
    
     
    
    optionalarguments:
    
      -h, --help            show this help message and exit
    
      -m analysis/ios/module1;analysis/ios/module2,--modules analysis/ios/module1;analysis/ios/module2
    
                            modules to be run -seperated by ; - will be run in order
    
      -a argument1=value1;argument1=value2;,--arguments argument1=value1;argument1=value2;
    
                            arguments for themodules to be run
    
      -f /path/to/the/app.[apk|ipa],--full-analysis /path/to/the/app.[apk|ipa]
    
                            runs a full analysis onthe application
    
      -d device_id, --device device_id
    
                            device to be used bythe modules
    
      -l, --list            list available devices and modules
    
      -o, --options         prints the required options for theselected modules
    
      -p /path/to/full-analysis.json,--print-results /path/to/full-analysis.json
    
                            prints the results of afull analysis json file
    
      -V, --verbose         prints more information when runningthe modules
    
      -D, --debug           prints more information when runningscrounger

## 使用命令行

    
    
    $scrounger -o -m "misc/android/decompile_apk"
    
     
    
    ModuleOptions (misc.android.decompile_apk):
    
     
    
        Name  Required Description               Default
    
        ----  -------- -----------               -------    
        output True     local output directory     None
    
        apk   True     local path to the APKfile None
    
     
    
    $scrounger -m "misc/android/decompile_apk" -a"apk=./a.apk;output=./cli-demo"
    
    ExcutingModule 0
    
    2018-05-0111:17:42 -                  decompile_apk: Creating decompilation directory
    
    2018-05-0111:17:42 -                  decompile_apk: Decompiling application
    
    2018-05-0111:17:46 -                       manifest: Checking for AndroidManifest.xml file
    
    2018-05-0111:17:46 -                       manifest: Creating manifest object
    
    [+]Application decompiled to ./cli-demo/com.eg.challengeapp.decompiled

### 演示视频

视频地址：<https://asciinema.org/a/hC7sfGHVc5x7CWa57IXcGb3Um>

***参考来源：[scrounger](https://github.com/nettitude/scrounger)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


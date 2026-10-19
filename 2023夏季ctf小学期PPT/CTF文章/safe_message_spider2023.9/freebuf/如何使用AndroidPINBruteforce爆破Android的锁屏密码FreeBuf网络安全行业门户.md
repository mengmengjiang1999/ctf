![](https://image.3001.net/images/20210426/1619411234_60864122015f18ec45e2d.jpg!small)

## 写在前面的话

在这篇文章中，我们将教大家如何通过暴力破解Android手机的锁屏密码来解锁Android设备。并介绍Android-PIN-Bruteforce工具，该工具可以将你的Kali
Nethunter手机转换成一台针对Android设备的暴力破解PIN码设备，而且无需进行Root也无需adb。

Android-PIN-Bruteforce需要使用一条USB
OTG线来将锁定的手机跟Nethunter设备连接，它会模拟一个键盘，并自动尝试输入PIN码，然后不断地进行暴力破解尝试。

![](https://image.3001.net/images/20210426/1619411245_6086412dd782b38e20c0d.png!small)

> [Nethunter手机] <\--> [USB线] <\--> [USB OTG适配器] <\--> [锁定的Android手机]

USB HID小工具驱动程序可以提供USB HID模拟功能，这将允许Android
Nethunter设备在锁定的Android手机中模拟出一个键盘，这就好比直接将实体键盘跟锁屏手机连接在了一起。

对于三星S5来说，尝试所有可能的4位PIN码需要大概16.6个小时，但如果使用优化后的PIN码列表之后，可能就不需要这么长的时间了。

## 设备要求

> 一台锁定的Android手机
>
> 一台Nethunter手机（或者任意支持HID内核的已Root的Android设备）
>
> USB OTG线缆/适配器
>
> 标准充电线

## 功能介绍

> 爆破1-10位任意长度的PIN码；
>
> 使用配置文件以支持不同的手机；
>
> 针对3、4、5、6位PIN码提供了优化后的PIN码列表；
>
> 绕过手机弹窗，包括低电量警告；
>
> 检测手机何时拔下插头或关机，并在重试时每5秒等待一次；
>
> 每尝试X个PIN码后可配置N秒延迟；
>
> 日志记录

## 执行脚本

如果你将脚本安装到了/sdcard/路径下，你就可以通过下列命令执行Android-PIN-Bruteforce了：

    
    
    bash ./android-pin-bruteforce

注意，Android会使用noexec标签挂载/sdcard，你可以可以使用mount命令进行验证。

## 工具使用

    
    
    Android-PIN-Bruteforce (0.1) is used to unlock an Android phone (or device) by bruteforcing the lockscreen PIN.
    
      Find more information at: https://github.com/urbanadventurer/Android-PIN-Bruteforce
    
     
    
    Commands:
    
      crack                Begin cracking PINs
    
      resume               Resume from a chosen PIN
    
      rewind               Crack PINs in reverse from a chosen PIN
    
      diag                 Display diagnostic information
    
      version              Display version information and exit
    
     
    
    Options:
    
      -f, --from PIN       Resume from this PIN
    
      -a, --attempts       Starting from NUM incorrect attempts
    
      -m, --mask REGEX     Use a mask for known digits in the PIN
    
      -t, --type TYPE      Select PIN or PATTERN cracking
    
      -l, --length NUM     Crack PINs of NUM length
    
      -c, --config FILE    Specify configuration file to load
    
      -p, --pinlist FILE   Specify a custom PIN list
    
      -d, --dry-run        Dry run for testing. Doesn't send any keys.
    
      -v, --verbose        Output verbose logs
    
     
    
    Usage:
    
      android-pin-bruteforce <command> [options]

## PIN码列表

默认配置下，工具会使用优化后的PIN码列表，用户也可以选择使用自定义PIN码列表。

### 破解不同长度的PIN码

此时可以使用--length命令行选项。

下列命令可以破解3位PIN码：

    
    
    ./android-pin-bruteforce crack --length 3

下列命令可以破解6位PIN码：

    
    
    ./android-pin-bruteforce crack --length 6

### 使用掩码破解

我们可以使用正则表达式来指定破解密码：

    
    
    ./android-pin-bruteforce crack --mask "...[45]" --dry-run

## 项目地址

 **Android-PIN-Bruteforce：** https://github.com/urbanadventurer/Android-PIN-Bruteforce


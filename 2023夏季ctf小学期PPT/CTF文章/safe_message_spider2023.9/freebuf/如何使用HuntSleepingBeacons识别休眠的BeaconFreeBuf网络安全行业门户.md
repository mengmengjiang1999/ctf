![](https://image.3001.net/images/20220630/1656602662_62bdc026710d238e89f88.png!small)

## 关于Hunt-Sleeping-Beacons

Hunt-Sleeping-Beacons项目的主要功能是帮助广大研究人员在运行时或其他正在运行进程的上下文场景中识别休眠的Beacon。为了实现这个目标，我们通过观察发现，Beacon会在回调过程中尝试调用sleep函数。在调用sleep的过程中，会将线程的状态设置为“DelayExecution”，而我们就可以将其作为第一个指标来识别线程是否在执行某个Beacon。

将所有状态为“DelayExecution”的线程全部枚举出来之后，我们就可以通过多种度量指标来识别潜在的休眠Beacon了。

## 度量指标

> 1、如果Beacon不使用基于文件的内存，那么NtDelayExecution的调用堆栈将包含无法与磁盘上的文件关联的内存区域；
>
> 2、如果Beacon使用了模块Stomping技术，则修改NtDelayExecution调用堆栈中的一个模块；
>
> 3、通过枚举标记为私有（非共享）存储的内存区域，可以对睡眠的内联钩子进行指纹识别；
>
>
> 4、由于Beacon等待命令的时间比实际执行代码的时间要长，因此可以通过比较SYSTEM_THREAD_INFORMATION的KernelTime和UserTime字段来对其进行指纹识别；

为了减少误报率，我们只考虑使用wininet.dll或winhttp.dll。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/thefLink/Hunt-Sleeping-Beacons.git

## 工具使用

### 不基于文件的Beacon样例

    
    
    [!] Suspicious Process: PhantomDllHollower.exe
    
     
    
            [*] Thread (9192) has State: DelayExecution and abnormal calltrace:
    
     
    
                    NtDelayExecution -> C:\WINDOWS\SYSTEM32\ntdll.dll
    
                    SleepEx -> C:\WINDOWS\System32\KERNELBASE.dll
    
                    0x00007FF8C13A103F -> Unknown or modified module
    
                    0x000001E3C3F48FD0 -> Unknown or modified module
    
                    0x00007FF700000000 -> Unknown or modified module
    
                    0x00007FF7C00000BB -> Unknown or modified module
    
     
    
            [*] Suspicious Sleep() found
    
            [*] Sleep Time: 600s

### 使用了模块Stomping的Beacon样例

    
    
    [!] Suspicious Process: beacon.exe (5296)
    
     
    
           [*] Thread (2968) has State: DelayExecution and uses potentially stomped module
    
           [*] Potentially stomped module: C:\Windows\SYSTEM32\xpsservices.dll
    
     
    
                   NtDelayExecution -> C:\Windows\SYSTEM32\ntdll.dll
    
                   SleepEx -> C:\Windows\System32\KERNELBASE.dll
    
                   DllGetClassObject -> C:\Windows\SYSTEM32\xpsservices.dll
    
     
    
           [*] Suspicious Sleep() found
    
           [*] Sleep Time: 5s

### Beacon内联钩子休眠

    
    
    [!] Suspicious Process: ThreadStackSpoofer.exe (4876). Potentially hooked Sleep / Modifies Kernel32.dll
    
    通过对比KernelTime和UserTime来识别常见Beacon行为
    
    [!] Suspicious Process: ThreadStackSpoofer.exe (4876). Thread 1132 has state DelayExecution and spends 94% of the time in usermode

## 项目地址

 **Hunt-Sleeping-Beacons** ：【[ _GitHub传送门_](https://github.com/thefLink/Hunt-Sleeping-Beacons)】

## 参考资料

> [
> _https://github.com/mgeeky/ThreadStackSpoofer_](https://github.com/mgeeky/ThreadStackSpoofer)
>
> [ _https://github.com/waldo-> irc/YouMayPasser/blob/master/Lockd/Lockd/Sleep.cpp_](https://github.com/waldo-> irc/YouMayPasser/blob/master/Lockd/Lockd/Sleep.cpp)
>
> [ _https://twitter.com/_forrestorr_](https://twitter.com/_forrestorr)
>
> [ _https://twitter.com/waldoirc_](https://twitter.com/waldoirc)
>
> [ _https://www.forrest-orr.net/post/malicious-memory-artifacts-part-i-dll-> hollowing_](https://www.forrest-orr.net/post/malicious-memory-artifacts-> part-i-dll-hollowing)


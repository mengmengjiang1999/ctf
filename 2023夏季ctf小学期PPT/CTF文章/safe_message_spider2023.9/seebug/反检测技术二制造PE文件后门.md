原文：[Art of Anti Detection 2 – PE Backdoor
Manufacturing](https://pentest.blog/art-of-anti-detection-2-pe-backdoor-manufacturing/)  
译者： **MyKings@知道创宇404实验室**  
前文回顾：[反检测技术之反病毒检测](http://paper.seebug.org/222/)

本文主要讲述在网络攻防演练中红队如何在PE(Portable
Executable)文件中放置后门的几种方法。为了让读者能够充分掌握本文的内容，您需要具有中级x86汇编知识，并熟悉调试器与PE文件格式。

## 1\. 背景说明

目前几乎所有的安全研究人员、渗透测试人员和恶意软件分析师每天都在处理后门程序，将后门放置到系统或具体某个应用程序是一种较为常见的攻击方式。

本文的大部分内容是关于将后门植入32位PE文件的方法, 但由于PE文件格式是Unix COFF（Common Object File Format,
通用对象文件格式）的修改版本，所以这些方法也可以用于其他可执行二进制文件类型。

此外，后门的隐蔽性尤为重要，这里也会分析一些反检测技术的方法。在阅读本文之前，您可以先阅读 [Introduction To AV & Detection
Techniques ](https://pentest.blog/art-of-anti-detection-1-introduction-to-av-detection-techniques/)([反检测技术之反病毒检测](http://paper.seebug.org/222/)) ,
这将有助于您了解反病毒产品的内部工作原理和反检测技术的基本思想。

## 2\. 专业术语

**红队(Red Team Pentesting):**

在网络攻防演练中，红队是由一群白帽黑客组成，作为攻击者负责攻击组织(通常为蓝队)的数字基础设施，以测试组织的防御能力（通常称为“渗透测试”）。

其好处体现在先入为主的观念与挑战，发现更多的潜在威胁减少安全问题。其次可更准确地了解敏感信息是如何被泄漏的，以及可利用的模式。目前包括微软在内的一些公司会定期进行红队与蓝队的网络对抗演练。

![](http://ogb2rw42s.bkt.clouddn.com/teams.png) _图片译者添加_

**地址空间布局随机化(ASLR):**

`ASLR` 是一种针对缓冲区溢出的安全保护技术。为了防止攻击者能够直接定位内存中攻击代码位置，`ASLR` 随机排列进程的关键数据区域的内存地址，如:
可执行文件的基址、栈、堆和库的位置。

**代码洞(Code Caves):**

`Code Caves`是由另一个程序写入另一个进程的内存的一段代码。这段代码可以通过在目标进程内创建远程线程来执行。代码的`Code
Caves`通常是对代码的脚本函数的一部分的引用，该脚本函数具有注入自定义指令的能力。例如，如果脚本的内存允许5个字节，并且只使用3个字节，则剩余的2个字节可以用于向脚本添加外部代码,
这就是所谓的代码洞。

**校验和(Checksum):**

`校验和`是来自数字数据块的小尺寸数据，用于检测在其传输或存储期间可能引入的错误。它通常从远端服务器下载到本地接收到之后应用于安装文件。通过自身，校验和通常用于验证数据完整性，但不依赖于验证数据的真实性。

> 译者注: "校验和" 是冗余校验的一种形式。
> 它是通过错误检测方法，对经过空间（如通信）或者时间（如计算机存储）传送的数据的完整性进行检查的一种简单方法。计算机领域常见的校验和的方法有:
> CRC、MD5、SHA家族等。

## 3\. 基本流程

本文中将通过 [putty.exe](http://www.putty.org/)
这个SSH客户端来做示例演示。这里使用`putty`的主要原因有如下几个:

  * `putty` 客户端是一个使用多个库和 Windows API 的本地 C++ 项目;
  * SSH客户端的后门吸引较少关注，因为程序主要就是执行TCP连接，这将更容易避免蓝色团队网络监控。

这个后门代码将使用 [`metasploit`](https://github.com/rapid7/metasploit-framework) 项目中
Stephen Fever’s 开发的TCP反向链接的
[`ShellCode`](https://github.com/rapid7/metasploit-framework/blob/master/external/source/shellcode/windows/x86/src/stager/stager_reverse_tcp_nx.asm)。
主要将 `ShellCode` 注入目标PE文件中，并且不影响程序的正常功能。注入的 `ShellCode`
将在一个新的线程上执行，并不断地尝试连接到控制端。完成以上目标后我们还要做一些免杀, 来减少被检测到的风险。

大致流程主要分以下四个步骤:

  * 完成可用空间的后门代码(添加区段)
  * 劫持执行流程
  * 注入后门代码
  * 恢复执行流程

在每一个步骤中都有一些关键操作, 这些细节保证了后门的隐蔽与降低被检测到的风险。

## 4\. 可用空间问题

第一步我们需要找到可用空间，如何在PE文件中选择合适的空间来插入后门代码非常重要, 这将影响到后门被检测到的风险系数。 有如下两种方法解决空间大小问题:

### 4.1 添加新区段

与其他方法相比，这种方法容易被检测引擎检测到，但另一个好处是附加了一个新的区段，对于将被植入的后门代码没有空间限制。

使用一个汇编程序或PE编辑器(如`LordPE`)，所有的PE文件可以添加一个新的段头，这是 `putty` 可执行文件的节表，借助PE编辑器添加了一个
"`NewSec`" 区段, 大小为 1000 字节，

![](http://ogb2rw42s.bkt.clouddn.com/sectiontable.png)

当创建一个新的区段时，将段标志设置为 “读/写/执行” 对于当PE映像映射到内存时运行后门 `ShellCode` 至关重要。

![](http://ogb2rw42s.bkt.clouddn.com/sectionflags.png)

在添加段头之后，需要调整文件大小，这可以通过在十六进制编辑器中添加空文件和文件末尾的段大小来实现。

![](http://ogb2rw42s.bkt.clouddn.com/hexedit.png)

在这些操作之后，新的空段被成功地添加到PE文件中，运行修改后的 `putty` 文件，如果正常运行, 则新段可以在调试器上被修改。

![](http://ogb2rw42s.bkt.clouddn.com/newsec.png)

为了解决空间问题，我们添加一个新的区段，但是几乎所有的AV产品都能识别不常见的区段，同时给一个不常见的区段所有（读/写/执行）权限肯定是非常可疑的。即使向putty可执行文件添加空的完整权限，也会被某些AV产品标记为恶意。

![](http://ogb2rw42s.bkt.clouddn.com/VirusTotal.png)

### 4.2 代码洞(Code Caves)

解决空间问题的第二种方法是使用目标可执行文件的`Code Caves`。几乎所有编译的二进制文件都有`Code
Caves`，可以在进行后门操作时使用。使用`Code
Caves`而不是新添加的区段的方法将降低被AV产品检测的风险，因为使用已经存在的公共部分。此外，PE文件的总体大小在添加后门结束时不会被改变，但是该方法也具有缺点。

`Code Caves`的数量和大小根据文件的不同而不同，与添加区段比通常没有太多的空间。当使用`Code
Caves`时，后门代码应尽可能短小。另一个缺点是段标志, 由于应用程序的执行将被重定向到 Caves，包含 Caves 的部分应该具有 “execute”
权限，甚至一些shellcode（以自修改的方式编码或混淆）也需要 “write” 权限，以便进行更改里面的区段。

使用多个`Code
Caves`将有助于克服空间限制问题，也将后门代码分割为块同时降低了被AV检测的风险，但不幸的是更改段特权将看起来可疑。有一些高级方法可以修改运行时的内存区域权限，来避免直接更改段权限，但由于这些方法需要定制的
`ShellCode` 编码和IAT解析技术，它将在下一篇文章中来介绍。

借助于一个名为`Cminer`的工具，很容易枚举二进制文件的所有代码洞，`./Cminer putty.exe 300` 命令枚举`Code
Caves`大于300字节。

![](http://ogb2rw42s.bkt.clouddn.com/cminer1.png)

在这种情况下，有5个好的`Code
Caves`可以使用。起始地址给出了`Caves`的虚拟内存地址（VMA）。这是`Caves`的地址，当PE文件加载到内存中时，文件偏移量是以字节为单位的PE文件内的`Caves`地址。

![](http://ogb2rw42s.bkt.clouddn.com/cminer2.png)

看来大部分`Caves`都在数据段内，因为数据段没有执行特权段标志,
这里需要更改。后门代码将在400-500字节左右，所以5个`Caves`应该是足够的。`Caves`的起始地址应该被保存，在将段特权更改为R/W/E后，第一步的后门过程就完成了。

下面开始需要重定向执行的时候了。

## 5\. 劫持执行流程

在此步骤中，我们目的是通过修改目标可执行文件的指令将执行流重定向到后门代码。这里有一个关于选择将被修改的指令重要细节,
所有二进制指令具有字节大小，为了跳转到后门代码地址，将使用5或6字节的长跳跃。
因此，当修补二进制时，将被修补的指令需要与长跳转指令的大小相同，否则上一条或下一条指令将被破坏。

选择适当的空间来重定向执行对于绕过AV产品的动态检测和沙箱分析机制是非常重要的。如果直接发生重定向，则可能在AV的动态扫描分析阶段就被检测到。

**隐藏在用户交互下：**

绕过沙盒与动态分析阶段的第一件事是延迟`ShellCode`的执行或设计沙箱感知和触发机制。
但在添加后门时，大多数时候没有这么多的空间用于在PE文件中添加这些额外的代码。在汇编级语言中设计防检测机制这需要大量的时间和知识。

该方法主要是利用与用户交互来执行操作的功能,
作为一个触发机制，当一个用户操作程序时激活后门代码。如果这个方法可以正确实现，它将有100%的成功率，而且不会增加后门代码的大小。

在`putty`启动后的界面中, 点击 “Open” 按钮会启动一个检查IP地址是否有效的功能。

![](http://ogb2rw42s.bkt.clouddn.com/putty.png)

如果IP地址字段值不为空并且有效，则它启动尝试连接给定IP地址的连接功能。如果客户端成功创建SSH会话，将弹出一个新窗口并请求凭据，

![](http://ogb2rw42s.bkt.clouddn.com/puttyLogin.png)

这将是重定向发生的点，因为AV产品不能够复制这种复杂的环境，植入的后门将不会被自动化沙盒和动态分析机制检测到。

使用基本的逆向方法，搜索下面的字符串和字符串引用，将不难找到连接函数的地址。客户端建立与给定IP的连接后，有一个字符串 “login as:”
打印到出现的窗口。 这个字符串将帮助我们找到连接函数的地址，`IDA Pro`在这方面做得很好。

为了找到 **“login as:”** 字符串, 在`IDA`上依次打开 **Views- >Open Subviews->Strings**

![](http://ogb2rw42s.bkt.clouddn.com/idastring.png)

找到字符串后，双击转到所在位置，在数据节内部`IDA`查找所有对字符串的交叉引用，按 “Ctrl+X”，它显示所有交叉引用，这个引用在打印 “login
as:” 字符串的函数内部。

![](http://ogb2rw42s.bkt.clouddn.com/Screenshot_2.png)
![](http://ogb2rw42s.bkt.clouddn.com/Screenshot_3.png)

这将是要修补的指令，在进行任何更改之前，请注意上下文的指令。 执行后门代码后，将再次使用。

![](http://ogb2rw42s.bkt.clouddn.com/Screenshot_4.png)

通过将`PUSH 467C7C`指令改为`JMP 0x47A478`，完成后门过程的重定向阶段。
重要的是注意下一个指令地址。它将在执行后门代码后用作返回地址。

接下来将是注入后门代码的环节。

## 6\. 注入后门代码

在注入后门代码时，首先需要做的是在执行后门之前保存寄存器中的内容。所有寄存器中的每个值对于程序的执行是非常重要的。通过在代码的OEP(程序入口点)放置`PUSHED`和`PUSHED`指令，所有寄存器内的值和寄存器标志都存储在堆栈中。
这些值将在执行完后门代码之后弹出，以便程序可以继续执行而没有任何问题。

![](http://ogb2rw42s.bkt.clouddn.com/savereg.png)

如前所述，使用的后门代码是来自`metasploit`项目的`meterpreter`反向TCP
`ShellCode`。但是在`ShellCode`中需要做少量修改。 通常，反向TCP
`ShellCode`会有尝试连接到处理程序的次数或时间限定，如果连接失败，则通过调用`ExitProcess API`调用关闭进程。

![](http://ogb2rw42s.bkt.clouddn.com/dmet.png)

这是问题的所在，如果连接到处理程序失败，`putty`客户端的执行将停止。改变几行`ShellCode`使其每次连接失败时`ShellCode`将重试连接到处理器，这样也会相应的减少`ShellCode`的体积。

![](http://ogb2rw42s.bkt.clouddn.com/nmet.png)

在汇编代码中进行更改后，使用`nasm -f bin stager_reverse_tcp_nx.asm`命令进行编译。现在反向的TCP
`ShellCode`已经可以使用了，但是它不会被直接放置, 我们的目标是在新线程上执行`ShellCode`。
为了创建一个新的线程实例，需要另一个`ShellCode`，使`CreateThread`API调用指向反向TCP
`ShellCode`。这里使用`Metasploit`项目中创建线程的[`ShellCode`](https://github.com/rapid7/metasploit-framework/blob/master/external/source/shellcode/windows/x86/src/single/createthread.asm)。

![](http://ogb2rw42s.bkt.clouddn.com/CreateThread.png)

如上, 将 [createthread.asm](https://github.com/rapid7/metasploit-framework/blob/master/external/source/shellcode/windows/x86/src/single/createthread.asm)
文件中的代码转换为十六进制格式的`ShellCode`，使用`nasm -f bin
createthread.asm`命令进行编译。在这里，`ShellCode`准备插入到`Caves`中，但在插入`ShellCode`之前，它应该被编码以便绕过AV产品的静态/特征分析机制。因为`Metasploit`项目中的所有编码器被大多数AV产品所知，所以强烈建议使用自定义编码器。
本文不会覆盖这种自定义`ShellCode`编码器的制作，它将在下一篇文章中介绍到，这里还可以使用多个`Metasploit`编码器来工作。在每个编码过程完成之后，将编码的`ShellCode`上传到线上的病毒检测站点，根据检测分数。
尝试每个组合，直到它不被检测到或等待下一篇文章。

在正确编码`ShellCode`之后，就可以把它插入`Code Caves`。选择在`PUSHFD`下的指令，然后在免调试器上按下 “Ctrl +
E”，`ShellCode`将以十六进制格式粘贴。

![](http://ogb2rw42s.bkt.clouddn.com/Insert.png)

使用`xxd -ps
createthread`命令，以十六进制格式打印编码创建线程的`ShellCode`或使用十六进制编辑器打开`ShellCode`并复制十六进制值。当将十六进制值粘贴到调试器时，请注意字节限制，这些修补操作是用免试器进行的，免调试器在粘贴到编辑代码窗口时有一个字节限制。
它不会粘贴所有`ShellCode`，记住粘贴的`ShellCode`的最后2个字节在编辑代码窗口内，按下OK按钮后继续粘贴字节，当所有`ShellCode`粘贴到`Code
Cave`时后门代码就插入完了。

## 7\. 恢复执行流程

在创建后门代码线程之后，程序需要恢复到其正常执行流程，这意味着EIP应该跳回到将执行重定向到`Cave`的函数。但是在跳回到该函数之前，应该检索所有保存的寄存器。

![](http://ogb2rw42s.bkt.clouddn.com/pop.png)

通过在`ShellCode`的末尾放置`POPFD`和`POPAD`指令，所有保存的寄存器都以相同的顺序从堆栈中弹出。在检索寄存器后，还有一件事要做，执行被劫持的指令。为了将程序的执行重定向到`Code
Cave`, 我们将`PUSH 467C7C`指令替换为了`JMP 0x47A478`。 现在把`PUSH
467C7C`指令放在最后，被劫持的指令也被检索。现在是返回到通过插入`JMP
0x41CB73`指令将执行重定向到`Cave`的函数的时候了，结果代码应该如下图所示。

![](http://ogb2rw42s.bkt.clouddn.com/end.png)

最后选择所有修补和插入的指令，按右键单击并复制到可执行文件。此操作应对已修改的每个指令执行。当所有指令被复制并保存到文件时，关闭调试器并测试可执行文件，如果可执行文件运行顺畅，则后门可以使用。

最后，建议固定最终文件校验和，以保持文件的真实性，而不是看起来可疑，这也可能对降低检测分数有影响。

![](http://ogb2rw42s.bkt.clouddn.com/Screenshot_6.png)

## 8\. 总结与预防措施

最后，当所有操作都正常完成后，产生的后门是完全不会被检测到的。针对以上的两种代码注入方式，下面给出这些相应技术的对策，这些策略可以帮助系统管理员、恶意软件记录器、反病毒与反恶意软件产品的开发人员。

### 8.1 区段特权控制

当谈论后门文件时，区段的特权对于检测异常是非常重要的，编译器永远不会设置对区段的完全权限，除非开发人员强制添加。特别是像`.data`或`.rdata`这样的数据段不应该有执行权限，类似`.text`的代码段不应该有写权限，这些异常应该被认为是可疑的行为。

### 8.2 不常见区段识别

如果开发人员不进行任何配置,
编译器通常创建5-6个通用类型的区段，所有安全产品应该具有识别不常见和可疑段的机制，这种机制可以寻找段内的熵和数据对齐，如果一个段包含高熵和异常排序的数据，它应该被认为是可疑的。

### 8.3 签名检查

这种对策非常经典，也是最有效的，当下载一个新的程序或任何一块可执行文件，检查sha1签名来验证程序是否被修改。

### 8.4 检查文件校验和

当内部镜像和文件的实际校验和的值之间存在差异时，这表明该文件已被修改过，安全产品和系统管理员应计算实际校验和并与镜像头比较，来检查文件的真实性。

![](http://ogb2rw42s.bkt.clouddn.com/Scan.png)

## 9\. 原文链接

  * http://NoDistribute.com/result/image/Ye0pnGHXiWvSVErkLfTblmAUQ.png
  * https://github.com/secretsquirrel/the-backdoor-factory
  * https://www.shellterproject.com/
  * https://en.wikipedia.org/wiki/Red_team
  * https://en.wikipedia.org/wiki/Address_space_layout_randomization
  * https://en.wikipedia.org/wiki/Code_cave
  * https://en.wikipedia.org/wiki/Checksum

## 10\. 译者参考

  * https://ccdcoe.org/publications/LockedShields13_AAR.pdf

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/264/>


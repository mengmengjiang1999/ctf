**作者：启明星辰ADLab  
原文链接：<https://mp.weixin.qq.com/s/93HyZBf803WucqEUG0uI7g>**

### 一、漏洞背景

近日，国外安全研究人员披露一个Linux eBPF
verifier组件错误验证漏洞，此漏洞源于bpf验证系统在Linux内核中没有正确计算某些操作的寄存器边界跟踪，导致本地攻击者可以利用此缺陷进行内核信息泄露或特权提升，该漏洞编号为CVE-2020-27194。

### 二、影响范围与防护措施

**影响范围**

  * Linux-5.7 ~ Linux-5.8.14
  * Ubuntu 20.10

**防护措施**

  * 及时更新升级内核
  * 将kernel.unprivileged_bpf_disabled.sysctl设置为1，临时限制普通用户权限

### 三、漏洞原理与调试分析

**漏洞原理**

该漏洞和Pwn2own2020比赛中使用的CVE-2020-8835漏洞原理一致，均是错误计算了寄存器边界跟踪，导致可以绕过验证器检查达到越界读写。缺陷代码出现在kernel/bpf/verifier.c的scalar32_min_max_or()函数中，该函数是在commit_id：3f50f132d840中引入的，该功能实现了显式的ALU32(32位计算类操作)寄存器边界跟踪，处理OR运算时，调用scalar32_min_max_or()函数进行32位寄存器边界跟踪，该函数实现如下：

![](https://images.seebug.org/content/images/2020/11/61a7f83b-5445-4973-ae03-aaba434c2938.png-w331s)

行5365和行5366，直接将dst_reg寄存器中的64位无符号值赋值给32位有符号值，这明显是错误的。例如设置dst_reg->umin_value=1，dst_reg->umax_value=0x600000001，当进行如上操作后，dst_reg->s32_min_value为1，但是dst_reg->s32_max_value也将是1，因为0x600000001的高位将被截断，这时dst_reg寄存器的范围从[1,0x600000001]变成了[1,1]，这会被验证器识别为常数1，进而绕过验证器检查。漏洞补丁中，进行了正确的32位有符号值赋值操作，如下所示：

![](https://images.seebug.org/content/images/2020/11/909d6927-1300-4a28-a05c-1d852db639e3.png-w331s)

**调试分析**

首先将寄存器的umin_value设置为0x1，可以通过如下BPF指令实现：

![](https://images.seebug.org/content/images/2020/11/0e71963f-2a26-45de-b612-e10ab9ff5b88.png-w331s)

此时寄存器的状态如下所示：

![](https://images.seebug.org/content/images/2020/11/93b1c5d2-7b09-4f0b-9380-6880cdcb14b5.png-w331s)

设置完umin_value后，设置umax_value为0x600000001，可以通过如下BPF指令实现：

![](https://images.seebug.org/content/images/2020/11/d8cce5b9-d455-470d-a152-7bd6a7cdc9d3.png-w331s)

断点命中后，调用栈如下所示：

![](https://images.seebug.org/content/images/2020/11/e629ce7c-badf-4e99-b68b-9461cde472d1.png-w331s)

执行完BPF_JMP_REG(BPF_JLT,BPF_REG_6,BPF_REG_5,1)指令后，将R6寄存器范围设置为0x1到0x600000001之间。R6寄存器状态如下所示：

![](https://images.seebug.org/content/images/2020/11/d2e96d07-d75c-4a05-9485-4e7b17573b04.png-w331s)

接着设置R6寄存器中32位的无符号最小值和最大值，

![](https://images.seebug.org/content/images/2020/11/a20e4d71-e77c-469a-b825-8014b6df76e0.png-w331s)

设置完之后，R6寄存器状态如下所示：

![](https://images.seebug.org/content/images/2020/11/235f7c73-542d-4539-8055-058a3f4d157f.png-w331s)

红框中设置的值是必须要保证的，需要提前进行设置，方便后面绕过if判断进入缺陷代码块中。接着设置R6寄存器32位有符号最小值和最大值，代码如下所示：

![](https://images.seebug.org/content/images/2020/11/5592fc02-8dfd-45e0-af13-8e8dfdda9bc3.png-w331s)

行5355，if语句判断不成立，会走到行5362分支中，调试情况如下所示：

![](https://images.seebug.org/content/images/2020/11/020eaa5e-d34a-4048-830d-ffbc8b625141.png-w331s)

触发漏洞后，R6寄存器状态如下：

![](https://images.seebug.org/content/images/2020/11/64c366ff-1364-4081-8b18-db61dc8045d9.png-w331s)

此时s32_min_value和s32_max_value都为0x1，在验证器中，R6寄存器的32位有符号取值为常数1。但R6寄存器的取值实际是有范围的。接着将R6寄存器进行32位MOV到R7寄存器中，执行到如下代码所示：

![](https://images.seebug.org/content/images/2020/11/03aa67d2-d90c-40b5-9ae8-b38069d5b5be.png-w331s)

此时，src_reg寄存器如下所示：

![](https://images.seebug.org/content/images/2020/11/e958cf03-ad65-40ff-a78a-9a47a95bc2e4.png-w331s)

执行MOV操作之前，R7寄存器状态如下所示：

![](https://images.seebug.org/content/images/2020/11/0c36541f-2b6e-4a25-acf1-d94a5cfd8bbc.png-w331s)

执行MOV操作后，R7寄存器状态如下所示：

![](https://images.seebug.org/content/images/2020/11/c50de35c-3ee8-4f89-b200-1e87f340c39d.png-w331s)

R7寄存器为常量1，实际运行情况下是有范围的，可以设置为2。 执行BPF_ALU64_IMM(BPF_RSH,BPF_REG_7,1)后，即R7 >>=
1，R7寄存器如下所示：

![](https://images.seebug.org/content/images/2020/11/665063c0-7e84-45b3-b113-45666778bd8e.png-w331s)

此时umin_value和umax_value为0，即为R7寄存器进行右移操作后，在验证器中被识别为常数0，此时R7寄存器进行加减运算都不会发生越界，绕过了验证器的边界检查。但是如果R7寄存器实际设置为2，2>>1为1，R7寄存器为1，此时和R7寄存器进行加减运算，达到越界读写。

### 四、漏洞复现

在Linux-5.7.7版本中进行漏洞利用，成功提权。

![](https://images.seebug.org/content/images/2020/11/34cdeaac-c69c-4d4b-93ed-ff8c1f67920d.png-w331s)

### 五、参考链接

<https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-27194>  
<https://github.com/torvalds/linux/commit/5b9fbeb75b6a98955f628e205ac26689bcb1383e>  
<https://github.com/torvalds/linux/commit/3f50f132d8400e129fc9eb68b5020167ef80a244>  
<https://scannell.me/fuzzing-for-ebpf-jit-bugs-in-the-linux-kernel/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1391/>


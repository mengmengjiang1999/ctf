在 2021 年年末与 2022 年，Proofpoint 的研究人员发现 TA453 与 Charming Kitten、PHOSPHORUS 和
APT42 的攻击活动存在重叠，并且不断创新攻击方法实现攻击目标。在 2022 年 6 月，攻击者开始使用被 Proofpoint
称为多人模拟（MPI）的技术。通过该技术，TA453
将社会工程学提升到一个新的水平，攻击者构建并控制了多个角色，来提高鱼叉邮件的真实性。Proofpoint 此前曾在 TA2520
组织发起的攻击行动中就发现过使用这种技术。

## 典型的 TA453 攻击

Proofpoint 的研究人员发现 TA453 会伪装成个人，例如记者、政策相关人员等。从历史上来看，TA453
的攻击目标通常是学者、政策制定者、外交官、记者和人权工作者。

几乎所有的攻击行动中，TA453 都会与攻击目标进行一对一的对话，但这种情况在 2022 年年中发生了变化。

## 多重人格的 TA453

TA453 的攻击方式从 2022 年 6 月开始发生转变。其中一次攻击中，TA453 伪装成 FRPI 研究总监 Aaron Stein
的身份与攻击目标进行对话。对话的内容涉及以色列、海湾国家和亚伯拉罕协议等，为后续发送恶意链接或者恶意文件提供故事背景。

![image.png-183.8kB](https://image.3001.net/images/20220921/1663728308_632a7ab44a22a67919dbe.png!small)假冒
Aaron Stein 的电子邮件

在电子邮件中，TA453 伪装成的 Aaron Stein 在线上提到 PEW 研究中心全球态度研究主任 Richard
Wike，这就是攻击者对多重角色模拟（MPI）的应用。

电子邮件发送一天后，Richard Wike
就回复了该电子邮件。攻击者通过这种方法来提高真实性背书并且提高攻击目标回复概率，但此时未发现恶意文件或者恶意链接。

![image.png-66.8kB](https://image.3001.net/images/20220921/1663728309_632a7ab51efe32dfa83cd.png!small)假冒
Richard Wike 的回复

2022 年 6 月下旬，TA453 以 Harald Ott
的身份联系了一个专门从事基因组研究的攻击目标，并且抄送了另外两个攻击者控制的账户：Centre for Universal Health in
Chatham House's Global Health Programme 的助理主任 Claire Parry、Nature
Biotechnology 的主编 Andrew Marshall，形成三个骗子对一个攻击目标进行诱骗的局面。

![image.png-138.5kB](https://image.3001.net/images/20220921/1663728310_632a7ab6194e0c4f7b4ff.png!small)TA453
的针对医学研究人员的攻击

当攻击目标回复最初的电子邮件时，Harald 提供了一个 OneDrive 链接，通过该链接可以下载一个名为 Ott-Lab 371.docx 的恶意
Word 文档文件。该文件的 SHA256 为
f6456454be8cb77858d24147b1529890cd06d314aed70c07fc0b5725ac84542b。

针对医疗领域与基因组研究相关人员发起攻击，并不是 TA453 的常态，但这也不是该攻击者第一次表现出对医疗领域的关注。早在 2020 年 12 月，就发现过
TA453 开展了针对医学研究人员的网络钓鱼活动。

2022 年 6 月，TA453 的 Carroll Doherty
联系了一位参与核军备控制的著名学者，讨论可能存在的美俄冲突。攻击者并不局限于只针对一个攻击目标，而是同时针对同一所大学的两个攻击目标发起攻击。在这一邮件中，Carroll
Doherty 还抄送了另外三个 TA453 控制的角色：Daniel Krcmaric、Aaron Stein 与 Sharan Grewal。

![image.png-92.5kB](https://image.3001.net/images/20220921/1663728310_632a7ab6bbd7784f8bf6f.png!small)攻击时间线

其中一个攻击目标回复了电子邮件，随后 Carroll Doherty 好心地提供了原始电子邮件中引用的文章的 OneDrive
链接，点击该链接会下载一份名为 `The possible US-Russia clash.docx`的文件。

![image.png-72.5kB](https://image.3001.net/images/20220921/1663728311_632a7ab75b414e382478a.png!small)Carroll
Doherty 发送电子邮件

![image.png-62.2kB](https://image.3001.net/images/20220921/1663728312_632a7ab80a82fc1e5ff2c.png!small)Carroll
Doherty 发送电子邮件

Carroll Doherty 单独发送了密码，并表示文件是安全的。四天后，抄送的 TA453 角色之一 Aaron Stein 回复了 Carroll
Doherty，在邮件中向攻击目标表示歉意并重新发送了相同的 OneDrive 链接与密码。

![image.png-46.5kB](https://image.3001.net/images/20220921/1663728312_632a7ab89957256e00376.png!small)抄送角色的助攻

恶意文档是类似的，都使用了远程模板注入下载 Korg。

## Korg - 远程模板注入

部署的恶意文档也是普华永道于 2022 年 7 月披露的 TA453 远程模板注入文档的最新版本。这些受密码保护的文档从
`354pstw4a5f8.filecloudonline.com`下载了启用宏的模板文档，在多个攻击活动中重复使用特定的
`filecloudonline.com`主机。

下载的模板被 Proofpoint 称为 Korg ，其中具有三个宏：Module1.bas、Module2.bas 与
ThisDocument.cls。宏代码会收集用户名、正在运行的进程列表以及用户的公共 IP 等信息，然后使用 Telegram API 回传这些信息。

Proofpoint 只发现了信标，并没有观察到任何后续的利用行为。TA453 的宏代码中缺少代码执行或命令和控制能力，这是不正常的。Proofpoint
推测，攻击者可能是根据失陷主机的具体情况部署后续的攻击利用。

## 归因

Proofpoint 仍然将 TA453 归因为伊朗的革命卫队。业界披露的多份内容也都指向该结论，例如普华永道对 Charming Kitten
的分析、美国司法部对 Monica Witt 与 IRGC 附属攻击者的起诉以及其他相关分析报告。

Proofpoint 通过受害者、攻击技术和基础设施对 TA453
的多个小组进行区分。在他们的典型攻击活动中，一些小组会在传递恶意链接之前与目标进行数周的良性对话。也有某些子组倾向于立即在电子邮件中就发送恶意链接。

可能与 TA453 相关的指标包括：

> 使用 Gmail、Outlook、Hotmail 或 AOL
>
> 使用的电子邮件地址不是机构的电子邮件
>
> 会话中包括其他人
>
> 会回复空白电子邮件
>
> 内容与中东问题有关
>
> 提供 Zoom 会话

## 结论

所有的攻击者都会不断迭代攻击的技战术。TA453 对多人模拟（MPI）技术的使用，表示他们也在不断进步。最新的攻击行动中，TA453
试图发送一封空白电子邮件，然后在回复空白电子邮件的同时将所有伪装身份都抄送上，这应该是在尝试绕过安全检测。

提醒从事国际安全领域的研究人员，特别是那些专门从事中东研究或核安全的研究人员，在收到不请自来的电子邮件时应保持高度的警惕。

## 参考来源

> [Proofpoint](https://www.proofpoint.com/us/blog/threat-insight/ta453-uses-> multi-persona-impersonation-capitalize-fomo)


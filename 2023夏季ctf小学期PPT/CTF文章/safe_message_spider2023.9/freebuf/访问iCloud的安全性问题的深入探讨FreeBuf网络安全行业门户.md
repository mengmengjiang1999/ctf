**在iOS取证中，当无法进行物理采集时，云提取将会是一种可行的替代方案。在即将发布的iOS
13版中增添了额外的安全措施，这无疑将使物理访问变得更加困难。虽然我们可以下载iCloud备份，但需要提供用户登录名和密码以及双因素身份验证这对我们来说始终是一个障碍。**

**![apple_icloud_storage_cost_3x2_apple_logo_cloud_computing_illustration_thinkstock-100748384-large.jpg](https://image.3001.net/images/20190806/15650859664378.jpg!small)**

大约五年前，我们学习了如何使用身份验证令牌来访问无需密码的iCloud备份。并在”[进入iCloud：无需密码](https://blog.elcomsoft.com/2014/06/breaking-into-icloud-no-password-required/)“一文中，我们讨论了这种方法的好处。在接下来的几年当中，我们学习了如何使用身份验证令牌访问存储在iCloud中的其他类型的数据，包括用户的照片库，浏览历史记录，联系人，日历以及Apple在登录到同一账户的所有用户设备上同步的其他信息。

也是从那时起，情况开始发生了变化。令牌不能再用于访问iCloud备份。令牌不能用于访问密码（icloud
keychain）、屏幕时间、运行状况和消息。在去年的某个时候，苹果将认证令牌固定到了一台特定的计算机上，使得它们仅能从创建它们的PC或Mac上使用。为此，我们花了一年多的时间才找到解决方案，以允许从用户的计算机上传输身份验证令牌。
时至今日，这种方法也仅在用户拥有macOS计算机时才有效。有了这些限制，身份验证令牌是否仍然可用？使用身份验证令牌，你可以从用户的iCloud帐户获得什么？使用登录名和密码可以访问到什么？双因素身份验证对iCloud帐户的影响，以及为什么知道锁屏密码（或Mac系统密码）会有所帮助？这些问题你将在下面找到答案。

## iCloud 安全

苹果没有存储其用户数据的服务器（或更确切地说是服务）。iCloud备份，照片，消息甚至密码都被保存在了亚马逊，微软，谷歌，AT&T等第三方服务器上。但是，这并不意味着亚马逊，谷歌等可以随时访问任何这些数据。让我们来看看苹果是如何保护iCloud数据免受物理威胁的，我们以iCloud备份为例。

用户的iCloud备份被分成多个块，每个单独的块被上传到（以看似随机的顺序）一个或多个服务器。每个块都使用唯一单独加密密钥进行加密。没有这些密钥，即使以正确的顺序组装拼凑，块仍将是加密二进制数据块。

而密钥则始终被存储在Cupertino数据中心的苹果自己的服务器上。它们永远不会被传递给苹果的合作伙伴，承包商或中国政府（除非提出法律需求）。

从这种[保护方案](https://support.apple.com/en-us/HT202303)来看，我们可以得知：

> 1.苹果拥有对加密信息的完全访问权，因为其同时拥有数据和加密密钥。
>
> 2.苹果可以解密数据并将其传送给执法部门。
>
> 3.具有适当身份验证凭据的人可以访问数据和加密密钥，从而检索和解密备份。

## iCloud 备份安全

说到iCloud备份，重要的是要了解虽然备份的大部分都可以使用凭据进行解密，但iCloud备份的某些内容将使用高度安全的基于硬件的加密密钥进行额外的加密。加密发生在iOS设备内部（在iPhone或iPad本身）;
所有这些数据都没有脱离设备，或者已任何未加密的形式保存。因此，只能将此类内容还原到备份该内容的同一硬件设备上。在iOS 12和iOS
13（测试版）中，此内容包括：

>  **keychain**
> 。用户的Safari和第三方应用密码在iCloud备份中仍然受到安全保护（请记住，我们只讨论iCloud备份中的keychain存储；更多的是关于cloud
> keychain保护和后续提取）。keychain只能在生成备份的设备上解密。如果没有原始设备，苹果和执法部门都无法访问这部分iCloud备份。

以下数据永远不会被包含在iCloud备份中：

> Health data
>
> Home data

此外，如果用户为该数据类别启用iCloud同步，则会从iCloud备份中明确排除某些项目。这些项目包括：

> iCloud Photos
>
> Messages (SMS 和 iMessages)

iOS 13还排除了以下两个数据类别（最新）：

> Call logs
>
> Safari history

## iCloud 备份和令牌

在我们2014年发表的那篇“[进入Cloud：无需密码](https://blog.elcomsoft.com/2014/06/breaking-into-icloud-no-password-required/)”一文中，我们讨论了使用身份验证令牌来访问iCloud备份。现在，这已经不可能了。

iCloud身份验证令牌不能用于访问iCloud备份。

## 同步数据

自2011年iCloud备份出现以来，苹果公司正逐渐将一些数据内容从备份中转移出去。iCloud Photo
Library的推出使照片通过iCloud中的专用服务在设备间同步。一旦用户启用了他们的iCloud Photo
Library，图片将不再被保存到iCloud备份中。同样，一旦用户启用了iCloud Messages（需要iOS
11.4及更高版本），消息也将不再被保存在iCloud备份中，而是通过用户的iCloud帐户进行同步。iOS 13将停止在iCloud备份中包含Call
Logs和Safari历史记录；这两个类别将仅作为同步数据提供。

身份验证令牌适用于提取同步数据（受保护类别除外）。以下总结了iCloud中同步信息的保护：

> 要访问同步的iCloud数据，只需要用户的Apple ID，密码和2FA码。
>
> 你还可以使用身份验证令牌来访问已同步的数据。
>
> Apple具有访问iCloud中同步数据的技术能力。
>
> 在政府请求时同步数据将被提供。
>
> 在GDPR请求时同步数据将被提供。
>
> 最后，第三方应用程序（如[ElcomSoft Phone
> Breaker](https://www.elcomsoft.com/eppb.html)）可以提取同步的iCloud数据。

## 一些 iCloud 数据使用密码加密

某些数据类别会受到不同的处理。

如果你知道使用相同Apple ID注册的设备的锁屏密码（或Mac系统密码），则只能解密以下数据类型：

>  **iCloud Keychain**
> 。keychain包含包含来自Safari浏览器和第三方应用程序的用户同步登录名和密码以及一些身份验证令牌。最重要的是，iCloud
> Keychain还存储保护其他加密数据类型的加密密钥（例如，如果不首先解密icloud keychain，则无法解密消息）。
>
>  **iCloud中的消息** 。包括SMS和iMessages。
>
> 自iOS 12起， **Health数据** 。与iOS 11相比，iOS 12中同步健康数据的保护有所改变。

要访问这些受保护的数据类别，你将需要满足以下条件：

> 用户的Apple ID和密码
>
> 一次性2FA码（没有2FA的任何类别都不会有iCloud同步）
>
> 已在iCloud Keychain中注册设备的密码或系统密码

访问限制如下：

> 身份验证令牌不能用于访问任何这些类型的数据。
>
>
> 普通用户在使用iCloud同步Keychain，Health或Messages时不会遇到任何问题。在初始化新iPhone以接收同步数据时，他们只需要向他们的旧iPhone（或任何启用了iCloud
> Keychain的设备，包括Mac计算机）提供他们的锁屏密码即可。
>
> Apple无权访问已同步的密码，消息或健康数据。即使数据存储在Apple服务器上，Apple也无法对其进行解密。
>
> 在政府或GDPR提出请求时，Apple不会提供属于受保护类别的任何数据（有一个例外）。
>
> 如果知道设备密码/系统密码（[Elcomsoft Phone
> Breaker](https://www.elcomsoft.com/eppb.html)），使用第三方应用程序提取仍然受限。

## 例外：在 iOS 11 和 iOS 12 中保护和提取健康数据

从iOS 11开始，Apple实现了与iCloud的健康数据同步。在iOS
11中，除CDA记录之外的所有类型的数据，都将以与其他类型的同步数据（如图片或联系人）完全相同的方式与iCloud同步。对活动，睡眠，营养，mindfulness（正念）和类似类型的数据没有额外的保护。

 **在 iCloud 中保护健康数据：iOS 1**

要访问同步的健康数据，只需要用户的Apple ID，密码和2FA码。

> Apple具有访问iCloud中的健康数据的技术能力。
>
> 在政府请求时提供健康数据。
>
> 在GDPR请求时提供健康数据。
>
> 最后，第三方应用程序，如[Elcomsoft Phone
> Breaker](https://www.elcomsoft.com/eppb.html)可以提取健康数据。

 **在 iCloud 中保护健康数据：iOS 12 和 13**

iOS 12实现了另一种保护iCloud中健康数据的方法，即采用存储在iCloud Keychain中的密钥进行安全加密。与iOS
11相比，实际数据现在存储在不同的（加密）容器中。有趣的是，在用户将最后一个设备更新到iOS 12之后，旧的（未加密的）容器可以保持一段时间可用。

加密密钥使用已参与运行状况同步的设备的用户密码（锁屏密码或系统密码）进行保护。这确保了苹果无法访问存储在云中的健康数据（或者iCloud
Keychain，如果这很重要的话）。我们认为这种保护机制可以提供足够的安全性。

要通过运行iOS 12及更高版本的设备访问与iCloud同步的健康数据，需要满足以下条件：

> 用户的Apple ID和密码
>
> 一次性2FA码（没有2FA的任何类别都不会有iCloud同步）
>
> 已在Health iCloud同步中注册设备的密码或系统密码

访问限制如下：

> 初始化新iPhone时，用户需要提供旧iPhone（或任何启用了iCloud
> Keychain的设备，包括Mac计算机）的锁屏密码，以接收同步的健康数据。
>
> Apple无权访问同步的健康数据。即使数据存储在Apple服务器上，Apple也无法对其进行解密。
>
> Apple在政府或GDPR提出请求时也不会提供健康数据。
>
> 使用第三方应用程序进行提取仍受限制（[Elcomsoft Phone
> Breaker](https://www.elcomsoft.com/eppb.html)）。

## 双因素身份验证：优势

如果用户在其帐户上启用了双因素身份验证，则会获得一系列无法在没有2FA的帐户中使用的功能。他们只需使用密码就可以[立即从iPhone上重置他们的Apple
ID密码](https://blog.elcomsoft.com/2017/11/breaking-apple-icloud-reset-password-and-bypass-two-factor-authentication/)。他们可以在不知道iCloud密码的情况下[禁用“查找我的iPhone”功能](https://blog.elcomsoft.com/2017/11/breaking-apple-icloud-reset-password-and-bypass-two-factor-authentication/)。此外，取证专家还发现了一些其他非常有用的功能。只有具有双因素身份验证的帐户才能执行以下操作：

> 通过iCloud同步密码（iCloud Keychain）
>
> 同步消息（SMS和iMessages）
>
> 同步健康数据
>
> 同步屏幕时间数据（包括从属帐户的屏幕时间数据）

在某种程度上，双因素身份验证对于执法来说是一种福气，因为与未受保护的帐户相比，具有2FA的帐户通过iCloud同步更多信息。

你可以使用身份验证令牌完全跳过2FA提示。这就是我们受到限制的地方。

## 令牌和双因素身份验证：限制

当我们最初研究iCloud身份验证令牌时，我们可以使用它们从云端获取几乎所有内容，包括备份。而如今，Apple限制了使用身份验证令牌。你无法再使用身份验证令牌来访问使用双因素身份验证帐户的iCloud备份。虽然你仍然可以使用令牌从非2FA帐户下载iCloud备份，但这些令牌的生命周期仅限于创建令牌后的一小时内。

无论双因素身份验证状态如何，你仍然可以使用身份验证令牌（没有明显的时间限制）来访问以下类别的同步数据：

> 多个类别的同步数据，包括联系人、日历和备忘录
>
> Safari浏览历史记录和打开的选项卡
>
> 钱包
>
> 通讯记录
>
> iCloud照片
>
> 来自iCloud Drive的文件，包括许多第三方应用程序容器（1Password、WhatsApp、Viber等）
>
> FileVailt2加密驱动的恢复令牌
>
> 云邮件

启用双因素身份验证：

> 无法使用令牌访问iCloud备份

未启用双因素身份验证：

> 可以使用令牌访问iCloud备份，但仅在创建令牌后的1小时内

以下类别对身份验证令牌是不可访问的：

> 密码（iCloud Keychain）
>
> 健康
>
> 屏幕时间
>
> 消息（SMS和iMessage），如果启用了iCloud中的消息*

*如果未启用iCloud中的消息，则消息将被存储在iCloud备份中。

 **Windows vs. macOS**

虽然Apple为Windows和Mac用户提供相应版本的iCloud软件，但在这些平台上创建的身份验证令牌却不同。

在Windows计算机上，令牌被深埋在文件系统中。它还使用用户凭据加密，因此你必须能够登录到用户的帐户（或至少知道他们的登录名和密码）才能解密令牌。ElcomSoft
Phone Breaker可以自动完成这一过程；只需启动该工具，摁几个按钮，令牌就会被保存到一个文本（XML）文件中，并随时可与EPB一起使用。

就这么简单吗？虽然你可以从Windows计算机中提取令牌并将其解密与EPB一起使用，以访问iCloud中的选定数据类别（有关详细信息，请参阅“限制”部分），但你只能在创建令牌的同一台计算机上执行所有这些操作。你甚至无法从用户磁盘映像创建的虚拟机中使用它；它必须是创建令牌的物理计算机才行。

如果用户拥有Mac，除了受限的令牌外，你还可以提取一个完整的，不受限制的令牌。在其受控的生态系统中，Apple能够实施更强大的保护（为2FA帐户使用令牌固定）。我们能够在Elcomsoft
Phone
Breaker中绕过这种保护，允许您提取，传输和使用这些完整的身份验证令牌。完整令牌可以在任何计算机，Windows或Mac上使用；你只需安装了最新版本的Elcomsoft
Phone Breaker即可。

## 提取和使用身份验证令牌

提取身份验证令牌有以下几种支持的方案。

> Windows计算机，从当前登录的帐户中提取受限令牌；
>
> Windows计算机，从其他帐户中提取受限令牌；
>
> macOS计算机，从当前用户中提取受限和不受限令牌（需要keychain password）；
>
> macOS计算机，从keychain数据库中提取受限和不受限令牌（需要keychain password）；
>
> iOS设备，从密码保护备份或物理获取keychain。

 **Windows，当前用户**

你需要：Elcomsoft Phone Breaker（Forensic Edition）。必须以你要提取其令牌的用户身份登录。

从命令行启动atex.exe。该工具将自动提取身份验证令牌。你刚刚已提取了固定在当前计算机的受限令牌（保存到文本文件中）。请注意，你只能在从中提取令牌的计算机上使用提取的令牌。

![1.png](https://image.3001.net/images/20190806/1565058719_5d48e69f4c8bd.png!small)![2.png](https://image.3001.net/images/20190806/1565058719_5d48e69f51551.png!small)

 **Windows，其他用户**

你需要：Elcomsoft Phone Breaker（Forensic Edition）。必须以你要提取其令牌的用户身份登录。

您将使用主GUI从其他用户的帐户中提取令牌。有关详细信息，[请参阅用户手册](https://www.elcomsoft.com/help/en/eppb/index.html)

 **macOS，当前用户**

你需要：Elcomsoft Phone Breaker（Forensic Edition）。必须以你要提取其令牌的用户身份登录。必须要知道keychain
password（通常但不总是与帐户密码相同）。注意：同时提取完整和受限令牌。

![3.png](https://image.3001.net/images/20190806/1565058742_5d48e6b667477.png!small)

或者，使用macOS Keychain实用程序来提取令牌。

![4.png](https://image.3001.net/images/20190806/1565058755_5d48e6c3d5381.png!small)

 **macOS，其他用户**

你需要：Elcomsoft Phone Breaker（Forensic
Edition）。从你将要获取令牌的用户提取keychain数据库。必须要知道keychain password。

![5.png](https://image.3001.net/images/20190806/1565058773_5d48e6d51d3b7.png!small)![6.png](https://image.3001.net/images/20190806/1565058773_5d48e6d54e650.png!small)

 **iOS 设备**

你需要：Elcomsoft Phone Breaker（Forensic
Edition）。解密的keychain数据库（物理采集）或受密码保护的备份（必须要知道密码）。

使用Elcomsoft Phone Breaker手动检查keychain。

![7.png](https://image.3001.net/images/20190806/1565058788_5d48e6e4c1ed0.png!small)

##  **使用身份验证令牌**

你需要：Elcomsoft Phone Breaker（Forensic Edition）。

macOS：如果从macOS中提取完整（不受限的）令牌，则可以复制该文件并在任何计算机，Windows或Mac上使用它。

![8.png](https://image.3001.net/images/20190806/1565058808_5d48e6f8d2e70.png!small)![9.png](https://image.3001.net/images/20190806/1565058808_5d48e6f8d3ee6.png!small)

Windows：受限令牌只能用于从提取它们的同一台计算机进行身份验证。

受限令牌：

![10.png](https://image.3001.net/images/20190806/1565058825_5d48e709af107.png!small)

![11.png](https://image.3001.net/images/20190806/1565058837_5d48e715d54a9.png!small)

## 发现身份验证凭据

由于身份验证令牌具有限制性，因此在使用登录名和密码（以及对具有2FA的帐户进行辅助身份验证）时，从iCloud提取数据成功的可能性更大。可以尝试以下方法获取用户的身份验证凭据：

> Windows：使用[Elcomsoft Internet Password
> Breaker](https://www.elcomsoft.com/einpb.html)从用户的Web浏览器中提取存储的密码。这些通常可以在“apple.com”，“icloud.com”或“appleid.apple.com”的记录中找到。
>
> macOS：使用[Elcomsoft Password
> Digger](https://www.elcomsoft.com/epd.html)提取和分析macOS
> keychain。登录名和密码可以存储在包含关键字“apple”或“icloud”的记录中。
>
> iOS：如果你能够从iOS设备中提取keychain（通过使用[Elcomsoft iOS Forensic
> Toolkit](https://www.elcomsoft.com/eift.html)进行逻辑或物理采集），则可以使用[Elcomsoft
> Phone Breaker](https://www.elcomsoft.com/eppb.html)来分析 keychain。注意：用户的Apple
> TV也可能包含这些密码，因此分析它可能是一个不错的选择。

注意，你仍然必须通过双因素身份验证才能够访问受2FA保护的帐户。

## 总结

iCloud身份验证令牌不再像过去一年前那样易于使用。令牌的加密和保护与访问限制相结合，使得认证令牌对于访问选定类型的同步数据非常有用。最有趣的证据类型，如iCloud备份，保存的密码，运行状况和消息都将无法使用令牌进行访问。

 ***参考来源：[elcomsoft](https://blog.elcomsoft.com/2019/07/accessing-icloud-with-and-without-a-password-in-2019/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  


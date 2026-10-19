## ➊ TL;DR（太长了，不想读）

第二代密码管理器：有主密码保护的独立密码管理器

 **安全技术：** 设置独立的主密码，端到端加密

 **安全问题：** 一旦主密码泄露，可能导致所有密码被盗

硬核警告，请酌情食用。

## ➋ 进化

第一代有管理，无保护；要么不加密，要么加密没卵用。

对于密码这么重要的数据，第一代密码管理器实在是太不安全了。

为了解决这个问题，早在2000年左右，海外的一些技术狂人和鬼才程序员们已经开始埋头苦干，奋力研究如何更好地保护大家的密码。

也就是从那时开始，独立的专业密码管理器接二连三地诞生，其中包括比较知名的开源密码管理器：[Password Safe(since
2002)](https://www.pwsafe.org/)和 [KeePass(since 2006)](https://keepass.info/)

![keepass.jpg](https://image.3001.net/images/20200311/1583903131_5e68719b09953.jpg!small)

☝️ 很多人还在用的 KeePass 密码管理器

第二代密码管理器带来了真正的加密保护：独立的主密码。

私密笔记也可以设置密码，输入密码才能看到保存的密码呢！

虽然用起来差不多，但关键还得看是怎样加密的。

很多私密笔记设置的密码仅仅用于访问控制，

 **根本没有加密！**

 **根本没有加密！**

 **根本没有加密！**

## ➌ 加密

加密为什么这么重要？因为良好的加密设计能够保证，目前的计算机水平无法破解！

> 同时也要明白， **加密 ≠ 安全**

密码管理器一般都使用对称加密算法（至于非对称加密算法，本文不展开），就是加密和解密都使用相同的密钥 `key`，

cipher = encrypt(key, plain)

plain = decrypt(key, cipher)

  

密码学的设计认为，

• 加密算法 `encrypt`/`decrypt`无法保密，黑客是可以知道的；

• 使用密钥 `key`可以很容易从密文 `cipher`解密得到明文 `plain`（要保护的数据），没有 `key`就不行；

• 要求保护好密钥 `key`，要求密钥 `key`完全随机，防止黑客破解。

目前最流行的对称加密算法是 `AES(Advanced Encryption Standard)`，根据密钥
`key`的长度分为3个级别：128/192/256 bit。其中
`AES-256`作为最高级别的算法，被广泛应用于金融、军事等领域，也被很多密码管理器采用。

有些密码管理器声称使用了军事级别等加密技术，一般就是指使用了 `AES-256`算法加密。

![bent-gun.jpg](https://image.3001.net/images/20200311/1583903148_5e6871ac67e81.jpg!small)

☝️ 军事级别加密只是营销口号

然而并不是使用了最高等级的加密算法，密码管理器就达到了最高的安全水平！

黑客通常不会破解加密算法，只会尝试获得密钥 `key`。

## ➍ 密钥生成

既然黑客最惦记的是密钥 `key`，那怎样保护好密钥就是密码管理器的关键技术了。

一般来说，用户设置的主密码是不能用作密钥 `key`加密数据的，不满足随机性要求。

最低等级的 `AES-128`要求至少需要20个完全随机的字符，没人记得住！！！

于是密码学家们发明了 基于密码生成密钥的算法 `PBKDF(Password-Based Key Derivation
Function)`，把密码转换成足够长又完全随机的安全密钥，就可以加密数据了。

![unbelievable.jpg](https://image.3001.net/images/20200311/1583904234_5e6875ea7d794.jpg!small)

目前推荐的算法是 [PBKDF2](https://baike.baidu.com/item/PBKDF2)， `bcrypt`,
`scrypt`等其他算法也有应用。

尽管每个算法的具体细节不尽相同，但基本原理其实都是一样的，如下：

key = Hash(password, salt)

这里的 `salt`非常关键，它是完全随机的。所以即使是很简单的密码，也能通过单向的 `Hash`函数计算出完全随机的 `key`作为密钥，满足了加密要求。

> `salt`应该使用 `真随机数生成器(True Random Number Generator)`生成

一句话解释：通过主密码生成保护数据的安全密钥 `key`。

## ➎ 暴力破解

密码搜索空间肯定没有密钥那么大，那黑客是不是可以暴力破解密码呢？

当然，密码学的算法都是公开的，黑客也可以使用同样的算法，一个一个试，总能够算出那个相同的密钥 `key`，然后解密出数据原文。

为了应对暴力破解，`PBKDF`算法并不像普通的 `Hash`算法那样快，相反它被故意设计成很慢（或者需要消耗较多计算资源）。

`PBKDF`还可以设置迭代次数 `count`，开发者可以根据当前的计算机硬件水平选择合适的迭代次数。`PBKDF2`算法推荐设置为 10000
左右。这样黑客要暴力破解，消耗的计算资源也就增长了10000倍。

不要把迭代次数 `count`设置为 1,000,000，否则用户输入主密码的时候，要计算很久。

![fading-flower.jpg](https://image.3001.net/images/20200311/1583903394_5e6872a23b875.jpg!small)

一句话解释：生成密钥的算法很消耗计算资源，提高了暴力破解的难度。

## ➏ 核心算法

把前面的知识串起来就是第二代密码管理器的核心算法设计了，

 **（1）设置主密码**

![image.png](https://image.3001.net/images/20200311/1583900579_5e6867a32cddb.png!small)

用户设置主密码后，密码管理器通过 `PBKDF2`生成了加密密钥 `key`，并且把参数 `salt`和 `count`保存起来 `KeyFile`。

• 密钥 `key`用于加密数据，只在程序运行中使用，并不保存

• `KeyFile`用于解锁时生成密钥 `key`

大声说三遍，

不保存主密码！

不保存主密码！

不保存主密码！

一句话解释：通过主密码生成安全的加密密钥 `key`，并且保存密钥生成算法的参数。

 **（2）加密数据**

**![image.png](https://image.3001.net/images/20200311/1583901324_5e686a8cc3c2c.png!small)  
**

加密后，把加密的参数`IV(Initial Vector)`和密文 `cipher`一起保存下来 `CipherFile`。密钥
`key`和被保护的数据明文 `plain`不保存。

一句话解释：使用安全密钥加密数据，保存密文（加密后的数据）。

 **（3）解密数据**

![image.png](https://image.3001.net/images/20200311/1583901406_5e686aded4fe4.png!small)

解密就是把前面两个步骤反过来，

• 先从 `KeyFile`中读取 `PBKDF2`参数 `salt`和 `count`，经过同样的计算得到密钥 `key`

• 再读取加密参数 `IV`和 密文 `cipher`，使用AES解密算法得到原文 `plain`

一句话解释：按照同样的方法从主密码生成密钥 `key`，再使用解密算法从密文解密出原文。

实际应用中，每个密码管理器都可能做一些独特的设计和扩展。

比如不直接使用密码生成的密钥 `key`来加密保存的数据，而是加密另一个密钥 `key2`，再用 `key2`来加密真正要保护的数据。

## ➐ 第二代安全技术

第二代密码管理器技术特点：

• 使用 `PBKDF`算法，从主密码生成安全的密钥 `key`

• 使用高强度的加密算法（如AES）加密数据

• 不以任何形式存储 `主密码`

AES加密算法本身很安全，只要选取了合适的密钥生成算法（如 `PBKDF2`） + 真正随机的 `salt`\+ 合理的迭代次数
`count`，第二代密码管理器就极难被破解，除非黑客能够破解主密码。

相比第一代密码管理器，第二代密码管理器大大提升了安全水平，只要保护好 `主密码`，就能保证数据安全。

第二代密码管理器使用主密码加密数据，真正提升了数据的安全性，是一个巨大的进步。

今天仍然有很多人使用小本子记密码，使用浏览器保存密码，这都是不推荐的，因为密码并没有得到多少保护。

 **保存密码，至少应该使用第二代密码管理器**

## ➑ 假二代？

并不是设置了主密码就是第二代密码管理器。市面上很多密码管理器甚至声称 `军事级别加密`，实际上大部分仍然停留在第一代的设计水平。

我们来打假吧。

[TeamSIK](https://team-sik.org/trent_portfolio/password-manager-apps/)在并不遥远的2016年，找到了一些密码管理器的安全漏洞，从披露的信息中可以得知它们的设计水平。

我们只能判断漏洞修复前的设计水平，开发商有可能在修复漏洞时改善设计。

（1）[SIK-2016-020 My Passwords](https://team-sik.org/sik-2016-020/)披露的主要信息，

  * > The app stores an encrypted version of the user’s master password (“master_key”) in the shared preferences file.
>
> With these two values, it is possible to reconstruct the user’s master
> password and log into the app. The attacker can thus extract all of the
> user’s stored passwords.

点评：

`My Passwords`使用了一个很弱的自创加密算法，加密并保存主密码，安全性远远不如第二代密码管理器不保存主密码的设计。

（2）[SIK-2016-021 Mirsoft Password Manager](https://team-sik.org/sik-2016-021/)披露的主要信息，

  * > The master password is stored in an insecure way. The password is encrypted, but the key for this encryption is part of the application code (equal on all devices).

点评：

`Mirsoft Password Manager`使用了写死的密钥，加密并保存主密码，违背了密钥应该保密的原则，而且也不应该保存主密码（即使是加密保存）。

（3）[SIK-2016-022 LastPass Password Manager](https://team-sik.org/sik-2016-022/)披露的主要信息，

  * > The master key and the PIN are symmetrically encrypted and stored in a shared preferences file in the local app folder. The key/PIN are stored encrypted. The key for encrypting/decrypting the credentials is hard coded into the application’s source code.

点评：

`LastPass`是非常流行的密码管理器，和 `Mirsoft Password
Manager`一样使用写死的密钥，加密并保存主密码，同样属于第一代设计水平。

（4）[SIK-2016-026 Keeper Password Manager](https://team-sik.org/sik-2016-026/)披露的主要信息，

  * > If the user is logged out the master password has to be entered to access the passwords in the app.
>
> By entering the password incorrectly once the adversary can select “Forgot
> Password” after which a verification code has to be entered.
>
> The app then fails to show the login activity but shows an empty password
> list with a different background. When spawning the
> com.callpod.android_apps.keeper/.DeepLinkActivity it is possible to add new
> passwords without providing the master password. When adding new passwords a
> user is able to attach files to the entry. An adversary could abuse this by
> attaching malicious files to the password entries. A user might wonder what
> these files contain when using the keeper desktop application or the online
> service. This can trick the user to execute code on his machine.

点评：

黑客没有输入主密码，也能够保存数据到 `Keeper`里面。从这个漏洞描述来推断，数据很可能没有经过主密码生成的密钥加密，不符合第二代密码管理器的安全特性。

（5）[SIK-2016-027 F-Secure KEY Password Manager](https://team-sik.org/sik-2016-027/)披露的主要信息，

  * > The master password of this password manager is stored in plain text in the local app folder.

点评：

F-Secure 是一家历史悠久的安全公司，旗下的密码管理器产品竟然犯下明文保存主密码的低级错误。。。

只能说，他们知道怎么杀病毒，但完全不知道怎么保护密码。

（6）[SIK-2016-030 Dashlane Password Manager](https://team-sik.org/sik-2016-030/)披露的主要信息，

  * > The Dashlane password manager implements an own browser. This browser contains an implementation flaw wich allows local app folder read access without root permission. An attacker can abuse this vulnerability to read out sensitive information from the local app folder.

点评：

`Dashlane`也保存了主密码，黑客偷取主密码就可以偷取所有密码了。

（7）[SIK-2016-032 Hide Pictures Keep Safe Vault](https://team-sik.org/sik-2016-032/)披露的主要信息，

  * > Application stores master password or pin in plain text in app folder.
>
> For a system using „military encryption“ standards this is a serious
> vulnerability.

点评：

又一个“明文保存主密码”，`军事级别加密`那只是营销口号，并不代表安全。

再强调一遍，以上漏洞都已经修复

![no-do-bad.jpg](https://image.3001.net/images/20200311/1583903417_5e6872b92e03e.jpg!small)

### 小心网络密码管理器

密码只需要保存一次，就可以自动同步到所有设备终端，网络密码管理器好方便，但也好危险。

按照第二代密码管理器的方法设计，加上网络同步功能，

• 在设备A上创建主密码并保存了 `salt`和 `count`，加密数据；

• 通过网络/云服务，将保存的 `salt`, `count`和 加密后的数据同步到设备B；

• 设备B上输入同样的主密码，有 `salt`, `count`生成密钥，解密，查看保存的数据；

这就是著名的端到端加密(End-to-end Encryption)技术。只有终端设备上可以查看信息，中间的传输网络无法解密。

如果网络密码管理器可以重置主密码，那可要小心了。

> 是重置主密码，不是修改主密码

既然加密密钥 `key`只能够通过主密码生成，那在不提供主密码的情况下，服务商怎么帮你重置主密码呢？

答案是，服务商很可能帮你保管加密密钥。

既帮你在云端保管加密数据，又帮你保管加密密钥，好贴心！

![worry.jpg](https://image.3001.net/images/20200311/1583903436_5e6872cc79cd7.jpg!small)

你的密码离破解连一个主密码的距离都没有了

这还是第一代密码管理器的安全水平！

## ➒ 怎样设置主密码

既然安全的关键在于主密码，那应该怎样设置主密码呢？

斯诺登建议使用密码短语(Passphrase)

> 顺便帮他打一波广告，他的书《永久记录》在中国出版了，强烈推荐！

本文建议使用一整句话作为主密码。例如，

Isetupmymasterpasswordin2020

2020nianWuhanbaofalebingdu

没有特殊符号安全吗？

从信息量的角度计算，16个大小写字母和数字组合，和12个字母、数字、符号组合强度差不多。当然你也可以在末尾加上标点符号。

从暴力破解的角度来看，如果黑客不知道你的密码长度，通常会按照密码长度递增的方式尝试破解。越长的密码，暴力破解浪费的计算资源也就越多，增加了破解成本。

## ➓ 主密码的安全问题

要想第二代密码管理器能够真正保护密码的安全，主密码需要满足两个条件：

• 要足够长，要足够强

• 不能被别人知道

遗憾的是，现实中还是会遇到很多问题，

• 主密码强度不够

很多用户并不知道主密码需要很高的强度，也不知道怎样设置高强度的主密码。

• 主密码很多时候会泄露

比如在输入主密码时，可能被不怀好意的人偷窥；被电梯的摄像头录制下来；被设备上的恶意App录屏；女朋友问密码，说还是不说，这是个问题。

![shoulder-surfing.jpg](https://image.3001.net/images/20200311/1583904710_5e6877c679afd.jpg!small)

• 主密码会被重用

可能是记忆密码实在是太困难了，以至于还有不少用户会重用主密码。重用主密码其实很危险。一方面，这增加了主密码被偷窥的机会。另一方面，很多互联网服务安全性并不高，一旦另一个互联网服务泄露了密码，那密码管理器的主密码也就暴露了。

如果使用网络密码管理器，还重用主密码，那真的是很可能：哦豁，完蛋！

讲个故事吧，

> 有个小白叫小白，很喜欢用 `第一密码`这个网络密码管理器，她把所有银行账号密码都存进去了，数据同步到云端很方便。
>
> 有个小黑叫小黑，偷偷打开了 `第一密码`的服务器，在里面找到了好多宝贝，都是加密的！
>
> 解密宝贝这事儿可难不倒小黑，他找来 `你的空间`这个平台泄露的密码数据库，发现 `第一密码`和 `你的空间`有很多相同的用户，其中就有小白。
>
> （这不是什么奇怪的事情，要知道前几年谁都有 `你的空间`的账号呀）
>
> 小黑试了一下，发现小白的 `你的空间`密码也可以解锁她在 `第一密码`存的数据呢！
>
> （然后，小黑打开银行网站...）

密码管理器厂商会被入侵的吗？

是的，是的，密码管理器厂商也会被入侵，看这个 [LastPass Security
Notification](https://blog.lastpass.com/2011/05/lastpass-security-notification.html/)，还有这个 [LastPass
Hacked](https://blog.lastpass.com/2015/06/lastpass-security-notice.html/)

![surprise.jpg](https://image.3001.net/images/20200311/1583904724_5e6877d4d34e6.jpg!small)

互联网服务真的会泄露密码吗？

已经有很多互联网服务都泄露密码了，[have i been
pwned](https://haveibeenpwned.com/)能收集到证据的记录就已经超过地球人口总数了，～95亿。

> 曾经著名的社交网站 `My Space`一家就泄露了3.6亿之多。

![haveibeenpwned.png](https://image.3001.net/images/20200311/1583904736_5e6877e0aeb1d.png!small)

没能收集到证据的还有很多，全部泄露的总数不敢想象。


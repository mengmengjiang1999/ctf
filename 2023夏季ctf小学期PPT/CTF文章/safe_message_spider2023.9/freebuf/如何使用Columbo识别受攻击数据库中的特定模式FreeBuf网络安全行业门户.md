![](https://image.3001.net/images/20210411/1618123777_60729c01408fe1f335a66.jpg!small)

## 关于Columbo

Columbo是一款计算机信息取证与安全分析工具，可以帮助广大研究人员识别受攻击数据库中的特定模式。该工具可以将数据拆分成很小的数据区块，并使用模式识别和机器学习模型来识别攻击者的入侵行为以及在受感染Windows平台中的感染位置，然后给出建议表格。需要注意的是，当前版本的Columbo仅支持在Windows操作系统平台上执行任务。

## 依赖组件&高级架构

Columbo依赖于volatility
3、autorunsc.exe和sigcheck.exe实现其数据提取功能。因此，广大用户在使用Columbo之前必须下载这些依赖工具，并将它们存放在\Columbo\bin目录下。这些工具所生成的输出数据将会通过管道自动传输到Columbo的主引擎中。接下来，Columbo会将传入的数据进行拆分，并对其进行预处理，然后使用机器学习模型对受感染系统的路径位置、可执行文件和其他攻击行为进行分类。

## 视频资料

1、在你开始使用Columbo之前，请先观看【https://www.youtube.com/watch?v=7rUCC1Wz4Gc】。

2、使用【Columbo Memory-forensics】（https://www.youtube.com/watch?v=fOa62iVemAQ）进行内存取证分析。

## 工具安装与配置

1、下载并安装Python 3.7或3.8（未测试3.9），确保你已经在安装过程中将python.exe添加到了PATH环境变量中。

2、访问项目的【https://github.com/visma-prodsec/columbo/releases】下载最新的Columbo源码。

3、下载下列组件，然后将它们存储至\Columbo\bin中：Volatility 3源码、autorunsc.exe和sigcheck.exe。

为了避免报错，目录结构必须为\Columbo\bin\volatility3-master、\Columbo\bin\autorunsc.exe
和\Columbo\bin\sigcheck.exe。

4、最后，双击\Columbo目录中的“exe”即可启动Columbo。

## Columbo与机器学习

![](https://image.3001.net/images/20210411/1618123807_60729c1f347dcea0cc7be.jpg!small)

Columbo使用数据预处理技术来组织数据和机器学习模型来识别可疑行为。它的输出要么是1（可疑的），要么是0（正常的），它会以一种建议的形式帮助网络安全与计算机取证人员进行决策分析。我们使用了不同的测试用例来训练该模型，并以最大限度提升了输出数据的准确性，以及减少误报的出现。但是，工具输出的假阳性依然会存在，因此我们目前仍在定期更新模型。

## 假阳性

减少误报其实并不容易，尤其是涉及到机器学习的时候。机器学习模型产生的输出假阳性高或低，这取决于用于训练模型的数据的质量。但是，为了协助网络安全与计算机取证人员进行调查，Columbo会为其输出提供相应的准确百分比系数（1-可疑的，0-正常的），这种方法有助于研究人员选择需要进行分析的可疑路径、命令或进程。

![](https://image.3001.net/images/20210411/1618123818_60729c2a074043adcbbda.png!small)

## 操作选项

### 实时分析-文件和进程跟踪

此选项将分析正在运行的Windows进程以识别正在运行的恶意活动（如果有的话）。Columbo会使用autorunsc.exe从目标设备中提取数据，并输出通过管道传输到机器学习模型和模式识别引擎，对可疑活动进行分类。接下来，输出将以Excel文件的形式保存在\Columbo\ML\Step-2-results下，以供进一步分析。此外，Columbo还为用户提供了检查正在运行进程的选项。结果将包含诸如进程跟踪、与每个进程相关联的命令（如果适用）以及进程是否负责执行新进程等信息。

### 扫描和分析硬盘镜像文件（.vhdx）

该选项可以获取已挂载的Windows硬盘镜像路径，它将使用sigcheck.exe从目标文件系统中提取数据。然后将结果导入机器学习模型，对可疑活动进行分类。输出将以Excel文件的形式保存在\Columbo\ML\Step-3-results下。

### 内存信息取证

使用该选项时，Columbo会选择内存镜像的路径，并生成以下选项供用户选择。

> 内存信息：使用Volatility 3提取关于镜像的信息。
>
> 进程扫描：使用Volatility
> 3提取进程和每个进程给相关的DLL以及处理信息。接下来，Columbo会使用分组和聚类机制，根据每个进程的上级进程对它们进行分组。此选项稍后会由异常检测下的进程跟踪选项使用。
>
> 进程树：使用Volatility 3提取进程的进程树。
>
> 异常检测和进程跟踪：使用Volatility
> 3提取异常检测进程的列表。但是，Columbo提供了一个名为“进程跟踪”的选项来分别检查每个进程，并生成以下信息：可执行文件和相关命令的路径、利用机器学习模型确定所识别进程的合法性、将每个进程一直追溯到其根进程（完整路径）及其执行日期和时间、确定进程是否负责执行其他进程、收集整理每个进程的上述信息并提供给用户。

## 项目地址

Columbo：https://github.com/visma-prodsec/columbo

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。


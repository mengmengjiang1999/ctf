![](https://image.3001.net/images/20201204/1607096602_5fca591a55b25b0dc25fd.png!small)

## Pesidious

Pesidious能够使用深度强化学习和生成对抗网络（GAN）来对恶意软件进行变异，简而言之，它可以使用人工智能技术来生成恶意软件变种样本（PE32），并绕过基于人工智能的恶意软件分类器，而不会影响恶意软件的原有功能。在此之前，已经有很多研究人员在这一领域已做出了一些有意义的工作，研究人员要么选择使用强化学习，要么选择使用生成对抗网络来作为他们修改恶意软件可执行状态的武器，以尝试欺骗反病毒代理。

PS：本文仅用于技术研究与讨论，严禁用于任何非法用途，违者后果自负

但是，我们现在所设计的解决方案将深度强化学习和GANs结合起来，以克服在独立使用这些方法时所面临的一些限制，整个解决方案架构如下图所示：

![](https://image.3001.net/images/20201204/1607096610_5fca5922e198b1f351270.png!small)

## 依赖组件

> PyTorch
>
> Lief
>
> PE Bliss
>
> Gym-Malware
>
> MalwareGAN

## Pesidious安装

注意，由于该工具处理的是恶意软件和恶意文件，因此我们强烈建议使用虚拟机来进行测试。工具安装完成后，确保设备断开网络连接。

接下来，大家可以按照下列步骤安装工具依赖组件并配置相关环境。

首先，我们需要在本地主机上安装并配置好[ _Python 3.6环境_](https://realpython.com/installing-python/)。

接下来，使用下列方式将该项目源码克隆至本地：

    
    
    git clone https://github.com/CyberForce/Pesidious

将项目源码克隆至本地之后，需要在命令行工具中切换到Pesidious主目录中：

    
    
    cd Pesidious

然后，安装、配置并激活安装了Python 3.6的虚拟环境。确保我们已经安装并配置好了pip 8.1.1：

    
    
    pip install pip==8.1.1

接下来，安装Pesidious所有的依赖组件，这里可以直接利用requirements.txt文件来进行安装：

    
    
    pip install -r pip_requirements/requirements.txt

## 如何生成恶意软件变种

生成对抗网络（GAN）的输出数据会以RL_Features/adverarial_imports_set.pk和RL_Features/adverarial_sections_set.pk的形式进行存储，之后将用于对恶意软件进行变异操作。

1、我们可以测试样本分类器来对恶意软件文件进行评估：

    
    
    python classifier.py -d /path/to/directory/with/malware/files

2、运行mutate.py脚本来对恶意软件样本进行变异操作：

    
    
    python mutate.py -d /path/to/directory/with/malware/files

3、恶意软件样本变种文件将会以下列格式存储在一个名为Mutated_malware的目录中：

    
    
    Mutated_malware/mutated_<name-of-the-file>

4、当恶意软件文件变异完成后，你可以再次运行恶意软件分类器来对变异后的恶意软件样本进行评估：

    
    
    python classifier.py -d Mutated_malware/

## 项目地址

Pesidious：【[ _GitHub传送门_](https://github.com/CyberForce/Pesidious)】

## 参考资料

> [
> _https://vaya97chandni.gitbook.io/pesidious/_](https://vaya97chandni.gitbook.io/pesidious/)
>
> [ _https://arxiv.org/abs/1801.08917_](https://arxiv.org/abs/1801.08917)
>
> [ _https://docs.microsoft.com/en-us/windows/win32/debug/pe-format#general-> concepts_](https://docs.microsoft.com/en-us/windows/win32/debug/pe-> format#general-concepts)
>
> [
> _https://ieeexplore.ieee.org/abstract/document/8676031_](https://ieeexplore.ieee.org/abstract/document/8676031)
>
> [
> _https://resources.infosecinstitute.com/_](https://resources.infosecinstitute.com/)
>
> [ _https://resources.infosecinstitute.com/2-malware-researchers-handbook-> demystifying-pe-> file/#gref_](https://resources.infosecinstitute.com/2-malware-researchers-> handbook-demystifying-pe-file/#gref)
>
> [ _https://arxiv.org/abs/1702.05983﻿_](https://arxiv.org/abs/1702.05983)

  


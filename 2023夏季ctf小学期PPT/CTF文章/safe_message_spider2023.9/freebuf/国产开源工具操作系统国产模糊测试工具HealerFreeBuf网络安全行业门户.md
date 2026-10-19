数字化技术的应用，成为了金融机构良性发展的驱动力，却也在诸多方面留下了安全隐患。近期人民银行办公厅联合中央网信办等多家单位联合发布的《关于规范金融业开源技术应用与发展的意见》（以下简称《意见》），再次将金融信息安全的问题放到了舆论的风口浪尖。

“鼓励金融机构将开源技术应用纳入自身信息化发展规划，加强对开源技术应用的组织管理和统筹协调”，《意见》从政策层面规范了金融科研机构对于新兴数字化技术的使用场景和使用模式，而在技术层面，诸多国内技术团队也在提供更智能的开源自动化模糊检测方案，强化我国在相关技术方向的自主可控能力。

最近，水木羽林联合清华大学软件学院Wingtecher
Lab就开源了操作系统模糊测试工具Healer，本文将介绍利用Healer进行操作系统安全测试的基础原理及其使用方法，Healer是一款ƒ高效的内核模糊测试工具，由水木羽林与清华大学软件学院Wingtecher
Lab联合研发，可用于快速挖掘内核风险。

Healer项目开源地址：https://github.com/SunHao-0/healer

## Healer原理介绍

操作系统内核测试需要解决的一个核心问题是高质量调用序列的生成。Healer兼容现有kernel fuzzer的特征，例如，
Healer可以直接利用业界广泛使用的Google
Syzkaller的接口描述，来自动生成满足结构约束和部分语义约束的系统调用序列，从而保证生成的每个调用不被简单的内核参数检查拒绝，并通过执行生成的调用序列来触发内核崩溃、不断地发现内核漏洞。
但又不同于现有工具，Healer设计实现了高效的算法和框架来优化整个Fuzz流程，例如，Healer通过使用系统调用之间的影响关系来引导调用序列的生成与变异，尽可能地保证调用序列中的前序调用为后续调用设定需要的内核状态，并通过关系学习算法在运行时不断精化和发现新的影响关系、优化整个fuzz过程。如下图所示，关系学习算法实际上在推导一个非常复杂的图结构，其中每个节点对应一个系统调用，每条边对应调用之间的影响关系。
![](https://image.3001.net/images/20211025/1635140254_6176429e956c4b8e2145a.png!small)

最终效果上，Healer生成的系统调用序列步骤更多、更有效，可以提高每个测试用例达到内核深层逻辑、挖掘深层漏洞的效率。
基于标准对比实验可以发现，相比于Google
Syzkaller、Moonshine等同类工具，Healer可以达到28%以上的覆盖深度提升、2倍以上的覆盖速度加速。

![](https://image.3001.net/images/20211025/1635140477_6176437dde2c8f2cc5ddc.png!small)

关于Healer的更多信息，可阅读孙浩、沈煜恒、刘建中及姜宇等人发表在ACM SOSP 2021的论文[《HEALER: Relation Learning
Guided Kernel
Fuzzing》](http://www.wingtecher.com/themes/WingTecherResearch/assets/papers/healer-sosp21.pdf)。 截止目前，Healer已向Linux社区汇报了数百个漏洞，已确认并修复60余个。

## Healer使用方式

### 安装Healer

除了少部分补丁代码（Golang，C），Healer是使用高效的系统级编程语言rust从零研发。 编译构建Healer需要安装下述依赖：

  * 最新版rust工具链
  * Golang环境，启用Go mod
  * Gcc，1.0版本或更新
  * Qemu，0版或更新

除了上述工具依赖，一些常见的工具也需要被安装，例如sha384sum、patch、make工具。

一旦上述工具准备就绪，Healer可以通过如下命令一键构建：

> > cargo build --release

 **小提示** ：使用nightly版本，并设置构建目标可获得进一步的性能加速（RUSTFLAGS="-C target-cpu=native"）

最终，编译好的二进制可以在项目目录下的target/release目录中找到，其中healer为最核心的可执行文件，syz-bin下有构建好的打过补丁的执行器。

## Healer基础用法

使用Healer对Linux内核进行模糊测试仅需两个步骤：

（1）构建磁盘镜像与内核；

（2）创建工作目录与启动Healer。

Healer利用Qemu启动待测内核，因此我们需要准备一个磁盘镜像和待测内核本身。
磁盘镜像可以通过两种方式获得：第一种是利用完全自动化的脚本来构建，例如使用Syzkaller提供的[create-image.sh](https://github.com/google/syzkaller/blob/master/tools/create-image.sh)脚本；第二种是使用三方构建好的镜像，例如Linux发行版提供的镜像。 得益于Linux内核本身优秀的构建方案，编译待测内核也非常容易。
在获得Linux内核源码后，我们仅需在内核编译配置文件（.config文件）中添加覆盖率、sanitizer选项，随后一键构建即可（make）。
推荐启用如下配置项，更多编译配置可参考[这部分指导](https://github.com/google/syzkaller/blob/master/docs/linux/kernel_configs.md)。

> # 覆盖率  
> CONFIG_KCOV=y  
> # 用于符号化的调试信息  
> CONFIG_DEBUG_INFO=y  
> # 内存错误检测器  
> CONFIG_KASAN=y  
> CONFIG_KASAN_INLINE=y  
> # 部分镜像要求的特性  
> CONFIG_CONFIGFS_FS=y  
> CONFIG_SECURITYFS=y

上述步骤结束后，我们就获得了stretch镜像与用于登录的ssh密钥文件stretch.id_rsa以及待测内核bzImage。

随后我们可以构建一个工作目录，下面用环境变量WORK-DIR表示。
把准备好的镜像拷贝到工作目录，并把可执行文件拷贝到工作目录下的bin目录，最后工作目录应该有如下内容：

> > cd $WORK_DIR && ls  
> bin bzImage stretch.id_rsa stretch.img  
> > ls $WORK_DIR/bin  
> healer linux_amd64 syz-repro syz-symbolize syz-sysgen

到了这一步，我们的准备工作就都完成了，我们可以使用如下命令一键启动Healer，开始整个fuzz过程：

> > healer -d stretch.img -s stretch.id_rsa -k bzImage

其中，-d、-s、-k分别指定了磁盘镜像、ssh-key以及待测内核，也可以使用默认参数直接启动Healer，无需提供任何命令行参数。
如果一切正常，那么如下日志会被打印：

![](https://image.3001.net/images/20211025/1635140358_61764306d4ffc969d6e3b.png!small)

可以看到，Healer会自动加载输入语料、检测内核特性、预启动检错，等待初始setup、检测过程完成，整个fuzz过程就开始了，可以通过日志数据、存储在输出目录的数据查看内核奔溃、覆盖数据等。

## Healer进阶用法

为了支持不同的使用场景，Healer还支持更高级的使用方法，下面将进行简单介绍。

 **架构支持** **：**
Healer支持非常多架构的运行和Fuzz，例如x86/x86_64、arm/arm64、mips、ppc64等架构，这一特性在编译时会自动配置，无需任何手动的配置。

 **多实例** **fuzz** **：** Healer支持并发多实例fuzz，通过-j参数即可指定，每个实例对应一个工作线程，工作线程会单独启动Qemu、执行整个fuzz流程，并与其它工作线程共享&同步数据。

 **Fuzz** **数据自动恢复：**
Healer支持Fuzz数据自动恢复与维护，每次Fuzz的数据，例如语料输入、崩溃数据，都会被Healer用特定的方式写出到输出目录，在每次重新启动时，用户无需做任何事，Healer会自动恢复Fuzz状态，并维护历史数据，例如为崩溃数据打时间戳，也可以通过-i选项指定新的输入语料，从而不断演进输出目录的语料质量。

 **错误注入白名单**
Healer：在测试时可以利用内核特性自动注入错误，从而检测内核鲁棒性。但一些内核模块稳定性较差，在这种模式下很容易引起重复崩溃，通过使用白名单、利用正则表达式可过滤掉对应模块。


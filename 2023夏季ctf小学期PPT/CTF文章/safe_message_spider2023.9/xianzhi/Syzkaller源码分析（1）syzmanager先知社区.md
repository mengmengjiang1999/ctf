# 0x00.一切开始之前

syzkaller 是由 Google 开发的一个十分强大的针对内核的 fuzzer，自其面世以来已经帮助全世界的内核安全研究员发现了数量惊人的内核漏洞

为了深入学习 fuzzing theory，笔者决定先从这个非常经典的 kernel fuzzer 的源码进行分析学习 ：）

## PRE.工作原理

对于 syzkaller 的架构，官方给出了这样的一张 Overview

![](./img/5842622352732233907.png)

syzkaller 整体上为一个 **双机调试结构** ：由一台机器负责管控整个 fuzzing 流程（本文称为 `Host`），在另一台机器上进行
fuzzing（本文称为 `Guest`），Guest 通常为虚拟机，从而能让 Host 更好地管控整个流程

syzkaller 分为三大组件：

  * 位于 Host：
    * `syz-manager` ：syzkaller 的控制中枢，其会启动多个 VM 实例（如图所示的一个黄色卡片就是一个实例）并进行监视，同时通过 RPC 来启动 `syz-fuzzer`
  * 位于 Guest：

    * `syz-fuzzer` ：负责引导整个 fuzz 的过程：
      * 生成 input
      * 启动 `syz-executor` 进程进行 fuzz
      * 从被 fuzz 的 kernel 的 `/sys/kernel/debug/kcov` 获得覆盖（coverage）的相关信息
      * 通过 RPC 将新的覆盖回送到 `syz-manager`
    * `syz-executor`：负责 **执行单个输入** ——从 `syz-fuzzer` 处接受 input 并执行，最后回送结果

`syz-manager` 为 syzkaller 的控制中枢，其会启动多个 VM 实例并进行监视，同时通过 RPC 来启动 `syz-fuzzer`，我们通常启动 fuzzing 时便是以 `syz-manager` 作为程序启动的入口点，因此笔者也先从此处开始分析

# 0x01. 基本结构体

相比于直接开始分析源码，笔者认为有必要在此之前先列出一些基本的结构体，你也可以把这一节当成一个表来查 ：）

## VM 管控相关

Host 需要去感知与管控 Guest VMs，因而在 `syz-manager` 当中有着一套相应的表示与管理 Guest VM 的结构体

### 1\. Instance：VM 实例

`syz-manager` 中的 VM 实际上是使用一个名为 `Instance` 的结构体来表示的，定义于 `vm/vm.go` 中：

    
    
    type Instance struct {
        impl     vmimpl.Instance
        workdir  string
        timeouts targets.Timeouts
        index    int
        onClose  func()
    }
    

类似地，其需要实现 `Interface` 接口，定义于 `vm/vmimpl/vmimpl.go` 中：

    
    
    // Instance 表示一个单独的 VM.
    type Instance interface {
        // Copy 复制一个 hostSrc 文件到 VM 中并返回 VM 中的文件名.
        Copy(hostSrc string) (string, error)
    
        // Forward 设置从虚拟机内到主机上给定 tcp 端口的转发，
        // 并返回要在虚拟机中使用的地址.
        Forward(port int) (string, error)
    
        // Run 在虚拟机内执行命令 (类似 ssh cmd).
        // outc 接受混合了命令行与内核控制台的输出.
        // errc 接受命令等待返回 error 或 vmimpl.ErrTimeout.
        // Command 在 timeout 后停止. 在 stop chan 上发送可以用以更早将其终止.
        Run(timeout time.Duration, stop <-chan bool, command string) (outc <-chan []byte, errc <-chan error, err error)
    
        // Diagnose 从 VM 上检索额外的调试信息
        // (例如通过发送一些 sys-rq's 或 SIGABORT'ing 一个 Go 程序).
        //
        // 选择性地直接返回 (一些或所有) 信息. 若 wait == true,
        // 调用者必须等待 VM 直接输出信息到其日志.
        //
        // rep 描述了 Diagnose 被调用的原因.
        Diagnose(rep *report.Report) (diagnosis []byte, wait bool)
    
        // Close 停止并销毁 VM.
        Close()
    }
    

  * `Copy()`：将一个来自宿主机的文件拷贝至虚拟机中，返回虚拟机中的文件名.
  * `Forward()`：设置从虚拟机内到主机上给定 tcp 端口的转发，并返回要在虚拟机中使用的地址
  * `Run()`：在虚拟机内执行命令
  * `Diagnose()`：在虚拟机上检索额外的调试信息
  * `Close()`：停止并销毁虚拟机

需要注意的是 **不同类型的 Guest VM 所实现的 Interface 接口是不同的**

> 以 QEMU 为例，其实现主要位于 `vm/qemu/qemu.go` 中

### 2.Pool：VM 池

类似于线程池的概念，在 `syz-manager` 中使用一个 **VM 池** —— `Pool` 结构体来管控 Guest VM，该结构体定义于
`vm/vm.go` 中：

    
    
    type Pool struct {
        impl        vmimpl.Pool
        workdir     string
        template    string
        timeouts    targets.Timeouts
        activeCount int32
    }
    

该结构体实现了 `Pool` 接口，定义于 `vm/vmimpl/vmimpl.go` 中：

    
    
    // Pool 表示了一组特定类型的测试机器 (虚拟机, 物理设备, etc).
    type Pool interface {
        // Count 返回池中所有 VM 的数量.
        Count() int
    
        // Create 创建并启动一个新的 VM 实例.
        Create(workdir string, index int) (Instance, error)
    }
    

  * `Count()`：返回池中所有 VM 的数量
  * `Create()`： **新建并启动一个 VM实例** ，返回新建的实例对象

#### QEMU VM 浅析

以 QEMU 为例的 Pool 接口实现如下，对于 `Count()` 而言会直接返回配置文件中的计数：

    
    
    func (pool *Pool) Count() int {
        return pool.cfg.Count
    }
    

`Create()` 则会首先检查文件系统镜像是否为 `9p` 格式，若是则会生成一个 ssh key 存放到 `key` 文件中并生成一个
`init.sh` 文件；接下来就是调用 `ctor()` 函数创建虚拟机：

    
    
    func (pool *Pool) Create(workdir string, index int) (vmimpl.Instance, error) {
        sshkey := pool.env.SSHKey
        sshuser := pool.env.SSHUser
        if pool.env.Image == "9p" {
            sshkey = filepath.Join(workdir, "key")
            sshuser = "root"
            if _, err := osutil.RunCmd(10*time.Minute, "", "ssh-keygen", "-t", "rsa", "-b", "2048",
                "-N", "", "-C", "", "-f", sshkey); err != nil {
                return nil, err
            }
            initFile := filepath.Join(workdir, "init.sh")
            if err := osutil.WriteExecFile(initFile, []byte(strings.Replace(initScript, "{{KEY}}", sshkey, -1))); err != nil {
                return nil, fmt.Errorf("failed to create init file: %v", err)
            }
        }
    
        for i := 0; ; i++ {
            inst, err := pool.ctor(workdir, sshkey, sshuser, index)
            if err == nil {
                return inst, nil
            }
            // Older qemu prints "could", newer -- "Could".
            if i < 1000 && strings.Contains(err.Error(), "ould not set up host forwarding rule") {
                continue
            }
            if i < 1000 && strings.Contains(err.Error(), "Device or resource busy") {
                continue
            }
            return nil, err
        }
    }
    

`ctor()` 的实现比较简单，主要就是创建一个带着 ssh key 及一些配置信息与一个 channel 的 `instance`
实例，初始化实例内的管道并调用 `boot()` 函数进行正式的创建：

    
    
    func (pool *Pool) ctor(workdir, sshkey, sshuser string, index int) (vmimpl.Instance, error) {
        inst := &instance{
            index:      index,
            cfg:        pool.cfg,
            target:     pool.target,
            archConfig: pool.archConfig,
            version:    pool.version,
            image:      pool.env.Image,
            debug:      pool.env.Debug,
            os:         pool.env.OS,
            timeouts:   pool.env.Timeouts,
            workdir:    workdir,
            sshkey:     sshkey,
            sshuser:    sshuser,
            diagnose:   make(chan bool, 1),
        }
        if st, err := os.Stat(inst.image); err != nil && st.Size() == 0 {
            // Some kernels may not need an image, however caller may still
            // want to pass us a fake empty image because the rest of syzkaller
            // assumes that an image is mandatory. So if the image is empty, we ignore it.
            inst.image = ""
        }
        closeInst := inst
        defer func() {
            if closeInst != nil {
                closeInst.Close()
            }
        }()
    
        var err error
        inst.rpipe, inst.wpipe, err = osutil.LongPipe()
        if err != nil {
            return nil, err
        }
    
        if err := inst.boot(); err != nil {
            return nil, err
        }
    
        closeInst = nil
        return inst, nil
    }
    

`boot()` 函数主要就是各种参数判断，之后 **把 QEMU 起了以后 ssh 连上去** ，这里就不摘抄代码了：）

### 3\. Env：单个 VM Pool 的环境变量

`Env` 结构体为用于一个 VM Pool 的环境变量，定义于 `vm/vmimpl/vmimpl.go` 中：

    
    
    // Env 包含了用于 VM 池的全局常量参数.
    type Env struct {
        // 独特的名字
        // 若几个 Pool 共享了全局命名空间则可被用于 VM name 的冲突解决
        Name      string
        OS        string // 目标 OS
        Arch      string // 目标 arch
        Workdir   string
        Image     string
        SSHKey    string
        SSHUser   string
        Timeouts  targets.Timeouts
        Debug     bool
        Config    []byte // json-序列化的 VM-类型-特定配置
        KernelSrc string
    }
    

### 4\. Type：VM 类型

一个 VM Pool 中只能有一种类型的 VM，因而不同类型的 VM 的 Pool 应当要有不同的构造函数，在 `syz-manager` 中使用
`Type` 结构体表示一种 VM 的类型信息，定义于 `vm/vmimpl/vmimpl.go` 中：

    
    
    type Type struct {
        Ctor       ctorFunc
        Overcommit bool
    }
    
    type ctorFunc func(env *Env) (Pool, error)
    

`ctorFunc` 为构造函数类型，其接受一个 `Env` 类型的结构体指针（储存了全局的一些基本信息），并返回一个 VM Pool 实例

由一个全局的 `string→Type` 映射表存储了不同类型 VM 的信息，在正式启动之前程序会通过 `Register()` 函数将不同类型的 VM
信息注册到该表中，定义于 `vm/vmimpl/vmimpl.go` 中：

    
    
    // Register 在包中注册一个新的 VM 类型.
    func Register(typ string, ctor ctorFunc, allowsOvercommit bool) {
        Types[typ] = Type{
            Ctor:       ctor,
            Overcommit: allowsOvercommit,
        }
    }
    
    //...
    
    var(
        //...
        Types = make(map[string]Type)
    

以 `QEMU` 为例，其在包被导入时注册构造函数，主要是调用 `LoadData()` 解析配置文件后进行检查，这里不再赘叙：

    
    
    func init() {
        var _ vmimpl.Infoer = (*instance)(nil)
        vmimpl.Register("qemu", ctor, true)
    }
    
    //...
    
    func ctor(env *vmimpl.Env) (vmimpl.Pool, error) {
        archConfig := archConfigs[env.OS+"/"+env.Arch]
        cfg := &Config{
            Count:       1,
            CPU:         1,
            Mem:         1024,
            ImageDevice: "hda",
            Qemu:        archConfig.Qemu,
            QemuArgs:    archConfig.QemuArgs,
            NetDev:      archConfig.NetDev,
            Snapshot:    true,
        }
        if err := config.LoadData(env.Config, cfg); err != nil {
            return nil, fmt.Errorf("failed to parse qemu vm config: %v", err)
        }
        if cfg.Count < 1 || cfg.Count > 128 {
            return nil, fmt.Errorf("invalid config param count: %v, want [1, 128]", cfg.Count)
        }
        if env.Debug && cfg.Count > 1 {
            log.Logf(0, "limiting number of VMs from %v to 1 in debug mode", cfg.Count)
            cfg.Count = 1
        }
        if _, err := exec.LookPath(cfg.Qemu); err != nil {
            return nil, err
        }
        if env.Image == "9p" {
            if env.OS != targets.Linux {
                return nil, fmt.Errorf("9p image is supported for linux only")
            }
            if cfg.Kernel == "" {
                return nil, fmt.Errorf("9p image requires kernel")
            }
        } else {
            if !osutil.IsExist(env.Image) {
                return nil, fmt.Errorf("image file '%v' does not exist", env.Image)
            }
        }
        if cfg.CPU <= 0 || cfg.CPU > 1024 {
            return nil, fmt.Errorf("bad qemu cpu: %v, want [1-1024]", cfg.CPU)
        }
        if cfg.Mem < 128 || cfg.Mem > 1048576 {
            return nil, fmt.Errorf("bad qemu mem: %v, want [128-1048576]", cfg.Mem)
        }
        cfg.Kernel = osutil.Abs(cfg.Kernel)
        cfg.Initrd = osutil.Abs(cfg.Initrd)
    
        output, err := osutil.RunCmd(time.Minute, "", cfg.Qemu, "--version")
        if err != nil {
            return nil, err
        }
        version := string(bytes.Split(output, []byte{'\n'})[0])
    
        pool := &Pool{
            env:        env,
            cfg:        cfg,
            version:    version,
            target:     targets.Get(env.OS, env.Arch),
            archConfig: archConfig,
        }
        return pool, nil
    }
    

### 5\. ResourcePool：VM 资源池队列

Guest VM 的资源调配主要是通过`ResourcePool` 这一结构来完成的，这实际上是一个 **存放空闲 VM の idx 的单向队列，决定了
VM 的调度顺序** ：

    
    
    type ResourcePool struct {
        ids   []int
        mu    sync.RWMutex
        Freed chan interface{}
    }
    

主要定义了这些方法来操纵资源池队列：

  * `Put()` ：向队列末尾添加空闲 VM の idx
  * `Len()` ：获取队列长度
  * `Take()`：从队列首部取出 `cnt` 个成员
  * `TakeOne()` ：从队列首部取出单个成员

    
    
    func (pool *ResourcePool) Put(ids ...int) {
        pool.mu.Lock()
        defer pool.mu.Unlock()
        pool.ids = append(pool.ids, ids...)
        // Notify the listener.
        select {
        case pool.Freed <- true:
        default:
        }
    }
    
    func (pool *ResourcePool) Len() int {
        pool.mu.RLock()
        defer pool.mu.RUnlock()
        return len(pool.ids)
    }
    
    //...
    
    func (pool *ResourcePool) Take(cnt int) []int {
        pool.mu.Lock()
        defer pool.mu.Unlock()
        totalItems := len(pool.ids)
        if totalItems < cnt {
            return nil
        }
        ret := append([]int{}, pool.ids[totalItems-cnt:]...)
        pool.ids = pool.ids[:totalItems-cnt]
        return ret
    }
    
    func (pool *ResourcePool) TakeOne() *int {
        ret := pool.Take(1)
        if ret == nil {
            return nil
        }
        return &ret[0]
    }
    

同时有一个 `SequentialResourcePool()` 函数用以初始化资源池：

    
    
    func SequentialResourcePool(count int, delay time.Duration) *ResourcePool {
        ret := &ResourcePool{Freed: make(chan interface{}, 1)}
        go func() {
            for i := 0; i < count; i++ {
                ret.Put(i)
                time.Sleep(delay)
            }
        }()
        return ret
    }
    

## 全局管控相关

### 1\. Manager：基本信息

`Manager` 结构体用于 **表示一个 syz-manager 的基本信息** ，定义于 `syz-manager/manager.go` 中：

    
    
    type Manager struct {
        cfg            *mgrconfig.Config
        vmPool         *vm.Pool
        target         *prog.Target
        sysTarget      *targets.Target
        reporter       *report.Reporter
        crashdir       string
        serv           *RPCServer
        corpusDB       *db.DB
        startTime      time.Time
        firstConnect   time.Time
        fuzzingTime    time.Duration
        stats          *Stats
        crashTypes     map[string]bool
        vmStop         chan bool
        checkResult    *rpctype.CheckArgs
        fresh          bool
        numFuzzing     uint32
        numReproducing uint32
    
        dash *dashapi.Dashboard
    
        mu                    sync.Mutex
        phase                 int
        targetEnabledSyscalls map[*prog.Syscall]bool
    
        candidates       []rpctype.Candidate // untriaged inputs from corpus and hub
        disabledHashes   map[string]struct{}
        corpus           map[string]CorpusItem
        seeds            [][]byte
        newRepros        [][]byte
        lastMinCorpus    int
        memoryLeakFrames map[string]bool
        dataRaceFrames   map[string]bool
        saturatedCalls   map[string]bool
    
        needMoreRepros chan chan bool
        hubReproQueue  chan *Crash
        reproRequest   chan chan map[string]bool
    
        // For checking that files that we are using are not changing under us.
        // Maps file name to modification time.
        usedFiles map[string]time.Time
    
        modules            []host.KernelModule
        coverFilter        map[uint32]uint32
        coverFilterBitmap  []byte
        modulesInitialized bool
    
        assetStorage *asset.Storage
    }
    

这里只说明比较关键的几个字段：

  * `cfg`：基本设置信息，对应存放在一个 json 文件中
  * `vmPool` ：所用的 VM Pool
  * `reporter`：用以报告 crash
  * `serv` ：RPC Server，用以与 Guest 间通信
  * `corpusDB`：存放语料的数据库
  * `targetEnabledSyscalls`：测试用例所允许使用的系统调用
  * `candidates`：待执行测试用例
  * `corpus`：语料库
  * `seeds`：用来对语料库变异的种子

### 2\. fuzzing phase

`syz-manager` 中将 fuzzing 流程分为如下的不同阶段：

    
    
    const (
        // 刚刚开始，啥都没做.
        phaseInit = iota
        // 加载了语料库且检查了机器.
        phaseLoadedCorpus
        // 从语料库中分类了所有输入.
        // 这是我们开始查询 hub 与最小化连续语料库的时候.
        phaseTriagedCorpus
        // 第一个请求发送到了 hub.
        phaseQueriedHub
        // 分类所有来自 hub 的新输入.
        // 这是我们开始复现 crashes 的时候.
        phaseTriagedHub
    )
    

## Fuzzing 结果相关

### 1\. Crash：记录 crash 信息

`manager.go` 中定义了`Crash` 结构体用以记录产生 crash 的 VM、机器信息等， **真正的 crash
信息主要存放在一个`Report` 结构体中**：

    
    
    type Crash struct {
        vmIndex int
        hub     bool // this crash was created based on a repro from hub
        *report.Report
        machineInfo []byte
    }
    

### 2\. Report：单次执行结果报告

`pkg/report/rteport.go` 中的 `Report` 结构体用以表示单次执行的结果，包括是否产生了 crash、Oops 的信息等等：

  * `Title`： **Oops 的第一行文本，用来标识特定类型的 crash**

> 例如 `BUG: unable to handle page fault for address: ffffffff81001619` 这样的

    
    
    type Report struct {
        // Title contains a representative description of the first oops.
        Title string
        // Alternative titles, used for better deduplication.
        // If two crashes have a non-empty intersection of Title/AltTitles, they are considered the same bug.
        AltTitles []string
        // Bug type (e.g. hang, memory leak, etc).
        Type Type
        // The indicative function name.
        Frame string
        // Report contains whole oops text.
        Report []byte
        // Output contains whole raw console output as passed to Reporter.Parse.
        Output []byte
        // StartPos/EndPos denote region of output with oops message(s).
        StartPos int
        EndPos   int
        // SkipPos is position in output where parsing for the next report should start.
        SkipPos int
        // Suppressed indicates whether the report should not be reported to user.
        Suppressed bool
        // Corrupted indicates whether the report is truncated of corrupted in some other way.
        Corrupted bool
        // CorruptedReason contains reason why the report is marked as corrupted.
        CorruptedReason string
        // Recipients is a list of RecipientInfo with Email, Display Name, and type.
        Recipients vcs.Recipients
        // GuiltyFile is the source file that we think is to blame for the crash  (filled in by Symbolize).
        GuiltyFile string
        // reportPrefixLen is length of additional prefix lines that we added before actual crash report.
        reportPrefixLen int
        // symbolized is set if the report is symbolized.
        symbolized bool
    }
    

# 0x02. main()：加载配置文件，启动 manager

`syz-manager` 的 `main()` 函数其实比较简单，主要就是载入配置文件信息并调用 `RunManager()` ：

    
    
    func main() {
        if prog.GitRevision == "" {
            log.Fatalf("bad syz-manager build: build with make, run bin/syz-manager")
        }
        flag.Parse()
        log.EnableLogCaching(1000, 1<<20)
        cfg, err := mgrconfig.LoadFile(*flagConfig)
        if err != nil {
            log.Fatalf("%v", err)
        }
        RunManager(cfg)
    }
    

> 这一节好像没什么好说的，直接继续往下看 RunManager() 吧 ：）

# 0x03. RunManager()：进行初始化工作

### Step 1. 初始化 VM Pool

首先是初始化 VM Pool，这里调用了 `vm/vm.go` 中的 `Create()` 来完成 VM pool 的创建

    
    
    var vmPool *vm.Pool
        // "none" 类型对于调试/开发而言是一种特殊情况，manager 并不会启动任何 VM，
        // 但相应的是你应当手动启动 VM 并在此启动 syz-fuzzer.
        if cfg.Type != "none" {
            var err error
            vmPool, err = vm.Create(cfg, *flagDebug)
            if err != nil {
                log.Fatalf("%v", err)
            }
        }
    

该函数主要就是获取 VM 类型、封装一个 Env 结构体、调用对应类型 VM Pool 的构造函数：

    
    
    // Create 创建一个可用于创建独立 VMs 的 VM pool.
    func Create(cfg *mgrconfig.Config, debug bool) (*Pool, error) {
        typ, ok := vmimpl.Types[cfg.Type]
        if !ok {
            return nil, fmt.Errorf("unknown instance type '%v'", cfg.Type)
        }
        env := &vmimpl.Env{
            Name:      cfg.Name,
            OS:        cfg.TargetOS,
            Arch:      cfg.TargetVMArch,
            Workdir:   cfg.Workdir,
            Image:     cfg.Image,
            SSHKey:    cfg.SSHKey,
            SSHUser:   cfg.SSHUser,
            Timeouts:  cfg.Timeouts,
            Debug:     debug,
            Config:    cfg.VM,
            KernelSrc: cfg.KernelSrc,
        }
        impl, err := typ.Ctor(env)
        if err != nil {
            return nil, err
        }
        return &Pool{
            impl:     impl,
            workdir:  env.Workdir,
            template: cfg.WorkdirTemplate,
            timeouts: cfg.Timeouts,
        }, nil
    }
    

### Step 2. 初始化 Manager，载入语料库，建立通信服务器

随后会创建用于存储 crash 的文件夹与一个新的 Reporter 实例：

    
    
    crashdir := filepath.Join(cfg.Workdir, "crashes")
        osutil.MkdirAll(crashdir)
    
        reporter, err := report.NewReporter(cfg)
        if err != nil {
            log.Fatalf("%v", err)
        }
    

接下来创建一个基本的 Manager 实例，然后是四步走：

  * `preloadCorpus()`：检查 `corpus.db` 文件是否存在（若不存在则创建）并载入 `sys/要fuzz的OS/test` 目录下的测试用模板

> 语料库载入的模板本身类似于 syzlang 文件，例如 `sys/linux/pipe`：
>  
>     >     pipe2(&(0x7f0000000000)={<r0=>0x0, <r1=>0x0}, 0x0)
>     close(r0)
>     close(r1)

  * `initStats()`：注册一个 prometheus 监视器（一个开源的监视&预警工具包）

  * `initHTTP()`：创建一个 HTTP 服务器并注册一系列的目录（用以供使用者访问）

  * `collectUsedFiles()`：检查所需文件是否存在

    
    
    mgr := &Manager{
            cfg:              cfg,
            vmPool:           vmPool,
            target:           cfg.Target,
            sysTarget:        cfg.SysTarget,
            reporter:         reporter,
            crashdir:         crashdir,
            startTime:        time.Now(),
            stats:            &Stats{haveHub: cfg.HubClient != ""},
            crashTypes:       make(map[string]bool),
            corpus:           make(map[string]CorpusItem),
            disabledHashes:   make(map[string]struct{}),
            memoryLeakFrames: make(map[string]bool),
            dataRaceFrames:   make(map[string]bool),
            fresh:            true,
            vmStop:           make(chan bool),
            hubReproQueue:    make(chan *Crash, 10),
            needMoreRepros:   make(chan chan bool),
            reproRequest:     make(chan chan map[string]bool),
            usedFiles:        make(map[string]time.Time),
            saturatedCalls:   make(map[string]bool),
        }
    
        mgr.preloadCorpus()
        mgr.initStats() // 初始化 prometheus 变量.
        mgr.initHTTP()  // 创建 HTTP 服务.
        mgr.collectUsedFiles()
    

之后创建一个 RPC Server，用以在 Host 与 Guest VMs 之间进行通信：

    
    
    // Create 为 fuzzer 创建 PRC 服务器.
        mgr.serv, err = startRPCServer(mgr)
        if err != nil {
            log.Fatalf("failed to create rpc server: %v", err)
        }
    

### _Step 3. 初始化 dashboard 相关_

    
    
    if cfg.DashboardAddr != "" {
            mgr.dash, err = dashapi.New(cfg.DashboardClient, cfg.DashboardAddr, cfg.DashboardKey)
            if err != nil {
                log.Fatalf("failed to create dashapi connection: %v", err)
            }
        }
    
        if !cfg.AssetStorage.IsEmpty() {
            mgr.assetStorage, err = asset.StorageFromConfig(cfg.AssetStorage, mgr.dash)
            if err != nil {
                log.Fatalf("failed to init asset storage: %v", err)
            }
        }
    

### Step 4. 创建【日志输出】协程

接下来会新起一个协程进行数据记录的工作，内部其实就是一个 **每 10s 进行一次进度采集并输出日志的无限循环**
，主要是采集执行信息、语料覆盖率、crashes 信息等：

    
    
    go func() {
            for lastTime := time.Now(); ; {
                time.Sleep(10 * time.Second)
                now := time.Now()
                diff := now.Sub(lastTime)
                lastTime = now
                mgr.mu.Lock()
                if mgr.firstConnect.IsZero() {
                    mgr.mu.Unlock()
                    continue
                }
                mgr.fuzzingTime += diff * time.Duration(atomic.LoadUint32(&mgr.numFuzzing))
                executed := mgr.stats.execTotal.get()
                crashes := mgr.stats.crashes.get()
                corpusCover := mgr.stats.corpusCover.get()
                corpusSignal := mgr.stats.corpusSignal.get()
                maxSignal := mgr.stats.maxSignal.get()
                mgr.mu.Unlock()
                numReproducing := atomic.LoadUint32(&mgr.numReproducing)
                numFuzzing := atomic.LoadUint32(&mgr.numFuzzing)
    
                log.Logf(0, "VMs %v, executed %v, cover %v, signal %v/%v, crashes %v, repro %v",
                    numFuzzing, executed, corpusCover, corpusSignal, maxSignal, crashes, numReproducing)
            }
        }()
    

### Step 5. 创建 bench 协程（每隔一分钟最小化语料库并将 bench data 写入 bench 文件）

这里会判断命令行传入参数是否有 `bench=`，若是则调用 `initBench()`：

    
    
    if *flagBench != "" {
            mgr.initBench()
        }
    

这里的 `flagBench` 是一个全局的 flag 变量，golang 提供了一个 `flag` 包用以处理命令行参数：

    
    
    var (
        flagConfig = flag.String("config", "", "configuration file")
        flagDebug  = flag.Bool("debug", false, "dump all VM output to console")
        flagBench  = flag.String("bench", "", "write execution statistics into this file periodically")
    )
    

`initBench()` 会启动一个协程，主要就是一个每隔一分钟运行一次的循环：

  * 调用 `minimizeCorpus()` 将语料库进行最小化
  * 向 `bench` 参数指定的文件当中写入 `语料库长度、启动时间、fuzzing 时间\n`

    
    
    func (mgr *Manager) initBench() {
        f, err := os.OpenFile(*flagBench, os.O_WRONLY|os.O_CREATE|os.O_EXCL, osutil.DefaultFilePerm)
        if err != nil {
            log.Fatalf("failed to open bench file: %v", err)
        }
        go func() {
            for {
                time.Sleep(time.Minute)
                vals := mgr.stats.all()
                mgr.mu.Lock()
                if mgr.firstConnect.IsZero() {
                    mgr.mu.Unlock()
                    continue
                }
                mgr.minimizeCorpus()
                vals["corpus"] = uint64(len(mgr.corpus))
                vals["uptime"] = uint64(time.Since(mgr.firstConnect)) / 1e9
                vals["fuzzing"] = uint64(mgr.fuzzingTime) / 1e9
                mgr.mu.Unlock()
    
                data, err := json.MarshalIndent(vals, "", "  ")
                if err != nil {
                    log.Fatalf("failed to serialize bench data")
                }
                if _, err := f.Write(append(data, '\n')); err != nil {
                    log.Fatalf("failed to write bench data")
                }
            }
        }()
    }
    

### Step 6. 启动 dashboard 协程，进入下一阶段

接下来会启动一个新的协程，主要是 _每隔一分钟上报一次 syz-manager 的状态，这里不再展开_ ：

    
    
    if mgr.dash != nil {
            go mgr.dashboardReporter()
        }
    

最后会简单检查一下 VM Pool ，随后调用 `vmLoop()` 进入下一阶段：

    
    
    osutil.HandleInterrupts(vm.Shutdown)
        if mgr.vmPool == nil {
            log.Logf(0, "no VMs started (type=none)")
            log.Logf(0, "you are supposed to start syz-fuzzer manually as:")
            log.Logf(0, "syz-fuzzer -manager=manager.ip:%v [other flags as necessary]", mgr.serv.port)
            <-vm.Shutdown
            return
        }
        mgr.vmLoop()
    }
    

# 0x04. vmLoop()：启动 fuzzing，管控整体流程

## 一、VM 分组，初始化资源池等变量

一开始首先会将所有的 VM 分为两组：一组负责 fuzzing，一组负责复现 crash （`maxReproVMs`）：

    
    
    // Manager needs to be refactored (#605).
    // nolint: gocyclo, gocognit, funlen
    func (mgr *Manager) vmLoop() {
        log.Logf(0, "booting test machines...")
        log.Logf(0, "wait for the connection from test machine...")
        instancesPerRepro := 4
        vmCount := mgr.vmPool.Count()
        maxReproVMs := vmCount - mgr.cfg.FuzzingVMs
        if instancesPerRepro > maxReproVMs && maxReproVMs > 0 {
            instancesPerRepro = maxReproVMs
        }
    

随后会调用 `SequentialResourcePool()` 新建一个 `ResourcePool` 队列，主要负责对 **空闲 VM 使用顺序**
的调控 ：

    
    
    instances := SequentialResourcePool(vmCount, 10*time.Second*mgr.cfg.Timeouts.Scale)
    

接下来会初始化一系列的变量：

  * `runDone`：保存 fuzzing 结果为 crash 的 **Crash 队列**
  * `pendingRepro`：标识 **待复现的 Crash**
  * `reproducing`：标识 **某个类型 Crash** 是否准备被复现
  * `reproQueue`：Crash 的复现队列
  * `reproDone`：Crash 的复现结果
  * `stopPending`：等待停止标志位
  * `shutdown`：工作终止标志位

    
    
    runDone := make(chan *RunResult, 1)
        pendingRepro := make(map[*Crash]bool)
        reproducing := make(map[string]bool)
        var reproQueue []*Crash
        reproDone := make(chan *ReproResult, 1)
        stopPending := false
        shutdown := vm.Shutdown
    

最后进入到一个大循环中，这个大循环才是真正的 fuzzing 调控流程

## 二、外层大循环：调配空闲 VM 进行 fuzz & crash repro，等待处理不同 channel 数据

大循环的终止条件为 `shutdown == nil` 或是 ResourcePool 中的 VM 数量与总数量不相等，进入循环后首先会获取当前所在阶段：

    
    
    for shutdown != nil || instances.Len() != vmCount {
            mgr.mu.Lock()
            phase := mgr.phase
            mgr.mu.Unlock()
    

### Step 1. 内层小循环：获取待复现 crash 加入复现队列

小循环会遍历 `pendingRepro` 中的 crash：

  * 若未被复现则从 pendingRepro 中删除
  * 调用 `needRepro()` 检查是否需要复现
  * 标记该标题的 crash 已在复现，并加入复现队列中

这里的 `crash.Title` 其实是 **Oops 的第一行文本，** 即 **同一时刻仅会复现同类 crash 中的一个** ：

    
    
    for crash := range pendingRepro {
                if reproducing[crash.Title] {
                    continue
                }
                delete(pendingRepro, crash)
                if !mgr.needRepro(crash) {
                    continue
                }
                log.Logf(1, "loop: add to repro queue '%v'", crash.Title)
                reproducing[crash.Title] = true
                reproQueue = append(reproQueue, crash)
            }
    

### Step 2. 判断是否可以对 crash 进行复现并调控 VM

接下来会输出一行日志，之后定义一个闭包函数 `canRepro`，用来判断 **当前是否可以进行 crash 复现** ，主要判断以下三个条件是否满足：

  * 当前阶段是否超过 `phaseTriagedHub`
  * 待复现队列 `reproQueue` 是否不为空
  * 加上该 crash 后所有用来复现 crash 的 VM 数量是否小于 `maxReproVMs`

    
    
    log.Logf(1, "loop: phase=%v shutdown=%v instances=%v/%v %+v repro: pending=%v reproducing=%v queued=%v",
                phase, shutdown == nil, instances.Len(), vmCount, instances.Snapshot(),
                len(pendingRepro), len(reproducing), len(reproQueue))
    
            canRepro := func() bool {
                return phase >= phaseTriagedHub && len(reproQueue) != 0 &&
                    (int(atomic.LoadUint32(&mgr.numReproducing))+1)*instancesPerRepro <= maxReproVMs
            }
    

接下来是两个小循环：

#### ① 循环启动协程调度 VM 进行 crash 复现

第一个小循环会循环判断是否可以进行 crash 复现：

  * 若可以复现则从资源池队列中取出一个 VM idx，若资源池为空则直接跳出
  * 从 `reproQueue` 中取出一个 crash，更新 manager 的 `numReproducing` 计数
  * 启动一个新的协程调用 `runRepro()` 对该 crash 进行复现，结果输出至 `reproDone` 队列中

    
    
    if shutdown != nil {
                for canRepro() {
                    vmIndexes := instances.Take(instancesPerRepro)
                    if vmIndexes == nil {
                        break
                    }
                    last := len(reproQueue) - 1
                    crash := reproQueue[last]
                    reproQueue[last] = nil
                    reproQueue = reproQueue[:last]
                    atomic.AddUint32(&mgr.numReproducing, 1)
                    log.Logf(1, "loop: starting repro of '%v' on instances %+v", crash.Title, vmIndexes)
                    go func() {
                        reproDone <- mgr.runRepro(crash, vmIndexes, instances.Put)
                    }()
                }
    

而 `runRepro()` 其实就是 `repro.Run()` 的 wrapper ＋ 一些错误检查后将 VM idx 放回资源池，这里就不展开了：

    
    
    func (mgr *Manager) runRepro(crash *Crash, vmIndexes []int, putInstances func(...int)) *ReproResult {
        features := mgr.checkResult.Features
        res, stats, err := repro.Run(crash.Output, mgr.cfg, features, mgr.reporter, mgr.vmPool, vmIndexes)
        //...
    

`Run()` 一开始主要是一些检查，之后根据 crash 类型的不同设置不同的复现时间上限：

    
    
    func Run(crashLog []byte, cfg *mgrconfig.Config, features *host.Features, reporter *report.Reporter,
        vmPool *vm.Pool, vmIndexes []int) (*Result, *Stats, error) {
        if len(vmIndexes) == 0 {
            return nil, nil, fmt.Errorf("no VMs provided")
        }
        entries := cfg.Target.ParseLog(crashLog)
        if len(entries) == 0 {
            return nil, nil, fmt.Errorf("crash log does not contain any programs")
        }
        crashStart := len(crashLog)
        crashTitle, crashType := "", report.Unknown
        if rep := reporter.Parse(crashLog); rep != nil {
            crashStart = rep.StartPos
            crashTitle = rep.Title
            crashType = rep.Type
        }
        testTimeouts := []time.Duration{
            3 * cfg.Timeouts.Program, // 以捕获更简单的 crashes (即 no races and no hangs)
            20 * cfg.Timeouts.Program,
            cfg.Timeouts.NoOutputRunningTime, // 以捕获 "no output", races and hangs
        }
        switch {
        case crashTitle == "":
            crashTitle = "no output/lost connection"
            // Lost connection 可以被更快地检测到,
            // 但理论上若其由竞争造成，则可能需要最长的 timeout.
            // No output 仅能在最大的 timeout 下被复现.
            // 作为妥协，我们使用最小与最大的 timeouts.
            testTimeouts = []time.Duration{testTimeouts[0], testTimeouts[2]}
        case crashType == report.MemoryLeak:
            // 由于昂贵的设置与扫描，内存泄露不能被很快地检测到.
            testTimeouts = testTimeouts[1:]
        case crashType == report.Hang:
            testTimeouts = testTimeouts[2:]
        }
    

接下来会将崩溃信息存储到一个 `context` 结构体中，并新建一个 WaitGroup：

    
    
    ctx := &context{
            target:       cfg.SysTarget,
            reporter:     reporter,
            crashTitle:   crashTitle,
            crashType:    crashType,
            instances:    make(chan *reproInstance, len(vmIndexes)),
            bootRequests: make(chan int, len(vmIndexes)),
            testTimeouts: testTimeouts,
            startOpts:    createStartOptions(cfg, features, crashType),
            stats:        new(Stats),
            timeouts:     cfg.Timeouts,
        }
        ctx.reproLogf(0, "%v programs, %v VMs, timeouts %v", len(entries), len(vmIndexes), testTimeouts)
        var wg sync.WaitGroup
        wg.Add(len(vmIndexes))
    

随后循环获取用以复现的 VM idx 并依次启动新协程调用 `CreateExecProgInstance()` **创建 VM 并拷贝 crash
程序** ，若失败则休眠 10s 后重试，最多会尝试 `maxTry` 次；成功的结果会输出到 `ctx.instances` 中：

    
    
    for _, vmIndex := range vmIndexes {
            ctx.bootRequests <- vmIndex
            go func() {
                defer wg.Done()
                for vmIndex := range ctx.bootRequests {
                    var inst *instance.ExecProgInstance
                    maxTry := 3
                    for try := 0; try < maxTry; try++ {
                        select {
                        case <-vm.Shutdown:
                            try = maxTry
                            continue
                        default:
                        }
                        var err error
                        inst, err = instance.CreateExecProgInstance(vmPool, vmIndex, cfg,
                            reporter, &instance.OptionalConfig{Logf: ctx.reproLogf})
                        if err != nil {
                            ctx.reproLogf(0, "failed to init instance: %v", err)
                            time.Sleep(10 * time.Second)
                            continue
                        }
                        break
                    }
                    if inst == nil {
                        break
                    }
                    ctx.instances <- &reproInstance{execProg: inst, index: vmIndex}
                }
            }()
        }
        // 一些收尾工作...
        go func() {
            wg.Wait()
            close(ctx.instances)
        }()
        defer func() {
            close(ctx.bootRequests)
            for inst := range ctx.instances {
                inst.execProg.VMInstance.Close()
            }
        }()
    

`CreateExecProgInstance()` 主要就是调用 `vmPool.Create()` 启动虚拟机后调用 `SetupExecProg()`
拷贝要执行的二进制文件，这里就不展开了：

    
    
    func CreateExecProgInstance(vmPool *vm.Pool, vmIndex int, mgrCfg *mgrconfig.Config,
        reporter *report.Reporter, opt *OptionalConfig) (*ExecProgInstance, error) {
        vmInst, err := vmPool.Create(vmIndex)
        if err != nil {
            return nil, fmt.Errorf("failed to create VM: %v", err)
        }
        ret, err := SetupExecProg(vmInst, mgrCfg, reporter, opt)
        if err != nil {
            vmInst.Close()
            return nil, err
        }
        return ret, nil
    }
    

回到 `Run()` 中，其最后会调用 `context.repro()` **正式开始复现 crash 的工作** ，检查结果后返回：

    
    
    res, err := ctx.repro(entries, crashStart)
        if err != nil {
            return nil, nil, err
        }
        if res != nil {
            ctx.reproLogf(3, "repro crashed as (corrupted=%v):\n%s",
                ctx.report.Corrupted, ctx.report.Report)
            // Try to rerun the repro if the report is corrupted.
            for attempts := 0; ctx.report.Corrupted && attempts < 3; attempts++ {
                ctx.reproLogf(3, "report is corrupted, running repro again")
                if res.CRepro {
                    _, err = ctx.testCProg(res.Prog, res.Duration, res.Opts)
                } else {
                    _, err = ctx.testProg(res.Prog, res.Duration, res.Opts)
                }
                if err != nil {
                    return nil, nil, err
                }
            }
            ctx.reproLogf(3, "final repro crashed as (corrupted=%v):\n%s",
                ctx.report.Corrupted, ctx.report.Report)
            res.Report = ctx.report
        }
        return res, ctx.stats, nil
    }
    

`repro()` 函数主要分两部分：

  * 调用 `extractProg()` **获取触发 crash 的程序集合**
    
        func (ctx *context) repro(entries []*prog.LogEntry, crashStart int) (*Result, error) {
      // 去除在 crash 发生后执行的程序.
      for i, ent := range entries {
          if ent.Start > crashStart {
              entries = entries[:i]
              break
          }
      }
    
      reproStart := time.Now()
      defer func() {
          ctx.reproLogf(3, "reproducing took %s", time.Since(reproStart))
      }()
    
      res, err := ctx.extractProg(entries)
      if err != nil {
          return nil, err
      }
      if res == nil {
          return nil, nil
      }
      defer func() {
          if res != nil {
              res.Opts.Repro = false
          }
      }()
    

  * 最小化程序集合并尝试生成可以触发该 crash 的 C 程序，返回结果：
    
        // 尝试最小化程序集
      res, err = ctx.minimizeProg(res)
      if err != nil {
          return nil, err
      }
    
      // 首先尝试在不简化配置的情况下提取 C repro.
      res, err = ctx.extractC(res)
      if err != nil {
          return nil, err
      }
    
      // 简化配置并尝试提取 C repro.
      if !res.CRepro {
          res, err = ctx.simplifyProg(res)
          if err != nil {
              return nil, err
          }
      }
    
      // 简化 C 相关的配置.
      if res.CRepro {
          res, err = ctx.simplifyC(res)
          if err != nil {
              return nil, err
          }
      }
    
      return res, nil
    }
    

`extractProg()` 的逻辑比较简单：

  * 逆序后调用 `context.extractProgSingle()` **逐个运行单个程序** ，若某一程序触发了 crash 则直接返回
  * 若单一程序无法触发 crash，则调用 `context.extractProgBisect()` **使用二分法找出触发 crash 的程序集合**

    
    
    func (ctx *context) extractProg(entries []*prog.LogEntry) (*Result, error) {
        ctx.reproLogf(2, "extracting reproducer from %v programs", len(entries))
        start := time.Now()
        defer func() {
            ctx.stats.ExtractProgTime = time.Since(start)
        }()
    
        // Extract last program on every proc.
        procs := make(map[int]int)
        for i, ent := range entries {
            procs[ent.Proc] = i
        }
        var indices []int
        for _, idx := range procs {
            indices = append(indices, idx)
        }
        sort.Ints(indices)
        var lastEntries []*prog.LogEntry
        for i := len(indices) - 1; i >= 0; i-- {
            lastEntries = append(lastEntries, entries[indices[i]])
        }
        for _, timeout := range ctx.testTimeouts {
            // 分别执行每个程序以检测由单个程序造成的简单的 crash.
            // 程序被逆序执行, 通常最后一个程序就是罪魁祸首.
            res, err := ctx.extractProgSingle(lastEntries, timeout)
            if err != nil {
                return nil, err
            }
            if res != nil {
                ctx.reproLogf(3, "found reproducer with %d syscalls", len(res.Prog.Calls))
                return res, nil
            }
    
            // 若只有一个 entry 则不进行二分.
            if len(entries) == 1 {
                continue
            }
    
            // 执行多个程序并二分 log 以找到造成崩溃的多个程序.
            res, err = ctx.extractProgBisect(entries, timeout)
            if err != nil {
                return nil, err
            }
            if res != nil {
                ctx.reproLogf(3, "found reproducer with %d syscalls", len(res.Prog.Calls))
                return res, nil
            }
        }
    
        ctx.reproLogf(0, "failed to extract reproducer")
        return nil, nil
    }
    

这两个函数主要就是通过如下调用链来在 VM 中执行程序，这里就不展开了：

    
    
    context.testProg()
        context.testProgs()
            context.testWithInstance()
                ExecProgInstance.RunSyzProg()
                    ExecProgInstance.RunSyzProgFile()
                        ExecProgInstance.runCommand()

#### ② 循环启动协程进行 fuzzing

此时已经不满足可以进行 crash 复现的条件了，因而会有第二个小循环启动新协程 **将资源池中剩余 VM 调度去 fuzzing** ， 并将结果输出到
`runDone` 中：

    
    
    for !canRepro() {
                    idx := instances.TakeOne()
                    if idx == nil {
                        break
                    }
                    log.Logf(1, "loop: starting instance %v", *idx)
                    go func() {
                        crash, err := mgr.runInstance(*idx)
                        runDone <- &RunResult{*idx, crash, err}
                    }()
                }
            }
    

`runInstance()` 函数实际上会调用 `runInstanceInner()`，该函数 **仅当产生了 Crash 时返回的结果才不为
nil，即 runRepro 队列实际上为 Crash 队列：**

    
    
    func (mgr *Manager) runInstance(index int) (*Crash, error) {
        mgr.checkUsedFiles()
        instanceName := fmt.Sprintf("vm-%d", index)
    
        rep, vmInfo, err := mgr.runInstanceInner(index, instanceName)
    
        machineInfo := mgr.serv.shutdownInstance(instanceName)
        if len(vmInfo) != 0 {
            machineInfo = append(append(vmInfo, '\n'), machineInfo...)
        }
    
        // Error that is not a VM crash.
        if err != nil {
            return nil, err
        }
        // No crash.
        if rep == nil {
            return nil, nil
        }
        crash := &Crash{
            vmIndex:     index,
            hub:         false,
            Report:      rep,
            machineInfo: machineInfo,
        }
        return crash, nil
    }
    

`runInstanceInner()` 的核心部分主要是：

  * 调用 `vmPool.Create()` 创建 VM，调用 `inst.Forward()` 进行 TCP 转发，拷贝 `syz-fuzzer` 与 `syz-executor` 到 VM 文件系统中
    
        func (mgr *Manager) runInstanceInner(index int, instanceName string) (*report.Report, []byte, error) {
      inst, err := mgr.vmPool.Create(index)
      if err != nil {
          return nil, nil, fmt.Errorf("failed to create instance: %v", err)
      }
      defer inst.Close()
    
      fwdAddr, err := inst.Forward(mgr.serv.port)
      if err != nil {
          return nil, nil, fmt.Errorf("failed to setup port forwarding: %v", err)
      }
    
      fuzzerBin, err := inst.Copy(mgr.cfg.FuzzerBin)
      if err != nil {
          return nil, nil, fmt.Errorf("failed to copy binary: %v", err)
      }
    
      // 若提供了 ExecutorBin , 这意味着 syz-executor 早已在镜像中,
      // 故无需进行拷贝.
      executorBin := mgr.sysTarget.ExecutorBin
      if executorBin == "" {
          executorBin, err = inst.Copy(mgr.cfg.ExecutorBin)
          if err != nil {
              return nil, nil, fmt.Errorf("failed to copy binary: %v", err)
          }
      }
    
      fuzzerV := 0
      procs := mgr.cfg.Procs
      if *flagDebug {
          fuzzerV = 100
          procs = 1
      }
    

  * 调用 `instance.FuzzerCmd()` 生成命令行后调用 `inst.Run()` 启动 `syz-fuzzer`
    
        // Run the fuzzer binary.
      start := time.Now()
      atomic.AddUint32(&mgr.numFuzzing, 1)
      defer atomic.AddUint32(&mgr.numFuzzing, ^uint32(0))
    
      args := &instance.FuzzerCmdArgs{
          Fuzzer:    fuzzerBin,
          Executor:  executorBin,
          Name:      instanceName,
          OS:        mgr.cfg.TargetOS,
          Arch:      mgr.cfg.TargetArch,
          FwdAddr:   fwdAddr,
          Sandbox:   mgr.cfg.Sandbox,
          Procs:     procs,
          Verbosity: fuzzerV,
          Cover:     mgr.cfg.Cover,
          Debug:     *flagDebug,
          Test:      false,
          Runtest:   false,
          Optional: &instance.OptionalFuzzerArgs{
              Slowdown:   mgr.cfg.Timeouts.Slowdown,
              RawCover:   mgr.cfg.RawCover,
              SandboxArg: mgr.cfg.SandboxArg,
          },
      }
      cmd := instance.FuzzerCmd(args)
      outc, errc, err := inst.Run(mgr.cfg.Timeouts.VMRunningTime, mgr.vmStop, cmd)
      if err != nil {
          return nil, nil, fmt.Errorf("failed to run fuzzer: %v", err)
      }
    

  * 调用 `inst.MonitorExecution()` 监控 VM 运行，该函数主要是 **通过获取 kernel oops 来判断是否触发了 crash** （KASAN 不会造成 kernel panic，从而使得一个 VM 实例长期运行，不过 dmesg 中仍有 oops）
    
        var vmInfo []byte
      rep := inst.MonitorExecution(outc, errc, mgr.reporter, vm.ExitTimeout)
      if rep == nil {
          // This is the only "OK" outcome.
          log.Logf(0, "%s: running for %v, restarting", instanceName, time.Since(start))
      } else {
          vmInfo, err = inst.Info()
          if err != nil {
              vmInfo = []byte(fmt.Sprintf("error getting VM info: %v\n", err))
          }
      }
    
      return rep, vmInfo, nil
    }
    

### Step 3. 等待处理不同 channel 数据

`vmLoop()` 的最后主要就是一个大的 `select`，等待某个 channel 中有数据后进行处理，之后重新跳回等待处理或是开始下一轮循环：

    
    
    var stopRequest chan bool
            if !stopPending && canRepro() {
                stopRequest = mgr.vmStop
            }
    
        wait:
            select {
    

首先是资源池的 `Freed` channel，在 `Put()` 中会将空闲 VM idx 放回资源池后向该 channel 送入一个
`true`，而这里什么都没有做，笔者估计会在后续版本中更新：

    
    
    case <-instances.Freed:
                // An instance has been released.
    

`stopRequest` 其实是 `Manager.vmStop` ，这个 channel 会在 VM instance 所实现的 `Run()`
方法中被使用：

    
    
    case stopRequest <- true:
                log.Logf(1, "loop: issued stop request")
                stopPending = true
    

当 `runDone` 中有数据时说明 **fuzz 产生了 crash** ，此时会将产生 crash 的 VM 释放回资源池，将 crash 写入
`pendingRepro` 表中等待下一轮循环进行处理：

    
    
    case res := <-runDone:
                log.Logf(1, "loop: instance %v finished, crash=%v", res.idx, res.crash != nil)
                if res.err != nil && shutdown != nil {
                    log.Logf(0, "%v", res.err)
                }
                stopPending = false
                instances.Put(res.idx)
                // On shutdown qemu crashes with "qemu: terminating on signal 2",
                // which we detect as "lost connection". Don't save that as crash.
                if shutdown != nil && res.crash != nil {
                    needRepro := mgr.saveCrash(res.crash)
                    if needRepro {
                        log.Logf(1, "loop: add pending repro for '%v'", res.crash.Title)
                        pendingRepro[res.crash] = true
                    }
                }
    

`reproDone` 中为 crash 的复现结果，这里会保存复现结果并将对应的 crash 从 `reproducing` 表中删除

    
    
    case res := <-reproDone:
                atomic.AddUint32(&mgr.numReproducing, ^uint32(0))
                crepro := false
                title := ""
                if res.repro != nil {
                    crepro = res.repro.CRepro
                    title = res.repro.Report.Title
                }
                log.Logf(1, "loop: repro on %+v finished '%v', repro=%v crepro=%v desc='%v'",
                    res.instances, res.report0.Title, res.repro != nil, crepro, title)
                if res.err != nil {
                    log.Logf(0, "repro failed: %v", res.err)
                }
                delete(reproducing, res.report0.Title)
                if res.repro == nil {
                    if !res.hub {
                        mgr.saveFailedRepro(res.report0, res.stats)
                    }
                } else {
                    mgr.saveRepro(res)
                }
    

`shutdown` 中有数据则表示收到了终止信号，此时会将 `shutdown` 置为 nil，终止循环：

    
    
    case <-shutdown:
                log.Logf(1, "loop: shutting down...")
                shutdown = nil
    

`hubReproQueue` 上也可能传来 crash，此处将其送入 `pendingRepro` 表中等待在后续循环中复现：

    
    
    case crash := <-mgr.hubReproQueue:
                log.Logf(1, "loop: get repro from hub")
                pendingRepro[crash] = true
    

`needMoreRepros` 是一个传输 channel 的 channel，这里会将一个条件判断结果传入传来的 channel 中并重新跳回等待：

    
    
    case reply := <-mgr.needMoreRepros:
                reply <- phase >= phaseTriagedHub &&
                    len(reproQueue)+len(pendingRepro)+len(reproducing) == 0
                goto wait
    

最后是 `reproRequest`，该 channel 意为 **主动进行复现的请求** ，这里会拷贝 `reproducing` 位图后将其传入传来的
channel 中：

    
    
    case reply := <-mgr.reproRequest:
                repros := make(map[string]bool)
                for title := range reproducing {
                    repros[title] = true
                }
                reply <- repros
                goto wait
            }
        }
    }
    

至此，`syz-manager` 的基本运行逻辑分析完毕


# 前言

本文使用代码片段的形式来解释在 `go`语言开发中经常遇到的小功能点，由于本人主要使用 `java`开发，因此会与其作比较，希望对大家有所帮助。

## 1\. hello world

新手村的第一课，毋庸置疑。

    
    
    package main
    
    import "fmt"
    
    func main() {
    	fmt.Printf("hello world")
    }
    

## 2\. 隐形初始化

    
    
    package main
    
    import "fmt"
    
    func main() {
    	load()
    }
    
    func load() {
    	fmt.Printf("初始化..手动%s 不错\n", "1")
    }
    
    func init() {
    	fmt.Printf("隐形初始化。。\n")
    }
    

在 go 中定义 `init`函数，程序在运行时会自动执行。类似使 `junit`的
`[@before](https://my.oschina.net/u/3870904)`注解。

## 3\. 多模块的访问

`java`中 `package`包的概念，`go`是通过文件夹 + `package`关键字来定义的。

一般而言，我们会通过 `go init`来创建项目，生成的 `go.mod`文件位于根目录。

常见的实践是，创建文件夹并且保持 package 名称与文件夹保持一致。这样 `import`的永远是文件夹，遵循以上规则则意味着文件夹的名称即为模块名。

同一个 `package`可以创建多个 `.go`文件，虽然分布在不同的文件中。但是他们中的方法名称不能相同。需要注意，这里与
`java`中不同类中方法可以重名不同。

此外，也没有诸如 `private、protected、public`等包访问权限关键字。只要定义的函数首字母为大写。则可以被外部成功调用。

来看一下示例：

    
    
    go-tour
    └── ch3
        ├── model
        │   └── test
        │   │   ├── testNest.go
        │   └── helper.go
        │   └── helper2.go
        │  
        └── main.go           
        └── go.mod
    

此处，`ch3、model、test`均为文件夹，也可以说是 `package`。`helper.go`位于 `model`下，它的代码如下：

    
    
    package model
    
    import "fmt"
    
    var AppName = "bot"
    var appVersion = "1.0.0"
    
    func Say() {
    	fmt.Printf("%s", "hello")
    }
    
    func init() {
    	fmt.Printf("%s,%s", AppName, appVersion)
    }
    

再来看看 `main.go`

    
    
    package main
    
    import (
    	"ch3/model"
    	"ch3/model/test"
    )
    
    func main() {
    	model.Say()
    }
    

显然它的调用是通过 `packageName.MethodName()`来使用的。需要注意的是，一个 `go.mod`下只能有一个 `main`包。

## 4\. 引用外部库

和 `java`的 `maven`类似，`go`几经波折也提供了官方仓库。如下，通过 `go get
github.com/satori/go.uuid`命令即可安装 `uuid`库，未指定版本，因此下载的为最新版本。

使用时是这样的：

    
    
    package main
    
    import (
    	"fmt"
    	uuid "github.com/satori/go.uuid"
    )
    
    func main() {
    
    	uuid := uuid.NewV4()
    	fmt.Printf("%s", uuid)
    }
    

## 5\. 数组字典和循环

直接看代码就是了。

    
    
    package main
    
    import "fmt"
    
    var item []int
    var m = map[int]int{
    	100: 1000,
    }
    var m2 = make(map[int]int)
    
    func main() {
    
    	for i := 0; i < 10; i++ {
    		item = append(item, i)
    		m[i] = i
    		m2[i] = i
    	}
    
    	for i := range item {
    		fmt.Printf("item vlaue=%d\n", i)
    	}
    
    	for key, value := range m {
    		fmt.Printf("m:key=%d,value=%d\n", key, value)
    	}
    
    	for _, value := range m2 {
    		fmt.Printf("m2:value=%d\n", value)
    	}
    }
    

  * := 的形式只能在方法内
  * 全局的只能用 var x=..
  * map 输出没有顺序

## 6\. 结构体和 JSON

`go`中通过 `struct`来定义结构体，你可以把它简单理解为对象。一般长这样。

    
    
    type App struct {
    	AppName    string
    	AppVersion string `json:"app_version"`
    	appAuthor  string "pleuvoir"
    	DefaultD   string "default"
    }
    

我们经常在 `java`程序中使用 `fastjson`来输出 `JSON字符串`。 `go`中自带了这样的类库。

    
    
    package main
    
    import (
    	app2 "app/app" //可以定义别名
    	"encoding/json"
    	"fmt"
    )
    
    func main() {
    
    	a := app2.App{}
    	fmt.Printf("%s\n", a)
    
    	app := app2.App{AppName: "bot", AppVersion: "1.0.1"}
    
    	json, _ := json.Marshal(app) //转换为字符串
    
    	fmt.Printf("json is %s\n", json)
    }
    

  * 结构体中 `JSON`序列化不会转变大小写，可以指定它输出的 `key`名称通过 json:xxx 的描述标签。
  * 结构体中的默认值赋值了也不展示

## 7\. 异常处理

作为一个有经验的程序员：），`go`的异常处理涉及的很简单，也往往为人所诟病。比如满屏幕的 `err`使用。

    
    
    package main
    
    import (
    	"fmt"
    	"os"
    )
    
    func _readFile() (int, error) {
    	file, err := os.ReadFile("test.txt")
    	if err != nil {
    		fmt.Printf("error is = %s\n", err)
    		return 0, err
    	}
    	fmt.Printf("file = %s \n", file)
    	return len(file), err
    }
    
    func readFile() (int, error) {
    	fileLength, err := _readFile()
    	if err != nil {
    		fmt.Printf("异常，存在错误 %s\n", err)
    	}
    	return fileLength, err
    }
    
    func main() {
    	fileLength, _ := readFile()
    	fmt.Printf("%d\n", fileLength)
    
    }
    

和 `java`不同，它支持多返回值，为我们的使用带来了很多便利。如果不需要处理这个异常，可以使用 `_`忽略。

## 8\. 异步

千呼万唤始出来，令人兴奋的异步。

    
    
    package main
    
    import (
    	"bufio"
    	"fmt"
    	"os"
    )
    
    func worker() {
    	for i := 0; i < 10; i++ {
    		fmt.Printf("i=%d\n", i)
    	}
    }
    func main() {
    
    	go worker()
    	go worker()
    
    	//阻塞 获取控制台的输出
    	reader := bufio.NewReader(os.Stdin)
    	read, err := reader.ReadBytes('\n') //注意是单引号 回车后结束控制台输出
    	if err != nil {
    		fmt.Printf("err is =%s\n", err)
    		return
    	}
    	fmt.Printf("read is %s \n", read)
    }
    

如此的优雅，如此的简单。只需要一个关键字 `go`便可以启动一个协程。我们在 `java`中经常使用的是线程池，而在
`go`中也存在协程池。据我观察，部分协程池 `benchmark`的性能确实比官方语言关键字高很多。

## 9\. 异步等待

这里就类似 `java`中使用 `countdownLatch`等关键字空值并发编程中程序的等待问题。

    
    
    package main
    
    import (
    	"fmt"
    	"sync"
    	"time"
    )
    
    func upload(waitGroup *sync.WaitGroup) {
    	for i := 0; i < 5; i++ {
    		fmt.Printf("正在上传 i=%d \n", i)
    	}
    	time.Sleep(5 * time.Second)
    	waitGroup.Done()
    }
    
    func saveToDb() {
    	fmt.Printf("保存到数据库中\n")
    	time.Sleep(3 * time.Second)
    }
    
    func main() {
    
    	begin := time.Now()
    	fmt.Printf("程序开始 %s \n", begin.Format(time.RFC850))
    
    	waitGroup := sync.WaitGroup{}
    	waitGroup.Add(1)
    
    	go upload(&waitGroup)
    	go saveToDb()
    	waitGroup.Wait()
    
    	fmt.Printf("程序结束 耗时 %d ms ", time.Now().UnixMilli()-begin.UnixMilli())
    }
    

`sync`包类似于 `J.U.C`包，里面可以找到很多并发编程的工具类。`sync.WaitGroup`便可以简简单单认为是
`countdownLatch`吧。也不能多次调用变为负数，否则会报错。

注意，这里需要传入指针，因为它不是一个引用类型。一定要通过指针传值，不然进程会进入死锁状态。

## 10\. 管道

    
    
    package main
    
    import (
    	"fmt"
    	"sync"
    )
    
    var ch = make(chan int)
    var sum = 0 //是线程安全的
    
    func consumer(wg *sync.WaitGroup) {
    	for {
    		select {
    		case num, ok := <-ch:
    			if !ok {
    				wg.Done()
    				return
    			}
    			sum = sum + num
    		}
    	}
    }
    
    func producer() {
    	for i := 0; i < 10_0000; i++ {
    		ch <- i
    	}
    	close(ch) //如果不关闭则会死锁
    }
    
    func main() {
    
    	wg := sync.WaitGroup{}
    	wg.Add(1)
    	go producer()
    	go consumer(&wg)
    
    	wg.Wait()
    	fmt.Printf("sum = %d \n", sum)
    }
    

这里演示的是什么呢？管道类似一个队列，进行线程间数据的传递。当关闭时消费端也退出，如果没关闭管道，运行时会报死锁。可以看出全局变量在线程间是安全的。

可以衍生出一种固定写法：

    
    
    //固定写法
    func consumer(wg *sync.WaitGroup) {
    	for {
    		select {
    		case num, ok := <-ch:
    			if !ok {
    				wg.Done()
    				return
    			}
    			sum = sum + num
    		}
    	}
    }
    

## 11\. 接口

    
    
    package main
    
    import "fmt"
    
    type Person interface {
    	Say()
    	SetName(name string)
    }
    
    type ZhangSan struct {
    	Value string
    }
    
    func (z *ZhangSan) Say() {
    	fmt.Printf("name=%s", z.Value)
    }
    
    func (z *ZhangSan) SetName(name string) {
    	z.Value = name + ":hehe"
    }
    
    func main() {
    	zhangSan := ZhangSan{}
    	zhangSan.SetName("pleuvoir")
    	zhangSan.Say()
    }
    

如上的程序演示了接口的使用。

  * go 的接口没有强依赖
  * 通过结构体 + 方法的形式实现，注意方法传入的可以是引用也可以是值

## 12\. 锁

    
    
    package main
    
    import (
    	"fmt"
    	"sync"
    )
    
    type Number struct {
    	Value int
    	mutex sync.Mutex //加锁
    }
    
    func (receiver *Number) Add() {
    	receiver.mutex.Lock()
    	defer receiver.mutex.Unlock() //退出时会执行
    	receiver.Value = receiver.Value + 1
    	//fmt.Printf("add\n")
    }
    
    func (receiver *Number) Get() int {
    	receiver.mutex.Lock()
    	defer receiver.mutex.Unlock()
    	return receiver.Value
    }
    
    func main() {
    	number := Number{Value: 0}
    
    	wg := sync.WaitGroup{}
    
    	n := 100_0000
    	wg.Add(n)
    
    	for i := 0; i < n; i++ {
    		go func(wg *sync.WaitGroup) {
    			number.Add()
    			wg.Done()
    		}(&wg)
    	}
    
    	wg.Wait()
    	fmt.Printf("count=%d", number.Get())
    }
    

这里是什么？显然就像是显示锁的 `ReentrantLock`的使用，相信大家都能看懂。这里出现了新关键字 `defer`，我暂且是理解为
`finally`。不知道你怎么看？

## 13\. 读写配置文件

这也是一个很常规的功能，看看怎么实现。

    
    
    package main
    
    import (
    	"encoding/json"
    	"fmt"
    	"os"
    )
    
    type Preferences struct {
    	Name    string  `json:"name"`
    	Version float64 `json:"version"`
    }
    
    const configPath = "config.json"
    
    func main() {
    
    	preferences := Preferences{Name: "app", Version: 100.01}
    	marshal, err := json.Marshal(preferences)
    
    	err = os.WriteFile(configPath, marshal, 777)
    	if err != nil {
    		fmt.Printf("写入配置文件错误，%s\n", err)
    		return
    	}
    
    	//读取配置文件
    	file, err := os.ReadFile(configPath)
    	if err != nil {
    		fmt.Printf("读取文件错误，%s\n", err)
    		return
    	}
    	fmt.Printf("%s\n", file) //{"name":"app","version":100.01}
    
    	//构建一个对象用来序列化
    	readConfig := Preferences{}
    
    	//反序列化
    	err = json.Unmarshal(file, &readConfig)
    	if err != nil {
    		fmt.Printf("配置文件转换为JSON错误，%s\n", err)
    	}
    
    	fmt.Printf("%v", readConfig) //{app 100.01}
    

这里挺没意思的，写入 `JSON`字符串，然后读取回来在加载到内存中。不过，简单的示例也够说明问题了。

## 14\. 宕机处理

这是类似于一种最上层异常捕获的机制，在程序的入口处捕获所有的异常。

    
    
    package main
    
    import (
    	"fmt"
    	"time"
    )
    
    func worker() {
    	//defer func() {  //不能写在主函数，最外层catch没啥用
    	//	if err := recover(); err != nil {
    	//		fmt.Printf("%s", err)
    	//	}
    	//}()
    	defer recovery()
    	panic("严重错误")
    }
    
    func recovery() {
    	if err := recover(); err != nil {
    		fmt.Printf("死机了。%s\n", err)
    	}
    }
    
    func main() {
    	for true {
    		worker()
    		time.Sleep(1 * time.Second)
    	}
    }
    

注释写的很清楚，聪明的你一看就懂。

## 15\. 单元测试

与 `java`不同，`go`建议单元测试文件尽可能的离源代码文件近一些。比如这样：

    
    
    go-tour
        └── main.go      
        └── main_test.go  
    

并且它的命名也是这样简单粗暴：

    
    
    package main
    
    import (
    	"testing"
    )
    
    func TestInit(t *testing.T) {
    	t.Log("heh")
    
    	helper := PersonHelper{}
    	helper.init("pleuvoir")
    	t.Log(helper.Name)
    }
    

以大写的 `Test`开头，文件名称以 `_test`结尾，很清爽的感觉。

## 16\. 启动传参

这也是一个很常用的知识点。这里有两种方式：

  * 直接传
  * 使用 flag

    
    
    package main
    
    import (
    	"encoding/json"
    	"flag"
    	"fmt"
    	"os"
    )
    
    func main() {
    
    	//第一种方式
    	args := os.Args
    
    	for i, arg := range args {
    		println(i, arg)
    	}
    
    	//第二种方式
    	config := struct {
    		Debug bool
    		Port  int
    	}{}
    
    	flag.BoolVar(&config.Debug, "debug", true, "是否开启debug模式")
    	flag.IntVar(&config.Port, "port", 80, "端口")
    
    	flag.Parse()
    
    	json, _ := json.Marshal(config)
    
    	fmt.Printf("json is %s\n", json)
    }
    

我建议使用第二种，更便捷自带类型转换，还可以给默认值，非常好。

## 17\. 优雅退出

    
    
    package main
    
    import (
    	"fmt"
    	"os"
    	"os/signal"
    	"syscall"
    )
    
    func quit() {
    	println("执行一些清理工作。。")
    }
    
    //正常的退出
    //终端 CTRL+C退出
    //异常退出
    
    func main() {
    
    	defer quit()
    	println("进来了")
    
    	//读取信号，没有一直会阻塞住
    	exitChan := make(chan os.Signal)
    
    	//监听信号
    	signals := make(chan os.Signal)
    	signal.Notify(signals, syscall.SIGINT, syscall.SIGQUIT)
    
    	go func() {
    		//有可能一次接收到多个
    		for s := range signals {
    			switch s {
    			case syscall.SIGINT, syscall.SIGQUIT:
    				println("\n监听到操作系统信号。。")
    				quit() //如果监听到这个信号没处理，那么程序就不会退出了
    				if i, ok := s.(syscall.Signal); ok {
    					value := int(i)
    					fmt.Printf("是信号类型，准备退出 %d", value)
    				} else {
    					println("不知道是啥，0退出")
    					os.Exit(0)
    				}
    				//	os.Exit(value)
    				exitChan <- s
    			}
    		}
    	}()
    
    	println("\n程序在这里被阻塞了。")
    	<-exitChan
    	//panic("heh")
    	println("\n阻塞被终止了。")
    }
    

这其实是在监听操作系统的信号，`java`中也有类似的回调的接口（我忘了名字）。

## 18\. 反射

作为一门高级语言，反射肯定是有的。还是使用 `reflect`包。

    
    
    package main
    
    import (
    	"fmt"
    	"reflect"
    )
    
    type Person struct {
    	Name string `json:"name"`
    }
    
    func (p *Person) SetName(name string) {
    	p.Name = name
    }
    
    func (p *Person) GetName() (string, string) {
    	return p.Name, "1.0.1"
    }
    
    func worker1() {
    	p := Person{}
    	p.SetName("pleuvoir")
    	name, _ := p.GetName()
    	fmt.Printf(name)
    }
    
    // 获取方法
    func worker2() {
    	p := Person{}
    	rv := reflect.ValueOf(&p)
    	value := []reflect.Value{reflect.ValueOf("peluvoir")}
    	rv.MethodByName("SetName").Call(value)
    	values := rv.MethodByName("GetName").Call(nil)
    	for i, v := range values {
    		fmt.Printf("\ni=%d,value=%s\n", i, v)
    	}
    }
    
    func worker3() {
    	s := Person{}
    	rt := reflect.TypeOf(s)
    	if field, ok := rt.FieldByName("Name"); ok {
    		tag := field.Tag.Get("json")
    		fmt.Printf("tag is %s \n", tag)
    	}
    }
    
    func main() {
    	//正常获取
    	worker1()
    	//获取方法
    	worker2()
    	//获取标签
    	worker3()
    }
    

没什么好说的，写代码全靠猜。

## 19\. atomic

类似 `java`中的 `atomic`原子变量。

    
    
    package main
    
    import (
    	"fmt"
    	"sync"
    	"sync/atomic"
    )
    
    func main() {
    
    	workers := 1000
    
    	wg := sync.WaitGroup{}
    	wg.Add(workers)
    	for i := 0; i < workers; i++ {
    		go worker2(&wg)
    	}
    	wg.Wait()
    
    	fmt.Printf("count = %d", count)
    }
    
    var count int64 = 0
    
    func worker1(wg *sync.WaitGroup) {
    	count++
    	wg.Done()
    }
    
    func worker2(wg *sync.WaitGroup) {
    	atomic.AddInt64(&count, 1) //特别简单
    	wg.Done()
    }
    

真的是特别简单。

## 20\. 线程安全的 Map

类似于 `ConcurrentHashMap`，与普通的 `api`有所不同。

    
    
    var sessions = sync.Map{}
    sessions.Store(uuid, uuid)
    load, ok := sessions.Load(value.Token)
    		if ok {
    			// 做你想做的事情
    		}
    

## 21\. return func

这里就是函数式变成的例子了。函数是一等公民可以作为参数随意传递。`java`什么时候能支持呢？

    
    
    package main
    
    import "fmt"
    
    func main() {
    	engine := Engine{}
    	engine.Function = regular()
    
    	function := engine.Function
    
    	for i := 0; i < 3; i++ {
    		s := function("pleuvoir")
    		fmt.Printf("s is %s\n", s)
    	}
    
    }
    
    type Engine struct {
    	Function func(name string) string
    }
    
    func regular() (ret func(name string) string) {
    	fmt.Printf("初始化一些东西。\n")
    	return func(name string) string {
    		fmt.Printf("我是worker。name is %s\n", name)
    		return "我是匿名函数的返回值"
    	}
    }
    

比如这里，如果要初始化日志什么。最后需要让框架在哪里打印日志，就需要将这个初始化的日志实例传递过去。总而言之，言而总之。会需要让代码各种传递。

这种方式在于第一次调用的时候会执行上面的代码片段，后面只是保存了这个函数的句柄，然后可以一直调用这个匿名函数。

## 22\. context

    
    
    package main
    
    import (
    	"context"
    	"fmt"
    	"time"
    )
    
    func main() {
    	worker1()
    }
    
    func worker1() {
    
    	//总共2秒超时
    	value := context.WithValue(context.Background(), "token", "pleuvoir")
    	timeout, cancelFunc := context.WithTimeout(value, 5*time.Second)
    	defer cancelFunc()
    
    	//模拟任务
    	fmt.Println("开始任务")
    	deep := 10
    	go handler(timeout, deep)
    
    	fmt.Println("开始阻塞", time.Now())
    	//等待主线程超时，阻塞操作
    	select {
    	case <-timeout.Done():
    		fmt.Println("阻塞结束", timeout.Err(), time.Now())
    	}
    
    }
    
    // 模拟任务处理，循环下载图片等
    func handler(timeout context.Context, deep int) {
    
    	if deep > 0 {
    		fmt.Printf("[begin]token is %s %s deep=%d\n", timeout.Value("token"), time.Now(), deep)
    		time.Sleep(1 * time.Second)
    		go handler(timeout, deep-1)
    	}
    
    	//下面的哪个先返回 先执行哪个
    	//如果整体超时 或者 当前方法超过2秒 就结束
    	select {
    
    	//等待超时会返回
    	case <-timeout.Done():
    		fmt.Println("超时了。", timeout.Err())
    		//等待这么久 然后会返回 这个函数可不是比较时间，这里其实是在模拟处理任务，固定执行一秒 和休息一秒效果一样
    		//但是休息一秒的话就不会实时返回了，所以这里实际应用可以是一个带超时的回调？
    	case <-time.After(time.Second):
    		fmt.Printf("[ end ]执行完成耗时一秒     %s %d\n", time.Now(), deep)
    	}
    }
    

作用：在不同的协程中传递上下文。

  * 传值 类似于 threadLocal
  * 可以使用超时机制，无论往下传递了多少协程，只要最上层时间到了 后面的都不执行
  * 俄罗斯套娃一次一层包装

## 23\. 字符串处理

这是最高频率的操作了，使用任何语言都无法错过。

    
    
    package main
    
    import (
    	"fmt"
    	"strings"
    )
    
    func main() {
    
    	str := " pleuvoir  "
    
    	trimSpace := strings.TrimSpace(str)
    
    	fmt.Printf("去除空格 %s\n", trimSpace)
    
    	subString := trimSpace[4:len(trimSpace)]
    	fmt.Printf("subString after is %s\n", subString)
    
    	prefix := strings.HasPrefix(subString, "vo")
    	fmt.Printf("是否有前缀 vo : %v\n", prefix)
    
    	suffix := strings.HasSuffix(subString, "ir")
    	fmt.Printf("是否有后缀 ir : %v\n", suffix)
    
    	builder := strings.Builder{}
    	builder.WriteString("hello")
    	builder.WriteString(" ")
    	builder.WriteString("world")
    
    	fmt.Printf("stringBuilder append is %s\n", builder.String())
    
    	eles := []string{"1", "2"}
    
    	join := strings.Join(eles, "@")
    	fmt.Printf("join after is %s\n", join)
    
    	//拼接格式化字符串，并且能返回
    	sprintf := fmt.Sprintf("%s@%s", "1", "20")
    	fmt.Printf("Sprintf after is %s\n", sprintf)
    
    	//打印一个对象 比较清晰的方式
    	person := struct {
    		Name string
    		Age  int
    	}{"pleuvoir", 18}
    	fmt.Printf("%v", person) // 输出 {Name:pleuvoir Age:18}
    }
    

主要是使用 `fmt`包。

## 24\. 任务投递

如果说使用 `go`最激动人心的是什么？是大量的协程。如果在下载任务中，我们可以启动很多协程进行分片下载。如下，即展示使用多路复用高速下载。

    
    
    package main
    
    import (
    	"fmt"
    	"sync"
    	"time"
    )
    
    func main() {
    
    	chunks := 10 //文件分成n份
    	workers := 5 //个线程处理
    
    	wg := sync.WaitGroup{}
    	wg.Add(chunks)
    
    	jobs := make(chan int, chunks) //带缓冲的管道 等于任务数
    
    	for i := 0; i < workers; i++ {
    		go handler1(i, jobs, &wg)
    	}
    
    	//将任务全部投递给worker
    	scheduler(jobs, chunks)
    
    	wg.Wait()
    
    	fmt.Println("download finished .")
    }
    
    // 分成 chunks 份任务 里分发
    // 将 n 份下载任务都到管道中去，这里管道数量等于 任务数量n 管道不会阻塞
    func scheduler(jobs chan int, chunks int) {
    	for i := 0; i < chunks; i++ {
    		//time.Sleep(time.Duration(rand.Intn(3)) * time.Second)
    		jobs <- i
    	}
    }
    
    // 写法2
    // 注意这里的是直接接受管道，这也是一种固定写法，下面的 range jobs 可以认为是阻塞去抢这个任务，多个线程都在抢任务
    func handler2(workerId int, jobs <-chan int, wg *sync.WaitGroup) {
    	for job := range jobs {
    		//	fmt.Printf("workerId[%d] job[%d] start download .\n", workerId, job)
    		time.Sleep(1 * time.Second)
    		fmt.Printf("workerId[%d] job[%d] download ok.\n", workerId, job)
    		wg.Done() //这里不要break，这样执行完当前的线程就能继续抢了
    	}
    }
    
    // 写法1，select case 多路复用
    func handler1(workerId int, jobs chan int, wg *sync.WaitGroup) {
    	for {
    		select {
    		case job, _ := <-jobs:
    			//	fmt.Printf("workerId[%d] job[%d] start download .\n", workerId, job)
    			time.Sleep(3 * time.Second)
    			fmt.Printf("workerId[%d] job[%d] download ok.\n", workerId, job)
    			wg.Done() //这里不要break，这样执行完当前的线程就能继续抢了
    		}
    	}
    }
    

# 后语

以上都是一个新手 `Gopher`的经验总结，文中难免有错误，恳请指正。

> 作者：京东零售 付伟
>
> 来源：京东与开发者社区


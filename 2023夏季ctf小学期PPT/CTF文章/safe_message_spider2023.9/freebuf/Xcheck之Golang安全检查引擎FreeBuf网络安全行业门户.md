![1615801192_604f2b68d48b14ed51af4.png!small?1615801193273](https://image.3001.net/images/20210315/1615801192_604f2b68d48b14ed51af4.png!small?1615801193273)

## Golang安全检查引擎

Go语言近几年开始越来越流行，凭借其强大的性能和跨平台的优势，对web和后台开发都是一个不错的选择。Xcheck支持Golang的代码安全检查，覆盖常用web框架，包括golang内建的net/http，以及一些流行的第三方web框架：gin，iris，mux，httprouter，fasthttp，fasthttprouter等。自然，也可以通过Xcheck的扩展能力，来适配其他框架。目前覆盖的Web漏洞类型包括但不限于以下：

  * 命令注入
  * SQL注入
  * URL跳转
  * 路径穿越
  * SSRF
  * ...

## 检测数据

我们在github上面选取了10000个golang项目进行安全检查，发现其中存在风险的项目182个，风险数317个，误报数19个，整体误报率6%左右。

![1615801244_604f2b9c1c903e2b83cd6.png!small?1615801244396](https://image.3001.net/images/20210315/1615801244_604f2b9c1c903e2b83cd6.png!small?1615801244396)

![1615801266_604f2bb2808202d85d988.png!small?1615801266789](https://image.3001.net/images/20210315/1615801266_604f2bb2808202d85d988.png!small?1615801266789)

使用Xcheck扫描内部golang项目19w次任务，其中耗时小于1分钟的项目占18万个，换句话说，90%以上的项目都在1分钟内扫描完毕。

## 检测案例

### SQL注入漏洞

![1615801312_604f2be0413df32c20aab.png!small?1615801312522](https://image.3001.net/images/20210315/1615801312_604f2be0413df32c20aab.png!small?1615801312522)

这是整理的部分golang进行sql查询时不正确地使用方式会引发风险的函数。

package| 函数  
---|---  
database/sql| `Query,QueryRow,QueryContext,QueryRowContext`  
gorm| `Exec,Raw,Select,Where`  
xorm| `Query,QueryString,SQL,Where`  
  
以国外安全团队NemoSecurity在github的一个golang靶场项目GoVWA(https://github.com/0c34/govwa.git)为例：

![1615801380_604f2c244ac7219405dd3.png!small?1615801380540](https://image.3001.net/images/20210315/1615801380_604f2c244ac7219405dd3.png!small?1615801380540)

靶场中共存在两个sql注入漏洞，以其中一个为例，触发漏洞的所用的package为`database/sql`。数据流分析如下：

  1. /vulnerability/sqli/sqli.go 72行 引入污点：`uid := r.FormValue("uid")`
  2. /vulnerability/sqli/sqli.go 74行 获取一个profile的实例p：`p := NewProfile()`
  3. /vulnerability/sqli/sqli.go 79行 调用p的方法UnsafeQueryGetData: `err := p.UnsafeQueryGetData(uid)`
  4. /vulnerability/sqli/function.go 37行 拼接sql语句
  5. /vulnerability/sqli/function.go 41行 将拼接的sql参数进行查询。

![1615801526_604f2cb6e0394c46f5793.png!small](https://image.3001.net/images/20210315/1615801526_604f2cb6e0394c46f5793.png!small)

![1615801433_604f2c5994037bfa53b83.png!small?1615801434298](https://image.3001.net/images/20210315/1615801433_604f2c5994037bfa53b83.png!small?1615801434298)

这里我们也使用了github开源高星项目的gosec代码扫描工具进行检测，很遗憾，工具报错了未能得到结果。

### 命令注入

![1615801557_604f2cd56dbb401eef75d.png!small?1615801557697](https://image.3001.net/images/20210315/1615801557_604f2cd56dbb401eef75d.png!small?1615801557697)

对于命令注入，Golang引擎原生支持识别os/exec相关的函数和结构体，包括exec.Command，exec.CommandContext以及相关实际执行函数CombinedOutput/Output/Run/Start。

package| 执行函数  
---|---  
os/exec| `CombinedOutput,Output,Run,Start`  
  
举一个实际项目的案例，图中317行是一个污点，318行是一个Cmd的实例，339行才是真实执行。值得注意的是，如果没有执行Start函数（319行），是不会报漏洞的。

![1615801582_604f2cee4565672588326.png!small?1615801582673](https://image.3001.net/images/20210315/1615801582_604f2cee4565672588326.png!small?1615801582673)

### URL跳转和SSRF

对于扫描引擎来说，这两类漏洞的检测除了支持一些相关触发函数的识别外，难点在于对url字符串的精确判断和分析，如果能做到这个效果，就能降低一些误报。

来看一个SSRF案例，Xcheck识别出这是一个SSRF问题，但是在最后的触发点，“过滤”字段提示这个url的host部分不可控制，其实无法造成危害，对于这种无法被利用的风险，Xcheck给出的漏洞级别是“提示（可忽略）”，这也是Xcheck精准识别的一个体现。

![1615801608_604f2d08bb6305031311c.png!small?1615801609042](https://image.3001.net/images/20210315/1615801608_604f2d08bb6305031311c.png!small?1615801609042)

专注于代码安全 | 公众号：腾讯代码安全检查Xcheck


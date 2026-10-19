**fireELF是一个开源的跨平台无文件Linux恶意代码框架，它允许用户轻松的创建和管理payloads。默认情况下附带了'memfd_create'，这是一种从内存中完全运行linux
elf可执行文件的新方法。**

## 截图

![fireELF：无文件Linux恶意代码框架](https://image.3001.net/images/20190429/1556494771_5cc639b37f6c6.png!small)![fireELF：无文件Linux恶意代码框架](https://image.3001.net/images/20190429/1556494771_5cc639b381877.png!small)

## 特性

> 选择并构建payloads
>
> 能够缩小payloads
>
> 能够通过将payloads上传到pastebin来缩小payloads，然后创建一个与python <= 2.7兼容的非常小的stager
>
> 输出已创建的payloads到文件
>
> 能够从URL或本地二进制文件创建payloads

## 包含的 payload memfd_create

这是一个linux系统的底层调用函数，它在内核3.17中引入，会创建一个匿名文件并返回一个文件描述符指向它，该文件表现和常规文件类同，
可以进行修改，截断，内存映射等等，但不同的是，它存在于RAM当中。这就是可以被攻击者所利用的，如果有办法将需要执行elf通过memfd_create写入内存中进行执行的话就可以达到我们的目的。

## 创建 Payload

除此之外，用户还可以开发自己的payload。默认情况下，payload存储在payloads/下，想要创建有效的payload，你只需include一个名为'desc'的dictonary，其参数为'name'，'description'，'archs'和'python_vers'。示例如下：

    
    
    desc = {"name" : "test payload", "description" : "new memory injection or fileless elf payload", "archs" : "all", "python_vers" : ">2.5"}

除了'desc' dictonary之外，我构建的插件引擎使用的entry
point（入口点）需要一个main函数，它将自动传递两个参数，一个是布尔值，如果为真则意味着它传递了一个url，第二个参数传递的是数据。以下是一个简单入口点的示例：

    
    
    def main(is_url, url_or_payload):
        return

## 安装

依赖项安装：

    
    
    pip3 -U -r dep.txt

fireELF是在Python 3.x.x中开发的。

## 使用

    
    
    usage: main.py [-h] [-s] [-p PAYLOAD_NAME] [-w PAYLOAD_FILENAME]
                   (-u PAYLOAD_URL | -e EXECUTABLE_PATH)
    
    fireELF, Linux Fileless Malware Generator
    
    optional arguments:
      -h, --help           显示帮助信息并退出
      -s                   Supress Banner
      -p PAYLOAD_NAME      使用的PAYLOAD名称
      -w PAYLOAD_FILENAME  要写入PAYLOAD的文件的名称（强烈建议，如果你没有使用Paste Site选项）                      
      -u PAYLOAD_URL       要执行的payload url
      -e EXECUTABLE_PATH   可执行文件的位置

***参考来源：[GitHub](https://github.com/rek7/fireELF)，FB小编secist编译，转载请注明来自FreeBuf.COM**  


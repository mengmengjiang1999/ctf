![](https://image.3001.net/images/20220118/1642477493_61e637b561044defc72f8.png!small)

## 关于Mesh-Kridik

Mesh-Kridik是一款功能强大的开源安全检测工具，可以帮助广大研究人员针对Kubernetes集群执行各种安全检测，并输出详细的安全检测报告，以增强Kubernetes服务的安全性。其中，所有的安全检查测试都是基于“[
_istio安全最佳实践_](https://istio.io/latest/docs/ops/best-practices/security/)”完整实现的。

Mesh-Kridik可以利用istio服务和OPA（开放策略代理）来增强Kubernetes服务的安全规则。输出的扫描报告包括导致安全问题产生的根本原因以及安全补救措施建议。

## 工具要求

> Go 1.16+
>
> jq
>
> istio

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并完成代码构建：

    
    
    git clone https://github.com/chen-keinan/mesh-kridik
    
    cd mesh-kridik
    
    make build

注意：Mesh-Kridik的执行需要使用root用户权限。

## 工具使用

如果在执行Mesh-Kridik时没有提供运行参数的话，工具将默认执行所有测试：

    
    
    ./mesh-kridik

如果在执行Mesh-Kridik时提供了运行参数的话，可以控制工具按需执行扫描任务：

    
    
    Usage: mesh-kridik [--version] [--help] <command> [<args>]
    
    Available commands are:
    
      -r , --report : run security checks and generate remediation report
    
      -i , --include: execute only specific security check, example -i=1.1
    
      -e , --exclude: ignore specific security check,  example -e=1.1,2.0

执行测试并生成错误测试报告：

    
    
    ./mesh-kridik -r

## 用户插件使用（Go插件）

Kube-kridik提供了一个用户插件钩子：MeshSecurityCheckResultHook，这个钩子可以接收k8s服务mesh安全检测结果。

 **编译用户插件：**

    
    
    go build -buildmode=plugin -o=~/<plugin folder>/<plugin>.so ~/<plugin folder>/<plugin>.go

 **然后将插件拷贝到目录中即可：**

    
    
    cp ~/<plugin folder>/<plugin>.so ~/.kube-kridik/plugins/compile/<plugin>.so

## 工具使用演示

![](https://image.3001.net/images/20220118/1642477853_61e6391d660e66e78bc46.gif)![](https://image.3001.net/images/20220118/1642477897_61e639497199ded1d0a56.gif)

## 项目地址

 **Mesh-Kridik：** 【[ _GitHub传送门_](https://github.com/chen-keinan/mesh-kridik)】

## 参考资料

> [ _https://istio.io/latest/docs/ops/best-> practices/security/_](https://istio.io/latest/docs/ops/best-> practices/security/)
>
> [ _https://github.com/chen-keinan/mesh-> kridik/tree/master/examples/plugins_](https://github.com/chen-keinan/mesh-> kridik/tree/master/examples/plugins)


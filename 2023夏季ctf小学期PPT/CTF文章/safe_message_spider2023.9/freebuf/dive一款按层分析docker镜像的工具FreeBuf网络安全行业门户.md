**这是一款用于分析docker镜像、图层内容以及探索缩小Docker镜像大小的方法的工具。**

![Image](https://image.3001.net/images/20190123/15482324394633.gif)
要分析Docker镜像，只需使用image tag/id/digest运行：

    
    
    dive <your-image-tag>
    

或者如果你想新建一个自己的image，那就直接使用命令:

    
    
    dive build -t <some-tag> .
    

## 基本功能

 **按层分解显示的ocker图像内容** 当您在左侧选择一个图层时，将显示该图层的内容结合右边的所有先前图层。 此外，你可以充分探索带箭头键的文件树。
**现实每层的变化** 文件树显示已更改，已修改，添加或删除的文件。可以调整此值以显示特定图层的更改，或聚合更改到此层。 **估计image效率**
左下方窗格显示基本图层信息和实验指标猜猜您的图片包含多少浪费的空间。
这可能来自重复跨层文件，跨层移动文件或不完全删除文件。提供了百分比“得分”和总浪费的文件空间。 **快速构建/分析周期**
您可以构建Docker镜像并使用一个命令立即进行分析:`dive build -t some-tag .`您只需要使用相同的`dive
build`替换`docker build`命令

## 安装

 **Ubuntu/Debian**

    
    
    wget https://github.com/wagoodman/dive/releases/download/v0.4.1/dive_0.4.1_linux_amd64.deb
    sudo apt install ./dive_0.4.1_linux_amd64.deb
    

**RHEL/Centos**

    
    
    curl -OL https://github.com/wagoodman/dive/releases/download/v0.4.1/dive_0.4.1_linux_amd64.rpm
    rpm -i dive_0.4.1_linux_amd64.rpm
    

**Arch Linux** 在Arch User Repository（AUR）中以[dive](a%20href=)的形式提供。

    
    
    yay -S dive
    

以上示例假定[`yay`]（<https://aur.archlinux.org/packages/yay/>）作为安装AUR包的工具。 **Mac**

    
    
    brew tap wagoodman/dive
    brew install dive
    

or download the latest Darwin build from the [releases page](a%20href=).
**Windows** 或者下载最新的Darwin版本 [latest release](a%20href=). **Go tools**

    
    
    go get github.com/wagoodman/dive
    

Note: 以这种方式安装，您将无法在运行时看到正确的版本 `dive -v`. **Docker**

    
    
    docker pull wagoodman/dive
    

or

    
    
    docker pull quay.io/wagoodman/dive
    

运行时，您需要包含docker客户端二进制文件和套接字文件：

    
    
    docker run --rm -it \
        -v /var/run/docker.sock:/var/run/docker.sock \
        wagoodman/dive:latest <dive arguments...>
    

适用于Windows的Docker（显示PowerShell兼容的换行符;折叠为一行以实现命令提示符兼容性）

    
    
    docker run --rm -it `
        -v /var/run/docker.sock:/var/run/docker.sock `
        wagoodman/dive:latest <dive arguments...>
    

**Note:** 根据您在本地运行的docker版本，您可能需要将docker API版本指定为环境变量：

    
    
       DOCKER_API_VERSION=1.37 dive ...
    

or if you are running with a docker image:

    
    
    docker run --rm -it \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -e DOCKER_API_VERSION=1.37
        wagoodman/dive:latest <dive arguments...>
    

## KeyBindings

Key Binding  | Description  
---|---  
<kbd>Ctrl + C</kbd> | 退出  
<kbd>Tab</kbd> or <kbd>Ctrl + Space</kbd> | 在图层和文件树视图之间切换  
<kbd>Ctrl + F</kbd> | 过滤文件  
<kbd>Ctrl + A</kbd> | 图层视图：查看聚合图像修改  
<kbd>Ctrl + L</kbd> | 图层视图：查看当前图层修改  
<kbd>Space</kbd> | Filetree视图：折叠/取消折叠目录  
<kbd>Ctrl + A</kbd> | Filetree视图： 显示/隐藏添加的文件  
<kbd>Ctrl + R</kbd> | Filetree视图：显示/隐藏已删除的文件  
<kbd>Ctrl + M</kbd> | Filetree视图：显示/隐藏已修改的文件  
<kbd>Ctrl + U</kbd> | Filetree视图：显示/隐藏未修改的文件  
<kbd>PageUp</kbd> | Filetree视图：向上滚动页面  
<kbd>PageDown</kbd> | Filetree视图：向下滚动页面  
  
## Configuration

无需配置，但是，您可以创建配置文件并覆盖值：

    
    
    log:
      enabled: true
      path: ./dive.log
      level: info
    # Note: you can specify multiple bindings by separating values with a comma.
    # Note: UI hinting is derived from the first binding
    keybinding:
      # Global bindings
      quit: ctrl+c
      toggle-view: tab, ctrl+space
      filter-files: ctrl+f, ctrl+slash
      # Layer view specific bindings  
      compare-all: ctrl+a
      compare-layer: ctrl+l
      # File view specific bindings
      toggle-collapse-dir: space
      toggle-added-files: ctrl+a
      toggle-removed-files: ctrl+r
      toggle-modified-files: ctrl+m
      toggle-unmodified-files: ctrl+u
      page-up: pgup
      page-down: pgdn
      
    diff:
      # You can change the default files show in the filetree (right pane). All diff types are shown by default. 
      hide:
        - added
        - removed
        - changed
        - unchanged
    filetree:
      # The default directory-collapse state
      collapse-dir: false
      # The percentage of screen width the filetree should take on the screen (must be >0 and <1)
      pane-width: 0.5
    layer:
      # Enable showing all changes from this layer and ever previous layer
      show-aggregated-changes: false
    

dive将在以下位置搜索配置：

`~/.dive.yaml`

`$XDG_CONFIG_HOME/dive.yaml`

`~/.config/dive.yaml`

***参考来源：[github](https://github.com/wagoodman/dive)，由周大涛编译，转载请注明来自FreeBuf.COM**


# **作者：Pamela@涂鸦智能安全实验室**

# Docker镜像简介

Docker镜像是由文件系统叠加而成。最底层是bootfs，之上的部分为rootfs。

 **bootfs** 是docker镜像最底层的引导文件系统，包含bootloader和操作系统内核。

 **rootfs** 通常包含一个操作系统运行所需的文件系统。这一层作为基础镜像。

在基础镜像之上，会加入各种镜像，如emacs、apache等![img](https://image.3001.net/images/20230506/1683344121_6455caf9a85c5cff26786.png!small)

Linux中的文件系统有些功能设计的很巧妙，比如挂载(mount)，允许把一个外部的文件系统（如CD，USB）以本地路径的形式去访问。例如放置一张CD后，我们可以通过访问`/mnt/cdrom`来查看CD中的内容。

Union File System（UnionFS）则设计的更加巧妙。在「挂载」功能的基础上，UnionFS允许在本地路径挂载多个目标目录。

UnionFS技术在Docker容器技术中的运用，首先体现在「镜像（image）」和「容器（container）」上。每一个Docker镜像都是一个只读的文件夹，当在容器中运行镜像时，Docker会自动挂载镜像中的、只读的文件目录，以及宿主机上一个临时的、可写的文件目录。容器中所有文件修改，都会写入这个临时目录里去。容器终结后，这个临时目录也会被相应删除。

UnionFS在Docker中的另一个应用，还体现在镜像本身上。容器运行时，在挂载的临时目录中如果写入数据，还可以选择把这部分数据从临时目录中保存下来，这样就生成了一个新的镜像。Docker在保存新镜像时，会把它们两部分——原镜像和增量——都保存在新镜像中。其中新的增量部分，就被称为「层（layer）」。

docker镜像是是分层存储的， 存储器包括aufs和overlay，overlay2等，默认存储在根路径`/var/lib/docker`下。

使用`docker image insepect ubuntu`，查看ubuntu镜像的layer地址

  

    
    
    "GraphDriver": {
        "Name": "overlay2",
        "Data": {
            "LowerDir": "/var/lib/docker/overlay2/dae8b41387884954d897fdab0aace674b1ccf29d7122d2b4aaa72f1874ac4b8b/diff:/var/lib/docker/overlay2/f5ae89ddaae69a185e5b352dbf5a18390f3f2024492db3d0e981892c767b919f/diff:/var/lib/docker/overlay2/c59b417d51fc4a6e590391d59a5a273b44d1c9c1a45d02806591dc735ee785e5/diff",
            "MergedDir": "/var/lib/docker/overlay2/8a801c1be8981cb28da1083b255216027fc68449efe36cc39f7d7ea8cbb96e98/merged",
            "UpperDir": "/var/lib/docker/overlay2/8a801c1be8981cb28da1083b255216027fc68449efe36cc39f7d7ea8cbb96e98/diff",
            "WorkDir": "/var/lib/docker/overlay2/8a801c1be8981cb28da1083b255216027fc68449efe36cc39f7d7ea8cbb96e98/work"
        }
    },

  

 **LowerDir** 是包含image的只读层，表示更改的读写层是 **UpperDir** 的一部分。 **MergedDir**
表示Docker用于运行容器的`UpperDir`和`LowerDi`r的结果。 **WorkDir** 是`overlay2`的内部目录，应该为空。

# clair扫描原理

Clair首先对镜像进行特征的提取，然后再将这些特征匹配CVE漏洞库，若发现漏洞则进行提示，其功能侧重于扫描容器中的OS及APP的CVE漏洞。该工具可以交叉检查Docker镜像的操作系统以及上面安装的任何包是否与任何已知不安全的包版本相匹配，支持跟K8S、Registry结合在一起，在镜像构建过程进行漏洞扫描，支持OS广泛，提供API，能提供构建阻断和报警。

在开始分析Clair之前，我们需要明白几点：

  * Clair是以静态分析的方式对镜像进行分析的，有点类似于杀毒软件用特征码来扫描病毒。
  * Clair镜像分析是按镜像Layer层级来进行的，如果某一层的软件有漏洞，在上层被删除了，该漏洞还是存在的。
  * Clair的漏洞扫描是通过软件版本比对来完成的，如果某个应用，比如Nginx ，它在镜像中的版本为1.0.0，而该版本在数据库中存在1.0.0对应的漏洞数据，则表示该镜像存在对应的漏洞。

 **架构：**

![img](https://image.3001.net/images/20230506/1683344130_6455cb027d447e4371230.png!small)

整体处理流程如下：

  * Clair定期从配置的源获取漏洞元数据然后存进数据库。
  * 客户端使用Clair API处理镜像，获取镜像的特征并存进数据库。
  * 客户端使用Clair API从数据库查询特定镜像的漏洞情况，为每个请求关联漏洞和特征，避免需要重新扫描镜像。
  * 当更新漏洞元数据时，将会有系统通知产生。另外，还有WebHook用于配置将受影响的镜像记录起来或者拦截其部署。

![img](https://image.3001.net/images/20230506/1683344134_6455cb0639d9711c0e437.png!small)

## 客户端扫描

客户端 [analyze-local-images](https://raw.githubusercontent.com/coreos/analyze-local-images/master/main.go)，执行流程

`main()->intMain()->AnalyzeLocalImage()—>analyzeLayer()->getLayer()`

1） 在tmp文件夹新建临时文件夹

    
    
    tmpPath, err := ioutil.TempDir("", "analyze-local-image-")
    if err != nil {
    	log.Fatalf("Could not create temporary folder: %s", err)
    }
    defer os.RemoveAll(tmpPath)
    // Intercept SIGINT / SIGKILl signals.
    interrupt := make(chan os.Signal)
    signal.Notify(interrupt, os.Interrupt, os.Kill)
    // Analyze the image.
    analyzeCh := make(chan error, 1)
    go func() {
    	analyzeCh <- AnalyzeLocalImage(imageName, minSeverity, *flagEndpoint, *flagMyAddress, tmpPath)
    }()  
      
    

2） 跟进AnalyzeLocalImage函数

    
    
    func AnalyzeLocalImage(imageName string, minSeverity database.Severity, endpoint, myAddress, tmpPath string) error {
    	// Save image.
    	log.Printf("Saving %s to local disk (this may take some time)", imageName)
    	err := save(imageName, tmpPath)
    	if err != nil {
    		return fmt.Errorf("Could not save image: %s", err)
    	}
    	// Retrieve history.
    	log.Println("Retrieving image history")
    	layerIDs, err := historyFromManifest(tmpPath)
    	if err != nil {
    		layerIDs, err = historyFromCommand(imageName)
    	}
    	if err != nil || len(layerIDs) == 0 {
    		return fmt.Errorf("Could not get image's history: %s", err)
    	}

跟进save函数，使用`docker save`保存镜像，并解压到上面建的tmp文件夹下

    
    
    func save(imageName, path string) error {
    	var stderr bytes.Buffer
    	save := exec.Command("docker", "save", imageName)
    	save.Stderr = &stderr
    	extract := exec.Command("tar", "xf", "-", "-C"+path)
    	extract.Stderr = &stderr
    	pipe, err := extract.StdinPipe()
    	if err != nil {
    		return err
    	}

跟进historyFromMainfest函数，分析manifest.json，获取镜像的layer信息

    
    
    func historyFromManifest(path string) ([]string, error) {
    	mf, err := os.Open(path + "/manifest.json")
    	if err != nil {
    		return nil, err
    	}
    	defer mf.Close()
    	// https://github.com/docker/docker/blob/master/image/tarexport/tarexport.go#L17
    	type manifestItem struct {
    		Config   string
    		RepoTags []string
    		Layers   []string
    	}
    	var manifest []manifestItem
    	if err = json.NewDecoder(mf).Decode(&manifest); err != nil {
    		return nil, err
    	} else if len(manifest) != 1 {
    		return nil, err
    	}
    	var layers []string
    	for _, layer := range manifest[0].Layers {
    		layers = append(layers, strings.TrimSuffix(layer, "/layer.tar"))
    	}
    	return layers, nil
    }

3）跟进分析analyzeLayer和getLayer函数，分别是发送请求到服务端和从服务端获取漏洞信息结果

    
    
    func analyzeLayer(endpoint, path, layerName, parentLayerName string) error {
    	payload := v1.LayerEnvelope{
    		Layer: &v1.Layer{
    			Name:       layerName,
    			Path:       path,
    			ParentName: parentLayerName,
    			Format:     "Docker",
    		},
    	}
    	jsonPayload, err := json.Marshal(payload)
    	if err != nil {
    		return err
    	}
    	request, err := http.NewRequest("POST", endpoint+postLayerURI, bytes.NewBuffer(jsonPayload))
    	if err != nil {
    		return err
    	}
    	request.Header.Set("Content-Type", "application/json")
    	client := &http.Client{}
    	response, err := client.Do(request)
    	if err != nil {
    		return err
    	}
    	defer response.Body.Close()
    	if response.StatusCode != 201 {
    		body, _ := ioutil.ReadAll(response.Body)
    		return fmt.Errorf("Got response %d with message %s", response.StatusCode, string(body))
    	}
    	return nil
    }
    func getLayer(endpoint, layerID string) (v1.Layer, error) {
    	response, err := http.Get(endpoint + fmt.Sprintf(getLayerFeaturesURI, layerID))
    	if err != nil {
    		return v1.Layer{}, err
    	}
    	defer response.Body.Close()
    	if response.StatusCode != 200 {
    		body, _ := ioutil.ReadAll(response.Body)
    		err := fmt.Errorf("Got response %d with message %s", response.StatusCode, string(body))
    		return v1.Layer{}, err
    	}
    	var apiResponse v1.LayerEnvelope
    	if err = json.NewDecoder(response.Body).Decode(&apiResponse); err != nil {
    		return v1.Layer{}, err
    	} else if apiResponse.Error != nil {
    		return v1.Layer{}, errors.New(apiResponse.Error.Message)
    	}
    	return *apiResponse.Layer, nil
    }

客户端做的事情很简单， **就是将layer.tar发送给clair，并将clair分析后的结果通过API接口获取到并在本地打印。**

## 服务端扫描

analyze-local-images 发送layer.tar文件后主要是由/worker.go下的ProcessLayer方法进行处理的。

这里先简单讲下clair的目录结构，我们仅需要重点关注有注释的文件夹。

> |–api //api接口
>
> |– cmd//服务端主程序
>
> |–contrib
>
> |–database //数据库相关
>
> |–Documentation
>
> |–ext //拓展功能
>
> |– pkg//通用方法
>
> |– testdata
>
> `–vendor

为了能够深入理解Clair，我们还是要从其main函数开始分析。

/cmd/clair/main.go

He1m4n6a

  * [主页](https://he1m4n6a.github.io/)
  * [标签](https://he1m4n6a.github.io/tags)
  * [存档](https://he1m4n6a.github.io/archive)
  * [关于](https://he1m4n6a.github.io/about/)
  * 搜索

  1. [Docker镜像简介](https://he1m4n6a.github.io/2019/12/19/Docker%E9%95%9C%E5%83%8F%E6%89%AB%E6%8F%8F%E5%8E%9F%E7%90%86/#Docker%E9%95%9C%E5%83%8F%E7%AE%80%E4%BB%8B)
    1. [docker镜像保存](https://he1m4n6a.github.io/2019/12/19/Docker%E9%95%9C%E5%83%8F%E6%89%AB%E6%8F%8F%E5%8E%9F%E7%90%86/#docker%E9%95%9C%E5%83%8F%E4%BF%9D%E5%AD%98)
  2. [clair扫描原理](https://he1m4n6a.github.io/2019/12/19/Docker%E9%95%9C%E5%83%8F%E6%89%AB%E6%8F%8F%E5%8E%9F%E7%90%86/#clair%E6%89%AB%E6%8F%8F%E5%8E%9F%E7%90%86)
    1. [客户端扫描](https://he1m4n6a.github.io/2019/12/19/Docker%E9%95%9C%E5%83%8F%E6%89%AB%E6%8F%8F%E5%8E%9F%E7%90%86/#%E5%AE%A2%E6%88%B7%E7%AB%AF%E6%89%AB%E6%8F%8F)
    2. [服务端扫描](https://he1m4n6a.github.io/2019/12/19/Docker%E9%95%9C%E5%83%8F%E6%89%AB%E6%8F%8F%E5%8E%9F%E7%90%86/#%E6%9C%8D%E5%8A%A1%E7%AB%AF%E6%89%AB%E6%8F%8F)

Docker镜像扫描原理

发布于：2019-12-19 23:49:52 标签：/
[docker镜像](https://he1m4n6a.github.io/tags/#docker%E9%95%9C%E5%83%8F
"docker镜像")/ [clair](https://he1m4n6a.github.io/tags/#clair "clair")/ 访问：252

# Docker镜像简介

Docker镜像是由文件系统叠加而成。最底层是bootfs，之上的部分为rootfs。

 **bootfs** 是docker镜像最底层的引导文件系统，包含bootloader和操作系统内核。

 **rootfs** 通常包含一个操作系统运行所需的文件系统。这一层作为基础镜像。

在基础镜像之上，会加入各种镜像，如emacs、apache等。

![img](https://image.3001.net/images/20230506/1683344761_6455cd7974f40d16ae5ba.png!small)

Linux中的文件系统有些功能设计的很巧妙，比如挂载(mount)，允许把一个外部的文件系统（如CD，USB）以本地路径的形式去访问。例如放置一张CD后，我们可以通过访问`/mnt/cdrom`来查看CD中的内容。

Union File System（UnionFS）则设计的更加巧妙。在「挂载」功能的基础上，UnionFS允许在本地路径挂载多个目标目录。

UnionFS技术在Docker容器技术中的运用，首先体现在「镜像（image）」和「容器（container）」上。每一个Docker镜像都是一个只读的文件夹，当在容器中运行镜像时，Docker会自动挂载镜像中的、只读的文件目录，以及宿主机上一个临时的、可写的文件目录。容器中所有文件修改，都会写入这个临时目录里去。容器终结后，这个临时目录也会被相应删除。

UnionFS在Docker中的另一个应用，还体现在镜像本身上。容器运行时，在挂载的临时目录中如果写入数据，还可以选择把这部分数据从临时目录中保存下来，这样就生成了一个新的镜像。Docker在保存新镜像时，会把它们两部分——原镜像和增量——都保存在新镜像中。其中新的增量部分，就被称为「层（layer）」。

## docker镜像保存

docker镜像是是分层存储的， 存储器包括aufs和overlay，overlay2等，默认存储在根路径`/var/lib/docker`下。

使用`docker image insepect ubuntu`，查看ubuntu镜像的layer地址

    
    
    "GraphDriver": {
        "Name": "overlay2",
        "Data": {
            "LowerDir": "/var/lib/docker/overlay2/dae8b41387884954d897fdab0aace674b1ccf29d7122d2b4aaa72f1874ac4b8b/diff:/var/lib/docker/overlay2/f5ae89ddaae69a185e5b352dbf5a18390f3f2024492db3d0e981892c767b919f/diff:/var/lib/docker/overlay2/c59b417d51fc4a6e590391d59a5a273b44d1c9c1a45d02806591dc735ee785e5/diff",
            "MergedDir": "/var/lib/docker/overlay2/8a801c1be8981cb28da1083b255216027fc68449efe36cc39f7d7ea8cbb96e98/merged",
            "UpperDir": "/var/lib/docker/overlay2/8a801c1be8981cb28da1083b255216027fc68449efe36cc39f7d7ea8cbb96e98/diff",
            "WorkDir": "/var/lib/docker/overlay2/8a801c1be8981cb28da1083b255216027fc68449efe36cc39f7d7ea8cbb96e98/work"
        }
    },

 **LowerDir** 是包含image的只读层，表示更改的读写层是 **UpperDir** 的一部分。 **MergedDir**
表示Docker用于运行容器的`UpperDir`和`LowerDi`r的结果。 **WorkDir** 是`overlay2`的内部目录，应该为空。

# clair扫描原理

Clair首先对镜像进行特征的提取，然后再将这些特征匹配CVE漏洞库，若发现漏洞则进行提示，其功能侧重于扫描容器中的OS及APP的CVE漏洞。该工具可以交叉检查Docker镜像的操作系统以及上面安装的任何包是否与任何已知不安全的包版本相匹配，支持跟K8S、Registry结合在一起，在镜像构建过程进行漏洞扫描，支持OS广泛，提供API，能提供构建阻断和报警。

在开始分析Clair之前，我们需要明白几点：

  * Clair是以静态分析的方式对镜像进行分析的，有点类似于杀毒软件用特征码来扫描病毒。
  * Clair镜像分析是按镜像Layer层级来进行的，如果某一层的软件有漏洞，在上层被删除了，该漏洞还是存在的。
  * Clair的漏洞扫描是通过软件版本比对来完成的，如果某个应用，比如Nginx ，它在镜像中的版本为1.0.0，而该版本在数据库中存在1.0.0对应的漏洞数据，则表示该镜像存在对应的漏洞。

 **架构：**

![img](https://image.3001.net/images/20230506/1683344764_6455cd7ce44f3e508b877.png!small)

整体处理流程如下：

  * Clair定期从配置的源获取漏洞元数据然后存进数据库。
  * 客户端使用Clair API处理镜像，获取镜像的特征并存进数据库。
  * 客户端使用Clair API从数据库查询特定镜像的漏洞情况，为每个请求关联漏洞和特征，避免需要重新扫描镜像。
  * 当更新漏洞元数据时，将会有系统通知产生。另外，还有WebHook用于配置将受影响的镜像记录起来或者拦截其部署。

![img](https://image.3001.net/images/20230506/1683344770_6455cd8243731b8b8ad87.png!small)

## 客户端扫描

客户端 [analyze-local-images](https://raw.githubusercontent.com/coreos/analyze-local-images/master/main.go)，执行流程

`main()->intMain()->AnalyzeLocalImage()—>analyzeLayer()->getLayer()`

1） 在tmp文件夹新建临时文件夹

    
    
    tmpPath, err := ioutil.TempDir("", "analyze-local-image-")
    if err != nil {
    	log.Fatalf("Could not create temporary folder: %s", err)
    }
    defer os.RemoveAll(tmpPath)
    // Intercept SIGINT / SIGKILl signals.
    interrupt := make(chan os.Signal)
    signal.Notify(interrupt, os.Interrupt, os.Kill)
    // Analyze the image.
    analyzeCh := make(chan error, 1)
    go func() {
    	analyzeCh <- AnalyzeLocalImage(imageName, minSeverity, *flagEndpoint, *flagMyAddress, tmpPath)
    }()

2） 跟进AnalyzeLocalImage函数

    
    
    func AnalyzeLocalImage(imageName string, minSeverity database.Severity, endpoint, myAddress, tmpPath string) error {
    	// Save image.
    	log.Printf("Saving %s to local disk (this may take some time)", imageName)
    	err := save(imageName, tmpPath)
    	if err != nil {
    		return fmt.Errorf("Could not save image: %s", err)
    	}
    	// Retrieve history.
    	log.Println("Retrieving image history")
    	layerIDs, err := historyFromManifest(tmpPath)
    	if err != nil {
    		layerIDs, err = historyFromCommand(imageName)
    	}
    	if err != nil || len(layerIDs) == 0 {
    		return fmt.Errorf("Could not get image's history: %s", err)
    	}

跟进save函数，使用`docker save`保存镜像，并解压到上面建的tmp文件夹下

    
    
    func save(imageName, path string) error {
    	var stderr bytes.Buffer
    	save := exec.Command("docker", "save", imageName)
    	save.Stderr = &stderr
    	extract := exec.Command("tar", "xf", "-", "-C"+path)
    	extract.Stderr = &stderr
    	pipe, err := extract.StdinPipe()
    	if err != nil {
    		return err
    	}

跟进historyFromMainfest函数，分析manifest.json，获取镜像的layer信息

    
    
    func historyFromManifest(path string) ([]string, error) {
    	mf, err := os.Open(path + "/manifest.json")
    	if err != nil {
    		return nil, err
    	}
    	defer mf.Close()
    	// https://github.com/docker/docker/blob/master/image/tarexport/tarexport.go#L17
    	type manifestItem struct {
    		Config   string
    		RepoTags []string
    		Layers   []string
    	}
    	var manifest []manifestItem
    	if err = json.NewDecoder(mf).Decode(&manifest); err != nil {
    		return nil, err
    	} else if len(manifest) != 1 {
    		return nil, err
    	}
    	var layers []string
    	for _, layer := range manifest[0].Layers {
    		layers = append(layers, strings.TrimSuffix(layer, "/layer.tar"))
    	}
    	return layers, nil
    }
    

3）跟进分析analyzeLayer和getLayer函数，分别是发送请求到服务端和从服务端获取漏洞信息结果

    
    
    func analyzeLayer(endpoint, path, layerName, parentLayerName string) error {
    	payload := v1.LayerEnvelope{
    		Layer: &v1.Layer{
    			Name:       layerName,
    			Path:       path,
    			ParentName: parentLayerName,
    			Format:     "Docker",
    		},
    	}
    	jsonPayload, err := json.Marshal(payload)
    	if err != nil {
    		return err
    	}
    	request, err := http.NewRequest("POST", endpoint+postLayerURI, bytes.NewBuffer(jsonPayload))
    	if err != nil {
    		return err
    	}
    	request.Header.Set("Content-Type", "application/json")
    	client := &http.Client{}
    	response, err := client.Do(request)
    	if err != nil {
    		return err
    	}
    	defer response.Body.Close()
    	if response.StatusCode != 201 {
    		body, _ := ioutil.ReadAll(response.Body)
    		return fmt.Errorf("Got response %d with message %s", response.StatusCode, string(body))
    	}
    	return nil
    }
    func getLayer(endpoint, layerID string) (v1.Layer, error) {
    	response, err := http.Get(endpoint + fmt.Sprintf(getLayerFeaturesURI, layerID))
    	if err != nil {
    		return v1.Layer{}, err
    	}
    	defer response.Body.Close()
    	if response.StatusCode != 200 {
    		body, _ := ioutil.ReadAll(response.Body)
    		err := fmt.Errorf("Got response %d with message %s", response.StatusCode, string(body))
    		return v1.Layer{}, err
    	}
    	var apiResponse v1.LayerEnvelope
    	if err = json.NewDecoder(response.Body).Decode(&apiResponse); err != nil {
    		return v1.Layer{}, err
    	} else if apiResponse.Error != nil {
    		return v1.Layer{}, errors.New(apiResponse.Error.Message)
    	}
    	return *apiResponse.Layer, nil
    }
    

客户端做的事情很简单， **就是将layer.tar发送给clair，并将clair分析后的结果通过API接口获取到并在本地打印。**

## 服务端扫描

analyze-local-images 发送layer.tar文件后主要是由/worker.go下的ProcessLayer方法进行处理的。

这里先简单讲下clair的目录结构，我们仅需要重点关注有注释的文件夹。

> |–api //api接口
>
> |– cmd//服务端主程序
>
> |–contrib
>
> |–database //数据库相关
>
> |–Documentation
>
> |–ext //拓展功能
>
> |– pkg//通用方法
>
> |– testdata
>
> `–vendor

为了能够深入理解Clair，我们还是要从其main函数开始分析。

/cmd/clair/main.go

    
    
    funcmain() {
       // 解析命令行参数，默认从/etc/clair/config.yaml读取数据库配置信息
       ......
       // 加载配置文件
       config, err :=LoadConfig(*flagConfigPath)
       if err != nil {
          log.WithError(err).Fatal("failedto load configuration")
       }
       // 初始化日志系统
    ......
    //启动clair
       Boot(config)
    }
     
    # /cmd/clair/main.go
    funcBoot(config *Config) {
       ......
       // 打开数据库
       db, err :=database.Open(config.Database)
       if err != nil {
          log.Fatal(err)
       }
       defer db.Close()
       // 启动notifier服务
       st.Begin()
       go clair.RunNotifier(config.Notifier,db, st)
       // 启动clair的Rest API 服务
       st.Begin()
       go api.Run(config.API, db, st)
       st.Begin()
    //启动clair的健康检测服务
       go api.RunHealth(config.API, db, st)
       // 启动updater服务
       st.Begin()
       go clair.RunUpdater(config.Updater,db, st)
       // Wait for interruption and shutdowngracefully.
       waitForSignals(syscall.SIGINT,syscall.SIGTERM)
       log.Info("Received interruption,gracefully stopping ...")
       st.Stop()
    }

Go api.Run执行后，clair会开启Rest服务。

/api/api.go

    
    
    func Run(cfg *Config, store database.Datastore, st *stopper.Stopper) {
       defer st.End()
       // 如果配置为空就不启动服务
       ......
       srv := &graceful.Server{
          Timeout:          0,    // Already handled by our TimeOut middleware
          NoSignalHandling: true, // We want to use our own Stopper
          Server: &http.Server{
             Addr:      ":" + strconv.Itoa(cfg.Port),
             TLSConfig: tlsConfig,
             Handler:   http.TimeoutHandler(newAPIHandler(cfg, store), cfg.Timeout, timeoutResponse),
          },
       }
    //启动HTTP服务   
    listenAndServeWithStopper(srv, st, cfg.CertFile, cfg.KeyFile)
       log.Info("main API stopped")
    }

Api.Run中调用api.newAPIHandler生成一个API Handler来处理所有的API请求。

/api/router.go

    
    
    funcnewAPIHandler(cfg *Config, store database.Datastore) http.Handler {
       router := make(router)
       router["/v1"] =v1.NewRouter(store, cfg.PaginationKey)
       return router
    }

所有的router对应的Handler都在

/api/v1/router.go中：

    
    
    funcNewRouter(store database.Datastore, paginationKey string) *httprouter.Router {
       router := httprouter.New()
       ctx := &context{store,paginationKey}
       // Layers
       router.POST("/layers",httpHandler(postLayer, ctx))
      router.GET("/layers/:layerName", httpHandler(getLayer, ctx))
      router.DELETE("/layers/:layerName", httpHandler(deleteLayer,ctx))
       // Namespaces
       router.GET("/namespaces",httpHandler(getNamespaces, ctx))
       // Vulnerabilities
      router.GET("/namespaces/:namespaceName/vulnerabilities",httpHandler(getVulnerabilities, ctx))
       router.POST("/namespaces/:namespaceName/vulnerabilities",httpHandler(postVulnerability, ctx))
      router.GET("/namespaces/:namespaceName/vulnerabilities/:vulnerabilityName",httpHandler(getVulnerability, ctx))
      router.PUT("/namespaces/:namespaceName/vulnerabilities/:vulnerabilityName",httpHandler(putVulnerability, ctx))
      router.DELETE("/namespaces/:namespaceName/vulnerabilities/:vulnerabilityName",httpHandler(deleteVulnerability, ctx))
       // Fixes
      router.GET("/namespaces/:namespaceName/vulnerabilities/:vulnerabilityName/fixes",httpHandler(getFixes, ctx))
      router.PUT("/namespaces/:namespaceName/vulnerabilities/:vulnerabilityName/fixes/:fixName",httpHandler(putFix, ctx))
      router.DELETE("/namespaces/:namespaceName/vulnerabilities/:vulnerabilityName/fixes/:fixName",httpHandler(deleteFix, ctx))
       // Notifications
      router.GET("/notifications/:notificationName",httpHandler(getNotification, ctx))
      router.DELETE("/notifications/:notificationName",httpHandler(deleteNotification, ctx))
       // Metrics
       router.GET("/metrics",httpHandler(getMetrics, ctx))
       return router
    }

而具体的Handler是在/api/v1/routers.go中

例如analyze-local-images 发送的layer.tar文件，最终会交给postLayer方法处理。

    
    
    funcpostLayer(w http.ResponseWriter, r *http.Request, p httprouter.Params, ctx*context) (string, int) {
      ......
       err = clair.ProcessLayer(ctx.Store,request.Layer.Format, request.Layer.Name, request.Layer.ParentName,request.Layer.Path, request.Layer.Headers)
       ......
    }

而ProcessLayer 方法就是在/worker.go中定义的。

    
    
    funcpostLayer(w http.ResponseWriter, r *http.Request, p httprouter.Params, ctx*context) (string, int) {
      ......
       err = clair.ProcessLayer(ctx.Store,request.Layer.Format, request.Layer.Name, request.Layer.ParentName,request.Layer.Path, request.Layer.Headers)
       ......
    }
    而ProcessLayer 方法就是在/worker.go中定义的。
    
    funcProcessLayer(datastore database.Datastore, imageFormat, name, parentName, pathstring, headers map[string]string) error {
      //参数验证
    ......
       // 检测层是否已经入库
      layer, err := datastore.FindLayer(name, false, false)
       if err != nil && err !=commonerr.ErrNotFound {
          return err
       }
    //如果存在并且该layer的Engine Version比DB中记录的大于等于3（目前最大的worker version）,则表明已经detect过这个layer，则结束返回。否则detectContent对数据进行解析。
      
       // Analyze the content.
       layer.Namespace, layer.Features, err =detectContent(imageFormat, name, path, headers, layer.Parent)
       if err != nil {
          return err
       }
       return datastore.InsertLayer(layer)
    }

在detectContent方法如下：

    
    
    func detectContent(imageFormat,name, path string, headers map[string]string, parent *database.Layer)(namespace *database.Namespace, featureVersions []database.FeatureVersion, errerror) {
      ......
    //解析namespace
       namespace, err = detectNamespace(name,files, parent)
       if err != nil {
          return
       }
       //解析特征版本
      featureVersions, err = detectFeatureVersions(name, files, namespace,parent)
       if err != nil {
          return
       }
      ......
    return
    }

 **参考：**

<https://blog.csdn.net/weixin_39800144/article/details/79019503>

<https://cloud.tencent.com/developer/article/1039768>

<https://zhuanlan.zhihu.com/p/43372662>

<https://zhuanlan.zhihu.com/p/41958018>

<https://www.freebuf.com/column/157784.html>

[https://www.freecodecamp.org/news/where-are-docker-images-stored-docker-container-paths-explained/﻿](https://www.freecodecamp.org/news/where-are-docker-images-stored-docker-container-paths-explained/)

 **漏洞悬赏计划：涂鸦智能安全响应中心（https://src.tuya.com）欢迎白帽子来探索。**

招聘内推计划：涵盖安全开发、安全测试、代码审计、安全合规等所有方面的岗位，简历投递[sec@tuya.com](mailto:sec@tuya.com)，
**请注明来自FreeBuf** 。

 **Pamela@涂鸦智能安全实验室**


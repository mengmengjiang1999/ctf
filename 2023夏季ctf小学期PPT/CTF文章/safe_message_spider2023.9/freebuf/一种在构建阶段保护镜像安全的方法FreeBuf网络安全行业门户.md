首先，可以参考网上各类文章，在构建命令的时候多加注意，避免触及安全边界。

接下来，我们可以通过已有的镜像安全检测工具，对早已存在的镜像进行安全扫描，并对当前正在构建的镜像设置阻断规则，将安全防护前移至 CI/CD
阶段，当前市面上已知的镜像检测工具有：trivy、anchor、veinmind等，我只使用了veinmind，所以描述一下veinmind的详细功能：

首先 veinmind 支持检测镜像内的恶意文件、敏感信息、弱口令、后门、异常历史命令，支持镜像资产清点，支持集成到 CI/CD
进行检测，支持镜像阻断，支持使用 helm 安装部署。

## 一、docker 镜像阻断功能：

    
    
    # first
    ./veinmind-runner authz -c config.toml 
    # second
    dockerd --authorization-plugin=veinmind-broker
    

其中config.toml,包含如下字段

|  **字段名**|  **字段属性**|  **含义**  
---|---|---|---  
policy| action| string| 需要监控的行为  
| enabled_plugins| []string| 使用哪些插件  
| plugin_params| []string| 各个插件的参数  
| risk_level_filter| []string| 风险等级  
| block| bool| 是否阻断  
| alert| bool| 是否报警  
log| report_log_path| string| 插件扫描日志  
| authz_log_path| string| 阻断服务日志  
  
action 原则上支持
[DockerAPI](https://docs.docker.com/engine/api/v1.41/#operation/)所提供的操作接口
如下的配置表示：当 创建容器或推送镜像 时，使用 veinmind-weakpass 插件扫描ssh服务，如果发现有弱密码存在，并且风险等级为 High
则阻止此操作，并发出警告。最终将扫描结果存放至plugin.log,将风险结果存放至auth.log。

    
    
    [log]
    plugin_log_path = "plugin.log"
    auth_log_path = "auth.log"
    [listener]
    listener_addr = "/run/docker/plugins/veinmind-broker.sock"
    [[policies]]
    action = "container_create"
    enabled_plugins = ["veinmind-weakpass"]
    plugin_paramas = ["veinmind-weakpass:scan.serviceName=ssh"]
    risk_level_filter = ["High"]
    block = true
    alert = true
    [[policies]]
    action = "image_push"
    enabled_plugins = ["veinmind-weakpass"]
    plugin_params = ["veinmind-weakpass:scan.serviceName=ssh"]
    risk_level_filter = ["High"]
    block = true
    alert = true
    

## 二、集成到 Jenkins：

![image](https://image.3001.net/images/20220801/1659340382_62e7865ebc7ac4535c69f.png!small)

扫描在 Job 过程中构建的镜像

>
>     注意：所有的使用方式都是默认Jenkins安装了以下插件:<br/>
>  
>
>   * Docker plugin
>
>     * Pipeline: Groovy Libraries
>
>

  1. 通过Pipeline Libraries引入配置

在 Manage Jenkins » Configure System » Global Pipeline Libraries 添加

    
    
    https://github.com/chaitin/veinmind-jenkins
    

![image](https://image.3001.net/images/20220801/1659340407_62e7867771d1275e37ff1.png!small)

随后即可在Jenkinsfile内使用:

    
    
    // import library
    @Library('veinmind-runner') _
    
    pipeline {
    agent any
    
    stages {
      stage('build') {
          steps {
              script {
                  sh 'docker build -t YOUR_IMAGE:YOUR_TAG  .'
              }
          }
      }
    
      // add scan
      stage('scan') {
          steps {
              script {
                  // easy mod
                  veinmindRunner.scan("YOUR_IMAGE:YOUR_TAG")
    
                  // set exit-code
                  veinmindRunner.scan("YOUR_IMAGE:YOUR_TAG", 1)
    
                  // set output
                  veinmindRunner.scan("YOUR_IMAGE:YOUR_TAG", outPut="report.json", exitCode=0)
    
                  // set all config params
                  veinmindRunner.scan("YOUR_IMAGE:YOUR_TAG", "scan-host", "report.json", 0)
              }
          }
      }
    }
    }
    

**参数设置**

 **参数名称**|  **参数作用**|  **默认值**  
---|---|---  
imageRef| 镜像| Reference  
scanAction| 扫描功能类型| scan-host  
outPut| 报告输出名称| report.json  
exitCode| 当发现安全问题时的程序退出码, 非零时阻断Pipeline| 0  
  
## 三、集成到 Gitlab：

![image](https://image.3001.net/images/20220801/1659340434_62e7869224d2a1a683785.png!small)

扫描在 Job 过程中构建的镜像

  1. 通过远程配置引入

    
    
    stages:
    - build
    
    # import scan runner
    include:
    - remote: https://download.veinmind.tech/scripts/veinmind-runner-gitlab-ci.yml
    
    YOUR_JOB:
    stage: build
    image: YOUR_BUILD_IMAGE:latest
    # add default config
    extends: .scan-config
    # add your config
    variables:
      IMAGE_REF: YOUR_APP:APP_TAG
    script:
      - docker build -t YOUR_APP:APP_TAG .
      # add scan script
      - !reference [.scan-script, script]
    

  2. 通过构建 veinmind/veinmind-gitlab-CI 仓库方式引入

此方式需要首先clone该仓库到您的的gitlab内。

    
    
    stages:
    - build
    
    # import scan runner
    include:
    - project: veinmind-gitlab-CI # absolute path
      file: runner.yml
    
    
    YOUR_JOB:
    stage: build
    image: YOUR_BUILD_IMAGE:latest
    # add default config
    extends: .scan-config
    # add your config
    variables:
      IMAGE_REF: YOUR_APP:APP_TAG
    script:
      - docker build -t YOUR_APP:APP_TAG .
      # add scan script
      - !reference [.scan-script, script]
    

  3. 直接修改.gitlab-ci.yml文件

    
    
    stages:
    - build
    
    YOUR_JOB:
    stage: build
    image: YOUR_BUILD_IMAGE:latest
    # add your config
    variables:
      SCAN_ACTION: scan-host
      IMAGE_REF: YOUR_APP:APP_TAG
      OUT_PUT: report.json
      EXIT_CODE: 0
    script:
      - docker build -t YOUR_APP:APP_TAG .
      # add scan script
      - docker run --rm --mount 'type=bind,source=/,target=/host,readonly' -v /var/run/docker.sock:/var/run/docker.sock -v `pwd`:/tool/resource veinmind/veinmind-runner $SCAN_ACTION $IMAGE_REF -o $OUT_PUT -e $EXIT_CODE
    

参数名称| 参数作用| 默认值  
---|---|---  
SCAN_ACTION| 扫描功能类型| scan-host  
IMAGE_REF| 镜像 Reference|  
EXIT_CODE| 当发现安全问题时的程序退出码, 非零时阻断Pipeline| 0  
OUT_PUT| 报告输出名称| report.json  
  
项目地址：<https://github.com/chaitin/veinmind-tools>

使用文档：<https://veinmind.chaitin.com/docs/>


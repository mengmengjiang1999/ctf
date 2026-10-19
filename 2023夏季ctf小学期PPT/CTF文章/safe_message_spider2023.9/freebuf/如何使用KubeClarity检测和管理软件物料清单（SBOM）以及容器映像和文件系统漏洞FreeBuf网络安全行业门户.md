![](https://image.3001.net/images/20220711/1657550201_62cc357945d1794c2ff9a.png!small)

## 关于KubeClarity

KubeClarity是一款专门用于检测和管理软件物料清单（SBOM）以及容器映像和文件系统漏洞的工具。在该工具的帮助下，广大研究人员可以扫描运行时K8s集群和CI/CD管道，以增强软件供应链的安全性。

## 功能介绍

> 1、完整的仪表盘信息：支持按漏洞严重性分类、显示完整的漏洞信息、显示漏洞新趋势等；
>
> 2、应用程序检测：支持自动检测K8s运行时环境中的应用程序、创建/编辑/删除应用程序、显示应用程序详细信息和漏洞；
>
> 3、查看应用程序资源：包、镜像、目录、文件、漏洞等；
>
> 4、K8s运行时扫描：按需扫描或计划任务扫描、自动检测目标命名空间、CIS Docker基准；
>
> 5、CLI（CI/CD）支持：使用多个集成内容分析器（Syft、cyclonedx-> gomod）生成SBOM、使用多个集成扫描仪扫描SBOM/镜像/目录漏洞、将结果导出到KubeClarity后端；
>
> 6、API支持：KubeClarity提供了[
> _API_](https://github.com/openclarity/kubeclarity/blob/master/api/swagger.yaml)服务；

## 工具架构

![](https://image.3001.net/images/20220711/1657550224_62cc35900329d250df158.png!small)

## 工具安装

广大研究人员可以使用Helm在一个K8s集群中安装KubeClarity：

1、首先，我们需要添加Helm项目：

    
    
    helm repo add kubeclarity https://openclarity.github.io/kubeclarity

2、存储KubeClarity默认图标值：

    
    
    helm show values kubeclarity/kubeclarity > values.yaml

3、检查values.yaml中的配置信息，更新所需的其他值；

4、使用Helm部署KubeClarity：

    
    
    helm install --values values.yaml --create-namespace kubeclarity kubeclarity/kubeclarity -n kubeclarity

或者，使用下列方法安装和部署KubeClarity：

    
    
    helm install --values values.yaml --create-namespace kubeclarity kubeclarity/kubeclarity -n kubeclarity --set global.openShiftRestricted=true \
    
      --set kubeclarity-postgresql.securityContext.enabled=false --set kubeclarity-postgresql.containerSecurityContext.enabled=false \
    
      --set kubeclarity-postgresql.volumePermissions.enabled=true --set kubeclarity-postgresql.volumePermissions.securityContext.runAsUser="auto" \
    
      --set kubeclarity-postgresql.shmVolume.chmod.enabled=false

5、将端口信息转发至KubeClarity UI：

    
    
    kubectl port-forward -n kubeclarity svc/kubeclarity-kubeclarity 9999:8080

6、在浏览器中访问下列地址以打开KubeClarity UI：

    
    
    http://localhost:9999/

## 工具使用

### 使用多个整合的内容分析器生成SBOM

    
    
    kubeclarity-cli analyze <image/directory name> --input-type <dir|file|image(default)> -o <output file or stdout>
    
    # 样例:
    ANALYZER_LIST="syft" kubeclarity-cli analyze nginx:latest -o nginx.sbom

### 使用多个整合的扫描器扫描安全漏洞

    
    
    kubeclarity-cli scan <image/sbom/directoty/file name> --input-type <sbom|dir|file|image(default)> -f <output file>
    
    # 样例:
    SCANNERS_LIST="grype" kubeclarity-cli scan nginx.sbom --input-type sbom

### 将结果导出到KubeClarity后端

 **导出SBOM** ：

    
    
    BACKEND_HOST=<KubeClarity backend address> BACKEND_DISABLE_TLS=true kubeclarity-cli analyze <image> --application-id <application ID> -e -o <SBOM output file>
    
    # 样例:
    BACKEND_HOST=localhost:9999 BACKEND_DISABLE_TLS=true kubeclarity-cli analyze nginx:latest --application-id 23452f9c-6e31-5845-bf53-6566b81a2906 -e -o nginx.sbom

 **导出漏洞扫描结果** ：

    
    
    BACKEND_HOST=<KubeClarity backend address> BACKEND_DISABLE_TLS=true kubeclarity-cli scan <image> --application-id <application ID> -e
    
    # 样例:
    SCANNERS_LIST="grype" BACKEND_HOST=localhost:9999 BACKEND_DISABLE_TLS=true kubeclarity-cli scan nginx.sbom --input-type sbom  --application-id 23452f9c-6e31-5845-bf53-6566b81a2906 -e

### 跨不同CI/CD整合SBOM和漏洞信息

    
    
    # 样例:
    
    ANALYZER_LIST="syft" kubeclarity-cli analyze nginx:latest -o nginx.sbom --merge-sbom inputsbom.xml

## 工具运行截图

![](https://image.3001.net/images/20220711/1657550364_62cc361c34ae0baec6db3.png!small)

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/openclarity/kubeclarity/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **KubeClarity** ：【[ _GitHub传送门_](https://github.com/openclarity/kubeclarity)】

## 参考资料

> [
> _https://github.com/openclarity/kubeclarity/blob/master/api/swagger.yaml_](https://github.com/openclarity/kubeclarity/blob/master/api/swagger.yaml)
>
> [ _https://github.com/anchore/syft_](https://github.com/anchore/syft)
>
> [ _https://github.com/CycloneDX/cyclonedx-> gomod_](https://github.com/CycloneDX/cyclonedx-gomod)
>
> [ _https://github.com/anchore/grype_](https://github.com/anchore/grype)
>
> [ _https://github.com/DependencyTrack/dependency-> track_](https://github.com/DependencyTrack/dependency-track)
>
> [
> _https://github.com/openclarity/kubeclarity/tree/master/shared/pkg/analyzer_](https://github.com/openclarity/kubeclarity/tree/master/shared/pkg/analyzer)
>
> [
> _https://github.com/openclarity/kubeclarity/tree/master/shared/pkg/scanner_](https://github.com/openclarity/kubeclarity/tree/master/shared/pkg/scanner)
>
> [
> _https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console_](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console)
>
> [ _https://cloud.google.com/docs/authentication/getting-> started#creating_a_service_account_](https://cloud.google.com/docs/authentication/getting-> started#creating_a_service_account)
>
> [ _https://developers.google.com/identity/protocols/application-default-> credentials_](https://developers.google.com/identity/protocols/application-> default-credentials)
>
> [
> _https://docs.docker.com/registry/spec/manifest-v2-2/_](https://docs.docker.com/registry/spec/manifest-v2-2/)


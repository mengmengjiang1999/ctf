![](https://image.3001.net/images/20220315/1647357221_6230ad25ccb0136c5154a.jpeg!small)

## 关于Checkov

Checkov是一款针对基础设施即代码（IaC）的静态代码安全分析工具，在该工具的帮助下，广大研究人员可以在在Terraform、CloudFormation、Kubernetes、Serverless
Framework和其他基础设施的构建期间，轻松检测出云端代码安全问题。

Checkov使用了基于图表的扫描技术来扫描那些使用了[ _Terraform_](https://terraform.io/)、[ _Terraform
plan_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/Terraform%20Plan%20Scanning.md)、[
_Cloudformation_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/Cloudformation.md)、[
_AWS
SAM_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/AWS%20SAM.md)、[
_Kubernetes_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/Kubernetes.md)、[
_Helm
charts_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/Helm.md)、[
_Kustomize_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/Kustomize.md)、[
_Dockerfile_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/Dockerfile.md)、[
_Serverless_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/Serverless%20Framework.md)、[
_Bicep_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/Bicep.md)或[
_ARM模板配置_](https://github.com/bridgecrewio/checkov/blob/master/docs/7.Scan%20Examples/Azure%20ARM%20templates.md)的云基础设施，并尝试检测出潜在的安全性问题或合规性错误配置。

## 功能介绍

> 1、内置了超过1000种针对AWS、Azure和Google Cloud的安全和合规性最佳实践[
> _策略_](https://github.com/bridgecrewio/checkov/blob/master/docs/5.Policy%20Index/all.md)。
>
> 2、支持扫描Terraform、Terraform Plan、CloudFormation、AWS
> SAM、Kubernetes、Dockerfile、Serverless Framework、Bicep和ARM模板文件。
>
> 3、支持基于内存扫描的上下文感知策略。
>
> 4、属性策略支持Python格式，属性和混合策略支持YAML格式。
>
> 5、支持检测EC2用户数据、Lambda环境变量和Terraform中的[
> _AWS凭据_](https://github.com/bridgecrewio/checkov/blob/master/docs/2.Basics/Scanning%20Credentials%20and%20Secrets.md)。
>
> 6、使用正则表达式、关键字和基于熵的检测来识别[ _敏感数据_](https://bridgecrew.io/blog/checkov-secrets-> scanning-find-exposed-credentials-in-iac/)。
>
> 7、评估Terraform提供商设置，以规范那些通过[
> _Terraform_](https://registry.terraform.io/browse/providers)管理的IaaS、PaaS或SaaS的创建、管理和更新行为。
>
> 8、支持以CLI、CycloneDX、JSON、JUnit XML、SARIF和Github Markdown等形式[
> _输出结果_](https://github.com/bridgecrewio/checkov/blob/master/docs/2.Basics/Reviewing%20Scan%20Results.md)。

## 工具要求

> 1、Python >= 3.7
>
> 2、Terraform >= 0.12

## 工具安装

    
    
    pip3 install checkov

### Alpine安装

    
    
    pip3 install --upgrade pip && pip3 install --upgrade setuptools
    
    pip3 install checkov

### Ubuntu 18.04安装

    
    
    sudo apt update
    
    sudo apt install software-properties-common
    
    sudo add-apt-repository ppa:deadsnakes/ppa
    
    sudo apt install python3.7
    
    sudo apt install python3-pip
    
    sudo python3.7 -m pip install -U checkov #to install or upgrade checkov)

### Homebrew安装（macOS）

    
    
    brew install checkov

或

    
    
    brew upgrade checkov

## 工具使用样例

执行两种特定的安全检测：

    
    
    checkov --directory . --check CKV_AWS_20,CKV_AWS_57

运行所有的检测（排除一个）：

    
    
    checkov -d . --skip-check CKV_AWS_20

运行所有中危或高危问题检测（需要API密钥）：

    
    
    checkov -d . --check MEDIUM --bc-api-key ...

运行所有中危或高危问题检测，并检测CKV_123：

    
    
    checkov -d . --check MEDIUM,CKV_123 --bc-api-key ...

跳过所有的中危或低危问题检测：

    
    
    checkov -d . --skip-check MEDIUM --bc-api-key ...

跳过所有的中危或低危问题，以及CKV_789的检测：

    
    
    checkov -d . --skip-check MEDIUM,CKV_789 --bc-api-key ...

## 工具配置

工具的配置文件config.yaml样例如下：

    
    
    branch: develop
    
    check:
    
      - CKV_DOCKER_1
    
    compact: true
    
    directory:
    
      - test-dir
    
    docker-image: sample-image
    
    dockerfile-path: Dockerfile
    
    download-external-modules: true
    
    evaluate-variables: true
    
    external-checks-dir:
    
      - sample-dir
    
    external-modules-download-path: .external_modules
    
    framework:
    
      - all
    
    no-guide: true
    
    output: cli
    
    quiet: true
    
    repo-id: bridgecrew/sample-repo
    
    skip-check:
    
      - CKV_DOCKER_3
    
      - CKV_DOCKER_2
    
    skip-fixes: true
    
    skip-framework:
    
      - dockerfile
    
      - secrets
    
    skip-suppressions: true
    
    soft-fail: true

我们可以通过命令行参数传递一个config配置文件的路径：

    
    
    checkov --config-file path/to/config.yaml

或者使用“--create-config”命令来创建一个配置文件：

    
    
    checkov --compact --directory test-dir --docker-image sample-image --dockerfile-path Dockerfile --download-external-modules True --external-checks-dir sample-dir --no-guide --quiet --repo-id bridgecrew/sample-repo --skip-check CKV_DOCKER_3,CKV_DOCKER_2 --skip-fixes --skip-framework dockerfile secrets --skip-suppressions --soft-fail --branch develop --check CKV_DOCKER_1 --create-config /Users/sample/config.yml

## 工具运行截图

![](https://image.3001.net/images/20220315/1647357346_6230ada2966d4042084d0.png!small)

![](https://image.3001.net/images/20220315/1647357354_6230adaa996ab2068a837.png!small)

![](https://image.3001.net/images/20220315/1647357365_6230adb515be68374666b.png!small)

![](https://image.3001.net/images/20220315/1647357405_6230addd36a841921e9aa.png!small)

## 许可证协议

本项目的开发与发布遵循[
_Apache-2.0_](https://github.com/bridgecrewio/checkov/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Checkov：** 【[ _GitHub传送门_](https://github.com/bridgecrewio/checkov)】

## 参考资料

> [ _https://docs.bridgecrew.io/docs/aws-policy-> index_](https://docs.bridgecrew.io/docs/aws-policy-index)
>
> [
> _https://github.com/bridgecrewio/checkov/blob/master/docs/1.Welcome/Quick%20Start.md_](https://github.com/bridgecrewio/checkov/blob/master/docs/1.Welcome/Quick%20Start.md)
>
> [ _https://bridgecrew.io/?utm_source=github
> &utm_medium=organic_oss&utm_campaign=checkov_](https://bridgecrew.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)


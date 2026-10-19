> Scorecard 是 OpenSSF 旗下的开源项目，用于评估开源软件风险，本文由该项目的主要贡献者 Naveen 撰写。

现代软件是建立在数百个甚至数千个第三方开源组件之上的，这些通常被称为依赖项。它们可以帮助开发团队快速迭代并保持生产力。

由于生产力的提升，大部分企业正在快速采用开源软件（OSS），导致承载关键任务的应用程序依赖于成千上万的直接和传递依赖项。随着开源软件包正在成为恶意用户的攻击目标，这些依赖项的健康状况已经成为整个供应链安全至关重要的部分。

一个依赖项的健康程度牵涉到诸多影响因素：它是否被良好维护？它是否经常更新？该项目是否有多个维护者？或者当其中一个维护者离开之后，这个项目是否会停止运转？在代码中是否有严重的漏洞？

无论何时，当你考虑要引入一个新的依赖项时，如果能获得该项目健康和安全程度的评分将帮助你评估该项目是否安全。那么 OpenSSF Scorecard
将是你的不二之选，在之前的文章中我们也对 [OpenSSF Scorecard
进行了拆解](https://mp.weixin.qq.com/s/KO52evTurLoJqo6HhrGCjw "OpenSSF Scorecard
进行了拆解")。目前，Seal 软件供应链防火墙已经集成 Scorecard，对用户扫描出来的漏洞进行评分，进而对其进行修复优先级的排序。

OpenSSF Scorecard
是一款自动化工具，用于评估与软件安全相关的几个重要启发式（heuristics）检查，并给每项检查从0-10分打分。这些分数有助于了解需要改善的具体环节，以加强依赖项的安全。

其中一些检查是：

  * 决定项目在PR合并之前是否需要代码审查

  * 检查项目的默认分支和发布分支是否受到 GitHub 的分支保护

  * 检查项目是否在源仓库生成可执行的二进制构件

诸如`envoy.proxy`、`tensorflow`和`flutter`等知名项目都在使用 Scorecard，以彰显他们的安全意识。

当前，Scorecards 每周扫描超过100万个代码仓库，扫描结果会被储存在
BigQuery（https://github.com/ossf/scorecard#public-data ）中。

# Scorecard API 发布

Scorecard API 已于本月初正式发布，它可以用于访问可用的数据集，这让 Scorecard 的能力更上一层楼。

地址：https://api.securityscorecards.dev

# 为什么 Scorecard API 如此有意义？

由于软件供应链对于整个项目的安全来说极其重要，因此最好能有一个明确的安全策略。在理想状况下，机器检查/强制执行可以确保新的依赖项的高质量标准，减缓不必要的依赖项增加，并解决结构性问题（如项目中所包含重复的依赖项、已知有问题的依赖项）。

我们的策略可以解决如下问题：

随着时间的推移，依赖项是如何变化的？

  * 那些依赖项做了什么？

  * 它们如何影响项目安全？

  * 它们如何更新？

  * 你如何限制你的暴露？

依赖项数量的快速增长会带来一些问题，比如难以跟踪：

  * 依赖项相对于其上游的陈旧程度

  * 是否有适用于项目依赖项的任何已知的常见漏洞和暴露（CVE）

  * 外部依赖项在多大程度上遵循最佳实践，例如，代码审查、更新依赖项、双因子认证（2FA）、漏洞披露过程、定期发布实践等

以下例子可以说明Envoy如何使用明确的外部依赖性策略：

https://github.com/envoyproxy/envoy/blob/main/DEPENDENCY_POLICY.md

# 使用 API 查看依赖项健康状况

如“木桶效应”所阐述的那样，一只水桶能装多少水取决于其最短的那块木板。软件供应链的健壮程度也取决于其最薄弱的环节。但是，在持续的时间范围内确定最薄弱的环节并非易事。接下来，我们将演示如何使用
Scorecard API 来评估 Golang 项目中的一组依赖项是否在其项目内部使用模糊测试，这是验证项目中是否存在零日漏洞的方法之一。

要解决这一问题会涉及到以下步骤：

1、 获取指定项目中的依赖项和传递依赖列表：

    
    
    // FetchDependencies parses the dependencies in the go.mod using the `go list command`
    // This functions expects the directory to contain the go.mod file.
    func FetchDependencies(directory string) ([]string, error) {
      modquery := `
      go list -m -f '{{if not (or  .Main)}}{{.Path}}{{end}}' all \
      | grep "^github" \
      | sort -u \
      | cut -d/ -f1-3 \
      | awk '{print $1}' \
      | tr '\n' ',' 
      `
      // Runs the modquery to generate the dependencies
      c := exec.Command("bash", "-c", fmt.Sprintf("cd %s;", directory)+modquery)
      data, err := c.Output()
      if err != nil {
        return nil, fmt.Errorf("failed to run go list: %w %s", err, string(data))
      }
      m := make(map[string]bool)
      parameters := []string{}
      result := append(parameters, strings.Split(string(data), ",")...)
      //filter the result to remove empty strings and duplicates
      for _, dep := range result {
        if dep != "" {
          m[dep] = true
        }
      }
      result = []string{}
      for dep := range m {
        result = append(result, dep)
      }
      return result, nil
    }
    

以上代码只是为演示准备的，不能在生产环境中使用。最后会返回项目中所有传递依赖项。

2、 接下来，该函数从 API 中获取 Scorecard 的结果，并检查某个项目是否经过模糊测试：

    
    
    func fuzzed(repo string) (bool, int, error) {
      //repo = "github.com/sigstore/sigstore"
      req, err := http.NewRequest("GET", fmt.Sprintf("https://api.securityscorecards.dev/projects/%s", repo), nil)
      if err != nil {
        panic(err)
      }
      req.Header.Set("Accept", "application/json")
    
      resp, err := http.DefaultClient.Do(req)
      if err != nil {
        return false, 0, err
      }
      defer resp.Body.Close()
      result, err := ioutil.ReadAll(resp.Body)
      if err != nil {
        return false, 0, err
      }
      var scorecard Scorecard
      err = json.Unmarshal(result, &scorecard)
      if err != nil {
        return true, 0, err
      }
      for _, check := range scorecard.Checks {
        if check.Name == "Fuzzing" {
          if check.Score >= 7 || check.Score < 0 {
            return true, check.Score, nil
          }
          return false, 0, nil
        }
      }
      return false, 0, nil
    }
    

3、 最后一步是将这两个函数结合起来，获得最终结果：

    
    
    func main() {
      repoLocation := os.Args[1]
      if repoLocation == "" {
        panic("repoLocation is empty")
      }
      dependencies, err := FetchDependencies(repoLocation)
      if err != nil {
        panic(err)
      }
      fmt.Println("Projects that are being fuzzed:")
      var ops uint64
      var wg sync.WaitGroup
    
      for _, dep := range dependencies {
        dependency := dep
        wg.Add(1)
        go func(dep string) {
          defer wg.Done()
          maintained, score, err := fuzzed(dependency)
          if err != nil {
            return
          }
          if maintained && score >= 7 {
            atomic.AddUint64(&ops, 1)
            fmt.Println(dependency, score)
          }
        }(dep)
      }
      wg.Wait()
      fmt.Println("-----------------")
      fmt.Println("Total number of dependencies :", len(dependencies))
      fmt.Println("The number of dependencies that are fuzzed :", ops)
    }
    

访问以下链接可以查看完整的工作实例：

https://github.com/naveensrinivasan/scorecard-api-demo

Scorecard 项目可以让用户更容易测量依赖项的健康程度，并根据其创建策略。而Scorecard API
让依赖项策略的自动化和执行都更轻松了。在未来的版本中，Seal 软件供应链防火墙计划集成 Scorecard API ，更好地保障用户依赖项安全。


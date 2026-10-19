现在API在软件趋势（例如移动应用程序、物联网等）中扮演着越来越重要的角色，对这些 API
进行适当的自动化测试变得不可或缺。有许多不同的工具可以帮助您在API 级别编写这些[
**自动化测试**](https://www.alltesting.cn/jsp/newVersion2/bigNews/alltestingAR.jsp
"自动化测试")。我将向您展示如何使用流行的开源工具之一来完成此任务：REST Assured。

REST Assured 是一个Java库，它提供了一种域特定语言(DSL)，用于为 RESTful API编写功能强大、可维护的[
**测试**](https://www.alltesting.cn/ "测试")。在以下部分中，我将向您展示如何设置和配置 REST
Assured、编写和运行 REST Assured 测试以及应用其一些强大的功能。我将使用真实世界的代码示例，您可以在自己的 **测试自动化**
工作中直接复制、运行和重用。

## 入门：配置

要开始使用REST Assured，只需将其作为依赖项添加到您的项目中即可。如果您使用的是Maven，请将以下条目添加到您的
pom.xml（更改版本号以反映您要使用的版本）：

`<dependency>  
<groupId>io.rest-assured</groupId>  
<artifactId>rest-assured</artifactId>  
<version>3.0.2</version>  
<scope>test</scope>  
</dependency>`

对于Gradle：

`testCompile 'io.rest-assured:rest-assured:3.0.2'`

REST Assured 可以轻松地与现有的[ **单元测试**](https://www.alltesting.cn/news/259.html
"单元测试")框架（例如 JUnit 和 TestNG）结合使用。对于本教程中提供的示例，我使用了 REST Assured 和 TestNG。

设置好 REST Assured 的导入后，将以下静态导入添加到您的测试类：

`import static io.restassured.RestAssured.*;  
import static org.hamcrest.Matchers.*;`

并且已准备好创建 REST Assured 测试。

## 测试：理解语法

在本教程中，我们将测试Ergast赛车数据库API，可在此处找到。此API提供与一级方程式比赛、车手、赛道等相关的历史数据。

为了说明使用 REST Assured 编写测试的方式，这里有一个测试，它以JSON格式检索 2017 年一级方程式赛季的赛道列表，并检查列表中是否有 20
个赛道：

`@Test  
public void test_NumberOfCircuitsFor2017Season_ShouldBe20() {  
  
given().  
when().  
get("http://ergast.com/api/f1/2017/circuits.json").  
then().  
assertThat().  
body("MRData.CircuitTable.Circuits.circuitId",hasSize(20));  
}`

请注意，REST Assured使用的 fluent API支持行为驱动开发(BDD) 中熟悉的 Given/When/Then
语法，从而使测试易于阅读并处理一切（设置、执行和验证）只需一行代码。

该hasSize（） Hamcrest匹配计数的数量电路，这就是为什么你需要对Hamcrest添加为静态导入。Hamcrest
库包含一组匹配器，允许您创建各种验证，同时保持它们的可读性。

测试的验证部分执行以下操作：

  1. 捕获 API 调用的 (JSON) 响应

  2. 使用 Groovy GPath 表达式“MRData.CircuitTable.Circuits.circuitId”查询所有名为 circuitId 的元素

  3. 验证（使用前面提到的 Hamcrest 匹配器）生成的 circuitId 元素集合的大小为 20

有Hamcrest匹配器用于大量不同的检查，包括equalTo（）平等，每种不超过（）和GREATERTHAN（）进行比较，hasItem（）来检查集合是否包含给定的元素，等等。有关匹配器的完整列表，请参考Hamcrest
库文档。

要运行测试，只需使用与您选择的[ **单元测试**](https://www.alltesting.cn/news/259.html "单元测试")框架（即
JUnit 或 TestNG）相关联的测试运行器。

## 验证技术响应数据

使用 REST Assured，您不仅可以验证响应正文内容，还可以检查技术响应数据的正确性，例如 HTTP
响应状态代码、响应内容类型和其他响应标头。下面的示例检查：

  * 响应状态代码等于 200。

  * 响应内容类型（告诉响应的接收者如何解释响应正文）等于“application/json”。

  * 响应头“Content-Length”的值等于“4567”。

`@Test  
public void test_ResponseHeaderData_ShouldBeCorrect() {  
  
given().  
when().  
get("http://ergast.com/api/f1/2017/circuits.json").  
then().  
assertThat().  
statusCode(200).  
and().  
contentType(ContentType.JSON).  
and().  
header("Content-Length",equalTo("4567"));  
}`这个例子还展示了如何使用and()方法以可读的方式轻松地连接检查，这只是语法糖，这意味着它所做的就是使代码更具可读性。

## 参数化测试

通常，您需要使用不同的（输入和输出）参数集重复相同的测试——这个概念被称为数据驱动测试。您不需要为每个测试数据记录编写新测试，而是希望创建一个参数化测试，并根据所需的测试覆盖率向其提供尽可能多的测试数据记录。

RESTful API 支持两种不同类型的参数：

  *  **查询参数：** 这些 **参数** 附加在 RESTful API 端点的末尾，可以通过它们前面的问号来识别。例如，在端点 http://md5.jsontest.com/?text=test 中，“text”是一个查询参数（值为“test”）。

  *  **路径参数：** 这些是 RESTful API 端点的一部分。比如我们之前使用的端点：http://ergast.com/api/f1/2017/circuits.json，“2017”就是一个路径参数值。尝试将其替换为“2016”，看看会发生什么（提示：之前的测试应该失败，因为 2016 年有 21 场一级方程式比赛，而不是 20 场）。

REST Assured 可以使用这两种类型的参数。首先，让我们看看如何指定和使用上面示例中的查询参数：

`@Test  
public void test_Md5CheckSumForTest_ShouldBe098f6bcd4621d373cade4e832627b4f6()
{  
  
String originalText = "test";  
String expectedMd5CheckSum = "098f6bcd4621d373cade4e832627b4f6";  
  
given().  
param("text",originalText).  
when().  
get("http://md5.jsontest.com").  
then().  
assertThat().  
body("md5",equalTo(expectedMd5CheckSum));  
}`

如您所见，在 REST Assured 中使用查询参数就像使用param()方法指定它们的名称和值一样简单。路径参数以类似的方式指定：

`@Test  
public void test_NumberOfCircuits_ShouldBe20_Parameterized() {  
  
String season = "2017";  
int numberOfRaces = 20;  
  
given().  
pathParam("raceSeason",season).  
when().  
get("http://ergast.com/api/f1/{raceSeason}/circuits.json").  
then().  
assertThat().  
body("MRData.CircuitTable.Circuits.circuitId",hasSize(numberOfRaces));  
}`

代替param()，路径参数是使用pathParam()方法定义的。此外，您需要定义端点路径的哪一部分代表路径变量，这是使用上面示例中看到的大括号表示法完成的。您可以以相同的方式轻松创建多个路径参数，如果
API 支持或需要，甚至可以在单个调用中组合路径和查询参数。

现在我们已经创建了一个参数化测试，通过使用外部测试数据集使其数据驱动是一项简单的任务。正如我在本教程开头所说的，使用 TestNG 容易做到这一点，但
JUnit 也支持参数化。使用
TestNG，您需要做的就是创建一个包含所需测试数据的DataProvider对象——在本例中，是一组包含年份和每年一级方程式比赛数量的记录：

`@DataProvider(name="seasonsAndNumberOfRaces")  
public Object[][] createTestDataRecords() {  
return new Object[][] {  
{"2017",20},  
{"2016",21},  
{"1966",9}  
};  
}`

然后你只需通过测试方法参数将测试数据对象传递给参数化测试：

`@Test(dataProvider="seasonsAndNumberOfRaces")  
public void test_NumberOfCircuits_ShouldBe_DataDriven(String season, int
numberOfRaces) {  
  
given().  
pathParam("raceSeason",season).  
when().  
get("http://ergast.com/api/f1/{raceSeason}/circuits.json").  
then().  
assertThat().  
body("MRData.CircuitTable.Circuits.circuitId",hasSize(numberOfRaces));  
}`

当您有一个测试数据对象时，您可以通过创建、删除或修改适当的测试数据记录来添加、删除或更新单个测试用例。如果测试本身需要更新——例如当端点或响应主体结构发生变化时——您需要做的就是更新测试，所有测试用例都将遵循更新的过程。

## 访问安全 API

通常，API使用某种身份验证机制来保护。REST Assured支持基本、摘要、表单和 OAuth 身份验证。下面是如何调用使用基本身份验证保护的
RESTful API 的示例（即，此 API 的使用者每次调用 API 时都需要提供有效的用户名和密码组合）：

`@Test  
public void test_APIWithBasicAuthentication_ShouldBeGivenAccess() {  
  
given().  
auth().  
preemptive().  
basic("username", "password").  
when().  
get("http://path.to/basic/secured/api").  
then().  
assertThat().  
statusCode(200);  
}`

假设您拥有有效的身份验证令牌，访问受 OAuth2 保护的 API 也同样简单：

`@Test  
public void test_APIWithOAuth2Authentication_ShouldBeGivenAccess() {  
  
given().  
auth().  
oauth2(YOUR_AUTHENTICATION_TOKEN_GOES_HERE).  
when().  
get("http://path.to/oath2/secured/api").  
then().  
assertThat().  
statusCode(200);  
}`

## 在测试之间传递参数

通常，在测试 RESTful API 时，您可能需要创建更复杂的测试场景，您需要从一个 API 调用的响应中捕获一个值并在后续调用中重用它。REST
Assured
使用extract()方法支持这一点。例如，这里有一个测试场景，它提取2017年一级方程式赛季一条赛道的ID，并使用它来检索和验证该赛道的附加信息（在本例中，赛道位于澳大利亚）：

`@Test  
public void
test_ScenarioRetrieveFirstCircuitFor2017SeasonAndGetCountry_ShouldBeAustralia()
{  
  
// First, retrieve the circuit ID for the first circuit of the 2017 season  
String circuitId = given().  
when().  
get("http://ergast.com/api/f1/2017/circuits.json").  
then().  
extract().  
path("MRData.CircuitTable.Circuits.circuitId[0]");  
  
// Then, retrieve the information known for that circuit and verify it is
located in Australia  
given().  
pathParam("circuitId",circuitId).  
when().  
get("http://ergast.com/api/f1/circuits/{circuitId}.json").  
then().  
assertThat().  
body("MRData.CircuitTable.Circuits.Location[0].country",equalTo("Australia"));  
}`

## 使用 ResponseSpecBuilder 重用检查

提高 RESTful API 测试的可重用性和可维护性的另一种方法是重用特定检查。例如，如果您想检查所有 API 响应的状态代码是否等于
200，内容类型是否等于“application/json”，那么为每个测试指定此项会很快让人厌烦。

此外，如果由于某种原因默认状态代码和内容类型返回了更改，那么只需在一个地方而不是整个测试套件中更新它不是很好吗？REST Assured 支持使用
ResponseSpecBuilder 机制重用特定的验证。

下面是一个示例，说明如何创建可重用的 ResponseSpecification 来检查上述状态代码和内容类型，以及如何在测试中使用它：

`ResponseSpecification checkStatusCodeAndContentType =  
new ResponseSpecBuilder().  
expectStatusCode(200).  
expectContentType(ContentType.JSON).  
build();`

`@Test  
public void test_NumberOfCircuits_ShouldBe20_UsingResponseSpec() {  
  
given().  
when().  
get("http://ergast.com/api/f1/2017/circuits.json").  
then().  
assertThat().  
spec(checkStatusCodeAndContentType).  
and().  
body("MRData.CircuitTable.Circuits.circuitId",hasSize(20));  
}`

除了使用 ResponseSpecification 之外，您还可以创建特定于该测试的检查。

## 其他的REST Assured功能

除了上面介绍的那些之外，REST Assured 还提供了许多其他有用的功能，让您可以创建更强大的测试，例如：

  * 能够（反）序列化普通旧 Java 对象 (POJO)。这允许您将与 Java 对象实例关联的属性和值直接序列化为 JSON 或 XML 文档，然后可以使用 POST 方法将其发送到 RESTful API。这也可以反过来工作——API 返回的 JSON 或 XML 响应也可以由 REST Assured 反序列化为 POJO 实例。

  * 记录请求和响应。当您需要检查 API 响应以创建适当的检查时，或者当您想确保发送到 API 的请求正确时，这尤其有用。您可以选择记录所有内容（参数、标题和正文）、仅记录标题、仅记录参数等等。

  * REST Assured 带有一个 Spring Mock MVC 模块，允许您使用 REST Assured 语法为 Spring 控制器编写测试。


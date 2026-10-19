**Author：Longofo@ Knownsec 404 Team**  
**Time: April 8, 2020**  
**Chinese version:<https://paper.seebug.org/1166/>**

Nexus Repository Manager 3 recently exposed two El expression parsing
vulnerabilities, [cve-2020-10199](https://support.sonatype.com/hc/en-us/articles/360044882533) and
[cve-2020-10204](https://support.sonatype.com/hc/en-us/articles/360044356194-cve-2020-10204-nexus-repository-manager-3-remote-code-execution-2020-03-31), both of which are found by GitHub security Lab
team's @pwntester. I didn't track the vulnerability of nexus3 before, so diff
had a headache at that time. In addition, the nexus3 bug and security fix are
all mixed together, which makes it harder to guess the location of the
vulnerability. Later, I reappeared
[cve-2020-10204](https://support.sonatype.com/hc/en-us/articles/360044356194-cve-2020-10204-nexus-repository-manager-3-remote-code-execution-2020-03-31) with @r00t4dm,
[cve-2020-10204](https://support.sonatype.com/hc/en-us/articles/360044356194-CVE-2020-10204-Nexus-Repository-Manager-3-Remote-Code-Execution-2020-03-31) is a bypass of
[cve-2018-16621](https://support.sonatype.com/hc/en-us/articles/360010789153-CVE-2018-16621-Nexus-Repository-Manager-Java-Injection-October-17-2018). After that, others reappeared
[cve-2020-10199](https://support.sonatype.com/hc/en-us/articles/360044882533).
The root causes of these three vulnerabilities are the same. In fact, there
are more than these three. The official may have fixed several such
vulnerabilities. Since history is not easy to trace back, it is only a
possibility. Through the following analysis, we can see it. There is also the
previous [CVE-2019-7238](https://support.sonatype.com/hc/en-us/articles/360017310793-CVE-2019-7238-Nexus-Repository-Manager-3-Missing-Access -Controls-and-Remote-Code-Execution-2019-02-05), this is a jexl
expression parsing, I will analyze it together here, explain the repair
problems to it. I have seen some analysis before, the article said that this
vulnerability was fixed by adding a permission. Maybe it was really only a
permission at that time, but the newer version I tested, adding the permission
seems useless. In the high version of Nexus3, the sandbox of jexl whitelist
has been used.

#### Test Environment

Three Nexus3 environments will be used in this article:

  * nexus-3.14.0-04
  * nexus-3.21.1-01
  * nexus-3.21.2-03

nexus-3.14.0-04 is used to test jexl expression parsing, nexus-3.21.1-01 is
used to test jexl expression parsing and el expression parsing and diff,
nexus-3.21.2-03 is used to test el expression Analysis and diff.

#### Vulnerability diff

The repair limit of CVE-2020-10199 and CVE-2020-10204 vulnerabilities is
3.21.1 and 3.21.2, but the github open source code branch does not seem to
correspond, so I have to download the compressed package for comparison. The
official download of nexus-3.21.1-01 and nexus-3.21.2-03, but beyond
comparison requires the same directory name, the same file name, and some
files for different versions of the code are not the same. I first decompiled
all the jar packages in the corresponding directory, and then used a script to
replace all the files in nexus-3.21.1-01 directory and the file name with
3.21.1-01 to 3.21.2-03, and deleted the META folder, this folder is not useful
for the vulnerability diff and affects the diff analysis, so it has been
deleted. The following is the effect after processing:

![](https://images.seebug.org/content/images/2020/04/5de5550c-f326-41fe-9690-27271f52763d.png-w331s)

If you have not debugged and familiar with the previous Nexus 3
vulnerabilities, it may be headache to look at diff. There is no target diff.

#### Routing and corresponding processing class

##### General routing

Grab the packet sent by nexus3, random, you can see that most requests are
POST type, URI is /service/extdirect:

![](https://images.seebug.org/content/images/2020/04/ba0b8050-eb86-4083-a349-73169335585d.png-w331s)

The content of the post is as follows:

    
    
    {"action":"coreui_Repository","method":"getBrowseableFormats","data":null,"type":"rpc","tid":7}

We can look at other requests. In post json, there are two keys: action and
method. Search for the keyword "coreui_Repository" in the code:

![](https://images.seebug.org/content/images/2020/04/6b48528b-85b7-4d71-8377-9df59b934365.png-w331s)

We can see this, expand and look at the code:

![](https://images.seebug.org/content/images/2020/04/93166ad5-b66c-41b6-b1ac-4c05abf2887c.png-w331s)

The action is injected through annotations, and the method
"getBrowseableFormats" in the post above is also included, the corresponding
method is injected through annotations:

![](https://images.seebug.org/content/images/2020/04/57b33edc-3c4b-4fe3-9acb-ef45b5be2161.png-w331s)

So after such a request,It is very easy to locate routing and corresponding
processing class.

##### API routing

The Nexus3 API also has a vulnerability. Let's see how to locate the API
route. In the admin web page, we can see all the APIs provided by Nexus3:

![](https://images.seebug.org/content/images/2020/04/4fa77acd-9740-4b59-b02e-7a36aeea64fc.png-w331s)

look at the package, there are GET, POST, DELETE, PUT and other types of
requests:

![](https://images.seebug.org/content/images/2020/04/144dcd27-7321-403c-8b19-9422b443621b.png-w331s)

Without the previous action and method, we use URI to locate it, but direct
search of /service/rest/beta/security/content-selectors cannot be located, so
shorten the keyword and use /beta/security/content-selectors to locate:

![](https://images.seebug.org/content/images/2020/04/f413efc8-0d5a-4573-9595-b0966d9646f0.png-w331s)

![](https://images.seebug.org/content/images/2020/04/3a66cf0b-9bfe-4450-a1d2-19b693d36cde.png-w331s)

Inject URI through @Path annotation, the corresponding processing method also
uses the corresponding @GET, @POST to annotate.

There are may be other types of routing, but you can also use a similar search
method to locate. There is also the permission problem of Nexus. You can see
that some of the above requests set the permissions through
@RequiresPermissions, but the actual test permissions are still prevailing.
Some permissions are also verified before arrival. Some operations are on the
admin page, but it may not require admin permissions, may be no need
permissions or only ordinary permissions.

#### Several Java EL vulnerabilities caused by
buildConstraintViolationWithTemplate

After debugging [CVE-2018-16621](https://support.sonatype.com/hc/en-us/articles/360010789153-CVE-2018-16621-Nexus-Repository-Manager-Java-Injection- October-17-2018) and
[CVE-2020-10204](https://support.sonatype.com/hc/en-us/articles/360044356194-CVE-2020-10204-Nexus-Repository-Manager-3- Remote-Code-Execution-2020-03-31), I feel that the keyword
`buildConstraintViolationWithTemplate` can be used as the root cause of this
vulnerability, because the call stack shows that the function call is on the
boundary between the Nexus package and the hibernate-validator package, and
the pop-up of the calculator is also after it enters the processing flow of
hibernate-validator, that is, `buildConstraintViolationWithTemplate (xxx)
.addConstraintViolation ()`, and finally expressed in the ElTermResolver class
in the hibernate-validator package through `valueExpression.getValue
(context)` :

![](https://images.seebug.org/content/images/2020/04/98ecc0d5-603d-45c8-acb7-63bafdd4eb1c.png-w331s)

So I decompile all jar packages of Nexus3, and then search for this keyword
(use the repair version search, mainly to see if there are any missing areas
that are not repaired; Nexue3 has some open source code, you can also search
directly in the source code):

    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\com\sonatype\nexus\plugins\nexus-healthcheck-base\3.21.2-03\nexus-healthcheck-base-3.21.2-03\com\sonatype\nexus\clm\validator\ClmAuthenticationValidator.java:
       26           return this.validate(ClmAuthenticationType.valueOf(iqConnectionXo.getAuthenticationType(), ClmAuthenticationType.USER), iqConnectionXo.getUsername(), iqConnectionXo.getPassword(), context);
       27        } else {
       28:          context.buildConstraintViolationWithTemplate("unsupported annotated object " + value).addConstraintViolation();
       29           return false;
       30        }
       ..
       35        case 1:
       36           if (StringUtils.isBlank(username)) {
       37:             context.buildConstraintViolationWithTemplate("User Authentication method requires the username to be set.").addPropertyNode("username").addConstraintViolation();
       38           }
       39  
       40           if (StringUtils.isBlank(password)) {
       41:             context.buildConstraintViolationWithTemplate("User Authentication method requires the password to be set.").addPropertyNode("password").addConstraintViolation();
       42           }
       43  
       ..
       52           }
       53  
       54:          context.buildConstraintViolationWithTemplate("To proceed with PKI Authentication, clear the username and password fields. Otherwise, please select User Authentication.").addPropertyNode("authenticationType").addConstraintViolation();
       55           return false;
       56        default:
       57:          context.buildConstraintViolationWithTemplate("unsupported authentication type " + authenticationType).addConstraintViolation();
       58           return false;
       59        }
    
    
    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\hibernate\validator\hibernate-validator\6.1.0.Final\hibernate-validator-6.1.0.Final\org\hibernate\validator\internal\constraintvalidators\hv\ScriptAssertValidator.java:
    34        if (!validationResult && !this.reportOn.isEmpty()) {
    35           constraintValidatorContext.disableDefaultConstraintViolation();
    36:          constraintValidatorContext.buildConstraintViolationWithTemplate(this.message).addPropertyNode(this.reportOn).addConstraintViolation();
    37        }
    38  
    
    
    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\hibernate\validator\hibernate-validator\6.1.0.Final\hibernate-validator-6.1.0.Final\org\hibernate\validator\internal\engine\constraintvalidation\ConstraintValidatorContextImpl.java:
       55     }
       56  
       57:    public ConstraintViolationBuilder buildConstraintViolationWithTemplate(String messageTemplate) {
       58        return new ConstraintValidatorContextImpl.ConstraintViolationBuilderImpl(messageTemplate, this.getCopyOfBasePath());
       59     }
    
    
    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-cleanup\3.21.0-02\nexus-cleanup-3.21.0-02\org\sonatype\nexus\cleanup\storage\config\CleanupPolicyAssetNamePatternValidator.java:
    18           } catch (RegexCriteriaValidator.InvalidExpressionException var4) {
    19              context.disableDefaultConstraintViolation();
    20:             context.buildConstraintViolationWithTemplate(var4.getMessage()).addConstraintViolation();
    21              return false;
    22           }
    
    
    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-cleanup\3.21.2-03\nexus-cleanup-3.21.2-03\org\sonatype\nexus\cleanup\storage\config\CleanupPolicyAssetNamePatternValidator.java:
       18           } catch (RegexCriteriaValidator.InvalidExpressionException var4) {
       19              context.disableDefaultConstraintViolation();
       20:             context.buildConstraintViolationWithTemplate(this.getEscapeHelper().stripJavaEl(var4.getMessage())).addConstraintViolation();
       21              return false;
       22           }
    
    
    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-scheduling\3.21.2-03\nexus-scheduling-3.21.2-03\org\sonatype\nexus\scheduling\constraints\CronExpressionValidator.java:
       29        } catch (IllegalArgumentException var4) {
       30           context.disableDefaultConstraintViolation();
       31:          context.buildConstraintViolationWithTemplate(this.getEscapeHelper().stripJavaEl(var4.getMessage())).addConstraintViolation();
       32           return false;
       33        }
    
    
    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-security\3.21.2-03\nexus-security-3.21.2-03\org\sonatype\nexus\security\privilege\PrivilegesExistValidator.java:
       42           if (!privilegeId.matches("^[a-zA-Z0-9\\-]{1}[a-zA-Z0-9_\\-\\.]*$")) {
       43              context.disableDefaultConstraintViolation();
       44:             context.buildConstraintViolationWithTemplate("Invalid privilege id: " + this.getEscapeHelper().stripJavaEl(privilegeId) + ". " + "Only letters, digits, underscores(_), hyphens(-), and dots(.) are allowed and may not start with underscore or dot.").addConstraintViolation();
       45              return false;
       46           }
       ..
       55        } else {
       56           context.disableDefaultConstraintViolation();
       57:          context.buildConstraintViolationWithTemplate("Missing privileges: " + missing).addConstraintViolation();
       58           return false;
       59        }
    
    
    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-security\3.21.2-03\nexus-security-3.21.2-03\org\sonatype\nexus\security\role\RoleNotContainSelfValidator.java:
       49              if (this.containsRole(id, roleId, processedRoleIds)) {
       50                 context.disableDefaultConstraintViolation();
       51:                context.buildConstraintViolationWithTemplate(this.message).addConstraintViolation();
       52                 return false;
       53              }
    
    
    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-security\3.21.2-03\nexus-security-3.21.2-03\org\sonatype\nexus\security\role\RolesExistValidator.java:
       42        } else {
       43           context.disableDefaultConstraintViolation();
       44:          context.buildConstraintViolationWithTemplate("Missing roles: " + missing).addConstraintViolation();
       45           return false;
       46        }
    
    
    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-validation\3.21.2-03\nexus-validation-3.21.2-03\org\sonatype\nexus\validation\ConstraintViolationFactory.java:
       75        public boolean isValid(ConstraintViolationFactory.HelperBean bean, ConstraintValidatorContext context) {
       76           context.disableDefaultConstraintViolation();
       77:          ConstraintViolationBuilder builder = context.buildConstraintViolationWithTemplate(this.getEscapeHelper().stripJavaEl(bean.getMessage()));
       78           NodeBuilderCustomizableContext nodeBuilder = null;
       79           String[] var8;

Later I saw the [Vulnerability
Analysis](https://github.com/Cryin/Paper/blob/master/CVE-2018-16621%20Nexus%20Repository%20Manager3%20%E4%BB%BB%E6%84%8FEL%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5.md)
published by the author, indeed used `buildConstraintViolationWithTemplate` as
the source of the vulnerability , use this key point to do tracking analysis.

As can be seen from the search results above, the three CVE key points caused
by the el expression are also among them, and there are several other places,
a few used `this.getEscapeHelper().StripJavaEl` , There are a few, it seems
ok, a ecstasy in my heart? However, although several other places that have
not been cleared and can be accessed by routing, they cannot be used. One of
them will be selected for analysis later. So at the beginning, I said that the
official may have fixed several similar places. I guess there are two
possibilities:

  * Officials have noticed that there are also el parsing vulnerabilities in those places, so they did a cleanup.
  * There are other vulnerability discoverers who submitted the cleared vulnerability points, because those places can be used; but the uncleared places cannot be used, so the discoverers did not submit, and the official did not go do clear

However, I feel that the latter possibility is more likely. After all, it is
unlikely that the official will clear some places, and some places will not do
it.

##### CVE-2018-16621 analysis

This vulnerability corresponds to the above search result is
RolesExistValidator. Since the key point is searched, I will manually reverse
the traceback to see if it can be traced back to the place where there is
routing processing. Here is a simple search traceback.

The key point is isValid in RolesExistValidator, which calls
buildConstraintViolationWithTemplate. Search if there is a place to call
RolesExistValidator:

![](https://images.seebug.org/content/images/2020/04/cb18302f-1a57-4a9a-8c99-7d2c4b03e6a8.png-w331s)

There is a call in RolesExist, this way of writing will generally use
RolesExist as a comment, and will call `RolesExistValidator.isValid ()` during
verification. Continue to search for RolesExist:

![](https://images.seebug.org/content/images/2020/04/7c07c99f-64e7-4311-b552-25f933cbc3c0.png-w331s)

There are several places that directly use RolesExist to annotate the roles
attribute. We can go back one by one, but according to the Role keyword,
RoleXO is more likely, so look at this (UserXO is also), continue to search
for RoleXO:

![](https://images.seebug.org/content/images/2020/04/74e2a7a6-ef3d-4a21-9fd6-719df97aa674.png-w331s)

There may be some other disturbances, such as the first red label
RoleXOResponse, this can be ignored, we find the place to use RoleXO directly.
In RoleComponent, if you see the second red annotation, you probably know that
you can enter the route here. The third red annotation uses roleXO and has the
roles keyword. RolesExist also annotates roles above, so the guess is
attribute injection to roleXO. The decompiled code in some places is not easy
to understand, you can look at the source code:

![](https://images.seebug.org/content/images/2020/04/2495a892-04db-4947-aa64-8d64347b8816.png-w331s)

It can be seen that the submitted parameters are injected into roleXO, and the
route corresponding to RoleComponent is as follows:

![](https://images.seebug.org/content/images/2020/04/0372a592-6bb3-46c8-af67-a4d6630a0613.png-w331s)

Through the above analysis, we probably know that we can enter the final
RolesExistValidator, but there are may be many conditions to be met in the
middle, we need to construct the payload and then measure it step by step. The
location of the web page corresponding to this route is as follows:

![](https://images.seebug.org/content/images/2020/04/8e4ebc01-2be3-4738-aaf9-6655e3eaaf01.png-w331s)

Test (the 3.21.1 version used here, CVE-2018-16621 is the previous
vulnerability, which was fixed earlier in 3.21.1, but 3.21.1 was bypassed
again, so the following is the bypass situation, will`$`Is replaced with`$ \\
x` to bypass):

![](https://images.seebug.org/content/images/2020/04/1da1e135-6b99-41b9-baa3-55ee83123130.png-w331s)

Repair method:

![](https://images.seebug.org/content/images/2020/04/5a92961a-faa1-4d1b-8035-caa73682940e.png-w331s)

Added `getEscapeHelper (). StripJavaEL` to clear the el expression,
replacing`$ {`with`{`, the next two CVEs are bypassing this fix:

![](https://images.seebug.org/content/images/2020/04/6d4d3915-97de-45fa-a2fb-200738ae82a5.png-w331s)

##### CVE-2020-10204 analysis

This is the bypass of the previous stripJavaEL repair mentioned above, and it
will not be analyzed here. The use of the `$\\x{` format will not be replaced
(tested with version 3.21.1):

![](https://images.seebug.org/content/images/2020/04/08bb559e-783e-41dd-a3f0-de223a6598c1.png-w331s)

##### CVE-2020-10199 analysis

This vulnerability corresponds to ConstraintViolationFactory in the search
results above:

![](https://images.seebug.org/content/images/2020/04/ee625dd0-8598-4f45-83f7-927fab6fcd87.png-w331s)

buildConstraintViolationWith (label 1) appears in the isValid of
HelperValidator class (label 2), HelperValidator is annotated on
HelperAnnotation (label 3, 4), HelperAnnotation is annotated on HelperBean
(label 5), on `ConstraintViolationFactory.createViolation` HelperBean (labels
6, 7) is used in the method. Follow this idea to find the place where
`ConstraintViolationFactory.createViolation` is called.

Let's also go back to the manual reverse trace to see if we can trace back to
where there is routing.

Search ConstraintViolationFactory:

![](https://images.seebug.org/content/images/2020/04/9fe0e978-03e7-4693-9161-7595e815dd93.png-w331s)

There are several, here uses the first BowerGroupRepositoriesApiResource
analysis, click to see that we can see that it is an API route:

![](https://images.seebug.org/content/images/2020/04/de188c9c-b3bb-47cb-b1e7-e6d6832d6d41.png-w331s)

ConstraintViolationFactory was passed to super, and other functions of
ConstraintViolationFactory were not called in
BowerGroupRepositoriesApiResource, but its two methods also called super
corresponding methods. Its super is AbstractGroupRepositoriesApiResource
class:

![](https://images.seebug.org/content/images/2020/04/40435bb6-04eb-4ee9-9f5d-f70ee93a50ee.png-w331s)

The super called in the BowerGroupRepositoriesApiResource constructor assigns
ConstraintViolationFactory (label 1) in AbstractGroupRepositoriesApiResource,
the use of ConstraintViolationFactory (label 2), and calls createViolation (we
can see the memberNames parameter), which is needed to reach the vulnerability
point. This call is in validateGroupMembers (label 3). The call to
validateGroupMembers is called in both createRepository (label 4) and
updateRepository (label 5), and these two methods can also be seen from the
above annotations that they are routing methods.

The route of BowerGroupRepositoriesApiResource is
/beta/repositories/bower/group, find it in the admin page APIs to make a call
(use 3.21.1 test):

![](https://images.seebug.org/content/images/2020/04/de26da22-c1dc-40a6-b6f6-f9112e1ff1a9.png-w331s)

Several other subclasses of AbstractGroupRepositoriesApiResource are the same:

![](https://images.seebug.org/content/images/2020/04/8c41bbfb-2f72-4cb5-a046-61916fed2379.png-w331s)

##### CleanupPolicyAssetNamePatternValidator does not do cleanup point
analysis

Corresponding to the CleanupPolicyAssetNamePatternValidator in the search
results above, we can see that there is no StripEL removal operation here:

![](https://images.seebug.org/content/images/2020/04/fd94d365-4c14-43e6-bcde-24e977a06250.png-w331s)

This variable is thrown into buildConstraintViolationWithTemplate through an
error report. If the error message contains the value, then it can be used
here.

Search CleanupPolicyAssetNamePatternValidator:

![](https://images.seebug.org/content/images/2020/04/5cfd7107-8220-41ed-a99f-3f4c200fe6cf.png-w331s)

Used in CleanupPolicyAssetNamePattern class annotation, continue to search for
CleanupPolicyAssetNamePattern:

![](https://images.seebug.org/content/images/2020/04/158622ca-da43-4a1f-8498-7ada7a550102.png-w331s)

The attribute regex in CleanupPolicyCriteria is annotated by
CleanupPolicyAssetNamePattern, and continue to search for
CleanupPolicyCriteria:

![](https://images.seebug.org/content/images/2020/04/62cd5e98-6101-4c6f-a619-fa142c9146cb.png-w331s)

![](https://images.seebug.org/content/images/2020/04/e1f146ed-a7d5-447b-ab09-da96516236a6.png-w331s)

Called in the toCleanupPolicy method in CleanupPolicyComponent, where
`cleanupPolicyXO.getCriteria` also happens to be CleanupPolicyCriteria object.
toCleanupPolicy calls toCleanupPolicy in the createup and previewCleanup
methods of the CleanupPolicyComponent that can be accessed through routing.

Construct the payload test:

![](https://images.seebug.org/content/images/2020/04/c5e37eac-e5eb-4dcd-9f70-5d73f5e904a8.png-w331s)

![](https://images.seebug.org/content/images/2020/04/d267f217-01bd-44c5-98ea-46ed507dd0dd.png-w331s)

However, it cannot be used here, and the value value will not be included in
the error message. After reading RegexCriteriaValidator.validate, no matter
how it is constructed, it will only throw a character in the value, so it
cannot be used here.

Similar to this is the CronExpressionValidator, which also throws an exception
there, it can be used, but it has been fixed, and someone may have submitted
it before. There are several other places that have not been cleared,but
either skipped by if or else, or cannot be used.

The way of manual backtracking search may be okay if there are not many places
where the keyword is called, but if it is used a lot, it may not be so easy to
deal with. However, for the above vulnerabilities, we can see that it is still
feasible to search through manual backtracking.

#### Vulnerabilities caused by JXEL (CVE-2019-7238)

we can refer to @iswin's previous analysis
<https://www.anquanke.com/post/id/171116>, here is no longer going Debugging
screenshots. Here I want to write down the previous fix for this
vulnerability, saying that it was added with permission to fix it. If only the
permission is added, can it still be submitted? However, after testing version
3.21.1, even with admin permissions can not be used, I want to see if it can
be bypassed. Tested in 3.14.0, it is indeed possible:

![](https://images.seebug.org/content/images/2020/04/4ed3933f-dfa5-429d-ab52-7cc3106ca44f.png-w331s)

But in 3.21.1, even if the authority is added, it will not work. Later, I
debug and compare separately, and pass the following test:

    
    
    JexlEngine jexl = new JexlBuilder().create();
    
    String jexlExp = "''.class.forName('java.lang.Runtime').getRuntime().exec('calc.exe')";
    JexlExpression e = jexl.createExpression(jexlExp);
    JexlContext jc = new MapContext();
    jc.set("foo", "aaa");
    
    e.evaluate(jc);

I learned that 3.14.0 and the above test used
`org.apache.commons.jexl3.internal.introspection.Uberspect` processing, and
its getMethod method is as follows:

![](https://images.seebug.org/content/images/2020/04/9a27cbe9-819a-46d2-8bb5-62e538d80cec.png-w331s)

In 3.21.1, Nexus is set to
`org.apache.commons.jexl3.internal.introspection.SandboxJexlUberspect`, this
SandboxJexlUberspect, its getMethod method is as follows:

![](https://images.seebug.org/content/images/2020/04/8d741754-50d5-4f47-a6a4-42c433adeac1.png-w331s)

![](https://images.seebug.org/content/images/2020/04/d18458c4-96c3-4b7f-be5d-08c3a414f1f3.png-w331s)

It can be seen that only a limited number of methods of type String, Map, and
Collection are allowed.

#### Conclusion

  * After reading the above content, I believe that we have a general understanding of the Nexus3 loopholes, and you will no longer feel that you can't start. Try to look at other places, for example, there is an LDAP in the admin page, which can be used for jndi connect operation, but the `context.getAttribute` is called there. Although the class file will be requested remotely, the class will not be loaded, so there is no harm.
  * The root cause of some vulnerabilities may appear in a similar place in an application, just like the keyword `buildConstraintViolationWithTemplate` above, good luck maybe a simple search can encounter some similar vulnerabilities (but my luck looks bad Click, we can see the repair in some places through the above search, indicating that someone has already taken a step forward, directly called `buildConstraintViolationWithTemplate` and the available places seem to be gone)
  * Look closely at the payloads of the above vulnerabilities, it seems that the similarity is very high, so we can get a tool similar to fuzz parameters to collect the historical vulnerability payload of this application, each parameter can test the corresponding payload, good luck may be Hit some similar vulnerabilities.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1167/>


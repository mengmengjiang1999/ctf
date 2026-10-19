## 0x00 概述

近期，国外研究员Daniel 'f0o' Preussker报告了OpenStack组件Keystone Credentials
API中的一处缺陷。当Keystone 的部署配置中将`enforce_scope`设置为`False`时，`list
credentials`接口的相关过滤操作失效，导致在操作的`project`中拥有角色的用户可以获取该`project`下的所有用户`credentials`，造成信息泄露。

## 0x01 影响范围

Keystone <= 15.0.0 and <=16.0.0

## 0x02 漏洞修复

相关修复代码已经合并到主分支，详见[Commit](https://opendev.org/openstack/keystone/commit/17c337dbdbfb9d548ad531c2ad0483c9bce5b98f)。

## 0x03 漏洞分析

该漏洞产生的源于将`enforce_scope`的配置值引入了凭据结果过滤的操作判断逻辑中，当其取`False`时造成对应处理逻辑绕过，进而造成信息泄露
。补丁的修复也是对该部分逻辑进行了变更，详细如下：

    
    
            # /keystone/api/credentials.py
            def _list_credentials(self):
            filters = ['user_id', 'type']
            if not self.oslo_context.system_scope:
                target = {'credential': {'user_id': self.oslo_context.user_id}}
            else:
                target = None
            ENFORCER.enforce_call(action='identity:list_credentials',
                                  filters=filters, target_attr=target)
            hints = self.build_driver_hints(filters)
            refs = PROVIDERS.credential_api.list_credentials(hints) 
            # If the request was filtered, make sure to return only the
            # credentials specific to that user. This makes it so that users with
            # roles on projects can't see credentials that aren't theirs.
    -        if (not self.oslo_context.system_scope and
    -                CONF.oslo_policy.enforce_scope): 
    -            filtered_refs = []
    -            for ref in refs:
    -                if ref['user_id'] == target['credential']['user_id']:
    -                    filtered_refs.append(ref)
    -            refs = filtered_refs
    +        filtered_refs = []
    +        for ref in refs:
    +            # Check each credential again to make sure the user has access to
    +            # it, either by owning it, being a project admin with
    +            # enforce_scope=false, being a system user, or having some other
    +            # custom policy that allows access.
    +            try:
    +                cred = PROVIDERS.credential_api.get_credential(ref['id'])
    +                ENFORCER.enforce_call(
    +                    action='identity:get_credential',
    +                    target_attr={'credential': cred}
    +                )
    +                filtered_refs.append(ref)
    +            except exception.Forbidden:
    +                pass
    +       refs = filtered_refs
            refs = [self._blob_to_json(r) for r in refs]
            return self.wrap_collection(refs, hints=hints)
    

漏洞成因较为简单，但可以借此一窥Keystone API以及OpenStak背后的一些底层组件以及处理逻辑：

`Oslo` 维护了一套公共库，实现了OpenStack各项目中用到的共有功能，避免了各项目重复造轮子。
产生本次漏洞的`enforce_scope`选项即为其中的`oslo_policy`所需的配置项，该库为OpenStack各项目中`基于角色的访问控制`(RBAC:
Role-Based Access
Control）功能提供实施策略的支持。具体地，`enforce_scope`对应于请求验证过程中对特定异常处理的控制（请求与`scope_type`允许范围不匹配时，抛出异常或记日志）。

`oslo.policy`通过以下两个类实现各项功能支持：

  * `oslo_policy.policy.RuleDefault`: 用于定义检查策略/规则。
  * `oslo_policy.policy.Enforcer` : 负责加载和执行规则/策略

这两个类也对应oslo.policy的两个入口点：`oslo.policy.policies`和`oslo.policy.enforcer`

当服务发起一定操作时，由`Enforce`加载并执行`Policy`，完成对操作的鉴权和访问控制。

如下为`Credentials
API`中`list_credentials`的一个`oslo_policy.policy.DocumentedRuleDefault`(继承`RuleDefault`)实例，记录了一个`policy
enforcement`的相关策略：

    
    
     policy.DocumentedRuleDefault(
            name=base.IDENTITY % 'list_credentials',
            check_str=base.SYSTEM_READER_OR_CRED_OWNER,
            scope_types=['system', 'project'],  # scope of the operation
            description='List credentials.',
            operations=[{'path': '/v3/credentials',
                         'method': 'GET'}],
            deprecated_rule=deprecated_list_credentials,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since=versionutils.deprecated.STEIN
        ),
    

其中:

  * `name`: `policy`名称
  * `check_str`: `policy`的策略规则表达式。
  * `scope_types`: 规定了`operate`的作用范围。策略执行阶段，会将此值与请求中`token`对应的scope进行比对，进行控制。
  * `description`: 描述
  * `operations`: 操作属性
  * `deprecated_rule`: 用于 `Policy Deprecation Managerment`，比如对旧名的替换。
  * `deprecated_reason`: 弃用原因
  * `deprecated_since`: 弃用版本节点

## 0x04 参考

  1. [oslo.policy](https://docs.openstack.org/oslo.policy/train/)
  2. [policy deprecation](https://specs.openstack.org/openstack/oslo-specs/specs/queens/policy-deprecation.html)
  3. [Credentials API allows listing and retrieving of all users credentials](https://bugs.launchpad.net/keystone/+bug/1855080)
  4. [Fix Review](https://review.opendev.org/#/c/697355/)
  5. [Commitdiff](https://review.opendev.org/gitweb?p=openstack%2Fkeystone.git;a=commitdiff;h=17947516b0095c51da5cff94771247f2e7c44ee6)
  6. [KeyStone Document](https://docs.openstack.org/api-ref/identity/index.html)


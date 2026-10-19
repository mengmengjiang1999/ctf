作者：Ricter Z  
作者博客：<https://ricterz.me/posts/Drupal%207%20-%20CVE-2018-7600%20PoC%20Writeup>

#### 0x00 前言

前几天我分析了 Drupal 8.5.0 的 PoC 构造方法，但是 Drupal 7 还是仍未构造出 PoC。今天看到了
[Drupalgeddon2](https://github.com/dreadlocked/Drupalgeddon2/blob/master/drupalgeddon2.rb
"Drupalgeddon2") 支持了 Drupal 7 的 Exploit，稍微分析了下，发现 PoC 构建的十分精妙，用到了诸多 Drupal
本身特性，我构造不出果然还是太菜。

首先，Drupal 7 和 Drupal 8 这两个 PoC 本质上是同一原因触发的，我说的同一个原因并不是像是 `#pre_render` 的
callback 这样，而是都是由于 `form_parent` 导致 Drupal 遍历到用户控制的 `#value`，接着进行 render 的时候导致
RCE。Drupal 8 中的 `element_parents` 十分明显，且从 `$_GET` 中直接获取，所以很容易的能分析出来，而 Drupal 7
中的 `form_parent` 就藏得比较隐晦了。

那么，这个 PoC 用到了 Drupal 中的哪些特性呢？

  * Drupal 的 router 传参

  * Drupal 的 form cache

那么，先从 router 讲起。

#### 0x01 Router

当访问 `file/ajax/name/#default_value/form-xxxx` 的时候，在 `menu.inc` 中，Drupal
是这样处理的：

    
    
    function menu_get_item($path = NULL, $router_item = NULL) {
      $router_items = &drupal_static(__FUNCTION__);
      if (!isset($path)) {
        $path = $_GET['q'];
      }
        var_dump($router_items);
      if (isset($router_item)) {
        $router_items[$path] = $router_item;
      }
      if (!isset($router_items[$path])) {
        // Rebuild if we know it's needed, or if the menu masks are missing which
        // occurs rarely, likely due to a race condition of multiple rebuilds.
        if (variable_get('menu_rebuild_needed', FALSE) || !variable_get('menu_masks', array())) {
          if (_menu_check_rebuild()) {
            menu_rebuild();
          }
        }
        $original_map = arg(NULL, $path);
    
        $parts = array_slice($original_map, 0, MENU_MAX_PARTS);
        $ancestors = menu_get_ancestors($parts);
        $router_item = db_query_range('SELECT * FROM {menu_router} WHERE path IN (:ancestors) ORDER BY fit DESC', 0, 1, array(':ancestors' => $ancestors))->fetchAssoc();
    
        if ($router_item) {
          // Allow modules to alter the router item before it is translated and
          // checked for access.
          drupal_alter('menu_get_item', $router_item, $path, $original_map);
    
          $map = _menu_translate($router_item, $original_map);
          $router_item['original_map'] = $original_map;
          if ($map === FALSE) {
            $router_items[$path] = FALSE;
            return FALSE;
          }

看不动？没关系，我来解释下：

  * 从 `$_GET["q"]` 取出 path；
  * 将 path 分割后进行组合，得到一个数组；
  * 数组进入数据库查询；

组合的结果大概是这样：

    
    
    0 = file/ajax/name/#default_value/form-xxxx
    1 = file/ajax/name/#default_value/%
    2 = file/ajax/name/%/form-xxxxx
    3 = file/ajax/name/%/%
    4 = file/ajax/%/%/%
    5 = file/%/name/%/form-xxxxx
    ....
    12 = file/%/name
    13 = file/ajax
    14 = file/%
    15 = file

这些是什么呢？实际上这些是 Drupal 的 router，在数据库的 menu_router 表里。这么一串 array 最终和数据库中的
`file/ajax` 相匹配。Drupal 会根据数据库中的 `page_callback` 进行回调，也就是回调到 `file_ajax_upload`
函数。回调的现场：

![](https://images.seebug.org/content/images/2018/04/19da3cd6-c3c8-4a07-bdf5-a55b6a5ceb64.png-w331s)

可以注意到回调的参数为我们 `$_GET["q"]` 剩下的 `name/#default_value/form-xxxx`。

#### 0x02 file_ajax_upload

`file_ajax_upload` 即漏洞触发点了，直接分析代码就好。

    
    
    function file_ajax_upload() {
      $form_parents = func_get_args();
      $form_build_id = (string) array_pop($form_parents);
    
      if (empty($_POST['form_build_id']) || $form_build_id != $_POST['form_build_id']) {
          ...
      }
    
      list($form, $form_state, $form_id, $form_build_id, $commands) = ajax_get_form();
    
      if (!$form) {
          ...
      }
    
      // Get the current element and count the number of files.
      $current_element = $form;
      foreach ($form_parents as $parent) {
        $current_element = $current_element[$parent];
      }
      $current_file_count = isset($current_element['#file_upload_delta']) ? $current_element['#file_upload_delta'] : 0;
    
      // Process user input. $form and $form_state are modified in the process.
      drupal_process_form($form['#form_id'], $form, $form_state);
    
      // Retrieve the element to be rendered.
      foreach ($form_parents as $parent) {
        $form = $form[$parent];
      }
    
      // Add the special Ajax class if a new file was added.
      if (isset($form['#file_upload_delta']) && $current_file_count < $form['#file_upload_delta']) {
        $form[$current_file_count]['#attributes']['class'][] = 'ajax-new-content';
      }
      // Otherwise just add the new content class on a placeholder.
      else {
        $form['#suffix'] .= '<span class="ajax-new-content"></span>';
      }
    
      $form['#prefix'] .= theme('status_messages');
      $output = drupal_render($form);

这段代码的作用为：

  1. 获取参数的最后一个值作为 `$form_build_id`，验证这个值和 `$_POST["form_build_id"]` 是否相等；
  2. 通过 `$form_build_id` 从`ajax_get_form`获取被缓存的 `$form`；
  3. `foreach ($form_parents as $parent)` 这个循环即和 Drupal 8 中的 `NestedArray::getValue` 异曲同工，将 `$form` 中的值按照 `name/#default_value` 的路径取出；
  4. 最后，`drupal_render($form);` 进行渲染，这是漏洞的最终触发点，不做详细分析。

这是一个获取到最终 $form 的现场：

![](https://images.seebug.org/content/images/2018/04/a97cba47-a923-47b4-b2f4-a633dead2d99.png-w331s)

#### 0x03 Form Cache

现在的问题是怎么得到一个被缓存的 `$form`。首先我们 POST 一个找回密码的请求包，内容如下：

![](https://images.seebug.org/content/images/2018/04/40b72fba-51f2-4c87-acd4-edcfbc8d4175.png-w331s)

通过分析代码，可以得知，若想 `$form` 被 cache，需要满足以下几个条件：

    
    
        if (($form_state['rebuild'] || !$form_state['executed']) && !form_get_errors()) {
          // Form building functions (e.g., _form_builder_handle_input_element())
          // may use $form_state['rebuild'] to determine if they are running in the
          // context of a rebuild, so ensure it is set.
          $form_state['rebuild'] = TRUE;
          $form = drupal_rebuild_form($form_id, $form_state, $form);
        }

`drupal_rebuild_form` 中：

    
    
    function drupal_rebuild_form($form_id, &$form_state, $old_form = NULL) {
      $form = drupal_retrieve_form($form_id, $form_state);
      ....
      if (empty($form_state['no_cache'])) {
        form_set_cache($form['#build_id'], $form, $form_state);
      }

在诸多条件中，`($form_state['rebuild'] || !$form_state['executed'])` 是默认就被满足的，唯一的问题是
`form_get_errors()` 会出现问题。由于我们 POST 的 name 需要注入 payload，那么必然会验证失败。

![](https://images.seebug.org/content/images/2018/04/800000a3-85d2-43ff-ae54-263148ca5d0f.png-w331s)

如上图所示，`form_get_errors`返回了一个错误信息。我们跟进`form_set_errors` 看一看，这个函数名字像是设置错误信息的函数。

    
    
    function form_set_error($name = NULL, $message = '', $limit_validation_errors = NULL) {
      $form = &drupal_static(__FUNCTION__, array());
      $sections = &drupal_static(__FUNCTION__ . ':limit_validation_errors');
      if (isset($limit_validation_errors)) {
        $sections = $limit_validation_errors;
      }
    
      if (isset($name) && !isset($form[$name])) {
        $record = TRUE;
        if (isset($sections)) {
          // #limit_validation_errors is an array of "sections" within which user
          // input must be valid. If the element is within one of these sections,
          // the error must be recorded. Otherwise, it can be suppressed.
          // #limit_validation_errors can be an empty array, in which case all
          // errors are suppressed. For example, a "Previous" button might want its
          // submit action to be triggered even if none of the submitted values are
          // valid.
          $record = FALSE;
          foreach ($sections as $section) {
            // Exploding by '][' reconstructs the element's #parents. If the
            // reconstructed #parents begin with the same keys as the specified
            // section, then the element's values are within the part of
            // $form_state['values'] that the clicked button requires to be valid,
            // so errors for this element must be recorded. As the exploded array
            // will all be strings, we need to cast every value of the section
            // array to string.
            if (array_slice(explode('][', $name), 0, count($section)) === array_map('strval', $section)) {
              $record = TRUE;
              break;
            }
          }
        }
        if ($record) {
          $form[$name] = $message;
          if ($message) {
            drupal_set_message($message, 'error');
          }
        }
      }
    
      return $form;
    }

注意到这个 `$record` 变量。当 `$sections` 也就是通过 `isset` 函数检测时（也就是不为 null），`$record`
就会设置为 FALSE，也就不会进行错误的记录。通过查阅 `form.inc` 的代码，我注意到第 1412 行有如下代码：

    
    
    if (isset($form_state['triggering_element']['#limit_validation_errors']) && ($form_state['triggering_element']['#limit_validation_errors'] !== FALSE) && !($form_state['submitted'] && !isset($form_state['triggering_element']['#submit']))) {
      form_set_error(NULL, '', $form_state['triggering_element']['#limit_validation_errors']);
    }
    // If submit handlers won't run (due to the submission having been triggered
    // by an element whose #executes_submit_callback property isn't TRUE), then
    // it's safe to suppress all validation errors, and we do so by default,
    // which is particularly useful during an Ajax submission triggered by a
    // non-button. An element can override this default by setting the
    // #limit_validation_errors property. For button element types,
    // #limit_validation_errors defaults to FALSE (via system_element_info()),
    // so that full validation is their default behavior.
    elseif (isset($form_state['triggering_element']) && !isset($form_state['triggering_element']['#limit_validation_errors']) && !$form_state['submitted']) {
      form_set_error(NULL, '', array());
    }
    // As an extra security measure, explicitly turn off error suppression if
    // one of the above conditions wasn't met. Since this is also done at the
    // end of this function, doing it here is only to handle the rare edge case
    // where a validate handler invokes form processing of another form.
    else {
        //form_set_error(NULL, '', array()); // set _triggering_element_name
        drupal_static_reset('form_set_error:limit_validation_errors');
    }

当我们普通的 POST 的时候，会进入普通的最后的 else 分支，但是如果满足：

    
    
    (isset($form_state['triggering_element']) && !isset($form_state['triggering_element']['#limit_validation_errors']) && !$form_state['submitted']

这个条件时，就会调用：

    
    
    form_set_error(NULL, '', array());

这样调用的话，`$limit_validation_errors` 就是 Array，可以通过 `isset`，不会记录错误。我们来看一下这三个条件：

  1. `isset($form_state['triggering_element'])`，默认为 submit 按钮，true
  2. `!isset($form_state['triggering_element']['#limit_validation_errors'])` ，默认设置了这个值，false
  3. `!$form_state['submitted']`，默认为 false

看起来形式严峻。首先我在将所有 `$form_state['submitted']` 设置为 TRUE 的地方设置了断点，单步调试后发现断在了这个位置：

    
    
        // 如果没设置 triggering_element，那么将 triggering_element 设置为 form 的第一个 button
        if (!$form_state['programmed'] && !isset($form_state['triggering_element']) && !empty($form_state['buttons'])) {
          $form_state['triggering_element'] = $form_state['buttons'][0];
        }
    
        // If the triggering element specifies "button-level" validation and submit
        // handlers to run instead of the default form-level ones, then add those to
        // the form state.
        foreach (array('validate', 'submit') as $type) {
          if (isset($form_state['triggering_element']['#' . $type])) {
            $form_state[$type . '_handlers'] = $form_state['triggering_element']['#' . $type];
          }
        }
    
        // If the triggering element executes submit handlers, then set the form
        // state key that's needed for those handlers to run.
        if (!empty($form_state['triggering_element']['#executes_submit_callback'])) {
          #################################################
          $form_state['submitted'] = TRUE; // <--- こ↑こ↓
          #################################################
        }

又是 triggering_element，这到底是什么东西？看代码写的，如果没设置 triggering_element，那么将
triggering_element 设置为 form 的第一个 button。我搜索了设置
`$form_state['triggering_element']` 的代码：

    
    
      // Determine which element (if any) triggered the submission of the form and
      // keep track of all the clickable buttons in the form for
      // form_state_values_clean(). Enforce the same input processing restrictions
      // as above.
      if ($process_input) {
              // Detect if the element triggered the submission via Ajax.
              if (_form_element_triggered_scripted_submission($element, $form_state)) {
                  $form_state['triggering_element'] = $element;
              }
    
        // If the form was submitted by the browser rather than via Ajax, then it
        // can only have been triggered by a button, and we need to determine which
        // button within the constraints of how browsers provide this information.
        if (isset($element['#button_type'])) {
          // All buttons in the form need to be tracked for
          // form_state_values_clean() and for the form_builder() code that handles
          // a form submission containing no button information in $_POST.
          $form_state['buttons'][] = $element;
          if (_form_button_was_clicked($element, $form_state)) {
            $form_state['triggering_element'] = $element;
          }
        }
      }

进入`_form_element_triggered_scripted_submission`：

    
    
    /**
     * Detects if an element triggered the form submission via Ajax.
     *
     * This detects button or non-button controls that trigger a form submission via
     * Ajax or some other scriptable environment. These environments can set the
     * special input key '_triggering_element_name' to identify the triggering
     * element. If the name alone doesn't identify the element uniquely, the input
     * key '_triggering_element_value' may also be set to require a match on element
     * value. An example where this is needed is if there are several buttons all
     * named 'op', and only differing in their value.
     */
    function _form_element_triggered_scripted_submission($element, &$form_state) {
      if (!empty($form_state['input']['_triggering_element_name']) && $element['#name'] == $form_state['input']['_triggering_element_name']) {
        if (empty($form_state['input']['_triggering_element_value']) || $form_state['input']['_triggering_element_value'] == $element['#value']) {
          return TRUE;
        }
      }
      return FALSE;
    }

这段代码的意思是，如果用户输入的 `_triggering_element_value` 和 `$element['#name']`
相等，那么就万事大吉了。那么，我将 POST 的 `_triggering_element_name` 设置成
name，在此处下一个断点，获取到的现场如下：

![](https://images.seebug.org/content/images/2018/04/a3dcb9d6-c57a-4ce3-b3fe-5481793f1608.png-w331s)

`$form_state['triggering_element']` 果然变成了 name 元素。继续单步：

![](https://images.seebug.org/content/images/2018/04/8faffb3a-f728-4fdb-8c2b-ab617c981868.png-w331s)

发现此处三个条件都满足，执行了：

    
    
    form_set_error(NULL, '', array());

继续跟进：

![](https://images.seebug.org/content/images/2018/04/4e0eae66-f165-4d13-bf72-0a7c60b5f048.png-w331s)

进入缓存设置函数。最终查看数据库：

![](https://images.seebug.org/content/images/2018/04/cec74e87-1192-40b2-b952-e736284a3945.png-w331s)

#### 0x04 Inject # to Form

现在我们可以得到一个被缓存的 `$form`，但是，这个被缓存的 `$form` 并没有注入我们想要的数组，所以也就不能通过 `0x02`
所述的漏洞触发点进行触发。现在的问题是，如何将我们的 payload 注入到 `$form` 里。

单步跟入到 `user_pass` 函数：

    
    
    function user_pass() {
      global $user;
    
      $form['name'] = array(
        '#type' => 'textfield',
        '#title' => t('Username or e-mail address'),
        '#size' => 60,
        '#maxlength' => max(USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH),
        '#required' => TRUE,
        '#default_value' => isset($_GET['name']) ? $_GET['name'] : '',
      );
      // Allow logged in users to request this also.
      if ($user->uid > 0) {
        $form['name']['#type'] = 'value';
        $form['name']['#value'] = $user->mail;
        $form['mail'] = array(
          '#prefix' => '<p>',
          // As of https://www.drupal.org/node/889772 the user no longer must log
          // out (if they are still logged in when using the password reset link,
          // they will be logged out automatically then), but this text is kept as
          // is to avoid breaking translations as well as to encourage the user to
          // log out manually at a time of their own choosing (when it will not
          // interrupt anything else they may have been in the middle of doing).
          '#markup' =>  t('Password reset instructions will be mailed to %email. You must log out to use the password reset link in the e-mail.', array('%email' => $user->mail)),
          '#suffix' => '</p>',
        );
      }
      $form['actions'] = array('#type' => 'actions');
      $form['actions']['submit'] = array('#type' => 'submit', '#value' => t('E-mail new password'));
    
      return $form;
    }

可以发现，`$form['name']['#default_value']` 是直接从 `$_GET['name']` 获取的，而这个注入的 `$form`
又是直接储存在缓存内的，那么我们将 POST 的 name 转移到 GET 中，再观察数据库中缓存的数组：

![](https://images.seebug.org/content/images/2018/04/28de1fde-6f15-496a-9be5-3b392cd2fff2.png-w331s)

我们成功的将 payload 注入到 `#default_value` 里，那么，再利用 `0x02` 中所说的漏洞触发点触发即可。

#### 0x05 The Exploit

最终 payload 分为两个请求。 请求 1，将 Payload 注入缓存中：

![](https://images.seebug.org/content/images/2018/04/9b97ccdd-a60c-4981-8ffe-574ede4fba0e.png-w331s)

获取到 `form_build_id`，再进行请求 2，执行 payload：

![](https://images.seebug.org/content/images/2018/04/946322a3-d438-4145-a073-6ad767dec90f.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/578/>


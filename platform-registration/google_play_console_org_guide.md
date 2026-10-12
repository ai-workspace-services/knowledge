# Google Play Console（企业开发者号）注册攻略模板

## 为什么不卷国内开发平台

为什么不把工具类 App 先押在国内开发平台上？因为“某米”“某车”“某遥遥领先”再热，也替代不了稳定的跨平台生态。另一个原因是生态过于封闭：接口、工具链、分发和设备覆盖一旦被单一平台锁住，迁移成本和不确定性都由开发者与用户承担。最近做的工具类 App，会明确写出：暂不支持鸿蒙 OS——不是唱衰国产，而是不拿用户的可用性和团队的维护成本做实验。

更新日期：2026-10-11

## 适用场景

这篇适用于准备以公司、组织或商业主体名义发布 Android 应用的开发者。组织号适合长期运营、多人协作、品牌发布、广告或内购变现，以及金融、健康、VPN、政府等高敏感类别应用。

组织号和个人号功能基本一致，但验证逻辑不同。组织号更重视 D-U-N-S、组织文件、付款资料、授权人身份、官网所有权和企业联系方式。

需要注意：Google 当前官方写法是，新个人开发者账号在申请生产发布前，需要至少 12 名测试者连续 opt-in 14 天；不是 20 人。组织账号不按这个“新个人号测试门槛”处理，但仍然要完成组织身份、联系方式、网站和付款资料验证。

Google Play Console 注册费是一次性 25 美元。

## 入口

- Play Console：https://play.google.com/console/signup
- Android Developer Console 帮助：https://support.google.com/android-developer-console/
- Play Console 帮助：https://support.google.com/googleplay/android-developer/

## 注册前提

| 项目 | 要求 | 准备方式 |
| --- | --- | --- |
| Google Account | 用来创建和持有 Play Console 开发者账号 | 使用长期可控的公司用途 Google 账号；开启 2FA |
| 账号类型 | 选择 Organization | 商业发布优先选组织号，不要先随手开个人号 |
| Google Payments profile | 注册时绑定；法定名称和地址来自 payments profile | 创建或选择组织 payments profile，名称地址与公司文件一致 |
| D-U-N-S | 组织号必需；Google 明确说没有 D-U-N-S 不能创建组织账号，少数无法获取 D-U-N-S 的地区需先联系支持 | 先确认 D&B 档案准确，再注册 Play Console |
| 组织文件 | 官方组织文件；名称要与 D&B 档案匹配 | 准备成立文件、注册证书、良好存续证明、税务文件或政府登记文件 |
| 授权人身份证件 | 需要提交可代表组织的人的官方身份证件 | 准备护照、身份证或当地支持的证件 |
| 官网 | 组织账号必须验证网站所有权 | 提前把官网加入 Google Search Console |
| 联系方式 | 联系邮箱、电话要 OTP 验证；组织账号邮箱应关联企业 | 准备 `admin@[company-domain]`、`dev@[company-domain]` 或申请人的企业邮箱 |

## 官网和域名准备

Google 对组织账号要求验证网站所有权。流程是 Android Developer Console 与 Google Search Console 建立 association。如果网站还没加入 Search Console，需要先注册并完成域名验证。

建议申请前完成：

- 主域名统一：所有平台邮箱、官网、政策页尽量使用同一个主域名。
- Search Console 域名验证：DNS TXT 最稳。
- 官网政策页：Privacy Policy 和 Terms of Service。
- Play Store 公开联系信息：developer email、developer phone、website 都要能长期维护。
- 隐私政策 URL：如果 App 收集个人或设备数据，隐私政策是后续上架必备项。


## 官网与工作邮箱标准

详细标准见 `website_email_standard_guide.md`。Google 组织号会验证网站所有权，建议先用 Google Workspace 管理公司邮箱，再用同一个生态完成 Google Search Console 域名验证。

主申请账号可以使用 Workspace 账号。对外 developer email 建议用 `support@[company-domain]`，平台 owner 或 payments profile 管理人建议使用真人企业邮箱，例如 `firstname@[company-domain]`。组织账号不建议使用个人邮箱或与公司无关的 generic 邮箱。

官网至少要有 Home、Product / Solutions、Privacy Policy、Terms of Service、Contact / Support。Privacy Policy URL 后续会被应用上架、数据安全表和审核流程反复使用。

## 推荐办理顺序

1. 确定主域名，并配置公司邮箱、官网、Privacy Policy、Terms of Service。
2. 在 Google Search Console 完成主域名验证。
3. 核对 D-U-N-S：公司名、地址、法律实体和注册文件一致。
4. 准备组织 payments profile。不要用个人 payments profile 代替公司主体。
5. 准备公司文件：成立文件、良好存续证明、税号文件、D&B 信息、公司地址证明或账单材料。
6. 准备授权人身份证件，以及能接收 OTP 的公司邮箱和电话。
7. 进入 Play Console 注册，支付 25 美元注册费。
8. 选择 Organization，填 developer name、D-U-N-S、组织名称、地址、网站、联系人、语言、组织类型和规模。
9. 完成身份验证：D-U-N-S、授权人证件、官方组织文件、联系邮箱/电话 OTP。
10. 完成网站验证：通过 Search Console association 批准。
11. 如果要变现，进入 Payments settings 配置商户税务、银行和收款资料。
12. 创建 App 前，先把包名、签名密钥、隐私政策、数据安全表、测试账号和审核说明准备好。

## 税务与收款

Google 的注册身份验证和商户税务是两条线。组织账号创建时，核心是 D-U-N-S、组织文件、授权人身份、payments profile、网站和联系方式。要获得及时商户付款，还要进入 payments profile 补税务信息。

Google 官方写明：LLC、corporation、partnership 需要在 payments profile 中提供 EIN 和 IRS 登记的 legal business name，确保 Google 报给 IRS 的信息能匹配。美国商户通常提交 W-9；非美国商户通常按系统问题提交 Certificate of Foreign Status（W-8BEN 等）。

示例：如果主体是美国 LLC，建议等 EIN 确认文件到手后再认真配置商户税务，避免 TIN / 公司名尝试次数耗尽或触发人工复核。

## 网络与账号风控

Google 的风控比表面流程更敏感，建议把“账号环境”当成注册材料的一部分管理。

- 用干净、固定、长期稳定的设备和网络管理 Play Console。
- 不要和曾被封禁的开发者账号、设备、浏览器配置、支付资料、手机号、邮箱混用。
- 不要频繁切换代理、国家/地区、设备指纹和登录地点。
- Google Account、payments profile、D-U-N-S、官网、Search Console、税务资料尽量用同一公司身份闭环。
- 注册后先少量、规范操作，不要短期内大量创建包名、频繁删改应用或提交低完成度 APK / AAB。
- 所有公开信息要真实可联系，Google 可能邮件或电话检查账号活跃度。

## 会卡在哪里

| 卡点 | 典型原因 | 处理方式 |
| --- | --- | --- |
| D-U-N-S 不通过 | D&B 公司名/地址和 payments profile 不一致 | 先修 D&B，再修 payments profile，保持完全一致 |
| 组织文件不被支持 | 文件不是政府、税务、商会、商业登记等可信来源 | 提交官方 formation、registration、good standing 或 tax authority 文件 |
| 网站验证失败 | Search Console owner 不同意，或 URL 填错 | 用同一个 Google 账号完成 Search Console 域名验证 |
| 邮箱电话验证失败 | OTP 收不到、邮箱过于个人化或不可长期维护 | 换企业域名邮箱和稳定电话 |
| 税务信息失败 | EIN、legal business name 与 IRS 记录不一致 | 以税号确认文件上的名称为准填写 |
| 审核被拖慢 | 注册资料、设备、网络、付款资料不一致 | 暂停变更，统一资料后再补件 |

## 官方资料

- Get started with Play Console：https://support.google.com/googleplay/android-developer/answer/6112435
- Required information to create an Android Developer Console account：https://support.google.com/android-developer-console/answer/16640818
- Choose a developer account type：https://support.google.com/android-developer-console/answer/16641046
- Verify your Android developer identity information：https://support.google.com/android-developer-console/answer/16641416
- Contact information requirements：https://support.google.com/googleplay/android-developer/answer/10840893
- App testing requirements for new personal developer accounts：https://support.google.com/googleplay/android-developer/answer/14151465
- Enter merchant tax information：https://support.google.com/googleplay/android-developer/answer/7163598

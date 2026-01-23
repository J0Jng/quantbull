# 安全配置清单（必填项）

> 生产环境必须设置以下配置项，否则服务将拒绝启动或处于不安全状态。

## 必填环境变量

### 1) JWT 与管理员初始化
- `JWT_SECRET`（user-service）
  - 说明：JWT 对称签名密钥，必须为强随机值（≥ 32 字节）。
  - 影响文件：user-service/core/config.py、user-service/main.py、docker-compose.yml
  - 示例：`JWT_SECRET="<random-32+>"`

- `JWT_ISSUER` / `JWT_AUDIENCE`
  - 说明：JWT 发行者与受众标识，生产建议按环境区分。
  - 影响文件：user-service/core/config.py、user-service/auth/jwt.py

- `ADMIN_USERNAME` / `ADMIN_PASSWORD`（user-service）
  - 说明：管理员初始账号口令。生产必须修改默认值。
  - 影响文件：user-service/core/config.py、user-service/main.py

### 2) CORS 白名单
- `CORS_ALLOW_ORIGINS`
  - 说明：允许跨域的前端域名列表（JSON 数组）。
  - 影响文件：api-gateway/core/config.py、api-gateway/main.py、user-service/core/config.py、user-service/main.py
  - 示例：
    ```json
    ["https://example.com", "https://app.example.com"]
    ```

- `CORS_ALLOW_CREDENTIALS`
  - 说明：是否允许携带凭证（true/false）。
  - 建议：启用 Cookie 登录时必须设为 `true`。

### 3) Cookie 与 CSRF
- `AUTH_COOKIE_NAME`
  - 说明：认证 Cookie 名称（HttpOnly）。
- `CSRF_COOKIE_NAME`
  - 说明：CSRF Cookie 名称（前端可读）。
- `COOKIE_SECURE`
  - 说明：仅 HTTPS 传输（生产必须为 true）。
- `COOKIE_SAMESITE`
  - 说明：SameSite 策略，建议 `Lax` 或 `Strict`；如需跨站点嵌入则需评估 `None` + `Secure`。
- `COOKIE_DOMAIN`
  - 说明：可选，设置跨子域共享时使用。

> 说明：使用 Cookie 登录后，前端需在非幂等请求中携带 `X-CSRF-Token` 头，值为 `CSRF_COOKIE_NAME` 对应的 Cookie。
> 若修改 Cookie 名称，请同步更新前端 [frontend/niuniu/src/services/http.js](frontend/niuniu/src/services/http.js)。

### 4) 可信代理（限流真实 IP）
- `TRUSTED_PROXIES`
  - 说明：网关前置反代 IP 列表（JSON 数组）。仅当请求来自这些 IP 时才读取 `X-Forwarded-For`。
  - 影响文件：api-gateway/core/config.py、api-gateway/middlewares/rate_limit.py
  - 影响文件（user-service 登录/注册限流）：user-service/core/config.py、user-service/routers/auth.py
  - 示例：
    ```json
    ["10.0.0.10", "10.0.0.11"]
    ```

### 5) AI Hub 密钥（非 local 必填）
- `DEEPSEEK_API_KEY` / `QWEN_API_KEY` / `OPENAI_API_KEY`
  - 说明：ai-hub 在非 `local` 环境会对缺失密钥 fail-closed（启动失败）。
  - 影响文件：ai-hub/core/config.py、docker-compose.yml

## 其他建议项

- `ENV` / `env`
  - 说明：环境标识（local / prod）。
  - 影响：非 local 时启用强制安全检查（默认密钥/管理员口令拦截、CORS 收敛）。

## 部署提示

- **严禁使用默认值**：`JWT_SECRET=change-me-in-prod`、`ADMIN_PASSWORD=admin123`。
- 生产环境建议通过密钥管理系统注入环境变量，不要写入仓库或镜像。
- 如果使用 Nginx/Envoy/云负载均衡，请确保仅该反代向网关注入 `X-Forwarded-For`。

## 示例配置

- 参考 [.env.example](.env.example) 进行配置（生产务必替换默认值）。

## 本地开发提示

- 本地环境可将 `ENV=local`，系统会自动允许非 HTTPS Cookie。

## 前端安全提示

- 已在前端加入 CSP meta，但生产环境建议在静态服务器上配置响应头级 CSP（比 meta 更可靠）。
- 若启用 CSP 严格模式，需要为第三方资源（图片/CDN）明确添加允许域名。

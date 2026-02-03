# QuantBull 前端（Vite）在宿主机 Nginx 部署

适用场景：
- 服务器宿主机安装 Nginx（不把前端放进容器）
- 后端用 `docker compose up -d` 在同一台服务器上运行（`api-gateway` 暴露 `8000:8000`）
- 前端生产环境通过同域 `/api/*` 访问后端（本项目默认如此）

已知服务器：
- 公网 IP：<SERVER_IP>
- 私网 IP：<PRIVATE_IP>

## 1) 构建前端产物（dist）

在本地或 CI（推荐）执行：

```bash
cd frontend/niuniu
npm ci
npm run build
```

产物在：`frontend/niuniu/dist/`。

> 说明：你仓库里现在已经有 `dist/`，但线上建议始终以构建生成的 `dist/` 为准，不要直接用旧产物。

## 2) 上传到服务器

建议在服务器创建目录：

```bash
sudo mkdir -p /var/www/quantbull
sudo chown -R $USER:$USER /var/www/quantbull
```

从本地上传（示例）：

```bash
scp -r frontend/niuniu/dist/* root@<SERVER_IP>:/var/www/quantbull/
```

（也可以用 `rsync -av --delete` 做增量发布。）

## 3) 确保后端网关在本机可访问

在服务器项目根目录运行后端：

```bash
docker compose up -d
```

验证网关端口（同机执行）：

```bash
curl -I http://127.0.0.1:8000/
```

如果你 FastAPI 开了文档，通常也可以：

```bash
curl -I http://127.0.0.1:8000/docs
curl -I http://127.0.0.1:8000/openapi.json
```

> 若 `127.0.0.1:8000` 访问不到，但 `<PRIVATE_IP>:8000` 能访问，则把 Nginx 的 `proxy_pass` 改成 `http://<PRIVATE_IP>:8000;`。

## 4) 安装并配置 Nginx

安装（Ubuntu/Debian）：

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

把仓库里的示例配置部署到服务器（推荐放到 conf.d）：
> 注意：不要把这个文件内容直接覆盖写进 `/etc/nginx/nginx.conf`（那是主配置文件，包含 `events {}` / `http {}` 等顶层结构）。

### 常见坑：把“完整 nginx.conf”放进 conf.d

`/etc/nginx/conf.d/*.conf`（或 `sites-enabled`）里通常只能放 `server { ... }`（以及少量允许的 http 级别指令），不能放 `worker_processes` / `events {}` / `http {}` 这种“主配置文件级别”的内容。

如果你手上的是类似下面这种“完整 nginx.conf”（包含 `worker_processes`、`events`、`http`），它应该放在 `/etc/nginx/nginx.conf`，而不是 conf.d：

```nginx
worker_processes 1;
events { worker_connections 1024; }
http { ... }
```

推荐做法：保留系统默认的 `/etc/nginx/nginx.conf`，只把本项目的 `server { ... }` 放到 `/etc/nginx/conf.d/quantbull.conf`。

然后检查 `root` 是否是 `/var/www/quantbull`。

验证并重载：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 5) 放通端口与云安全组

- 云厂商安全组：放通 TCP `80`（如果要 HTTPS 再放通 `443`）
- 服务器防火墙（如果开启了）：放通 `80/443`

## 6) Cookie / 登录相关的环境变量建议（重要）

前端 axios 配置是 `withCredentials: true`，且生产环境默认走同域 `/api`。
如果你用 **IP 直连**（不是域名）并且是 **HTTP**：
- `COOKIE_SECURE` 建议为 `false`（否则浏览器不会在 HTTP 下携带 Secure Cookie）
- `COOKIE_DOMAIN` 建议留空（让浏览器用 host-only cookie；不要强行设置成别的域名）

这些变量在 compose 里由环境注入（例如 `api-gateway` 的 `COOKIE_*`）。

## 7) 访问验证

浏览器打开：
- `http://<SERVER_IP>/`

然后用开发者工具观察：
- 页面静态资源是否 200
- API 请求是否命中 `http://<SERVER_IP>/api/...` 且返回正常

## 常见报错排查

### 0) 打开 IP 看到 Apache 的 "Welcome to HTTP Server Test Page"

这表示：当前 **80 端口是 Apache(httpd/apache2) 在对外提供服务**，而不是 Nginx。所以你即使改了 Nginx 配置，浏览器也不会访问到。

在服务器上执行以下命令定位并切换：

1) 看看 80 端口到底被谁占用：

```bash
sudo ss -ltnp | grep ':80'
```

2) 如果是 CentOS/RHEL 系（服务名通常是 `httpd`）：

```bash
sudo systemctl stop httpd
sudo systemctl disable httpd
sudo systemctl enable --now nginx
```

3) 如果是 Ubuntu/Debian 系（服务名通常是 `apache2`）：

```bash
sudo systemctl stop apache2
sudo systemctl disable apache2
sudo systemctl enable --now nginx
```

4) 验证 Nginx 配置生效：

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I http://127.0.0.1/
```

如果你确实还需要 Apache（跑别的网站），那就把 Apache 改到别的端口（例如 8080），让 Nginx 监听 80/443。

#### 如果 `ss` 显示是 Nginx，但页面仍是“默认页”

当 `ss -ltnp` 已经显示 `:80` 是 `nginx`，但你访问 `http://<SERVER_IP>/` 仍看到“Welcome/默认页”，通常是：

- **Nginx 命中了默认站点**（你的 quantbull 站点配置未加载，或 `server_name/root` 没匹配）
- **Nginx 的 `root` 仍指向默认目录**（例如 `/usr/share/nginx/html`），里面正好放着默认页

排查顺序：

1) 先看响应头是不是 Nginx：

```bash
curl -I http://127.0.0.1/
curl -I http://<SERVER_IP>/
```

2) 打印 Nginx 实际加载的完整配置，确认 quantbull 的 `server {}` 是否存在：

```bash
sudo nginx -T | grep -n "server_name\|root\|conf.d" | head
```

3) 确认你的站点文件放对了位置（建议：`/etc/nginx/conf.d/quantbull.conf`），并且把系统自带的默认站点禁用/移走（常见文件名：`default.conf`）。

改完执行：`sudo nginx -t`、`sudo systemctl reload nginx`。

### 1) `Failed to load module script ... MIME type of "text/plain"`

这几乎总是以下两类原因之一：

- **原因 A：静态文件没找到（404）**。浏览器请求 `/assets/*.js`，但 Nginx 找不到文件，返回了 404（通常是 `text/plain`）。
	- 服务器上确认文件存在：`/var/www/quantbull/index.html`、`/var/www/quantbull/assets/` 目录下有 `*.js` `*.css`
	- 确认 Nginx `root` 指向的就是包含 `index.html` 和 `assets/` 的目录（不要指到别的路径）

- **原因 B：Nginx 没加载 MIME types**，导致 `.js` 被当成 `text/plain`。
	- 检查 `/etc/nginx/nginx.conf` 的 `http { ... }` 内是否有：

```nginx
http {
	include /etc/nginx/mime.types;
	default_type application/octet-stream;
	include /etc/nginx/conf.d/*.conf;
}
```

改完执行：`sudo nginx -t`、`sudo systemctl reload nginx`。

快速验证（在你电脑或服务器上）：
- `curl -I http://<SERVER_IP>/assets/你的js文件名.js` 应该返回 `200` 且 `Content-Type: application/javascript`

### 2) `The Content Security Policy directive 'frame-ancestors' is ignored when delivered via a <meta> element`

这是浏览器提示：`frame-ancestors` 只能通过 **HTTP 响应头** 下发，放在 HTML 的 `<meta http-equiv>` 里会被忽略。

如果你确实需要禁止页面被 iframe 嵌入，建议在 Nginx 的 `server {}` 里加响应头（示例）：

```nginx
add_header Content-Security-Policy "frame-ancestors 'none'" always;
```

---

## 可选：HTTPS（有域名时更推荐）

如果你后续绑定域名，最省事的方式是用 `certbot` 申请 Let’s Encrypt 证书并自动改 Nginx 配置。

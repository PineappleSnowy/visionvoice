from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)

# CORS(app)


@app.route('/')
def index():
    return render_template('test.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

    """
    您可以尝试在前端代码中添加HTTPS协议来更安全地请求用户摄像头权限，因为现代浏览器对未加密的HTTP请求限制了一些敏感操作，比如访问摄像头。您还可以尝试在页面加载时就请求摄像头权限，以确保用户能够正常使用摄像头。

另外，您可以在后端代码中添加适当的CORS设置，以允许前端页面从不同的源（比如局域网中的地址）访问后端服务。

以下是修改后的一些可能的代码示例：

前端代码：
```js
navigator.mediaDevices.getUserMedia({ video: true })
    .then(handleCameraStream)
    .catch(handleCameraError);

// 请求访问HTTPS协议
if (location.protocol !== 'https:') {
    location.replace(`https:${location.href.substring(location.protocol.length)}`);
}

// 修改WebSocket连接代码
const socket = io('http://your_server_ip:5000');
```

后端代码：
```python
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('test.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
```

请注意，以上代码仅供参考，具体的调整可能会根据您的实际情况有所不同。同时，请确保您的网络设置和防火墙允许在局域网中访问摄像头。祝您顺利解决问题！如果还有其他疑问，请随时提出。
    """

    """
    在Chrome浏览器中，访问摄像头需要使用HTTPS协议，而在本地开发环境中，使用localhost或者IP地址是不支持HTTPS的。推荐的解决方案是使用ngrok工具将本地服务通过HTTPS映射到外网，这样就可以在局域网中访问摄像头。

你可以按照以下步骤进行操作：

1. 安装ngrok，并在命令行中执行以下命令：ngrok http 5000（5000是你Flask应用的端口号）。

2. ngrok会生成一个https://xxxxx.ngrok.io或者类似的URL，将该URL替换掉前端代码中的localhost或者IP地址，如：const url = 'https://xxxxx.ngrok.io'。

3. 将前端代码部署到服务器上，确保也是通过HTTPS协议访问。

这样就可以在局域网中访问摄像头了。希望能帮到你。
    """

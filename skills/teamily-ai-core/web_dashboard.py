"""
Teamily AI Core - Web 可视化界面
"""

from flask import Flask, render_template_string, jsonify, request
import sys
import os

# 添加 scripts 目录
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

app = Flask(__name__)

# 模拟数据（实际使用时替换为真实数据）
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teamily AI Core 控制台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        /* 头部 */
        header { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid #333; }
        .logo { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .status { display: flex; align-items: center; gap: 10px; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #00ff88; }
        
        /* 卡片 */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 30px; }
        .card { background: #16213e; border-radius: 12px; padding: 20px; border: 1px solid #0f3460; }
        .card h3 { color: #00d4ff; margin-bottom: 15px; font-size: 16px; }
        .card-value { font-size: 36px; font-weight: bold; color: #fff; }
        .card-label { color: #888; font-size: 14px; margin-top: 5px; }
        
        /* 智能体列表 */
        .agent-list { margin-top: 30px; }
        .agent-item { display: flex; justify-content: space-between; align-items: center; padding: 15px; background: #16213e; border-radius: 8px; margin-bottom: 10px; }
        .agent-info { display: flex; align-items: center; gap: 15px; }
        .agent-avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #00d4ff, #0099ff); display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .agent-name { font-weight: bold; }
        .agent-role { color: #888; font-size: 14px; }
        .agent-status { padding: 5px 12px; border-radius: 20px; font-size: 12px; }
        .status-online { background: #00ff8833; color: #00ff88; }
        
        /* 聊天区域 */
        .chat-section { margin-top: 30px; }
        .chat-container { background: #16213e; border-radius: 12px; height: 400px; display: flex; flex-direction: column; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; }
        .message { margin-bottom: 15px; display: flex; gap: 10px; }
        .message-avatar { width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0; }
        .message-content { background: #0f3460; padding: 12px 16px; border-radius: 12px; max-width: 70%; }
        .message-time { font-size: 12px; color: #666; margin-top: 5px; }
        .chat-input { display: flex; padding: 15px; border-top: 1px solid #0f3460; }
        .chat-input input { flex: 1; padding: 12px; border: none; border-radius: 8px; background: #0f3460; color: #fff; outline: none; }
        .chat-input button { margin-left: 10px; padding: 12px 24px; background: #00d4ff; border: none; border-radius: 8px; color: #000; font-weight: bold; cursor: pointer; }
        .chat-input button:hover { background: #00bbee; }
        
        /* 技能市场 */
        .skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }
        .skill-card { background: #0f3460; padding: 15px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .skill-card:hover { background: #1a4a7a; }
        .skill-name { font-weight: bold; color: #00d4ff; }
        .skill-desc { font-size: 12px; color: #888; margin-top: 5px; }
        .skill-stars { font-size: 12px; color: #ffd700; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">🤖 Teamily AI Core</div>
            <div class="status">
                <span class="status-dot"></span>
                <span>在线</span>
            </div>
        </header>
        
        <!-- 统计卡片 -->
        <div class="grid">
            <div class="card">
                <h3>🤖 智能体数量</h3>
                <div class="card-value">{{ agents|length }}</div>
                <div class="card-label">活跃 Agent</div>
            </div>
            <div class="card">
                <h3>💬 群组数量</h3>
                <div class="card-value">{{ groups|length }}</div>
                <div class="card-label">协作群组</div>
            </div>
            <div class="card">
                <h3>🧠 记忆条目</h3>
                <div class="card-value">128</div>
                <div class="card-label">知识向量</div>
            </div>
            <div class="card">
                <h3>📦 技能数量</h3>
                <div class="card-value">3008</div>
                <div class="card-label">ClawHub + 内置</div>
            </div>
        </div>
        
        <!-- 智能体列表 -->
        <div class="agent-list">
            <h2 style="margin-bottom: 15px;">👥 智能体</h2>
            {% for agent in agents %}
            <div class="agent-item">
                <div class="agent-info">
                    <div class="agent-avatar">{{ agent.name[0] }}</div>
                    <div>
                        <div class="agent-name">{{ agent.name }}</div>
                        <div class="agent-role">{{ agent.role }}</div>
                    </div>
                </div>
                <span class="agent-status status-online">在线</span>
            </div>
            {% endfor %}
        </div>
        
        <!-- 聊天区域 -->
        <div class="chat-section">
            <h2 style="margin-bottom: 15px;">💬 群聊协作</h2>
            <div class="chat-container">
                <div class="chat-messages" id="messages">
                    <div class="message">
                        <div class="message-avatar" style="background: linear-gradient(135deg, #00d4ff, #0099ff);">🤖</div>
                        <div class="message-content">
                            你好！我是 Teamily AI Core，有什么可以帮你的？
                            <div class="message-time">现在</div>
                        </div>
                    </div>
                </div>
                <div class="chat-input">
                    <input type="text" id="userInput" placeholder="输入消息..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()">发送</button>
                </div>
            </div>
        </div>
        
        <!-- 技能市场 -->
        <div class="agent-list">
            <h2 style="margin-bottom: 15px;">🛒 ClawHub 技能市场</h2>
            <div class="skills-grid">
                <div class="skill-card">
                    <div class="skill-name">📧 gmail</div>
                    <div class="skill-desc">发送和读取 Gmail 邮件</div>
                    <div class="skill-stars">⭐ 1,250</div>
                </div>
                <div class="skill-card">
                    <div class="skill-name">🐙 github</div>
                    <div class="skill-desc">GitHub 操作</div>
                    <div class="skill-stars">⭐ 980</div>
                </div>
                <div class="skill-card">
                    <div class="skill-name">💬 slack</div>
                    <div class="skill-desc">Slack 消息</div>
                    <div class="skill-stars">⭐ 856</div>
                </div>
                <div class="skill-card">
                    <div class="skill-name">📝 notion</div>
                    <div class="skill-desc">Notion 页面管理</div>
                    <div class="skill-stars">⭐ 723</div>
                </div>
                <div class="skill-card">
                    <div class="skill-name">🔍 google-search</div>
                    <div class="skill-desc">Google 搜索</div>
                    <div class="skill-stars">⭐ 654</div>
                </div>
                <div class="skill-card">
                    <div class="skill-name">📅 calendar</div>
                    <div class="skill-desc">日历事件管理</div>
                    <div class="skill-stars">⭐ 489</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function handleKeyPress(e) {
            if (e.key === 'Enter') sendMessage();
        }
        
        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;
            
            // 添加用户消息
            addMessage('你', message, '#00d4ff');
            input.value = '';
            
            // 模拟 AI 回复
            setTimeout(() => {
                addMessage('🤖 Teamily', '收到你的消息！多个 AI 智能体正在协作处理...', '#00ff88');
            }, 500);
        }
        
        function addMessage(name, text, color) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'message';
            div.innerHTML = `
                <div class="message-avatar" style="background: ${color}">${name[0]}</div>
                <div class="message-content">
                    ${text}
                    <div class="message-time">${new Date().toLocaleTimeString()}</div>
                </div>
            `;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>
'''

# 模拟数据
mock_agents = [
    {"name": "研究员", "role": "负责调研和信息收集"},
    {"name": "写手", "role": "负责文档撰写"},
    {"name": "分析师", "role": "负责数据分析和可视化"}
]

mock_groups = [
    {"name": "项目组", "members": 3},
    {"name": "技术讨论组", "members": 5},
    {"name": "市场部", "members": 4}
]


@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML, agents=mock_agents, groups=mock_groups)


@app.route('/api/agents')
def get_agents():
    return jsonify(mock_agents)


@app.route('/api/groups')
def get_groups():
    return jsonify(mock_groups)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    # TODO: 这里接入真实的 AI 响应
    response = f"收到消息: {message} - 多个智能体正在协作处理中..."
    
    return jsonify({"response": response})


if __name__ == '__main__':
    print("=" * 50)
    print("🌐 Teamily AI Core Web 控制台")
    print("📍 访问地址: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

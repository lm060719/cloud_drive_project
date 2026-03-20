# app.py
import os
import json
import uuid
import shutil
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
# 假设 config.py 中定义了 INVITATION_CODE
from config import INVITATION_CODE 

# --- 配置 ---
app = Flask(__name__)

# Session 修复：使用固定的长密钥，确保 Gunicorn 多进程环境下的 Session 稳定
# ⚠️ 生产环境中，请务必将其替换为你自己生成的安全长字符串！
app.secret_key = 'your_own_super_secret_key_that_is_at_least_32_characters_long_for_production' 
# 设置 session 有效期
app.permanent_session_lifetime = timedelta(minutes=30)

# 基础目录配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 存储用户数据的 '数据库' 文件
USER_DATA_FILE = os.path.join(BASE_DIR, 'users.json') 
# 存储所有用户文件的根目录
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'user_files') 

# 确保文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- 辅助函数 ---

def load_users():
    """加载用户数据，如果文件不存在或为空，则返回空字典"""
    if not os.path.exists(USER_DATA_FILE) or os.path.getsize(USER_DATA_FILE) == 0:
        return {}
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"警告：用户数据文件 {USER_DATA_FILE} 内容无效，已重置为空。")
        return {}

def save_users(users):
    """保存用户数据"""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# 路径修复：统一的路径获取函数，解决了所有文件操作的路径问题
def get_user_file_path(username, relative_path=''):
    """
    获取用户专属文件存储路径下的某个相对路径。
    Args:
        username (str): 当前用户名。
        relative_path (str): 用户文件根目录下的相对路径。
    """
    user_root = os.path.join(UPLOAD_FOLDER, username)
    
    # 如果 relative_path 存在，则拼接
    if relative_path:
        # 去除开头的斜杠，避免 os.path.join 错误处理
        relative_path = relative_path.lstrip('/') 
        full_path = os.path.join(user_root, relative_path)
    else:
        full_path = user_root
        
    # 安全检查：确保用户无法跳出自己的目录 (防止路径遍历攻击)
    user_root_abs = os.path.abspath(user_root)
    full_path_abs = os.path.abspath(full_path)
    
    if not full_path_abs.startswith(user_root_abs):
        return user_root # 如果尝试跳出，则回到根目录

    return full_path

# --- 路由：认证 ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面和处理"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        invite_code = request.form['invite_code'] 
        
        users = load_users()

        # 1. 检查邀请码 (修复：直接渲染模板，确保消息立即显示)
        if invite_code != INVITATION_CODE:
            flash('邀请码错误，无法注册', 'danger')
            return render_template('register.html') 

        # 2. 检查用户是否已存在 (修复：直接渲染模板，确保消息立即显示)
        if username in users:
            flash('用户已存在', 'danger')
            return render_template('register.html') 

        # 3. 注册新用户
        hashed_password = generate_password_hash(password)
        users[username] = {'password': hashed_password}
        save_users(users)

        # 4. 创建用户专属文件目录
        user_folder = get_user_file_path(username) 
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面和处理"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        
        if username in users and check_password_hash(users[username]['password'], password):
            session.permanent = True
            session['logged_in'] = True
            session['username'] = username 
            flash('登录成功', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    flash('已登出', 'info')
    return redirect(url_for('login'))

# --- 路由：云盘功能 ---

@app.route('/', defaults={'path': ''})
@app.route('/dashboard/<path:path>')
def dashboard(path):
    """云盘主界面：展示当前路径下的文件和文件夹"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    username = session.get('username')
    # 使用修正后的 get_user_file_path 来获取当前目录的绝对路径
    current_dir_path = get_user_file_path(username, path) 

    if not os.path.isdir(current_dir_path):
        flash('目录不存在', 'danger')
        # 如果目录不存在，回退到上一级或根目录
        path_segments = [p for p in path.split('/') if p]
        if path_segments:
             return redirect(url_for('dashboard', path='/'.join(path_segments[:-1])))
        else:
             return redirect(url_for('dashboard'))

    # 读取目录内容
    items = []
    try:
        for item_name in os.listdir(current_dir_path):
            item_path = os.path.join(current_dir_path, item_name)
            item_type = 'folder' if os.path.isdir(item_path) else 'file'
            item_size = os.path.getsize(item_path) if item_type == 'file' else 0
            
            # 隐藏点开头的文件 (如 .DS_Store)
            if item_name.startswith('.'):
                continue

            # 构建当前路径段
            path_segments = [p for p in path.split('/') if p]
            
            items.append({
                'name': item_name,
                'type': item_type,
                'size': item_size,
                # 'full_path' 是用于 URL 的相对路径
                'full_path': '/'.join(path_segments + [item_name]) 
            })
    except Exception as e:
        flash(f'读取目录内容失败: {e}', 'danger')
        items = []

    # 排序：文件夹在前，文件在后，然后按名称排序
    items.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))

    # 构建面包屑导航数据
    breadcrumbs = []
    path_segments = [p for p in path.split('/') if p]
    current_path_so_far = []
    for segment in path_segments:
        current_path_so_far.append(segment)
        breadcrumbs.append({
            'name': segment,
            'url': url_for('dashboard', path='/'.join(current_path_so_far))
        })
    
    return render_template('dashboard.html', 
                           username=session['username'], 
                           items=items, 
                           breadcrumbs=breadcrumbs,
                           current_path_string=path) # 传递当前路径字符串

@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上传处理"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('没有文件部分', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['file']
    current_path_string = request.form.get('current_path', '')
    username = session['username']
    
    # 使用新的辅助函数获取当前目录的绝对路径
    current_dir_path = get_user_file_path(username, current_path_string) 

    if file.filename == '':
        flash('没有选择文件', 'warning')
        return redirect(url_for('dashboard', path=current_path_string))

    if file and current_dir_path:
        filename = file.filename
        file_path = os.path.join(current_dir_path, filename)
        try:
            file.save(file_path)
            flash(f'文件 "{filename}" 上传成功', 'success')
        except Exception as e:
            flash(f'文件保存失败: {e}', 'danger')
    else:
        flash('上传失败', 'danger')
        
    return redirect(url_for('dashboard', path=current_path_string))

@app.route('/new_folder', methods=['POST'])
def new_folder():
    """新建文件夹处理"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    current_path_string = request.form.get('current_path', '')
    folder_name = request.form.get('folder_name', '').strip()
    username = session['username']
    
    if not folder_name:
        flash('文件夹名称不能为空', 'warning')
        return redirect(url_for('dashboard', path=current_path_string))

    # 使用新的辅助函数获取当前目录的绝对路径
    current_dir_path = get_user_file_path(username, current_path_string)
    
    if current_dir_path:
        new_folder_path = os.path.join(current_dir_path, folder_name)
        
        if os.path.exists(new_folder_path):
            flash(f'文件夹 "{folder_name}" 已存在', 'warning')
        else:
            try:
                os.makedirs(new_folder_path) 
                flash(f'文件夹 "{folder_name}" 创建成功', 'success')
            except Exception as e:
                flash(f'创建文件夹失败: {e}', 'danger')
    else:
        flash('创建文件夹失败', 'danger')

    return redirect(url_for('dashboard', path=current_path_string))

@app.route('/delete', methods=['POST'])
def delete_item():
    """处理文件和文件夹的删除请求"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    item_path = request.form.get('item_path') 
    username = session['username']
    
    # 使用新的辅助函数获取完整绝对路径
    full_path = get_user_file_path(username, item_path) 
    
    # 1. 计算被删除项的父目录路径
    # 例如：item_path='A/B/C' -> parent_path='A/B'
    # 例如：item_path='A' -> parent_path='' (空字符串代表根目录)
    parent_path = os.path.dirname(item_path)
    
    # 2. 规范化路径，避免出现如 'A/B/..' 等不规范路径
    redirect_path = os.path.normpath(parent_path)
    
    # 3. 特殊处理：如果规范化后路径为 '.'，则代表根目录
    if redirect_path == '.':
        redirect_path = '' 
    
    if not os.path.exists(full_path):
        flash(f"错误：文件或文件夹 {item_path} 不存在。", 'danger')
        return redirect(url_for('dashboard', path=redirect_path))

    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
            flash(f"文件 '{os.path.basename(item_path)}' 已删除。", 'success')
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)
            flash(f"文件夹 '{os.path.basename(item_path)}' 及其内容已删除。", 'success')
        
    except Exception as e:
        flash(f"删除失败: {e}", 'danger')

    # 删除后重定向回父目录
    return redirect(url_for('dashboard', path=redirect_path))

@app.route('/download/<path:file_path>')
def download_file(file_path):
    """文件下载处理"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # 使用新的辅助函数获取完整绝对路径
    full_file_path = get_user_file_path(session['username'], file_path)
    
    # 构造文件所在的目录和文件名
    download_dir_path = os.path.dirname(full_file_path)
    file_name = os.path.basename(full_file_path) 
    
    if os.path.isfile(full_file_path):
        try:
            # send_from_directory 负责文件下载，并执行安全检查
            return send_from_directory(download_dir_path, 
                                       file_name, 
                                       as_attachment=True) 
        except Exception as e:
            flash(f'文件下载失败: {e}', 'danger')
    else:
        flash('文件不存在或无权访问', 'danger')

    # 下载失败，重定向回文件所在目录
    dir_segments = os.path.dirname(file_path)
    return redirect(url_for('dashboard', path=dir_segments))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
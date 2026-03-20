// 显示模态框
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

// 隐藏模态框
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// 点击模态框背景时关闭模态框
window.onclick = function (event) {
    const modal = document.querySelector('.modal[style*="block"]');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

// 删除确认函数
function confirmDelete(itemType, itemName, itemFullPath, event) 
{
    // 关键：阻止事件冒泡，避免触发 <tr> 的 onclick 跳转
    event.stopPropagation();

    if (confirm(`确定要删除 ${itemType === 'folder' ? '文件夹' : '文件'}：${itemName} 吗？\n此操作不可撤销。`)) 
    {
        const form = document.createElement('form');

        form.method = 'POST';
        form.action = '/delete';

        const input = document.createElement('input');

        input.type = 'hidden';
        input.name = 'item_path';
        input.value = itemFullPath;

        form.appendChild(input);

        document.body.appendChild(form);

        form.submit();
    }
}


// DOM 加载完成后执行
document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name-display');
    const uploadSubmitBtn = document.getElementById('upload-submit-btn');
    const uploadForm = document.getElementById('upload-form');

    // 进度条相关元素
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');

    // 文件选择监听
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
                uploadSubmitBtn.disabled = false;
            } else {
                fileNameDisplay.textContent = '未选择文件';
                uploadSubmitBtn.disabled = true;
            }
        });
    }

    // AJAX 文件上传逻辑
    if (uploadForm) {
        uploadForm.addEventListener('submit', function (e) {
            e.preventDefault(); // 阻止默认表单提交

            const file = fileInput.files[0];
            if (!file) {
                alert('请选择一个文件。');
                return;
            }

            // 禁用按钮并显示进度条
            uploadSubmitBtn.disabled = true;
            progressContainer.style.display = 'block';
            progressFill.style.width = '0%';
            progressFill.textContent = '0%';

            // 构造 FormData
            const formData = new FormData(uploadForm);

            // 创建 XMLHttpRequest
            const xhr = new XMLHttpRequest();

            // 监听上传进度
            xhr.upload.addEventListener('progress', function (event) {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    const percent = Math.round(percentComplete) + '%';
                    progressFill.style.width = percent;
                    progressFill.textContent = percent;
                }
            });

            // 监听请求完成
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    progressContainer.style.display = 'none'; // 隐藏进度条
                    if (xhr.status === 200) {
                        // 上传成功，刷新页面
                        window.location.reload();
                    } else {
                        // 上传失败
                        alert('文件上传失败，请检查服务器日志。');
                        uploadSubmitBtn.disabled = false;
                    }
                }
            };

            // 发送请求
            xhr.open('POST', '/upload', true);
            xhr.send(formData);
        });
    }
});
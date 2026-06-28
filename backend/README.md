# ZeKin Backend

## 人脸识别依赖（Windows）

管理员录入人脸 / 学生人脸打卡需要以下 Python 包。若缺失会返回 **503 Service Unavailable**。

推荐安装顺序：

```bash
cd backend
pip install dlib-bin opencv-python-headless
pip install face-recognition-models face-recognition --no-deps
```

说明：

- `dlib-bin` 提供预编译 dlib，避免 Windows 上编译失败
- `opencv-python-headless` 作为 `face_recognition` 不可用时的回退方案
- 安装完成后需 **重启后端进程**

验证：

```bash
python -c "import cv2; import face_recognition; print('ok')"
```

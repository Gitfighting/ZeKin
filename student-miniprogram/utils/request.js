const app = getApp();

function request(path, options = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.baseUrl}${path}`,
      method: options.method || "GET",
      data: options.data || {},
      header: {
        "Content-Type": "application/json",
        "X-Client": "student-miniapp",
        ...(app.globalData.token ? { Authorization: `Bearer ${app.globalData.token}` } : {}),
        ...(options.header || {})
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data.data);
        } else {
          reject(new Error(res.data?.message || "请求失败"));
        }
      },
      fail() {
        reject(new Error("网络异常，请稍后重试"));
      }
    });
  });
}

module.exports = { request };

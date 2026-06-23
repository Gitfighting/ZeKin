const { request } = require("../../utils/request");
const app = getApp();

Page({
  data: {
    username: "teacher_demo",
    password: "Passw0rd!",
    loading: false
  },

  onInput(e) {
    this.setData({ [e.currentTarget.dataset.field]: e.detail.value });
  },

  async prepareDemo() {
    wx.showLoading({ title: "准备中" });
    try {
      await request("/api/auth/register", {
        method: "POST",
        data: {
          username: "teacher_demo",
          password: "Passw0rd!",
          real_name: "华老师",
          role: "teacher",
          class_name: "软件一班",
          phone: "13910000003"
        }
      }).catch(() => null);
      wx.showToast({ title: "演示账号已准备" });
    } finally {
      wx.hideLoading();
    }
  },

  async login() {
    if (!this.data.username || !this.data.password) {
      wx.showToast({ title: "请输入账号密码", icon: "none" });
      return;
    }
    this.setData({ loading: true });
    try {
      const data = await request("/api/auth/login", {
        method: "POST",
        data: {
          username: this.data.username,
          password: this.data.password
        }
      });
      app.globalData.token = data.access_token;
      app.globalData.user = data.user;
      wx.setStorageSync("teacher_token", data.access_token);
      wx.setStorageSync("teacher_user", data.user);
      wx.switchTab({ url: "/pages/reviews/reviews" });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  }
});

const app = getApp();

Page({
  data: {
    user: null
  },

  onShow() {
    this.setData({ user: app.globalData.user || wx.getStorageSync("teacher_user") });
  },

  logout() {
    app.globalData.token = "";
    app.globalData.user = null;
    wx.removeStorageSync("teacher_token");
    wx.removeStorageSync("teacher_user");
    wx.navigateTo({ url: "/pages/login/login" });
  }
});

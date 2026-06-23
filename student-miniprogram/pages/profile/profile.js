const app = getApp();

Page({
  data: {
    user: null
  },

  onShow() {
    this.setData({ user: app.globalData.user || wx.getStorageSync("student_user") });
  },

  logout() {
    app.globalData.token = "";
    app.globalData.user = null;
    wx.removeStorageSync("student_token");
    wx.removeStorageSync("student_user");
    wx.navigateTo({ url: "/pages/login/login" });
  }
});

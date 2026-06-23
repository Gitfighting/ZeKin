App({
  onLaunch() {
    this.globalData.token = wx.getStorageSync("teacher_token") || "";
    this.globalData.user = wx.getStorageSync("teacher_user") || null;
  },
  globalData: {
    baseUrl: "http://127.0.0.1:8000",
    token: "",
    user: null
  }
});

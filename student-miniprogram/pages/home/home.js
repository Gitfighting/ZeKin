const { request } = require("../../utils/request");

Page({
  data: {
    latest: null,
    statusText: "未打卡",
    recent: []
  },

  onShow() {
    this.loadData();
  },

  async loadData() {
    try {
      const data = await request("/api/checkins/my");
      const recent = data.items || [];
      const latest = recent[0] || null;
      this.setData({
        recent,
        latest,
        statusText: latest ? this.statusText(latest.status) : "未打卡"
      });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
      wx.navigateTo({ url: "/pages/login/login" });
    }
  },

  statusText(status) {
    return { pending: "待审核", approved: "已通过", rejected: "已拒绝" }[status] || "未打卡";
  },

  goSubmit() {
    wx.navigateTo({ url: "/pages/submit/submit" });
  }
});

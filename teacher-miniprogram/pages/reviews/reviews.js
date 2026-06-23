const { request } = require("../../utils/request");

Page({
  data: {
    items: [],
    pendingCount: 0,
    approvedCount: 0,
    rejectedCount: 0,
    filter: "pending"
  },

  onShow() {
    this.loadData();
  },

  async loadData() {
    try {
      const data = await request("/api/teacher/checkins");
      const items = data.items || [];
      this.setData({
        items,
        pendingCount: items.filter((item) => item.status === "pending").length,
        approvedCount: items.filter((item) => item.status === "approved").length,
        rejectedCount: items.filter((item) => item.status === "rejected").length
      });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
      wx.navigateTo({ url: "/pages/login/login" });
    }
  },

  chooseFilter(e) {
    this.setData({ filter: e.currentTarget.dataset.status });
  },

  goDetail(e) {
    wx.navigateTo({ url: `/pages/review-detail/review-detail?id=${e.currentTarget.dataset.id}` });
  }
});

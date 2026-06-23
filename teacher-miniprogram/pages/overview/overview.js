const { request } = require("../../utils/request");

Page({
  data: {
    stats: null
  },

  onShow() {
    this.loadData();
  },

  async loadData() {
    try {
      const stats = await request("/api/stats/overview");
      this.setData({ stats });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    }
  }
});

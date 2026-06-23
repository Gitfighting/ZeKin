const { request } = require("../../utils/request");

Page({
  data: {
    items: [],
    filter: ""
  },

  onShow() {
    this.loadData();
  },

  async loadData() {
    try {
      const data = await request("/api/checkins/my");
      this.setData({ items: data.items || [] });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
      wx.navigateTo({ url: "/pages/login/login" });
    }
  },

  chooseFilter(e) {
    this.setData({ filter: e.currentTarget.dataset.status || "" });
  },

  statusText(status) {
    return { pending: "待审核", approved: "已通过", rejected: "已拒绝" }[status] || status;
  }
});

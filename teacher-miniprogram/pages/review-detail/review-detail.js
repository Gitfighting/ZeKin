const { request } = require("../../utils/request");

Page({
  data: {
    id: "",
    item: null,
    comment: "",
    loading: false
  },

  onLoad(options) {
    this.setData({ id: options.id || "" });
    this.loadData();
  },

  async loadData() {
    try {
      const data = await request("/api/teacher/checkins");
      const item = (data.items || []).find((record) => String(record.id) === String(this.data.id));
      this.setData({ item });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    }
  },

  onCommentInput(e) {
    this.setData({ comment: e.detail.value });
  },

  async review(e) {
    const action = e.currentTarget.dataset.action;
    if (action === "rejected" && !this.data.comment.trim()) {
      wx.showToast({ title: "拒绝必须填写评语", icon: "none" });
      return;
    }
    this.setData({ loading: true });
    try {
      await request("/api/teacher/reviews", {
        method: "POST",
        data: {
          checkin_id: Number(this.data.id),
          action,
          comment: this.data.comment
        }
      });
      wx.showToast({ title: action === "approved" ? "已通过" : "已拒绝" });
      wx.navigateBack();
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  }
});

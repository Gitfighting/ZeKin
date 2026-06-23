const { request } = require("../../utils/request");

Page({
  data: {
    type: "dorm",
    content: "",
    photoUrl: "",
    lat: null,
    lng: null,
    loading: false
  },

  chooseType(e) {
    this.setData({ type: e.currentTarget.dataset.type });
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value });
  },

  getLocation() {
    wx.getLocation({
      type: "gcj02",
      success: (res) => {
        this.setData({ lat: res.latitude, lng: res.longitude });
        wx.showToast({ title: "定位成功" });
      },
      fail: () => wx.showToast({ title: "定位失败，可继续提交", icon: "none" })
    });
  },

  async submit() {
    if (!this.data.content.trim()) {
      wx.showToast({ title: "请填写打卡内容", icon: "none" });
      return;
    }
    this.setData({ loading: true });
    try {
      await request("/api/checkins", {
        method: "POST",
        data: {
          type: this.data.type,
          content: this.data.content,
          photo_url: this.data.photoUrl || "https://example.com/mock.jpg",
          lat: this.data.lat,
          lng: this.data.lng
        }
      });
      wx.showToast({ title: "提交成功" });
      wx.switchTab({ url: "/pages/history/history" });
    } catch (error) {
      wx.showToast({ title: error.message, icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  }
});

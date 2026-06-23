const app = getApp();

const mockUser = {
  id: 10001,
  username: "student_demo",
  real_name: "王同学",
  role: "student",
  class_name: "软件一班",
  phone: "13910000002"
};

Page({
  data: {
    heroPaddingTop: 96,
    activeTab: "login",
    tabs: [
      { key: "login", label: "登录" },
      { key: "register", label: "注册" }
    ],
    pageMock: {
      title: "考勤助手",
      subtitle: "智慧考勤，轻松校园生活",
      notice: "欢迎回来！请登录您的账号继续使用"
    },
    form: {
      account: "student_demo",
      password: "Passw0rd!",
      captcha: ""
    },
    captchaButtonText: "获取验证码",
    captchaCounting: false,
    passwordVisible: false,
    remember: true,
    loading: false
  },

  onLoad() {
    this.updateHeroPadding();
  },

  onUnload() {
    this.clearCaptchaTimer();
  },

  updateHeroPadding() {
    try {
      const system = wx.getSystemInfoSync();
      const menu = wx.getMenuButtonBoundingClientRect ? wx.getMenuButtonBoundingClientRect() : null;
      const menuBottom = menu && menu.bottom ? menu.bottom : system.statusBarHeight + 44;
      this.setData({ heroPaddingTop: menuBottom + 34 });
    } catch (error) {
      this.setData({ heroPaddingTop: 96 });
    }
  },

  onInput(e) {
    const { field } = e.currentTarget.dataset;
    this.setData({
      [`form.${field}`]: e.detail.value
    });
  },

  switchTab(e) {
    const activeTab = e.currentTarget.dataset.key;
    this.setAuthMode(activeTab);
  },

  toggleAuthMode() {
    this.setAuthMode(this.data.activeTab === "login" ? "register" : "login");
  },

  setAuthMode(activeTab) {
    this.setData({
      activeTab,
      pageMock: {
        ...this.data.pageMock,
        notice: activeTab === "login" ? "欢迎回来！请登录您的账号继续使用" : "欢迎加入！使用 mock 信息快速注册"
      }
    });
  },

  togglePassword() {
    this.setData({ passwordVisible: !this.data.passwordVisible });
  },

  toggleRemember() {
    this.setData({ remember: !this.data.remember });
  },

  getCaptcha() {
    if (this.data.captchaCounting) {
      return;
    }

    this.setData({
      "form.captcha": "246810",
      captchaCounting: true,
      captchaButtonText: "60s"
    });
    wx.showToast({ title: "验证码 246810", icon: "none" });

    let seconds = 60;
    this.captchaTimer = setInterval(() => {
      seconds -= 1;
      if (seconds <= 0) {
        this.clearCaptchaTimer();
        this.setData({
          captchaCounting: false,
          captchaButtonText: "获取验证码"
        });
        return;
      }
      this.setData({ captchaButtonText: `${seconds}s` });
    }, 1000);
  },

  clearCaptchaTimer() {
    if (this.captchaTimer) {
      clearInterval(this.captchaTimer);
      this.captchaTimer = null;
    }
  },

  forgotPassword() {
    wx.showToast({ title: "已发送 mock 找回提示", icon: "none" });
  },

  schoolLogin() {
    wx.showToast({ title: "校园统一身份认证暂为 mock", icon: "none" });
  },

  openAgreement() {
    wx.showToast({ title: "用户协议静态页占位", icon: "none" });
  },

  openPrivacy() {
    wx.showToast({ title: "隐私政策静态页占位", icon: "none" });
  },

  submitAuth() {
    const { account, password, captcha } = this.data.form;
    if (!account || !password) {
      wx.showToast({ title: "请输入账号和密码", icon: "none" });
      return;
    }
    if (!captcha) {
      wx.showToast({ title: "请输入验证码", icon: "none" });
      return;
    }

    this.setData({ loading: true });

    setTimeout(() => {
      const token = "mock-student-token";
      app.globalData.token = token;
      app.globalData.user = mockUser;
      if (this.data.remember) {
        wx.setStorageSync("student_token", token);
        wx.setStorageSync("student_user", mockUser);
      }

      wx.showToast({
        title: this.data.activeTab === "login" ? "登录成功" : "注册成功",
        icon: "success"
      });

      this.setData({ loading: false });
    }, 600);
  }
});

<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

import { tryRestoreSession } from '@/services/auth'

onLaunch(() => {
  const session = tryRestoreSession()
  if (session) {
    console.info('[auth] 已恢复登录会话', {
      userType: session.user.userType,
      displayName: session.user.displayName,
    })
  }
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>
<style lang="scss">
/* 小程序不再引入 iconfont.scss，避免 font-family:iconfont 触发 /static/fonts/iconfont.ttf 500 */
/* #ifndef MP-WEIXIN */
@import '@/styles/iconfont.scss';
/* #endif */

page,
text,
button,
input,
textarea {
  letter-spacing: 1px;
}
</style>

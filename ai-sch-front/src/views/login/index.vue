<template>
  <div class="login-container">
    <!-- 粒子动画背景 -->
    <div class="particles-container" ref="particlesContainer"></div>
    
    <!-- 登录盒子 -->
    <div class="login-box">
      <div class="login-logo">
        <h2 class="animated-title">智能排课系统</h2>
        <p>AI Smart Course Scheduling</p>
      </div>
      
      <!-- 登录表单 -->
      <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" autocomplete="on" label-position="left">
        <div class="title-container">
          <h3 class="title">用户登录</h3>
        </div>

        <el-form-item prop="username">
          <span class="icon-container">
            <i class="el-icon-user pulse"></i>
          </span>
          <el-input
            ref="username"
            v-model="loginForm.username"
            placeholder="用户名"
            name="username"
            type="text"
            tabindex="1"
            autocomplete="on"
            @focus="handleInputFocus('username')"
            @blur="handleInputBlur"
          />
        </el-form-item>

        <div class="tip-text" v-if="activeTip === 'username'">推荐使用工号/学号作为用户名</div>

        <el-form-item prop="password">
          <span class="icon-container">
            <i class="el-icon-lock pulse"></i>
          </span>
          <el-input
            :key="passwordType"
            ref="password"
            v-model="loginForm.password"
            :type="passwordType"
            placeholder="密码"
            name="password"
            tabindex="2"
            autocomplete="on"
            @keyup.enter.native="handleLogin"
            @focus="handleInputFocus('password')"
            @blur="handleInputBlur"
          />
          <span class="show-pwd" @click="showPwd">
            <i :class="passwordType === 'password' ? 'el-icon-view' : 'el-icon-close'" />
          </span>
        </el-form-item>

        <div class="tip-text" v-if="activeTip === 'password'">密码至少需要6位</div>

        <div class="additional-options">
          <el-checkbox v-model="rememberMe">记住密码</el-checkbox>
          <span class="forgot-password" @click="forgotPassword">忘记密码?</span>
        </div>

        <el-button 
          :loading="loading" 
          type="primary" 
          class="login-button"
          :class="{'button-hover': buttonHover}" 
          @mouseenter="buttonHover = true"
          @mouseleave="buttonHover = false"
          @click.native.prevent="handleLogin">
          <span class="button-text">登录</span>
          <i class="el-icon-right arrow-icon"></i>
        </el-button>

        <div class="system-info">
          <p>点击登录即表示您同意我们的<span class="highlight-text" @click="showTerms">服务条款</span></p>
          <p>系统版本 v1.0.0</p>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { validUsername } from '@/utils/validate'

export default {
  name: 'Login',
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!validUsername(value)) {
        callback(new Error('请输入正确的用户名'))
      } else {
        callback()
      }
    }
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('密码不能少于6位'))
      } else {
        callback()
      }
    }
    return {
      loginForm: {
        username: 'admin',
        password: '111111'
      },
      loginRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }]
      },
      loading: false,
      passwordType: 'password',
      redirect: undefined,
      rememberMe: false,
      activeTip: '', // 当前激活的提示
      buttonHover: false, // 按钮悬停状态
      particles: [] // 粒子数组
    }
  },
  watch: {
    $route: {
      handler: function(route) {
        this.redirect = route.query && route.query.redirect
      },
      immediate: true
    }
  },
  mounted() {
    if (this.loginForm.username === '') {
      this.$refs.username.focus()
    } else if (this.loginForm.password === '') {
      this.$refs.password.focus()
    }
    
    // 初始化粒子背景
    this.initParticles()
    
    // 检查本地存储的用户名和密码
    this.checkSavedCredentials()
    
    // 添加键盘事件监听
    window.addEventListener('keydown', this.handleKeyDown)
  },
  beforeDestroy() {
    // 销毁粒子动画
    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
    }
    
    // 移除事件监听
    window.removeEventListener('keydown', this.handleKeyDown)
  },
  methods: {
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          
          // 如果选择了记住密码，保存用户名和密码到本地存储
          if (this.rememberMe) {
            localStorage.setItem('rememberedUsername', this.loginForm.username)
            localStorage.setItem('rememberedPassword', window.btoa(this.loginForm.password)) // 简单编码，不是安全加密
          } else {
            localStorage.removeItem('rememberedUsername')
            localStorage.removeItem('rememberedPassword')
          }
          
          this.$store.dispatch('user/login', this.loginForm)
            .then(() => {
              this.$router.push({ path: this.redirect || '/home' })
              this.loading = false
            })
            .catch(() => {
              this.$message({
                message: '登录失败，请检查用户名和密码',
                type: 'error',
                duration: 3000,
                showClose: true
              })
              this.loading = false
              // 登录失败动画
              this.shakeForm()
            })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    // 处理输入框聚焦事件
    handleInputFocus(type) {
      this.activeTip = type
    },
    // 处理输入框失焦事件
    handleInputBlur() {
      setTimeout(() => {
        this.activeTip = ''
      }, 200)
    },
    // 处理忘记密码
    forgotPassword() {
      this.$message({
        message: '请联系系统管理员重置密码',
        type: 'info',
        duration: 3000,
        showClose: true
      })
    },
    // 显示服务条款
    showTerms() {
      this.$alert('本系统仅供教学管理使用，所有用户需遵守相关规定，保护数据安全。', '服务条款', {
        confirmButtonText: '我已了解',
        callback: action => {
          this.$message({
            type: 'info',
            message: '感谢您的理解与支持'
          })
        }
      })
    },
    // 表单抖动效果
    shakeForm() {
      const form = this.$refs.loginForm.$el
      form.classList.add('shake')
      setTimeout(() => {
        form.classList.remove('shake')
      }, 500)
    },
    // 检查本地存储的凭据
    checkSavedCredentials() {
      const username = localStorage.getItem('rememberedUsername')
      const password = localStorage.getItem('rememberedPassword')
      
      if (username && password) {
        this.loginForm.username = username
        this.loginForm.password = window.atob(password) // 解码
        this.rememberMe = true
      }
    },
    // 处理键盘事件
    handleKeyDown(e) {
      if (e.ctrlKey && e.key === 'Enter') {
        this.handleLogin()
      }
    },
    // 初始化粒子背景
    initParticles() {
      const canvas = document.createElement('canvas')
      this.$refs.particlesContainer.appendChild(canvas)
      const ctx = canvas.getContext('2d')
      
      const resizeCanvas = () => {
        canvas.width = window.innerWidth
        canvas.height = window.innerHeight
      }
      
      resizeCanvas()
      window.addEventListener('resize', resizeCanvas)
      
      // 创建粒子
      this.particles = []
      const particleCount = 150 // 增加粒子数量
      
      const createParticle = (x, y, isUserCreated = false) => {
        // 提高速度，使粒子运动更有活力
        const speed = isUserCreated ? 3 + Math.random() * 3 : 0.5 + Math.random() * 1.5
        const angle = Math.random() * Math.PI * 2  // 随机角度 0-360度
        
        return {
          x: x || Math.random() * canvas.width,
          y: y || Math.random() * canvas.height,
          radius: Math.random() * 2 + (isUserCreated ? 2 : 1),
          vx: Math.cos(angle) * speed,  // 使用角度和速度计算x分量
          vy: Math.sin(angle) * speed,  // 使用角度和速度计算y分量
          opacity: Math.random() * 0.5 + (isUserCreated ? 0.5 : 0.3),
          color: isUserCreated ? this.getRandomColor() : this.getBaseColor(),
          life: isUserCreated ? 100 : Infinity,
          isUserCreated,
          // 添加波动参数，使粒子闪烁
          pulseSpeed: Math.random() * 0.03 + 0.02, // 提高闪烁速度
          pulseDirection: 1,
          originalOpacity: Math.random() * 0.5 + (isUserCreated ? 0.5 : 0.3),
          // 添加颜色变化
          colorShift: !isUserCreated && Math.random() > 0.7, // 30%的普通粒子会变色
          colorPhase: Math.random() * 360, // 随机颜色相位
          currentColor: null
        }
      }
      
      for (let i = 0; i < particleCount; i++) {
        this.particles.push(createParticle())
      }
      
      // 鼠标位置追踪
      let mouseX = null
      let mouseY = null
      let mousePrevX = null
      let mousePrevY = null
      let isMouseDown = false
      
      // 添加鼠标事件监听
      canvas.addEventListener('mousemove', (e) => {
        mouseX = e.clientX
        mouseY = e.clientY
        
        // 如果鼠标按下状态，每次移动也创建粒子
        if (isMouseDown && Math.random() > 0.3) { // 提高拖动时的粒子产生率
          for (let i = 0; i < 3; i++) { // 增加每次产生的粒子数量
            const p = createParticle(mouseX, mouseY, true)
            p.life = 80 // 拖动产生的粒子生命周期较短
            p.radius = 1 + Math.random() * 2
            // 速度偏向移动方向，但有随机偏移
            if (mousePrevX !== null) {
              const moveAngle = Math.atan2(mouseY - mousePrevY, mouseX - mousePrevX)
              const speed = 1 + Math.random() * 1.5
              p.vx = Math.cos(moveAngle) * speed + (Math.random() - 0.5) * 1
              p.vy = Math.sin(moveAngle) * speed + (Math.random() - 0.5) * 1
            }
            this.particles.push(p)
          }
        }
        
        // 记录上一个鼠标位置用于计算移动方向
        mousePrevX = mouseX
        mousePrevY = mouseY
      })
      
      canvas.addEventListener('mousedown', (e) => {
        isMouseDown = true
        // 鼠标点击时创建爆发效果，增加粒子数量
        const burstCount = 20 // 增加粒子数量
        for (let i = 0; i < burstCount; i++) {
          const angle = (Math.PI * 2 / burstCount) * i
          const speed = 3 + Math.random() * 4 // 提高爆发速度
          const p = createParticle(e.clientX, e.clientY, true)
          p.vx = Math.cos(angle) * speed
          p.vy = Math.sin(angle) * speed
          // 增加生命周期和粒子大小
          p.life = 150
          p.radius = 2 + Math.random() * 3
          this.particles.push(p)
        }
        
        // 添加第二波螺旋爆发效果
        setTimeout(() => {
          const spiralCount = 15
          for (let i = 0; i < spiralCount; i++) {
            const angle = (Math.PI * 2 / spiralCount) * i + (Math.PI / spiralCount)
            const speed = 1 + Math.random() * 3
            const p = createParticle(e.clientX, e.clientY, true)
            p.vx = Math.cos(angle) * speed
            p.vy = Math.sin(angle) * speed
            p.life = 120
            this.particles.push(p)
          }
        }, 100) // 第二波爆发延迟100ms
      })
      
      canvas.addEventListener('mouseup', () => {
        isMouseDown = false
      })
      
      canvas.addEventListener('mouseleave', () => {
        mouseX = null
        mouseY = null
        isMouseDown = false
      })
      
      // 指向鼠标的特殊粒子
      const mouseFollowers = []
      const followerCount = 8 // 增加跟随者数量
      
      for (let i = 0; i < followerCount; i++) {
        mouseFollowers.push({
          x: canvas.width / 2,
          y: canvas.height / 2,
          radius: 3 - (i * 0.25), // 减小粒子尺寸递减率
          opacity: 0.9 - (i * 0.1),
          delay: i * 2, // 减少延迟
          color: i % 3 // 不同颜色的跟随者
        })
      }
      
      const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        
        // 更新并绘制粒子
        for (let i = 0; i < this.particles.length; i++) {
          const p = this.particles[i]
          
          // 减少用户创建粒子的生命值
          if (p.isUserCreated) {
            p.life--
            if (p.life <= 0) {
              this.particles.splice(i, 1)
              i--
              continue
            }
          }
          
          // 添加随机游动效果
          if (!p.isUserCreated && Math.random() < 0.08) { // 提高变向概率
            // 随机改变方向，增加幅度
            p.vx += (Math.random() - 0.5) * 0.2
            p.vy += (Math.random() - 0.5) * 0.2
            
            // 限制最大速度，但提高上限
            const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy)
            if (speed > 2.0) { // 提高最大速度限制
              p.vx = (p.vx / speed) * 2.0
              p.vy = (p.vy / speed) * 2.0
            }
            
            // 确保粒子不会太慢
            if (speed < 0.3) {
              const boost = 0.3 / speed
              p.vx *= boost
              p.vy *= boost
            }
          }
          
          // 移动粒子
          p.x += p.vx
          p.y += p.vy
          
          // 添加鼠标吸引/排斥效果
          if (mouseX && mouseY) {
            const dx = mouseX - p.x
            const dy = mouseY - p.y
            const distance = Math.sqrt(dx * dx + dy * dy)
            
            if (distance < 150) { // 增加影响范围
              // 在鼠标附近时添加力，增强效果
              const force = isMouseDown ? 0.3 : -0.15
              const angle = Math.atan2(dy, dx)
              p.vx += Math.cos(angle) * force / (distance * 0.05)
              p.vy += Math.sin(angle) * force / (distance * 0.05)
            }
          }
          
          // 检查边界
          if (p.x < 0) p.x = canvas.width
          if (p.x > canvas.width) p.x = 0
          if (p.y < 0) p.y = canvas.height
          if (p.y > canvas.height) p.y = 0
          
          // 减少阻力，让粒子运动更持久
          p.vx *= 0.995
          p.vy *= 0.995
          
          // 粒子闪烁和颜色变化效果
          if (!p.isUserCreated) {
            // 改变不透明度
            p.opacity += p.pulseDirection * p.pulseSpeed
            
            // 在最大和最小不透明度之间切换方向
            if (p.opacity >= p.originalOpacity + 0.3) {
              p.pulseDirection = -1
            } else if (p.opacity <= p.originalOpacity - 0.3) {
              p.pulseDirection = 1
            }
            
            // 颜色变化效果
            if (p.colorShift) {
              p.colorPhase = (p.colorPhase + 0.5) % 360
              
              // 根据相位计算HSL颜色
              const h = p.colorPhase
              const s = 70
              const l = 70
              
              // 将HSL转换为RGB
              const hslToRgb = (h, s, l) => {
                s /= 100
                l /= 100
                const k = n => (n + h / 30) % 12
                const a = s * Math.min(l, 1 - l)
                const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)))
                return [255 * f(0), 255 * f(8), 255 * f(4)]
              }
              
              const [r, g, b] = hslToRgb(h, s, l)
              p.currentColor = `rgba(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)},`
            }
          }
          
          // 绘制粒子
          ctx.beginPath()
          ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
          
          // 用户创建的粒子使用特殊颜色
          if (p.isUserCreated) {
            ctx.fillStyle = p.color.replace(')', `,${p.opacity * (p.life / 100)})`);
          } else if (p.colorShift && p.currentColor) {
            // 对于变色的粒子使用计算出的颜色
            ctx.fillStyle = `${p.currentColor}${p.opacity})`
          } else {
            ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`
          }
          
          ctx.fill()
        }
        
        // 绘制连线
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
        ctx.lineWidth = 0.5
        for (let i = 0; i < this.particles.length; i++) {
          for (let j = i + 1; j < this.particles.length; j++) {
            const p1 = this.particles[i]
            const p2 = this.particles[j]
            const distance = Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2))
            
            // 当两个粒子速度方向相似时，更容易形成连线
            const dotProduct = p1.vx * p2.vx + p1.vy * p2.vy
            const speedProduct = Math.sqrt(p1.vx * p1.vx + p1.vy * p1.vy) * Math.sqrt(p2.vx * p2.vx + p2.vy * p2.vy)
            const angleConsistency = speedProduct > 0.1 ? dotProduct / speedProduct : 0
            const consistencyBonus = angleConsistency > 0 ? 30 : 0 // 增加相似方向的连线距离
            
            // 颜色粒子和普通粒子更容易连线
            const colorBonus = (p1.colorShift || p2.colorShift) ? 20 : 0
            
            if (distance < 100 + consistencyBonus + colorBonus) {
              ctx.beginPath()
              ctx.moveTo(p1.x, p1.y)
              ctx.lineTo(p2.x, p2.y)
              
              // 用户创建的粒子之间的连线更明显
              if (p1.isUserCreated && p2.isUserCreated) {
                ctx.strokeStyle = `rgba(100, 200, 255, ${0.2 * (1 - distance / 100)})`
                ctx.lineWidth = 1
              } else if (p1.isUserCreated || p2.isUserCreated) {
                ctx.strokeStyle = `rgba(200, 200, 255, ${0.15 * (1 - distance / 100)})`
                ctx.lineWidth = 0.8
              } else {
                let opacity = 0.1 * (1 - distance / 100)
                // 类似方向的粒子连线更明显
                if (angleConsistency > 0.8) {
                  opacity *= 1.5
                }
                ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`
                ctx.lineWidth = 0.5
              }
              
              ctx.stroke()
            }
          }
        }
        
        // 更新和绘制鼠标跟随者
        if (mouseX && mouseY) {
          for (let i = 0; i < mouseFollowers.length; i++) {
            const follower = mouseFollowers[i]
            
            // 平滑跟随鼠标位置，减少延迟
            follower.x += (mouseX - follower.x) / (5 + follower.delay)
            follower.y += (mouseY - follower.y) / (5 + follower.delay)
            
            // 绘制跟随者
            ctx.beginPath()
            ctx.arc(follower.x, follower.y, follower.radius, 0, Math.PI * 2)
            
            // 根据索引使用不同颜色
            if (follower.color === 0) {
              ctx.fillStyle = `rgba(100, 200, 255, ${follower.opacity})`
            } else if (follower.color === 1) {
              ctx.fillStyle = `rgba(100, 255, 200, ${follower.opacity})`
            } else {
              ctx.fillStyle = `rgba(255, 200, 100, ${follower.opacity})`
            }
            
            ctx.fill()
            
            // 添加光环效果
            if (i < 3) { // 只给前几个粒子添加光环
              ctx.beginPath()
              ctx.arc(follower.x, follower.y, follower.radius * 2, 0, Math.PI * 2)
              
              if (follower.color === 0) {
                ctx.strokeStyle = `rgba(100, 200, 255, ${follower.opacity * 0.3})`
              } else if (follower.color === 1) {
                ctx.strokeStyle = `rgba(100, 255, 200, ${follower.opacity * 0.3})`
              } else {
                ctx.strokeStyle = `rgba(255, 200, 100, ${follower.opacity * 0.3})`
              }
              
              ctx.lineWidth = 1
              ctx.stroke()
            }
          }
        }
        
        // 维持粒子数量
        if (this.particles.length < particleCount) {
          this.particles.push(createParticle())
        }
        
        this.animationId = requestAnimationFrame(animate)
      }
      
      animate()
    },
    
    // 生成随机颜色
    getRandomColor() {
      const colors = [
        'rgba(100, 200, 255,', // 蓝色
        'rgba(100, 255, 200,', // 青色
        'rgba(200, 255, 100,', // 黄绿色
        'rgba(255, 100, 200,', // 粉色
        'rgba(255, 200, 100,'  // 橙色
      ]
      return colors[Math.floor(Math.random() * colors.length)]
    },
    getBaseColor() {
      const colors = [
        'rgba(255, 255, 255,', // 白色
        'rgba(200, 200, 255,', // 浅蓝色
        'rgba(100, 100, 255,', // 浅蓝色
        'rgba(200, 200, 200,', // 灰色
        'rgba(100, 100, 100,'  // 灰色
      ]
      return colors[Math.floor(Math.random() * colors.length)]
    }
  }
}
</script>

<style lang="scss" scoped>
$bg: #2d3a4b;
$light_gray: #fff;
$cursor: #fff;
$primary: #409EFF;
$highlight: #66b1ff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: $cursor;
  }
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.05); opacity: 1; }
  100% { transform: scale(1); opacity: 0.8; }
}

@keyframes titleGlow {
  0% { text-shadow: 0 0 5px rgba(64, 158, 255, 0.5); }
  50% { text-shadow: 0 0 15px rgba(64, 158, 255, 0.8), 0 0 30px rgba(64, 158, 255, 0.5); }
  100% { text-shadow: 0 0 5px rgba(64, 158, 255, 0.5); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.login-container {
  min-height: 100%;
  width: 100%;
  background-color: $bg;
  background-image: linear-gradient(135deg, #2d3a4b 0%, #1a2236 100%);
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;

  .particles-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
  }

  .login-box {
    width: 520px;
    max-width: 100%;
    padding: 30px;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
    position: relative;
    z-index: 1;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
  }

  .login-logo {
    text-align: center;
    margin-bottom: 30px;

    h2 {
      font-size: 28px;
      color: $light_gray;
      margin-bottom: 5px;
      
      &.animated-title {
        animation: titleGlow 3s infinite;
      }
    }

    p {
      font-size: 14px;
      color: #8899ac;
      letter-spacing: 1px;
    }
  }

  .login-form {
    position: relative;
    width: 100%;
    max-width: 100%;
    overflow: hidden;
    
    &.shake {
      animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
    }
  }

  .icon-container {
    padding: 6px 5px 6px 15px;
    color: $light_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
    
    .pulse {
      animation: pulse 2s infinite;
    }
  }

  .title-container {
    position: relative;

    .title {
      font-size: 22px;
      color: $light_gray;
      margin: 0px auto 30px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $light_gray;
    cursor: pointer;
    user-select: none;
  }

  .additional-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    color: $light_gray;

    .forgot-password {
      color: $highlight;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.3s;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }

  .login-button {
    width: 100%;
    margin-bottom: 20px;
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
    overflow: hidden;
    position: relative;
    
    .button-text {
      margin-right: 10px;
      transition: all 0.3s;
    }
    
    .arrow-icon {
      transition: all 0.3s;
      opacity: 0;
      transform: translateX(-20px);
    }
    
    &.button-hover {
      .button-text {
        transform: translateX(-10px);
      }
      
      .arrow-icon {
        opacity: 1;
        transform: translateX(0);
      }
    }
  }

  .tip-text {
    color: $highlight;
    font-size: 12px;
    margin-top: -15px;
    margin-bottom: 15px;
    padding-left: 40px;
    opacity: 0.8;
    transition: all 0.3s;
  }

  .system-info {
    text-align: center;
    color: rgba(255, 255, 255, 0.5);
    font-size: 12px;
    
    .highlight-text {
      color: $highlight;
      cursor: pointer;
      
      &:hover {
        text-decoration: underline;
      }
    }
    
    p {
      margin: 5px 0;
    }
  }
}
</style>

<style lang="scss">
$bg: #2d3a4b;
$light_gray: #eee;

.login-container {
  .el-input {
    display: inline-block;
    height: 47px;
    width: 85%;

    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
      caret-color: $light_gray;

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px $bg inset !important;
        -webkit-text-fill-color: $light_gray !important;
      }
    }
  }

  .el-form-item {
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
    margin-bottom: 20px;
    transition: all 0.3s;
    
    &:focus-within {
      border-color: rgba(64, 158, 255, 0.5);
      box-shadow: 0 0 10px rgba(64, 158, 255, 0.3);
    }
  }

  .el-button--primary {
    background: #409EFF;
    border: none;
    font-size: 16px;
    font-weight: bold;
    border-radius: 5px;
    box-shadow: 0 5px 15px rgba(64, 158, 255, 0.3);
    transition: all 0.3s;

    &:hover {
      background: #66b1ff;
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(64, 158, 255, 0.4);
    }
    
    &:active {
      transform: translateY(0);
      box-shadow: 0 3px 10px rgba(64, 158, 255, 0.3);
    }
  }
  
  .el-checkbox__input.is-checked .el-checkbox__inner,
  .el-checkbox__input.is-indeterminate .el-checkbox__inner {
    background-color: #409EFF;
    border-color: #409EFF;
  }
  
  .el-checkbox__inner:hover {
    border-color: #409EFF;
  }
  
  .el-checkbox__label {
    color: $light_gray;
  }
}
</style> 
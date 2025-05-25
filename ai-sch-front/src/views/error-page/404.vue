<template>
  <div class="error-container">
    <div class="error-content">
      <div class="error-code">404</div>
      <div class="error-message">{{ message }}</div>
      <div class="error-desc">请检查您输入的URL是否正确，或者点击下方按钮返回首页。</div>
      <router-link to="/home" class="error-btn">返回首页</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Page404',
  computed: {
    message() {
      return '很抱歉，您访问的页面不存在...'
    }
  }
}
</script>

<style lang="scss" scoped>
.error-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f8f9;
}

.error-content {
  text-align: center;
  width: 500px;
  padding: 40px;
  background: #fff;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #1482f0;
  margin-bottom: 20px;
  line-height: 1;
  position: relative;
  display: inline-block;
  
  &:before, &:after {
    content: '';
    position: absolute;
    background: #d0e8ff;
    border-radius: 50%;
    z-index: -1;
  }
  
  &:before {
    width: 60px;
    height: 60px;
    top: -10px;
    left: -20px;
    opacity: 0.7;
  }
  
  &:after {
    width: 40px;
    height: 40px;
    bottom: 10px;
    right: -10px;
    opacity: 0.5;
  }
}

.error-message {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
}

.error-desc {
  font-size: 16px;
  color: #666;
  margin-bottom: 30px;
}

.error-btn {
  display: inline-block;
  padding: 10px 30px;
  background: #1482f0;
  border-radius: 50px;
  color: white;
  font-weight: bold;
  text-decoration: none;
  transition: all 0.3s ease;
  
  &:hover {
    background: #0056b3;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 86, 179, 0.3);
  }
}
</style> 
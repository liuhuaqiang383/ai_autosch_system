<template>
  <div :class="{'hidden':hidden}" class="pagination-container">
    <el-pagination
      :background="background"
      :current-page.sync="currentPage"
      :page-size.sync="pageSize"
      :layout="layout"
      :page-sizes="pageSizes"
      :pager-count="pagerCount"
      :hide-on-single-page="false"
      :total="total"
      v-bind="$attrs"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script>
export default {
  name: 'Pagination',
  props: {
    total: {
      required: true,
      type: Number
    },
    page: {
      type: Number,
      default: 1
    },
    limit: {
      type: Number,
      default: 10
    },
    pageSizes: {
      type: Array,
      default() {
        return [5, 10, 15, 20]
      }
    },
    // 移动端页码按钮的数量端默认值5
    pagerCount: {
      type: Number,
      default: document.body.clientWidth < 992 ? 5 : 7
    },
    layout: {
      type: String,
      default: 'prev, pager, next'
    },
    background: {
      type: Boolean,
      default: true
    },
    autoScroll: {
      type: Boolean,
      default: true
    },
    hidden: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    currentPage: {
      get() {
        return this.page
      },
      set(val) {
        this.$emit('update:page', val)
      }
    },
    pageSize: {
      get() {
        return this.limit
      },
      set(val) {
        this.$emit('update:limit', val)
      }
    }
  },
  methods: {
    handleSizeChange(val) {
      if (this.currentPage * val > this.total) {
        this.currentPage = 1
      }
      this.$emit('pagination', { page: this.currentPage, limit: val })
      if (this.autoScroll) {
        scrollTo(0, 800)
      }
    },
    handleCurrentChange(val) {
      this.$emit('pagination', { page: val, limit: this.pageSize })
      if (this.autoScroll) {
        scrollTo(0, 800)
      }
    }
  }
}

function scrollTo(to, duration) {
  const start = document.documentElement.scrollTop || document.body.scrollTop
  const change = to - start
  const increment = 20
  let currentTime = 0
  
  duration = (typeof (duration) === 'undefined') ? 500 : duration
  
  const animateScroll = function() {
    currentTime += increment
    const val = easeInOutQuad(currentTime, start, change, duration)
    document.documentElement.scrollTop = val
    document.body.scrollTop = val
    
    if (currentTime < duration) {
      setTimeout(animateScroll, increment)
    }
  }
  
  animateScroll()
}

function easeInOutQuad(t, b, c, d) {
  t /= d / 2
  if (t < 1) {
    return c / 2 * t * t + b
  }
  t--
  return -c / 2 * (t * (t - 2) - 1) + b
}
</script>

<style scoped>
.pagination-container {
  background: #fff;
  padding: 10px;
  display: flex;
  justify-content: center;
  margin-top: 5px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}
.pagination-container.hidden {
  display: none;
}
.pagination-container .el-pagination {
  padding: 0;
  font-weight: normal;
}
.pagination-container .el-pagination button {
  min-width: 35px;
}
.pagination-container .el-pagination .el-pager li {
  min-width: 35px;
}
.pagination-container .el-pagination .el-pager li.active {
  color: #fff;
  background-color: #409EFF;
  border-radius: 2px;
}
</style> 
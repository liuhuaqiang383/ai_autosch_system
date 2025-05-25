<template>
  <div :class="classObj" class="app-wrapper">
    <sidebar class="sidebar-container" :is-collapse="isCollapse" />
    <div class="main-container">
      <div :class="{'fixed-header':fixedHeader}">
        <navbar @toggleClick="toggleSideBar" :is-collapse="isCollapse" />
      </div>
      <app-main />
    </div>
  </div>
</template>

<script>
import { Navbar, Sidebar, AppMain } from './components'

export default {
  name: 'Layout',
  components: {
    Navbar,
    Sidebar,
    AppMain
  },
  data() {
    return {
      isCollapse: false
    }
  },
  computed: {
    classObj() {
      return {
        hideSidebar: this.isCollapse,
        openSidebar: !this.isCollapse,
        withoutAnimation: false
      }
    },
    fixedHeader() {
      return true
    }
  },
  methods: {
    toggleSideBar() {
      this.isCollapse = !this.isCollapse
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/styles/variables.scss";

.app-wrapper {
  @include clearfix;
  position: relative;
  height: 100%;
  width: 100%;
  overflow: hidden;

  &.mobile.openSidebar {
    position: fixed;
    top: 0;
  }
}

.fixed-header {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9;
  width: calc(100% - #{$sideBarWidth});
  transition: width 0.28s;
}

.hideSidebar .fixed-header {
  width: calc(100% - 54px)
}

</style> 
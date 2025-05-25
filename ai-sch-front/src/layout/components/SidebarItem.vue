<template>
  <div v-if="!item.hidden" class="menu-wrapper">
    <!-- 没有子菜单的情况 -->
    <template v-if="!hasChildren(item)">
      <router-link :to="resolvePath(item.path)">
        <el-menu-item :index="resolvePath(item.path)">
          <i v-if="item.meta && item.meta.icon" :class="'el-icon-' + item.meta.icon"></i>
          <span slot="title">{{ item.meta.title }}</span>
        </el-menu-item>
      </router-link>
    </template>
    
    <!-- 有子菜单的情况 -->
    <el-submenu v-else ref="submenu" :index="resolvePath(item.path)" popper-append-to-body>
      <template slot="title">
        <i v-if="item.meta && item.meta.icon" :class="'el-icon-' + item.meta.icon"></i>
        <span>{{ item.meta.title }}</span>
      </template>
      
      <sidebar-item
        v-for="child in item.children"
        :key="child.path"
        :is-nest="true"
        :item="child"
        :base-path="resolvePath(child.path)"
        class="nest-menu"
      />
    </el-submenu>
  </div>
</template>

<script>
import path from 'path'

export default {
  name: 'SidebarItem',
  props: {
    // 路由对象
    item: {
      type: Object,
      required: true
    },
    // 是否嵌套
    isNest: {
      type: Boolean,
      default: false
    },
    // 基础路径
    basePath: {
      type: String,
      default: ''
    }
  },
  methods: {
    hasChildren(item) {
      return item.children && item.children.length > 0 && !item.hidden
    },
    resolvePath(routePath) {
      if (this.isExternalLink(routePath)) {
        return routePath
      }
      if (this.isExternalLink(this.basePath)) {
        return this.basePath
      }
      return path.resolve(this.basePath, routePath)
    },
    isExternalLink(path) {
      return /^(https?:|mailto:|tel:)/.test(path)
    }
  }
}
</script> 
<template>
  <component :is="type" v-bind="linkProps(to)">
    <slot />
  </component>
</template>

<script>
import { isExternal } from '@/utils/validate'

export default {
  name: 'AppLink',
  props: {
    to: {
      type: String,
      required: true
    }
  },
  computed: {
    type() {
      if (isExternal(this.to)) {
        return 'a'
      }
      return 'router-link'
    }
  },
  methods: {
    linkProps(url) {
      if (isExternal(url)) {
        return {
          href: url,
          target: '_blank',
          rel: 'noopener'
        }
      }
      return {
        to: url
      }
    }
  }
}
</script> 
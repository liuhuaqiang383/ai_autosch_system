    // 获取教师列表
    getTeacherOptions() {
      getTeachers({ _fetchAll: true }).then(response => {
        if (response && response.results) {
          this.teacherOptions = response.results
          console.log(`加载了${this.teacherOptions.length}名教师选项`)
        }
      })
    }, 
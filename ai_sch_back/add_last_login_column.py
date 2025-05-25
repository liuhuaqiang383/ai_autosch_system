import os
import django
import MySQLdb

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sch_back.settings')
django.setup()

from django.conf import settings

def add_missing_columns():
    """
    直接在数据库中添加缺失的列
    """
    # 获取数据库配置
    db_settings = settings.DATABASES['default']
    
    # 连接数据库
    conn = MySQLdb.connect(
        host=db_settings['HOST'],
        user=db_settings['USER'],
        passwd=db_settings['PASSWORD'],
        db=db_settings['NAME'],
        port=int(db_settings.get('PORT', 3306))
    )
    
    try:
        # 创建游标
        cursor = conn.cursor()
        
        # 需要添加的列
        columns = [
            ("last_login", "DATETIME NULL COMMENT '最后登录时间'"),
            ("is_superuser", "TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否超级用户'"),
            ("is_active", "TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否活跃'"),
            ("is_staff", "TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否是管理员'")
        ]
        
        for column_name, column_def in columns:
            # 检查列是否已存在
            cursor.execute(f"SHOW COLUMNS FROM sys_user LIKE '{column_name}'")
            column_exists = cursor.fetchone()
            
            if not column_exists:
                # 添加列
                cursor.execute(f"ALTER TABLE sys_user ADD COLUMN {column_name} {column_def}")
                conn.commit()
                print(f"成功添加{column_name}列")
            else:
                print(f"{column_name}列已存在")
        
        # 检查权限相关表是否存在
        cursor.execute("SHOW TABLES LIKE 'auth_group'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE `auth_group` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `name` varchar(150) NOT NULL,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `name` (`name`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """)
            print("成功创建auth_group表")
        
        cursor.execute("SHOW TABLES LIKE 'auth_group_permissions'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE `auth_group_permissions` (
                    `id` bigint NOT NULL AUTO_INCREMENT,
                    `group_id` int NOT NULL,
                    `permission_id` int NOT NULL,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
                    KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """)
            print("成功创建auth_group_permissions表")
        
        cursor.execute("SHOW TABLES LIKE 'auth_permission'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE `auth_permission` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `name` varchar(255) NOT NULL,
                    `content_type_id` int NOT NULL,
                    `codename` varchar(100) NOT NULL,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """)
            print("成功创建auth_permission表")
        
        cursor.execute("SHOW TABLES LIKE 'django_content_type'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE `django_content_type` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `app_label` varchar(100) NOT NULL,
                    `model` varchar(100) NOT NULL,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """)
            print("成功创建django_content_type表")
        
        # 添加用户权限关联表
        cursor.execute("SHOW TABLES LIKE 'sys_user_groups'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE `sys_user_groups` (
                    `id` bigint NOT NULL AUTO_INCREMENT,
                    `sysuser_id` bigint NOT NULL,
                    `group_id` int NOT NULL,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `sys_user_groups_sysuser_id_group_id_unique` (`sysuser_id`,`group_id`),
                    KEY `sys_user_groups_group_id_fk` (`group_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """)
            print("成功创建sys_user_groups表")
        
        cursor.execute("SHOW TABLES LIKE 'sys_user_user_permissions'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE `sys_user_user_permissions` (
                    `id` bigint NOT NULL AUTO_INCREMENT,
                    `sysuser_id` bigint NOT NULL,
                    `permission_id` int NOT NULL,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `sys_user_user_permissions_sysuser_id_permission_id_unique` (`sysuser_id`,`permission_id`),
                    KEY `sys_user_user_permissions_permission_id_fk` (`permission_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """)
            print("成功创建sys_user_user_permissions表")
            
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭连接
        conn.close()

if __name__ == "__main__":
    add_missing_columns() 
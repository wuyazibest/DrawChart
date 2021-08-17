



CREATE TABLE `open_api_uri` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `create_time` datetime NOT NULL COMMENT '创建时间',
  `update_time` datetime NOT NULL COMMENT '更新时间',
  `author` varchar(191) NOT NULL COMMENT '变更人',
  `is_deleted` int(11) NOT NULL COMMENT '删除标志',
  `comment` text NOT NULL COMMENT '备注',
  `request_method` varchar(191) NOT NULL COMMENT '请求方式',
  `uri` varchar(191) NOT NULL COMMENT 'uri',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_open_api_uri_request_method_uri` (`request_method`,`uri`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='接口开放平台uri';


CREATE TABLE `open_api_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `create_time` datetime NOT NULL COMMENT '创建时间',
  `update_time` datetime NOT NULL COMMENT '更新时间',
  `author` varchar(191) NOT NULL COMMENT '变更人',
  `is_deleted` int(11) NOT NULL COMMENT '删除标志',
  `comment` text NOT NULL COMMENT '备注',
  `username` varchar(191) NOT NULL COMMENT '用户名',
  `nickname` varchar(191) NOT NULL COMMENT '昵称',
  `password_hash` varchar(191) NOT NULL COMMENT '密码hash',
  `last_login` datetime NOT NULL COMMENT '最后登录时间',
  `role` varchar(191) NOT NULL COMMENT '角色',
  `is_active` tinyint(1) NOT NULL COMMENT '活跃标志',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_open_api_user_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='接口开放平台用户';


CREATE TABLE `open_api_user_uri` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `create_time` datetime NOT NULL COMMENT '创建时间',
  `update_time` datetime NOT NULL COMMENT '更新时间',
  `author` varchar(191) NOT NULL COMMENT '变更人',
  `is_deleted` int(11) NOT NULL COMMENT '删除标志',
  `comment` text NOT NULL COMMENT '备注',
  `username` varchar(191) NOT NULL COMMENT '用户名',
  `request_method` varchar(191) NOT NULL COMMENT '请求方式',
  `uri` varchar(191) NOT NULL COMMENT 'uri',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_open_api_username_uri_request_method_uri` (`username`,`request_method`,`uri`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='接口开放平台用户的uri';
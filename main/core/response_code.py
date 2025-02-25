# coding:utf-8

class RET:
    OK                      = "0"       # 成功
    SUCCESS                 = "0"       # 成功
    
    PARAMERR                = "4100"    # 参数错误
    RequiredERR             = "4101"    # 必填参数缺失
    VALIDERR                = "4102"    # 参数校验错误
    EnumERR                 = "4103"    # 参数枚举错误
    
    AUTHERR                 = "4200"    # 认证失败
    UserNotExite            = "4201"    # 用户不存在
    PWDERR                  = "4202"    # 密码错误
    NotActive               = "4203"    # 用户未启用
    JWTDecodeError          = "4204"    # token解析失败
    JWTExpiredError         = "4205"    # token超时
    JWTImmatureError        = "4206"    # token未生效
    JWTFormatError          = "4207"    # token格式
    
    PermERR                 = "4300"    # 权限错误
    NotLogging              = "4301"    # 用户未登录
    NoPerm                  = "4302"    # 用户无权限
    
    DATAERR                 = "4400"    # 数据错误
    NODATA                  = "4401"    # 数据不存在
    EXISTDATA               = "4402"    # 数据已存在
    DBERR                   = "4403"    # 数据库错误
    
    SYSERR                  = "4500"    # 系统错误
    REQERR                  = "4501"    # 非法请求或请求次数受限
    IPERR                   = "4502"    # IP受限
    METHODERR               = "4503"    # 请求方法错误
    INNERERR                = "4504"    # 内部错误
    IOERR                   = "4505"    # 文件读写错误
    
    THIRDERR                = "4600"    # 三方系统错误
    
    UNKOWNERR               = "4700"    # 未知错位


error_map = {
    RET.OK              : u"成功",
    RET.SUCCESS         : u"成功",
    RET.PARAMERR        : u"参数错误",
    RET.RequiredERR     : u"必填参数缺失",
    RET.VALIDERR        : u"参数校验错误",
    RET.EnumERR         : u"参数枚举错误",
    RET.AUTHERR         : u"认证失败",
    RET.UserNotExite    : u"用户不存在",
    RET.PWDERR          : u"密码错误",
    RET.NotActive       : u"用户未启用",
    RET.JWTDecodeError  : u"token解析失败",
    RET.JWTExpiredError : u"token超时",
    RET.JWTImmatureError: u"token未生效",
    RET.JWTFormatError  : u"token格式",
    RET.PermERR         : u"权限错误",
    RET.NotLogging      : u"用户未登录",
    RET.NoPerm          : u"用户无权限",
    RET.DATAERR         : u"数据错误",
    RET.NODATA          : u"数据不存在",
    RET.EXISTDATA       : u"数据已存在",
    RET.DBERR           : u"数据库错误",
    RET.SYSERR          : u"系统错误",
    RET.REQERR          : u"非法请求或请求次数受限",
    RET.IPERR           : u"IP受限",
    RET.METHODERR       : u"请求方法错误",
    RET.INNERERR        : u"内部错误",
    RET.IOERR           : u"文件读写错误",
    RET.THIRDERR        : u"三方系统错误",
    RET.UNKOWNERR       : u"未知错位",
    }

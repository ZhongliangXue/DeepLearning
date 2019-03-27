import logging
# import os
# import SimpleITK as sitk # 由于类型未定义，暂时使用 SimpleITK
# import glob
# import abc
#
# class AlgFailedError:
#     """
#     @brief 算法错误处理标准类
#
#     @li OtherFailed          位置错误
#     @li PathCanNotFound      路径不存在
#     @li FileExist            文件已存在
#     @li FolderNotEmpty       文件夹非空
#     @li FolderEmpty          文件夹为空
#     @li ReadImageFailed      图像读取错误
#     @li DataError            数据错误
#     @li RuntimeFailed        运行过程中失败
#     @li OutofResources       资源不足
#     @li ParametersError      参数错误
#     @li TempFilePathNotExist 临时文件路径不存在
#     @li PythonFailed         捕获到的 Python 异常
#     """
#     OtherFailed          = -1
#     PathCanNotFound      = -2
#     FileExist            = -3
#     FolderNotEmpty       = -4
#     FolderEmpty          = -5
#     ReadImageFailed      = -6
#     DataError            = -7
#     RuntimeFailed        = -8
#     OutofResources       = -9
#     ParametersError      = -10
#     TempFilePathNotExist = -11
#     PythonFailed         = -12
#
#     def __init__(self, error: int, msg: str, *args, **kwargs):
#         """
#         @brief 创建错误
#
#         @param error  错误代码（使用预定义枚举类型）
#         @param msg    错误消息
#         @param args   附带的参数
#         @param kwargs 附带的参数
#         """
#         self._error_code   = error
#         self._error_msg    = msg
#         self._error_args   = args
#         self._error_kwargs = kwargs
#
#     @property
#     def error_code(self):
#         """
#         获取错误码
#         """
#         return self._error_code
#
#     @property
#     def error_msg(self):
#         """
#         获取错信息
#         """
#         return self._error_msg
#
# class ToolObject:
#     """
#     @brief 工具类基础函数
#
#     使用工厂函数创建类。
#
#     @note 派生类需要提供如下属性或者函数
#     @li ker_func 核心函数
#     @li fg_params   前端传递的参数
#     @li path_params 传递的图像路径参数
#     @li var_params  传递的变量参数
#     @li result_from_var 将结果转变为 SimpleITK 对象（暂时）
#
#     所有参数会被放置在 会传入 ker_func。self.ker_func(**self.__params) ker_func 需要把参数写入 self.result 变量中
#
#     fg_params 由字典组成，字典中每个键值就是一个参数（的名称），键值对应的值还是一个字典。
#     这个字典里面包括如下内容：类型、默认值、和检查函数，默认值和检查函数。这三者够可以缺少。
#     类型(typ)会通过 `isinstance(var,type)`来检查（var 是传入的数据，type 是字典里的类型）；
#     默认值(default)是当一个参数没有被填写时，使用的默认值，如果没有默认值，参数就是必填的，在没有填写的时候会报错。此外不对默认参数进行检查。
#     检查函(check)数是用来检查参数是否错误的，返回内容是一个元组，第一个参数是 bool, 第二个是错误原因（正确情况下随便）。
#
#     path_params 也是由字典组成的，每个键值就是参数（的名称），键值对应的值还是一个字典。
#     字典中还要包括如下内容：类型（str，还是list<str>)，处理文件还是目录，处理函数。
#     类型(typ)是字符串数组或者字符串。
#     “处理文件还是目录”(is_file)是指传入的参数是文件夹还是文件。
#     处理函数(handler)是把读取到的文件对象（已经解析出来的，带数据和标签的，目前用的是 SimpleITK）转化成所需要的数据（以字典形式存储，键值就是参数，应该是var_params中的键值，值就是具体内容
#
#     var_params 和 fg_params 一样。
#     """
#
#     __metaclass__ = abc.ABCMeta
#
#     @property
#     @abc.abstractclassmethod
#     def fg_params(self):
#         pass
#
#     @property
#     @abc.abstractclassmethod
#     def var_params(self):
#         pass
#
#     @property
#     @abc.abstractclassmethod
#     def path_params(self):
#         pass
#
#     @abc.abstractclassmethod
#     def ker_func(self, **kwargs):
#         pass
#
#     @abc.abstractclassmethod
#     def result_from_var(self, result):
#         return result
#
#     @property
#     def result(self):
#         return self._result
#     @result.setter
#     def result(self, value):
#         self._result = value
#
#     # __init__ 初始化函数
#     def __init__(self, **kwargs):
#         """
#         @brief 初始化函数，读取前端传递函数
#         """
#         self.__params  = {}
#         self.__is_vars = None
#
#         # 设置变量对应的值，并检查
#         for key in kwargs:
#             value = kwargs[key]
#             if key in self.fg_params:
#                 slot  = self.fg_params.pop(key)
#                 if not isinstance(value, slot.get('typ', ())):
#                     logging.error('参数 %s 的类型与要求的不符合' % key, key, value, slot.get('typ', ()), slot)
#                     return None # TODO write return
#                 check = slot.get('check', lambda x: (True,None))(value)
#                 if not check[0]:
#                     logging.error('参数 %s 未通过检查，原因是 %s' % (key, check[1]), key, value, slot.get('typ', ()), slot, check)
#                     return None # TODO write return
#                 logging.debug('设置参数 %s 为 %s' % (key, repr(value)), key, value, slot.get('typ', ()), slot, check)
#                 self.__params[key] = value
#             else:
#                 logging.warning('参数 %s 是未定义的，将会被忽略' % key, repr(key), repr(value))
#         # 检查是否有必填值未设置，同时设置默认值
#         for key in self.fg_params:
#             slot = self.fg_params[key]
#             if 'default' in slot:
#                 logging.debug('参数 %s 使用默认值 %s' % (key, repr(slot['default'])), key, slot)
#                 self.__params[key] = slot['default']
#             else:
#                 logging.error('参数 %s 未设置， 也没有默认值' % key, key, slot)
#                 return None # TODO
#
#
#     # set_params_from_files 设置影像文件参数
#     def set_params_from_files(self, **kwargs):
#         """
#         @brief 设置路径参数
#         """
#         if self.__is_vars == True:
#             logging.error('图像路径参数和变量参数互斥，不可同时使用')
#             return None # TODO write return
#         self.__is_vars = False
#
#         # 设置参数
#         for key in kwargs:
#             value = kwargs[key]
#             if key in self.path_params:
#                 slot = self.path_params.pop(key)
#                 if not os.path.exists(str(value)):
#                     logging.error('参数 %s 路径 %s 不存在' % (key, value), key, value, slot)
#                     return None # TODO write return
#                 read_result = None
#                 typ = slot.get('typ', str)
#                 if typ is str:
#                     if slot.get('is_file', True):
#                         read_result = sitk.ReadImage(str(value))
#                     else:
#                         files = glob.glob(os.path.join(str(value), '*'))
#                         files.sort()
#                         read_result = [sitk.ReadImage(p) for p in files]
#                 elif typ is list:
#                     read_result = [sitk.ReadImage(str(p)) for p in list(value)]
#                 if 'handler' in slot:
#                     keypairs = slot['handler'](read_result)
#                     for k in keypairs:
#                         if k in self.__params:
#                             logging.error('处理完的参数名 %s 一存在于 参数字典中' % k, k, self.__params)
#                             return None # TODO write
#                         self.__params[k] = keypairs[k]
#                 else:
#                     if key in self.__params:
#                         logging.error('参数 %s 已经存在，值为 %s' % (key, repr(self.__params[key])), key, self.__params)
#                         return None # TODO write return
#                     self.__params[key] = read_result
#             else:
#                 logging.warning('参数 %s 是未定义的，将被忽略' % key, key, value)
#         # 检查未定义参数
#         if len(self.path_params) != 0:
#             logging.error('有未填写的参数 %s' % list(self.path_params.keys()))
#             return None # TODO write return
#
#     # set_params_from_var   设置变量类参数
#     def set_params_from_var(self, **kwargs):
#         if self.__is_vars == False:
#             logging.error('图像路径参数和变量参数互斥，不可同时使用')
#             return None # TODO write return
#         self.__is_vars = True
#
#         # 设置变量对应的值，并检查
#         for key in kwargs:
#             value = kwargs[key]
#             if key in self.var_params:
#                 slot  = self.var_params.pop(key)
#                 if not isinstance(value, slot.get('typ', ())):
#                     logging.error('参数 %s 的类型与要求的不符合' % key, key, value, slot.get('typ', ()), slot)
#                     return None # TODO write return
#                 check = slot.get('check', lambda x: (True,None))(value)
#                 if not check[0]:
#                     logging.error('参数 %s 未通过检查，原因是 %s' % (key, check[1]), key, value, slot.get('typ', ()), slot, check)
#                     return None # TODO write return
#                 logging.debug('设置参数 %s 为 %s' % (key, repr(value)), key, value, slot.get('typ', ()), slot, check)
#                 self.__params[key] = value
#             else:
#                 logging.warning('参数 %s 是未定义的，将会被忽略' % key, key, value)
#         # 检查是否有必填值未设置，同时设置默认值
#         for key in self.var_params:
#             slot = self.var_params[key]
#             if 'default' in slot:
#                 logging.debug('参数 %s 使用默认值 %s' % (key, repr(slot['default'])), key, slot)
#                 self.__params[key] = slot['default']
#             else:
#                 logging.error('参数 %s 未设置， 也没有默认值' % key, key, slot)
#                 return None # TODO write return
#
#     # __call__ 调用函数
#     def __call__(self):
#         if self.__is_vars is None:
#             logging.error('路径参数或者变量参数未设置', self.__params)
#             return None # TODO write return
#         self.ker_func(**self.__params)
#
#     # get_result_as_files   获得结果
#     def get_result_as_file(self, path_to_save):
#         sitk.WriteImage(self.result_from_var(self.result), path_to_save)
#         return None
#     # get_result_as_var     获得变量
#     def get_result_as_var(self):
#         return self.result
#
# # class Test2(ToolObject):
# #     # ToolFactory('TestClass',print, dict(a = dict(typ=int,default=1,check=lambda x: (x > 0, ""))), dict(), dict(b = dict(typ=int,default=1,check=lambda x: (x > 0, ""))), True)):
# #     @property
# #     def fg_params(self):
# #         return dict(
# #             a = dict(typ=int, default=1, check=lambda x: (x > 0, ""))
# #             c = dict(typ=int, default=1, check=lambda x: (x > 0, ""))
# #             )
# #     @property
# #     def var_params(self):
# #         return dict(
# #             b = dict(typ=int, default=1, check=lambda x: (x > 0, ""))
# #             )
# #     @property
# #     def path_params(self):
# #         return dict()
#
# #     def ker_func(self, **kwargs):
# #         print(kwargs)
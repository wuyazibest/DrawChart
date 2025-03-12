#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : view.py
# @Time   : 2025/3/11 16:36
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import logging
import os
import uuid

from flask import request, send_file, send_from_directory, render_template
import numpy as np
import pandas as pd

from main.chaoxi.data_source import nmdis
from main.config import BASE_DIR
from main.core import (
    ModelViewSet,
    permission_classes,
    IsLoginPermission,
    IsAdminPermission,
    RequestFromPermission,
    RET,
    ParamError,
    DataError,
    AuthenticationFailed,
    jwt_encode_handler,
    json_resp,
    )
from main.draw_chart.data_source import tiobe, tencent_stock, ifeng_stock
from main.util.draw import draw_bar, draw_line, draw_timeline

logger = logging.getLogger(__name__)


class ChaoXiView(ModelViewSet):
    decorators = ()
    resources = "tiobe"
    
    def get_query(self):
        self.resources += "查询"
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_args}")
        
        file_name = "line_chaoxi_chart.html"
        file_path = os.path.join(BASE_DIR, "dist", file_name)
        if os.path.exists(file_path):
            return render_template(file_name)
        
        title = {
            "path"      : file_path,
            "title"     : "潮汐表",
            "xaxis_name": "时间",
            "yaxis_name": "潮高",
            }
        
        df = nmdis.get_fmt_data()
        draw_line(df.index.values.tolist(), df.to_dict("list"), **title)
        
        return render_template(file_name)

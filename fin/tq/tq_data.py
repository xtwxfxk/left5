import logging
import os.path
from datetime import datetime, timedelta
from typing import Union

import ray
import pandas as pd
from pandas import Series, Timestamp, DataFrame
from tqsdk2 import TqApi, TqAuth

SETTING = {'user': 'ahaha', 'password': 'xxxx',
           'FUTURE': 'future_symbols.csv', 'STOCK': 'stock_symbols.csv', 'OPTION': 'option_symbols.csv'}


@ray.remote
class TraceData:
    def __init__(self, account, password, save_dir: str = None):
        self.symbol = None
        self.klines_flag = False
        self.exchange = None
        self.logger = None
        self.api = TqApi(auth=TqAuth(account, password))
        self.root_dir = os.path.abspath(os.path.curdir)
        self.save_dir = save_dir if save_dir is not None else self.root_dir
        print(self.save_dir)

        self.init()

    def init(self, exchange: str = None, symbol: str = None) -> None:
        # 订阅数据需要的字段
        self.exchange = exchange
        self.symbol = symbol

        # 检查klines和log目录是否创建
        # klines_dir = os.path.join(self.root_dir, "klines")
        klines_dir = os.path.join(self.save_dir, "klines")
        if not os.path.exists(klines_dir):
            os.mkdir(klines_dir)
        log_dir = os.path.join(self.root_dir, "log")
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        # 准备日志记录工具
        self.logger = logging.getLogger("loging")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        logfile_path = os.path.join(os.path.join(self.root_dir, "log"),
                                    (datetime.now().date().strftime('%Y%m%d')))
        file_handler = logging.FileHandler(logfile_path, mode="a",
                                           encoding="utf8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    # 获取所有交易标的合约
    def get_all_symbols(self, ins_class, expired=False) -> list:
        """
        ins_class (str): [可选] 合约类型
                * FUTURE: 期货
                * STOCK: 股票
        """
        exchanges = []
        all_symbols = []
        if ins_class == "FUTURE":
            exchanges = ["SHFE", "CFFEX", "DCE", "CZCE", "INE"]
        elif ins_class == "STOCK":
            exchanges = ["SSE", "SZSE"]

        for exchange in exchanges:
            symbol = self.api.query_quotes(ins_class=ins_class,
                                           exchange_id=exchange,
                                           expired=expired)
            all_symbols.extend(symbol)
        df: Series = pd.Series(all_symbols,
                               index=[i + 1 for i in range(len(all_symbols))])

        filename = SETTING.get(ins_class)
        filepath = os.path.join(self.save_dir, filename)
        if not os.path.exists(filepath):
            df.to_csv(filepath, index=True, header=False)

        return all_symbols

    def save_klines(self, symbols: list):
        """下载指定标的k线数据"""
        klines_dir_path = os.path.join(os.path.join(self.save_dir, "klines"),
                                       datetime.now().date().strftime('%Y%m%d'))

        if not os.path.exists(klines_dir_path):
            os.mkdir(klines_dir_path)

        for symbol in symbols:
            klines_file_path = os.path.join(klines_dir_path, f"{symbol}.csv")
            if os.path.exists(klines_file_path):
                continue

            klines = pd.DataFrame()

            try:
                klines = self.api.get_kline_serial(symbol, 60, 600)

            except Exception as e:
                self.logger.log(logging.WARNING, f"{e}")
                print(f"{datetime.now()}:{e}")

            if not klines.empty:
                klines_copy = klines.copy(deep=True)
                klines_copy["new_datetime"]: datetime = klines_copy[
                    "datetime"].apply(
                    lambda x: Timestamp(x).to_pydatetime() + timedelta(hours=8))
                local_time = datetime.now()
                klines_copy = klines_copy[
                    (klines_copy.new_datetime >= datetime(local_time.year,
                                                          local_time.month,
                                                          local_time.day - 1,
                                                          15,
                                                          30)) & (
                            klines_copy.new_datetime < datetime(local_time.year,
                                                                local_time.month,
                                                                local_time.day,
                                                                15,
                                                                30))]
                klines_copy["date"] = klines_copy["new_datetime"].apply(
                    lambda x: x.date().strftime("%Y%m%d"))
                klines_copy["time"] = klines_copy["new_datetime"].apply(
                    lambda x: x.time().strftime("%H:%M:%S"))
                klines_copy = klines_copy.drop(["new_datetime", "datetime"],
                                               axis=1)
                klines_copy.to_csv(klines_file_path, index=False)
                # 输出日志
                self.logger.log(logging.INFO, f"{symbol}.csv文件创建完成！")
                print(f"{datetime.now()},{symbol}.csv文件创建完成！")
            else:
                # 输出日志
                self.logger.log(logging.WARNING, f"{symbol}.csv文件为空！")
                print(f"{datetime.now()},{symbol}.csv文件为空！")

    def save_bars(self, symbols: list, duration_seconds: int, start: datetime,
                  end: datetime,
                  adj_type: Union[str, None] = None):
        """下载指定标的k线数据
        adj_type (str/None): [可选]指定复权类型，默认为 None。adj_type 参数只对股票和基金类型合约有效。\
            "F" 表示前复权；"B" 表示后复权；None 表示不做处理。
        """
        if adj_type == "F":
            klines_dir_path = os.path.join(self.save_dir,
                                           f"F_klines_{str(duration_seconds)}s")
        elif adj_type == "B":
            klines_dir_path = os.path.join(self.save_dir,
                                           f"B_klines_{str(duration_seconds)}s")
        else:
            klines_dir_path = os.path.join(self.save_dir,
                                           f"klines_{str(duration_seconds)}s")
        if not os.path.exists(klines_dir_path):
            os.mkdir(klines_dir_path)

        klines = pd.DataFrame()

        for symbol in symbols:
            klines_file_path = os.path.join(klines_dir_path, f"{symbol}.csv")
            if os.path.exists(klines_file_path):
                continue
            try:
                klines = self.api.get_kline_data_series(symbol,
                                                        duration_seconds, start,
                                                        end, adj_type)

            except Exception as e:
                self.logger.log(logging.WARNING, f"{e}")
                print(f"{datetime.now()}:{e}")

            if not klines.empty:
                klines_copy = klines.copy(deep=True)
                klines_copy["new_datetime"]: datetime = klines_copy[
                    "datetime"].apply(
                    lambda x: Timestamp(x).to_pydatetime() + timedelta(hours=8))
                klines_copy["date"] = klines_copy["new_datetime"].apply(
                    lambda x: x.date().strftime("%Y%m%d"))
                klines_copy["time"] = klines_copy["new_datetime"].apply(
                    lambda x: x.time().strftime("%H:%M:%S"))
                klines_copy = klines_copy.drop(["new_datetime", "datetime"],
                                               axis=1)
                klines_copy.to_csv(klines_file_path, index=False)
                # 输出日志
                self.logger.log(logging.INFO, f"{symbol}.csv文件创建完成！")
                print(f"{datetime.now()},{symbol}.csv文件创建完成！")
            else:
                # 输出日志
                self.logger.log(logging.WARNING, f"{symbol}.csv文件为空！")
                print(f"{datetime.now()},{symbol}.csv文件为空！")


def download_today_klines(task_num, ins_class) -> None:
    """
    task_num: 进程数
    ins_class = FUTURE/STOCK
    """
    symbols_filepath = SETTING.get(ins_class)

    if not os.path.exists(symbols_filepath):
        tq = TraceData.remote(SETTING.get("user"), SETTING.get("password"), 'Y:/tq_data')
        symbols = ray.get(tq.get_all_symbols.remote(ins_class=ins_class))
        ray.shutdown()
    else:
        symbols = pd.read_csv(symbols_filepath)
        symbols = list(symbols.iloc[:, 1].values)

    start_time = datetime.now()
    tqs = [TraceData.remote(SETTING.get("user"), SETTING.get("password"), 'Y:/tq_data') for _
           in range(task_num)]
    length = len(symbols) // task_num
    task_id = []
    for i in range(task_num):
        if i == task_num - 1:
            symbols_part = symbols[i * length:]
        else:
            symbols_part = symbols[i * length:(i + 1) * length]
        id_ = tqs[i].save_klines.remote(symbols_part)
        task_id.append(id_)
    ray.get(task_id)
    end_time = datetime.now()
    print(end_time - start_time)


def download_history_klines(task_num, ins_class, start, end,
                            adj_type: Union[str, None] = None) -> None:
    """
    task_num: 进程数
    ins_class = FUTURE/STOCK
    start: 开始时间
    end: 结束时间
    """
    symbols_filepath = SETTING.get(ins_class)

    expired = True if ins_class == 'FUTURE' or ins_class == 'OPTION' else False

    if not os.path.exists(symbols_filepath):
        tq = TraceData.remote(SETTING.get("user"), SETTING.get("password"), 'Y:/tq_data')
        symbols = ray.get(tq.get_all_symbols.remote(
            ins_class=ins_class,
            expired=expired))
        ray.shutdown()
    else:
        symbols = pd.read_csv(symbols_filepath)
        symbols = list(symbols.iloc[:, 1].values)

    start_time = datetime.now()
    tqs = [TraceData.remote(SETTING.get("user"), SETTING.get("password"), 'Y:/tq_data') for _
           in range(task_num)]
    length = len(symbols) // task_num
    task_id = []
    for i in range(task_num):
        if i == task_num - 1:
            symbols_part = symbols[i * length:]
        else:
            symbols_part = symbols[i * length:(i + 1) * length]

        duration_seconds = 60 if ins_class == "FUTURE" else 86400

        id_ = tqs[i].save_bars.remote(symbols_part,
                                      duration_seconds=duration_seconds,
                                      start=start, end=end,
                                      adj_type=adj_type)  # 确保数据都可以下载到
        task_id.append(id_)
    ray.get(task_id)
    end_time = datetime.now()
    print(end_time - start_time)


if __name__ == '__main__':
    download_history_klines(8, ins_class="FUTURE", start=datetime(2018, 1, 1),
                            end=datetime(2023, 5, 1))
    # download_history_klines(8, ins_class="STOCK", start=datetime(2018, 1, 1),
    #                         end=datetime(2023, 4, 19), adj_type="F")
    # download_history_klines(8, ins_class="STOCK", start=datetime(2018, 1, 1),
    #                         end=datetime(2023, 4, 19), adj_type="B")
    # download_history_klines(8, ins_class="STOCK", start=datetime(2018, 1, 1),
    #                         end=datetime(2023, 4, 19))

    # download_history_klines(8, ins_class="OPTION", start=datetime(2018, 1, 1),
                            # end=datetime(2023, 4, 19))


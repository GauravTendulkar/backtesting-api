import os
from filelock import FileLock
import pandas as pd
import pyarrow.parquet as pq
import pyarrow.feather as feather

extension = ".parquet"
# extension = ".csv"



def if_path_exist(path, extension = extension):
    return os.path.exists(f"{path}{extension}")

def lock_file(path, extension = extension):
    # print("lock_file", extension )
    lock_path = f"{path}{extension}" + ".lock"
    # print(lock_path)
    lock = FileLock(lock_path)
    return lock

def read_file(path, extension = extension, col= None):
    # print("read_file",extension)
    if extension == ".csv":
        if col is None:
            return pd.read_csv(f"{path}.csv", low_memory=False,index_col=["index"])
        elif "datetime" in col:
            return pd.read_csv(f"{path}.csv", low_memory=False,index_col=["index"])
        else:
            return pd.read_csv(f"{path}.csv", low_memory=False,index_col=["index"])

    if extension == ".parquet":
        if col is None:
            return pd.read_parquet(f"{path}.parquet", columns=col)
        elif "datetime" in col:
            return pd.read_parquet(f"{path}.parquet", columns=col)
        else:
            return pd.read_parquet(f"{path}.parquet", columns=col)
        

    if extension == ".feather":
        if col is None:
            return pd.read_feather(f"{path}.feather", columns=col)
        elif "datetime" in col:
            return pd.read_feather(f"{path}.feather", columns=col)
        else:
            return pd.read_feather(f"{path}.feather", columns=col )
        

    if extension == ".pickle":
        if col is None:
            return pd.read_pickle(f"{path}.pickle" )
        if col :
            df = pd.read_pickle(f"{path}.pickle" )
            try:
                    col.remove('datetime')
            except:
                    pass
            df = df[col]
            return df 
        
def to_file(df, path, extension = extension):
    # print("to_file", extension)
    if extension == ".csv":
        
        df.to_csv(f"{path}.csv")

    if extension == ".parquet":
        df.to_parquet(f"{path}.parquet")
        

    if extension == ".feather":
        df.to_feather(f"{path}.feather")
        

    if extension == ".pickle":
        df.to_pickle(f"{path}.pickle")


def get_columns(path, extension = extension):
    # print("get_columns", extension)
    if extension == ".csv":
        return pd.read_csv(f"{path}.csv", nrows=0).columns.tolist()
        

    if extension == ".parquet":
        return pq.read_schema(f"{path}.parquet").names          
        

    if extension == ".feather":
        return feather.read_table(f"{path}.feather").column_names  
        

    if extension == ".pickle":
        return pd.read_pickle(f"{path}.pickle").columns.tolist()          
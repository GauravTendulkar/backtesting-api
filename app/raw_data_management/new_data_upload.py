import os
import shutil
import aiofiles
import asyncio
from functools import partial
from ..backtesting_duckdb import CLEAN_NEW_DATA, TEMP_CHUNKS_DIR
from ..config.files_path import SHARED_FILES_PATH
import duckdb

UPLOAD_DIR = CLEAN_NEW_DATA
# TEMP_DIR = f"{SHARED_FILES_PATH}/Clean_data/temp_chunks"
# os.makedirs(TEMP_DIR, exist_ok=True)


def new_file_upload(files):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved_files = []
    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)
    return {"message": "Files uploaded successfully", "files": saved_files}
    

# upload-chunk
async def upload_by_chunk(file, chunk_index, total_chunks, file_name):

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    temp_dir = os.path.join(TEMP_CHUNKS_DIR, file_name)
    os.makedirs(temp_dir, exist_ok=True)

    # Save this chunk
    chunk_path = os.path.join(temp_dir, f"chunk_{chunk_index}")
    async with aiofiles.open(chunk_path, "wb") as f:
        while data := await file.read(1024 * 1024):  # 1MB read buffer
            await f.write(data)

    # If last chunk — reassemble
    if chunk_index == total_chunks - 1:
        final_path = os.path.join(UPLOAD_DIR, file_name)
        async with aiofiles.open(final_path, "wb") as final_file:
            for i in range(total_chunks):
                chunk_file = os.path.join(temp_dir, f"chunk_{i}")
                async with aiofiles.open(chunk_file, "rb") as cf:
                    while data := await cf.read(1024 * 1024):
                        await final_file.write(data)

        shutil.rmtree(temp_dir)  # cleanup temp chunks
        return {"status": "complete", "file": file_name}

    return {"status": "chunk_received", "chunk": chunk_index, "total": total_chunks}


def upload_progress(file_name):
    temp_dir = os.path.join(TEMP_CHUNKS_DIR, file_name)
    if not os.path.exists(temp_dir):
        return {"uploaded_chunks": []}
    chunks = os.listdir(temp_dir)
    uploaded = [int(c.replace("chunk_", "")) for c in chunks if c.startswith("chunk_")]
    return {"uploaded_chunks": sorted(uploaded)}


def sizeof_fmt(num, suffix='B', unit="Gi"):
    for i in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if i == unit:
            # return f"{num:3.1f}{unit}{suffix}"
            return [num, f"{unit}{suffix}"]
        num /= 1024.0
    # return f"{num:.1f}Yi{suffix}"
    return [num, f"Yi{suffix}"]

def get_file_names(folder_name):
    # List all files and directories in a path
    files = os.listdir(folder_name)  # Replace with your path
    try:
        files.remove(".gitkeep")
        
    except:
        pass
    files_details = []

    conn = duckdb.connect()
    for i in range(0, len(files)):
        temp = {}
        temp["file_name"] = files[i]
        a = files[i].split(".")
        # print("a", a)
        
        if "csv" == a[1] or "parquet" == a[1] or "feather" == a[1] or "pickle" == a[1]:
            # if folder_name == "fastCache":
            #     # print()
            #     if len(a) < 3:
            #         df_clean = fastCache_saving.read_file(f"{folder_name}/{a[0]}", extension = f".{a[1]}")
            #         # temp["last_date"] = str(df_clean.index[-1])
            #         temp["last_date"] = int(df_clean.loc[df_clean.index[-1] ,"date_number"])
            #     else:
            #         temp["last_date"] = 0
            # else:
            #     if len(a) < 3:
            #         df_clean = df_saving.read_file(f"{folder_name}/{a[0]}", extension = f".{a[1]}")
            #         temp["last_date"] = str(df_clean.index[-1])
            #     else:
            #         temp["last_date"] = 0
            extension = a[1]
            if extension == "parquet":
                # path = "files/shared/Clean_data/1min"
                df = conn.sql(f""" 
                SELECT DATE(MAX(datetime)) AS last_date
                FROM "{folder_name}/{a[0]}.parquet";

                        """).df()

                last_date = str(df["last_date"].iloc[0])[:10]
                temp["last_date"] = last_date 
            else:
                temp["last_date"] = 0
        else:
            temp["last_date"] = 0
        

        m_size = sizeof_fmt(os.path.getsize(f"{folder_name}/{files[i]}"),  unit="Mi")
        m_size[0] = round(m_size[0],2)
        # print(m_size)
        temp["file_size"] = m_size
        # temp["file_size"] = [0, 'MiB']
        files_details.append(temp)

    return files_details


def delete_file_one_by_one(payload):
    for file_name in payload.files_list:
        try:
            os.remove(f"{payload.folder_name}/{file_name}")
        except Exception as e:
            print(e)
            pass
    return {"status": "success"}


async def run_in_thread(func, thread_pool):
    """Run function in thread pool"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool, partial(func))


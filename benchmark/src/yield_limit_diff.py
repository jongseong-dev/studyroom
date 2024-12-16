from memory_profiler import memory_usage
import time
import psutil
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 33306)),
    "user": os.getenv("DB_USER", "test_user"),
    "password": os.getenv("DB_PASSWORD", "test_password"),
    "database": os.getenv("DB_NAME", "test_db"),
}
url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
# 데이터베이스 설정
Base = declarative_base()
engine = create_engine(url)
Session = sessionmaker(bind=engine)
SIZE = 100000
chunk_size = 10000
# 샘플 데이터 모델
class TestData(Base):
    __tablename__ = "test_data"
    id = Column(Integer, primary_key=True)
    value = Column(String(255))


class TestData2(Base):
    __tablename__ = "test_data2"
    id = Column(Integer, primary_key=True)
    value = Column(String(255))
# 데이터베이스 초기화 및 더미 데이터 생성
def initialize_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # 20,000개의 더미 데이터 생성
    session = Session()
    session.bulk_save_objects([TestData(value=f"Value {i}") for i in range(SIZE)])
    session.bulk_save_objects([TestData2(value=f"Value {i}") for i in range(SIZE)])
    session.commit()
    session.close()

# 메모리 사용량 및 시간 측정 도구
# 메모리 사용량 및 시간 측정 도구
def profile_memory_and_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()

        # memory_profiler를 사용하여 메모리 사용량 측정
        mem_usage = memory_usage((func, args, kwargs), interval=0.1, retval=False)

        end_time = time.time()
        print(f"{func.__name__}: Time: {end_time - start_time:.2f}s, Peak Memory Usage: {max(mem_usage):.2f} MB")
    return wrapper

# yield_per 벤치마크
@profile_memory_and_time
def benchmark_yield_per(batch_size):
    session = Session()
    count = 0
    for row in session.query(TestData2).yield_per(batch_size):
        count += 1
    session.close()
    print(f"Processed rows (yield_per): {count}")

# limit 벤치마크
@profile_memory_and_time
def benchmark_limit(batch_size):
    session = Session()
    count = 0
    offset = 0
    while True:
        results = session.query(TestData).limit(batch_size).offset(offset).all()
        if not results:
            break
        for row in results:
            count += 1
        offset += batch_size
    session.close()
    print(f"Processed rows (limit): {count}")

# 실행
if __name__ == "__main__":
    # 데이터 초기화
    initialize_database()
    for i in range(10):
        print("="* 10, "start profiling", "="*10)
        # print("Starting yield_per Benchmark")
        # benchmark_yield_per(batch_size=chunk_size)

        print("\nStarting limit Benchmark")
        benchmark_limit(batch_size=chunk_size)




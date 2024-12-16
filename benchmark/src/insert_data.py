import os
from pymysql import connect
from faker import Faker

INSERT_SIZE = 1000000
BATCH_SIZE = 100000

# 환경 변수에서 DB 정보 가져오기
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 33306)),
    "user": os.getenv("DB_USER", "test_user"),
    "password": os.getenv("DB_PASSWORD", "test_password"),
    "database": os.getenv("DB_NAME", "test_db"),
}

# 가짜 데이터 생성기
fake = Faker("ko_KR")

def insert_sample_data():
    # MySQL 연결
    with connect(**db_config) as conn:
        cursor = conn.cursor()

        data_batch = []  # 데이터 배치 리스트

        for i in range(INSERT_SIZE):  # 10,000개의 사용자 데이터 생성
            username = fake.user_name()
            is_admin = False
            mobile = fake.phone_number()
            data_batch.append((username, mobile, is_admin))

            # 배치 크기만큼 쌓이면 DB에 삽입
            if len(data_batch) == BATCH_SIZE:
                cursor.executemany(
                    "INSERT INTO users (username, mobile, is_admin) VALUES (%s, %s, %s)", data_batch
                )
                conn.commit()
                print(f"{len(data_batch)} records inserted.")
                data_batch = []  # 배치 초기화

        # 남아있는 데이터를 삽입
        if data_batch:
            cursor.executemany(
                "INSERT INTO users (username, mobile, is_admin) VALUES (%s, %s, %s)", data_batch
            )
            conn.commit()
            print(f"{len(data_batch)} remaining records inserted.")

        print("All sample data inserted successfully.")


if __name__ == "__main__":
    insert_sample_data()

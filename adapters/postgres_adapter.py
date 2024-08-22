import psycopg2


class Postgres:

    def __init__(
        self, user, password, host="localhost", db="postgres", port=5432
    ) -> None:
        with psycopg2.connect(
            database=db,
            host=host,
            user=user,
            password=password,
            port=port,
        ) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cmd = """
                CREATE TABLE IF NOT EXISTS Element (
                    id INT PRIMARY KEY,
                    name VARCHAR(255),
                    description TEXT
                );
                """
                cursor.execute(cmd)

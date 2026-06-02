from common_tools.env_config import envConfig

conf_init = envConfig
db_data = conf_init["database"]

# Database configuration dictionary
DB_CONF = {
    "host": db_data["host"],
    "port": int(db_data["port"]),
    "user": db_data["user"],
    "password": db_data["passwd"],
    "db": db_data.get("db") if db_data.get("db") is not None else f"rental_{conf_init.get('login_account').get('code')}"
}


def db_log(db_conf):
    # Log basic database connection information
    logger.sub_step("DB Connection Info", f"{db_conf.get('host')}:{db_conf.get('port')}/{db_conf.get('db')}/{db_conf.get('user')}")


@allure_step("Check if database connection is available")
def is_mysql_connect(db_conf=None):
    """Check if database connection is available
    :param db_conf: Database configuration
    :return: True/False
    """
    if db_conf is None:
        db_conf = DB_CONF
    db_log(db_conf)
    host, port, user, password, db_name = db_conf.get("host"), db_conf.get("port"), db_conf.get("user"), \
                                          db_conf.get("password"), db_conf.get("db")
    # Ensure each database connection is checked only once
    db_variable_name = f"{host}_{port}_{user}_{password}_{db_name}"
    db_status = global_variable.get_value(db_variable_name)
    if db_status is not None:
        return db_status
    # Check if database connection is available
    try:
        pymysql.connect(**db_conf, connect_timeout=3)
        global_variable.set_value(db_variable_name, True)
        return True
    except Exception as err:
        print(db_conf)
        logger.error_without_fail(f"Database connection error: {err}")
        global_variable.set_value(db_variable_name, False)
        return False


class MysqlDb:

    def __init__(self, db_conf=None):
        # Unpack dictionary to pass configuration and establish database connection
        if db_conf is None:
            db_conf = DB_CONF
        self.db_conf = db_conf
        self.is_connect = is_mysql_connect(db_conf)
        if self.is_connect:
            self.conn = pymysql.connect(**db_conf, autocommit=True)
            # Create cursor object via cursor() and output query results as dictionary format
            self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __del__(self):  # Triggered when object resources are released, final operations before object deletion
        if self.is_connect:
            try:
                # Close cursor
                self.cur.close()
                # Close database connection
                self.conn.close()
                if db_data["is_ssh"] is True:
                    # Close SSH connection
                    self.server.close()
            except TypeError:  # Some Python versions raise TypeError when closing db connection, but it's actually closed; catch annoying exception info
                pass

    @allure_step("Query database")
    def select_db(self, sql):
        """Query database"""
        if not self.is_connect:
            return None
        db_log(self.db_conf)
        # Check if connection is closed; reconnect if needed
        self.conn.ping(reconnect=True)
        logger.sub_step("DB_SQL", sql)
        # Execute SQL using execute()
        self.cur.execute(sql)
        # Fetch query results using fetchall()
        data = self.cur.fetchall()
        logger.sub_step("DB_RESULT", data)
        return data

    def execute_db(self, sql):
        """Update/Insert/Delete operations"""
        if not self.is_connect:
            return None
        db_log(self.db_conf)
        try:
            logger.sub_step("DB_SQL", sql)
            self.conn.ping(reconnect=True)
            update_count = self.cur.execute(sql)
            # Commit transaction
            self.conn.commit()
            logger.sub_step("DB_RESULT", "Successfully updated {} row(s).".format(update_count))
            return update_count
        except Exception as e:
            logger.info("MySQL operation error: {}".format(e))
            # Rollback all changes
        self.conn.rollback()


db = MysqlDb(DB_CONF)

if __name__ == "__main__":
    # Desensitized database connection info - replace with actual config in production
    db_info = {'host': '{DESENSITIZED_HOST}', 'port': {DESENSITIZED_PORT}, 'user': '{DESENSITIZED_USER}', 'password': '{DESENSITIZED_PASSWORD}', 'db': '{DESENSITIZED_DB_NAME}'}
    is_mysql_connect(db_info)
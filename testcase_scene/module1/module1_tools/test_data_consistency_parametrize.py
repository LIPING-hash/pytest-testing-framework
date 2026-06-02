case_section_item = get_data("data/data1.yaml", "section_item", currentDir=currentDir)

class TestCommissionView:

    # Commission record (section item) validation test
    @pytest.mark.parametrize("case,params,expected", case_section_item)
    def test_section_item(self, case, params, expected):
        # SQL query to fetch commission section item from source table (RC)
        rc_commission_section_item_sql = """SELECT
                                                    id,
                                                    start_date,
                                                    end_date,
                                                    amount,
                                                    business_volume_amount 
                                                FROM
                                                    [REDACTED] 
                                                WHERE
                                                    id = '{}' AND is_deleted = 0""".format(params["section_item_id"])  # section_item_id refers to commission record ID

        # SQL query to fetch commission section view data from target table (DM)
        dm_commission_section_item_sql = """SELECT
                                                    section_item_id,
                                                    section_item_start_date,
                                                    section_item_end_date,
                                                    section_item_amount,
                                                    section_item_business_volume_amount 
                                                FROM
                                                    [REDACTED]
                                                WHERE
                                                section_item_id = '{}'""".format(params["section_item_id"])

        # Execute both queries and fetch data
        rc_commission_section_item_data = db.select_db(rc_commission_section_item_sql)
        dm_commission_section_item_data = db.select_db(dm_commission_section_item_sql)

        # Assert that source data matches target view data
        assert rc_commission_section_item_data == dm_commission_section_item_data
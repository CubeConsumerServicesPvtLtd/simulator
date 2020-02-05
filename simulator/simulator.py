__author__ = 'SHASHANK'

from datetime import datetime, timedelta
from .date_utils import DateUtils
from .constants import setting
from contextlib import closing

import sys
import traceback
import mysql.connector.pooling
import flows as flows

calender = DateUtils()

## db config
DBCONN = {}
for k, v in setting.items():
    DBCONN[k] = mysql.connector.pooling.MySQLConnectionPool(**v)


def getdate(mode, t_date, scheme_id, gateway=0, toacc=""):

    t_date = t_date + timedelta(hours=5, minutes=30)

    if t_date < datetime.strptime("2020-01-01", "%Y-%m-%d") < datetime.strptime("2021-01-01", "%Y-%m-%d"):
        raise ValueError("Transaction Date is out of 1 year window")

    if gateway in [0, 1, 3, 4, 6]:
        partner_credit_date = calender.get_next_date(t_date, orientation=0)
    elif gateway == 2:
        partner_credit_date = t_date = calender.get_next_date(t_date, 3 if t_date.hour < 15 else 4)
    else:
        raise ValueError("Gateway Not Implemented")

    func = "flow_" + str(mode) + "_" + "bank" if toacc == "bank" else "flow_" + str(mode) + "_"

    try:
        final_date, _ = getattr(flows, func)(t_date, partner_credit_date, calender, scheme_id)
        return final_date.replace(hour=0, minute=0, second=0)
    except AttributeError:
        raise ValueError("Processor Not Implemented")


def get(trans_id):
    with closing(DBCONN['orchestrator'].get_connection()) as cnx:
        with closing(cnx.cursor()) as cursor:
            try:
                cursor.execute(""" select t.processor, t.toacc, o.status, ADDTIME(o.lastupdatets, "5:30"), h.id, h.status,
                                   h.gw, ADDTIME(t.createts, "5:30"), fromacc from orchestrator.tlog_trans t, orchestrator.tlog_transorder o,
                                   orchestrator.tlog_transgw g, orchestrator.tlog_transgwheader h where t.id=o.trans_id
                                   and t.id=g.trans_id and g.transgwheader_id= h.id and t.id=%s""" % trans_id)
                (processor, toacc, status, lastupdatets, payment_id, payment_status, gateway, t_date, fromacc) = cursor.fetchone()

                if t_date < datetime.strptime("2020-01-01", "%Y-%m-%d") < datetime.strptime("2021-01-01", "%Y-%m-%d"):
                    raise ValueError("Transaction Date is out of 1 year window")

                if payment_status == 3:
                    cursor.execute(""" select ADDTIME(createts, "5:30") from orchestrator.tlog_transgwheaderlog where transgwheader_id=%s
                                       and status=3 order by createts desc limit 1""" % payment_id)
                    t_date = payment_confirmation_date = cursor.fetchone()[0]

                    if processor == 1 and toacc != "bank":
                        payment_credit_date = calender.get_next_date(payment_confirmation_date, orientation=0)
                else:
                    if gateway in [0, 1, 3, 4, 6]:
                        t_date = payment_confirmation_date = calender.get_next_date(t_date, orientation=0)
                    elif gateway == 2:
                        t_date = payment_confirmation_date = calender.get_next_date(t_date, 3 if t_date.hour < 15 else 4)


                if processor == 0:
                    final_date = flows.calculate_date_for_0(payment_confirmation_date)

                elif processor == 1:
                    cursor.execute(""" select s.code from mutual_fund.cube_account a, mutual_fund.scheme s
                                       where a.scheme_id=s.id and a.id = %s""" % (toacc if toacc != "bank" else fromacc))
                    scheme_id = cursor.fetchone()[0]

                    if toacc not in ["bank"]:
                        final_date = flows.calculate_date_for_1(calender, payment_credit_date, status, lastupdatets, scheme_id)
                    else:
                        final_date = flows.calculate_date_for_1_bank(calender, t_date, status, lastupdatets, scheme_id)

                elif processor == 2:
                    final_date = flows.calculate_date_for_2(calender, payment_confirmation_date)

                elif processor == 3:
                    final_date = flows.calculate_date_for_3(payment_confirmation_date)

                elif processor == 4:
                    if toacc not in ["bank"]:
                        final_date = flows.calculate_date_for_4(calender, payment_confirmation_date)
                    else:
                        final_date = flows.calculate_date_for_4_bank(calender, t_date)

                elif processor == 5:
                    final_date = flows.calculate_date_for_5(payment_confirmation_date)

                elif processor == 6:
                    if toacc not in ["bank"]:
                        final_date = flows.calculate_date_for_6(payment_confirmation_date)
                    else:
                        final_date = flows.calculate_date_for_6_bank(calender, t_date)

                elif processor == 7:
                    final_date = flows.calculate_date_for_7(payment_confirmation_date)

                elif processor == 8:
                    if toacc not in ["bank"]:
                        final_date = flows.calculate_date_for_8(calender, payment_confirmation_date)
                    else:
                        final_date = flows.calculate_date_for_8_bank(calender, t_date)

                elif processor == 9:
                    if toacc not in ["bank"]:
                        final_date = flows.calculate_date_for_9(calender, payment_confirmation_date)
                    else:
                        final_date = flows.calculate_date_for_9_bank(calender, t_date)

                elif processor == 10:
                    final_date = flows.calculate_date_for_10(payment_confirmation_date)

                else:
                    raise ValueError("Processor Not Implemented!!")
                return final_date.replace(hour=0, minute=0, second=0)
            except Exception as e:
                print(e)
                traceback.print_exc(file=sys.stdout)

# if __name__ == '__main__':
#     print(get(12961), getdate(1, datetime(2020,5,26,17,46,24), 'RELLFTPI-GR', 3, 'bank'))
#     print(get(12963), getdate(1, datetime(2020,5,26,17,46,24), 'RELLFTPI-GR', 0, ''))
#     print(get(13051), getdate(9, datetime(2020,1,17,5,47,47), 'RELLFTPI-GR', 0, ''))



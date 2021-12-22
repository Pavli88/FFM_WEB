from django.db import connection
from mysite.my_functions.general_functions import *

# Database imports
from robots.models import *
from instrument.models import *

# Process imports
from robots.processes.robot_balance_calc import balance_calc


def pricing_robot(robot, calc_date, instrument_id):

    t_min_one_date = previous_business_day(currenct_day=calc_date.strftime('%Y-%m-%d'))
    robot_data = Robots.objects.filter(name=robot).values()
    robot_inception_date = robot_data[0]['inception_date']
    cursor = connection.cursor()

    if calc_date.weekday() == 6 or calc_date.weekday() == 5:
        print("    Weekend. No pricing calculations at weekends.")
    else:
        if robot_inception_date > calc_date:
            print("    Pricing calculation date is less than robot inception date. Calculation stopped!")
        else:
            if robot_inception_date == calc_date:
                price = 1.0
                print("    T-1 Robot Price:", price)
            else:
                try:
                    cursor.execute("""
                                        select inst.id, inst.instrument_name,inst.source, pr.date, pr.price
                                            from instrument_instruments as inst,
                                                instrument_prices as pr
                                            where inst.id = pr.inst_code 
                                            and inst.instrument_name='{inst_name}' 
                                            and pr.date='{end_date}'
                                    """.format(end_date=t_min_one_date, inst_name=robot))

                    row = cursor.fetchall()[0]
                    price = row[-1]
                except:
                    return "There is no price for T-1 date"

            # Get latest robot balance for daily return
            try:
                balance = Balance.objects.filter(robot_name=robot).filter(date=calc_date).values()[0]
            except:
                return "There is no calculated balance and return."

            ret = balance['ret']
            t_price = price*(1+ret)

            # Saving calculated price to database
            try:
                price_record = Prices.objects.get(inst_code=instrument_id, date=calc_date)
                price_record.price = t_price
                price_record.source = "ffm_system"
                price_record.save()
                return "Existing record is updated : " + str(round(t_price, 3))
            except:
                Prices(inst_code=instrument_id,
                       date=calc_date,
                       price=t_price,
                       source='ffm_system').save()
                return "New record is saved : " + str(round(t_price, 3))

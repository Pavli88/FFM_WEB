from django.db import connection
from mysite.my_functions.general_functions import *

# Database imports
from robots.models import *
from instrument.models import *


def pricing(robot, calc_date, instrument_id):

    t_min_one_date = previous_business_day(currenct_day=calc_date.strftime('%Y-%m-%d'))
    robot_data = Robots.objects.filter(name=robot).values()
    robot_inception_date = robot_data[0]['inception_date']

    print("")
    print("    CALC DATE:", calc_date)
    print("    T-1 DATE:", t_min_one_date)

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

                    print("    T-1 Robot Price:", price)
                    print("")
                except:
                    return "There is no price for T-1 for"

            # Get latest robot balance for daily return
            try:
                balance = Balance.objects.filter(robot_name=robot).filter(date=calc_date).values()[0]
            except:
                return "There is no calculated balance and return."

            ret = balance['ret']
            t_price = price*(1+ret)

            print("    PRICE RETURN:", ret)
            print("    T PRICE:", t_price)

            # Saving calculated price to database
            try:
                price_record = Prices.objects.get(inst_code=instrument_id, date=calc_date)
                price_record.price = t_price
                price_record.source = "ffm_system"
                price_record.save()
                print("    Overwriting existing record.")
            except:
                Prices(inst_code=instrument_id,
                       date=calc_date,
                       price=t_price,
                       source='ffm_system').save()
                print("    New record saved to database")

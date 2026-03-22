
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from datetime import date,datetime

def check_tf_range(tf, start_date, end_date, 
                   date_ranges={1: {'years': 1, 'months': 0, 'days': 0},
                                2: {'years': 1, 'months': 0, 'days': 0},
                                3: {'years': 1, 'months': 0, 'days': 0},
                                5: {'years': 1, 'months': 0, 'days': 0},
                                10: {'years': 1, 'months': 0, 'days': 0},
                                15: {'years': 1, 'months': 0, 'days': 0},
                                30: {'years': 1, 'months': 0, 'days': 0},
                                60: {'years': 1, 'months': 0, 'days': 0},
                                120: {'years': 1, 'months': 0, 'days': 0},
                                180: {'years': 1, 'months': 0, 'days': 0},
                                240: {'years': 1, 'months': 0, 'days': 0},
                                'Daily': {'years': 1, 'months': 0, 'days': 0},
                                'Weekly': {'years': 1, 'months': 0, 'days': 0},
                                'Monthly': {'years': 1, 'months': 0, 'days': 0}}):
    date_format = "%Y-%m-%d"
    try:
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)
    except ValueError:
        # return HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
        return {"exception" : HTTPException, "status_code" : 400, "detail": "Invalid date format. Use YYYY-MM-DD."}
    
    # print(end - relativedelta(years=3))
    # print(end - relativedelta(months=3) >= start)
    
    limit = {
        1 : end - relativedelta(years=date_ranges[1]["years"], months=date_ranges[1]["months"], days=date_ranges[1]["days"] ),
        2 : end - relativedelta(years=date_ranges[2]["years"], months=date_ranges[2]["months"], days=date_ranges[2]["days"] ),
        3 : end - relativedelta(years=date_ranges[3]["years"], months=date_ranges[3]["months"], days=date_ranges[3]["days"] ),
        5 : end - relativedelta(years=date_ranges[5]["years"], months=date_ranges[5]["months"], days=date_ranges[5]["days"] ),
        10 : end - relativedelta(years=date_ranges[10]["years"], months=date_ranges[10]["months"], days=date_ranges[10]["days"] ),
        15 : end - relativedelta(years=date_ranges[15]["years"], months=date_ranges[15]["months"], days=date_ranges[15]["days"] ),
        30 : end - relativedelta(years=date_ranges[30]["years"], months=date_ranges[30]["months"], days=date_ranges[30]["days"] ),
        60 : end - relativedelta(years=date_ranges[60]["years"], months=date_ranges[60]["months"], days=date_ranges[60]["days"] ),
        120 : end - relativedelta(years=date_ranges[120]["years"], months=date_ranges[120]["months"], days=date_ranges[120]["days"] ),
        180 : end - relativedelta(years=date_ranges[180]["years"], months=date_ranges[180]["months"], days=date_ranges[180]["days"] ),
        240 : end - relativedelta(years=date_ranges[240]["years"], months=date_ranges[240]["months"], days=date_ranges[240]["days"] ),
        "Daily" : end - relativedelta(years=date_ranges["Daily"]["years"], months=date_ranges["Daily"]["months"], days=date_ranges["Daily"]["days"] ),
        "Weekly" : end - relativedelta(years=date_ranges["Weekly"]["years"], months=date_ranges["Weekly"]["months"], days=date_ranges["Weekly"]["days"] ),
        "Monthly" : end - relativedelta(years=date_ranges["Monthly"]["years"], months=date_ranges["Monthly"]["months"], days=date_ranges[1]["days"] ),

    }

    # print("tf ************", tf)
    data = {
        "error" : f"Date range exceeds the allowed limit for timeframe '{tf}'. "
                   f"Minimum allowed start date: {limit[tf].strftime('%Y-%m-%d')}",
             "fromDate": limit[tf].strftime('%Y-%m-%d')
    }

    if limit[tf] <= start:
        pass
    else:
        # raise HTTPException(status_code=400, detail="Date range exceeds the allowed limit of 1 year.")
        # return HTTPException(
        #     status_code=400,
        #     detail= data
        
                
        # )
        return {"exception" : HTTPException, "status_code" : 400, "detail": data}
    return None
    


from ..database import db



collection_strategy_run = db["strategy_run"]


def get_agg_pipeline(pipeline):
    return list(collection_strategy_run.aggregate(pipeline))


def insert_one_strategy_data(contentId, link, tradeMode, email, current_datetime):
    return collection_strategy_run.insert_one({"contentId": contentId, 
                                                       "link" : link,
                                                       "tradeMode" : tradeMode, 
                                                       "email" : email,
        
                                                       "strategy_run_at" : current_datetime})


def delete_all_with_email(email : str):
    return collection_strategy_run.delete_many({"email" : email})

from fastapi import FastAPI, Request, APIRouter, BackgroundTasks

# from backtesting import router
from app.routes.backtesting import router
from app.routes.auth import oauth_router
from app.routes.equations import equation_router
from app.routes.stock_list import stock_list_router
from app.routes.new_user import new_user_social
from app.routes.admin_requests  import admin_dashboard
from app.routes.likesdislikes import likesdislikes
from app.routes.verifytoken import protected
from app.routes.user_role_manager import admin_dashboard_social_role_change
from app.routes.strategy_categories import strategy_categories
from app.routes.dateRange import date_range

app_router = APIRouter()

app_backtesting = APIRouter()

 

app_router.include_router(router, prefix="/backend/api/run-backtesting", tags=["backtesting"])


app_router.include_router(oauth_router, prefix="/backend/oauth", tags=["oauth"])
app_router.include_router(equation_router, prefix="/backend/equations",  tags=["equation_router"])
app_router.include_router(stock_list_router, prefix="/backend/api/stock-list", tags=["stock-list"]) 
app_router.include_router(new_user_social, prefix="/backend/api/social-signin", tags=["user-signin"])
app_router.include_router(admin_dashboard, prefix="/backend/api/admin-dashboard", tags=["user-signin"])
app_router.include_router(likesdislikes, prefix="/backend/api/likes-dislikes", tags=["user-signin"])
app_router.include_router(protected, prefix="/backend/api/protected", tags=["user-signin"])
app_router.include_router(admin_dashboard_social_role_change, prefix="/backend/api/social-user-role-change", tags=["user-signin"])
app_router.include_router(strategy_categories, prefix="/backend/api/strategy_categories", tags=["user-signin"])
app_router.include_router(date_range, prefix="/backend/api/date_range", tags=["user-signin"])


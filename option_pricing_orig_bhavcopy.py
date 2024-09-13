import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import sys
import py_vollib_vectorized as vollib
import matplotlib.pyplot as plt
# from  py_vollib_vectorized import vectorized_implied_volatility as bsimplied
# from  py_vollib_vectorized import vectorized_black_scholes as bs
from common import logger, calc_business_days, today, yesterday, data_dir
from download_bhavcopy_2 import bhav_df
from option_pricing_gfd import modified_gfd, gfd_columns, gfd_columns_dict

# bhav=pd.read_csv("/kaggle/input/bhav-copy/BhavCopy_NSE_FO_0_0_0_20240823_F_0000.csv")

choice = str(input('Enter your choice (bhavcopy, GFD or YFinance):'))
if choice.lower() == 'bhavcopy':
    bhav = bhav_df
    bhav_columns = ['TradDt', 'TckrSymb', 'XpryDt', 'StrkPric', 'OptnTp', 'ClsPric', 'PrvsClsgPric', 'OpnIntrst',
                    'ChngInOpnIntrst', 'TtlTradgVol', 'UndrlygPric']
    bhav_columns_dict = {'TradDt': 'Date', 'TckrSymb': "Symbol", 'XpryDt': "Expiry_Date", 'StrkPric': "Strike_Price",
                         'OptnTp': 'Option_Type', 'ClsPric': 'Close_Price',
                         'UndrlygPric': 'Spot', 'PrvsClsgPric': 'Prev_Close', 'OpnIntrst': 'OI',
                         'ChngInOpnIntrst': 'OI_Change', 'TtlTradgVol': 'Volume'}
elif choice.lower() == 'gfd':
    bhav = modified_gfd.copy()
    bhav = bhav[bhav['Time'] == '15:30:59']
    bhav_columns = gfd_columns
    bhav_columns_dict = gfd_columns_dict
    # --------------------------------------------------------------------------------
    # unknown in gfd - prevcloseprice, changeinoi, underlyingprice/spot
    # --------------------------------------------------------------------------------
# bhav = bhav_df
# holiday_list=pd.read_csv("/kaggle/input/nse-holiday-list/Holidays.csv")

def optchain(bhav,bhav_columns, bhav_columns_dict):
    bhav=bhav[bhav_columns].copy()
    bhav.rename(columns=bhav_columns_dict,inplace=True)
    bhav["Date"]=pd.to_datetime(bhav.Date).copy()
    bhav["Expiry_Date"]=pd.to_datetime(bhav.Expiry_Date).copy()
    # if choice.lower() == 'bhavcopy':
    #     bhav=bhav.reindex(columns=['Symbol', 'Expiry_Date', 'Strike_Price', 'Option_Type','Close_Price', 'Spot','Prev_Close', 'OI', 'OI_Change', 'Volume','Date'])
    # elif choice.lower() == 'gfd':
    bhav = bhav.reindex(
        columns=['Symbol', 'Expiry_Date', 'Strike_Price', 'Option_Type', 'Close_Price', 'Spot', 'Prev_Close', 'OI',
                 'OI_Change', 'Volume', 'Date'])
    # logger.info(f'bhav test is \n{bhav}')
    # bhav.to_csv(os.path.join(data_dir, f'bhav_test.csv'), index=False)
    bhav.fillna({"Strike_Price":0,"Option_Type":"XX"},inplace=True)
    bhav["CALDTE"]=((bhav.Expiry_Date-bhav.Date)/np.timedelta64(1, 'D')).astype("int")
    # bhav.to_csv(os.path.join(data_dir, f'bhav_test1.csv'), index=False)
    bhavce=bhav.query("Option_Type=='CE'")[['Symbol', 'Expiry_Date', 'Strike_Price','Close_Price', 'Spot', 'Prev_Close', 'OI', 'OI_Change', 'Volume', 'Date','CALDTE']]
    bhavpe=bhav.query("Option_Type=='PE'")[['Symbol', 'Expiry_Date', 'Strike_Price','Close_Price', 'Spot', 'Prev_Close', 'OI', 'OI_Change', 'Volume', 'Date','CALDTE']]
    bhavchain=pd.merge(bhavce, bhavpe, on =['Symbol', 'Expiry_Date', 'Strike_Price','Spot','Date','CALDTE'], how = "outer",suffixes=("_CE","_PE"))
    start=[pd.to_datetime(bhavchain.Date).dt.date]
    # logger.info(f'start is \n{type(start)}\n{start}')
    end= [pd.to_datetime(bhavchain.Expiry_Date).dt.date]
    # logger.info(f'end is \n{type(end)}\n{end}')
    bhavchain['DTE'] = calc_business_days(today_date=start, exp_date=end)
    # hol=pd.to_datetime(holiday_list.Holidays,dayfirst=True).dt.date.tolist()
    # bdd = np.busdaycalendar(holidays=hol,weekmask=[1,1,1,1,1,0,0]) #Defining holiday calendar
    # bhavchain["DTE"]=np.busday_count(start,end,busdaycal=bdd)[0]
    #
    bhavchain=bhavchain.reindex(columns=['Symbol', 'Expiry_Date', 'Strike_Price', 'DTE','CALDTE','Spot','Close_Price_CE','Close_Price_PE','OI_CE','OI_PE','Volume_CE','Volume_PE',
                                         'OI_Change_CE','OI_Change_PE','Prev_Close_CE','Prev_Close_PE','Date'])
    bhavchain.fillna(0,inplace=True)
    return bhavchain
    # # return True
# bhavchain=bhavchain.astype({'Symbol':'category','Expiry_Date':'category','DTE':'category','CALDTE':'category','Date':'category',
#                             'Strike_Price':'float32','Close_Price_CE':'float32','Close_Price_PE':'float32','Prev_Close_CE':'float32','Prev_Close_CE':'float32',
#                             'OI_CE':'int','OI_PE':'int','Volume_CE':'int','Volume_PE':'int','OI_Change_CE':'int','OI_Change_PE':'int'})

def fut_summary(bhav,bhav_columns, bhav_columns_dict):
    bhav=bhav[bhav_columns].copy()
    bhav.rename(columns=bhav_columns_dict,inplace=True)
    bhav["Date"]=pd.to_datetime(bhav.Date).copy()
    bhav["Expiry_Date"]=pd.to_datetime(bhav.Expiry_Date).copy()
    bhav=bhav.reindex(columns=['Symbol', 'Expiry_Date', 'Strike_Price', 'Option_Type','Close_Price', 'Spot','Prev_Close', 'OI', 'OI_Change', 'Volume','Date'])
    bhav.fillna({"Strike_Price":0,"Option_Type":"XX"},inplace=True)
    bhav["CALDTE"]=((bhav.Expiry_Date-bhav.Date)/np.timedelta64(1, 'D')).astype("int")
    bhavfut=bhav.query("Option_Type=='XX'")[['Symbol', 'Expiry_Date', 'Strike_Price','Close_Price', 'Spot', 'Prev_Close', 'OI', 'OI_Change', 'Volume', 'Date','CALDTE']]
    start=[pd.to_datetime(bhavfut.Date).dt.date]
    logger.info(f'fut start is \n{type(start)}\n{start}')
    end= [pd.to_datetime(bhavfut.Expiry_Date).dt.date]
    logger.info(f'fut end is \n{type(end)}\n{end}')
    bhavfut['DTE'] = calc_business_days(today_date=start, exp_date=end, fut=True)
    # hol=pd.to_datetime(holiday_list.Holidays,dayfirst=True).dt.date.tolist()
    # bdd = np.busdaycalendar(holidays=hol,weekmask=[1,1,1,1,1,0,0]) #Defining holiday calendar
    # bhavfut["DTE"]=np.busday_count(start,end,busdaycal=bdd)[0]

    bhavfut=bhavfut.reindex(columns=['Symbol', 'Expiry_Date', 'Strike_Price', 'DTE','CALDTE','Spot','Close_Price','OI','Volume','OI_Change','Prev_Close','Date'])
    bhavfut.fillna(0,inplace=True)
    bhavfut.sort_values(by=["Symbol","Expiry_Date"],inplace=True)
    bhavfut.rename(columns={'OI':'OI_Fut','Volume':'Volume_Fut',},inplace=True)
    bhavfut[['OI_Fut','Volume_Fut']]/=10_000_000
    return bhavfut
#
def tv_calc_lambda(K,S,CE,PE):
    if (CE>0 and PE>0):
        return min(CE,PE)
    if K>=S:
        return max(CE,0)

    return max(PE,0)
vect_tv_calc=np.vectorize(tv_calc_lambda)

def tv_calc_apply(row):
    if (row['Close_Price_CE']>0 and row['Close_Price_PE']>0):
        return min(row['Close_Price_CE'],row['Close_Price_PE'])
    if row['Strike_Price']>=row['Fwd']:
        return max(row['Close_Price_CE'],0)

    return max(row['Close_Price_PE'],0)
# #
# # # opt_summary['TV']=opt_summary.apply(lambda row:tv_calc_lambda(row['Strike_Price'],row['Fwd'],row['Close_Price_CE'],row['Close_Price_PE']),axis=1)
# # # opt_summary['TV_Apply']=opt_summary.apply(tv_calc_apply,axis=1)
# # # opt_summary['TV_vectorized']=vect_func(opt_summary['Strike_Price'],opt_summary['Fwd'],opt_summary['Close_Price_CE'],opt_summary['Close_Price_PE'])
# #
def optsummary(bhavchain):
    bhavchain['Syn_Fut']=bhavchain['Strike_Price']+bhavchain['Close_Price_CE']-bhavchain['Close_Price_PE']
    bhavchain['Total_OI']=bhavchain['OI_CE']+bhavchain['OI_PE']
    bhavchain['Product_OI']=bhavchain['OI_CE']*bhavchain['OI_PE']
    atm=bhavchain.groupby(by=['Symbol','Expiry_Date'])['Product_OI'].idxmax()
    atm=pd.DataFrame(atm)
    atm.rename(columns={'Product_OI':'Fwd_Index'},inplace=True)
    atm.reset_index(inplace=True)
    atm['Fwd']=bhavchain.iloc[atm.Fwd_Index].reset_index()['Syn_Fut']
    atm.drop(columns=['Fwd_Index'],inplace=True)
    df=pd.merge(bhavchain,atm,on=['Symbol','Expiry_Date'],how='outer')
    opt_summary=df[['Symbol', 'Expiry_Date', 'Strike_Price', 'DTE','Fwd',
                    'Close_Price_CE', 'Close_Price_PE','OI_CE', 'OI_PE','OI_Change_CE', 'OI_Change_PE','Volume_CE','Volume_PE','Date']].copy()
    opt_summary['TV']=vect_tv_calc(opt_summary['Strike_Price'],opt_summary['Fwd'],opt_summary['Close_Price_CE'],opt_summary['Close_Price_PE'])
    opt_summary['OTM']=np.where(opt_summary['Fwd']>opt_summary['Strike_Price'],'p','c')
    try:
        opt_summary['IV']=vollib.vectorized_implied_volatility(price=opt_summary['TV'],S=opt_summary['Fwd'],K=opt_summary['Strike_Price'],t=opt_summary['DTE']/365,r=0,flag=opt_summary['OTM'])
    except ZeroDivisionError:
        opt_summary['IV'] = np.nan
    opt_summary['Gamma']=vollib.vectorized_gamma(sigma=opt_summary['IV'],S=opt_summary['Fwd'],K=opt_summary['Strike_Price'],t=opt_summary['DTE']/365,r=0,flag=opt_summary['OTM'])
    opt_summary['Vega']=vollib.vectorized_vega(sigma=opt_summary['IV'],S=opt_summary['Fwd'],K=opt_summary['Strike_Price'],t=opt_summary['DTE']/365,r=0,flag=opt_summary['OTM'])
    opt_summary['Theta']=vollib.vectorized_theta(sigma=opt_summary['IV'],S=opt_summary['Fwd'],K=opt_summary['Strike_Price'],t=opt_summary['DTE']/365,r=0,flag=opt_summary['OTM'])
    opt_summary['Delta']=vollib.vectorized_delta(sigma=opt_summary['IV'],S=opt_summary['Fwd'],K=opt_summary['Strike_Price'],t=opt_summary['DTE']/365,r=0,flag='c')
    opt_summary['CE_Cash_Delta_Cr']=opt_summary['Delta']*opt_summary['Fwd']*opt_summary['OI_CE']/10**7
    opt_summary['PE_Cash_Delta_Cr']=(opt_summary['Delta']-1)*opt_summary['Fwd']*opt_summary['OI_PE']/10**7
    opt_summary['CE_Cash_Gamma_Cr']=opt_summary['Gamma']*opt_summary['Fwd']*opt_summary['Fwd']*opt_summary['OI_CE']/10**7
    opt_summary['PE_Cash_Gamma_Cr']=opt_summary['Gamma']*opt_summary['Fwd']*opt_summary['Fwd']*opt_summary['OI_PE']/10**7
    opt_summary['CE_Cash_Vega_Cr']=opt_summary['Vega']*opt_summary['Fwd']*opt_summary['OI_CE']/10**7
    opt_summary['PE_Cash_Vega_Cr']=opt_summary['Vega']*opt_summary['Fwd']*opt_summary['OI_PE']/10**7
    opt_summary['CE_Cash_Theta_Cr']=opt_summary['Theta']*opt_summary['Fwd']*opt_summary['OI_CE']/10**7
    opt_summary['PE_Cash_Theta_Cr']=opt_summary['Theta']*opt_summary['Fwd']*opt_summary['OI_PE']/10**7
    opt_summary['CE_TV_Cr']=opt_summary['OI_CE']*opt_summary['TV']/10**7
    opt_summary['PE_TV_Cr']=opt_summary['OI_PE']*opt_summary['TV']/10**7
    opt_summary['CE_Total_Cr']=opt_summary['OI_CE']*opt_summary['Close_Price_CE']/10**7
    opt_summary['PE_Total_Cr']=opt_summary['OI_CE']*opt_summary['Close_Price_PE']/10**7

    return opt_summary
# #
def straddle(df):
    df=df.query("Strike_Price<1.03*Fwd and Strike_Price>0.97*Fwd and OI_CE > 100000 and OI_PE > 100000 ").copy()
    df['Strd']=df['Close_Price_CE']+df['Close_Price_PE']
    df=pd.DataFrame(df.groupby(by=["Symbol","Expiry_Date"])[['Strd']].min()).reset_index()
    return(df)

bhavchain=optchain(bhav,bhav_columns, bhav_columns_dict)
# logger.info(f'bhavchain is \n{bhavchain}')
# bhavchain.to_csv(os.path.join(data_dir, f'bhavchain_{today.date()}_1.csv'), index=False)
bhavfut=fut_summary(bhav,bhav_columns, bhav_columns_dict)
# logger.info(f'bhavfut is \n{bhavfut}')
# bhavfut.to_csv(os.path.join(data_dir, f'bhavfut_{yesterday.date()}_1.csv'), index=False)
opt_summary=optsummary(bhavchain)
logger.info(f'opt_summary is \n{opt_summary}')
opt_summary.to_csv(os.path.join(data_dir, f'option_summary_{yesterday.date()}_1.csv'), index=False)
#
#     # print(bhavchain.query('Symbol=="NIFTY"'))
#     # print(opt_summary.columns)
#     #
df=pd.DataFrame(opt_summary.groupby(by=['Symbol','Expiry_Date'])[['OI_CE', 'OI_PE','OI_Change_CE', 'OI_Change_PE','Volume_CE','Volume_PE','CE_Cash_Delta_Cr', 'PE_Cash_Delta_Cr',
                                                                  'CE_Cash_Gamma_Cr', 'PE_Cash_Gamma_Cr', 'CE_Cash_Vega_Cr', 'PE_Cash_Vega_Cr','CE_Cash_Theta_Cr', 'PE_Cash_Theta_Cr',
                                                                  'CE_TV_Cr', 'PE_TV_Cr', 'CE_Total_Cr','PE_Total_Cr']].sum()).reset_index()
df=pd.merge(df,straddle(opt_summary),on=['Symbol','Expiry_Date'],how='outer')
df=pd.merge(df,opt_summary[['Symbol','Expiry_Date','Fwd','DTE']].drop_duplicates(),on=['Symbol','Expiry_Date'],how='inner')
logger.info(df)
df.to_csv(os.path.join(data_dir, f'opt_summary_df_{yesterday.date()}_1.csv'), index=False)
#     #
#     # print(df.query("Symbol=='MIDCPNIFTY'"))
#     df.query('Symbol=="NIFTY"')['Volume_PE'].plot()
# plt.show()
# opt_summary.query('Symbol=="NIFTY" and DTE==9')[['IV']].plot()
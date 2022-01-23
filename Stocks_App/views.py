from datetime import datetime

from django.shortcuts import render
from django.db import connection

# might need to import relations
from Stocks_App.models import Transactions, Investor, Stock, Company, Buying


def home(request):
    return render(request, 'home.html')

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def Query_Results(request):
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT Name, ROUND(Total_Sum,3) as Total_Sum
        FROM Varied_Investors_with_Total_Sum
        ORDER BY Total_Sum DESC
        """)
        sql_res1 = dictfetchall(cursor)
        cursor.execute("""
        SELECT *
        FROM Popular_Companies_Max_Investor
        ORDER BY Symbol,Name;
                """)
        sql_res2 = dictfetchall(cursor)
        cursor.execute("""
        SELECT *
        FROM A_Groise_mezie
        ORDER BY tDate, Symbol;
                        """)
        sql_res3 = dictfetchall(cursor)
    return render(request, 'Query_Results.html', {'sql_res1': sql_res1, 'sql_res2': sql_res2, 'sql_res3': sql_res3})




def Add_Transaction(request):
    with connection.cursor() as cursor:
        sql_res4 = 0
        if request.method == 'POST' and request.POST:
            investorID = request.POST["ID"]
            tSum = request.POST["TSum"]
            today = datetime.today().strftime('%Y-%m-%d')
            cursor.execute(f"""
            SELECT
            CASE WHEN {investorID} NOT IN (SELECT ID FROM Investor) THEN '0'
            WHEN '{today}' IN (SELECT tDate
                            FROM Transactions
                            WHERE ID = {investorID}) THEN (SELECT TQuantity
                                                           FROM Transactions
                                                           WHERE ID = {investorID} and tDate = '{today}')
            ELSE '1'
            END AS Answer;
            """)
            sql_temp_res = dictfetchall(cursor)
            answer = sql_temp_res[0]['Answer']
            cursor.execute(f"""
             SELECT AvailableCash,Name FROM Investor WHERE ID = {investorID}
             """)
            sql_temp_res1 = dictfetchall(cursor)

            if answer == 0:
                sql_res4 = 404
            elif answer == 1:
                cash = int(sql_temp_res1[0]['AvailableCash']) - int(tSum)
                nametoadd = sql_temp_res1[0]['Name']
                new_row1 = Investor(id=investorID,
                                    name=nametoadd,
                                    availablecash=cash)
                new_row1.save()

                new_row = Transactions(tdate=datetime.today(),
                                       id=Investor.objects.get(id=investorID),
                                       tquantity=tSum)
                new_row.save()
            else:
                cash = int(sql_temp_res1[0]['AvailableCash']) - int(tSum)
                nametoadd = sql_temp_res1[0]['Name']
                new_row1 = Investor(id=investorID,
                                    name=nametoadd,
                                    availablecash=cash + answer)
                new_row1.save()
                new_row = Transactions(tdate=datetime.today(),
                                       id=Investor.objects.get(id=investorID),
                                       tquantity=tSum)
                new_row.save()

        cursor.execute("""
        SELECT TOP 10 *
        FROM Transactions
        ORDER BY tDate DESC ,ID DESC;
        """)
        sql_res5 = dictfetchall(cursor)

    return render(request, 'Add_Transaction.html', {'sql_res4': sql_res4, 'sql_res5': sql_res5})




def Buy_Stocks(request):
    with connection.cursor() as cursor:
        sql_res7 = 3
        if request.method == 'POST' and request.POST:
            investorID = request.POST["ID"]
            company = request.POST["Symbol"]
            Quantity = request.POST["Quantity"]
            today = datetime.today().strftime('%Y-%m-%d')
            cursor.execute(f"""
            SELECT
            CASE WHEN {investorID} NOT IN (SELECT ID FROM Investor) AND '{company}' NOT IN (SELECT Symbol FROM Company) THEN '0'
            WHEN {investorID} NOT IN (SELECT ID FROM Investor) THEN '1'
            WHEN '{company}' NOT IN (SELECT Symbol FROM Company) THEN '2'            
            ELSE '3'
            END AS Answer;
            """)
            sql_res7 = dictfetchall(cursor)
            answer = sql_res7[0]['Answer']
            if answer == '0':
                sql_res7 = 0
            elif answer == '1':
                sql_res7 = 1
            elif answer == '2':
                sql_res7 = 2
            else:
                cursor.execute(f"""
                SELECT TOP 1 Price
                FROM Stock
                WHERE Symbol = '{company}'
                ORDER BY tDate DESC;
                """)
                price_res = dictfetchall(cursor)
                price = price_res[0]['Price']
                payed = float(price)*float(Quantity)
                cursor.execute(f"""
                SELECT AvailableCash-{payed} as money
                FROM Investor
                WHERE ID={investorID};
                """)
                enough_money = dictfetchall(cursor)
                cursor.execute(f"""
                SELECT
                CASE WHEN {investorID} IN (SELECT ID FROM Buying
                                               WHERE ID = {investorID} and '{today}' = tDate and Symbol = '{company}')  THEN '0'   
                ELSE '1'
                END AS Answer2;
                """)
                exists = dictfetchall(cursor)
                if exists[0]['Answer2'] == '0':
                    sql_res7 = 4
                else:
                    if enough_money[0]['money'] < 0:
                        sql_res7 = 5
                    else:
                        cursor.execute(f"""
                        SELECT
                        CASE WHEN '{company}' IN (SELECT Symbol FROM Stock
                                                       WHERE '{today}' = tDate and Symbol = '{company}')  THEN '0'   
                        ELSE '1'
                        END AS Answer3;
                        """)
                        exists1 = dictfetchall(cursor)
                        if exists1[0]['Answer3'] == '1':
                            cursor.execute(f"""
                            INSERT INTO Stock (Symbol, tDate, Price) VALUES ('{company}','{today}',{price})
                            """)
                        cursor.execute(f"""
                        INSERT INTO Buying (tDate, ID, Symbol, BQuantity) VALUES ('{today}',{investorID},'{company}',{Quantity})
                        """)
                        cursor.execute(f"""
                        SELECT Name FROM Investor WHERE ID = {investorID}
                        """)
                        sql_temp_res1 = dictfetchall(cursor)
                        new_row1 = Investor(id=investorID,
                                            name=sql_temp_res1[0]['Name'],
                                            availablecash=enough_money[0]['money'])
                        new_row1.save()

        cursor.execute("""
        SELECT *
        FROM Top10_Purchases
        ORDER BY Payed DESC ,ID DESC;
                """)
        sql_res6 = dictfetchall(cursor)

    return render(request, 'Buy_Stocks.html', {'sql_res7': sql_res7, 'sql_res6': sql_res6})

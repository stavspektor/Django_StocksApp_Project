-- query 1 -------------------------------------------------------------------------------------------------------------

CREATE VIEW Buying_With_Sector
AS
SELECT tDate,ID, Sector, Buying.Symbol as Symbol, BQuantity
FROM Buying, Company
WHERE Buying.Symbol = Company.Symbol;


CREATE VIEW Varied_Investors_ID
AS
SELECT distinct ID
FROM (SELECT ID,count(distinct Sector) as count
FROM Buying_With_Sector
GROUP BY tDate,ID) count_columns
WHERE count>=8;


CREATE VIEW Varied_Investors
AS
SELECT Name, Varied_Investors_ID.ID as ID
FROM Varied_Investors_ID, Investor
WHERE Varied_Investors_ID.ID = Investor.ID;


CREATE VIEW Buying_With_Price
AS
SELECT Buying.tDate as tDate, ID, Buying.Symbol as Symbol, BQuantity, Price
FROM Buying LEFT OUTER JOIN Stock
ON Buying.Symbol = Stock.Symbol and Buying.tDate = Stock.tDate;


CREATE VIEW Multiplyprice
AS
SELECT tDate, ID, Symbol,(BQuantity*Price) as Total_Price
FROM Buying_With_Price


CREATE VIEW Buying_totalsum
AS
SELECT ID, sum(Total_Price) as Total_Sum
FROM Multiplyprice
GROUP BY ID


CREATE VIEW Varied_Investors_with_Total_Sum
AS
SELECT Name, Varied_Investors.ID as ID, Total_Sum
FROM Varied_Investors,Buying_totalsum
WHERE Buying_totalsum.ID = Varied_Investors.ID


-- query 2 -------------------------------------------------------------------------------------------------------------


CREATE VIEW Wanted_num_of_days
AS
SELECT count(distinct tDate)/2 as half_num_of_dates
FROM Buying;


CREATE VIEW Popular_Companies
AS
SELECT Symbol
FROM (SELECT Symbol, count(distinct tDate) as num_of_days
FROM Buying
GROUP BY Symbol) companies , Wanted_num_of_days
WHERE companies.num_of_days > Wanted_num_of_days.half_num_of_dates;


CREATE VIEW Num_Of_Stocks_per_investor_and_Company
AS
SELECT ID,Symbol,sum(BQuantity) as num_of_stocks
FROM Buying
GROUP BY ID,Symbol;


CREATE VIEW Small_Investors
AS
SELECT N1.ID as ID, N1.Symbol,N1.num_of_stocks
FROM Num_Of_Stocks_per_investor_and_Company N1, Num_Of_Stocks_per_investor_and_Company N2
WHERE N1.Symbol = N2.Symbol and N1.num_of_stocks < N2.num_of_stocks


CREATE VIEW biggest_investor_per_company
AS
SELECT *
FROM Num_Of_Stocks_per_investor_and_Company
EXCEPT
SELECT *
FROM Small_Investors;


CREATE VIEW Popular_Companies_Max_Investor
AS
SELECT biggest_investor_per_company.Symbol as Symbol, Investor.Name,biggest_investor_per_company.num_of_stocks as Quantity
FROM biggest_investor_per_company,Investor,Popular_Companies
WHERE biggest_investor_per_company.ID = Investor.ID and biggest_investor_per_company.Symbol = Popular_Companies.Symbol and num_of_stocks>10;


-- query 3 -------------------------------------------------------------------------------------------------------------

CREATE VIEW one_buying
AS
SELECT Symbol
FROM (SELECT Symbol, count(*) as num_of_buying
FROM Buying
GROUP BY Symbol) buyings_with_num
WHERE num_of_buying = 1;

CREATE VIEW one_buying_with_date
AS
SELECT one_buying.Symbol as Symbol, tDate
FROM one_buying,Buying
WHERE one_buying.Symbol = Buying.Symbol and tDate < ALL (SELECT max(Stock.tDate)
                                                         FROM Stock);

CREATE VIEW company_following_bDay
AS
SELECT Symbol, min(tDate) as following_day
FROM (SELECT one_buying_with_date.Symbol as Symbol, Stock.tDate as tDate
        FROM one_buying_with_date,Stock
        WHERE one_buying_with_date.tDate < Stock.tDate) symbol_following_day
GROUP BY Symbol;


CREATE VIEW withGrowth
AS
SELECT S1.Symbol as Symbol, S1.Price /S2.Price as growth, one_buying_with_date.tDate as tDate
FROM one_buying_with_date, company_following_bDay, Stock S1, Stock S2
WHERE one_buying_with_date.Symbol = company_following_bDay.Symbol and S1.Symbol = one_buying_with_date.Symbol and S2.Symbol = one_buying_with_date.Symbol
      and S1.tDate = company_following_bDay.following_day and S2.tDate = one_buying_with_date.tDate;


CREATE VIEW A_Groise_mezie
AS
SELECT withGrowth.tDate, withGrowth.Symbol, Name
FROM withGrowth,Buying, Investor
WHERE Buying.Symbol = withGrowth.Symbol and Buying.tDate = withGrowth.tDate and growth > 1.03 and Buying.ID=Investor.ID;




-- query 4 -------------------------------------------------------------------------------------------------------------


CREATE VIEW Top10_Purchases
as
SELECT TOP 10 Stock.tDate, ID, Stock.Symbol, CAST(ROUND(BQuantity*Price,2) as float) as Payed
FROM Buying,Stock
WHERE Buying.tDate = Stock.tDate and Buying.Symbol = Stock.Symbol
ORDER BY Payed DESC ,ID DESC;


SELECT ID
FROM Buying
WHERE ID = 101701610 and '2021-12-16' = tDate and Symbol = 'AMAT';

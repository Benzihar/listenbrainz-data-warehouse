/******************************************************************************************
 Project      : ListenBrainz ETL Assignment for Scalable Capital
 Author       : Benzihar Stanley

 Description
 -----------
 Parameterized analytical SQL queries executed against the Gold Semantic View
 (GLD_300_PL.VW_LISTEN_ANALYTICS).

 When executed in DBeaver, you will be prompted to enter the required parameters.

 Parameters
 ----------
 ${from_date}       Reporting period start date (YYYY-MM-DD)
 ${to_date}         Reporting period end date (YYYY-MM-DD)
 ${top_n}           Number of top users to return
 ${top_days}        Number of top listening days per user
 ${interval_days}   Rolling active-user window in days

 Example
 -------
 from_date      = 2019-01-01
 to_date        = 2019-03-31
 top_n          = 10
 top_days       = 3
 interval_days  = 6

******************************************************************************************/
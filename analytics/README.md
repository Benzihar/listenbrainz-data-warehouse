/******************************************************************************************
Project      : ListenBrainz Assignment for Scalable Capital
Author       : Benzihar Stanley

Description  :
Analytical SQL queries built on the Gold Semantic Layer
(GLD_300_PL.VW_LISTEN_ANALYTICS)

DuckDB will prompt for these values during execution.

Parameters
----------
  `${from_date}` – Reporting period start date
  `${to_date}` – Reporting period end date
  `${top_n}` – Number of users to return
  `${top_days}` – Number of top listening days per user
  `${interval_days}` – Rolling active-user window in days

Example
-------
 from_date 		= 2019-01-01
 to_date   		= 2019-03-31
 ${top_n}	 		= 10
 ${top_days} 		= 10
 ${interval_days}	= 6

******************************************************************************************/
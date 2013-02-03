r-ranking-fun
=============

· Define the question

Find the best boost factor for a document score based on Lucene's SVM with the following data:
 - pubdate
 - incoming citations
 - outgoing references
 - status (refereeed/non-refereed;article/book)
 - reads

· Define the ideal data set

The click-through data which shows for each query the documents on which the users clicked. It records the query, the timestamp of the query, number of returned hits, which documents were clicked on (incl timestamp)

Best would be to have several windows: 30-day, 90-day, 1-year window datasets

· Determine what data you can access

For each paper (but probably, realistic is only for core journals: ApJ...)
 - pubdate 
 - # of outgoing references for each paper
 - # of reads
 - list of citing papers

· Obtain the data
· Clean the data
· Exploratory data analysis
· Statistical prediction/modeling
· Interpret results
· Challenge results
· Synthesize/write up results
· Create reproducible code


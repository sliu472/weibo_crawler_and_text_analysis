# weibo_crawler_and_text_analysis  

Overview: Weibo crawler by keywords input, get related comments content, make wordcloud &amp; sentiment analysis  
## content:  
1. scraping [weibo] https://m.weibo.cn/ by user input keyword and how many pages they want to search
- main package: requests
2. parse page content with json and save to .csv file
3. read comments from saved file, cut words and make wordcloud
- main package: jieba, wordcloud
4. sentiment analysis
- main package: snowNLP, matplotlib
  
## future work:  
- long comment text (with more than 140 words) is only partially retrieved
- sentiment analysis is only based on the basic library from snowNLP without extra training, therefore maynot be accurate

from flask import Flask, render_template, request
from pyspark.sql import SparkSession
from pyspark.sql.functions import desc

app = Flask(__name__, template_folder='templates')

# Initialize SparkSession with Java configurations
spark = SparkSession.builder \
    .appName("Top Keywords App") \
    .config("spark.driver.extraJavaOptions", "-Duser.timezone=UTC") \
    .config("spark.executor.extraJavaOptions", "-Duser.timezone=UTC") \
    .getOrCreate()

# Load the DataFrame from a CSV file
df = spark.read.csv('/app/final_data_drone.csv', header=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    sort_by = request.args.get('sort-by')
    if sort_by == 'most-recent':
        df_sorted = df.sort("priority date", ascending=False)
    elif sort_by == 'most-ancient':
        df_sorted = df.sort("priority date", ascending=True)
    else:
        df_sorted = df

    results = df_sorted.filter(df["title"].contains(query.lower())) \
        .select('id', 'title', 'assignee', 'priority date', 'result_link', 'figure_link')

    results_count = results.count()
    total_pages = (results_count + 19) // 20
    page = int(request.args.get('page', 1))
    start = (page - 1) * 20
    end = start + 20
    results = results.collect()[start:end]

    # Execute Spark processing to get the top 10 keywords
    top_10_keywords = df.groupBy("title").count().orderBy(desc("count")).limit(10).collect()

    return render_template('search_results.html', results=results, results_count=results_count, total_pages=total_pages,
                           page=page, top_10_keywords=top_10_keywords)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5020)

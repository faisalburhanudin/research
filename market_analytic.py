from datetime import date
from pprint import pprint

import boto3
from pyspark.sql import SparkSession
from pyspark.sql import functions
from pyspark.sql.functions import udf


def get_session():
    return SparkSession \
        .builder \
        .appName("Market Analytics") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()


def load_data(session):
    return session.read.format("csv").option("header", "true").load("dataset/raw.csv")


def clean_dataframe(df):
    return df.where(
        df['item_sold'].isNotNull() & df['pid'].isNotNull() &
        df['pid'].isNotNull() & df['price'].isNotNull() &
        df['title'].isNotNull() & df['url'].isNotNull() &
        ~df['item_sold'].like("http%") &
        df['url'].like("http%")
    )


@udf
def extract_seller(x):
    return x.split("/")[3]


@udf
def extract_seller_url(seller):
    return 'https://www.tokopedia.com/' + seller


@udf
def price(x):
    return int(x.replace(".", ""))


def extract_dataframe(df):
    df = df.withColumn('seller', extract_seller(df.url))
    df = df.withColumn('seller_url', extract_seller_url(df.seller))
    df = df.withColumn('item_sold', df.item_sold.cast("int"))
    df = df.withColumn('pid', df.pid.cast("int"))
    df = df.withColumn('price', price(df.price))
    return df


def get_total_transaction(df):
    return df.agg(functions.sum('item_sold')).first()[0]


def get_omset(df):
    return int(df.agg(functions.sum('price')).first()[0])


def get_total_seller(df):
    return df.select('seller').distinct().count()


def get_total_product(df):
    return df.count()


def get_best_selling(df):
    return df.groupBy('pid').agg(functions.sum('item_sold').alias('sale')).orderBy(functions.desc('sale'))


def get_best_seller(df):
    return df.groupBy('seller').agg(functions.sum('item_sold').alias('sale')).orderBy(functions.desc('sale'))


def selling_to_dict(df):
    rows = df.collect()

    result = []
    for r in rows:
        result.append({
            "pid": r.pid,
            "sale": r.sale
        })
    return result


def seller_to_dict(df):
    rows = df.collect()

    result = []
    for r in rows:
        result.append({
            "seller": r.seller,
            "sale": r.sale
        })
    return result


def prepare_data():
    sess = get_session()
    load = load_data(sess)
    clean = clean_dataframe(load)
    return extract_dataframe(clean)


if __name__ == '__main__':
    data = prepare_data()

    total_transaction = get_total_transaction(data)
    total_omset = get_omset(data)
    total_seller = get_total_seller(data)
    total_selling = get_total_product(data)

    best_selling = get_best_selling(data).limit(10)
    best_seller = get_best_seller(data).limit(10)

    item = {
        "date": str(date.today()),
        "total_transaction": total_transaction,
        "total_omset": total_omset,
        "total_seller": total_seller,
        "total_selling": total_selling,
        "best_selling": selling_to_dict(best_selling),
        "best_seller": seller_to_dict(best_seller)
    }

    pprint(item)

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table('overview')
    table.put_item(Item=item)

from pyspark.sql import SparkSession


def get_raw(session):
    """Get raw dataset

    :param session: spark session
    :return: Dataframe
    """
    df = session.read.format("csv").option("header", "true").load("dataset/raw.csv")
    return df


def cast_datatype(session, df):
    """Cast datatype

    :param session: spark session
    :param df: DataFrame
    :return: Dataframe
    """
    return df.where()


if __name__ == '__main__':
    spark = SparkSession \
        .builder \
        .appName("Market Analytics") \
        .getOrCreate()

    # load raw dataset
    raw = get_raw(spark)

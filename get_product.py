import boto3

from market_analytic import prepare_data


def list_products(df):
    for i in df.select("pid", "title", "price", "seller", "item_sold").toLocalIterator():
        yield {"pid": i.pid, "title": i.title, "price": i.price, "seller": i.seller, "item_sold": i.item_sold}


if __name__ == '__main__':
    data = prepare_data()

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table('product')

    with table.batch_writer() as batch:
        for item in list_products(data):
            batch.put_item(Item=item)
